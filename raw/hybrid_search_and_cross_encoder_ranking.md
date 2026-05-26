# Гибридный поиск + кросс-энкодер для коротких русских запросов: что внедрять за один вечер

## TL;DR
- **Минимум-усилий-максимум-импакта:** добавить два слоя поверх существующего e5-base — **(1) BM25-гибрид через RRF (k=60)** с лемматизацией PyMorphy3 и **(2) кросс-энкодер `BAAI/bge-reranker-v2-m3`** на top-30 кандидатов. Это закрывает оба слабых места симптома «курс валют»: лексический сигнал «вытащит» документ с точным словосочетанием в кандидаты, а кросс-энкодер разорвёт сжатый кластер косинусов (0.841 / 0.820 / 0.800 / 0.796) полноценной парной attention-оценкой.
- **Реалистичный прогноз качества:** на близком домене (RusBEIR, Kovalev, Tikhomirov, Kozhevnikov, Kornilov, Loukachevitch, МГУ им. Ломоносова, Dialogue-2025 / arXiv:2504.12879) добавление `bge-reranker-v2-m3` к dense-ретриверу даёт **+4.7–5.6 п.п. nDCG@10** в среднем, а к BM25 — **+7.7 п.п.**; cross-encoder rerank в целом приносит **+5…+15 п.п. nDCG@10** на BEIR/MTEB и до +17.4 % Recall@5 / +39.7 % MRR@3 на финансовом T²-RAGBench (Akarsu, Karaman, Mierbach, arXiv:2604.01733, Apr 2026). Для вашей `cap_precision = 0.89` это означает реалистичный потолок ~0.93–0.96 после rerank, при условии что релевантный документ уже находится в top-K кандидатов.
- **Ограничение «<500 MB» нереалистично для сильного русского реранкера.** Лучший открытый мультиязычный реранкер с реальным русским качеством — `bge-reranker-v2-m3` — весит **2.27 GB (fp32) / ~1.14 GB (fp16) / ~570 MB (int8 ONNX)**. На CPU FP32 — порядка **80–150 мс на пару** при max_length=512 (HuggingFace: ~130 ms на батч из 16 пар), то есть top-30 ре-ранкинг укладывается в ~2.5–4.5 c, что вмещается в бюджет 5–10 c.

---

## Key Findings

### 1. Симптом «диффузных эмбеддингов» — это классический failure mode dense-ретривала
Vespa-команда (Vespa Blog, «Simplify Search with Multilingual Embedding Models»), Elastic Search Labs и BEIR-команда формулируют это так: bi-энкодер кодирует запрос и документ независимо, поэтому короткие vague-запросы дают «плоский» вектор, близкий ко всему «околофинансовому». BM25, наоборот, опирается на точное совпадение токенов и аккуратно отделяет «курс валют» от «нефть Ирана» и «пошлина на подсолнечное масло». На BEIR:trec-covid Vespa с линейной комбинацией e5 + BM25 подняла nDCG@10 до 0.7670; у Elastic-команды (Improving information retrieval in the Elastic Stack) показано, что в режиме «зашумлённый dense + точный BM25» weighted sum при правильной калибровке превосходит RRF, но требует ~40+ размеченных пар (Bruch et al., ACM TOIS 2023, «An Analysis of Fusion Functions for Hybrid Retrieval»). У вас разметки почти нет — поэтому **RRF (Cormack, Clarke, Büttcher, SIGIR 2009 «Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods»)** с k=60 и равными весами — стандартный «production default» в OpenSearch, Elasticsearch, Azure AI Search, MongoDB Atlas, Weaviate. Авторы оригинальной статьи прямо пишут: *«The constant k mitigates the impact of high rankings by outlier systems»* и отмечают, что оптимум плоский в k∈[20, 100].

### 2. Cross-encoder rerank — самый эффективный single ROI improvement
Парная attention в cross-encoder снимает именно то ограничение, которое мешает в вашем кейсе: оценка релевантности «курс валют» ↔ «цена на иранскую нефть» становится не косинусом двух средненных эмбеддингов, а целевой attention-сверткой над склеенной парой. Подтверждённые цифры: Akarsu et al. (arXiv:2604.01733, Apr 2026) на T²-RAGBench (23 088 запросов, 7 318 документов) фиксируют, что Hybrid RRF + Cohere Rerank v4.0 Pro даёт Recall@5 = 0.816 против 0.695 для Hybrid RRF без реранкера (**+17.4 %**), а *«MRR@3 jumping from 0.433 to 0.605 (+39.7 % relative)»*. Независимые обзоры 2025–2026 (TianPan «Cross-Encoder Reranking in Practice», BigData Boutique «RAG Reranking», LocalAIMaster) сходятся на типовом приросте **+5…+15 п.п. nDCG@10**, на «лексически тяжёлых» запросах — до +20.

