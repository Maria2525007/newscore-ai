"""Матчеры: EmbeddingMatcher (Must), Bm25Matcher (Should)."""

import re
from typing import Protocol

import numpy as np

from newscore.models import EnrichedArticle, Match


class Matcher(Protocol):
    name: str
    version: str

    def rank(
        self,
        query: str,
        articles: list[EnrichedArticle],
        top_n: int,
    ) -> list[Match]: ...


def _article_text(a: EnrichedArticle) -> str:
    if a.body:
        return f"{a.title}\n\n{a.body}"
    if a.snippet:
        return f"{a.title}\n{a.snippet}"
    return a.title


def _topn_indices(scores: np.ndarray, top_n: int) -> np.ndarray:
    if len(scores) <= top_n:
        return np.argsort(-scores)
    unsorted_top = np.argpartition(-scores, top_n)[:top_n]
    return unsorted_top[np.argsort(-scores[unsorted_top])]


class EmbeddingMatcher:
    """sentence-transformers + intfloat/multilingual-e5-base.

    e5-префиксы (``query: ``, ``passage: ``) применяются ВНУТРИ rank.
    """

    name = "embedding"

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-base",
        min_score: float = 0.0,
    ) -> None:
        self.model_name = model_name
        self.min_score = min_score
        self._model = None

    @property
    def version(self) -> str:
        return f"{self.model_name}@1.0"

    def _ensure_model(self):
        if self._model is None:
            from newscore.embeddings import get_st_model

            self._model = get_st_model(self.model_name)
        return self._model

    def rank(
        self,
        query: str,
        articles: list[EnrichedArticle],
        top_n: int,
    ) -> list[Match]:
        if not articles:
            return []
        model = self._ensure_model()

        q_text = f"query: {query}"
        passages = [f"passage: {_article_text(a)}" for a in articles]

        q_emb = model.encode(
            [q_text], normalize_embeddings=True, show_progress_bar=False
        )[0]
        p_embs = model.encode(
            passages,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=16,
        )

        scores = np.asarray(p_embs) @ np.asarray(q_emb)
        idx = _topn_indices(scores, top_n)

        matches: list[Match] = []
        for i in idx:
            s = float(scores[i])
            if s < self.min_score:
                continue
            matches.append(Match(article=articles[int(i)], score=s))
        return matches


_RU_STOPWORDS = frozenset(
    {
        "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а",
        "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же",
        "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот", "от",
        "меня", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг",
        "ли", "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас",
        "нибудь", "опять", "уж", "вам", "ведь", "там", "потом", "себя",
        "ничего", "ей", "может", "они", "тут", "где", "есть", "надо", "ней",
        "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без",
        "будто", "чего", "раз", "тоже", "себе", "под", "будет", "ж", "тогда",
        "кто", "этот", "того", "потому", "этого", "какой", "совсем", "ним",
        "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее",
        "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно",
        "при", "наконец", "два", "об", "другой", "хоть", "после", "над",
        "больше", "тот", "через", "эти", "нас", "про", "всего", "них",
        "какая", "много", "разве", "три", "эту", "моя", "впрочем", "хорошо",
        "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя",
        "такой", "им", "более", "всегда", "конечно", "всю", "между",
    }
)


class Bm25Matcher:
    """rank_bm25 + минимальная токенизация."""

    name = "bm25"
    version = "rank_bm25_okapi@0.2"

    def rank(
        self,
        query: str,
        articles: list[EnrichedArticle],
        top_n: int,
    ) -> list[Match]:
        if not articles:
            return []
        from rank_bm25 import BM25Okapi

        corpus = [self._tokenize(_article_text(a)) for a in articles]
        bm25 = BM25Okapi(corpus)
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []
        scores = np.asarray(bm25.get_scores(q_tokens), dtype=float)
        idx = _topn_indices(scores, top_n)

        matches: list[Match] = []
        for i in idx:
            s = float(scores[i])
            if s <= 0:
                continue
            matches.append(Match(article=articles[int(i)], score=s))
        return matches

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
        return [t for t in tokens if t not in _RU_STOPWORDS and len(t) > 1]
