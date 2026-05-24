# Step 1 — Архитектура (briefing-first)

> Step 1 наслаивается поверх закрытого Step 0 (см. `step0-architecture.md`).
> Контракты Step 0 (`BriefingRequest`, `BriefingResult`, `BriefingOrchestrator`,
> `FeedParser`, `Matcher`) **не меняются**.

---

## 1. Бизнес-цель

Перейти от модели «вбил запрос → получил ответ» (Step 0) к модели
«задал тему → агент сам приходит с обновлениями».

**Концепт «тема»:** NL-запрос + период обновления + параметры матчинга.

---

## 2. Состав

- **`backend/src/newscore/themes/`** — новый subpackage:
  - `models.py` — Pydantic v2: `Theme`, `ThemeRun`, `ArticleSnapshot`.
  - `db.py` — SQLite + PRAGMA + миграции (`_SCHEMA_V1`, `PRAGMA user_version=1`).
  - `service.py` — `ThemeService` (CRUD + `run_now` + delta + queries).
  - `scheduler.py` — `AsyncScheduler.run_forever` для daemon.
  - `cli.py` — typer subgroup `theme` + `daemon` command.
- **`backend/src/newscore/cli.py`** — многокомандный typer (`briefing`,
  `theme`, `daemon`) + backward-compat argv-rewrite в `main()`.
- **`data/newscore.db`** — single-file SQLite (в `.gitignore`).

---

## 3. ADR

### ADR-18 — SQLite через stdlib `sqlite3`, без ORM

**Контекст.** Нужна persistence для тем/runs/articles. Варианты: SQLAlchemy,
SQLModel, stdlib `sqlite3`, чистый JSON-файл.

**Решение.** Stdlib `sqlite3` + raw SQL в `db.py`.

**Обоснование.** Три таблицы, 100 LoC SQL, никаких миграционных фреймворков.
SQLAlchemy/SQLModel — overkill для single-user локального приложения. Переход
на SQLAlchemy остаётся открытым, если в Step 4 потребуется PostgreSQL.

---

### ADR-19 — Миграции как идемпотентный `_SCHEMA_V1: list[str]`

**Контекст.** Способ применять схему при первом запуске и при апгрейдах.

**Решение.** Константа `_SCHEMA_V1: list[str]` с `CREATE … IF NOT EXISTS`,
запускается в одной транзакции под `BEGIN IMMEDIATE`. Версия отслеживается
через `PRAGMA user_version`.

**Обоснование.** Alembic избыточен для Step 1. Переключимся на Alembic, когда
появится первая разрушительная миграция (Step 3, если NER-поля потребуют
структурных колонок вместо JSON).

---

### ADR-20 — Asyncio-loop scheduler в `daemon`, без APScheduler / cron

**Контекст.** Способ запускать темы по периоду.

**Решение.** `AsyncScheduler` — простой `while not stop: tick_once; sleep(tick)`
внутри `asyncio.run` в команде `newscore daemon`. Темы исполняются
**последовательно** (не `gather`).

**Обоснование.**
- APScheduler = лишняя зависимость + cron-expr учить ради одного `WHERE
  next_run_at <= now`. Не платит.
- Cron-driven = пользователь редактирует crontab + холодный старт embedding
  модели на каждый tick (~5s).
- Asyncio-loop = ~40 LoC, без зависимостей, держит embedding-модель тёплой
  между runs, тривиально тестируется через injected `clock`.

---

### ADR-21 — `url_hash = sha256(lower(url).rstrip('/'))[:32]` как cross-run identity

**Контекст.** Нужен детерминированный ключ для дедупликации статей по runs.

**Решение.** Хеш sha256 от нормализованного URL, первые 32 hex-символа (128
бит). Используется как часть PK `articles(theme_id, url_hash)`.

**Обоснование.** 128 бит коллизий: вероятность ≈ 2⁻¹⁰⁰ при тысячах статей —
пренебрежимо. URL уже выбран как dedup-ключ в Step 0
(`dedupe.dedupe_by_url`) — согласованность.

---

### ADR-22 — `payload_json` / `meta_json` денормализованы в TEXT

**Контекст.** Step 3 добавит summary/NER/importance — нежелательно переделывать
schema каждый раз.

**Решение.** Хранить `Match.model_dump_json()` в `articles.payload_json` и
`RunMeta.model_dump_json()` в `runs.meta_json`. CHECK-констрейнт
`json_valid(...)`. Никаких JSON1-индексов — нет hot path с фильтром по JSON.

