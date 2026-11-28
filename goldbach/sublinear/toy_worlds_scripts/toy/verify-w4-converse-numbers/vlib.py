# independent loader (verifier). Uses sympy for primes, gmpy2 for CRT.
import math, numpy as np, sympy, gmpy2
COVER = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000
def get():
    line = [l for l in open(COVER) if l.startswith("COVER")][0].split()
    cov = {}
    for tok in line[2:]:
        r, a = tok.split(":"); cov[int(r)] = int(a)
    rows = []
    for q in sympy.primerange(3, Q):
        if all(q % r != a for r, a in cov.items()): rows.append(q)
    return cov, np.array(rows, dtype=np.int64)
def win(cov):
    # N even, N = a_r mod r ; solve by CRT with modulus 2 residue 0
    mods = [2] + list(cov.keys()); res = [0] + list(cov.values())
    M = 1
    for m in mods: M *= m
    N0 = 0
    for m, a in zip(mods, res):
        Mi = M // m; N0 += a * Mi * int(gmpy2.invert(Mi, m))
    N0 %= M
    X = 10 ** 200
    K = (X - 1 - N0) // M + 1     # members N0 + kM < X
    return N0, M, K
def tab(rows, s):
    t = np.zeros(s, dtype=np.int64); np.add.at(t, rows % s, 1); return t
def lp(lo, hi): return [int(p) for p in sympy.primerange(lo, hi)]
