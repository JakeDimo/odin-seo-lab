---
title: Page-one differentiators — what orders the top 3
type: spec
status: active
updated: 2026-06-08
---

# What orders the TOP 3 within page 1

**Plain-English version:** getting *onto* page one and *winning* page one are two different games. Our own corpus proves it. Across the top 10, the authority signals (backlinks, referring domains, Authority Score) are basically flat. So backlinks are the **ticket onto page one**, not the thing that sorts positions 1, 2, 3 from 4 through 10. The sorter is a different layer Google calls re-ranking, and almost all of it is a signal class we were not yet capturing. This doc names that class and makes it measurable.

> **Status of everything below: LEADS, not rules.** These are correlational reads from public studies, the 2024 Google "Content Warehouse" leak, and Google patents. None is a confirmed live ranking weight. A signal only earns the word "rule" after it survives an authority-controlled comparison in our corpus *and* a controlled live test. (See `methodology.md`.)

---

## What our data already showed (the negative result)

Within page 1: referring domains 216 (top-3) vs 188 (4-10), Authority Score 12 vs 14 — flat. Word count and internal links show a *modest* top-3 edge; everything else we capture is flat. Conclusion: the real lever lives in signals we hadn't captured. The flat-authority finding is an **asset** — it gives us a clean band where top-3 and 4-10 are equally linked, so anything that separates them there is the re-ranking layer showing through.

---

## The 8 hypotheses (ranked by evidence strength)

| # | Hypothesis | Strength | Mechanism / source |
|---|---|---|---|
| **H1** | **Click satisfaction beats expected CTR for the slot** (NavBoost / COEC — clicks over expected clicks for that position) | **Strongest** | NavBoost confirmed under DOJ oath + leak as the *re-ranker* on the retrieved set. This is the only hypothesis that tests the sorting mechanism itself. Measurable on **our own** pages via GSC. |
| **H2** | **Brand demand** (branded search volume, unlinked brand mentions, Knowledge-Panel presence) | Strong | Ahrefs 75K-brand study: branded web mentions (0.66), branded anchors (0.53), branded search (0.39) all *beat* DR (0.33) and referring domains (0.30). Most likely reason a flat-authority SERP reshuffles. |
| **H3** | **Relevance / intent-format match, measured semantically** (a blog ranking a transactional query loses) | Strong | Semrush 16,298-keyword study: BERT text-relevance vs the rest of the SERP (0.47) dominated; keyword-in-title presence "not a strong impact" (75%+ already clear that floor). |
| **H4** | **Content comprehensiveness vs the SERP** (subtopic coverage, not raw length) | Moderate-strong | Backlinko 11.8M: +1 Content Grade ≈ +1 position; raw word count did *not* vary by position. Matches our modest word-count edge. |
| **H5** | **Information gain / originality** | Moderate (highest value if true, hardest) | Leak fields `OriginalContentScore`, `contentEffort`; 2024 Information-Gain patent. |
| **H6** | **Freshness, but only on query-deserves-freshness queries** | Conditional | Freshness is query-gated. Headline is the **freshness × query-type interaction**, not freshness alone. |
| **H7** | **Link QUALITY gradient, not volume** (median referring-domain DR, anchor relevance) | Moderate | Volume is flat (as predicted); the untested cut is quality at equal counts. |
| **H8** | **Core Web Vitals / UX as a gate, not a lever** | Weak within page 1 | Backlinko + our own data: flat across positions. **Treat as pass/fail ceiling. Stop investing here.** |

---

## What we capture NOW (live as of 2026-06-08)

Seven new signals, all pure HTML or label parsing in `seo_parse.py` — **zero extra API spend**. They flow through `accumulate.py` into the corpus and surface in `grades/by-position-latest.md` (top-3 vs 4-10 vs non-placer). They are sparse until the 8-hourly rotation re-scrapes the full pool (~1 day), then compound.

