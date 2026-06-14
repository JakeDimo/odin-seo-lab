"""Rank MOVEMENT over time — the longitudinal read the per-run shards make possible.

Everything else in the lab compares pages cross-sectionally. This script instead keys on
(url, niche|keyword) and follows the SAME page's rank across run_dates: how sticky is a
top-3 spot, how much churn happens on page 1, which niches are volatile. Reads shards
directly (NOT the coalescing loader — that would collapse the history we're after).

Rank-only observations (observation="rank") count the same as rendered ones: an
observation is an observation. As the 8-hourly rotation runs, every page accrues a rank
time-series at near-zero cost; once we change a page (ours or a client's), this is where
the before/after shows up — the bridge from correlation to causation.

Run: uv run analyze_movement.py data/corpus.jsonl > grades/movement-latest.md
"""
import sys, json, re, os, glob, statistics
from collections import defaultdict


def rank_of(label):
    m = re.search(r"\|r(\d+)$", label or "")
    return int(m.group(1)) if m else None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    src = sys.argv[1]
    files = ([src] if os.path.exists(src) else [])
    files += sorted(glob.glob(os.path.join(os.path.dirname(src) or ".", "corpus", "*.jsonl")))

    series = defaultdict(dict)   # (url, niche|kw) -> {date: rank}
    for fp in files:
        try:
            fh = open(fp, encoding="utf-8")
        except Exception:
            continue
        for line in fh:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            rank, day = rank_of(r.get("label")), r.get("run_date")
            if rank is None or not day:
                continue
            p = r.get("label", "").split("|")
            key = (r.get("final_url") or r.get("url"), "|".join(p[1:3]))
            series[key][day] = rank          # last observation that day wins
        fh.close()

    multi = {k: sorted(v.items()) for k, v in series.items() if len(v) >= 2}
    print(f"# Rank movement over time ({len(series)} tracked page-keyword pairs, "
          f"{len(multi)} observed on 2+ days)\n")
    if not multi:
        print("_No pair observed on two different days yet — movement appears once the "
              "rotation has run on consecutive days._")
        return

    moves = []
    for (url, nk), obs in multi.items():
        first, last = obs[0], obs[-1]
        moves.append({"url": url, "nk": nk, "from": first[1], "to": last[1],
                      "d0": first[0], "d1": last[0], "delta": first[1] - last[1]})  # + = improved

    deltas = [m["delta"] for m in moves]
    moved = [m for m in moves if m["delta"] != 0]
    print(f"- pairs that moved at all: **{len(moved)}/{len(moves)}** "
          f"({round(100*len(moved)/len(moves))}%)")
    print(f"- median |move|: **{statistics.median([abs(d) for d in deltas])}** positions"
          f" · biggest rise +{max(deltas)} · biggest fall {min(deltas)}")

    # top-3 stickiness: of pairs that STARTED in the top 3, how many stayed?
    started_top3 = [m for m in moves if m["from"] <= 3]
    if started_top3:
        stayed = sum(1 for m in started_top3 if m["to"] <= 3)
        print(f"- top-3 stickiness: **{stayed}/{len(started_top3)}** "
              f"({round(100*stayed/len(started_top3))}%) of top-3 starters were still top-3 at last look")
    entered = [m for m in moves if m["from"] > 3 and m["to"] <= 3]
    print(f"- broke INTO the top 3: **{len(entered)}** pairs")

    by_niche = defaultdict(list)
    for m in moves:
        by_niche[m["nk"].split("|")[0]].append(abs(m["delta"]))
    print("\n## Volatility by niche (median |move|, pairs tracked)\n")
    print("| niche | median |move| | pairs |")
    print("|---|---|---|")
    for n, ds in sorted(by_niche.items(), key=lambda x: -statistics.median(x[1])):
        print(f"| {n} | {statistics.median(ds)} | {len(ds)} |")

    risers = sorted(moves, key=lambda m: -m["delta"])[:10]
    fallers = sorted(moves, key=lambda m: m["delta"])[:10]
    print("\n## Biggest risers\n\n| Δ | from→to | keyword | url |\n|---|---|---|---|")
    for m in risers:
        if m["delta"] <= 0:
            break
        print(f"| +{m['delta']} | r{m['from']}→r{m['to']} | {m['nk']} | {m['url'][:80]} |")
    print("\n## Biggest fallers\n\n| Δ | from→to | keyword | url |\n|---|---|---|---|")
    for m in fallers:
        if m["delta"] >= 0:
            break
        print(f"| {m['delta']} | r{m['from']}→r{m['to']} | {m['nk']} | {m['url'][:80]} |")

    print("\n> An observation is one (day, rank) snapshot per page-keyword pair. Movement "
          "is first-vs-last observation. Correlation discipline applies: a mover proves "
          "volatility, not cause — causation needs a logged page CHANGE between the two looks.")


if __name__ == "__main__":
    main()
