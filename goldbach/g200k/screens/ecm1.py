"""(c)2, ECM: one stage-1 curve (Montgomery form, Suyama sigma, ladder) at B1 = 1000 on real composite survivors; kill fraction and
cost in Fermat tests (modular multiplications / 664)."""
import sys, math, multiprocessing as mp
import gmpy2
from sympy import primerange
B1 = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
PP = []
for p in primerange(2, B1 + 1):
    q = p
    while q * p <= B1: q *= p
    PP.append(q)
def curve(n, sigma):
    u = (sigma * sigma - 5) % n; v = (4 * sigma) % n
    X = pow(u, 3, n); Z = pow(v, 3, n)
    num = pow(v - u, 3, n) * (3 * u + v) % n; den = 16 * pow(u, 3, n) * v % n
    g = gmpy2.gcd(den, n)
    if g != 1: return g, 0
    a24 = num * gmpy2.invert(den, n) % n
    mm = 0
    for k in PP:
        X0, Z0 = X, Z
        # ladder: R0 = P, R1 = 2P
        def dbl(X, Z):
            t1 = (X + Z) ** 2 % n; t2 = (X - Z) ** 2 % n; t3 = t1 - t2
            return t1 * t2 % n, t3 * (t2 + a24 * t3) % n
        def add(Xp, Zp, Xq, Zq):
            a = (Xp - Zp) * (Xq + Zq) % n; b = (Xp + Zp) * (Xq - Zq) % n
            return Z0 * (a + b) ** 2 % n, X0 * (a - b) ** 2 % n
        R0 = (X0, Z0); R1 = dbl(X0, Z0); mm += 5
        for bit in bin(k)[3:]:
            if bit == "1": R0 = add(*R0, *R1); R1 = dbl(*R1)
            else: R1 = add(*R0, *R1); R0 = dbl(*R0)
            mm += 11
        X, Z = R0
    return gmpy2.gcd(Z, n), mm
def work(args):
    i, n = args
    n = gmpy2.mpz(n)
    g, mm = curve(n, 11 + i)
    return (1 < g < n), mm
if __name__ == "__main__":
    comps = [l.split()[3] for l in open("surv.txt").read().splitlines() if l.split()[2] == "0"][:NMAX]
    with mp.Pool(4) as pool:
        res = pool.map(work, list(enumerate(comps)), chunksize=32)
    kills = sum(k for k, _ in res); mm = max(m for _, m in res)
    c = kills / len(res); e = mm / 664
    print(f"ECM stage 1, one curve, B1 = {B1}: {len(res)} composites, {kills} killed, c = {c:.4f}; cost {mm} mulmods = {e:.1f} Fermat tests; c/e = {c / e:.5f} (break-even 1.081)")
