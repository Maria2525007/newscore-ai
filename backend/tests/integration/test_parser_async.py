"""Integration-тесты async FeedParser.collect через respx-моки.

Тесты вызывают sync-контракт `collect()` — он внутри запускает `asyncio.run`.
Не требует pytest-asyncio.
"""

from datetime import datetime, timezone

import httpx
import pytest
import respx

from newscore.config import AppConfig, SourceConfig
from newscore.parser import FeedParser


def _src(
    name: str,
    rss_url: str,
    body_extractor: str = "trafilatura",
    optional: bool = False,
) -> SourceConfig:
    return SourceConfig(
        name=name,
        rss_url=rss_url,
        body_extractor=body_extractor,
        optional=optional,
    )


def _now_rfc822() -> str:
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def _item(title: str, link: str, pubdate: str | None = None) -> str:
    return (
        f"<item>"
        f"<title>{title}</title>"
        f"<link>{link}</link>"
        f"<pubDate>{pubdate or _now_rfc822()}</pubDate>"
        f"<description>desc</description>"
        f"</item>"
    )


def _rss(items: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<rss version="2.0"><channel><title>Test</title>'
        f"{items}"
        "</channel></rss>"
    ).encode("utf-8")


def _make_cfg(sources: list[SourceConfig]) -> AppConfig:
    return AppConfig(
        sources=sources,
        freshness_days=7,
        fetch_concurrency_per_host=3,
        fetch_concurrency_total=10,
        retry_attempts=2,
        retry_backoff_s=0.01,
        request_timeout_s=5.0,
    )


HTML_OK = (
    "<html><body><article><p>Полный текст статьи. "
    "Тут много содержания о финансах и экономике.</p></article></body></html>"
)


