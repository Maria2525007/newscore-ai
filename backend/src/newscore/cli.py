"""typer-приложение, entry point.

Многокомандный layout (Step 1+):
- `newscore briefing "query"` — Step 0 brief one-shot
- `newscore "query"`          — backward-compat alias к `briefing`
- `newscore theme ...`        — управление темами (Step 1)
- `newscore daemon`           — фоновый scheduler (Step 1)
"""

import json
import sys
import uuid
from enum import Enum
from pathlib import Path

import typer

from newscore.briefing import (
    BriefingDeps,
    BriefingOrchestrator,
    BriefingRequest,
)
from newscore.config import load_config
from newscore.domain import DomainChecker
from newscore.logging import TraceWriter, configure
from newscore.matcher import (
    Bm25Matcher,
    EmbeddingMatcher,
    HybridMatcher,
    Matcher,
    RerankMatcher,
)
from newscore.parser import FeedParser
from newscore.repository import InMemoryRepository
from newscore.summarizer import ExtractiveSummarizer
from newscore.themes.cli import _build_service, daemon_cmd, theme_app
from newscore.themes.db import DEFAULT_DB_PATH


class MatcherChoice(str, Enum):
    embedding = "embedding"
    bm25 = "bm25"
    hybrid = "hybrid"
    rerank = "rerank"  # = hybrid + bge-reranker-v2-m3


class LogFormat(str, Enum):
    console = "console"
    json = "json"


def _matcher_factory(name: str) -> Matcher:
    if name == "embedding":
        return EmbeddingMatcher()
    if name == "bm25":
        return Bm25Matcher()
    if name == "hybrid":
        return HybridMatcher()
    if name == "rerank":
        return RerankMatcher()  # base = HybridMatcher() (default)
    raise ValueError(f"unknown matcher: {name}")


app = typer.Typer(
    help="NewsCore AI — briefing-first новостной агент.",
    no_args_is_help=True,
)
app.add_typer(theme_app, name="theme")
app.command("daemon", help="Запустить фоновый scheduler (Step 1).")(daemon_cmd)


