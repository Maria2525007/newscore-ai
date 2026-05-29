"""Unit: post-match relevance floor в BriefingOrchestrator.

Проверяем, что по нерелевантному запросу низкоскоринговые матчи отсекаются
и результат становится `no_relevant_matches` — сервис не выдаёт «шум».
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from newscore.briefing import (
    BriefingDeps,
    BriefingOrchestrator,
    BriefingRequest,
)
from newscore.config import AppConfig, SourceConfig
from newscore.models import EnrichedArticle, Match
from newscore.parser import ParseReport
from newscore.repository import InMemoryRepository


def _article(title: str) -> EnrichedArticle:
    return EnrichedArticle(
        source="X",
        title=title,
        url=f"https://example.com/{abs(hash(title))}",
        published_at=datetime.now(timezone.utc),
        snippet=title,
        body=title,
        body_extracted=True,
        body_extractor="test",
    )


class _FakeParser:
    def __init__(self, articles: list[EnrichedArticle]) -> None:
        self._articles = articles

    def collect(self, sources, freshness_days):  # noqa: ANN001
        return ParseReport(
            articles=self._articles, failed_sources=[], partial=False
        )


class _ScriptedMatcher:
    """Возвращает заранее заданные scores, игнорируя сам запрос."""

    def __init__(self, name: str, scores: list[float]) -> None:
        self.name = name
        self.version = "test@1.0"
        self._scores = scores

    def rank(self, query, articles, top_n):  # noqa: ANN001
        return [
            Match(article=a, score=s)
            for a, s in zip(articles, self._scores)
        ][:top_n]


def _make_orchestrator(matcher) -> BriefingOrchestrator:
    cfg = AppConfig(
        sources=[
            SourceConfig(
                name="s",
                rss_url="https://x/feed",
                body_extractor="trafilatura",
            )
        ]
    )
    articles = [_article(f"статья {i}") for i in range(len(matcher._scores))]
    deps = BriefingDeps(
        parser=_FakeParser(articles),
        matcher_factory=lambda _name: matcher,
        repository=InMemoryRepository(),
        trace_writer=None,
        summarizer=None,
        domain_checker=None,
    )
    return BriefingOrchestrator(cfg=cfg, deps=deps)


def _request(matcher_name: str) -> BriefingRequest:
    return BriefingRequest(
        query="нерелевантный запрос",
        top_n=10,
        freshness_days=7,
        matcher_name=matcher_name,
        trace=False,
        run_id="run-test-001",
    )


def test_rerank_floor_drops_noise() -> None:
    # релевантные 0.31/0.49 проходят, «шум» 0.0001/0.0 отсекается (floor 0.05).
    matcher = _ScriptedMatcher("rerank", [0.49, 0.31, 0.0001, 0.0])
    result = _make_orchestrator(matcher).run(_request("rerank"))
    assert [round(m.score, 4) for m in result.items] == [0.49, 0.31]
    assert result.meta.reason == "ok"


def test_rerank_floor_all_noise_means_no_results() -> None:
    matcher = _ScriptedMatcher("rerank", [0.0001, 0.0, 0.0001])
    result = _make_orchestrator(matcher).run(_request("rerank"))
    assert result.items == []
    assert result.meta.reason == "no_relevant_matches"


def test_embedding_floor_still_applies() -> None:
    matcher = _ScriptedMatcher("embedding", [0.83, 0.76, 0.74])
    result = _make_orchestrator(matcher).run(_request("embedding"))
    assert [round(m.score, 2) for m in result.items] == [0.83]


def test_bm25_has_no_floor() -> None:
    # bm25 уже отсекает score<=0 внутри матчера; здесь floor не применяется.
    matcher = _ScriptedMatcher("bm25", [0.01, 0.5])
    result = _make_orchestrator(matcher).run(_request("bm25"))
    assert len(result.items) == 2
