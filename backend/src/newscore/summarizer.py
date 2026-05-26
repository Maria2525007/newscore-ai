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
    """Top-K предложений из body, ранжированных по близости к запросу.

    Query-focused — подходит для одиночных briefings (Step 0). Для
    дайджестов тем (Step 1+), где summary независим от user query,
    используйте `CentroidExtractiveSummarizer`.
    """

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


class CentroidExtractiveSummarizer:
    """Unsupervised centroid-greedy extractive summarizer.

    Gonçalves, Correia, Pernes, Mendes (Priberam Labs + Porto,
    arXiv:2311.17771, doc-010 §3.2 eq.5-6):

        e_{S∪{s}} = Σ_{s'∈S} e_{s'} + e_s
        s* = argmax_{s ∈ D \\ S} cosine(e_{S∪{s}}, centroid_D)

    Где centroid_D = mean(всех sentence embeddings документа).

    Ключевая идея (doc-010 §3.2): «redundancy is mitigated since the
    centroid is compared to the whole candidate summary S ∪ {s} at
    each iteration» — implicit redundancy reduction без явного MMR.

    Это unsupervised baseline (Gholipour Ghalandari 2017). Не query-
    focused: query параметр принимается для совместимости с Summarizer
    protocol, но игнорируется. Для query-focused briefing'ов
    используйте `ExtractiveSummarizer`.
    """

    name = "centroid_extractive"

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-base",
        budget_sentences: int = 3,
        min_sentences: int = 2,
    ) -> None:
        self.model_name = model_name
        self.budget_sentences = budget_sentences
        self.min_sentences = min_sentences

    @property
    def version(self) -> str:
        return f"{self.model_name}@centroid_b{self.budget_sentences}"

    def summarize(self, query: str, article: EnrichedArticle) -> str | None:
        # query игнорируется — centroid-метод document-focused.
        del query
        text = article.body if article.body else article.snippet
        if not text or not text.strip():
            return None

        sentences = split_sentences(text)
        if not sentences:
            return None
        if len(sentences) <= self.min_sentences:
            return " ".join(sentences)
        if len(sentences) <= self.budget_sentences:
            return " ".join(sentences)

        model = get_st_model(self.model_name)
        embs = np.asarray(
            model.encode(
                [f"passage: {s}" for s in sentences],
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32,
            )
        )
        centroid = embs.mean(axis=0)
        # cos = (a·b) / (||a||·||b||); centroid_norm пред-вычислен.
        centroid_norm = float(np.linalg.norm(centroid)) + 1e-12

        selected: list[int] = []
        cumulative = np.zeros_like(centroid)

        for _ in range(min(self.budget_sentences, len(sentences))):
            best_score = -np.inf
            best_i = -1
            for i in range(len(sentences)):
                if i in selected:
                    continue
                cand = cumulative + embs[i]
                cand_norm = float(np.linalg.norm(cand)) + 1e-12
                score = float(cand @ centroid) / (cand_norm * centroid_norm)
                if score > best_score:
                    best_score = score
                    best_i = i
            if best_i < 0:
                break
            selected.append(best_i)
            cumulative = cumulative + embs[best_i]

        # Возвращаем в исходном порядке документа (читаемость).
        return " ".join(sentences[i] for i in sorted(selected))
