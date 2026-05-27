"""Typer-subgroup `theme` + `daemon` command (Step 1)."""

from __future__ import annotations

import asyncio
import json
import re
import signal
import sys
from pathlib import Path

import typer

from newscore.briefing import BriefingDeps, BriefingOrchestrator
from newscore.config import load_config
from newscore.logging import configure
from newscore.matcher import Bm25Matcher, EmbeddingMatcher, HybridMatcher, Matcher, RerankMatcher
from newscore.parser import FeedParser
from newscore.repository import InMemoryRepository
from newscore.summarizer import ExtractiveSummarizer
from newscore.themes.db import DEFAULT_DB_PATH, connect
from newscore.themes.models import MatcherName
from newscore.themes.scheduler import AsyncScheduler
from newscore.themes.service import ThemeNotFound, ThemeService

theme_app = typer.Typer(
    help="Управление темами (Step 1: briefing-first).",
    no_args_is_help=True,
)


_PERIOD_RE = re.compile(r"^\s*(\d+)\s*([smhd]?)\s*$", re.IGNORECASE)


def _parse_period(value: str) -> int:
    """`60s`, `30m`, `2h`, `1d` или голое число секунд → секунды."""
    m = _PERIOD_RE.match(value)
    if not m:
        raise typer.BadParameter(f"невалидный период: {value!r}")
    n, unit = int(m.group(1)), m.group(2).lower()
    multiplier = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    seconds = n * multiplier
    if seconds < 60:
        raise typer.BadParameter("минимальный период — 60s")
    return seconds


def _build_service(
    db_path: Path,
    config_path: Path,
) -> ThemeService:
    """Lazy: config/parser/matcher грузятся только при первом run_now."""
    matchers: dict[str, Matcher] = {}

    def _matcher_factory(name: str) -> Matcher:
        if name not in matchers:
            if name == "embedding":
                matchers[name] = EmbeddingMatcher()
            elif name == "bm25":
                matchers[name] = Bm25Matcher()
            elif name == "hybrid":
                matchers[name] = HybridMatcher()
            elif name == "rerank":
                matchers[name] = RerankMatcher()
            else:
                raise ValueError(f"unknown matcher: {name}")
        return matchers[name]

    summarizer = ExtractiveSummarizer()

    def _orch_factory() -> BriefingOrchestrator:
        cfg = load_config(config_path)
        deps = BriefingDeps(
            parser=FeedParser(cfg),
            matcher_factory=_matcher_factory,
            repository=InMemoryRepository(),
            trace_writer=None,
            summarizer=summarizer,
        )
        return BriefingOrchestrator(cfg=cfg, deps=deps)

    return ThemeService(
        conn_factory=lambda: connect(db_path),
        orchestrator_factory=_orch_factory,
    )


# ---- CRUD commands ------------------------------------------------------


