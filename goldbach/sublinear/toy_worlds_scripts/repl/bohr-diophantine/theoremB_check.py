#!/usr/bin/env python3
"""Theorem B in miniature, exhaustively: for EVERY bijection Phi of the window [0, K) onto a product A_1 x ... x A_n,
(every table score k -> f(k mod s) is a sum of functions of single coordinates)  <=>  (k mod s is a function of one coordinate),
and the moduli with that property have product <= K unless one coordinate is the whole window."""
import itertools, math, numpy as np
def check(K, shape, mods):
    cells = list(itertools.product(*[range(a) for a in shape])); assert len(cells) == K
    # design matrix of separable functions for a given assignment member -> cell
    sep_count = {s: 0 for s in mods}; func_count = {s: 0 for s in mods}; disagree = 0; total = 0; worst = 0
    onehots = []
    for i, a in enumerate(shape):
        M_ = np.zeros((K, a)); 
        for c, cell in enumerate(cells): M_[c, cell[i]] = 1
        onehots.append(M_)
    X = np.hstack(onehots); rk = np.linalg.matrix_rank(X)
    Pj = X @ np.linalg.pinv(X)                       # projector on separable functions of the cells
    for perm in itertools.permutations(range(K)):
        total += 1; prodsep = 1
        for s in mods:
            # member k sits in cell perm[k]; indicator of class c as a function of the cell
            sep = True
            for c in range(s):
                v = np.zeros(K)
                for k in range(c, K, s): v[perm[k]] = 1
                if np.abs(Pj @ v - v).max() > 1e-9: sep = False; break
            # is k mod s a function of one coordinate?
            fn = False
            for i in range(len(shape)):
                m = {}
                if all(m.setdefault(cells[perm[k]][i], k % s) == k % s for k in range(K)): fn = True; break
            sep_count[s] += sep; func_count[s] += fn; disagree += (sep != fn)
            if sep: prodsep *= s
        worst = max(worst, prodsep)
    return total, sep_count, func_count, disagree, worst
for K, shape, mods in ((6, (2, 3), (2, 3, 4, 5)), (8, (2, 4), (2, 3, 4, 5, 7)), (8, (2, 2, 2), (2, 3, 4, 5, 7)), (9, (3, 3), (2, 3, 4, 5, 7))):
    total, sc, fc, dis, worst = check(K, shape, mods)
    print(f"K = {K}, product {shape}: {total} bijections; separable for all tables, by modulus: {sc}; residue a function of one coordinate: {fc}; disagreements {dis}; largest product of pairwise coprime-or-not separable moduli over all bijections: {worst} (K = {K})")
