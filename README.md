# NewsCore AI

Персональный брифинг-агент для предпринимателей и руководителей — веб-сервис с AI-суммаризацией деловых новостей.

**Партнёры:** Евразийское рейтинговое агентство × ИТМО ФТМИ
**Статус:** Концепция MVP

---

## Структура репозитория

```
newscore-ai/
├── backend/            # FastAPI: API, AI-пайплайн, парсинг
├── frontend/           # Next.js: веб-интерфейс
├── infra/              # Docker, K8s, CI/CD
├── docs/               # Финальные документы
└── research/           # Сырые материалы: исследования, презентации
```

## Быстрый старт

```bash
git clone https://github.com/USERNAME/newscore-ai.git
cd newscore-ai
cp .env.example .env
docker-compose up
```

## Стек

| Слой   | Технологии                              |
| ---------- | ------------------------------------------------- |
| Frontend   | Next.js, React                                    |
| Backend    | Python 3.12, FastAPI                              |
| БД       | PostgreSQL 16, Redis 7, Elasticsearch 8           |
| AI         | YandexGPT Pro, ruBERT, natasha NER, LightGBM      |
| Инфра | Kubernetes, Yandex Cloud, GitHub Actions, Grafana |
