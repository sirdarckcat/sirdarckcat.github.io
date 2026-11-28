# independent set-up (verifier): cover, rows, tables
import math, numpy as np, sympy
from math import prod, log
COVER_FILE = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
X = 10**200; Q = 200000
line = [l for l in open(COVER_FILE) if l.startswith("COVER")][0].split()
claimed_rows = int(line[1])
cover = {}
for tok in line[2:]:
    r, a = tok.split(":"); cover[int(r)] = int(a)
cprimes = sorted(cover)
allp = np.array(list(sympy.primerange(3, Q)), dtype=np.int64)   # odd primes below Q
def rows_for(assign):
    keep = np.ones(len(allp), dtype=bool)
    for r, a in assign.items():
        keep &= (allp % r != a)
    return allp[keep]
ROWS = rows_for(cover); n0 = len(ROWS)
M = 2 * prod(cprimes)
def crt_pairs(pairs):
    # pairs: list of (modulus, residue); returns N mod prod
    N, mod = 0, 1
    for r, a in pairs:
        N = sympy.ntheory.modular.crt([mod, r], [N, a])[0] if False else (N + mod * (((a - N) * pow(mod, -1, r)) % r)); mod *= r
    return N, mod
N0, _m = crt_pairs([(2, 0)] + [(r, cover[r]) for r in cprimes]); assert _m == M
K = (X - 1 - N0) // M + 1
LATER = [int(p) for p in sympy.primerange(464, 800)]
def dlt_table(r):
    other = {q: a for q, a in cover.items() if q != r}
    U = rows_for(other)
    cnt = np.bincount(U % r, minlength=r)
    return (len(U) - cnt) - n0       # rows left if class of r is c, minus n0
def hit_table(s):
    return np.bincount(ROWS % s, minlength=s)
if __name__ == "__main__":
    print("rows", n0, "claimed", claimed_rows, "cover primes", len(cprimes), "max", max(cprimes), "all odd primes<=463:", cprimes == [int(p) for p in sympy.primerange(3, 464)])
    print("M bits", M.bit_length(), "K", K, "ln(X/M)", 200*log(10) - sum(log(r) for r in cprimes) - log(2))
    for r in cprimes: assert N0 % r == cover[r]
    assert N0 % 2 == 0
    print("p =", 2 * prod(r/(r-1) for r in cprimes) / (200*log(10)), "n0*p", n0 * 2 * prod(r/(r-1) for r in cprimes) / (200*log(10)))
