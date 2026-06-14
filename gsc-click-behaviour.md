---
title: GSC click-behaviour read (COEC) — our own pages
type: spec
status: active
updated: 2026-06-09
---

# Click-behaviour read (COEC) on our own pages

**Why this exists:** the 2,659-page page-one audit ([[page-one-differentiators]]) proved that no on-page/content signal we can *scrape* sorts the top 3 once authority is controlled. The literature says the real sorter is **click satisfaction** (Google's NavBoost re-ranker), which we cannot see on competitors. But on **our own** client pages, Search Console gives actual CTR + position, so we *can* measure it.

**The metric — COEC (clicks over expected clicks):**
- `expected CTR` = the average organic CTR for a result at that position.
- `COEC = actual CTR / expected CTR`. Below 1 = the page earns fewer clicks than its slot deserves (a title/snippet opportunity, and the kind of page NavBoost tends to *demote*). Above 1 = it out-clicks its slot (what NavBoost rewards).
- `click_gap = impressions × (expected − actual CTR)` = clicks left on the table.

**Tool:** `wiki/seo-lab/gsc_coec.py`. Pull GSC via Make tool `s4675016` (dimension page or query), then `uv run gsc_coec.py <export.json> [brand_token]`. Brand token excludes brand searches (they over-click regardless of slot).

> **Hard caveat:** the expected-CTR curve is generic desktop organic. **Local-service SERPs (plumbers, dentists) carry a Google MAP PACK + ads above the organic results**, which eat most of the clicks. So absolute organic CTR sits far below the curve for these queries. Treat COEC as a **relative** ranking of opportunities, and always check whether a map pack is present before blaming the title.

---

## First read — Hobson Bay Plumbing (90 days to 2026-06-06)

Across 31 non-brand queries ranking organic positions 2-20, the **median COEC is ~0.0** — Hobson Bay ranks page-one organically on its money queries but earns almost **zero** clicks:

| Query | Org. pos | Impressions | Actual CTR | Expected | COEC |
|---|---|---|---|---|---|
| plumber williamstown | 5.2 | 1,321 | 0.5% | 5.3% | 0.09 |
| plumber altona | 6.4 | 1,425 | 0.4% | 4.1% | 0.10 |
| plumber footscray | 8.3 | 1,702 | 0.5% | 2.9% | 0.16 |
| hot water service altona | 2.9 | 118 | 0.0% | 10.6% | 0.00 |
| emergency plumber williamstown | 14.0 | 640 | 0.0% | 1.4% | 0.00 |

**Interpretation (a lead, not proof):** this is the signature of the **local map pack**. For "plumber [suburb]" queries Google shows ads + a 3-business map pack above the organic list, so a "position 5" organic result is physically far down the page and barely clicked. The implication is strategic: **for this client, climbing organic rank on local-service queries is a weak lever; the clicks live in the map pack (Google Business Profile).** A title/snippet rewrite recovers a little, but the bulk is structural.

**The one bright spot:** `plumber near me` at organic position 12.5 pulls a 5.5% CTR (COEC 3.24) — it out-clicks its slot by 3x, worth understanding and replicating.

**How this ties back to the audit:** it reinforces the page-one finding. For local-service queries the click game (NavBoost's input) is decided by the map pack, not the organic snippet, which is exactly why on-page title/content tweaks showed no within-page-1 leverage. The levers that remain: authority, internal linking (the one confirmed on-page lead), and the GBP/map pack.

**To confirm before acting:** look at a live SERP for "plumber williamstown" (is the map pack present? where does Hobson Bay's organic result actually sit?). Single 90-day snapshot; generic CTR curve.

**Next properties to run:** any client with GSC shared to `jake@veritasdigital.com.au` — currently Hobson Bay (live), Swan Windows (property needs updating to the new domain), Redgate Farmstay (pending re-verification). Repoint by changing the `siteUrl`.
