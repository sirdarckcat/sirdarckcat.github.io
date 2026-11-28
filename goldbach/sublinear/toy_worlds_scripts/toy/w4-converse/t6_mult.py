#!/usr/bin/env python3
"""t6: multiplicative structure (lists that are cosets of a subgroup of index e) and what Proposition D can buy.
 (a) character sums of the rows, orders e = 2..6, primes 467..5000: |sum_q chi(q)|^2 / (rows not 0 mod s); noise level 1.
 (b) index 2: the heavier coset of squares/non-squares at s gains |sum_q (q/s)| / (s-1) rows over a random member; total over
     the primes to 5000 and to 200,000 if the sign could be chosen freely at every prime; the same for random rows.
 (c) forced signs: N = c y^2 has (N/s) = (c/s) at every s: gain(c) = sum_s (c/s) sum_q (q/s)/(s-1), all c <= 10^5 coprime to M.
 (d) Proposition D, an instance: prescribed signs at the m primes after 463, c = product of a subset of the next J primes
     (linear algebra over F_2); ln c against the m ln 2 nats of constraint."""
import math, numpy as np, random
from common import *
cov, rows = load(); n = len(rows); rng = np.random.default_rng(3)
def proot(r):
    fac = []; m = r - 1; d = 2
    while d * d <= m:
        if m % d == 0:
            fac.append(d)
            while m % d == 0: m //= d
        d += 1
    if m > 1: fac.append(m)
    for g in range(2, r):
        if all(pow(g, (r - 1) // f, r) != 1 for f in fac): return g
LP = later_primes(464, 5000)
pw = {e: [] for e in (2, 3, 4, 5, 6)}; pwn = {e: [] for e in pw}; allp = []; allmax = []; allmaxn = []
EI = (2, 3, 4, 5, 6, 7, 8, 10, 12); cg = {e: [] for e in EI}; cgn = {e: [] for e in EI}
for s in LP:
    g = proot(s); dl = np.zeros(s, dtype=np.int64); x = 1
    for j in range(s - 1): dl[x] = j; x = x * g % s
    c = rows % s; nz = c[c != 0]; m = len(nz); a = np.bincount(dl[nz], minlength=s - 1).astype(float); P = np.abs(np.fft.fft(a)) ** 2 / m
    b = np.bincount(rng.integers(0, s - 1, size=m), minlength=s - 1).astype(float); Pn = np.abs(np.fft.fft(b)) ** 2 / m
    allp.append(P[1:].mean()); allmax.append(P[1:].max() / math.log(s - 2)); allmaxn.append(Pn[1:].max() / math.log(s - 2))
    for e in EI:
        if (s - 1) % e == 0:
            for arr, dst in ((a, cg), (b, cgn)):
                sums = np.bincount(np.arange(s - 1) % e, weights=arr, minlength=e); dst[e].append((sums.max() / ((s - 1) / e) - m / (s - 1)) / math.log(e))
    for e in pw:
        if (s - 1) % e == 0:
            ks = [(s - 1) // e * t for t in range(1, e) if math.gcd(t, e) == 1]; pw[e].append(np.mean(P[ks])); pwn[e].append(np.mean(Pn[ks]))
print(f"(a) character sums of the {n} rows, primes 467..5000 (noise = 1)")
for e in pw: print(f"    order {e}: {len(pw[e]):3d} primes, mean normalised power {np.mean(pw[e]):.3f} +- {np.std(pw[e])/math.sqrt(len(pw[e])):.3f}   (random rows: {np.mean(pwn[e]):.3f})")

print(f"    all nontrivial characters: mean normalised power {np.mean(allp):.4f}; largest power / ln(s-2): mean {np.mean(allmax):.3f}, max {np.max(allmax):.3f}; random rows: mean {np.mean(allmaxn):.3f}, max {np.max(allmaxn):.3f}")
print("    heaviest coset of the subgroup of index e: rate (gain over a random member)/ln e, rows per nat: " + "; ".join(f"e={e}: real {np.mean(cg[e]):.4f} random {np.mean(cgn[e]):.4f} ({len(cg[e])} primes)" for e in EI))
def legendre_table(s):
    t = -np.ones(s, dtype=np.int8); t[(np.arange(1, s, dtype=np.int64) ** 2) % s] = 1; t[0] = 0; return t
AP = primes_upto(Q); AP = [int(x) for x in AP[AP > 463]]
W = {}; Wr = {}
for s in AP:
    T = legendre_table(s); W[s] = int(T[rows % s].sum()); Wr[s] = int(T[rng.integers(1, s, size=n)].sum())
print("(b) index 2, sign free at every prime: gain sum_s |sum_q (q/s)|/(s-1) in rows")
for hi in (5000, 20000, 200000):
    g = sum(abs(W[s]) / (s - 1) for s in AP if s <= hi); gr = sum(abs(Wr[s]) / (s - 1) for s in AP if s <= hi); k = sum(1 for s in AP if s <= hi)
    print(f"    primes 467..{hi:6d} ({k:5d} primes): real {g:6.2f} rows = {g*0.0243:.3f} nats; random rows {gr:6.2f};  constraint {k*math.log(2):8.1f} nats; rows per nat of constraint {g/(k*math.log(2)):.4f};"
          f"  mean |sum|/sqrt(rows) real {np.mean([abs(W[s]) for s in AP if s <= hi])/math.sqrt(n):.3f} (noise sqrt(2/pi) = 0.798)")
print(f"    the first prime: |sum| at 467 = {abs(W[467])}, gain {abs(W[467])/466:.4f} rows for ln 2 nats")
M = math.prod(r for r, _ in cov) * 2
C = np.array([c for c in range(1, 100001) if math.gcd(c, M) == 1], dtype=np.int64)
for hi in (5000, 20000):
    acc = np.zeros(len(C))
    for s in AP:
        if s > hi: break
        acc += legendre_table(s)[C % s] * (W[s] / (s - 1))
    sd = math.sqrt(sum((W[s] / (s - 1)) ** 2 for s in AP if s <= hi)); i = int(np.argmax(acc))
    print(f"(c) forced signs, N = c y^2, primes 467..{hi}: {len(C)} values of c <= 10^5 coprime to M: gain mean {acc.mean():+.3f}, sd {acc.std():.3f} (predicted sd {sd:.3f}), best {acc[i]:+.3f} rows at c = {int(C[i])}"
          f" = {acc[i]*0.0243:.3f} nats; c = 1 (N = y^2): {acc[0]:+.3f}")

print("(d) Proposition D: prescribed quadratic characters at m primes by linear algebra over F_2")
random.seed(2)
for m in (10, 20, 40, 80):
    tg = AP[:m]; gens = AP[m:m + m + 8]; target = [random.choice((1, -1)) for _ in tg]
    A = [[0 if legendre_table(s)[p % s] == 1 else 1 for p in gens] + [0 if t == 1 else 1] for s, t in zip(tg, target)]
    J = len(gens); piv = []; r = 0
    for col in range(J):
        pr = next((i for i in range(r, m) if A[i][col]), None)
        if pr is None: continue
        A[r], A[pr] = A[pr], A[r]
        for i in range(m):
            if i != r and A[i][col]: A[i] = [x ^ y for x, y in zip(A[i], A[r])]
        piv.append(col); r += 1
        if r == m: break
    assert r == m, "rank deficient"
    x = [0] * J
    for i, col in enumerate(piv): x[col] = A[i][J]
    c = math.prod(p for p, b in zip(gens, x) if b)
    ok = all((1 if pow(c % s, (s - 1) // 2, s) == 1 else -1) == t for s, t in zip(tg, target))
    print(f"    m = {m:3d} signs at {tg[0]}..{tg[-1]}: c = product of {sum(x)} of the primes {gens[0]}..{gens[-1]}, ln c = {math.log(c):7.1f} nats, constraint m ln 2 = {m*math.log(2):5.1f} nats, verified {ok};"
          f"  gain if the signs were the heavy cosets: {sum(abs(W[s])/(s-1) for s in tg):.3f} rows")
