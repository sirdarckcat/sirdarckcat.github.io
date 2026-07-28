"""Bisect the feasibility boundary H + E = D*ln10 and tabulate E_min(D).

For each digit size D and each conditioning mode (classic k=1 vs
set-valued), find the Lagrange price lambda where the size budget is
exactly spent, and report the resulting failure exponent E -- the log of
the number of candidates any search must examine at that size.

Usage: frontier_table.py [--rc RC] [--Q Q] [--digits 100,110,...]
"""

import argparse
import json
import math

import entropy_frontier as ef

LN10 = math.log(10)


def boundary(digits, rc, q, classic, lo=0.003, hi=0.30, iters=9):
    """Bisect lambda for H + E == lnB; return the best feasible state."""
    best = None
    for _ in range(iters):
        mid = math.sqrt(lo * hi)
        f = ef.Frontier(digits, rc, q, classic)
        f.sweep(mid, rounds=3)
        H, E = f.H(), f.E()
        if H + E <= f.lnB:                 # feasible: can afford to spend more
            if best is None or E < best["E"]:
                best = {"lam": mid, "H": H, "E": E,
                        "moduli": sum(1 for r, k in f.k.items() if k < r),
                        "k1": sum(1 for r, k in f.k.items() if k == 1)}
            hi = mid
        else:
            lo = mid
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rc", type=int, default=5000)
    ap.add_argument("--Q", type=int, default=100003)
    ap.add_argument("--digits", default="100,110,120,130,140,150")
    ap.add_argument("--out")
    a = ap.parse_args()
    ds = [float(x) for x in a.digits.split(",")]
    rows = []
    print(f"{'D':>5} {'mode':>10} {'E':>7} {'cands':>10} {'H':>7} "
          f"{'moduli':>7} {'k=1':>5}")
    for d in ds:
        for classic in (True, False):
            b = boundary(d, a.rc, a.Q, classic)
            if b is None:
                print(f"{d:5.0f} {'classic' if classic else 'set':>10} "
                      f"{'INFEASIBLE':>7}")
                continue
            b.update(digits=d, classic=classic)
            rows.append(b)
            print(f"{d:5.0f} {'classic' if classic else 'set':>10} "
                  f"{b['E']:7.2f} {'10^%.1f' % (b['E'] / LN10):>10} "
                  f"{b['H']:7.1f} {b['moduli']:7d} {b['k1']:5d}", flush=True)
    if a.out:
        json.dump(rows, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
