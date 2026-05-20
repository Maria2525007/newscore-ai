"""Тесты дедупликации (модуль newscore.dedupe)."""

from datetime import datetime

from newscore.dedupe import dedupe_by_url
from newscore.models import EnrichedArticle


def _article(url: str, title: str = "t") -> EnrichedArticle:
    return EnrichedArticle(
        source="s",
        title=title,
        url=url,
        published_at=datetime(2026, 5, 20),
        snippet="",
        body=None,
        body_extracted=False,
        body_extractor="trafilatura",
    )


def test_dedupe_by_url_removes_duplicates() -> None:
    arts = [
        _article("https://a.example/1"),
        _article("https://a.example/2"),
        _article("https://a.example/1"),
    ]
    unique, removed = dedupe_by_url(arts)
    assert removed == 1
    assert len(unique) == 2
    assert str(unique[0].url) == "https://a.example/1"
    assert str(unique[1].url) == "https://a.example/2"


def test_dedupe_by_url_preserves_order() -> None:
    arts = [
        _article("https://a.example/3"),
        _article("https://a.example/1"),
        _article("https://a.example/2"),
    ]
    unique, _ = dedupe_by_url(arts)
    assert [str(a.url) for a in unique] == [
        "https://a.example/3",
        "https://a.example/1",
        "https://a.example/2",
    ]


def test_dedupe_by_url_empty() -> None:
    unique, removed = dedupe_by_url([])
    assert unique == []
    assert removed == 0
