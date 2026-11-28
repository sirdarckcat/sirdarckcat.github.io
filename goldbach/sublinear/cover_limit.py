#!/usr/bin/env python3
"""The limit of the counting law for complete covers (heuristic; nothing fitted).

    python3 cover_limit.py                       the limit profile, the price constant, the limit of the law
    python3 cover_limit.py correction Q [Q ...]  how far the pair-sum dispersion at Q is from the limit profile: c(alpha) = (limit - v) ln Q
    python3 cover_limit.py approach              D/(x ln^2 x) from x = 10^3 to 10^200 with the dispersion limit - c(alpha)/ln Q

1. The dispersion in the limit.  For a modulus s and a target Q put alpha = ln s/ln Q.  The variance over the mean of the
   alive rows in a class of s is, by the Hardy-Littlewood pair sum (cover_price_hl.py),

       1 - (2 phi(s)/(J ln Q)) sum_{m<J} R(m),   J = Q/(6s),   R(m) = a m - sum_{j<=m} W_s(j) = a c [ m sum_{d>m} u(d)/d + sum_{d<=m} u(d) {m/d} ],

   where W_s(j) = a c prod_{t | j} (1 + u_t) exactly, u_t = 2/(t-3) for the moduli 5 <= t < s and 1/(t-2) for the primes
   t > s, u(d) their product over the primes of a squarefree d prime to 6s, a = 6s/(s-1), c = prod (1 + u_t/t)^-1.
   To leading order R(m) = (a c/2) M(m), M(m) = sum_{d<=m} u(d).  M has dimension 2 below s and 1 above: with
   M(s^rho) = g2 ln^2 s * m(rho),

       m(rho) = rho^2 (rho <= 1),      rho m'(rho) = 2 m(rho) - m(rho - 1) (rho > 1),      m(rho) ~ 2 e^gamma (rho - 1),

   and the constants combine exactly (c g2 = 1/(24 C2), phi(s) ~ 2 C2 e^-gamma/ln s) to

       v(alpha) = 1 - (e^-gamma/2) alpha m((1 - alpha)/alpha):     1 at alpha = 1,  0.86 at 1/2,  2 alpha for small alpha.

   The dispersion at finite Q lies below this by about c(alpha)/ln Q (cover_limit.txt).

2. The price in the limit.  The recursion p_s = p_{s+} - kappa_s(p_{s+})/(s-1), kappa = (e^{vp} - 1)/v, becomes
   dp/d ln(alpha) = (e^{v(alpha) p} - 1)/v(alpha), with p infinite at the last modulus, alpha = lam = ln x/ln Q.  For small
   alpha, p = Lam(lam) alpha, the price before the first modulus is 2 C2 e^-gamma Lam/ln Q, and

       ln g0(x, Q) = theta(x) - 2 C2 e^-gamma Lam(ln x/ln Q) Q/ln^2 Q.

   Rows independent (v = 1) give Lam = 1/lam, the first-moment count.  Complete covers end where the loss is theta(x):
   D = F(lam) x ln^2 x, F(lam) = e^gamma/(2 C2 lam^2 Lam(lam)), lam = ln x/ln D -> 1.
"""
import math
import numpy as np

EG = 0.5772156649015329; C2 = 0.6601618158468696

def m_table(rmax=40.0, h=1e-4):
    n = int(rmax / h); n1 = int(round(1 / h)); rho = np.arange(n + 1) * h; m = np.zeros(n + 1); m[:n1 + 1] = rho[:n1 + 1] ** 2
    for i in range(n1, n):
        r = rho[i]; d0 = m[i - n1]; d2 = m[i - n1 + 1]; d1 = 0.5 * (d0 + d2)
        k1 = (2 * m[i] - d0) / r; k2 = (2 * (m[i] + 0.5 * h * k1) - d1) / (r + 0.5 * h)
        k3 = (2 * (m[i] + 0.5 * h * k2) - d1) / (r + 0.5 * h); k4 = (2 * (m[i] + h * k3) - d2) / (r + h)
        m[i + 1] = m[i] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return rho, m

RHO, M = m_table()

def m_of(r):
    return float(np.interp(r, RHO, M)) if r <= RHO[-1] else 2 * math.exp(EG) * (r - 1)

def v_limit(alpha):
    return 1 - 0.5 * math.exp(-EG) * alpha * m_of((1 - alpha) / alpha)

def price_constant(v, lam=1.0, eps=1e-9, amin=2e-4):
    """Lam(lam): p/alpha for small alpha, when p is infinite at alpha = lam"""
    a = lam * (1 - eps); p = -math.log(eps) / v(lam); t = math.log(a)
    def f(t, p):
        vv = v(math.exp(t)); return math.expm1(vv * p) / vv
    while a > amin:
        d = f(t, p); dt = -min(0.002, 0.002 * p / d)
        k1 = f(t, p); k2 = f(t + dt / 2, p + dt / 2 * k1); k3 = f(t + dt / 2, p + dt / 2 * k2); k4 = f(t + dt, p + dt * k3)
        p += dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6; t += dt; a = math.exp(t)
    return p / a

