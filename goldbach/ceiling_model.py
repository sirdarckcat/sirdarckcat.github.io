#!/usr/bin/env python3
"""How large can g(N) get for a number of a given size?  A model with no fitted constant.

g(N) is the least prime p with N - p prime.  Nothing about its maximum is
proved (Goldbach's conjecture itself is open).  This file computes what the
Hardy-Littlewood prime tuple heuristic predicts, which is the best available
substitute for an exact answer:

    python3 ceiling_model.py count N g [particles]
        expected number of even n < N with g(n) >= g
    python3 ceiling_model.py ceiling N [particles]
        the largest g below N: median and 5% / 95% points of its distribution
    python3 ceiling_model.py table d1,d2,... [particles]
        the same for N = 10^d, written to ceiling_table.json (closeness.py reads it)
    python3 ceiling_model.py holders [minN]
        check against record_holders.txt (the 69 record holders below 4*10^18)
    python3 ceiling_model.py tail samples.txt A B y1 y2 ...
        check against a sample of random even N in [A, B) made by gsample.c

The model.  Fix the residues c_q = N mod q for the odd primes q <= z.  The
complement N - p has no prime factor <= z exactly when p != c_q (mod q) for
all of them.  A complement that survives is prime with probability

    eps_z = (1 / ln N) * prod_{q <= z} (1 - 1/q)^-1,

independently of the others.  So for a random even N of size e^L

    Z(L, g) = P(g(N) >= g) = average over the residues of
              (1 - eps_z)^(number of odd primes p < g that survive).

This is the inclusion-exclusion sum over tuples of primes p < g weighted by
their Hardy-Littlewood singular series, written as an average.  The answer
does not depend on z once z is past the point where a residue class holds
more than one surviving p.

How it is evaluated.  Sequential importance sampling: the residues are drawn
prime by prime with probability proportional to (1 - eps)^(-rows killed),
and the exact likelihood ratio is kept, so the estimate is unbiased for the
model (checked against full enumeration of the residue vectors on small
cases).  The sampler runs over the primes q <= min(g, ZCAP); the primes
beyond contribute a small closed-form factor: two surviving complements are
slightly less often killed together than independent ones would be.

The expected number of even n < N with g(n) >= g is the sum of Z(ln n, g).
The largest g below N is then distributed like the first arrival of a
Poisson process: P(max < g) = exp(-expected count), so the median is where
the count equals ln 2.

Needs numpy.  Seconds per point up to 30 digits, minutes at 150.
"""
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZCAP = 20000
LEVELS = (math.log(2), 3.0, 0.0513)          # expected counts at the median, 5% and 95% points of the maximum


def primes_upto(n):
    s = np.ones(n + 1, bool)
    s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


_P = primes_upto(4_000_000)


def _tail(a, eps, zmax, y):
    """log factor from the primes q > zmax, for a surviving rows with prime probability eps.
    Such a prime kills two given rows together only if it divides their difference: never for q > y,
    and for q <= y about as often as two random points of [0, y] differ by a multiple of q."""
    u2c = (eps / (1 - eps)) ** 2 * a * (a - 1) / 2
    t = 0.0
    if zmax < y:
        qs = _P[(_P > zmax) & (_P <= y)].astype(float)
        M = np.floor(y / qs)
        pq = 2 * (y * M - qs * M * (M + 1) / 2) / (y * y)
        t -= u2c * float(np.sum(1 / qs ** 2 - pq / qs))
    ly = math.log(max(y, zmax))
    t -= u2c / (max(y, zmax) * ly) * (1 - 1 / ly + 2 / ly ** 2)   # sum of 1/q^2 over the primes q > y
    return t


def _sis(args):
    L, g, particles, seed = args
    rng = np.random.default_rng(seed)
    rows = _P[(_P >= 3) & (_P < g)]
    # the density of z-rough numbers near e^L is the Mertens product only for z well below e^(L/2)
    zmax = min(g - 1, ZCAP, int(math.exp(L / 3)))
    qs = _P[(_P >= 3) & (_P <= zmax)]
    out = np.empty(particles)
    for t in range(particles):
        a = rows
        eps = 2.0 / L                                 # an odd number of size e^L is prime with probability 2/L
        lw = len(a) * math.log1p(-eps)
        for q in qs:
            q = int(q)
            eps2 = eps * q / (q - 1)
            r = a % q
            cnt = np.bincount(r, minlength=q)         # rows that die in each residue class of N mod q
            lwc = -math.log1p(-eps2) * cnt
            m = lwc.max()
            w = np.exp(lwc - m)
            lw += len(a) * (math.log1p(-eps2) - math.log1p(-eps)) + m + math.log(w.mean())
            c = int(np.searchsorted(np.cumsum(w), rng.random() * w.sum()))
            a = a[r != c]
            eps = eps2
        out[t] = lw + _tail(len(a), eps, zmax, g - 1)
    return out


