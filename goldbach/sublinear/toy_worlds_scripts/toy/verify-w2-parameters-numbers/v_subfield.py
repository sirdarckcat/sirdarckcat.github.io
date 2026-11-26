import itertools, math, random, sys
import numpy as np
from flint import nmod_poly, nmod_mat
from vcore import irreducibles, residues, xpow_table
def field(p,r):
    mod=nmod_poly(irreducibles(p,r)[0],p)
    els=[nmod_poly(list(t),p) for t in itertools.product(range(p),repeat=r)]
    return mod,els
def vec(f,r): c=[int(x) for x in f.coeffs()]; return c+[0]*(r-len(c))
def count_linear(p,r,k):
    """F_Q=F_{p^r}, subfield F_q, q=p^k. polynomials over F_Q of degree <= (Q-1)/(q-1) with all values in F_q"""
    Q=p**r; q=p**k; D=(Q-1)//(q-1); mod,els=field(p,r)
    xb=[nmod_poly([0]*t+[1],p) for t in range(r)]
    rows=[]
    for a in els:
        row=[[] for _ in range(r)]
        ai=nmod_poly([1],p)
        cols=[]
        for i in range(D+1):
            for t in range(r):
                v=(xb[t]*ai)%mod
                w=(pow(v,q,mod)-v)%mod
                cols.append(vec(w,r))
            ai=(ai*a)%mod
        for j in range(r): rows.append([c[j] for c in cols])
    A=nmod_mat(len(rows),len(rows[0]),[x for rr in rows for x in rr],p)
    dim=(D+1)*r-A.rank()
    return Q,q,D,dim
def cosets(p,r,k):
    Q=p**r; q=p**k; D=(Q-1)//(q-1); n=Q-1; seen=set(); dim=0
    for i in range(0,D+1):
        if i in seen: continue
        orb=[]; j=i
        while j not in orb:
            orb.append(j); j=(j*q)%n if j else 0
        seen.update(orb)
        if max(orb)<=D: dim+=len(orb)          # F_q-dimension contributed (c_i free in F_{q^len})
    return dim   # count = q^dim
for p,r,k in ((3,2,1),(3,3,1),(5,2,1),(2,4,2)):
    Q,q,D,dim=count_linear(p,r,k)
    m=r//k
    dens=q/Q; E=Q**(D+1)*dens**Q
    print(f"F_{Q}/F_{q}: degree<={D}: count p^dim = {p}^{dim} = {p**dim}; coset count q^{cosets(p,r,k)} = {q**cosets(p,r,k)}; q^(2^m) = {q**(2**m)}; random lists same density E = {E:.3g}")
# brute force F_9
p,r=3,2; mod,els=field(p,r); Q=9
import time; t=time.time()
val={}
mul=lambda a,b:(a*b)%mod
idx={tuple(vec(e,r)):i for i,e in enumerate(els)}
MT=[[idx[tuple(vec(mul(a,b),r))] for b in els] for a in els]; AT=[[idx[tuple(vec(a+b,r))] for b in els] for a in els]
sub={idx[(c,0)] for c in range(3)}
cnt=0
for co in itertools.product(range(Q),repeat=5):
    ok=True
    for a in range(Q):
        v=0
        for c in reversed(co): v=AT[MT[v][a]][c]
        if v not in sub: ok=False;break
    cnt+=ok
print("brute force F_9, degree<=4, all 59049 polynomials: count with all values in F_3 =",cnt,"(%.0fs)"%(time.time()-t))
# affine (hyperplane) lists vs random lists of same density: q=3, 3 quadratics + 8 cubics
rng=random.Random(5)
def affine_vs_random(q,degs,n,inst,codim=1):
    places=[pl for d in degs for pl in irreducibles(q,d)][:]
    if degs==[2,3]: pass
    R=residues(q,n,places); out=[];rnd=[];ranks=[]
    co=np.stack([(np.arange(q**n)//q**k)%q for k in range(n)],axis=1)
    for _ in range(inst):
        ok=np.ones(q**n,bool); rows=[]
        okr=np.ones(q**n,bool)
        for i,pl in enumerate(places):
            d=len(pl)-1; T=xpow_table(q,pl,n)
            lam=np.array([rng.randrange(q) for _ in range(d)])
            while not lam.any(): lam=np.array([rng.randrange(q) for _ in range(d)])
            b=rng.randrange(q)
            f=(T@lam)%q                 # functional on coefficients of N
            ok&=((co@f)%q==b); rows.append(list(f))
            L=rng.sample(range(q**d),q**(d-1)); tab=np.zeros(q**d,bool); tab[L]=True; okr&=tab[R[i]]
        out.append(int(ok.sum())); rnd.append(int(okr.sum()))
        ranks.append(nmod_mat(len(rows),n,[int(x) for rr in rows for x in rr],q).rank())
    from collections import Counter
    print(f"q={q} places deg {degs} (m={len(places)}) hyperplane lists n={n}: affine counts {dict(Counter(out))}, ranks {dict(Counter(ranks))}; random lists mean {np.mean(rnd):.2f} range {min(rnd)}..{max(rnd)}; E={q**n*(1/q)**len(places):.2f}")
affine_vs_random(3,[2,3],13,60); affine_vs_random(3,[2,3],12,60); affine_vs_random(3,[3],10,60)
