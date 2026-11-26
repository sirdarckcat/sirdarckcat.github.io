#!/usr/bin/env python3
"""Is the count of live rows in a class c modulo a later prime r predictable from the multiplicative structure of c?
For each prime r in (463, 2000]: the table w(c) = rows q = c (mod r) of the 200,000 cover, relabelled by discrete logarithm
(c = g^j), and its Fourier transform over the cyclic group of order r - 1, i.e. the character sums sum_q chi(q) over the rows.
Under the null (rows fall in classes independently) |sum|^2 / n is exponential with mean about 1 - n/(r-1)... (multinomial)."""
import sys, math, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import cover_record as cr
rows, p = cr.load(cr.S + "q200000_m89.txt"); rows = rows[rows < 200000]; n = len(rows)
def primitive_root(r):
    fac = []; m = r - 1; d = 2
    while d * d <= m:
        if m % d == 0:
            fac.append(d)
            while m % d == 0: m //= d
        d += 1
    if m > 1: fac.append(m)
    for g in range(2, r):
        if all(pow(g, (r - 1) // f, r) != 1 for f in fac): return g
rng = np.random.default_rng(1)
res = []; lowres = {2: [], 3: [], 4: [], 5: [], 6: []}; maxes = []; nullmaxes = []; addmaxes = []
for r in [int(x) for x in cr.PR[(cr.PR > 463) & (cr.PR < 2000)]]:
    g = primitive_root(r); dlog = np.zeros(r, dtype=np.int64); x = 1
    for j in range(r - 1): dlog[x] = j; x = x * g % r
    c = rows % r; nz = c[c != 0]; m = len(nz)
    a = np.bincount(dlog[nz], minlength=r - 1).astype(float)
    P = np.abs(np.fft.fft(a)) ** 2 / m                      # multiplicative characters, k = 0 trivial
    res.append(P[1:].mean()); maxes.append(P[1:].max() / math.log(r - 2))
    for d in lowres:
        if (r - 1) % d == 0:
            ks = [(r - 1) // d * t for t in range(1, d) if math.gcd(t, d) == 1]
            lowres[d].append(np.mean([P[k] for k in ks]))
    # null: the same number of rows thrown into nonzero classes at random
    b = np.bincount(rng.integers(0, r - 1, size=m), minlength=r - 1).astype(float)
    Pn = np.abs(np.fft.fft(b)) ** 2 / m; nullmaxes.append(Pn[1:].max() / math.log(r - 2))
    # additive transform of the same table (class index as an integer)
    t = np.bincount(c, minlength=r).astype(float); Pa = np.abs(np.fft.fft(t)) ** 2 / n; addmaxes.append(Pa[1:].max() / math.log(r - 1))
print(f"rows {n}; primes r in (463, 2000): {len(res)}")
print(f"multiplicative characters: mean normalised power over nontrivial characters {np.mean(res):.4f} (noise: 1.000 - small); largest power / ln(number of characters): mean {np.mean(maxes):.3f}, max {np.max(maxes):.3f}; the same for random rows: mean {np.mean(nullmaxes):.3f}, max {np.max(nullmaxes):.3f}")
for d, v in lowres.items():
    if v: print(f"  characters of order {d}: mean normalised power {np.mean(v):.3f} +- {np.std(v) / math.sqrt(len(v)):.3f} over {len(v)} primes (noise 1)")
print(f"additive characters (class index as an integer): largest power / ln r: mean {np.mean(addmaxes):.3f}, max {np.max(addmaxes):.3f}")