def lnZ(L, g, particles=160, seed=1, pool=None):
    """(estimate, standard error) of ln P(g(N) >= g) for a random even N of size e^L."""
    if pool is None:
        lw = _sis((L, g, particles, seed))
    else:
        n = pool._max_workers
        lw = np.concatenate(list(pool.map(_sis, [(L, g, (particles + n - 1) // n, seed * 1000 + i) for i in range(n)])))
    m = lw.max()
    w = np.exp(lw - m)
    return m + math.log(w.mean()), float(w.std() / w.mean() / math.sqrt(len(w)))


def expected_count(N, g, particles=160, seed=1, pool=None):
    """Expected number of even n < N with g(n) >= g.
    It is the integral of Z(L, g) e^L / 2 dL up to ln N.  ln Z is fitted by a parabola in 1/L through
    four points below ln N; the integrand falls by a factor of about 8 per unit of L, so the fit only
    has to be good near the top."""
    LN = math.log(N)
    Ls = [LN, LN - 0.75, LN - 1.75, LN - 3.25]
    zs = [lnZ(L, g, particles, seed + i, pool)[0] for i, L in enumerate(Ls)]
    co = np.polyfit([1 / L for L in Ls], zs, 2)
    x = np.linspace(max(LN - 14, 3.0), LN, 4001)
    f = np.exp(np.polyval(co, 1 / x) + x - LN) / 2
    return float(np.sum((f[1:] + f[:-1]) / 2 * np.diff(x))) * N


def ceiling(N, levels=LEVELS, g0=None, particles=160, pool=None):
    """The g at which expected_count(N, g) equals each level.  ln(count) is computed at three primes
    around the guess and fitted by a line in g; the bracket is moved if the answer falls outside."""
    L = math.log(N)
    g = g0 or 1.42 * L * L * math.log(L)
    for attempt in range(3):
        gs = [int(_P[np.searchsorted(_P, g * f)]) for f in (0.96, 1.0, 1.04)]
        les = [math.log(expected_count(N, gi, particles, 10 * attempt + i + 1, pool)) for i, gi in enumerate(gs)]
        b, a = np.polyfit(gs, les, 1)
        sol = [(math.log(lv) - a) / b for lv in levels]
        if gs[0] * 0.98 <= sol[0] <= gs[-1] * 1.02:
            break
        g = sol[0]
    return sol, list(zip(gs, les))


def cmd_table(digits, particles):
    out = os.path.join(HERE, "ceiling_table.json")
    res = json.load(open(out)) if os.path.exists(out) else {}
    with ProcessPoolExecutor() as pool:
        for d in digits:
            (med, lo, hi), pts = ceiling(10.0 ** d, particles=particles, pool=pool)
            L = d * math.log(10)
            res[repr(d)] = {"L": L, "median": med, "p05": lo, "p95": hi, "pi": int(np.searchsorted(_P, med)) - 1,
                            "points": pts, "particles": particles}     # pi: odd primes below the median
            print(f"10^{d}: largest g below it: median {med:,.0f}, 5%..95% {lo:,.0f}..{hi:,.0f}; "
                  f"median / (ln^2 N ln ln N) = {med / (L * L * math.log(L)):.4f}", flush=True)
            json.dump(dict(sorted(res.items(), key=lambda kv: float(kv[0]))), open(out, "w"), indent=1)


def cmd_holders(lo, particles):
    """N_i is the first even number with g >= g_i, so the expected count below N_i at level g_i behaves
    like an Exp(1) variable if the model is right: mean of its log -0.58, median 0.69."""
    ch = [tuple(map(int, l.split())) for l in open(os.path.join(HERE, "record_holders.txt")) if l[0].isdigit()]
    les = []
    with ProcessPoolExecutor() as pool:
        for N, g in ch:
            if N < lo:
                continue
            e = expected_count(N, g, particles, 1, pool)
            les.append(math.log(e))
            L = math.log(N)
            print(f"{N:>20} {g:>5}  g/(ln^2 N ln ln N) = {g / (L * L * math.log(L)):5.3f}  "
                  f"expected count below N: {e:7.3f}", flush=True)
    les = np.array(les)
    print(f"{len(les)} record holders: mean ln(count) = {les.mean():.2f} (Exp(1): -0.58), "
          f"median count = {math.exp(np.median(les)):.2f} (Exp(1): 0.69)")


def cmd_tail(path, A, B, ys):
    rows = [l.split() for l in open(path) if l[0].isdigit()]
    g = np.array([int(a) for a, b in rows])
    c = np.array([int(b) for a, b in rows])
    n, L = int(c.sum()), math.log((A + B) / 2)
    print(f"{n} random even N in [{A:.3g}, {B:.3g})")
    print("    y  measured P(g >= y)      events  model           ln(measured/model)")
    for y in ys:
        y = int(_P[np.searchsorted(_P, y)])
        k = int(c[g >= y].sum())
        lz, se = lnZ(L, y, 600, 3)
        if k:
            print(f"{y:>5}  {k / n:.4e}       {k:>11}  {math.exp(lz):.4e}      {math.log(k / n) - lz:+.3f} +- {math.hypot(1 / math.sqrt(k), se):.3f}")
        else:
            print(f"{y:>5}  no events; the model expects {n * math.exp(lz):.2f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "count":
        N, g = float(sys.argv[2]), int(sys.argv[3])
        with ProcessPoolExecutor() as pool:
            print(f"expected number of even n < {N:.4g} with g(n) >= {g}: "
                  f"{expected_count(N, g, int(sys.argv[4]) if len(sys.argv) > 4 else 160, 1, pool):.4g}")
    elif cmd == "ceiling":
        N = float(sys.argv[2])
        with ProcessPoolExecutor() as pool:
            (med, lo, hi), _ = ceiling(N, particles=int(sys.argv[3]) if len(sys.argv) > 3 else 160, pool=pool)
        print(f"largest g below {N:.4g}: median {med:,.0f}, 5%..95% {lo:,.0f}..{hi:,.0f}")
    elif cmd == "table":
        cmd_table([float(x) for x in sys.argv[2].split(",")], int(sys.argv[3]) if len(sys.argv) > 3 else 128)
    elif cmd == "holders":
        cmd_holders(int(float(sys.argv[2])) if len(sys.argv) > 2 else 10 ** 9, int(sys.argv[3]) if len(sys.argv) > 3 else 160)
    elif cmd == "tail":
        cmd_tail(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), [int(v) for v in sys.argv[5:]])
    else:
        print(__doc__)
