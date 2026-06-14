"""Enrich render results with DataForSEO PAID signals via cheap BULK endpoints:
  - referring domains + domain rank  (backlinks, DOMAIN-level — the authority granularity)
  - estimated organic traffic        (Labs, PAGE-level — keyed by the exact ranking URL,
                                       so a giant domain ranking poorly no longer inflates it)
Merges into the render JSON in place. Degrades gracefully and SELF-DIAGNOSES: any task
error is logged with DataForSEO's own status message, so we learn exactly why (e.g. a
backlinks access/funds gate) instead of silently crashing. Creds from env / auth file.

Run: uv run --with requests enrich_dataforseo.py data/results_batch_render.json
"""
import sys, os, json, re
from urllib.parse import urlparse
import requests

AUTH_FILE = (r"C:\Users\jaked\.claude\projects"
             r"\C--Users-jaked-Documents-Obsidian-obsidian-vault\memory\reference_dataforseo_api.md")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CAP = 1000  # max targets per bulk call (DataForSEO bulk endpoints handle up to 1000)


def get_auth():
    b = os.environ.get("DATAFORSEO_B64")
    if b:
        return b
    try:
        with open(AUTH_FILE, encoding="utf-8") as f:
            m = re.search(r"Basic ([A-Za-z0-9+/=]{20,})", f.read())
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def post(path, body, hdr):
    r = requests.post(f"https://api.dataforseo.com/v3/{path}", headers=hdr, json=body, timeout=120)
    return r.json()


def items_of(resp):
    task = (resp.get("tasks") or [{}])[0]
    if task.get("status_code") != 20000:
        raise RuntimeError(f"task {task.get('status_code')}: {task.get('status_message')}")
    res = task.get("result") or []
    return ((res[0] or {}).get("items") or []) if res else []


def main():
    src = sys.argv[1]
    recs = json.load(open(src, encoding="utf-8"))
    a = get_auth()
    if not a:
        print("no auth; skipping enrichment")
        return
    hdr = {"Authorization": f"Basic {a}", "Content-Type": "application/json",
           "Accept": "application/json", "User-Agent": UA}

    domains, urls = [], []
    for r in recs:
        u = r.get("final_url") or r.get("url")
        if not u:
            continue
        if u not in urls:
            urls.append(u)
        d = urlparse(u).netloc.replace("www.", "")
        if d and d not in domains:
            domains.append(d)
    domains, urls = domains[:CAP], urls[:CAP]
    print(f"backlinks targets: {len(domains)} domains | traffic targets: {len(urls)} page URLs")

    ref, rank, etv, rkw, posd = {}, {}, {}, {}, {}
    try:
        for it in items_of(post("backlinks/bulk_referring_domains/live", [{"targets": domains}], hdr)):
            ref[it.get("target")] = it.get("referring_domains")
    except Exception as e:
        print("referring_domains failed:", str(e)[:180])
    try:
        for it in items_of(post("backlinks/bulk_ranks/live", [{"targets": domains}], hdr)):
            rank[it.get("target")] = it.get("rank")
    except Exception as e:
        print("bulk_ranks failed:", str(e)[:180])
    try:
        body = [{"targets": urls, "location_name": "Australia", "language_code": "en"}]
        for it in items_of(post("dataforseo_labs/google/bulk_traffic_estimation/live", body, hdr)):
            m = (it.get("metrics") or {}).get("organic") or {}
            tgt = it.get("target")
            etv[tgt] = m.get("etv")
            rkw[tgt] = m.get("count")  # how many keywords the target ranks for
            posd[tgt] = {"pos_1": m.get("pos_1"), "pos_2_3": m.get("pos_2_3"),
                         "pos_4_10": m.get("pos_4_10"), "pos_11_20": m.get("pos_11_20")}
    except Exception as e:
        print("traffic_estimation failed:", str(e)[:180])

    for r in recs:
        u = r.get("final_url") or r.get("url")
        if not u:
            continue
        dn = urlparse(u).netloc.replace("www.", "")
        r["referring_domains"] = ref.get(dn)
        r["domain_rank"] = rank.get(dn)
        r["etv"] = etv.get(u)  # page-level (keyed by exact URL)
        r["ranked_keywords"] = rkw.get(u)  # how many keywords this page ranks for
        pd = posd.get(u) or {}
        r["kw_pos_1"] = pd.get("pos_1")        # of those, how many it ranks #1 for
        r["kw_pos_2_3"] = pd.get("pos_2_3")
        r["kw_pos_4_10"] = pd.get("pos_4_10")
        r["kw_pos_11_20"] = pd.get("pos_11_20")

    json.dump(recs, open(src, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"enriched: referring_domains={len(ref)} ranks={len(rank)} page_traffic={len(etv)} ranked_kw={len(rkw)}")


if __name__ == "__main__":
    main()
