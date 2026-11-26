#!/usr/bin/env python3
"""(a) continued: the multiple-choice closest-vector formulation and LLL (Kannan embedding), on the real tables.
Unknowns y_{j,c} in {0,1}, at most one per prime j (the reference class c0_j is chosen when none is set);
k = A0 + sum y_{j,c} (A_{j,c} - A_{j,c0}) mod P_J must lie in [0, K).   Lattice rows:
    (lam e_{j,c} | 2 (A_{j,c} - A_{j,c0}) mod 2P | 0),   (0 | 2P | 0),   (0 | 2 A0 - K | lam)
a member in all lists is the vector +-(lam y | 2k - K | lam), of norm <= lam sqrt(J + 2) with lam = K.
Test 1 (planted): J = 12 real later primes, lists = the best l - 1 classes plus the class of one real member k*; does LLL return k*?
Test 2 (real lists, nothing planted): lists = best rho of the classes; does LLL return any of the members that the scan finds?"""
import sys, math, time, numpy as np, random
from flint import fmpz_mat
from base import *
from lists_scan import lists, scan, LATER
def lattice(Ls):
    mods = [s for s, _ in Ls]; P = math.prod(mods)
    E = [(P // s) * pow(P // s, -1, s) % P for s in mods]
    idx = []; A0 = 0
    for j, (s, G) in enumerate(Ls):
        c0 = int(G[0]); A0 += c0 * E[j]
        for c in G[1:]: idx.append((j, int(c), (int(c) - c0) * E[j] % P))
    n = len(idx); lam = K
    rows = []
    for i, (j, c, a) in enumerate(idx):
        v = [0] * (n + 2); v[i] = lam; v[n] = 2 * a % (2 * P); rows.append(v)
    v = [0] * (n + 2); v[n] = 2 * P; rows.append(v)
    v = [0] * (n + 2); v[n] = (2 * (A0 % P) - K) % (2 * P); v[n + 1] = lam; rows.append(v)
    return rows, idx, P, lam
def solutions_in_basis(B, idx, Ls, lam):
    n = len(idx); found = set(); norms = []
    for i in range(B.nrows()):
        v = [int(B[i, t]) for t in range(n + 2)]
        norms.append(math.sqrt(sum(x * x for x in v)) / lam)
        if abs(v[n + 1]) != lam: continue
        sg = 1 if v[n + 1] == lam else -1
        y = [sg * x for x in v[:n]]
        if any(x not in (0, lam) for x in y): continue
        if abs(v[n]) > K: continue
        cls = {j: int(G[0]) for j, (s, G) in enumerate(Ls)}; per = {}
        for (j, c, a), x in zip(idx, y):
            if x: per[j] = per.get(j, 0) + 1; cls[j] = c
        if any(t > 1 for t in per.values()): continue
        k = (sg * v[n] + K) // 2
        if all(k % s == cls[j] for j, (s, G) in enumerate(Ls)) and 0 <= k < K: found.add(k)
    return found, sorted(norms)
def run(Ls, label, truth):
    rows, idx, P, lam = lattice(Ls); n = len(idx)
    D = math.log(P / K); dens = sum(math.log(len(G)) for _, G in Ls) / D
    t = time.time(); B = fmpz_mat(rows).lll(delta=0.99, eta=0.51); dt = time.time() - t
    found, norms = solutions_in_basis(B, idx, Ls, lam)
    J = len(Ls)
    print(f"{label}: dimension {n + 2}; density {dens:.2f}; members in all lists (scan) {len(truth)}; LLL {dt:.1f} s; "
          f"basis vectors that are such members: {len(found)} (correct: {found <= truth}); basis norms/lam min {norms[0]:.2f} median {norms[len(norms) // 2]:.2f} max {norms[-1]:.2f}; a member has norm <= {math.sqrt(J + 2):.2f}", flush=True)
    return len(found)
if __name__ == "__main__":
    random.seed(1); rng = np.random.default_rng(1)
    print("TEST 1: planted member, J = 12 later primes (D = 57.93), lists of l classes = best l - 1 classes + the class of k*; 5 trials each")
    for l in (2, 4, 8, 12, 16, 24, 32, 48):
        ok = 0; tr = 5 if l <= 24 else 2
        for trial in range(tr):
            kstar = int(rng.integers(0, K)); Ls = []
            for s in LATER[:12]:
                f, g = tables(s); order = [int(c) for c in np.argsort(-g, kind="stable") if c != kstar % s][:l - 1]
                G = np.array(sorted(order + [kstar % s])); Ls.append((s, G))
            # truth: by construction k* ; other members in all lists are expected K * prod(l/s) << 1
            ok += run(Ls, f"  l = {l} trial {trial}", {kstar})
        print(f"l = {l}: density {12 * math.log(l) / 57.93:.2f}; planted member recovered in {ok} of {tr} trials")
    print("\nTEST 2: real lists, nothing planted")
    for J, rho in ((4, 0.05), (6, 0.05), (6, 0.10), (8, 0.10)):
        L = lists(J, rho); tot, _ = scan(L); truth = set(int(k) for k in np.nonzero(tot == J)[0])
        if sum(len(G) for _, G, _, _ in L) > 330 and J == 8:
            pass
        run([(s, G) for s, G, _, _ in L], f"J = {J} rho = {rho}", truth)