На русском конкретно — в RusBEIR (Kovalev, Tikhomirov, Kozhevnikov, Kornilov, Loukachevitch, arXiv:2504.12879v1, 17 Apr 2025) усреднённые nDCG@10 по 17 датасетам:

| Система | avg nDCG@10 |
|---|---|
| BM25 (с PyMorphy3-лемматизацией) | 52.16 |
| mE5-base (ваш baseline-энкодер) | 56.43 |
| mE5-large | 60.12 |
| BGE-M3 | 61.13 |
| **BM25 + bge-reranker-v2-m3** | **59.87** (+7.71 п.п. vs BM25) |
| **mE5-large + bge-reranker-v2-m3** | **65.71** (+5.59 п.п. vs mE5-large) |
| **BGE-M3 + bge-reranker-v2-m3** | **65.85** (best overall) |

Дословная цитата из статьи: *«the best performance on the benchmark is achieved through the combination of the BGE-M3 model and the BGE reranker. Notably, the combination of mE5-large bi-encoder with the BGE reranker yields close results»*. То есть формула «mE5 + bge-reranker-v2-m3» — практически SOTA для русского, без замены базового энкодера.

### 3. Реалистичные размеры моделей и CPU-латентность

| Модель | Params | Disk fp32 | License | Multilingual / RU | CPU latency на пару (max_len=512) |
|---|---|---|---|---|---|
| **BAAI/bge-reranker-v2-m3** | 568M | 2.27 GB (fp16 ≈ 1.14 GB; int8 ONNX ≈ 570 MB) | Apache-2.0 | да, foundation BGE-M3 поддерживает 100+ языков (Novita AI говорит «18+», карточка BAAI/bge-m3 — «100+ working languages»); русский явно перечислен | ~80–150 ms (FP32, batch=16: ~130 ms / батч, эффективно ≈ 8 ms/пара) |
| BAAI/bge-reranker-base | 278M | ~1.1 GB | Apache-2.0 | **только en/zh** — не подходит для русского | ~50 ms |
| jinaai/jina-reranker-v2-base-multilingual | 278M | ~1.1 GB | **CC-BY-NC-4.0** (research/eval) | да, 100+ языков; быстрее v2-m3 ×15 с Flash Attention 2 (на CPU выигрыш меньше) | ~30–60 ms на CPU |
| Qwen/Qwen3-Reranker-0.6B | 0.6B | ~1.2 GB (GGUF) / ~2.4 GB (fp32) | Apache-2.0 | да, 100+ языков | ~250–400 ms (causal LM «yes/no» подход дороже SeqCls) |
| mixedbread-ai/mxbai-rerank-base-v2 | 0.5B | ~2 GB | Apache-2.0 | да, 100+ языков (mxbai-rerank-base-v2 BEIR 55.57, Mr.TyDi 28.56) | ~150 ms на CPU |
| cross-encoder/ms-marco-MiniLM-L-6-v2 | 22M | ~90 MB | Apache-2.0 | **только en** — не подходит | ~5 ms |

**Под ваш «<500 MB» реально только int8-ONNX версия `bge-reranker-v2-m3` (~570 MB) или MiniLM, но MiniLM не знает русского. Честный ответ: в полностью открытом стеке нет реранкера <500 MB с хорошим русским.** Идите на компромисс: либо 2.27 GB FP32 / 1.14 GB FP16 BGE-v2-m3, либо ONNX-int8 (~570 MB), либо research-only Jina v2 multilingual (~1.1 GB).

### 4. Параметры по умолчанию (не нужно ничего тюнить)

