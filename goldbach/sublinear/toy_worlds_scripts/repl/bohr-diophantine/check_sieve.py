#!/usr/bin/env python3
"""Independent check of sieve_exact on a few members: gcd of N - q with the product of the primes in (463, z]."""
import numpy as np, gmpy2, random
from base import *
z = 10 ** 6
ps = primes_upto(z); ps = ps[ps > 463]
prod = gmpy2.mpz(1); chunks = []
for i in range(0, len(ps), 2000):
    c = gmpy2.mpz(1)
    for s in ps[i:i + 2000].tolist(): c *= s
    chunks.append(c)
S = np.fromfile("S_1000000.u16", dtype=np.uint16); S5 = np.fromfile("S_509.u16", dtype=np.uint16)
random.seed(3); ks = [0, K - 1, int(np.argmin(S))] + [random.randrange(K) for _ in range(3)]
for k in ks:
    N = gmpy2.mpz(N0) + k * gmpy2.mpz(M); left = 0; left5 = 0
    for q in ROWS.tolist():
        n = N - q
        if all(gmpy2.gcd(n, c) == 1 for c in chunks): left += 1
        if all(n % s for s in (467, 479, 487, 491, 499, 503, 509)): left5 += 1
    print(k, "rows left to 1e6: direct", left, "sieve_exact", int(S[k]), "| to 509:", left5, int(S5[k]), "OK" if left == S[k] and left5 == S5[k] else "MISMATCH")
