"""Источники и body-экстракторы."""

from typing import Protocol

import httpx

from newscore.models import RawArticle


class BodyExtractor(Protocol):
    name: str

    def extract(self, raw: RawArticle, http: httpx.Client) -> str | None: ...


class RbcNativeExtractor:
    """Берёт <rbc_news:full-text> из RSS, без сетевого вызова."""

    name = "rbc_native"

    def extract(self, raw: RawArticle, http: httpx.Client) -> str | None:
        if raw.rss_full_text and raw.rss_full_text.strip():
            return raw.rss_full_text.strip()
        return None


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


_REGISTRY: dict[str, type] = {
    "rbc_native": RbcNativeExtractor,
    "trafilatura": TrafilaturaExtractor,
}


def build_extractor(name: str) -> BodyExtractor:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"unknown body_extractor: {name}")
    return cls()
