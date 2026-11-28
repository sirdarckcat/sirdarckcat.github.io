#!/usr/bin/env python3
"""The parity of Omega(n) on z-rough n <= x against the Buchstab-type prediction
      sum_{n<=x, P^-(n)>z} lambda(n) ~ -(x/ln z) rho(u-1)/u,   u = ln x/ln z,
   so that mean lambda on rough numbers = -rho(u-1)/(u omega(u)) and P(prime | rough, Omega odd) = 2/(u omega(u) + rho(u-1)).
   usage: rough_parity.py X"""
import sys, math, numpy as np, time
X = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10 ** 9
# Dickman rho and Buchstab omega on a grid
h = 1e-3; U = 12; ng = int(round(U / h)) + 1; ug = np.arange(ng) * h
rho = np.ones(ng); om = np.zeros(ng); i1 = int(round(1 / h)); i2 = 2 * i1
for i in range(i1 + 1, ng):   # u rho(u) = integral_{u-1}^{u} rho  (positive terms only)
    rho[i] = h * (rho[i - i1] / 2 + rho[i - i1 + 1:i].sum()) / (ug[i] - h / 2)
om[i1:i2 + 1] = 1 / ug[i1:i2 + 1]; W = ug * om
for i in range(i2 + 1, ng):   # (u omega)' = omega(u-1)
    W[i] = W[i - 1] + h * 0.5 * (om[i - 1 - i1] + om[i - i1]); om[i] = W[i] / ug[i]
R = lambda u: float(np.interp(u, ug, rho)); O = lambda u: float(np.interp(u, ug, om))
print(f"rho(10) = {R(10):.6e} (literature 2.77017e-11)"); print(f"rho(2) = {R(2):.6f} (1 - ln 2 = {1 - math.log(2):.6f}), rho(3) = {R(3):.6f}, omega(3) = {O(3):.6f}, e^gamma omega(10) = {math.exp(0.5772156649) * O(10):.8f}")
ZMAX = 1100
sq = int(X ** .5) + 1
s = np.ones(sq + 1, dtype=bool); s[:2] = False
for i in range(2, int(sq ** .5) + 1):
    if s[i]: s[i * i::i] = False
P = np.nonzero(s)[0]
zs = sorted(set(int(round(X ** (1 / u))) for u in (3, 3.5, 4, 4.5, 5, 6, 7, 8)))
tot = {z: [0, 0, 0, 0.0, 0.0] for z in zs}       # rough count, sum lambda, primes
L = 20_000_000; t0 = time.time()
for a in range(1, X + 1, L):
    b = min(a + L, X + 1); n = b - a
    omg = np.zeros(n, dtype=np.int8); lg = np.zeros(n, dtype=np.float32); lpf = np.zeros(n, dtype=np.int16)
    for p in P:
        p = int(p); lp = math.log(p); pk = p
        while pk <= X:
            i0 = (-a) % pk
            if i0 < n:
                omg[i0::pk] += 1; lg[i0::pk] += lp
            pk *= p
        if p <= ZMAX:
            i0 = (-a) % p; sl = lpf[i0::p]; sl[sl == 0] = p; lpf[i0::p] = sl
    nn = np.arange(a, b, dtype=np.float64); rem = np.log(nn) - lg > 0.5
    omg += rem.astype(np.int8)
    isprime = (omg == 1) & rem & (lg == 0)
    lam = 1 - 2 * (omg & 1).astype(np.int64)
    for z in zs:
        rough = (lpf == 0) | (lpf > z)
        if a == 1: rough[0] = False
        tot[z][0] += int(rough.sum()); tot[z][1] += int(lam[rough].sum()); tot[z][2] += int((isprime & rough).sum())
        inv = 1.0 / nn[rough]; tot[z][3] += float((lam[rough] * inv).sum()) + (1.0 if a == 1 else 0.0); tot[z][4] += float(inv.sum()) + (1.0 if a == 1 else 0.0)
print(f"x = {X}; time {time.time() - t0:.0f} s")
I = np.concatenate([[0], np.cumsum((om[1:] + om[:-1]) * h / 2)])      # integral of omega from 0 (omega = 0 below 1)
print("LOGARITHMIC sums, the term n = 1 included (limit: rho(u); the error is of the order of the Mertens error at z):")
print("z | u | sum of lambda(n)/n over z-rough n <= x | rho(u) | sum of 1/n over z-rough n <= x | 1 + integral_1^u omega | mean lambda, log weight | rho(u)/(1 + int omega)")
for z in zs:
    u = math.log(X) / math.log(z); c, sl, pr, a1, a0 = tot[z]; io = 1 + float(np.interp(u, ug, I))
    print(f"{z} | {u:.3f} | {a1:+.6f} | {R(u):+.6f} | {a0:.5f} | {io:.5f} | {a1 / a0:+.6f} | {R(u) / io:+.6f}")
print("\nNATURAL sums (leading term only; corrections of relative order 1/ln z):")
print("z | u | rough n <= x | sum lambda | mean lambda on rough | rho'(u)/omega(u) = -rho(u-1)/(u omega(u)) | primes/odd-Omega rough | predicted 2/(u omega(u) + rho(u-1)) | share of rough that are prime, 1/(u omega(u))")
for z in zs:
    u = math.log(X) / math.log(z); c, sl, pr = tot[z][:3]; odd = (c - sl) / 2
    print(f"{z} | {u:.3f} | {c} | {sl} | {sl / c:+.6f} | {-R(u - 1) / (u * O(u)):+.6f} | {pr / odd:.5f} | {2 / (u * O(u) + R(u - 1)):.5f} | {pr / c:.5f}, {1 / (u * O(u)):.5f}")
print("working points and the exact function-field table: parity_worth.py; local check at 1e12: mini_parity.py, law_check.py")
