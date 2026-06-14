"""THE RULEBOOK — auto-generated, self-updating every run.

Two layers, kept honest:
  1. AUDIT-VERIFIED verdicts (the authoritative truth) come from the six-skeptic adversarial
     audit (significance + page-type + per-niche controls). They are hard-coded here as VERIFIED
     and override the screen, because a quick median screen cannot replicate that rigour.
  2. For every OTHER factor, a conservative screen runs over the live corpus: authority-controlled
     gap + a significance gate for yes/no factors. It never auto-promotes to LEAD without
     significance; the most it says on its own is WATCH (a candidate the next audit should test).

Verdicts: LEAD (survives authority control + significant / audit-verified) · CONFOUND (vanishes
or reverses at equal authority) · WATCH (right direction, not yet significant — needs more data
or an audit) · GATE (flat; a floor not a lever). Nothing is a RULE until a controlled live test
moves a real page (see experiments.md). Update VERIFIED when a new audit lands.

Run: uv run rulebook.py data/corpus.jsonl grades/rulebook.md
"""
import sys
import re
import math
import statistics
from corpus_load import load

# Authoritative verdicts from the adversarial audits (findings-log.md, 663 -> 2,659 -> 23,626
# pages). These override the screen. Add the date the audit confirmed them.
VERIFIED = {
    "Internal links to the page": ("LEAD", "audit 2026-06-09: survives joint authority+homepage control (p=0.019)"),
    "Topical breadth (keywords the page ranks for)": ("LEAD", "audit 2026-06-09: holds in every authority band (+15 mid)"),
    "Title 40-60 chars (truncation-safe)": ("WATCH", "audit: borderline, shrank with more data"),
    "Query front-loaded in title": ("CONFOUND", "audit 2026-06-09: washed out at scale (p=0.073)"),
    "Exact query in title": ("CONFOUND", "audit 2026-06-09: homepage/brand-title artefact; +2.4pt on real pages"),
    "Word count / depth": ("CONFOUND", "audit 2026-06-09: washes out under authority+page-type double control"),
    "Freshness (page age, days)": ("CONFOUND", "audit 2026-06-09: near coin-flip; halves under authority control"),
    "Page speed (mobile LCP)": ("GATE", "audit: flat across positions; a pass/fail floor"),
}

# factor: (label, getter, kind, lower_is_better, what-to-do-if-real)
FACTORS = [
    ("Internal links to the page", lambda r: r.get("internal_links"), "num", False,
     "Add internal links pointing at the target page from elsewhere on the site."),
    ("Contextual (in-content) internal links", lambda r: r.get("main_internal_links"), "num", False,
     "Add internal links from inside the body content (not nav/footer) — the evidence says contextual links carry the value, not raw count."),
    ("Topical breadth (keywords the page ranks for)", lambda r: r.get("ranked_keywords"), "num", False,
     "Build out the related cluster so the page covers the whole topic, not one term."),
    ("Word count / depth", lambda r: r.get("word_count"), "num", False, "Longer content."),
    ("Freshness (page age, days)", lambda r: r.get("page_age_days"), "num", True, "Update the page more recently."),
    ("Lists (ul/ol)", lambda r: r.get("list_count"), "num", False, "Add structured lists."),
    ("Stat / $ density", lambda r: r.get("stat_count"), "num", False, "Add original figures/data."),
    ("E-E-A-T score", lambda r: r.get("eeat_score"), "num", False, "Add author + review dates."),
    ("Keyword density /1k", lambda r: r.get("kw_density_per_1k"), "num", False, "Mention the term more often."),
    ("Page speed (mobile LCP)", lambda r: r.get("lcp_ms"), "num", True, "Speed the page up."),
    ("Title 40-60 chars (truncation-safe)", lambda r: r.get("title_len_ok"), "bin", False,
     "Trim/expand the title into the 40-60 character band."),
    ("Exact query in title", lambda r: r.get("query_in_title"), "bin", False, "Put the exact query in the title."),
    ("Query front-loaded in title", lambda r: r.get("query_early_title"), "bin", False,
     "Move the query to the front of the title."),
    ("Query in lead paragraph", lambda r: r.get("query_in_lead"), "bin", False, "Use the query in the opening lines."),
    ("Has author / byline", lambda r: r.get("has_author"), "bin", False, "Add a visible author + bio."),
    ("Has FAQ schema", lambda r: r.get("has_faq"), "bin", False, "Add an FAQ block with schema."),
    ("Has freshness date", lambda r: r.get("has_freshness_date"), "bin", False, "Show a published/updated date."),
]


def rank_of(r):
    m = re.search(r"\|r(\d+)$", r.get("label", ""))
    return int(m.group(1)) if m else None


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return statistics.median(xs) if xs else None


def bin_stat(rows, getter):
    vals = [1 if getter(r) else 0 for r in rows if getter(r) is not None]
    n = len(vals)
    return (sum(vals) / n if n else None), n


def num_stat(rows, getter):
    vals = [getter(r) for r in rows if isinstance(getter(r), (int, float)) and not isinstance(getter(r), bool)]
    return (med(vals), len(vals))


def ztest(pa, na, pb, nb):
    if not (na and nb) or pa is None or pb is None:
        return 0.0
    p = (pa * na + pb * nb) / (na + nb)
    se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb)) if 0 < p < 1 else 0
    return (pa - pb) / se if se else 0.0


