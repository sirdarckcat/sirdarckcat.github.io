#!/usr/bin/env python3
"""The entropy of the first m moduli in the constrained solution, with the dispersions from the primes and with the
write-up's, for comparison with the number of settings of those moduli seen among sampled complete covers.

    python3 prefix_entropies.py DIR x m1,m2,... Q ...        (DIR: the research session's cover_price.py, cover_price_hl.py)
"""
import math
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import cover_price as cp          # noqa: E402
import cover_price_hl as hl       # noqa: E402
import prefix_check as pc         # noqa: E402

x = int(sys.argv[2]); ms = [int(a) for a in sys.argv[3].split(",")]; Qs = [int(a) for a in sys.argv[4:]]
print(f"# prefix_entropies.py: x = {x}; entropy in nats of the first m moduli (prefix sum of the level entropies)")
print("Q | dispersions | ln g0 as it was, with the constraint | " +
      " | ".join(f"first {m} moduli: as it was, with the constraint" for m in ms) + " | moduli with weight > 1, largest")
ps = hl.PairSums(x, max(Qs))
for Q in Qs:
    pt = pc.Point(x, Q); mods = pt.mods; n = len(mods)
    ve, _ = pt.vs(mods)
    vh, _ = ps.dispersions(Q); vh = np.clip(np.array(vh, dtype=float), 1e-4, 1.0)
    for name, vs in (("from the primes", ve), ("the write-up's", vh)):
        D0, e0, _, _, _ = pc.passes(mods, vs, pt.rows, np.ones(n)); D, lam, w, e1, _, _ = pc.solve_dual(mods, vs, pt.rows)
        P0 = np.cumsum(e0); P1 = np.cumsum(e1)
        cols = " | ".join(f"(up to {mods[m - 1]}) {P0[m - 1]:.1f}, {P1[m - 1]:.1f}" for m in ms)
        nf, mf = pc.frozen_up_to(mods, w)
        print(f"{Q} | {name} | {D0:.1f}, {D:.1f} | {cols} | {nf}, {mf}", flush=True)
