"""Тесты AsyncScheduler."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from newscore.themes.scheduler import AsyncScheduler


class _FakeService:
    def __init__(self, due_by_tick: list[list[object]]) -> None:
        self._due = due_by_tick
        self.executed: list[str] = []
        self.fail_on: set[str] = set()

    def due_themes(self, now):
        return self._due.pop(0) if self._due else []

    def run_now(self, theme_id: str) -> None:
        if theme_id in self.fail_on:
            raise RuntimeError(f"boom: {theme_id}")
        self.executed.append(theme_id)


class _T:
    """Lightweight stand-in для Theme (только .id используется)."""

    def __init__(self, theme_id: str) -> None:
        self.id = theme_id


def test_scheduler_runs_due_themes_then_stops() -> None:
    svc = _FakeService(due_by_tick=[[_T("a"), _T("b")], []])
    scheduler = AsyncScheduler(svc, tick_seconds=0)

    async def _run() -> None:
        task = asyncio.create_task(scheduler.run_forever())
        await asyncio.sleep(0.05)
        scheduler.stop()
        await task

    asyncio.run(_run())
    assert svc.executed == ["a", "b"]


def test_scheduler_serializes_execution() -> None:
    """Темы должны исполняться по очереди, не параллельно."""
    order: list[str] = []

    class _SlowService(_FakeService):
        def run_now(self, theme_id: str) -> None:
            order.append(f"start:{theme_id}")
            import time

            time.sleep(0.02)
            order.append(f"end:{theme_id}")

    svc = _SlowService(due_by_tick=[[_T("a"), _T("b")], []])
    scheduler = AsyncScheduler(svc, tick_seconds=0)

    async def _run() -> None:
        task = asyncio.create_task(scheduler.run_forever())
        await asyncio.sleep(0.2)
        scheduler.stop()
        await task

    asyncio.run(_run())
    # Должны быть в порядке: start:a, end:a, start:b, end:b (не перекрытие)
    assert order == ["start:a", "end:a", "start:b", "end:b"]


def test_scheduler_continues_on_theme_failure() -> None:
    svc = _FakeService(due_by_tick=[[_T("bad"), _T("good")], []])
    svc.fail_on = {"bad"}
    scheduler = AsyncScheduler(svc, tick_seconds=0)

    async def _run() -> None:
        task = asyncio.create_task(scheduler.run_forever())
        await asyncio.sleep(0.05)
        scheduler.stop()
        await task

    asyncio.run(_run())
    assert "good" in svc.executed
    assert "bad" not in svc.executed


def test_scheduler_clock_injection_works() -> None:
    svc = _FakeService(due_by_tick=[[]])
    fixed = datetime(2026, 5, 24, 10, 0, tzinfo=timezone.utc)
    called: list[datetime] = []

    class _Spy(_FakeService):
        def due_themes(self, now):
            called.append(now)
            return []

    spy = _Spy(due_by_tick=[[]])
    scheduler = AsyncScheduler(spy, tick_seconds=0, clock=lambda: fixed)

    async def _run() -> None:
        task = asyncio.create_task(scheduler.run_forever())
        await asyncio.sleep(0.02)
        scheduler.stop()
        await task

    asyncio.run(_run())
    assert called and called[0] == fixed
