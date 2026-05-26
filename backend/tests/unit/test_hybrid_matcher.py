"""Тесты HybridMatcher (RRF fusion BM25 + e5).

Использует mock-матчеры для проверки RRF математики и интеграции без
вызова реальной e5-base модели.
"""

from datetime import datetime, timezone

import pytest

from newscore.matcher import Bm25Matcher, HybridMatcher
from newscore.models import EnrichedArticle, Match


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


class _FakeMatcher:
    """Возвращает заранее заданный ranked-список."""

    name = "fake"
    version = "fake@1.0"

    def __init__(self, ordering: list[EnrichedArticle], scores: list[float] | None = None):
        self.ordering = ordering
        self.scores = scores or [1.0 / (i + 1) for i in range(len(ordering))]

    def rank(self, query: str, articles, top_n: int):
        return [
            Match(article=self.ordering[i], score=self.scores[i])
            for i in range(min(top_n, len(self.ordering)))
        ]


def test_rrf_score_formula() -> None:
    """RRF: doc на позиции 1 у обоих ретриверов → score = 2/(60+1)."""
    a = _article("https://a.example/1", "тест", "тело")
    b = _article("https://a.example/2", "другое", "тело")
    bm25 = _FakeMatcher([a, b])
    emb = _FakeMatcher([a, b])
    h = HybridMatcher(n_candidates=2, rrf_k=60, bm25=bm25, embedding=emb)
    matches = h.rank("q", [a, b], top_n=2)
    assert len(matches) == 2
    # a — на rank 1 у обоих, score = 2 * 1/61
    assert matches[0].article.url == a.url
    assert matches[0].score == pytest.approx(2 / 61)
    # b — на rank 2 у обоих
    assert matches[1].article.url == b.url
    assert matches[1].score == pytest.approx(2 / 62)


def test_rrf_doc_in_one_retriever_only() -> None:
    """Doc найден только одним retriever → score = 1/(k+rank)."""
    a = _article("https://a.example/1", "только в bm25", "тело")
    b = _article("https://a.example/2", "только в эмбеддинге", "тело")
    bm25 = _FakeMatcher([a])
    emb = _FakeMatcher([b])
    h = HybridMatcher(n_candidates=10, rrf_k=60, bm25=bm25, embedding=emb)
    matches = h.rank("q", [a, b], top_n=2)
    # Оба на rank 1 — равные scores
    assert {str(m.article.url) for m in matches} == {str(a.url), str(b.url)}
    assert matches[0].score == pytest.approx(1 / 61)
    assert matches[1].score == pytest.approx(1 / 61)


def test_rrf_prefers_doc_in_both_retrievers() -> None:
    """Doc найденный обоими ретриверами обгоняет doc найденный одним."""
    a = _article("https://a.example/both", "в обоих", "тело")
    b = _article("https://a.example/bm25", "только в bm25", "тело")
    c = _article("https://a.example/emb", "только в emb", "тело")
    bm25 = _FakeMatcher([a, b])   # a:1, b:2
    emb = _FakeMatcher([a, c])    # a:1, c:2
    h = HybridMatcher(n_candidates=10, rrf_k=60, bm25=bm25, embedding=emb)
    matches = h.rank("q", [a, b, c], top_n=3)
    assert matches[0].article.url == a.url
    # a побеждает с 2/61, b и c имеют 1/62
    assert matches[0].score > matches[1].score


def test_rrf_top_n_limit() -> None:
    arts = [_article(f"https://a.example/{i}", f"t{i}", "тело") for i in range(5)]
    bm25 = _FakeMatcher(arts)
    emb = _FakeMatcher(list(reversed(arts)))
    h = HybridMatcher(n_candidates=10, rrf_k=60, bm25=bm25, embedding=emb)
    matches = h.rank("q", arts, top_n=3)
    assert len(matches) == 3


def test_rrf_empty_corpus() -> None:
    assert HybridMatcher().rank("q", [], top_n=5) == []


