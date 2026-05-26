# Run 01 — Multilingual News Retrieval (ultrasearch snapshot)

Снапшот после первого успешного запуска ultrasearch (Stage 1, serial-parsing).
Сохранён перед апдейтом скилла (параллелизм parser'а) на случай несовместимостей.

## Метаданные

- **Дата:** 2026-05-26 ~20:18 (Europe/Moscow)
- **Query:** `multilingual dense retrieval news short query long document hybrid BM25 e5 BGE`
- **Параметры:** `--depth default --lang auto --max-papers 30`
- **Pipeline version:** ultrasearch Stage 1 (academic profile), pre-параллелизм parser
- **Total wallclock:** 825s (~14 мин; из них parse = 732s)

## Что внутри

| Файл | Размер | Назначение |
|---|---|---|
| `corpus.db` | 3.6 M | SQLite: 30 papers / 59 chunks / 154 citation edges. SPECTER embeddings в `vec_chunks`. WAL checkpointed. |
| `pdfs/` | 47 M | 28 скачанных PDF (md5(URL) имена). Совпадает с `data/cache/pdfs/` скилла на момент снапшота. |
| `report.md` | 13 K | Финальный markdown-брифинг (78 строк, 13 inline `[Sn]`, 15 References). |
| `pipeline.log` | 5.2 K | Полный stderr/stdout pipeline. Содержит per-source stats и HTTP errors (S2/arXiv 429, MDPI 403). |
| `stats.json` | 1.8 K | Извлечённая последняя JSON-строка `[ultrasearch] {...}` с метриками всех стадий. |

## Discover stats (для контекста — без `S2_API_KEY` и `CORE_API_KEY`)

| Source | Hits | Note |
|---|---|---|
| openalex | 29 | ✅ |
| crossref | 50 | ✅ |
| s2 | 0 | HTTP 429 — нужен `S2_API_KEY` |
| arxiv | 0 | HTTP 429 burst — для retry нужен delay или другой client |
| europepmc | 0 | биомед, тема нерелевантна |
| core | 0 | `CORE_API_KEY` не установлен |

## Валидационный checklist (по SKILL.md)

- ✅ Все параграфы цитируют `[Sn]` (0 bad)
- ✅ Все `[Sn]` в body есть в References
- ⚠️ В References есть `[S14]`, `[S15]` без in-body marker (minor, не блокер)
- ✅ Все DOI в `report.md` либо в `corpus.db.papers.doi`, либо помечены как traversal candidates (Open Questions section, 6 DOIs)
- ✅ corpus.db grew с 0 до 30 papers (clean restart перед запуском)

## Как восстановить в обновлённый скилл

```bash
# 1. Закрыть любой активный ultrasearch процесс
pkill -f ultrasearch || true

# 2. Слить snapshot обратно
cp corpus.db ~/.claude/skills/ultrasearch/data/corpus.db
rsync -a pdfs/ ~/.claude/skills/ultrasearch/data/cache/pdfs/

# 3. Проверить совместимость schema (если скилл обновил schema.sql)
sqlite3 ~/.claude/skills/ultrasearch/data/corpus.db ".schema papers"
# Если новые поля — мигрировать или передавать через MIGRATE script от скилла
```

**Если schema обновился:** corpus.db может потребовать миграции — проверить `~/.claude/skills/ultrasearch/data/schema.sql` после апдейта. Если миграция нетривиальна — проще сбросить (`rm corpus.db`) и переиндексировать заново; PDFs останутся в cache, fetch-стадия пропустит их (cache hit).

## Архивы (если стало больше runs)

Этот формат для одного run'а. Для multi-run работы — обернуть в tar.gz:
```bash
tar -czf run-01-snapshot-$(date +%Y%m%d).tar.gz -C /Volumes/Dev/newscore-ai/raw/research run-01-multilingual-news-retrieval
```
