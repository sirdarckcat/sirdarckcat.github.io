"""Independent check of the WP3 decoding-vs-existence barrier.

WP3 (goldbach/phd/wp3_small_representative_memo.md) argues that no
parameter choice makes an oversized CRT cover both *realisable* and
*decodable*: representatives below B exist only when the modulus pool is
large, but the GSS/Johnson list-decoding radius grows with the pool, so
the radius always outruns the achievable cover mass.  v1 of that memo
claimed the opposite ("open window") by optimising the two conditions at
different agreement sizes; this script re-derives both at the SAME mass A
from an independent parametrisation and confirms the retraction.

Design entropy is obtained as a Legendre transform rather than by
binomial counting: at inverse temperature beta each position r is
occupied with probability L*r^-beta/(1 + L*r^-beta), giving

    A(beta)     = sum_r ln r * occ_r                (cover mass)
    G(beta)     = beta*A + sum_r ln(1 + L*r^-beta)  (design entropy)
    exists  <=> A - G(A) <= ln B
    decodes <=> A > A_J = sqrt(L * ln B * P),  P = sum_pool ln r

Usage: verify_barrier.py [--digits 100] [--json out.json]
"""

import argparse
import json
import math

import numpy as np
from sympy import primerange


def analyse(R, L, lnB):
    r = np.array(list(primerange(3, R)), dtype=np.float64)
    lnr = np.log(r)
    P = float(lnr.sum())
    AJ = math.sqrt(L * lnB * P)

    def AmG(beta):
        w = L * np.exp(-beta * lnr)
        occ = w / (1.0 + w)
        A = float((lnr * occ).sum())
        return A, A - (beta * A + float(np.log1p(w).sum()))

    lo, hi = 1e-6, 50.0            # A - G decreases as beta rises
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if AmG(mid)[1] > lnB:
            lo = mid
        else:
            hi = mid
    Amax = AmG(0.5 * (lo + hi))[0]
    return {"R": R, "L": L, "n": len(r), "pool_mass": P,
            "A_max_exists": Amax, "A_J_decodes": AJ, "ratio": Amax / AJ}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digits", type=float, default=100.0)
    ap.add_argument("--json")
    a = ap.parse_args()
    lnB = a.digits * math.log(10)
    rows = [analyse(R, L, lnB)
            for R in (300, 1000, 3000, 10000, 30000, 60000,
                      100000, 300000, 1000000)
            for L in (1, 2, 4, 16, 64)]
    print(f"B = 10^{a.digits:g}   (ln B = {lnB:.1f})")
    print(f"{'R':>8} {'L':>3} {'poolmass':>9} {'A_max':>8} {'A_J':>8} {'ratio':>7}")
    for row in rows:
        if row["L"] in (1, 16):
            print(f"{row['R']:8d} {row['L']:3d} {row['pool_mass']:9.0f} "
                  f"{row['A_max_exists']:8.0f} {row['A_J_decodes']:8.0f} "
                  f"{row['ratio']:7.3f}")
    b = max(rows, key=lambda x: x["ratio"])
    print(f"\nbest ratio {b['ratio']:.3f} at R={b['R']}, L={b['L']} "
          f"(A_max={b['A_max_exists']:.0f} vs A_J={b['A_J_decodes']:.0f})")
    print("WINDOW OPEN — barrier broken" if b["ratio"] > 1 else
          "WINDOW CLOSED at every pool size — WP3 retraction confirmed")
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
