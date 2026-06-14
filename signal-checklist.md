---
type: seo-reference
title: SEO Signal Checklist — master scrape catalogue
created: 2026-06-03
updated: 2026-06-03
status: living document
---

# SEO Signal Checklist (master scrape catalogue)

Every data point worth capturing from a ranking page, in one place, so we **scrape wide once and never re-scrape to answer a new question.** Supports [[seo-anatomy-engine]]; raw method demoed in [[2026-06-03-marketing-agency-teardown]].

## Design principle: capture once, derive forever

For every page we touch we store three things permanently:
1. **The raw HTML snapshot** (the whole page source).
2. **A screenshot** (desktop + mobile).
3. **The parsed fields** below.

Because we keep the raw HTML and screenshot, any signal we think of later is extracted by **re-reading stored data, not re-fetching the live web.** New idea next month = re-parse, not re-crawl. This is the answer to "we don't want to scrape pages over and over."

## The observability boundary (be honest about what's knowable)

Not everything Jake listed is knowable for a *competitor's* page. Three tiers:

| Tier | What | Available for |
|---|---|---|
| **A — Directly observable** | Content, markup, technical, performance, UI/UX structure | **Any** page on the web |
| **B — Estimable via paid API** | Rankings, keywords-per-page, traffic, backlinks | Any page, as a paid *estimate* (Semrush / DataForSEO / Ahrefs) |
| **C — Private analytics** | True traffic, **conversions**, bounce, dwell, GSC query data | **Only our own / client sites** |

So competitor **conversions are not directly knowable** (Tier C). What we *can* do is capture the conversion-*design* signals (CTA count, form length, click-to-call, trust proof) as a **predictor** of how well a page is built to convert, and measure real conversions only on sites where we own the analytics. Flagged below as such.

**Source legend:** `[Scrape]` free from raw HTML/screenshot · `[PSI]` free Google PageSpeed/CrUX API (rate-limited) · `[Paid]` Semrush/DataForSEO/Ahrefs · `[AI]` AI-scored from content or screenshot · `[Own]` our analytics only (GA4/GSC).

---

## A. Content signals `[Scrape]` / `[AI]`

| Signal | Why it matters | Source |
|---|---|---|
| Title tag — text, length (chars + pixels), keyword present + position | Strongest single on-page tag | Scrape |
| Meta description — text, length, keyword present, CTA present | CTR driver (indirect) | Scrape |
| H1 — text, count, keyword present, **brand vs benefit vs exact-match** | The demo's headline question | Scrape |
| H2–H6 — counts + full outline, keyword usage in subheads | Topical structure | Scrape |
| Body word count (unique vs boilerplate) | Depth proxy | Scrape |
| Target-keyword frequency + density + variant/synonym usage | On-page relevance | Scrape |
| **Keywords the page is *targeting*** (inferred from title/H1/headings/repetition) | Breadth of on-page intent | Scrape / AI |
| Entity & topic coverage vs the top corpus (what concepts are covered) | Topical comprehensiveness (the ~30% that mimicry tools chase) | AI |
| Readability grade (Flesch-Kincaid) | Audience match | Scrape |
| Content freshness — published + modified dates | Freshness signal | Scrape |
| FAQ block present (+ FAQ schema) | SERP feature eligibility | Scrape |
| Images — count, alt-text coverage %, descriptive filenames | Image SEO + a11y | Scrape |
| Video embedded (+ VideoObject schema) | Engagement/dwell | Scrape |
| Internal links — count + anchor text + targets | Site architecture | Scrape |
| Outbound links — count + authority of targets | Trust/citation | Scrape |
| Lists/tables count (formatting richness) | Scannability | Scrape |
| Author/byline + author bio (E-E-A-T) | Expertise signal | Scrape |
| Trust proof — reviews, testimonials, ratings, badges, client logos, certifications | Conversion + E-E-A-T | Scrape / AI |
| NAP (name/address/phone) + click-to-call | Local relevance | Scrape |

## B. Conversion-design signals `[Scrape]` / `[AI]` (predictor, not actual conversions)

