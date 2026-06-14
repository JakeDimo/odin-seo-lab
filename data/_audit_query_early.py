import json

PATH = r'C:/Users/jaked/Documents/Obsidian/obsidian-vault/wiki/seo-lab/data/analysis_snapshot.json'
d = json.load(open(PATH, encoding='utf-8'))

# Parse group from label: group|niche|kw|rank
def group_of(r):
    return r['label'].split('|')[0]

# Restrict to page-1 (rank 1-10). top3 = 1-3, challenger = 4-10. Ignore 21-45.
page1 = [r for r in d if isinstance(r.get('__rank'), int) and 1 <= r['__rank'] <= 10]
print("total records:", len(d))
print("page-1 records (rank 1-10):", len(page1))

# rank distribution
from collections import Counter
print("rank dist (all):", dict(sorted(Counter(r.get('__rank') for r in d).items(), key=lambda x:(x[0] is None, x[0]))))

def rate(rows, field='query_early_title'):
    vals = [bool(r.get(field)) for r in rows if r.get(field) is not None]
    if not vals:
        return None, 0
    return sum(vals)/len(vals), len(vals)

top3 = [r for r in page1 if 1 <= r['__rank'] <= 3]
chal = [r for r in page1 if 4 <= r['__rank'] <= 10]

print("\n=== STEP 1: RAW GAP (query_early_title) ===")
r3, n3 = rate(top3)
rc, nc = rate(chal)
print(f"top3:   {r3:.3f}  (n={n3})")
print(f"4-10:   {rc:.3f}  (n={nc})")
print(f"raw gap (pt): {(r3-rc)*100:+.1f}")

# Also check query_in_title for context
print("\n--- query_in_title for reference ---")
print("top3:", rate(top3,'query_in_title'), "4-10:", rate(chal,'query_in_title'))

print("\n=== STEP 2: AUTHORITY CONTROL (referring_domains tertiles over page-1) ===")
rd = sorted([r.get('referring_domains') for r in page1 if isinstance(r.get('referring_domains'),(int,float))])
import statistics
n = len(rd)
t1 = rd[n//3]
t2 = rd[2*n//3]
print(f"referring_domains over page-1: min={rd[0]} median={statistics.median(rd)} max={rd[-1]}")
print(f"tertile cuts: low<{t1} <= mid < {t2} <= high")

def band(r):
    v = r.get('referring_domains')
    if not isinstance(v,(int,float)): return None
    if v < t1: return 'low'
    if v < t2: return 'mid'
    return 'high'

for b in ['low','mid','high']:
    bt3 = [r for r in top3 if band(r)==b]
    bch = [r for r in chal if band(r)==b]
    rt, nt = rate(bt3)
    rcb, ncb = rate(bch)
    # also report median rd in each cell to show comparability
    mt = statistics.median([r['referring_domains'] for r in bt3]) if bt3 else None
    mc = statistics.median([r['referring_domains'] for r in bch]) if bch else None
    gap = (rt-rcb)*100 if (rt is not None and rcb is not None) else None
    print(f"\n[{b}] top3: rate={rt} n={nt} medRD={mt} | 4-10: rate={rcb} n={ncb} medRD={mc} | gap_pt={gap:+.1f}" if gap is not None else f"[{b}] insufficient")

print("\n=== STEP 3: PER-NICHE (raw top3 vs 4-10) ===")
niches = sorted(set(r.get('__niche') for r in page1 if r.get('__niche')))
print("niches present:", niches)
for nic in niches:
    nt3 = [r for r in top3 if r.get('__niche')==nic]
    nch = [r for r in chal if r.get('__niche')==nic]
    rt, nt = rate(nt3)
    rcb, ncb = rate(nch)
    if rt is None or rcb is None:
        print(f"  {nic}: insufficient"); continue
    print(f"  {nic}: top3={rt:.3f}(n={nt})  4-10={rcb:.3f}(n={ncb})  gap={ (rt-rcb)*100:+.1f}pt")

print("\n=== STEP 3b: PER-NICHE within MID authority band ===")
for nic in niches:
    nt3 = [r for r in top3 if r.get('__niche')==nic and band(r)=='mid']
    nch = [r for r in chal if r.get('__niche')==nic and band(r)=='mid']
    rt, nt = rate(nt3)
    rcb, ncb = rate(nch)
    if rt is None or rcb is None or nt<3 or ncb<3:
        print(f"  {nic}: thin (n_top3={nt}, n_410={ncb})"); continue
    print(f"  {nic}: top3={rt:.3f}(n={nt})  4-10={rcb:.3f}(n={ncb})  gap={ (rt-rcb)*100:+.1f}pt")

print("\n=== STEP 4: ALTERNATIVE EXPLANATIONS ===")
# Brand/home pages: page_type distribution by rank band; query_early_title naturally true for many?
print("page_type counts top3:", dict(Counter(r.get('page_type') for r in top3)))
print("page_type counts 4-10:", dict(Counter(r.get('page_type') for r in chal)))
# Does query_early_title correlate with page_type homepage/brand?
for pt in set(r.get('page_type') for r in page1):
    rows=[r for r in page1 if r.get('page_type')==pt]
    print(f"  page_type={pt}: query_early_title rate={rate(rows)[0]} (n={rate(rows)[1]})")
