"""Тесты RerankMatcher с mock CrossEncoder.

Не загружает настоящий bge-reranker-v2-m3 (568M params, ~570MB ONNX или
2.27GB FP32). Mock через _model DI.
"""

from datetime import datetime, timezone

import pytest

from newscore.matcher import (
    EmbeddingMatcher,
    HybridMatcher,
    Match,
    RerankMatcher,
)
from newscore.models import EnrichedArticle


def _article(url: str, title: str, body: str | None = None) -> EnrichedArticle:
    return EnrichedArticle(
        source="s",
        title=title,
        url=url,
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet="",
        body=body,
        body_extracted=body is not None,
        body_extractor="trafilatura",
    )


class _FakeBase:
    """Mock base matcher — отдаёт articles в заданном порядке."""

    name = "fake"
    version = "fake@1.0"

    def __init__(self, ordering: list[EnrichedArticle]):
        self.ordering = ordering

    def rank(self, query: str, articles, top_n: int):
        return [
            Match(article=a, score=1.0 / (i + 1))
            for i, a in enumerate(self.ordering[:top_n])
        ]


class _FakeReranker:
    """Mock CrossEncoder — отдаёт заранее заданные scores."""

    def __init__(self, scores_by_text: dict[str, float] | None = None):
        self.scores_by_text = scores_by_text or {}
        self.calls: list[list[tuple[str, str]]] = []

    def predict(self, pairs, batch_size=16, show_progress_bar=False):
        self.calls.append(list(pairs))
        return [self.scores_by_text.get(text, 0.0) for _, text in pairs]


def test_rerank_reorders_by_cross_encoder_score() -> None:
    """Base даёт [a,b,c]; reranker scores: c>b>a → output [c,b,a]."""
    a = _article("https://a.example/a", "topic a", "тело a")
    b = _article("https://a.example/b", "topic b", "тело b")
    c = _article("https://a.example/c", "topic c", "тело c")
    base = _FakeBase([a, b, c])
    fake = _FakeReranker(
        {
            f"topic a. тело a": 0.1,
            f"topic b. тело b": 0.5,
            f"topic c. тело c": 0.9,
        }
    )
    rm = RerankMatcher(base=base, n_candidates=10, _model=fake)
    matches = rm.rank("q", [a, b, c], top_n=3)
    assert [str(m.article.url) for m in matches] == [
        "https://a.example/c",
        "https://a.example/b",
        "https://a.example/a",
    ]
    assert matches[0].score == pytest.approx(0.9)


def test_rerank_top_n_limits_output() -> None:
    arts = [
        _article(f"https://a.example/{i}", f"t{i}", f"тело {i}")
        for i in range(5)
    ]
    base = _FakeBase(arts)
    fake = _FakeReranker(
        {f"t{i}. тело {i}": float(i) for i in range(5)}
    )
    rm = RerankMatcher(base=base, n_candidates=5, _model=fake)
    matches = rm.rank("q", arts, top_n=2)
    assert len(matches) == 2
    # Самые высокие scores = t4 и t3
    assert {str(m.article.url) for m in matches} == {
        "https://a.example/4",
        "https://a.example/3",
    }


def test_rerank_passes_n_candidates_to_base() -> None:
    """n_candidates пробрасывается в base.rank — критично для T²-RAGBench ≥50."""
    arts = [_article(f"https://a.example/{i}", f"t{i}", "тело") for i in range(60)]

    class CountingBase:
        name = "count"
        version = "v1"
        last_top_n: int | None = None

        def rank(self, query, articles, top_n: int):
            CountingBase.last_top_n = top_n
            return [Match(article=arts[0], score=1.0)]

    fake = _FakeReranker({"t0. тело": 1.0})
    rm = RerankMatcher(base=CountingBase(), n_candidates=50, _model=fake)
    rm.rank("q", arts, top_n=10)
    assert CountingBase.last_top_n == 50


def test_rerank_empty_corpus() -> None:
    assert RerankMatcher(base=_FakeBase([]), _model=_FakeReranker()).rank(
        "q", [], top_n=5
    ) == []


def test_rerank_empty_base_result() -> None:
    """Base вернул пусто (например, BM25 IDF=0) → reranker не вызывается."""
    a = _article("https://a.example/a", "t", "тело")
    fake = _FakeReranker()
    rm = RerankMatcher(base=_FakeBase([]), _model=fake)
    assert rm.rank("q", [a], top_n=5) == []
    assert fake.calls == []


def test_rerank_pair_text_uses_title_plus_body() -> None:
    """RerankMatcher формирует pair text как «title. body[:1500]»."""
    a = _article(
        "https://a.example/a",
        "Заголовок статьи",
        "Это тело статьи. Здесь много текста про экономику.",
    )
    text = RerankMatcher._pair_text(a, body_chars=1500)
    assert text.startswith("Заголовок статьи. Это тело")


