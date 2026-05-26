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
    expect(page.locator("h1")).to_have_text("Темы")
    expect(page.get_by_text("Нет тем")).to_be_visible()
    expect(page.get_by_role("link", name="Создать первую")).to_have_attribute(
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
    expect(page.locator("h1")).to_have_text("курс валют")
    expect(page.get_by_text("Ещё не запускалась")).to_be_visible()

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

    expect(page.locator("h2", has_text="Последний запуск")).to_be_visible()
    expect(page.locator("h2", has_text="Статьи (2)")).to_be_visible()

    articles = page.locator("ol.articles > li")
    expect(articles).to_have_count(2)

    first = articles.nth(0)
    expect(first.get_by_role("link", name="ЦБ повысил ключевую ставку")).to_have_attribute(
        "href", "https://example.com/news/1"
    )
    expect(first.locator("p.summary")).to_contain_text(
        "ЦБ РФ поднял ставку до 21%"
    )


def test_pause_then_resume_flips_status_button(
    live_server: LiveServer, page: Page
) -> None:
    theme = live_server.service.create("ставка ЦБ", period_seconds=3600)
    detail = f"{live_server.base_url}/themes/{theme.id}"

    page.goto(detail)
    expect(page.locator(".status.status-active")).to_have_text("active")
    page.get_by_role("button", name="Пауза").click()

    expect(page.locator(".status.status-paused")).to_have_text("paused")
    expect(page.get_by_role("button", name="Активировать")).to_be_visible()
    assert live_server.service.get(theme.id).status == "paused"

    page.get_by_role("button", name="Активировать").click()
    expect(page.locator(".status.status-active")).to_have_text("active")
    assert live_server.service.get(theme.id).status == "active"


def test_delete_theme_with_confirm_dialog_returns_home(
    live_server: LiveServer, page: Page
) -> None:
    theme = live_server.service.create("санкции", period_seconds=3600)
    page.goto(f"{live_server.base_url}/themes/{theme.id}")

    page.once("dialog", lambda d: d.accept())
    page.get_by_role("button", name="Удалить").click()

    expect(page).to_have_url(live_server.base_url + "/")
    expect(page.get_by_text("Нет тем")).to_be_visible()
    assert live_server.service.list() == []


def test_index_lists_existing_themes_with_links(
    live_server: LiveServer, page: Page
) -> None:
    t1 = live_server.service.create("курс валют", period_seconds=1800)
    live_server.service.create("ставка ЦБ", period_seconds=3600)

    page.goto(live_server.base_url + "/")
    rows = page.locator("table.themes tbody tr")
    expect(rows).to_have_count(2)
    expect(page.get_by_role("link", name="курс валют")).to_have_attribute(
        "href", f"/themes/{t1.id}"
    )
    expect(page.get_by_role("link", name="ставка ЦБ")).to_be_visible()
