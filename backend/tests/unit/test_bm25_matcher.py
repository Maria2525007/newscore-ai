"""Тесты Bm25Matcher (быстрые, без torch)."""

from datetime import datetime, timezone

from newscore.matcher import Bm25Matcher
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


def test_bm25_ranks_relevant_first() -> None:
    arts = [
        _article("https://a.example/1", "Курс доллара упал", "Доллар снизился относительно рубля."),
        _article("https://a.example/2", "Футбольный матч в Москве"),
        _article("https://a.example/3", "Рубль укрепился, курс валют меняется", "Валютный рынок: рубль показал рост."),
    ]
    m = Bm25Matcher()
    matches = m.rank("курс валют", arts, top_n=3)
    assert len(matches) >= 1
    assert str(matches[0].article.url) in {
        "https://a.example/1",
        "https://a.example/3",
    }


def test_bm25_empty_corpus() -> None:
    assert Bm25Matcher().rank("q", [], top_n=5) == []


def test_bm25_empty_query() -> None:
    arts = [_article("https://a.example/1", "Курс доллара")]
    assert Bm25Matcher().rank("   ", arts, top_n=5) == []


def test_bm25_no_match_returns_empty() -> None:
    arts = [
        _article("https://a.example/1", "Футбольный матч"),
        _article("https://a.example/2", "Шахматный турнир"),
    ]
    matches = Bm25Matcher().rank("криптовалюта", arts, top_n=5)
    assert matches == []


def test_bm25_top_n_limit() -> None:
    # mix relevant + irrelevant: на идентичном корпусе BM25 даёт IDF=0
    arts = [
        _article(f"https://a.example/rel{i}", f"курс валют доллар новость{i}")
        for i in range(8)
    ] + [
        _article(f"https://a.example/irrel{i}", f"футбол спорт матч новость{i}")
        for i in range(5)
    ]
    matches = Bm25Matcher().rank("курс валют", arts, top_n=5)
    assert len(matches) == 5
    assert all("rel" in str(m.article.url) for m in matches)


def test_bm25_identical_corpus_returns_empty() -> None:
    # документируем поведение: identical corpus → IDF=0 → нечего ранжировать
    arts = [
        _article(f"https://a.example/{i}", "курс валют доллар")
        for i in range(5)
    ]
    matches = Bm25Matcher().rank("курс валют", arts, top_n=3)
    assert matches == []


def test_bm25_lemmatization_matches_different_word_forms() -> None:
    """PyMorphy3 нормализация: query «валюта» матчит body «валютами»/«валют»."""
    # Корпус ≥3 doc нужен, чтобы IDF был положительным при df=1.
    arts = [
        _article(
            "https://a.example/match",
            "Новости рынка",
            "Сегодня валютами активно торговали на бирже.",
        ),
        _article(
            "https://a.example/nomatch1",
            "Спортивный обзор",
            "Команда выиграла матч с большим счётом.",
        ),
        _article(
            "https://a.example/nomatch2",
            "Кино",
            "Премьера нового фильма прошла в Москве.",
        ),
    ]
    matches = Bm25Matcher().rank("валюта", arts, top_n=3)
    assert len(matches) == 1
    assert str(matches[0].article.url) == "https://a.example/match"


def test_bm25_lemmatization_handles_russian_cases() -> None:
    """Падежи приводятся к нормальной форме: query «доллар» матчит «доллару»."""
    arts = [
        _article(
            "https://a.example/1",
            "Финансы",
            "Курс доллару упал против рубля.",
        ),
        _article(
            "https://a.example/2",
            "Спорт",
            "Футболист забил гол в матче.",
        ),
        _article(
            "https://a.example/3",
            "Кино",
            "Премьера нового фильма прошла в Москве.",
        ),
    ]
    matches = Bm25Matcher().rank("доллар", arts, top_n=3)
    assert len(matches) == 1
    assert str(matches[0].article.url) == "https://a.example/1"


def test_bm25_title_boost_prioritizes_title_matches() -> None:
    """Title boost ×3: документ с query в title обходит документ только с body."""
    body_filler = "Это длинная статья про экономику и финансы страны."
    arts = [
        # Title без query, body содержит query один раз
        _article(
            "https://a.example/body",
            "Экономика страны",
            f"{body_filler} Криптовалюта также упомянута в конце.",
        ),
        # Title содержит query — должен победить благодаря ×3 boost
        _article(
            "https://a.example/title",
            "Криптовалюта подорожала",
            body_filler,
        ),
        # Нерелевантный
        _article(
            "https://a.example/other",
            "Спорт",
            "Футбольный матч завершился ничьей.",
        ),
    ]
    matches = Bm25Matcher().rank("криптовалюта", arts, top_n=3)
    assert len(matches) >= 1
    assert str(matches[0].article.url) == "https://a.example/title"


def test_bm25_latin_tokens_preserved() -> None:
    """PyMorphy3 на латинских токенах не должен ломать ранжирование."""
    arts = [
        _article(
            "https://a.example/1",
            "Embedding model",
            "Модель bge-reranker-v2-m3 показала хороший результат.",
        ),
        _article(
            "https://a.example/2",
            "Спорт",
            "Футбольный матч завершился ничьей.",
        ),
        _article(
            "https://a.example/3",
            "Кино",
            "Премьера нового фильма прошла в Москве.",
        ),
    ]
    matches = Bm25Matcher().rank("bge", arts, top_n=3)
    assert len(matches) == 1
    assert str(matches[0].article.url) == "https://a.example/1"
