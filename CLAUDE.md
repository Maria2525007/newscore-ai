# NewsCore AI — Project Context for AI Assistants

## Что за проект

NewsCore AI — briefing-first новостной агент. Учебный проект **ИТМО ФТМИ**. Сейчас **Step 0**: CLI-ядро, парсер 5 RSS-источников + embedding-матчер по NL-запросу.

**Не путать Step 0 с полным продуктом.** Полный продукт описан в `raw/roadmap.md`. На Step 0 НЕТ: UI, HTTP-сервиса, БД, расписания, суммаризации, NER, классификации, доставки в Telegram/email.

---

## Команда (важно для контекста)

Это **командный** проект, не работа на внешнего стейкхолдера. В исходной концепции (`raw/concept.md`, `raw/research.md`) упомянуто **ЕРА (Евразийское рейтинговое агентство)** как потенциальный B2B-партнёр — но это бизнес-контекст полного продукта (Step 5+), не текущая аудитория Step 0.

**Состав команды:**
- **Дима (Дмитрий Гальченко)** — опытный разработчик-сокомандник, даёт архитектурный фидбек («не нейрослоп», «не overengineering»). **НЕ внешний заказчик** — все решения принимаются командой коллективно.
- **Влад (Владислав Пахомов)** — разработка.
- **Маша (Maria)** — менеджмент, ведёт чат, custdev.
- **Алиса** — опрос целевой аудитории (Google Forms).
- **zevtos** — текущий разработчик (этот аккаунт).

Принимаемые архитектурные решения — **общекомандные**, не «нужно согласие Димы извне». Если AI-помощник по ошибке считает Диму «заказчиком» — это устаревший фрейминг, поправь.

---

## Дедлайны

- **29.05.2026, 17:30 — защита** (офлайн, Кронверкский, ИТМО ФТМИ). Главный текущий дедлайн.

---

## Принятые решения (фиксируем, чтобы не путаться)

| # | Решение | Источник |
|---|---|---|
| Step 0 closed | Принято командой 2026-05-23 по обновлённому DoD | `raw/step0-qual-baseline.md` §9 |
| DoD Step 0 = cap_precision | precision @ min(K, \|expected\|) ≥ 0.5 на ≥4 из 6 непустых запросов. Не precision@10 — слишком строгая для узких эталонов. | `raw/step0-spec.md` §9 |
| Embedding-матчер = default | `intfloat/multilingual-e5-base`, локально. 2× cap_precision vs BM25. | `raw/step0-architecture.md` ADR-07 |
| BM25 = Should baseline | для side-by-side сравнения, не primary | `raw/step0-spec.md` MoSCoW |
| **Step 1→2→3 — в работе (2026-05-24)** | Пользователь отменил «стоп до защиты». Идём Step 1 (briefing-first) → Step 2 (web) → Step 3 (summary) автономно. | пользователь 2026-05-24 |
| **Доставка = браузер** | Step 2 = веб-страница (FastAPI + Jinja2). НЕ Telegram-бот, НЕ email. | пользователь 2026-05-24 |

---

## Где брать контекст

В порядке полезности:

1. `raw/step0-spec.md` — спецификация (user stories, MoSCoW, NFR, §9 = DoD update)
2. `raw/step0-architecture.md` — архитектура, **17 ADR** (1–11 базовый стек, 12–17 async fetch), контракты
3. `raw/step0-qual-baseline.md` — результаты qual-eval, обоснование DoD pivot
4. `raw/mvp-brief.md` — короткий бриф v3
5. `raw/sources-research.md` — выбор источников, проверка RSS
6. `raw/roadmap.md` — что строится ПОСЛЕ Step 0
7. `raw/mvp-pm-review.md` — исторический PM-разбор v1 брифа
8. `docs/` — KB через `doc2kb` (может быть устаревшей — регенерируется командой по необходимости)

---

## Конвенции

- **Язык документации:** русский. Идентификаторы, технологии, имена файлов — латиницей.
- **Python:** 3.11+, type hints везде, Pydantic v2 для доменных моделей.
- **Layout:** код в `backend/src/newscore/`, тесты в `backend/tests/{unit,integration,qualitative}/`.
- **Тесты:** `pytest` + `respx`. Qual-тесты — отдельный CLI (`backend/tests/qualitative/eval.py`), не pytest. `qual` маркер зарезервирован.
- **Конфиг:** YAML (`configs/sources.yaml`). `.env` — только runtime overrides.
- **Сетевые вызовы:** только в `backend/src/newscore/parser.py` через `httpx.AsyncClient`. В тестах — mock через `respx`.

---

## Команды

```bash
uv sync                                                              # установка
uv run newscore "курс валют"                                         # CLI
uv run newscore "курс валют" --matcher bm25                          # сравнить с BM25
uv run newscore "запрос" --trace                                     # сохранить полный trace
uv run pytest backend/tests/unit                                     # быстрые тесты (46)
uv run pytest backend/tests/integration                              # integration через respx (8)
uv run pytest backend/tests                                          # все 54
uv run python backend/tests/qualitative/eval.py collect --days 30    # снять snapshot корпуса
uv run python backend/tests/qualitative/eval.py score --id sample-30d  # прогнать score
```

---

## Текущий scope (Step 1→2→3 в работе)

**В скоупе сейчас:**
- **Step 1 — briefing-first:** SQLite (single-file `data/newscore.db`) + темы + scheduler + дельтинг
- **Step 2 — web delivery:** FastAPI + Jinja2 templates, минимальный CSS, без auth, без SPA
- **Step 3 — summary:** extractive через embeddings (без LLM API), 2-4 предложения на статью

**Step 0 заморожен:** код стабилен, qual-eval baseline зафиксирован. Не трогаем без причины.

**Не в скоупе:**
- **НЕ** Docker prod / K8s / CI/CD — это Step 5.
- **НЕ** массовое масштабирование источников / web-краулинг — это Step 4.
- **НЕ** Telegram-бот / email — доставка только через браузер (решение 2026-05-24).
- **НЕ** платный LLM API для summary — только локальная extractive через e5-base.
- **НЕ** реализовывать `dedupe_by_title_url_hash` и `FileCache.get/put` — оставлены как `NotImplementedError`, это **Should** (см. spec §4 + §9).
- **НЕ** удалять `frontend/`, `infra/` — заглушки для будущих шагов.

Если фича пахнет Step 4-5 — отказать, сослаться на `raw/roadmap.md`.

---

## Git

Remote: `git@github.com:Maria2525007/newscore-ai.git` (репо переехал с `Maria2525007/startdown`, GitHub автоматически редиректит — но при желании обновить URL локально: `git remote set-url origin git@github.com:Maria2525007/newscore-ai.git`).

---

## Search tooling

В этом репо принято: использовать `Grep` (не `bash grep`) и `Glob` (не `find`). Соответствует глобальному CLAUDE.md пользователя.
