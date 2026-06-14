---
type: seo-lab-demo
created: 2026-06-03
keywords: [digital marketing agency, google ads agency]
niche: marketing agencies
geo: US (demo — see limitations)
status: phase-0 proof
---

# Marketing Agency On-Page Teardown (Phase 0 demo)

First live run of the SEO learning loop, on-page signals only. Goal: prove we can systematically pull what top-ranking pages have in common, and surface candidate hypotheses. Niche chosen because Odin is itself an agency, so the findings feed our own SEO. Related: [[seo-anatomy-engine]].

## Method

- 2 keywords: `digital marketing agency`, `google ads agency`.
- 10 real ranking pages (agency sites, not directories) pulled from live search results.
- Scraper: `wiki/seo-lab/scrape_onpage.py` (requests + BeautifulSoup via `uv`). Raw data: `wiki/seo-lab/data/onpage_results.json`.
- This is the Phase 1 mechanism in miniature. Phase 1 swaps `requests` for Crawl4AI (browser rendering) and JSON for SQLite.

## The data (9 of 10 pages)

| Page | Title len | "agency" in title | exact kw in title | # H1 | kw in H1 | Words | Schema |
|---|---|---|---|---|---|---|---|
| coalition / digital-marketing | 52 | ✅ | ✅ | 1 | ✅ | 5,494 | ✅ 7 types |
| npdigital.com | 57 | ✅ | ✅ | 1 | ❌ | 1,196 | ✅ 5 |
| powerdigitalmarketing.com | 62 | ✅ | ✅ | 1 (`POWER`) | ❌ | 1,524 | ✅ 4 |
| level.agency | 43 | ✅ | ✅ | 1 (`GOOD ENOUGH ISN'T.`) | ❌ | 1,483 | ✅ 8 |
| adcetera / the-woodlands | 49 | ✅ | ✅ | 2 | ✅ | 2,697 | ❌ none |
| digitalmarketingagencyllc.com | 28 | ✅ | ✅ | 1 (`Search Engine Optimization`) | ❌ | 1,327 | ❌ none |
| sol8.com | 53 | ✅ | ✅ | 1 (`We Don't Run Ads.`) | ❌ | 1,452 | ✅ 8 |
| growmyads / google-ads-agency | 44 | ✅ | ✅ | 1 | ✅ | 3,247 | ✅ 4 |
| coalition / google-ads-mgmt | 52 | ✅ | near ("Google Ads Marketing Agency") | 1 | ❌ | 3,189 | ✅ 6 |
| thriveagency.com | — | — | — | — | — | — | blocked (HTTP 422) |

## Candidate hypotheses

Per the confidence model in [[seo-anatomy-engine]]: a pattern seen in **one niche** is a **Hunch (≤60%)** no matter how strong in-niche, until it's tested in other verticals. So everything here is a Hunch — strong signal, not yet proof. That discipline is the whole point.

1. **The keyword lives in the TITLE, not the H1.** (Headline finding, ~45%, Hunch)
   - `agency` is in the title on **9/9** pages; the near-exact keyword on **9/9**.
   - But the keyword is in the H1 on only **3/9**. Most winners use a **brand or benefit H1** instead: `POWER`, `GOOD ENOUGH ISN'T.`, `We Don't Run Ads. We Grow Businesses.`
   - This *contradicts* the common SEO advice "always put your exact keyword in the H1." Exactly the kind of "what they say vs what winners do" gap this project exists to find.
   - **Next test:** does title-yes / H1-brand hold for dentists, solar, plumbers? Is it causal, or just that strong brands rank for other reasons?

2. **Exactly one H1.** 8/9 (the lone exception, Adcetera, also has the messiest markup). ~55%, Hunch. High prior (matches HTML best practice).

3. **Title kept to SERP-display length.** 8/9 land in 43–62 characters (the ~50–60 range Google shows). One outlier at 28. ~50%, Hunch.

4. **Meta description always present.** 9/9. Length is *not* tightly controlled (86–337 chars; one well over the truncation limit). So presence looks like table-stakes, precise length less so. ~55%, Hunch.

5. **A standard schema stack, but it's not mandatory.** 7/9 ship JSON-LD; the common stack is Organization (7), WebSite (7), WebPage (7), BreadcrumbList (6), with LocalBusiness on 4. But **2 pages rank with no schema at all** — so it's correlational, not required, at this level. ~45%, Hunch.

6. **Page type drives length.** Dedicated service/landing pages run long (2,700–5,500 words); brand homepages sit ~1,200–1,500. ~40%, Hunch. Needs more data points.

7. **WordPress-heavy.** 5/9 are clearly WordPress (WP Rocket ×3, Elementor ×2). Weak signal (~35%) — likely says more about agency tooling habits than about ranking.

## Limitations (and what they teach us about Phase 1)

- **Geo:** these are US results (my demo search tool is US-only). Odin needs **Australian** SERPs — that's exactly what DataForSEO's location targeting buys us in Phase 1.
- **One page blocked us (thriveagency, HTTP 422).** Simple scrapers get refused by bot protection. Phase 1's Crawl4AI uses a real browser, which gets past most of this. Honest proof we need the better tool.
- **Correlation only.** Nine pages, one niche. None of this is causal yet. Causation needs the cross-niche tests (Phase 3) and live changes on a real site (Phase 5).
- **Head-term reality:** for `digital marketing agency` the actual top results are stuffed with **directories** (Clutch, Semrush, DesignRush). Strategic read for Odin: you rarely out-rank directories for the head term — the play is longer-tail + local + getting *listed in* those directories. (Observed from the search results, not the scrape.)

## What this proves

The loop works end to end on real data: pick keyword → get rankers → extract on-page facts → spot patterns → write confidence-scored hypotheses. Nothing here needed a paid tool or a local LLM. The next move is breadth (more niches, AU geo) and depth (the head-element + schema fields the simple scraper got, which Crawl4AI will get more reliably).
