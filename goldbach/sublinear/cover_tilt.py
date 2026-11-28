#!/usr/bin/env python3
"""The mechanism of the price recursion, checked on complete covers themselves.

    python3 cover_tilt.py dump.txt Q [ncovers=1500]

dump.txt: "COVER k r:a ..." lines of complete covers at the target Q (e.g. PT_DUMP of ../fscan/cover/ptcover with
PT_KDUMP=0).  Along each cover, modulus by modulus, smallest first: the rows still alive before the modulus, the
variance over the mean of the alive rows in its nonzero classes, and the rows the chosen class strikes over the mean
of a class.  Printed against the same for random vectors and against the recursion of cover_price_hl.py, in which
the chosen class strikes exp(v p) times the mean (v the dispersion for random vectors, p the price after the modulus).
"""
import sys, math, random
import numpy as np, cover_price as cp, cover_price_hl as hl
dump, Q = sys.argv[1], int(sys.argv[2]); ncov = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
covers = []
for l in open(dump):
    t = l.split()
    if t and t[0] == "COVER": covers.append([tuple(map(int, u.split(":"))) for u in t[2:]])
random.Random(1).shuffle(covers); covers = covers[:ncov]
mods = [r for r, a in covers[0]]; x = mods[-1]
s_ = np.ones(Q, dtype=bool); s_[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if s_[i]: s_[i * i::i] = False
rows = np.nonzero(s_)[0]; rows = rows[rows > 2]; res = {r: rows % r for r in mods}
def walk(cover):
    alive = np.ones(len(rows), dtype=bool); out = []
    for r, a in cover:
        cnt = np.bincount(res[r][alive], minlength=r)[1:]            # nonzero classes
        A = int(alive.sum()); mu = cnt.mean(); var = cnt.var()
        out.append((A, var / mu if mu > 0 else np.nan, cnt[a - 1] if a > 0 else 0, mu, cnt.max()))
        alive &= res[r] != a
    return out
T = np.array([walk(c) for c in covers], dtype=float)                  # tilted ensemble
rng = random.Random(2)
Rn = np.array([walk([(r, rng.randrange(1, r)) for r in mods]) for _ in range(300)], dtype=float)
ps = hl.PairSums(x, Q); vs = hl.clamp(ps.dispersions(Q)[0]); piQ = cp.odd_primes_below(Q)
# prices after each modulus by the recursion (forward from the largest feasible start price)
p0, _ = hl.start_price(mods, vs, Q); p = p0; pr = []
for s, v in zip(mods, vs):
    top = math.log(s - 1) / v; lo, hi = p, top
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if mid - math.expm1(v * mid) / (v * (s - 1)) < p: lo = mid
        else: hi = mid
    p = 0.5 * (lo + hi); pr.append(p)
print(f"# {len(covers)} complete covers at Q = {Q} on {len(mods)} moduli; {len(rows)} rows; recursion start price {p0:.4f}")
print("modulus | rows alive before it: complete covers / random vectors | dispersion: covers / random / pair sum | rows struck by the chosen class over the class mean: covers / recursion exp(v p) | fullest class over mean: covers")
for i in list(range(0, 12)) + list(range(12, len(mods), 6)) + [len(mods) - 1]:
    s = mods[i]; t = T[:, i, :]; r = Rn[:, i, :]
    print(f"{s} | {t[:,0].mean():.1f} / {r[:,0].mean():.1f} | {np.nanmean(t[:,1]):.3f} / {np.nanmean(r[:,1]):.3f} / {vs[i]:.3f} | {(t[:,2] / t[:,3]).mean():.2f} / {math.exp(vs[i] * pr[i]):.2f} | {(t[:,4] / t[:,3]).mean():.2f}")
