"""The smallest instance (rows below 160, moduli 3..13, even N < 840): the free bounds of the seven maximal pinnable
designs taken together.  A candidate is excluded when, in some design, no number with its classes on the design
could be left with fewer rows than the optimum, whatever its classes modulo the other moduli."""
import itertools
rows=[q for q in range(3,160,2) if all(q%d for d in range(3,int(q**0.5)+1,2))]
mods=(3,5,7,11,13)
def left_cls(cls): return sum(all(q%r!=a for r,a in cls.items()) for q in rows)
def score(N): return left_cls({r:N%r for r in mods})
cands=list(range(0,840,2)); OPT=min(score(N) for N in cands)
designs=[(3,5,7),(3,5,11),(3,5,13),(3,7,11),(3,7,13),(5,7,11),(11,13)]
LB={}
for T in designs:
    rest=[r for r in mods if r not in T]
    for cls in itertools.product(*[range(r) for r in T]):
        base=dict(zip(T,cls))
        LB[(T,cls)]=min(left_cls({**base,**dict(zip(rest,c2))}) for c2 in itertools.product(*[range(r) for r in rest]))
def B(N): return max(LB[(T,tuple(N%r for r in T))] for T in designs)
from collections import Counter
print("OPT",OPT)
for T in designs:
    below=[N for N in cands if LB[(T,tuple(N%r for r in T))]<OPT]
    cells=set(tuple(N%r for r in T) for N in below)
    print("design",T,"cells",len(set(tuple(N%r for r in T) for N in cands)),"cells with free bound below OPT",len(cells),"candidates in them",len(below))
allb=[N for N in cands if B(N)<OPT]
print("candidates not excluded by the free bound of any of the seven designs:",len(allb),allb,[score(N) for N in allb])
eq=[N for N in cands if B(N)==OPT]; print("with best bound == OPT:",len(eq),eq,[score(N) for N in eq])
print("histogram of the score minus the best bound over the designs:",sorted(Counter(score(N)-B(N) for N in cands).items()))
# every subset of four primes read (all but one prime): bound = score with the best class of the missing prime
def B4(N):
    best=0
    for miss in mods:
        base={r:N%r for r in mods if r!=miss}
        best=max(best,min(left_cls({**base,miss:a}) for a in range(miss)))
    return best
b4=[N for N in cands if B4(N)<OPT]; print("not excluded when all classes but one are read:",len(b4),b4)
