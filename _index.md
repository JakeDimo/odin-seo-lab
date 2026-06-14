---
type: index
title: SEO Lab — Index
updated: 2026-06-03
---

# SEO Lab

Prototype home for the SEO learning loop — the Phase 1 on-ramp of [[seo-anatomy-engine]]. Lives in the main vault for now; the Lucas / research-lab split is deferred (Jake, 2026-06-03: "get the research working first, figure out sharing later").

## Contents
- `wiki/seo-lab/seo_parse.py` — shared field extractor (one source of truth for both scrapers)
- **Daily cloud pipeline** (accumulate-mode): `serp_batch.py` (rotating 1/3 of `keywords.json`) → `scrape_render.py` → `enrich_dataforseo.py` (traffic + ranked-keywords; backlinks deferred) → `pagespeed.py` (Core Web Vitals sample) → `accumulate.py` (append to corpus) → `grade.py` (grade the whole corpus)
- `wiki/seo-lab/keywords.json` — keyword pool (36, rotated /3 across daily runs)
- `wiki/seo-lab/data/corpus.jsonl` — the accumulating page corpus (grows each run; the path to a sample big enough to call something a rule)
- `wiki/seo-lab/grades/corpus-latest.md` — current corpus grade (correlations / leads, **not rules** — see disclaimer in the file)
- `wiki/seo-lab/scrape_render.py` — **render path** (Playwright Chromium): rendered DOM + screenshot + raw-vs-rendered JS-dependency diff. Setup once: `uv run --with playwright python -m playwright install chromium`. Run: `uv run --with playwright --with beautifulsoup4 --with requests scrape_render.py data/urls_clients.json data/results_render.json`
- `wiki/seo-lab/scrape_page.py` — fast path (requests, no JS) + raw-HTML storage
- `wiki/seo-lab/scrape_onpage.py` — v1 on-page extractor (kept for reference)
- `wiki/seo-lab/data/render/` + `data/screenshots/` — rendered HTML + full-page screenshots
- `wiki/seo-lab/data/` — input URL lists (`urls.json`) + raw results (`onpage_results.json`)
- Dated teardowns:
  - [[2026-06-03-marketing-agency-teardown]] — marketing agencies, US, on-page only (first run)
- Reference:
  - [[signal-checklist]] — master catalogue of every signal we scrape + the rigor / promotion gates
  - [[seed-hypotheses]] — practitioner / leak / experiment theories to test, hat-tagged

## How findings graduate
Hunch (1 niche) → Pattern (2+ niches) → Validated (counter-examples explained) → Actionable (≥90%, live-tested). Confidence model lives in [[seo-anatomy-engine]].