- **RRF:** `k=60` (Cormack 2009; «optimum is flat in k∈[20, 100]»). Брать **top-50 из BM25 и top-50 из e5**, объединять, оставлять для реранкинга **top-30**. На корпусе 500–700 документов top-50 покрывает ~7–10 % коллекции и почти всегда содержит все релевантные.
- **Convex combination как альтернатива RRF:** `score = α·dense + (1−α)·sparse_minmax`, **α=0.5** по умолчанию (Bruch et al., 2022, ACM TOIS: α=0.5 устойчиво лучше RRF при наличии 40+ размеченных пар; в чисто zero-shot — RRF). Для **коротких лексических запросов типа «курс валют» сместите α к 0.4** (больше веса BM25). Без разметки — оставайтесь на RRF.
- **Top-K для rerank:** **30** — баланс между качеством и латентностью. На T²-RAGBench (Akarsu et al., arXiv:2604.01733) Recall@5 продолжает заметно расти при увеличении кандидатов до 50–100, затем плато; для корпуса 500–700 30–50 — золотая середина.
- **max_length=512** для cross-encoder (это hard-limit `bge-reranker-v2-m3`), **batch_size=8 или 16** на CPU. Подавать reranker'у строку `title + ". " + body[:первые ~400 токенов]` — обычно полезной информации в первых двух абзацах новости больше чем достаточно.

### 5. Дешёвые добавки специфичные под news-домен

- **Лемматизация PyMorphy3 для BM25 — обязательно.** Recipe из RusBEIR (Kovalev et al., раздел 4.1):
  1. Lowercasing;
  2. Удаление пунктуации (regex `[^\w\s]`);
  3. Нормализация пробелов;
  4. Токенизация;
  5. **Лемматизация PyMorphy3** — «*particularly effective for the Russian language due to its rich morphology, as it avoids the inaccuracies that stemming introduces by truncating words without context*»;
  6. Stopwords: NLTK Russian + `который`, `такой`.
  
  Без лемматизации BM25 на русском теряет ~10–15 п.п. на словоформах. Это самый дешёвый и обязательный апгрейд BM25. Пакет `bm25s` (Xing Han Lù, arXiv:2407.03618) даёт скорость на порядки выше `rank_bm25` и встроенный токенизатор/стеммер.
- **Title-boost через BM25F-pattern:** склеить документ как `(title + " ") * 3 + body` перед индексацией BM25 (Robertson, Zaragoza, Taylor, CIKM 2004 «Simple BM25 extension to multiple weighted fields» — это математически эквивалентно полной формулировке BM25F и не ломает нелинейность TF-saturation). Эффект на news ощутимый: «курс валют» в заголовке статьи про курсы валют почти гарантирует попадание в top-50 BM25.
- **Separate title/body embedding с weighted sum:** `score = 0.4·cos(q, title_emb) + 0.6·cos(q, body_emb)` иногда даёт +1–2 п.п. precision@5 на news; стоит только удвоения индекса и embed-вызова. Делать, только если успеете прогнать qual-eval.
- **Pseudo-relevance feedback / RM3:** в теории сильный baseline (BM25+RM3 близок к нейронным baselines на TREC, Jaleel et al. 2004), но требует тюнинга количества expansion-терминов и риск topic drift на «курс валют» (расширится в «доллар нефть инфляция»). На 3 дня — **пропустить**.
- **Score-gap thresholding:** после reranker'а отбрасывать всё после первого gap >0.15 в нормализованных скорах. Микроулучшение для cap_precision (метрика штрафует false positives после правильного top-K).

---

## Details: рабочий код

Зависимости (уже в стеке кроме лемматизатора и реранкера):
```bash
uv add pymorphy3 FlagEmbedding
# опционально: uv add bm25s  # быстрее rank_bm25 в 10-500x
```

### Шаг 1 — нормализация для BM25 (Russian-aware)

```python
import re
import pymorphy3
from nltk.corpus import stopwords

_morph = pymorphy3.MorphAnalyzer()
_STOP = set(stopwords.words("russian")) | {"который", "такой"}
_TOKEN_RE = re.compile(r"[^\w\s]", re.UNICODE)

def normalize_ru(text: str) -> list[str]:
    text = _TOKEN_RE.sub(" ", text.lower())
    tokens = []
    for w in text.split():
        if w in _STOP or w.isdigit():
            continue
        lemma = _morph.parse(w)[0].normal_form
        if lemma not in _STOP and len(lemma) > 1:
            tokens.append(lemma)
    return tokens
```

### Шаг 2 — индексация: title-boost + лемматизация

```python
from rank_bm25 import BM25Okapi
import numpy as np

TITLE_BOOST = 3

def build_bm25(docs):  # docs: list[dict(title, body)]
    tokenized = [
        normalize_ru((d["title"] + " ") * TITLE_BOOST + d["body"])
        for d in docs
    ]
    return BM25Okapi(tokenized, k1=1.5, b=0.75)
```

