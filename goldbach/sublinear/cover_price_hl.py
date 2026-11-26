#!/usr/bin/env python3
"""The price recursion of cover_price.py with the dispersion taken from the whole Hardy-Littlewood pair sum.

    python3 cover_price_hl.py loss x Q[:lng0] ...   loss theta(x) - ln g0(x, Q) at the targets (against measured ln g0 if given)
    python3 cover_price_hl.py disp x Q s ...        variance/mean of the alive rows in a class of s: pair sum and closed formula
    python3 cover_price_hl.py ends x ...            where complete covers end on the odd primes up to x

cover_price.py uses a closed formula for the dispersion (the second-order term of the average of singular series).
Here nothing is approximated beyond the Hardy-Littlewood conjecture itself.  For a modulus s the alive rows K in one
class (alive = struck by none of the random nonzero classes of the smaller moduli) have

    E K(K-1) = (2 phi(s)^2/(s-1)) sum_{j>=1} W_s(j) L2(h j),      h = 6s (6 for s = 3),

    W_s(j) = [prod over moduli t < s of rho_t(h j)] * S(h j),  rho_t(d) = (1 - nu_t(d)/(t-1))/(1 - 1/(t-1))^2,
    S(d) the singular series of the pair (q, q + d),  L2(d) = int_3^{Q-d} dt/(ln t ln(t+d)).

The mean of W_s over j is exactly a = 6s/(s-1) (3 for s = 3; CoverPairs.lean, sum_pair_weight), and that part of the
sum is the square of the mean of K: at leading order the classes are Poisson.  What is left is written so that no
large numbers cancel.  With R(m) = sum_{j<=m} (a - W_s(j)) (a slowly growing positive number: ln^2 m for m < s,
ln m/(2 phi(s)) beyond) and Euler-Maclaurin for the smooth part,

    variance/mean = 1 - (phi(s)/li) [ 2 sum_m R(m) (L2(h m) - L2(h (m+1))) + a L2(0) ],     li = int_3^Q dt/ln t.

R does not depend on Q, so it is built once per x (up to the largest target) and every target costs one pass.
"""
import math, sys
import numpy as np
import cover_price as cp

C2 = 0.6601618158468696

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

