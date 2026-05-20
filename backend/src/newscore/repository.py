"""Тонкий repo-интерфейс. Готовит почву для SQLite в Step 1."""

from typing import Protocol

from newscore.models import BriefingResult


class BriefingRepository(Protocol):
    def save_run(self, result: BriefingResult) -> None: ...
    def latest_for_query(self, query: str) -> BriefingResult | None: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self._latest: dict[str, BriefingResult] = {}

    def save_run(self, result: BriefingResult) -> None:
        self._latest[result.query] = result

    def latest_for_query(self, query: str) -> BriefingResult | None:
        return self._latest.get(query)
