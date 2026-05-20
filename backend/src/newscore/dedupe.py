"""Дедупликация материалов."""

from newscore.models import EnrichedArticle


def dedupe_by_url(
    articles: list[EnrichedArticle],
) -> tuple[list[EnrichedArticle], int]:
    """Удаляет точные дубли по URL, сохраняя порядок."""
    seen: set[str] = set()
    unique: list[EnrichedArticle] = []
    for a in articles:
        url = str(a.url)
        if url in seen:
            continue
        seen.add(url)
        unique.append(a)
    return unique, len(articles) - len(unique)


def dedupe_by_title_url_hash(
    articles: list[EnrichedArticle],
) -> tuple[list[EnrichedArticle], int]:
    raise NotImplementedError
