#!/usr/bin/env python3
"""Do algebraically structured targets N of 200 digits tie their rows?  (Bateman-Horn says no.)

For each family of even N near 10^200: all odd primes q < 200,000 are rows; a row survives if N - q has no prime factor
<= Z; every survivor gets a base-2 Fermat test.  Under independence given the residues, the number of primes of a
target is binomial(survivors, p_Z) with p_Z = (1/ln N) / prod_{s <= Z} (1 - 1/s).  A tie of order h between rows
(as for translation-invariant N in F_q[x], or real N in Z[i]) would show as dispersion h; rows that are composite for
an algebraic reason would show as a ratio found/expected below 1.
Families: generic; A^2; A^3; A^4; 2^a 3^b; A^2 + A (norm-like, discriminant 4q+1); x^2 + y^2.
For N = A^2 also checked: J(q | N - q) = +1 for every row (every prime factor of N - q splits in Q(sqrt q)).
usage: python3 structured_N.py [targets per family=150] [Z=100000]
"""
import sys, math, random, time
import numpy as np, gmpy2
from sympy import primerange
NT = int(sys.argv[1]) if len(sys.argv) > 1 else 150
Z = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
Q = 200000
random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 11)
sp = [int(s) for s in primerange(3, Z + 1)]
rows = np.array(list(primerange(3, Q)), dtype=np.int64)
mert = 0.5 * math.prod(1 - 1 / s for s in sp)
X = 10 ** 200
def rnd(lo, hi): return random.randrange(lo, hi)
def gen(fam):
    if fam == "generic": return rnd(X // 10, X) // 2 * 2
    if fam == "A^2": a = rnd(gmpy2.isqrt(X // 10) + 1, gmpy2.isqrt(X)) // 2 * 2; return int(a) ** 2
    if fam == "A^3": a = rnd(gmpy2.iroot(X // 10, 3)[0] + 1, gmpy2.iroot(X, 3)[0]) // 2 * 2; return int(a) ** 3
    if fam == "A^4": a = rnd(gmpy2.iroot(X // 10, 4)[0] + 1, gmpy2.iroot(X, 4)[0]) // 2 * 2; return int(a) ** 4
    if fam == "2^a 3^b":
        while True:
            a = rnd(1, 660); b = int((math.log(X) - a * math.log(2)) / math.log(3)); n = 2 ** a * 3 ** b
            if X // 10 <= n < X: return n
    if fam == "A^2+A": a = rnd(gmpy2.isqrt(X // 10) + 1, gmpy2.isqrt(X) - 1); return int(a) ** 2 + int(a)
    if fam == "x^2+y^2":
        s = int(gmpy2.isqrt(X // 2)); x = rnd(s // 3, s) | 1; y = rnd(s // 3, s) | 1; return x * x + y * y
print(f"rows: the {len(rows)} odd primes below {Q}; sieve to {Z}; survivor prime probability at 10^200: {1 / (200 * math.log(10)) / mert:.5f}")
print("family | targets | survivors per target | Fermat tests | primes found | expected | found/expected | dispersion (1 = independent)")
for fam in (sys.argv[4].split(",") if len(sys.argv) > 4 else ("generic", "A^2", "A^3", "A^4", "2^a 3^b", "A^2+A", "x^2+y^2")):
    t0 = time.time(); found = []; expd = []; var = []; surv = []; seen = set(); jac_bad = 0; jac_n = 0
    while len(found) < NT:
        N = gen(fam)
        if N in seen or N % 2: continue
        seen.add(N)
        dead = np.zeros(Q, dtype=bool)
        for s in sp: dead[N % s::s] = True
        dead[:Z + 1] = True          # rows q <= Z are sieved by q itself only when q | N: drop them all to keep the model exact
        idx = rows[~dead[rows]]
        pZ = 1 / math.log(N) / mert
        c = 0
        for q in idx:
            n = gmpy2.mpz(N - int(q))
            if gmpy2.powmod(2, n - 1, n) == 1: c += 1
            if fam == "A^2":
                jac_n += 1
                if gmpy2.jacobi(int(q), n) != 1: jac_bad += 1
        found.append(c); expd.append(len(idx) * pZ); var.append(len(idx) * pZ * (1 - pZ)); surv.append(len(idx))
    f = np.array(found); e = np.array(expd); v = np.array(var)
    ratio = f.sum() / e.sum(); disp = ((f - e) ** 2).sum() / v.sum()
    extra = f"   [J(q|N-q) = +1 on {jac_n - jac_bad} of {jac_n} rows]" if fam == "A^2" else ""
    print(f"{fam} | {NT} | {np.mean(surv):.0f} | {sum(surv)} | {f.sum()} | {e.sum():.0f} | {ratio:.4f} +- {1 / math.sqrt(f.sum()):.4f} | {disp:.3f} +- {math.sqrt(2 / NT):.3f}{extra}   ({time.time() - t0:.0f} s)", flush=True)
