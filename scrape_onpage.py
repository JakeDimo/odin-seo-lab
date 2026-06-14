"""
Phase 1 seed: on-page SEO fact extractor.
Reads a list of {keyword, url} from argv[1], fetches each page, pulls the
on-page signals we care about, writes JSON to argv[2], prints a summary.

Run (PC):
  uv run --with requests --with beautifulsoup4 scrape_onpage.py data/urls.json data/onpage_results.json

This is deliberately simple. The real Phase 1 swaps requests for Crawl4AI
(browser rendering, handles JS sites) and SQLite for the JSON output.
"""
import sys, json
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def word_count(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.extract()
    return len(soup.get_text(separator=" ").split())


def schema_types(soup):
    types = set()
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = s.string or s.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if not isinstance(it, dict):
                continue
            nodes = it.get("@graph") if isinstance(it.get("@graph"), list) else [it]
            for n in nodes:
                if isinstance(n, dict):
                    t = n.get("@type")
                    if isinstance(t, list):
                        types.update(t)
                    elif isinstance(t, str):
                        types.add(t)
    return sorted(types)


def analyze(entry):
    kw = entry["keyword"].lower()
    out = {"keyword": entry["keyword"], "url": entry["url"]}
    try:
        r = requests.get(entry["url"], headers=HEADERS, timeout=20, allow_redirects=True)
        out["status"], out["final_url"], html = r.status_code, r.url, r.text
    except Exception as e:
        out["status"], out["error"] = None, str(e)[:200]
        return out
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    md = soup.find("meta", attrs={"name": "description"})
    metadesc = (md.get("content") or "").strip() if md else ""
    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    gen = soup.find("meta", attrs={"name": "generator"})
    out.update({
        "title": title, "title_len": len(title),
        "meta_description": metadesc, "metadesc_len": len(metadesc),
        "h1": h1s, "h1_count": len(h1s),
        "h2_count": len(soup.find_all("h2")), "h3_count": len(soup.find_all("h3")),
        "word_count": word_count(html),
        "schema_types": schema_types(soup),
        "generator": (gen.get("content") if gen else "") or "",
        "has_canonical": bool(soup.find("link", attrs={"rel": "canonical"})),
        "title_has_kw": kw in title.lower(),
        "title_has_agency": "agency" in title.lower(),
        "h1_has_kw": any(kw in h.lower() for h in h1s),
    })
    return out


def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        entries = json.load(f)
    results = [analyze(e) for e in entries]
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    for r in results:
        if r.get("status") != 200:
            print(f"[{r.get('status')}] {r['url']}  {r.get('error', '')}")
            continue
        print(f"[200] {r['final_url']}")
        print(f"   title({r['title_len']}): {r['title'][:95]}")
        print(f"   h1({r['h1_count']}): {' | '.join(r['h1'])[:95]}")
        print(f"   metadesc={r['metadesc_len']}  h2={r['h2_count']}  h3={r['h3_count']}  words={r['word_count']}")
        print(f"   schema: {', '.join(r['schema_types']) or 'none'}   platform: {r['generator'][:30] or '?'}")
        print(f"   kw_in_title={r['title_has_kw']}  agency_in_title={r['title_has_agency']}  kw_in_h1={r['h1_has_kw']}")
    ok = sum(1 for r in results if r.get("status") == 200)
    print(f"\nWROTE {sys.argv[2]}  ({ok}/{len(results)} fetched OK)")


if __name__ == "__main__":
    main()
