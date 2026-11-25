import numpy as np, sys, math
X, Q = 10**9, 1000
SMALL = [3, 5, 7, 11, 13, 17, 19, 23, 29]
def allowed(N):
    ok = (N % 2 == 0)
    for p in SMALL: ok &= (N % p != 0)
    return ok
Nlo = (Q + 200 + 1) & ~1
# squares: N within [m^2, m^2+Q) or ((m+1)^2-Q, (m+1)^2]
lst = []
for mm in range(int(math.isqrt(Nlo)) + 1, math.isqrt(X) + 1):
    a = np.arange(mm * mm, mm * mm + Q, dtype=np.int64); b = np.arange((mm + 1) ** 2 - Q + 1, (mm + 1) ** 2 + 1, dtype=np.int64)
    c = np.concatenate([a, b]); c = c[(c >= Nlo) & (c < X)]; lst.append(c[allowed(c)])
S = np.unique(np.concatenate(lst)); print('square-neighbourhood members', len(S))
(S // 2).astype(np.uint32).tofile('fam_sq.u32')
# random sample of members for the coherence-index test (uniform over allowed N), plus we evaluate all successes of A separately
rng = np.random.default_rng(5); n = 4_000_000
N = rng.integers(Nlo // 2, X // 2, size=int(n * 3.3)) * 2; N = N[allowed(N)][:n]
N.astype(np.int64); (N // 2).astype(np.uint32).tofile('fam_rand.u32'); print('random sample', len(N))
