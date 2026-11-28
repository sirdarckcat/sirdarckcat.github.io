# Is there a "warmer/colder" signal along a progression?  Correlation of the sieve score u_z(N)
# (rows q < G whose N - q has no prime factor <= z) between N and N + d, after removing the
# mean of each class mod 30030 (the part a cover on primes <= 13 already fixes).
import sys, math
import numpy as np
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, math.isqrt(n) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
N0, L, G, z = int(1e10), int(4e6), 278, 10000
lo, hi = N0 - G, N0 + 2 * L
rough = np.ones(hi - lo, dtype=np.int8)
for s in primes_upto(z):
    s = int(s); rough[-(-lo // s) * s - lo::s] = 0
rq = primes_upto(G); rq = rq[rq >= 3]
u = np.zeros(L, dtype=np.float64)
for q in rq:
    a = N0 - lo - int(q); u += rough[a:a + 2 * L:2][:L]
cls = (N0 + 2 * np.arange(L, dtype=np.int64)) % 30030
mean_c = np.bincount(cls, weights=u, minlength=30030) / np.maximum(np.bincount(cls, minlength=30030), 1)
r = u - mean_c[cls]
print(f"u_{z}: mean {u.mean():.2f}, sd {u.std():.2f}; sd left after removing the class mod 30030: {r.std():.2f}")
for d in (6, 30, 210, 30030, 60060, 2 * 30030 * 7):
    j = d // 2
    print(f"  corr of the residual score at N and N + {d:>6}: {np.corrcoef(r[:-j], r[j:])[0, 1]:+.3f}")
