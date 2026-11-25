#!/usr/bin/env python3
"""A referee's implementation of the price recursion with the entropy of every prefix of the moduli.

Written from the description in the research session's write-up (goldbach/sublinear/README.md on branch
ccr-d4a17dd0-7uu03r at commit fbf0b09, section "The entropy of the small moduli"), not from its code.
Differences on purpose:

* the dispersion of the alive rows in a class of a modulus is computed from the actual primes below Q (the exact
  number of pairs of odd primes at every difference, by one autocorrelation), not from the Hardy-Littlewood count;
* the moduli can be taken in any order, so that "every prefix in increasing order" can be compared with other
  families of constraints.

Model (the research session's).  Rows: the odd primes below Q.  Moduli: the odd primes up to x, taken in some order.
Before a modulus s, A rows are alive, mu = A/(s - 1) per class.  With tilt t the chosen class holds mu e^{v t} rows
and the level has entropy  ln(s - 1) - mu (t e^{v t} - k(t)),  k(t) = (e^{v t} - 1)/v,  v = variance/mean of the
alive rows in a class of s when the moduli before s have uniform random nonzero classes.

    python3 prefix_check.py table            the seven points of the write-up, increasing order
    python3 prefix_check.py orders x Q       the same point with the moduli in other orders
    python3 prefix_check.py levels x Q       level by level
    python3 prefix_check.py primal x Q       the constrained maximum found without the dual (SLSQP), for small x
    python3 prefix_check.py ends x ...       where complete covers end, both ways
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize

BETA = 40.0          # price of a row left at the end


def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]


def pair_counts(Q):
    """N2[d] = number of pairs (q, q + d) of odd primes below Q, every d in [0, Q); N2[0] = number of rows"""
    ind = np.zeros(Q, dtype=np.float64); p = primes_upto(Q - 1); ind[p[p > 2]] = 1.0
    L = 1 << int(math.ceil(math.log2(2 * Q)))
    F = np.fft.rfft(ind, L); ac = np.fft.irfft(F * np.conj(F), L)
    return np.rint(ac[:Q])


def dispersions(order, Q, N2, exact=True):
    """variance/mean of the alive rows in a nonzero class of each modulus s, over the s - 1 classes and over uniform
    random nonzero classes of the moduli before s (in `order`).  Exact for the odd primes below Q.

    Two rows at difference d are both alive with probability phi^2 G(d), G(d) = prod over the earlier moduli t of
    rho_t(d), and the pairs at difference d are counted by an autocorrelation, so every modulus costs one dot product.
    With exact=True the rows that are moduli themselves are treated as they are: a row q is never struck by the
    modulus q (its class there is 0), and the row s lies in no nonzero class of s.  This is kept up by weights on
    those rows (a pair with the row q > 3 gets the factor (q-2)/(q-3), the row alone (q-1)/(q-2)); pairs with the row
    3 are summed apart, because G vanishes at their differences.  At the smallest moduli none of this is small:
    without it the value at 5 is off by 1/2.  Checked against the enumeration of every class vector (`brute`)."""
    P = primes_upto(Q - 1); P = P[P > 2]
    W = np.zeros(Q); W[P] = 1.0                      # pair weights of the rows
    AC = N2.astype(np.float64).copy()                # AC[d] = sum_q W[q] W[q + d]
    G = np.ones(Q); G3 = np.ones(Q)                  # G3: the same product without the factor of the modulus 3
    phi = 1.0; alive1 = float(N2[0])                 # sum over the rows of P(alive)/phi
    three_done = False; out = []
    for s in order:
        EK = phi * (alive1 - (1.0 if s < Q else 0.0)) / (s - 1)
        pairs = float(np.dot(G[s::s], AC[s::s]))
        if exact and three_done and s != 3:          # pairs (3, q'), q' = 3 mod s: factor (1/2)/(1/2)^2 = 2 at the modulus 3
            qq = np.arange(3 + s, Q, s)
            pairs += 2.0 * float(np.dot(G3[qq - 3], W[qq]))
        EKK = 2 * phi * phi / (s - 1) * pairs        # E K(K-1)
        out.append(1 + EKK / EK - EK)
        if s == 3:                                   # both alive after 3 only if 3 divides the difference
            keep = G[::3] * 2.0; G[:] = 0.0; G[::3] = keep; three_done = True
            if exact and s < Q: alive1 += 1.0        # the row 3 is alive with probability 2 phi
        else:
            f = 1 - 1 / (s - 2) ** 2; G *= f; G[::s] *= (s - 2) / (s - 3); G3 *= f; G3[::s] *= (s - 2) / (s - 3)
            if exact and s < Q:
                c = (s - 2) / (s - 3)
                AC[1:Q - s] += (c - 1) * W[s + 1:Q]; AC[1:s + 1] += (c - 1) * W[s - 1::-1][:s]
                W[s] = c; alive1 += 1.0 / (s - 2)
        phi *= 1 - 1 / (s - 1)
    return np.array(out)


def brute(order, Q, upto):
    """the same by enumeration of every class vector of the first `upto` moduli (a check of `dispersions`)"""
    import itertools
    P = primes_upto(Q - 1); P = P[P > 2]; out = []
    for k in range(upto + 1):
        B = order[:k]; s = order[k]; tot = 0; m1 = 0.0; m2 = 0.0
        for a in itertools.product(*[range(1, t) for t in B]):
            alive = np.ones(len(P), dtype=bool)
            for t, c in zip(B, a): alive &= (P % t) != c
            cnt = np.bincount(P[alive] % s, minlength=s)[1:]
            m1 += cnt.sum(); m2 += float((cnt.astype(float) ** 2).sum()); tot += s - 1
        m1 /= tot; m2 /= tot; out.append((m2 - m1 * m1) / m1)
    return out


def passes(order, vs, rows, w, beta=BETA):
    """backward: the prices; forward: alive rows, entropies of the levels.  Returns D = sum w ln(s-1) - p_start rows,
    the entropies, the tilts, the rows alive at the end"""
    n = len(order); taus = np.empty(n); p = beta; D = 0.0
    for i in range(n - 1, -1, -1):
        s = order[i]; v = vs[i]; t = min(p / w[i], math.log(s - 1) / v)
        taus[i] = t; e = math.exp(v * t); k = math.expm1(v * t) / v
        p -= (p * e - w[i] * (t * e - k)) / (s - 1); D += w[i] * math.log(s - 1)
    D -= p * rows
    ents = np.empty(n); A = rows
    for i in range(n):
        s = order[i]; v = vs[i]; t = taus[i]; mu = A / (s - 1); e = math.exp(v * t)
        ents[i] = math.log(s - 1) - mu * (t * e - math.expm1(v * t) / v); A -= mu * e
    return D, ents, taus, A, p


def solve_dual(order, vs, rows, lam0=None, beta=BETA, maxiter=6000):
    n = len(order)
    def f(lam):
        D, ents, _, _, _ = passes(order, vs, rows, 1.0 + np.cumsum(lam[::-1])[::-1], beta)
        return D, np.cumsum(ents)
    r = minimize(f, np.zeros(n) if lam0 is None else lam0, jac=True, method="L-BFGS-B", bounds=[(0, None)] * n,
                 options={"maxiter": maxiter, "maxfun": 4 * maxiter, "ftol": 1e-15, "gtol": 1e-9})
    lam = r.x; w = 1.0 + np.cumsum(lam[::-1])[::-1]
    D, ents, taus, A, p = passes(order, vs, rows, w, beta)
    return D, lam, w, ents, taus, A


def kkt(lam, ents, D, A_end, beta=BETA):
    """the certificate: prefix entropies >= 0, zero where the multiplier is positive, and the value of the primal at
    the dual's tilts (sum of the entropies - beta A_end) equal to the dual value"""
    P = np.cumsum(ents)
    return float(P.min()), float(np.abs(P[lam > 1e-9]).max()) if (lam > 1e-9).any() else 0.0, float(ents.sum() - beta * A_end - D)


