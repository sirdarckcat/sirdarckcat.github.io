#!/usr/bin/env python3
# Independent recomputation of the integer-side numbers of page w2-parameters.
import math, sys, time
import numpy as np
t0=time.time()
F="/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
line=[x for x in open(F) if x.startswith("COVER")][0].split()
cov=[tuple(map(int,t.split(":"))) for t in line[2:]]
print("cover pairs",len(cov),"max",max(r for r,_ in cov),"declared rows",line[1])
def sieve(n):
    s=np.ones(n+1,dtype=bool); s[:2]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0]
P8=sieve(10**8)
print("primes to 1e8:",len(P8), "t=%.1f"%(time.time()-t0))
small=P8[P8<200000]
rows=np.array([q for q in small if q>2 and all(q%r!=a for r,a in cov)],dtype=np.int64)
R=len(rows); print("rows (odd primes <200000 in no class):",R)
# is 2 a row?  (N-2 even) not counted
lnK=24.35*math.log(2); print("lnK",lnK, "K",2**24.35)
later=P8[P8>463].astype(np.int64)
lp=np.log(later.astype(float)); pf=later.astype(float)
m2e6=later<=2_000_000
print("primes 467..2e6:",int(m2e6.sum()),"sum ln p/p = %.4f"%float((lp/pf)[m2e6].sum()), " ln(2e6/463)=%.4f"%math.log(2e6/463))
print("sum ln p/p 467..1e8 = %.4f  vs ln(1e8/463)=%.4f"%(float((lp/pf).sum()),math.log(1e8/463)))
print("typical strikes R*sum 1/p (467..1e8) = %.1f"%(R*float((1/pf).sum())))
# histograms for p<200000 : number of classes holding k rows
lo=later[later<200000]
KM=40
H=np.zeros((len(lo),KM),dtype=np.int64)
for i,p in enumerate(lo):
    cnt=np.bincount(np.bincount(rows%p,minlength=int(p)))
    H[i,:len(cnt)]=cnt
assert (H@np.arange(KM)==R).all() and (H.sum(1)==lo).all()
print("max rows in one class:",int(np.nonzero(H.sum(0))[0].max()), "t=%.1f"%(time.time()-t0))
ks=np.arange(KM,dtype=float)
nlo=len(lo); hi_p=pf[nlo:]; hi_lp=lp[nlo:]
def stats(th,upto=None):
    # returns per-prime arrays KL, chi2, strikes, sparse(sum over occupied classes of pi^2)
    w=np.exp(th*ks)[None,:]
    Z=(H*w).sum(1); pk=w/Z[:,None]
    KLlo=(H*pk*np.log(pk*pf[:nlo,None])).sum(1)
    S2lo=pf[:nlo]*(H*pk*pk).sum(1)
    stlo=(H*pk*ks).sum(1)
    splo=(H[:,1:]*pk[:,1:]**2).sum(1)
    Zh=hi_p-R+R*math.exp(th)
    KLhi=np.log(hi_p/Zh)+th*R*math.exp(th)/Zh
    S2hi=hi_p*(R*math.exp(2*th)+hi_p-R)/Zh**2
    sthi=R*math.exp(th)/Zh
    sphi=R*math.exp(2*th)/Zh**2
    return (np.concatenate([KLlo,KLhi]),np.concatenate([S2lo,S2hi])-1,np.concatenate([stlo,sthi]),np.concatenate([splo,sphi]))
def solve(kappa):
    a,b=0.0,3.0
    for _ in range(50):
        m=(a+b)/2
        if stats(m)[0].sum()<kappa: a=m
        else: b=m
    return (a+b)/2
typ=stats(0.0)[2].sum()
print("typical strikes via histograms %.1f"%typ)
print("kappa theta strikes ratio X chi2_467 KL_467 need y_mertens README_old README_new")
res={}
for kappa in (1.0,4.2,8.0,12.0,16.6,30.0):
    th=solve(kappa); KL,chi,st,sp=stats(th)
    X=float(((lp/pf)*chi).sum()); need=lnK-X
    y=463*math.exp(need)
    old=(math.sqrt(lnK)-math.sqrt(2*kappa*math.log(467)/467))**2
    new=lnK-2*kappa*math.log(467)/467
    res[kappa]=(th,X)
    print("%5.1f %.4f %.1f %.3f X=%.4f %.4f %.4f need=%.3f y=%.3e pi~%.3e | old %.3f->%.3e | new(M+2k ln p/p>=lnK) %.3f->%.3e"%(kappa,th,st.sum(),st.sum()/typ,X,chi[0],KL[0],need,y,y/math.log(y),old,463*math.exp(old),new,463*math.exp(new)))
    if kappa==16.6:
        print("   sparse (occupied classes only) sum ln p*pi^2: to 2e6 %.4f ; to 1e8 %.4f ; exp -> %.2f members"%(float((lp*sp)[m2e6].sum()),float((lp*sp).sum()),math.exp(float((lp*sp).sum()))))
        print("   check 2*KL-weighted: sum (ln p/p)*2KL = %.4f ; max-bound 2 kappa ln467/467 = %.4f"%(float(((lp/pf)*2*KL).sum()),2*kappa*math.log(467)/467))
# greedy minimal number of weighted classes, primes to 2e6 as on the page
def greedy(target,th,limit=2_000_000):
    w=np.exp(th*ks)
    # low primes: per (prime,k) value and multiplicity
    Z=(H*w[None,:]).sum(1)
    vlo=(lp[:nlo,None]*(w[None,:]/Z[:,None])**2).ravel(); mlo=H.ravel().astype(float)
    sel=(later[nlo:]<=limit)
    hp=hi_p[sel]; hl=hi_lp[sel]; Zh=hp-R+R*math.exp(th)
    v=np.concatenate([vlo, hl/Zh**2, hl*math.exp(2*th)/Zh**2]); m=np.concatenate([mlo, hp-R, np.full(len(hp),float(R))])
    o=np.argsort(-v); v=v[o]; m=m[o]
    cs=np.cumsum(v*m); cn=np.cumsum(m)
    if cs[-1]<target: return None,cs[-1]
    j=int(np.searchsorted(cs,target))
    pc=cn[j-1] if j else 0.; ps=cs[j-1] if j else 0.
    return pc+math.ceil((target-ps)/v[j]),cs[-1]
for Ks in (2,16,256,1024,4096):
    th=solve(min(16.6,math.log(Ks)))
    nw,tot=greedy(math.log(Ks),th)
    sp=stats(th)[3]
    print("K_s=%d theta=%.4f: min weighted classes %s (%.3g per member); all classes to 2e6 give %.3f; sparse to 2e6 %.3f"%(Ks,th,nw,(nw or 0)/Ks,tot,float((lp*sp)[m2e6].sum())))
# prime powers
allp=P8[P8<=2_000_000].astype(float)
f=lambda a: float(sum((e*np.log(a)/a**e).sum() for e in range(2,60)))
print("prime powers e>=2: all p<=2e6: %.5f ; closed form sum ln p (2p-1)/(p(p-1)^2) over p<=1e8: %.5f"%(f(allp), float((np.log(P8.astype(float))*(2*P8-1.0)/(P8*(P8-1.0)**2)).sum())))
print("   p>463: %.5f (to 2e6), %.5f (to 1e8)"%(f(allp[allp>463]), float((np.log(pf)*(2*pf-1)/(pf*(pf-1)**2)).sum())))
print("ratios e/p^(e-1):",[(p,e,round(e/p**(e-1),4)) for p,e in ((2,2),(2,3),(3,2),(5,2),(467,2))])
print("t=%.1f"%(time.time()-t0))
