# NewsCore AI — Research-driven decisions for Step 1→3

> Synthesis of 3 ultrasearch runs (academic literature) + Claude-research (engineering plan).
> Дата: 2026-05-26. Цель: подготовить ADR-кандидаты для Step 1 (briefing-first), Step 2 (web), Step 3 (extractive summary без LLM).
> Подробные снапшоты: `run-01-*/`, `run-02-*/`, `run-03-*/` рядом.

---

## Executive summary

| Шаг | Решение | Source |
|---|---|---|
| Step 0 retrofit | **ADR-24** — RRF hybrid (BM25+e5) + `bge-reranker-v2-m3` cross-encoder | Run 1 + Claude-research |
| Step 1 novelty | **ADR-25** — semantic novelty beyond `url_hash`: cosine threshold 1-NN (FSD baseline), затем DP-Means clustering | Run 2 (Stanford 2025) |
| Step 3 summary | **ADR-26** — extractive via Supervising Centroid Baseline + MMR redundancy | Run 3 ([S1]) |
| Step 3 importance | **Peyrard 2019 model** — formal importance function для ранжирования предложений | Run 3 ([S10]) |

**ADR-07 (`multilingual-e5-base`) НЕ меняется** — Stanford 2025 (Run 2 [S5]) использует тот же e5-base-v2 в production news tracking. Подтверждено как baseline.

---

## Run 1 — Multilingual news retrieval

**Контекст:** Step 0 `cap_precision = 0.89` (DoD pivot 2026-05-23) с e5-base only. Run 1 + Claude-research отвечают на вопрос «как доехать до 0.93–0.96 без замены embedder».

### Academic landscape (Run 1)

| Папира | DOI / arXiv | Зачем |
|---|---|---|
| **RusBEIR** (Kovalev, Tikhomirov, Kozhevnikov, Kornilov, Loukachevitch, МГУ) | arXiv:2504.12879 / 10.28995/2075-7182-2025-23-195-205 | RU IR benchmark, 17 датасетов, nDCG@10 таблица |
| **From BM25 to Corrective RAG (T²-RAGBench)** (Akarsu, Karaman, Mierbach) | arXiv:2604.01733 | Hybrid RRF + reranker → +17.4% Recall@5, +39.7% MRR@3 |
| **M3-Embedding (BGE-M3)** (Chen, Xiao, Zhang) | arXiv:2402.03216 / 10.18653/v1/2024.findings-acl.137 | 100+ языков, multi-functionality, foundation для bge-reranker |
| **mGTE** (Zhang et al., Alibaba) | arXiv:2407.19669 / 10.18653/v1/2024.emnlp-industry.103 | Long-context multilingual, для длинных news статей |
| **MILCO** (Nguyen, Lei, Ju et al.) | arXiv:2510.00671 | Cross-lingual Learned Sparse Retrieval, alt direction |

### Claude-research action plan (`raw/hybrid_search_and_cross_encoder_ranking.md`)

| Слой | Параметры | Ожидаемый прирост cap_precision |
|---|---|---|
| BM25 нормализация (PyMorphy3 лемматизация, title-boost ×3) | `bm25s` или `rank_bm25`, k1=1.5, b=0.75 | +5–10 п.п. над dirty BM25 |
| RRF hybrid с e5 | k=60, top-50+top-50 → top-30 для rerank | +2–4 п.п. над dense-only |
| Cross-encoder `bge-reranker-v2-m3` | max_length=512, batch=16, fp16=False на CPU | +3–6 п.п. (RusBEIR пруф: +5.59 п.п. nDCG@10 для mE5-large) |

**Latency budget:** ~2.5–5 c на CPU для корпуса 500–700 doc (≤ 10 c бюджет ✅).
**Лицензия:** bge-reranker-v2-m3 = Apache-2.0 ✅. Альтернативная Jina v2 multilingual = CC-BY-NC, не для прода.

### ADR-24 — Hybrid retrieval + cross-encoder rerank (кандидат)

**Контекст.** Step 0 closed на cap_precision = 0.89 с e5-base. Симптом «диффузных эмбеддингов» на коротких лексических запросах («курс валют») — классический failure mode bi-encoder.

**Решение.**
1. `BM25Okapi` с **PyMorphy3-лемматизацией**, **title-boost ×3**, NLTK Russian stopwords + `который, такой`.
2. RRF (k=60) над top-50 BM25 ∪ top-50 e5 → top-30 кандидатов.
3. `BAAI/bge-reranker-v2-m3` (Apache-2.0) через `FlagReranker` на топ-30 пар (query, title + body[:1500]).
4. Финальный top-K = 10.