class Point:
    def __init__(self, x, Q, N2=None):
        self.x, self.Q = x, Q
        self.N2 = pair_counts(Q) if N2 is None else N2
        self.rows = float(self.N2[0])
        self.mods = [int(p) for p in primes_upto(x) if p > 2]
        self.theta = sum(math.log(s) for s in self.mods)

    def vs(self, order, lo=1e-4, hi=1.0):
        raw = dispersions(order, self.Q, self.N2)
        return np.clip(raw, lo, hi), raw


def frozen_up_to(order, w):
    f = [s for s, ww in zip(order, w) if ww > 1.001]
    return (len(f), max(f)) if f else (0, 0)


def report(pt, order, label, quiet=False):
    vs, raw = pt.vs(order); n = len(order)
    D0, e0, t0, A0, p0 = passes(order, vs, pt.rows, np.ones(n))
    P0 = np.cumsum(e0); ident = float(e0.sum() - BETA * A0 - D0)
    D, lam, w, e1, t1, A1 = solve_dual(order, vs, pt.rows)
    pmin, slack, gap = kkt(lam, e1, D, A1)
    i0 = int(P0[:-1].argmin())
    nf, mf = frozen_up_to(order, w)
    if not quiet:
        print(f"{label} | {pt.theta - D0:.1f} | {ident:+.1e} | {P0[:-1].min():.1f} at {order[i0]} (position {i0 + 1} of {n}) | {pt.theta - D:.1f} | {nf}, largest {mf} | {w[0]:.3f} | "
              f"{pmin:+.1e}, {slack:.1e}, {gap:+.1e} | v > 1 at {int((raw > 1).sum())}, v < 1e-4 at {int((raw < 1e-4).sum())}", flush=True)
    return D0, D, P0, w, vs, raw, e0, e1, t0, t1


