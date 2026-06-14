import json, math
from collections import defaultdict
PATH = r'C:/Users/jaked/Documents/Obsidian/obsidian-vault/wiki/seo-lab/data/analysis_snapshot.json'
d = json.load(open(PATH, encoding='utf-8'))
top3=[r for r in d if r.get('__rank') and 1<=r['__rank']<=3]
chal=[r for r in d if r.get('__rank') and 4<=r['__rank']<=10]

def prop_true(rows, field):
    vals=[bool(r.get(field)) for r in rows if r.get(field) is not None]
    return sum(vals), len(vals)
def z2(k1,n1,k2,n2):
    if not n1 or not n2: return float('nan'),float('nan')
    p1,p2=k1/n1,k2/n2; p=(k1+k2)/(n1+n2)
    se=math.sqrt(p*(1-p)*(1/n1+1/n2))
    if se==0: return float('nan'),float('nan')
    z=(p1-p2)/se; return z, math.erfc(abs(z)/math.sqrt(2))

# 1) What does title_len_ok actually flag? Check the 40-60 truncation-safe claim
print("=== title_len_ok decode ===")
buckets=defaultdict(lambda:[0,0])  # len-range -> [ok_true, ok_false]
for r in d:
    tl=r.get('title_len'); ok=r.get('title_len_ok')
    if tl is None or ok is None: continue
    b = '00-39' if tl<40 else '40-60' if tl<=60 else '61-70' if tl<=70 else '71+'
    buckets[b][0 if ok else 1]+=1
for b in ['00-39','40-60','61-70','71+']:
    t,f=buckets[b]
    print(f"  len {b}: ok=True {t}, ok=False {f}")

# 2) Define a strict truncation-safe 40-60 flag ourselves and retest
print("\n=== STRICT 40-60 char flag (our own), raw ===")
def safe(r):
    tl=r.get('title_len')
    return None if tl is None else (40<=tl<=60)
k1=sum(1 for r in top3 if safe(r)); n1=sum(1 for r in top3 if safe(r) is not None)
k2=sum(1 for r in chal if safe(r)); n2=sum(1 for r in chal if safe(r) is not None)
z,pv=z2(k1,n1,k2,n2)
print(f"top3 {k1}/{n1}={k1/n1*100:.1f}% | 4-10 {k2}/{n2}={k2/n2*100:.1f}% gap={(k1/n1-k2/n2)*100:+.1f}pt z={z:.2f} p={pv:.4f}")

# 3) Home-page confound: title_len_ok gap EXCLUDING home pages
print("\n=== title_len_ok gap EXCLUDING home pages ===")
t3=[r for r in top3 if r.get('page_type')!='home']
c3=[r for r in chal if r.get('page_type')!='home']
k1,n1=prop_true(t3,'title_len_ok'); k2,n2=prop_true(c3,'title_len_ok')
z,pv=z2(k1,n1,k2,n2)
print(f"non-home: top3 {k1/n1*100:.1f}%(n{n1}) | 4-10 {k2/n2*100:.1f}%(n{n2}) gap={(k1/n1-k2/n2)*100:+.1f}pt z={z:.2f} p={pv:.4f}")
print("\n=== title_len_ok gap HOME ONLY ===")
t3=[r for r in top3 if r.get('page_type')=='home']
c3=[r for r in chal if r.get('page_type')=='home']
k1,n1=prop_true(t3,'title_len_ok'); k2,n2=prop_true(c3,'title_len_ok')
z,pv=z2(k1,n1,k2,n2)
print(f"home: top3 {k1/n1*100:.1f}%(n{n1}) | 4-10 {k2/n2*100:.1f}%(n{n2}) gap={(k1/n1-k2/n2)*100:+.1f}pt z={z:.2f} p={pv:.4f}")

# 4) Stratified (Cochran-Mantel-Haenszel-ish) across the 3 RD bands - pooled
print("\n=== Pooled across RD tertiles (CMH common z) for title_len_ok ===")
both=top3+chal
rds=sorted([r['referring_domains'] for r in both if r.get('referring_domains') is not None])
n=len(rds); t1=rds[n//3]; t2=rds[2*n//3]
def band(r):
    rd=r.get('referring_domains')
    if rd is None: return None
    return 'low' if rd<t1 else ('mid' if rd<=t2 else 'high')
# CMH for 2x2 across strata
num=0; den=0  # sum(a - E[a]) and sum(Var)
for b in ['low','mid','high']:
    bt=[r for r in top3 if band(r)==b]; bc=[r for r in chal if band(r)==b]
    a=sum(1 for r in bt if r.get('title_len_ok')); b1=sum(1 for r in bt if r.get('title_len_ok') is not None)-a
    c=sum(1 for r in bc if r.get('title_len_ok')); d2=sum(1 for r in bc if r.get('title_len_ok') is not None)-c
    Ntot=a+b1+c+d2
    if Ntot==0: continue
    row1=a+b1; col1=a+c
    Ea=row1*col1/Ntot
    Va=row1*(Ntot-row1)*col1*(Ntot-col1)/(Ntot**2*(Ntot-1)) if Ntot>1 else 0
    num+=(a-Ea); den+=Va
cmh_chi2 = (abs(num)-0.5)**2/den if den>0 else float('nan')
print(f"CMH chi2(1df) = {cmh_chi2:.3f}  (crit 3.84 for p<0.05); sum(a-E)={num:.2f}")

# 5) numeric title_len Mann-Whitney as a robustness check on the underlying signal
print("\n=== Mann-Whitney on raw title_len (top3 vs 4-10) ===")
def mwu(x,y):
    # rank-sum
    combined=sorted([(v,0) for v in x]+[(v,1) for v in y])
    # assign average ranks
    ranks=[0.0]*len(combined); i=0
    while i<len(combined):
        j=i
        while j+1<len(combined) and combined[j+1][0]==combined[i][0]: j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): ranks[k]=avg
        i=j+1
    R1=sum(ranks[idx] for idx,(_,g) in enumerate(combined) if g==0)
    n1=len(x); n2=len(y)
    U1=R1-n1*(n1+1)/2
    mu=n1*n2/2; sd=math.sqrt(n1*n2*(n1+n2+1)/12)
    z=(U1-mu)/sd
    return z, math.erfc(abs(z)/math.sqrt(2))
x=[r['title_len'] for r in top3 if r.get('title_len') is not None]
y=[r['title_len'] for r in chal if r.get('title_len') is not None]
import statistics
print(f"median title_len top3={statistics.median(x):.0f} 4-10={statistics.median(y):.0f}")
z,pv=mwu(x,y)
print(f"MWU z={z:.2f} p={pv:.4f}")
