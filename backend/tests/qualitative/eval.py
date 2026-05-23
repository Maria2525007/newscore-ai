"""Qualitative evaluation runner для Story 6 (step0-spec.md §8).

Два режима:
- ``collect`` — снимает snapshot корпуса (один прогон FeedParser, сохранение в JSONL).
- ``score``  — гоняет матчеры на snapshot против expected/qXX_*.yaml, считает precision@K.

Эталоны хранятся в ``expected/qXX_*.yaml`` рядом с этим скриптом.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import typer
import yaml

from newscore.config import load_config
from newscore.matcher import Bm25Matcher, EmbeddingMatcher, Matcher
from newscore.models import EnrichedArticle
from newscore.parser import FeedParser

app = typer.Typer(no_args_is_help=True, help="NewsCore Step 0 qualitative eval")

THIS_DIR = Path(__file__).parent
QUERIES_PATH = THIS_DIR / "queries.yaml"
EXPECTED_DIR = THIS_DIR / "expected"
SNAPSHOTS_DIR = THIS_DIR / "snapshots"
REPORTS_DIR = THIS_DIR / "reports"
DEFAULT_CONFIG = Path("configs/sources.yaml")


def _now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@app.command()
def collect(
    config: Path = typer.Option(DEFAULT_CONFIG, "--config", "-c", exists=True),
    days: int = typer.Option(7, "--days"),
    snapshot_id: str | None = typer.Option(None, "--id"),
) -> None:
    """Снять snapshot корпуса (один прогон FeedParser)."""
    cfg = load_config(config)
    sid = snapshot_id or _now_id()
    sdir = SNAPSHOTS_DIR / sid
    sdir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Collecting → {sdir}")
    t0 = time.time()
    parser = FeedParser(cfg)
    report = parser.collect(cfg.sources, freshness_days=days)
    dur = time.time() - t0

    corpus_path = sdir / "corpus.jsonl"
    with corpus_path.open("w", encoding="utf-8") as f:
        for a in report.articles:
            f.write(a.model_dump_json() + "\n")

    meta = {
        "snapshot_id": sid,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "freshness_days": days,
        "articles_count": len(report.articles),
        "partial": report.partial,
        "failed_sources": [fs.model_dump() for fs in report.failed_sources],
        "by_source": _count_by_source(report.articles),
        "duration_s": round(dur, 2),
    }
    (sdir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    typer.echo(
        f"✓ {len(report.articles)} статей за {dur:.1f}s, partial={report.partial}"
    )
    typer.echo(f"  snapshot_id = {sid}")


def _count_by_source(articles: list[EnrichedArticle]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in articles:
        counts[a.source] = counts.get(a.source, 0) + 1
    return counts


def _load_corpus(snapshot_id: str) -> list[EnrichedArticle]:
    path = SNAPSHOTS_DIR / snapshot_id / "corpus.jsonl"
    if not path.exists():
        raise typer.BadParameter(f"no snapshot at {path}")
    out: list[EnrichedArticle] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(EnrichedArticle.model_validate_json(line))
    return out


def _load_queries() -> list[dict]:
    with QUERIES_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)["queries"]


def _load_expected(query_id: str) -> dict | None:
    matches = sorted(EXPECTED_DIR.glob(f"{query_id}_*.yaml"))
    if not matches:
        return None
    with matches[0].open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_matcher(name: str) -> Matcher:
    if name == "embedding":
        return EmbeddingMatcher()
    if name == "bm25":
        return Bm25Matcher()
    raise ValueError(f"unknown matcher: {name}")


@app.command()
def score(
    snapshot_id: str = typer.Option(..., "--id"),
    top_n: int = typer.Option(10, "--top-n"),
    matchers: str = typer.Option("embedding,bm25", "--matchers"),
    threshold: float = typer.Option(0.5, "--threshold"),
    required_passed: int = typer.Option(4, "--required-passed"),
) -> None:
    """Прогнать матчеры на snapshot, посчитать precision@N, отчёт markdown."""
    corpus = _load_corpus(snapshot_id)
    queries = _load_queries()
    matcher_names = [m.strip() for m in matchers.split(",") if m.strip()]
    cached_matchers = {n: _build_matcher(n) for n in matcher_names}

    rows: list[dict] = []
    missing_expected: list[str] = []
    for q in queries:
        qid = q["id"]
        qtext = q["text"]
        expected = _load_expected(qid)
        if expected is None:
            missing_expected.append(qid)
            continue
        expected_urls = {str(u).rstrip("/") for u in (expected.get("expected_top10_urls") or [])}

        row: dict = {"id": qid, "query": qtext, "expected": len(expected_urls)}
        for name in matcher_names:
            matches = cached_matchers[name].rank(qtext, corpus, top_n=top_n)
            returned = [str(m.article.url).rstrip("/") for m in matches]
            overlap = expected_urls & set(returned)
            # primary metric (DoD): precision@top_n
            precision = len(overlap) / top_n
            # secondary: recall and capped precision (honest for small expected sets)
            recall = len(overlap) / len(expected_urls) if expected_urls else None
            cap_k = min(top_n, len(expected_urls)) if expected_urls else top_n
            cap_precision = (len(overlap) / cap_k) if cap_k else None
            row[f"{name}_precision"] = precision
            row[f"{name}_recall"] = recall
            row[f"{name}_cap_precision"] = cap_precision
            row[f"{name}_overlap"] = len(overlap)
            row[f"{name}_returned"] = len(returned)
        rows.append(row)

    report_md = _render_report(
        rows,
        snapshot_id=snapshot_id,
        top_n=top_n,
        matcher_names=matcher_names,
        threshold=threshold,
        required_passed=required_passed,
        missing_expected=missing_expected,
        corpus_size=len(corpus),
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rid = _now_id()
    rpath = REPORTS_DIR / f"{rid}.md"
    rpath.write_text(report_md, encoding="utf-8")
    typer.echo(report_md)
    typer.echo(f"\n✓ Saved {rpath}")

    # DoD: эталон в spec'е — embedding ≥ threshold на ≥ required_passed
    primary = matcher_names[0]
    passed = sum(1 for r in rows if r.get(f"{primary}_precision", 0) >= threshold)
    if passed < required_passed:
        raise typer.Exit(code=1)


def _render_report(
    rows: list[dict],
    *,
    snapshot_id: str,
    top_n: int,
    matcher_names: list[str],
    threshold: float,
    required_passed: int,
    missing_expected: list[str],
    corpus_size: int,
) -> str:
    lines: list[str] = []
    lines.append(f"# Qualitative eval — snapshot `{snapshot_id}`")
    lines.append("")
    lines.append(f"- Corpus: **{corpus_size}** статей")
    lines.append(f"- top_n = {top_n}, threshold = {threshold}, required = {required_passed}/7")
    if missing_expected:
        lines.append(f"- ⚠ Нет эталонов для: {', '.join(missing_expected)}")
    lines.append("")
    lines.append(f"## Primary metric: precision@{top_n} (DoD из spec §8)")
    lines.append("")
    header = "| Query | Expected |" + "".join(f" {n} p@{top_n} ({n} hit) |" for n in matcher_names)
    sep = "|---|---|" + "---|" * len(matcher_names)
    lines.append(header)
    lines.append(sep)
    for r in rows:
        cells = [f"`{r['id']}` {r['query'][:60]}", str(r["expected"])]
        for n in matcher_names:
            p = r.get(f"{n}_precision", 0)
            o = r.get(f"{n}_overlap", 0)
            cells.append(f"{p:.2f} ({o})")
        lines.append("| " + " | ".join(cells) + " |")
    if rows:
        avg_cells = ["**avg**", "—"]
        for n in matcher_names:
            avg = sum(r.get(f"{n}_precision", 0) for r in rows) / len(rows)
            avg_cells.append(f"**{avg:.2f}**")
        lines.append("| " + " | ".join(avg_cells) + " |")

    lines.append("")
    lines.append("## Secondary: capped precision (precision@min(K, |expected|))")
    lines.append("")
    lines.append("Честная метрика для запросов с малым |expected| — потолок precision@K не ограничен лимитом эталона.")
    lines.append("")
    sec_header = "| Query | |expected| |" + "".join(f" {n} cap_p ({n} hit/total) |" for n in matcher_names)
    sec_sep = "|---|---|" + "---|" * len(matcher_names)
    lines.append(sec_header)
    lines.append(sec_sep)
    for r in rows:
        cells = [f"`{r['id']}`", str(r["expected"])]
        for n in matcher_names:
            cp = r.get(f"{n}_cap_precision")
            o = r.get(f"{n}_overlap", 0)
            cp_str = f"{cp:.2f}" if cp is not None else "—"
            cells.append(f"{cp_str} ({o}/{r['expected']})")
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("## DoD (step0-spec §8)")
    for n in matcher_names:
        passed = sum(1 for r in rows if r.get(f"{n}_precision", 0) >= threshold)
        verdict = "✅" if passed >= required_passed else "❌"
        lines.append(
            f"- **{n}**: {passed}/{len(rows)} запросов с precision@{top_n} ≥ {threshold} {verdict}"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    app()
