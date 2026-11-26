from fractions import Fraction as Fr
from sympy import divisors, mobius
def I(q,e): return sum(int(mobius(e//d))*q**d for d in divisors(e))//e
# window q^w; a place of degree e > w sees only q^w occupied classes. lists (density rho) restricted to occupied classes:
# typical member inside the guarantee iff rho * sum_e e I(e) / q^min(e,w) > w-1
for q,rho,d0,w in [(2,Fr(1,2),9,24),(3,Fr(2,3),4,12),(5,Fr(4,5),3,10),(3,Fr(1,3),4,12),(5,Fr(2,5),3,10)]:
    for adapted in (False,True):
        mu=Fr(0);e=d0;T=0;ent=0
        while True:
            mu+=Fr(e*I(q,e),q**(min(e,w) if adapted else e)); T+=e*I(q,e); ent+=I(q,e)*q**(min(e,w) if adapted else e)
            if rho*mu>w-1: break
            e+=1
        print(f"q={q} rho={rho} d0={d0} w={w} typical member, {'occupied classes only' if adapted else 'all classes (page)   '}: degrees {d0}..{e}, T={float(T):.3e} = {float(T)/q**w:.4g} windows; table entries {float(ent):.3e} = {float(ent)/q**w:.3g} per member")
