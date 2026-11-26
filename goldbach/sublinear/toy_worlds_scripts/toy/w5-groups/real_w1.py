#!/usr/bin/env python3
"""World 1 on the real tables, and the cover's own window for every j.
(a) j = 1, 2 (P < X, D < 0: no constraint).  Every class vector of the later primes occurs floor or ceil of K/T times in
    the window, so the best members are the coordinatewise best; the heap listing (w5lib.kbest_product) of the later
    tables is compared with the window's distinct class vectors sorted by score.
(b) j = 1..8: the best first-order score in the cover's own window (brute force over all K members), its mean, and
    the unconstrained optimum."""
import math, numpy as np, common as C, w5lib as L
M, X, N0 = C.M, C.X, C.N0; K = (X - 1 - N0) // M + 1
print(f"window of the cover: K = {K} members")
for j in (1, 2):
    js = C.later_primes(j); lt = C.later_tables(js); T = math.prod(js)
    k = np.arange(K, dtype=np.int64); idx = np.zeros(K, dtype=np.int64); tot = np.zeros(K, dtype=np.int64)
    for s in js:
        res = (N0 % s + k % s * (M % s)) % s; idx = idx * s + res; tot += lt[s][res]
    mult = np.bincount(idx, minlength=T)
    print(f"j = {j}: T = {T}, K/T = {K / T:.3f}; multiplicities of the {T} class vectors in the window: min {mult.min()}, max {mult.max()}")
    score_of_vec = np.zeros(T, dtype=np.int64); score_of_vec[idx] = tot
    srt = np.sort(-score_of_vec)                          # brute force: scores of all class vectors, best first
    kk = 5000 if j == 2 else T
    out, pushes = L.kbest_product([(-lt[s]).tolist() for s in js], kk)
    ok = [s for s, _ in out] == srt[:kk].tolist()
    print(f"   heap listing of the {kk} best class vectors = brute force over the window: {ok}; pushes per output {pushes / kk:.2f}; best hits {-out[0][0]} -> {C.n0 + out[0][0]} rows")
print("\n j   D        unconstrained   own window: best   mean hits   members at the best")
for j in range(1, 9):
    js = C.later_primes(j); lt = C.later_tables(js); T = math.prod(js)
    tot = np.zeros(K, dtype=np.int16)
    for s in js:
        pat = lt[s][(N0 % s + np.arange(s, dtype=np.int64) * (M % s)) % s].astype(np.int16); tot += np.resize(pat, K)
    G = sum(int(lt[s].max()) for s in js); D = math.log(M) + math.log(T) - math.log(X)
    print(f" {j}  {D:7.3f}   {C.n0 - G:6d}          {C.n0 - int(tot.max()):6d}          {tot.mean():6.2f}      {int((tot == tot.max()).sum())}")