### Шаг 3 — RRF-гибрид

```python
def rrf_fuse(rank_lists: list[list[int]], k: int = 60) -> list[tuple[int, float]]:
    scores: dict[int, float] = {}
    for ranked in rank_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])

def hybrid_retrieve(query, e5_model, doc_embs, bm25, n_candidates=50):
    # dense
    q_emb = e5_model.encode("query: " + query, normalize_embeddings=True)
    dense_scores = doc_embs @ q_emb
    dense_top = np.argsort(-dense_scores)[:n_candidates].tolist()
    # sparse
    q_tokens = normalize_ru(query)
    sparse_scores = bm25.get_scores(q_tokens)
    sparse_top = np.argsort(-sparse_scores)[:n_candidates].tolist()
    # fuse
    fused = rrf_fuse([dense_top, sparse_top], k=60)
    return [doc_id for doc_id, _ in fused]
```

### Шаг 4 — cross-encoder rerank top-30

```python
from FlagEmbedding import FlagReranker

# fp16 не даёт ускорения на CPU; оставить False
reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=False)

def rerank(query, candidate_ids, docs, top_n=30, max_length=512):
    cands = candidate_ids[:top_n]
    pairs = [
        [query, docs[i]["title"] + ". " + docs[i]["body"][:1500]]
        for i in cands
    ]
    scores = reranker.compute_score(
        pairs, batch_size=16, max_length=max_length, normalize=True
    )
    order = sorted(range(len(cands)), key=lambda j: -scores[j])
    return [cands[j] for j in order]
```

### Шаг 5 — собранный pipeline

```python
def search(query, e5_model, doc_embs, bm25, docs, final_k=10):
    candidates = hybrid_retrieve(query, e5_model, doc_embs, bm25, n_candidates=50)
    reranked = rerank(query, candidates, docs, top_n=30)
    return reranked[:final_k]
```

### Альтернатива fusion — convex combination (если хотите попробовать α-тюнинг)

```python
def minmax(x):
    x = np.asarray(x, dtype=np.float32)
    lo, hi = x.min(), x.max()
    return (x - lo) / (hi - lo + 1e-9)

def convex_fuse(dense_scores, sparse_scores, alpha=0.5):
    return alpha * minmax(dense_scores) + (1 - alpha) * minmax(sparse_scores)
```
Для коротких запросов начать с **α=0.4**, сравнить с RRF на вашем qual-eval.

---

## Оценка латентности на корпусе 500–700 документов (CPU)

| Стадия | Время |
|---|---|
| Query e5 embed (1 запрос) | ~30–60 ms |
| Dense cos against 700 docs | <5 ms (precomputed matrix) |
| BM25 query (rank_bm25, 700 docs) | ~10–30 ms |
| RRF fuse | <1 ms |
| Cross-encoder rerank 30 пар (`bge-reranker-v2-m3`, FP32, max_len=512, batch=16) | ~2.4–4.5 c (~80–150 ms × 30 пар через батчи) |
| **Итого** | **~2.5–5 c** |

Это умещается в ваш бюджет 5–10 c. Если хотите запас — используйте **ONNX-int8 версию `onnx-community/bge-reranker-v2-m3-ONNX`** (sentence-transformers документация по efficiency даёт «ONNX with int8 quantization is even stronger with a 3.08× speedup»): даёт ~3× speedup и ~570 MB на диске.

---

## Recommendations (приоритеты под 3 дня)

**Вечер 1 (обязательно, ~3 часа):**
1. Заменить «примитивную токенизацию + ru-stopwords» в BM25 на `normalize_ru()` (PyMorphy3 + правильный stopword-список). Ожидаемый прирост BM25 alone: **+5–10 п.п.** cap_precision (с 0.47 в район 0.55–0.60).
2. Включить title-boost = 3 в индексации BM25.
3. Добавить RRF (k=60, top-50 + top-50) над существующим e5 и обновлённым BM25. Ожидаемый прирост cap_precision: **+2–4 п.п.** над dense-only baseline 0.89 → ~0.91–0.93. Это уже решает симптом «курса валют» — BM25 точно пушит в top-K документ с буквальным совпадением.

