#!/usr/bin/env python3
"""Independent recomputation on the real 200,000 cover (own code; only the cover file and the repo's cover_record loader are read).
  python3 v_real.py basics            theta, D(z), level counts, own window j = 1..8
  python3 v_real.py list j sigma      all N < 10^200 with first-order excess <= sigma, by my own sort-and-match
"""
import sys, math, time, numpy as np, sympy
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear"); sys.dont_write_bytecode = True
import cover_record as cr
F = cr.S + "q200000_m89.txt"
rows_all, _ = cr.load(F); rows = rows_all[rows_all < 200000]
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in open(F).readline().split() if ":" in t]
assert len(cov) == 89 and len(rows) == 1502, (len(cov), len(rows))
n0 = 1502; X = 10 ** 200
M = 2 * math.prod(r for r, _ in cov)
def crt(pairs):
    N, m = 0, 1
    for r, a in pairs:
        N += m * (((a - N) * pow(m, -1, r)) % r); m *= r
    return N
N0 = crt([(2, 0)] + cov)
assert N0 % 2 == 0 and all(N0 % r == a for r, a in cov) and 0 <= N0 < M
K0 = (X - 1 - N0) // M + 1
later = [int(p) for p in sympy.primerange(464, 700)]
allodd = np.array(list(sympy.primerange(3, 200000)), dtype=np.int64)
def dlt_tables():
    out = {}
    for r, a in cov:
        alive = np.ones(len(allodd), dtype=bool)
        for r2, a2 in cov:
            if r2 != r: alive &= (allodd % r2) != a2
        U = allodd[alive]
        d = len(U) - np.bincount(U % r, minlength=r) - n0
        assert d[a] == 0
        out[r] = d
    return out
hit = lambda s: np.bincount(rows % s, minlength=s)

def basics():
    th463 = sum(math.log(p) for p in sympy.primerange(2, 464)); lnX = 200 * math.log(10)
    print(f"theta(463) = {th463:.3f}, ln M = {math.log(M):.3f}, ln X = {lnX:.3f}, K0 = {K0}")
    for z in (467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 600, 700, 1000, 2000, 5000, 10 ** 4, 10 ** 5, 2 * 10 ** 5, 10 ** 6):
        th = sum(math.log(p) for p in sympy.primerange(2, z + 1)); print(f"   D({z}) = {th - lnX:.1f}", end=";")
    print()
    dl = dlt_tables()
    print("cover 1-optimal (all dlt >= 0):", all((d >= 0).all() for d in dl.values()), "; cover primes with a second class at cost 0:", sum(1 for d in dl.values() if (d == 0).sum() > 1))
    poly = np.zeros(8, dtype=object); poly[0] = 1
    for r, a in cov:
        h = np.bincount(np.minimum(dl[r], 8), minlength=9)[:8]
        new = np.zeros(8, dtype=object)
        for i in range(8):
            if poly[i]:
                for k in range(8 - i):
                    if h[k]: new[i + k] += poly[i] * int(h[k])
        poly = new
    print("cover class vectors at first-order cost exactly 0..7:", [int(v) for v in poly])
    k = np.arange(K0, dtype=np.int64); tot = np.zeros(K0, dtype=np.int32); unc = 0
    for j, s in enumerate(later[:8], 1):
        h = hit(s); tot += h[(N0 % s + k * (M % s)) % s].astype(np.int32); unc += int(h.max())
        best = int(tot.max()); print(f"   j={j} (s={s}): D = {math.log(M) + sum(math.log(x) for x in later[:j]) - 200 * math.log(10):.3f}; unconstrained optimum {n0 - unc}; own window best {n0 - best} "
                                     f"({int((tot == best).sum())} members), mean hits {tot.mean():.2f}")
    # multiplicities for j = 1, 2
    for j in (1, 2):
        T = math.prod(later[:j]); cnt = np.bincount(((N0 % T) + k * (M % T)) % T, minlength=T); print(f"   j={j}: class-vector multiplicities in the window: min {cnt.min()}, max {cnt.max()}")

