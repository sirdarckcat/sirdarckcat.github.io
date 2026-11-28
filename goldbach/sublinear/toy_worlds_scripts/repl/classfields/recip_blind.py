#!/usr/bin/env python3
"""Reciprocity symbols of N - q on the real 200,000 cover: do they know anything about primality?

Members N = N0 + k*M of the real cover (random k below 2^24.35), all 1,502 rows; a row survives if N - q has no prime
factor s with 463 < s <= Z; every survivor gets a base-2 Fermat test.  For each survivor a list of cheap +-1 symbols
is computed, and the prime rate of the survivors is compared between the two values of each symbol.

Symbols (all at most 1/50 of a Fermat test):
  J(a | n) for primes a just beyond the sieve depth Z (conductor a: NOT a sieve datum at depth Z)
  J(a | n) for a = 467..521 (inside the sieve: knows only n mod a)
  J(q | n) (row prime against N - q; = J(N | q) up to signs: N mod q)
  J(n' | n) with n' = N - q' the next surviving row (= J(q - q' | n) up to signs)
  J(R | n) for a fixed random 200-digit odd R (conductor of 200 digits)
  chi4(n) = n mod 4, chi8
Also: dispersion of the number of primes per member, overall and inside Frobenius classes of the rows in three
non-abelian fields (splitting fields of x^3-2, x^4-2, x^5-x-1), a test of "ties through a shared Artin symbol".

usage: python3 recip_blind.py [members=1500] [Z=200000] [seed=1]
"""
import sys, os, math, random, time
import numpy as np, gmpy2
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
from sympy.ntheory.modular import crt
from sympy import primerange, Poly, symbols, GF, factor_list
from sympy.abc import x

