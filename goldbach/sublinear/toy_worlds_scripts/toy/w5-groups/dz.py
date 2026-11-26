#!/usr/bin/env python3
"""D(z) = ln(P_z / X) for P_z = product of the primes <= z (theta(z), Chebyshev) and X = 10^200: the precision of the
single additive constraint when every prime up to z is a coordinate.  Also: what the dynamic programme (e^D states),
the certified meet in the middle and e^(D/2) lists would be at each depth."""
import math, numpy as np
LNX = 200 * math.log(10)
def theta_table(zs):
    zmax = max(zs); seg = 10 ** 7; small = np.ones(int(zmax ** .5) + 2, dtype=bool); small[:2] = False
    for i in range(2, int(len(small) ** .5) + 1):
        if small[i]: small[i * i::i] = False
    sp = np.nonzero(small)[0]; out = {}; th = 0.0; cnt = 0; zs = sorted(zs); zi = 0; lo = 2
    while lo <= zmax:
        hi = min(lo + seg, zmax + 1); sv = np.ones(hi - lo, dtype=bool)
        for p in sp:
            if p * p >= hi: break
            st = max(p * p, (lo + p - 1) // p * p); sv[st - lo::p] = False
        pr = np.nonzero(sv)[0] + lo
        while zi < len(zs) and zs[zi] < hi:
            sel = pr[pr <= zs[zi]]
            out[zs[zi]] = (th + float(np.log(sel.astype(np.float64)).sum()), cnt + len(sel)); zi += 1
        th += float(np.log(pr.astype(np.float64)).sum()); cnt += len(pr); lo = hi
    return out
zs = [463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 600, 700, 1000, 2000, 5000, 10 ** 4, 10 ** 5, 2 * 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8]
tt = theta_table(zs)
print(f"ln X = {LNX:.3f}   (theta(463) = {tt[463][0]:.3f}: the cover's modulus M = 2 * prod of the 89 odd primes; ln(X/M) = {LNX - tt[463][0]:.3f})")
print(f"{'z':>10} {'pi(z)':>9} {'theta(z)':>14} {'D = theta - 460.517':>20} {'D/ln 10 (digits)':>17} {'later primes':>13}")
for z in zs:
    th, c = tt[z]; D = th - LNX
    print(f"{z:>10} {c:>9} {th:>14.3f} {D:>20.3f} {D / math.log(10):>17.1f} {c - 90:>13}")
print("\nreach: D <= 14.04 (z = 499) dynamic programme run here; D <= 20.26 (503) certified meet in the middle run here;"
      "\n       D <= 26.49 (509) certified with the hybrid; e^(D/2) = 10^9 list entries at D = 41.4 (z about 523 to 541).")