@theme_app.command("create")
def create_cmd(
    query: str = typer.Argument(..., help="NL-запрос темы"),
    period: str = typer.Option("1h", "--period", "-p", help="60s | 30m | 2h | 1d"),
    matcher: MatcherName = typer.Option("embedding", "--matcher"),
    top_n: int = typer.Option(10, "--top-n"),
    days: int = typer.Option(7, "--days"),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Создать тему."""
    configure(level="WARNING", fmt="console")
    svc = _build_service(db, config)
    period_seconds = _parse_period(period)
    theme = svc.create(
        query=query,
        period_seconds=period_seconds,
        matcher=matcher,
        top_n=top_n,
        days=days,
    )
    print(theme.model_dump_json(indent=2))


@theme_app.command("list")
def list_cmd(
    json_out: bool = typer.Option(False, "--json"),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Список тем."""
    configure(level="WARNING", fmt="console")
    svc = _build_service(db, config)
    themes = svc.list()
    if json_out:
        print(
            json.dumps(
                [t.model_dump(mode="json") for t in themes],
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if not themes:
        print("(тем нет)")
        return
    print(f"{'ID':<14} {'QUERY':<30} {'MATCHER':<10} {'PERIOD':<8} {'NEXT_RUN':<20} {'STATUS'}")
    for t in themes:
        period_h = t.period_seconds // 3600
        period_m = (t.period_seconds % 3600) // 60
        period = f"{period_h}h" if period_m == 0 else f"{period_h}h{period_m}m"
        if t.period_seconds < 3600:
            period = f"{t.period_seconds // 60}m"
        q = t.query[:28] + ".." if len(t.query) > 30 else t.query
        next_run = t.next_run_at.isoformat()[:19]
        print(
            f"{t.id:<14} {q:<30} {t.matcher:<10} {period:<8} {next_run:<20} {t.status}"
        )


@theme_app.command("show")
def show_cmd(
    theme_id: str = typer.Argument(...),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Полная карточка темы + последний run + последние статьи."""
    configure(level="WARNING", fmt="console")
    svc = _build_service(db, config)
    try:
        theme = svc.get(theme_id)
    except ThemeNotFound:
        typer.echo(f"тема не найдена: {theme_id}", err=True)
        raise typer.Exit(code=1) from None
    latest = svc.latest_run(theme_id)
    articles = svc.latest_articles(theme_id, limit=20)
    print(
        json.dumps(
            {
                "theme": theme.model_dump(mode="json"),
                "latest_run": latest.model_dump(mode="json") if latest else None,
                "articles": [a.model_dump(mode="json") for a in articles],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@theme_app.command("run")
def run_cmd(
    theme_id: str = typer.Argument(...),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Запустить тему сейчас (синхронно)."""
    configure(level=log_level, fmt="console")
    svc = _build_service(db, config)
    try:
        run = svc.run_now(theme_id)
    except ThemeNotFound:
        typer.echo(f"тема не найдена: {theme_id}", err=True)
        raise typer.Exit(code=1) from None
    print(run.model_dump_json(indent=2))


@theme_app.command("delete")
def delete_cmd(
    theme_id: str = typer.Argument(...),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Удалить тему (cascade по runs/articles)."""
    configure(level="WARNING", fmt="console")
    svc = _build_service(db, config)
    try:
        svc.delete(theme_id)
    except ThemeNotFound:
        typer.echo(f"тема не найдена: {theme_id}", err=True)
        raise typer.Exit(code=1) from None
    print(f"тема {theme_id} удалена")


@theme_app.command("pause")
def pause_cmd(
    theme_id: str = typer.Argument(...),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Поставить тему на паузу (scheduler пропустит)."""
    configure(level="WARNING", fmt="console")
    svc = _build_service(db, config)
    try:
        t = svc.pause(theme_id)
    except ThemeNotFound:
        typer.echo(f"тема не найдена: {theme_id}", err=True)
        raise typer.Exit(code=1) from None
    print(t.model_dump_json(indent=2))


@theme_app.command("resume")
def resume_cmd(
    theme_id: str = typer.Argument(...),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Снять тему с паузы."""
    configure(level="WARNING", fmt="console")
    svc = _build_service(db, config)
    try:
        t = svc.resume(theme_id)
    except ThemeNotFound:
        typer.echo(f"тема не найдена: {theme_id}", err=True)
        raise typer.Exit(code=1) from None
    print(t.model_dump_json(indent=2))


# ---- Daemon -------------------------------------------------------------


def daemon_cmd(
    tick: int = typer.Option(60, "--tick", help="секунды между опросами due-тем"),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Запустить фоновый scheduler (блокирующий процесс).

    Темы исполняются последовательно; SIGINT/SIGTERM завершают gracefully
    после текущего run.
    """
    configure(level=log_level, fmt="console")
    svc = _build_service(db, config)
    scheduler = AsyncScheduler(svc, tick_seconds=tick)

    async def _run() -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, scheduler.stop)
            except NotImplementedError:
                pass  # Windows
        await scheduler.run_forever()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        sys.exit(0)
