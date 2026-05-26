"""SQLite persistence layer для Step 1.

ADR-18: stdlib sqlite3, no ORM.
ADR-19: миграции — raw SQL, идемпотентно.
ADR-22: payload/meta — JSON в TEXT-колонках.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from newscore.themes.models import ArticleSnapshot, Theme, ThemeRun

DEFAULT_DB_PATH = Path("data/newscore.db")
SCHEMA_VERSION = 2

_SCHEMA_V1: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS themes (
      id              TEXT PRIMARY KEY,
      query           TEXT NOT NULL,
      period_seconds  INTEGER NOT NULL CHECK (period_seconds >= 60),
      matcher         TEXT NOT NULL CHECK (matcher IN ('embedding','bm25')),
      top_n           INTEGER NOT NULL DEFAULT 10 CHECK (top_n BETWEEN 1 AND 50),
      days            INTEGER NOT NULL DEFAULT 7 CHECK (days BETWEEN 1 AND 30),
      status          TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','paused')),
      created_at      TEXT NOT NULL,
      next_run_at     TEXT NOT NULL,
      last_run_id     TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_themes_due ON themes(status, next_run_at)",
    """
    CREATE TABLE IF NOT EXISTS runs (
      id              TEXT PRIMARY KEY,
      theme_id        TEXT NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
      started_at      TEXT NOT NULL,
      finished_at     TEXT NOT NULL,
      matcher_name    TEXT NOT NULL,
      matcher_version TEXT NOT NULL,
      partial         INTEGER NOT NULL,
      reason          TEXT,
      items_total     INTEGER NOT NULL,
      items_new       INTEGER NOT NULL DEFAULT 0,
      meta_json       TEXT NOT NULL CHECK (json_valid(meta_json))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_runs_theme_started ON runs(theme_id, started_at DESC)",
    """
    CREATE TABLE IF NOT EXISTS articles (
      url_hash         TEXT NOT NULL,
      theme_id         TEXT NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
      first_run_id     TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
      last_seen_run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
      first_seen_at    TEXT NOT NULL,
      last_score       REAL NOT NULL,
      payload_json     TEXT NOT NULL CHECK (json_valid(payload_json)),
      PRIMARY KEY (theme_id, url_hash)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_articles_theme_first_seen "
    "ON articles(theme_id, first_seen_at DESC, url_hash)",
]


# ADR-25 + ADR-24: semantic novelty + расширение matcher до hybrid/rerank.
# Изменения:
#   1) articles += title_emb BLOB, duplicate_of_url_hash TEXT, similarity_score REAL
#   2) themes.matcher CHECK расширен до {embedding,bm25,hybrid,rerank}
#      (требует recreate-таблицы, т.к. SQLite не умеет ALTER CHECK)
_SCHEMA_V2: list[str] = [
    # 1) Add novelty columns to articles. SQLite поддерживает ADD COLUMN с 3.2+.
    "ALTER TABLE articles ADD COLUMN title_emb BLOB",
    "ALTER TABLE articles ADD COLUMN duplicate_of_url_hash TEXT",
    "ALTER TABLE articles ADD COLUMN similarity_score REAL",
    # 2) Recreate themes с расширенным CHECK на matcher.
    """
    CREATE TABLE themes_v2 (
      id              TEXT PRIMARY KEY,
      query           TEXT NOT NULL,
      period_seconds  INTEGER NOT NULL CHECK (period_seconds >= 60),
      matcher         TEXT NOT NULL
                        CHECK (matcher IN ('embedding','bm25','hybrid','rerank')),
      top_n           INTEGER NOT NULL DEFAULT 10 CHECK (top_n BETWEEN 1 AND 50),
      days            INTEGER NOT NULL DEFAULT 7 CHECK (days BETWEEN 1 AND 30),
      status          TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','paused')),
      created_at      TEXT NOT NULL,
      next_run_at     TEXT NOT NULL,
      last_run_id     TEXT
    )
    """,
    "INSERT INTO themes_v2 (id, query, period_seconds, matcher, top_n, days, "
    "status, created_at, next_run_at, last_run_id) "
    "SELECT id, query, period_seconds, matcher, top_n, days, status, "
    "created_at, next_run_at, last_run_id FROM themes",
    "DROP TABLE themes",
    "ALTER TABLE themes_v2 RENAME TO themes",
    "CREATE INDEX IF NOT EXISTS idx_themes_due ON themes(status, next_run_at)",
]


def connect(path: Path | str) -> sqlite3.Connection:
    """Открыть соединение с применением миграций и PRAGMA."""
    p = Path(path) if not isinstance(path, Path) else path
    if str(p) != ":memory:":
        p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        str(p),
        detect_types=sqlite3.PARSE_DECLTYPES,
        check_same_thread=False,
        isolation_level=None,  # autocommit; transactions via BEGIN
    )
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    migrate(conn)
    return conn


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for stmt in (
        "PRAGMA journal_mode = WAL",
        "PRAGMA synchronous = NORMAL",
        "PRAGMA foreign_keys = ON",
        "PRAGMA busy_timeout = 5000",
        "PRAGMA cache_size = -20000",
        "PRAGMA temp_store = MEMORY",
        "PRAGMA mmap_size = 268435456",
    ):
        cur.execute(stmt)


def migrate(conn: sqlite3.Connection) -> None:
    """Поступательная миграция 0 → 1 → 2; идемпотентно."""
    cur = conn.cursor()
    current = cur.execute("PRAGMA user_version").fetchone()[0]
    if current >= SCHEMA_VERSION:
        return
    cur.execute("BEGIN IMMEDIATE")
    try:
        if current < 1:
            for stmt in _SCHEMA_V1:
                cur.execute(stmt)
            cur.execute("PRAGMA user_version = 1")
        if current < 2:
            for stmt in _SCHEMA_V2:
                cur.execute(stmt)
            cur.execute("PRAGMA user_version = 2")
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise


# ---- Row mappers --------------------------------------------------------


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def row_to_theme(row: sqlite3.Row) -> Theme:
    return Theme(
        id=row["id"],
        query=row["query"],
        period_seconds=row["period_seconds"],
        matcher=row["matcher"],
        top_n=row["top_n"],
        days=row["days"],
        status=row["status"],
        created_at=_parse_dt(row["created_at"]),
        next_run_at=_parse_dt(row["next_run_at"]),
        last_run_id=row["last_run_id"],
    )


def row_to_run(row: sqlite3.Row) -> ThemeRun:
    return ThemeRun(
        id=row["id"],
        theme_id=row["theme_id"],
        started_at=_parse_dt(row["started_at"]),
        finished_at=_parse_dt(row["finished_at"]),
        matcher_name=row["matcher_name"],
        matcher_version=row["matcher_version"],
        partial=bool(row["partial"]),
        reason=row["reason"],
        items_total=row["items_total"],
        items_new=row["items_new"],
    )


def row_to_article(row: sqlite3.Row) -> ArticleSnapshot:
    # row.keys() безопасно — sqlite3.Row поддерживает iteration.
    cols = set(row.keys())
    return ArticleSnapshot(
        url_hash=row["url_hash"],
        theme_id=row["theme_id"],
        first_run_id=row["first_run_id"],
        last_seen_run_id=row["last_seen_run_id"],
        first_seen_at=_parse_dt(row["first_seen_at"]),
        last_score=row["last_score"],
        payload=json.loads(row["payload_json"]),
        duplicate_of_url_hash=(
            row["duplicate_of_url_hash"]
            if "duplicate_of_url_hash" in cols
            else None
        ),
        similarity_score=(
            row["similarity_score"] if "similarity_score" in cols else None
        ),
    )


def dt_to_iso(dt: datetime) -> str:
    return dt.isoformat()