def lists(j, sigma):
    t0 = time.time(); js = later[:j]; T = math.prod(js); P = M * T; Minv = pow(M, -1, T)
    D = math.log(P) - math.log(X); dl = dlt_tables()
    H = {s: hit(s) for s in js}; Gmax = sum(int(H[s].max()) for s in js)
    # later list: (deficit, a = t * Minv mod T) with t the CRT integer of the later classes; a is linear mod T
    assert T < 2 ** 63
    dfc = np.zeros(1, dtype=np.int8); pos = np.zeros(1, dtype=np.uint64)
    for s in js:
        e = (T // s) * pow(T // s, -1, s) % T
        d = H[s].max() - H[s]; cl = [c for c in range(s) if d[c] <= sigma]
        cd = np.array([int(d[c]) for c in cl], dtype=np.int8); cp = np.array([(c * e * Minv) % T for c in cl], dtype=np.uint64)
        nd = (dfc[:, None] + cd[None, :]).ravel(); keep = nd <= sigma
        npos = ((pos[:, None] + cp[None, :]) % np.uint64(T)).ravel()
        dfc = nd[keep]; pos = npos[keep]
    order = np.argsort(pos, kind="stable"); pos = pos[order]; dfc = dfc[order]
    # cover list in exact integers: (cost, N_v in [0,M))
    alt = [(r, a, [(int(c), int(dl[r][c])) for c in range(r) if c != a and dl[r][c] <= sigma]) for r, a in cov]
    alt = [(r, a, [(((c - a) * (M // r) * pow(M // r, -1, r)) % M, cst) for c, cst in al]) for r, a, al in alt if al]
    cv_cost = []; cv_N = []
    def rec(i, cost, N):
        if i == len(alt): cv_cost.append(cost); cv_N.append(N % M); return
        rec(i + 1, cost, N)
        for dN, cst in alt[i][2]:
            if cost + cst <= sigma: rec(i + 1, cost + cst, N + dN)
    rec(0, 0, N0)
    nI = len(cv_N); nC = len(pos)
    b = np.array([(N * Minv) % T for N in cv_N], dtype=np.uint64); Kv = np.array([(X - 1 - N) // M + 1 for N in cv_N], dtype=np.uint64)
    cst = np.array(cv_cost, dtype=np.int8)
    Tn = np.uint64(T)
    lo = np.searchsorted(pos, b, side="left")
    end = b + Kv                                         # < 2^64
    wrap = end >= Tn
    hi = np.where(wrap, nC, np.searchsorted(pos, np.minimum(end, Tn - np.uint64(1)), side="left"))
    hi2 = np.where(wrap, np.searchsorted(pos, end - Tn, side="left"), 0)     # positions in [0, end - T)
    found = {}
    cand = 0
    for v in np.nonzero((hi > lo) | (hi2 > 0))[0].tolist():
        idx = list(range(int(lo[v]), int(hi[v]))) + list(range(0, int(hi2[v])))
        for w in idx:
            cand += 1
            sc = int(cst[v]) + int(dfc[w])
            if sc <= sigma:
                kk = (int(pos[w]) - int(b[v])) % T; N = cv_N[v] + kk * M
                assert N < X and N % M == cv_N[v]
                # exact first-order score from the definition
                S = n0 + sum(int(dl[r][N % r]) for r, _ in cov) - sum(int(H[s][N % s]) for s in js)
                assert S == n0 - Gmax + sc
                found[N] = S
    hist = {}
    for S in found.values(): hist[S] = hist.get(S, 0) + 1
    print(f"j={j}, sigma={sigma}: D={D:.3f}, e^D={math.exp(D):.4g}; my lists: covers {nI}, later {nC} (sum {nI + nC}); candidates in position windows {cand}; "
          f"N < X within slack: {len(found)} by score {dict(sorted(hist.items()))}; unconstrained optimum {n0 - Gmax}; {time.time() - t0:.1f} s")
    # predicted count: number of pairs within slack times e^-D
    hc = np.bincount(cst, minlength=sigma + 1); hw = np.bincount(dfc, minlength=sigma + 1)
    npairs = sum(int(hc[i]) * int(hw[k]) for i in range(sigma + 1) for k in range(sigma + 1 - i))
    print(f"      n(sigma) = {npairs}, n(sigma) e^-D = {npairs * math.exp(-D):.2f}")
    return found

if __name__ == "__main__":
    if sys.argv[1] == "basics": basics()
    else: lists(int(sys.argv[2]), int(sys.argv[3]))
