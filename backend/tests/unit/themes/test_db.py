"""Тесты слоя persistence для тем."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from newscore.themes.db import (
    SCHEMA_VERSION,
    connect,
    dt_to_iso,
    migrate,
    row_to_article,
    row_to_run,
    row_to_theme,
)


def test_connect_creates_file(tmp_path: Path) -> None:
    db = tmp_path / "subdir" / "x.db"
    conn = connect(db)
    assert db.exists()
    conn.close()


def test_connect_applies_pragmas(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
    fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    assert journal == "wal"
    assert fk == 1


def test_migrate_sets_user_version(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    assert version == SCHEMA_VERSION


def test_migrate_is_idempotent(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    migrate(conn)
    migrate(conn)
    # Если бы не было IF NOT EXISTS — упало бы. Проверка через двойной apply.
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"themes", "runs", "articles"} <= tables


def test_json_valid_constraint_blocks_garbage(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    conn.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("t1", "q", 60, "embedding", 10, 7, "active", "now", "now"),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO runs (id, theme_id, started_at, finished_at, "
            "matcher_name, matcher_version, partial, items_total, meta_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("r1", "t1", "now", "now", "embedding", "v", 0, 0, "not-json"),
        )


def test_foreign_keys_cascade(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    conn.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("t1", "q", 60, "embedding", 10, 7, "active", "now", "now"),
    )
    conn.execute(
        "INSERT INTO runs (id, theme_id, started_at, finished_at, "
        "matcher_name, matcher_version, partial, items_total, meta_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("r1", "t1", "now", "now", "embedding", "v", 0, 0, "{}"),
    )
    conn.execute("DELETE FROM themes WHERE id = ?", ("t1",))
    assert conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0


def test_row_to_theme(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    now = datetime(2026, 5, 24, 10, 0, tzinfo=timezone.utc)
    conn.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at, last_run_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "t1",
            "курс",
            3600,
            "embedding",
            10,
            7,
            "active",
            dt_to_iso(now),
            dt_to_iso(now),
            None,
        ),
    )
    row = conn.execute("SELECT * FROM themes WHERE id = ?", ("t1",)).fetchone()
    theme = row_to_theme(row)
    assert theme.id == "t1"
    assert theme.query == "курс"
    assert theme.period_seconds == 3600
    assert theme.matcher == "embedding"
    assert theme.status == "active"
    assert theme.last_run_id is None


def test_row_to_run_and_article(tmp_path: Path) -> None:
    conn = connect(tmp_path / "x.db")
    now_iso = dt_to_iso(datetime(2026, 5, 24, tzinfo=timezone.utc))
    conn.execute(
        "INSERT INTO themes (id, query, period_seconds, matcher, top_n, days, "
        "status, created_at, next_run_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("t1", "q", 60, "embedding", 10, 7, "active", now_iso, now_iso),
    )
    conn.execute(
        "INSERT INTO runs (id, theme_id, started_at, finished_at, "
        "matcher_name, matcher_version, partial, items_total, items_new, "
        "meta_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("r1", "t1", now_iso, now_iso, "embedding", "v", 0, 3, 1, "{}"),
    )
    conn.execute(
        "INSERT INTO articles (url_hash, theme_id, first_run_id, "
        "last_seen_run_id, first_seen_at, last_score, payload_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("h1", "t1", "r1", "r1", now_iso, 0.92, json.dumps({"x": 1})),
    )
    run = row_to_run(
        conn.execute("SELECT * FROM runs WHERE id = ?", ("r1",)).fetchone()
    )
    art = row_to_article(
        conn.execute(
            "SELECT * FROM articles WHERE url_hash = ?", ("h1",)
        ).fetchone()
    )
    assert run.items_total == 3
    assert run.items_new == 1
    assert run.partial is False
    assert art.last_score == 0.92
    assert art.payload == {"x": 1}
