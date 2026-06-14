"""Off-page authority from the Semrush Analytics API (backlinks_overview):
  referring_domains (domains_num) · domain_rank (Authority Score) · backlinks_total.

CACHED + THROTTLED so we pay Semrush ONCE per domain, ever. Authority barely moves week to
week, yet a plumber's domain ranks for dozens of our keywords — querying it every run is what
drained the whole Semrush unit allowance. So we persist a domain->authority cache as shards
under data/authority/ (committed, burst-safe like the corpus). Each run only queries domains
we've NEVER successfully fetched (capped + paced), writes the new ones to a shard, and enriches
rows from the merged cache. Failed/zero-unit fetches are NOT cached, so they retry when units
return.

Key from env SEMRUSH_API_KEY, else the auth-memory file.
Run:  uv run --with requests backlinks_semrush.py data/results_batch_render.json
Seed: uv run backlinks_semrush.py seed data/corpus.jsonl   (cache the authority we already have)
"""
import sys, os, json, re, time, glob, datetime
from urllib.parse import urlparse
import requests

AUTH_FILE = (r"C:\Users\jaked\.claude\projects"
             r"\C--Users-jaked-Documents-Obsidian-obsidian-vault\memory\reference_semrush_api_key.md")
ENDPOINT = "https://api.semrush.com/analytics/v1/"
CAP = int(os.environ.get("SEMRUSH_CAP", "400"))  # max NEW (uncached) domains queried per run


def get_key():
    k = os.environ.get("SEMRUSH_API_KEY")
    if k:
        return k
    try:
        with open(AUTH_FILE, encoding="utf-8") as f:
            m = re.search(r"\b([a-f0-9]{32})\b", f.read())
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def overview(domain, key):
    params = {"key": key, "type": "backlinks_overview", "target": domain,
              "target_type": "root_domain", "export_columns": "ascore,total,domains_num"}
    r = requests.get(ENDPOINT, params=params, timeout=40)
    t = (r.text or "").strip()
    if not t or t.upper().startswith("ERROR") or ";" not in t:
        return None
    lines = t.splitlines()
    if len(lines) < 2:
        return None
    d = dict(zip(lines[0].split(";"), lines[1].split(";")))

    def num(x):
        try:
            return int(float(x))
        except Exception:
            return None
    return {"ascore": num(d.get("ascore")), "total": num(d.get("total")), "domains_num": num(d.get("domains_num"))}


def dom(u):
    return urlparse(u or "").netloc.replace("www.", "")


def cache_dir(src):
    return os.path.join(os.path.dirname(src) or ".", "authority")


def load_cache(src):
    cache = {}
    for fp in sorted(glob.glob(os.path.join(cache_dir(src), "*.jsonl"))):
        try:
            for l in open(fp, encoding="utf-8"):
                if l.strip():
                    e = json.loads(l)
                    if e.get("domain"):
                        cache[e["domain"]] = e   # later shards refresh earlier
        except Exception:
            pass
    return cache


def write_shard(src, entries):
    if not entries:
        return None
    cd = cache_dir(src)
    os.makedirs(cd, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    shard = os.path.join(cd, f"{stamp}-{os.getpid()}.jsonl")
    with open(shard, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return shard


def load_rows(src):
    if src.endswith(".jsonl"):
        return [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    return json.load(open(src, encoding="utf-8"))


def seed(src):
    """One-time: cache the authority already sitting in the corpus, so we never re-pay for it."""
    try:
        from corpus_load import load as _coalesce   # all shards, coalesced, so we capture every value
        rows = _coalesce(src)
    except Exception:
        rows = load_rows(src)
    today = datetime.date.today().isoformat()
    seen, entries = set(), []
    for r in rows:
        if r.get("referring_domains") is None:
            continue
        d = dom(r.get("final_url") or r.get("url"))
        if not d or d in seen:
            continue
        seen.add(d)
        entries.append({"domain": d, "ascore": r.get("domain_rank"), "total": r.get("backlinks_total"),
                        "domains_num": r.get("referring_domains"), "fetched": today, "seeded": True})
    shard = write_shard(src, entries)
    print(f"seeded {len(entries)} domains into authority cache -> {shard}")


def main():
    if sys.argv[1] == "seed":
        return seed(sys.argv[2])
    src = sys.argv[1]
    rows = load_rows(src)
    key = get_key()
    if not key:
        print("no Semrush key; skipping")
        return
    cache = load_cache(src)

    batch = []
    for r in rows:
        d = dom(r.get("final_url") or r.get("url"))
        if d and d not in batch:
            batch.append(d)
    todo = [d for d in batch if d not in cache][:CAP]
    print(f"{len(batch)} domains in batch | {sum(1 for d in batch if d in cache)} already cached "
          f"({len(cache)} cached total) | querying {len(todo)} new (cap {CAP})")

    new_entries = []
    today = datetime.date.today().isoformat()
    for i, d in enumerate(todo):
        o = None
        try:
            o = overview(d, key)
        except Exception as e:
            print("  err", d, str(e)[:60])
        if o and o.get("domains_num") is not None:        # cache ONLY real successes
            e = {"domain": d, "ascore": o["ascore"], "total": o["total"],
                 "domains_num": o["domains_num"], "fetched": today}
            cache[d] = e
            new_entries.append(e)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(todo)} queried")
        time.sleep(0.2)
    shard = write_shard(src, new_entries)
    if shard:
        print(f"cached {len(new_entries)} new domains -> {shard}")

    hit = 0
    for r in rows:
        e = cache.get(dom(r.get("final_url") or r.get("url")))
        if e and e.get("domains_num") is not None:
            r["referring_domains"] = e["domains_num"]
            r["domain_rank"] = e["ascore"]
            r["backlinks_total"] = e["total"]
            hit += 1
    if src.endswith(".jsonl"):
        with open(src, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        json.dump(rows, open(src, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"rows enriched from cache: {hit}/{len(rows)}")


if __name__ == "__main__":
    main()
