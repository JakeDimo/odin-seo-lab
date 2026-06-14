---
title: SEO Lab — index & how to read it
type: index
status: active
updated: 2026-06-09
---

# SEO Lab

An autonomous, self-auditing experiment to work out what actually makes pages rank in Australian local-service search. Every 8 hours it pulls a rotating third of the keyword pool's SERPs (so the FULL pool gets a rank observation daily), renders only new or stale pages, accumulates everything into a growing corpus, and re-grades the whole thing so findings sharpen over time. Built to run for the long term.

## Start here (the three things to read)

1. **[[insights]]** — the living "what we know" digest. Read this first. Confirmed leads, debunked myths, open hypotheses.
2. **[[findings-log]]** — how the findings have *evolved* over time (each audit dated). This is where the long-term story lives as the data densifies.
3. **`grades/corpus-latest.md`**, **`grades/by-position-latest.md`** and **`grades/movement-latest.md`** — the latest auto-refreshed scoreboards (rewritten every run; movement = the longitudinal rank-tracking read).
4. **`grades/rulebook.md`** — the auto-generated, confidence-rated rulebook (LEAD vs CONFOUND vs WATCH per factor; defers to the audit-verified verdicts; refreshed every run). And **[[experiments]]** — the controlled-live-test ledger, the **only** path from a correlational lead to a proven RULE. Filling its "Rules" section is the end goal.

Deeper specs: [[page-one-differentiators]] (the within-page-1 question), [[gsc-click-behaviour]] (our own Search Console / click read), [[methodology]] (winner definition, CTR curve, controls).

## How the data is organised (so it stays readable as it grows)

- **`data/corpus/*.jsonl`** — the raw corpus, written as one small SHARD per run (never one giant file, so concurrent runs never collide). The graders read every shard and dedupe to the latest observation per page.
- **`data/corpus.jsonl`** — legacy single file, still read for back-compat.
- Each page row carries: rank label, on-page signals (title/headings/links/schema/word count/keyword density/freshness/page-type/E-E-A-T), authority (referring domains, Authority Score), traffic + ranked-keyword breadth, and Core Web Vitals.
- **One signal = one column.** New hypotheses become new columns, never new files, so the audit harness picks them up automatically.

## The pipeline (run order, all driven hourly by `.github/workflows/seo-grade.yml`)

| Step | Script | Does |
|---|---|---|
| 1 | `gen_keywords.py` | Builds `keywords.json` (services x cities + national terms + cluster test bed). |
| 2 | `serp_batch.py` | Pulls AU SERPs per keyword (a rotating 1/3 slice per run), winners + losers + SERP features. |
| 3 | `filter_render.py` | **Incremental split:** never-seen / >14-day-stale URLs go to render; already-fresh URLs become cheap rank-only observations. This is what keeps a run inside the free Actions quota. |
| 4 | `scrape_render.py` | Renders the new+stale pages (Playwright, chunked + crash-proof) and extracts on-page signals via `seo_parse.py`. |
| 5 | `enrich_dataforseo.py` | Adds traffic + ranked-keyword count (DataForSEO Labs). |
| 6 | `backlinks_semrush.py` | Adds referring domains / Authority Score (Semrush, cached once per domain) — runs on rendered AND rank-only rows so authority coverage compounds. |
| 7 | `pagespeed.py` | Samples Core Web Vitals (PageSpeed Insights). |
| 8 | `accumulate.py` | Writes this run's shards into `data/corpus/` (rendered rows stamp `rendered_date`; rank-only rows merge into their page via the coalescing loader while the shard preserves rank history). |
| 9 | `grade.py` + `analyze_by_position.py` + `analyze_movement.py` | Re-grade the whole corpus → `grades/`. |

**Analysis tools (run on demand):** `analyze_controlled.py` (authority-controlled read — the one that tells leads from confounds), `analyze_breadth.py` (does a winner own a related-keyword cluster), `analyze_movement.py` (longitudinal rank movement / top-3 stickiness), `gsc_coec.py` (click-behaviour on our own client pages).

## Running it

- It runs itself every 8 hours in the cloud and pings Slack #admin. Nothing manual required.
- Local commands use `uv` (e.g. `uv run analyze_controlled.py data/corpus.jsonl`). Note: the DataForSEO SERP POST is refused from the home network — SERP pulls only work from cloud egress; everything else runs fine locally.
- Re-run the full adversarial audit by re-invoking the `verify-page1-leads` workflow against a fresh `data/analysis_snapshot.json`.

## Cost & cadence

- Every 8h, a rotating 1/3 of the pool per run → the full 1,726-keyword pool gets a rank observation daily; each page re-renders at most fortnightly (`RENDER_TTL_DAYS`).
- DataForSEO is the only real meter (~1,726 SERP calls/day). Semrush is cached once-per-domain and degrades gracefully if it caps.
- **GitHub Actions is NOT free at scale (learned 2026-06-10):** private-repo free tier = 2,000 runner-minutes/month, and the old hourly render-everything design burned ~75 min/run — the quota died and the pipeline silently stopped (no runner = not even the Slack alert fires). The incremental design budgets ~45-60 min/day. Don't add burst runs without checking the remaining quota (Settings → Billing), and expect scheduled runs to resume by themselves when the monthly quota resets.
- Keep the DataForSEO balance topped up or runs fail gracefully (Slack ❌).

## Scope & honesty

Findings are **Australian local-service SERPs** and **correlational** until a controlled live test moves the needle. See the findings-are-not-rules discipline in [[methodology]].
