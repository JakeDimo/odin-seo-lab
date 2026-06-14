import json, math
from collections import defaultdict

PATH = r'C:/Users/jaked/Documents/Obsidian/obsidian-vault/wiki/seo-lab/data/analysis_snapshot.json'
d = json.load(open(PATH, encoding='utf-8'))

def is_top3(r): return r is not None and 1 <= r <= 3
def is_chal(r): return r is not None and 4 <= r <= 10

# Buckets
top3 = [r for r in d if is_top3(r.get('__rank'))]
chal = [r for r in d if is_chal(r.get('__rank'))]
print("Total records:", len(d))
print("top3 n:", len(top3), " 4-10 n:", len(chal))

def prop_true(rows, field):
    vals = [bool(r.get(field)) for r in rows if r.get(field) is not None]
    n = len(vals); k = sum(vals)
    return k, n, (k/n if n else float('nan'))

def two_prop_z(k1,n1,k2,n2):
    if n1==0 or n2==0: return float('nan'), float('nan')
    p1=k1/n1; p2=k2/n2
    p=(k1+k2)/(n1+n2)
    se=math.sqrt(p*(1-p)*(1/n1+1/n2))
    if se==0: return float('nan'), float('nan')
    z=(p1-p2)/se
    # two-sided p
    pval=math.erfc(abs(z)/math.sqrt(2))
    return z, pval

# ---- STEP 1: raw gap title_len_ok ----
print("\n=== STEP 1: RAW title_len_ok gap (top3 vs 4-10) ===")
k1,n1,p1 = prop_true(top3,'title_len_ok')
k2,n2,p2 = prop_true(chal,'title_len_ok')
print(f"top3: {k1}/{n1} = {p1*100:.1f}%")
print(f"4-10: {k2}/{n2} = {p2*100:.1f}%")
print(f"raw gap = {(p1-p2)*100:+.1f} pt")
z,pv = two_prop_z(k1,n1,k2,n2)
print(f"z = {z:.3f}, two-sided p = {pv:.4f}")

# Inspect title_len_ok definition vs title_len: confirm 40-60 char truncation-safe
print("\n--- title_len_ok vs title_len sanity ---")
lens_ok = [r['title_len'] for r in d if r.get('title_len_ok') and r.get('title_len') is not None]
lens_not = [r['title_len'] for r in d if r.get('title_len_ok')==False and r.get('title_len') is not None]
if lens_ok:
    print(f"title_len_ok=True: title_len range {min(lens_ok)}-{max(lens_ok)} (n={len(lens_ok)})")
if lens_not:
    print(f"title_len_ok=False: title_len range {min(lens_not)}-{max(lens_not)} (n={len(lens_not)})")

# ---- STEP 2: control for authority via referring_domains tertiles ----
print("\n=== STEP 2: referring_domains tertiles, retest MIDDLE band ===")
both = top3 + chal
rds = sorted([r['referring_domains'] for r in both if r.get('referring_domains') is not None])
n=len(rds)
t1 = rds[n//3]
t2 = rds[2*n//3]
print(f"referring_domains tertile cuts: low<={t1}, mid {t1}-{t2}, high>{t2} (over both buckets, n={n})")

def band(r):
    rd = r.get('referring_domains')
    if rd is None: return None
    if rd < t1: return 'low'
    if rd <= t2: return 'mid'
    return 'high'

for b in ['low','mid','high']:
    bt = [r for r in top3 if band(r)==b]
    bc = [r for r in chal if band(r)==b]
    k1,n1,p1 = prop_true(bt,'title_len_ok')
    k2,n2,p2 = prop_true(bc,'title_len_ok')
    z,pv = two_prop_z(k1,n1,k2,n2)
    print(f"\n[{b} band] top3 {k1}/{n1}={p1*100:.1f}%  | 4-10 {k2}/{n2}={p2*100:.1f}%  gap={(p1-p2)*100:+.1f}pt  z={z:.3f} p={pv:.4f}  min_top3_cell_n={n1}")

# ---- STEP 4: per niche ----
print("\n=== STEP 4: per-niche direction (raw title_len_ok) ===")
niches = sorted(set(r.get('__niche') for r in d if r.get('__niche')))
print("niches:", niches)
for nm in niches:
    nt = [r for r in top3 if r.get('__niche')==nm]
    nc = [r for r in chal if r.get('__niche')==nm]
    k1,n1,p1 = prop_true(nt,'title_len_ok')
    k2,n2,p2 = prop_true(nc,'title_len_ok')
    z,pv = two_prop_z(k1,n1,k2,n2)
    rev = " <-- REVERSER" if (p1-p2)<0 else ""
    print(f"{nm:20s} top3 {k1}/{n1}={p1*100:.0f}% | 4-10 {k2}/{n2}={p2*100:.0f}% gap={(p1-p2)*100:+.1f}pt z={z:.2f}{rev}")

# ---- STEP 5: page_type breakdown + query_in_title control ----
print("\n=== STEP 5: page_type distribution top3 vs 4-10 ===")
def ptdist(rows):
    c=defaultdict(int)
    for r in rows: c[r.get('page_type')]+=1
    return c
pt3=ptdist(top3); ptc=ptdist(chal)
allpt=sorted(set(list(pt3)+list(ptc)), key=lambda x:str(x))
for pt in allpt:
    print(f"  {str(pt):20s} top3 {pt3.get(pt,0):4d} ({pt3.get(pt,0)/len(top3)*100:4.1f}%) | 4-10 {ptc.get(pt,0):4d} ({ptc.get(pt,0)/len(chal)*100:4.1f}%)")

print("\n=== STEP 5b: query_in_title raw + controlled by page_type ===")
k1,n1,p1 = prop_true(top3,'query_in_title')
k2,n2,p2 = prop_true(chal,'query_in_title')
z,pv=two_prop_z(k1,n1,k2,n2)
print(f"query_in_title RAW: top3 {p1*100:.1f}% vs 4-10 {p2*100:.1f}% gap={(p1-p2)*100:+.1f}pt z={z:.2f} p={pv:.4f}")
for pt in allpt:
    pt3rows=[r for r in top3 if r.get('page_type')==pt]
    ptcrows=[r for r in chal if r.get('page_type')==pt]
    k1,n1,p1=prop_true(pt3rows,'query_in_title')
    k2,n2,p2=prop_true(ptcrows,'query_in_title')
    if n1>=15 and n2>=15:
        z,pv=two_prop_z(k1,n1,k2,n2)
        print(f"  [{str(pt):16s}] q_in_title top3 {p1*100:.0f}%(n{n1}) vs 4-10 {p2*100:.0f}%(n{n2}) gap={(p1-p2)*100:+.1f}pt z={z:.2f}")
