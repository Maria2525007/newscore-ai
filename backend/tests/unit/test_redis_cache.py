"""Тесты RedisCache: graceful fallback + типизированные helpers.

Используем fakeredis для проверки логики без реального сервера.
Отдельно проверяем что без Redis всё деградирует в no-op.
"""

from __future__ import annotations

import numpy as np
import pytest

from newscore import redis_cache
from newscore.redis_cache import RedisCache, content_hash


@pytest.fixture
def fake_cache(monkeypatch) -> RedisCache:
    """RedisCache поверх fakeredis (in-memory, без сервера)."""
    import fakeredis

    fake = fakeredis.FakeRedis()

    cache = RedisCache.__new__(RedisCache)
    cache._client = fake
    cache._enabled = True
    cache._url = "redis://fake"
    return cache


# ---- graceful fallback (no Redis) --------------------------------------


def test_disabled_when_no_url(monkeypatch) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)
    cache = RedisCache()
    assert cache.enabled is False
    # все операции — no-op, не падают
    assert cache.get_bytes("k") is None
    cache.set_bytes("k", b"v", ttl=10)
    assert cache.get_float("k") is None
    assert cache.get_str("k") is None
    assert cache.mget_bytes(["a", "b"]) == [None, None]


def test_disabled_on_bad_url(monkeypatch) -> None:
    # Несуществующий сервер → ping падает → disabled, без исключения наружу.
    cache = RedisCache(url="redis://127.0.0.1:6399/0")
    assert cache.enabled is False
    assert cache.get_bytes("x") is None


# ---- bytes / str / float roundtrip -------------------------------------


def test_bytes_roundtrip(fake_cache: RedisCache) -> None:
    fake_cache.set_bytes("k1", b"hello", ttl=60)
    assert fake_cache.get_bytes("k1") == b"hello"


def test_str_roundtrip(fake_cache: RedisCache) -> None:
    fake_cache.set_str("k2", "привет", ttl=60)
    assert fake_cache.get_str("k2") == "привет"


def test_float_roundtrip(fake_cache: RedisCache) -> None:
    fake_cache.set_float("score", 0.8137, ttl=60)
    got = fake_cache.get_float("score")
    assert got is not None
    assert got == pytest.approx(0.8137, abs=1e-6)


def test_get_missing_returns_none(fake_cache: RedisCache) -> None:
    assert fake_cache.get_bytes("nope") is None
    assert fake_cache.get_float("nope") is None
    assert fake_cache.get_str("nope") is None


def test_float_wrong_size_returns_none(fake_cache: RedisCache) -> None:
    fake_cache.set_bytes("bad", b"not4bytes", ttl=60)
    assert fake_cache.get_float("bad") is None


# ---- embedding helpers --------------------------------------------------


def test_emb_roundtrip(fake_cache: RedisCache) -> None:
    emb = np.random.default_rng(0).standard_normal(768).astype(np.float32)
    fake_cache.set_emb("e1", emb, ttl=60)
    got = fake_cache.get_emb("e1", dim=768)
    assert got is not None
    np.testing.assert_array_almost_equal(got, emb, decimal=5)


def test_emb_wrong_dim_returns_none(fake_cache: RedisCache) -> None:
    emb = np.zeros(384, dtype=np.float32)
    fake_cache.set_emb("e2", emb, ttl=60)
    assert fake_cache.get_emb("e2", dim=768) is None


def test_emb_missing_returns_none(fake_cache: RedisCache) -> None:
    assert fake_cache.get_emb("absent", dim=768) is None


# ---- mget batch ---------------------------------------------------------


def test_mget_mixed_hits(fake_cache: RedisCache) -> None:
    fake_cache.set_bytes("a", b"AA", ttl=60)
    fake_cache.set_bytes("c", b"CC", ttl=60)
    got = fake_cache.mget_bytes(["a", "b", "c"])
    assert got[0] == b"AA"
    assert got[1] is None
    assert got[2] == b"CC"


def test_mget_empty(fake_cache: RedisCache) -> None:
    assert fake_cache.mget_bytes([]) == []


# ---- content_hash -------------------------------------------------------


def test_content_hash_stable() -> None:
    h1 = content_hash("Заголовок", "тело статьи", "сниппет")
    h2 = content_hash("Заголовок", "тело статьи", "сниппет")
    assert h1 == h2
    assert len(h1) == 40  # sha1 hex


def test_content_hash_changes_with_body() -> None:
    h1 = content_hash("T", "версия 1")
    h2 = content_hash("T", "версия 2")
    assert h1 != h2


def test_content_hash_none_body() -> None:
    # None body не должен падать
    h = content_hash("T", None)
    assert len(h) == 40


# ---- key namespacing / redaction ---------------------------------------


def test_keys_namespaced(fake_cache: RedisCache) -> None:
    fake_cache.set_bytes("mykey", b"v", ttl=60)
    # ключ должен быть с префиксом nc:
    raw_keys = [k.decode() for k in fake_cache._client.keys("*")]
    assert any(k == "nc:mykey" for k in raw_keys)


def test_url_redaction() -> None:
    from newscore.redis_cache import _redact

    assert _redact("redis://user:secret@host:6379/0") == "redis://***@host:6379/0"
    assert _redact("redis://localhost:6379") == "redis://localhost:6379"


# ---- singleton ----------------------------------------------------------


def test_singleton_override_and_reset() -> None:
    custom = RedisCache.__new__(RedisCache)
    custom._enabled = False
    custom._client = None
    custom._url = None
    redis_cache.set_cache(custom)
    assert redis_cache.get_cache() is custom
    redis_cache.reset_cache()
    # после reset — новый singleton (disabled, т.к. без REDIS_URL в тестах)
    fresh = redis_cache.get_cache()
    assert fresh is not custom
    redis_cache.reset_cache()


# ---- embedding L1+L2 integration (embeddings.py) -----------------------


def test_passage_emb_l2_redis_backing(fake_cache: RedisCache) -> None:
    """cache_passage_emb пишет в L1+L2; после очистки L1 — read-through из L2."""
    from newscore import embeddings, redis_cache

    redis_cache.set_cache(fake_cache)
    embeddings.clear_cache()  # очистить L1
    try:
        emb = np.random.default_rng(1).standard_normal(768).astype(np.float32)
        embeddings.cache_passage_emb("e5", "chash_abc", emb)

        # L1 hit
        got1 = embeddings.get_cached_passage_emb("e5", "chash_abc")
        assert got1 is not None
        np.testing.assert_array_almost_equal(got1, emb, decimal=5)

        # очистить только L1 → должно подняться из L2 (Redis)
        embeddings._PASSAGE_CACHE.clear()
        got2 = embeddings.get_cached_passage_emb("e5", "chash_abc")
        assert got2 is not None
        np.testing.assert_array_almost_equal(got2, emb, decimal=5)
        # и снова осесть в L1
        assert ("e5", "chash_abc") in embeddings._PASSAGE_CACHE
    finally:
        embeddings.clear_cache()
        redis_cache.reset_cache()


def test_passage_emb_miss_returns_none(fake_cache: RedisCache) -> None:
    from newscore import embeddings, redis_cache

    redis_cache.set_cache(fake_cache)
    embeddings.clear_cache()
    try:
        assert embeddings.get_cached_passage_emb("e5", "absent") is None
    finally:
        embeddings.clear_cache()
        redis_cache.reset_cache()
