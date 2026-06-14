"""Generate keywords.json by expanding service templates x AU cities per niche.
Easy to widen later — just add services or cities. Run: uv run gen_keywords.py keywords.json
"""
import sys, json

CITIES = ["gold coast", "brisbane", "sydney", "melbourne", "perth", "adelaide",
          "canberra", "newcastle", "sunshine coast", "wollongong", "geelong", "hobart",
          "townsville", "cairns", "darwin", "toowoomba", "ballarat", "bendigo", "launceston",
          "mackay", "rockhampton", "bundaberg", "hervey bay", "wagga wagga", "coffs harbour",
          "port macquarie", "tamworth", "dubbo", "orange", "albury"]
PLUMBING = ["plumber", "emergency plumber", "blocked drain", "hot water repair",
            "gas fitter", "leaking tap repair", "burst pipe repair"]
WINDOW = ["window cleaning", "window cleaner", "commercial window cleaning",
          "gutter cleaning", "pressure washing", "solar panel cleaning"]
DENTAL = ["dentist", "emergency dentist", "dental implants", "teeth whitening",
          "invisalign", "root canal"]
ELECTRICIAN = ["electrician", "emergency electrician", "ceiling fan installation",
               "switchboard upgrade", "ev charger installation"]
HVAC = ["air conditioning installation", "air conditioning service", "ducted heating repair",
        "split system installation", "heating and cooling"]
ROOFING = ["roof repairs", "roof restoration", "metal roofing", "roof replacement",
           "gutter replacement"]
PEST_CONTROL = ["pest control", "termite inspection", "termite treatment", "cockroach control"]
LOCKSMITH = ["locksmith", "emergency locksmith", "car locksmith", "lock change"]
CITY_NICHES = {"plumbing": PLUMBING, "window-cleaning": WINDOW,
               "dental": DENTAL, "electrician": ELECTRICIAN, "hvac": HVAC,
               "roofing": ROOFING, "pest-control": PEST_CONTROL, "locksmith": LOCKSMITH}
THERAPY = [  # national (MeHelp) — no city expansion
    "online psychologist australia", "bulk billed psychologist online",
    "telehealth psychologist australia", "online therapy australia",
    "online counselling australia", "medicare online psychologist",
    "best online therapy australia", "online psychologist near me",
    "telehealth counselling australia", "online mental health support australia",
    "affordable online psychologist australia", "online psychiatrist australia",
]
SOLAR = [  # national (ShineHub vertical) — no city expansion
    "solar panel installation australia", "solar rebate australia",
    "home battery storage australia", "solar quotes australia",
    "best solar panels australia", "solar system cost australia",
]
NATIONAL_NICHES = {"online-therapy": THERAPY, "solar": SOLAR}

# Cluster test bed: tight modifier variations around a few head terms x cities, so the
# ranking-breadth measure can see a page OWNING a related cluster (Jake's hypothesis + the
# "combine templates to broaden coverage" pattern from the SEO-prospector video, see
# wiki/sources/youtube-arvo-claude-seo-prospector-2026-05-25.md). New phrasings only — the
# plain "{head} {city}" already exists in the grid above, so we don't pay to scan it twice.
CLUSTER_HEADS = {"plumbing": "plumber", "window-cleaning": "window cleaning",
                 "dental": "dentist", "electrician": "electrician", "hvac": "air conditioning",
                 "roofing": "roof repairs", "pest-control": "pest control", "locksmith": "locksmith"}
CLUSTER_CITIES = ["sydney", "melbourne", "brisbane", "perth", "adelaide", "gold coast",
                  "canberra", "newcastle"]
CLUSTER_TEMPLATES = ["{c} {h}", "best {h} {c}", "local {h} {c}", "cheap {h} {c}",
                     "affordable {h} {c}", "{h} {c} cost", "best {h} in {c}"]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "keywords.json"
    kws = []
    for niche, services in CITY_NICHES.items():
        for s in services:
            for c in CITIES:
                kws.append({"niche": niche, "keyword": f"{s} {c}", "location": "Australia"})
    for niche, terms in NATIONAL_NICHES.items():
        for k in terms:
            kws.append({"niche": niche, "keyword": k, "location": "Australia"})
    for niche, h in CLUSTER_HEADS.items():
        for c in CLUSTER_CITIES:
            for t in CLUSTER_TEMPLATES:
                kws.append({"niche": niche, "keyword": t.format(h=h, c=c), "location": "Australia"})
    seen, uniq = set(), []          # never pay to scan the same keyword twice
    for k in kws:
        if k["keyword"] not in seen:
            seen.add(k["keyword"])
            uniq.append(k)
    kws = uniq
    json.dump(kws, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    by = {}
    for k in kws:
        by[k["niche"]] = by.get(k["niche"], 0) + 1
    print(f"wrote {len(kws)} keywords -> {out}  ({by})")


if __name__ == "__main__":
    main()
