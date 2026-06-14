import json, statistics
from collections import Counter

PATH = r'C:/Users/jaked/Documents/Obsidian/obsidian-vault/wiki/seo-lab/data/analysis_snapshot.json'
d = json.load(open(PATH, encoding='utf-8'))
page1 = [r for r in d if isinstance(r.get('__rank'), int) and 1 <= r['__rank'] <= 10]
top3 = [r for r in page1 if 1 <= r['__rank'] <= 3]
chal = [r for r in page1 if 4 <= r['__rank'] <= 10]

def rate(rows, field='query_early_title'):
    vals=[bool(r.get(field)) for r in rows if r.get(field) is not None]
    if not vals: return None,0
    return sum(vals)/len(vals), len(vals)

# 1) Niche composition by band — is mid band dominated by window-cleaning?
rd=sorted(r['referring_domains'] for r in page1 if isinstance(r.get('referring_domains'),(int,float)))
n=len(rd); t1=rd[n//3]; t2=rd[2*n//3]
def band(r):
    v=r.get('referring_domains')
    if not isinstance(v,(int,float)): return None
    if v<t1: return 'low'
    if v<t2: return 'mid'
    return 'high'

print("=== Niche composition of the MID band ===")
mid_t3=[r for r in top3 if band(r)=='mid']
mid_ch=[r for r in chal if band(r)=='mid']
print("mid top3 niches:", dict(Counter(r['__niche'] for r in mid_t3)))
print("mid 4-10 niches:", dict(Counter(r['__niche'] for r in mid_ch)))

# 2) Pooled vs niche-balanced mid-band gap (Simpson check):
#    compute per-niche mid gap, then average weighting equally so window-cleaning can't dominate
print("\n=== Mid-band gap: pooled vs niche-weighted ===")
gaps=[]
for nic in ['plumbing','window-cleaning','online-therapy']:
    a=[r for r in mid_t3 if r['__niche']==nic]
    b=[r for r in mid_ch if r['__niche']==nic]
    ra,na=rate(a); rb,nb=rate(b)
    if ra is None or rb is None or na<3 or nb<3:
        print(f"  {nic}: thin (n_t3={na}, n_ch={nb}) -> excluded from equal-weight avg")
        continue
    g=(ra-rb)*100
    gaps.append(g)
    print(f"  {nic}: gap={g:+.1f}pt (n_t3={na}, n_ch={nb})")
if gaps:
    print(f"  equal-weight avg of niches with n>=3: {statistics.mean(gaps):+.1f}pt over {len(gaps)} niche(s)")

# 3) Robustness to band definition: quartiles and median split
print("\n=== Robustness: median split on referring_domains ===")
med=statistics.median(rd)
def mid_band_median(lo,hi):
    # central band = interquartile (25-75) to isolate comparable authority
    return None
q1=rd[n//4]; q3=rd[3*n//4]
print(f"quartiles: q1={q1} median={med} q3={q3}")
def rdval(r):
    v=r.get('referring_domains'); return v if isinstance(v,(int,float)) else -1
iqr_t3=[r for r in top3 if q1<=rdval(r)<q3]
iqr_ch=[r for r in chal if q1<=rdval(r)<q3]
rt,nt=rate(iqr_t3); rc,nc=rate(iqr_ch)
print(f"IQR band (q1<=rd<q3): top3={rt:.3f}(n={nt}) 4-10={rc:.3f}(n={nc}) gap={(rt-rc)*100:+.1f}pt")

# 4) Within mid band, is referring_domains actually balanced, or is top3 systematically higher?
print("\n=== RD balance inside mid band ===")
print(f"mid top3 RD: median={statistics.median([r['referring_domains'] for r in mid_t3])} mean={statistics.mean([r['referring_domains'] for r in mid_t3]):.0f}")
print(f"mid 4-10 RD: median={statistics.median([r['referring_domains'] for r in mid_ch])} mean={statistics.mean([r['referring_domains'] for r in mid_ch]):.0f}")

# 5) Alternative: does query_in_title (the weaker condition) show same pattern? And query_early among query_in_title pages only
print("\n=== Conditioning: query_early_title GIVEN query_in_title ===")
t3_q=[r for r in mid_t3 if r.get('query_in_title')]
ch_q=[r for r in mid_ch if r.get('query_in_title')]
print(f"mid, among query_in_title=True: top3 early-rate={rate(t3_q)} | 4-10 early-rate={rate(ch_q)}")

# 6) Fisher exact-ish: just show the 2x2 for mid band
print("\n=== Mid-band 2x2 (query_early_title) ===")
def c(rows):
    t=sum(1 for r in rows if r.get('query_early_title')); return t, len(rows)-t
a3,b3=c(mid_t3); ac,bc=c(mid_ch)
print(f"            early=Y  early=N")
print(f"top3        {a3:>5}   {b3:>5}   (n={a3+b3})")
print(f"4-10        {ac:>5}   {bc:>5}   (n={ac+bc})")
# quick two-proportion z
import math
p1=a3/(a3+b3); p2=ac/(ac+bc); p=(a3+ac)/(a3+b3+ac+bc)
se=math.sqrt(p*(1-p)*(1/(a3+b3)+1/(ac+bc)))
z=(p1-p2)/se if se>0 else 0
print(f"two-proportion z={z:.2f}  (|z|>1.96 ~ p<0.05)")
