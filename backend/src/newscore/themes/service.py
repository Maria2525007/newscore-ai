"""ThemeService — CRUD + run + delta-логика (Step 1)."""

from __future__ import annotations

import hashlib
import sqlite3
import threading
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import numpy as np
import structlog

from newscore.briefing import BriefingOrchestrator, BriefingRequest
from newscore.models import BriefingResult, Match
from newscore.themes.db import (
    dt_to_iso,
    row_to_article,
    row_to_run,
    row_to_theme,
)
from newscore.themes.models import (
    ArticleSnapshot,
    MatcherName,
    Theme,
    ThemeRun,
    ThemeStatus,
)

log = structlog.get_logger(__name__)

# ADR-25: semantic novelty — cosine 1-NN threshold над e5-base заголовками+сниппетом.
# Stanford 2025 (Hanley/Okabe/Durumeric arXiv:2501.09102, doc-006 §3.3) production-
# deployed e5-base-v2 + DP-Means на 4082 news sites. Наш 1-NN — упрощённая
# baseline той же идеи.
#
# Threshold 0.92 откалиброван эмпирически: e5-base даёт высокий baseline cos
# (~0.85) даже на коротких разнотематических заголовках (политика vs кулинария).
# Для надёжной "CO-like" (high overlap) детекции дубликатов нужен >0.90.
# PO+CO модель Zhao 2005 (doc-009 §3.1) даёт формальное обоснование такого порога.
_NOVELTY_THRESHOLD: float = 0.92
_NOVELTY_WINDOW_DAYS: int = 7
_NOVELTY_MODEL: str = "intfloat/multilingual-e5-base"
_NOVELTY_EMB_DIM: int = 768
# Float32 для компактности на диске: 768 * 4 = 3 KB / статья.
_NOVELTY_EMB_DTYPE = np.float32
# Сколько символов snippet/body добавлять к title в emb input — обогащает
# контекст и снижает baseline cos между разнотематическими статьями.
_NOVELTY_BODY_CHARS: int = 300


class ThemeNotFound(Exception):
    """Raised when a theme_id does not exist."""


