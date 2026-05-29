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
_PASSAGE_CACHE_MAX = 200_000  # ≈ 600 MB для e5-base 768-float32 (31 GB RAM в запасе)

# Резолвленный device-синглтон. resolve_device() кэширует сюда, чтобы
# matchers и warmup были консистентны (один и тот же GPU).
_DEVICE: str | None = None


class DeviceUnavailable(RuntimeError):
    """Явно запрошенный device (cuda/mps) недоступен — fail-fast."""


def resolve_device(prefer: str | None = None) -> str:
    """Определить torch device: cuda → mps → cpu, с возможностью override.

    prefer:
      - None / "auto" — автоопределение (cuda если доступна, иначе mps/cpu).
        Молча деградирует до cpu — никогда не падает.
      - "cuda" / "cuda:0" / "mps" — ЯВНЫЙ выбор: если устройство недоступно,
        бросаем DeviceUnavailable (fail-fast, без молчаливого отката на cpu).
      - "cpu" — всегда доступен.
    Override через env NEWSCORE_DEVICE; явный аргумент CLI (prefer) бьёт env.
    """
    global _DEVICE

    # Явный выбор из аргумента имеет приоритет над всем.
    if prefer and prefer != "auto":
        _DEVICE = _validate_device(prefer)
        return _DEVICE

    if _DEVICE is not None:
        return _DEVICE

    import os

    env = os.environ.get("NEWSCORE_DEVICE")
    if env and env != "auto":
        _DEVICE = _validate_device(env)
        return _DEVICE

    import torch

    if torch.cuda.is_available():
        _DEVICE = "cuda"
    elif torch.backends.mps.is_available():
        _DEVICE = "mps"
    else:
        _DEVICE = "cpu"
    return _DEVICE


def _validate_device(dev: str) -> str:
    """Проверить доступность явно запрошенного device; иначе DeviceUnavailable."""
    import torch

    if dev.startswith("cuda"):
        if not torch.cuda.is_available():
            raise DeviceUnavailable(
                f"запрошен device={dev!r}, но CUDA недоступна "
                "(torch.cuda.is_available() == False). Проверь nvidia-smi, "
                "драйвер и что установлен GPU-torch: uv sync --extra cu128. "
                "Для CPU явно укажи --device cpu или --device auto."
            )
        return dev
    if dev == "mps":
        if not torch.backends.mps.is_available():
            raise DeviceUnavailable(
                f"запрошен device={dev!r}, но MPS (Apple Metal) недоступен."
            )
        return dev
    # cpu и любые прочие — пропускаем как есть (torch сам бросит при загрузке).
    return dev


def get_st_model(name: str, device: str | None = None) -> "SentenceTransformer":
    if name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer

        _MODEL_CACHE[name] = SentenceTransformer(
            name, device=resolve_device(device)
        )
    return _MODEL_CACHE[name]


def get_reranker_model(
    name: str = "BAAI/bge-reranker-v2-m3",
    max_length: int = 512,
    device: str | None = None,
    use_fp16: bool | None = None,
) -> "CrossEncoder":
    """Lazy-load cross-encoder reranker.

    BAAI/bge-reranker-v2-m3: Apache-2.0, 568M, multilingual (100+ языков).
    RusBEIR (Kovalev 2025, doc-001 Table 3): BM25+BGE-reranker +7.71 п.п.
    nDCG@10 avg vs BM25 alone. T²-RAGBench (Akarsu 2026, doc-002 Table I):
    Hybrid+Rerank R@5=0.816 vs Hybrid alone 0.695 (+17.4 п.п.).

    fp16: на CUDA даёт ~2× speedup + 2× меньше VRAM (cross-encoder logits
    устойчивы к fp16). На CPU/MPS fp16 не помогает → fp32. use_fp16=None →
    авто (True только на cuda). cross-encoder fp16 безопаснее e5-fp16, т.к.
    выдаёт relevance-logits, а не косинусы между близкими векторами.
    """
    cache_key = f"{name}|{max_length}"
    if cache_key not in _RERANKER_CACHE:
        from sentence_transformers import CrossEncoder

        dev = resolve_device(device)
        if use_fp16 is None:
            use_fp16 = dev.startswith("cuda")

        model_kwargs = None
        if use_fp16:
            import torch

            model_kwargs = {"torch_dtype": torch.float16}

        _RERANKER_CACHE[cache_key] = CrossEncoder(
            name,
            max_length=max_length,
            device=dev,
            model_kwargs=model_kwargs,
        )
    return _RERANKER_CACHE[cache_key]


# e5-base dim — для валидации Redis-blob'ов. Mismatch → переэнкод.
_E5_DIM = 768


def get_cached_passage_emb(model_name: str, key_id: str):
    """Вернуть passage embedding из L1 (in-memory) или L2 (Redis).

    key_id — content_hash статьи (не url): меняется при изменении текста,
    что даёт корректную инвалидацию. L1-miss проверяет L2-Redis и поднимает
    найденное в L1 (read-through).
    """
    key = (model_name, key_id)
    emb = _PASSAGE_CACHE.get(key)
    if emb is not None:
        _PASSAGE_CACHE.move_to_end(key)  # LRU bump
        return emb

    # L2: Redis (переживает рестарт, шарится между процессами).
    from newscore import redis_cache

    rc = redis_cache.get_cache()
    if rc.enabled:
        rkey = redis_cache.emb_key(model_name, key_id)
        emb = rc.get_emb(rkey, _E5_DIM)
        if emb is not None:
            # поднимаем в L1, но без повторной записи в L2
            _PASSAGE_CACHE[key] = emb
            _PASSAGE_CACHE.move_to_end(key)
            while len(_PASSAGE_CACHE) > _PASSAGE_CACHE_MAX:
                _PASSAGE_CACHE.popitem(last=False)
            return emb
    return None


def cache_passage_emb(model_name: str, key_id: str, emb) -> None:
    """Записать embedding в L1 (in-memory LRU) + L2 (Redis, если включён)."""
    key = (model_name, key_id)
    _PASSAGE_CACHE[key] = emb
    _PASSAGE_CACHE.move_to_end(key)
    while len(_PASSAGE_CACHE) > _PASSAGE_CACHE_MAX:
        _PASSAGE_CACHE.popitem(last=False)

    from newscore import redis_cache

    rc = redis_cache.get_cache()
    if rc.enabled:
        rkey = redis_cache.emb_key(model_name, key_id)
        rc.set_emb(rkey, emb, redis_cache.TTL_EMB)


def passage_cache_stats() -> dict[str, int]:
    """Размер passage cache (для debug/metrics)."""
    return {"size": len(_PASSAGE_CACHE), "max": _PASSAGE_CACHE_MAX}


def clear_cache() -> None:
    """Освободить ссылки на модели (для тестов)."""
    _MODEL_CACHE.clear()
    _RERANKER_CACHE.clear()
    _PASSAGE_CACHE.clear()