NM = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
Z = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
random.seed(seed)
f = cr.S + "q200000_m89.txt"
rows, p = cr.load(f); rows = [int(q) for q in rows if q < 200000]
line = [l for l in open(f) if l.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
mods = [2] + [r for r, a in cov]; res = [0] + [a for r, a in cov]
N0, M = crt(mods, res); N0 = int(N0); M = int(M)
X = 10 ** 200; K = (X - N0) // M
print(f"rows {len(rows)}  M = 10^{math.log10(M):.2f}  members below 10^200: 2^{math.log2(K):.2f}")
for r, a in cov: assert N0 % r == a
assert N0 % 2 == 0
sp = np.array(list(primerange(464, Z + 1)), dtype=np.int64)
rows_np = np.array(rows, dtype=np.int64)
N0m = np.array([N0 % int(s) for s in sp], dtype=np.int64); Mm = np.array([M % int(s) for s in sp], dtype=np.int64)
CH = 3000
chunks = [(i, min(i + CH, len(sp))) for i in range(0, len(sp), CH)]
ks = [random.randrange(K) for _ in range(NM)]
alive = np.ones((NM, len(rows)), dtype=bool)
t0 = time.time()
for (i, j) in chunks:
    S = sp[i:j]; Rm = (rows_np[:, None] % S[None, :]).astype(np.int32)
    for m, k in enumerate(ks):
        Nm = ((N0m[i:j] + (k % S) * Mm[i:j]) % S).astype(np.int32)
        alive[m] &= ~(Rm == Nm[None, :]).any(axis=1)
print(f"sieve to {Z}: {time.time() - t0:.0f} s; survivors per member {alive.sum(1).mean():.1f} ({alive.mean():.4f})")

# symbols
A_out = [int(a) for a in primerange(Z + 1, Z + 400)][:12]
A_in = [int(a) for a in primerange(464, 530)]
Rbig = random.getrandbits(664) | 1
names = [f"J({a}|n)" for a in A_out] + [f"J({a}|n) in" for a in A_in] + ["J(q|n)", "J(n_next|n)", "J(R200|n)", "chi4(n)", "chi8(n)"]
nf = len(names)
cnt = np.zeros((nf, 2, 2), dtype=np.int64)       # feature, symbol value (0: -1, 1: +1), prime?
prime = np.zeros((NM, len(rows)), dtype=bool)
t0 = time.time(); ntest = 0
for m, k in enumerate(ks):
    N = N0 + k * M
    idx = np.nonzero(alive[m])[0]
    ns = [gmpy2.mpz(N - rows[i]) for i in idx]
    for t, i in enumerate(idx):
        n = ns[t]; q = rows[i]
        pr = gmpy2.powmod(2, n - 1, n) == 1; ntest += 1
        prime[m, i] = pr
        feats = [gmpy2.jacobi(a, n) for a in A_out] + [gmpy2.jacobi(a, n) for a in A_in]
        feats.append(gmpy2.jacobi(q, n))
        feats.append(gmpy2.jacobi(ns[(t + 1) % len(ns)], n))
        feats.append(gmpy2.jacobi(Rbig, n))
        feats.append(1 if n % 4 == 1 else -1)
        feats.append(1 if n % 8 in (1, 7) else -1)
        for j, v in enumerate(feats):
            if v != 0: cnt[j, (v + 1) // 2, int(pr)] += 1
print(f"{ntest} Fermat tests in {time.time() - t0:.0f} s; primes {prime.sum()}  rate among survivors {prime.sum() / ntest:.5f}")
print(f"primes per row (all rows, covered rows excluded): {prime.sum() / (NM * len(rows)):.5f}   (model 0.0243)")
print("\nsymbol | survivors with -1 | prime rate | survivors with +1 | prime rate | z of the difference")
zs = []
for j in range(nf):
    (a0, a1), (b0, b1) = cnt[j]
    n0 = a0 + a1; n1 = b0 + b1
    if n0 == 0 or n1 == 0:
        print(f"{names[j]} | {n0} | - | {n1} | {b1 / max(n1, 1):.5f} | constant"); continue
    p0 = a1 / n0; p1 = b1 / n1; pp = (a1 + b1) / (n0 + n1)
    z = (p1 - p0) / math.sqrt(pp * (1 - pp) * (1 / n0 + 1 / n1)); zs.append(z)
    print(f"{names[j]} | {n0} | {p0:.5f} | {n1} | {p1:.5f} | {z:+.2f}")
zs = np.array(zs)
print(f"\n{len(zs)} non-constant symbols: max |z| = {abs(zs).max():.2f}, sum z^2 = {(zs ** 2).sum():.1f} (chi-square, {len(zs)} dof if independent)")

# dispersion, overall and by Frobenius class of the row in non-abelian fields
def disp(mask_rows):
    s = alive[:, mask_rows].sum(1); c = prime[:, mask_rows].sum(1)
    ph = c.sum() / s.sum()
    num = ((c - s * ph) ** 2).sum(); den = (s * ph * (1 - ph)).sum()
    return num / den, c.sum(), s.sum()
d, c, s = disp(np.ones(len(rows), dtype=bool))
print(f"\ndispersion of primes per member (variance / binomial given the survivors): {d:.3f} +- {math.sqrt(2 / NM):.3f}   [{c} primes, {s} survivors]")
import flint
def frob_type(poly_coeffs, q):
    fq = flint.nmod_poly(poly_coeffs, q)
    return tuple(sorted(g.degree() for g, e in fq.factor()[1] for _ in range(e)))
for label, coeffs in (("x^3-2 (S3)", [-2, 0, 0, 1]), ("x^4-2 (D4)", [-2, 0, 0, 0, 1]), ("x^5-x-1 (S5)", [-1, -1, 0, 0, 0, 1])):
    types = {}
    for i, q in enumerate(rows):
        types.setdefault(frob_type(coeffs, q), []).append(i)
    print(f"rows by cycle type of Frobenius in the splitting field of {label}:")
    for ty, ii in sorted(types.items()):
        mask = np.zeros(len(rows), dtype=bool); mask[ii] = True
        if len(ii) < 30: continue
        d, c, s = disp(mask)
        # pair excess: observed co-primes within class vs independence
        cc = prime[:, mask].sum(1); pairs = (cc * (cc - 1) // 2).sum()
        ss = alive[:, mask].sum(1); ph = c / s; exp_pairs = (ss * (ss - 1) / 2 * ph * ph).sum()
        print(f"  type {ty}: {len(ii)} rows, dispersion {d:.3f} +- {math.sqrt(2 / NM):.3f}; pairs of primes inside the class {pairs} against {exp_pairs:.0f} expected (+- {math.sqrt(exp_pairs):.0f})")
# strongest pair of rows
co = prime.T.astype(np.int32) @ prime.astype(np.int32)
np.fill_diagonal(co, 0)
pr_row = prime.mean(0)
print(f"\nlargest number of members in which two given rows are both prime: {co.max()} (rows prime in {pr_row.mean() * NM:.1f} members on average, at most {prime.sum(0).max()}); a tie would give about {pr_row.mean() * NM:.0f}")
vals, counts = np.unique(co[np.triu_indices(len(rows), 1)], return_counts=True)
rng = np.random.default_rng(7)
sh = prime.copy()
for j in range(sh.shape[1]): sh[:, j] = sh[rng.permutation(NM), j]
co2 = sh.T.astype(np.int32) @ sh.astype(np.int32); np.fill_diagonal(co2, 0)
v2, c2 = np.unique(co2[np.triu_indices(len(rows), 1)], return_counts=True); d2 = dict(zip(v2.tolist(), c2.tolist()))
print("co-occurrences c | pairs of rows observed | the same after shuffling each row over the members (ties destroyed)")
for v, c_ in zip(vals, counts): print(f"{v} | {c_} | {d2.get(int(v), 0)}")
print(f"largest after shuffling: {co2.max()}")
