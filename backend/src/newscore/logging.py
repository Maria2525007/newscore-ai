"""Конфигурация structlog + TraceWriter.

NB: модуль называется ``logging`` намеренно (ADR-09).
Внутри обращаемся к stdlib через ``logging as stdlib_logging``.
"""

import json
import logging as stdlib_logging
import sys
from pathlib import Path
from typing import Any, Literal

import structlog

from newscore.models import BriefingResult


def configure(
    level: str,
    fmt: Literal["console", "json"],
    run_id: str,
) -> None:
    lvl = getattr(stdlib_logging, level.upper(), stdlib_logging.INFO)

    stdlib_logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=lvl,
        force=True,
    )

    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]
    if fmt == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=False))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(lvl),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(run_id=run_id)


class TraceWriter:
    def __init__(self, run_id: str, dir: Path) -> None:
        self.run_id = run_id
        self.dir = dir
        self._steps: list[dict[str, Any]] = []

    def step(self, name: str, **kwargs: Any) -> None:
        self._steps.append({"name": name, **kwargs})

    def finalize(self, result: BriefingResult) -> Path:
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / f"{self.run_id}.json"
        payload = {
            "run_id": self.run_id,
            "query": result.query,
            "steps": self._steps,
            "result_meta": result.meta.model_dump(mode="json"),
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
        return path