| Signal | Why it matters | Source |
|---|---|---|
| Primary CTA — present, type (form/call/chat/book), above the fold? | Conversion intent | Scrape |
| CTA count + repetition down the page | Conversion design | Scrape |
| Form present — field count, friction | Lead capture friction | Scrape |
| Phone / click-to-call present | Local conversion path | Scrape |
| Live chat / booking widget | Conversion path | Scrape |
| **Actual conversions + conversion rate** | The real outcome | **Own only** |

## C. Technical & markup signals `[Scrape]`

| Signal | Why it matters | Source |
|---|---|---|
| **Schema / structured data — all JSON-LD @types** | The "schema codes" Jake listed | Scrape |
| Canonical tag (present, self vs cross) | Duplicate handling | Scrape |
| Meta robots (index/noindex, follow/nofollow) | Crawl directives | Scrape |
| Open Graph + Twitter Card tags | Social/SERP presentation | Scrape |
| hreflang (international/AU targeting) | Geo targeting | Scrape |
| URL — length, depth, keyword in slug, params | URL signal | Scrape |
| HTTPS, status code, redirect chain | Health | Scrape |
| HTML lang + viewport (mobile) | Mobile/locale | Scrape |
| CMS / platform (generator, fingerprints) | Tooling pattern | Scrape |
| Page weight (HTML KB) + resource count | Performance proxy | Scrape |
| Sitemap + robots.txt (site-level) | Crawlability | Scrape |

## D. Performance / Core Web Vitals `[PSI]`

| Signal | Why it matters | Source |
|---|---|---|
| **Load speed** — LCP, INP, CLS (the 3 Core Web Vitals) | Confirmed ranking factor | PSI/CrUX |
| TTFB, FCP, Speed Index, Total Blocking Time | Speed diagnostics | PSI |
| Lighthouse scores — Performance, SEO, Best Practices, Accessibility | Composite health | PSI |
| Field (real-user CrUX) vs lab — mobile **and** desktop | Real vs synthetic | PSI/CrUX |

## E. UI / UX signals `[AI]` / `[PSI]`

Structural bits are measurable; "good design" is subjective, so we score screenshots against a fixed rubric with a vision model (consistent 1–5 scoring), not vibes.

| Signal | Why it matters | Source |
|---|---|---|
| Layout type, visual hierarchy, above-fold clarity | UX quality | AI (screenshot) |
| Intrusive pop-ups / interstitials | Known Google penalty | Scrape / AI |
| Tap-target size, font size, contrast (mobile UX) | Mobile usability | PSI/Lighthouse |
| Navigation depth, menu structure, clicks-to-convert | Friction | Scrape / AI |
| Sticky header / sticky CTA | Conversion UX | AI |
| Mobile responsiveness | Mobile-first index | PSI/Scrape |
| Overall UI/UX rubric score (1–5) | Comparable UX number | AI (screenshot) |

## F. Authority / off-page `[Paid]`

| Signal | Why it matters | Source |
|---|---|---|
| **Backlinks** — total + referring domains | Core authority | Paid (Ahrefs best; DataForSEO cheaper; Semrush ok) |
| Domain Rating / page-level URL Rating | Authority strength | Paid |
| Anchor-text distribution of inbound links | Relevance of authority | Paid |
| Linking-domain quality (DR of referrers), dofollow ratio | Link quality | Paid |
| Link velocity (new/lost over time) | Momentum | Paid |
| Unlinked brand mentions, local citations / NAP consistency | Brand + local authority | Paid |

## G. SERP / ranking / visibility `[Paid]` / `[Own]`

| Signal | Why it matters | Source |
|---|---|---|
| **Keywords the page actively ranks for** + position of each | Jake's "actively ranking for" | Paid (Semrush/DataForSEO) |
| Count of ranking keywords; how many in top 3 / top 10 | Breadth of success | Paid |
| **Estimated organic traffic to the page** + traffic value | Jake's "how much traffic" | Paid (competitors) / GSC (own) |
| Position for the *target* query + SERP features it triggers | The outcome we're explaining | Paid |
| Target query: search volume, keyword difficulty, **intent type** | Query context (see segmentation) | Paid |
| SERP make-up for the query — ads count, local pack, featured snippet, PAA, directories present | What you're actually competing with | Paid / Scrape |
| GSC: impressions, clicks, CTR, avg position per query | Truth, for own sites | Own |

---

## From practitioner research + the Google API leak (added 2026-06-03)

