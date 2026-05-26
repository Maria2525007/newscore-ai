"""Per-package conftest для themes/-tests.

Цель: ADR-25 добавил semantic novelty в ThemeService._upsert_articles, который
дёргает e5-base через get_st_model(). Unit-тесты не должны грузить ~600 MB
модель — подмена через autouse fixture гарантирует быструю/изолированную работу.

Mock возвращает уникальный embedding per title (через hash) — этого достаточно
чтобы legacy-тесты с разными URL'ами не получали false-positive duplicate hit.
"""

from __future__ import annotations

import hashlib
from typing import Iterable

import numpy as np
import pytest


_EMB_DIM = 768


def _stable_unit_emb(text: str, dim: int = _EMB_DIM) -> np.ndarray:
    """Детерминированный unit-vector embedding на основе SHA256."""
    seed_bytes = hashlib.sha256(text.encode("utf-8")).digest()
    # Сид numpy generator на основе хеша — повторяемо.
    rng = np.random.default_rng(
        int.from_bytes(seed_bytes[:8], "little", signed=False)
    )
    v = rng.standard_normal(dim).astype(np.float32)
    n = float(np.linalg.norm(v))
    return v / (n + 1e-12)


class _FakeEmbedModel:
    """Стаб sentence-transformers совместимый с encode(...)."""

    def encode(
        self,
        texts: Iterable[str],
        normalize_embeddings: bool = False,
        show_progress_bar: bool = False,
        batch_size: int = 16,
    ):
        del normalize_embeddings, show_progress_bar, batch_size
        return np.array([_stable_unit_emb(t) for t in texts])


@pytest.fixture(autouse=True)
def _mock_e5_for_theme_tests(monkeypatch):
    """Каждый theme-test получает безопасный fake e5 модель."""
    monkeypatch.setattr(
        "newscore.embeddings.get_st_model",
        lambda _name: _FakeEmbedModel(),
    )
    yield
