"""FastAPI приложение Step 2.

Темы создаются/просматриваются/запускаются из браузера. Один процесс,
один экземпляр ThemeService, per-thread SQLite-connection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from newscore.themes.cli import _parse_period
from newscore.themes.service import ThemeNotFound, ThemeService

_HERE = Path(__file__).parent
TEMPLATES_DIR = _HERE / "templates"
STATIC_DIR = _HERE / "static"


def create_app(service: ThemeService) -> FastAPI:
    app = FastAPI(title="NewsCore AI")
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
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
            request, "new.html", {"now": datetime.now(timezone.utc)}
        )

    @app.post("/themes")
    def create_theme(
        query: str = Form(..., min_length=1, max_length=500),
        period: str = Form("1h"),
        matcher: str = Form("embedding"),
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
        return RedirectResponse(url=f"/themes/{theme.id}", status_code=303)

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
        """Синхронный запуск (~30s холодный embedding). Браузер ждёт."""
        try:
            service.run_now(theme_id)
        except ThemeNotFound:
            raise HTTPException(status_code=404, detail="theme not found") from None
        return RedirectResponse(url=f"/themes/{theme_id}", status_code=303)

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
