#!/usr/bin/env python3
"""t4: Theorem A at work.  Lists that are arithmetic progressions of classes at m later primes, window k < K.
Solutions <-> points of the lattice L = {(k, e_1 k - s_1 j_1, ..., e_m k - s_m j_m)} (e_i = 1/d_i mod s_i) in the box
o + [0,K) x prod [0,L_i), o = (0, e_i a_i).  For a basis b_1..b_n: w+_j = sum_i max(b_i[j],0), w-_j = sum_i max(-b_i[j],0),
tau_j = (w+_j + w-_j)/l_j.  Theorem A: E prod(1-tau_j) <= Z <= E prod(1+tau_j), E = K prod(L_i/s_i); the breadth-first search
over the lattice points x with x_j - o_j in [-w+_j, l_j + w-_j], by the steps +-b_i, from the corner of the tile of the centre,
visits at most E prod(1+2tau_j) points and meets every solution.
Part 1: the real window (K = 21,378,978), the real later primes, random progressions; every count checked by brute force.
Part 2: the room a certificate needs: for n = m+1 coordinates, the least ln(E)/n at which the reduced basis has
        prod(1+2tau_j)/prod(1-tau_j) <= e (cost at most e * 2n neighbour evaluations per solution)."""
import math, sys, random, numpy as np, flint
from collections import deque
from common import *
cov, rows = load(); N0, M, K0 = window(cov); LPall = later_primes(464, 5000)

