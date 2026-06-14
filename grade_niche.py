"""Grade a niche: winners-vs-losers comparison across signals from a render run.
Render labels are 'win|rN|keyword' / 'lose|rN|keyword' (set by serp_au.py).

Run:
  uv run grade_niche.py data/results_grade_render.json data/grade_gc_plumber.md
"""
import sys, json, statistics


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.median(xs), 2) if xs else None


def pct(flags):
    flags = [f for f in flags if f is not None]
    return round(100 * sum(1 for f in flags if f) / len(flags)) if flags else None


def main():
    src, out = sys.argv[1], sys.argv[2]
    recs = [r for r in json.load(open(src, encoding="utf-8"))
            if r.get("status") == 200 and "word_count" in r]
    kw, W, L = "", [], []
    for r in recs:
        parts = r.get("label", "").split("|")
        if len(parts) >= 3:
            kw = parts[-1]
        (W if parts and parts[0] == "win" else L).append(r)

    def kw_in(t):
        return kw.lower() in (t or "").lower()

    lines = [f"# Niche grade — {kw} (AU)", ""]
    lines.append(f"Winners (top-10): **{len(W)}** · Losers (rank 21–45): **{len(L)}**. "
                 f"Pilot run, single niche, small n, so **every row is a Hunch** until it holds across niches with bigger samples.")
    lines.append("")
    lines.append("| Signal | Winners | Losers |")
    lines.append("|---|---|---|")

    def binrow(name, fn):
        lines.append(f"| {name} (% with) | {pct([fn(r) for r in W])} | {pct([fn(r) for r in L])} |")

    def numrow(name, fn):
        lines.append(f"| {name} (median) | {med([fn(r) for r in W])} | {med([fn(r) for r in L])} |")

    binrow("keyword in title", lambda r: kw_in(r.get("title", "")))
    binrow("keyword in H1", lambda r: any(kw_in(h) for h in r.get("h1", [])))
    binrow("has schema", lambda r: bool(r.get("schema_types")))
    binrow("aggregateRating schema", lambda r: bool(r.get("schema_aggregate_rating")))
    binrow("has canonical", lambda r: r.get("has_canonical"))
    binrow("OpenGraph tags", lambda r: r.get("og_present"))
    binrow("a form present", lambda r: (r.get("form_count") or 0) > 0)
    numrow("word count", lambda r: r.get("word_count"))
    numrow("schema type count", lambda r: len(r.get("schema_types", [])))
    numrow("H2 count", lambda r: r.get("h2_count"))
    numrow("internal links", lambda r: r.get("internal_links"))
    numrow("title length", lambda r: r.get("title_len"))
    numrow("CTAs", lambda r: r.get("cta_count"))
    numrow("image alt coverage", lambda r: r.get("alt_coverage"))

    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWROTE {out}")


if __name__ == "__main__":
    main()
