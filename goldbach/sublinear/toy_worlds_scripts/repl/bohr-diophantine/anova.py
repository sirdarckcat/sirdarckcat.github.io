#!/usr/bin/env python3
"""(b) How much of the exact sieve count S (to 10^8, real window, every member) is a function of ONE coordinate phi(k)?
eta2(phi) = Var(E[S | phi]) / Var(S); for a coordinate with R values that knows nothing, eta2 * (K - 1) is chi-square-like
with mean R - 1 (chance = (R - 1)/(K - 1)).   F = eta2/(R-1) / ((1-eta2)/(K-R)) is 1 +- sqrt(2/(R-1)) under chance."""
import math, numpy as np
from base import *
S = np.fromfile("S_100000000.u16", dtype=np.uint16).astype(np.float64); mu = S.mean(); V = S.var(); k = np.arange(K, dtype=np.int64)
W = mu / len(ROWS)
def eta(phi, R):
    cnt = np.bincount(phi, minlength=R).astype(np.float64); sm = np.bincount(phi, weights=S, minlength=R)
    ok = cnt > 0; R_ = int(ok.sum())
    e = float((cnt[ok] * (sm[ok] / cnt[ok] - mu) ** 2).sum() / (K * V))
    F = e / (R_ - 1) / ((1 - e) / (K - R_))
    return e, R_, F
print(f"K = {K}; S: mean {mu:.3f} var {V:.3f}; share of rows surviving W = {W:.6f}")
print("coordinate | values R | eta2 | chance (R-1)/(K-1) | F (1 = chance) | sd of F under chance | first-order prediction W'^2 Var(g_s)/Var(S)")
tot = 0.0; first12 = []
def line(name, phi, R, pred=None):
    e, R_, F = eta(phi, R)
    print(f"{name} | {R_} | {e:.3e} | {(R_ - 1) / (K - 1):.3e} | {F:.3f} | {math.sqrt(2 / (R_ - 1)):.3f} | {'' if pred is None else f'{pred:.3e}'}", flush=True)
    return e
later = [int(s) for s in primes_upto(560) if s > 463]
for s in later + [1009, 10007, 100003, 1000003]:
    f, g = tables(s); pred = (W / (1 - 1 / s)) ** 2 * g.var() / V
    e = line(f"k mod {s} (a later prime)", k % s, s, pred)
    if s in later: first12.append((s, e))
print("-- moduli that are not multiples of a later prime (the window structure offers them; the score should not see them)")
for R in (2, 3, 5, 7, 11, 13, 30, 210, 466, 468, 480, 512, 1000, 4096, 30030, 65536, 467 * 479 + 1):
    line(f"k mod {R}", k % R, R)
print("-- digits")
line("floor(k/467) mod 479 (second mixed-radix digit)", (k // 467) % 479, 479)
line("floor(k/(467*479)) (top mixed-radix digit)", k // (467 * 479), K // (467 * 479) + 1)
line("floor(k/2^12) mod 2^9", (k >> 12) & 511, 512)
line("floor(k/2^15) (top binary digits)", k >> 15, (K >> 15) + 1)
line("k mod 2^9", k & 511, 512)
print("-- blocks (residues modulo products of later primes)")
e2 = line("k mod 467*479", k % (467 * 479), 467 * 479)
print(f"   sum of the two primes' eta2: {first12[0][1] + first12[1][1]:.3e}; chance for the block {(467 * 479 - 1) / (K - 1):.3e}; block minus primes minus chance for the interaction part {(e2 - first12[0][1] - first12[1][1] - (466 * 478) / (K - 1)):.2e}")
print("-- the exact trade-off in residue coordinates: T = the first J later primes; D = max(0, ln prod s - ln K); share of Var(S) that is separable on T")
acc = 0.0; lp = 0.0
for j, (s, e) in enumerate(first12, 1):
    acc += e - (s - 1) / (K - 1); lp += math.log(s)
    print(f"   J = {j}: D = {max(0.0, lp - math.log(K)):.2f} nats; separable share {acc:.4%}")
# the same share by the first-order formula for deeper sets of primes
print("-- by the first-order formula (checked above on 16 primes): primes to z | D | share of Var(S)")
for z in (509, 1000, 2000, 5000, 20000, 200000, 10 ** 6):
    ps = [int(s) for s in primes_upto(z) if s > 463]; acc = 0.0; lp = 0.0
    for s in ps:
        f = np.bincount(ROWS % s, minlength=s); acc += (W / (1 - 1 / s)) ** 2 * f.var() / V; lp += math.log(s)
    print(f"   z = {z}: {len(ps)} primes; D = {max(0.0, lp - math.log(K)):.0f}; share {acc:.3%}")
