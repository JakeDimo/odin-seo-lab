"""DataForSEO SERP step — pull AU top rankers (+ a control set of losers) for a keyword,
formatted for the render scraper.

Credentials are read at runtime from env DATAFORSEO_B64, else from the auth-memory file
(outside the vault). The secret is NEVER stored in this script (this file lives in the
git-synced vault).

Run:
  uv run --with requests serp_au.py "plumber gold coast" data/serp_gc_plumber.json data/urls_grade.json
Optional 4th arg = location_name (default "Australia").
"""
import sys, os, json, re, time
import requests

AUTH_FILE = (r"C:\Users\jaked\.claude\projects"
             r"\C--Users-jaked-Documents-Obsidian-obsidian-vault\memory\reference_dataforseo_api.md")


def get_auth():
    b64 = os.environ.get("DATAFORSEO_B64")
    if b64:
        return b64
    try:
        with open(AUTH_FILE, encoding="utf-8") as f:
            m = re.search(r"Basic ([A-Za-z0-9+/=]+)", f.read())
            if m:
                return m.group(1)
    except Exception:
        pass
    raise SystemExit("No DataForSEO auth (set $env:DATAFORSEO_B64 or check the auth file).")


def main():
    keyword, serp_out, urls_out = sys.argv[1], sys.argv[2], sys.argv[3]
    location = sys.argv[4] if len(sys.argv) > 4 else "Australia"
    auth = get_auth()
    body = [{"keyword": keyword, "location_name": location, "language_code": "en",
             "device": "desktop", "depth": 50}]
    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json",
               "Accept": "application/json",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    data = None
    for attempt in range(5):  # endpoint can drop the connection intermittently; retry
        try:
            r = requests.post(url, headers=headers, json=body, timeout=90)
            data = r.json()
            break
        except Exception as e:
            if attempt == 4:
                raise SystemExit(f"SERP request failed after 5 retries: {e}\n"
                                 "If this persists locally, run from the cloud runner (clean egress).")
            time.sleep(3)
    if data.get("status_code") != 20000:
        raise SystemExit(f"DataForSEO API error {data.get('status_code')}: {data.get('status_message')}")
    task = (data.get("tasks") or [{}])[0]
    if task.get("status_code") != 20000:
        raise SystemExit(f"DataForSEO task error {task.get('status_code')}: {task.get('status_message')}")
    items = []
    try:
        result = data["tasks"][0]["result"][0]
        for it in result.get("items", []):
            if it.get("type") == "organic" and it.get("url"):
                items.append({"rank": it.get("rank_group"), "url": it["url"],
                              "domain": it.get("domain"), "title": it.get("title")})
    except Exception as e:
        raise SystemExit(f"SERP parse error: {e}")

    winners = [x for x in items if x["rank"] and x["rank"] <= 10][:10]
    losers = [x for x in items if x["rank"] and 21 <= x["rank"] <= 45][:10]
    with open(serp_out, "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "location": location, "cost": data.get("cost"),
                   "items": items, "winners": winners, "losers": losers}, f, indent=2, ensure_ascii=False)
    urls = [{"client": f"win|r{x['rank']}|{keyword}", "url": x["url"]} for x in winners]
    urls += [{"client": f"lose|r{x['rank']}|{keyword}", "url": x["url"]} for x in losers]
    with open(urls_out, "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2, ensure_ascii=False)

    print(f"keyword='{keyword}'  location='{location}'  cost=${data.get('cost')}  organic={len(items)}")
    print(f"winners={len(winners)}  losers={len(losers)}")
    for x in winners:
        print(f"  WIN  r{x['rank']:>2}  {x['domain']}")
    for x in losers:
        print(f"  LOSE r{x['rank']:>2}  {x['domain']}")
    print(f"WROTE {serp_out} + {urls_out}")


if __name__ == "__main__":
    main()