HEAD = ("order | loss, recursion as it was | sum of level entropies - (theta' - p_start rows) | lowest prefix entropy, at modulus | loss with the constraint | "
        "moduli with weight > 1 | weight of the first | certificate: lowest prefix entropy, largest |entropy| where the multiplier is positive, primal - dual | dispersion outside the cut")

TABLE = [(463, [10000, 14000, 15300, 15907]), (797, [18559, 23198, 26291, 28766]), (997, [15000, 25000, 38000, 40111]),
         (1499, [42067, 52583, 59594, 65203]), (1999, [59239, 74048, 83921, 91820]), (2999, [50000, 100000]), (9973, [100000, 300000])]


def orders_of(mods, seed=1):
    rng = np.random.default_rng(seed); n = len(mods)
    small = [s for s in mods if s <= 17]; rest = [s for s in mods if s > 17]
    half = n // 2
    out = [("increasing", list(mods)),
           ("decreasing", list(mods[::-1])),
           ("3..17 first, then decreasing", small + rest[::-1]),
           ("upper half increasing, then lower half increasing", list(mods[half:]) + list(mods[:half])),
           ("lower half decreasing, then upper half increasing", list(mods[:half][::-1]) + list(mods[half:])),
           ("random 1", [mods[i] for i in rng.permutation(n)]),
           ("random 2", [mods[i] for i in rng.permutation(n)])]
    return out