**Альтернативы.**
- Convex combination α·dense + (1−α)·sparse: лучше RRF при ≥40 размеченных пар (Bruch 2023 ACM TOIS); у нас разметки нет → RRF.
- ColBERT / late-interaction: слишком много инфраструктуры.
- Замена e5-base на BGE-M3: только +0.7 п.п. на RusBEIR average; rerank даёт кратно больше.
- Fine-tune реранкера: нет данных.

**Последствия.**
- ~570 MB ONNX-int8 версия / 2.27 GB FP32 — лимит «<500 MB» нереалистичен для сильного RU реранкера.
- Latency 2.5–5 c per query, укладывается в 5–10 c.
- Должен пересдавать qual-eval после внедрения каждого слоя.

---

## Run 2 — Briefing-first novelty / topic tracking

**Контекст:** Step 1 уже спроектирован (`step1-architecture.md`): SQLite, asyncio scheduler, `url_hash = sha256(lower(url).rstrip('/'))[:32]` (ADR-21) для exact dedup. Run 2 ищет **алгоритмические upgrade** для semantic novelty.

### Academic landscape (Run 2)

| Папира | DOI / arXiv | Зачем |
|---|---|---|
| **Tracking News Narratives across Trustworthy and Worrisome Websites** (Hanley, Okabe, Durumeric, Stanford) | arXiv:2501.09102 | **e5-base-v2 + DP-Means clustering + zero-shot stance** в production — прямой match нашему стеку |
| **BERTrend: Neural Topic Modeling for Emerging Trends** (Boutaleb, Picault, Grosjean) | arXiv:2411.05930 | Dynamic weak-signal tracking, neural emerging trends — для future iteration Step 3+ |
| **How UMass-FSD Inadvertently Leverages Temporal Bias** (Wurzer, Qin) | arXiv:2208.01347 / 10.1145/3397271.3401306 | Анализ First Story Detection пайплайнов: temporal bias влияет на metrics |
| **The Nature of Novelty Detection** (Zhao, Zhang, Ma, Tsinghua 2005) | arXiv:0510054 | Formal model: novelty = partial overlap + complete overlap между предложениями |

**Foundation в traversal (не indexed):**
- TDT Pilot Study Final Report (1998) — First Story Detection как streaming task, 1-NN TF.IDF cosine
- Streaming First Story Detection with application to Twitter
- First Story Detection in TDT is hard

### Шум (false positives Run 2)

- **Z3 3HDM 3-Higgs Doublet Model** — particle physics paper случайно матчит «novelty detection» (anomaly detection в HEP). Игнорировать.
- Predicted-Updates Dynamic Model 2023 — theory of dynamic graph algorithms, не наш домен.

### ADR-25 — Semantic novelty layer over `url_hash` (кандидат)

**Контекст.** ADR-21 даёт exact dedup по URL — но не ловит:
1. Один и тот же event на разных URLs (cross-source duplication: РИА vs ТАСС про одно событие).
2. Updates той же статьи (URL тот же, тело изменилось).

**Решение.** Двухслойная новизна:
1. **Layer 1: `url_hash`** (текущий ADR-21) — exact match.
2. **Layer 2: semantic 1-NN cosine threshold** на e5-embeddings заголовков статей внутри theme history. Если max_cosine_similarity(new, history_in_window) > 0.85 → mark as duplicate-of (storing parent `url_hash`).
3. **Window:** последние `days` статей темы (тот же параметр что в Step 0).

**Альтернативы.**
- MinHash + LSH (упомянут в roadmap Step 3): хорош для exact-content dedup, не для near-duplicates с rewording.
- Full BERTopic / BERTrend: сложнее, требует больше памяти; включаем в Step 3+ если cosine threshold недостаточен.
- DP-Means clustering (Stanford 2025 [S5]): production-tested но прозрачнее как Step 4 при росте корпуса.

**Последствия.**
- Reuse existing e5-embeddings (бесплатно, embedder уже горячий).
- Расширение `articles` schema: `duplicate_of_url_hash TEXT, similarity_score REAL`.
- Threshold 0.85 — нужно валидировать на qual-eval.

---

## Run 3 — Extractive summarization без LLM

**Контекст:** Roadmap Step 3 упоминает ruT5 / YandexGPT / LLM, но решение 2026-05-24 = «НЕ платный LLM API, только локальная extractive через e5-base». Run 3 ищет конкретные алгоритмы.