@respx.mock
def test_two_sources_ok() -> None:
    sources = [
        _src("a", "https://a.example/rss"),
        _src("b", "https://b.example/rss"),
    ]
    respx.get("https://a.example/rss").mock(
        return_value=httpx.Response(
            200, content=_rss(_item("Курс доллара", "https://a.example/1"))
        )
    )
    respx.get("https://b.example/rss").mock(
        return_value=httpx.Response(
            200, content=_rss(_item("Ставка ЦБ", "https://b.example/2"))
        )
    )
    respx.get("https://a.example/1").mock(
        return_value=httpx.Response(200, text=HTML_OK)
    )
    respx.get("https://b.example/2").mock(
        return_value=httpx.Response(200, text=HTML_OK)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert len(report.articles) == 2
    assert report.partial is False
    assert report.failed_sources == []
    titles = {a.title for a in report.articles}
    assert titles == {"Курс доллара", "Ставка ЦБ"}


@respx.mock
def test_one_source_503_after_retries_marks_partial() -> None:
    sources = [
        _src("a", "https://a.example/rss"),
        _src("b", "https://b.example/rss"),
    ]
    respx.get("https://a.example/rss").mock(
        return_value=httpx.Response(
            200, content=_rss(_item("Item", "https://a.example/1"))
        )
    )
    respx.get("https://a.example/1").mock(
        return_value=httpx.Response(200, text=HTML_OK)
    )
    respx.get("https://b.example/rss").mock(
        return_value=httpx.Response(503)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert len(report.articles) == 1
    assert report.partial is True
    assert len(report.failed_sources) == 1
    assert report.failed_sources[0].name == "b"
    assert report.failed_sources[0].reason == "http_503"


@respx.mock
def test_optional_source_failure_does_not_mark_partial() -> None:
    sources = [
        _src("ok", "https://ok.example/rss"),
        _src("opt", "https://opt.example/rss", optional=True),
    ]
    respx.get("https://ok.example/rss").mock(
        return_value=httpx.Response(
            200, content=_rss(_item("Item", "https://ok.example/1"))
        )
    )
    respx.get("https://ok.example/1").mock(
        return_value=httpx.Response(200, text=HTML_OK)
    )
    respx.get("https://opt.example/rss").mock(
        return_value=httpx.Response(503)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert len(report.articles) == 1
    assert report.partial is False
    assert report.failed_sources == []


@respx.mock
def test_retry_succeeds_on_second_attempt() -> None:
    sources = [_src("a", "https://a.example/rss")]
    route = respx.get("https://a.example/rss").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(
                200, content=_rss(_item("Item", "https://a.example/1"))
            ),
        ]
    )
    respx.get("https://a.example/1").mock(
        return_value=httpx.Response(200, text=HTML_OK)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert len(report.articles) == 1
    assert report.partial is False
    assert route.call_count == 2


@respx.mock
def test_no_retry_on_404() -> None:
    sources = [_src("a", "https://a.example/rss")]
    route = respx.get("https://a.example/rss").mock(
        return_value=httpx.Response(404)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert report.articles == []
    assert len(report.failed_sources) == 1
    assert report.failed_sources[0].reason == "http_404"
    assert route.call_count == 1


@respx.mock
def test_article_404_keeps_article_without_body() -> None:
    sources = [_src("a", "https://a.example/rss")]
    respx.get("https://a.example/rss").mock(
        return_value=httpx.Response(
            200, content=_rss(_item("Item", "https://a.example/1"))
        )
    )
    respx.get("https://a.example/1").mock(
        return_value=httpx.Response(404)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert len(report.articles) == 1
    assert report.articles[0].body is None
    assert report.articles[0].body_extracted is False


@respx.mock
def test_rbc_native_does_not_fetch_article_url() -> None:
    sources = [_src("rbc", "https://rbc.example/rss", body_extractor="rbc_native")]
    rss = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<rss version="2.0" xmlns:rbc_news="http://rbc.ru/news">'
        "<channel><title>Test</title>"
        "<item>"
        "<title>Курс доллара</title>"
        "<link>https://rbc.example/article1</link>"
        f"<pubDate>{_now_rfc822()}</pubDate>"
        "<description>Short</description>"
        "<rbc_news:full-text>Полный текст из RSS.</rbc_news:full-text>"
        "</item></channel></rss>"
    ).encode()
    respx.get("https://rbc.example/rss").mock(
        return_value=httpx.Response(200, content=rss)
    )

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert len(report.articles) == 1
    assert report.articles[0].body_extracted is True
    assert "Полный текст из RSS" in report.articles[0].body


@respx.mock
def test_all_sources_fail_returns_empty_corpus() -> None:
    sources = [
        _src("a", "https://a.example/rss"),
        _src("b", "https://b.example/rss"),
    ]
    respx.get("https://a.example/rss").mock(return_value=httpx.Response(503))
    respx.get("https://b.example/rss").mock(return_value=httpx.Response(503))

    report = FeedParser(_make_cfg(sources)).collect(sources, freshness_days=7)
    assert report.articles == []
    assert len(report.failed_sources) == 2
    # partial=True iff some succeeded; здесь ноль успехов → False
    assert report.partial is False


@respx.mock
def test_body_and_feed_cache_skip_repeat_http(monkeypatch) -> None:
    """Второй collect с тем же Redis-кэшем не делает HTTP (feed+body из кэша)."""
    import fakeredis

    from newscore import redis_cache

    fake = redis_cache.RedisCache.__new__(redis_cache.RedisCache)
    fake._client = fakeredis.FakeRedis()
    fake._enabled = True
    fake._url = "redis://fake"
    redis_cache.set_cache(fake)
    try:
        sources = [_src("a", "https://a.example/rss")]
        rss_route = respx.get("https://a.example/rss").mock(
            return_value=httpx.Response(
                200, content=_rss(_item("Новость", "https://a.example/news/1"))
            )
        )
        body_route = respx.get("https://a.example/news/1").mock(
            return_value=httpx.Response(200, text=HTML_OK)
        )

        cfg = _make_cfg(sources)
        # 1-й прогон — оба endpoint'а вызываются, заполняем кэш.
        r1 = FeedParser(cfg).collect(sources, freshness_days=7)
        assert len(r1.articles) == 1
        assert r1.articles[0].body_extracted is True
        assert rss_route.call_count == 1
        assert body_route.call_count == 1

        # 2-й прогон — feed + body уже в кэше → HTTP не дёргается повторно.
        r2 = FeedParser(cfg).collect(sources, freshness_days=7)
        assert len(r2.articles) == 1
        assert r2.articles[0].body_extracted is True
        assert rss_route.call_count == 1  # не вырос
        assert body_route.call_count == 1  # не вырос
    finally:
        redis_cache.reset_cache()


@respx.mock
def test_body_cache_negative_marker_no_refetch(monkeypatch) -> None:
    """Если body не извлёкся (paywall/404) — маркер не даёт долбить повторно."""
    import fakeredis

    from newscore import redis_cache

    fake = redis_cache.RedisCache.__new__(redis_cache.RedisCache)
    fake._client = fakeredis.FakeRedis()
    fake._enabled = True
    fake._url = "redis://fake"
    redis_cache.set_cache(fake)
    try:
        sources = [_src("a", "https://a.example/rss")]
        respx.get("https://a.example/rss").mock(
            return_value=httpx.Response(
                200, content=_rss(_item("Новость", "https://a.example/news/1"))
            )
        )
        body_route = respx.get("https://a.example/news/1").mock(
            return_value=httpx.Response(404)
        )

        cfg = _make_cfg(sources)
        r1 = FeedParser(cfg).collect(sources, freshness_days=7)
        assert r1.articles[0].body_extracted is False
        assert body_route.call_count == 1

        r2 = FeedParser(cfg).collect(sources, freshness_days=7)
        assert r2.articles[0].body_extracted is False
        # негативный маркер в кэше → повторного GET статьи нет
        assert body_route.call_count == 1
    finally:
        redis_cache.reset_cache()
