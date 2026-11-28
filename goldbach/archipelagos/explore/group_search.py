# Small-N cost check of "follow the group": evaluate a random sample of even N; for every big one
# (top 1%) also evaluate its neighbours N +- 6j (j = 1..10) and N +- 30j (j = 1..7).
# Cost = primality tests = rows tried before the first prime (pi(g) - 1).  Compares huge (top 0.01%)
# finds per test against plain random sampling.  usage: python3 group_search.py N0 L
import sys, math
import numpy as np
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, math.isqrt(n) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
N0 = int(float(sys.argv[1])); L = int(float(sys.argv[2])); PMAX = 40000
lo, hi = N0 - PMAX, N0 + 2 * L
seg = np.ones(hi - lo, dtype=bool)
for p in primes_upto(math.isqrt(hi) + 1):
    p = int(p); seg[max(p * p, -(-lo // p) * p) - lo::p] = False
rows = primes_upto(PMAX); rows = rows[rows >= 3]
g = np.zeros(L, dtype=np.int32); cost = np.zeros(L, dtype=np.int32); un = np.arange(L, dtype=np.int64)
for i, q in enumerate(rows):
    hit = seg[N0 - lo - int(q) + 2 * un]
    g[un[hit]] = q; cost[un[hit]] = i + 1; un = un[~hit]
    if un.size == 0: break
big = g >= np.percentile(g, 99) + 1; huge = g >= np.percentile(g, 99.99) + 1
lags = np.array([6 * j for j in range(1, 11)] + [30 * j for j in range(1, 8)]) // 2
lags = np.unique(np.concatenate([lags, -lags]))
rng = np.random.default_rng(1)
for frac in (0.01, 0.1):
    base = rng.choice(np.arange(200, L - 200), int(frac * L), replace=False)
    ev = np.zeros(L, dtype=bool); ev[base] = True
    tR, hR = cost[base].sum(), huge[base].sum()
    nb = (base[big[base]][:, None] + lags[None, :]).ravel()
    ev[nb] = True
    tG, hG = cost[ev].sum(), huge[ev].sum()
    print(f"sample {100*frac:>4.0f}% of N: random: {hR} huge in {tR:,} tests ({tR/max(hR,1):,.0f} tests/huge); "
          f"follow groups: {hG} huge in {tG:,} tests ({tG/max(hG,1):,.0f} tests/huge)")
print(f"tests per N: mean {cost.mean():.1f}; exhaustive interval sieve instead finds all {int(huge.sum())} huge N")
