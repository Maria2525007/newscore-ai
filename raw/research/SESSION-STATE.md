# Session state — research → ADR drafts → implementation (2026-05-26)

> **Status (evening update):** все 6 ADR (24a, 24b, 24c, 24d, 25, 26) **реализованы**, протестированы (164 теста: 131 unit + 27 integration + 6 e2e — все зелёные), qual-eval измерен. Детали — `raw/research-driven-adrs.md`. Полные snapshot'ы — `backend/tests/qualitative/reports/`.

## Финальное ранжирование matchers (sample-30d, 679 doc, 7 queries)

| # | Matcher | avg cap_p (q01-q06) | comment |
|---|---|---|---|
| 1 | embedding (ADR-07 baseline) | **0.888** | winner на семантических queries — Stanford 2025 confirm |
| 2 | hybrid_cc α=0.5 (ADR-24d) | 0.625 | best fusion-only, q04 +0.25 |
| 3 | hybrid RRF k=60 (ADR-24b) | 0.600 | parameter-free baseline |
| 4 | rerank-on-hybrid (ADR-24c) | 0.583 | hurt by sparse-only docs not in pool |
| 5 | bm25 (ADR-24a PyMorphy3) | 0.567 | +0.10 vs raw bm25 |
| — | bm25 (raw, baseline) | 0.467 | reference |

Default matcher в Theme и CLI остаётся **`embedding`** — все новые опции доступны через `--matcher {hybrid,hybrid_cc,rerank,rerank_embed}` но не default.

## Что merge-ready (по уровню риска)

- ✅ **ADR-24a** (PyMorphy3 + title boost) — чистый upside, 0 регрессий. **Merge first.**
- ✅ **ADR-25** (semantic novelty, threshold 0.92) — изолированная feature, schema V2 migration tested.
- ✅ **ADR-26** (CentroidExtractiveSummarizer) — новый module, не трогает existing pipeline.
- ⚠️ **ADR-24b/c/d** — как опции в CLI, default остаётся `embedding`. Полная польза проявится на ≥10K corpus.

## TODO (post-implementation)

- Расширить qual-eval snapshot с 7 до 20-30 queries (cross-cutting prerequisite для всех validations)
- bge-reranker-v2-m3 ONNX-int8 (570 MB vs 2.27 GB FP32, ~3× speedup) — production optimization
- Embedding cache в SQLite per URL (избегать re-encode между runs)
- Возможно: интеграция CentroidExtractiveSummarizer в theme_digest pipeline (briefing.py использует ExtractiveSummarizer query-focused)

---

> Этот файл — точка восстановления после `/compact`. Тут весь in-memory контекст исследовательской сессии плюс приоритизированный TODO для продолжения.

---

## 1. Что было сделано в этой сессии

### Ultrasearch (3 runs, academic literature)

| # | Query | Out | Snapshot |
|---|---|---|---|
| 1 | `multilingual dense retrieval news short query long document hybrid BM25 e5 BGE` | `run-01-*/report.md` | `raw/research/run-01-multilingual-news-retrieval/` (28 PDFs, 47 MB) |
| 2 | `personalized news briefing novelty detection redundancy temporal deduplication topic tracking incremental update` | `run-02-*/report.md` | `raw/research/run-02-briefing-novelty/` |
| 3 | `extractive summarization news multi-document embeddings TextRank LexRank MMR sentence selection reference-free evaluation` | `run-03-*/report.md` | `raw/research/run-03-extractive-summary/` |

Параллелизм parse'а в ultrasearch заработал между Run 1 и Run 2 (apply user'ом) — 3× speedup. arXiv больше не 429-ит.

### doc2kb (Tier A — 12 PDFs)

Прогнаны через `mineru-vlm@3.2.0` backend `vlm-auto-engine` (MLX MPS), `--keep-raw` для возможного Popo постпроцесса.

