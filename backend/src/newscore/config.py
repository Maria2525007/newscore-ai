"""Загрузка и валидация sources.yaml."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, HttpUrl


class SourceConfig(BaseModel):
    name: str
    rss_url: HttpUrl
    body_extractor: Literal["rbc_native", "trafilatura"]
    optional: bool = False


class AppConfig(BaseModel):
    sources: list[SourceConfig]
    freshness_days: int = 7
    top_n: int = 10
    user_agent: str = "NewsCoreAI/0.1 (+briefing)"
    request_timeout_s: float = 15.0
    cache_dir: Path | None = None


def load_config(path: Path) -> AppConfig:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        raise ValueError(f"empty config: {path}")
    if not data.get("sources"):
        raise ValueError(f"no sources configured in: {path}")
    return AppConfig.model_validate(data)
