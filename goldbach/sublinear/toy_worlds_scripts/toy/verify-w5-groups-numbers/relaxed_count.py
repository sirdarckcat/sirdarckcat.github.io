# Size of the relaxed set R (Theorem 3) restricted to excess <= sigma, computed WITHOUT the dense programme:
# two lists of rounded partial sums mod B (cover side, later side), matched on the target arc.  usage: j sigma eps_num eps_den
import sys, math, numpy as np
from fractions import Fraction
from base import *
j, sigma, en, ed = map(int, sys.argv[1:5]); eps = Fraction(en, ed)
later = LATER[:j]; T = prod(later); P = M * T
dl = {r: dlt_table(r) for r in cprimes}; hit = {s: hit_table(s) for s in later}
E = sigma + sum(1 for r in cprimes if (dl[r] == 0).sum() > 1) + j
B = int(math.ceil(Fraction(E * P, X) / eps))
def levels(tabs):   # tabs: list of (r, base, cost array)
    lev = [np.zeros(1, dtype=np.int64)] + [np.zeros(0, dtype=np.int64) for _ in range(sigma)]
    for r, b, cost in tabs:
        u = pow((P // r) % r, -1, r)
        add = [[] for _ in range(sigma + 1)]
        for c in range(r):
            dc = int(cost[c])
            if dc > sigma: continue
            sh = (B * (((c - b) * u) % r)) // r
            for l in range(sigma + 1 - dc):
                if len(lev[l]): add[l + dc].append((lev[l] + sh) % B)
        lev = [np.concatenate(a) if a else np.zeros(0, dtype=np.int64) for a in add]
    return lev
CL = levels([(r, cover[r], dl[r]) for r in cprimes])
LL = levels([(s, N0 % s, hit[s].max() - hit[s]) for s in later])
lo = Fraction(-B * N0, P) - E; hi = Fraction(B * (X - N0), P)
nlo = math.floor(lo) + 1; nhi = math.ceil(hi) - 1; width = nhi - nlo + 1; assert width < B
total = 0
for d in range(sigma + 1):
    if len(LL[d]) == 0: continue
    Ls = np.sort(LL[d])
    for c in range(sigma + 1 - d):
        a = CL[c]
        if len(a) == 0: continue
        s0 = (nlo - a) % B; s1 = s0 + width - 1          # need b in [s0, s1] cyclically
        cnt = np.searchsorted(Ls, np.minimum(s1, B - 1), side="right") - np.searchsorted(Ls, s0, side="left")
        w = s1 >= B
        cnt = cnt + np.where(w, np.searchsorted(Ls, s1 - B, side="right"), 0)
        total += int(cnt.sum())
print(f"j={j} sigma={sigma} eps={eps}: E={E} B={B}; targets {width}; cover vectors {sum(len(x) for x in CL)}, later vectors {sum(len(x) for x in LL)}; relaxed points with excess <= sigma: {total}")
