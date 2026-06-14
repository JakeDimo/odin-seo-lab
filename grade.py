"""Grade the SEO corpus — winner-definition per methodology.md, GLANCE-READABLE and honest.

Classes (from organic rank in the label ...|rN):
  WINNER = 1-3 · CHALLENGER = 4-10 · NON-PLACER = 21-45.
Primary comparison: WINNERS vs NON-PLACERS (cleanest contrast). Secondary: WINNERS vs
CHALLENGERS (what separates good from great). Each run overall + per niche + per page-type
where both cohorts clear >=30. Speed is read as CWV PASS-RATE (not raw seconds). Traffic and
ranked-keyword count are AUTHORITY CONTROLS, not the target. Everything is correlation, not a
rule, until a controlled test confirms it.

Reads a single run's results JSON or the accumulated corpus (.jsonl, deduped to latest/page).
Run: uv run grade.py data/corpus.jsonl grades/corpus-latest.md
"""
import sys, json, statistics, re, os, glob
from urllib.parse import urlparse

MIN_N, GAP_PT, GAP_REL = 30, 25, 0.20
LOWER_BETTER = {"LCP (median ms)", "CLS (median)", "URL length"}

NAMES_NOTE = "_% = share of pages with the feature; medians otherwise. Correlation only, not proven cause._"


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.median(xs), 2) if xs else None


def pct(flags):
    flags = [f for f in flags if f is not None]
    return round(100 * sum(1 for f in flags if f) / len(flags)) if flags else None


def kw_tokens(kw):
    return [w for w in re.findall(r"[a-z0-9]+", (kw or "").lower()) if len(w) > 2]


def kw_in(t, kw):
    toks = kw_tokens(kw)
    s = (t or "").lower()
    return bool(toks) and all(w in s for w in toks)


def rank_of(r):
    m = re.search(r"\|r(\d+)$", r.get("label", ""))
    return int(m.group(1)) if m else None


def class_of(rank):
    if rank is None:
        return None
    if 1 <= rank <= 3:
        return "winner"
    if 4 <= rank <= 10:
        return "challenger"
    if 21 <= rank <= 45:
        return "nonplacer"
    return None


CITIES = ["gold-coast", "goldcoast", "brisbane", "sydney", "melbourne", "perth", "adelaide", "hobsons-bay", "hobsonsbay"]


def page_type(r):
    u = (r.get("final_url") or r.get("url") or "").lower()
    path = urlparse(u).path.strip("/")
    if path in ("", "index", "home", "index.html"):
        return "homepage"
    if any(s in u for s in ["/blog", "/article", "/news", "/guide", "/post", "/insight", "/resource", "/tips", "/learn"]):
        return "blog"
    if any(s in u for s in ["/product", "/shop", "/store", "/p/"]):
        return "product"
    if any(c in u for c in CITIES):
        return "location"
    if any(s in u for s in ["/service", "/plumb", "/drain", "/hot-water", "/gas", "/window", "/clean", "/gutter",
                            "/psycholog", "/therap", "/counsel", "/emergency"]):
        return "service"
    if path.count("/") == 0 and len(path) < 40:
        return "service"
    return "other"


def intent(kw):
    k = (kw or "").lower()
    if "near me" in k:
        return "local"
    if any(w in k for w in ["best", " vs ", "review", "compare", "cheap", "affordable", "top "]):
        return "commercial-investigation"
    if any(w in k for w in ["how ", "what ", "why ", "guide"]):
        return "informational"
    return "transactional"


