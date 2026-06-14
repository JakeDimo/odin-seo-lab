"""Backfill the new within-page-1 signals onto the EXISTING corpus, with no SERP cost.

We already have every URL in the corpus; the new signals (page_type, freshness,
title click-score, query position, E-E-A-T, structure) are pure HTML reads. So we just
re-render the pages and MERGE the fresh signal fields into the existing rows, preserving
their enrichment (etv, referring_domains, backlinks, speed). Two modes:

  build <corpus.jsonl> <out_urls.json> [limit]            -> url list for scrape_render
  merge <corpus.jsonl> <render_results.json> <shard_dir>  -> write a merged shard

The merged rows get today's run_date so they win the grader's latest-per-page dedupe.
Run: uv run backfill_signals.py build  data/corpus.jsonl data/backfill_urls.json
     (then scrape_render on that file)
     uv run backfill_signals.py merge data/corpus.jsonl data/backfill_render.json data/corpus
"""
import sys, os, json, glob, datetime

NEW = ["page_type", "date_published", "date_modified", "page_age_days", "has_freshness_date",
       "title_ctr_score", "title_has_number", "title_has_bracket", "title_has_power", "title_len_ok",
       "query_in_title", "query_in_h1", "query_in_lead", "query_early_title",
       "has_author", "has_review_date", "eeat_score",
       "list_count", "table_count", "has_faq", "stat_count", "lead_para_words"]


def load(src):
    from corpus_load import load as _coalesce   # coalescing dedupe: nulls never clobber real values
    return _coalesce(src)


def build(corpus, out, limit=None):
    rows = load(corpus)
    seen, urls = set(), []
    for r in rows:
        u = r.get("final_url") or r.get("url")
        lab = r.get("label", "")
        if not u or (lab, u) in seen:
            continue
        seen.add((lab, u))
        urls.append({"client": lab, "url": u})
    if limit:
        urls = urls[:int(limit)]
    json.dump(urls, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"built {len(urls)} urls -> {out}")


def merge(corpus, render, shard_dir):
    rows = load(corpus)
    res = json.load(open(render, encoding="utf-8"))
    by_label = {x.get("label", ""): x for x in res if x.get("status") == 200 and "word_count" in x}
    os.makedirs(shard_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    shard = os.path.join(shard_dir, f"{stamp}-backfill.jsonl")
    today = datetime.date.today().isoformat()
    upd = 0
    with open(shard, "w", encoding="utf-8") as f:
        for r in rows:
            ren = by_label.get(r.get("label", ""))
            if not ren:
                continue                       # leave un-rendered pages on their existing row
            row = dict(r)                      # keep enrichment (etv/backlinks/speed)
            for k in NEW:
                if k in ren:
                    row[k] = ren[k]
            row["run_date"] = today            # win the latest-per-page dedupe
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            upd += 1
    print(f"merged {upd} updated rows -> {shard}  (of {len(rows)} unique pages)")


def main():
    mode = sys.argv[1]
    if mode == "build":
        build(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif mode == "merge":
        merge(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit("mode must be build|merge")


if __name__ == "__main__":
    main()
