---
title: SEO Lab — findings log (how the answers evolve)
type: log
status: active
updated: 2026-06-22
---

# Findings log

A dated record of what each audit concluded, newest first. The point of this file: as the corpus densifies over months, you can see how each signal's verdict *moves* (promoted, demoted, confirmed, killed) rather than only seeing the latest snapshot. Append a block per audit; never overwrite.

**Convention:** each entry = date, corpus size, method, and a one-line verdict per signal. The live "current best answer" lives in [[insights]]; this is the history behind it.

---

## Signal verdicts over time (at a glance)

| Signal | 663 pages (2026-06-08) | 2,659+ pages (2026-06-09) | 23,626 pages (2026-06-12) |
|---|---|---|---|
| Internal links to the page | confound (plumbing-only) | ✅ **confirmed lead** (survives joint control, p=0.019) | ✅ holds, conditional on authority (mid +14, high +23, low reversed) |
| Topical breadth (ranks for a related cluster) | not yet tested | ✅ **strong lead** (survives authority control: +34 in clean band) | ✅ holds (mid-band +15; cluster ownership 43% top3 vs 32% rest of p1 vs 3% low) |
| Schema variety (type count) | candidate pattern (+50-60%) | not re-tested | ❌ **killed** — dead flat at scale (7.0 vs 7.0 vs 7.0) |
| Query in lead paragraph | not tracked | not tracked | 👀 new hunch — clean raw gradient 63/53/47%, not yet authority-controlled |
| Title 40-60 chars | promising | demoted → weak/underpowered | 👀 keeps showing in controlled bands (mid +11pt, low +14pt) — watch |
| Query front-loaded in title | promising | ❌ washed out (small-sample noise) | ❌ stays washed out (raw +5pt, high band reversed) |
| Exact query in title | confound | ❌ confound (homepage/brand-title artefact) | ❌ stays confound (top3 are 48% homepages vs 34% low) |
| Word count / depth | confound | ❌ confound (authority + page type) | ❌ stays confound (raw gap +49 words on 23.6k pages — nothing) |
| Freshness (page age) | confound | ❌ confirmed null | ❌ null overall; thin mid-band/trades hint (-67d) — not promoted |
| Core Web Vitals / speed | gate not lever | gate not lever (settled) | ❌ not even a gate here: top3 median LCP 7.3s, 97% of top3 fail "good" and rank anyway |
| Authority within page 1 | flat (ticket, not sorter) | flat | 👀 revision candidate: top3 247 vs 4-10 174.5 refdomains — but only 6% coverage, recheck when enrichment compounds |

---

## 2026-06-22 — Weekly self-audit: corpus flat, no verdict change, pipeline looks stalled

**Method:** scheduled weekly re-grade. `rulebook.py` + `analyze_controlled.py` + `analyze_movement.py` over the coalesced corpus (`data/corpus.jsonl` + `data/corpus/` shards, deduped by url+keyword).

- **Corpus flat at 25,503 graded pages** (top3 4,137 / 4-10 10,173). Authority-controlled mid band unchanged at **337 top-3 / 1,045 challengers** — n grew by 0 this week. `rulebook.md` regenerated **byte-identical**, and the movement grade is byte-identical too (34,476 pairs / 22,501 seen on 2+ days). No new data has landed since the last pipeline commit on 2026-06-16 — the 8-hourly scrape workflow on the public repo looks stalled (worth a check of GitHub Actions).
- **No verdict flipped, no new WATCH candidate.** Audit-verified leads hold: **internal links to the page** and **topical breadth**. Significant-but-not-yet-audited leads also hold (author/byline mid +16pt at n=337, freshness date mid +11pt, query in lead paragraph). Watch list unchanged: contextual in-content internal links (n=17), FAQ schema (flat), title 40-60 chars.
- **No promotion-ready candidate.** None of the three WATCH factors clears the bar (mid-band top-3 n≥120 with a consistent same-direction gap): title 40-60 is the only one at n≥120 (337) but its mid-band gap reversed to -1pt this snapshot (raw +6pt) so direction is inconsistent; FAQ schema is dead flat (+1pt); contextual internal links is still tiny (n=17). Promotion stays blocked on data throughput, not analysis.
- **Rank movement (unchanged):** 56% of 22,501 tracked pairs moved ≥1 position; top-3 sticky at 87% (3,691/4,221); 448 pairs broke into the top 3; biggest single-day rise +24 (Brisbane root-canal page r28→r4), biggest fall -23; all niches median |move| = 1.
- **Binding constraint this week is pipeline uptime, not authority coverage.** The mid-authority band can't densify (still n≈337) while no new SERP runs are committing. Action for Jake: check why the scrape Action stopped after 2026-06-16.

---

## 2026-06-12 — Full-corpus grade at 23,626 pages; schema variety killed; first movement baseline

**Method:** first whole-corpus grade since the burst (the pipeline was down 2026-06-09→12 — Actions quota exhaustion, see [[log/2026-06-12]]). `grade.py` + `analyze_by_position.py` + `analyze_controlled.py` + `analyze_breadth.py` + new `analyze_movement.py` over 23,626 coalesced pages (4,104 winners / 9,832 challengers / 9,690 non-placers, 10 niches).

