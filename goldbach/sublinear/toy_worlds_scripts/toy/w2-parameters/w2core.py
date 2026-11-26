#!/usr/bin/env python3
"""World 2 (linear coupling) core: F_q[x] (q prime), N of degree < n, places = monic irreducibles pi of degree d,
lists L_pi inside F_q[x]/pi.  Brute-force enumeration of the consistent N, and the weighted interpolation step
(Guruswami-Sudan / Koetter-Vardy / ideal-code form) with exact linear algebra over F_q (python-flint).

Conventions.  A polynomial of degree < n is a coefficient vector (c_0..c_{n-1}), encoded as the integer
sum c_k q^k.  A residue modulo pi (degree d) is encoded the same way with d digits.
"""
import itertools, math, random
import numpy as np
from flint import nmod_poly, nmod_mat


def irreducibles(q, d):
    """all monic irreducible polynomials of degree d over F_q (q prime), as coefficient lists low..high"""
    out = []
    for tail in itertools.product(range(q), repeat=d):
        f = nmod_poly(list(tail) + [1], q)
        fac = f.factor()[1]
        if len(fac) == 1 and fac[0][1] == 1:
            out.append(list(tail) + [1])
    return out


def all_polys(q, n):
    """array (q^n, n) of all coefficient vectors; row index = encoding"""
    idx = np.arange(q ** n, dtype=np.int64)
    return np.stack([(idx // q ** k) % q for k in range(n)], axis=1)


def residue_codes(q, n, pi):
    """for every N of degree < n: code of N mod pi (array of length q^n)"""
    d = len(pi) - 1
    P = nmod_poly(pi, q)
    R = np.zeros((n, d), dtype=np.int64)
    for k in range(n):
        r = nmod_poly([0] * k + [1], q) % P
        cs = [int(c) for c in r.coeffs()]
        R[k, :len(cs)] = cs
    C = all_polys(q, n)
    res = (C @ R) % q
    return res @ (q ** np.arange(d, dtype=np.int64))


def code_to_poly(code, q, d):
    return [(code // q ** k) % q for k in range(d)]


def poly_mod_code(Ncoeffs, q, pi):
    d = len(pi) - 1
    r = nmod_poly(list(Ncoeffs), q) % nmod_poly(pi, q)
    cs = [int(c) for c in r.coeffs()]
    return sum(c * q ** k for k, c in enumerate(cs))


def random_lists(q, places, sizes, rng, planted=None):
    """independent uniformly random lists of the given sizes; with planted=N (coefficients) the class of N is forced in"""
    L = []
    for pi, l in zip(places, sizes):
        d = len(pi) - 1
        M = q ** d
        if planted is None:
            L.append(sorted(rng.sample(range(M), l)))
        else:
            c = poly_mod_code(planted, q, pi)
            others = rng.sample([x for x in range(M) if x != c], l - 1)
            L.append(sorted([c] + others))
    return L


def consistent(q, n, places, lists):
    """brute force: codes of all N of degree < n with N mod pi in L_pi for every place; also the agreement count of every N"""
    agree = np.zeros(q ** n, dtype=np.int32)
    ok = np.ones(q ** n, dtype=bool)
    for pi, L in zip(places, lists):
        d = len(pi) - 1
        tab = np.zeros(q ** d, dtype=bool)
        tab[L] = True
        hit = tab[residue_codes(q, n, pi)]
        ok &= hit
        agree += hit
    return np.nonzero(ok)[0], agree


def monomials(n, D):
    """(a, b) with a + (n-1) b < D : the monomials x^a y^b of (1, n-1)-weighted degree < D"""
    out = []
    b = 0
    while (n - 1) * b < D:
        for a in range(D - (n - 1) * b):
            out.append((a, b))
        b += 1
    return out


def count_monomials(n, D):
    if D <= 0:
        return 0
    J = (D - 1) // (n - 1)
    return (J + 1) * D - (n - 1) * J * (J + 1) // 2


def n_constraints(places, lists, mult):
    """sum over (place, class) of d s(s+1)/2 ; mult[i] is an int (same for the whole list) or a dict class->s"""
    tot = 0
    for i, (pi, L) in enumerate(zip(places, lists)):
        d = len(pi) - 1
        for c in L:
            s = mult[i][c] if isinstance(mult[i], dict) else mult[i]
            tot += d * s * (s + 1) // 2
    return tot


def interpolation_matrix(q, n, D, places, lists, mult):
    """rows: the F_q-linear conditions "Q in (pi, y - c)^s" for every listed class c of every place;
    columns: the monomials of weighted degree < D.  Condition: with Q(x, c + z) = sum_j Qj(x) z^j,
    pi^(s-j) divides Qj for j < s; Qj = sum_{a,b} Q_ab binom(b,j) c^(b-j) x^a."""
    mons = monomials(n, D)
    bmax = max(b for _, b in mons)
    amax = [0] * (bmax + 1)
    for a, b in mons:
        amax[b] = max(amax[b], a + 1)
    col = {m: k for k, m in enumerate(mons)}
    rows = []
    X = nmod_poly([0, 1], q)
    for i, (pi, L) in enumerate(zip(places, lists)):
        d = len(pi) - 1
        P = nmod_poly(pi, q)
        for c in L:
            s = mult[i][c] if isinstance(mult[i], dict) else mult[i]
            if s == 0:
                continue
            cp = nmod_poly(code_to_poly(c, q, d), q)
            Ps = P ** s
            cpow = [nmod_poly([1], q)]
            for _ in range(bmax):
                cpow.append((cpow[-1] * cp) % Ps)
            for j in range(s):
                Mj = P ** (s - j)
                dj = d * (s - j)
                block = np.zeros((dj, len(mons)), dtype=np.int64)
                for b in range(j, bmax + 1):
                    binom = math.comb(b, j) % q
                    if binom == 0:
                        continue
                    g = (cpow[b - j] * binom) % Mj
                    for a in range(amax[b]):
                        cs = g.coeffs()
                        if cs:
                            block[:len(cs), col[(a, b)]] = [int(t) for t in cs]
                        g = (g * X) % Mj
                rows.append(block)
    A = np.concatenate(rows, axis=0) if rows else np.zeros((0, len(mons)), dtype=np.int64)
    return A, mons


def kernel(q, A):
    """rank and a basis of the right kernel over F_q (list of coefficient vectors)"""
    r, c = A.shape
    M = nmod_mat(r, c, [int(t) for t in A.reshape(-1)], q)
    Xk, nullity = M.nullspace()
    basis = []
    for k in range(nullity):
        basis.append([int(Xk[i, k]) for i in range(c)])
    return c - nullity, basis


def eval_at(q, mons, vec, Ncoeffs):
    """Q(x, N(x)) as an nmod_poly"""
    N = nmod_poly(list(Ncoeffs), q)
    bmax = max(b for _, b in mons)
    Qb = [[0] * 1 for _ in range(bmax + 1)]
    polys = [dict() for _ in range(bmax + 1)]
    for (a, b), v in zip(mons, vec):
        if v:
            polys[b][a] = v
    res = nmod_poly([0], q)
    for b in range(bmax, -1, -1):
        co = [0] * (max(polys[b]) + 1) if polys[b] else [0]
        for a, v in polys[b].items():
            co[a] = v
        res = res * N + nmod_poly(co, q)
    return res


def y_roots(q, n, mons, vec):
    """brute force: all N of degree < n with Q(x, N(x)) = 0"""
    out = []
    for code in range(q ** n):
        if eval_at(q, mons, vec, code_to_poly(code, q, n)).is_zero():
            out.append(code)
    return out
