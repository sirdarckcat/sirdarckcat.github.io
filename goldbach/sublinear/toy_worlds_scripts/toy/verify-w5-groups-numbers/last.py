import math, numpy as np
from math import prod
from base import *
def widths(mods, X):
    out = []
    for cut in range(1, len(mods)):
        PI = prod(mods[:cut]); PIc = prod(mods[cut:]); fut = {}
        for x in range(X): fut.setdefault(x % PI, set()).add(x % PIc)
        out.append((len({frozenset(v) for v in fut.values()}), min(PI, PIc, X)))
    return out
for mods, X in (([3, 5, 7, 11, 13], 7000), ([13, 11, 7, 5, 3], 300), ([5, 7, 11, 13, 17], 40000), ([7, 3, 13, 5, 11, 2], 2000)):
    print(mods, X, widths(mods, X))
dl = {r: dlt_table(r) for r in cprimes}
for j, sg in ((5, 4), (6, 5), (5, 2), (4, 3)):
    later = LATER[:j]; hit = {s: hit_table(s) for s in later}
    nc = sum(int((dl[r] <= sg).sum()) for r in cprimes if (dl[r] <= sg).sum() > 1) + sum(int(((hit[s].max() - hit[s]) <= sg).sum()) for s in later)
    ncoord = sum(1 for r in cprimes if (dl[r] <= sg).sum() > 1) + j
    E = sg + 1 + j; P = M * prod(later); B = -(-E * P // X)
    print(f"j={j} sigma={sg}: coordinates {ncoord}, classes kept {nc}, B = {B} ({B * X / P:.2f} e^D), B*classes = {B * nc:.4g}")
# exponents
import math
D = {j: math.log(M * prod(LATER[:j])) - 200 * math.log(10) for j in range(3, 10)}
print("ln(lists)/D at sigma*:", [round(math.log(n) / D[j], 3) for j, n in ((4, 571), (5, 36982), (6, 17779831))], "j=7: lists only", round(math.log(62019102) / D[7], 3), "with scanned members", round(math.log(62019102 + 42757956) / D[7], 3), "; full lists to slack 7 (206592422 + 1244986255):", round(math.log(206592422 + 1244986255) / D[7], 3))
print("lists/e^(D/2):", [round(n / math.exp(D[j] / 2), 1) for j, n in ((4, 571), (5, 36982), (6, 17779831), (7, 62019102), (7, 62019102 + 42757956))], " lists/e^D j=7:", (62019102) / math.exp(D[7]), (62019102 + 42757956) / math.exp(D[7]))
print("D reached by 1e9 entries at c e^(D/2): c=10:", 2 * math.log(1e8), " c=2.5:", 2 * math.log(4e8), "; D(521), D(523) =", round(D[8], 2), round(D[9], 2), "; entries needed at D(523): 2.5x, 10x =", 2.5 * math.exp(D[9] / 2), 10 * math.exp(D[9] / 2))
p = 2 * prod(r / (r - 1) for r in cprimes) / (200 * math.log(10)); print("p", p, "-ln(1-p)", -math.log(1 - p), "1502 rows ->", -1502 * math.log(1 - p))
print("4(b) at j=5, eps=1: X/(Lam^2/4P + Lam/T + 1) in units of e^D:", 1 / (2.25 + 3 * math.exp(D[5]) / prod(LATER[:5])), "; e^D/(18 eps) vs B: ratio 18*E at E=8:", 144)
