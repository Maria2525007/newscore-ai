"""Тесты ThemeService: CRUD + delta-логика."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from newscore.briefing import BriefingRequest
from newscore.models import (
    BriefingResult,
    EnrichedArticle,
    FailedSource,
    Match,
    RunMeta,
)
from newscore.themes.db import connect
from newscore.themes.service import ThemeNotFound, ThemeService, url_hash


# ---- helpers ------------------------------------------------------------


def _enriched(url: str, title: str | None = None) -> EnrichedArticle:
    # Default title = unique per URL — semantic novelty (ADR-25) не должен
    # считать legacy-тестовые статьи дубликатами друг друга.
    if title is None:
        title = f"Title for {url}"
    return EnrichedArticle(
        source="s",
        title=title,
        url=url,
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet="",
        body=None,
        body_extracted=False,
        body_extractor="trafilatura",
    )


def _result(query: str, urls: list[str], *, run_id: str = "r1") -> BriefingResult:
    matches = [Match(article=_enriched(u), score=0.9) for u in urls]
    # Используем настоящий now() чтобы каждый вызов давал монотонно растущий
    # started_at — иначе ORDER BY started_at DESC недетерминирован на ties.
    started = datetime.now(timezone.utc)
    finished = started + timedelta(seconds=2)
    meta = RunMeta(
        run_id=run_id,
        started_at=started,
        finished_at=finished,
        matcher_name="embedding",
        matcher_version="v",
        sources_snapshot_at=started,
        freshness_days=7,
        partial=False,
        failed_sources=[],
        reason="ok" if matches else "no_relevant_matches",
    )
    return BriefingResult(query=query, items=matches, meta=meta)


class FakeOrchestrator:
    """Возвращает предзаписанные BriefingResult по очереди."""

    def __init__(self, scripted: list[BriefingResult]) -> None:
        self._scripted = list(scripted)
        self.calls: list[BriefingRequest] = []

    def run(self, req: BriefingRequest) -> BriefingResult:
        self.calls.append(req)
        result = self._scripted.pop(0) if self._scripted else _result(req.query, [])
        # Подменяем run_id на сгенерированный сервисом — он его передаёт через req.
        result.meta.run_id = req.run_id
        return result


def _make_service(
    tmp_path: Path, orchestrator: FakeOrchestrator
) -> ThemeService:
    db = tmp_path / "themes.db"
    conn = connect(db)
    return ThemeService(
        conn_factory=lambda: conn,
        orchestrator_factory=lambda: orchestrator,
    )


# ---- url_hash -----------------------------------------------------------


def test_url_hash_is_deterministic_and_url_normalized() -> None:
    a = url_hash("https://example.com/x")
    b = url_hash("HTTPS://example.com/x/")
    c = url_hash("https://example.com/x ")
    assert a == b == c
    assert len(a) == 32


def test_url_hash_differs_on_different_urls() -> None:
    assert url_hash("https://a.com/1") != url_hash("https://a.com/2")


# ---- CRUD ---------------------------------------------------------------


def test_create_returns_theme_with_id(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t = svc.create("курс валют", period_seconds=3600)
    assert len(t.id) == 12
    assert t.query == "курс валют"
    assert t.period_seconds == 3600
    assert t.matcher == "embedding"
    assert t.status == "active"


def test_create_strips_whitespace(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t = svc.create("  ставка  ", period_seconds=600)
    assert t.query == "ставка"


def test_list_orders_by_created_desc(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t1 = svc.create("a", period_seconds=60)
    t2 = svc.create("b", period_seconds=60)
    listed = svc.list()
    assert [t.id for t in listed] == [t2.id, t1.id]


def test_list_filters_by_status(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t1 = svc.create("a", period_seconds=60)
    svc.create("b", period_seconds=60)
    svc.pause(t1.id)
    assert {t.id for t in svc.list(status="active")} == {
        t.id for t in svc.list() if t.status == "active"
    }
    assert {t.id for t in svc.list(status="paused")} == {t1.id}


def test_get_raises_on_unknown(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    with pytest.raises(ThemeNotFound):
        svc.get("nope")


def test_delete_removes_theme(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t = svc.create("x", period_seconds=60)
    svc.delete(t.id)
    assert svc.list() == []


def test_delete_raises_on_unknown(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    with pytest.raises(ThemeNotFound):
        svc.delete("nope")


def test_pause_resume(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t = svc.create("x", period_seconds=60)
    paused = svc.pause(t.id)
    assert paused.status == "paused"
    resumed = svc.resume(t.id)
    assert resumed.status == "active"


# ---- due_themes ---------------------------------------------------------


def test_due_themes_returns_only_active_and_due(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    t_active = svc.create("a", period_seconds=60)
    t_paused = svc.create("b", period_seconds=60)
    svc.pause(t_paused.id)

    now = datetime.now(timezone.utc) + timedelta(seconds=1)
    due = svc.due_themes(now)
    due_ids = {t.id for t in due}
    assert t_active.id in due_ids
    assert t_paused.id not in due_ids


# ---- run_now + delta ----------------------------------------------------


def test_run_now_persists_run_and_increments_items_new(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [_result("q", ["https://a.com/1", "https://a.com/2"], run_id="ignored")]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    run = svc.run_now(t.id)
    assert run.items_total == 2
    assert run.items_new == 2
    assert run.theme_id == t.id


def test_run_now_keeps_items_new_zero_on_revisit(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [
            _result("q", ["https://a.com/1"], run_id="ignored"),
            _result("q", ["https://a.com/1"], run_id="ignored"),
        ]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    first = svc.run_now(t.id)
    second = svc.run_now(t.id)
    assert first.items_new == 1
    assert second.items_new == 0
    assert second.items_total == 1


def test_run_now_normalizes_url_for_dedup(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [
            _result("q", ["https://a.com/x"], run_id="r1"),
            _result("q", ["https://A.COM/x/"], run_id="r2"),
        ]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    svc.run_now(t.id)
    second = svc.run_now(t.id)
    assert second.items_new == 0


def test_run_now_updates_next_run_at_and_last_run_id(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [_result("q", ["https://a.com/1"], run_id="ignored")]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=3600)
    original_next = t.next_run_at
    run = svc.run_now(t.id)
    updated = svc.get(t.id)
    assert updated.last_run_id == run.id
    assert updated.next_run_at >= original_next + timedelta(seconds=3590)


def test_run_now_raises_on_unknown_theme(tmp_path: Path) -> None:
    svc = _make_service(tmp_path, FakeOrchestrator([]))
    with pytest.raises(ThemeNotFound):
        svc.run_now("nope")


# ---- queries для UI -----------------------------------------------------


def test_latest_run_returns_most_recent(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [
            _result("q", ["https://a.com/1"]),
            _result("q", ["https://a.com/2"]),
        ]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    svc.run_now(t.id)
    second = svc.run_now(t.id)
    latest = svc.latest_run(t.id)
    assert latest is not None
    assert latest.id == second.id


def test_list_runs_limit(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [_result("q", [f"https://a.com/{i}"]) for i in range(5)]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    for _ in range(5):
        svc.run_now(t.id)
    assert len(svc.list_runs(t.id, limit=3)) == 3


def test_latest_articles_and_new_since(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [
            _result("q", ["https://a.com/1", "https://a.com/2"]),
            _result("q", ["https://a.com/3"]),
        ]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    svc.run_now(t.id)
    import time

    time.sleep(0.01)
    boundary = datetime.now(timezone.utc)
    time.sleep(0.01)
    svc.run_now(t.id)
    articles = svc.latest_articles(t.id)
    assert len(articles) == 3
    new_after = svc.new_since(t.id, boundary)
    assert {a.url_hash for a in new_after} == {url_hash("https://a.com/3")}


def test_delete_cascades_runs_and_articles(tmp_path: Path) -> None:
    fake = FakeOrchestrator(
        [_result("q", ["https://a.com/1"], run_id="ignored")]
    )
    svc = _make_service(tmp_path, fake)
    t = svc.create("q", period_seconds=60)
    svc.run_now(t.id)
    svc.delete(t.id)
    assert svc.latest_run(t.id) is None
    assert svc.latest_articles(t.id) == []
