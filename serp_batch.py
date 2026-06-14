"""Batch SERP step: loop keywords.json, pull AU winners + losers for each keyword,
dedupe by URL across the whole batch, write ONE combined urls file for the render
scraper. Label format: group|niche|keyword|rN  (group = win/lose).

Creds from env DATAFORSEO_B64, else the auth-memory file. Cloud egress handles the POST.

Run: uv run --with requests serp_batch.py keywords.json data/urls_batch.json
"""
import sys, os, json, re, time
import requests

AUTH_FILE = (r"C:\Users\jaked\.claude\projects"
             r"\C--Users-jaked-Documents-Obsidian-obsidian-vault\memory\reference_dataforseo_api.md")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def get_auth():
    b64 = os.environ.get("DATAFORSEO_B64")
    if b64:
        return b64
    try:
        with open(AUTH_FILE, encoding="utf-8") as f:
            m = re.search(r"Basic ([A-Za-z0-9+/=]{20,})", f.read())
            if m:
                return m.group(1)
    except Exception:
        pass
    raise SystemExit("No DataForSEO auth (set DATAFORSEO_B64).")


def fetch_serp(keyword, location, auth):
    body = [{"keyword": keyword, "location_name": location, "language_code": "en",
             "device": "desktop", "depth": 50}]
    hdr = {"Authorization": f"Basic {auth}", "Content-Type": "application/json",
           "Accept": "application/json", "User-Agent": UA}
    # Auth/account errors are fatal (no point retrying the whole batch); everything
    # else (transient 40502 "POST Data Is Empty", rate limits, network) is retried,
    # then the keyword is SKIPPED rather than killing the run.
    FATAL = {40100, 40101, 40102, 40103, 40104, 40200}
    for attempt in range(5):
        try:
            r = requests.post("https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
                              headers=hdr, json=body, timeout=90)
            d = r.json()
            sc = d.get("status_code")
            if sc in FATAL:
                raise SystemExit(f"FATAL auth/account error {sc}: {d.get('status_message')}")
            if sc != 20000:
                raise RuntimeError(f"api {sc}: {d.get('status_message')}")
            task = (d.get("tasks") or [{}])[0]
            if task.get("status_code") != 20000:
                raise RuntimeError(f"task {task.get('status_code')}: {task.get('status_message')}")
            res = task.get("result") or []
            return (res[0].get("items", []) if res else []), float(d.get("cost") or 0)
        except SystemExit:
            raise
        except Exception as e:
            if attempt == 4:
                print(f"  ! SKIP '{keyword}' after 5 tries: {e}")
                return [], 0.0
            time.sleep(3)


def main():
    kw_file, out_file = sys.argv[1], sys.argv[2]
    auth = get_auth()
    queue = json.load(open(kw_file, encoding="utf-8"))
    if len(sys.argv) > 4:  # rotation: process keyword i where i % slices == idx
        slices, idx = int(sys.argv[3]), int(sys.argv[4])
        queue = [q for i, q in enumerate(queue) if i % slices == idx]
        print(f"slice {idx}/{slices}: {len(queue)} keywords this run")
    # SERP features we record per keyword (returned in the call we already pay for).
    FEATURES = {"featured_snippet", "people_also_ask", "local_pack", "ai_overview",
                "knowledge_graph", "map", "related_searches", "shopping", "video",
                "people_also_search", "faq", "discussions_and_forums", "twitter", "images"}
    urls, total = [], 0.0
    # NO cross-keyword dedup: we keep every (keyword, url, rank) pair so the keyword->URL
    # graph (breadth) is preserved. A URL ranking for many keywords gets many rows; the
    # render step is what bears the cost, so this is free SERP data we'd otherwise discard.
    for q in queue:
        kw, niche, loc = q["keyword"], q.get("niche", "general"), q.get("location", "Australia")
        items, cost = fetch_serp(kw, loc, auth)
        total += cost
        feats = sorted({it.get("type") for it in items if it.get("type") in FEATURES})
        org = [it for it in items if it.get("type") == "organic" and it.get("url") and it.get("rank_group")]
        winners = [x for x in org if x["rank_group"] <= 10][:10]
        near = [x for x in org if 11 <= x["rank_group"] <= 20][:5]   # page-2 near-miss cohort
        losers = [x for x in org if 21 <= x["rank_group"] <= 45][:6]
        n = 0
        for grp, lst in (("win", winners), ("near", near), ("lose", losers)):
            for x in lst:
                urls.append({"client": f"{grp}|{niche}|{kw}|r{x['rank_group']}", "url": x["url"],
                             "serp_title": x.get("title"), "serp_snippet": x.get("description"),
                             "serp_rank_absolute": x.get("rank_absolute"),
                             "is_featured_snippet": bool(x.get("is_featured_snippet")),
                             "serp_features": feats})
                n += 1
        print(f"{kw} ({niche}): {len(winners)}w/{len(near)}n/{len(losers)}l (+{n} rows)  feats={feats}  cost=${cost}")
    json.dump(urls, open(out_file, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nTOTAL {len(urls)} ranking rows across {len(queue)} keywords. SERP cost ~${round(total, 4)}")
    print(f"WROTE {out_file}")


if __name__ == "__main__":
    main()
