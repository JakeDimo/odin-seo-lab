"""GSC click-behaviour read (COEC) — the one within-page-1 lever competitor-scraping can't
see. For OUR OWN pages, Search Console gives actual CTR + position, so we can compute
whether a page/query earns MORE or FEWER clicks than its rank slot deserves. Under-clicking
a good slot = a title/snippet opportunity (and, per NavBoost, a page that out-clicks its
slot is the kind Google promotes).

  COEC = actual CTR / expected CTR for the average position  (<1 = under-clicking)
  click_gap = impressions * (expected - actual CTR)          (est. clicks left on the table)

CAVEAT: local-service SERPs (plumbers, dentists) carry a Google MAP PACK + ads that eat
organic clicks, so ABSOLUTE organic CTR sits below the generic curve. Treat COEC as a
RELATIVE ranking of opportunities (who under-clicks most vs peers at the same position),
not a literal missed-click count.

Reads the Make GSC tool's bundle-array JSON (dimension = page OR query).
Run: uv run gsc_coec.py <export.json> [brand_token]
"""
import sys, json, os

# Approx organic CTR by position (AWR/Backlinko blended). Interpolated for decimals.
CTR = {1: .270, 2: .140, 3: .100, 4: .073, 5: .055, 6: .044, 7: .036, 8: .030, 9: .026,
       10: .023, 11: .020, 12: .018, 13: .016, 14: .014, 15: .013, 16: .012, 17: .011,
       18: .010, 19: .009, 20: .008}


def expected(pos):
    if pos < 1:
        pos = 1.0
    lo = int(pos)
    if lo >= 20:
        return 0.006
    clo, chi = CTR.get(lo, 0.006), CTR.get(lo + 1, 0.005)
    return clo + (chi - clo) * (pos - lo)


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    arr = d.get("tool_output", {}).get("array", d if isinstance(d, list) else [])
    rows = []
    for x in arr:
        b = x.get("bundle", x)
        rows.append({"key": b.get("query") or b.get("page") or "",
                     "clicks": b.get("clicks", 0) or 0, "impr": b.get("impressions", 0) or 0,
                     "ctr": b.get("ctr", 0) or 0, "pos": b.get("position", 0) or 0})
    return rows


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    path = sys.argv[1]
    brand = sys.argv[2].lower() if len(sys.argv) > 2 else None
    rows = load(path)
    for r in rows:
        r["exp"] = expected(r["pos"])
        r["coec"] = (r["ctr"] / r["exp"]) if r["exp"] > 0 else None
        r["gap"] = r["impr"] * (r["exp"] - r["ctr"])
        r["brand"] = bool(brand and brand in r["key"].lower())

    opp = [r for r in rows if 2 <= r["pos"] <= 20 and r["impr"] >= 100 and not r["brand"]]
    opp.sort(key=lambda r: r["gap"], reverse=True)
    over = [r for r in rows if r["impr"] >= 100 and r["coec"] and r["coec"] >= 1.2
            and 2 <= r["pos"] <= 20 and not r["brand"]]
    over.sort(key=lambda r: r["coec"], reverse=True)

    tot_gap = sum(max(0, r["gap"]) for r in opp)
    med_coec = sorted(r["coec"] for r in opp if r["coec"] is not None)
    med = med_coec[len(med_coec) // 2] if med_coec else None
    print(f"# GSC click-behaviour (COEC) — {os.path.basename(path)}")
    print(f"\nNon-brand entries at pos 2-20 with >=100 impressions: {len(opp)} "
          f"(median COEC {med:.2f} — {'under' if (med is not None and med < 1) else 'over'}-clicking their slots)")
    print(f"Est. clicks left on the table (relative): ~{round(tot_gap)}\n")
    print("## Biggest click opportunities (good rank, under-clicking the slot → fix title/snippet)")
    print("| key | pos | impr | actual CTR | expected | COEC | est. missed clicks |")
    print("|---|---|---|---|---|---|---|")
    for r in opp[:15]:
        print(f"| {r['key'][:58]} | {r['pos']:.1f} | {r['impr']} | {r['ctr']*100:.1f}% | "
              f"{r['exp']*100:.1f}% | {r['coec']:.2f} | {round(max(0, r['gap']))} |")
    print("\n## Over-performers (beating their slot — the title/snippet pattern that works)")
    print("| key | pos | impr | actual CTR | expected | COEC |")
    print("|---|---|---|---|---|---|")
    for r in over[:8]:
        print(f"| {r['key'][:58]} | {r['pos']:.1f} | {r['impr']} | {r['ctr']*100:.1f}% | "
              f"{r['exp']*100:.1f}% | {r['coec']:.2f} |")


if __name__ == "__main__":
    main()