@app.command("web")
def web_cmd(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    db: Path = typer.Option(DEFAULT_DB_PATH, "--db"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
    log_level: str = typer.Option("INFO", "--log-level"),
    default_matcher: str = typer.Option(
        "hybrid",
        "--default-matcher",
        help="hybrid (BM25+e5 RRF, ~1-2с/run) — безопасный default для CPU. "
        "rerank (bge-reranker-v2-m3, ~30-60с/run) — макс. точность, "
        "требует AVX-512/быстрый CPU или GPU. embedding/bm25 — baseline.",
    ),
    warmup: bool = typer.Option(
        True,
        "--warmup/--no-warmup",
        help="Прогреть ML-модели на старте (e5 ~7s + reranker ~4s). "
        "Без этого первый запрос темы ждёт холодную загрузку.",
    ),
    device: str = typer.Option(
        "auto",
        "--device",
        help="torch device: auto (cuda→mps→cpu) | cuda | cuda:0 | mps | cpu. "
        "На GPU-машине auto сам выберет cuda. Также env NEWSCORE_DEVICE.",
    ),
    warmup_all: bool = typer.Option(
        False,
        "--warmup-all",
        help="Прогреть ВСЕ ML-модели (e5 + reranker) независимо от "
        "--default-matcher. Полезно на GPU: грузим всё в VRAM сразу, "
        "чтобы любой выбранный в UI матчер был в боевой готовности.",
    ),
    redis_url: str = typer.Option(
        "",
        "--redis-url",
        help="Redis для многоуровневого кэша (body/emb/rerank/result). "
        "Пусто → берётся env REDIS_URL; если и его нет — кэш отключён "
        "(graceful fallback, работает как без Redis).",
    ),
) -> None:
    """Запустить web-интерфейс в браузере (Step 2)."""
    import uvicorn

    from newscore.web import create_app
    from newscore.embeddings import DeviceUnavailable, resolve_device

    configure(level=log_level, fmt="console")

    # Инициализация кэша до warmup: явный --redis-url бьёт env REDIS_URL.
    from newscore import redis_cache

    if redis_url:
        redis_cache.set_cache(redis_cache.RedisCache(url=redis_url))
    cache = redis_cache.get_cache()
    print(f"[cache] redis = {'enabled' if cache.enabled else 'disabled'}")

    try:
        dev = resolve_device(device)
    except DeviceUnavailable as exc:
        # fail-fast: явно запрошенный --device cuda недоступен — не стартуем
        # молча на CPU, а падаем с понятным сообщением.
        print(f"[device] ОШИБКА: {exc}")
        raise typer.Exit(code=1) from exc
    print(f"[device] torch device = {dev}")
    if warmup:
        _warmup_models(default_matcher, device=dev, warmup_all=warmup_all)
    service = _build_service(db, config)
    app_ = create_app(service, default_matcher=default_matcher)
    uvicorn.run(app_, host=host, port=port, log_level=log_level.lower())


def _warmup_models(
    default_matcher: str, device: str = "auto", warmup_all: bool = False
) -> None:
    """Eager-init ML моделей чтобы первый user request не ждал cold load.

    e5-base: 7s холодный → 0.02s горячий запрос.
    bge-reranker-v2-m3: 4s холодный → доступ к pre-loaded weights.

    На CUDA модели остаются резидентными в VRAM (sentence-transformers
    держит их на device между запросами). warmup_all=True грузит обе
    модели независимо от default_matcher — «всё в боевой готовности».
    """
    import time

    on_cuda = device.startswith("cuda")
    # На GPU имеет смысл грузить всё сразу (VRAM есть); warmup_all форсит это.
    load_all = warmup_all or on_cuda
    needs_e5 = load_all or default_matcher in {"embedding", "hybrid", "rerank"}
    needs_rerank = load_all or default_matcher == "rerank"
    if not (needs_e5 or needs_rerank):
        return

    if needs_e5:
        from newscore.embeddings import get_st_model

        t = time.time()
        m = get_st_model("intfloat/multilingual-e5-base", device=device)
        # Прогон tiny encode для разогрева CUDA-контекста / mlock weights.
        m.encode(["warmup"], normalize_embeddings=True, show_progress_bar=False)
        print(f"[warmup] e5-base ready on {device} in {time.time() - t:.1f}s")
    if needs_rerank:
        from newscore.embeddings import get_reranker_model

        t = time.time()
        rr = get_reranker_model(device=device)
        rr.predict([("q", "d")], batch_size=1, show_progress_bar=False)
        print(
            f"[warmup] bge-reranker-v2-m3 ready on {device} "
            f"in {time.time() - t:.1f}s"
        )

    if on_cuda:
        _log_vram()


def _log_vram() -> None:
    """Залогировать занятую/зарезервированную VRAM (только для cuda)."""
    try:
        import torch

        if torch.cuda.is_available():
            alloc = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            name = torch.cuda.get_device_name(0)
            print(
                f"[vram] {name}: allocated {alloc:.2f} GB, "
                f"reserved {reserved:.2f} GB"
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[vram] недоступно: {type(exc).__name__}")


@app.command("briefing")
def briefing(
    query: str = typer.Argument(..., help="NL-запрос пользователя"),
    matcher: MatcherChoice = typer.Option(MatcherChoice.embedding, "--matcher"),
    top_n: int = typer.Option(10, "--top-n"),
    days: int = typer.Option(7, "--days"),
    trace: bool = typer.Option(False, "--trace"),
    summary: bool = typer.Option(True, "--summary/--no-summary"),
    log_format: LogFormat = typer.Option(LogFormat.console, "--log-format"),
    log_level: str = typer.Option("INFO", "--log-level"),
    config: Path = typer.Option(
        Path("configs/sources.yaml"), "--config", "-c", exists=True
    ),
) -> None:
    """Собрать брифинг по NL-запросу (Step 0 core)."""
    q = query.strip()
    if not q:
        print(json.dumps({"error": "query is empty"}, ensure_ascii=False))
        raise typer.Exit(code=2)

    run_id = uuid.uuid4().hex[:12]
    configure(level=log_level, fmt=log_format.value, run_id=run_id)

    cfg = load_config(config)
    parser = FeedParser(cfg)
    repo = InMemoryRepository()
    tw = TraceWriter(run_id=run_id, dir=Path("traces")) if trace else None
    deps = BriefingDeps(
        parser=parser,
        matcher_factory=_matcher_factory,
        repository=repo,
        trace_writer=tw,
        summarizer=ExtractiveSummarizer() if summary else None,
        domain_checker=DomainChecker(),
    )
    orch = BriefingOrchestrator(cfg=cfg, deps=deps)
    req = BriefingRequest(
        query=q,
        top_n=top_n,
        freshness_days=days,
        matcher_name=matcher.value,
        trace=trace,
        run_id=run_id,
        use_result_cache=True,  # one-shot: повтор того же запроса мгновенный
    )
    result = orch.run(req)

    sys.stdout.write(result.model_dump_json(indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()

    if result.meta.reason == "all_sources_failed":
        raise typer.Exit(code=1)


_SUBCOMMANDS = {"briefing", "theme", "daemon", "web"}


def main() -> None:
    """Entry point с backward-compat роутингом.

    `newscore "query"` без подкоманды → перенаправляем на `newscore briefing "query"`,
    чтобы README/команда Step 0 продолжали работать.
    """
    if len(sys.argv) >= 2:
        first = sys.argv[1]
        if (
            first not in _SUBCOMMANDS
            and not first.startswith("-")
            and first not in {"--help", "-h"}
        ):
            sys.argv.insert(1, "briefing")
    app()


if __name__ == "__main__":
    main()
