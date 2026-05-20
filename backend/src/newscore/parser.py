"""RSS-fetch, freshness-filter, body extraction."""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
import structlog
from pydantic import ValidationError

from newscore.cache import ArticleCache, NullCache
from newscore.config import AppConfig, SourceConfig
from newscore.models import EnrichedArticle, FailedSource, RawArticle
from newscore.sources import build_extractor

log = structlog.get_logger(__name__)


@dataclass
class ParseReport:
    articles: list[EnrichedArticle]
    failed_sources: list[FailedSource]
    partial: bool


class FeedParser:
    def __init__(
        self,
        cfg: AppConfig,
        http: httpx.Client,
        cache: ArticleCache | None = None,
    ) -> None:
        self.cfg = cfg
        self.http = http
        self.cache = cache or NullCache()

    def collect(
        self, sources: list[SourceConfig], freshness_days: int
    ) -> ParseReport:
        cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)
        all_articles: list[EnrichedArticle] = []
        failed: list[FailedSource] = []
        ok_sources = 0

        for src in sources:
            t0 = time.time()
            try:
                raw_items = self._fetch_and_parse(src)
                fresh = [r for r in raw_items if r.published_at >= cutoff]
                enriched = self._enrich(src, fresh)
                all_articles.extend(enriched)
                ok_sources += 1
                log.info(
                    "source_collected",
                    source=src.name,
                    items_in_feed=len(raw_items),
                    items_fresh=len(fresh),
                    items_with_body=sum(1 for e in enriched if e.body_extracted),
                    duration_ms=int((time.time() - t0) * 1000),
                )
            except Exception as e:
                reason = self._classify_error(e)
                log.warning(
                    "source_failed",
                    source=src.name,
                    optional=src.optional,
                    reason=reason,
                    error=str(e)[:500],
                )
                if not src.optional:
                    failed.append(
                        FailedSource(
                            name=src.name, reason=reason, error=str(e)[:500]
                        )
                    )

        partial = bool(failed) and ok_sources > 0
        return ParseReport(
            articles=all_articles, failed_sources=failed, partial=partial
        )

    def _fetch_and_parse(self, src: SourceConfig) -> list[RawArticle]:
        resp = self.http.get(
            str(src.rss_url),
            headers={"Accept": "application/rss+xml,application/xml,text/xml,*/*"},
            timeout=self.cfg.request_timeout_s,
        )
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
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
        snippet = (entry.get("summary") or entry.get("description") or "")
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
        # feedparser нормализует <rbc_news:full-text> в ключ rbc_news_full-text.
        # Для надёжности пробуем варианты.
        for key in ("rbc_news_full-text", "rbc_news_fulltext", "full-text"):
            val = entry.get(key)
            if val:
                if isinstance(val, dict):
                    val = val.get("value")
                if isinstance(val, str) and val.strip():
                    return val.strip()
        return None

    def _enrich(
        self, src: SourceConfig, raw_items: list[RawArticle]
    ) -> list[EnrichedArticle]:
        extractor = build_extractor(src.body_extractor)
        enriched: list[EnrichedArticle] = []
        for raw in raw_items:
            body = extractor.extract(raw, self.http)
            enriched.append(
                EnrichedArticle(
                    source=raw.source,
                    title=raw.title,
                    url=raw.url,
                    published_at=raw.published_at,
                    snippet=raw.snippet,
                    body=body,
                    body_extracted=body is not None,
                    body_extractor=src.body_extractor,
                )
            )
        return enriched

    @staticmethod
    def _classify_error(e: Exception) -> str:
        if isinstance(e, httpx.TimeoutException):
            return "timeout"
        if isinstance(e, httpx.HTTPStatusError):
            return f"http_{e.response.status_code}"
        if isinstance(e, httpx.HTTPError):
            return "http_error"
        msg = str(e).lower()
        if "xml_invalid" in msg or "bozo" in msg:
            return "xml_invalid"
        if "no_items" in msg:
            return "no_items"
        return "unknown"
