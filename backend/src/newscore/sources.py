"""Источники и body-экстракторы.

Hybrid Protocol (ADR-12): sync `BodyExtractor` для тестов / fallback +
async `AsyncBodyExtractor` для production hot path. Каждый extractor
реализует оба интерфейса.
"""

import asyncio
from typing import Protocol

import httpx

from newscore.models import RawArticle


class BodyExtractor(Protocol):
    """Sync интерфейс — для тестов и потенциального fallback."""

    name: str

    def extract(self, raw: RawArticle, http: httpx.Client) -> str | None: ...


class AsyncBodyExtractor(Protocol):
    """Async интерфейс — production hot path."""

    name: str

    async def aextract(
        self, raw: RawArticle, http: httpx.AsyncClient
    ) -> str | None: ...


class RbcNativeExtractor:
    """Берёт <rbc_news:full-text> из RSS, без сетевого вызова."""

    name = "rbc_native"

    def extract(self, raw: RawArticle, http: httpx.Client) -> str | None:
        if raw.rss_full_text and raw.rss_full_text.strip():
            return raw.rss_full_text.strip()
        return None

    async def aextract(
        self, raw: RawArticle, http: httpx.AsyncClient
    ) -> str | None:
        # Сети нет — оверхеда от async-обёртки никакого.
        return self.extract(raw, None)  # type: ignore[arg-type]


class TrafilaturaExtractor:
    """HTTP GET по URL → trafilatura.extract."""

    name = "trafilatura"

    def extract(self, raw: RawArticle, http: httpx.Client) -> str | None:
        import trafilatura

        try:
            resp = http.get(str(raw.url))
            resp.raise_for_status()
            html = resp.text
        except Exception:
            return None
        body = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        if body and body.strip():
            return body.strip()
        return None

    async def aextract(
        self, raw: RawArticle, http: httpx.AsyncClient
    ) -> str | None:
        import trafilatura

        resp = await http.get(str(raw.url))
        # 4xx — final (paywall / not found), 5xx — пробрасываем вверх
        # (вызывающая сторона решает по retry-политике).
        if resp.status_code >= 500:
            resp.raise_for_status()
        if resp.status_code >= 400:
            return None
        html = resp.text

        body = await asyncio.to_thread(
            trafilatura.extract,
            html,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        if body and body.strip():
            return body.strip()
        return None


_REGISTRY: dict[str, type] = {
    "rbc_native": RbcNativeExtractor,
    "trafilatura": TrafilaturaExtractor,
}


def build_extractor(name: str) -> BodyExtractor:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"unknown body_extractor: {name}")
    return cls()


def build_async_extractor(name: str) -> AsyncBodyExtractor:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"unknown body_extractor: {name}")
    return cls()
