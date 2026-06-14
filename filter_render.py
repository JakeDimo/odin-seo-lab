"""Incremental-render splitter — the GitHub-minutes fix.

Sits between serp_batch.py and scrape_render.py. SERP rank data changes daily and is
cheap; page CONTENT barely changes week to week, yet re-rendering every ranking URL is
what made each cloud run cost 30-75 runner-minutes and killed the free Actions quota.

Split this run's SERP rows into:
  - RENDER  — URLs we've never rendered, or whose last render is older than
              RENDER_TTL_DAYS (default 14). Capped at RENDER_CAP (default 500),
              never-rendered first, then stalest-first.
  - RANK-ONLY — URLs already fresh in the corpus. Written as lightweight rank
              observations (label + SERP fields, final_url mapped from the corpus so
              the coalescing loader merges them into the rendered row). They refresh
              rank/serp_features/run_date daily at ~zero runner cost, and the per-run
              shards preserve full rank HISTORY for analyze_movement.py.

Staleness reads `rendered_date` (stamped by accumulate.py at render time), falling
back to run_date for rows from before the field existed.

Run: uv run filter_render.py data/urls_batch.json data/corpus.jsonl \
        data/urls_to_render.json data/rank_only.json
"""
import sys, os, json, datetime

TTL_DAYS = int(os.environ.get("RENDER_TTL_DAYS", "14"))
CAP = int(os.environ.get("RENDER_CAP", "500"))


def main():
    batch_f, corpus_f, render_f, rank_f = sys.argv[1:5]
    batch = json.load(open(batch_f, encoding="utf-8"))

    from corpus_load import load as coalesce
    today = datetime.date.today()
    seen = {}   # url AND final_url -> (rendered_age_days or None, final_url)
    for r in coalesce(corpus_f):
        if "word_count" not in r:
            continue                       # rank-only stub, not a rendered page
        stamp = r.get("rendered_date") or r.get("run_date")
        age = None
        try:
            age = (today - datetime.date.fromisoformat(stamp)).days
        except Exception:
            pass
        fu = r.get("final_url") or r.get("url")
        for k in {r.get("url"), fu} - {None}:
            seen[k] = (age, fu)

    to_render, rank_only = [], []

    def rank_row(e, final_url):
        # serp_batch labels rows under "client"; normalise so accumulate/corpus_load match
        r = {**e, "final_url": final_url}
        r["label"] = r.pop("client", None) or r.get("label")
        return r

    for e in batch:
        hit = seen.get(e["url"])
        if hit and hit[0] is not None and hit[0] <= TTL_DAYS:
            rank_only.append(rank_row(e, hit[1]))
        else:
            # sort key: never-rendered (age None) first, then stalest first
            e["_age"] = -1 if not hit or hit[0] is None else hit[0]
            to_render.append(e)

    to_render.sort(key=lambda e: (0 if e["_age"] == -1 else 1, -e["_age"]))
    overflow = to_render[CAP:]
    to_render = to_render[:CAP]
    for e in to_render:
        e.pop("_age", None)
    # overflow URLs still count as rank observations (only if we know their final_url,
    # i.e. they exist in the corpus — never-seen overflow waits for a future slice)
    dropped = 0
    for e in overflow:
        e.pop("_age", None)
        hit = seen.get(e["url"])
        if hit:
            rank_only.append(rank_row(e, hit[1]))
        else:
            dropped += 1

    json.dump(to_render, open(render_f, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.dump(rank_only, open(rank_f, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"batch {len(batch)} rows -> render {len(to_render)} (cap {CAP}, ttl {TTL_DAYS}d) "
          f"| rank-only {len(rank_only)} | overflow waiting for a future slice {dropped}")
    print(f"WROTE {render_f} + {rank_f}")


if __name__ == "__main__":
    main()
