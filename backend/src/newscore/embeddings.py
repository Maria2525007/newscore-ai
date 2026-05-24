"""Глобальный кэш sentence-transformers моделей (Step 3).

EmbeddingMatcher и ExtractiveSummarizer делят одну инстанцию e5-base, чтобы
не грузить ~600MB дважды. Кэш ключуется по имени модели.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

_MODEL_CACHE: dict[str, "SentenceTransformer"] = {}


def get_st_model(name: str) -> "SentenceTransformer":
    if name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer

        _MODEL_CACHE[name] = SentenceTransformer(name)
    return _MODEL_CACHE[name]


def clear_cache() -> None:
    """Освободить ссылки на модели (для тестов)."""
    _MODEL_CACHE.clear()
