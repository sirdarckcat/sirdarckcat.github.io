#!/usr/bin/env python3
"""Miniature of the parity obstruction, where lambda can be computed: integers n in [X, X + L), X = 10^12, fully factored by a sieve.
   Among the z-rough n (no prime factor <= z), does any function of the small-prime pattern of the neighbourhood predict lambda(n) = (-1)^Omega(n),
   or primality?  usage: mini_parity.py [X] [L] [z]"""
import sys, math, numpy as np, time
X = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10 ** 12
L = int(float(sys.argv[2])) if len(sys.argv) > 2 else 20_000_000
z = int(sys.argv[3]) if len(sys.argv) > 3 else 100
pad = 8; a = X - pad; n = L + 2 * pad; hi = a + n
sq = int(math.isqrt(hi)) + 1
s = np.ones(sq + 1, dtype=bool); s[:2] = False
for i in range(2, int(sq ** .5) + 1):
    if s[i]: s[i * i::i] = False
P = np.nonzero(s)[0]; t0 = time.time()
omg = np.zeros(n, dtype=np.int8); lg = np.zeros(n, dtype=np.float64); lpf = np.zeros(n, dtype=np.int32); osm = np.zeros(n, dtype=np.int8); lsm = np.zeros(n, dtype=np.float32)
for p in P:
    p = int(p); lp = math.log(p); pk = p
    while pk < hi:
        i0 = (-a) % pk
        if i0 < n: omg[i0::pk] += 1; lg[i0::pk] += lp
        pk *= p
    if p <= 1000:
        i0 = (-a) % p; sl = lpf[i0::p]; sl[sl == 0] = p; lpf[i0::p] = sl; osm[i0::p] += 1; lsm[i0::p] += lp
nn = np.arange(a, hi, dtype=np.float64); rem = (np.log(nn) - lg) > 1e-6; omg += rem.astype(np.int8)
lam = (1 - 2 * (omg & 1)).astype(np.float64); isp = (omg == 1)
print(f"X = {X}, L = {L}: factored in {time.time() - t0:.0f} s; mean lambda over all n = {lam[pad:-pad].mean():+.6f}; primes {int(isp[pad:-pad].sum())} (expected {L / math.log(X):.0f})")
idx = np.arange(pad, n - pad); rough = (lpf[idx] == 0) | (lpf[idx] > z); I = idx[rough]; m = len(I)
u = math.log(X) / math.log(z)
y = lam[I]; yp = isp[I].astype(np.float64)
print(f"z = {z} (u = {u:.2f}): rough {m} ({m / L:.5f}); mean lambda on rough {y.mean():+.6f} +- {1 / math.sqrt(m):.6f}; primes among rough {yp.mean():.5f}; primes among rough with Omega odd {yp.sum() / (y < 0).sum():.5f}")
feats = {}
for c in (-6, -4, -3, -2, -1, 1, 2, 3, 4, 6):
    feats[f"number of primes <= 1000 dividing n{c:+d}"] = osm[I + c].astype(float)
    feats[f"ln of the 1000-smooth squarefree kernel of n{c:+d}"] = lsm[I + c].astype(float)
    feats[f"n{c:+d} has no prime factor in (2, 1000]"] = ((lpf[I + c] == 0) | (lpf[I + c] == 2) & (osm[I + c] == 1)).astype(float)
    feats[f"lambda(n{c:+d})"] = lam[I + c]
    feats[f"n{c:+d} is prime"] = isp[I + c].astype(float)
    feats[f"Omega(n{c:+d})"] = omg[I + c].astype(float)
nv = (a + I).astype(np.int64)
for q_ in (3, 4, 5, 7, 8, 11, 13, 16):
    for r_ in range(1, q_):
        if math.gcd(r_, q_) == 1 and (q_ > 4 or r_ == 1): feats[f"n = {r_} mod {q_}"] = (nv % q_ == r_).astype(float)
feats["own: number of primes in (z, 1000] dividing n"] = osm[I].astype(float)
feats["own: least prime factor <= 1000 (0 if none)"] = np.where(lpf[I] > 0, np.log(np.maximum(lpf[I], 1)), 0.0)
res = []; resp = []
# for the primality target, compare inside the rough numbers; 'own' features are legitimately informative for lambda? (they are functions of n's own small factors above z)
for name, x in feats.items():
    sd = x.std()
    if sd == 0: continue
    xc = x - x.mean()
    res.append(((xc * (y - y.mean())).mean() / (sd * y.std()) * math.sqrt(m), name)); resp.append(((xc * (yp - yp.mean())).mean() / (sd * yp.std()) * math.sqrt(m), name))
for label, rr in (("lambda(n)", res), ("primality of n", resp)):
    nb = [(zv, nme) for zv, nme in rr if not nme.startswith("own")]; own = [(zv, nme) for zv, nme in rr if nme.startswith("own")]
    zz = np.array([zv for zv, _ in nb]); nb.sort(key=lambda t: -abs(t[0]))
    print(f"\ntarget {label}: {len(zz)} features of the neighbourhood and of n modulo small numbers: max |z| = {abs(zz).max():.2f}, mean z^2 = {(zz ** 2).mean():.3f}; expected max of {len(zz)} normals about {math.sqrt(2 * math.log(len(zz))):.2f}")
    print("   largest: " + "; ".join(f"{nme}: {zv:+.2f}" for zv, nme in nb[:6]))
    print("   n's own factors between z and 1000 (inside the sieve range if the sieve went to 1000): " + "; ".join(f"{nme}: {zv:+.2f}" for zv, nme in own))
