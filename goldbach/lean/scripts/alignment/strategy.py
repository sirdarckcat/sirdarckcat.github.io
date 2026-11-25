"""Question about strategies: how many windows must be looked at to find the optimum?

Instance as in tiny.c: rows = odd primes below Q, moduli = first odd primes, candidates = even N < X = w M,
M = 2 p_1 ... p_l (the line), b primes beyond the line.  A cell is a class of N modulo M; its w members are its window.

The game.  Free: everything that depends on the cover alone, i.e. for every cell c the set R_c of rows it leaves.
Costly: looking at a window, i.e. the classes of its members modulo the later primes (one unit per cell).  A procedure
picks cells one at a time from what is free and what it has seen.  From R_c alone one can compute, for a member of c
whose later classes were uniform and independent, the exact law of its score (by enumerating the class vectors of the
later primes); in particular
   LB(c)   the least score any class vector of the later primes gives: no member of c can do better;
   P_c(v)  the chance that at least one of w such members has score <= v.
Orders compared, by the number of cells looked at before the first optimal member is seen (ties: best and worst case):
   cover first     increasing |R_c|;
   bound first     increasing LB(c);
   chance first    decreasing P_c(OPT), the chance of holding an optimum (hindsight on the value OPT only);
and the certificate: the cells with LB(c) < OPT, which every procedure that proves optimality from free information
must look at (nothing free excludes them), against the number of cells.
  python strategy.py Q LINE_INDEX W B"""
import itertools, math, sys
import numpy as np
PR = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.int64)
def study(Q, lidx, w, b, verbose=True):
    rows = [q for q in primes_upto(Q - 1) if q > 2]; n = len(rows); Wd = (n + 63) // 64
    M = 2 * math.prod(PR[:lidx]); X = M * w; later = PR[lidx:lidx + b]; ncell = M // 2
    def mask(r):
        m = np.zeros((r, Wd), dtype=np.uint64)
        for j, q in enumerate(rows): m[q % r, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
        return m
    N0 = np.arange(0, M, 2, dtype=np.int64)                      # one representative per cell
    left = np.zeros((ncell, Wd), dtype=np.uint64)
    for j in range(n): left[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    for r in PR[:lidx]: left &= ~mask(r)[N0 % r]
    L = pc(left); lm = [mask(s) for s in later]
    # actual members
    best_actual = np.full(ncell, 10 ** 9, dtype=np.int64)
    for k in range(w):
        Nk = N0 + k * M; cur = left.copy()
        for s, m in zip(later, lm): cur &= ~m[Nk % s]
        best_actual = np.minimum(best_actual, pc(cur))
    OPT = int(best_actual.min()); has_opt = best_actual == OPT
    # law of the score of a member with uniform later classes, per cell: enumerate the class vectors
    tot = math.prod(later); hist = np.zeros((ncell, n + 2), dtype=np.float64)
    for combo in itertools.product(*[range(s) for s in later]):
        cur = left.copy()
        for a, m in zip(combo, lm): cur &= ~m[a]
        np.add.at(hist, (np.arange(ncell), pc(cur)), 1.0)
    hist /= tot; cdf = np.cumsum(hist, axis=1)
    LB = (hist > 0).argmax(axis=1)
    Pc = 1 - (1 - cdf[:, OPT]) ** w
    def rank(key):                                                # cells strictly before the first optimal cell: best and worst case of ties
        kopt = key[has_opt].min(); return int((key < kopt).sum()), int((key <= kopt).sum()) - 1
    cf = rank(L); bf = rank(LB); ch = rank(-Pc); must = int((LB < OPT).sum())
    out = {"Q": Q, "line": PR[lidx - 1], "w": w, "b": b, "cells": ncell, "OPT": OPT, "optcells": int(has_opt.sum()), "cover_first": cf, "bound_first": bf, "chance_first": ch,
           "must": must, "Dl": int(L.min()), "Lopt": sorted(set(int(x) for x in L[has_opt])), "expected_opt_cells": float(Pc.sum())}
    if verbose:
        print(f"Q={Q} line={PR[lidx - 1]} window={w} later primes {later}: {ncell:,d} cells; OPT {OPT} in {out['optcells']} cell(s) (rows left by their covers {out['Lopt']}, best cover {out['Dl']}); "
              f"cells looked at before the first optimum: cover first {cf[0]:,d}..{cf[1]:,d}; bound first {bf[0]:,d}..{bf[1]:,d}; chance first {ch[0]:,d}..{ch[1]:,d}; "
              f"cells no free bound excludes (LB < OPT): {must:,d} = {must / ncell:.1%} of all; expected number of cells holding a member <= OPT under uniform later classes: {out['expected_opt_cells']:.2f}", flush=True)
    return out
if __name__ == "__main__":
    if len(sys.argv) > 4:
        study(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        study(160, 3, 4, 2)                                       # the smallest instance (target 160, X = 840)
        for Q, lidx, w in ((300, 4, 2), (500, 4, 2), (1000, 4, 2), (1000, 4, 8), (300, 5, 2), (500, 5, 2), (1000, 5, 2), (1000, 5, 8)):
            for b in (1, 2, 3):
                if math.prod(PR[lidx:lidx + b]) * math.prod(PR[:lidx]) > 6e8: continue
                study(Q, lidx, w, b)