class PairSums:
    """R_s(m) for every modulus s <= x and every m with h m < qmax"""
    def __init__(self, x, qmax):
        self.x, self.qmax = x, int(qmax)
        n = self.qmax + 1
        H = np.zeros(n); H[2::2] = 2 * C2                     # singular series at even d
        for p in primes_upto(n - 1):
            p = int(p)
            if p > 2: H[p::p] *= (p - 1) / (p - 2)
        self.mods = [int(p) for p in primes_upto(x) if p > 2]
        self.phis, self.R, self.a, self.h = [], [], [], []
        phi = 1.0; G0 = 1.0                                   # G0 = prod of rho_t at differences t does not divide
        for s in self.mods:
            h = 6 if s == 3 else 6 * s; a = 3.0 if s == 3 else 6 * s / (s - 1)
            w = G0 * H[h::h]                                  # W_s(j), j = 1, 2, ...
            self.R.append(np.cumsum(a - w)); self.a.append(a); self.h.append(h); self.phis.append(phi)
            # s becomes a smaller modulus for the next ones
            phi *= 1 - 1 / (s - 1)
            if s == 3: G0 *= 2.0; H[1::2] = 0.0; H[np.arange(n) % 3 != 0] = 0.0     # rho_3 = 2 if 3 | d, else 0
            else: G0 *= 1 - 1 / (s - 2) ** 2; H[s::s] *= (s - 2) / (s - 3)          # rho_s(dvd)/rho_s(not dvd)

    def dispersions(self, Q):
        """variance/mean for every modulus at the target Q (Q <= qmax)"""
        assert Q <= self.qmax
        t = np.geomspace(3.0, Q, 200001); li = float(np.trapezoid(1 / np.log(t), t)); L20 = float(np.trapezoid(1 / np.log(t) ** 2, t))
        # g(d) = -dL2/dd = 1/(ln(Q-d) ln Q) + int_3^{Q-d} dt/(ln t (t+d) ln^2(t+d)), on a grid of d
        dg = np.unique(np.concatenate([np.linspace(0, Q - 3.001, 1500), Q - 3.001 - np.geomspace(1e-3, Q - 3.001, 500)]))
        dg = dg[(dg >= 0) & (dg <= Q - 3.001)]
        g = np.empty(len(dg))
        for i, d in enumerate(dg):
            hi = Q - d
            tt = np.geomspace(3.0, hi, 2001) if hi > 3.01 else np.array([3.0, hi])
            g[i] = 1 / (math.log(hi) * math.log(Q)) + float(np.trapezoid(1 / (np.log(tt) * (tt + d) * np.log(tt + d) ** 2), tt))
        out = []
        for s, phi, R, a, h in zip(self.mods, self.phis, self.R, self.a, self.h):
            J = int((Q - 3) // h)
            if J < 1: out.append(1.0); continue
            mid = h * (np.arange(1, J + 1) + 0.5)
            dL = h * np.interp(mid, dg, g, right=0.0)          # L2(h m) - L2(h (m+1)), m = 1..J
            tail = Q - 3 - h * (J + 1)                         # the last interval may run past the end of the range
            if tail < 0: dL[-1] *= max(0.0, (Q - 3 - h * J) / h)
            v = 1 - (phi / li) * (2 * float(np.dot(R[:J], dL)) + a * L20)
            out.append(v)
        return out, li

def closed_formula(mods, phis, Q):
    piQ = cp.odd_primes_below(Q)
    return [1 - 6 * phi * (s / (s - 1)) * (piQ / Q) * math.log(max(Q / (6 * s), 1.0)) for s, phi in zip(mods, phis)]

def start_price(mods, vs, Q):
    """the largest price before the first modulus that the recursion carries through every modulus"""
    piQ = cp.odd_primes_below(Q)
    def run(p):
        for s, v in zip(mods, vs):
            top = math.log(s - 1) / v
            if p > top - math.expm1(v * top) / (v * (s - 1)): return False
            q = p                                   # solve q - (e^{vq} - 1)/(v (s-1)) = p on [p, top]: concave and increasing,
            for _ in range(60):                     # so Newton from the left climbs to the root without passing it
                e = math.exp(v * q); d = 1 - e / (s - 1)
                if d < 1e-9: break
                step = (p - q + (e - 1) / (v * (s - 1))) / d
                q += step
                if step < 1e-13 * (1 + q): break
            p = q
        return True
    lo, hi = 0.0, 5.0
    for _ in range(42):
        mid = 0.5 * (lo + hi)
        if run(mid): lo = mid
        else: hi = mid
    return lo, piQ

def clamp(vs): return [min(1.0, max(0.02, v)) for v in vs]

def loss(ps, Q):
    vs, _ = ps.dispersions(Q); p, piQ = start_price(ps.mods, clamp(vs), Q)
    junk = sum(math.log(s / (s - 1)) for s in ps.mods)        # vectors with a zero class are not complete covers
    return p * piQ + junk

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "loss":
        x = int(sys.argv[2]); targets = [(int(a.split(":")[0]), float(a.split(":")[1]) if ":" in a else None) for a in sys.argv[3:]]
        ps = PairSums(x, max(q for q, _ in targets)); th = sum(math.log(s) for s in ps.mods)
        print(f"x = {x}, {len(ps.mods)} moduli, theta = {th:.1f}\nQ | loss with the pair sum | with the closed formula | ln g0 measured | loss measured | measured / pair sum | measured / closed formula")
        for Q, g in targets:
            lp = loss(ps, Q); pc, piQ = start_price(ps.mods, clamp(closed_formula(ps.mods, ps.phis, Q)), Q)
            lc = pc * piQ + sum(math.log(s / (s - 1)) for s in ps.mods)
            print(f"{Q} | {lp:.1f} | {lc:.1f}" + (f" | {g:.2f} | {th - g:.1f} | {(th - g) / lp:.3f} | {(th - g) / lc:.3f}" if g is not None else ""), flush=True)
    elif mode == "disp":
        x, Q = int(sys.argv[2]), int(sys.argv[3]); ps = PairSums(x, Q); vs, li = ps.dispersions(Q); cl = closed_formula(ps.mods, ps.phis, Q)
        print(f"x = {x}, Q = {Q}: variance/mean of the alive rows in a class\nmodulus s | pair sum | closed formula")
        for s in [int(a) for a in sys.argv[4:]]:
            i = ps.mods.index(s); print(f"{s} | {vs[i]:.3f} | {cl[i]:.3f}")
    elif mode == "ends":
        print("x | moduli | end of complete covers, pair sum | / (x ln^2 x) | end, closed formula | / (x ln^2 x)")
        for x in [int(a) for a in sys.argv[2:]]:
            sc = x * math.log(x) ** 2; ps = PairSums(x, int(1.6 * sc) + 1000); th = sum(math.log(s - 1) for s in ps.mods)
            junk = sum(math.log(s / (s - 1)) for s in ps.mods); out = []
            for use_closed in (False, True):
                lo, hi = float(x), 1.6 * sc
                for _ in range(26):
                    mid = math.sqrt(lo * hi); Q = int(mid)
                    if use_closed: p, piQ = start_price(ps.mods, clamp(closed_formula(ps.mods, ps.phis, Q)), Q); l = p * piQ
                    else: l = loss(ps, Q) - junk
                    if l < th: lo = mid
                    else: hi = mid
                out.append(lo)
            print(f"{x} | {len(ps.mods)} | {out[0]:,.0f} | {out[0] / sc:.3f} | {out[1]:,.0f} | {out[1] / sc:.3f}", flush=True)
