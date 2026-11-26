#!/usr/bin/env python3
"""World 2 experiments at tiny parameters (python-flint + numpy).  Seeds fixed; every number is reproducible.

E1  random dense lists: the number of N of degree < n consistent with every list, by brute force, against
    E = q^n prod rho_i and against the exact variance.
E2  inside the guarantee of Theorem 1 (planted N): the interpolation step is run; its kernel is nonzero and the
    common y-roots of the kernel are exactly the consistent N found by brute force.
E3  outside the guarantee: dimension of the interpolation space V(D = sum s_i d_i, s) on random lists.
E4  the abundant regime (many consistent N): the interpolation space is zero.
"""
import sys, time, math, random
import numpy as np
from w2core import *

T0 = time.time()


def deg1(q, pts=None):
    return [[(-a) % q, 1] for a in (range(q) if pts is None else pts)]


def exact_moments(q, n, places, sizes):
    """E X and Var X for X = #consistent, lists independent uniform of the given sizes"""
    rho = [l / q ** (len(p) - 1) for p, l in zip(places, sizes)]
    EX = q ** n * math.prod(rho)
    # E X^2 = EX * sum over Delta (deg < n) of prod_{i: pi_i does not divide Delta} (l_i - 1)/(q^d_i - 1)
    tot = np.ones(q ** n)
    for p, l in zip(places, sizes):
        d = len(p) - 1
        z = residue_codes(q, n, p) == 0
        tot *= np.where(z, 1.0, (l - 1) / (q ** d - 1))
    EX2 = EX * tot.sum()
    return EX, EX2 - EX * EX


def common_roots(q, n, mons, basis):
    roots = None
    for v in basis:
        if roots is None:
            roots = y_roots(q, n, mons, v)
        else:
            roots = [c for c in roots if eval_at(q, mons, v, code_to_poly(c, q, n)).is_zero()]
        if len(basis) > 6 and roots is not None and len(roots) <= 1 and v is not basis[-1]:
            # keep checking all vectors on the few survivors (cheap)
            pass
    return roots


print("=== E1. brute-force count of consistent N against E = q^n prod rho_i ===")
rng = random.Random(20261126)
E1 = [("q=13, all 13 points, lists of 6", 13, deg1(13), [6] * 13, [3, 4, 5]),
      ("q=13, 8 points, lists of 6", 13, deg1(13, range(8)), [6] * 8, [2, 3, 4]),
      ("q=5, 5 points (lists of 3) + 10 quadratics (lists of 15)", 5, deg1(5) + irreducibles(5, 2), [3] * 5 + [15] * 10, [5, 6, 7]),
      ("q=3, 3 points (lists of 2) + 3 quadratics (6) + 8 cubics (18)", 3, deg1(3) + irreducibles(3, 2) + irreducibles(3, 3),
       [2] * 3 + [6] * 3 + [18] * 8, [6, 8, 10])]
for name, q, places, sizes, ns in E1:
    for n in ns:
        trials = 200 if q ** n < 10 ** 5 else 60
        xs = []
        for _ in range(trials):
            lists = random_lists(q, places, sizes, rng)
            xs.append(len(consistent(q, n, places, lists)[0]))
        xs = np.array(xs, dtype=float)
        EX, VX = exact_moments(q, n, places, sizes)
        print(f"{name}; n={n}: q^n={q ** n}; mean count {xs.mean():.3f} +- {xs.std(ddof=1) / math.sqrt(trials):.3f} "
              f"(trials {trials}); E = {EX:.3f}; sample var {xs.var(ddof=1):.3f}, exact var {VX:.3f}; max {int(xs.max())}")
    sys.stdout.flush()

print()
print("=== E2. inside the guarantee, planted N: interpolation run, common y-roots of the kernel against brute force ===")
rng = random.Random(7)
E2 = [("q=13 points ell=6", 13, deg1(13), [6] * 13, 2, [1] * 13, 20),
      ("q=5 points ell=2", 5, deg1(5), [2] * 5, 3, [3] * 5, 20),
      ("q=5 deg 1-2 rho=2/5", 5, deg1(5) + irreducibles(5, 2), [2] * 5 + [10] * 10, 4, [5] * 5 + [1] * 10, 10),
      ("q=3 deg 1-3 rho=1/3", 3, deg1(3) + irreducibles(3, 2) + irreducibles(3, 3), [1] * 3 + [3] * 3 + [9] * 8, 6, [9] * 3 + [3] * 3 + [1] * 8, 10),
      ("q=3 deg 1-3 rho=1/3", 3, deg1(3) + irreducibles(3, 2) + irreducibles(3, 3), [1] * 3 + [3] * 3 + [9] * 8, 7, [18] * 3 + [6] * 3 + [2] * 8, 5),
      ("q=5 deg 1-2 rho=2/5", 5, deg1(5) + irreducibles(5, 2), [2] * 5 + [10] * 10, 5, [20] * 5 + [4] * 10, 2),
      ("q=3 deg 1-3 rho=1/3", 3, deg1(3) + irreducibles(3, 2) + irreducibles(3, 3), [1] * 3 + [3] * 3 + [9] * 8, 8, [36] * 3 + [12] * 3 + [4] * 8, 1)]