Net-new signals harvested from the SEO community (r/SEO, r/bigseo), the **May 2024 Google Content Warehouse API leak** (14k+ features), the single-variable testing crowd (Kyle Roof, Matt Diggity), 2026 local-SEO studies, and the GEO/AI-search shift. Hypotheses derived from these live in [[seed-hypotheses]].

### H. Engagement & click signals (NavBoost) — `[Own]` to measure, `[Scrape]` to predict
The leak confirmed Google uses clicks: `goodClicks`, `badClicks`, `lastLongestClicks`, 13 months of history, split by device + region.

| Signal | Why | Source |
|---|---|---|
| Real CTR from search, per query | NavBoost's core input | Own (GSC) |
| Dwell / "last longest click" (pogo-sticking back to SERP) | good vs bad click | Own (GA4) |
| Snippet attractiveness — power words, numbers, brackets, "#1 / best / free" in title/meta | Predicts CTR for any page | Scrape / AI |
| Direct + branded traffic share | Brand strength (correlates with rank) | Own / Paid |

### I. Brand & entity signals — `[Paid]` / `[Scrape]`
| Signal | Why | Source |
|---|---|---|
| Brand search volume | Correlates with rank + AI citations (~0.33) | Paid |
| Branded vs exact-match anchor ratio | Natural vs manipulated profile | Paid |
| Unlinked brand mentions | Entity prominence | Paid |
| Knowledge Graph presence + `sameAs` links (LinkedIn, Wikidata) | Entity confirmation | Scrape / Paid |
| Author entity + bio + external author profiles | E-E-A-T | Scrape |
| Site-level topical depth (same-topic page count + intra-cluster internal links) | "siteAuthority" is topic-specific; deep clusters beat shallow strong domains | Scrape (site crawl) |

### J. Local / Google Business Profile — `[Paid]` / `[Scrape]` (critical: 3 of 4 pilot clients are local)
Local-pack weighting (2026): GBP ~32%, on-page ~19%, reviews ~16%, links ~15%, behavioural ~8%, citations ~7%.

| Signal | Why | Source |
|---|---|---|
| GBP primary category | The #1 local ranking factor | Paid (Maps API) / manual |
| Review count + average rating | Prominence | Paid / Scrape (review schema) |
| Review recency + velocity | Steady recent flow beats stale high count | Paid |
| Keywords in review text | Relevance | Paid |
| NAP consistency (GBP vs site vs directories) | Discrepancies suppress rank | Scrape + Paid |
| Citations / directory listings | Prominence | Paid |
| GBP post cadence + photo count/recency | Freshness + engagement | Paid |
| Proximity to searcher | The "distance" pillar | Paid (geo-grid) |
| Map-pack presence for the query | The local outcome | Paid / Scrape |

### K. AI / generative-search (GEO) — `[Scrape]` / `[AI]` / `[Paid]`
76% of AI-cited URLs rank top-10, but 80% of LLM citations aren't in Google's top-100 — a separate surface worth tracking.

| Signal | Why | Source |
|---|---|---|
| AI Overview / LLM citation presence (ChatGPT, Perplexity, Gemini, AIO) | New visibility surface | Paid / AI |
| Extractable-fact / semantic-triplet density ("[entity] is/does/has [attribute]") | How LLMs parse & cite | AI |
| Answer-first intro (key facts in first 30% of the page) | 44% of LLM citations come from there | Scrape / AI |
| Structured Q&A / FAQ coverage | Citation-friendly | Scrape |

### L. Black / grey-hat detection flags — `[Scrape]` / `[Paid]` (detect, don't emulate)
Tracked to (a) explain ranking anomalies that *violate* our hypotheses, and (b) flag tactics whose gains are usually temporary (spammy parasite pages now last ~6–8 weeks).

| Flag | What it catches | Source |
|---|---|---|
| Review-schema vs visible-reviews mismatch | Fake `aggregateRating` schema spam | Scrape |
| Exact-match anchor over-optimization | Link manipulation | Paid |
| PBN footprint (linking domains share host/registrant/template, thin content) | Private blog networks | Paid |
| Cloaking (raw vs rendered, or Googlebot-UA vs normal-UA diff) | Different content shown to Google | Scrape (dual fetch) |
| AI / spun / thin content patterns | Mass low-value content | Scrape / AI |
| Hidden text / keyword stuffing (display:none, tiny font, stuffed alt) | Old-school spam | Scrape |
| Programmatic doorway pages (near-duplicate templated pages at scale) | Doorway networks | Scrape (site crawl) |

