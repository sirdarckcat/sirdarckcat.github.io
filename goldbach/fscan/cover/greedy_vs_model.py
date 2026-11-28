import math, numpy as np
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes_upto(200000); Q = 122000
rows = P[(P >= 3) & (P < Q)]
mods = [int(p) for p in P if 3 <= p <= 439] + [467, 487, 491, 683]
def D(x, a):
    if x >= 1: return -math.log(a)
    return x * math.log(x / a) + (1 - x) * math.log((1 - x) / (1 - a))
alive = rows.copy(); n = len(rows); lnm = 0.0
tot_actual = tot_model = tot_mean = 0
print(" r   alive  mean class  greedy max  model max (given the actual alive)   Poisson-extreme")
for r in mods:
    cnt = np.bincount(alive % r, minlength=r); cnt[0] = 0
    c = int(cnt.argmax()); mx = int(cnt[c]); mu = len(alive) / (r - 1)
    lnm += math.log(r); d = min(1.0, lnm / math.log(Q))
    a = len(alive) / n; N = n / (r - 1)
    lo, hi = a, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if N * D(mid, a) <= d * math.log(r - 1): lo = mid
        else: hi = mid
    model = lo * N
    # largest count such that (r-1) * P(Poisson(mu) >= c) >= 1
    cc = int(mu); tail = 1.0
    from math import exp, lgamma, log
    def ptail(c0): return sum(exp(-mu + k * log(mu) - lgamma(k + 1)) for k in range(c0, c0 + 400))
    while (r - 1) * ptail(cc + 1) >= 1: cc += 1
    tot_actual += mx; tot_model += model; tot_mean += mu
    if r in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 53, 71, 97, 127, 151, 199, 251, 307, 359, 401, 439, 683):
        print(f"{r:4d} {len(alive):6d} {mu:9.1f} {mx:9d} {model:12.1f} {cc:30d}")
    alive = alive[alive % r != c]
print(f"greedy residual {len(alive)}; total kills: greedy {tot_actual}, model given the actual alive sets {tot_model:.0f}, mean classes {tot_mean:.0f}")
