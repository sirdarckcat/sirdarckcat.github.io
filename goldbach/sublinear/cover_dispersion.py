#!/usr/bin/env python3
"""How evenly the alive rows fill the classes of a modulus, against the formula used by cover_price.py.

    python3 cover_dispersion.py x Q trials

Rows are the odd primes below Q.  For `trials` random vectors of nonzero classes on the odd primes up to x, taken in
increasing order, the rows alive before modulus s (in no class of a smaller modulus) are counted in each nonzero class
of s; printed for a selection of s: the mean count, the measured variance/mean, and

    1 - 6 phi(s) (s/(s-1)) (pi(Q)/Q) ln(Q/(6 s)),     phi(s) = prod over odd primes t < s of (1 - 1/(t-1)),

which is what the Hardy-Littlewood count of prime pairs gives with the second-order term of the average of singular
series (see README, "How many complete covers there are").  The formula is for s large enough that the mean count is
small against Q/(6 s); it fails for the smallest moduli.
"""
import sys, math, numpy as np
x, Q, T = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(1)
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
mods = [int(p) for p in primes(x) if p > 2]; rows = primes(Q - 1); rows = rows[rows > 2]
res = {s: rows % s for s in mods}; acc = {s: [0.0, 0.0] for s in mods}
for t in range(T):
    alive = np.ones(len(rows), dtype=bool)
    for s in mods:
        K = np.bincount(res[s][alive], minlength=s)[1:].astype(float)
        acc[s][0] += K.var(); acc[s][1] += K.mean()
        alive &= res[s] != int(rng.integers(1, s))
print(f"x = {x}, Q = {Q}, {len(rows)} rows, {T} random vectors")
print("modulus s | mean alive rows per class | variance/mean measured | formula")
phi = 1.0; want = set(mods[i] for i in sorted(set(list(range(0, len(mods), max(1, len(mods) // 14))) + [len(mods) - 1])))
for s in mods:
    if s in want:
        f = 1 - 6 * phi * (s / (s - 1)) * (len(rows) / Q) * math.log(max(Q / (6 * s), 1.0))
        print(f"{s} | {acc[s][1] / T:.2f} | {acc[s][0] / acc[s][1]:.3f} | {f:.3f}")
    phi *= 1 - 1 / (s - 1)