### Kyle Roof's confirmed keyword zones (400+ single-variable tests)
Keyword placement tested as a ranking factor in these exact zones: **URL slug · title tag · H1 · body text · image ALT.** Two counter-findings worth falsifying ourselves: "Google can't *read*" (grammar, spelling, reading level not ranking factors) and "Google can't *see*" (visual design drives conversion, not ranking). Both are in [[seed-hypotheses]].

---

## Segmentation axes (Jake's "it depends on the search term")

Jake is right: whether the keyword belongs in the H1 (and almost every other pattern) **depends on the query**. So every scraped page is tagged with these, and **every hypothesis is scoped to a cell**, never stated globally:

- **Query/intent type:** branded · generic head · generic long-tail · local ("near me"/geo) · commercial-investigation · transactional · informational
- **Page type:** homepage · service page · location page · blog/article · product · category
- **Vertical:** agencies · dental · solar · plumbing · …
- **Geo:** country/region (**Australia is the priority** once DataForSEO is wired in)
- **Device:** mobile · desktop

A finding reads: *"For **local transactional** queries in **dental**, **AU**, on **location pages**, winners put the suburb in the H1 (not the service keyword)."* Scoped, testable, honest. A global "put the keyword in the H1" claim is exactly the weak guesswork we're replacing.

---

## Rigor: when a hunch is allowed to become a pattern

Jake's rule: *"only after an X amount of data, it can't be too weak."* Codified, and this **extends the confidence model in [[seo-anatomy-engine]]**:

### 1. Scrape the losers, not just the winners (the biggest upgrade)
Describing what winners share proves nothing on its own. The signal is **what winners do that losers DON'T.** For every keyword we also scrape a **control set** (pages ranking ~20–50, or page 2–5). If winners and losers both do X, X is table-stakes, not a lever.

### 2. Minimum evidence to promote a finding

| Promotion | Gate |
|---|---|
| Observation → **Hunch** | Any pattern in ≥1 segment cell. Not actionable. |
| Hunch → **Pattern (60–80%)** | ≥30 winners **and** ≥30 losers in a cell; winners-vs-losers gap is statistically significant **and** materially large (see below) |
| Pattern → **Validated (80–90%)** | Holds in **≥3 verticals**, survives confounder control, counter-examples explained, replicates on a held-out sample |
| Validated → **Actionable (90–99%)** | A controlled **live change** on a real page moves ranking in the predicted direction (the only causation proof) |

### 3. "Can't be too weak" — the strength bar
- **Effect size, not just significance.** Require a real gap: for yes/no signals, winners−losers ≥ ~25 percentage points (or Cramér's V ≥ 0.2). A 52%-vs-48% split is noise even if "significant" at huge sample sizes.
- **Proper test.** Two-proportion z-test / chi-square for yes/no signals; Mann-Whitney U for numbers like word count (distributions, not just averages); p < 0.05.
- **Correct for testing many signals at once.** We test 50+ signals, so ~2–3 will look "significant" by pure chance. Apply Benjamini-Hochberg correction so we don't chase false patterns.
- **Control for authority (confounder).** High-authority domains rank for reasons unrelated to on-page. When testing an on-page factor, compare winners vs losers **within the same backlink/DR band**, so authority doesn't masquerade as the on-page effect.
- **Decay.** Re-test every ~90 days or after a known Google update; confidence drops if it stops holding.

---

## Phase 1 capture priority (what we grab first)

1. **Now, free:** all of A, B, C (one wide scrape per page) + store raw HTML + screenshot. Plus the control set (losers).
2. **Add free API:** D (PageSpeed/CrUX) per page.
3. **Add paid (DataForSEO, AU geo):** G first (rankings, keywords-per-page, traffic, SERP make-up, intent), then F (backlinks).
4. **Add AI layer:** E (UI/UX rubric) + content entity coverage in A.
5. **Own sites only:** wire GA4/GSC for true traffic + conversions, to anchor the estimates and run Phase-5 live tests.
