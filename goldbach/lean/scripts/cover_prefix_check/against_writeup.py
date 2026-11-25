#!/usr/bin/env python3
"""The referee's implementation (prefix_check.py) set against the research session's own inputs.

Needs the research session's cover_price.py and cover_price_hl.py (branch ccr-d4a17dd0-7uu03r, goldbach/sublinear/,
read at commit fbf0b09) in a directory DIR; they are not copied here.

    python3 against_writeup.py DIR table          my recursion and my dual with its dispersions: is its table reproduced?
    python3 against_writeup.py DIR dispersions    its dispersions (Hardy-Littlewood pair sum, closed formula) against the exact ones
    python3 against_writeup.py DIR sensitivity    which moduli carry the difference
"""
import math
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import cover_price as cp          # noqa: E402
import cover_price_hl as hl       # noqa: E402
import prefix_check as pc         # noqa: E402


def table():
    print("# my passes and my dual with the write-up's dispersions (its Hardy-Littlewood pair sum, cut to [1e-4, 1])")
    print("x | Q | loss as it was | lowest prefix entropy, at modulus | loss with the constraint | largest modulus with weight > 1.001 | weight at 3 | "
          "sum of level entropies - ln g0 | certificate: lowest prefix entropy, largest |entropy| where the multiplier is positive, primal - dual")
    for x, Qs in pc.TABLE:
        ps = hl.PairSums(x, max(Qs)); mods = [int(m) for m in ps.mods]; n = len(mods); theta = sum(math.log(s) for s in mods)
        for Q in Qs:
            vh, _ = ps.dispersions(Q); vs = np.clip(np.array(vh, dtype=float), 1e-4, 1.0); rows = float(cp.odd_primes_below(Q))
            D0, e0, t0, A0, p0 = pc.passes(mods, vs, rows, np.ones(n)); P0 = np.cumsum(e0)[:-1]
            D, lam, w, e1, t1, A1 = pc.solve_dual(mods, vs, rows)
            pmin, slack, gap = pc.kkt(lam, e1, D, A1)
            print(f"{x} | {Q} | {theta - D0:.1f} | {P0.min():.1f}, {mods[int(P0.argmin())]} | {theta - D:.1f} | {pc.frozen_up_to(mods, w)[1]} | {w[0]:.3f} | "
                  f"{e0.sum() - pc.BETA * A0 - D0:+.1e} | {pmin:+.1e}, {slack:.1e}, {gap:+.1e}", flush=True)


def dispersions():
    print("# variance/mean of the alive rows in a class: from the primes (prefix_check.dispersions, checked by enumeration) against the write-up's two formulas")
    for x, Q in ((463, 15907), (2999, 100000), (9973, 300000)):
        ps = hl.PairSums(x, Q); vh, li = ps.dispersions(Q); cl = hl.closed_formula(ps.mods, ps.phis, Q)
        pt = pc.Point(x, Q); vs, raw = pt.vs(pt.mods)
        print(f"\nx = {x}, Q = {Q}: {pt.rows:.0f} rows")
        print("modulus | from the primes | Hardy-Littlewood pair sum | closed formula | primes - pair sum")
        n = len(pt.mods); idx = sorted(set(list(range(0, 14)) + list(range(14, n, max(1, n // 20))) + [n - 1]))
        for i in idx:
            print(f"{pt.mods[i]} | {raw[i]:.4f} | {vh[i]:.4f} | {cl[i]:.4f} | {raw[i] - vh[i]:+.4f}")
        d = raw - np.array(vh); m = np.array(pt.mods)
        print(f"mean of (primes - pair sum): {d[m <= 43].mean():+.4f} over the moduli up to 43, {d[m > 43].mean():+.4f} above; root mean square above 43: {math.sqrt((d[m > 43] ** 2).mean()):.4f}")


def sensitivity():
    print("# which moduli carry the difference between the two sets of dispersions")
    print("x | Q | dispersions | loss as it was | loss with the constraint")
    for x, Q in ((463, 15907), (997, 40111), (1999, 91820), (9973, 300000)):
        ps = hl.PairSums(x, Q); vh, _ = ps.dispersions(Q); vh = np.clip(np.array(vh, dtype=float), 1e-4, 1.0)
        pt = pc.Point(x, Q); mods = pt.mods; n = len(mods); ve, raw = pt.vs(mods); m = np.array(mods)
        cases = [("Hardy-Littlewood pair sum, cut to [1e-4, 1] (the write-up's)", vh),
                 ("from the primes", ve),
                 ("from the primes, but 1e-4 at 3, 5, 7", np.where(m <= 7, 1e-4, ve)),
                 ("from the primes at 3, 5, 7, the pair sum above", np.where(m <= 7, ve, vh)),
                 ("from the primes up to 43, the pair sum above", np.where(m <= 43, ve, vh)),
                 ("the pair sum up to 43, from the primes above", np.where(m <= 43, vh, ve))]
        for name, vs in cases:
            D0 = pc.passes(mods, vs, pt.rows, np.ones(n))[0]; D = pc.solve_dual(mods, vs, pt.rows)[0]
            print(f"{x} | {Q} | {name} | {pt.theta - D0:.1f} | {pt.theta - D:.1f}", flush=True)


if __name__ == "__main__":
    {"table": table, "dispersions": dispersions, "sensitivity": sensitivity}[sys.argv[2]]()