def url_hash(url: str) -> str:
    """Канонический url_hash: sha256(lower(url).rstrip('/'))[:32]."""
    normalized = url.strip().lower().rstrip("/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ThemeService:
    """Single-class service для тем. Per-thread SQLite-connection через threading.local."""

    def __init__(
        self,
        conn_factory: Callable[[], sqlite3.Connection],
        orchestrator_factory: Callable[[], BriefingOrchestrator],
    ) -> None:
        self._make_conn = conn_factory
        self._make_orch = orchestrator_factory
        self._local = threading.local()
        self._orch: BriefingOrchestrator | None = None

    def _conn(self) -> sqlite3.Connection:
        c = getattr(self._local, "conn", None)
        if c is None:
            c = self._make_conn()
            self._local.conn = c
        return c

    def _orchestrator(self) -> BriefingOrchestrator:
        if self._orch is None:
            self._orch = self._make_orch()
        return self._orch

    # ---- CRUD ------------------------------------------------------------

    def create(
        self,
        query: str,
        period_seconds: int,
        *,
        matcher: MatcherName = "embedding",
        top_n: int = 10,
        days: int = 7,
    ) -> Theme:
        theme = Theme(
            id=uuid.uuid4().hex[:12],
            query=query.strip(),
            period_seconds=period_seconds,
            matcher=matcher,
            top_n=top_n,
            days=days,
            status="active",
            created_at=_now(),
            next_run_at=_now(),
        )
        conn = self._conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute(
                "INSERT INTO themes (id, query, period_seconds, matcher, top_n, "
                "days, status, created_at, next_run_at, last_run_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                (
                    theme.id,
                    theme.query,
                    theme.period_seconds,
                    theme.matcher,
                    theme.top_n,
                    theme.days,
                    theme.status,
                    dt_to_iso(theme.created_at),
                    dt_to_iso(theme.next_run_at),
                ),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        log.info("theme_created", theme_id=theme.id, query=theme.query)
        return theme

    def list(self, status: ThemeStatus | None = None) -> list[Theme]:
        if status is None:
            rows = self._conn().execute(
                "SELECT * FROM themes ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = self._conn().execute(
                "SELECT * FROM themes WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        return [row_to_theme(r) for r in rows]

    def get(self, theme_id: str) -> Theme:
        row = self._conn().execute(
            "SELECT * FROM themes WHERE id = ?", (theme_id,)
        ).fetchone()
        if row is None:
            raise ThemeNotFound(theme_id)
        return row_to_theme(row)

    def delete(self, theme_id: str) -> None:
        conn = self._conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            cur = conn.execute("DELETE FROM themes WHERE id = ?", (theme_id,))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        if cur.rowcount == 0:
            raise ThemeNotFound(theme_id)
        log.info("theme_deleted", theme_id=theme_id)

    def pause(self, theme_id: str) -> Theme:
        return self._set_status(theme_id, "paused")

    def resume(self, theme_id: str) -> Theme:
        return self._set_status(theme_id, "active")

    def _set_status(self, theme_id: str, status: ThemeStatus) -> Theme:
        conn = self._conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            cur = conn.execute(
                "UPDATE themes SET status = ? WHERE id = ?", (status, theme_id)
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        if cur.rowcount == 0:
            raise ThemeNotFound(theme_id)
        return self.get(theme_id)

    # ---- Run / delta -----------------------------------------------------

    def due_themes(self, now: datetime | None = None) -> list[Theme]:
        ts = dt_to_iso(now or _now())
        rows = self._conn().execute(
            "SELECT * FROM themes WHERE status = 'active' AND next_run_at <= ? "
            "ORDER BY next_run_at",
            (ts,),
        ).fetchall()
        return [row_to_theme(r) for r in rows]

    def run_now(self, theme_id: str) -> ThemeRun:
        theme = self.get(theme_id)
        req = BriefingRequest(
            query=theme.query,
            top_n=theme.top_n,
            freshness_days=theme.days,
            matcher_name=theme.matcher,
            trace=False,
            run_id=uuid.uuid4().hex[:12],
        )
        log.info("theme_run_started", theme_id=theme.id, run_id=req.run_id)
        result = self._orchestrator().run(req)
        run = self._persist_run(theme, result)
        log.info(
            "theme_run_done",
            theme_id=theme.id,
            run_id=run.id,
            items_total=run.items_total,
            items_new=run.items_new,
        )
        return run

    def _persist_run(self, theme: Theme, result: BriefingResult) -> ThemeRun:
        conn = self._conn()
        conn.execute("BEGIN IMMEDIATE")
        try:
            items_total = len(result.items)
            meta_json = result.meta.model_dump_json()
            conn.execute(
                "INSERT INTO runs (id, theme_id, started_at, finished_at, "
                "matcher_name, matcher_version, partial, reason, "
                "items_total, items_new, meta_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
                (
                    result.meta.run_id,
                    theme.id,
                    dt_to_iso(result.meta.started_at),
                    dt_to_iso(result.meta.finished_at),
                    result.meta.matcher_name,
                    result.meta.matcher_version,
                    int(result.meta.partial),
                    result.meta.reason,
                    items_total,
                    meta_json,
                ),
            )
            items_new = self._upsert_articles(
                conn, theme.id, result.meta.run_id, result.items
            )
            conn.execute(
                "UPDATE runs SET items_new = ? WHERE id = ?",
                (items_new, result.meta.run_id),
            )
            next_run_at = result.meta.finished_at + timedelta(
                seconds=theme.period_seconds
            )
            conn.execute(
                "UPDATE themes SET last_run_id = ?, next_run_at = ? WHERE id = ?",
                (result.meta.run_id, dt_to_iso(next_run_at), theme.id),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

        return ThemeRun(
            id=result.meta.run_id,
            theme_id=theme.id,
            started_at=result.meta.started_at,
            finished_at=result.meta.finished_at,
            matcher_name=result.meta.matcher_name,
            matcher_version=result.meta.matcher_version,
            partial=result.meta.partial,
            reason=result.meta.reason,
            items_total=items_total,
            items_new=items_new,
        )

    def _upsert_articles(
        self,
        conn: sqlite3.Connection,
        theme_id: str,
        run_id: str,
        matches: list[Match],
    ) -> int:
        """Persist matches с двухслойной дедупликацией:

        Layer 1 (ADR-21, existing): exact `url_hash` — короткий путь.
        Layer 2 (ADR-25, new): cosine 1-NN над e5-emb заголовков в окне
        `_NOVELTY_WINDOW_DAYS`, threshold `_NOVELTY_THRESHOLD`. Cross-source
        duplicates («РИА vs ТАСС» про одно событие) ловятся даже при разных URL.
        """
        items_new = 0
        now_iso = dt_to_iso(_now())

        # Заранее посчитаем embeddings для всех новых матчей одной batch-сессией —
        # это быстрее, чем encode-per-article. e5 уже горячий из briefing pipeline.
        new_matches: list[Match] = []
        for m in matches:
            h = url_hash(str(m.article.url))
            row = conn.execute(
                "SELECT 1 FROM articles WHERE theme_id = ? AND url_hash = ?",
                (theme_id, h),
            ).fetchone()
            if row is None:
                new_matches.append(m)

        embs_by_url: dict[str, np.ndarray] = {}
        if new_matches:
            try:
                from newscore.embeddings import get_st_model

                model = get_st_model(_NOVELTY_MODEL)
                # title + snippet/body[:N] — больше контекста чем title only,
                # снижает baseline cos между разнотематическими статьями.
                texts: list[str] = []
                for m in new_matches:
                    body = m.article.body or m.article.snippet or ""
                    text = m.article.title
                    if body:
                        text = f"{text}. {body[:_NOVELTY_BODY_CHARS]}"
                    texts.append(f"passage: {text}")
                embs = model.encode(
                    texts,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                    batch_size=16,
                )
                embs = np.asarray(embs, dtype=_NOVELTY_EMB_DTYPE)
                for i, m in enumerate(new_matches):
                    embs_by_url[str(m.article.url)] = embs[i]
            except Exception as exc:
                # Не блокируем persist если encoder упал. Logging + продолжаем.
                log.warning(
                    "novelty_encode_failed",
                    theme_id=theme_id,
                    err=type(exc).__name__,
                )
                embs_by_url = {}

        # Pre-load history embeddings для cosine 1-NN.
        history = self._load_history_embeddings(conn, theme_id, _NOVELTY_WINDOW_DAYS)

        for m in matches:
            h = url_hash(str(m.article.url))
            payload = m.model_dump_json()
            row = conn.execute(
                "SELECT 1 FROM articles WHERE theme_id = ? AND url_hash = ?",
                (theme_id, h),
            ).fetchone()
            if row is None:
                title_emb = embs_by_url.get(str(m.article.url))
                duplicate_of, sim_score = self._compute_novelty(
                    title_emb, history
                )
                emb_blob = title_emb.tobytes() if title_emb is not None else None
                conn.execute(
                    "INSERT INTO articles (url_hash, theme_id, first_run_id, "
                    "last_seen_run_id, first_seen_at, last_score, payload_json, "
                    "title_emb, duplicate_of_url_hash, similarity_score) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        h,
                        theme_id,
                        run_id,
                        run_id,
                        now_iso,
                        m.score,
                        payload,
                        emb_blob,
                        duplicate_of,
                        sim_score,
                    ),
                )
                # Только не-дубликаты считаются "новыми" в items_new — это
                # делает дельтинг семантически осмысленным.
                if duplicate_of is None:
                    items_new += 1
                # Добавляем в in-memory history, чтобы внутри одного run'а
                # последующие matches тоже сравнивались с этим (батчевая
                # дедупликация внутри пачки).
                if title_emb is not None:
                    history.append((h, title_emb))
            else:
                conn.execute(
                    "UPDATE articles SET last_seen_run_id = ?, last_score = ?, "
                    "payload_json = ? WHERE theme_id = ? AND url_hash = ?",
                    (run_id, m.score, payload, theme_id, h),
                )
        return items_new

    def _load_history_embeddings(
        self,
        conn: sqlite3.Connection,
        theme_id: str,
        window_days: int,
    ) -> list[tuple[str, np.ndarray]]:
        """Подгрузить (url_hash, title_emb) для статей в скользящем окне."""
        since = _now() - timedelta(days=window_days)
        rows = conn.execute(
            "SELECT url_hash, title_emb FROM articles "
            "WHERE theme_id = ? AND first_seen_at >= ? "
            "AND title_emb IS NOT NULL",
            (theme_id, dt_to_iso(since)),
        ).fetchall()
        out: list[tuple[str, np.ndarray]] = []
        for r in rows:
            blob = r["title_emb"]
            if blob is None:
                continue
            emb = np.frombuffer(blob, dtype=_NOVELTY_EMB_DTYPE)
            if emb.shape == (_NOVELTY_EMB_DIM,):
                out.append((r["url_hash"], emb))
        return out

    @staticmethod
    def _compute_novelty(
        title_emb: np.ndarray | None,
        history: list[tuple[str, np.ndarray]],
        threshold: float = _NOVELTY_THRESHOLD,
    ) -> tuple[str | None, float | None]:
        """Cosine 1-NN: вернуть (parent_url_hash, similarity) если sim > threshold.

        Иначе (None, max_sim_observed) — even при max_sim ≤ threshold мы храним
        наблюдённый максимум для analytics/tuning.
        """
        if title_emb is None or not history:
            return None, None
        # title_emb уже unit-normalized (e5 normalize_embeddings=True).
        # history embs тоже unit. cos = dot product.
        best_score = -float("inf")
        best_url_hash: str | None = None
        for u, emb in history:
            score = float(np.dot(title_emb, emb))
            if score > best_score:
                best_score = score
                best_url_hash = u
        if best_score >= threshold:
            return best_url_hash, best_score
        return None, best_score if best_score > -float("inf") else None

    # ---- Queries for view layer -----------------------------------------

    def latest_run(self, theme_id: str) -> ThemeRun | None:
        row = self._conn().execute(
            "SELECT * FROM runs WHERE theme_id = ? "
            "ORDER BY started_at DESC LIMIT 1",
            (theme_id,),
        ).fetchone()
        return row_to_run(row) if row else None

    def list_runs(self, theme_id: str, limit: int = 20) -> list[ThemeRun]:
        rows = self._conn().execute(
            "SELECT * FROM runs WHERE theme_id = ? "
            "ORDER BY started_at DESC LIMIT ?",
            (theme_id, limit),
        ).fetchall()
        return [row_to_run(r) for r in rows]

    def latest_articles(
        self, theme_id: str, limit: int = 50
    ) -> list[ArticleSnapshot]:
        rows = self._conn().execute(
            "SELECT * FROM articles WHERE theme_id = ? "
            "ORDER BY first_seen_at DESC, url_hash LIMIT ?",
            (theme_id, limit),
        ).fetchall()
        return [row_to_article(r) for r in rows]

    def new_since(
        self, theme_id: str, since: datetime
    ) -> list[ArticleSnapshot]:
        rows = self._conn().execute(
            "SELECT * FROM articles WHERE theme_id = ? AND first_seen_at >= ? "
            "ORDER BY first_seen_at DESC, url_hash",
            (theme_id, dt_to_iso(since)),
        ).fetchall()
        return [row_to_article(r) for r in rows]
