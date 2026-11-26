#!/usr/bin/env python3
"""Newman's phenomenon, recomputed: E_a(x) = sum over n < x, n = a mod 3 of (-1)^(binary digit sum of n).
Claim used: E_0(4^j) = 2*3^(j-1) exactly for powers of 4 (so the bias of a residue class mod 3 decays like x^(log 3/log 4 - 1) = x^-0.2075)."""
import numpy as np, math
J = 13; n = np.arange(4 ** J, dtype=np.int64); s = np.zeros_like(n); t = n.copy()
while t.any(): s += t & 1; t >>= 1
sg = 1 - 2 * (s & 1)
for j in (4, 6, 8, 10, 12, 13):
    x = 4 ** j; E = [int(sg[:x][n[:x] % 3 == a].sum()) for a in range(3)]
    print(f"x = 4^{j:2d}: E_0, E_1, E_2 = {E},  E_0 / 3^j = {E[0] / 3 ** j:.4f},  share of odd digit sums in classes 1 and 2: {0.5 - E[1] / (2 * x / 3):.5f} {0.5 - E[2] / (2 * x / 3):.5f},  x^-0.2075 = {x ** (math.log(3) / math.log(4) - 1):.5f}")
# prediction for the scan: N even <= 2e10, N = 2m, digit sum of N = digit sum of m, N mod 3 = 2m mod 3: class N=2 <-> m=1, N=1 <-> m=2
x = 1e10; print(f"at m ~ 10^10 the bias scale is x^-0.2075 = {x ** (math.log(3) / math.log(4) - 1):.5f}; at 10^200: {10 ** (200 * (math.log(3) / math.log(4) - 1)):.1e}")
