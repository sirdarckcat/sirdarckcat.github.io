#!/usr/bin/env python3
"""Johnson accounting for list recovery in F_q[x] with places of several degrees (exact arithmetic, no randomness).

Places: all monic irreducibles of degree d0..d1 (I_q(e) of degree e).  Lists of density rho: l_e = rho q^e classes.
Theorem 1 (page): multiplicities s_i on the listed classes; if  M_n(D) > C = sum_i l_i d_i s_i(s_i+1)/2  then every N of
degree < n with  sum_{i agreeing} s_i d_i >= D  is a y-root of one nonzero Q of (1,n-1)-weighted degree < D.
Full agreement: D = sum_i s_i d_i.  Large-multiplicity limit with s_i ~ 1/l_i :  n - 1 < sum_i d_i / l_i = mu / rho,
mu = sum_i d_i q^(-d_i) the "Mertens mass" of the places (at most 1 per degree).
"""
import math
from fractions import Fraction as F
from sympy import divisors, mobius


def I(q, e):
    return int(sum(int(mobius(e // d)) * q ** d for d in divisors(e)) // e)


def M(n, D):
    if D <= 0:
        return 0
    J = (D - 1) // (n - 1)
    return (J + 1) * D - (n - 1) * J * (J + 1) // 2


def table(q, rho, d0, d1, tmax=60):
    degs = range(d0, d1 + 1)
    le = {e: rho * q ** e for e in degs}
    assert all(l.denominator == 1 and l >= 1 for l in le.values()), "rho q^e must be a positive integer"
    Ie = {e: I(q, e) for e in degs}
    T = sum(e * Ie[e] for e in degs)
    m = sum(Ie.values())
    mu = sum(F(e * Ie[e], q ** e) for e in degs)
    lim = mu / rho                                    # n - 1 < lim
    nmax_lim = math.ceil(lim)                         # largest n with n - 1 < lim   (n - 1 <= ceil(lim) - 1)
    tables = sum(Ie[e] * int(le[e]) for e in degs)    # list entries read
    print(f"q={q} rho={rho} degrees {d0}..{d1}: places m={m}, total degree T={T}, Mertens mass mu={float(mu):.4f}, "
          f"list entries={tables}")
    print(f"   limit of the guarantee: n - 1 < mu/rho = {float(lim):.4f}  ->  n <= {nmax_lim}"
          f"   (T/n = {T / nmax_lim:.1f})")
    for n in range(max(2, nmax_lim - 2), nmax_lim + 2):
        lnE = n * math.log(q) + m * math.log(float(rho))
        found = None
        for t in range(1, tmax + 1):
            s = {e: t * q ** (d1 - e) for e in degs}                       # s_e proportional to 1/l_e
            C = sum(Ie[e] * int(le[e]) * e * s[e] * (s[e] + 1) // 2 for e in degs)
            D = sum(Ie[e] * e * s[e] for e in degs)                         # full agreement
            if M(n, D) > C:
                found = (t, C, M(n, D), D, (D - 1) // (n - 1))
                break
        if found:
            t, C, Mn, D, J = found
            print(f"   n={n:3d}: guaranteed at t={t} (s_e = t q^(d1-e)): constraints C={C}, unknowns M_n(D)={Mn}, D={D}, "
                  f"y-degree bound J={J};  q^n={q ** n:.3e};  ln E|C(L)| for random lists = {lnE:.1f}")
        else:
            print(f"   n={n:3d}: no guarantee for t <= {tmax};  q^n={q ** n:.3e};  ln E|C(L)| = {lnE:.1f}")
    return mu


print("=== A. full agreement, lists of density rho at every place of degree d0..d1 ===")
for q, rho, d0, d1 in [(5, F(2, 5), 1, 1), (5, F(2, 5), 1, 2), (5, F(2, 5), 1, 3), (5, F(2, 5), 1, 4),
                       (3, F(1, 3), 1, 3), (3, F(1, 3), 1, 4), (3, F(1, 3), 1, 6), (3, F(2, 3), 1, 6),
                       (13, F(6, 13), 1, 1), (13, F(6, 13), 1, 3), (2, F(1, 2), 1, 8), (2, F(1, 2), 1, 12)]:
    table(q, rho, d0, d1)
    print()

print("=== B. Mertens mass per degree  e I_q(e) / q^e  (at most 1) ===")
for q in (2, 3, 5, 13):
    print(q, [round(e * I(q, e) / q ** e, 4) for e in range(1, 13)])

print()
print("=== C. a window of dimension w after pins; later places of degree d0..d1; lists of density rho, list-symmetric")
print("       weights.  typical member (agreement rho by mass) is inside the guarantee iff rho*mu > w - 1;")
print("       fully consistent member iff mu/rho > w - 1.  Compare the size of the input with the window q^w. ===")
for q, rho, d0, w in [(3, F(1, 3), 4, 12), (3, F(2, 3), 4, 12), (5, F(2, 5), 3, 10), (5, F(4, 5), 3, 10), (2, F(1, 2), 9, 24)]:
    for kind, need in (("full agreement", (w - 1) * rho), ("typical member ", (w - 1) / rho)):
        mu = F(0); d1 = d0 - 1
        while mu <= need:
            d1 += 1
            mu += F(d1 * I(q, d1), q ** d1)
        T = sum(e * I(q, e) for e in range(d0, d1 + 1))
        m = sum(I(q, e) for e in range(d0, d1 + 1))
        lnE = w * math.log(q) + m * math.log(float(rho))
        print(f"q={q} rho={rho} d0={d0} w={w} ({kind}): needs mass > {float(need):.2f}: degrees {d0}..{d1}, T={T:.3e}, "
              f"window q^w={q ** w:.3e}, T/q^w={T / q ** w:.3e}" + (f", ln E(#fully consistent in window)={lnE:.3e}" if kind.startswith("full") else ""))

print()
print("=== D. the same boundary in one line (places of all degrees 1..d, density rho):  n_max = ceil(mu_d / rho) ===")
for q in (3, 5, 13, 101):
    for rho in (0.25, 0.5, 0.75):
        row = []
        for d in (1, 2, 4, 8, 16):
            mu = sum(e * I(q, e) / q ** e for e in range(1, d + 1))
            m = sum(I(q, e) for e in range(1, d + 1))
            n = math.ceil(mu / rho)
            row.append(f"d={d}: n<={n}, log10 E={(n * math.log(q) + m * math.log(rho)) / math.log(10):.3g}")
        print(f"q={q} rho={rho}: " + "; ".join(row))
