"""Опциональный файловый кэш статей (Should)."""

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel


class CachedArticle(BaseModel):
    url: str
    fetched_at: str
    html_or_body: str
    status: int


class ArticleCache(Protocol):
    def get(self, url: str) -> CachedArticle | None: ...
    def put(self, url: str, payload: CachedArticle) -> None: ...


class NullCache:
    def get(self, url: str) -> CachedArticle | None:
        return None

    def put(self, url: str, payload: CachedArticle) -> None:
        return None


class FileCache:
    def __init__(self, cache_dir: Path, ttl_hours: int = 6) -> None:
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours

    def get(self, url: str) -> CachedArticle | None:
        raise NotImplementedError

    def put(self, url: str, payload: CachedArticle) -> None:
        raise NotImplementedError
