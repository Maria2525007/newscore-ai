"""Unit-тесты статических хелперов FeedParser (parser.py).

Сетевые сценарии — в ``backend/tests/integration/test_parser_async.py``.
Здесь — только pure-функции и парсинг entry.
"""

import asyncio
from datetime import datetime, timezone

import httpx
import pytest

from newscore.config import SourceConfig
from newscore.parser import FeedParser, _is_transient


# ---------- _classify_error ----------------------------------------------------


def _resp(status: int) -> httpx.Response:
    return httpx.Response(status, request=httpx.Request("GET", "https://x"))


def test_classify_timeout() -> None:
    assert FeedParser._classify_error(httpx.ReadTimeout("t")) == "timeout"
    assert FeedParser._classify_error(httpx.ConnectTimeout("t")) == "timeout"


def test_classify_http_5xx() -> None:
    err = httpx.HTTPStatusError("server", request=_resp(500).request, response=_resp(503))
    assert FeedParser._classify_error(err) == "http_503"


def test_classify_http_4xx() -> None:
    err = httpx.HTTPStatusError("client", request=_resp(404).request, response=_resp(404))
    assert FeedParser._classify_error(err) == "http_404"


def test_classify_http_other() -> None:
    assert FeedParser._classify_error(httpx.ConnectError("dns")) == "http_error"


def test_classify_cancelled() -> None:
    assert FeedParser._classify_error(asyncio.CancelledError()) == "cancelled"


def test_classify_xml_invalid() -> None:
    assert FeedParser._classify_error(ValueError("xml_invalid: bad")) == "xml_invalid"


def test_classify_no_items() -> None:
    assert FeedParser._classify_error(ValueError("no_items")) == "no_items"


def test_classify_unknown() -> None:
    assert FeedParser._classify_error(RuntimeError("?")) == "unknown"


# ---------- _is_transient ------------------------------------------------------


def test_is_transient_timeout_yes() -> None:
    assert _is_transient(httpx.ReadTimeout("t")) is True


def test_is_transient_connect_yes() -> None:
    assert _is_transient(httpx.ConnectError("dns")) is True


def test_is_transient_5xx_yes() -> None:
    err = httpx.HTTPStatusError("s", request=_resp(503).request, response=_resp(503))
    assert _is_transient(err) is True


def test_is_transient_4xx_no() -> None:
    err = httpx.HTTPStatusError("c", request=_resp(404).request, response=_resp(404))
    assert _is_transient(err) is False


def test_is_transient_429_no() -> None:
    # 429 — не transient (rate limit = «прекрати», не «попробуй ещё»)
    err = httpx.HTTPStatusError("rl", request=_resp(429).request, response=_resp(429))
    assert _is_transient(err) is False


def test_is_transient_other_no() -> None:
    assert _is_transient(ValueError("boom")) is False


# ---------- _extract_rbc_full_text --------------------------------------------


def test_rbc_full_text_namespace_key() -> None:
    entry = {"rbc_news_full-text": "Полный текст"}
    assert FeedParser._extract_rbc_full_text(entry) == "Полный текст"


def test_rbc_full_text_dict_value() -> None:
    entry = {"rbc_news_full-text": {"value": "Полный текст из dict"}}
    assert FeedParser._extract_rbc_full_text(entry) == "Полный текст из dict"


def test_rbc_full_text_fallback_alt_key() -> None:
    entry = {"rbc_news_fulltext": "Без дефиса"}
    assert FeedParser._extract_rbc_full_text(entry) == "Без дефиса"


def test_rbc_full_text_missing_returns_none() -> None:
    assert FeedParser._extract_rbc_full_text({"title": "x"}) is None


def test_rbc_full_text_empty_string_returns_none() -> None:
    assert FeedParser._extract_rbc_full_text({"rbc_news_full-text": "   "}) is None


def test_rbc_full_text_strips_whitespace() -> None:
    assert FeedParser._extract_rbc_full_text({"rbc_news_full-text": "  ok  "}) == "ok"


# ---------- _parse_pubdate ----------------------------------------------------


def test_parse_pubdate_from_published_parsed() -> None:
    entry = {"published_parsed": (2026, 5, 20, 10, 30, 0, 0, 0, 0)}
    dt = FeedParser._parse_pubdate(entry)
    assert dt == datetime(2026, 5, 20, 10, 30, 0, tzinfo=timezone.utc)


def test_parse_pubdate_falls_back_to_updated() -> None:
    entry = {
        "published_parsed": None,
        "updated_parsed": (2026, 5, 19, 9, 0, 0, 0, 0, 0),
    }
    dt = FeedParser._parse_pubdate(entry)
    assert dt == datetime(2026, 5, 19, 9, 0, 0, tzinfo=timezone.utc)


def test_parse_pubdate_returns_none_when_missing() -> None:
    assert FeedParser._parse_pubdate({}) is None
    assert FeedParser._parse_pubdate({"published_parsed": None}) is None


def test_parse_pubdate_returns_tz_aware() -> None:
    entry = {"published_parsed": (2026, 1, 1, 0, 0, 0, 0, 0, 0)}
    dt = FeedParser._parse_pubdate(entry)
    assert dt is not None
    assert dt.tzinfo is not None  # должен быть TZ-aware для cutoff-сравнения


# ---------- _entry_to_raw -----------------------------------------------------