- **Time:** 66 мин wallclock (M5 Pro 24GB, ~15-20 s/page)
- **Output:** `raw/research/tier-a-kb/` (96 MB total)
  - `docs/` — 12 markdown (1.2 MB)
  - `assets/` — 202 jpeg (22 MB, diagrams + tables-as-images)
  - `_mineru/` — 73 MB raw VLM cache (можно удалить если Popo не планируется)
  - `AGENTS.md` + `INDEX.md` + `manifest.json` + `llms.txt` — навигация для next-session agent
- **Quality:** 0 warnings / 0 errors / 351,881 tokens total
- **Baseline для compare:** `raw/research/tier-a-kb-pymupdf-baseline/` (быстрый, но ligatures + dropped_pictures)

### Code survey

Backend (`/Volumes/Dev/newscore-ai/backend/src/newscore/`):
- ✅ **Step 0 closed**: `matcher.py` (EmbeddingMatcher e5-base + Bm25Matcher), `parser.py`, `briefing.py`, `cli.py`, `models.py`, `embeddings.py`, `dedupe.py`, `cache.py`
- ✅ **Step 1 ПОЛНОСТЬЮ написан**: `themes/{models,db,service,scheduler,cli}.py` (ADR-18..23 реализованы)
- ✅ **Step 2 начат**: `web/app.py` (FastAPI + Jinja2 templates, themes CRUD из браузера)
- ✅ Tests: `unit/themes/`, `integration/test_theme_cli.py`, `e2e/test_theme_flow.py`, `qualitative/eval.py`
- ❌ **Не написано**: hybrid matcher, cross-encoder rerank, semantic novelty layer, extractive summarizer (`summarizer.py` — заглушка)

### Артефакты-результаты (документация)

| Файл | Назначение |
|---|---|
| `raw/research/CONSOLIDATED-BRIEF.md` | Синтез 3 ultrasearch + Claude-research + проектный контекст. Decision map. |
| `raw/research-driven-adrs.md` | **Draft ADR-24/25/26** с first-hand цитатами + привязкой к файлам кода + implementation order |
| `raw/research/tier-a-kb/` | Готовая doc2kb knowledge base для feeding в следующую сессию |
| `raw/hybrid_search_and_cross_encoder_ranking.md` | (от пользователя) Inженерный action plan для retrieval — cross-link для ADR-24 |

---

## 2. Принятые research decisions (короткая выжимка)

### ADR-07 (e5-base) — confirmed, не менять

Stanford 2025 (Hanley/Okabe/Durumeric, arXiv:2501.09102) production-deployed e5-base-v2 + DP-Means clustering + zero-shot stance на 4082 news sites за 18 месяцев → 146K stories. **Прямое подтверждение** нашего ADR-07.

### ADR-24 — Hybrid retrieval + cross-encoder rerank

- BM25 enhancement: **PyMorphy3 лемматизация** + **title boost ×3** + `bm25s` (опц., 10-500× speedup)
- HybridMatcher: **RRF** (Cormack 2009) с k=60, top-50+top-50 → top-50 кандидатов для следующего слоя (ablation T²-RAGBench: 20→R@5=0.458, **50→0.826**, 100→0.888)
- RerankMatcher: `BAAI/bge-reranker-v2-m3` (Apache-2.0, 568M, FlagReranker), batch=16, max_length=512, fp16=False на CPU. Финальный top_k=10
- Latency ~2.5-5s/query (бюджет 10s ✅)
- T²-RAGBench Table I: Hybrid+Rerank R@5=0.816 vs hybrid alone 0.695 (+17.4 п.п.), MRR@3 0.605 vs 0.433 (+39.7%)
- RusBEIR avg: BM25+bge-reranker +7.71 п.п. nDCG@10, mE5-large+bge-reranker +5.59 п.п.

### ADR-25 — Semantic novelty layer над `url_hash`

