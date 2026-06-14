---
title: Experiments — the only path from LEAD to proven RULE
type: spec
status: active
updated: 2026-06-14
---

# Experiments — turning leads into proven rules

The corpus tells us what **correlates** with ranking ([[rulebook]]). It can never tell us what **causes** it. The goal — a proven, repeatable way to lift a page's rank — needs **controlled live tests**: change ONE variable on a real page, hold everything else, watch the rank move (or not). A factor graduates from LEAD to **RULE** only after it moves real pages here. This file is the ledger; the system's whole purpose is to grow the "Rules" section below.

## Protocol (single-variable causal test)

1. **Pick a candidate** from [[rulebook]] — a confirmed LEAD first (internal links, topical breadth).
2. **Pick targets:** 5-15 of *our* client pages stuck at ranks ~4-15 for a specific query (on page one but not top-3, where there's headroom and the re-ranking layer is what's in play).
3. **Split** into treatment and matched controls (similar rank, niche, authority).
4. **Apply the ONE change** to treatment pages only. Record the date.
5. **Track** weekly for 6-12 weeks with Search Console (`analyze_movement.py` for position, `gsc_coec.py` for click behaviour). NavBoost-class effects take weeks, not days.
6. **Read the result:** did treatment pages climb relative to controls, beyond normal week-to-week noise?
7. **Verdict:** CONFIRMED → promote to a RULE (add to `rulebook.py` VERIFIED + [[findings-log]]); NULL → mark the lead dead; INCONCLUSIVE → rerun with more pages.

## Rules (proven by a live test)

_None yet. Filling this section is the entire point of the project. The first entry is the moment we have a guaranteed lever._

## Queue (ranked — confirmed leads first)

| # | Factor | The single change to make | Targets | Status | Result |
|---|---|---|---|---|---|
| 1 | **Internal links** | Add a set of internal links pointing at one stuck page from relevant pages on the same site | client pages, TBD | proposed | — |
| 2 | **Topical breadth** | Add related-cluster pages/sections so the target page covers the whole topic, not one term | TBD | proposed | — |
| 3 | Title 40-60 chars | Retitle a stuck page into the truncation-safe band, nothing else | TBD | proposed | — |

## Guardrails

- **One variable per test**, or the rank move can't be attributed.
- **Matched controls always** — a page that moved without a control proves nothing.
- **Client pages only, with Jake's explicit go** — these are live sites.
- **6-12 week window** — rank is noisy week to week; short reads lie.
- **Write everything here.** A result that isn't logged didn't happen.

## Status: framework ready, awaiting go

Jake owns when a live test starts. The protocol, queue, and tracking (movement + COEC) are ready; **nothing runs on a client page without explicit approval.** When you say go, we pick a factor and targets and start the clock.
