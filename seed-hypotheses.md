---
type: seo-reference
title: Seed Hypotheses — practitioner theories to test
created: 2026-06-03
updated: 2026-06-03
status: living document
---

# Seed Hypotheses (what working SEOs believe — for us to test)

Harvested 2026-06-03 from r/SEO + r/bigseo, the **May 2024 Google API leak**, the single-variable testers (Kyle Roof, Matt Diggity), 2026 local-SEO studies, correlation studies (Backlinko/Ahrefs/Semrush), and the GEO/AI-search shift. These are **starting points to falsify, not facts.** Each starts at **Hunch** and only graduates through the gates in [[signal-checklist]] → confidence model in [[seo-anatomy-engine]].

Tags: 🟢 white hat · 🟡 grey hat · 🔴 black hat (detect, don't emulate) · ⭐ counter-intuitive (highest learning value).

## On-page & content

1. 🟢⭐ **Keyword belongs in the TITLE, not necessarily the H1.** Our own demo: 9/9 had it in title, 3/9 in H1. *Test:* winners-vs-losers, kw-in-title and kw-in-H1, scoped by query type. *Source: our teardown + Kyle Roof (title is a confirmed zone).*
2. 🟢 **Keyword placement matters in 5 zones: URL, title, H1, body, image ALT.** *Test:* presence in each zone, winners vs losers. *Source: Kyle Roof, 400+ single-variable tests.*
3. 🟢⭐ **"Google can't read" — grammar, spelling, and reading level are NOT ranking factors.** Contradicts common advice. *Test:* readability grade of winners vs losers; expect little/no gap. *Source: Kyle Roof.*
4. 🟢⭐ **"Google can't see" — visual design / UX quality does NOT directly drive ranking** (it drives conversion). *Test:* UI/UX rubric score vs rank; expect weak correlation. Tension with Google's "page experience." *Source: Kyle Roof.*
5. 🟢 **Content comprehensiveness / topical coverage correlates with rank** (the ~30% mimicry tools chase). *Test:* entity coverage vs top corpus, winners vs losers. *Source: Backlinko/Clearscope.*
6. 🟢⭐ **Information gain (original info not already in the SERP) helps.** *Test:* AI-score uniqueness of facts; winners vs losers. *Source: Google information-gain patent + 2026 entity-SEO talks.*

## Engagement & clicks (NavBoost — leak-confirmed)

7. 🟢⭐ **Higher real CTR + longer dwell ("last longest click") lifts rank.** *Test:* GSC CTR & GA4 dwell vs position **on our own client sites**. *Source: Google API leak (goodClicks/badClicks/lastLongestClicks).*
8. 🟡 **Snippet engineering (numbers, brackets, "#1/free/best") raises CTR and so, indirectly, rank.** *Test:* snippet features vs CTR (own sites). *Source: leak + practitioner consensus.*
9. 🔴 **CTR manipulation (click bots) can move rank short-term by gaming NavBoost.** *Detect, never use.* Explains some volatile competitor wins. *Source: black-hat guides.*

## Authority & links

10. 🟢 **The #1 result has ~3.8× more backlinks than #2–10; referring-domain count tracks traffic.** *Test:* once DataForSEO/Ahrefs is wired in. *Source: Backlinko 11.8M-result study.*
11. 🟢 **Topical authority is per-cluster, not per-domain: deep coverage of one topic beats a stronger domain with shallow coverage.** *Test:* site-level same-topic page count + intra-cluster links vs rank. *Source: Feb 2026 Google update analyses.*
12. 🔴 **PBNs still work but are footprint-detectable (shared host/registrant/template, thin AI content).** *Detect* to explain anomalies. *Source: black-hat guides.*

## Local (Swan Windows, Creative Coast, Hobson Bay)

13. 🟢⭐ **GBP primary category is the single biggest local-pack lever** (bigger than anything on the website). *Test:* category vs map-pack position across local competitors. *Source: 2026 local-SEO weighting (~32% GBP).*
14. 🟢⭐ **Review recency + velocity beats total review count** (80 reviews with weekly flow > 200 stale). *Test:* review recency vs map-pack rank. *Source: 2026 local studies.*
15. 🟢 **NAP consistency across GBP / site / directories; keywords in review text; monthly fresh photos all lift local rank.** *Test:* per signal, local competitors. *Source: 2026 local studies.*
16. 🔴 **Fake `aggregateRating` schema injection boosts CTR.** *Detect* (schema rating vs visible reviews mismatch). *Source: black-hat case studies (~30% CTR lift claimed).*

## Brand & entity

17. 🟢 **Brand search volume correlates with rank AND with AI-citation probability (~0.33).** *Test:* brand volume vs rank/citations. *Source: 2026 entity-SEO data.*
18. 🟢 **Entity confirmation via schema + `sameAs` (LinkedIn/Wikidata) accelerates Knowledge Graph recognition.** *Test:* sameAs presence vs entity/rank signals. *Source: entity-SEO guides.*

## AI / generative search (GEO)

19. 🟢⭐ **AI citation is a separate game from ranking: 80% of LLM citations aren't in Google's top-100.** *Test:* track AIO/ChatGPT/Perplexity citations independently of rank. *Source: 2026 GEO studies.*
20. 🟢 **Extractable facts / semantic triplets + answer-first intros win citations (44% come from the first 30% of a page).** *Test:* fact density + intro structure vs citation. *Source: GEO studies.*

## Page experience / speed

21. 🟢⭐ **Page speed has weak-to-no correlation with first-page rank** (despite the hype), though Core Web Vitals act as a tiebreaker. *Test:* CWV vs position; expect a weak effect. *Source: Backlinko (no speed↔rank correlation) vs Google page-experience.*

## Channel / surface

22. 🟡 **Reddit/UGC now occupies 3–5 page-1 slots for many queries** — ranking *on* Reddit can beat ranking your own page. *Test:* count UGC/Reddit results per query in our niches. *Source: r/SEO 2026.*

---

**How these feed the loop:** each becomes a row in the learnings store with a scope (query × page-type × vertical × geo), a hat tag, and a confidence that only rises when winners-vs-losers data clears the gates. The ⭐ counter-intuitive ones are the priority — if we can confirm or kill "speed doesn't matter," "grammar doesn't matter," "category beats your website," that's real proprietary knowledge, not received wisdom.

---

## Mining round — community + video (added 2026-06-03)

**Honesty on sources:** direct scraping of Reddit and YouTube transcripts was **blocked in this environment** (Reddit refuses the fetcher; the transcript service returned HTTP 403). So these are mined from **search-surfaced** community threads, practitioner blogs, and video summaries, not raw thread/transcript text. For true raw-thread mining we'd need an authenticated Reddit API (via an MCP) or a transcript API. The Kyle Roof / Matt Diggity video findings are already captured as #2–#4 above; Diggity's rigour rule (10 control + 10 test pages minimum, 50 better) independently validates our ≥30-per-cell gate.

23. 🟡⭐ **Templated location pages now get penalised; only genuinely unique ones survive.** City × service pages where the variable text is 80%+ of the page took **−40% to −90%** in the March + May 2026 core updates. Survivors have ≥60% unique per-page content from 3+ sources. *Guardrail — directly relevant to Creative Coast / Hobson Bay service-area pages: scaled local pages help only if each is genuinely unique.* *Source: 2026 programmatic-SEO post-mortems.*
24. 🟢 **Per-service-area landing pages with real, area-specific content lift local rank** (vs one generic "services" page). *Test:* presence + uniqueness of area pages vs local rank. *Source: 2026 local-SEO guides.*
25. 🟢 **Directory citations (Yelp, Angi, Thumbtack, local directories) rank and feed local prominence** — being listed + NAP-consistent is part of the local play, not just your own site. *Test:* citation count/consistency vs local rank. *Source: 2026 local-SEO guides.*

---

## First pooled evidence (2026-06-04 — AU, 175 pages)

First gated run ([[2026-06-04-batch|grade]]); plumbing cleared the ≥30/side gate (57 win / 63 lose). Early reads:

- **On-page signals do NOT separate winners from losers.** In plumbing, keyword-in-title (61% vs 65%), keyword-in-H1 (46% vs 54%), has-schema (81% vs 92%), aggregateRating (39% vs 40%) and word count came out **flat or slightly losers-favoured**. So #1–#6 (on-page keyword/schema tactics) read as **table-stakes, not ranking levers** — the first data *against* treating them as differentiators. Confidence that they move rank on their own: **down**.
- **What did separate winners:** internal-link depth (**+23%**, cleared the gate) and domain-level traffic/authority (winners on **~6× higher-traffic** domains). Points at **off-page authority + site architecture** as the real drivers — the project's founding thesis, now with AU evidence.
- **Caveats:** traffic is domain-level (confounded — a giant general domain ranking 21–45 inflates the loser median, e.g. a 205M-visit outlier in online-therapy); backlinks (the decisive signal) failed to populate (Backlinks API access/parse — hardened to self-diagnose next run); only plumbing cleared the gate.

## Second pooled evidence (2026-06-08 — AU, 239 pages, page-traffic de-confounded)

Wider run (19 keywords; **plumbing 49/54 and window-cleaning 30/44 both cleared the ≥30 gate**; therapy 24/38 just under). Traffic now page-level.

- **CONFIRMED null result: on-page keyword/schema-presence does NOT separate winners.** kw-in-title, kw-in-H1, has-schema, aggregateRating, LocalBusiness all flat in plumbing AND window-cleaning (and overall). Two runs, three niches → solid, not a Hunch: these are **table-stakes, not levers**. Hypotheses #1–#6 (on-page keyword/schema tactics) confidence as *differentiators*: **low**.
- **First cross-niche candidate Pattern — winners use more schema *variety*.** schema-type-count **+50% (plumbing)** and **+60% (window-cleaning)**, consistent across both gated niches. Not "has schema" (flat) but the *number of distinct types* (Organization, WebSite, BreadcrumbList, FAQ, Service…). Winners layer richer structured data. Re-test next run to confirm.
- **Page-level traffic: winners ≈28× losers** (plumbing 178.7 vs 6.3 etv). De-confounded but still partly circular (rank→traffic) — read as "winning pages are established/authoritative," pending backlinks.
- **Watch, don't act:** image-alt coverage came out *lower* on winners (−22% overall, −30% window) — likely a directory confound.
- **Backlinks: confirmed gated** — DataForSEO `40204 Access denied` (needs the $100/mo Backlinks subscription). Plan: route via Make.com to avoid the floor (~$2–5/mo). Until then the decisive authority signal is unmeasured.
- **Fixes applied:** traffic only covered the first 120 URLs last run (enrichment cap) → cap raised so all niches get traffic next run; grade header now reports traffic-vs-backlinks status accurately.

## More free signals tested (2026-06-08b — same 239 pages, no re-scrape)

Added by re-reading stored data (capture-once paying off — new questions, zero cost). New reads:

- ⭐ **Keyword in the URL does NOT help — and inversely correlates in plumbing** (winners 18% vs losers 48%, gate cleared). Contradicts the "keyword in the URL slug is a ranking zone" advice (Kyle Roof #2). Likely a small-business tell: keyword-stuffed slugs mark the *losing* cohort, while winners use clean/brand URLs or are directories. Hypothesis #2 (URL as a keyword zone): **evidence against** as a differentiator.
- **Readability doesn't matter** — Flesch ≈47 for winners and losers across all niches. Confirms Kyle Roof #3 ("reading level not a ranking factor"). Null confirmed.
- **Schema *variety* is the lever, not any single type.** schema-type-count ✅ in both gated niches (+50% plumbing, +60% window-cleaning), but no individual type (Breadcrumb, Organization, WebSite, Service, FAQ…) cleared the gate on its own. So it's *layering several*, not one magic type.
- **Outbound links: niche-dependent, not a clean Pattern.** ✅ plumbing (7 vs 3) but ❌ window-cleaning (1.5 vs 3.5). Don't generalise.
- **AU (.au) domain, image-alt:** .au ≈90% both (no difference — everyone's local). Image-alt still inversely correlates (winners lower) — persistent, likely a directory confound; watch, don't act.
- **Queued:** "keywords this page ranks for" (free Labs `count`) now captured by enrich for the next run; Core Web Vitals (PageSpeed, free key) is the next external add to test the "speed barely matters" hypothesis (#21).