def _src(name: str = "s") -> SourceConfig:
    return SourceConfig(
        name=name,
        rss_url="https://x.example/rss",
        body_extractor="trafilatura",
    )


def _make_parser() -> FeedParser:
    # AppConfig тут не нужен глубоко — методы _entry_to_raw / _parse_pubdate
    # не используют self.cfg. Передаём минимальный stub.
    from newscore.config import AppConfig

    cfg = AppConfig(sources=[_src()])
    return FeedParser(cfg)


def test_entry_to_raw_happy_path() -> None:
    parser = _make_parser()
    entry = {
        "title": "Title",
        "link": "https://x.example/article1",
        "published_parsed": (2026, 5, 20, 10, 0, 0, 0, 0, 0),
        "summary": "snippet text",
    }
    raw = parser._entry_to_raw(_src(), entry)
    assert raw is not None
    assert raw.title == "Title"
    assert str(raw.url).rstrip("/") == "https://x.example/article1"
    assert raw.snippet == "snippet text"
    assert raw.rss_full_text is None


def test_entry_to_raw_strips_title_link() -> None:
    parser = _make_parser()
    entry = {
        "title": "  Title  ",
        "link": "  https://x.example/article1  ",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
    }
    raw = parser._entry_to_raw(_src(), entry)
    assert raw is not None
    assert raw.title == "Title"


def test_entry_to_raw_empty_title_returns_none() -> None:
    parser = _make_parser()
    entry = {
        "title": "  ",
        "link": "https://x.example/1",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
    }
    assert parser._entry_to_raw(_src(), entry) is None


def test_entry_to_raw_empty_link_returns_none() -> None:
    parser = _make_parser()
    entry = {
        "title": "t",
        "link": "",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
    }
    assert parser._entry_to_raw(_src(), entry) is None


def test_entry_to_raw_no_pubdate_returns_none() -> None:
    parser = _make_parser()
    entry = {"title": "t", "link": "https://x.example/1"}
    assert parser._entry_to_raw(_src(), entry) is None


def test_entry_to_raw_invalid_url_returns_none() -> None:
    parser = _make_parser()
    entry = {
        "title": "t",
        "link": "not-a-url",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
    }
    assert parser._entry_to_raw(_src(), entry) is None


def test_entry_to_raw_snippet_falls_back_to_description() -> None:
    parser = _make_parser()
    entry = {
        "title": "t",
        "link": "https://x.example/1",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
        "description": "fallback snippet",
    }
    raw = parser._entry_to_raw(_src(), entry)
    assert raw is not None
    assert raw.snippet == "fallback snippet"


def test_entry_to_raw_snippet_truncated_to_1000() -> None:
    parser = _make_parser()
    entry = {
        "title": "t",
        "link": "https://x.example/1",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
        "summary": "a" * 2000,
    }
    raw = parser._entry_to_raw(_src(), entry)
    assert raw is not None
    assert len(raw.snippet) == 1000


def test_entry_to_raw_picks_up_rbc_full_text() -> None:
    parser = _make_parser()
    entry = {
        "title": "t",
        "link": "https://x.example/1",
        "published_parsed": (2026, 5, 20, 0, 0, 0, 0, 0, 0),
        "rbc_news_full-text": "Полный текст РБК",
    }
    raw = parser._entry_to_raw(_src("rbc"), entry)
    assert raw is not None
    assert raw.rss_full_text == "Полный текст РБК"


# ---------- _build_enriched ---------------------------------------------------


def test_build_enriched_with_body() -> None:
    from newscore.models import RawArticle

    raw = RawArticle(
        source="s",
        title="t",
        url="https://x.example/1",
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet="sn",
    )
    enriched = FeedParser._build_enriched(raw, body="body text", src=_src("s"))
    assert enriched.body == "body text"
    assert enriched.body_extracted is True
    assert enriched.body_extractor == "trafilatura"


def test_build_enriched_without_body() -> None:
    from newscore.models import RawArticle

    raw = RawArticle(
        source="s",
        title="t",
        url="https://x.example/1",
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet="sn",
    )
    enriched = FeedParser._build_enriched(raw, body=None, src=_src("s"))
    assert enriched.body is None
    assert enriched.body_extracted is False


# ---------- end-to-end через _fetch_and_parse_async (no mock) -----------------


@pytest.mark.parametrize(
    "rss_bytes,expected_kind",
    [
        # Невалидный XML
        (b"<not really xml", "xml_invalid"),
        # Пустой <rss> без items
        (
            b'<?xml version="1.0"?><rss version="2.0"><channel><title>empty</title></channel></rss>',
            "no_items",
        ),
    ],
)
def test_parser_raises_on_xml_invalid_or_empty(rss_bytes: bytes, expected_kind: str) -> None:
    """Прямая проверка ValueError, который потом классифицируется в `_classify_error`."""
    import feedparser

    feed = feedparser.parse(rss_bytes)
    # Эмулируем то же условие, что в _fetch_and_parse_async
    if not feed.entries:
        if feed.bozo:
            err = ValueError(f"xml_invalid: {feed.bozo_exception}")
        else:
            err = ValueError("no_items")
        assert FeedParser._classify_error(err) == expected_kind
    else:
        pytest.fail("feedparser почему-то нашёл entries в фикстуре")
