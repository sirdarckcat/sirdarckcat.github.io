#!/usr/bin/env python3
"""The constant K of the research session's price heuristic, with rigorous error bounds.

    K = exp(2 L),     L = lim_{y -> 0+} [ int_y^oo dt / (t + e^t - 1)  +  (1/2) ln y ]

(goldbach/sublinear/README.md on branch ccr-d4a17dd0-7uu03r, "How many complete covers there are").
Everything below is exact rational arithmetic (fractions.Fraction); the only inputs that are not
rational, e^-1 and the final exponential, are bracketed by partial sums of their series.  The
analytic steps, each elementary:

1.  Write g(t) = 1 / (t + e^t - 1).  Then

        L = int_0^1 f(t) dt + int_1^oo g(t) dt,        f(t) = g(t) - 1/(2t),

    because int_y^1 g = int_y^1 f - (1/2) ln y and f is bounded near 0 (step 2).

2.  With phi(t) = (e^t - 1 - t)/t^2 = sum_{n>=0} t^n/(n+2)!  one has  t + e^t - 1 = t (2 + t phi(t)),  so

        f(t) = - phi(t) / (4 + 2 t phi(t)).

    Its Taylor coefficients c_n at 0 are rational and satisfy (multiply out f * (4 + 2 t phi) = -phi)

        4 c_n = - 1/(n+2)! - sum_{k=1..n} d_k c_{n-k},        d_k = 2/(k+1)!.

    Bound: |c_n| <= A rho^n with rho = 2/3, A = 3/8.  Induction: the right side is at most
    1/(n+2)! + A rho^n S with S = sum_{k>=1} d_k rho^-k = (4/3)(e^{3/2} - 5/2) < 2.65, so
    |c_n| <= (1/4)/(n+2)! + (2.65/4) A rho^n <= A rho^n, as (1/4)/(n+2)! <= (1.35/4) A rho^n for
    all n >= 0 (at n = 0: 1/8 <= 0.1265...; the left side falls faster than the right).
    (The bound S < 2.65 is checked below with a rational upper bound of e^{3/2}.)
    Hence the series converges on [0, 1] and

        int_0^1 f = sum_{n<=N} c_n/(n+1) + R,     |R| <= A rho^(N+1) / ((1 - rho)(N+2)).

3.  For t >= 1 put u = (t - 1) e^-t, 0 <= u <= e^-2.  Then g = e^-t / (1 + u) = sum_k (-1)^k (t-1)^k e^{-(k+1)t},
    the sum of absolute values is integrable, and int_1^oo (t-1)^k e^{-(k+1)t} dt = k! e^{-(k+1)} / (k+1)^(k+1):

        int_1^oo g = sum_{k>=0} (-1)^k T_k,      T_k = k! e^{-(k+1)} / (k+1)^(k+1),

    an alternating series with decreasing terms (T_{k+1}/T_k = e^-1 (1 + 1/(k+1))^-(k+1) (k+1)/(k+2) < 1),
    so consecutive partial sums bracket it.

4.  e^-1 = sum (-1)^j / j!  (alternating, decreasing terms: partial sums bracket it), and for 0 <= x < 1
    sum_{j<=m} x^j/j!  <=  e^x  <=  sum_{j<=m} x^j/j! + x^(m+1) / ((m+1)! (1 - x/(m+2))).

    python3 -I K_enclosure.py > K_enclosure.txt
"""
from fractions import Fraction as F
from math import factorial
import math

N_TAYLOR = 150        # terms of the series of f
M_TAIL = 40           # terms of the alternating series of the tail (an even number of them + 1)
J_E = 60              # terms for e^-1


def exp_bounds(x, m=60):
    """rational lower and upper bounds for e^x, 0 <= x < 2"""
    assert 0 <= x < 2
    s, term = F(0), F(1)
    for j in range(m + 1):
        s += term
        term = term * x / (j + 1)
    # term is now x^(m+1)/(m+1)!
    return s, s + term / (1 - x / (m + 2))


