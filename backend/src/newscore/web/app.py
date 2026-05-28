"""FastAPI приложение Step 2.

Темы создаются/просматриваются/запускаются из браузера. Один процесс,
один экземпляр ThemeService, per-thread SQLite-connection.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from newscore.themes.cli import _parse_period
from newscore.themes.service import ThemeNotFound, ThemeService

_HERE = Path(__file__).parent


def _to_msk(value: datetime | str, fmt: str = "%d.%m %H:%M") -> str:
    """Конвертирует UTC datetime или ISO-строку в МСК (UTC+3)."""
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    else:
        dt = value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt + timedelta(hours=3)).strftime(fmt)
TEMPLATES_DIR = _HERE / "templates"
STATIC_DIR = _HERE / "static"


_running: dict[str, bool] = {}  # theme_id → выполняется прямо сейчас
_errors: dict[str, str] = {}   # theme_id → последняя ошибка воркера

_log = logging.getLogger(__name__)


def create_app(service: ThemeService, default_matcher: str = "hybrid") -> FastAPI:
    app = FastAPI(title="NewsCore AI")
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    templates.env.filters["msk"] = _to_msk
    app.mount(
        "/static", StaticFiles(directory=str(STATIC_DIR)), name="static"
    )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        themes = service.list()
        return templates.TemplateResponse(
            request,
            "index.html",
            {"themes": themes, "now": datetime.now(timezone.utc)},
        )

    @app.get("/themes/new", response_class=HTMLResponse)
    def new_form(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request, "new.html", {"now": datetime.now(timezone.utc), "default_matcher": default_matcher}
        )

    @app.post("/themes")
    def create_theme(
        query: str = Form(..., min_length=1, max_length=500),
        period: str = Form("1h"),
        matcher: str = Form(default_matcher),
        top_n: int = Form(10),
        days: int = Form(7),
    ) -> RedirectResponse:
        try:
            period_seconds = _parse_period(period)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if matcher not in {"embedding", "bm25", "hybrid", "rerank"}:
            raise HTTPException(status_code=400, detail="bad matcher")
        theme = service.create(
            query=query,
            period_seconds=period_seconds,
            matcher=matcher,  # type: ignore[arg-type]
            top_n=top_n,
            days=days,
        )
        return RedirectResponse(url=f"/themes/{theme.id}?autorun=1", status_code=303)

    @app.get("/themes/{theme_id}", response_class=HTMLResponse)
    def theme_detail(theme_id: str, request: Request) -> HTMLResponse:
        try:
            theme = service.get(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        latest = service.latest_run(theme_id)
        articles = service.latest_articles(theme_id, limit=50)
        runs = service.list_runs(theme_id, limit=10)
        return templates.TemplateResponse(
            request,
            "theme.html",
            {
                "theme": theme,
                "latest": latest,
                "articles": articles,
                "runs": runs,
                "now": datetime.now(timezone.utc),
            },
        )

    @app.post("/themes/{theme_id}/run")
    def run_theme(theme_id: str) -> RedirectResponse:
        """Синхронный запуск — оставлен для совместимости."""
        try:
            service.run_now(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        return RedirectResponse(url=f"/themes/{theme_id}", status_code=303)

    @app.post("/themes/{theme_id}/run-async")
    def run_theme_async(theme_id: str) -> JSONResponse:
        """Запуск в фоновом потоке — браузер не блокируется."""
        if _running.get(theme_id):
            return JSONResponse({"status": "already_running"})
        try:
            service.get(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None

        def _worker() -> None:
            _running[theme_id] = True
            _errors.pop(theme_id, None)
            try:
                service.run_now(theme_id)
            except Exception as exc:
                _log.exception("run_worker_error theme_id=%s", theme_id)
                _errors[theme_id] = str(exc)
            finally:
                _running[theme_id] = False

        threading.Thread(target=_worker, daemon=True).start()
        return JSONResponse({"status": "started"})

    @app.get("/themes/{theme_id}/running")
    def theme_is_running(theme_id: str) -> JSONResponse:
        """Проверка: идёт ли сейчас запуск темы."""
        return JSONResponse({"running": _running.get(theme_id, False)})

    @app.get("/themes/{theme_id}/briefing")
    def theme_briefing(theme_id: str) -> JSONResponse:
        """Краткий брифинг по последним статьям темы."""
        try:
            theme = service.get(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        articles = service.latest_articles(theme_id, limit=10)
        if not articles:
            return JSONResponse({"text": ""})

        _NOISE = ("фото:", "источник:", "читайте также", "подписывайтесь", "©")
        sentences: list[str] = []
        for a in articles[:5]:
            art = a.payload.get("article", {})
            raw = art.get("summary") or art.get("snippet") or ""
            if not raw:
                continue
            for part in raw.replace("…", ".").replace("\n", " ").split("."):
                part = part.strip()
                if (len(part) > 40
                        and not any(n in part.lower() for n in _NOISE)
                        and part[-1:] not in ("«", "„", '"')):
                    sentences.append(part.rstrip(".,:;") + ".")
                    break

        if not sentences:
            return JSONResponse({"text": ""})

        text = " ".join(sentences[:3])
        return JSONResponse({"text": text})

    @app.delete("/themes/{theme_id}/articles")
    def clear_articles(theme_id: str) -> JSONResponse:
        try:
            service.get(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        service.clear_articles(theme_id)
        return JSONResponse({"ok": True})

    @app.post("/themes/{theme_id}/pause")
    def pause_theme(theme_id: str) -> RedirectResponse:
        try:
            service.pause(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        return RedirectResponse(url=f"/themes/{theme_id}", status_code=303)

    @app.post("/themes/{theme_id}/resume")
    def resume_theme(theme_id: str) -> RedirectResponse:
        try:
            service.resume(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        return RedirectResponse(url=f"/themes/{theme_id}", status_code=303)

    @app.post("/themes/{theme_id}/delete")
    def delete_theme(theme_id: str) -> RedirectResponse:
        try:
            service.delete(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        return RedirectResponse(url="/", status_code=303)

    return app
