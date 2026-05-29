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

# ---- briefing result cache (Redis) -------------------------------------


class _CountingParser:
    """Парсер, считающий сколько раз его вызвали (для проверки cache hit)."""

    def __init__(self, articles: list[EnrichedArticle]) -> None:
        self._articles = articles
        self.calls = 0

    def collect(self, sources, freshness_days):  # noqa: ANN001
        self.calls += 1
        return ParseReport(
            articles=self._articles, failed_sources=[], partial=False
        )


def _orch_with_parser(parser, matcher) -> BriefingOrchestrator:
    cfg = AppConfig(
        sources=[
            SourceConfig(
                name="s", rss_url="https://x/feed", body_extractor="trafilatura"
            )
        ]
    )
    deps = BriefingDeps(
        parser=parser,
        matcher_factory=lambda _name: matcher,
        repository=InMemoryRepository(),
        trace_writer=None,
        summarizer=None,
        domain_checker=None,
    )
    return BriefingOrchestrator(cfg=cfg, deps=deps)


def test_result_cache_hit_skips_parse() -> None:
    """use_result_cache=True: повтор того же запроса не парсит заново."""
    import fakeredis

    from newscore import redis_cache

    fake = redis_cache.RedisCache.__new__(redis_cache.RedisCache)
    fake._client = fakeredis.FakeRedis()
    fake._enabled = True
    fake._url = "redis://fake"
    redis_cache.set_cache(fake)
    try:
        articles = [_article("курс валют растёт"), _article("вторая статья")]
        parser = _CountingParser(articles)
        matcher = _ScriptedMatcher("embedding", [0.9, 0.85])
        orch = _orch_with_parser(parser, matcher)

        req = BriefingRequest(
            query="курс валют",
            top_n=10,
            freshness_days=7,
            matcher_name="embedding",
            trace=False,
            run_id="run-1",
            use_result_cache=True,
        )
        r1 = orch.run(req)
        assert r1.meta.reason == "ok"
        assert parser.calls == 1

        # повтор — тот же query/matcher/days/top_n → из кэша, parse не зовётся
        req2 = BriefingRequest(
            query="курс валют",
            top_n=10,
            freshness_days=7,
            matcher_name="embedding",
            trace=False,
            run_id="run-2",
            use_result_cache=True,
        )
        r2 = orch.run(req2)
        assert parser.calls == 1  # НЕ вырос — cache hit
        assert r2.meta.run_id == "run-2"  # свежий run_id
        assert len(r2.items) == len(r1.items)
    finally:
        redis_cache.reset_cache()


def test_result_cache_disabled_by_default() -> None:
    """Без use_result_cache (default) — парсер зовётся каждый раз."""
    import fakeredis

    from newscore import redis_cache

    fake = redis_cache.RedisCache.__new__(redis_cache.RedisCache)
    fake._client = fakeredis.FakeRedis()
    fake._enabled = True
    fake._url = "redis://fake"
    redis_cache.set_cache(fake)
    try:
        articles = [_article("статья один")]
        parser = _CountingParser(articles)
        matcher = _ScriptedMatcher("embedding", [0.9])
        orch = _orch_with_parser(parser, matcher)

        req = BriefingRequest(
            query="q", top_n=10, freshness_days=7,
            matcher_name="embedding", trace=False, run_id="r1",
        )  # use_result_cache по умолчанию False
        orch.run(req)
        orch.run(req)
        assert parser.calls == 2  # каждый раз свежий parse
    finally:
        redis_cache.reset_cache()
