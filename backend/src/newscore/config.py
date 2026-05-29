"""Загрузка и валидация sources.yaml."""

import os
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
    # async fetch knobs (ADR-14, ADR-15). Дефолты подняты под 8-ядерный
    # сервер: fetch — I/O-bound (httpx async), таски дешёвые, поэтому
    # широкий параллелизм безопасен и кратно ускоряет parse-фазу. Сам
    # trafilatura-parse уже выносится в thread-pool (asyncio.to_thread).
    fetch_concurrency_per_host: int = Field(default=10, ge=1)
    fetch_concurrency_total: int = Field(default=64, ge=1)
    retry_attempts: int = Field(default=2, ge=0)
    retry_backoff_s: float = Field(default=0.5, gt=0)


def _env_int(name: str, default: int | None) -> int | None:
    """Прочитать int из env; None/мусор → default."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def load_config(path: Path) -> AppConfig:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        raise ValueError(f"empty config: {path}")
    if not data.get("sources"):
        raise ValueError(f"no sources configured in: {path}")
    cfg = AppConfig.model_validate(data)

    # Env-override параллелизма без правки YAML (удобно для разных машин).
    total = _env_int("NEWSCORE_FETCH_TOTAL", None)
    per_host = _env_int("NEWSCORE_FETCH_PER_HOST", None)
    if total is not None and total >= 1:
        cfg.fetch_concurrency_total = total
    if per_host is not None and per_host >= 1:
        cfg.fetch_concurrency_per_host = per_host
    return cfg
