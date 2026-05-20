"""Загрузка и валидация sources.yaml."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, HttpUrl


class SourceConfig(BaseModel):
    name: str
    rss_url: HttpUrl
    body_extractor: Literal["rbc_native", "trafilatura"]
    optional: bool = False


class AppConfig(BaseModel):
    sources: list[SourceConfig]
    freshness_days: int = Field(default=7, ge=1)
    top_n: int = Field(default=10, ge=1)
    user_agent: str = "NewsCoreAI/0.1 (+briefing)"
    request_timeout_s: float = Field(default=15.0, gt=0)
    cache_dir: Path | None = None
    # async fetch knobs (ADR-14, ADR-15)
    fetch_concurrency_per_host: int = Field(default=5, ge=1)
    fetch_concurrency_total: int = Field(default=20, ge=1)
    retry_attempts: int = Field(default=2, ge=0)
    retry_backoff_s: float = Field(default=0.5, gt=0)


def load_config(path: Path) -> AppConfig:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        raise ValueError(f"empty config: {path}")
    if not data.get("sources"):
        raise ValueError(f"no sources configured in: {path}")
    return AppConfig.model_validate(data)
