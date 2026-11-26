# prime-indicator matrix of real members of the 200,000 cover (base-2 Fermat test on every row)
import numpy as np, random, time, gmpy2
from gmpy2 import mpz
from common import setup
rows, cov, N0, M, K = setup()
print("rows", len(rows), "members in window 2^%.2f" % np.log2(K), "digits of M", len(str(M)))
random.seed(20261126)
nm = 2000
ks = sorted(random.sample(range(K), nm))
ind = np.zeros((nm, len(rows)), dtype=np.uint8)
t = time.time()
for i, k in enumerate(ks):
    N = N0 + k * M
    for j, q in enumerate(rows):
        m = N - q
        if gmpy2.powmod(2, m - 1, m) == 1: ind[i, j] = 1
print("time", time.time() - t, "tests", ind.size, "primes", int(ind.sum()), "rate", ind.mean())
np.savez_compressed("ind.npz", ks=np.array(ks, dtype=np.int64), ind=ind, rows=np.array(rows))
