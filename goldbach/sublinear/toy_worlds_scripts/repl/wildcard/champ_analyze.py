#!/usr/bin/env python3
"""Every even N <= 2*10^10 with g(N) >= 500 (from champ.c): is there structure in the deep N that is NOT a function of
N modulo primes?  Under Hardy-Littlewood the chance that N - q is prime depends on N only through N mod r (r prime) and ln N.
So, inside a class of N mod r, the sub-classes modulo r^2 must hold equal shares of the hits; N mod 2^j must be uniform;
digit-sum parities must be fair.  Chi-square of each, at four levels.  Positive control: N mod 3, 5, 7 themselves."""
import numpy as np, math
from math import erfc
d = np.fromfile("big/hits_2e10.bin", dtype=np.dtype([("N", "<u8"), ("g", "<u4")]))
N = d["N"].astype(np.int64); g = d["g"]
print("hits g>=500:", len(N), " max g", g.max(), "at", N[g.argmax()])
def chi2_p(x, k):                        # upper tail of chi-square with k dof (Wilson-Hilferty)
    if k == 0: return 1.0
    z = ((x / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k)); return 0.5 * erfc(z / math.sqrt(2))
def sub(Nh, r, e=2):
    """chi-square of the sub-classes modulo r^e inside each class modulo r (pooled); also the largest relative deviation"""
    chi = 0; dof = 0; worst = 0
    for a in range(r):
        m = Nh[Nh % r == a]
        if len(m) < 50 * r: continue
        c = np.bincount((m % r ** e) // r, minlength=r ** (e - 1)).astype(float); ex = c.sum() / len(c)
        chi += ((c - ex) ** 2 / ex).sum(); dof += len(c) - 1; worst = max(worst, np.abs(c / ex - 1).max())
    return chi, dof, worst
def flat(v, m):
    c = np.bincount(v, minlength=m).astype(float); ex = c.sum() / m
    return ((c - ex) ** 2 / ex).sum(), m - 1, np.abs(c / ex - 1).max()
def popc(a):
    a = a.copy(); s = np.zeros(len(a), dtype=np.int64)
    while a.any(): s += a & 1; a >>= 1
    return s
def dsum(a, b):
    a = a.copy(); s = np.zeros(len(a), dtype=np.int64)
    while a.any(): s += a % b; a //= b
    return s
for L in (500, 700, 1000, 1300):
    Nh = N[g >= L]; n = len(Nh)
    print(f"\nlevel g >= {L}: {n} hits; relative sd of a class share with 1/3 of the hits: {math.sqrt(3 / n):.4f}")
    # positive controls: residues modulo primes
    for r in (3, 5, 7):
        c = np.bincount(Nh % r, minlength=r); print(f"  control N mod {r}: shares", " ".join(f"{x / n:.4f}" for x in c))
    for r in (3, 5, 7, 11, 13):
        chi, dof, w = sub(Nh, r); print(f"  N mod {r}^2 inside N mod {r}: chi2 {chi:.1f} on {dof} dof, p = {chi2_p(chi, dof):.3f}, largest relative deviation {w:.4f}")
    chi, dof, w = sub(Nh, 3, 3); print(f"  N mod 27 inside N mod 3: chi2 {chi:.1f} on {dof} dof, p = {chi2_p(chi, dof):.3f}, largest relative deviation {w:.4f}")
    for j in (2, 3, 4, 6):
        chi, dof, w = flat(((Nh >> 1) % 2 ** (j - 1)).astype(np.int64), 2 ** (j - 1)); print(f"  N mod 2^{j}: chi2 {chi:.1f} on {dof} dof, p = {chi2_p(chi, dof):.3f}, largest relative deviation {w:.4f}")
    for name, v in (("binary digit sum mod 2 (Thue-Morse)", popc(Nh) % 2), ("decimal digit sum mod 2", dsum(Nh, 10) % 2), ("base-7 digit sum mod 4", dsum(Nh, 7) % 4), ("base-3 digit sum mod 4", dsum(Nh, 3) % 4)):
        m = int(v.max()) + 1; c = np.bincount(v, minlength=m)
        # base-3 and base-7 digit sums have the parity of N (even): only the even residues occur
        occ = c[c > 0].astype(float); ex = occ.sum() / len(occ); chi = ((occ - ex) ** 2 / ex).sum()
        print(f"  {name}: counts {list(c)}, chi2 {chi:.1f} on {len(occ) - 1} dof, p = {chi2_p(chi, len(occ) - 1):.3f}, largest relative deviation {np.abs(occ / ex - 1).max():.4f}")
# how concentrated are the hits on the best class at each small prime (what cover first sees)
print()
for L in (1000, 1300, 1600):
    Nh = N[g >= L]; s = np.ones(len(Nh), dtype=bool); out = []
    for r in (3, 5, 7, 11, 13, 17, 19, 23, 29):
        c = np.bincount(Nh % r, minlength=r); best = c.argmax(); s &= (Nh % r == best); out.append(f"{r}:{best} {c[best] / len(Nh):.2f} (all so far {s.mean():.3f})")
    print(f"g >= {L} ({len(Nh)} hits): share in the most popular class, prime by prime, and in all of them together:\n   " + "; ".join(out))
