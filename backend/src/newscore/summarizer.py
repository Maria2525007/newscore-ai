"""Extractive summarizer (Step 3).

Алгоритм:
1. Сегментация тела на предложения через razdel (RU-aware).
2. Эмбеддинг каждого предложения и запроса через тот же e5-base, что и
   matcher (общий кэш моделей в `newscore.embeddings`).
3. Top-K предложений по cos-similarity к запросу, пере-сортированные
   в исходном порядке для читаемости.

Никаких LLM API — полностью локально.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

from newscore.embeddings import get_st_model
from newscore.models import EnrichedArticle


class Summarizer(Protocol):
    name: str
    version: str

    def summarize(self, query: str, article: EnrichedArticle) -> str | None: ...


def split_sentences(text: str) -> list[str]:
    """Разбить на предложения через razdel; fallback на пустой список."""
    from razdel import sentenize

    return [s.text.strip() for s in sentenize(text) if s.text.strip()]


class ExtractiveSummarizer:
    """Top-K предложений из body, ранжированных по близости к запросу."""

    name = "extractive_e5"

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-base",
        top_k: int = 3,
        min_sentences: int = 2,
    ) -> None:
        self.model_name = model_name
        self.top_k = top_k
        self.min_sentences = min_sentences

    @property
    def version(self) -> str:
        return f"{self.model_name}@extractive_top{self.top_k}"

    def summarize(self, query: str, article: EnrichedArticle) -> str | None:
        text = article.body if article.body else article.snippet
        if not text or not text.strip():
            return None

        sentences = split_sentences(text)
        if len(sentences) <= self.min_sentences:
            return " ".join(sentences) if sentences else None
        if len(sentences) <= self.top_k:
            return " ".join(sentences)

        model = get_st_model(self.model_name)
        q_emb = model.encode(
            [f"query: {query}"],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        sent_embs = model.encode(
            [f"passage: {s}" for s in sentences],
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        scores = np.asarray(sent_embs) @ np.asarray(q_emb)
        top_idx = sorted(np.argsort(-scores)[: self.top_k].tolist())
        return " ".join(sentences[i] for i in top_idx)
