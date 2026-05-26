"""E2E helpers: FakeOrchestrator + builders, отдельно от conftest,
чтобы импортироваться и из фикстур, и из тестов одним и тем же путём."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from newscore.briefing import BriefingRequest
from newscore.models import BriefingResult, EnrichedArticle, Match, RunMeta
from newscore.themes.service import ThemeService


def make_article(
    url: str, title: str, summary: str | None = None, source: str = "rbc"
) -> EnrichedArticle:
    return EnrichedArticle(
        source=source,
        title=title,
        url=url,
        published_at=datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc),
        snippet="фрагмент текста статьи для отображения",
        body=None,
        body_extracted=False,
        body_extractor="trafilatura",
        summary=summary,
    )


def make_result(
    query: str, articles: list[EnrichedArticle], run_id: str = "x"
) -> BriefingResult:
    started = datetime.now(timezone.utc)
    matches = [
        Match(article=a, score=0.9 - i * 0.05) for i, a in enumerate(articles)
    ]
    meta = RunMeta(
        run_id=run_id,
        started_at=started,
        finished_at=started + timedelta(seconds=1),
        matcher_name="embedding",
        matcher_version="e5-base",
        sources_snapshot_at=started,
        freshness_days=7,
        partial=False,
        failed_sources=[],
        reason="ok" if matches else "no_relevant_matches",
    )
    return BriefingResult(query=query, items=matches, meta=meta)


class FakeOrchestrator:
    """Отдаёт scripted результаты по очереди; пустой → no_relevant_matches."""

    def __init__(self) -> None:
        self._scripted: list[BriefingResult] = []

    def push(self, result: BriefingResult) -> None:
        self._scripted.append(result)

    def run(self, req: BriefingRequest) -> BriefingResult:
        result = (
            self._scripted.pop(0) if self._scripted else make_result(req.query, [])
        )
        result.meta.run_id = req.run_id
        return result


@dataclass
class LiveServer:
    base_url: str
    service: ThemeService
    orchestrator: FakeOrchestrator
