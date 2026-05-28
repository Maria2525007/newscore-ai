"""Глобальный кэш sentence-transformers моделей (Step 3).

EmbeddingMatcher и ExtractiveSummarizer делят одну инстанцию e5-base, чтобы
не грузить ~600MB дважды. Кэш ключуется по имени модели.

Дополнительно — passage embedding cache (LRU): на повторных запусках темы
тот же корпус re-encoder'ится впустую (~16 мс/doc), поэтому кэшируем
по url. На 1000 articles экономим ~16 секунд на каждом run.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from sentence_transformers import CrossEncoder, SentenceTransformer

_MODEL_CACHE: dict[str, "SentenceTransformer"] = {}
_RERANKER_CACHE: dict[str, "CrossEncoder"] = {}

# Passage embedding cache. key = (model_name, url), value = np.ndarray (unit-norm).
# LRU через OrderedDict.move_to_end на hit.
_PASSAGE_CACHE: OrderedDict[tuple[str, str], "np.ndarray"] = OrderedDict()
_PASSAGE_CACHE_MAX = 50_000  # ≈ 150 MB для e5-base 768-float32


def get_st_model(name: str) -> "SentenceTransformer":
    if name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer

        _MODEL_CACHE[name] = SentenceTransformer(name)
    return _MODEL_CACHE[name]


def get_reranker_model(
    name: str = "BAAI/bge-reranker-v2-m3",
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


def get_cached_passage_emb(model_name: str, url: str):
    """Вернуть закэшированный passage embedding или None."""
    key = (model_name, url)
    emb = _PASSAGE_CACHE.get(key)
    if emb is not None:
        _PASSAGE_CACHE.move_to_end(key)  # LRU bump
    return emb


def cache_passage_emb(model_name: str, url: str, emb) -> None:
    """Сохранить embedding в LRU-кэш; вытеснить старейший при превышении лимита."""
    key = (model_name, url)
    _PASSAGE_CACHE[key] = emb
    _PASSAGE_CACHE.move_to_end(key)
    while len(_PASSAGE_CACHE) > _PASSAGE_CACHE_MAX:
        _PASSAGE_CACHE.popitem(last=False)


def passage_cache_stats() -> dict[str, int]:
    """Размер passage cache (для debug/metrics)."""
    return {"size": len(_PASSAGE_CACHE), "max": _PASSAGE_CACHE_MAX}


def clear_cache() -> None:
    """Освободить ссылки на модели (для тестов)."""
    _MODEL_CACHE.clear()
    _RERANKER_CACHE.clear()
    _PASSAGE_CACHE.clear()
