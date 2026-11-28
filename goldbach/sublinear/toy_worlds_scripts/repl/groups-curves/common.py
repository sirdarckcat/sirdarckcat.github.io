import sys, math
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
import gmpy2
from gmpy2 import mpz
F = cr.S + "q200000_m89.txt"
def cover():
    l = [x for x in open(F) if x.startswith(("COVER", "BEST"))][0].split()
    return [(int(t.split(":")[0]), int(t.split(":")[1])) for t in l if ":" in t]
def setup():
    rows, p = cr.load(F)
    rows = [int(q) for q in rows if q < 200000]
    cov = cover()
    M = mpz(2); N0 = mpz(0)
    # CRT, even
    for r, a in cov:
        # find N0 + t*M = a mod r
        t = ((a - N0) * gmpy2.invert(M, r)) % r
        N0 += t * M; M *= r
    assert N0 % 2 == 0 and all(N0 % r == a for r, a in cov)
    K = (mpz(10) ** 200 - N0) // M
    return rows, cov, N0, M, int(K)
if __name__ == "__main__":
    rows, cov, N0, M, K = setup()
    print(len(rows), len(cov), math.log10(M), math.log2(K), N0.bit_length())
