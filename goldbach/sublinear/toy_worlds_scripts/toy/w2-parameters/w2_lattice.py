#!/usr/bin/env python3
"""World 2, average case: noisy polynomial interpolation (Naor-Pinkas) by the lattice of Bleichenbacher-Nguyen (2000),
run with LLL (python-flint) on random lists with one planted polynomial.

q prime, N of degree < n, m points, a list of ell values at each point containing N(x_i).  Unknown 0/1 vector delta
(one 1 per block).  N = sum_i (sum_j delta_ij y_ij) L_i(x), and deg N < n iff the coefficients of x^n..x^(m-1) vanish:
m - n linear conditions A delta = 0 (mod q).  The lattice {delta in Z^(m ell): A delta = 0 mod q} contains the target
(norm sqrt(m)); we add m-1 coordinates W (sum_j delta_0j - sum_j delta_ij) so that only vectors with equal block sums
stay short.  Success: a row of the LLL-reduced basis is +-(one 1 per block) and decodes to a consistent polynomial.

Parasites: a vector supported in one block with sum 0 and sum_j delta_j y_ij = 0 (mod q) is in the lattice and says
nothing about N.  By pigeonhole one with entries in {-1,0,1} exists in every block as soon as binom(ell, ell//2) > q.
"""
import sys, math, random, time
from flint import nmod_mat, fmpz_mat


def instance(q, n, m, ell, rng, planted=True):
    xs = list(range(1, m + 1))
    N = [rng.randrange(q) for _ in range(n)]
    ev = lambda x: sum(c * pow(x, k, q) for k, c in enumerate(N)) % q
    lists = []
    for x in xs:
        if planted:
            v = ev(x); oth = rng.sample([y for y in range(q) if y != v], ell - 1); L = [v] + oth
        else:
            L = rng.sample(range(q), ell)
        rng.shuffle(L); lists.append(L)
    return xs, N, lists


def attack(q, n, m, ell, xs, lists, W=None):
    W = W or 4 * m
    V = nmod_mat(m, m, [pow(x, k, q) for x in xs for k in range(m)], q)       # values = V coeffs
    Vi = V.inv()                                                                 # coeffs = Vi values
    r = m - n; dim = m * ell
    A = nmod_mat(r, dim, [int(Vi[n + c, i]) * lists[i][j] % q for c in range(r) for i in range(m) for j in range(ell)], q)
    R, rank = A.rref()
    assert rank == r
    piv = []
    for c in range(r):
        k = 0
        while int(R[c, k]) == 0:
            k += 1
        piv.append(k)
    free = [k for k in range(dim) if k not in piv]
    rows = []
    for c, pk in enumerate(piv):
        v = [0] * dim; v[pk] = q; rows.append(v)
    for f in free:
        v = [0] * dim; v[f] = 1
        for c, pk in enumerate(piv):
            v[pk] = (-int(R[c, f])) % q
            if v[pk] > q // 2:
                v[pk] -= q
        rows.append(v)
    ext = []
    for v in rows:
        s = [sum(v[i * ell:(i + 1) * ell]) for i in range(m)]
        ext.append(v + [W * (s[0] - s[i]) for i in range(1, m)])
    B = fmpz_mat(len(ext), dim + m - 1, [x for v in ext for x in v])
    Bl = B.lll()
    found = None; parasites = 0; shortest = None
    for k in range(Bl.nrows()):
        v = [int(Bl[k, c]) for c in range(dim)]
        tail = [int(Bl[k, c]) for c in range(dim, dim + m - 1)]
        nrm2 = sum(x * x for x in v) + sum(x * x for x in tail)
        if nrm2 and (shortest is None or nrm2 < shortest):
            shortest = nrm2
        blocks = [i for i in range(m) if any(v[i * ell:(i + 1) * ell])]
        if len(blocks) == 1 and not any(tail):
            parasites += 1
        for sgn in (1, -1):
            w = [sgn * x for x in v]
            if all(x in (0, 1) for x in w) and all(sum(w[i * ell:(i + 1) * ell]) == 1 for i in range(m)):
                found = [lists[i][w[i * ell:(i + 1) * ell].index(1)] for i in range(m)]
    return found, parasites, shortest, dim


def trial_set(q, n, m, ell, trials, rng, planted=True):
    ok = 0; par = []; sh = []; t0 = time.time()
    for _ in range(trials):
        xs, N, lists = instance(q, n, m, ell, rng, planted)
        found, parasites, shortest, dim = attack(q, n, m, ell, xs, lists)
        if found is not None:
            # check it is a consistent polynomial of degree < n (interpolate and verify)
            V = nmod_mat(m, m, [pow(x, k, q) for x in xs for k in range(m)], q)
            co = V.inv() * nmod_mat(m, 1, found, q)
            if all(int(co[k, 0]) == 0 for k in range(n, m)):
                ok += 1
        par.append(parasites); sh.append(shortest)
    lnE = n * math.log(q) + m * math.log(ell / q)
    print(f"q={q} n={n} m={m} ell={ell} (rho={ell / q:.4f}, lattice dim {m * ell}, planted={planted}): solved {ok}/{trials}; "
          f"single-block parasites in the reduced basis: mean {sum(par) / trials:.1f}; shortest reduced vector norm^2 "
          f"{min(sh)}..{max(sh)} (target {m}); binom(ell, ell//2) = {math.comb(ell, ell // 2)} {'>' if math.comb(ell, ell // 2) > q else '<='} q; "
          f"ln E(spurious consistent) = {lnE:.1f}; {(time.time() - t0) / trials:.1f}s each")
    sys.stdout.flush()


rng = random.Random(2000)
print("=== planted polynomial, sparse to dense lists ===")
for q in (257, 65537):
    for ell in (2, 3, 4, 5, 6, 8, 10, 12, 16):
        trial_set(q, 4, 14, ell, 8, rng)
print()
print("=== dense lists (constant fraction of the field), no planting needed: consistent polynomials are abundant ===")
trial_set(31, 4, 10, 15, 5, rng, planted=False)
trial_set(31, 4, 12, 15, 5, rng, planted=False)
trial_set(61, 4, 8, 30, 3, rng, planted=False)
