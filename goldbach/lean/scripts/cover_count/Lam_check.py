#!/usr/bin/env python3
"""An independent computation of the research session's limit constant Lam(1).

The equations are the research session's (goldbach/sublinear/cover_limit.py on branch ccr-d4a17dd0-7uu03r;
heuristic, see there).  This script only asks: given those equations, what is the number?

    m(rho) = rho^2 on [0, 1],      rho m'(rho) = 2 m(rho) - m(rho - 1) for rho > 1,
    v(alpha) = 1 - (e^-gamma / 2) alpha m((1 - alpha)/alpha),            0 < alpha <= 1,
    dp/d ln(alpha) = (e^{v(alpha) p} - 1)/v(alpha),    p = +oo at alpha = 1,
    Lam = lim_{alpha -> 0} p/alpha.

The method here shares nothing with cover_limit.py (which uses RK4 on a table of m with linear interpolation,
starts the price at alpha = 1 - 1e-9 and stops at alpha = 2e-4):

1.  m.  With n = m/rho^2 the delay equation is n'(rho) = -m(rho - 1)/rho^3, so on [k, k+1]
    n(rho) = n(k) - int_k^rho m(t - 1)/t^3 dt.  Each unit interval is represented at 33 Chebyshev points (m is
    analytic inside it), the integrals are done by 24-point Gauss-Legendre.  On [1, 2] there is a closed form,
    m = rho^2 (5/2 - ln rho) - 2 rho + 1/2, used as a check.  Beyond rho = 41 the asymptote 2 e^gamma (rho - 1).
2.  The price.  With s = ln p as the variable and L = ln alpha as the unknown the equation is regular at both ends:

        dL/ds = B(v(alpha) p),      B(x) = x/(e^x - 1),

    L = ln(1 - e^-p) for large p (exact when v = 1, and v = 1 - O((1 - alpha)^2) there), and L - s -> -ln Lam as
    p -> 0.  Integrated by RK4 in s from p = 40 down to p = 1e-7 with three step sizes; the tail below 1e-7 is
    added to first order.
3.  Checks: v = 1 must give Lam = 1, and v = alpha must give K = 1.51645160795950258... (K_enclosure.py).

    python3 -I Lam_check.py > Lam_check.txt

This is floating point with convergence checks, not an enclosure.
"""
import math

EG = 0.57721566490153286060651209008240243104215933593992      # Euler's constant
C2 = 0.66016181584686957392781211001455577843262336028473      # twin-prime constant
K_EXACT = 1.5164516079595025850511213122

NCH = 32                                                         # Chebyshev degree on each unit interval
KMAX = 40                                                        # tables on [1, KMAX + 1]


def gauss_legendre(n):
    """nodes and weights on [-1, 1] by Newton's iteration"""
    xs, ws = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-17: break
        xs.append(x); ws.append(2 / ((1 - x * x) * dp * dp))
    return xs, ws


GLX, GLW = gauss_legendre(24)
CHX = [math.cos(math.pi * j / NCH) for j in range(NCH + 1)]      # Chebyshev points on [-1, 1], from 1 down to -1
CHW = [(0.5 if j in (0, NCH) else 1.0) * (-1) ** j for j in range(NCH + 1)]


def bary(vals, t):
    """the polynomial through (CHX[j], vals[j]) at t in [-1, 1]"""
    num = den = 0.0
    for x, w, f in zip(CHX, CHW, vals):
        d = t - x
        if d == 0.0: return f
        c = w / d; num += c * f; den += c
    return num / den


TABLE = {}                                                       # k -> values of m at the Chebyshev points of [k, k+1]


def m_of(rho):
    if rho <= 1.0: return rho * rho
    k = int(rho)
    if k > KMAX: return 2 * math.exp(EG) * (rho - 1)
    return bary(TABLE[k], 2 * (rho - k) - 1)


def build():
    n_left = 1.0                                                 # n(k) = m(k)/k^2 at the left end
    for k in range(1, KMAX + 1):
        vals = []
        for x in CHX:
            rho = k + 0.5 * (x + 1)
            half = 0.5 * (rho - k)
            integ = sum(w * m_of(k + half * (g + 1) - 1) / (k + half * (g + 1)) ** 3 for g, w in zip(GLX, GLW)) * half
            vals.append(rho * rho * (n_left - integ))
        TABLE[k] = vals
        n_left = vals[0] / (k + 1) ** 2


