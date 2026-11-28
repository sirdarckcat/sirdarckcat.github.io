#!/usr/bin/env python3
"""autocorr.py PREFIX DEPTH: the full autocorrelation of the exact sieve count over the real window, by FFT.
rho(D) = corr(S(k), S(k+D)) for every 0 < D < K/2: the complete list of 'translation moves' and what each preserves."""
import sys, numpy as np, math
pre, depth = sys.argv[1], sys.argv[2]
S = np.fromfile(f"{pre}.{depth}.u16", dtype=np.uint16).astype(np.float64); K = len(S)
mu, var = S.mean(), S.var(); Z = (S - mu) / math.sqrt(var); del S
L = 1 << 26
F = np.fft.rfft(Z, L); A = np.fft.irfft(F.real ** 2 + F.imag ** 2, L); del F
H = K // 2
D = np.arange(1, H); rho = A[1:H] / (K - D)        # unbiased pair mean (Z has global mean 0, var 1)
noise = 1 / np.sqrt(K - D)
print(f"depth {depth}: K {K}; D in [1,{H}); pair-noise sd between {noise.min():.2e} and {noise.max():.2e}")
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
PR = [int(p) for p in primes(6000) if p > 463]
free = np.ones(H - 1, dtype=bool)
for p in PR: free[p - 1::p] = False
print(f"D with no prime factor in (463,6000]: {free.sum()} : mean rho {rho[free].mean():+.2e}, sd {rho[free].std():.3e} (pair noise alone would give {np.sqrt((noise[free]**2).mean()):.3e}); max {rho[free].max():.5f} at D={D[free][rho[free].argmax()]}; min {rho[free].min():.5f}")
zs = rho[free] / noise[free]; print(f"   in units of pair noise: sd {zs.std():.3f}, max {zs.max():.2f}, min {zs.min():.2f}; expected max of {free.sum()} unit normals {math.sqrt(2*math.log(free.sum())):.2f}")
order = np.argsort(-rho)[:25]
print("the 25 most correlated translates D (rho, D, later-prime factors below 6000):")
for i in order:
    d = int(D[i]); fs = [p for p in PR if d % p == 0]; print(f"   {rho[i]:.5f}  D={d}  {fs}")
# by class of D: multiples of one prime p, and of two
for p in (467, 479, 487, 1009, 2003, 4001):
    m = np.zeros(H - 1, dtype=bool); m[p - 1::p] = True
    only = m.copy()
    for p2 in PR:
        if p2 != p: only[p2 - 1::p2] = False
    print(f"D multiple of {p} and of no other prime in (463,6000]: n {only.sum()}, mean rho {rho[only].mean():.5f}, sd {rho[only].std():.5f}, max {rho[only].max():.5f}")
pairs = [(467, 479), (467, 487), (479, 487), (467, 491), (487, 491), (499, 503)]
for a, b in pairs:
    m = np.arange(a * b, H, a * b) - 1; print(f"D multiple of {a}*{b}: n {len(m)}, mean rho {rho[m].mean():.5f} +- {rho[m].std()/math.sqrt(len(m)):.5f}, max {rho[m].max():.5f}")
np.save(f"rho.{pre}.{depth}.npy", rho.astype(np.float32))
