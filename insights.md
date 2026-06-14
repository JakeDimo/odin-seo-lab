---
title: SEO Lab — what we know so far (living digest)
type: spec
status: active
updated: 2026-06-12
---

# SEO Lab — what we know so far

One-page digest of everything the lab has established. Scope: **Australian local-service SERPs** (plumbing, window cleaning, dental, electrician, HVAC, roofing, pest control, locksmith + national online-therapy & solar). Detail lives in [[page-one-differentiators]], [[gsc-click-behaviour]], [[methodology]]. Everything here is correlational until a controlled live test, per the findings-are-not-rules rule.

**Corpus:** 23,626 pages; 1,726 keywords / 10 verticals (incl. a related-keyword cluster test bed); audited by six independent skeptics; pipeline fully autonomous (8-hourly incremental runs — full keyword pool gets a rank observation daily, pages re-render fortnightly). History of how findings evolved: [[findings-log]].

---

## 1. What holds up (the two real leads)

**Internal links to a page is one of two signals that still track top-3 ranking after you control for authority and page type.** Confirmed at 2,659 pages: raw +19 median links (p=0.000016), and it survives a joint model controlling for backlinks and homepage nav (p=0.019). The clincher: homepages crowd the top 3 but carry *fewer* internal links, so they drag the gap *down*, yet it still holds, inside service (+27), product (+48) and home (+16) pages. Replicates independently in plumbing (+31, p=0.003) and electrician (+32, p=0.003).

> Plain English: of all the on-page things people obsess over, the one that genuinely correlates with winning page one is how well a page is linked *from the rest of its own site*. And unlike backlinks, that's something we fully control.

**Topical breadth — owning a related-keyword cluster.** The second signal that survives authority control: top-3 pages rank for roughly twice as many related keywords as the rest of page one (73 vs 39 in the equal-authority band), and the gap *widens* when authority is held flat (the opposite of word count and freshness, which collapsed).
> Plain English: a page that ranks for "plumber sydney" also tends to rank for "best plumber sydney", "local plumber sydney", "24 hour plumber sydney" and so on. Owning the related cluster tracks the top spots, independent of backlinks. Still partly chicken-and-egg (a strong page ranks for more by being strong), so a strong lead, not yet a rule.

## 2. What we DEBUNKED (SEO folklore that did not survive)

| Belief | Verdict | Why it failed |
|---|---|---|
| Keyword in the title ranks you | ❌ confound | A homepage artefact ("Service City \| Brand" titles auto-contain the query). On real content pages +2.4pt, not significant. |
| Longer / deeper content ranks | ❌ confound | Long pages just have more backlinks. Match authority + page type and it washes out (+106 words, p=0.76). |
| Fresher content ranks | ❌ confirmed null | "111 days fresher" was a median mirage. Real effect a coin-flip (0.53). No query-deserves-freshness pattern. |
| Keyword front-loaded in title | ❌ noise | Looked like +17.6pt at 663 pages, collapsed to +5.4pt and failed at 2,659. Classic small-sample regression. |
| Title length 40-60 chars | ~ weak maybe | Borderline (pooled p≈0.049), contradicted by a flat continuous test — but keeps reappearing in equal-authority bands at 23.6k (+11pt). Cheap to trial, not a rule. |
| Schema variety (more types = better) | ❌ killed at scale | +50-60% at 663 pages → dead flat at 23,626 (median 7.0 types in every rank bucket). Small-sample pattern, erased by data. |
| Page speed / Core Web Vitals | ❌ not even a gate here | At 23.6k pages top-3 are *slower* than non-placers (median LCP 7.3s vs 6.6s); 97% of top-3 fail Google's "good" and rank anyway. Stop investing here for AU local. |

## 3. The structural finding (from our own Search Console)

**For local-service queries, ranking organically is NOT the same as getting clicks, because the Google map pack eats them.** Hobson Bay Plumbing ranks organic positions 3-8 on its money searches ("plumber williamstown" etc.) but earns a ~0.5% click rate against an expected 3-5%, a click-over-expected score of basically zero across 31 non-brand searches.

