# NewsCore AI

> Briefing-first новостной агент для деловой аудитории. По NL-запросу пользователя («новости про курс валют») собирает релевантные материалы из 5 ключевых российских деловых источников.
>
> Сейчас **Step 0**: CLI-ядро. Полный продукт — см. `raw/roadmap.md`.

---

## Быстрый старт

```bash
# 1. Установка uv (если ещё нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Зависимости
uv sync

# 3. Первый прогон
uv run newscore "курс валют"
```

Первый запуск загрузит embedding-модель `intfloat/multilingual-e5-base` (~280 МБ) — это 2–3 минуты на средней сети. Дальнейшие запуски — десятки секунд.

---

## CLI

```
uv run newscore "запрос на естественном языке"

опции:
  --matcher embedding|bm25     матчер (default: embedding)
  --top-n N                    сколько материалов в output (default: 10)
  --days N                     окно свежести в днях (default: 7)
  --trace                      сохранить trace в traces/<run_id>.json
  --log-format console|json    формат логов в stderr (default: console)
  --config PATH                путь к sources.yaml (default: configs/sources.yaml)
```

---

## Output

JSON в stdout. Схема:

```json
{
  "query": "...",
  "items": [{"article": {...}, "score": 0.87}, ...],
  "meta": {"run_id": "...", "matcher_name": "embedding", "partial": false, "failed_sources": [], "reason": "ok"}
}
```

Полная схема — `raw/step0-architecture.md` секция 3.4.

---

## Структура

| Папка | Содержимое |
|---|---|
| `backend/src/newscore/` | Python-пакет: CLI, парсер, матчер, оркестратор |
| `backend/tests/` | `unit/` / `integration/` / `qualitative/` |
| `configs/sources.yaml` | Конфиг 5 RSS-источников |
| `raw/` | Исходные документы: spec, architecture, brief, roadmap |
| `docs/` | Сгенерированная KB (через `doc2kb` skill) |
| `frontend/`, `infra/` | Заглушки. Появятся в Step 2 / Step 5 |

---

## Документы

Все ключевые решения зафиксированы в `raw/`:

- `mvp-brief.md` — что строим (v3)
- `step0-spec.md` — формальная спецификация (user stories, MoSCoW, NFR)
- `step0-architecture.md` — архитектура и 11 ADR
- `sources-research.md` — выбор источников
- `roadmap.md` — что наслаивается ПОСЛЕ Step 0

---

## Стек

Python 3.11+ / `uv` / `httpx` / `feedparser` / `trafilatura` / `sentence-transformers` + `intfloat/multilingual-e5-base` / `structlog` / `typer` / `pytest`.

Без БД, без HTTP-сервиса, без Docker, без облака — на Step 0 ничего из этого не нужно. Появляется в Step 1+ (см. `raw/roadmap.md`).

---

## Definition of Done (Step 0)

- CLI запускается одной командой
- 5 источников парсятся, падение одного не валит остальные
- Embedding-матчер ранжирует материалы
- На ≥4 из 7 эталонных запросов precision@10 ≥ 0.5
- README позволяет внешнему человеку запустить за ≤5 шагов

Подробнее — `raw/step0-spec.md` секция 8.
