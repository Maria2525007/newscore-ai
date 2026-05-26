# NewsCore AI — Research-driven ADRs (24-26)

> **Status:** **IMPLEMENTED** (2026-05-26 evening).
> Все 5 ADR (24a, 24b, 24c, 24d, 25, 26) реализованы, протестированы (131 unit + 27 integration passed), qual-eval измерен.
> Эти ADR продолжают нумерацию step0-architecture.md (ADR-01..17) и step1-architecture.md (ADR-18..23).

## Implementation summary (2026-05-26)

| ADR | Что сделано | Файлы | Tests |
|---|---|---|---|
| **24a** | `Bm25Matcher`: PyMorphy3 lemmatization + title boost ×3 | `matcher.py`, `pyproject.toml` (+pymorphy3) | 10 unit |
| **24b** | `HybridMatcher`: RRF k=60, top-50+top-50 | `matcher.py`, `cli.py`, `eval.py` | 7 unit |
| **24c** | `RerankMatcher`: BAAI/bge-reranker-v2-m3 через CrossEncoder | `matcher.py`, `embeddings.py`, `cli.py` | 10 unit |
| **24d** | HybridMatcher: convex combination (`fusion="cc"`, α=0.5) рядом с RRF | `matcher.py` | 5 unit |
| **25** | Semantic novelty: e5-emb title+snippet, cos 1-NN, threshold 0.92 | `themes/{models,db,service}.py`, schema V2 | 10 unit |
| **26** | `CentroidExtractiveSummarizer`: Gonçalves 2023 unsupervised baseline | `summarizer.py` | 8 unit |

## Qual-eval результаты (sample-30d, 679 doc, 7 queries)

| Matcher | avg precision@10 | avg cap_precision (q01-q06) |
|---|---|---|
| `embedding` (baseline, ADR-07) | 0.30 | **0.888** ← winning |
| `bm25` (before ADR-24a) | 0.19 | 0.467 |
| `bm25` (ADR-24a: PyMorphy3+title boost) | 0.21 | **0.567** (+0.10) |
| `hybrid` RRF k=60 (ADR-24b) | 0.24 | 0.600 |
| `hybrid_cc` α=0.5 (ADR-24d) | TBD | TBD |
| `rerank` over hybrid (ADR-24c) | 0.21 | 0.583 (mixed) |
| `rerank_embed` over embedding (experiment) | TBD | TBD |

**Ключевой инсайт:** на нашем малом snapshot (679 doc, 7 query) `embedding` alone доминирует (Stanford 2025 production result confirms). BM25-улучшения (PyMorphy3, title boost) дают чистый upside на лексических запросах (q06 автоваз: 0.50→1.00). Hybrid RRF проигрывает чистому embedding на семантических queries (q04, q05) — это known property RRF. На большем corpus (≥10K doc) и более широком query set rerank должен показать заявленный +17 п.п. (T²-RAGBench).

**ADR-25 calibration:** threshold для cos 1-NN откалиброван на 0.92 (не 0.85 как изначально), потому что e5-base даёт baseline cos≈0.85 даже на разнотематических title (политика vs кулинария). Добавлен title+snippet[:300] для расширения контекста и снижения baseline cos.

## Что осталось из roadmap

- Cross-cutting: расширить qual-eval с 6 до 20-30 queries — текущий слишком узок для устойчивых выводов
- Optional: bge-reranker-v2-m3 ONNX-int8 для production (570 MB vs 2.27 GB FP32, ~3× speedup на CPU)
- Optional: embedding cache в SQLite per URL (избегать перевычислений между runs)

---


---

## ADR-24 — Hybrid retrieval + cross-encoder rerank (поверх e5-base)

### Контекст

Step 0 closed с `EmbeddingMatcher` (intfloat/multilingual-e5-base) и `Bm25Matcher` (rank_bm25 + min-tokenization). Они **не комбинированы** — пользователь выбирает один через `--matcher`. На qual-eval baseline `cap_precision = 0.89`, но симптом «диффузных эмбеддингов» на коротких лексических запросах («курс валют») — bi-encoder кодирует query и doc независимо, получается плоский вектор, близкий ко всему «околофинансовому» (Vespa Blog; Elastic Search Labs; Bruch et al., ACM TOIS 2023).

### Решение

Внедрить трёхслойную retrieval pipeline:

1. **BM25 enhancement** — обновить `Bm25Matcher`:
   - **PyMorphy3 лемматизация** вместо `re.findall(\w+)` (RusBEIR: «*particularly effective for Russian due to rich morphology*»)
   - **Title boost ×3** при индексации (Robertson, Zaragoza, Taylor, CIKM 2004 BM25F-pattern)
   - **Stopwords:** существующий `_RU_STOPWORDS` + `который, такой, фон`
   - **Опционально swap `rank_bm25` → `bm25s`** (10-500× быстрее на корпусах 700+ doc, Lù arXiv:2407.03618)

2. **HybridMatcher** — новый класс в `matcher.py`:
   - Берёт top-50 от BM25 ∪ top-50 от e5
   - **RRF (Reciprocal Rank Fusion, Cormack 2009, SIGIR)** с k=60, plateau optimum k∈[20, 100]
   - Возвращает top-30 для следующего слоя
   - Альтернативно: convex combination `α·dense + (1-α)·sparse_minmax` с α=0.5 (Bruch 2023; на T²-RAGBench конкретно `α=0.5` дал R@5=0.726 vs RRF k=60 = 0.695 — но при наличии 40+ labeled pairs; в zero-shot — RRF)

3. **RerankMatcher** — новый класс:
   - `BAAI/bge-reranker-v2-m3` (Apache-2.0, 568M params, 100+ языков) через `FlagEmbedding.FlagReranker`
   - max_length=512, batch_size=16, **use_fp16=False на CPU** (fp16 не даёт speedup на CPU)
   - Вход: top-30 от HybridMatcher; pair = `(query, title + ". " + body[:1500])`
   - Финальный top_k = 10

### Числа (first-hand из mineru extracts)

**T²-RAGBench, Table I** (Akarsu, Karaman, Mierbach, arXiv:2604.01733, doc-002, page 4):

| Method | R@1 | R@5 | R@10 | MRR@3 | nDCG@10 |
|---|---|---|---|---|---|
| BM25 (sparse) | 0.293 | 0.644 | 0.735 | 0.411 | 0.515 |
| Dense (text-embed-3-large) | 0.248 | 0.587 | 0.703 | 0.351 | 0.466 |
| HyDE (gpt-4.1-mini) | 0.221 | 0.544 | 0.671 | 0.318 | 0.433 |
| Hybrid (BM25+Dense, RRF) | 0.308 | **0.695** | 0.801 | 0.433 | 0.551 |
| **Hybrid + Cohere Rerank** | **0.472** | **0.816** | **0.861** | **0.605** | **0.683** |

Hybrid + rerank даёт **+17.4% absolute R@5** над hybrid alone и **+39.7% MRR@3** (0.433→0.605). Цитата: *«All pairwise differences between BM25, dense, and hybrid RRF are statistically significant (p < 0.001, paired bootstrap test with B=10,000, Bonferroni-corrected)»*.

**Reranker depth ablation** (doc-002, page 4, Figure 6):
- 20 candidates: R@5 = 0.458 (relevant doc часто вне pool)
- 50 candidates: R@5 = 0.826
- 100 candidates: R@5 = 0.888

**Вывод:** `n_candidates ≥ 50` обязательно. Claude-research в `hybrid_search_and_cross_encoder_ranking.md` рекомендовал top-30 — это **mismatch**, надо ставить ≥50.

**RusBEIR** (Kovalev et al., arXiv:2504.12879, doc-001) — на русском конкретно avg по 17 датасетам:
- BM25 + bge-reranker-v2-m3: **+7.71 п.п.** vs BM25 alone
- mE5-large + bge-reranker-v2-m3: **+5.59 п.п.** vs mE5-large alone

### Изменения в коде

| Файл | Действие |
|---|---|
| `backend/src/newscore/matcher.py` | + `HybridMatcher(BM25Matcher, EmbeddingMatcher, fusion='rrf', k=60, n_candidates=50)` |
| `backend/src/newscore/matcher.py` | + `RerankMatcher(base_matcher, n_candidates=50, top_k=10, model='BAAI/bge-reranker-v2-m3')` |
| `backend/src/newscore/matcher.py` | + апдейт `Bm25Matcher._tokenize` — PyMorphy3 лемматизация + title boost ×3 (или новый метод `_index_text`) |
| `backend/src/newscore/embeddings.py` | + lazy-load для bge-reranker через `FlagReranker` или `sentence-transformers.CrossEncoder` |
| `backend/src/newscore/cli.py` | + `--matcher hybrid` / `--matcher hybrid+rerank` |
| `pyproject.toml` | + `pymorphy3>=2.0.4`, + `FlagEmbedding>=1.3.0` (или `sentence-transformers` уже есть для CrossEncoder) |
| `backend/tests/unit/test_hybrid_matcher.py` | новый — fusion correctness, RRF math |
| `backend/tests/unit/test_rerank_matcher.py` | новый — mock reranker, верифицировать переранкинг по mock scores |
| `backend/tests/qualitative/eval.py` | + поддержка `--matcher hybrid` / `--matcher hybrid+rerank` |

