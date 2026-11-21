#!/usr/bin/env python3
"""Cost ladder for BLS-certified Game-1 deserts (full cover + one modexp).

For each rung Q, the script:
  * builds the full cover (or uses the paper's size for 10^8);
  * sizes P: F = 2^n must satisfy F^3 > P, so P has ~1.5x the cover's digits;
  * estimates expected BLS tests as ln P / (e^gamma ln S), where S is the
    sieve bound (validated: Q=1e5 predicted 123, observed 122);
  * prices one test from a power law fitted to measured single-core GMP
    modexps (gmpy2 2.3.2 / GMP 6.3.0, 2.1 GHz Xeon).

    python3 goldbach/bls/ladder.py            # table from the fitted model
    python3 goldbach/bls/ladder.py --bench    # re-measure the modexp points
"""
import argparse
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from full_cover import build  # noqa: E402

# measured (digits, seconds per a^((P-1)/2) mod P), this container, 1 core
MEASURED = [(11500, 7.01), (17500, 17.16), (37500, 91.02), (67000, 342.29)]
RUNGS = [1_200_000, 2_000_000, 5_000_000, 10_000_000, 16_045_849,
         100_000_000]
PAPER_DIGITS = {100_000_000: 327_455}   # paper Table tab:results
EG = math.exp(0.5772156649015329)


def bench():
    import gmpy2
    rng = random.Random(7)
    out = []
    for d, _ in MEASURED:
        bits = math.ceil(d * math.log2(10))
        n = gmpy2.mpz(rng.getrandbits(bits) | (1 << (bits - 1)) | 1)
        t0 = time.perf_counter()
        gmpy2.powmod(3, (n - 1) // 2, n)
        out.append((d, time.perf_counter() - t0))
        print(f"  measured {d} digits: {out[-1][1]:.2f}s", flush=True)
    return out


def fit(points):
    """least-squares power law t = c * d^k in log space"""
    xs = [math.log(d) for d, _ in points]
    ys = [math.log(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    k = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
         / sum((x - mx) ** 2 for x in xs))
    return math.exp(my - k * mx), k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--sieve-small", type=float, default=2e8)
    ap.add_argument("--sieve-big", type=float, default=1e10)
    a = ap.parse_args()
    pts = bench() if a.bench else MEASURED
    c, k = fit(pts)
    print(f"modexp model: t = {c:.3g} * digits^{k:.2f} s (GMP, 1 core)")
    print(f"{'Q':>12} {'cover':>7} {'M dig':>8} {'P dig':>8} {'s/test':>8} "
          f"{'tests':>7} {'core-days':>10} {'4-core box':>11}")
    for Q in RUNGS:
        if Q in PAPER_DIGITS:
            dM, cong = PAPER_DIGITS[Q], 60_627
        else:
            cover, _ = build(Q)
            dM = int(sum(math.log10(r) for r, _ in cover)) + 1
            cong = len(cover) + 1
        dP = int(1.5 * dM) + 9
        S = a.sieve_small if Q < 5_000_000 else a.sieve_big
        tests = dP * math.log(10) / (EG * math.log(S))
        t = c * dP ** k
        core_s = tests * t
        box = core_s / 4
        box_s = (f"{box / 3600:.1f} h" if box < 2 * 86400
                 else f"{box / 86400:.1f} d")
        print(f"{Q:>12,} {cong:>7,} {dM:>8,} {dP:>8,} {t:>8.0f} "
              f"{tests:>7,.0f} {core_s / 86400:>10.2f} {box_s:>11}")


if __name__ == "__main__":
    main()