**Обоснование.** Платим ~1 KB на статью, экономим миграции. Если в Step 3
понадобится фильтр по NER-тегам — добавим колонку и backfill.

---

### ADR-23 — `BriefingOrchestrator` остаётся sync; bridge через `asyncio.to_thread`

**Контекст.** Scheduler работает в asyncio-loop. Orchestrator внутри вызывает
`FeedParser.collect`, который запускает `asyncio.run(...)`. Нельзя
вкладывать `asyncio.run` в работающий loop.

**Решение.** Scheduler делает `await asyncio.to_thread(svc.run_now, theme.id)`.
`run_now` исполняется в worker thread → там свой event loop у parser.

**Обоснование.** Sync-контракт оркестратора неизменён, async добавлен только
на оборачивании. Бонус: per-thread SQLite-connection (через `threading.local`
в `ThemeService`) естественно ложится на ту же модель.

---

## 4. Схема данных

См. `_SCHEMA_V1` в `backend/src/newscore/themes/db.py`. Кратко:

| Таблица   | PK                          | Назначение                                             |
|-----------|-----------------------------|--------------------------------------------------------|
| `themes`  | `id`                        | Конфиг темы + `next_run_at` для scheduler              |
| `runs`    | `id`                        | История запусков; `meta_json` = полный `RunMeta` JSON  |
| `articles`| `(theme_id, url_hash)`      | Дедупнутая «лента» темы; `payload_json` = `Match` JSON |

Индексы:
- `idx_themes_due (status, next_run_at)` — scheduler `due_themes`.
- `idx_runs_theme_started (theme_id, started_at DESC)` — `latest_run`.
- `idx_articles_theme_first_seen (theme_id, first_seen_at DESC, url_hash)` —
  `new_since` + тайбрейкер для детерминированной пагинации.

PRAGMA при connect: `journal_mode=WAL`, `synchronous=NORMAL`,
`foreign_keys=ON`, `busy_timeout=5000`, `cache_size=-20000`,
`temp_store=MEMORY`, `mmap_size=268435456`.

---

## 5. Контракты

```python
# newscore.themes.service
class ThemeService:
    def __init__(self, conn_factory: Callable[[], sqlite3.Connection],
                 orchestrator_factory: Callable[[], BriefingOrchestrator]): ...
    # CRUD
    def create(self, query: str, period_seconds: int, *,
               matcher="embedding", top_n=10, days=7) -> Theme
    def list(self, status: ThemeStatus | None = None) -> list[Theme]
    def get(self, theme_id: str) -> Theme                 # raises ThemeNotFound
    def delete(self, theme_id: str) -> None
    def pause(self, theme_id: str) -> Theme
    def resume(self, theme_id: str) -> Theme
    # Run
    def due_themes(self, now: datetime | None = None) -> list[Theme]
    def run_now(self, theme_id: str) -> ThemeRun
    # Queries (для Step 2 web)
    def latest_run(self, theme_id: str) -> ThemeRun | None
    def list_runs(self, theme_id: str, limit: int = 20) -> list[ThemeRun]
    def latest_articles(self, theme_id: str, limit: int = 50) -> list[ArticleSnapshot]
    def new_since(self, theme_id: str, since: datetime) -> list[ArticleSnapshot]
```

`run_now` — единственная точка записи в БД. Внутри одной транзакции:
1. INSERT в `runs`.
2. UPSERT в `articles` (новый url → `items_new += 1`).
3. UPDATE `runs.items_new`.
4. UPDATE `themes.last_run_id`, `themes.next_run_at = finished_at + period`.

---

## 6. CLI

```bash
newscore theme create "курс валют" --period 30m       # 60s | 30m | 2h | 1d
newscore theme list [--json]
newscore theme show <id>                              # карточка + последние 20 статей
newscore theme run <id>                               # синхронно сейчас
newscore theme delete <id>
newscore theme pause <id>
newscore theme resume <id>
newscore daemon [--tick 60]                           # фоновый scheduler
```

`newscore "запрос"` (без подкоманды) → backward-compat алиас к
`newscore briefing "запрос"` через argv-rewrite в `cli.main()`.

---

## 7. Решения, отложенные на Step 2

- `theme update` (смена периода/матчера) — будет через web UI; CLI пока
  только create + delete (re-create если надо).
- Article retention / pruning — пока никогда не удаляем.
- Lock-file для предотвращения двух daemon-ов на одну БД — не блокер для
  single-user dev; добавим если потребуется.