def main():
    mode = sys.argv[1]
    if mode == "table":
        print("# prefix_check.py table: the points of cover_price_prefix.txt, dispersions exact for the primes below Q, moduli in increasing order")
        for x, Qs in TABLE:
            print(f"\nx = {x}"); print("Q | " + HEAD.split(" | ", 1)[1])
            for Q in Qs:
                pt = Point(x, Q); report(pt, pt.mods, str(Q))
    elif mode == "orders":
        x, Q = int(sys.argv[2]), int(sys.argv[3]); pt = Point(x, Q)
        print(f"# prefix_check.py orders {x} {Q}: {len(pt.mods)} moduli, {pt.rows:.0f} rows, theta = {pt.theta:.1f}"); print(HEAD)
        for label, order in orders_of(pt.mods):
            report(pt, order, label)
    elif mode == "levels":
        x, Q = int(sys.argv[2]), int(sys.argv[3]); pt = Point(x, Q); order = pt.mods; n = len(order)
        D0, D, P0, w, vs, raw, e0, e1, t0, t1 = report(pt, order, "increasing", quiet=True)
        print(f"# prefix_check.py levels {x} {Q}: ln g0 = {D0:.1f} as it was, {D:.1f} with the constraint")
        print("modulus | dispersion | as it was: tilt e^(v t), entropy of the level, of the prefix | with the constraint: weight, tilt, level, prefix")
        P1 = np.cumsum(e1); step = max(1, n // 40)
        for i in list(range(0, n, step)) + [n - 1]:
            print(f"{order[i]} | {vs[i]:.4f} | {math.exp(vs[i] * t0[i]):.2f}, {e0[i]:.2f}, {P0[i]:.1f} | {w[i]:.3f}, {math.exp(vs[i] * t1[i]):.2f}, {e1[i]:.2f}, {P1[i]:.1f}")
    elif mode == "primal":
        x, Q = int(sys.argv[2]), int(sys.argv[3]); pt = Point(x, Q); order = pt.mods; n = len(order); vs, _ = pt.vs(order)
        caps = np.array([math.log(s - 1) / v for s, v in zip(order, vs)])
        def forward(t):
            A = pt.rows; ents = np.empty(n)
            for i in range(n):
                s = order[i]; v = vs[i]; mu = A / (s - 1); e = math.exp(v * t[i])
                ents[i] = math.log(s - 1) - mu * (t[i] * e - math.expm1(v * t[i]) / v); A -= mu * e
            return ents, A
        def obj(t):
            ents, A = forward(t); return -(ents.sum() - BETA * A)
        cons = [{"type": "ineq", "fun": lambda t: np.cumsum(forward(t)[0])}]
        D0, e0, t0, A0, _ = passes(order, vs, pt.rows, np.ones(n)); D, lam, w, e1, t1, A1 = solve_dual(order, vs, pt.rows)
        best = None
        for start, name in ((np.minimum(t0 * 0.5, caps), "half the unconstrained tilts"), (np.minimum(np.full(n, 0.05), caps), "small tilts")):
            r = minimize(obj, start, method="SLSQP", bounds=[(0.0, float(c)) for c in caps], constraints=cons, options={"maxiter": 3000, "ftol": 1e-12})
            ents, A = forward(r.x)
            print(f"SLSQP from {name}: value {-r.fun:.4f} (ln g0), lowest prefix entropy {np.cumsum(ents).min():+.2e}, rows alive at the end {A:.2e}, {r.nit} iterations, {r.message}")
            best = -r.fun if best is None else max(best, -r.fun)
        print(f"unconstrained maximum {D0:.4f}; dual minimum {D:.4f}; primal by SLSQP {best:.4f}; difference {best - D:+.2e}")
    elif mode == "ends":
        print("x | moduli | end, recursion as it was | / (x ln^2 x) | end with the constraint | / (x ln^2 x) | moduli with weight > 1 at the end, weight of the first")
        for x in [int(a) for a in sys.argv[2:]]:
            sc = x * math.log(x) ** 2; qmax = int(1.3 * sc + 1000); N2full = None
            mods = [int(p) for p in primes_upto(x) if p > 2]; n = len(mods)
            def at(Q):
                pt = Point(x, Q); vs, _ = pt.vs(pt.mods); return pt, vs
            lo, hi = 0.6 * sc, 1.3 * sc
            for _ in range(13):
                mid = math.sqrt(lo * hi); pt, vs = at(int(mid))
                if passes(pt.mods, vs, pt.rows, np.ones(n))[0] > 0: lo = mid
                else: hi = mid
            e0 = lo; lo, hi = 0.6 * sc, e0 * 1.001; lam = None; info = (0, 1.0)
            for _ in range(13):
                mid = math.sqrt(lo * hi); pt, vs = at(int(mid)); D, lam, w, _, _, _ = solve_dual(pt.mods, vs, pt.rows, lam)
                if D > 0: lo = mid; info = (frozen_up_to(pt.mods, w), float(w[0]))
                else: hi = mid
            print(f"{x} | {n} | {e0:,.0f} | {e0 / sc:.3f} | {lo:,.0f} | {lo / sc:.3f} | {info[0]}, {info[1]:.2f}", flush=True)


if __name__ == "__main__":
    main()
