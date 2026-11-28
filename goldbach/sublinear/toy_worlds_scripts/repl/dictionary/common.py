import sys, math
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
import gmpy2
from gmpy2 import mpz
def setup():
    f = cr.S + "q200000_m89.txt"
    rows, p = cr.load(f)
    rows = rows[rows < 200000]
    l = [x for x in open(f) if x.startswith("COVER")][0].split()
    cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
    M = mpz(2)
    for r, _ in cov: M *= r
    # CRT, even
    N0 = mpz(0); mod = mpz(2)
    for r, a in cov:
        t = ((a - N0) * gmpy2.invert(mod, r)) % r
        N0 += mod * t; mod *= r
    assert mod == M and N0 % 2 == 0
    for r, a in cov: assert N0 % r == a
    X = mpz(10) ** 200
    K = int((X - N0) // M)
    return [int(q) for q in rows], cov, N0, M, K
