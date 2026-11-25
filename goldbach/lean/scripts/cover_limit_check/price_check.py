#!/usr/bin/env python3
"""Step 4 of the research session's limit, tested alone: does the recursion over the primes tend to the
price equation?

The recursion (goldbach/sublinear/README.md on branch ccr-d4a17dd0-7uu03r):

    p_s = p_{s+} - kappa_s(p_{s+})/(s - 1),      kappa_s(p) = (e^{v_s p} - 1)/v_s,

over the odd primes s <= x, s+ the next prime, "the price before the first modulus being the largest that
the recursion can carry to the last one".  Its claimed limit: dp/d ln(alpha) = (e^{v p} - 1)/v with p infinite
at alpha = lam = ln x/ln Q, p = Lam(lam) alpha for small alpha, and the price before the first modulus equal to
2 C2 e^-gamma Lam(lam)/ln Q.

To test that passage and nothing else, both sides get the same dispersion: the limit profile
v_s = v(ln s/ln Q) of cover_limit.py (computed here by scripts/cover_count/Lam_check.py).  Then

    Lam_disc(x) = p_3 ln Q/(2 C2 e^-gamma)        (p_3 the largest price before the first modulus)

should tend to Lam(lam) as x grows.  The price before the first modulus is found by running the recursion
backwards from a price P after the last modulus and taking the largest result over P (the map P -> p_3 rises,
has one maximum near P = ln(x - 1)/v_x, and falls); the table also shows how flat that maximum is.

    python3 -I price_check.py > price_check.txt
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cover_count"))
import Lam_check as LC  # noqa: E402

EG, C2 = LC.EG, LC.C2


def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]


def v_table():
    """m(rho) on a fine grid, for linear interpolation (spacing 0.0005: error below 1e-7)"""
    rho = np.linspace(0, 41, 82001)
    m = np.array([LC.m_of(float(r)) for r in rho])
    return rho, m


def price_constant_lam(lam, h, x40=40.0, p_lo=1e-7):
    """Lam(lam) = lim p/alpha for the solution of dp/d ln(alpha) = (e^{v p} - 1)/v that is infinite at alpha = lam.
    With alpha = lam a:  dL/ds = B(v(lam a) p),  L = ln a,  s = ln p;  L = ln(1 - e^{-v(lam) p}) for large p."""
    v1 = LC.v_limit(lam, 1 - lam)
    def v(a_log):
        a = math.exp(a_log); al = lam * a
        return LC.v_limit(al, 1 - al)
    def f(s, L):
        return LC.bern(v(L) * math.exp(s))
    p_hi = x40 / v1
    s0, s1 = math.log(p_hi), math.log(p_lo)
    n = int(math.ceil((s0 - s1) / h)); h = (s0 - s1) / n
    s, L = s0, math.log1p(-math.exp(-v1 * p_hi))
    for _ in range(n):
        k1 = f(s, L); k2 = f(s - h / 2, L - h / 2 * k1); k3 = f(s - h / 2, L - h / 2 * k2); k4 = f(s - h, L - h * k3)
        L -= h * (k1 + 2 * k2 + 2 * k3 + k4) / 6; s -= h
    E = L - s1                                  # ln(a/p) at p_lo; below it (1 - B(v p))/p ~ v/2 ~ lam a = lam p e^E
    tail = lam * math.exp(E) * p_lo ** 2 / 2
    return math.exp(-(E + tail)) / lam


RHO_T, M_T = None, None


def v_of_alpha(alpha):
    """vectorised limit profile"""
    alpha = np.asarray(alpha, dtype=float)
    rho = (1 - alpha) / alpha
    m = np.where(rho <= 1, rho * rho, np.where(rho >= 41, 2 * math.exp(EG) * (rho - 1), np.interp(rho, RHO_T, M_T)))
    return 1 - 0.5 * math.exp(-EG) * alpha * m


def backward(primes, v, P):
    """the price before the first modulus when the price after the last one is P"""
    p = P
    for s, vs in zip(primes[::-1].tolist(), v[::-1].tolist()):
        x = vs * p
        p -= (math.expm1(x) / vs if x < 700 else float("inf")) / (s - 1)
        if p < 0: return -1.0
    return p


def largest_start(primes, v):
    x = int(primes[-1]); P0 = math.log(x - 1) / float(v[-1])
    best = (-1.0, None); curve = []
    for f in (0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2):
        r = backward(primes, v, f * P0); curve.append((f, r))
        if r > best[0]: best = (r, f)
    # refine around the best factor by golden section
    lo, hi = best[1] - 0.1, best[1] + 0.1
    g = (math.sqrt(5) - 1) / 2
    a, b = hi - g * (hi - lo), lo + g * (hi - lo); fa, fb = backward(primes, v, a * P0), backward(primes, v, b * P0)
    for _ in range(10):
        if fa < fb: lo, a, fa = a, b, fb; b = lo + g * (hi - lo); fb = backward(primes, v, b * P0)
        else: hi, b, fb = b, a, fa; a = hi - g * (hi - lo); fa = backward(primes, v, a * P0)
    return max(fa, fb, best[0]), 0.5 * (lo + hi), P0, curve


def main():
    global RHO_T, M_T
    LC.build()
    RHO_T, M_T = v_table()
    # interpolation check
    worst = max(abs(float(v_of_alpha(a)) - LC.v_limit(a, 1 - a)) for a in [0.03 + 0.001 * i for i in range(960)])
    print("# price_check.py: the recursion over the primes against the price equation, with the same dispersion v(alpha)")
    print(f"# interpolated v against the direct evaluation, largest difference on [0.03, 0.99]: {worst:.1e}")
    P = primes_upto(10 ** 8); P = P[P > 2]
    for lam in (1.0, 0.9, 0.8):
        Lam = price_constant_lam(lam, 1 / 512)
        print(f"\nlam = ln x/ln Q = {lam}:  continuum Lam(lam) = {Lam:.8f}   (independent rows: 1/lam = {1 / lam:.6f})")
        print("       x     moduli   Lam_disc = p_3 ln Q/(2 C2 e^-gamma)   ratio to Lam   (Lam_disc - Lam) ln x   best P/P0, P0 = ln(x-1)/v_x   p_3 at P/P0 = 0.8, 0.9, 1, 1.1, 1.2 relative to the largest")
        for e in (3, 4, 5, 6, 7, 8):
            x = 10 ** e; pr = P[P <= x]; lnQ = math.log(x) / lam
            v = v_of_alpha(np.log(pr) / lnQ); v = np.maximum(v, 1e-9)
            p3, fbest, P0, curve = largest_start(pr, v)
            Ld = p3 * lnQ / (2 * C2 * math.exp(-EG))
            rel = " ".join(f"{dict(curve)[f] / p3:.6f}" for f in (0.8, 0.9, 1.0, 1.1, 1.2))
            print(f"  10^{e}  {len(pr):9d}   {Ld:.8f}                         {Ld / Lam:.6f}        {(Ld - Lam) * math.log(x):8.4f}            {fbest:.3f}                      {rel}", flush=True)


if __name__ == "__main__":
    main()
