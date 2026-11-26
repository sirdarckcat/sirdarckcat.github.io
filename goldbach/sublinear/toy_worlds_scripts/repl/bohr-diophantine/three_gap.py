#!/usr/bin/env python3
"""Three-distance check on the real window: for a class pair (c1, c2) of (467, 479) the members are k = k12 + 223693 t,
t < ceil((K - k12)/223693) <= 96, and their classes modulo a third prime s form a progression in Z/s.  Gap lengths of that
progression on the circle Z/s (three-distance theorem: at most 3 values), and what it buys for lists."""
import numpy as np, math
from base import *
P2 = 467 * 479
for s in (487, 491, 499, 503, 509, 521):
    d = P2 % s; L = K // P2
    pts = np.sort((np.arange(L) * d) % s); gaps = np.diff(np.concatenate([pts, [pts[0] + s]]))
    f, g = tables(s); n = int(math.ceil(0.10 * s)); G = np.argsort(-g, kind="stable")[:n]
    ind = np.zeros(s, bool); ind[G] = True
    # how many of the best-10% classes fall on the progression (for k12 = 0), against L * rho
    hit = int(ind[(np.arange(L) * d) % s].sum())
    runs = int((np.diff(np.sort(G)) > 1).sum()) + 1
    print(f"s = {s}: step {d}, {L} points, gap lengths {sorted(set(gaps.tolist()))} (count {len(set(gaps.tolist()))}); best-10% list: {n} classes in {runs} runs of consecutive classes (an interval would be 1 run); points of the progression in the list {hit} (L*rho = {L * n / s:.1f})")
