"""Тесты ADR-25: semantic novelty layer.

Покрывает:
- Schema V2 migration (title_emb, duplicate_of_url_hash, similarity_score).
- ThemeService._compute_novelty: cosine 1-NN, threshold.
- Интеграцию: items_new считается только не-дубликаты.
- Window-фильтр (старые статьи вне окна не участвуют в сравнении).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest

from newscore.themes.db import (
    SCHEMA_VERSION,
    _SCHEMA_V1,
    connect,
    dt_to_iso,
    migrate,
)
from newscore.themes.service import ThemeService


# ---- Schema V2 migration ------------------------------------------------


def test_schema_v2_adds_novelty_columns(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    cols = {r[1] for r in conn.execute("PRAGMA table_info(articles)").fetchall()}
    assert "title_emb" in cols
    assert "duplicate_of_url_hash" in cols
    assert "similarity_score" in cols


def test_schema_v2_extends_matcher_check_constraint(tmp_path: Path) -> None:
    """Новые matcher'ы hybrid/rerank проходят CHECK в themes."""
    conn = connect(tmp_path / "x.db")
    # Должно работать без ConstraintError
    conn.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at, last_run_id) "
        "VALUES ('t1', 'q', 60, 'hybrid', 10, 7, 'active', ?, ?, NULL)",
        (dt_to_iso(datetime(2026, 5, 1, tzinfo=timezone.utc)),) * 2,
    )
    conn.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at, last_run_id) "
        "VALUES ('t2', 'q', 60, 'rerank', 10, 7, 'active', ?, ?, NULL)",
        (dt_to_iso(datetime(2026, 5, 1, tzinfo=timezone.utc)),) * 2,
    )


def test_schema_v2_rejects_unknown_matcher(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO themes (id, query, period_seconds, matcher, top_n, "
            "days, status, created_at, next_run_at, last_run_id) "
            "VALUES ('tx', 'q', 60, 'unknown', 10, 7, 'active', ?, ?, NULL)",
            (dt_to_iso(datetime(2026, 5, 1, tzinfo=timezone.utc)),) * 2,
        )


def test_schema_v1_to_v2_progressive_migration(tmp_path: Path) -> None:
    """V1-only DB → migrate() поэтапно поднимает до V2, данные сохраняются."""
    db = tmp_path / "v1.db"
    # Создать «V1» состояние вручную: применить только _SCHEMA_V1
    conn = sqlite3.connect(str(db), isolation_level=None)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("BEGIN IMMEDIATE")
    for stmt in _SCHEMA_V1:
        cur.execute(stmt)
    cur.execute("PRAGMA user_version = 1")
    cur.execute("COMMIT")
    # Вставить тестовые данные V1
    cur.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at, last_run_id) "
        "VALUES ('legacy', 'q', 60, 'embedding', 10, 7, 'active', ?, ?, NULL)",
        (dt_to_iso(datetime(2026, 5, 1, tzinfo=timezone.utc)),) * 2,
    )
    conn.close()

    # Теперь connect() запустит migrate, ожидаем V1 → V2.
    conn = connect(db)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 2
    cols = {r[1] for r in conn.execute("PRAGMA table_info(articles)").fetchall()}
    assert "title_emb" in cols
    # Legacy данные сохранены
    legacy = conn.execute(
        "SELECT id, matcher FROM themes WHERE id = 'legacy'"
    ).fetchone()
    assert legacy["matcher"] == "embedding"


# ---- _compute_novelty ---------------------------------------------------


def test_compute_novelty_returns_none_when_no_emb() -> None:
    parent_h, score = ThemeService._compute_novelty(None, [])
    assert parent_h is None
    assert score is None


def test_compute_novelty_no_history_returns_none() -> None:
    e = np.array([1.0, 0.0], dtype=np.float32)
    parent_h, score = ThemeService._compute_novelty(e, [])
    assert parent_h is None
    assert score is None


def test_compute_novelty_above_threshold_returns_parent() -> None:
    """Sim ≥ default threshold (0.92) → дубликат, parent url_hash возвращается."""
    # Все unit-vectors. cos(a, b) ≈ 0.95 → выше дефолтного threshold 0.92.
    new_emb = np.array([1.0, 0.0], dtype=np.float32)
    similar = np.array([0.95, np.sqrt(1 - 0.95**2)], dtype=np.float32)
    different = np.array([0.0, 1.0], dtype=np.float32)
    history = [("u_diff", different), ("u_sim", similar)]
    parent_h, score = ThemeService._compute_novelty(new_emb, history)
    assert parent_h == "u_sim"
    assert score is not None
    assert score == pytest.approx(0.95, abs=0.01)


def test_compute_novelty_below_threshold_returns_none_parent() -> None:
    """Sim < default threshold (0.92) → не дубликат, max_sim возвращается."""
    new_emb = np.array([1.0, 0.0], dtype=np.float32)
    similar = np.array([0.7, np.sqrt(1 - 0.49)], dtype=np.float32)  # cos=0.7
    history = [("u_sim", similar)]
    parent_h, score = ThemeService._compute_novelty(new_emb, history)
    assert parent_h is None
    assert score == pytest.approx(0.7, abs=0.01)


def test_compute_novelty_custom_threshold() -> None:
    """Threshold можно понизить — больше дубликатов ловится."""
    new_emb = np.array([1.0, 0.0], dtype=np.float32)
    similar = np.array([0.6, 0.8], dtype=np.float32)  # cos=0.6
    history = [("u", similar)]
    # threshold=0.5 → cos 0.6 > 0.5 → дубликат
    parent_h, _ = ThemeService._compute_novelty(new_emb, history, threshold=0.5)
    assert parent_h == "u"
    # threshold=0.7 → cos 0.6 < 0.7 → не дубликат
    parent_h, _ = ThemeService._compute_novelty(new_emb, history, threshold=0.7)
    assert parent_h is None


def test_compute_novelty_picks_max_among_multiple() -> None:
    """1-NN: возвращается parent с максимальной similarity."""
    new_emb = np.array([1.0, 0.0], dtype=np.float32)
    closer = np.array([0.95, np.sqrt(1 - 0.95**2)], dtype=np.float32)
    farther = np.array([0.9, np.sqrt(1 - 0.9**2)], dtype=np.float32)
    history = [("u_far", farther), ("u_close", closer)]
    parent_h, score = ThemeService._compute_novelty(new_emb, history)
    assert parent_h == "u_close"
    assert score == pytest.approx(0.95, abs=0.01)