# binary signals
BIN = [
    ("keyword in title", lambda r: kw_in(r.get("title", ""), r["_kw"])),
    ("keyword in H1", lambda r: any(kw_in(h, r["_kw"]) for h in (r.get("h1") or []))),
    ("keyword in URL", lambda r: kw_in((urlparse(r.get("final_url") or r.get("url") or "").path).replace("-", " ").replace("/", " "), r["_kw"])),
    ("has schema", lambda r: bool(r.get("schema_types"))),
    ("aggregateRating schema", lambda r: bool(r.get("schema_aggregate_rating"))),
    ("LocalBusiness schema", lambda r: any(t in ("LocalBusiness", "Plumber", "HomeAndConstructionBusiness") for t in (r.get("schema_types") or []))),
    ("FAQ schema", lambda r: "FAQPage" in (r.get("schema_types") or [])),
    ("OpenGraph", lambda r: r.get("og_present")),
    ("has canonical", lambda r: r.get("has_canonical")),
    ("contact form", lambda r: (r.get("form_count") or 0) > 0),
    # link-context + rich-content + local-trust (added 2026-06-12; sparse until re-render)
    ("has video embed", lambda r: r.get("has_video")),
    ("has map embed", lambda r: r.get("has_map_embed")),
    ("has breadcrumbs", lambda r: r.get("has_breadcrumb")),
    ("trust mentions (licensed/insured)", lambda r: (r.get("trust_mentions") or 0) > 0 if r.get("trust_mentions") is not None else None),
    ("service-area block", lambda r: r.get("has_service_area")),
    ("question-style H2s", lambda r: (r.get("h2_question_count") or 0) > 0 if r.get("h2_question_count") is not None else None),
]
# speed as pass-rate (only counts pages with measured LCP)
SPEED_BIN = [
    ("CWV all-good (LCP<2.5s & CLS<0.1)", lambda r: (r.get("lcp_ms") is not None) and r["lcp_ms"] < 2500 and (r.get("cls") if r.get("cls") is not None else 1) < 0.1),
    ("LCP good (<2.5s)", lambda r: (r.get("lcp_ms") is not None) and r["lcp_ms"] < 2500),
    ("really slow (LCP>4s)", lambda r: (r.get("lcp_ms") is not None) and r["lcp_ms"] > 4000),
]
NUM = [
    ("word count", lambda r: r.get("word_count")),
    ("schema types", lambda r: len(r.get("schema_types") or [])),
    ("internal links", lambda r: r.get("internal_links")),
    ("in-content internal links", lambda r: r.get("main_internal_links")),
    ("nav/footer links", lambda r: r.get("nav_link_count")),
    ("question H2/H3s", lambda r: r.get("h2_question_count")),
    ("trust mentions", lambda r: r.get("trust_mentions")),
    ("outbound links", lambda r: r.get("external_links")),
    ("readability", lambda r: r.get("readability_flesch")),
    ("title length", lambda r: r.get("title_len")),
    ("URL length", lambda r: len(r.get("final_url") or r.get("url") or "")),
    ("LCP (median ms)", lambda r: r.get("lcp_ms")),
    ("CLS (median)", lambda r: r.get("cls")),
    # off-page authority (Semrush) — the real off-page signal (reverse-causation caveat C3 applies)
    ("referring domains", lambda r: r.get("referring_domains")),
    ("Authority Score", lambda r: r.get("domain_rank")),
    ("total backlinks", lambda r: r.get("backlinks_total")),
    # authority controls (downstream of rank — context, not levers)
    ("[ctrl] est. traffic", lambda r: r.get("etv")),
    ("[ctrl] ranked keywords", lambda r: r.get("ranked_keywords")),
]


def load(src):
    """Single-run JSON array, or the accumulated corpus via the coalescing loader
    (nulls never clobber real values, so a failed re-scan can't wipe earlier enrichment)."""
    if not src.endswith(".jsonl"):
        return json.load(open(src, encoding="utf-8"))
    from corpus_load import load as _coalesce
    return _coalesce(src)


def vbin(a, b, big):
    if a is None or b is None:
        return "—"
    d = a - b
    if abs(d) < GAP_PT:
        return "➖ no link"
    base = "✅ more in winners" if d > 0 else "❌ less in winners"
    return base if big else base + " (low n)"


def vnum(a, b, big, key):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or not b:
        return "—"
    rel = (a - b) / abs(b)
    if abs(rel) < GAP_REL:
        return "➖ no link"
    higher = rel > 0
    if key in LOWER_BETTER:
        base = "❌ winners worse (higher)" if higher else "✅ winners better (lower)"
    else:
        base = "✅ higher in winners" if higher else "❌ lower in winners"
    return base + ("" if big else " (low n)")


