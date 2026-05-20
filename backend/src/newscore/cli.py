"""typer-приложение, entry point."""

import json
import sys
import uuid
from enum import Enum
from pathlib import Path

import typer

from newscore.briefing import (
    BriefingDeps,
    BriefingOrchestrator,
    BriefingRequest,
)
from newscore.config import load_config
from newscore.logging import TraceWriter, configure
from newscore.matcher import Bm25Matcher, EmbeddingMatcher, Matcher
from newscore.parser import FeedParser
from newscore.repository import InMemoryRepository


class MatcherChoice(str, Enum):
    embedding = "embedding"
    bm25 = "bm25"


class LogFormat(str, Enum):
    console = "console"
    json = "json"


def _matcher_factory(name: str) -> Matcher:
    if name == "embedding":
        return EmbeddingMatcher()
    if name == "bm25":
        return Bm25Matcher()
    raise ValueError(f"unknown matcher: {name}")


def briefing(
    query: str = typer.Argument(..., help="NL-запрос пользователя"),
    matcher: MatcherChoice = typer.Option(MatcherChoice.embedding, "--matcher"),
    top_n: int = typer.Option(10, "--top-n"),
    days: int = typer.Option(7, "--days"),
    trace: bool = typer.Option(False, "--trace"),
    log_format: LogFormat = typer.Option(LogFormat.console, "--log-format"),
    log_level: str = typer.Option("INFO", "--log-level"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Собрать брифинг по NL-запросу."""
    q = query.strip()
    if not q:
        print(json.dumps({"error": "query is empty"}, ensure_ascii=False))
        raise typer.Exit(code=2)

    run_id = uuid.uuid4().hex[:12]
    configure(level=log_level, fmt=log_format.value, run_id=run_id)

    cfg = load_config(config)
    parser = FeedParser(cfg)
    repo = InMemoryRepository()
    tw = TraceWriter(run_id=run_id, dir=Path("traces")) if trace else None
    deps = BriefingDeps(
        parser=parser,
        matcher_factory=_matcher_factory,
        repository=repo,
        trace_writer=tw,
    )
    orch = BriefingOrchestrator(cfg=cfg, deps=deps)
    req = BriefingRequest(
        query=q,
        top_n=top_n,
        freshness_days=days,
        matcher_name=matcher.value,
        trace=trace,
        run_id=run_id,
    )
    result = orch.run(req)

    sys.stdout.write(result.model_dump_json(indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()

    if result.meta.reason == "all_sources_failed":
        raise typer.Exit(code=1)


def main() -> None:
    typer.run(briefing)


if __name__ == "__main__":
    main()
