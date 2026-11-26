#!/usr/bin/env python3
"""Independent recomputation: cover, rows, Prop C, C2, window, pins, Prop E, rates."""
import math, sympy, gmpy2, itertools, numpy as np
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000
line = [x for x in open(COVER) if x.startswith("COVER")][0].split()
print("header:", line[:6])
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rs = [r for r, a in cov]
print("cover primes:", len(cov), "= all odd primes <= 463:", rs == list(sympy.primerange(3, 464)), "a_3,a_5,a_7,a_11:", cov[:4], "any a_r = 0:", any(a == 0 for r, a in cov))
rows = [q for q in sympy.primerange(3, Q) if all(q % r != a for r, a in cov)]
print("rows:", len(rows), "rows<=463:", [q for q in rows if q <= 463], " is 2 a row by convention? (N even so N-2 even) excluded")
sift = [q for q in range(465, Q, 2) if all(q % r not in (0, a) for r, a in cov)]
print("Prop C: sifted set size", len(sift), "equal to rows>463:", sift == [q for q in rows if q > 463], "467^2 =", 467 ** 2)
R = set(rows); n = len(rows)
print("C2: rows mod 6:", sorted(set(q % 6 for q in rows)), " classes mod 30:", len(set(q % 30 for q in rows)), " mod 210:", len(set(q % 210 for q in rows)), " mod 2310:", len(set(q % 2310 for q in rows)))
print("n/Q =", n / Q, " 6n/Q =", 6 * n / Q, " (5n/Q)/ln6 =", 5 * n / Q / math.log(6))
# alternatives the page did not price above Q: classes mod 30, 210, 2310 at s = Q
for D in (6, 30, 210, 2310):
    cl = {}
    for q in rows: cl[q % D] = cl.get(q % D, 0) + 1
    best = max(cl.values()); print(f"   s=Q, best single class mod {D}: {best} rows in Q/{D} classes: rate {(best / (Q / D) - n / Q) / math.log(D):.5f} rows/nat;  union of all {len(cl)} row classes: {(n / (len(cl) * Q / D) - n / Q) / math.log(D / len(cl)):.5f} (not a progression)")
# initial segment [0,Q') of the mod-6 progression at s = Q
for f in (2, 4, 10, 50):
    c = sum(1 for q in rows if q < Q // f); print(f"   s=Q, list {{1+6t < Q/{f}}}: rows {c}, rate {(c / (Q / f / 6) - n / Q) / math.log(6 * f):.5f}")
# window
M = 2; N0 = 0
for r, a in cov:
    t = ((a - N0) * pow(M, -1, r)) % r; N0 += M * t; M *= r
assert all(N0 % r == a for r, a in cov) and N0 % 2 == 0 and 0 <= N0 < M
K = (10 ** 200 - 1 - N0) // M + 1   # members N < 10^200
K2 = (10 ** 200 - N0) // M + 1
print("digits of M:", len(str(M)), "ln M =", float(gmpy2.log(M)), "K (N<10^200) =", K, "page formula K =", K2, "ln K =", math.log(K), "log2 K =", math.log2(K))
# tables
def table(s): return np.bincount(np.array(rows) % s, minlength=s)
LP = list(sympy.primerange(467, 5000)); print("later primes 467..5000:", len(LP))
T = {s: table(s) for s in LP}
vm = np.mean([T[s].var() / T[s].mean() for s in LP]); print("var/mean all:", vm, " pin rate at 467:", (T[467].max() - T[467].mean()) / math.log(467), T[467].max(), T[467].mean())
best = max(((T[s].max() - n / s) + (T[t].max() - n / t), s, t) for s, t in itertools.combinations(LP, 2) if s * t <= K)
print("best pair of pins with product <= K:", best)
best1 = max(((T[s].max() - n / s) / math.log(s), s) for s in LP); print("best single pin rate:", best1)
# Prop E: brute force on several pairs
import random; random.seed(1); bad = 0; tot = 0
allp = list(sympy.primerange(467, 60000))
for _ in range(300):
    s, s2 = sorted(random.sample(allp, 2))
    assert s * s2 > Q
    A = {}; B = {}
    for q in rows: A.setdefault(q % s, set()).add(q); B.setdefault(q % s2, set()).add(q)
    for c in range(s):
        sh = A.get(c, set()) & B.get(c, set()); tot += 1
        if sh != ({c} if c in R else set()): bad += 1
print("Prop E: classes checked", tot, "violations", bad)
# D values
P = 1
for i, s in enumerate(LP[:10], 1):
    P *= s
    if i in (2, 3, 4, 5, 6, 8, 10): print(f"  {i} later primes: ln(P/K) = {math.log(P / K):.2f}")
# variance shares
allpr = list(sympy.primerange(467, Q)); rw = np.array(rows)
var = {}
tot = 0.0; marks = {509: 0, 1000: 0, 2000: 0, 5000: 0, 20000: 0, 200000: 0}
for s in allpr:
    t = np.bincount(rw % s, minlength=s); v = t.var(); tot += v
    for mk in marks:
        if s <= mk: marks[mk] += v
print("sum of table variances 467..Q:", tot)
# tail Q..1e8: var of indicator table = n/s (1 - n/s) summed over primes; integral approx sum 1/p = lnln
import mpmath
tail = n * (math.log(math.log(1e8)) - math.log(math.log(Q)))
print("tail Q..1e8 approx n*(lnln 1e8 - lnln Q) =", tail, " total", tot + tail, "sd", math.sqrt(tot + tail))
for mk, v in marks.items(): print(f"   to {mk}: {100 * v / (tot + tail):.1f}%")
