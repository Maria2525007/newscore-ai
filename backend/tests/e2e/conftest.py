"""E2E фикстуры: живой uvicorn в фоновом потоке + FakeOrchestrator.

Один экземпляр сервера на тест (function-scope) → изоляция БД и состояния.
SQLite использует check_same_thread=False (см. themes/db.py),
так что web-потоки uvicorn спокойно делят коннекшн с тестовым потоком.
"""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
import uvicorn

from newscore.themes.db import connect
from newscore.themes.service import ThemeService
from newscore.web import create_app

from ._helpers import FakeOrchestrator, LiveServer


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def live_server(tmp_path: Path) -> Iterator[LiveServer]:
    db_path = tmp_path / "themes.db"
    conn = connect(db_path)
    orch = FakeOrchestrator()
    service = ThemeService(
        conn_factory=lambda: conn,
        orchestrator_factory=lambda: orch,
    )
    app = create_app(service)
    port = _free_port()
    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="warning", lifespan="off"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 5.0
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            r = httpx.get(base + "/", timeout=0.5)
            if r.status_code == 200:
                break
        except httpx.HTTPError as exc:
            last_err = exc
        time.sleep(0.05)
    else:
        server.should_exit = True
        thread.join(timeout=2)
        raise RuntimeError(f"uvicorn not ready in 5s: {last_err}")

    try:
        yield LiveServer(base_url=base, service=service, orchestrator=orch)
    finally:
        server.should_exit = True
        thread.join(timeout=3)
