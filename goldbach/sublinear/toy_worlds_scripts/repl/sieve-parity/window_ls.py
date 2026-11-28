#!/usr/bin/env python3
"""(c) The large sieve as a ceiling, on the WHOLE real window of the 200,000 cover.
   T(k) = sum over primes 463 < s <= S of f_s(N_k mod s)  (f_s(c) = rows = c mod s): first-order number of rows struck by the primes to S.
   Theorem (dual large sieve): sum over ANY K consecutive k of (T(k) - mu)^2 <= (K - 1 + S^2) * V,
       mu = sum_s rows_s/s,  V = sum_s (1/s) sum_c (f_s(c) - mean_s)^2 = the variance under independent uniform residues.
   Computed: the exact second, third and fourth moments, the extremes, and the tail counts of T over all K members against the product model."""
import sys, math, time, numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
Q = 200000; S = int(sys.argv[1]) if len(sys.argv) > 1 else 4600
f = cr.S + "q200000_m89.txt"
line = [x for x in open(f) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
rows, p = cr.load(f); rows = rows[rows < Q].astype(np.int64)
M = 2
for r, a in cov: M *= r
N0 = 0; mod = 1
for r, a in [(2, 0)] + cov:
    t = ((a - N0) * pow(mod, -1, r)) % r; N0 += mod * t; mod *= r
K = (10 ** 200 - N0) // M
sv = np.ones(S + 1, dtype=bool); sv[:2] = False
for i in range(2, int(S ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
PS = [int(s) for s in np.nonzero(sv)[0] if s > 463]
print(f"K = {K} = 2^{math.log2(K):.3f} members; primes in (463, {S}]: {len(PS)}; S^2/K = {S * S / K:.3f}")
tabs = []; mu = 0.0; V = 0.0; k3 = 0.0; k4 = 0.0; triv = 0
for s in PS:
    fs = np.bincount(rows % s, minlength=s).astype(np.float64); m = fs.mean(); d = fs - m
    mu += m; v = (d ** 2).mean(); V += v; k3 += (d ** 3).mean(); k4 += (d ** 4).mean() - 3 * v * v; triv += int(fs.max())
    a = N0 % s; b = M % s
    g = fs[(a + np.arange(s) * b) % s].astype(np.int16)          # period of k -> f_s(N_k mod s)
    tabs.append((s, g))
print(f"model: mean {mu:.3f}, variance {V:.3f} (sd {math.sqrt(V):.3f}), third cumulant {k3:.2f}, fourth cumulant {k4:.2f}; trivial ceiling sum of max f_s = {triv}")
L = 1 << 21; t0 = time.time()
s1 = s2 = s3 = s4 = 0.0; mn = 10 ** 9; mx = -1; hist = np.zeros(4000, dtype=np.int64)
for a in range(0, K, L):
    n = min(L, K - a); T = np.zeros(n, dtype=np.int16)
    for s, g in tabs:
        off = a % s; reps = (off + n + s - 1) // s
        T += np.tile(g, reps)[off:off + n]
    hist += np.bincount(T, minlength=4000); 
    if T.min() < mn: mn = int(T.min()); amin = a + int(T.argmin())
    if T.max() > mx: mx = int(T.max()); amax = a + int(T.argmax())
vals = np.arange(4000); tot = hist.sum(); assert tot == K
m1 = (hist * vals).sum() / tot; d = vals - mu
m2 = (hist * d ** 2).sum() / tot; m3 = (hist * d ** 3).sum() / tot; m4 = (hist * d ** 4).sum() / tot
print(f"window, all {K} members, {time.time() - t0:.0f} s: mean {m1:.3f}; second moment about mu {m2:.3f} = {m2 / V:.5f} V  (large sieve: at most {1 + (S * S - 1) / K:.3f} V); third {m3:.2f} (model {k3:.2f}); fourth {m4:.1f} (model {k4 + 3 * V * V:.1f})")
sd = math.sqrt(V)
print(f"extremes: max T = {mx} at k = {amax} ({(mx - mu) / sd:+.2f} sd), min T = {mn} at k = {amin} ({(mn - mu) / sd:+.2f} sd); sqrt(2 ln K) = {math.sqrt(2 * math.log(K)):.2f}")
# product model: exact distribution of T by convolution
dist = np.array([1.0])
for s, g in tabs:
    pm = np.bincount(g.astype(np.int64)) / s; dist = np.convolve(dist, pm)
tail_model = dist[::-1].cumsum()[::-1] * K; tail_real = hist[::-1].cumsum()[::-1]
print("tail: t | members of the window with T >= t | product model K*P(T >= t) | Chebyshev ceiling from the large sieve (K-1+S^2) V/(t-mu)^2")
for z in (2, 3, 4, 5, 5.5, 6, 6.5):
    t = int(math.ceil(mu + z * sd)); 
    if t < len(dist): print(f"   {t} ({z} sd) | {int(tail_real[t])} | {tail_model[t]:.2f} | {(K - 1 + S * S) * V / (t - mu) ** 2:.0f}")
tb = int(np.nonzero(tail_model >= 1)[0].max()); print(f"   level where the model expects one member: T = {tb}; found max {mx}; large-sieve (Chebyshev) ceiling on the best member: mu + sqrt((K+S^2)V) = {mu + math.sqrt((K - 1 + S * S) * V):.0f}, beyond the trivial {triv}")
