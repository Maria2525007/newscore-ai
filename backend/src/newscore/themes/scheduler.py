"""AsyncScheduler — фоновая обработка due themes (Step 1).

ADR-20: asyncio-loop в `daemon`, без APScheduler. Темы исполняются
последовательно через ``asyncio.to_thread`` (см. ADR-23).
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timezone

import structlog

from newscore.themes.service import ThemeService

log = structlog.get_logger(__name__)


class AsyncScheduler:
    def __init__(
        self,
        service: ThemeService,
        tick_seconds: int = 60,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._svc = service
        self._tick = tick_seconds
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    async def run_forever(self) -> None:
        log.info("scheduler_started", tick_s=self._tick)
        try:
            while not self._stop.is_set():
                await self._tick_once()
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=self._tick)
                except asyncio.TimeoutError:
                    pass
        finally:
            log.info("scheduler_stopped")

    async def _tick_once(self) -> None:
        now = self._clock()
        due = self._svc.due_themes(now)
        for theme in due:
            if self._stop.is_set():
                break
            try:
                await asyncio.to_thread(self._svc.run_now, theme.id)
            except Exception as exc:  # noqa: BLE001 — log, продолжать
                log.error(
                    "theme_run_failed",
                    theme_id=theme.id,
                    err=str(exc),
                )