def reduced_basis(sl, el, ell):
    n = len(sl) + 1; SC = max(ell) << 40; w = [SC // l for l in ell]
    G = [[0] * n for _ in range(n)]; G[0][0] = 1
    for i, (s, e) in enumerate(zip(sl, el)): G[0][i + 1] = e; G[i + 1][i + 1] = s
    A = flint.fmpz_mat([[G[i][j] * w[j] for j in range(n)] for i in range(n)]).lll()
    return [[int(A[i, j]) // w[j] for j in range(n)] for i in range(n)]

def taus(B, ell):
    n = len(B); wp = [sum(max(B[i][j], 0) for i in range(n)) for j in range(n)]; wm = [sum(max(-B[i][j], 0) for i in range(n)) for j in range(n)]
    return wp, wm, [(wp[j] + wm[j]) / ell[j] for j in range(n)]

def enumerate_box(sl, lists, K, limit=1_500_000):
    """lists: (a, d, L) per prime.  returns dict with E, taus, Z, visited, sols (sorted k)"""
    el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]; ell = [K] + [L for (a, d, L) in lists]
    o = [0] + [(e * a) % s for s, e, (a, d, L) in zip(sl, el, lists)]; n = len(ell)
    B = reduced_basis(sl, el, ell); wp, wm, tau = taus(B, ell)
    E = K * math.prod(L / s for s, (a, d, L) in zip(sl, lists))
    # start: corner of the tile that contains the centre of the box
    Bq = flint.fmpq_mat(flint.fmpz_mat(B)); y = flint.fmpq_mat([[flint.fmpq(2 * o[j] + ell[j], 2) for j in range(n)]])
    tc = y * Bq.inv(); fl = [int(tc[0, i].p // tc[0, i].q) for i in range(n)]
    x0 = tuple(sum(fl[i] * B[i][j] for i in range(n)) for j in range(n))
    lo = [o[j] - wp[j] for j in range(n)]; hi = [o[j] + ell[j] + wm[j] for j in range(n)]
    inW = lambda x: all(lo[j] <= x[j] <= hi[j] for j in range(n))
    assert inW(x0)
    seen = {x0}; dq = deque([x0]); sols = []
    while dq:
        x = dq.popleft()
        if all(o[j] <= x[j] < o[j] + ell[j] for j in range(n)): sols.append(x[0])
        for b in B:
            for sg in (1, -1):
                z = tuple(x[j] + sg * b[j] for j in range(n))
                if z not in seen and inW(z):
                    seen.add(z); dq.append(z)
        if len(seen) > limit: return dict(E=E, tau=tau, Z=None, visited=len(seen), sols=None)
    return dict(E=E, tau=tau, Z=len(sols), visited=len(seen), sols=sorted(sols))

def brute(sl, lists, K):
    ok = np.ones(K, dtype=bool); k = np.arange(K, dtype=np.int64)
    for s, (a, d, L) in zip(sl, lists):
        e = pow(d, -1, s); ok &= ((e * (k - a)) % s) < L
    return np.nonzero(ok)[0]

if __name__ == "__main__":
    random.seed(5); PART = sys.argv[1] if len(sys.argv) > 1 else "12"
    if "1" in PART:
        print(f"Part 1. real window K = {K0} (ln K = {math.log(K0):.2f}); primes 467, 479, ...; lists: random progressions (a, d, L = rho s)")
        print("   m   rho    ln(P/K)   KL=sum ln(1/rho)      E      prod(1-tau)E   Z (search)  Z (brute)  prod(1+tau)E   visited  bound prod(1+2tau)E  tau max  visited/Z")
        for m, f in ((1, 40), (2, 30), (3, 8), (3, 20), (4, 4), (4, 8), (5, 3), (5, 4), (6, 2), (6, 3), (8, 2), (10, 2), (12, 1.5), (16, 1.3)):
            sl = LPall[:m]; lists = [(random.randrange(s), random.randrange(1, s), int(round(s / f))) for s in sl]
            r = enumerate_box(sl, lists, K0); bz = brute(sl, lists, K0)
            t = r["tau"]; E = r["E"]; lowb = E * math.prod(max(0, 1 - x) for x in t); upb = E * math.prod(1 + x for x in t); vb = E * math.prod(1 + 2 * x for x in t)
            same = (r["sols"] is not None) and (len(bz) == r["Z"]) and all(int(a) == b for a, b in zip(bz, r["sols"]))
            KL = sum(math.log(s / L) for s, (a, d, L) in zip(sl, lists))
            print(f"  {m:2d}  1/{f:<4}  {math.log(math.prod(sl) / K0):7.2f}   {KL:6.2f}          {E:10.1f}  {lowb:10.1f}  {str(r['Z']):>9}  {len(bz):9d}  {upb:12.1f}  {r['visited']:8d}  {vb:14.1f}   {max(t):6.3f}"
                  f"  {(r['visited'] / r['Z'] if r['Z'] else float('nan')):8.2f}   {'identical sets' if same else 'MISMATCH or limit'}")
    if "2" in PART:
        random.seed(6)
        print("Part 2. the room a certificate needs.  n = m + 1 coordinates, primes from 467, random progressions of density 1/2,")
        print("        K = E 2^m; least c = ln(E)/n (step 0.05) with prod(1+2tau_j)/prod(1-tau_j) <= e for the LLL-reduced basis (median of 5 draws)")
        print("    n    c = ln E / n     ln n     Hadamard floor ln(1/geometric mean tau) at that c")
        for n in (2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 30, 40):
            m = n - 1; sl = LPall[:m]; cs = []; hs = []
            for rep in range(5):
                lists = [(random.randrange(s), random.randrange(1, s), s // 2) for s in sl]
                c = 0.5
                while True:
                    E = math.exp(c * n); K = int(E * math.prod(s / L for s, (a, d, L) in zip(sl, lists)))
                    el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]; ell = [K] + [L for (a, d, L) in lists]
                    B = reduced_basis(sl, el, ell); wp, wm, tau = taus(B, ell)
                    if max(tau) < 1 and math.prod(1 + 2 * x for x in tau) / math.prod(1 - x for x in tau) <= math.e: break
                    c += 0.05
                cs.append(c); hs.append(-sum(math.log(x) for x in tau) / n)
            print(f"   {n:2d}      {np.median(cs):5.2f}        {math.log(n):5.2f}     {np.median(hs):5.2f}")
