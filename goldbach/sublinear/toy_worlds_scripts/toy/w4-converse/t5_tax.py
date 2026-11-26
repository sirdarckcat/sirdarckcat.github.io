#!/usr/bin/env python3
"""t5: what an enumerator is worth on the real tables as a function of its price per constrained prime.
Model of an enumerator: it may impose at each later prime s in [467, 5000] any list A_s (no structure asked of it: an upper
bound for every structured family); a list of j classes costs ln(s/j) + t nats of room (t = the method's tax per prime) and
gains g_s(j) = (mean of the j heaviest classes) - (mean of the table) first-order strikes over a random member.
     max  sum_s g_s(j_s)   subject to   sum over the primes used of (ln(s/j_s) + t) <= B.
Solved by Lagrangian relaxation: for a multiplier lam each prime takes max_j [g - lam (ln(s/j) + t)]_+ ; the value
sum_s max(...) + lam B is an upper bound on the optimum for every lam >= 0, and the choice at the lam where the cost meets B is
feasible (a lower bound).  Chinese remaindering = lists of one class at cost ln s (t = 0, j = 1 only).
Rows are converted at 0.0243 nats a row (first order: repeats ignored, so an overestimate)."""
import math, numpy as np
from common import *
cov, rows = load(); LP = later_primes(464, 5000)
curves = []
for s in LP:
    t = np.sort(table(rows, s))[::-1].astype(float); j = np.arange(1, s + 1); g = np.cumsum(t) / j - t.mean(); c = np.log(s / j)
    curves.append((s, g[:-1], c[:-1]))
def solve(B, tax, pins_only=False):
    def at(lam):
        gain = cost = dual = 0.0; used = 0
        for s, g, c in curves:
            if pins_only: v = g[:1] - lam * (c[:1] + tax)
            else: v = g - lam * (c + tax)
            i = int(np.argmax(v))
            if v[i] > 0: gain += g[i]; cost += c[i] + tax; dual += v[i]; used += 1
        return gain, cost, dual + lam * B, used
    lo, hi = 1e-6, 50.0
    for _ in range(60):
        mid = math.sqrt(lo * hi); g, c, d, u = at(mid)
        if c > B: lo = mid
        else: hi = mid
    g, c, d, u = at(hi); ub = min(at(x)[2] for x in (lo, hi, hi * 1.01, lo * 0.99))
    return g, c, ub, u, hi
print(f"primes {len(LP)} in [467, 5000]; gains in first-order rows (x 0.0243 = nats)")
print("  B (nats)  method                         feasible gain (rows)  cost used  primes used   upper bound (rows)   nats (upper)   rows per nat of room")
for B in (4.2, 8.0, 12.0, 16.88, 50.0, 150.0):
    for name, tax, po in (("any lists, tax 0 (ideal)", 0.0, False), ("any lists, tax 0.25", 0.25, False), ("any lists, tax 0.5", 0.5, False), ("any lists, tax 1", 1.0, False),
                          ("any lists, tax 2", 2.0, False), ("any lists, tax 3", 3.0, False), ("pins (Chinese remainder)", 0.0, True)):
        g, c, ub, u, lam = solve(B, tax, po)
        print(f"  {B:6.2f}    {name:28s}   {g:8.2f}            {c:7.2f}     {u:4d}          {ub:8.2f}          {ub * 0.0243:6.3f}       {g / max(c, 1e-9):6.3f}")
    print()
print("break-even tax (any lists with tax t against pins with none), feasible gains:")
for B in (16.88, 50.0, 150.0):
    print(f"  B = {B}: pins {solve(B, 0.0, True)[0]:.2f};  " + "  ".join(f"t={t}: {solve(B, t, False)[0]:.2f}" for t in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5)))