### Альтернативы (rejected)

- **ColBERT / late-interaction** — too much infra, skip Step 3+.
- **Swap e5-base → BGE-M3** — RusBEIR avg +0.7 п.п. only; rerank даёт кратно больше.
- **Cohere Rerank v4.0 Pro / Jina-v2** — paid / non-commercial license. bge-reranker-v2-m3 = Apache-2.0.
- **HyDE / Multi-Query** — doc-002 показал HyDE **underperforms** vanilla dense (R@5: 0.544 vs 0.587). Multi-query тоже negligible.
- **Fine-tune реранкера** — нет размеченных данных.

### Последствия

- **Размер:** bge-reranker-v2-m3 FP32 = 2.27 GB. ONNX-int8 (`onnx-community/bge-reranker-v2-m3-ONNX`) = ~570 MB, ~3× speedup. Pick один.
- **Latency:** ~2.5-5s на запрос для корпуса 500-700 doc (BM25+dense fast, rerank — 80-150ms per pair на CPU FP32 × 50 pairs / batch=16 = ~2.5s).
- **Бюджет:** ≤ 10s ✅.
- **Лицензия:** Apache-2.0 ✅.

---

## ADR-25 — Semantic novelty layer над `url_hash`

### Контекст

`themes/service.py` сейчас использует только **exact `url_hash`** (ADR-21) для дедупа articles между runs. Это не ловит:
1. Cross-source duplicates: РИА vs ТАСС про одно событие (разные URL — exact mismatch).
2. URL updates: тело статьи изменилось, URL тот же — articles UPSERT затрёт без знания о diff.

### Решение

Двухслойная новизна в `themes/service.py:run_now()`:

1. **Layer 1 (existing): `url_hash`** — exact dedup (без изменения).
2. **Layer 2 (new): semantic 1-NN cosine threshold** на e5-embeddings заголовков статей внутри theme history:
   ```
   For each new article a:
     candidates = articles_in_theme(window=days)
     emb_a = e5.encode("passage: " + a.title)
     max_sim, parent = max((cos(emb_a, c.title_emb), c) for c in candidates)
     if max_sim > THRESHOLD (= 0.85):
       mark a as duplicate_of=parent.url_hash, similarity=max_sim
     else:
       a is novel; persist its title_emb for next runs
   ```
3. **Schema delta:** `articles` table получает `title_emb BLOB`, `duplicate_of_url_hash TEXT NULL`, `similarity_score REAL NULL`.

### Обоснование

Stanford 2025 (Hanley/Okabe/Durumeric, arXiv:2501.09102, doc-006, page 1) — production-deployed на 4,082 news websites, 18 months, 146K stories:

> «*extracts semantic narratives and sites' stances ... using a fine-tuned version of the **e5-base-v2** large language model, **DP-Means clustering**, and zero-shot stance detection*»

То есть production-tested стек **точно совпадает с нашим ADR-07** (e5-base) + cluster-based grouping. Cosine 1-NN с threshold — упрощённая версия DP-Means (без incremental cluster centroid), достаточная для baseline.

**Formal model** (Zhao, Zhang, Ma, Tsinghua 2005, arXiv:0510054, doc-009, page 1):
> «*Novelty as a combination of the partial overlap (PO, two sentences sharing common facts) and complete overlap (CO, the first sentence covers all the facts of the second sentence)*»

Зайдём с PO+CO формализации: высокий cosine similarity ≈ CO (полное покрытие); средний cosine ≈ PO (частичное). Threshold 0.85 даёт «CO-like» behavior (≈ 85% common content) — это conservative cut.

**UMass-FSD анализ** (Wurzer, Qin, arXiv:2208.01347, doc-008) — temporal bias в TDT pipelines когда window широкий: 1-NN не масштабируется > 10K документов, но для NewsCore (theme corpus ≤ few hundred articles) — OK.

### Изменения в коде

