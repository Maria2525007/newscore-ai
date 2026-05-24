"""Тесты Step 3: ExtractiveSummarizer.

Реальный sentence-transformers НЕ грузим — подменяем через monkeypatch.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from newscore.models import EnrichedArticle
from newscore.summarizer import ExtractiveSummarizer, split_sentences


def _article(body: str | None = None, snippet: str = "") -> EnrichedArticle:
    return EnrichedArticle(
        source="s",
        title="t",
        url="https://example.com/x",
        published_at=datetime(2026, 5, 20, tzinfo=timezone.utc),
        snippet=snippet,
        body=body,
        body_extracted=bool(body),
        body_extractor="trafilatura",
    )


class _FakeModel:
    """Стаб для sentence-transformers: предсказуемые эмбеддинги."""

    def __init__(self, text_to_vec: dict[str, np.ndarray]) -> None:
        self._map = text_to_vec

    def encode(self, texts, normalize_embeddings=False, **_kwargs):
        return np.array([self._map[t] for t in texts])


# ---- split_sentences ----------------------------------------------------


def test_split_sentences_basic_ru() -> None:
    text = "Курс рубля упал. Минфин выпустил облигации. ЦБ повысил ставку."
    sents = split_sentences(text)
    assert len(sents) == 3
    assert sents[0].startswith("Курс")


def test_split_sentences_empty() -> None:
    assert split_sentences("") == []
    assert split_sentences("   \n  ") == []


# ---- summarize ----------------------------------------------------------


def test_summarize_returns_none_on_empty_body_and_snippet() -> None:
    s = ExtractiveSummarizer()
    assert s.summarize("q", _article(body=None, snippet="")) is None


def test_summarize_falls_back_to_snippet_when_no_body() -> None:
    s = ExtractiveSummarizer(top_k=3, min_sentences=2)
    a = _article(body=None, snippet="Снippet короткий.")
    # 1 предложение, <= min_sentences → возвращаем как есть.
    assert s.summarize("q", a) == "Снippet короткий."


def test_summarize_returns_all_sentences_when_below_top_k(
    monkeypatch,
) -> None:
    s = ExtractiveSummarizer(top_k=5, min_sentences=2)
    a = _article(body="Первое. Второе. Третье.")
    # 3 предложения, top_k=5 → возвращаем все 3 без encode.
    out = s.summarize("q", a)
    assert out == "Первое. Второе. Третье."


def test_summarize_picks_top_k_by_relevance_to_query(monkeypatch) -> None:
    body = (
        "Первое предложение про погоду. "
        "Второе про курс валют. "
        "Третье про спорт. "
        "Четвёртое опять про курс рубля. "
        "Пятое про кулинарию."
    )
    article = _article(body=body)
    sents = split_sentences(body)
    assert len(sents) == 5

    # FakeModel: "курс" в эмбеддингах sentences 2 и 4 близок к query, остальные далеко.
    vec_query = np.array([1.0, 0.0])
    vec_close = np.array([0.99, 0.14])  # cos ≈ 0.99
    vec_far = np.array([0.0, 1.0])
    text_to_vec = {
        "query: курс валют": vec_query,
        f"passage: {sents[0]}": vec_far,
        f"passage: {sents[1]}": vec_close,
        f"passage: {sents[2]}": vec_far,
        f"passage: {sents[3]}": vec_close,
        f"passage: {sents[4]}": vec_far,
    }
    fake_model = _FakeModel(text_to_vec)
    monkeypatch.setattr(
        "newscore.summarizer.get_st_model", lambda _name: fake_model
    )

    s = ExtractiveSummarizer(top_k=2, min_sentences=2)
    summary = s.summarize("курс валют", article)
    assert summary is not None
    # Top-2 = предложения 1 и 3 (по 0-index); сохраняем порядок появления.
    assert sents[1] in summary
    assert sents[3] in summary
    # Order preserved: sent[1] идёт до sent[3] в summary.
    assert summary.index(sents[1]) < summary.index(sents[3])
    # Иные предложения НЕ включены.
    assert sents[0] not in summary
    assert sents[4] not in summary


def test_summarize_picks_first_k_when_query_relevance_tied(
    monkeypatch,
) -> None:
    body = (
        "Это первое полноценное предложение. "
        "Это второе полноценное предложение. "
        "Это третье полноценное предложение. "
        "Это четвёртое полноценное предложение."
    )
    article = _article(body=body)
    sents = split_sentences(body)
    assert len(sents) == 4

    same = np.array([1.0, 0.0])
    text_to_vec = {"query: x": same}
    for s_text in sents:
        text_to_vec[f"passage: {s_text}"] = same
    fake = _FakeModel(text_to_vec)
    monkeypatch.setattr(
        "newscore.summarizer.get_st_model", lambda _name: fake
    )

    s = ExtractiveSummarizer(top_k=2, min_sentences=2)
    summary = s.summarize("x", article)
    assert summary is not None
    # ties → argsort стабилен, первые 2 — sents[0] и sents[1].
    assert sents[0] in summary
    assert sents[1] in summary


# ---- protocol fields ----------------------------------------------------


def test_summarizer_has_name_and_version() -> None:
    s = ExtractiveSummarizer()
    assert s.name == "extractive_e5"
    assert "extractive_top3" in s.version
    assert "multilingual-e5-base" in s.version


def test_summary_field_is_mutable_on_pydantic_model() -> None:
    a = _article(body="x")
    a.summary = "set"
    assert a.summary == "set"
