"""Доменные модели. Pure data, без логики."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl


class RawArticle(BaseModel):
    """Сырая запись из RSS-фида до обогащения телом."""

    source: str
    title: str
    url: HttpUrl
    published_at: datetime
    snippet: str = ""
    rss_full_text: str | None = None


class EnrichedArticle(BaseModel):
    """RawArticle + извлечённое тело."""

    source: str
    title: str
    url: HttpUrl
    published_at: datetime
    snippet: str
    body: str | None
    body_extracted: bool
    body_extractor: str


class Match(BaseModel):
    article: EnrichedArticle
    score: float


class FailedSource(BaseModel):
    name: str
    reason: str
    error: str


class RunMeta(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime
    matcher_name: str
    matcher_version: str
    sources_snapshot_at: datetime
    freshness_days: int
    partial: bool
    failed_sources: list[FailedSource]
    reason: Literal["ok", "no_relevant_matches", "all_sources_failed"] | None = None


class BriefingResult(BaseModel):
    """Финальный объект, сериализуется в stdout JSON."""

    query: str
    items: list[Match]
    meta: RunMeta