def section(title, A, B, a_label, b_label, collect=None):
    big = len(A) >= MIN_N and len(B) >= MIN_N
    out = [f"\n### {title}", "",
           f"{a_label} **{len(A)}** vs {b_label} **{len(B)}** — "
           + ("enough data" if big else f"under {MIN_N}/side, hints only"),
           "", NAMES_NOTE, "",
           f"| Signal | {a_label} | {b_label} | Verdict |", "|---|---|---|---|"]
    for name, fn in BIN + SPEED_BIN:
        a, b = pct([fn(r) for r in A]), pct([fn(r) for r in B])
        v = vbin(a, b, big)
        out.append(f"| {name} | {f'{a}%' if a is not None else '–'} | {f'{b}%' if b is not None else '–'} | {v} |")
        if collect is not None and big and v.startswith("✅") and name != "really slow (LCP>4s)":
            collect.append(name)
    for name, fn in NUM:
        a, b = med([fn(r) for r in A]), med([fn(r) for r in B])
        v = vnum(a, b, big, name)
        out.append(f"| {name} | {a} | {b} | {v} |")
        if collect is not None and big and v.startswith("✅") and not name.startswith("[ctrl]"):
            collect.append(("lower " if name in LOWER_BETTER else "") + name)
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    src, out = sys.argv[1], sys.argv[2]
    recs = []
    for r in load(src):
        if r.get("status") != 200 or "word_count" not in r:
            continue
        p = r.get("label", "").split("|")
        r["_niche"], r["_kw"] = (p[1] if len(p) > 1 else "?"), (p[2] if len(p) > 2 else "")
        r["_cls"] = class_of(rank_of(r))
        r["_ptype"] = page_type(r)
        r["_intent"] = intent(r["_kw"])
        if r["_cls"]:
            recs.append(r)
    W = [r for r in recs if r["_cls"] == "winner"]
    C = [r for r in recs if r["_cls"] == "challenger"]
    N = [r for r in recs if r["_cls"] == "nonplacer"]
    niches = sorted(set(r["_niche"] for r in recs))

    wins = []
    primary = section("Overall — winners (1-3) vs non-placers (21-45)", W, N, "Win(1-3)", "Non(21-45)", collect=wins)

    lines = ["# What separates a top-3 page — AU test (LEADS, not rules)", "",
             f"Corpus: **{len(recs)}** graded pages — **{len(W)}** winners (rank 1-3), **{len(C)}** challengers (4-10), "
             f"**{len(N)}** non-placers (21-45), across {len(niches)} niches.", "",
             "> ⚠️ **Correlations, not proven rules.** Within-rank comparisons + page-type segmentation control for the "
             "obvious confounders, but nothing here is causal until a controlled live test confirms it. Traffic & ranked-keyword "
             "rows are `[ctrl]` (downstream of rank — context, not levers). Speed is read as CWV pass-rate.",
             "", "## Bottom line (winners vs non-placers)", ""]
    if wins:
        lines.append("**More common in top-3 pages (leads to test):**")
        for w in dict.fromkeys(wins):
            lines.append(f"- ✅ {w}")
    else:
        lines.append("**What separates top-3:** nothing cleared the bar at this sample size yet.")
    lines += ["", "Everything else showed no link (see ➖ rows). Authority controls (`[ctrl]`) below are context, not levers.", ""]
    lines += primary

    # winners vs challengers (good vs great)
    lines += ["", "## Winners (1-3) vs challengers (4-10) — what separates good from great", ""]
    lines += section("Overall — winners (1-3) vs challengers (4-10)", W, C, "Win(1-3)", "Chal(4-10)")

    # per niche (winners vs non-placers)
    lines += ["", "## By niche (winners vs non-placers)"]
    for n in niches:
        a = [r for r in W if r["_niche"] == n]
        b = [r for r in N if r["_niche"] == n]
        lines += section(f"{n}", a, b, "Win(1-3)", "Non(21-45)")

    # per page-type (winners vs non-placers), only types with data
    lines += ["", "## By page-type (winners vs non-placers)"]
    ptypes = sorted(set(r["_ptype"] for r in recs))
    for pt in ptypes:
        a = [r for r in W if r["_ptype"] == pt]
        b = [r for r in N if r["_ptype"] == pt]
        if len(a) + len(b) >= 20:
            lines += section(f"page-type: {pt}", a, b, "Win(1-3)", "Non(21-45)")

    # distributions
    def dist(rows, field):
        d = {}
        for r in rows:
            d[r[field]] = d.get(r[field], 0) + 1
        return ", ".join(f"{k}={v}" for k, v in sorted(d.items(), key=lambda x: -x[1]))
    lines += ["", "## Corpus composition", "",
              f"- Page-types: {dist(recs, '_ptype')}",
              f"- Intents: {dist(recs, '_intent')}",
              f"- Speed measured: {sum(1 for r in recs if isinstance(r.get('lcp_ms'), (int, float)))} pages (CWV pass-rate only meaningful on these)", ""]

    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:40]))
    print(f"\n... WROTE {out}  ({len(recs)} pages; W={len(W)} C={len(C)} N={len(N)})")


if __name__ == "__main__":
    main()