def classify(label, raw, mid, na, nb, kind, lb, za=None):
    if label in VERIFIED:
        return VERIFIED[label][0], "audit-verified"
    if raw is None or mid is None:
        return "NO DATA", "low"
    rg, mg = (-raw if lb else raw), (-mid if lb else mid)
    n = min(na, nb)
    if n < 25:
        return "WATCH", "low"
    if abs(mg) < 1e-9 or (rg > 0) != (mg > 0) or abs(mg) < 0.33 * abs(rg):
        return "CONFOUND", ("high" if n >= 80 else "medium")
    if kind == "bin":
        if za is not None and abs(za) >= 1.96:
            return "LEAD", ("high" if n >= 80 else "medium")
        return "WATCH", "low"          # right direction but not significant
    return "WATCH", "low"              # un-verified numeric: never auto-LEAD without a real test


def fmt(v, kind):
    if v is None:
        return "—"
    return f"{round(100*v)}%" if kind == "bin" else f"{round(v, 1)}"


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "grades/rulebook.md"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    recs = [r for r in load(src) if r.get("status") == 200 and "word_count" in r]
    for r in recs:
        r["__rank"] = rank_of(r)
    p1 = [r for r in recs if r.get("__rank") and 1 <= r["__rank"] <= 10]
    auth = sorted(r.get("referring_domains") for r in p1 if isinstance(r.get("referring_domains"), (int, float)))
    q1, q2 = (auth[len(auth)//3], auth[2*len(auth)//3]) if len(auth) >= 9 else (None, None)

    def band(r):
        a = r.get("referring_domains")
        return isinstance(a, (int, float)) and q1 is not None and q1 <= a <= q2

    t3m = [r for r in recs if r.get("__rank") and 1 <= r["__rank"] <= 3 and band(r)]
    restm = [r for r in recs if r.get("__rank") and 4 <= r["__rank"] <= 10 and band(r)]
    t3 = [r for r in recs if r.get("__rank") and 1 <= r["__rank"] <= 3]
    rest = [r for r in recs if r.get("__rank") and 4 <= r["__rank"] <= 10]

    rows_out = []
    for label, getter, kind, lb, action in FACTORS:
        st = bin_stat if kind == "bin" else num_stat
        a_raw, _ = st(t3, getter)
        b_raw, _ = st(rest, getter)
        a_mid, na = st(t3m, getter)
        b_mid, nb = st(restm, getter)
        raw_gap = (a_raw - b_raw) if (a_raw is not None and b_raw is not None) else None
        mid_gap = (a_mid - b_mid) if (a_mid is not None and b_mid is not None) else None
        za = ztest(a_mid, na, b_mid, nb) if kind == "bin" else None
        verdict, conf = classify(label, raw_gap, mid_gap, na, nb, kind, lb, za)
        rows_out.append((verdict, conf, label, raw_gap, mid_gap, min(na, nb), kind, action))

    order = {"LEAD": 0, "WATCH": 1, "GATE": 2, "CONFOUND": 3, "NO DATA": 4}
    rows_out.sort(key=lambda x: (order.get(x[0], 9), x[2]))
    leads = [r for r in rows_out if r[0] == "LEAD"]
    watch = [r for r in rows_out if r[0] == "WATCH"]

    L = []
    L.append("# The SEO Rulebook (auto-generated, self-updating)\n")
    L.append(f"Corpus: **{len(recs)}** graded pages · authority-controlled band n = {len(t3m)} top-3 / "
             f"{len(restm)} challengers. Regenerated every run; verified verdicts come from the audit.\n")
    L.append("> **No entry is a proven RULE yet.** LEAD = survives authority control (audit-verified or "
             "significant). CONFOUND = vanishes at equal authority. WATCH = right direction, not yet "
             "significant. GATE = flat floor. A lead becomes a rule only after a controlled live test "
             "moves a real page — see [[experiments]].\n")
    L.append(f"**Audit-verified leads: {sum(1 for r in leads if r[1]=='audit-verified')} · "
             f"candidates to watch: {len(watch)} · confounds ruled out: {sum(1 for r in rows_out if r[0]=='CONFOUND')}.**\n")
    L.append("| Factor | Verdict | Basis | Raw gap | Controlled gap | n | If real, do this |")
    L.append("|---|---|---|---|---|---|---|")
    for verdict, conf, label, raw_gap, mid_gap, n, kind, action in rows_out:
        rg = fmt(raw_gap, kind)
        mg = fmt(mid_gap, kind)
        act = action if verdict in ("LEAD", "WATCH") else "—"
        L.append(f"| {label} | **{verdict}** | {conf} | {rg} | {mg} | {n} | {act} |")
    L.append("\n## The playbook (confirmed leads first — these are what to test live)\n")
    confirmed = [r for r in leads]
    if confirmed:
        for i, (_, conf, label, _, _, _, _, action) in enumerate(confirmed, 1):
            L.append(f"{i}. **{label}** — {action}")
    else:
        L.append("_No confirmed leads right now._")
    if watch:
        L.append("\n**Watch list (promising, need more data or an audit):** " +
                 ", ".join(r[2] for r in watch) + ".")
    L.append("\n_The authoritative verdicts are set by the six-skeptic `verify-page1-leads` audit and "
             "recorded in VERIFIED here + [[findings-log]]. This screen surfaces new candidates between audits._")
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {out}: {len(leads)} leads ({sum(1 for r in leads if r[1]=='audit-verified')} audit-verified), "
          f"{len(watch)} watch, {sum(1 for r in rows_out if r[0]=='CONFOUND')} confounds")


if __name__ == "__main__":
    main()
