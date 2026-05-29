"""Оркестратор пайплайна."""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Literal

import structlog

from newscore.config import AppConfig
from newscore.dedupe import dedupe_by_url
from newscore.domain import DomainChecker
from newscore.logging import TraceWriter
from newscore.matcher import Matcher
from newscore.models import BriefingResult, FailedSource, RunMeta
from newscore.parser import FeedParser
from newscore.repository import BriefingRepository
from newscore.summarizer import Summarizer

log = structlog.get_logger(__name__)

# Минимальный score, ниже которого матч считается нерелевантным «шумом».
# См. подробный комментарий к шагу 3a (post-match relevance floor).
_RELEVANCE_FLOOR: dict[str, float] = {"embedding": 0.79, "rerank": 0.05}


@dataclass
class BriefingRequest:
    query: str
    top_n: int
    freshness_days: int
    matcher_name: Literal["embedding", "bm25", "hybrid", "rerank"]
    trace: bool
    run_id: str


@dataclass
class BriefingDeps:
    parser: FeedParser
    matcher_factory: Callable[[str], Matcher]
    repository: BriefingRepository
    trace_writer: TraceWriter | None
    summarizer: Summarizer | None = None
    domain_checker: DomainChecker | None = None


class BriefingOrchestrator:
    def __init__(self, cfg: AppConfig, deps: BriefingDeps) -> None:
        self.cfg = cfg
        self.deps = deps

    def run(self, req: BriefingRequest) -> BriefingResult:
        run_id = req.run_id
        started = datetime.now(timezone.utc)
        log.info(
            "briefing_start",
            query=req.query,
            matcher=req.matcher_name,
            top_n=req.top_n,
            days=req.freshness_days,
        )

        # 0. Domain pre-check (до fetch — экономит 2-5 сек на нерелевантных запросах)
        if self.deps.domain_checker is not None:
            relevant, max_sim = self.deps.domain_checker.is_relevant(req.query)
            if not relevant:
                log.info(
                    "domain_check_rejected",
                    query=req.query[:80],
                    max_sim=round(max_sim, 4),
                    threshold=self.deps.domain_checker.threshold,
                )
                finished = datetime.now(timezone.utc)
                meta = RunMeta(
                    run_id=run_id,
                    started_at=started,
                    finished_at=finished,
                    matcher_name=req.matcher_name,
                    matcher_version="skipped/domain_check",
                    sources_snapshot_at=started,
                    freshness_days=req.freshness_days,
                    partial=False,
                    failed_sources=[],
                    reason="no_relevant_matches",
                )
                result = BriefingResult(query=req.query, items=[], meta=meta)
                self.deps.repository.save_run(result)
                if self.deps.trace_writer:
                    self.deps.trace_writer.step(
                        "domain_check",
                        relevant=False,
                        max_sim=round(max_sim, 4),
                        threshold=self.deps.domain_checker.threshold,
                    )
                    self.deps.trace_writer.finalize(result)
                return result

        # 1. Parse + extract bodies
        t = time.time()
        report = self.deps.parser.collect(self.cfg.sources, req.freshness_days)
        parse_ms = int((time.time() - t) * 1000)
        if self.deps.trace_writer:
            self.deps.trace_writer.step(
                "fetch_and_extract",
                duration_ms=parse_ms,
                articles_total=len(report.articles),
                failed_sources=[fs.name for fs in report.failed_sources],
                partial=report.partial,
            )

        # 2. Dedupe by URL
        unique, removed = dedupe_by_url(report.articles)
        if self.deps.trace_writer:
            self.deps.trace_writer.step(
                "dedupe_url",
                items_in=len(report.articles),
                items_out=len(unique),
                removed=removed,
            )

        # 3. Match
        t = time.time()
        matcher = self.deps.matcher_factory(req.matcher_name)
        matches = matcher.rank(req.query, unique, req.top_n)

        # 3a. Post-match relevance floor — отсекаем нерелевантный «шум»,
        # чтобы по запросу-«мусору» сервис не выдавал случайные статьи.
        # Калибровка по реальному корпусу:
        #   embedding — релевантные дают top score ≥ 0.79, нерелевантные
        #               равномерный «шум» 0.74-0.78.
        #   rerank    — cross-encoder (sigmoid): релевантные 0.30-0.50+,
        #               нерелевантные ≤ 0.001 (зазор огромный, floor 0.05).
        # bm25/hybrid floor не задаём: bm25 уже отсекает score ≤ 0, а RRF-скоры
        # гибрида ранговые и не выражают абсолютную релевантность.
        floor = _RELEVANCE_FLOOR.get(req.matcher_name)
        if floor is not None and matches:
            matches = [m for m in matches if m.score >= floor]

        match_ms = int((time.time() - t) * 1000)
        if self.deps.trace_writer:
            self.deps.trace_writer.step(
                "match",
                matcher=matcher.name,
                matcher_version=matcher.version,
                duration_ms=match_ms,
                items_in=len(unique),
                items_out=len(matches),
                top_scores=[round(m.score, 4) for m in matches[:10]],
            )

        # 3b. Summarize (Step 3, optional)
        if self.deps.summarizer is not None and matches:
            t = time.time()
            for m in matches:
                try:
                    m.article.summary = self.deps.summarizer.summarize(
                        req.query, m.article
                    )
                except Exception as exc:  # noqa: BLE001
                    log.warning(
                        "summarize_failed",
                        url=str(m.article.url),
                        err=str(exc),
                    )
                    m.article.summary = None
            summarize_ms = int((time.time() - t) * 1000)
            if self.deps.trace_writer:
                self.deps.trace_writer.step(
                    "summarize",
                    summarizer=self.deps.summarizer.name,
                    summarizer_version=self.deps.summarizer.version,
                    duration_ms=summarize_ms,
                    items=len(matches),
                )

        # 4. Result
        finished = datetime.now(timezone.utc)
        all_failed = bool(report.failed_sources) and not report.articles
        if all_failed:
            reason: Literal["ok", "no_relevant_matches", "all_sources_failed"] = (
                "all_sources_failed"
            )
        elif not matches:
            reason = "no_relevant_matches"
        else:
            reason = "ok"

        if unique:
            sources_snapshot_at = min(a.published_at for a in unique)
        else:
            sources_snapshot_at = started

        meta = RunMeta(
            run_id=run_id,
            started_at=started,
            finished_at=finished,
            matcher_name=matcher.name,
            matcher_version=matcher.version,
            sources_snapshot_at=sources_snapshot_at,
            freshness_days=req.freshness_days,
            partial=report.partial,
            failed_sources=report.failed_sources,
            reason=reason,
        )
        result = BriefingResult(query=req.query, items=matches, meta=meta)
        self.deps.repository.save_run(result)

        if self.deps.trace_writer:
            self.deps.trace_writer.finalize(result)

        log.info(
            "briefing_done",
            run_id=run_id,
            items=len(matches),
            duration_ms=int((finished - started).total_seconds() * 1000),
            partial=report.partial,
            reason=reason,
        )

        return result
