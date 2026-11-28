"""Question 2: the smallest instances in which pinning cannot reach the optimum, with every pinnable set allowed.

Instance: rows = odd primes below Q; moduli = the first k odd primes; candidates = even N in [Q, X), so that N - q > 0 for every row; only X >= 5 Q is tried.
score_T(N) = rows q with N - q divisible by no prime of T;  the full score is score at T = all k moduli.
A set T is pinnable when 2 prod T <= X: then every vector of classes of T occurs below X.  Its design value is
D_T = min score_T, its best cells are the classes modulo 2 prod T reaching D_T, and "pinning T plus a full scan"
finds the least full score over the members of those cells.
  OPT         least full score over all candidates;
  PINSCAN     least, over all pinnable T, of what pinning T plus a full scan finds   (PINSCAN >= OPT);
  PINMEAN     for the T that realises PINSCAN: the mean full score over the members of its best cells (pinning with
              no choice inside the window).
The script lists, for increasing X, the instances with PINSCAN > OPT (no pinnable set has a true optimum among the
members of its best cells), smallest first.
  python smallest.py QMAX XMAX"""
import itertools, math, sys
import numpy as np
PR = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
def instance(Q, k, X, detail=False):
    rows = [q for q in primes_upto(Q - 1) if q > 2]; n = len(rows); assert n <= 64
    Ns = np.arange(Q + (Q & 1), X, 2, dtype=np.int64); full = np.uint64((1 << n) - 1) if n < 64 else np.uint64(0xFFFFFFFFFFFFFFFF)
    struck = []
    for r in PR[:k]:
        m = np.zeros(r, dtype=np.uint64)
        for j, q in enumerate(rows): m[q % r] |= np.uint64(1) << np.uint64(j)
        struck.append(m[Ns % r])
    def score(T):
        acc = np.zeros(len(Ns), dtype=np.uint64)
        for i in T: acc |= struck[i]
        return np.bitwise_count(full & ~acc).astype(np.int64)
    fullscore = score(range(k)); OPT = int(fullscore.min())
    best = None
    for size in range(k, 0, -1):
        for T in itertools.combinations(range(k), size):
            P = 2 * math.prod(PR[i] for i in T)
            if P > X: continue
            if any(P * PR[i] <= X for i in range(k) if i not in T): continue          # not maximal
            sT = score(T); D = int(sT.min()); cells = sT == D
            scan = int(fullscore[cells].min()); mean = float(fullscore[cells].mean())
            rec = (scan, D, [PR[i] for i in T], X / P, int(cells.sum()), mean)
            if best is None or rec[0] < best[0] or (rec[0] == best[0] and rec[1] < best[1]): best = rec
    out = {"Q": Q, "rows": n, "k": k, "X": X, "OPT": OPT, "nopt": int((fullscore == OPT).sum()), "PINSCAN": best[0], "T": best[2], "D_T": best[1], "window": best[3], "members_best_cells": best[4], "PINMEAN": best[5]}
    if detail: out["optima"] = [int(x) for x in Ns[fullscore == OPT]]
    return out
if __name__ == "__main__":
    QMAX = int(sys.argv[1]); XMAX = int(sys.argv[2]); found = []
    print("Q (rows) | moduli | X | OPT (N reaching it) | PINSCAN | best pinnable set, its design value, window | PINMEAN")
    for Q in [q for q in (20, 30, 40, 50, 60, 80, 100, 130, 160, 200, 250, 300) if q <= QMAX]:
        for k in range(2, 9):
            M = 2
            seen = set()
            # every X = 2 * (product of some prefix) * w, and the products of other sets, up to XMAX: take all even X on a coarse grid of "interesting" values
            cands = set()
            for size in range(1, k + 1):
                for T in itertools.combinations(range(k), size):
                    P = 2 * math.prod(PR[i] for i in T)
                    for w in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16):
                        if P * w <= XMAX: cands.add(P * w)
            for X in sorted(cands):
                if X < 5 * Q: continue
                if 2 * math.prod(PR[:k]) <= X: continue                                  # nothing beyond the line
                r = instance(Q, k, X)
                if r["PINSCAN"] > r["OPT"]:
                    found.append(r)
    found.sort(key=lambda r: (r["X"], r["rows"], r["k"]))
    for r in found[:40]:
        print(f"{r['Q']} ({r['rows']}) | 3..{PR[r['k'] - 1]} | {r['X']:,d} | {r['OPT']} ({r['nopt']}) | {r['PINSCAN']} | {r['T']}, {r['D_T']}, {r['window']:.2f} | {r['PINMEAN']:.2f}")
    print(f"# {len(found)} instances with PINSCAN > OPT among those tried")