def main():
    # step 4: e^-1
    s, lo, hi = F(0), None, None
    for j in range(J_E + 1):
        s += F((-1) ** j, factorial(j))
        if j == J_E - 1: a = s
        if j == J_E: b = s
    e1_lo, e1_hi = min(a, b), max(a, b)

    # step 2: the constant S and the coefficients
    e32_hi = exp_bounds(F(3, 2))[1]
    S_hi = F(4, 3) * (e32_hi - F(5, 2))
    assert S_hi < F(265, 100)
    A, rho = F(3, 8), F(2, 3)
    for n in range(0, 400):          # (1/4)/(n+2)! <= (1.35/4) A rho^n; beyond n = 0 the ratio only improves
        assert F(1, 4) / factorial(n + 2) <= F(135, 400) * A * rho ** n
    c = []
    for n in range(N_TAYLOR + 1):
        acc = F(1, factorial(n + 2))
        for k in range(1, n + 1):
            acc += F(2, factorial(k + 1)) * c[n - k]
        c.append(-acc / 4)
        assert abs(c[n]) <= A * rho ** n
    I0 = sum(c[n] / (n + 1) for n in range(N_TAYLOR + 1))
    R = A * rho ** (N_TAYLOR + 1) / ((1 - rho) * (N_TAYLOR + 2))
    I0_lo, I0_hi = I0 - R, I0 + R

    # step 3: the tail.  T_k is increasing in e^-1, so bracket each term and each partial sum.
    def T(k, e1):
        return F(factorial(k), (k + 1) ** (k + 1)) * e1 ** (k + 1)
    even_lo = sum(T(k, e1_lo) for k in range(0, M_TAIL + 1, 2))      # sums over even k, lower / upper
    even_hi = sum(T(k, e1_hi) for k in range(0, M_TAIL + 1, 2))
    odd_lo = sum(T(k, e1_lo) for k in range(1, M_TAIL + 1, 2))
    odd_hi = sum(T(k, e1_hi) for k in range(1, M_TAIL + 1, 2))
    # partial sum through k = M_TAIL (even) is an upper bound; through k = M_TAIL + 1 a lower bound
    I1_hi = even_hi - odd_lo
    I1_lo = even_lo - odd_hi - T(M_TAIL + 1, e1_hi)

    L_lo, L_hi = I0_lo + I1_lo, I0_hi + I1_hi
    assert 0 < L_lo <= L_hi < F(1, 2)
    K_lo = exp_bounds(2 * L_lo)[0]
    K_hi = exp_bounds(2 * L_hi)[1]

    def dec(x, up, digits=30):
        """decimal expansion of a rational, rounded down (up = False) or up (up = True)"""
        n = x.numerator * 10 ** digits
        q = -((-n) // x.denominator) if up else n // x.denominator
        sign, q = ('-' if q < 0 else ''), abs(q)
        t = f"{q:0{digits + 1}d}"
        return sign + t[:-digits] + '.' + t[-digits:]

    print("K = exp(2 L),  L = lim_{y->0+} [ int_y^oo dt/(t + e^t - 1) + (1/2) ln y ]")
    print("exact rational arithmetic; lower ends are rounded down and upper ends up (see the docstring for the proof)")
    print()
    print(f"int_0^1 [1/(t + e^t - 1) - 1/(2t)] dt  in  [{dec(I0_lo, False)}, {dec(I0_hi, True)}]")
    print(f"int_1^oo dt/(t + e^t - 1)              in  [{dec(I1_lo, False)}, {dec(I1_hi, True)}]")
    print(f"L                                      in  [{dec(L_lo, False)}, {dec(L_hi, True)}]")
    print(f"K                                      in  [{dec(K_lo, False)}, {dec(K_hi, True)}]")
    print(f"width of the enclosure of K: {float(K_hi - K_lo):.3e}")
    print()

    # an independent look in floating point: the definition itself, by Simpson's rule in the variable s = ln t
    def g(t):
        return 1.0 / (t + math.expm1(t))
    def simpson(fun, a, b, n):
        h = (b - a) / n
        return (fun(a) + fun(b) + 4 * sum(fun(a + (2 * i + 1) * h) for i in range(n // 2))
                + 2 * sum(fun(a + 2 * i * h) for i in range(1, n // 2))) * h / 3
    for y in (1e-3, 1e-5, 1e-7):
        val = simpson(lambda s: g(math.exp(s)) * math.exp(s), math.log(y), math.log(60.0), 400000) + 0.5 * math.log(y)
        print(f"floating point, the definition at y = {y:g}:  bracket = {val:.12f},  exp(2 bracket) = {math.exp(2 * val):.12f}"
              f"   (the bracket differs from L by about y/8 = {y / 8:.1e})")
    print()
    print("first Taylor coefficients of f(t) = 1/(t + e^t - 1) - 1/(2t):  " + ", ".join(str(x) for x in c[:6]))


if __name__ == "__main__":
    main()
