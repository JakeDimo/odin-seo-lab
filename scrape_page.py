"""Phase 1 scraper — FAST path (requests, no JS rendering) + raw-HTML storage.

Good for server-rendered sites (WordPress/Webflow). For JS-rendered SPAs
(Lovable, React) use scrape_render.py instead. Parsing is shared via seo_parse.py
so both scrapers always extract the same fields.

Run:
  uv run --with requests --with beautifulsoup4 scrape_page.py data/urls_clients.json data/results_v2.json
"""
import sys, os, json, hashlib
import requests
import seo_parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}
HTML_DIR = "html"


def analyze(entry, out_dir):
    label = entry.get("client") or entry.get("keyword") or ""
    out = {"label": label, "url": entry["url"]}
    try:
        r = requests.get(entry["url"], headers=HEADERS, timeout=25, allow_redirects=True)
        out["status"], out["final_url"], html = r.status_code, r.url, r.text
    except Exception as e:
        out["status"], out["error"] = None, str(e)[:200]
        return out
    os.makedirs(os.path.join(out_dir, HTML_DIR), exist_ok=True)
    fname = hashlib.md5(out["final_url"].encode()).hexdigest()[:12] + ".html"
    with open(os.path.join(out_dir, HTML_DIR, fname), "w", encoding="utf-8") as f:
        f.write(html)
    out["raw_html"] = f"{HTML_DIR}/{fname}"
    out["html_bytes"] = len(html.encode("utf-8"))
    out.update(seo_parse.extract_fields(html, out["final_url"], label))
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    out_dir = os.path.dirname(os.path.abspath(dst))
    with open(src, encoding="utf-8") as f:
        entries = json.load(f)
    results = [analyze(e, out_dir) for e in entries]
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    for r in results:
        if r.get("status") != 200:
            print(f"[{r.get('status')}] {r['label']}  {r['url']}  {r.get('error', '')}")
            continue
        print(f"\n[200] {r['label']}  {r['final_url']}")
        print(f"   title({r['title_len']}): {r['title'][:90]}")
        print(f"   h1({r['h1_count']}): {' | '.join(r['h1'])[:90]}")
        print(f"   words={r['word_count']}  flesch={r['readability_flesch']}  h2={r['h2_count']}  "
              f"int_links={r['internal_links']}  ext_links={r['external_links']}  alt_cov={r['alt_coverage']}")
        print(f"   CTAs={r['cta_count']}  forms={r['form_count']}  schema: {', '.join(r['schema_types']) or 'none'}")
        print(f"   aggregateRating={r['schema_aggregate_rating']}  fake_rating_flag={r['flag_fake_rating']}  raw_html -> {r['raw_html']}")
    ok = sum(1 for r in results if r.get("status") == 200)
    print(f"\nWROTE {dst}  ({ok}/{len(results)} fetched OK; raw HTML in {HTML_DIR}/)")


if __name__ == "__main__":
    main()
