"""Phase 1 scraper — RENDER path: PARALLEL + CHUNKED + crash-resilient.

Renders JS and parses on-page fields via seo_parse, running RENDER_CONCURRENCY pages at
once. For large batches (the corpus is ~1000 URLs/slice now) it renders in CHUNKS and
relaunches the browser between chunks, so one crashed page or an out-of-memory browser
can't take down the whole run (the classic CI "Target page/context/browser has been
closed"). Chromium launches with --disable-dev-shm-usage because GitHub runners have a
tiny /dev/shm, which is what crashes the browser at volume.

Screenshots OFF by default; rendered HTML is not saved (the corpus keeps parsed fields).

Setup once: uv run --with playwright python -m playwright install chromium
Run: uv run --with playwright --with beautifulsoup4 scrape_render.py data/urls_batch.json data/results_batch_render.json
"""
import sys, os, json, asyncio
import seo_parse
from playwright.async_api import async_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CONC = int(os.environ.get("RENDER_CONCURRENCY", "8"))
CHUNK = int(os.environ.get("RENDER_CHUNK", "150"))
# --disable-dev-shm-usage is the real fix for CI browser crashes (small /dev/shm).
LAUNCH_ARGS = ["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu"]


async def render_one(context, entry, sem, results):
    url = entry["url"]
    label = entry.get("client") or entry.get("keyword") or ""
    rec = {"label": label, "url": url, "status": None}
    for k in ("serp_title", "serp_snippet", "serp_rank_absolute", "is_featured_snippet", "serp_features"):
        if k in entry:
            rec[k] = entry[k]   # carry the SERP-side fields we already paid for
    async with sem:
        page = None
        try:
            page = await context.new_page()
            for attempt in range(2):
                try:
                    resp = await page.goto(url, wait_until="domcontentloaded", timeout=18000)
                    await page.wait_for_timeout(2200)  # let JS / any challenge resolve
                    html = await page.content()
                    fields = seo_parse.extract_fields(html, page.url, label)
                    rec["status"] = resp.status if resp else None
                    rec["final_url"] = page.url
                    rec.update(fields)
                    if rec["status"] and rec["status"] < 400 and fields.get("word_count", 0) >= 30:
                        rec.pop("error", None)
                        break
                except Exception as e:
                    rec["error"] = str(e)[:160]
                if attempt == 0:
                    try:
                        await page.wait_for_timeout(1500)  # back off, then retry once
                    except Exception:
                        break
        except Exception as e:                 # new_page / browser crash — never propagate
            rec["error"] = ("launch:" + str(e))[:160]
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass
    results.append(rec)


async def render_chunk(p, entries, results):
    browser = await p.chromium.launch(args=LAUNCH_ARGS)
    try:
        context = await browser.new_context(user_agent=UA, viewport={"width": 1366, "height": 900})
        sem = asyncio.Semaphore(CONC)
        # return_exceptions=True: a task that raises resolves to an exception object instead
        # of propagating and aborting the whole batch.
        await asyncio.gather(*[render_one(context, e, sem, results) for e in entries],
                             return_exceptions=True)
        try:
            await context.close()
        except Exception:
            pass
    finally:
        try:
            await browser.close()
        except Exception:
            pass


async def main_async(src, dst):
    entries = json.load(open(src, encoding="utf-8"))
    results = []
    total_chunks = (len(entries) + CHUNK - 1) // CHUNK
    async with async_playwright() as p:
        for i in range(0, len(entries), CHUNK):
            chunk = entries[i:i + CHUNK]
            try:
                await render_chunk(p, chunk, results)
            except Exception as e:
                print(f"  ! chunk {i // CHUNK + 1} crashed: {str(e)[:120]} (continuing)")
            print(f"  chunk {i // CHUNK + 1}/{total_chunks} done; {len(results)} rendered so far")
    json.dump(results, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    ok = sum(1 for r in results if r.get("status") == 200)
    print(f"rendered {ok}/{len(results)} OK (concurrency {CONC}, chunk {CHUNK}) -> {dst}")


def main():
    asyncio.run(main_async(sys.argv[1], sys.argv[2]))


if __name__ == "__main__":
    main()