- Текущий `themes/service.py` использует только exact `url_hash` (ADR-21) — не ловит cross-source duplicates и URL updates
- Добавить cosine 1-NN threshold на title embeddings: `if max_cos(new, history_in_window) > 0.85 → mark duplicate_of=parent`
- Schema `_SCHEMA_V2`: ALTER TABLE articles ADD title_emb BLOB, duplicate_of_url_hash TEXT, similarity_score REAL; bump user_version=2
- Формальная база: Zhao 2005 PO+CO model (partial+complete overlap)
- Stanford 2025 уже использует DP-Means с e5-base — наш cosine 1-NN это упрощённая baseline-версия

### ADR-26 — Extractive summarization через centroid + greedy

- `summarizer.py` сейчас заглушка → реализовать `CentroidExtractiveSummarizer`
- Algorithm (Gonçalves 2023, arXiv:2311.17771, **unsupervised baseline** без supervised attention extension)
- Greedy с **cumulative-centroid** comparison: `s* = argmax cos(e_{S∪{s}}, centroid)` → redundancy reduction implicit (не нужен явный MMR)
- ~200ms/article, переиспользуем e5-base
- Reference-free eval: smooth-cohesion + position-bias-aware (Earlier Isn't Always Better)
- Без LLM API (Step 3 constraint)

---

## 3. TODO (приоритизировано, состояние на 2026-05-26)

### Completed (текущая сессия)
- [x] Ultrasearch Run 1/2/3
- [x] Snapshot Run 1/2/3 в `raw/research/`
- [x] CONSOLIDATED-BRIEF.md
- [x] Code survey (Step 0/1/2 mapping)
- [x] doc2kb scout + mineru-vlm extract 12 Tier A
- [x] build_manifest для tier-a-kb
- [x] Draft ADR-24/25/26 в `research-driven-adrs.md`

### Pending — implementation (требует решения пользователя)

**Implementation order (~14h total):**

1. **ADR-24a (1h, low risk)** — обновить `Bm25Matcher`:
   - `matcher.py:_tokenize()` → PyMorphy3 лемматизация вместо `re.findall(\w+)`
   - Добавить title-boost ×3 в `Bm25Matcher.rank()` (склейка `title*3 + body` перед токенизацией)
   - `pyproject.toml`: + `pymorphy3>=2.0.4`
   - `tests/unit/test_bm25_matcher.py`: расширить кейсы морфологии (падежи)
   - qual-eval smoke-test → cap_precision before/after

2. **ADR-24b (2h, low risk)** — `HybridMatcher` в `matcher.py`:
   - Композиция BM25Matcher + EmbeddingMatcher
   - RRF (k=60), top-50+top-50 → output top-50
   - `cli.py`: + `--matcher hybrid`
   - `tests/unit/test_hybrid_matcher.py`: RRF math correctness
   - qual-eval

3. **ADR-24c (4h, high impact)** — `RerankMatcher`:
   - Lazy-load `BAAI/bge-reranker-v2-m3` через `FlagEmbedding.FlagReranker` (или `sentence-transformers.CrossEncoder` если уже в deps)
   - `pyproject.toml`: + `FlagEmbedding>=1.3.0`
   - `embeddings.py`: новая функция `get_reranker_model()`
   - `cli.py`: + `--matcher hybrid+rerank`
   - `tests/unit/test_rerank_matcher.py`: mock reranker, верифицировать переранкинг
   - Bandwidth check: ~570 MB ONNX-int8 или 2.27 GB FP32

4. **ADR-26 (3h, independent)** — `CentroidExtractiveSummarizer` в `summarizer.py`:
   - Sentence splitting (NLTK `sent_tokenize` или regex fallback)
   - e5-base embeddings всех предложений
   - Greedy selection с cumulative-centroid (algorithm 1 из ADR doc)
   - Опционально интеграция в `briefing.py` → `Match.article.summary`
   - `tests/unit/test_summarizer.py`: short doc, single sentence, budget edge cases

5. **ADR-25 (4h, schema migration)** — semantic novelty в `themes/`:
   - `themes/db.py:_SCHEMA_V2` — ALTER TABLE articles ADD title_emb BLOB, duplicate_of_url_hash TEXT, similarity_score REAL; bump user_version=2
   - `themes/models.py` — `ArticleSnapshot.{duplicate_of_url_hash, similarity_score}`
   - `themes/service.py:run_now()` — добавить `_compute_novelty(article, theme_id, window_days, threshold=0.85)` после exact dedup
   - `tests/unit/themes/test_novelty.py`: threshold edge cases, window expiry, migration

### Cross-cutting (после ADR-24)

- **Расширить qual-eval** с 6 до 20-30 queries (текущий слишком узок для оценки 3 новых ADR)
- Per-ADR metric:
  - ADR-24: `cap_precision` + `Recall@K`, `MRR@K`
  - ADR-25: precision/recall на novelty labels (нужна разметка cross-source pairs — 10-20 пар достаточно)
  - ADR-26: smooth-cohesion + reference-free position-bias check
- Trigger отказа от слоя: если metric падает на >2 п.п. → не мержить

### Опционально (cleanup)

- `rm -rf raw/research/tier-a-kb/_mineru/` — освободит 73 MB, если MinerU-Popo postprocess не планируется
- Удалить `/tmp/newscore-research/` — там копии 3 reports которые уже в snapshot'ах
- Удалить `/tmp/mineru-loop.sh` — runner script

---

## 4. Где смотреть first-hand цитаты

| Тема | KB doc | Ключевые страницы / разделы |
|---|---|---|
| Hybrid+Rerank numbers | `tier-a-kb/docs/doc-002-*.md` | Table I (стр.4), Section IV.A "Main Retrieval Results", ablations IV.C |
| RU IR benchmark | `tier-a-kb/docs/doc-001-*.md` | Abstract + Section 3 Datasets, sections 4-5 (results) |
| BGE-M3 self-distillation | `tier-a-kb/docs/doc-003-*.md` | Section 3 Methodology |
| Stanford prod stack | `tier-a-kb/docs/doc-006-*.md` | Section 1 Introduction (page 1), Section 3.3 System Architecture |
| BERTrend algorithm | `tier-a-kb/docs/doc-007-*.md` | Section 3 Methodology |
| Zhao PO+CO formalism | `tier-a-kb/docs/doc-009-*.md` | Section 3.1 The two relations |
| Centroid + greedy algorithm | `tier-a-kb/docs/doc-010-*.md` | Section 3.2 Sentence Selection (eq.5-6) |
| QFMS methods overview | `tier-a-kb/docs/doc-011-*.md` | Sections: ranking, selection, redundancy removal |

Загружать только нужное — по `INDEX.md` или `manifest.json`.

---

## 5. Известные gaps (анти-decisions)

Подтверждены HyDE underperforms (T²-RAGBench Table I: 0.544 vs 0.587 dense), Multi-Query negligible, ColBERT слишком много infra, замена e5→BGE-M3 не оправдана (+0.7 п.п. RusBEIR avg), Cohere/Jina нельзя по лицензии, fine-tune реранкера — нет данных.

`bge-reranker-base` (en/zh only) **не подходит** для RU — обязательно `bge-reranker-v2-m3` (Apache-2.0).

---

## 6. Команды для восстановления

После compact'а — выполнить:
```bash
# 1. Проверка артефактов на месте
ls -la /Volumes/Dev/newscore-ai/raw/research/
cat /Volumes/Dev/newscore-ai/raw/research/SESSION-STATE.md | head -50
cat /Volumes/Dev/newscore-ai/raw/research-driven-adrs.md | head -80

# 2. Проверка mineru KB
cat /Volumes/Dev/newscore-ai/raw/research/tier-a-kb/INDEX.md

# 3. Текущее состояние backend
ls /Volumes/Dev/newscore-ai/backend/src/newscore/
ls /Volumes/Dev/newscore-ai/backend/src/newscore/themes/
```