def test_rerank_pair_text_truncates_body() -> None:
    a = _article("https://a.example/a", "T", "x" * 2000)
    text = RerankMatcher._pair_text(a, body_chars=100)
    assert len(text) <= 100 + len("T. ") + 5  # title prefix + slack
    assert text.startswith("T. ")


def test_rerank_pair_text_falls_back_to_snippet() -> None:
    """Если body нет, используем snippet."""
    a = EnrichedArticle(
        source="s",
        title="T",
        url="https://a.example/a",
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet="Сниппет статьи",
        body=None,
        body_extracted=False,
        body_extractor="",
    )
    text = RerankMatcher._pair_text(a, body_chars=1500)
    assert text == "T. Сниппет статьи"


def test_rerank_default_n_candidates_is_50() -> None:
    """T²-RAGBench Fig 6 ablation: 50 cand — баланс recall/latency."""
    rm = RerankMatcher()
    assert rm.n_candidates == 50
    assert isinstance(rm.base, HybridMatcher)


def test_rerank_with_explicit_embedding_base() -> None:
    """RerankMatcher работает поверх любого matcher (не только HybridMatcher)."""
    a = _article("https://a.example/a", "topic a", "тело a")
    b = _article("https://a.example/b", "topic b", "тело b")
    base = _FakeBase([a, b])
    fake = _FakeReranker({"topic a. тело a": 0.9, "topic b. тело b": 0.1})
    rm = RerankMatcher(base=base, _model=fake)
    matches = rm.rank("q", [a, b], top_n=2)
    assert str(matches[0].article.url) == "https://a.example/a"


def test_rerank_score_cache_skips_repeat_predict() -> None:
    """Второй rank с тем же query+articles не зовёт reranker.predict (Redis hit)."""
    import fakeredis

    from newscore import redis_cache

    fake = redis_cache.RedisCache.__new__(redis_cache.RedisCache)
    fake._client = fakeredis.FakeRedis()
    fake._enabled = True
    fake._url = "redis://fake"
    redis_cache.set_cache(fake)
    try:
        a = _article("https://a.example/a", "topic a", "тело a")
        b = _article("https://a.example/b", "topic b", "тело b")
        base = _FakeBase([a, b])
        fake_rr = _FakeReranker(
            {"topic a. тело a": 0.9, "topic b. тело b": 0.3}
        )
        rm = RerankMatcher(base=base, n_candidates=10, _model=fake_rr)

        # 1-й прогон — predict вызывается один раз на 2 пары.
        r1 = rm.rank("курс валют", [a, b], top_n=2)
        assert str(r1[0].article.url) == "https://a.example/a"
        assert len(fake_rr.calls) == 1
        assert len(fake_rr.calls[0]) == 2  # обе пары прогнаны

        # 2-й прогон — scores в Redis → predict НЕ вызывается.
        r2 = rm.rank("курс валют", [a, b], top_n=2)
        assert str(r2[0].article.url) == "https://a.example/a"
        assert r2[0].score == pytest.approx(0.9, abs=1e-5)
        assert len(fake_rr.calls) == 1  # не вырос — всё из кэша
    finally:
        redis_cache.reset_cache()


def test_rerank_cache_partial_miss_only_predicts_new() -> None:
    """Если одна статья новая — predict зовётся только на неё."""
    import fakeredis

    from newscore import redis_cache

    fake = redis_cache.RedisCache.__new__(redis_cache.RedisCache)
    fake._client = fakeredis.FakeRedis()
    fake._enabled = True
    fake._url = "redis://fake"
    redis_cache.set_cache(fake)
    try:
        a = _article("https://a.example/a", "topic a", "тело a")
        b = _article("https://a.example/b", "topic b", "тело b")
        base_ab = _FakeBase([a, b])
        rr = _FakeReranker({"topic a. тело a": 0.9, "topic b. тело b": 0.3})
        rm = RerankMatcher(base=base_ab, n_candidates=10, _model=rr)
        rm.rank("q", [a, b], top_n=2)
        assert len(rr.calls[-1]) == 2

        # добавляем новую статью c — a,b из кэша, только c прогоняется
        c = _article("https://a.example/c", "topic c", "тело c")
        rr.scores_by_text["topic c. тело c"] = 0.7
        base_abc = _FakeBase([a, b, c])
        rm2 = RerankMatcher(base=base_abc, n_candidates=10, _model=rr)
        rm2.rank("q", [a, b, c], top_n=3)
        # последний вызов predict — только 1 пара (c)
        assert len(rr.calls[-1]) == 1
        assert rr.calls[-1][0][1] == "topic c. тело c"
    finally:
        redis_cache.reset_cache()
