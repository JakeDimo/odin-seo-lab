"""Analyse the corpus by ACTUAL rank position, not just the crude win/lose split — to
test whether finer buckets reveal gradients the top-10-vs-21-45 split hides, and to
answer 'are the top 3 actually different?' (esp. on speed). Rank is in the label (...|rN).

Buckets: top3 (1-3) · page-1 rest (4-10) · low (21-45).
Run: uv run analyze_by_position.py data/corpus.jsonl
"""
import sys, json, statistics, re, os, glob


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.median(xs), 2) if xs else None


def pct(flags):
    flags = [f for f in flags if f is not None]
    return round(100 * sum(1 for f in flags if f) / len(flags)) if flags else None


def kw_in(t, kw):
    toks = [w for w in re.findall(r"[a-z0-9]+", (kw or "").lower()) if len(w) > 2]
    s = (t or "").lower()
    return bool(toks) and all(w in s for w in toks)


def load(src):
    from corpus_load import load as _coalesce   # coalescing dedupe: nulls never clobber real values
    return _coalesce(src)


def rank_of(r):
    m = re.search(r"\|r(\d+)$", r.get("label", ""))
    return int(m.group(1)) if m else None


BUCKETS = [("top3 (1-3)", lambda n: 1 <= n <= 3),
           ("page1 rest (4-10)", lambda n: 4 <= n <= 10),
           ("low (21-45)", lambda n: 21 <= n <= 45)]

NUM = [("LCP ms (lower=faster)", lambda r: r.get("lcp_ms")),
       ("page-speed score", lambda r: r.get("perf_score")),
       ("CLS", lambda r: r.get("cls")),
       ("est. monthly traffic", lambda r: r.get("etv")),
       ("ranked keywords", lambda r: r.get("ranked_keywords")),
       ("word count", lambda r: r.get("word_count")),
       ("schema types", lambda r: len(r.get("schema_types") or [])),
       ("internal links", lambda r: r.get("internal_links")),
       ("outbound links", lambda r: r.get("external_links")),
       ("title length", lambda r: r.get("title_len")),
       # --- new within-page-1 signals (sparse until the rotation re-scrapes) ---
       ("page age days (lower=fresher)", lambda r: r.get("page_age_days")),
       ("title click-score /5", lambda r: r.get("title_ctr_score")),
       ("E-E-A-T score /3", lambda r: r.get("eeat_score")),
       ("lists (ul/ol)", lambda r: r.get("list_count")),
       ("tables", lambda r: r.get("table_count")),
       ("stat/$ mentions", lambda r: r.get("stat_count")),
       ("lead paragraph words", lambda r: r.get("lead_para_words")),
       ("keyword exact count", lambda r: r.get("kw_exact_count")),
       ("keyword density /1k words", lambda r: r.get("kw_density_per_1k")),
       # --- link-context + trust signals (added 2026-06-12; sparse until re-render) ---
       ("in-content internal links", lambda r: r.get("main_internal_links")),
       ("nav/footer links", lambda r: r.get("nav_link_count")),
       ("question H2/H3s", lambda r: r.get("h2_question_count")),
       ("trust mentions (licensed/insured)", lambda r: r.get("trust_mentions"))]

BIN = [("keyword in title", lambda r: kw_in(r.get("title", ""), r["__kw"])),
       ("keyword in H1", lambda r: any(kw_in(h, r["__kw"]) for h in (r.get("h1") or []))),
       ("has schema", lambda r: bool(r.get("schema_types"))),
       ("aggregateRating schema", lambda r: bool(r.get("schema_aggregate_rating"))),
       # --- new within-page-1 signals ---
       ("has freshness date", lambda r: r.get("has_freshness_date")),
       ("query in lead para", lambda r: r.get("query_in_lead")),
       ("query front-loaded in title", lambda r: r.get("query_early_title")),
       ("title 40-60 chars", lambda r: r.get("title_len_ok")),
       ("has author/byline (E-E-A-T)", lambda r: r.get("has_author")),
       ("has FAQ schema", lambda r: r.get("has_faq")),
       ("has video embed", lambda r: r.get("has_video")),
       ("has map embed", lambda r: r.get("has_map_embed")),
       ("has breadcrumbs", lambda r: r.get("has_breadcrumb")),
       ("service-area block", lambda r: r.get("has_service_area"))]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    recs = load(sys.argv[1])
    for r in recs:
        p = r.get("label", "").split("|")
        r["__kw"] = p[2] if len(p) >= 3 else ""
        r["__rank"] = rank_of(r)
    recs = [r for r in recs if r.get("status") == 200 and r.get("__rank") and "word_count" in r]
    cols = [(name, [r for r in recs if fn(r["__rank"])]) for name, fn in BUCKETS]

    print(f"# Corpus by rank position ({len(recs)} pages)\n")
    print("Per-bucket counts: " + " · ".join(f"{n}={len(rows)}" for n, rows in cols) + "\n")
    print("| Signal | " + " | ".join(n for n, _ in cols) + " |")
    print("|---" * (len(cols) + 1) + "|")
    for label, fn in NUM:
        print(f"| {label} (median) | " + " | ".join(str(med([fn(r) for r in rows])) for _, rows in cols) + " |")
    for label, fn in BIN:
        print(f"| {label} (%) | " + " | ".join(str(pct([fn(r) for r in rows])) for _, rows in cols) + " |")

    print("\n## Speed reality check (mobile LCP)")
    meas = [r for r in recs if isinstance(r.get("lcp_ms"), (int, float))]
    print(f"pages with speed measured: {len(meas)}")
    for name, fn in BUCKETS:
        b = sorted(r["lcp_ms"] for r in meas if fn(r["__rank"]))
        if b:
            good = round(100 * sum(1 for x in b if x < 2500) / len(b))
            print(f"  {name}: n={len(b)}  median LCP={round(statistics.median(b))}ms  "
                  f"best-quartile={round(b[len(b)//4])}ms  meeting Google 'good' (<2.5s)={good}%")

    # Page-type mix per bucket (H3: does the winner's FORMAT match query intent?)
    typed = [r for r in recs if r.get("page_type")]
    print(f"\n## Page-type mix by bucket (H3 intent-match — n with type: {len(typed)})")
    if typed:
        ptypes = sorted({r["page_type"] for r in typed})
        print("| page type | " + " | ".join(n for n, _ in BUCKETS) + " |")
        print("|---" * (len(BUCKETS) + 1) + "|")
        for pt in ptypes:
            row = []
            for _, fn in BUCKETS:
                grp = [r for r in typed if fn(r["__rank"])]
                row.append(f"{round(100*sum(1 for r in grp if r['page_type']==pt)/len(grp))}%" if grp else "-")
            print(f"| {pt} | " + " | ".join(row) + " |")
    else:
        print("_(no pages carry page_type yet — populates as the 8-hourly rotation re-scrapes, ~1 day)_")

    print("\n> **Read as leads, not rules.** New-signal rows are sparse until the rotation "
          "re-scrapes the corpus. Before crediting any signal, control for authority "
          "(restrict to equal-referring-domain SERPs, or add referring_domains as a covariate) — "
          "fresher/deeper/branded pages tend to be better-linked too.")


if __name__ == "__main__":
    main()
