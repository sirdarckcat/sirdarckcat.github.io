"""Closeness scoreboard: how big is each record's g(N) for the size of its N?

    python3 closeness.py            # table for every records/*/record.json

g(N) is the least prime p with N - p prime.  Three yardsticks, all functions
of L = ln N only:

  ceiling(N) = C * L^2 * ln L, C = 1.4
      the largest g any number of that size is expected to have (the
      Granville / van de Lune - te Riele law; C is fitted to the exhaustive
      data, g <= 9,781 for all even N <= 4*10^18 -- see
      SOK_GOLDBACH_GAPS.md section 6).  CONJECTURAL: nothing like it is proved.
  typical(N) = the 0.5665*L-th prime
      the mean g of a random even number of that size (Hardy-Littlewood:
      the count of primes p <= y with N - p prime is about S(N)*pi(y)/L;
      0.5665 is the mean of 1/S(N) over even N).  Measured on random
      numbers: 2,558 vs 2,689 predicted at 300 digits, 9,282 vs 10,691 at
      1,000 digits.
  ideal digits = the size at which ceiling() first reaches this g
      i.e. how small a "perfect" N for this g would be.

closeness = g / ceiling(N).  The trivial bound g <= N/2 is attained only by
N = 4 and N = 6; it says nothing at any other size.

frontier: a record is ON the frontier when no smaller N in the table has a g
at least as large.  Such a record is at once the smallest known N for its g
(threshold game T) and the largest known g below its N (budget game R);
every other row names the smaller N that beats it.

Python 3 standard library only.
"""
import glob
import json
import math
import os
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

C = 1.4
MEAN_INV_SINGULAR = 0.5665
HERE = os.path.dirname(os.path.abspath(__file__))

# Not ours: the largest g found by exhaustive search (Oliveira e Silva,
# Herzog & Pardi, Math. Comp. 2014).  C is fitted to it, so it scores ~100%.
REFERENCE = [("exhaustive search <= 4e18 (not ours)", 3325581707333960528, 9781)]


def ln_int(n):
    s = str(n)
    return math.log(float(s[:17])) + (len(s) - min(len(s), 17)) * math.log(10)


def ceiling(L):
    return C * L * L * math.log(L)


def typical(L):
    n = MEAN_INV_SINGULAR * L
    if n < 6:
        return float("nan")
    ln, lln = math.log(n), math.log(math.log(n))
    return n * (ln + lln - 1 + (lln - 2) / ln)      # n-th prime, to ~1%


def ideal_digits(g):
    lo, hi = 2.0, 1e9
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ceiling(mid) < g else (lo, mid)
    return hi / math.log(10)


def rows():
    out = [(name, N, g) for name, N, g in REFERENCE]
    for path in sorted(glob.glob(os.path.join(HERE, "records", "*", "record.json"))):
        r = json.load(open(path))
        if "N" in r and "g" in r:
            out.append((os.path.basename(os.path.dirname(path)), int(r["N"]), int(r["g"])))
    return out


def frontier(table):
    """name -> "yes", or the name of a smaller N with g at least as large."""
    out, best_g, best_name = {}, 0, None
    for N, g, name in sorted((N, g, name) for name, N, g in table):
        out[name] = "yes" if g > best_g else "no: " + best_name
        if g > best_g:
            best_g, best_name = g, name
    return out


def main():
    table, raw = [], rows()
    front = frontier(raw)
    for name, N, g in raw:
        L = ln_int(N)
        table.append((g / ceiling(L), name, g, len(str(N)), ceiling(L), g / typical(L), ideal_digits(g)))
    print(f"{'record':40s} {'g':>10s} {'digits':>7s} {'ceiling':>15s} {'closeness':>10s} "
          f"{'x typical':>9s} {'ideal digits':>12s}  frontier")
    for score, name, g, digits, ceil, xt, ideal in sorted(table, reverse=True):
        print(f"{name:40s} {g:>10,d} {digits:>7,d} {ceil:>15,.0f} {100 * score:>9.4f}% "
              f"{xt:>9.1f} {ideal:>12,.0f}  {front[name]}")


if __name__ == "__main__":
    main()
