# NewsCore AI — Ресёрч источников и фиксация выбора (Step 0)

> Источник: ресёрч + проверка доступности RSS-фидов 2026-05-20.
> Закрывает Open Question №1 и №2 из `mvp-brief.md`.

---

## Проверенные Tier 1 RSS-фиды (нативный RSS, парсится `feedparser`)

Проверка: HTTP GET с браузерным `User-Agent`, парсинг XML, замер свежести и наличия полного текста в RSS.

| Источник | URL | Status | Items | Свежесть (ч) | Полный текст в RSS? |
|---|---|---|---|---|---|
| **РБК main** | `https://rssexport.rbc.ru/rbcnews/news/30/full.rss` | 200 | 30 | 0 | **ДА** (тег `<rbc_news:full-text>`) |
| РБК business 20 | `https://rssexport.rbc.ru/rbcnews/news/20/full.rss` | **404** | — | — | URL устарел, исключаем |
| **Коммерсантъ** | `https://www.kommersant.ru/RSS/news.xml` | 200 | 423 | 0 | нет (description ~200 симв) |
| Ведомости news | `https://www.vedomosti.ru/rss/news` | 200 | 200 | 0 | нет (только title) |
| **Ведомости business** | `https://www.vedomosti.ru/rss/rubric/business` | 200 | 200 | 2 | нет (только title) |
| ТАСС | `https://tass.ru/rss/v2.xml` | 200 | 100 | 0 | нет (только title) |
| **Интерфакс** | `https://www.interfax.ru/rss.asp` | 200 | 25 | 0 | нет |
| Лента economics | `https://lenta.ru/rss/news/economics` | 200 | 200 | 0 | нет |
| **Forbes Russia** | `https://www.forbes.ru/newrss.xml` | 200 | 20 | 0 | нет |

**Все фиды доступны из РФ без VPN.** Миф про блокировку Forbes Russia (R1 в spec) опровергнут.

---

## Фиксация выбора для Step 0

Закрывает Open Q1 (`mvp-brief.md`):

1. **РБК main** (`full.rss`) — флагман, плюс полный текст бесплатно
2. **Коммерсантъ** — 423 items в окне, обязательный для бизнес-аудитории
3. **Ведомости business** (`rss/rubric/business`) — узкая рубрика, релевантнее общей ленты
4. **Интерфакс** — авторитетное агентство
5. **Forbes Russia** — бизнес/финансы

**Резерв** (не входят в Step 0, добавляются если на qual-тесте видны пробелы):
- ТАСС, Лента economics, Ведомости news (общая лента)

---

## Архитектурное замечание (важно для архитектора)

**Источники неоднородны по объёму данных в RSS.**

- РБК отдаёт **полный текст** статьи прямо в RSS через кастомный тег `<rbc_news:full-text>` (namespace `rbc_news`). Для этого источника `trafilatura` **не нужен** — экономия сетевых вызовов и времени.
- Остальные источники (Коммерсантъ / Ведомости / Интерфакс / Forbes) отдают только title или короткий description. Для них **обязателен второй этап**: HTTP GET по `<link>` + извлечение текста через `trafilatura`.

**Следствие для пайплайна:**
Парсер должен иметь **источник-специфичные экстракторы тела**:
- `RBCExtractor` — берёт из RSS namespace-тега.
- `GenericTrafilaturaExtractor` — fallback для всех остальных.

Конфиг источника указывает, какой экстрактор использовать (например, поле `body_extractor: rbc_native | trafilatura`).

---

## Закрывает Open Q2 (RSS vs RSS+crawl)

**Решение:** RSS + trafilatura-краулинг тела для тех источников, у кого тело в RSS не полное. Никакого открытого веб-краулинга (это Step 4 в roadmap).

---

## Подводные камни (заметки на будущее, не в DoD Step 0)

- **Ведомости и Коммерсантъ режут по `User-Agent`** — обязательно ставить браузерный UA в HTTP-клиенте.
- **CDATA-обёртки в title/description** — стандартный `xml.etree` парсит их корректно, но проверять что `element.text` не None.
- **Дедупликация по URL** — Must в Step 0 (см. MoSCoW). По хэшу `title + link` — Should.
- **ETag / Last-Modified для повторных проходов** — переносим в Step 1 (фоновый мониторинг), когда появится осмысленность переиспользовать кэш между запусками.

---

## Tier 2 и Tier 3 (Step 4+)

**Не входят в Step 0**, фиксирую для будущего:

**Tier 2 — HTML/JSON, нет RSS:**
- Frank Media (`frankmedia.ru`) — банковский фокус, HTML-парсинг
- The Bell — нестабильный RSS, fallback HTML
- BCS Express — CSS-селекторы по `/category`
- E-disclosure (`e-disclosure.ru`) — корпоративные раскрытия, есть JSON-эндпоинты

**Tier 3 — Telegram (через `telethon`/MTProto):**
- Каналы: `@rbc_news`, `@kommersant`, `@vedomosti`, `@tass_agency`, `@interfaxonline`, `@forbesrussia`, `@bell_tg`, `@frank_media`, `@cbonds`, `@markettwits`
- Telegram даёт ~30–60 секунд преимущества по сравнению с сайтами, но требует API-ключей и сессии.
- Roadmap: Step 4 (масштабирование источников до ∞).
