---
type: seo-reference
title: SEO Learner — Ranking-Factor Findings & Methodology Spec
created: 2026-06-08
updated: 2026-06-08
status: living document
---

# SEO Learner — Ranking-Factor Findings & Methodology Spec

*Decision-grade synthesis for the SEO-learning lab. Built 2026-06-08 from a multi-agent research bundle (Backlinko 11.8M, Advanced Web Ranking 3M, SupportHost 60K, Portent 5.8M, Ahrefs 44.6K, SearchPilot/Etsy split-tests, Google primary docs) + adversarial verdicts, then checked against a position-bucketed read of our own 663-page corpus (§6). Per [[seed-hypotheses]] and the findings-are-not-rules rule: everything here is a lead or a method, not a law, until a controlled test confirms it.*

> **Within-page-1 sorting** (what orders top-3 once authority gets you onto page one — backlinks are flat there) has its own decision-grade spec: [[page-one-differentiators]]. Seven new HTML signals are live in the pipeline; the COEC/GSC test is next.

## 1. How to define a WINNER

### CTR by position (use these numbers)
Organic CTR collapses with position (pooled industry figures; order-of-magnitude):

| Position | Organic CTR | Share of #1's clicks |
|---|---|---|
| 1 | ~27–39% | 100% |
| 2 | ~15–18% | ~45–55% |
| 3 | ~10–11% | ~30% |
| 4 | ~7–8% | ~22% |
| 5 | ~5–6% | ~16% |
| 6–10 | ~2–4% | ~8–12% |
| 11–20 | ~1% | ~3% |
| 21–45 | <0.5% (~0) | ~1% |

**#1 ≈ as many clicks as #2–#4 combined; top-3 capture ~60–65% of all organic clicks; page 2+ is functionally zero.** So rank 21–45 is a "did-not-place" contrast cohort, not a graded outcome.

### Verdict — two-layer winner definition (adopt next)
**Layer 1 (binary, for hypothesis tests):** WINNER = position **1–3**; CHALLENGER = **4–10** (kept separate); NON-PLACER = **21–45** (contrast). Test winners vs non-placers first (cleanest), then winners vs challengers ("good vs great").
**Layer 2 (continuous, for ML/reporting):** `value = stepped_CTR_weight(position) × intent_multiplier`. Never regress on raw rank (treats 1→2 same as 31→32 — economically false).

### Segment BEFORE comparing (mandatory)
Stratify every test by **search intent** (transactional / commercial / informational / navigational) × **niche-family** (AU local-service vs national-service) × **page-type** (home / service / location / product / blog / category). Never compare a service page to a blog post (page-type leakage). Min **30 URLs/cell** for inferential tests; else descriptive + flag n.

### Traffic — control, not target
Page traffic is downstream of rank (reverse-causation) and the weakest candidate signal (~0.18 Spearman). Use it as a CrUX-coverage proxy + sanity filter, never the outcome. Ranked-keyword count = topical-breadth control, not the prize.

## 2. Page speed, properly framed
The literature splits, and the reconciliation is the finding: Google's own position is **no boost for fast, only a penalty for really slow; page experience is a tiebreaker subordinate to relevance** (with a mild gradient up to "Good", flat above). Mobile is the surface that matters (mobile-first, lower pass rates) — we correctly prioritised it.

**Our 8.3s-vs-6.2s "winners slower" finding is inadmissible** — confounded by CrUX coverage, page-type (top pages are heavier/richer → slower), and small n; both cohorts sit far above the 2.5s "Good" bar, so speed is neutral between two failing groups. Report it as a **null**, never "slow ranks better." Client frame (locked): speed is **hygiene + tiebreaker** — getting into the green removes a penalty and breaks ties; it won't out-rank stronger content/links.

**Speed tests to run:** binary all-Good pass-rate (not median seconds) · drop no-CrUX URLs first (report coverage per cohort) · three-zone (bad >4s / soft 2.5–4s / good <2.5s) win-rate · bootstrap any median before quoting · eventually a SearchPilot-style split test (the only causal answer).

## 3. Hypothesis bank (prioritised)
`Data`: HAVE (corpus now) / ANALYTICS (GSC/CrUX joins) / BACKLINKS (blocked) / SPLIT-TEST (causal). Top-10 to run now (have-data, high value): **A1, A2, A4, A6, A11, B1, B2, B6, D1, E1.** Theme C (off-page authority) jumps to top priority the day backlink data lands.

**A — On-page (table-stakes):** A1 kw-in-title near-universal, non-discriminating · A2 schema presence doesn't separate · A3 schema variety tracks page-type not rank · A4 word count doesn't separate within intent×page-type · A5 readability flat by position · A6 kw-in-URL is a table-stake (never cleanly measured — our chance) · A9 internal-link density separates winners more in national niches · A11 *black-hat:* any on-page "winner" diff is page-type leakage — must survive page-type control.

