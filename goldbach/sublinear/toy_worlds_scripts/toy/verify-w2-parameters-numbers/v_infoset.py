import random, subprocess, itertools, math, sys
import numpy as np
def prefix_counts(q,n,m,lists):
    inp="\n".join(" ".join("1" if v in L else "0" for v in range(q)) for L in lists)
    out=subprocess.run(["./brute",str(q),str(n),str(m)],input=inp,capture_output=True,text=True).stdout.split()
    return [int(x) for x in out]
def my_infoset(q,n,m,lists):
    # independent: Lagrange basis by modular inverses, information set = points 0..n-1
    inv=lambda a: pow(a%q,q-2,q)
    def lag(c):  # coefficients e_i(c): N(c)=sum_i e_i(c) N(i)
        return [math.prod((c-k)*inv(i-k)%q for k in range(n) if k!=i)%q for i in range(n)]
    g=np.array(list(itertools.product(*[sorted(L) for L in lists[:n]])),dtype=np.int64)
    ok=np.ones(len(g),bool); surv=[len(g)]
    for c in range(n,m):
        tab=np.zeros(q,bool); tab[list(lists[c])]=True
        ok&=tab[(g@np.array(lag(c),dtype=np.int64))%q]; surv.append(int(ok.sum()))
    return len(g),surv
def run(q,n,ell,m,j,seed):
    rng=random.Random(seed)
    lists=[set(sorted(rng.sample(range(q),ell))) for _ in range(m)]     # same data as the page (same seed, same draw order)
    pc=prefix_counts(q,n,m,lists)
    cand,surv=my_infoset(q,n,m,lists)
    assert pc[n]==cand==ell**n and all(pc[n+i]==surv[i] for i in range(m-n+1))
    cons=pc[m]; E=q**n*(ell/q)**m
    h=n//2
    print(f"q={q} n={n} ell={ell} m={m}: consistent={cons} (E={E:.1f}); brute q^n={q**n} -> {q**n/max(cons,1):.3g}/out; infoset {cand} -> {cand/max(cons,1):.3g}/out (rho^-(m-n)={(q/ell)**(m-n):.3g})")
    for jj in range(1,n//2+1):
        left=ell**h; look=ell**jj*ell**(n-h); mt=pc[n+jj] if n+jj<=m else None
        if mt is None: continue
        tot=left+look+mt
        print(f"     merge j={jj}: {left}+{look}+{mt}={tot} -> {tot/max(cons,1):.3g}/out {'<- page' if jj==j else ''}")
    sys.stdout.flush()
run(13,5,6,13,1,1); run(17,6,8,17,2,2); run(17,6,8,12,2,3); run(17,6,8,8,2,4); run(19,6,9,19,2,5); run(23,6,11,23,2,6)
print("j bound (n/2) log_q(ell): q=17: %.2f ; q=13 n=5: %.2f ; q=23: %.2f"%(3*math.log(8)/math.log(17), 2.5*math.log(6)/math.log(13), 3*math.log(11)/math.log(23)))
