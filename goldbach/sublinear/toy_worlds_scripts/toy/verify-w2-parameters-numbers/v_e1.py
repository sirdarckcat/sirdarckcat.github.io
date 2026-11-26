import sys, math, random, time
import numpy as np
from vcore import *
rng=random.Random(20261126)
def run(q,cfg,n,trials,label):
    places=[]; ells=[]
    for d,cnt,ell in cfg:
        irr=irreducibles(q,d)[:cnt] if cnt else irreducibles(q,d)
        places+=irr; ells+=[ell]*len(irr)
    R=residues(q,n,places)
    E=q**n*math.prod(l/q**(len(p)-1) for l,p in zip(ells,places))
    # exact variance: E[X^2] = E + q^n * sum_{Delta!=0} prod_i p_i(Delta)
    prod=np.ones(q**n)
    for i,pl in enumerate(places):
        Q=q**(len(pl)-1); l=ells[i]
        prod*=np.where(R[i]==0,l/Q,l*(l-1)/(Q*(Q-1)))
    EX2=E+q**n*(prod.sum()-prod[0])
    var=EX2-E*E
    cnts=[]
    for _ in range(trials):
        lists=rand_lists(rng,q,places,ells)
        cnts.append(len(consistent(q,n,places,lists,R)))
    c=np.array(cnts,float)
    print(f"{label} n={n}: q^n={q**n} E={E:.3f} exact var={var:.3f} | mine: mean {c.mean():.3f} +- {c.std(ddof=1)/math.sqrt(trials):.3f}, sample var {c.var(ddof=1):.3f}, max {int(c.max())} ({trials} trials)"); sys.stdout.flush()
t=time.time()
for n,tr in ((3,400),(4,400),(5,100)): run(13,[(1,13,6)],n,tr,"q=13 13 points l=6")
for n,tr in ((2,400),(3,400),(4,400)): run(13,[(1,8,6)],n,tr,"q=13 8 points l=6")
for n in (5,6,7): run(5,[(1,0,3),(2,0,15)],n,300,"q=5 pts(3)+quadratics(15)")
for n in (6,8,10): run(3,[(1,0,2),(2,0,6),(3,0,18)],n,300,"q=3 deg1-3 rho=2/3")
print("time %.0fs"%(time.time()-t))
