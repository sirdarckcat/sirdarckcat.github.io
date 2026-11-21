"""Cost ladder for N-1-certified Goldbach deserts on lazy complete covers.

    python3 ladder.py                # table (covers up to 5e6 are rebuilt, ~1 min)
    python3 ladder.py --rebuild      # also rebuild the 1e7 and 16,045,849 covers (~7 min)

Per rung: digits of the lazy cover (desert.lazy_full_cover), size of
P = N - g (1.5x the cover plus slack), expected tests ln P / (e^gamma ln B)
at sieve depth B, and time from a power law fitted to measured single-core
GMP modexps.  The independent session's bls/ladder.py does the same for the
paper's fixed-order covers; this one is ~9% shorter in digits.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desert  # noqa: E402

EG = math.exp(0.5772156649015329)
# measured here: (bits of the modulus, seconds for one gmpy2.powmod), 1 idle core, 2.1 GHz Xeon
MEASURED = [(37000, 5.93), (50000, 11.25), (75000, 30.46), (100000, 57.28), (150000, 150.59)]
RUNGS = [1_200_000, 2_000_000, 3_000_000, 5_000_000, 10_000_000, 16_045_849]
# exact lazy-cover sizes computed in the 2026-11-21 session (digits of prod r, g)
CACHED = {10_000_000: (40880.94, 10000141), 16_045_849: (61161.88, 16046137)}


def fit(points):
    xs = [math.log(b) for b, _ in points]
    ys = [math.log(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return math.exp(my - k * mx), k


def main():
    rebuild = "--rebuild" in sys.argv
    B = 1e9
    c, k = fit(MEASURED)
    print(f"modexp model: t = {c:.3g} * bits^{k:.2f} s (GMP, 1 core); sieve depth {B:.0e}")
    print(f"{'target g >':>12} {'g':>10} {'cover digits':>13} {'digits of N':>12} {'tests':>7} "
          f"{'s/test':>7} {'core-h':>8} {'4 cores':>9}")
    for Q in RUNGS:
        if Q in CACHED and not rebuild:
            digits, g = CACHED[Q]
        else:
            cover = desert.lazy_full_cover(Q)
            digits = sum(math.log10(r) for r, _ in cover)
            g = desert.least_uncovered_prime(Q, cover)
        bm = digits * math.log2(10) + 20             # bits of m = m0 + t*Mc
        bits = 1.5 * bm + 3
        tests = bits * math.log(2) / (EG * math.log(B))
        t = c * bits ** k
        core_h = tests * t / 3600
        wall = core_h / 4
        print(f"{Q - 1 if Q == 16_045_849 else Q:>12,} {g:>10,} {digits:>13,.0f} {bits * math.log10(2):>12,.0f} "
              f"{tests:>7,.0f} {t:>7.0f} {core_h:>8.1f} "
              f"{(f'{wall:.1f} h' if wall < 48 else f'{wall / 24:.1f} d'):>9}")


if __name__ == "__main__":
    main()
