#!/usr/bin/env python3
"""Numerical check of Theorem 1 in its soft form (a multiplicity for every class of every place) and of Theorem 2
(the necessary condition) on random instances, places of degree 1 and 2 over F_5 and of degree 1..3 over F_3.

For multiplicities s[i][c] >= 0:  C = sum d_i s(s+1)/2,  D = least integer with M_n(D) > C,
captured set S = {N : A(N) = sum_i d_i s[i][N mod pi_i] >= D}.
Theorem 1: every N in S is a y-root of every Q in the interpolation space; |S| <= floor((D-1)/(n-1)).
Theorem 2: for nu uniform on S with marginals pi_i:
     sum_i d_i sum_{c: s[i][c] > 0} pi_i(c)^2  >  (sqrt(n-1) - (n-1)/(2 ||s||))^2 ,   ||s||^2 = sum d_i s^2.
"""
import math, random, sys
import numpy as np
from w2core import *

rng = random.Random(99)


def run(q, degs, n, plant_mult, noise, trials, nplant=1):
    places = [p for d in degs for p in irreducibles(q, d)]
    okroots = 0; okcount = 0; okT2 = 0; nonempty = 0; sizes = []; margins = []; star_ok = 0
    for _ in range(trials):
        Nstars = [[rng.randrange(q) for _ in range(n)] for _ in range(nplant)]
        mult = []; lists = []
        for pi in places:
            d = len(pi) - 1
            cstar = {poly_mod_code(Nstar, q, pi) for Nstar in Nstars}
            s = {}
            for c in range(q ** d):
                if c in cstar:
                    s[c] = plant_mult[d]
                elif rng.random() < noise[d]:
                    s[c] = rng.randint(1, max(1, plant_mult[d] // 2))
            mult.append(s); lists.append(sorted(s))
        C = n_constraints(places, lists, mult)
        D = 1
        while count_monomials(n, D) <= C:
            D += 1
        # agreement score of every N
        A = np.zeros(q ** n, dtype=np.int64); codes = []
        for pi, s in zip(places, mult):
            d = len(pi) - 1
            tab = np.zeros(q ** d, dtype=np.int64)
            for c, v in s.items():
                tab[c] = v
            rc = residue_codes(q, n, pi); codes.append(rc)
            A += d * tab[rc]
        S = np.nonzero(A >= D)[0]
        sizes.append(len(S))
        Amat, mons = interpolation_matrix(q, n, D, places, lists, mult)
        r, basis = kernel(q, Amat)
        assert len(basis) >= 1
        allroot = all(eval_at(q, mons, v, code_to_poly(int(c), q, n)).is_zero() for c in S for v in basis)
        okroots += allroot
        okcount += len(S) <= (D - 1) // (n - 1)
        norm2 = sum((len(pi) - 1) * v * v for pi, s in zip(places, mult) for v in s.values())
        star = sum((len(pi) - 1) * v * (v + 1) for pi, s in zip(places, mult) for v in s.values())
        # exact sufficient condition (*): A^2 > (n-1) sum d s(s+1)  implies captured
        star_ok += bool(np.all(A[A.astype(float) ** 2 > (n - 1) * star] >= D))
        if len(S):
            nonempty += 1
            lhs = 0.0
            for pi, s, rc in zip(places, mult, codes):
                d = len(pi) - 1
                cnt = np.bincount(rc[S], minlength=q ** d) / len(S)
                lhs += d * sum(cnt[c] ** 2 for c in s)
            rhs = (math.sqrt(n - 1) - (n - 1) / (2 * math.sqrt(norm2))) ** 2
            okT2 += lhs > rhs
            margins.append(lhs / rhs)
    print(f"q={q} degrees {degs} n={n} planted polynomials {nplant}, planted multiplicity by degree {plant_mult} noise {noise}: {trials} instances; "
          f"captured set size {min(sizes)}..{max(sizes)} (nonempty in {nonempty}); all captured N are roots of the whole kernel: "
          f"{okroots}/{trials}; |S| <= J: {okcount}/{trials}; (*) implies captured: {star_ok}/{trials}; "
          f"Theorem 2 inequality holds: {okT2}/{nonempty}" + (f", ratio lhs/rhs {min(margins):.2f}..{max(margins):.2f}" if margins else ""))
    sys.stdout.flush()


run(5, (1,), 2, {1: 3}, {1: 0.4}, 40)
run(5, (1,), 3, {1: 4}, {1: 0.2}, 40)
run(5, (1, 2), 3, {1: 6, 2: 2}, {1: 0.4, 2: 0.15}, 20)
run(5, (1, 2), 4, {1: 6, 2: 2}, {1: 0.2, 2: 0.08}, 20)
run(3, (1, 2, 3), 5, {1: 9, 2: 3, 3: 1}, {1: 0.3, 2: 0.2, 3: 0.1}, 20)
run(3, (1, 2, 3), 7, {1: 9, 2: 4, 3: 2}, {1: 0.0, 2: 0.1, 3: 0.05}, 10)
run(13, (1,), 2, {1: 2}, {1: 0.0}, 20, nplant=2)
run(13, (1,), 2, {1: 3}, {1: 0.05}, 20, nplant=3)
run(5, (1, 2), 3, {1: 6, 2: 2}, {1: 0.0, 2: 0.02}, 20, nplant=2)
run(3, (1, 2, 3), 5, {1: 9, 2: 3, 3: 1}, {1: 0.0, 2: 0.0, 3: 0.0}, 20, nplant=2)