| Signal (field) | Tests | What it proxies |
|---|---|---|
| `page_age_days`, `date_modified`, `has_freshness_date` | H6 | Freshness (from JSON-LD dates, `article:modified_time`, `<time>`) |
| `page_type` {home/blog-article/product/service/category/other} | H3 | Format-vs-intent match (page side) |
| `title_ctr_score` /5 (+ number, bracket, power-word, 40-60 char, query-front-loaded) | H1 | Title click-attractiveness (the NavBoost input we *can* see) |
| `query_in_title` / `query_in_h1` / `query_in_lead` / `query_early_title` | H3 | Exact-query placement (hygiene floor) |
| `eeat_score` /3 (`has_author`, `has_review_date`) | E-E-A-T | Authorship completeness (bites hardest in YMYL, e.g. SATH) |
| `list_count`, `table_count`, `has_faq`, `lead_para_words` | H1 (answer-first) | Answer/structure satisfaction |
| `stat_count` | H5 | Original-data density (info-gain proxy) |

---

## What's NEXT (deferred, in priority order)

**Needs-API (services we already pay for):**
1. **COEC ratio (H1) — the single most mechanism-aligned test.** GSC tool `s4675016`: our-pages-only actual CTR ÷ expected-CTR for the slot. Regress next-period position change on this-period COEC. This is the priority once the easy signals have a few days of data.
2. **SERP-feature flags + query-intent label (H1, H3).** Capture the SERP `description` and feature types (featured snippet, PAA, local pack, AI overview, knowledge graph) that `serp_batch.py` currently discards; add DataForSEO Labs `search_intent`. (Requires plumbing the SERP record through `scrape_render.py`.)
3. **Anchor-text relevance + exact-match % (H7)** and **referring-domain DR gradient (H7)** via Semrush `backlinks` / referring-domains export.
4. **Brand-demand bundle (H2):** Semrush branded-search volume + brand-mention count + Knowledge-Panel flag.

**Hard (new module — embeddings / re-crawl):**
5. **Embedding cosine(query, page) and cosine(page, top-3 centroid) (H3/H4)** — expected to be the strongest single separator.
6. **SERP-relative subtopic/entity coverage (H4)** — per-keyword heading/entity union, score each page's coverage %.
7. **Content novelty vs SERP corpus (H5)** and **measured change-rate (H6)** — re-crawl + diff to separate genuine updates from date-stamp gaming.

---

## How to test (winners = pos 1-3, challengers = pos 4-10)

The harness is `analyze_by_position.py` (buckets top-3 / 4-10 / 21-45; new signals added to its `NUM`/`BIN` lists + a page-type cross-tab).

**The one control that makes it meaningful:** fresher / deeper / branded pages tend to be better-linked too. Before crediting any signal, condition on authority — either (a) restrict to SERPs where top-3 and 4-10 have near-equal referring domains (we proved that band exists), or (b) run `P(top3) ~ signal + referring_domains + domain_rank + word_count` and read the signal's coefficient.

**Promotion bar.** Position-bucket comparisons are correlational snapshots = leads only. Anything that survives the authority-controlled comparison gets promoted to a controlled live test (single-variable change on stuck-at-4-7 pages, GSC-tracked 6-12 weeks) before it earns "rule". The ~13-month NavBoost window means click-signal tests need weeks, not days.

---

## Findings audit — 2026-06-08 (663-page snapshot, 6 adversarial skeptics)

> **SUPERSEDED 2026-06-09 by the 2,659-page re-audit below.** Most conclusions held, with one big change: internal links, dismissed here as a plumbing-only confound, was promoted to the single confirmed lead once the sample was big enough for a proper joint-control model. The 663 read was itself underpowered.

**Bottom line: 0 of 6 candidates survived as confirmed rules.** Six independent skeptics re-tested each signal on the frozen 663-page snapshot, authority-controlled, each trying to refute. Every signal is either underpowered or a confound. This is the system working: the adversarial pass killed three signals my first read had credited.

