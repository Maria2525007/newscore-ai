# NewsCore AI

> Briefing-first новостной агент. По NL-запросу пользователя («курс валют») собирает релевантные материалы из 5 российских деловых источников, ранжирует embedding-матчером, делает extractive summary 2–3 предложениями.
>
> Step 0 (CLI-ядро) закрыт. **Step 1–3 в разработке:** темы + scheduler (SQLite), web-интерфейс в браузере (FastAPI), summarizer без LLM API.

---

## Быстрый старт

```bash
# 1. Установка uv (если ещё нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Зависимости
uv sync

# 3. Брифинг one-shot
uv run newscore "курс валют"

# 4. Или: создать тему и открыть в браузере
uv run newscore theme create "курс валют" --period 30m
uv run newscore web                                   # http://127.0.0.1:8000
```

Первый запуск загрузит embedding-модель `intfloat/multilingual-e5-base` (~280 МБ) — это 2–3 минуты на средней сети. Дальнейшие запуски — секунды.

---

## CLI

### Step 0 — one-shot брифинг

```
uv run newscore "запрос на естественном языке" [опции]
uv run newscore briefing "запрос" [опции]            # эквивалент

опции:
  --matcher embedding|bm25     матчер (default: embedding)
  --top-n N                    сколько материалов в output (default: 10)
  --days N                     окно свежести в днях (default: 7)
  --trace                      trace в traces/<run_id>.json
  --summary/--no-summary       extractive summary (default: on)
  --log-format console|json    формат логов в stderr (default: console)
  --config PATH                путь к sources.yaml
```

### Step 1 — темы и scheduler

```
uv run newscore theme create "запрос" --period 60m   # 60s|30m|2h|1d
uv run newscore theme list
uv run newscore theme show <id>
uv run newscore theme run <id>                        # вручную сейчас
uv run newscore theme pause/resume/delete <id>
uv run newscore daemon                                # фон, обновляет по периоду
```

Состояние в `data/newscore.db` (SQLite, ignored из git).

### Step 2 — web

```
uv run newscore web --host 127.0.0.1 --port 8000
```

Создать тему через форму, посмотреть последний брифинг, запустить вручную, поставить на паузу — всё в браузере. Без авторизации, single-user локально. WAL-режим SQLite позволяет одновременно держать `web` и `daemon`.

---

## Output брифинга (one-shot)

JSON в stdout. Схема:

```json
{
  "query": "...",
  "items": [
    {
      "article": {
        "title": "...", "url": "...", "source": "rbc",
        "published_at": "...", "snippet": "...",
        "body": "...", "summary": "2-3 ключевых предложения."
      },
      "score": 0.87
    }
  ],
  "meta": {"run_id": "...", "matcher_name": "embedding", "partial": false,
           "failed_sources": [], "reason": "ok"}
}
```

Полная схема — `raw/step0-architecture.md` §3.4.

---

## Структура

| Папка | Содержимое |
|---|---|
| `backend/src/newscore/` | Python-пакет: CLI, парсер, матчер, оркестратор, summarizer |
| `backend/src/newscore/themes/` | Step 1: SQLite + ThemeService + AsyncScheduler |
| `backend/src/newscore/web/` | Step 2: FastAPI + Jinja2 templates |
| `backend/tests/` | `unit/` / `integration/` / `qualitative/` (114 тестов) |
| `configs/sources.yaml` | Конфиг 5 RSS-источников |
| `data/` | SQLite база (ignored) |
| `raw/` | Spec, architecture, brief, roadmap, baseline |
| `frontend/`, `infra/` | Заглушки для Step 4+ |

---

## Документы

Все ключевые решения зафиксированы в `raw/`:

- `mvp-brief.md` — что строим (v3)
- `step0-spec.md` — формальная спецификация (user stories, MoSCoW, NFR)
- `step0-architecture.md` — архитектура Step 0 + 17 ADR
- `step0-qual-baseline.md` — результаты qual-eval, обоснование DoD pivot
- `step1-architecture.md` — Step 1 (SQLite + scheduler) + 6 ADR
- `roadmap.md` — что наслаивается дальше (Step 4–5)

---

## Стек

| Слой | Что |
|---|---|
| Runtime | Python 3.11+ через `uv` |
| HTTP | `httpx.AsyncClient` (async fetch с per-source semaphores) |
| RSS | `feedparser` |
| Body | `trafilatura` через `asyncio.to_thread` |
| Embedding | `sentence-transformers` + `intfloat/multilingual-e5-base` |
| BM25 | `rank_bm25` (Should baseline) |
| Summary | extractive top-K по cos-similarity (тот же e5-base, без LLM API) |
| Persistence | stdlib `sqlite3`, WAL-режим |
| Scheduler | asyncio-loop в `newscore daemon` |
| Web | `fastapi` + `jinja2`, минимальный CSS |
| Tests | `pytest` + `respx` |

---

## Definition of Done

**Step 0** (закрыт 2026-05-23) — capped precision @ min(K, |expected|) ≥ 0.5 на ≥4 из 6 непустых эталонных запросов. Embedding 0.89 avg, BM25 0.47 avg. См. `raw/step0-qual-baseline.md`.

**Step 1** — тема создаётся → daemon видит её as due → запускает Step 0 → дельтит с предыдущим run → сохраняет в SQLite.

**Step 2** — в браузере: создать тему через форму, увидеть последний брифинг, запустить вручную, поставить на паузу.

**Step 3** — каждая статья в брифинге имеет `summary` 2–3 предложения, отбираемых по близости к query.
