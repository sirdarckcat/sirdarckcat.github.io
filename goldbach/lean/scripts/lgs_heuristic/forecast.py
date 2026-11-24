#!/usr/bin/env python3
"""Where does the next term of A025018 fall?  A forecast with no primes in it, against the real terms.

The N generator (GoldbachGaps/RecordWalk.lean, scripts/record_gen/ngen.c) announces N when no
striker up to the current record G hits it.  The model of model.py gives every even N a chance
u(N, m) of being unstruck by the m odd primes up to G, so after a term (N_k, g_k) the number of
announcements expected among the even numbers in (N_k, x] is

        E(x) = sum of u(N, m) over the even N in (N_k, x],      m = number of odd primes <= g_k,

and the next term is where a Poisson clock of that rate first rings: E(N_{k+1}) is exponential
with mean 1.  This script inverts E: for each known term it prints the 5%, 50% and 95% points of
the forecast for the next one, and where the next one really fell.

    python3 -I forecast.py terms.txt 0.92 terms_68_69.txt > forecast.txt

(further files of terms are appended to the first.)  This is the front law of model.py, section 3,
read on the N axis: the same model, the same constant, no new fit.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model  # noqa: E402

STEP, NSTEP = 0.0125, 1200           # grid in ln x: up to a factor e^15 beyond the term


def forecast(N0, m, c, levels):
    """the points x with E(x) = level, as multiples of N0 (None if beyond the grid)"""
    l0 = math.log(N0)
    ls = l0 + STEP * np.arange(NSTEP + 1)
    xs = np.exp(ls)
    mid = 0.5 * (ls[1:] + ls[:-1])
    dens = np.array([model.ubar(l, m, c) for l in mid])
    cum = np.concatenate(([0.0], np.cumsum(0.5 * (xs[1:] - xs[:-1]) * dens)))       # even numbers: half of them
    out = []
    for lev in levels:
        i = int(np.searchsorted(cum, lev))
        if i > NSTEP: out.append(None); continue
        f = (lev - cum[i - 1]) / (cum[i] - cum[i - 1])
        out.append(math.exp(ls[i - 1] + f * STEP - l0))
    return out, (lambda x: float(np.interp(math.log(x), ls, cum)))


def fmt(r):
    return "   beyond" if r is None else f"{r:9.3f}"


def main():
    terms = []
    for path in [sys.argv[1]] + sys.argv[3:]:
        terms += [tuple(map(int, l.split())) for l in open(path) if l.strip() and not l.startswith('#')]
    c = float(sys.argv[2]) if len(sys.argv) > 2 else 0.92
    idx = {int(p): i + 1 for i, p in enumerate(model.ODD)}
    levels = [-math.log(1 - q) for q in (0.05, 0.5, 0.95)]
    print(f"Forecast of the next term from the current one; dependence constant c = {c}")
    print("x5, x50, x95: the next term is expected below N * x with probability 5%, 50%, 95%")
    print("          term N     value      x5       x50       x95    real next/N   P(next <= real)")
    inside = below = above = 0
    ps, widths = [], []
    for k in range(len(terms)):
        N0, g0 = terms[k]
        if N0 < 1000: continue
        qs, E = forecast(N0, idx[g0], c, levels)
        if k + 1 < len(terms):
            r = terms[k + 1][0] / N0
            p = 1 - math.exp(-E(terms[k + 1][0]))
            ps.append(p)
            if p < 0.05: below += 1
            elif p > 0.95: above += 1
            else: inside += 1
            if qs[2] is not None: widths.append(qs[2] / qs[0])
            print(f"{N0:20d} {g0:6d} {fmt(qs[0])} {fmt(qs[1])} {fmt(qs[2])} {r:12.3f} {p:12.3f}")
        else:
            print(f"{N0:20d} {g0:6d} {fmt(qs[0])} {fmt(qs[1])} {fmt(qs[2])}      unknown")
            last = (N0, qs)
    K = len(ps)
    print(f"\n{K} forecasts: {inside} real terms inside the 5%-95% band ({0.9 * K:.1f} expected), {below} before it"
          f" ({0.05 * K:.1f} expected), {above} after it ({0.05 * K:.1f} expected)")
    print(f"mean of P(next <= real) = {np.mean(ps):.3f} (0.5 expected, standard error {1 / math.sqrt(12 * K):.3f})")
    print(f"the band is wide: x95 / x5 has median {np.median(widths):.0f}; the ratio of (x95 - 1) to (x5 - 1) is 58 by construction")
    N0, qs = last
    print(f"\nthe term after {N0}: 5% below {N0 * qs[0]:.3e}, 50% below {N0 * qs[1]:.3e}, 95% below "
          + ("beyond the grid" if qs[2] is None else f"{N0 * qs[2]:.3e}"))


if __name__ == "__main__":
    main()
