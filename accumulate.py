"""Append this run's results to the growing corpus as a PER-RUN SHARD file
(data/corpus/<timestamp>.jsonl). Sharding means concurrent runs / manual edits never
touch the same file, so the commit step can't hit a rebase conflict. The grader reads
the legacy corpus.jsonl + every shard and dedupes to the latest observation per page.

Two modes:
  render (default)    — full rows from scrape_render results; stamps rendered_date so
                        filter_render.py knows when a page was last rendered.
  --rank-only         — lightweight rank observations from filter_render.py (label +
                        SERP fields + any cache-enriched authority). No status filter
                        (they were never fetched); nulls stripped so shards stay lean.
                        The coalescing loader merges them into the rendered row;
                        the shard itself preserves rank history for analyze_movement.py.

Run: uv run accumulate.py data/results_batch_render.json data/corpus
     uv run accumulate.py data/rank_only.json data/corpus --rank-only
"""
import sys, os, json, datetime

KEEP = ["label", "status", "final_url", "url", "title", "h1", "schema_types",
        "schema_aggregate_rating", "has_canonical", "og_present", "form_count", "word_count",
        "readability_flesch", "h2_count", "internal_links", "external_links", "title_len",
        "cta_count", "alt_coverage", "etv", "ranked_keywords", "referring_domains",
        "domain_rank", "backlinks_total", "lcp_ms", "cls", "tbt_ms", "perf_score",
        # within-page-1 differentiator signals (see page-one-differentiators.md)
        "page_type", "date_published", "date_modified", "page_age_days", "has_freshness_date",
        "title_ctr_score", "title_has_number", "title_has_bracket", "title_has_power", "title_len_ok",
        "query_in_title", "query_in_h1", "query_in_lead", "query_early_title",
        "has_author", "has_review_date", "eeat_score",
        "list_count", "table_count", "has_faq", "stat_count", "lead_para_words",
        "kw_exact_count", "kw_density_per_1k", "kw_token_hits", "kw_in_h2",
        # SERP-side fields (free from the SERP call) + Labs ranking-position distribution
        "serp_title", "serp_snippet", "serp_rank_absolute", "is_featured_snippet", "serp_features",
        "kw_pos_1", "kw_pos_2_3", "kw_pos_4_10", "kw_pos_11_20",
        # link-context + rich-content + local-trust signals (added 2026-06-12)
        "main_internal_links", "nav_link_count", "h2_question_count", "has_video",
        "has_map_embed", "has_breadcrumb", "trust_mentions", "has_service_area"]

# rank-only observations carry just the SERP-side facts + identity + cached authority
RANK_KEEP = ["label", "url", "final_url", "serp_title", "serp_snippet", "serp_rank_absolute",
             "is_featured_snippet", "serp_features",
             "referring_domains", "domain_rank", "backlinks_total"]


def main():
    src, shard_dir = sys.argv[1], sys.argv[2]
    rank_only = "--rank-only" in sys.argv[3:]
    os.makedirs(shard_dir, exist_ok=True)
    recs = json.load(open(src, encoding="utf-8"))
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    suffix = "-rank" if rank_only else ""
    shard = os.path.join(shard_dir, f"{stamp}-{os.getpid()}{suffix}.jsonl")
    day = datetime.date.today().isoformat()
    n = 0
    with open(shard, "w", encoding="utf-8") as f:
        for r in recs:
            if rank_only:
                if not r.get("label") or not r.get("url"):
                    continue
                row = {k: r[k] for k in RANK_KEEP if r.get(k) is not None}
                row["observation"] = "rank"
            else:
                if r.get("status") != 200 or "word_count" not in r:
                    continue
                row = {k: r.get(k) for k in KEEP}
                row["rendered_date"] = day
            row["run_date"] = day
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    if n == 0:
        os.remove(shard)
        print("0 rows — no shard written")
        return
    print(f"wrote {n} {'rank-only ' if rank_only else ''}rows -> {shard}")


if __name__ == "__main__":
    main()