# c(alpha) measured with the pair sums at Q = 10^8 (the same within 0.1 at 10^6 and 10^7): python3 cover_limit.py correction 100000000
C_ALPHA = [(0.0, 4.3), (0.12, 4.14), (0.16, 3.89), (0.2, 3.72), (0.25, 3.49), (0.3, 3.23), (0.35, 2.91), (0.4, 2.53), (0.45, 2.15), (0.5, 1.77),
           (0.55, 1.45), (0.6, 1.17), (0.65, 0.95), (0.7, 0.74), (0.75, 0.56), (0.8, 0.45), (0.85, 0.31), (0.9, 0.23), (1.0, 0.0)]

def correction(Q):
    import cover_price_hl as hl
    ps = hl.PairSums(int(Q ** 0.92) + 50, Q); vs, _ = ps.dispersions(Q); lq = math.log(Q); lm = np.log(np.array(ps.mods))
    print(f"Q = {Q}\nalpha | modulus s | variance/mean by the pair sum | limit | c = (limit - pair sum) ln Q, mean over the 7 moduli around s")
    for al in [a for a, _ in C_ALPHA[1:-1]]:
        i = int(np.argmin(np.abs(lm - al * lq))); j0, j1 = max(0, i - 3), min(len(lm), i + 4)
        c = float(np.mean([(v_limit(lm[j] / lq) - vs[j]) * lq for j in range(j0, j1)]))
        print(f"{al} | {ps.mods[i]} | {vs[i]:.3f} | {v_limit(lm[i] / lq):.3f} | {c:.2f}", flush=True)

def approach(lnx, with_c=True):
    """D/(x ln^2 x) and lam = ln x/ln D from the continuum price equation, theta(x) = x and pi(D) = li(D)"""
    from scipy.special import expi
    ca = np.array([a for a, _ in C_ALPHA]); cc = np.array([c for _, c in C_ALPHA])
    def excess(lnD):
        v = (lambda a: max(0.02, v_limit(a) - float(np.interp(a, ca, cc)) / lnD)) if with_c else v_limit
        L = price_constant(v, lnx / lnD, amin=2e-3)
        return math.log(2 * C2 * math.exp(-EG) * L * float(expi(lnD)) / lnD) - lnx
    lo, hi = lnx + 0.5 * math.log(lnx), lnx + 4 * math.log(lnx)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if excess(mid) < 0: lo = mid
        else: hi = mid
    return math.exp(lo - lnx - 2 * math.log(lnx)), lnx / lo

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "correction":
        for a in sys.argv[2:]: correction(int(a))
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "approach":
        print("log10 x | D/(x ln^2 x), dispersion = limit - c(alpha)/ln Q | lam = ln x/ln D | with the limit profile alone")
        for e in (3, 4, 5, 6, 8, 10, 12, 15, 20, 30, 50, 100, 200):
            r, lam = approach(e * math.log(10)); r0, _ = approach(e * math.log(10), False)
            print(f"{e} | {r:.3f} | {lam:.3f} | {r0:.3f}", flush=True)
        sys.exit(0)
    print("# cover_limit.py: the limit of the counting law. 24 November 2026.")
    print("\nrho | m(rho) | m(rho)/(rho - 1)      (2 e^gamma = %.6f)" % (2 * math.exp(EG)))
    for r in (1, 1.5, 2, 3, 5, 10, 40):
        print(f"{r} | {m_of(r):.5f} | " + (f"{m_of(r) / (r - 1):.6f}" if r > 1 else ""))
    print("\nalpha = ln s/ln Q | limit of variance/mean | / alpha")
    for a in (0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05):
        print(f"{a} | {v_limit(a):.4f} | {v_limit(a) / a:.4f}")
    print("\nchecks of the price equation: rows independent (v = 1): Lam = %.5f (exactly 1);  v = alpha: Lam = %.6f (K = 1.5164516...)"
          % (price_constant(lambda a: 1.0), price_constant(lambda a: a)))
    print("\nlam = ln x/ln Q | Lam(lam) | constant of Q/ln^2 x: 2 C2 e^-gamma lam^2 Lam | F(lam) = D/(x ln^2 x) at this lam | first moment: 1/lam and e^gamma/(2 C2 lam)")
    for lam in (0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0):
        L = price_constant(v_limit, lam); c = 2 * C2 * math.exp(-EG) * lam * lam * L
        print(f"{lam} | {L:.5f} | {c:.4f} | {1 / c:.4f} | {1 / lam:.4f}, {math.exp(EG) / (2 * C2 * lam):.4f}", flush=True)
    L1 = price_constant(v_limit, 1.0)
    print(f"\nlimit: ln g0 = theta(x) - {2 * C2 * math.exp(-EG) * L1:.4f} Q/ln^2 x,   D(n)/(r ln^2 r) -> e^gamma/(2 C2 Lam(1)) = {math.exp(EG) / (2 * C2 * L1):.4f}   (Lam(1) = {L1:.5f})")
