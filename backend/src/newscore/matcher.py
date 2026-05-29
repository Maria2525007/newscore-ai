"""Матчеры: EmbeddingMatcher (Must), Bm25Matcher (Should)."""

import re
from typing import Protocol

import numpy as np

from newscore.models import EnrichedArticle, Match

# Lazy-init синглтон PyMorphy3 (init ~50ms, не дёшево на каждый вызов).
_morph = None


def _get_morph():
    """Возвращает MorphAnalyzer; инициализирует при первом обращении."""
    global _morph
    if _morph is None:
        from pymorphy3 import MorphAnalyzer

        _morph = MorphAnalyzer(lang="ru")
    return _morph


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

        q_emb = model.encode(
            [f"query: {query}"],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        p_embs = self._encode_passages_cached(model, articles)
        scores = np.asarray(p_embs) @ np.asarray(q_emb)
        idx = _topn_indices(scores, top_n)

        matches: list[Match] = []
        for i in idx:
            s = float(scores[i])
            if s < self.min_score:
                continue
            matches.append(Match(article=articles[int(i)], score=s))
        return matches

    def _encode_passages_cached(self, model, articles: list[EnrichedArticle]):
        """Encode только cache-miss articles; для остальных — вернуть из кэша.

        Ключ кэша = content_hash(title, body, snippet): меняется при
        изменении текста статьи → корректная инвалидация. Если статья та же —
        embedding берётся из L1 (in-memory) или L2 (Redis), без переэнкода.
        """
        from newscore.embeddings import (
            cache_passage_emb,
            get_cached_passage_emb,
        )
        from newscore.redis_cache import content_hash

        n = len(articles)
        result: list = [None] * n
        hashes = [
            content_hash(a.title, a.body, a.snippet) for a in articles
        ]
        miss_idx: list[int] = []
        miss_passages: list[str] = []
        for i, a in enumerate(articles):
            cached = get_cached_passage_emb(self.model_name, hashes[i])
            if cached is not None:
                result[i] = cached
            else:
                miss_idx.append(i)
                miss_passages.append(f"passage: {_article_text(a)}")

        if miss_passages:
            new_embs = model.encode(
                miss_passages,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=16,
            )
            new_embs = np.asarray(new_embs)
            for i, emb in zip(miss_idx, new_embs):
                result[i] = emb
                cache_passage_emb(self.model_name, hashes[i], emb)

        return np.asarray(result)


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


# Boost-фактор для title при индексации (BM25F-pattern, Robertson 2004).
# Совместно с PyMorphy3-лемматизацией — рецепт RusBEIR §4.1 (Kovalev 2025).
_TITLE_BOOST = 3


class Bm25Matcher:
    """rank_bm25 + PyMorphy3-лемматизация + title boost ×3.

    Recipe основан на RusBEIR §4.1 (Kovalev et al., arXiv:2504.12879):
    lowercase → punctuation removal → tokenize → PyMorphy3 lemmatize →
    NLTK stopwords + русские местоимения «который, такой».
    Title boost ×3 — BM25F-pattern для приоритизации заголовков.
    """

    name = "bm25"
    version = "bm25_okapi+pymorphy3@0.3"

    def rank(
        self,
        query: str,
        articles: list[EnrichedArticle],
        top_n: int,
    ) -> list[Match]:
        if not articles:
            return []
        from rank_bm25 import BM25Okapi

        corpus = [self._index_text(a) for a in articles]
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
    def _index_text(a: EnrichedArticle) -> list[str]:
        """Токенизация документа с boost'ом title ×3.

        Возвращает bag-of-words: токены title повторены _TITLE_BOOST раз
        + токены body (или snippet, если body отсутствует).
        """
        title_tokens = Bm25Matcher._tokenize(a.title)
        if a.body:
            body_tokens = Bm25Matcher._tokenize(a.body)
        elif a.snippet:
            body_tokens = Bm25Matcher._tokenize(a.snippet)
        else:
            body_tokens = []
        return title_tokens * _TITLE_BOOST + body_tokens

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Lowercase → \\w+ → stopwords filter → PyMorphy3 нормальная форма.

        Латинские/числовые токены PyMorphy3 либо распознаёт, либо возвращает
        как есть — поведение безопасное для смешанных RU/EN корпусов.
        """
        raw = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
        morph = _get_morph()
        result: list[str] = []
        for t in raw:
            if len(t) <= 1 or t in _RU_STOPWORDS:
                continue
            try:
                lemma = morph.parse(t)[0].normal_form
            except (IndexError, AttributeError):
                lemma = t
            # Доп. фильтр после леммы — лемма может попасть в stopwords
            # (например, «которая» → «который»).
            if lemma in _RU_STOPWORDS:
                continue
            result.append(lemma)
        return result


class HybridMatcher:
    """Композиция Bm25Matcher + EmbeddingMatcher через fusion (RRF или CC).

    Reciprocal Rank Fusion (Cormack, Clarke, Buettcher, SIGIR 2009):
        RRF(d) = Σᵢ 1 / (k + rankᵢ(d))

    Convex Combination (Bruch 2023, T²-RAGBench Akarsu 2026 §IV-C):
        CC(d) = α·minmax(dense_score(d)) + (1-α)·minmax(sparse_score(d))

    На T²-RAGBench (doc-002 Fig 5): CC α=0.5 → R@5=0.726 vs RRF k=60 → 0.695.
    Однако CC требует score-нормализации (min-max per ретривер), что меньше
    robust к выбросам. RRF — параметр-фри, default.

    n_candidates=50 обязательно — Figure 6 ablation: 20→R@5=0.458,
    50→0.826, 100→0.888. RusBEIR (Kovalev 2025, doc-001 Table 3):
    BM25+BGE rerank → +7.71 п.п. nDCG@10 vs BM25 alone.
    """

    name = "hybrid"
    version = "rrf+bm25+e5@0.2"

    def __init__(
        self,
        n_candidates: int = 50,
        rrf_k: int = 60,
        fusion: str = "rrf",
        cc_alpha: float = 0.5,
        bm25: Bm25Matcher | None = None,
        embedding: EmbeddingMatcher | None = None,
    ) -> None:
        if fusion not in {"rrf", "cc"}:
            raise ValueError(f"fusion must be 'rrf' or 'cc', got {fusion!r}")
        if not 0.0 <= cc_alpha <= 1.0:
            raise ValueError(f"cc_alpha must be in [0,1], got {cc_alpha}")
        self.n_candidates = n_candidates
        self.rrf_k = rrf_k
        self.fusion = fusion
        self.cc_alpha = cc_alpha
        self.bm25 = bm25 if bm25 is not None else Bm25Matcher()
        self.embedding = embedding if embedding is not None else EmbeddingMatcher()

    def rank(
        self,
        query: str,
        articles: list[EnrichedArticle],
        top_n: int,
    ) -> list[Match]:
        if not articles:
            return []

        # Тянем top-n_candidates с обоих ретриверов.
        bm25_matches = self.bm25.rank(query, articles, top_n=self.n_candidates)
        emb_matches = self.embedding.rank(query, articles, top_n=self.n_candidates)

        if self.fusion == "rrf":
            scores, article_by_url = self._rrf_fuse(bm25_matches, emb_matches)
        else:
            scores, article_by_url = self._cc_fuse(bm25_matches, emb_matches)

        if not scores:
            return []

        sorted_urls = sorted(scores, key=lambda u: -scores[u])[:top_n]
        return [
            Match(article=article_by_url[u], score=scores[u])
            for u in sorted_urls
        ]

    def _rrf_fuse(
        self,
        bm25_matches: list[Match],
        emb_matches: list[Match],
    ) -> tuple[dict[str, float], dict[str, EnrichedArticle]]:
        rrf_scores: dict[str, float] = {}
        article_by_url: dict[str, EnrichedArticle] = {}
        for rank, m in enumerate(bm25_matches, start=1):
            url = str(m.article.url)
            rrf_scores[url] = rrf_scores.get(url, 0.0) + 1.0 / (self.rrf_k + rank)
            article_by_url.setdefault(url, m.article)
        for rank, m in enumerate(emb_matches, start=1):
            url = str(m.article.url)
            rrf_scores[url] = rrf_scores.get(url, 0.0) + 1.0 / (self.rrf_k + rank)
            article_by_url.setdefault(url, m.article)
        return rrf_scores, article_by_url

    def _cc_fuse(
        self,
        bm25_matches: list[Match],
        emb_matches: list[Match],
    ) -> tuple[dict[str, float], dict[str, EnrichedArticle]]:
        """Convex combination с per-retriever min-max нормализацией.

        Doc'ы вне top-n_candidates одного ретривера получают нормированный
        score = 0 для этого ретривера. То же что doc отсутствующий в его
        ranked-списке.
        """
        bm25_norm = self._minmax_scores(bm25_matches)
        emb_norm = self._minmax_scores(emb_matches)
        article_by_url: dict[str, EnrichedArticle] = {}
        for m in bm25_matches:
            article_by_url.setdefault(str(m.article.url), m.article)
        for m in emb_matches:
            article_by_url.setdefault(str(m.article.url), m.article)
        urls = set(bm25_norm) | set(emb_norm)
        cc_scores: dict[str, float] = {}
        for u in urls:
            sparse = bm25_norm.get(u, 0.0)
            dense = emb_norm.get(u, 0.0)
            cc_scores[u] = self.cc_alpha * dense + (1.0 - self.cc_alpha) * sparse
        return cc_scores, article_by_url

    @staticmethod
    def _minmax_scores(matches: list[Match]) -> dict[str, float]:
        if not matches:
            return {}
        raw = {str(m.article.url): float(m.score) for m in matches}
        lo = min(raw.values())
        hi = max(raw.values())
        span = hi - lo
        if span <= 1e-12:
            # Все scores равны → все нормированные = 1.0 (max доступный).
            return {u: 1.0 for u in raw}
        return {u: (v - lo) / span for u, v in raw.items()}


class RerankMatcher:
    """Cross-encoder rerank поверх base matcher (default = HybridMatcher).

    Pipeline (T²-RAGBench Akarsu 2026, doc-002 §III.B; RusBEIR doc-001 §4.2):
        1. base.rank(top_n=n_candidates) — широкий recall (BM25 ∪ e5)
        2. CrossEncoder.predict([(q, title+". "+body[:1500]), ...]) — точность
        3. sort by rerank score → top_n

    Числа из ablation T²-RAGBench Figure 6 (doc-002 page 4):
        20 cand  → R@5=0.458  (relevant doc часто вне pool)
        50 cand  → R@5=0.826  ← баланс ↔ выбираем default
        100 cand → R@5=0.888  (diminishing returns + 2× latency)

    Главное достижение слоя (doc-002 Table I):
        Hybrid+Rerank R@5 = 0.816 vs Hybrid alone 0.695 (+17.4 п.п.)
        MRR@3 = 0.605 vs 0.433 (+39.7% relative)
    """

    name = "rerank"
    version = "bge-reranker-v2-m3@0.1"

    def __init__(
        self,
        base: "Matcher | None" = None,
        n_candidates: int = 50,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        max_length: int = 512,
        body_chars: int = 1500,
        batch_size: int = 16,
        _model=None,  # DI для тестов
    ) -> None:
        self.base = base if base is not None else HybridMatcher()
        self.n_candidates = n_candidates
        self.model_name = model_name
        self.max_length = max_length
        self.body_chars = body_chars
        self.batch_size = batch_size
        self._model = _model

    def _ensure_model(self):
        if self._model is None:
            from newscore.embeddings import get_reranker_model

            self._model = get_reranker_model(self.model_name, self.max_length)
        return self._model

    @staticmethod
    def _pair_text(a: EnrichedArticle, body_chars: int) -> str:
        body = a.body or a.snippet or ""
        return f"{a.title}. {body[:body_chars]}"

    def rank(
        self,
        query: str,
        articles: list[EnrichedArticle],
        top_n: int,
    ) -> list[Match]:
        if not articles:
            return []
        candidates = self.base.rank(query, articles, top_n=self.n_candidates)
        if not candidates:
            return []

        # Cross-encoder score = f(query, passage) НЕ зависит от корпуса (в
        # отличие от BM25-IDF/RRF-рангов), поэтому кэшируем per (query, pair).
        # pair_text = title + body[:N] → если статья не изменилась и query
        # тот же, берём score из Redis, НЕ прогоняем cross-encoder (главный
        # CPU-затык: ~50ms/пара). Это и есть «не матчить заново ту же новость».
        import struct

        from newscore import redis_cache

        rc = redis_cache.get_cache()
        pair_texts = [
            self._pair_text(m.article, self.body_chars) for m in candidates
        ]
        scores: list[float | None] = [None] * len(candidates)
        miss_idx: list[int] = []

        if rc.enabled:
            keys = [
                redis_cache.rerank_key(self.model_name, query, pt)
                for pt in pair_texts
            ]
            blobs = rc.mget_bytes(keys)
            for i, b in enumerate(blobs):
                if b is not None and len(b) == 4:
                    scores[i] = struct.unpack("f", b)[0]
                else:
                    miss_idx.append(i)
        else:
            miss_idx = list(range(len(candidates)))

        if miss_idx:
            model = self._ensure_model()
            miss_pairs = [(query, pair_texts[i]) for i in miss_idx]
            new_scores = model.predict(
                miss_pairs,
                batch_size=self.batch_size,
                show_progress_bar=False,
            )
            for j, i in enumerate(miss_idx):
                s = float(new_scores[j])
                scores[i] = s
                if rc.enabled:
                    rc.set_float(
                        redis_cache.rerank_key(
                            self.model_name, query, pair_texts[i]
                        ),
                        s,
                        redis_cache.TTL_RERANK,
                    )

        scored = sorted(
            zip(candidates, scores),
            key=lambda cs: -float(cs[1]),
        )
        return [
            Match(article=c.article, score=float(s))
            for c, s in scored[:top_n]
        ]