> Plain English: for a local trades business, pushing up the blue organic links barely moves the phone, because the map (with the 3 businesses + stars) sits above them. **The growth lever for these clients is the Google Business Profile / map pack, not organic SEO.** Bright spot: "plumber near me" out-clicks its slot 3x, worth understanding.

## 4. The meta-learnings (how ranking actually works here)

- **Authority gets you ONTO page one; something else sorts within it.** Backlinks/referring domains looked flat across the top 10 at 860 pages (216 vs 188). *Under review at 23.6k:* the medians now split top3 247 vs 4-10 174.5 — but authority coverage is only 6% of rows, so this re-tests as enrichment compounds. If it holds, authority is both ticket AND part of the sorter.
- **The within-page sorter is click behaviour** (Google's NavBoost), which we cannot see on competitors, only on our own pages via Search Console, and for local queries it is dominated by the map pack.
- **Authority and page type are the master confounds.** Almost every "lead" we found was really one of those two in disguise. Always control for them.
- **More data kills weak findings.** Two title "leads" looked strong at 663 pages and evaporated at 2,659; schema variety looked strong at 663 and died at 23,626. Small samples invent patterns; that's why we widened the pool.
- **Rankings are sticky at the top, churny below.** First longitudinal read (1,462 page-keyword pairs tracked across days): 90% of top-3 holders are still top-3 the next day, while half of all pairs move at least one position. Breaking in is the hard part; staying in is not. Plumbing and window-cleaning churn most.
- **The top 3 skew heavily to homepages** (48% of top-3 vs 34% of non-placers). For local-service queries Google resolves to the *business*, not the page — consistent with the map-pack/GBP finding below.

## 5. Open hypotheses (ranked by evidence, still to test)

| # | Hypothesis | Status |
|---|---|---|
| H1 | Click satisfaction (out-click your slot, NavBoost promotes you) | Strongest. Now partly measurable via our GSC. For local = map-pack dominated. |
| H2 | Brand demand (branded searches, brand mentions) | Strong in the literature, untested by us (needs brand-search data). |
| H3 | Semantic relevance / intent-format match | Keyword-in-title proxy debunked; true semantic match (embeddings) untested. |
| H4 | Content comprehensiveness vs the SERP | Word-count proxy debunked; real subtopic coverage untested. |
| H5 | Information gain / originality | Untested (hard, needs an embeddings build). |
| H6 | Freshness only on "needs-fresh" queries | Universal freshness debunked; the query-type interaction untested (data too thin). |
| H7 | Link QUALITY gradient (anchor relevance, referring-domain DR) | Untested. |
| H8 | Core Web Vitals as a gate | Settled, downgraded further at 23.6k: not even a gate on AU local SERPs. Done. |
| H9 | Query in the lead paragraph | New (2026-06-12): clean raw gradient 63/53/47% across rank buckets; awaiting authority-controlled read. |
| H10 | In-content links (not nav boilerplate) are what carries the internal-link lead | New (2026-06-12): now measured per page (`main_internal_links` vs `nav_link_count`); data accrues as pages re-render. |
| H11 | Local trust markers (licensed/insured/service-area/map embed) | New (2026-06-12): now measured; first read when re-render coverage arrives. |

## 6. Shortlist for a controlled live test (when we choose to)

1. **Internal links to a stuck mid-pack page** — confirmed correlation, highest-confidence bet.
2. **Build topical breadth around a target** — add closely-related cluster pages/sections so the page owns the whole related set, not one term. Survives authority control.
3. **Title length into the 40-60 char band** — cheap to trial; plumbing showed the cleanest hint.
4. **For local clients: the Google Business Profile / map pack** — where the clicks actually are.

## 7. Caveats

These findings are specific to **AU local-service SERPs** and are **correlational snapshots**, authority-controlled but not proof. A correlation earns the word "rule" only after a single-variable live change moves the ranking. The four newest verticals (HVAC, roofing, pest control, locksmith) only just entered the corpus and will sharpen the per-niche reads over the coming days.
