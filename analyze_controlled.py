"""Authority-CONTROLLED read of the within-page-1 signals.

The raw top-3-vs-4-10 gaps are confounded: fresher pages and homepages tend to be
better-linked too. This script (1) freezes a snapshot of the corpus so concurrent cloud
runs don't disturb the read, (2) reports the raw gap, then (3) re-tests each signal INSIDE
referring-domain tertiles — if a gap only shows in the high-authority tertile it's an
authority confound; if it holds in the low/mid band it's a real re-ranking lead.

Run: uv run analyze_controlled.py data/corpus.jsonl
"""
import sys, json, statistics, glob, os, re

NUM = ["ranked_keywords", "etv", "page_age_days", "title_ctr_score", "internal_links",
       "word_count", "list_count", "lead_para_words", "stat_count"]
BIN = ["title_len_ok", "query_in_title", "query_early_title", "has_freshness_date", "has_author"]
QDF = re.compile(r"\b(emergency|best|cost|price|near me|2024|2025|2026|rebate|quote)\b", re.I)


def load(src):
    from corpus_load import load as _coalesce   # coalescing dedupe: nulls never clobber real values
    return _coalesce(src)


def rank_of(r):
    m = re.search(r"\|r(\d+)$", r.get("label", ""))
    return int(m.group(1)) if m else None


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return round(statistics.median(xs), 1) if xs else None


def rate(xs):
    xs = [x for x in xs if x is not None]
    return round(100 * sum(1 for x in xs if x) / len(xs)) if xs else None


def cmp_block(t3, rest, title):
    print(f"\n### {title}  (top3 n={len(t3)} · 4-10 n={len(rest)})")
    print("| signal | top3 | 4-10 | gap | direction |")
    print("|---|---|---|---|---|")
    for k in NUM:
        a, b = med([r.get(k) for r in t3]), med([r.get(k) for r in rest])
        if a is None or b is None:
            continue
        gap = round(a - b, 1)
        better = "top3 lower" if k in ("page_age_days",) else ("top3 higher" if gap > 0 else ("flat" if gap == 0 else "4-10 higher"))
        print(f"| {k} (median) | {a} | {b} | {gap:+} | {better} |")
    for k in BIN:
        a, b = rate([r.get(k) for r in t3]), rate([r.get(k) for r in rest])
        if a is None or b is None:
            continue
        print(f"| {k} (%) | {a}% | {b}% | {a - b:+}pt | {'top3 higher' if a > b else ('flat' if a == b else '4-10 higher')} |")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    recs = load(sys.argv[1])
    for r in recs:
        r["__rank"] = rank_of(r)
        p = r.get("label", "").split("|")
        r["__kw"] = p[2] if len(p) >= 3 else ""
        r["__niche"] = p[1] if len(p) >= 2 else ""
    recs = [r for r in recs if r.get("status") == 200 and r.get("__rank") and "word_count" in r]
    json.dump(recs, open(os.path.join(os.path.dirname(sys.argv[1]) or ".", "analysis_snapshot.json"),
                         "w", encoding="utf-8"), ensure_ascii=False)

    t3 = [r for r in recs if 1 <= r["__rank"] <= 3]
    rest = [r for r in recs if 4 <= r["__rank"] <= 10]

    print(f"# Authority-controlled within-page-1 read ({len(recs)} pages; top3={len(t3)}, 4-10={len(rest)})")
    print("\n_Leads, not rules. A gap that survives the mid-authority band (where top3 and 4-10 are "
          "equally linked) is a real re-ranking lead; a gap that only appears in the high-authority "
          "tertile is an authority confound._")

    cmp_block(t3, rest, "RAW (uncontrolled)")

    # Authority tertiles on referring_domains across page-1 pages
    p1 = t3 + rest
    auth = sorted(r.get("referring_domains") for r in p1 if isinstance(r.get("referring_domains"), (int, float)))
    if len(auth) >= 9:
        q1, q2 = auth[len(auth) // 3], auth[2 * len(auth) // 3]
        print(f"\n## Authority tertiles (referring domains): low <{q1} · mid {q1}-{q2} · high >{q2}")
        bands = [("LOW authority", lambda r: r.get("referring_domains", -1) < q1),
                 ("MID authority (the clean test band)", lambda r: q1 <= r.get("referring_domains", -1) <= q2),
                 ("HIGH authority", lambda r: r.get("referring_domains", -1) > q2)]
        for name, fn in bands:
            cmp_block([r for r in t3 if isinstance(r.get("referring_domains"), (int, float)) and fn(r)],
                      [r for r in rest if isinstance(r.get("referring_domains"), (int, float)) and fn(r)], name)
    else:
        print("\n_(not enough authority data yet for tertiles — populates as enrichment lands)_")

    # Freshness by niche + by query type (QDF)
    print("\n## Freshness (page age days, lower=fresher) by niche")
    print("| niche | top3 | 4-10 | gap |")
    print("|---|---|---|---|")
    for n in sorted({r["__niche"] for r in p1}):
        a = med([r.get("page_age_days") for r in t3 if r["__niche"] == n])
        b = med([r.get("page_age_days") for r in rest if r["__niche"] == n])
        if a is not None and b is not None:
            print(f"| {n} | {a} | {b} | {round(a - b, 1):+} |")

    print("\n## Freshness by query type (QDF hypothesis)")
    print("| query type | top3 age | 4-10 age | gap | n(top3) |")
    print("|---|---|---|---|---|")
    for label, fn in [("QDF-ish (emergency/best/cost/year/quote)", lambda kw: bool(QDF.search(kw))),
                      ("evergreen", lambda kw: not QDF.search(kw))]:
        ta = [r for r in t3 if fn(r["__kw"])]
        ra = [r for r in rest if fn(r["__kw"])]
        a, b = med([r.get("page_age_days") for r in ta]), med([r.get("page_age_days") for r in ra])
        if a is not None and b is not None:
            print(f"| {label} | {a} | {b} | {round(a - b, 1):+} | {len(ta)} |")


if __name__ == "__main__":
    main()