def test_rrf_integration_with_real_bm25() -> None:
    """Интеграция с настоящим Bm25Matcher (без e5, через mock embedding)."""
    arts = [
        _article("https://a.example/1", "Курс доллара упал", "Доллар снизился."),
        _article("https://a.example/2", "Футбольный матч", "Матч завершён."),
        _article("https://a.example/3", "Курс валют меняется", "Рынок волатилен."),
    ]
    # Mock embedding ranks article[1] highest, чтобы проверить fusion
    emb = _FakeMatcher([arts[1], arts[0], arts[2]])
    h = HybridMatcher(
        n_candidates=10, rrf_k=60, bm25=Bm25Matcher(), embedding=emb
    )
    matches = h.rank("курс валют", arts, top_n=3)
    # bm25 даёт arts[0]/arts[2] высоко; emb даёт arts[1] высоко;
    # fusion должен поднять arts[0] или arts[2] на топ (в bm25 они rank 1-2)
    top_urls = {str(matches[0].article.url), str(matches[1].article.url)}
    assert top_urls & {"https://a.example/1", "https://a.example/3"}


def test_hybrid_uses_default_n_candidates_50() -> None:
    """Значение по умолчанию n_candidates=50 (T²-RAGBench ablation)."""
    h = HybridMatcher()
    assert h.n_candidates == 50
    assert h.rrf_k == 60
    assert h.fusion == "rrf"
    assert h.cc_alpha == 0.5


# ---- Convex Combination fusion ------------------------------------------


def test_hybrid_cc_combines_normalized_scores() -> None:
    """CC α=0.5: doc с топ scores в обоих → top после fusion."""
    a = _article("https://a.example/both", "оба", "тело")
    b = _article("https://a.example/bm25_only", "только в bm25", "тело")
    c = _article("https://a.example/emb_only", "только в emb", "тело")
    # bm25: a=1.0, b=0.5; emb: a=1.0, c=0.5. После min-max:
    # bm25 norm: a=1.0, b=0.0; emb norm: a=1.0, c=0.0.
    # CC α=0.5: a=1.0, b=0.0, c=0.0.
    bm25 = _FakeMatcher([a, b], scores=[1.0, 0.5])
    emb = _FakeMatcher([a, c], scores=[1.0, 0.5])
    h = HybridMatcher(
        n_candidates=10, fusion="cc", cc_alpha=0.5, bm25=bm25, embedding=emb
    )
    matches = h.rank("q", [a, b, c], top_n=3)
    assert str(matches[0].article.url) == str(a.url)
    assert matches[0].score == pytest.approx(1.0)


def test_hybrid_cc_alpha_weighting() -> None:
    """α=1.0 → только embedding score (sparse часть исчезает)."""
    a = _article("https://a.example/a", "a", "тело")
    b = _article("https://a.example/b", "b", "тело")
    bm25 = _FakeMatcher([a, b], scores=[1.0, 0.0])
    emb = _FakeMatcher([b, a], scores=[1.0, 0.0])
    # α=1.0 → CC = embedding only → b обгоняет a.
    h = HybridMatcher(
        n_candidates=10, fusion="cc", cc_alpha=1.0, bm25=bm25, embedding=emb
    )
    matches = h.rank("q", [a, b], top_n=2)
    assert str(matches[0].article.url) == str(b.url)


def test_hybrid_cc_rejects_invalid_alpha() -> None:
    with pytest.raises(ValueError):
        HybridMatcher(fusion="cc", cc_alpha=1.5)
    with pytest.raises(ValueError):
        HybridMatcher(fusion="cc", cc_alpha=-0.1)


def test_hybrid_rejects_invalid_fusion() -> None:
    with pytest.raises(ValueError):
        HybridMatcher(fusion="weighted")


def test_hybrid_cc_handles_constant_scores() -> None:
    """Если все scores равны — min-max получает 1.0 для всех (избегаем div-by-0)."""
    a = _article("https://a.example/a", "a", "тело")
    b = _article("https://a.example/b", "b", "тело")
    bm25 = _FakeMatcher([a, b], scores=[0.5, 0.5])
    emb = _FakeMatcher([a, b], scores=[0.5, 0.5])
    h = HybridMatcher(
        n_candidates=10, fusion="cc", cc_alpha=0.5, bm25=bm25, embedding=emb
    )
    matches = h.rank("q", [a, b], top_n=2)
    assert len(matches) == 2
    # Все scores = 1.0 после нормализации; обе статьи получают 1.0.
    assert matches[0].score == pytest.approx(1.0)
    assert matches[1].score == pytest.approx(1.0)
