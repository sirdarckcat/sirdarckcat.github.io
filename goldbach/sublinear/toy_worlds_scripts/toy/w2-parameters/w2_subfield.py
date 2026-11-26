#!/usr/bin/env python3
"""World 2: lists that are F_p-subspaces.  (i) The Guruswami-Rudra example (STOC 2005, Theorem 1): the polynomials over
F_{q^m} of degree <= (q^m - 1)/(q - 1) taking values in F_q on all of F_{q^m} number exactly q^(2^m): counted here by
F_p-linear algebra and, for F_9, by brute force.  (ii) Affine lists at places of F_q[x] of several degrees: the
consistent N form an affine subspace, found by Gaussian elimination, and have the same number as random lists of the
same density give on average.
"""
import itertools, math, random
import numpy as np
from flint import nmod_poly, nmod_mat
from w2core import irreducibles, residue_codes, all_polys


class GF:
    """F_{p^r} = F_p[t]/(f): elements are integers 0..p^r-1 in base p; add/mul tables"""
    def __init__(self, p, modulus):
        self.p = p; self.r = len(modulus) - 1; self.size = p ** self.r
        f = nmod_poly(modulus, p)
        assert len(f.factor()[1]) == 1 and f.factor()[1][0][1] == 1
        dec = lambda x: [(x // p ** k) % p for k in range(self.r)]
        enc = lambda cs: sum(int(c) * p ** k for k, c in enumerate(cs))
        self.dec = dec; self.enc = enc
        self.mul = np.zeros((self.size, self.size), dtype=np.int64)
        self.add = np.zeros((self.size, self.size), dtype=np.int64)
        for a in range(self.size):
            for b in range(self.size):
                self.add[a, b] = enc([(x + y) % p for x, y in zip(dec(a), dec(b))])
                pr = (nmod_poly(dec(a), p) * nmod_poly(dec(b), p)) % f
                self.mul[a, b] = enc(list(pr.coeffs()))

    def power(self, a, k):
        r = 1
        for _ in range(k):
            r = int(self.mul[r, a])
        return r


def count_by_linear_algebra(F, sub_basis, n):
    """number of N = sum_k c_k z^k (k < n, c_k in F) with N(a) in span_{F_p}(sub_basis) for every a in F"""
    p, r = F.p, F.r
    S = nmod_mat(len(sub_basis), r, [x for b in sub_basis for x in F.dec(b)], p)
    # functionals vanishing on the subspace: left kernel of S^T, i.e. rows w with w . s = 0 for s in S
    Xk, nul = S.nullspace()                       # S x = 0 : x in F_p^r
    Pm = [[int(Xk[i, k]) for i in range(r)] for k in range(nul)]          # (r - dimS) functionals
    rows = []
    for a in range(F.size):
        for w in Pm:
            row = []
            for k in range(n):
                ak = F.power(a, k)
                for e in range(r):                 # coordinate e of c_k : c_k = sum_e c_{k,e} t^e
                    v = F.dec(int(F.mul[ak, p ** e]))
                    row.append(sum(x * y for x, y in zip(w, v)) % p)
            rows.append(row)
    A = nmod_mat(len(rows), n * r, [x for row in rows for x in row], p)
    return n * r - A.rank(), len(rows)


print("=== (i) subfield lists (Guruswami-Rudra 2005, Theorem 1): count = q^(2^m) ===")
cases = [("F_9 over F_3", GF(3, [1, 0, 1]), [1], 3, 2),
         ("F_27 over F_3", GF(3, [2, 2, 0, 1]), [1], 3, 3),
         ("F_25 over F_5", GF(5, [3, 0, 1]), [1], 5, 2),
         ("F_16 over F_4", GF(2, [1, 1, 0, 0, 1]), None, 4, 2)]
for name, F, sb, q, m in cases:
    if sb is None:                                  # F_4 inside F_16: the elements with x^4 = x
        f4 = [x for x in range(16) if F.power(x, 4) == x]
        sb = [x for x in f4 if x not in (0, 1)][:1] + [1]
    k = (q ** m - 1) // (q - 1)
    dim, neq = count_by_linear_algebra(F, sb, k + 1)
    Nall = F.size
    rand = (k + 1) * math.log(Nall) + Nall * math.log(q / Nall)
    print(f"{name}: degree <= {k} (n = {k + 1} coefficients, |F|^n = {Nall}^{k + 1}), lists = F_{q} at all {Nall} points "
          f"(density 1/{Nall // q}): consistent set is an F_{F.p}-space of dimension {dim} -> {F.p}^{dim} = {F.p ** dim}; "
          f"theorem: {q}^(2^{m}) = {q ** (2 ** m)}; random lists of that density: E = e^{rand:.2f} = {math.exp(rand):.3g}; "
          f"Johnson (points only) allows n - 1 < {Nall}/{q} = {Nall // q}; {neq} equations in {(k + 1) * F.r} unknowns")
# brute force for F_9
F = GF(3, [1, 0, 1]); cnt = 0
pw = [[F.power(a, k) for k in range(5)] for a in range(9)]
for co in itertools.product(range(9), repeat=5):
    good = True
    for a in range(9):
        v = 0
        for k in range(5):
            v = int(F.add[v, F.mul[co[k], pw[a][k]]])
        if v >= 3:
            good = False; break
    cnt += good
print(f"F_9 over F_3, brute force over 9^5 = 59049 polynomials: {cnt} take values in F_3 everywhere")

print()
print("=== (ii) affine lists at places of F_q[x] against random lists of the same density ===")
rng = random.Random(5)
for q, degs, n, codim in [(3, (2, 3), 12, 1), (3, (2, 3), 13, 1), (3, (3,), 10, 1), (2, (3, 4, 5), 13, 1), (2, (5,), 14, 2)]:
    places = [p for d in degs for p in irreducibles(q, d)]
    m = len(places)
    res = {"affine": [], "random": []}
    ranks = []
    for trial in range(20):
        ok_aff = np.ones(q ** n, dtype=bool); ok_rnd = np.ones(q ** n, dtype=bool)
        rows = []
        for pi in places:
            d = len(pi) - 1
            codes = residue_codes(q, n, pi)
            digits = np.stack([(codes // q ** k) % q for k in range(d)], axis=1)
            # a random affine subspace of codimension codim: {r : H r = b}, H of full rank
            while True:
                H = np.array([[rng.randrange(q) for _ in range(d)] for _ in range(codim)], dtype=np.int64)
                if nmod_mat(codim, d, [int(x) for x in H.reshape(-1)], q).rank() == codim:
                    break
            b = np.array([rng.randrange(q) for _ in range(codim)], dtype=np.int64)
            ok_aff &= (((digits @ H.T) - b) % q == 0).all(axis=1)
            tab = np.zeros(q ** d, dtype=bool); tab[rng.sample(range(q ** d), q ** (d - codim))] = True
            ok_rnd &= tab[codes]
            # the linear system on the coefficients of N: H R^T c = b, R[k] = x^k mod pi
            R = np.zeros((n, d), dtype=np.int64)
            P = nmod_poly(pi, q)
            for k in range(n):
                cs = [int(c) for c in (nmod_poly([0] * k + [1], q) % P).coeffs()]
                R[k, :len(cs)] = cs
            rows.append((H @ R.T) % q)
        Asys = np.concatenate(rows, axis=0)
        ranks.append(nmod_mat(Asys.shape[0], n, [int(x) for x in Asys.reshape(-1)], q).rank())
        res["affine"].append(int(ok_aff.sum())); res["random"].append(int(ok_rnd.sum()))
    E = q ** n * float(q) ** (-codim * m)
    aff = np.array(res["affine"]); rnd = np.array(res["random"])
    print(f"q={q}, places of degree {degs} (m={m}), lists of density q^-{codim}, n={n}: E = q^(n - {codim} m) = {E:.3g}; "
          f"random lists: mean count {rnd.mean():.2f} (min {rnd.min()}, max {rnd.max()}); affine lists: counts "
          f"{sorted(set(aff.tolist()))} = q^(n - rank), rank of the {codim * m} equations {min(ranks)}..{max(ranks)} "
          f"(a count of 0 means an inconsistent system); Gaussian elimination on {codim * m} x {n} against q^n = {q ** n}")