### Academic landscape (Run 3)

| Папира | DOI / arXiv | Зачем |
|---|---|---|
| **Supervising the Centroid Baseline for Extractive MDS** (Gonçalves, Correia, Pernes) | arXiv:2311.17771 | **Embedding-based extractive, baseline без LLM — точный матч нашему constraint** |
| **Query-Focused MDS Survey** (Alanzi, Alballaa) | 10.14569/ijacsa.2023.0140688 | Обзор graph + clustering методов, ranking, selection, redundancy removal, evaluation |
| **A comprehensive review of ATS** (Cajueiro, Nery, Tavares et al.) | arXiv:2301.03403 | Landscape paper, систематика подходов |
| **Subtopic-driven MDS** (Zheng, Sun, Li, Muthuswamy, NTU+SAP) | 10.18653/v1/d19-1311 | Subtopic clustering перед extractive (релевант для briefing) |
| **A Simple Theoretical Model of Importance for Summarization** (Peyrard, EPFL) | 10.18653/v1/p19-1101 | Formal importance function = redundancy + relevance + informativeness |
| **Disentangling Specificity for Abstractive MDS** (Ma, Zhang, Wang et al.) | arXiv:2406.00005 | Document-specificity для MDS — для context |

**Foundation в traversal (не indexed):**
- Attention is All You Need (1706.03762)
- BERT, GPT-3, LDA, word2vec, GloVe
- TextRank, LexRank — implicitly через Query-Focused Survey

### ADR-26 — Extractive multi-document summary через centroid + MMR (кандидат)

**Контекст.** Browser-only доставка, нет LLM API, надо генерить 2-4 предложения на статью или briefing-level дайджест.

**Решение.**
1. **Centroid sentence embedding:** для статьи (или topic-cluster) вычислить centroid e5-embeddings всех предложений после chunking.
2. **Score = cos(sentence_emb, centroid)** — saliency через близость к центру.
3. **MMR redundancy filter** (λ=0.7): итеративно отбирать предложения, max-imизируя salience − λ·max_similarity_with_already_selected.
4. **Финал:** top-N (N=2–4) предложений в исходном порядке.

**Альтернативы.**
- TextRank / LexRank (graph-based): известные baselines, но centroid embedding обычно сильнее в современных evaluations (Gonçalves 2023).
- BertSumExt (supervised): требует разметки, нет у нас.
- Peyrard 2019 importance: математически чище, но centroid+MMR проще, deltaпрактикой сравним.
- Abstractive ruT5: требует prompt-инженерии или fine-tuning; outside «без LLM API» констрейнта если хост ruT5 локально (модель 220M, потребляет ~1.5 GB RAM при инференсе).

**Последствия.**
- Без новых dependencies — переиспользуем e5-base из retrieval pipeline.
- Reference-free evaluation: smooth-cohesion + factual-overlap (как proxy при отсутствии gold summaries).
- Если качество не вытягивает — fallback на extractive + abstractive postedit через локальный ruT5-base в Step 3.1.

---

## Cross-cutting open questions

1. **Cormack 2009 SIGIR (RRF foundation paper)** — пропущена Run 1 (academic query mismatch), но Claude-research её цитирует. Нужна для строгости ADR-24 — добавить в reading list manually.
2. **Lemmatization для briefing matcher** — Claude-research предлагает PyMorphy3 для BM25; нужно ли применять и для e5 embedding? Скорее нет (e5 trained на natural text), но qual-eval подтвердит.
3. **MinHash + LSH vs cosine 1-NN** — в roadmap Step 3 упомянут MinHash, но это для byte-level dedup. Cosine 1-NN — semantic. Возможно нужны оба слоя.
4. **Importance scoring для ранжирования brief items** — Peyrard 2019 формула или простой recency × source-weight × NER-сигналы (roadmap Step 3)?
5. **Cross-encoder budget на embedded-CPU**: что если развёртываем на ноутбуке c 8GB RAM? Тогда ONNX-int8 (~570 MB) обязательно.
6. **Qual-eval expansion** — текущий 6-query set явно мал для оценки 3 новых ADR. Нужно увеличить до ~30 queries (rusBEIR style) перед merging ADR-24/25/26.

---

## Tier A reading list для doc2kb / MinerU

Папиры, у которых **таблицы / формулы** существенны для принятия решения. Прогнать через `/doc2kb` с MinerU backend (лучше pymupdf4llm для math/tables).

