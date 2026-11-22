"""Closeness scoreboard: how big is each record's g(N) for the size of its N?

    python3 closeness.py            # table for every records/*/record.json

g(N) is the least prime p with N - p prime.  Three yardsticks, all functions
of L = ln N only:

  ceiling(N) = the largest g expected below N
      Nothing is proved about it, so this is a prediction: the median of the
      largest g among the even numbers below N in the Hardy-Littlewood model
      of ceiling_model.py, which has no fitted constant.  The model is
      tabulated in ceiling_table.json from 19 digits up and interpolated
      here.  Past the end of the table the formula below is used, which
      reproduces the table to about 1%: the ceiling is the prime number with
      index
          (L / 1.3203) * (L - ln 2 - A * ln L - B),
      1.3203 being twice the twin prime constant and A, B fitted to the table.
      Below the table (N < 3.3e18) the value is the table's first point scaled
      by L^2 ln L.  Checks of the model: ceiling_model.py and RESULTS.md.
      (Until 2026-11-22 this was 1.4 * L^2 * ln L, with the 1.4 fitted to the
      exhaustive search.  The model gives 1.40 at 19 digits as well, but the
      ratio grows with size, so that formula was 5% low at 25 digits and
      10% low at 40.)
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

TWIN2 = 1.3203236316                 # twice the twin prime constant
MEAN_INV_SINGULAR = 0.5665
HERE = os.path.dirname(os.path.abspath(__file__))

# Not ours: the largest g found by exhaustive search (Oliveira e Silva,
# Herzog & Pardi, Math. Comp. 2014).  The model's median for the largest g
# below this N is about 9,570, so it scores ~100%.
REFERENCE = [("exhaustive search <= 4e18 (not ours)", 3325581707333960528, 9781)]


def ln_int(n):
    s = str(n)
    return math.log(float(s[:17])) + (len(s) - min(len(s), 17)) * math.log(10)


def nth_prime(n):
    """The n-th prime from the first terms of its asymptotic expansion: 0.4% low at n = 6,000,
    0.1% at n = 100,000.  It is only used past the end of the table, where n is larger still."""
    ln, lln = math.log(n), math.log(math.log(n))
    return n * (ln + lln - 1 + (lln - 2) / ln - (lln * lln - 6 * lln + 11) / (2 * ln * ln))


def _load_table():
    """[(L, median ceiling)] from ceiling_table.json, and the least-squares fit of
    L - ln 2 - 1.3203 * (odd primes below the ceiling) / L  =  A * ln L + B."""
    rows = sorted(json.load(open(os.path.join(HERE, "ceiling_table.json"))).values(), key=lambda v: v["L"])
    pts = [(math.log(v["L"]), v["L"] - math.log(2) - TWIN2 * v["pi"] / v["L"]) for v in rows]
    n, sx, sy = len(pts), sum(x for x, _ in pts), sum(y for _, y in pts)
    sxx, sxy = sum(x * x for x, _ in pts), sum(x * y for x, y in pts)
    A = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return [(v["L"], v["median"]) for v in rows], A, (sy - A * sx) / n


TABLE, FIT_A, FIT_B = _load_table()


def _formula(L):
    return nth_prime(L / TWIN2 * (L - math.log(2) - FIT_A * math.log(L) - FIT_B))


def ceiling(L):
    """Median of the largest g among the even numbers below e^L (see the docstring)."""
    L0, c0 = TABLE[0]
    L1, c1 = TABLE[-1]
    if L < L0:
        return c0 * (L * L * math.log(L)) / (L0 * L0 * math.log(L0))
    if L >= L1:
        return _formula(L) * c1 / _formula(L1)       # continuous at the end of the table
    for (La, ca), (Lb, cb) in zip(TABLE, TABLE[1:]):
        if L <= Lb:
            f = (math.log(L) - math.log(La)) / (math.log(Lb) - math.log(La))
            return math.exp(math.log(ca) + f * (math.log(cb) - math.log(ca)))


def typical(L):
    n = MEAN_INV_SINGULAR * L
    if n < 6:
        return float("nan")
    ln, lln = math.log(n), math.log(math.log(n))
    return n * (ln + lln - 1 + (lln - 2) / ln)      # rough n-th prime: a yardstick, not a measurement


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
