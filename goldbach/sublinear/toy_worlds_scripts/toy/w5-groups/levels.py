#!/usr/bin/env python3
"""Exact level-set counts of the two half-scores (World 1 counting by generating functions) and what they predict.

A[k]  = number of class vectors of the 89 cover primes with first-order cost exactly k rows above the cover   (k <= KMAX)
Nj[t] = number of class vectors of the j later primes whose hits are exactly t below the maximum Gmax_j
pairs(sigma) = sum_{k+t <= sigma} A[k] Nj[t] = points of G with score <= n0 - Gmax + sigma (unconstrained)
expected feasible = pairs * X/P.  Lists a certified meet in the middle needs at slack sigma: A(<=sigma), Nj(<=sigma).
"""
import common as C, numpy as np, math, sys
KMAX = 16
ct = C.cover_tables()
A = [1] + [0] * KMAX
for r, d in ct.items():
    h = np.bincount(d[d <= KMAX], minlength=KMAX + 1).tolist()
    A = [sum(A[i] * h[k - i] for i in range(k + 1)) for k in range(KMAX + 1)]
print("A[k], covers at first-order cost exactly k:", A)
print("ln cumulative A:", [round(math.log(sum(A[:k + 1])), 2) for k in range(KMAX + 1)])
for j in range(1, 9):
    js = C.later_primes(j); lt = C.later_tables(js)
    Nj = [1]
    for s in js:
        h = np.bincount(lt[s].max() - lt[s]).tolist()
        new = [0] * (len(Nj) + len(h) - 1)
        for a, x in enumerate(Nj):
            for b, y in enumerate(h): new[a + b] += x * y
        Nj = new
    Gmax = sum(int(lt[s].max()) for s in js)
    P = C.M * math.prod(js); D = math.log(P) - math.log(C.X)
    print(f"\nj={j} later {js[-1]}: D = {D:.3f}, e^D = {math.exp(D):.4g}, e^(D/2) = {math.exp(D/2):.4g}, Gmax = {Gmax}, unconstrained optimum {C.n0 - Gmax}")
    cumA = np.cumsum(A, dtype=object); cumN = np.cumsum(Nj[:KMAX + 1], dtype=object)
    for sig in range(0, KMAX + 1):
        pairs = sum(A[k] * int(cumN[sig - k]) for k in range(sig + 1) if sig - k < len(cumN))
        exp = pairs * math.exp(-D)
        print(f"  slack {sig:2d}: points {pairs:.4g}  expected below X {exp:.4g}   lists: covers {int(cumA[sig]):.4g}, later {int(cumN[sig]):.4g}  sum {int(cumA[sig]) + int(cumN[sig]):.4g}")
        if exp > 3e4: break
