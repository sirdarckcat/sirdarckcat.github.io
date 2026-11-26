#!/usr/bin/env python3
"""What the members that agree with the most lists are worth: their exact sieve count (to 10^8) against the window's."""
import math, numpy as np
from base import *
from lists_scan import lists, scan
S = np.fromfile("S_100000000.u16", dtype=np.uint16).astype(np.float64); mu = S.mean(); sd = S.std()
cut = np.quantile(S, 0.015)
lam = -math.log(1 - 0.024 / 0.336642)          # nats per surviving row (0.074)
base_rate = float(np.exp(-lam * (S - mu)).mean())
print(f"window: mean {mu:.2f} sd {sd:.2f}; the 1.5% cut is S <= {cut:.0f}; nats per surviving row {lam:.4f}")
print("J | rho | agreement >= t | members | mean S | rows below the window mean | share of them under the 1.5% cut | hit chance of such a member / of an average member (e^(-lam dS) averaged)")
for J, rho in ((6, 0.1), (8, 0.1), (12, 0.05), (12, 0.1), (12, 0.2)):
    L = lists(J, rho); tot, _ = scan(L); mx = int(tot.max())
    r = np.corrcoef(tot, S)[0, 1]
    for t in range(mx, mx - 4, -1):
        sel = tot >= t; n = int(sel.sum())
        gain = float(np.exp(-lam * (S[sel] - mu)).mean()) / base_rate
        print(f"{J} | {rho} | {t} | {n} | {S[sel].mean():.1f} | {mu - S[sel].mean():.1f} | {100 * (S[sel] <= cut).mean():.1f}% | {gain:.2f}")
    print(f"   correlation of the agreement count with S over the window: {r:.4f}")
# the benchmark: selection by S itself
sel = S <= cut
print(f"benchmark, the kept 1.5% by sieve count: {int(sel.sum())} members, mean S {S[sel].mean():.1f}, hit chance / average member {float(np.exp(-lam * (S[sel] - mu)).mean()) / base_rate:.2f}")
