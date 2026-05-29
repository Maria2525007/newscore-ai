"""RSS-fetch, freshness-filter, body extraction.

Async внутри (ADR-13): `collect` остаётся sync-контрактом,
`asyncio.run(_acollect)` — единственная граница.
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
import structlog
from pydantic import ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from newscore.cache import ArticleCache, NullCache
from newscore.config import AppConfig, SourceConfig
from newscore.models import EnrichedArticle, FailedSource, RawArticle
from newscore.sources import AsyncBodyExtractor, build_async_extractor

log = structlog.get_logger(__name__)


@dataclass
class ParseReport:
    articles: list[EnrichedArticle]
    failed_sources: list[FailedSource]
    partial: bool


_TRANSIENT_HTTPX: tuple[type[BaseException], ...] = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
    httpx.ReadError,
)


def _is_transient(e: BaseException) -> bool:
    if isinstance(e, _TRANSIENT_HTTPX):
        return True
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code >= 500
    return False


class FeedParser:
    def __init__(
        self,
        cfg: AppConfig,
        http: httpx.Client | None = None,
        cache: ArticleCache | None = None,
    ) -> None:
        # `http` оставлен в сигнатуре для обратной совместимости (тесты,
        # потенциальный sync fallback). Hot-path использует AsyncClient,
        # создаваемый внутри `_acollect`.
        self.cfg = cfg
        self.http = http
        self.cache = cache or NullCache()

    def collect(
        self, sources: list[SourceConfig], freshness_days: int
    ) -> ParseReport:
        return asyncio.run(self._acollect(sources, freshness_days))

    async def _acollect(
        self, sources: list[SourceConfig], freshness_days: int
    ) -> ParseReport:
        cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)
        limits = httpx.Limits(
            max_connections=self.cfg.fetch_concurrency_total,
            max_keepalive_connections=self.cfg.fetch_concurrency_total,
        )
        async with httpx.AsyncClient(
            headers={"User-Agent": self.cfg.user_agent},
            follow_redirects=True,
            timeout=self.cfg.request_timeout_s,
            limits=limits,
        ) as ahttp:
            sems = {
                s.name: asyncio.Semaphore(self.cfg.fetch_concurrency_per_host)
                for s in sources
            }
            tasks = [
                self._process_source(src, ahttp, sems[src.name], cutoff)
                for src in sources
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles: list[EnrichedArticle] = []
        failed: list[FailedSource] = []
        ok_sources = 0
        for src, res in zip(sources, results, strict=True):
            if isinstance(res, BaseException):
                reason = self._classify_error(res)
                log.warning(
                    "source_failed",
                    source=src.name,
                    optional=src.optional,
                    reason=reason,
                    error=str(res)[:500],
                )
                if not src.optional:
                    failed.append(
                        FailedSource(
                            name=src.name, reason=reason, error=str(res)[:500]
                        )
                    )
                continue
            articles, n_with_body, items_in_feed, items_fresh, dur_ms = res
            all_articles.extend(articles)
            ok_sources += 1
            log.info(
                "source_collected",
                source=src.name,
                items_in_feed=items_in_feed,
                items_fresh=items_fresh,
                items_with_body=n_with_body,
                duration_ms=dur_ms,
            )

        partial = bool(failed) and ok_sources > 0
        return ParseReport(
            articles=all_articles, failed_sources=failed, partial=partial
        )

    async def _process_source(
        self,
        src: SourceConfig,
        ahttp: httpx.AsyncClient,
        sem: asyncio.Semaphore,
        cutoff: datetime,
    ) -> tuple[list[EnrichedArticle], int, int, int, int]:
        t0 = time.time()
        raw_items = await self._fetch_and_parse_async(src, ahttp)
        items_in_feed = len(raw_items)
        fresh = [r for r in raw_items if r.published_at >= cutoff]
        items_fresh = len(fresh)
        enriched = await self._enrich_async(src, fresh, ahttp, sem)
        n_with_body = sum(1 for e in enriched if e.body_extracted)
        dur_ms = int((time.time() - t0) * 1000)
        return enriched, n_with_body, items_in_feed, items_fresh, dur_ms

    async def _fetch_and_parse_async(
        self, src: SourceConfig, ahttp: httpx.AsyncClient
    ) -> list[RawArticle]:
        content = await self._aretry_get_rss(src, ahttp)
        feed = feedparser.parse(content)
        if not feed.entries:
            if feed.bozo:
                raise ValueError(f"xml_invalid: {feed.bozo_exception}")
            raise ValueError("no_items")
        result: list[RawArticle] = []
        for entry in feed.entries:
            raw = self._entry_to_raw(src, entry)
            if raw is not None:
                result.append(raw)
        return result

    async def _aretry_get_rss(
        self, src: SourceConfig, ahttp: httpx.AsyncClient
    ) -> bytes:
        # Feed cache (короткий TTL): на повторных run/refresh не бьём RSS.
        from newscore import redis_cache

        rc = redis_cache.get_cache()
        fkey = redis_cache.feed_key(str(src.rss_url))
        if rc.enabled:
            cached = await asyncio.to_thread(rc.get_bytes, fkey)
            if cached is not None:
                return cached

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.cfg.retry_attempts + 1),
            wait=wait_exponential_jitter(
                initial=self.cfg.retry_backoff_s, max=4.0
            ),
            retry=retry_if_exception(_is_transient),
            reraise=True,
        ):
            with attempt:
                resp = await ahttp.get(
                    str(src.rss_url),
                    headers={
                        "Accept": "application/rss+xml,application/xml,text/xml,*/*"
                    },
                )
                resp.raise_for_status()
                content: bytes = resp.content

        if rc.enabled and content:
            await asyncio.to_thread(
                rc.set_bytes, fkey, content, redis_cache.TTL_FEED
            )
        return content

    async def _enrich_async(
        self,
        src: SourceConfig,
        raw_items: list[RawArticle],
        ahttp: httpx.AsyncClient,
        sem: asyncio.Semaphore,
    ) -> list[EnrichedArticle]:
        extractor: AsyncBodyExtractor = build_async_extractor(src.body_extractor)

        # rbc_native — без сети, не плодим лишних задач
        if src.body_extractor == "rbc_native":
            out: list[EnrichedArticle] = []
            for raw in raw_items:
                body = await extractor.aextract(raw, ahttp)
                out.append(self._build_enriched(raw, body, src))
            return out

        # Body cache: отдельная новость по URL почти не меняется после
        # публикации, а HTTP GET полной страницы + trafilatura.extract —
        # самая дорогая часть parse-фазы. Кэшируем body на TTL_BODY (~24h).
        from newscore import redis_cache

        rc = redis_cache.get_cache()

        async def bound(raw: RawArticle) -> EnrichedArticle:
            bkey = redis_cache.body_key(str(raw.url))
            if rc.enabled:
                cached = await asyncio.to_thread(rc.get_str, bkey)
                if cached is not None:
                    # Пустая строка-маркер = «уже пытались, body нет»
                    # (не долбим paywall/404 повторно весь TTL).
                    return self._build_enriched(raw, cached or None, src)
            async with sem:
                try:
                    body = await extractor.aextract(raw, ahttp)
                except Exception:
                    # одна статья — не блокер, body=None
                    body = None
            if rc.enabled:
                await asyncio.to_thread(
                    rc.set_str, bkey, body or "", redis_cache.TTL_BODY
                )
            return self._build_enriched(raw, body, src)

        results = await asyncio.gather(
            *[bound(r) for r in raw_items], return_exceptions=True
        )
        enriched: list[EnrichedArticle] = []
        for r in results:
            if isinstance(r, BaseException):
                continue
            enriched.append(r)
        return enriched

    @staticmethod
    def _build_enriched(
        raw: RawArticle, body: str | None, src: SourceConfig
    ) -> EnrichedArticle:
        return EnrichedArticle(
            source=raw.source,
            title=raw.title,
            url=raw.url,
            published_at=raw.published_at,
            snippet=raw.snippet,
            body=body,
            body_extracted=body is not None,
            body_extractor=src.body_extractor,
        )

    def _entry_to_raw(
        self, src: SourceConfig, entry: dict
    ) -> RawArticle | None:
        title = (entry.get("title") or "").strip()
        url = (entry.get("link") or "").strip()
        if not title or not url:
            return None
        pub = self._parse_pubdate(entry)
        if pub is None:
            return None
        snippet = entry.get("summary") or entry.get("description") or ""
        if isinstance(snippet, str):
            snippet = snippet[:1000]
        else:
            snippet = ""
        full_text = self._extract_rbc_full_text(entry)
        try:
            return RawArticle(
                source=src.name,
                title=title,
                url=url,
                published_at=pub,
                snippet=snippet,
                rss_full_text=full_text,
            )
        except ValidationError:
            return None

    @staticmethod
    def _parse_pubdate(entry: dict) -> datetime | None:
        for key in ("published_parsed", "updated_parsed"):
            val = entry.get(key)
            if val:
                try:
                    return datetime(*val[:6], tzinfo=timezone.utc)
                except (TypeError, ValueError):
                    continue
        return None

    @staticmethod
    def _extract_rbc_full_text(entry: dict) -> str | None:
        for key in ("rbc_news_full-text", "rbc_news_fulltext", "full-text"):
            val = entry.get(key)
            if val:
                if isinstance(val, dict):
                    val = val.get("value")
                if isinstance(val, str) and val.strip():
                    return val.strip()
        return None

    @staticmethod
    def _classify_error(e: BaseException) -> str:
        if isinstance(e, httpx.TimeoutException):
            return "timeout"
        if isinstance(e, httpx.HTTPStatusError):
            return f"http_{e.response.status_code}"
        if isinstance(e, httpx.HTTPError):
            return "http_error"
        if isinstance(e, asyncio.CancelledError):
            return "cancelled"
        msg = str(e).lower()
        if "xml_invalid" in msg or "bozo" in msg:
            return "xml_invalid"
        if "no_items" in msg:
            return "no_items"
        return "unknown"