| Lead | Verdict | Conf. | min cell n | What it means |
|---|---|---|---|---|
| **query front-loaded in title** | underpowered | low | 31 | Cleanest of the lot. Clean band +17.6pt, holds in both testable niches, not a home-page artefact. Only z=1.73 (needs 1.96) stops it. |
| **title length 40-60 chars** | underpowered | medium | 13 | Real, consistent +14pt across every niche and band, survives removing home pages. Chi-square 3.80 (needs 3.84). |
| **internal links (plumbing only)** | niche-specific | low | 21 | Genuine +30 mid-band edge in plumbing (+74 ex-home); flat/reversing elsewhere. A plumbing experiment, not a rule. |
| query in title (exact) | authority-confound | medium | 31 | Killed. Home/brand pages ("Service City \| Brand") mechanically contain the query and over-index in top-3 (+15.8pt); ordinary pages +1.5pt. The lever is page type, not the title. |
| word count (depth) | authority-confound | medium | 1 | Killed. +166 not significant (p=0.37), flips negative when tightly authority-matched, reverses in 2 of 3 niches (Simpson's paradox via window-cleaning). |
| freshness (page age) | authority-confound | medium | 23 | Killed. "111 days fresher" is a median artefact; the mean has top-3 slightly older, effect size 0.53 (0.50 = none). Halves to -45d when authority-matched. 41% of rows have no date. |

**Why nothing is conclusive yet:** every clean-band cell is only ~13-31 top-3 pages. The two title leads point the right way and survive the confound checks, but they sit just under statistical significance purely on sample size. **More data (more keywords, more niches) is the unlock** — that is what the widened 162-keyword pool and the nightly rotation are for. Shortlist for an eventual live test, in order: (1) query front-loaded in title, (2) 40-60 char title, (3) internal links in plumbing.

---

## Re-audit — 2026-06-09 (2,659-page corpus, all 6 niches, 6 adversarial skeptics)

**This is the authoritative finding; it supersedes the 663-page audit above.** The corpus quadrupled (663 → 2,659 pages; top-3 now 375). At proper sample size the story changed: more data mostly **killed** the leads rather than confirming them. **1 of 6 confirmed, 1 weak maybe, 4 are confounds.**

| Lead | Verdict | Significant? | vs 663 | Plain-English meaning |
|---|---|---|---|---|
| **Internal links to the page** | ✅ confirmed-lead | yes (logistic p=0.019) | stronger | More internal links pointing at a page tracks top-3 even after stripping out backlinks + homepage nav. The one real on-page lever. |
| Title 40-60 chars | ~ weak maybe | borderline (pooled p≈0.049, flat elsewhere) | weaker | Thin and contradicted by a flat continuous test. Cheap to test, not a rule. |
| Query front-loaded in title | ✗ confound | no (raw p=0.073) | washed out | +17.6pt at 663 → +5.4pt now, fails even the raw test. Small-sample noise; 3 of 6 niches reverse. |
| Exact query in title | ✗ confound | no (CMH p>0.05) | weaker under control | Homepage/brand-title artefact ("Service City \| Brand"). On real content pages +2.4pt, not significant. |
| Word count / depth | ✗ confound | no (controlled p=0.117) | weaker | Longer = more backlinks + long page types, not length driving rank. Double-control washes to +106 words, p=0.76. |
| Freshness (page age) | ✗ confound | no (controlled p=0.26) | washed out (confirmed null) | Younger homepages crowding top-3. No query-deserves-freshness pattern survives. |

**Headline:** of every on-page/content signal we can scrape, **internal linking to the page is the only one that holds up as a within-page-1 correlate at scale, with authority and page-type controlled.** Keyword-in-title, word count, and freshness only *look* like they matter because they ride along with authority. The clincher for internal links: homepages crowd top-3 yet carry *fewer* internal links, so they drag the gap down rather than inflate it, and the effect persists inside service (+27), product (+48) and home (+16) page types; plumbing (+31, p=0.003) and electrician (+32, p=0.003) replicate individually.

**Why the 663 read flipped:** more data didn't power up the title leads, it exposed them as regression-to-the-mean noise; and a proper joint-control logistic (only possible at the bigger n) promoted internal links from "plumbing-only confound" to the one confirmed lead. This vindicates pulling more data before acting on anything.

**Shortlist for a controlled live test, ranked:** (1) internal links to a stuck mid-pack page [highest confidence], (2) title length 40-60 chars [cheap; plumbing showed +12pt], (3) front-loaded query in title [can ride along with #2]. Still correlations until a live single-variable change moves the needle.

---

**Files:** `seo_parse.py` (live signals), `accumulate.py` (KEEP list), `analyze_by_position.py` (test harness), `serp_batch.py` (SERP features — deferred), `backlinks_semrush.py` (anchor/DR — deferred), GSC tool `s4675016` (COEC — next). Research provenance: 6-agent workflow, 2026-06-08.
