#!/usr/bin/env python3
"""The search problem in miniature, exactly (no model): every even N below X is enumerated by toy_exact.c.

    python3 toy_compare.py exact_histogram.txt [tempering_output.txt]

1. Two search orders are compared by the number of N that must be examined per true success (g(N) >= Q):
   "cover first": N in increasing order of the rows left at the Chinese-remainder line z1 (what a cover search does);
   "ideal to z":  N in increasing order of the rows left at the deeper depth z.
2. With a tempering output of ideal_tilt.c for the same Q and z: the number of N by rows left at depth z predicted
   from residue vectors alone, against the exact count (the assumption behind Result 3).
"""
import math, sys
import numpy as np

lines = open(sys.argv[1]).read().split("\n")
par = dict(t.split("=") for t in lines[0].split()[1:5]); X, Q, z1, z = int(par["X"]), int(par["Q"]), int(par["z1"]), int(par["z"])
rows = [tuple(map(int, l.split())) for l in lines[1:] if l.strip()]
tot = sum(r[2] + r[3] for r in rows); succ = sum(r[3] for r in rows)
print(f"# X = {X}, Q = {Q}: {tot} even N with no prime factor in 3..29, {succ} of them with g(N) >= {Q} (one in e^{math.log(tot / succ):.2f})")

def order(idx, name):
    by = {}
    for r in rows:
        c = by.setdefault(r[idx], [0, 0]); c[0] += r[2] + r[3]; c[1] += r[3]
    n = s = 0; out = []
    for k in sorted(by):
        n += by[k][0]; s += by[k][1]; out.append((k, n, s))
    print(f"\n{name}:\n   rows left <=   N examined   successes found   N per success")
    shown = 0
    for k, n, s in out:
        if s > 0 and (shown < 9 or s == succ):
            print(f"   {k:10d} {n:12d} {s:12d} {n / s:16.0f}"); shown += 1
            if s == succ: break
    return out

a = order(0, f"cover first (rows left at depth z1 = {z1})")
b = order(1, f"ideal to depth z = {z}")
def cost(out, target):                     # N examined to find `target` successes, interpolating inside a level
    pn = ps = 0
    for k, n, s in out:
        if s >= target: return pn + (n - pn) * (target - ps) / (s - ps)
        pn, ps = n, s
print("\n   successes wanted   cover first   ideal to z   ratio   (nats)")
for t in (1, 3, 10, 30, 100, succ):
    ca, cb = cost(a, t), cost(b, t); print(f"   {t:14d} {ca:14.0f} {cb:12.0f} {ca / cb:7.1f}   ({math.log(ca / cb):.2f})")

if len(sys.argv) > 2:
    from ideal_tilt import read, wham, primes_upto
    tp, betas, hists, info = read(sys.argv[2])
    assert int(tp["Q"]) == Q and int(tp["z"]) == z
    E, lng, lnZ, its, _ = wham(betas, hists, float(tp["ln(states)"]))
    odd = primes_upto(z)[1:].astype(float); lnper = math.log(X / 2) - float(np.sum(np.log(odd)))
    exact = {}
    for r in rows: exact[r[1]] = exact.get(r[1], 0) + r[2] + r[3]
    print(f"\nNumber of N by rows left at depth {z}: exact count against the prediction from residue vectors (ln of N per vector {lnper:.2f})")
    print("   rows left   exact   predicted   ratio  |  cumulative exact   predicted   ratio")
    ce = 0; cp = 0.0
    for k in range(min(exact), min(exact) + 16):
        i = k - int(E[0]); pred = math.exp(lng[i] + lnper) if 0 <= i < len(E) and np.isfinite(lng[i]) else 0.0
        ex = exact.get(k, 0); ce += ex; cp += pred
        print(f"   {k:6d} {ex:10d} {pred:11.1f} {ex / pred if pred else float('nan'):7.2f}  | {ce:12d} {cp:13.1f} {ce / cp if cp else float('nan'):7.2f}")