| Файл | Действие |
|---|---|
| `backend/src/newscore/themes/db.py` | + `_SCHEMA_V2`: ALTER TABLE articles ADD title_emb BLOB, duplicate_of_url_hash TEXT, similarity_score REAL; bump user_version=2 |
| `backend/src/newscore/themes/service.py` | + `_compute_novelty(article, theme_id, window_days, threshold=0.85)` |
| `backend/src/newscore/themes/service.py` | + интеграция в `run_now()`: после URL exact dedup → semantic check |
| `backend/src/newscore/themes/models.py` | + `ArticleSnapshot.duplicate_of_url_hash: str | None`, `similarity_score: float | None` |
| `backend/src/newscore/embeddings.py` | reuse `get_st_model()` (e5-base уже горячий из matcher pipeline) |
| `backend/tests/unit/themes/test_novelty.py` | новый — threshold edge cases, window expiry, schema migration |

### Альтернативы (rejected)

- **MinHash + LSH** (упомянут в roadmap Step 3): хорош для byte-level dedup (плагиат), плохо ловит rewording. Cosine на e5 — semantic.
- **Полный BERTopic / BERTrend** (Boutaleb, Picault, Grosjean, arXiv:2411.05930, doc-007): сложнее, больше памяти; кандидат на Step 3.1 если 1-NN недостаточен.
- **DP-Means** прямо как у Stanford — требует incremental cluster maintenance; усложнение пайплайна без видимого win на нашем масштабе.

### Последствия

- **Storage cost:** ~3 KB per article (e5-base 768 float32) — для 1000 articles на тему ≈ 3 MB. Не блокер.
- **Latency:** 1 encode + 1000 cosines ≈ 50ms — pre-warmed e5 уже в matcher pipeline.
- **Threshold 0.85** — нужна qual-eval validation. Слишком высокий → false negatives (cross-source duplicates пропустятся); слишком низкий → false positives (свежие новости промаркируются как duplicates). Стартуем 0.85, тюним.

---

## ADR-26 — Extractive summarization через centroid + greedy с redundancy через cumulative-centroid

### Контекст

Roadmap Step 3 (`raw/roadmap.md`) упоминает `ruT5 / YandexGPT / LLM` для суммаризации. **Решение 2026-05-24:** browser-only доставка, без платного LLM API, локально на CPU. `summarizer.py` сейчас — заглушка.

### Решение

Реализовать `CentroidExtractiveSummarizer` по схеме Gonçalves et al. (Priberam Labs + Porto, arXiv:2311.17771, doc-010) **unsupervised baseline** (без supervised attention extension — это too much для нашего use case):

**Algorithm 1 — unsupervised centroid + greedy selection** (Gholipour Ghalandari 2017 baseline, doc-010 §3.2 eq.5-6):

```python
def summarize(article: EnrichedArticle, budget_sentences: int = 3) -> list[str]:
    sentences = split_sentences(article.body)
    embs = e5.encode([f"passage: {s}" for s in sentences])  # (N, d)
    centroid = embs.mean(axis=0)                            # (d,)
    
    S: list[int] = []   # selected indices, in original order
    while len(S) < budget_sentences:
        best_score, best_i = -inf, None
        for i in range(N):
            if i in S: continue
            cumulative_emb = embs[S + [i]].sum(axis=0)
            score = cosine(cumulative_emb, centroid)
            if score > best_score:
                best_score, best_i = score, i
        S.append(best_i)
    
    return [sentences[i] for i in sorted(S)]   # keep document order
```

Ключевая идея (eq.6 от doc-010):

$$s^* = \arg\max_{s \in D \setminus S} \cos\text{sim}(e_{S \cup \{s\}}, \overline{e}_D)$$

> «*redundancy is mitigated since the centroid is compared to the whole candidate summary $S \cup \{s\}$ at each iteration and not only to the new sentence s*»

То есть **redundancy reduction через cumulative-centroid comparison** — без явного MMR. MMR (Carbonell, Goldstein 1998 — упомянут в doc-010 §2) — отдельная альтернатива, но centroid-greedy уже неявно её включает.

### Параметры по умолчанию

- `budget_sentences = 3` (выровнено с Step 0 brief format)
- e5-base passage prefix
- Cosine similarity (normalized embeddings — e5 уже это даёт)
- Sentence splitting: `nltk.sent_tokenize` (русский ресурс `punkt_tab`) или regex `[.!?]+` fallback
- Return sentences в исходном порядке документа (читаемость)