- **Bottom line vs non-placers is authority, full stop.** The only signals clearing the grader's bar winners-vs-non-placers: referring domains (247 vs 158), Authority Score (16.5 vs 12), total backlinks (1,113 vs 775). Every on-page signal sits below the gap threshold at this scale.
- **Schema variety KILLED.** The 2026-06-08 candidate pattern (winners use more schema types, +50-60%) is dead flat at 23.6k: median 7.0 schema types in every rank bucket. Textbook small-sample pattern that more data erased — same fate as the title leads.
- **Breadth + internal links both hold** (see table) — still the only two on-page leads that survive authority control.
- **New raw gradient worth chasing: query in the lead paragraph** (63% top3 / 53% rest-of-p1 / 47% low). Not yet controlled; added to the watch list ahead of promotion. Title 40-60 chars also keeps reappearing in the controlled bands (+11pt mid) after being demoted at 2,659 — underpowered there (n≈220/band), so still "watch".
- **Speed downgraded from "gate" to "not even a gate" for AU local SERPs:** top-3 pages are *slower* than non-placers (median LCP 7,252ms vs 6,557ms); 0% of any bucket passes CWV all-good; 97% of top-3 fail Google's "good" LCP and rank anyway.
- **Freshness stays null overall** (raw 179 vs 180 days) with one honest wrinkle: in the equal-authority mid band top3 are 67 days fresher, and the niche split is directional (fresher wins in plumbing/window-cleaning/solar, reversed in roofing/HVAC/online-therapy; QDF-ish queries -10d vs evergreen +1d). Too thin to promote; flagged for the H6 query-type interaction once authority coverage grows.
- **Authority-within-page-1 revision candidate:** at 860 pages refdomains looked flat top3-vs-4-10 ("ticket, not sorter"); at 23.6k the medians split 247 vs 174.5. Coverage is only 6% of rows (Semrush drain), so this is a recheck-not-revision until enrichment compounds.
- **First longitudinal baseline (new `analyze_movement.py`, 1,462 pairs seen on 2+ days):** day-over-day, 50% of page-keyword pairs moved ≥1 position; top-3 is sticky (90% of top-3 starters still top-3 at last look); 33 pairs broke into the top 3 in a day; plumbing/window-cleaning are the most volatile niches (median |move| 1.0). This is the dataset that eventually turns correlations into before/after causal reads.
- **Constraint identified: authority coverage (6%) is the binding constraint on every controlled read** (tertile cells run at n≈53-160). Pipeline now enriches rank-only observations from the domain cache too, so coverage compounds run-over-run instead of only touching newly-rendered pages.

## 2026-06-09 (burst) — Scaled to 23,626 pages; breadth reconfirmed; Semrush drained

**Method:** front-loaded "burst" of 24 concurrent cloud runs over a 1,726-keyword pool (30 cities, 10 trades), spending ~$14 of DataForSEO. Re-ran the authority-controlled read.

- **Breadth (ranked keywords) reconfirmed at scale.** Top-3 vs 4-10 in the equal-authority band: +15 (41 vs 26), and the direction holds in all three authority bands (+25 low, +15 mid, +16 high). Most robust, most consistent lead we have (now confirmed at 663, 2,939 and 23,626 pages).
- **Internal links:** holds at mid (+14) and high (+23) authority, reverses at low. Real but conditional.
- **Two pipeline lessons banked (see auto-memory `reference_pipeline_concurrency_data_integrity`):** (1) the 24 concurrent runs drained Semrush API units to 0, so only 3% of pages got authority data, the controlled audit got *weaker* not stronger. The real bottleneck for learning is authority-enrichment throughput, not DataForSEO spend or raw page count. (2) The latest-row-wins dedupe let authority-less re-scans overwrite earlier authority; switched all graders to a coalescing loader (`corpus_load.py`), recovering coverage 3%→6% for free.
- **Open decision:** authority enrichment is blocked until Semrush units reset or are topped up. Future bursts must throttle Semrush.

## 2026-06-09 — Breadth, authority-controlled (corpus ~2,900)

**Method:** tertile-stratified read (`analyze_controlled.py`) of ranked-keyword count (how many keywords each URL ranks for on Google) by rank bucket.

- **Topical breadth survives authority control.** Top-3 vs 4-10: raw +22 keywords; in the equal-authority (mid) band it *widens* to **+34** (73 vs 39). Word count and freshness collapsed under the same control; breadth strengthened. → Promoted to a real, backlink-independent lead, alongside internal links.
- Residual caveat: partly circular (a strong page ranks for more by being strong). Earns "rule" only after a live test. Also added the cluster test bed to the keyword pool so the fine-grained version becomes measurable.

## 2026-06-09 — Re-audit at 2,659 pages (6 adversarial skeptics)

**Method:** 4x the data of the prior audit; six independent skeptics each tried to refute one signal; significance computed (z / chi-square / Mann-Whitney) inside an authority-controlled band.

- **0 of the title/content leads survived; 1 confirmed (internal links).** The two title leads that looked good at 663 pages shrank toward zero with more data (regression to the mean), proving they were small-sample noise.
- **Internal links** promoted to the one confirmed on-page lead (raw +19 median, p=1.6e-5; survives joint control for authority + homepage nav, p=0.019; replicates in plumbing & electrician).
- **Killed as confounds:** exact-query-in-title (homepage artefact), word count (authority), freshness (confirmed null).
- Lesson banked: more data kills weak findings; real effects sharpen instead. Validated the decision to widen the corpus.

## 2026-06-08 — First audit at 663 pages (6 adversarial skeptics)

**Method:** authority-tertile-stratified read; six skeptics; first attempt at significance on small per-cell n (~13-31 top-3 pages).

- **0 of 6 confirmed as rules.** Two title signals (front-loaded query, 40-60 char length) looked promising (+16-17pt in the clean band) but were underpowered (just under significance).
- Three signals flagged as authority/niche confounds (query-in-title, word count, freshness).
- Headline established: within page one, authority is flat, so the sorter is a signal class we weren't yet capturing → built the within-page-1 signal set ([[page-one-differentiators]]).
