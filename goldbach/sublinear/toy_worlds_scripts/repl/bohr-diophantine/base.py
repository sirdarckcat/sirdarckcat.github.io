#!/usr/bin/env python3
"""Common data: the real 200,000 cover, N0, M, K, rows; binary files for the C sieve.
   python3 base.py L      writes primes/n0/minv for the later primes 463 < s <= L"""
import sys, math, re, numpy as np, gmpy2, os
HERE = os.path.dirname(os.path.abspath(__file__))
F = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
Q = 200000; X = 10 ** 200
cov = [(int(a), int(b)) for a, b in re.findall(r"(\d+):(\d+)", open(F).readline())]
def primes_upto(n):
    sv = np.ones(n + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    return np.nonzero(sv)[0]
PR = primes_upto(Q - 1); PR = PR[PR > 2]
alive = np.ones(len(PR), dtype=bool)
for r, a in cov: alive &= (PR % r) != a
ROWS = PR[alive]                                   # 1502 rows
def crt(classes):
    N = 0; Mm = 2
    for (r, c) in classes:
        t = ((c - N) * pow(Mm, -1, r)) % r; N += Mm * t; Mm *= r
    return N, Mm
N0, M = crt(cov); K = (X - 1 - N0) // M + 1
def tables(s):
    """g[c] = rows struck by s at members k = c mod s   (k-coordinates); f[c] = rows in class c of s (N-coordinates)"""
    f = np.bincount(ROWS % s, minlength=s)
    k = np.arange(s); g = f[(N0 % s + k * (M % s)) % s]
    return f, g
if __name__ == "__main__":
    L = int(float(sys.argv[1]))
    assert N0 % 2 == 0 and all(N0 % r == a for r, a in cov)
    print(f"rows {len(ROWS)}  K {K} = 2^{math.log2(K):.3f} = e^{math.log(K):.3f}  ln M {math.log(M):.2f}  digits of N0+(K-1)M {len(str(N0 + (K - 1) * M))}")
    ps = primes_upto(L); ps = ps[ps > 463]
    n0 = np.empty(len(ps), dtype=np.uint32); mi = np.empty(len(ps), dtype=np.uint32)
    N0z = gmpy2.mpz(N0); Mz = gmpy2.mpz(M)
    for i, s in enumerate(ps.tolist()):
        n0[i] = int(N0z % s); mi[i] = int(gmpy2.invert(Mz % s, s))
    ps.astype(np.uint32).tofile(f"{HERE}/primes.bin"); n0.tofile(f"{HERE}/n0.bin"); mi.tofile(f"{HERE}/minv.bin")
    ROWS.astype(np.uint32).tofile(f"{HERE}/rows.bin")
    open(f"{HERE}/meta.txt", "w").write(f"{K} {len(ROWS)} {len(ps)}\n")
    print(f"later primes to {L}: {len(ps)}")