def v_limit(alpha, one_minus_alpha):
    if alpha >= 0.5: return 1 - 0.5 * math.exp(-EG) * one_minus_alpha ** 2 / alpha
    return 1 - 0.5 * math.exp(-EG) * alpha * m_of(one_minus_alpha / alpha)


def bern(x):
    if x < 1e-8: return 1 - x / 2 + x * x / 12
    return x / math.expm1(x)


def price_constant(v, h, p_hi=40.0, p_lo=1e-7):
    """Lam: RK4 in s = ln p for L = ln alpha, step h"""
    def f(s, L):
        return bern(v(math.exp(L), -math.expm1(L)) * math.exp(s))
    s0, s1 = math.log(p_hi), math.log(p_lo)
    n = int(math.ceil((s0 - s1) / h)); h = (s0 - s1) / n
    s, L = s0, math.log1p(-math.exp(-p_hi))
    for _ in range(n):
        k1 = f(s, L); k2 = f(s - h / 2, L - h / 2 * k1); k3 = f(s - h / 2, L - h / 2 * k2); k4 = f(s - h, L - h * k3)
        L -= h * (k1 + 2 * k2 + 2 * k3 + k4) / 6; s -= h
    E = L - s1
    # the tail: E(-oo) = E(s1) + int_0^p_lo (1 - B(v p))/p dp, with alpha = p e^E below p_lo
    tail = 0.0
    for g, w in zip(GLX, GLW):
        p = 0.5 * p_lo * (g + 1); a = p * math.exp(E)
        x = v(a, 1 - a) * p
        tail += w * (x / 2 - x * x / 12) / p
    tail *= 0.5 * p_lo
    return math.exp(-(E + tail))


def main():
    build()
    print("# Lam_check.py: an independent computation of the limit constant of goldbach/sublinear/cover_limit.py")
    print()
    print("1. m(rho):  rho | m(rho) | m(rho)/(rho - 1)     (2 e^gamma = %.12f)" % (2 * math.exp(EG)))
    for r in (1.5, 2, 3, 5, 10, 20, 40):
        print(f"   {r} | {m_of(r):.12f} | {m_of(r) / (r - 1):.12f}")
    worst = max(abs(m_of(r) - (r * r * (2.5 - math.log(r)) - 2 * r + 0.5)) for r in [1 + i / 997 for i in range(1, 997)])
    print(f"   largest difference from the closed form on [1, 2]: {worst:.2e}")
    print(f"   m - 2 e^gamma (rho - 1) at rho = 10, 15, 20, 41: " + ", ".join(f"{m_of(r) - 2 * math.exp(EG) * (r - 1):.2e}" for r in (10, 15, 20, 41)))
    print()
    print("2. the limit profile:  alpha | v(alpha)")
    for a in (0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05):
        print(f"   {a} | {v_limit(a, 1 - a):.10f}")
    print(f"   v(1/2) - (1 - e^-gamma/4) = {v_limit(0.5, 0.5) - (1 - math.exp(-EG) / 4):.2e}")
    print()
    print("3. the price constant, three step sizes in s = ln p (RK4, error like h^4):")
    print("   step      v = 1 (exact 1)        v = alpha (K = 1.51645160795950...)     the limit profile")
    rows = []
    for h in (1 / 256, 1 / 512, 1 / 1024):
        a = price_constant(lambda al, om: 1.0, h); b = price_constant(lambda al, om: al, h); c = price_constant(v_limit, h)
        rows.append((a, b, c))
        print(f"   1/{round(1 / h):<5d} {a:.14f}      {b:.14f}                         {c:.14f}")
    a, b, c = rows[-1]
    print(f"   errors at the smallest step: v = 1: {a - 1:.1e};  v = alpha: {b - K_EXACT:.1e}")
    print(f"   change of the third column between the last two steps: {rows[-1][2] - rows[-2][2]:.1e}")
    print()
    lam = c
    print(f"Lam(1) = {lam:.11f}")
    print(f"the constant of Q/ln^2 x in the limit law, 2 C2 e^-gamma Lam(1) = {2 * C2 * math.exp(-EG) * lam:.10f}")
    print(f"the limit of D(n)/(r ln^2 r),      e^gamma/(2 C2 Lam(1)) = {math.exp(EG) / (2 * C2 * lam):.10f}")
    print(f"(for independent rows, e^gamma/(2 C2) = {math.exp(EG) / (2 * C2):.10f})")


if __name__ == "__main__":
    main()