**Вечер 2 (главный апгрейд, ~3 часа):**
4. Поднять `bge-reranker-v2-m3` через `FlagReranker`. Прогнать на 30–50 запросах qual-eval, сравнить cap_precision до/после. Ожидаемый прирост: **+3–6 п.п.** поверх hybrid → ~0.94–0.97.
5. Зафиксировать `n_candidates=50`, `top_n=30`, `max_length=512`, `batch_size=16`.

**Вечер 3 (полировка):**
6. Если латентность поджимает — конвертировать реранкер в ONNX-int8 (Optimum + ONNX Runtime) или взять `onnx-community/bge-reranker-v2-m3-ONNX`.
7. Если cap_precision на коротких queries всё ещё не догоняет — попробовать convex fusion с α=0.4 вместо RRF.
8. Добавить score-gap threshold: отбрасывать всё после первого скачка >0.15 в нормализованных reranker-скорах.

**Что НЕ делать в эти 3 дня:**
- ColBERT / late-interaction — слишком много инфраструктуры.
- Fine-tune реранкера — нет данных.
- HyDE / LLM query expansion — out of scope и underperforms на entity-centric финансовых запросах (Akarsu et al., arXiv:2604.01733 явно: «HyDE underperforms vanilla dense retrieval»).
- Менять базовый энкодер на BGE-M3 — выигрыш только +0.7 п.п. в среднем на RusBEIR (61.13 vs 60.12), при том что у rerank выигрыш кратно больше.
- Qwen3-Reranker-0.6B на CPU — медленнее BGE-v2-m3 (~250–400 мс/пара из-за autoregressive yes/no decoding), хуже latency-budget.

**Триггеры для отказа от плана:**
- Если CPU-латентность реранкера на вашей машине превысит 8 c на запрос — откатиться на `top_n=15` или ONNX-int8.
- Если cap_precision **падает** после rerank — релевантного документа нет в top-50 кандидатов (recall-проблема, не precision-проблема): увеличить `n_candidates` до 100 и проверить лемматизацию BM25.

---

## Caveats

- Все цифры RusBEIR — это **average по 17 разнодоменным датасетам**, ваш домен (свежие RSS-новости по бизнесу) отличается: меньше длинных документов, больше дубликатов между источниками, named entities (компании, валюты) часто решают всё. **Прирост на вашем эвале может быть как больше (15+ п.п.), так и меньше — обязательно прогоните qual-eval.**
- В корпусе 500–700 документов BM25 шумнее, чем на больших коллекциях — IDF плохо оценивается. Лемматизация и stopword removal критичны. Рассмотрите `bm25s` (arXiv:2407.03618) вместо `rank_bm25` (тот же API, в 10–500× быстрее, лучше токенизатор).
- **Лицензия Jina v2 (CC-BY-NC-4.0)** — формально нельзя в коммерческой продуктивной системе; для академической защиты ОК, но если потом будете показывать на конференции / в портфолио как «реальный продукт» — лучше сразу `bge-reranker-v2-m3` (Apache-2.0).
- `bge-reranker-v2-m3` ограничен **512 токенов на пару**; на длинных Forbes/Коммерсант статьях вы передаёте title + начало тела. Для большинства запросов «о чём статья» этого хватает; для запросов «найди в статье X конкретный факт Y» — нет, но это не ваш use case.
- Cap_precision не показывает recall-потолок. Если BM25 + e5 вместе не нашли релевантный документ в top-50 — реранкер не спасёт. Мониторьте Recall@50 как sanity-check.
- Цифры «+17.4 % Recall@5» и «+39.7 % MRR@3» из Akarsu et al. (arXiv:2604.01733, Apr 2026) получены на T²-RAGBench с **платным Cohere Rerank v4.0 Pro**, а не с `bge-reranker-v2-m3`; они задают верхнюю планку «что приносит reranking как этап», а не нижнюю оценку конкретно для bge.
- Прогноз ~0.93–0.96 cap_precision основан на пропорциях из RusBEIR/BEIR/T²-RAGBench, не на прямом эксперименте на вашем корпусе — это инженерная оценка, а не гарантия.
- Все упомянутые «независимые обзоры» (TianPan, BigData Boutique, LocalAIMaster, Markaicode, AIMultiple) — это инженерные блоги, не peer-reviewed; используйте их для ориентира по латентности и относительному ранжированию моделей, но не как первоисточник цифр. Первоисточники для качества — это RusBEIR (МГУ, Dialogue-2025), Cormack 2009 (SIGIR), Bruch 2023 (ACM TOIS), Akarsu 2026 (arXiv), и карточки моделей на HuggingFace.