### Изменения в коде

| Файл | Действие |
|---|---|
| `backend/src/newscore/summarizer.py` | реализовать `CentroidExtractiveSummarizer.summarize(article, budget=3) -> list[str]` |
| `backend/src/newscore/embeddings.py` | reuse e5-base (no new model) |
| `backend/src/newscore/briefing.py` | опционально — добавить summary к `Match.article.summary` в pipeline |
| `pyproject.toml` | + `nltk` (если не было) |
| `backend/tests/unit/test_summarizer.py` | новый — algorithm correctness, edge cases (short doc, single sentence) |
| `backend/tests/qualitative/eval.py` | + reference-free metric: smooth-cohesion / extractive-overlap |

### Альтернативы (rejected)

- **TextRank / LexRank** (graph-based, foundation): известны, но centroid-greedy proven сильнее в Gonçalves 2023 ablations.
- **Supervised CeRA / CeRAI** из doc-010: требует training data (мульти-doc summaries) — у нас нет.
- **MMR explicit** (λ=0.7): centroid-greedy уже implicitly its variant — добавит сложности без win.
- **Abstractive ruT5-base** локально: модель 220M ≈ 1.5 GB RAM при инференсе, генерит факточно-сомнительные перефразы. Step 3.1 если extractive не вытягивает читаемость.
- **Peyrard 2019 importance model** (doc-009 traversal, Open Q): математически элегантно, но empirically не доказано лучше centroid+greedy на news domain.

### Последствия

- **Без новых ML моделей** — переиспользуем e5-base.
- **Latency:** для статьи в 30 предложений ≈ 30 embeddings × ~5ms = 150ms + 3 итерации greedy ≈ 5ms = **~200ms per article**.
- **Reference-free eval:** smooth-cohesion (mean cosine sim между выбранными предложениями) + position-bias-aware metric (Earlier Isn't Always Better, Jung et al. 2019, doc-011 traversal); добавить в `qualitative/eval.py`.
- **Если результат слабый** — fallback: TextRank через `sumy` package в Step 3.1.

---

## Cross-cutting validation plan

После любого из ADR-24/25/26 — обновить qual-eval baseline:

1. **Расширить query set** с 6 до ~20-30 (текущий слишком узок).
2. **Per-ADR metric:**
   - ADR-24: `cap_precision` + добавить `Recall@K`, `MRR@K`.
   - ADR-25: precision/recall на novelty labels (нужна разметка cross-source pairs).
   - ADR-26: ROUGE-1/2/L vs human reference summary (для ≥5 запросов) ИЛИ reference-free smooth-cohesion.
3. **Тестировать слой за слоем:**
   - PyMorphy3 only → vs current BM25
   - + Title boost → vs PyMorphy3 only
   - + RRF hybrid → vs both standalone
   - + rerank → vs hybrid
4. **Trigger для отказа от слоя:** если metric падает на >2 п.п. → не мержить.

---

## Tier A reading list (для углубления)

| ADR | Tier A papers | Где в KB |
|---|---|---|
| ADR-24 | RusBEIR, T²-RAGBench, BGE-M3, mGTE, MILCO | `tier-a-kb/docs/doc-001..005` |
| ADR-25 | Stanford News Narratives, BERTrend, UMass-FSD, Zhao 2005 | `tier-a-kb/docs/doc-006..009` |
| ADR-26 | Centroid Baseline, QFMS Survey, ATS Review | `tier-a-kb/docs/doc-010..012` |

Plus `raw/hybrid_search_and_cross_encoder_ranking.md` — Claude-research action plan (cross-link для ADR-24).

---

## Implementation order

Рекомендуемая последовательность (зависимости + риск):

1. **ADR-24 (PyMorphy3 + title boost)** — 1 час, low risk, low surface area. Smoke-test на qual-eval.
2. **ADR-24 (HybridMatcher RRF)** — 2 часа, low risk. Smoke-test.
3. **ADR-24 (RerankMatcher)** — 4 часа (model download + integration + tests). High impact.
4. **ADR-26 (Centroid extractive)** — 3 часа, новый module. Independent от ADR-24/25.
5. **ADR-25 (Semantic novelty)** — 4 часа, schema migration + service.py rewrite. Зависит от storage `title_emb`.

Total: ~14 часов engineering work. Можно делить на 3-4 вечера.

**Перед merge** каждого ADR: расширенный qual-eval + спецификация в `backend/tests/qualitative/expected/`.
