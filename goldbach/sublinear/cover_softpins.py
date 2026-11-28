#!/usr/bin/env python3
"""Hard pins, soft lists, and the soft lists a lattice can impose: rows per nat of constraint on the real 200,000 cover.

    python3 cover_softpins.py

Soft constraints that a lattice can impose: N mod s in an arithmetic progression of classes (an interval after multiplying by a unit u).
For the rows of the real 200,000 cover and each prime s after 463: the best (u, start) for a kept fraction phi of the classes,
rows gained per member at that prime against the mean, and rows per nat of constraint ln(1/phi).  Compared with: the single best class
(a hard pin), and the unconstrained best set of phi*s classes (what the ideal population uses; not constructible).
"""
import sys, math, numpy as np
f = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'fscan', 'cover', 'starts', 'q200000_m89.txt'); Q = 200000
line = [l for l in open(f) if l.startswith("COVER")][0].split(); cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
sv = np.ones(Q, dtype=bool); sv[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False; q = np.nonzero(sv)[0]; alive = np.ones(len(q), dtype=bool)
for r, a in cov: alive &= (q % r) != a
rows = q[alive]; n = len(rows)
print(f"rows {n}")
print("prime s | kept fraction | AP-interval: mean rows per kept class - mean, rows per nat | best arbitrary set of that size: gain, rows per nat | single best class: gain, rows per nat")
for s in (467, 541, 701, 997, 1499, 1999):
    w = np.bincount(rows % s, minlength=s).astype(float); mu = n / s
    best1 = w.max() - mu
    ws = np.sort(w)[::-1]
    for phi in (0.75, 0.5, 0.25, 0.1):
        L = int(round(phi * s)); bestap = -1.0
        idx = np.arange(s)
        for u in range(1, (s + 1) // 2):                      # u and -u give the same set of intervals
            wp = w[(idx * u) % s]; cs = np.concatenate([[0.0], np.cumsum(np.concatenate([wp, wp]))])
            m = (cs[L:L + s] - cs[:s]).max()
            if m > bestap: bestap = m
        g_ap = bestap / L - mu; g_any = ws[:L].sum() / L - mu; c = math.log(1 / phi)
        print(f"{s} | {phi} | {g_ap:.3f}, {g_ap / c:.2f} | {g_any:.3f}, {g_any / c:.2f} | {best1:.2f}, {best1 / math.log(s):.2f}", flush=True)
