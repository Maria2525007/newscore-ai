"""E2E: пользовательские потоки на веб-интерфейсе через настоящий браузер.

Не подменяем FastAPI — Playwright ходит на живой uvicorn (см. conftest.py),
оркестратор подменён FakeOrchestrator, чтобы не дёргать RSS и embedding-модель.
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from ._helpers import LiveServer, make_article, make_result

pytestmark = pytest.mark.e2e


def test_index_empty_shows_create_link(live_server: LiveServer, page: Page) -> None:
    page.goto(live_server.base_url + "/")
    # Новый UI: greeting вместо h1 "Темы"
    expect(page.locator(".greeting-text")).to_be_visible()
    expect(page.get_by_text("Тем пока нет")).to_be_visible()
    expect(page.get_by_role("link", name="Создать первую тему")).to_have_attribute(
        "href", "/themes/new"
    )


def test_create_theme_via_form_redirects_to_detail(
    live_server: LiveServer, page: Page
) -> None:
    page.goto(live_server.base_url + "/themes/new")
    page.fill('input[name="query"]', "курс валют")
    page.fill('input[name="period"]', "30m")
    page.select_option('select[name="matcher"]', "embedding")
    page.click('button[type="submit"]')

    expect(page).to_have_url(re.compile(r"/themes/[0-9a-f]{12}$"))
    expect(page.locator(".detail-title")).to_have_text("курс валют")
    # Новый UI: «Ещё не запускалась — нажмите…»
    expect(page.locator(".run-empty")).to_contain_text("Ещё не запускалась")

    themes = live_server.service.list()
    assert len(themes) == 1
    assert themes[0].query == "курс валют"
    assert themes[0].period_seconds == 30 * 60


def test_run_theme_renders_articles_with_summary(
    live_server: LiveServer, page: Page
) -> None:
    theme = live_server.service.create("курс валют", period_seconds=3600)
    live_server.orchestrator.push(
        make_result(
            "курс валют",
            [
                make_article(
                    "https://example.com/news/1",
                    "ЦБ повысил ключевую ставку",
                    summary="ЦБ РФ поднял ставку до 21%. Эксперты ожидали 20%.",
                ),
                make_article(
                    "https://example.com/news/2",
                    "Рубль укрепился к доллару",
                    summary="Курс рубля вырос на 1.5% за неделю.",
                ),
            ],
        )
    )

    page.goto(f"{live_server.base_url}/themes/{theme.id}")
    page.get_by_role("button", name="Запустить сейчас").click()
    # Кнопка triggers async POST + JS reload — ждём перерисовки списка.
    expect(page.locator(".articles-list .article-card")).to_have_count(
        2, timeout=15_000
    )
    expect(page.locator(".section-label").filter(has_text="Статьи (2)")).to_be_visible()

    articles = page.locator(".articles-list .article-card")
    first = articles.nth(0)
    # Сортировка по умолчанию = score desc. Оба score = 0.85 (равные),
    # поэтому проверяем что обе статьи присутствуют, без жёсткой позиции.
    titles = articles.locator(".article-title")
    expect(titles).to_have_text(
        [
            re.compile(r"(ЦБ повысил|Рубль укрепился)"),
            re.compile(r"(ЦБ повысил|Рубль укрепился)"),
        ]
    )
    expect(first.locator(".article-summary")).to_be_visible()


def test_pause_then_resume_flips_status_button(
    live_server: LiveServer, page: Page
) -> None:
    theme = live_server.service.create("ставка ЦБ", period_seconds=3600)
    detail = f"{live_server.base_url}/themes/{theme.id}"

    page.goto(detail)
    expect(page.locator(".detail-badges .badge-active")).to_have_text("активна")
    page.get_by_role("button", name="Пауза").click()

    expect(page.locator(".detail-badges .badge-paused")).to_have_text("пауза")
    expect(page.get_by_role("button", name="Активировать")).to_be_visible()
    assert live_server.service.get(theme.id).status == "paused"

    page.get_by_role("button", name="Активировать").click()
    expect(page.locator(".detail-badges .badge-active")).to_have_text("активна")
    assert live_server.service.get(theme.id).status == "active"


def test_delete_theme_with_confirm_dialog_returns_home(
    live_server: LiveServer, page: Page
) -> None:
    theme = live_server.service.create("санкции", period_seconds=3600)
    page.goto(f"{live_server.base_url}/themes/{theme.id}")

    page.once("dialog", lambda d: d.accept())
    page.get_by_role("button", name="Удалить").click()

    expect(page).to_have_url(live_server.base_url + "/")
    expect(page.get_by_text("Тем пока нет")).to_be_visible()
    assert live_server.service.list() == []


def test_index_lists_existing_themes_with_links(
    live_server: LiveServer, page: Page
) -> None:
    t1 = live_server.service.create("курс валют", period_seconds=1800)
    live_server.service.create("ставка ЦБ", period_seconds=3600)

    page.goto(live_server.base_url + "/")
    cards = page.locator(".themes-grid .theme-card")
    expect(cards).to_have_count(2)
    # theme-card сам по себе <a> — ищем по href, не по link role/тексту
    # (текст в карточке оборачивается в внутренние divs).
    expect(page.locator(f'a[href="/themes/{t1.id}"]')).to_be_visible()
    expect(page.locator(".theme-card-query").filter(has_text="курс валют")).to_be_visible()
    expect(page.locator(".theme-card-query").filter(has_text="ставка ЦБ")).to_be_visible()
