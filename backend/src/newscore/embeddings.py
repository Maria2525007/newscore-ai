"""Глобальный кэш sentence-transformers моделей (Step 3).

EmbeddingMatcher и ExtractiveSummarizer делят одну инстанцию e5-base, чтобы
не грузить ~600MB дважды. Кэш ключуется по имени модели.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder, SentenceTransformer

_MODEL_CACHE: dict[str, "SentenceTransformer"] = {}
_RERANKER_CACHE: dict[str, "CrossEncoder"] = {}


def get_st_model(name: str) -> "SentenceTransformer":
    if name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer

        _MODEL_CACHE[name] = SentenceTransformer(name)
    return _MODEL_CACHE[name]


def get_reranker_model(
    name: str = "BAAI/bge-reranker-base",
    max_length: int = 512,
) -> "CrossEncoder":
    """Lazy-load cross-encoder reranker.

    BAAI/bge-reranker-base: Apache-2.0, 568M, multilingual (100+ языков).
    RusBEIR (Kovalev 2025, doc-001 Table 3): BM25+BGE-reranker +7.71 п.п.
    nDCG@10 avg vs BM25 alone. T²-RAGBench (Akarsu 2026, doc-002 Table I):
    Hybrid+Rerank R@5=0.816 vs Hybrid alone 0.695 (+17.4 п.п.).

    use_fp16=False на CPU (fp16 не даёт speedup на CPU без специальных
    инструкций). max_length=512 — рекомендация авторов модели.
    """
    cache_key = f"{name}|{max_length}"
    if cache_key not in _RERANKER_CACHE:
        from sentence_transformers import CrossEncoder

        _RERANKER_CACHE[cache_key] = CrossEncoder(name, max_length=max_length)
    return _RERANKER_CACHE[cache_key]


def clear_cache() -> None:
    """Освободить ссылки на модели (для тестов)."""
    _MODEL_CACHE.clear()
    _RERANKER_CACHE.clear()