### Retrieval (Run 1)
- `c65988a5bb39222283f2e0cf459ee87f.pdf` — RusBEIR (arXiv:2504.12879): nDCG@10 таблица на 17 датасетах
- `b6e5fb95512db2775b199a15a16bdc88.pdf` — From BM25 to Corrective RAG: T²-RAGBench tables, +17.4%/+39.7% числа
- `1b8068550e381e734206f7060ebb80a2.pdf` — M3-Embedding: self-distillation формулы
- `78b427719ce862490ebe72f5b9ef41a1.pdf` — mGTE: long-context архитектура
- `472401f175f0fa4c25543b3977def34e.pdf` — MILCO: LSR architecture diagram

### Briefing/novelty (Run 2)
- `de05a8ade3d96865e9ff888fd68adff8.pdf` — Stanford News Narratives 2025: production setup с e5-base-v2 + DP-Means + NETINF
- `1a4070d61c4d4f7301358ece86cd8076.pdf` — BERTrend: weak-signal detection algorithm
- `3c8792f593ccaf99a0840230214421d3.pdf` — UMass-FSD Temporal Bias: TF.IDF cosine formulas, temporal weighting
- `c35162100e578d15abfde09e6a15ad70.pdf` — Zhao 2005 Nature of Novelty: PO+CO model formalization

### Summary (Run 3)
- `540bed37316b59063ceeaf60b9d844bb.pdf` — Supervising Centroid Baseline: extractive algorithm + ablations
- `57d14a1970e6e201bc6c980fe6fe4dd3.pdf` — QFMS Survey: redundancy removal techniques, MMR alternatives
- `f99a284f4a0a4f76f9760b391b11e36c.pdf` — Comprehensive ATS Review: landscape

**12 PDFs total.** PDFs физически в `~/.claude/skills/ultrasearch/data/cache/pdfs/` (live cache 59 PDFs cumulative).

---

## Statistics across 3 runs

| Run | Discover | Fetch | Parse | Chunks | Total wallclock |
|---|---|---|---|---|---|
| 1 — Retrieval | 79→30 | 25/30 | 732s serial | 59 | 825s (14m) |
| 2 — Briefing | 100→30 | 30/30 ✅ | 243s (×4) | 169 | 352s (5.9m) |
| 3 — Summary | 129→30 | 22/30 | 241s (×4) | 53 | 286s (4.8m) |
| **Total** | 308→90 | 77/90 (86%) | — | 281 | **1463s (24.4m)** |

Parser parallelism (твой апдейт скилла между Run 1 и Run 2) — **3× speedup**. arXiv больше не 429-ит, fetch coverage поднялся с 83% до 100% во втором ране.

---

## Что НЕ делать (явные anti-decisions из 3 runs + Claude-research)

- ❌ Менять e5-base на BGE-M3 (выигрыш +0.7 п.п. при кратной цене). ADR-07 stable.
- ❌ ColBERT / late-interaction в Step 1–3 — слишком много инфраструктуры.
- ❌ HyDE / LLM query expansion — Akarsu 2026: «HyDE underperforms vanilla dense retrieval» на entity-centric finance queries.
- ❌ Qwen3-Reranker-0.6B на CPU — autoregressive yes/no, ×2-3 медленнее BGE-v2-m3.
- ❌ Jina-reranker-v2 в проде — лицензия CC-BY-NC, формально нельзя в commercial Step 5.
- ❌ MDPI / Frontiers / Maastricht PDFs — paywall 403; не тратить tier-2/3 fetch budget.
- ❌ Fine-tune реранкера / embedder — нет размеченных данных.

---

## Прямые ссылки на артефакты

- **Run 1:** `raw/research/run-01-multilingual-news-retrieval/{report.md, stats.json, MANIFEST.md, corpus.db, pdfs/}`
- **Run 2:** `raw/research/run-02-briefing-novelty/{report.md, stats.json, corpus.db, pdfs/}`
- **Run 3:** `raw/research/run-03-extractive-summary/{report.md, stats.json, corpus.db, pdfs/}`
- **Claude-research:** `raw/hybrid_search_and_cross_encoder_ranking.md` (action plan для ADR-24)
- **Step 1 arch:** `raw/step1-architecture.md` (ADR-18..23, существующая структура для briefing)
- **Roadmap:** `raw/roadmap.md`

Следующий шаг: прогнать Tier A PDFs через `/doc2kb` с MinerU backend для подготовки человекочитаемой knowledge base (формулы и таблицы в markdown) перед написанием финальных ADR-24/25/26.
