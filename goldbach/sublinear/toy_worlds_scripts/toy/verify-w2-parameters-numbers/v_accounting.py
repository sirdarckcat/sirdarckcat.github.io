#!/usr/bin/env python3
# independent Johnson accounting (exact integers / Fractions)
from fractions import Fraction as Fr
import math, itertools
from sympy import divisors, mobius
def I(q,e): return sum(int(mobius(e//d))*q**d for d in divisors(e))//e
def Mbrute(n,D): return sum(1 for b in range(0,D) for a in range(0,D) if a+(n-1)*b<D)
def M(n,D):
    J=(D-1)//(n-1); return (J+1)*D-(n-1)*J*(J+1)//2, J
# check formula and the two bounds used in proofs of Thm 1 and 2
bad=0
for n in range(2,9):
    for D in range(1,200):
        m,J=M(n,D)
        if D<=60 and m!=Mbrute(n,D): bad+=1
        a=n-1
        if not (Fr(D*D,2*a)<=m<=Fr((2*D+a)**2,8*a)): bad+=1
        r=D-J*a
        # exact gap of upper bound: (a-2r)^2/(8a) ; page claims "difference is r(a-r)/(2a) <= a/8"
        assert Fr((2*D+a)**2,8*a)-m==Fr((a-2*r)**2,8*a)
print("M_n(D) formula vs brute force and bounds D^2/(2(n-1)) <= M <= (D+(n-1)/2)^2/(2(n-1)): failures",bad)
print("Mertens mass per degree:")
for q in (2,3,5,13):
    print(q,[round(e*I(q,e)/q**e,4) for e in range(1,13)])
def table(q,rho,d0,d1,nmaxshow=None):
    degs=range(d0,d1+1)
    m=sum(I(q,e) for e in degs); T=sum(e*I(q,e) for e in degs); mu=sum(Fr(e*I(q,e),q**e) for e in degs)
    lim=mu/rho
    nmax = int(lim) + 1 if lim.denominator!=1 else int(lim)   # n-1<lim
    out=f"q={q} rho={rho} deg {d0}..{d1}: m={m} T={T} mu={float(mu):.4f} mu/rho={float(lim):.4f} n<={nmax}"
    rows=[]
    for n in range(max(2,nmax-2),nmax+2):
        found=None
        for t in range(1,61):
            s={e:t*q**(d1-e) for e in degs}
            C=sum(I(q,e)*int(rho*q**e)*e*s[e]*(s[e]+1)//2 for e in degs)
            D=sum(I(q,e)*e*s[e] for e in degs)
            Mv,J=M(n,D)
            if Mv>C: found=(t,C,Mv,D,J); break
        lnE=n*math.log(q)+m*math.log(rho)
        rows.append((n,found,round(lnE,1)))
    return out,rows
for q,rho,d0,d1 in [(5,Fr(2,5),1,1),(5,Fr(2,5),1,2),(5,Fr(2,5),1,3),(5,Fr(2,5),1,4),(3,Fr(1,3),1,3),(3,Fr(1,3),1,4),(3,Fr(1,3),1,6),(3,Fr(2,3),1,6),(13,Fr(6,13),1,1),(13,Fr(6,13),1,3),(2,Fr(1,2),1,8),(2,Fr(1,2),1,12),(5,Fr(3,5),1,2),(3,Fr(2,3),1,3)]:
    o,r=table(q,rho,d0,d1); print(o)
    for x in r: print("    n=%d %s lnE=%s"%(x[0], "t=%d C=%d M=%d D=%d J=%d"%x[1] if x[1] else "no guarantee t<=60", x[2]))
# window form
print("window form")
def window(q,rho,d0,w):
    for kind,need in (("full",rho*(w-1)),("typical",(w-1)/rho)):
        mu=Fr(0);e=d0;T=0;m=0
        while True:
            mu+=Fr(e*I(q,e),q**e);T+=e*I(q,e);m+=I(q,e)
            if mu>need: break
            e+=1
        s=f"q={q} rho={rho} d0={d0} w={w} {kind}: need mass>{float(need):.2f}: degrees {d0}..{e}, T={T:.3e}, T/q^w={T/q**w:.4g}"
        if kind=="full": s+=f", lnE={w*math.log(q)+m*math.log(rho):.4g}"
        print(s)
for a in [(2,Fr(1,2),9,24),(3,Fr(2,3),4,12),(5,Fr(4,5),3,10),(3,Fr(1,3),4,12),(5,Fr(2,5),3,10)]: window(*a)
# corollary (a) estimate q^(2(d0+n-2))/(d0+n) vs true number of table entries needed for mass n-1 from degree d0 (uniform, chi2=0)
print("corollary (a): entries sum_e I(e) q^e needed for mass > n-1 starting at d0, vs q^(2(d0+n-2))/(d0+n)")
for q,d0,n in [(2,9,24),(3,4,12),(5,3,10),(2,1,10),(13,1,4)]:
    mu=Fr(0);e=d0;ent=0
    while True:
        mu+=Fr(e*I(q,e),q**e);ent+=I(q,e)*q**e
        if mu>n-1: break
        e+=1
    print(f"  q={q} d0={d0} n={n}: top degree {e}, entries {ent:.3e}, formula {q**(2*(d0+n-2))/(d0+n):.3e}, window^2={q**(2*n):.3e}")
