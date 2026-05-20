# NewsCore AI — Project Context for AI Assistants

## Что за проект

NewsCore AI — briefing-first новостной агент. Сейчас **Step 0**: CLI-ядро, парсер 5 RSS-источников + embedding-матчер по NL-запросу.

**Не путать Step 0 с полным продуктом.** Полный продукт описан в `raw/roadmap.md`. На Step 0 НЕТ: UI, HTTP-сервиса, БД, расписания, суммаризации, NER, классификации, доставки в Telegram/email.

## Где брать контекст

В порядке полезности:

1. `raw/step0-spec.md` — спецификация (user stories, MoSCoW, NFR)
2. `raw/step0-architecture.md` — архитектура, 11 ADR, контракты
3. `raw/mvp-brief.md` — короткий бриф v3
4. `raw/sources-research.md` — выбор источников
5. `raw/roadmap.md` — что строится ПОСЛЕ Step 0
6. `docs/` — собранная KB (через `doc2kb` skill)

## Конвенции

- **Язык документации:** русский. Идентификаторы, технологии, имена файлов — латиницей.
- **Python:** 3.11+, type hints везде, Pydantic v2 для доменных моделей.
- **Layout:** код в `backend/src/newscore/`, тесты в `backend/tests/{unit,integration,qualitative}/`.
- **Тесты:** `pytest` + `respx`. Qual-тесты помечены маркером `qual`, не запускаются по умолчанию.
- **Конфиг:** YAML (`configs/sources.yaml`). `.env` — только runtime overrides.

## Команды

```bash
uv sync                                       # установка
uv run newscore "курс валют"                  # CLI
uv run pytest backend/tests/unit              # быстрые тесты
uv run pytest -m qual backend/tests           # qualitative eval (медленно)
```

## Что НЕ делать на Step 0

- НЕ добавлять FastAPI / HTTP-эндпоинты — это Step 2.
- НЕ добавлять PostgreSQL / SQLite — это Step 1+.
- НЕ добавлять Docker prod / K8s / CI/CD — это Step 5.
- НЕ добавлять суммаризацию, NER, классификацию — это Step 3.
- НЕ добавлять авто-обновление тем, расписание — это Step 1.
- НЕ удалять `frontend/`, `infra/` — заглушки для Step 2/5.

Если фича пахнет ROADMAP — отказать, сослаться на `raw/roadmap.md`.

## Search tooling

В этом репо принято: использовать `Grep` (не `bash grep`) и `Glob` (не `find`). Соответствует глобальному CLAUDE.md пользователя.
