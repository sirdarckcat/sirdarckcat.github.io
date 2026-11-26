import random, math, sys
import numpy as np
from vcore import *
rng=random.Random(99)
def one(q,degs,n,smax,nplant):
    places=[pl for d in degs for pl in irreducibles(q,d)]
    R=residues(q,n,places)
    S=[np.array([rng.choice([0,0,1,1,2,smax]) if rng.random()<0.6 else 0 for _ in range(q**(len(pl)-1))]) for pl in places]
    pl_N=[rng.randrange(q**n) for _ in range(nplant)]
    for N0 in pl_N:
        for i in range(len(places)):
            if rng.random()<0.85: S[i][R[i][N0]]=max(S[i][R[i][N0]],rng.randint(2,smax+2))
    d=[len(p)-1 for p in places]
    C=sum(d[i]*int((S[i]*(S[i]+1)//2).sum()) for i in range(len(places)))
    s2=sum(d[i]*int((S[i]**2).sum()) for i in range(len(places)))
    D=1
    while Mcount(n,D)[0]<=C: D+=1
    Mv,J=Mcount(n,D)
    A_N=sum(d[i]*S[i][R[i]] for i in range(len(places)))
    G=np.nonzero(A_N>=D)[0]
    conds=[(places[i],c,int(S[i][c])) for i in range(len(places)) for c in range(len(S[i])) if S[i][c]>0]
    A,mons=interp_matrix(q,n,D,conds)
    K=kernel(q,A)
    roots=common_roots(q,n,D,mons,K,cands=[int(x) for x in G])
    t1=(len(K)>=Mv-C>0) and roots==sorted(int(x) for x in G) and len(G)<=J
    t2=True; ratio=None
    if len(G):
        lhs=0
        for i in range(len(places)):
            pi=np.bincount(R[i][G],minlength=len(S[i]))/len(G)
            lhs+=d[i]*float((pi[S[i]>0]**2).sum())
        rhs=math.sqrt(n-1)-(n-1)/(2*math.sqrt(s2))
        t2=math.sqrt(lhs)>rhs; ratio=math.sqrt(lhs)/rhs
        # also the bound D0 > sqrt(n-1)||s|| - (n-1)/2
        t2=t2 and D>math.sqrt((n-1)*s2)-(n-1)/2
    return t1,t2,len(G),J,ratio,A.shape
tot=0;ok1=0;ok2=0;ratios=[];ne=0
for q,degs,n,smax,npl in [(5,[1],2,3,1),(5,[1],3,3,2),(7,[1],3,2,1),(3,[1,2],3,3,2),(3,[1,2],4,2,1),(5,[1,2],3,2,2),(2,[1,2,3],4,3,2),(2,[1,2,3,4],5,2,1),(3,[1,2,3],4,2,3),(7,[1],4,3,3)]:
    for _ in range(12):
        t1,t2,g,J,ratio,shape=one(q,degs,n,smax,npl); tot+=1; ok1+=t1; ok2+=t2
        if ratio: ratios.append(ratio); ne+=1
    print(q,degs,n,"last: |G|=%d J=%d shape=%s"%(g,J,shape)); sys.stdout.flush()
print(f"instances {tot}: Theorem 1 (kernel nonzero, every N with A>=D0 a root of whole kernel, |G|<=J) {ok1}/{tot}; Theorem 2 inequality {ok2}/{tot} (G nonempty in {ne}); lhs/rhs between {min(ratios):.2f} and {max(ratios):.2f}")
