# NewsCore AI

> A briefing-first news agent. On a natural-language query ("exchange rate"), it pulls
> relevant material from 5 Russian business news sources, ranks it with an embedding
> matcher, and produces a 2–3 sentence extractive summary.
>
> Step 0 (CLI core) is done. Steps 1–3 (themes + scheduler, browser UI, summarizer)
> were built for the ITMO defense (2026-05-29) and aren't under active development
> right now.

My part: product spec, user research (custdev), part of the backend/CLI implementation,
and the pitch/presentation site — see
[startup-project](https://github.com/Maria2525007/startup-project).

---

## Quick start

```bash
# 1. Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Dependencies — pick a torch backend (sentence-transformers needs one)
uv sync --extra cpu      # default — VPS / Mac (CPU+MPS) / any machine without a GPU
# uv sync --extra cu128  # GPU server with CUDA 12.8

# 3. One-shot briefing
uv run newscore "exchange rate"

# 4. Or: create a theme and open it in the browser
uv run newscore theme create "exchange rate" --period 30m
uv run newscore web                                   # http://127.0.0.1:8000
```

First run downloads the embedding model `intfloat/multilingual-e5-base` (~280 MB) —
2–3 minutes on an average connection. Later runs take seconds.

---

## CLI

### Step 0 — one-shot briefing

```
uv run newscore "natural language query" [options]
uv run newscore briefing "query" [options]            # equivalent

options:
  --matcher embedding|bm25     matcher (default: embedding)
  --top-n N                    how many items in the output (default: 10)
  --days N                     freshness window in days (default: 7)
  --trace                      write a trace to traces/<run_id>.json
  --summary/--no-summary       extractive summary (default: on)
  --log-format console|json    stderr log format (default: console)
  --config PATH                path to sources.yaml
```

### Step 1 — themes and scheduler

```
uv run newscore theme create "query" --period 60m    # 60s|30m|2h|1d
uv run newscore theme list
uv run newscore theme show <id>
uv run newscore theme run <id>                        # run manually now
uv run newscore theme pause/resume/delete <id>
uv run newscore daemon                                # background, refreshes on schedule
```

State lives in `data/newscore.db` (SQLite, gitignored).

### Step 2 — web

```bash
# CPU server (default matcher = hybrid, ~1-2s/run)
uv run newscore web --host 127.0.0.1 --port 8000

# GPU machine: everything in VRAM + rerank ready to go (~0.1-0.3s/run)
uv sync --extra cu128
uv run newscore web --device cuda --default-matcher rerank --warmup-all
```

`--device cuda` (explicit) is **fail-fast**: if CUDA isn't available the process exits
1 with a clear error instead of silently falling back to CPU. For auto-select with a
silent CPU fallback, use `--device auto` (default).

Create a theme via a form, view the latest briefing, run it manually, pause it — all
in the browser. No auth, single-user, local. SQLite runs in WAL mode so `web` and
`daemon` can run at the same time.

**GPU mode.** sentence-transformers picks up CUDA on its own (`--device auto` → `cuda`
if available). `--warmup-all` loads e5 + bge-reranker-v2-m3 into VRAM at startup and
keeps them resident between requests; the reranker runs in fp16 automatically (2x
faster, half the VRAM). Startup logs show `[device] torch device = cuda` and
`[vram] <GPU>: allocated X GB`. Force CPU with `--device cpu` or `NEWSCORE_DEVICE=cpu`.

### Cache (Redis) — speeds up prod/defense runs

Optional multi-layer cache. **Everything works without Redis** (graceful fallback).
Enabled by setting `REDIS_URL` (or `--redis-url`):

```bash
# start Redis (Docker)
docker run -d --name nc-redis -p 6379:6379 redis:7-alpine

export REDIS_URL=redis://localhost:6379/0
uv run newscore web --device cuda --default-matcher rerank --warmup-all
# startup log shows: [cache] redis = enabled
```

What's cached (TTLs tuned to "moderately aggressive"):

| Layer | Key | TTL | Effect |
|---|---|---|---|
| RSS feed | `nc:feed:*` | 90s | a repeat refresh doesn't hit the source again |
| Article body | `nc:body:*` | 24h | don't fetch+parse the same article twice (the most expensive parse step) |
| Passage embedding | `nc:emb:*` | 24h | don't re-embed an unchanged article (L1 in-memory + L2 Redis) |
| Rerank score | `nc:rr:*` | 6h | **don't re-run the cross-encoder** on the same (query, article) pair — the main CPU bottleneck |
| Briefing result | `nc:brief:*` | 3min | an identical one-shot query returns instantly |

Invalidation is by content hash: if an article's text changed, the key changes and it
gets recomputed. Otherwise the cached result (same score, no re-matching) is reused.

Tune fetch parallelism to your hardware without touching YAML:
```bash
export NEWSCORE_FETCH_TOTAL=64       # concurrent HTTP connections (default 64)
export NEWSCORE_FETCH_PER_HOST=10    # per source (default 10)
```

---

## Briefing output (one-shot)

JSON on stdout:

```json
{
  "query": "...",
  "items": [
    {
      "article": {
        "title": "...", "url": "...", "source": "rbc",
        "published_at": "...", "snippet": "...",
        "body": "...", "summary": "2-3 key sentences."
      },
      "score": 0.87
    }
  ],
  "meta": {"run_id": "...", "matcher_name": "embedding", "partial": false,
           "failed_sources": [], "reason": "ok"}
}
```

Full schema — `raw/step0-architecture.md` §3.4.

---

## Structure

| Folder | Contents |
|---|---|
| `backend/src/newscore/` | Python package: CLI, parser, matcher, orchestrator, summarizer |
| `backend/src/newscore/themes/` | Step 1: SQLite + ThemeService + AsyncScheduler |
| `backend/src/newscore/web/` | Step 2: FastAPI + Jinja2 templates |
| `backend/tests/` | `unit/` / `integration/` / `qualitative/` / `e2e/` (114 + 6 Playwright) |
| `configs/sources.yaml` | Config for the 5 RSS sources |
| `data/` | SQLite database (gitignored) |
| `raw/` | Spec, architecture, brief, roadmap, baseline |
| `frontend/`, `infra/` | Stubs for Step 4+ |

---

## Docs

Key decisions are written up in `raw/`:

- `mvp-brief.md` — what we're building (v3)
- `step0-spec.md` — formal spec (user stories, MoSCoW, NFRs)
- `step0-architecture.md` — Step 0 architecture + 17 ADRs
- `step0-qual-baseline.md` — qual-eval results, DoD pivot rationale
- `step1-architecture.md` — Step 1 (SQLite + scheduler) + 6 ADRs
- `roadmap.md` — what layers on next (Step 4–5)

---

## Stack

| Layer | What |
|---|---|
| Runtime | Python 3.11+ via `uv` |
| HTTP | `httpx.AsyncClient` (async fetch with per-source semaphores) |
| RSS | `feedparser` |
| Body extraction | `trafilatura` via `asyncio.to_thread` |
| Embedding | `sentence-transformers` + `intfloat/multilingual-e5-base` |
| BM25 | `rank_bm25` (baseline comparison) |
| Summary | extractive top-K by cosine similarity (same e5-base, no LLM API) |
| Persistence | stdlib `sqlite3`, WAL mode |
| Scheduler | asyncio loop in `newscore daemon` |
| Web | `fastapi` + `jinja2`, minimal CSS |
| Tests | `pytest` + `respx` |

---

## Definition of Done

**Step 0** (closed 2026-05-23) — capped precision @ min(K, |expected|) ≥ 0.5 on ≥4 of 6
non-empty reference queries. Embedding scored 0.89 avg, BM25 0.47 avg. See
`raw/step0-qual-baseline.md`.

**Step 1** — a theme is created → the daemon sees it's due → runs Step 0 → diffs
against the previous run → saves to SQLite.

**Step 2** — in the browser: create a theme via a form, see the latest briefing, run
it manually, pause it.

**Step 3** — every article in a briefing has a 2–3 sentence `summary`, picked by
closeness to the query.
