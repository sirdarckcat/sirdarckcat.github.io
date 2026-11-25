#!/usr/bin/env python3
"""Steps 1 and 2 of the research session's limit, from the exact sums of pair_limit.c.

    python3 -I analyse.py pl_s101_1e10.txt pl_s1009_1e10.txt ... > steps_1_2.txt

Step 1 (claim): R(m) = (a c/2) M(m) (1 + o(1)).
Step 2 (claim): M(s^rho) = g2 ln^2 s m(rho) (1 + o(1)),  m = rho^2 on [0, 1],  rho m' = 2 m - m(rho - 1) beyond.

Second-order terms, for m and x below s (computed here from the Dirichlet series
sum u(d) d^-w = zeta(w + 1)^2 H(w), H(0) = 2 g2, H'(0)/H(0) = ln 12; and sum f(j) j^-w = zeta(w) zeta(w + 1)^2 H(w)):

    M(x)      = g2 [ ln^2 x + 2 (2 gamma + ln 12) ln x + B_M ]                 (+ a power-saving error)
    R(m)/(ac) = g2 [ ln^2 m / 2 + (2 gamma + ln 12 + ln 2 pi) ln m + B_R ]      (+ an oscillation of size about 0.5)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cover_count"))
import Lam_check as LC  # noqa: E402

EG, C2 = LC.EG, LC.C2
G1 = -0.07281584548367672486                     # Stieltjes constant gamma_1
ZETA2_0 = -2.00635645590858485121                # zeta''(0)


def primes_upto(n):
    import numpy as np
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]


def constants():
    """g2, c_infinity, and the second derivative of ln H at 0, from the primes up to 10^8 and integral tails"""
    import numpy as np
    P = primes_upto(10 ** 8).astype(float); P = P[P >= 5]; T = 1e8
    def e1(y):                                  # E1 by the asymptotic series (y ~ 18)
        s, term = 0.0, 1.0
        for n in range(1, 15):
            s += term; term *= -n / y
        return math.exp(-y) / y * s
    # ln of prod (p-1)^3/(p^2 (p-3)) ~ sum 3/p^2 ;  ln of prod p(p-3)/((p-1)(p-2)) ~ - sum 2/p^2
    lg = float(np.sum(3 * np.log(P - 1) - 2 * np.log(P) - np.log(P - 3))) + 3 * e1(math.log(T))
    lc = float(np.sum(np.log(P) + np.log(P - 3) - np.log(P - 1) - np.log(P - 2))) - 2 * e1(math.log(T))
    g2 = math.exp(lg) / 18; cinf = math.exp(lc)
    # (ln H)''(0) = -4 ln^2 2 - (3/2) ln^2 3 - 6 sum_{p >= 5} ln^2 p/(p-1)^2 ;  tail: int ln t/t^2 = (ln T + 1)/T
    d2 = -4 * math.log(2) ** 2 - 1.5 * math.log(3) ** 2 - 6 * (float(np.sum(np.log(P) ** 2 / (P - 1) ** 2)) + (math.log(T) + 1) / T)
    return g2, cinf, d2


def read(path):
    rows = []; head = open(path).readline()
    s = int(head.split("s = ")[1].split(",")[0]); a = float(head.split("a = 6s/(s-1) = ")[1].split(";")[0]); c = float(head.split("c = ")[1].split(" ")[0])
    for line in open(path):
        if line.startswith("#"): continue
        t = line.split(); rows.append((int(t[0]), float(t[1]), float(t[2]), float(t[3]), float(t[4]), float(t[5]) if len(t) > 5 else float("nan")))
    return s, a, c, rows


def interp_M(rows, x):
    """M at x by a cubic in ln x through the four nearest checkpoints (M is smooth on that scale)"""
    pts = []
    for r in rows:
        if r[0] >= 30 and (not pts or math.log(r[0]) - pts[-1][0] > 0.05): pts.append((math.log(r[0]), r[1]))   # no near-coincident nodes
    lx = math.log(x)
    if lx > pts[-1][0]: return float("nan")
    pts.sort(key=lambda t: abs(t[0] - lx)); near = sorted(pts[:4])
    val = 0.0
    for i, (xi, yi) in enumerate(near):
        w = 1.0
        for j, (xj, _) in enumerate(near):
            if j != i: w *= (lx - xj) / (xi - xj)
        val += w * yi
    return val


def main():
    LC.build()
    g2, cinf, d2 = constants()
    h1 = math.log(12); h2 = (h1 * h1 + d2) / 2
    A = 2 * (2 * EG + h1)
    BM = 2 * (EG * EG - 2 * G1 + h2 + 2 * EG * h1)
    z1 = math.log(2 * math.pi); z2 = -ZETA2_0
    AR = 2 * EG + h1 + z1
    BR = z2 + EG * EG - 2 * G1 + h2 + 2 * EG * z1 + z1 * h1 + 2 * EG * h1
    print("# analyse.py: steps 1 and 2 of the limit, from exact sums (pair_limit.c)")
    print(f"g2 = (1/2) prod (1 - 1/p)^2 (1 + u_p) = {g2:.10f};  c_infinity = prod (1 + u_p/p)^-1 = {cinf:.10f};  C2 = {C2:.10f}")
    print(f"step 3, the constants: 24 C2 c_infinity g2 = {24 * C2 * cinf * g2:.10f}   (claimed: 1)")
    print(f"second-order terms below s:  M(x) = g2 [ln^2 x + {A:.5f} ln x + {BM:.4f}],   R(m)/(a c) = g2 [ln^2 m/2 + {AR:.5f} ln m + {BR:.4f}] - 1/(2c) on the mean over integers m")
    print(f"   so  M(x) ~ g2 ln^2({math.exp(A / 2):.2f} x)  and  R(m) ~ (a c g2/2) ln^2({math.exp(AR):.1f} m):  the first correction is a shift of the logarithm,")
    print(f"   and in every range  R(m) ~ (a c/2) M(2 pi m) - a/2   (zeta(w)/zeta(0) = exp(w ln 2 pi + ...) in the Dirichlet series)")
    runs = [read(p) for p in sys.argv[1:]]
    print("\nSTEP 1.  R against (a c/2) M.  Rbar = mean of R over the 65536 integers ending at m (R at one m oscillates by a few units).")
    for s, a, c, rows in runs:
        name = "infinite" if s == 0 else str(s)
        print(f"\n  s = {name}  (a = {a:.6f}, c = {c:.9f})")
        print("              m       R(m)       Rbar   (a c/2) M(m)   Rbar/((a c/2) M(m))   (a c/2) M(2 pi m') - a/2   Rbar minus that   | expansion (m < s)      [m' = centre of the window; first three rows: R itself]")
        for m, M, S1, F, R, Rb in rows:
            lm = math.log(m)
            if abs(round(math.log10(m)) - math.log10(m)) > 1e-9 or m < 1000: continue
            use = Rb if Rb == Rb else R
            mc = m - 32767.5 if Rb == Rb else m                 # the centre of the window
            m2 = interp_M(rows, 2 * math.pi * mc); shifted = a * c * m2 / 2 - a / 2
            extra = ""
            lc = math.log(mc)
            if s == 0 or m < s: extra = f"   | {a * c * g2 * (lc * lc / 2 + AR * lc + BR) - a / 2:10.3f}"
            print(f"  {m:13d} {R:10.3f} {Rb:10.3f} {a * c * M / 2:12.3f}   {use / (a * c * M / 2):12.4f}          {shifted:12.3f}            {use - shifted:9.3f}{extra}")
    def mprime(rho):
        return 2 * rho if rho <= 1 else (2 * LC.m_of(rho) - LC.m_of(rho - 1)) / rho
    print("\nSTEP 2.  M(s^rho) against g2 ln^2 s m(rho);  d = (ratio - 1) ln s.")
    print("  First-order term (from the exact identity sum u(d) ln d = sum over prime powers, whose weight is 2 ln t - (2 gamma + ln 12) below s):")
    print("     M(s^rho) = g2 ln^2 s [ m(rho) + (2 gamma + ln 12) m'(rho)/ln s + ... ],   so d -> (2 gamma + ln 12) m'(rho)/m(rho).")
    print("          s    rho             x        M(x)   g2 ln^2 s m(rho)    ratio        d    d predicted   with the first-order term: ratio")
    for s, a, c, rows in runs:
        if s == 0: continue
        byM = {r[0]: r[1] for r in rows}
        for k in range(2, 41):
            rho = k / 4; x = round(s ** rho)
            if x not in byM or x < 10: continue
            ls = math.log(s)
            pred = g2 * ls ** 2 * LC.m_of(rho); dp = (A / 2) * mprime(rho) / LC.m_of(rho)
            pred1 = g2 * ls ** 2 * (LC.m_of(rho) + (A / 2) * mprime(rho) / ls)
            print(f"  {s:9d}  {rho:5.2f} {x:15d} {byM[x]:10.4f} {pred:12.4f}   {byM[x] / pred:8.4f}   {(byM[x] / pred - 1) * ls:8.3f}   {dp:8.3f}        {byM[x] / pred1:8.4f}")
        print()
    print("STEP 3, the first correction to the limit profile.  With rho0 = (1 - alpha)/alpha the same expansions give")
    print("     variance/mean = v(alpha) - c(alpha)/ln Q + ...,    c(alpha) = (e^-gamma/2) [ (2 gamma + ln 4 pi - 1) m'(rho0) + alpha m(rho0) ]")
    print("  against the research session's measured c (cover_limit.txt: Q = 10^6 and 10^8, mean over 7 moduli; their moduli at small alpha are below 100):")
    meas = {0.12: (4.05, 4.14), 0.16: (3.93, 3.89), 0.2: (3.71, 3.72), 0.25: (3.49, 3.49), 0.3: (3.26, 3.23), 0.35: (2.93, 2.91), 0.4: (2.58, 2.53),
            0.45: (2.18, 2.15), 0.5: (1.83, 1.77), 0.55: (1.49, 1.45), 0.6: (1.20, 1.17), 0.65: (0.97, 0.95), 0.7: (0.77, 0.74), 0.75: (0.63, 0.56),
            0.8: (0.46, 0.45), 0.85: (0.31, 0.31)}
    print("     alpha   c by the formula   measured at 10^6, 10^8   measured, extrapolated in 1/ln Q")
    for al in sorted(meas):
        r0 = (1 - al) / al
        cf = 0.5 * math.exp(-EG) * ((2 * EG + math.log(4 * math.pi) - 1) * mprime(r0) + al * LC.m_of(r0))
        c6, c8 = meas[al]; l6, l8 = math.log(1e6), math.log(1e8)
        ext = (c8 * l8 - c6 * l6) / (l8 - l6)
        print(f"     {al:5.2f}   {cf:8.3f}           {c6:5.2f}  {c8:5.2f}               {ext:6.2f}")
    print()
    for s, a, c, rows in runs:
        if s != 0: continue
        print("STEP 2, s infinite (every x is below s): M(x) against g2 ln^2 x and against the second-order form.")
        print("              x        M(x)    g2 ln^2 x    ratio    g2 [ln^2 x + A ln x + B]    difference")
        for m, M, S1, F, R, Rb in rows:
            if abs(round(math.log10(m)) - math.log10(m)) > 1e-9 or m < 100: continue
            lm = math.log(m); second = g2 * (lm * lm + A * lm + BM)
            print(f"  {m:13d} {M:11.5f} {g2 * lm * lm:11.5f} {M / (g2 * lm * lm):8.4f}   {second:14.5f}           {M - second:9.5f}")


if __name__ == "__main__":
    main()
