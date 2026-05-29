"""Опциональный Redis-кэш с graceful fallback (Step 2+ perf).

Дизайн:
- Активируется только при наличии env `REDIS_URL` (или явного `--redis-url`).
- При недоступности сервера (нет соединения, таймаут) — все операции no-op,
  система работает как раньше. Это значит: тесты и dev без Redis не ломаются,
  а на сервере с Redis получаем многоуровневое ускорение.
- Один синхронный клиент (redis-py). Redis обычно на localhost → latency
  <1ms, блокировка async event-loop в parser пренебрежимо мала; где важно —
  оборачиваем в asyncio.to_thread.

Уровни кэша (namespaced ключи):
  nc:body:{sha1(url)}                       — extracted article body (TTL ~24h)
  nc:feed:{sha1(rss_url)}                   — raw RSS bytes (TTL ~90s)
  nc:emb:{model}:{sha1(text)}               — passage embedding float32 (TTL ~24h)
  nc:rr:{model}:{sha1(q)}:{sha1(passage)}   — rerank score (TTL ~6h)
  nc:brief:{sha1(q)}:{matcher}:{days}       — full BriefingResult JSON (TTL ~3m)
"""

from __future__ import annotations

import hashlib
import os
import struct
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    import numpy as np
    import redis as redis_lib

log = structlog.get_logger(__name__)

# TTL-константы (секунды). «Средне-агрессивно»: тяжёлые неизменяемые
# артефакты живут долго, изменчивые (feed/result) — коротко.
TTL_BODY = 24 * 3600
TTL_FEED = 90
TTL_EMB = 24 * 3600
TTL_RERANK = 6 * 3600
TTL_BRIEF = 180

_KEY_PREFIX = "nc:"


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def content_hash(title: str, body: str | None, snippet: str = "") -> str:
    """Стабильный хэш контента статьи для cache-инвалидации.

    Если текст статьи изменился — хэш меняется → новый ключ → пересчёт.
    Если не изменился — тот же ключ → reuse кэшированного результата.
    """
    payload = f"{title}\x00{body or ''}\x00{snippet or ''}"
    return _sha1(payload)


# ---- key builders (единый источник правды для namespacing) -------------


def body_key(url: str) -> str:
    return f"body:{_sha1(url)}"


def feed_key(rss_url: str) -> str:
    return f"feed:{_sha1(rss_url)}"


def emb_key(model: str, text: str) -> str:
    return f"emb:{model}:{_sha1(text)}"


def rerank_key(model: str, query: str, passage: str) -> str:
    return f"rr:{model}:{_sha1(query)}:{_sha1(passage)}"


def brief_key(query: str, matcher: str, days: int, top_n: int) -> str:
    return f"brief:{matcher}:{days}:{top_n}:{_sha1(query)}"


class RedisCache:
    """Тонкая обёртка над redis-py с graceful fallback на no-op."""

    def __init__(self, url: str | None = None) -> None:
        self._client: "redis_lib.Redis | None" = None
        self._enabled = False
        self._url = url or os.environ.get("REDIS_URL")
        if self._url:
            self._connect()

    def _connect(self) -> None:
        try:
            import redis as redis_lib

            client = redis_lib.Redis.from_url(
                self._url,
                socket_connect_timeout=1.0,
                socket_timeout=2.0,
                retry_on_timeout=False,
                health_check_interval=30,
            )
            client.ping()
            self._client = client
            self._enabled = True
            log.info("redis_cache_enabled", url=_redact(self._url))
        except Exception as exc:  # noqa: BLE001
            self._client = None
            self._enabled = False
            log.warning(
                "redis_cache_disabled",
                reason=type(exc).__name__,
                detail=str(exc)[:200],
            )

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ---- low-level (graceful: любая ошибка → None / no-op) -------------

    def get_bytes(self, key: str) -> bytes | None:
        if not self._enabled:
            return None
        try:
            return self._client.get(_KEY_PREFIX + key)  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            return None

    def set_bytes(self, key: str, value: bytes, ttl: int) -> None:
        if not self._enabled:
            return
        try:
            self._client.set(_KEY_PREFIX + key, value, ex=ttl)  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            pass

    def get_str(self, key: str) -> str | None:
        b = self.get_bytes(key)
        return b.decode("utf-8") if b is not None else None

    def set_str(self, key: str, value: str, ttl: int) -> None:
        self.set_bytes(key, value.encode("utf-8"), ttl)

    def get_float(self, key: str) -> float | None:
        b = self.get_bytes(key)
        if b is None or len(b) != 4:
            return None
        try:
            return struct.unpack("f", b)[0]
        except struct.error:
            return None

    def set_float(self, key: str, value: float, ttl: int) -> None:
        self.set_bytes(key, struct.pack("f", value), ttl)

    # ---- numpy embedding helpers ---------------------------------------

    def get_emb(self, key: str, dim: int) -> "np.ndarray | None":
        b = self.get_bytes(key)
        if b is None:
            return None
        import numpy as np

        arr = np.frombuffer(b, dtype=np.float32)
        if arr.shape != (dim,):
            return None
        return arr

    def set_emb(self, key: str, emb: "np.ndarray", ttl: int) -> None:
        import numpy as np

        arr = np.ascontiguousarray(emb, dtype=np.float32)
        self.set_bytes(key, arr.tobytes(), ttl)

    # ---- mget (batch) для embeddings ----------------------------------

    def mget_bytes(self, keys: list[str]) -> list[bytes | None]:
        if not self._enabled or not keys:
            return [None] * len(keys)
        try:
            return self._client.mget(  # type: ignore[union-attr]
                [_KEY_PREFIX + k for k in keys]
            )
        except Exception:  # noqa: BLE001
            return [None] * len(keys)


def _redact(url: str) -> str:
    """Скрыть пароль в redis://user:pass@host из логов."""
    if "@" in url and "://" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            _, host = rest.rsplit("@", 1)
            return f"{scheme}://***@{host}"
    return url


# ---- module-level singleton --------------------------------------------

_CACHE: RedisCache | None = None


def get_cache() -> RedisCache:
    """Глобальный singleton; ленивая инициализация по REDIS_URL."""
    global _CACHE
    if _CACHE is None:
        _CACHE = RedisCache()
    return _CACHE


def set_cache(cache: RedisCache | None) -> None:
    """Override singleton (для тестов / явной конфигурации)."""
    global _CACHE
    _CACHE = cache


def reset_cache() -> None:
    global _CACHE
    _CACHE = None
