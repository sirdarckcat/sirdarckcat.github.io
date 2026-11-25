"""The smallest instance (rows below 160, moduli 3..13, even N < 840), design 3, 5, 7: the free bound of each of the
105 cells (the least number of rows left over all classes modulo 11 and 13), the cells below and at the optimum."""
rows=[q for q in range(3,160,2) if all(q%d for d in range(3,int(q**0.5)+1,2))]
assert len(rows)==36
def left(N, mods=(3,5,7,11,13)): return sum(all(q%r!=N%r for r in mods) for q in rows)
def leftWith(c,a,b): return sum(q%3!=c%3 and q%5!=c%5 and q%7!=c%7 and q%11!=a and q%13!=b for q in rows)
OPT=min(left(N) for N in range(0,840,2)); print("OPT",OPT,[N for N in range(0,840,2) if left(N)==OPT])
cells=range(0,210,2); LB={c:min(leftWith(c,a,b) for a in range(11) for b in range(13)) for c in cells}
cov={c:left(c,(3,5,7)) for c in cells}
act={c:sorted(left(N) for N in range(c,840,210)) for c in cells}
from collections import Counter
print("LB histogram",sorted(Counter(LB.values()).items()))
below=[c for c in cells if LB[c]<OPT]; print("cells with LB<OPT",below,[(LB[c],cov[c],act[c]) for c in below])
eq=[c for c in cells if LB[c]==OPT]; print("cells with LB==OPT",eq,[(cov[c],act[c]) for c in eq])
print("cover value histogram",sorted(Counter(cov.values()).items()))
print("cell of 578:",578%210,LB[578%210],cov[578%210],act[578%210])
# which (a,b) achieve LB in the below cells, and is any candidate N<840... (N' in full period achieving it)
for c in below:
    best=[(a,b) for a in range(11) for b in range(13) if leftWith(c,a,b)==LB[c]]
    # the N' in [0,30030) with these classes
    sol=[N for N in range(c,30030,210) if (N%11,N%13) in best]
    print(c,"LB",LB[c],"class pairs",best,"least N with them",sol[:4])