for name, q, places, sizes, n, mult, trials in E2:
    D = sum(m * (len(p) - 1) for p, m in zip(places, mult))
    okc = 0; kd = []; ncons = []; tb = 0.0
    for _ in range(trials):
        N = [rng.randrange(q) for _ in range(n)]
        lists = random_lists(q, places, sizes, rng, planted=N)
        cons, _ = consistent(q, n, places, lists)
        t1 = time.time()
        A, mons = interpolation_matrix(q, n, D, places, lists, mult)
        r, basis = kernel(q, A)
        tb += time.time() - t1
        roots = common_roots(q, n, mons, basis)
        kd.append(len(basis)); ncons.append(len(cons))
        okc += (sorted(roots) == sorted(int(c) for c in cons))
    C = n_constraints(places, lists, mult); Mn = count_monomials(n, D)
    print(f"{name}, n={n}, multiplicities by degree {sorted(set(mult), reverse=True)}: D={D}, constraints C={C}, unknowns M={Mn}, "
          f"q^n={q ** n}; kernel dim {min(kd)}..{max(kd)} (M-C={Mn - C}); consistent N per instance {min(ncons)}..{max(ncons)}; "
          f"common roots == brute-force consistent set in {okc}/{trials}; interpolation {tb / trials:.2f}s each; "
          f"work: q^n*m={q ** n * len(places)} residue checks against M^2={Mn * Mn} (structured) .. M^3={Mn ** 3:.2e} (dense elimination)")
    sys.stdout.flush()

print()
print("=== E3. outside the guarantee: dim of V(D = sum s_i d_i, s) on random lists (planted and not) ===")
rng = random.Random(11)
E3 = [("q=13 points ell=6 (limit n<=3)", 13, deg1(13), [6] * 13, 4, lambda t: [t] * 13, range(1, 7), 6),
      ("q=13 points ell=6 (limit n<=3)", 13, deg1(13), [6] * 13, 5, lambda t: [t] * 13, range(1, 7), 6),
      ("q=5 deg 1-2 rho=2/5 (limit n<=5)", 5, deg1(5) + irreducibles(5, 2), [2] * 5 + [10] * 10, 6, lambda t: [5 * t] * 5 + [t] * 10, range(1, 4), 4),
      ("q=5 deg 1-2 rho=3/5 (limit n<=3)", 5, deg1(5) + irreducibles(5, 2), [3] * 5 + [15] * 10, 5, lambda t: [5 * t] * 5 + [t] * 10, range(1, 4), 4),
      ("q=3 deg 1-3 rho=2/3 (limit n<=4)", 3, deg1(3) + irreducibles(3, 2) + irreducibles(3, 3), [2] * 3 + [6] * 3 + [18] * 8, 6,
       lambda t: [9 * t] * 3 + [3 * t] * 3 + [t] * 8, range(1, 4), 4)]
for name, q, places, sizes, n, multf, ts, trials in E3:
    for planted in (False, True):
        line = []
        for t in ts:
            mult = multf(t)
            D = sum(m * (len(p) - 1) for p, m in zip(places, mult))
            dims = []; cs = []
            for _ in range(trials):
                N = [rng.randrange(q) for _ in range(n)] if planted else None
                lists = random_lists(q, places, sizes, rng, planted=N)
                cs.append(len(consistent(q, n, places, lists)[0]))
                A, mons = interpolation_matrix(q, n, D, places, lists, mult)
                r, basis = kernel(q, A)
                dims.append(len(basis))
            C = n_constraints(places, lists, mult); Mn = count_monomials(n, D)
            line.append(f"t={t}: C={C} M={Mn} dimV={min(dims)}..{max(dims)} (#cons {min(cs)}..{max(cs)})")
        print(f"{name}, n={n}, planted={planted}, {trials} instances: " + "; ".join(line))
        sys.stdout.flush()

print()
print("=== E4. the abundant regime: q=13, 8 points, lists of 6, n=3 and 4 (E = 4.5 and 59 consistent N) ===")
rng = random.Random(13)
q = 13; places = deg1(13, range(8)); sizes = [6] * 8
for n in (3, 4):
    res = []
    for s in range(1, 9):
        D = 8 * s; dims = []; cs = []; forced = 0
        for _ in range(10):
            lists = random_lists(q, places, sizes, rng)
            c = len(consistent(q, n, places, lists)[0]); cs.append(c)
            forced += c > (D - 1) // (n - 1)
            A, mons = interpolation_matrix(q, n, D, places, lists, [s] * 8)
            r, basis = kernel(q, A); dims.append(len(basis))
        res.append(f"s={s}: C={n_constraints(places, lists, [s] * 8)} M={count_monomials(n, D)} J={(D - 1) // (n - 1)} "
                   f"dimV={min(dims)}..{max(dims)} #cons {min(cs)}..{max(cs)} (zero forced by |C(L)|>J in {forced}/10)")
    print(f"n={n}: " + "; ".join(res))
    sys.stdout.flush()
print(f"total time {time.time() - T0:.0f}s")
