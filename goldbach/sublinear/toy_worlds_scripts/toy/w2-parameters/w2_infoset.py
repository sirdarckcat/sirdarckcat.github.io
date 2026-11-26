#!/usr/bin/env python3
"""World 2: what is output-priced with generic lists: an information set, and a merge of two halves of it.

RS code over F_q (q prime), N of degree < n, lists L_a (size ell) at every point a of F_q.
(1) brute force over the q^n polynomials;
(2) information set: the ell^n combinations of list values at n points, one Lagrange interpolation each;
(3) meet in the middle on the information set with j extra check points: N = N1 + N2 (N1 carries the values on the first
    half of the set, N2 on the second), N(c) = N1(c) + N2(c) in L_c is a join on the key (y_c - N2(c))_c.
The three must return the same set.  Operation counts are candidates touched.
"""
import sys, math, random, itertools, time
import numpy as np
from flint import nmod_mat


def run(q, n, ell, m, j, seed):
    rng = random.Random(seed)
    pts = list(range(m))
    lists = [sorted(rng.sample(range(q), ell)) for _ in pts]
    tabs = np.zeros((m, q), dtype=bool)
    for i, L in enumerate(lists):
        tabs[i, L] = True
    # (1) brute force, chunked
    t0 = time.time(); brute = []
    step = 2_000_000
    for lo in range(0, q ** n, step):
        idx = np.arange(lo, min(lo + step, q ** n), dtype=np.int64)
        co = [(idx // q ** k) % q for k in range(n)]
        ok = np.ones(len(idx), dtype=bool)
        for i, a in enumerate(pts):
            v = np.zeros(len(idx), dtype=np.int64)
            for k in range(n - 1, -1, -1):
                v = (v * a + co[k]) % q
            ok &= tabs[i, v]
        brute.extend(idx[ok].tolist())
    t_brute = time.time() - t0
    # Lagrange data on the information set I = first n points
    V = nmod_mat(n, n, [pow(a, k, q) for a in pts[:n] for k in range(n)], q)      # values = V coeffs
    Vi = V.inv()
    Vinv = np.array([[int(Vi[r, c]) for c in range(n)] for r in range(n)], dtype=np.int64)   # coeffs = Vinv values
    W = np.array([[pow(a, k, q) for k in range(n)] for a in pts], dtype=np.int64)            # evaluation at all points
    EV = (W @ Vinv) % q                                                                        # N(a) = EV[a] . values on I
    # (2) information set
    t0 = time.time()
    grids = np.array(list(itertools.product(*lists[:n])), dtype=np.int64)                     # ell^n x n
    ok = np.ones(len(grids), dtype=bool)
    for i in range(n, m):
        ok &= tabs[i, (grids @ EV[i]) % q]
    sols = grids[ok]
    co = (sols @ Vinv.T) % q
    info = sorted(int(sum(int(c) * q ** k for k, c in enumerate(row))) for row in co)
    t_info = time.time() - t0
    # (3) meet in the middle
    t0 = time.time()
    h = n // 2
    left = np.array(list(itertools.product(*lists[:h])), dtype=np.int64)
    right = np.array(list(itertools.product(*lists[h:n])), dtype=np.int64)
    chk = list(range(n, n + j))
    lkey = np.zeros(len(left), dtype=np.int64); rpart = []
    for t, c in enumerate(chk):
        lkey += ((left @ EV[c, :h]) % q) * q ** t
        rpart.append((right @ EV[c, h:n]) % q)
    table = {}
    for r, k in enumerate(lkey.tolist()):
        table.setdefault(k, []).append(r)
    lookups = 0; matches = []
    for ys in itertools.product(*[lists[c] for c in chk]):
        key = np.zeros(len(right), dtype=np.int64)
        for t in range(j):
            key += ((ys[t] - rpart[t]) % q) * q ** t
        lookups += len(right)
        for r2, k in enumerate(key.tolist()):
            for r1 in table.get(k, ()):
                matches.append((r1, r2))
    mm = np.array(matches, dtype=np.int64).reshape(-1, 2)
    vals = np.concatenate([left[mm[:, 0]], right[mm[:, 1]]], axis=1)
    ok = np.ones(len(vals), dtype=bool)
    for i in range(n + j, m):
        ok &= tabs[i, (vals @ EV[i]) % q]
    co = (vals[ok] @ Vinv.T) % q
    mitm = sorted(int(sum(int(c) * q ** k for k, c in enumerate(row))) for row in co)
    t_mitm = time.time() - t0
    rho = ell / q
    E = q ** n * rho ** m
    assert sorted(brute) == info == mitm, (len(brute), len(info), len(mitm))
    ops_mitm = len(left) + lookups + len(matches)
    print(f"q={q} n={n} ell={ell} (rho={rho:.3f}) m={m} j={j}: consistent N = {len(brute)} (E = {E:.1f}); all three methods agree")
    print(f"   brute force: {q ** n} candidates ({t_brute:.1f}s) -> {q ** n / max(1, len(brute)):.3g} per output; predicted rho^-m = {rho ** -m:.3g}")
    print(f"   information set: {ell ** n} candidates ({t_info:.1f}s) -> {ell ** n / max(1, len(brute)):.3g} per output; predicted rho^-(m-n) = {rho ** -(m - n):.3g}")
    print(f"   meet in the middle: {len(left)} + {lookups} lookups + {len(matches)} matches = {ops_mitm} ({t_mitm:.1f}s) -> "
          f"{ops_mitm / max(1, len(brute)):.3g} per output; predicted matches ell^n rho^j = {ell ** n * rho ** j:.0f}")
    sys.stdout.flush()


run(13, 5, 6, 13, 1, 1)
run(17, 6, 8, 17, 2, 2)
run(17, 6, 8, 12, 2, 3)
run(17, 6, 8, 8, 2, 4)
run(19, 6, 9, 19, 2, 5)
run(23, 6, 11, 23, 2, 6)
print()
print("cost per output member, as a function of the number m of scoring places (n and rho fixed): rho^-(m - n) for the")
print("information set and about rho^-(m - n - j), j <= (n/2) log_q(ell), for the merge: exponential in m - n in both.")
