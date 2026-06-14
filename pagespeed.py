"""Sample Core Web Vitals via Google PageSpeed Insights (free; keyless, or set
PAGESPEED_API_KEY for higher quota). Lighthouse is slow (~10-30s/URL), so we CAP +
throttle per run; speed data then accumulates across runs like everything else.
Merges lcp_ms / cls / tbt_ms / perf_score into the run results in place.
Best-effort — runs continue-on-error in the workflow so it never sinks a run.

Run: uv run --with requests pagespeed.py data/results_batch_render.json
"""
import sys, os, json, time
import requests

CAP = int(os.environ.get("PAGESPEED_CAP", "40"))  # pages measured per run (raise with a key)
ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def main():
    src = sys.argv[1]
    recs = json.load(open(src, encoding="utf-8"))
    key = os.environ.get("PAGESPEED_API_KEY", "")
    done = 0
    for r in recs:
        if done >= CAP:
            break
        u = r.get("final_url") or r.get("url")
        if not u or r.get("status") != 200 or r.get("perf_score") is not None:
            continue
        params = {"url": u, "strategy": "mobile", "category": "performance"}
        if key:
            params["key"] = key
        try:
            resp = requests.get(ENDPOINT, params=params, timeout=70).json()
            lh = resp.get("lighthouseResult", {}) or {}
            aud = lh.get("audits", {}) or {}
            r["lcp_ms"] = (aud.get("largest-contentful-paint") or {}).get("numericValue")
            r["cls"] = (aud.get("cumulative-layout-shift") or {}).get("numericValue")
            r["tbt_ms"] = (aud.get("total-blocking-time") or {}).get("numericValue")
            r["perf_score"] = ((lh.get("categories") or {}).get("performance") or {}).get("score")
            if r["perf_score"] is not None:
                done += 1
        except Exception as e:
            print("psi fail:", u, str(e)[:90])
        time.sleep(1)
    json.dump(recs, open(src, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"pagespeed: measured {done} pages this run (cap {CAP})")


if __name__ == "__main__":
    main()
