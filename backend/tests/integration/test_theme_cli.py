"""Integration: typer CliRunner для CRUD-команд `theme`.

Команды `theme run` и `daemon` НЕ тестируются здесь — они инстанцируют
реальный FeedParser/EmbeddingMatcher (сеть + ~30s холодный старт).
Сетевое поведение покрыто unit-тестами ThemeService с FakeOrchestrator.
"""

import json
from pathlib import Path

from typer.testing import CliRunner

from newscore.cli import app

runner = CliRunner()


def _common_opts(tmp_path: Path) -> list[str]:
    cfg = Path(__file__).parent / "fixtures" / "minimal_sources.yaml"
    if not cfg.exists():
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text("sources: []\n", encoding="utf-8")
    db = tmp_path / "themes.db"
    return ["--db", str(db), "--config", str(cfg)]


def test_cli_create_then_list(tmp_path: Path) -> None:
    opts = _common_opts(tmp_path)
    result = runner.invoke(
        app, ["theme", "create", "курс валют", "--period", "30m", *opts]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["query"] == "курс валют"
    assert payload["period_seconds"] == 1800

    listed = runner.invoke(app, ["theme", "list", "--json", *opts])
    assert listed.exit_code == 0
    items = json.loads(listed.output)
    assert len(items) == 1
    assert items[0]["id"] == payload["id"]


def test_cli_create_invalid_period(tmp_path: Path) -> None:
    opts = _common_opts(tmp_path)
    result = runner.invoke(app, ["theme", "create", "x", "--period", "5s", *opts])
    assert result.exit_code != 0


def test_cli_show_returns_full_card(tmp_path: Path) -> None:
    opts = _common_opts(tmp_path)
    created = runner.invoke(
        app, ["theme", "create", "test", "--period", "1h", *opts]
    )
    theme_id = json.loads(created.output)["id"]
    result = runner.invoke(app, ["theme", "show", theme_id, *opts])
    assert result.exit_code == 0
    card = json.loads(result.output)
    assert card["theme"]["id"] == theme_id
    assert card["latest_run"] is None
    assert card["articles"] == []


def test_cli_delete(tmp_path: Path) -> None:
    opts = _common_opts(tmp_path)
    created = runner.invoke(
        app, ["theme", "create", "x", "--period", "1h", *opts]
    )
    theme_id = json.loads(created.output)["id"]
    deleted = runner.invoke(app, ["theme", "delete", theme_id, *opts])
    assert deleted.exit_code == 0

    listed = runner.invoke(app, ["theme", "list", "--json", *opts])
    assert json.loads(listed.output) == []


def test_cli_pause_resume(tmp_path: Path) -> None:
    opts = _common_opts(tmp_path)
    created = runner.invoke(
        app, ["theme", "create", "x", "--period", "1h", *opts]
    )
    theme_id = json.loads(created.output)["id"]
    paused = runner.invoke(app, ["theme", "pause", theme_id, *opts])
    assert json.loads(paused.output)["status"] == "paused"
    resumed = runner.invoke(app, ["theme", "resume", theme_id, *opts])
    assert json.loads(resumed.output)["status"] == "active"


def test_cli_show_unknown_theme_exits_with_error(tmp_path: Path) -> None:
    opts = _common_opts(tmp_path)
    result = runner.invoke(app, ["theme", "show", "nope", *opts])
    assert result.exit_code == 1


def test_cli_bare_query_backward_compat_routes_to_briefing(tmp_path: Path) -> None:
    """`newscore "запрос"` без подкоманды должен показать help briefing."""
    # Через CliRunner мы не задеваем argv-rewrite в main(), но проверим что
    # briefing-команда регистрирована и принимает аргумент.
    result = runner.invoke(app, ["briefing", "--help"])
    assert result.exit_code == 0
    assert "NL-запрос" in result.output
