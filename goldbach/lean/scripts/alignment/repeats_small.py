"""The same split (more strikes / fewer repeated strikes) for the true optima of the small instances of grid.py
(those with X up to 1e7), at 4 and at 8 primes beyond the line.  Controls: every candidate whose cell has the same
design value as the optimum's cell."""
import math, sys
import numpy as np
PR = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.float64)
def study(Q, lidx, w, extra):
    rows = [q for q in primes_upto(Q - 1) if q > 2]; M = 2 * math.prod(PR[:lidx]); X = M * w
    Ns = np.arange(0, X, 2, dtype=np.int64); W = (len(rows) + 63) // 64
    def mask(r):
        m = np.zeros((r, W), dtype=np.uint64)
        for j, q in enumerate(rows): m[q % r, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
        return m
    left = np.zeros((len(Ns), W), dtype=np.uint64)
    for j in range(len(rows)): left[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    for r in PR[:lidx]: left &= ~mask(r)[Ns % r]
    L = pc(left); cur = left.copy(); I = np.zeros(len(Ns)); logprod = np.zeros(len(Ns))
    for r in PR[lidx:lidx + extra]:
        cm = mask(r)[Ns % r]; K = pc(left & cm); I += K; logprod += np.log1p(-np.minimum(K / np.maximum(L, 1), 1 - 1e-12)); cur &= ~cm
    score = pc(cur); U = L - score; U0 = L * (1 - np.exp(logprod)); opt = score.min(); o = score == opt
    Lo = np.unique(L[o]); c = np.isin(L, Lo) & ~o
    return {"Q": Q, "line": PR[lidx - 1], "w": w, "opt": int(opt), "nopt": int(o.sum()), "L_opt": float(L[o].mean()), "Dl": float(L.min()),
            "I": float(I[o].mean()), "U": float(U[o].mean()), "U0": float(U0[o].mean()), "Ic": float(I[c].mean()), "Uc": float(U[c].mean()), "U0c": float(U0[c].mean())}
for extra in (4, 8):
    print(f"\n{extra} primes beyond the line")
    print("Q | line | window | OPT (N) | rows left by the optimum's cover (best cover) | optimum: incidences | distinct | chance distinct | same design value: incidences | distinct | chance distinct | advantage | more strikes | fewer repeats")
    tot = np.zeros(3); cnt = 0
    for Q in (300, 500, 1000):
        for lidx in (4, 5, 6):
            for w in (2, 4, 8):
                if 2 * math.prod(PR[:lidx]) * w > 9.5e6: continue
                r = study(Q, lidx, w, extra)
                adv = r["U"] - r["Uc"]; more = r["U0"] - r["U0c"]; fewer = (r["U"] - r["U0"]) - (r["Uc"] - r["U0c"])
                tot += (adv, more, fewer); cnt += 1
                print(f"{Q} | {r['line']} | {w} | {r['opt']} ({r['nopt']}) | {r['L_opt']:.1f} ({r['Dl']:.0f}) | {r['I']:.2f} | {r['U']:.2f} | {r['U0']:.2f} | {r['Ic']:.2f} | {r['Uc']:.2f} | {r['U0c']:.2f} | {adv:.2f} | {more:.2f} | {fewer:.2f}", flush=True)
    print(f"# mean over the {cnt} instances: advantage {tot[0] / cnt:.2f} rows = more strikes {tot[1] / cnt:.2f} + fewer repeats {tot[2] / cnt:.2f} (share of fewer repeats {tot[2] / tot[0]:.2f})")
