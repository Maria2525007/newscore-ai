"""Integration: FastAPI web-роуты через TestClient + FakeOrchestrator."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from newscore.briefing import BriefingRequest
from newscore.models import BriefingResult, EnrichedArticle, Match, RunMeta
from newscore.themes.db import connect
from newscore.themes.service import ThemeService
from newscore.web import create_app


_DISTINCT_TITLES = [
    "Курс рубля и доллара на бирже",
    "Футбольный матч Спартак Зенит",
    "Литература Достоевского переиздана",
    "Космический корабль запущен",
    "Кулинарные рецепты средиземноморья",
    "Политические выборы в регионе",
    "Музыкальный концерт филармонии",
    "Технологии искусственного интеллекта",
    "Медицина и вакцинация населения",
    "Образование школьников химии",
]


def _enriched(url: str, title: str | None = None) -> EnrichedArticle:
    # Default title — семантически РАЗНЫЙ per URL, чтобы semantic novelty
    # (ADR-25) не помечал тестовые статьи как duplicate друг друга на
    # реальной e5-модели. Stable mapping через sha256.
    if title is None:
        import hashlib

        digest = hashlib.sha256(url.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % len(_DISTINCT_TITLES)
        title = _DISTINCT_TITLES[idx]
    return EnrichedArticle(
        source="s",
        title=title,
        url=url,
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet="snippet",
        body=None,
        body_extracted=False,
        body_extractor="trafilatura",
    )


def _result(query: str, urls: list[str]) -> BriefingResult:
    started = datetime.now(timezone.utc)
    finished = started + timedelta(seconds=1)
    matches = [Match(article=_enriched(u), score=0.85) for u in urls]
    meta = RunMeta(
        run_id="ignored",
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
    def __init__(self, scripted: list[BriefingResult]) -> None:
        self._scripted = list(scripted)

    def run(self, req: BriefingRequest) -> BriefingResult:
        result = self._scripted.pop(0) if self._scripted else _result(req.query, [])
        result.meta.run_id = req.run_id
        return result


def _make_client(tmp_path: Path, orchestrator: FakeOrchestrator) -> tuple[TestClient, ThemeService]:
    db = tmp_path / "themes.db"
    conn = connect(db)
    service = ThemeService(
        conn_factory=lambda: conn,
        orchestrator_factory=lambda: orchestrator,
    )
    app = create_app(service)
    return TestClient(app), service


def test_index_empty(tmp_path: Path) -> None:
    client, _ = _make_client(tmp_path, FakeOrchestrator([]))
    response = client.get("/")
    assert response.status_code == 200
    assert "Тем пока нет" in response.text


def test_create_theme_via_form_redirects_to_detail(tmp_path: Path) -> None:
    client, service = _make_client(tmp_path, FakeOrchestrator([]))
    response = client.post(
        "/themes",
        data={"query": "курс валют", "period": "30m", "matcher": "embedding",
              "top_n": 10, "days": 7},
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/themes/")
    themes = service.list()
    assert len(themes) == 1
    assert themes[0].query == "курс валют"


def test_create_theme_invalid_period_400(tmp_path: Path) -> None:
    client, _ = _make_client(tmp_path, FakeOrchestrator([]))
    response = client.post(
        "/themes",
        data={"query": "x", "period": "5s", "matcher": "embedding",
              "top_n": 10, "days": 7},
    )
    assert response.status_code == 400


def test_create_theme_invalid_matcher_400(tmp_path: Path) -> None:
    client, _ = _make_client(tmp_path, FakeOrchestrator([]))
    response = client.post(
        "/themes",
        data={"query": "x", "period": "30m", "matcher": "nope",
              "top_n": 10, "days": 7},
    )
    assert response.status_code == 400


def test_theme_detail_renders(tmp_path: Path) -> None:
    client, service = _make_client(tmp_path, FakeOrchestrator([]))
    theme = service.create("test query", period_seconds=3600)
    response = client.get(f"/themes/{theme.id}")
    assert response.status_code == 200
    assert "test query" in response.text
    assert "Ещё не запускалась" in response.text


def test_theme_detail_404_on_unknown(tmp_path: Path) -> None:
    client, _ = _make_client(tmp_path, FakeOrchestrator([]))
    response = client.get("/themes/nope")
    assert response.status_code == 404


def test_run_theme_triggers_orchestrator(tmp_path: Path) -> None:
    fake = FakeOrchestrator([_result("q", ["https://a.com/1", "https://a.com/2"])])
    client, service = _make_client(tmp_path, fake)
    theme = service.create("q", period_seconds=3600)
    response = client.post(f"/themes/{theme.id}/run", follow_redirects=False)
    assert response.status_code == 303
    latest = service.latest_run(theme.id)
    assert latest is not None
    assert latest.items_total == 2
    assert latest.items_new == 2


def test_detail_shows_articles_after_run(tmp_path: Path) -> None:
    fake = FakeOrchestrator([_result("q", ["https://a.com/1"])])
    client, service = _make_client(tmp_path, fake)
    theme = service.create("q", period_seconds=3600)
    client.post(f"/themes/{theme.id}/run")
    detail = client.get(f"/themes/{theme.id}")
    assert "https://a.com/1" in detail.text


def test_pause_resume(tmp_path: Path) -> None:
    client, service = _make_client(tmp_path, FakeOrchestrator([]))
    theme = service.create("q", period_seconds=3600)
    client.post(f"/themes/{theme.id}/pause", follow_redirects=False)
    assert service.get(theme.id).status == "paused"
    client.post(f"/themes/{theme.id}/resume", follow_redirects=False)
    assert service.get(theme.id).status == "active"


def test_delete_removes_and_redirects_to_index(tmp_path: Path) -> None:
    client, service = _make_client(tmp_path, FakeOrchestrator([]))
    theme = service.create("q", period_seconds=3600)
    response = client.post(f"/themes/{theme.id}/delete", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert service.list() == []


def test_new_form_renders(tmp_path: Path) -> None:
    client, _ = _make_client(tmp_path, FakeOrchestrator([]))
    response = client.get("/themes/new")
    assert response.status_code == 200
    assert 'name="query"' in response.text


def test_index_with_themes_lists_them(tmp_path: Path) -> None:
    client, service = _make_client(tmp_path, FakeOrchestrator([]))
    service.create("курс валют", period_seconds=3600)
    service.create("ставка ЦБ", period_seconds=1800)
    response = client.get("/")
    assert "курс валют" in response.text
    assert "ставка ЦБ" in response.text
