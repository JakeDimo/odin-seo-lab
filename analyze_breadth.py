"""Ranking BREADTH: does a top-ranking URL also rank for closely-related keywords (a topic
cluster), or just the one term? Tests Jake's hypothesis that modern Google rewards pages that
own a related cluster (phrase-match-like), not single-term pages.

Computed FREE from the corpus we already collect: for each URL, how many DISTINCT keywords in
our pool it ranks for (top-20 / top-10). Then compare top3 vs 4-10 vs non-placers. The clean
cut is top3 vs 4-10 (both are page-1). Confounded with authority (stronger sites rank for
more), so a lead, not a rule.

Run: uv run analyze_breadth.py data/corpus.jsonl
"""
import sys, json, statistics, glob, os, re
from collections import defaultdict


def load(src):
    from corpus_load import load as _coalesce   # coalescing dedupe: nulls never clobber real values
    return _coalesce(src)


def rank_of(r):
    m = re.search(r"\|r(\d+)$", r.get("label", ""))
    return int(m.group(1)) if m else None


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.median(xs), 1) if xs else None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    recs = load(sys.argv[1])
    for r in recs:
        p = r.get("label", "").split("|")
        r["__kw"] = p[2] if len(p) >= 3 else ""
        r["__niche"] = p[1] if len(p) >= 2 else ""
        r["__rank"] = rank_of(r)
        r["__url"] = r.get("final_url") or r.get("url")
    recs = [r for r in recs if r["__rank"] and r["__url"]]

    kw20, kw10 = defaultdict(set), defaultdict(set)
    for r in recs:
        if r["__rank"] <= 20:
            kw20[r["__url"]].add(r["__kw"])
        if r["__rank"] <= 10:
            kw10[r["__url"]].add(r["__kw"])
    for r in recs:
        r["__b20"] = len(kw20[r["__url"]])
        r["__b10"] = len(kw10[r["__url"]])

    BUCKETS = [("top3 (1-3)", lambda n: 1 <= n <= 3),
               ("page1 rest (4-10)", lambda n: 4 <= n <= 10),
               ("low (21-45)", lambda n: 21 <= n <= 45)]
    print(f"# Ranking breadth — does a winner own a CLUSTER of related keywords? ({len(recs)} rows)")
    print("\n_Breadth = how many DISTINCT keywords in our pool the URL ranks for. Free from our own"
          " corpus. The clean comparison is top3 vs 4-10 (both page-1). Confounded with authority"
          " (stronger sites rank for more), so a lead not a rule._\n")
    print("| bucket | n rows | median keywords/URL (top-20) | median (top-10) | % single-keyword | % cluster (>=3 kw) |")
    print("|---|---|---|---|---|---|")
    for name, fn in BUCKETS:
        rows = [r for r in recs if fn(r["__rank"])]
        if not rows:
            continue
        b20 = [r["__b20"] for r in rows]
        single = round(100 * sum(1 for x in b20 if x <= 1) / len(b20))
        cluster = round(100 * sum(1 for x in b20 if x >= 3) / len(b20))
        print(f"| {name} | {len(rows)} | {med(b20)} | {med([r['__b10'] for r in rows])} | {single}% | {cluster}% |")

    # Within-page-1 cut by niche (clean: top3 vs 4-10)
    print("\n## Top-3 vs 4-10 breadth by niche (median keywords/URL, top-20)")
    print("| niche | top3 | 4-10 |")
    print("|---|---|---|")
    for n in sorted({r["__niche"] for r in recs}):
        t3 = med([r["__b20"] for r in recs if r["__niche"] == n and 1 <= r["__rank"] <= 3])
        rest = med([r["__b20"] for r in recs if r["__niche"] == n and 4 <= r["__rank"] <= 10])
        if t3 is not None and rest is not None:
            print(f"| {n} | {t3} | {rest} |")


if __name__ == "__main__":
    main()
