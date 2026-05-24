"""Доменные модели Step 1."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ThemeStatus = Literal["active", "paused"]
MatcherName = Literal["embedding", "bm25"]


class Theme(BaseModel):
    id: str
    query: str = Field(min_length=1, max_length=500)
    period_seconds: int = Field(ge=60)
    matcher: MatcherName = "embedding"
    top_n: int = Field(default=10, ge=1, le=50)
    days: int = Field(default=7, ge=1, le=30)
    status: ThemeStatus = "active"
    created_at: datetime
    next_run_at: datetime
    last_run_id: str | None = None


class ThemeRun(BaseModel):
    id: str
    theme_id: str
    started_at: datetime
    finished_at: datetime
    matcher_name: str
    matcher_version: str
    partial: bool
    reason: str | None = None
    items_total: int
    items_new: int = 0


class ArticleSnapshot(BaseModel):
    url_hash: str
    theme_id: str
    first_run_id: str
    last_seen_run_id: str
    first_seen_at: datetime
    last_score: float
    payload: dict