**B — Speed/CWV:** B1 pass-rate separates better than median seconds · B2 our reversed finding dissolves under pass/fail + CrUX-drop + page-type control · B3 soft gradient below Good · B4 only the really-slow tail penalised · B6 *CrUX-availability itself* correlates with winning (confounds everything).

**C — Off-page (blocked until backlinks):** C1 referring domains strongest correlate, esp. national (#1 ≈ 3.8× links of #2–10) · C2 authority near-necessary for competitive terms, NOT for local/long-tail · C3 *black-hat:* link-rank correlation is reverse-causation — can't call links "the driver" from observational data · C5 some winners (esp. local) rank with ~zero backlinks.

**D — Traffic/breadth:** D1 traffic is weakest signal + downstream → control only · D2 ranked-keyword count separates winners (but D3 *black-hat:* it's mechanically circular).

**E — Method:** E1 pooling local+national flips within-segment results · E2 range-restriction hides saturated factors (zero-correlation among universal adoption ≠ irrelevant) · E3 small-n medians unstable, pass-rates aren't.

## 4. Re-analysis / segmentation spec (by impact)
1. Stratify the whole corpus by intent × niche-family × page-type (min 30/cell). 2. Re-cut outcome to the two-layer winner def. 3. Join + audit CrUX coverage; drop no-field-data URLs for speed; report coverage. 4. Speed → pass-rate + three-zone, kill median-seconds. 5. Add controls to every model (page-type, word count, ranked-kw, traffic band, niche); any effect must survive or be demoted to leakage. 6. Flag adoption rate beside every null. 7. Bootstrap CIs for anything client-facing. 8. Reserve a backlinks-ready schema slot. 9. Stand up a split-test register on live client templates.

## 5. Our current findings: trust / distrust / re-test
**TRUST:** on-page mechanics are table-stakes not levers (holds across 11.8M+ pages); speed is hygiene+tiebreaker (Google's own position); prioritising mobile CWV was right.
**DISTRUST:** the 8.3-vs-6.2 "winners slower" data point (inadmissible — confounded); "title tags don't matter" (overstated — title *is* a small input, edits move clicks 4–15%); **"authority beats on-page" (WRONG — it inverts the only causal evidence we have: split-tests point at on-page; treat authority + on-page as complementary necessary conditions, not winner-vs-loser)**; page traffic as a "driver" (weakest claim).
**RE-TEST:** on-page table-stakes stratified (A1–A11); speed as pass-rate + three-zone (B1–B6); everything authority once backlinks land (C); causal questions via split tests (the only thing that proves *X moves rank*).

## 6. First position-bucketed read of our corpus (663 pages, 2026-06-08)
Re-cutting our data by **actual rank** (top-3 / page-1-rest / non-placer) instead of the crude top-10-vs-21-45 split immediately surfaced gradients the binary split flattened. Counts: top3 = 77 · rest 4–10 = 217 · low 21–45 = 369.

| Signal (median) | top-3 | 4–10 | 21–45 | Read |
|---|---|---|---|---|
| est. monthly traffic | **462** | 86 | 15 | steep climb to top-3 (authority proxy; circular) |
| ranked keywords | **45** | 19 | 10 | top-3 rank for ~4.5× more terms (breadth/authority) |
| internal links | **81** | 63 | 66 | top-3 notably higher |
| word count | **1504** | 1218 | 1213 | top-3 ~24% longer |
| outbound links | 7 | 6 | 5 | mild climb |
| keyword in title (%) | 62 | 54 | 54 | top-3 modestly higher |
| schema types | 9 | 9 | 9 | flat |
| has schema (%) | 82 | 78 | 78 | flat |
| keyword in H1 (%) | 38 | 38 | 35 | flat |
| **mobile LCP (ms)** | **11,896** | 6,934 | 6,179 | top-3 SLOWEST — page-weight confound (only 80 pages measured); ~0% meet <2.5s |

**Reads:** (1) The signals that actually climb toward the top-3 are **authority/breadth proxies** (traffic, ranked-keywords, internal links) + modestly word count + keyword-in-title — the schema/keyword-everywhere on-page stuff stays flat. (2) Top-3 being the *slowest* (LCP 11.9s) is the page-weight confound §2 predicted — heavier authoritative pages rank *and* load slower; speed isn't the lever. (3) This validates the two-layer winner definition: position buckets reveal what win/lose hid. Next: rebuild the grader to the top-3 binary + intent×niche×page-type segmentation, then run the §3 top-10.

---
*Provenance: research workflow wf_cb125687-904 (10 agents) + analyze_by_position.py on corpus.jsonl. Uncertainty: CTR figures pooled estimates (verify vs our GSC); speed bucket n=80 (small); on-page table-stakes high-confidence, exact CTR weights medium, kw-in-URL/H1 inferential.*
