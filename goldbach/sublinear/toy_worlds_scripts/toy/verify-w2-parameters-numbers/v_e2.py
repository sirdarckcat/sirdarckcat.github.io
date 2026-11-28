import sys, math, random, time
import numpy as np
from vcore import *
rng=random.Random(777)
def setup(q,degcfg):
    places=[];ells=[];dl=[]
    for d,cnt,ell in degcfg:
        irr=irreducibles(q,d); irr=irr[:cnt] if cnt else irr
        places+=irr; ells+=[ell]*len(irr)
    return places,ells
def inside(q,degcfg,n,sdeg,inst,label):
    places,ells=setup(q,degcfg); R=residues(q,n,places)
    D=sum((len(p)-1)*sdeg[len(p)-1] for p in places)
    C=sum(l*(len(p)-1)*sdeg[len(p)-1]*(sdeg[len(p)-1]+1)//2 for p,l in zip(places,ells))
    Mv,J=Mcount(n,D); kd=[];ok=0;nc=[];tm=0
    for _ in range(inst):
        N0=rng.randrange(q**n)
        lists=rand_lists(rng,q,places,ells,planted=N0,R=R)
        cons=sorted(int(x) for x in consistent(q,n,places,lists,R))
        t=time.time()
        conds=[(p,c,sdeg[len(p)-1]) for p,L in zip(places,lists) for c in L]
        A,mons=interp_matrix(q,n,D,conds)
        assert A.shape==(C,Mv),(A.shape,C,Mv)
        K=kernel(q,A); tm+=time.time()-t
        assert not ((A@K.T)%q).any()
        roots=common_roots(q,n,D,mons,K)
        kd.append(len(K)); nc.append(len(cons)); ok+=(roots==cons)
        if roots!=cons: print("   MISMATCH",roots,cons)
    print(f"{label} n={n} s={sdeg}: D={D} C={C} M={Mv} J={J} M-C={Mv-C} kernel dim {min(kd)}..{max(kd)}; #cons {min(nc)}..{max(nc)}; roots==brute in {ok}/{inst}; build+kernel {tm/inst:.1f}s each"); sys.stdout.flush()
def outside(q,degcfg,n,scales,inst,label,planted,dmax=None,base=None):
    places,ells=setup(q,degcfg); R=residues(q,n,places)
    dmax=max(len(p)-1 for p in places)
    res=[]
    for t in scales:
        sdeg={d:t*q**(dmax-d) for d in range(1,dmax+1)}
        D=sum((len(p)-1)*sdeg[len(p)-1] for p in places)
        C=sum(l*(len(p)-1)*sdeg[len(p)-1]*(sdeg[len(p)-1]+1)//2 for p,l in zip(places,ells))
        Mv,J=Mcount(n,D); dims=[];ncs=[];forced=0
        for _ in range(inst):
            N0=rng.randrange(q**n) if planted else None
            lists=rand_lists(rng,q,places,ells,planted=N0,R=R)
            nc=len(consistent(q,n,places,lists,R))
            conds=[(p,c,sdeg[len(p)-1]) for p,L in zip(places,lists) for c in L]
            A,mons=interp_matrix(q,n,D,conds)
            assert A.shape==(C,Mv)
            dims.append(Mv-rank(q,A)); ncs.append(nc); forced+=(nc>J)
        res.append(f"t={t}: C={C} M={Mv} J={J} dimV={min(dims)}..{max(dims)} #cons {min(ncs)}..{max(ncs)} forced {forced}/{inst}")
    print(f"{label} n={n} planted={planted}: "+"; ".join(res)); sys.stdout.flush()
which=sys.argv[1]
T0=time.time()
if which=="in":
    inside(13,[(1,13,6)],2,{1:1},20,"q=13 points l=6")
    inside(5,[(1,5,2)],3,{1:3},20,"q=5 points l=2")
    inside(5,[(1,0,2),(2,0,10)],4,{1:5,2:1},10,"q=5 deg1-2 rho=2/5")
    inside(3,[(1,0,1),(2,0,3),(3,0,9)],6,{1:9,2:3,3:1},10,"q=3 deg1-3 rho=1/3")
    inside(3,[(1,0,1),(2,0,3),(3,0,9)],7,{1:18,2:6,3:2},3,"q=3 deg1-3 rho=1/3")
    inside(5,[(1,0,2),(2,0,10)],5,{1:20,2:4},1,"q=5 deg1-2 rho=2/5")
    inside(3,[(1,0,1),(2,0,3),(3,0,9)],8,{1:36,2:12,3:4},1,"q=3 deg1-3 rho=1/3")
if which=="out":
    for pl in (False,True):
        outside(13,[(1,13,6)],4,range(1,7),4,"E3 q=13 points l=6",pl)
        outside(13,[(1,13,6)],5,range(1,7),4,"E3 q=13 points l=6",pl)
        outside(5,[(1,0,2),(2,0,10)],6,range(1,4),3,"E3 q=5 deg1-2 rho=2/5",pl)
        outside(5,[(1,0,3),(2,0,15)],5,range(1,4),3,"E3 q=5 deg1-2 rho=3/5",pl)
        outside(3,[(1,0,2),(2,0,6),(3,0,18)],6,range(1,4),3,"E3 q=3 deg1-3 rho=2/3",pl)
    outside(13,[(1,8,6)],3,range(1,9),10,"E4 q=13 8 points l=6",False)
    outside(13,[(1,8,6)],4,range(1,9),10,"E4 q=13 8 points l=6",False)
print("time %.0fs"%(time.time()-T0))
