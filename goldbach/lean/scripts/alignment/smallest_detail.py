"""The smallest instance of smallest.py in detail, and the least X with PINSCAN > OPT for each target Q."""
import itertools, math, sys
import numpy as np
import smallest as sm
PR = sm.PR
def describe(Q, k, X):
    rows = [q for q in sm.primes_upto(Q - 1) if q > 2]; n = len(rows)
    Ns = list(range(Q + (Q & 1), X, 2))
    def left(N, T): return [q for q in rows if all((N - q) % PR[i] for i in T)]
    full = {N: left(N, range(k)) for N in Ns}; OPT = min(len(v) for v in full.values())
    print(f"instance: rows = the {n} odd primes below {Q}; moduli {PR[:k]}; candidates = even N in [{Ns[0]}, {X}) ({len(Ns)} of them)")
    print(f"true optimum: {OPT} rows left, at N = {[N for N in Ns if len(full[N]) == OPT]}")
    for N in [N for N in Ns if len(full[N]) == OPT]:
        print(f"  N = {N}: classes {[(PR[i], N % PR[i]) for i in range(k)]}; rows struck by each modulus alone {[sum(1 for q in rows if (N - q) % PR[i] == 0) for i in range(k)]}; rows left {full[N]}")
    print("pinnable sets (2 prod T <= X, maximal): design value, best cells, what a full scan of them finds")
    for size in range(k, 0, -1):
        for T in itertools.combinations(range(k), size):
            P = 2 * math.prod(PR[i] for i in T)
            if P > X or any(P * PR[i] <= X for i in range(k) if i not in T): continue
            sT = {N: len(left(N, T)) for N in Ns}; D = min(sT.values()); cells = sorted({N % P for N in Ns if sT[N] == D}); mem = [N for N in Ns if sT[N] == D]
            # where the optimum's own cell ranks in this design
            opt_cells = sorted({sT[N] for N in Ns if len(full[N]) == OPT})
            print(f"  T = {[PR[i] for i in T]} (window {X / P:.2f}): design value {D} in {len(cells)} cells; their {len(mem)} members have full scores {sorted(len(full[N]) for N in mem)}; the optimum's cell has design value {opt_cells}")
if __name__ == "__main__":
    if len(sys.argv) > 3:
        describe(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    else:
        print("least X (>= 5 Q, on the grid of smallest.py) with PINSCAN > OPT, for each target")
        for Q in (60, 80, 100, 120, 140, 160, 180, 200):
            best = None
            for k in range(3, 8):
                cands = set()
                for size in range(1, k + 1):
                    for T in itertools.combinations(range(k), size):
                        P = 2 * math.prod(PR[i] for i in T)
                        for w in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16):
                            if 5 * Q <= P * w <= 60000: cands.add(P * w)
                for X in sorted(cands):
                    if best is not None and X >= best["X"]: break
                    if 2 * math.prod(PR[:k]) <= X: continue
                    r = sm.instance(Q, k, X)
                    if r["PINSCAN"] > r["OPT"]: best = r; break
            print(f"Q = {Q}: " + (f"X = {best['X']:,d}, moduli 3..{PR[best['k'] - 1]}, OPT {best['OPT']}, PINSCAN {best['PINSCAN']}, best pinnable set {best['T']} (design {best['D_T']}, window {best['window']:.2f})" if best else "none up to 60,000"), flush=True)
