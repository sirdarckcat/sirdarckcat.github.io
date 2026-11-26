# Theorem 4 (ii): folded RS, linear-algebraic interpolation Q = A_0 + sum_j A_j Y_j, product lists -> Q = 0 when D+k-1 <= W
import random, itertools
from flint import nmod_mat
rng=random.Random(8)
def primroot(q):
    for g in range(2,q):
        if len({pow(g,e,q) for e in range(q-1)})==q-1: return g
def run(q,m,s,k,per,product=True,trials=20):
    g=primroot(q); N=(q-1)//m; W=N*(m-s+1); out=[]
    for D in range(1,W+2):
        dims=set()
        for _ in range(trials):
            # planted f of degree<k, lists per coordinate
            f=[rng.randrange(q) for _ in range(k)]
            ev=lambda x: sum(c*pow(x,e,q) for e,c in enumerate(f))%q
            rows=[]
            for i in range(N):
                vals=[ev(pow(g,i*m+j,q)) for j in range(m)]
                if product:
                    L=[[vals[j]]+rng.sample([v for v in range(q) if v!=vals[j]],per-1) for j in range(m)]
                    tuples=None
                else:
                    tuples=[tuple(vals)]+[tuple(rng.randrange(q) for _ in range(m)) for _ in range(per-1)]
                for j in range(m-s+1):
                    a=pow(g,i*m+j,q)
                    ys=set(itertools.product(*L[j:j+s])) if product else {t[j:j+s] for t in tuples}
                    for y in ys:
                        r=[pow(a,e,q) for e in range(D+k-1)]
                        for t in range(s): r+=[y[t]*pow(a,e,q)%q for e in range(D)]
                        rows.append(r)
            A=nmod_mat(len(rows),len(rows[0]),[x for r in rows for x in r],q)
            dims.add(len(rows[0])-A.rank())
        out.append((D,sorted(dims)))
    print(f"q={q} m={m} N={N} s={s} k={k} W={W} {'product lists, %d values per coordinate'%per if product else 'arbitrary lists of %d tuples'%per}: dim of interpolation space by D: {out}  (Q=0 claimed for D+k-1<=W, i.e. D<={W-k+1}; count (i) needs (s+1-l)W > s(k-1))")
run(13,3,2,3,2); run(13,4,3,2,2); run(17,4,2,4,3); run(31,5,3,4,2,trials=5)
run(13,3,2,3,2,product=False); run(17,4,3,3,2,product=False); run(31,5,4,4,3,product=False,trials=5)
