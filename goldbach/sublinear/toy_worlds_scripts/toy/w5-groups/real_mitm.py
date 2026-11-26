#!/usr/bin/env python3
"""Meet in the middle (list form) on the real 200,000 cover with j later primes: every N < 10^200 (even, any classes at the
89 cover primes and the j later primes) whose first-order score is within `sigma` rows of the unconstrained optimum.

    python3 real_mitm.py j sigma [kcov] [bf | prod]      kcov = largest cover cost listed (default sigma)
    bf:   also brute force over the windows of the 61 covers of cost <= 1 and comparison of the two sets of N
    prod: uncertified mode: covers of cost <= kcov against later vectors of deficit <= sigma, every pair in the arc
    LCAP=n in the environment: list later vectors only to deficit n and scan the windows of the covers cheaper than sigma - n

Split: I = the 89 cover primes, Ic = the j later primes (T = their product).  x = N(c) + k M with N(c) in [0, M) the
integer of the cover classes c; for a vector t of later classes k = (i_t - i_c) mod T with i_t = t/M mod T,
i_c = N(c)/M mod T, and x < X  iff  k <= (X - 1 - N(c)) // M.   Lists: covers with cost <= kcov, later vectors with
deficit <= sigma; sort the later positions, one binary search per cover.  All positions are exact integers mod T.
Prints the list sizes (the cost), the feasible points by score, the best ones with their exact rows.
With `bf` as 4th argument: brute force over the windows of all covers of cost <= 1 and comparison (sets of N)."""
import sys, math, time, numpy as np
import common as C
j = int(sys.argv[1]); sigma = int(sys.argv[2]); kcov = int(sys.argv[3]) if len(sys.argv) > 3 else sigma
BF = len(sys.argv) > 4 and sys.argv[4] == "bf"
import os
LCAP = int(os.environ.get("LCAP", sys.argv[2]))     # later list only to this deficit; covers too cheap for it are scanned window by window
PROD = len(sys.argv) > 4 and sys.argv[4] == "prod"     # uncertified: every listed cover against every listed later vector
t0 = time.time()
js = C.later_primes(j); T = math.prod(js); M = C.M; X = C.X; N0 = C.N0
P = M * T; D = math.log(P) - math.log(X)
Minv = pow(M, -1, T) if T > 1 else 0
q, rho = divmod(X - 1, M)                      # x < X iff k <= q (N(c) <= rho) or k <= q - 1 (N(c) > rho)
ct = C.cover_tables(); lt = C.later_tables(js)
Gmax = sum(int(lt[s].max()) for s in js)
print(f"j = {j}, later primes {js}, T = {T}, D = ln(P/X) = {D:.4f}, e^D = {math.exp(D):.4g}, e^(D/2) = {math.exp(D / 2):.4g}; window {q + 1} members; Gmax = {Gmax}; unconstrained optimum {C.n0 - Gmax}")

# ---- later side: vectors with deficit <= sigma, position i_t = t * Minv mod T
assert 2 * T + 2 * (q + 1) < 2 ** 64
TT = np.uint64(T)
pos = np.zeros(1, dtype=np.uint64); dfc = np.zeros(1, dtype=np.int16)
for s in js:
    e = (T // s) * pow(T // s, -1, s)                              # CRT idempotent of s in Z/T
    iw = np.array([(c * e * Minv) % T for c in range(s)], dtype=np.uint64)
    d = (lt[s].max() - lt[s]).astype(np.int16)
    np_, nd = [], []
    for dv in range(0, min(sigma, LCAP) + 1):
        cls = np.nonzero(d == dv)[0]
        if len(cls) == 0: continue
        keep = dfc <= min(sigma, LCAP) - dv
        if not keep.any(): continue
        np_.append(((pos[keep][:, None] + iw[cls][None, :]) % TT).ravel()); nd.append(np.repeat(dfc[keep] + dv, len(cls)))
    pos = np.concatenate(np_); dfc = np.concatenate(nd).astype(np.int16)
o = np.argsort(pos, kind="stable"); pos = pos[o]; dfc = dfc[o]
nlater = len(pos)
print(f"later list (deficit <= {min(sigma, LCAP)}): {nlater} vectors   [{time.time() - t0:.1f} s]")

# ---- cover side: vectors with cost <= kcov; i_c = (i_0 + sum iw - wraps) mod T, wraps = floor(N0/M + sum theta)
i0 = (N0 * Minv) % T if T > 1 else 0
cls_info = []                                                   # per cover prime: (r, classes, cost, iw, theta, wbig)
for (r, a) in C.cov:
    d = ct[r]; cl = np.nonzero((d <= kcov) & (np.arange(r) != a))[0]
    if len(cl) == 0: continue
    e = (M // r) * pow(M // r, -1, r)                           # idempotent of r in Z/M
    wb = [((int(c) - a) * e) % M for c in cl]
    cls_info.append((r, a, cl, d[cl].astype(np.int16), np.array([(w * Minv) % T for w in wb], dtype=np.uint64), np.array([w / M for w in wb]), wb))
cpos = np.array([0], dtype=np.uint64); cth = np.array([N0 / M]); ccost = np.zeros(1, dtype=np.int16)
cpar = np.array([-1], dtype=np.int64); ccoord = np.array([-1], dtype=np.int16); ccls = np.array([-1], dtype=np.int16)
for ci, (r, a, cl, dc, iw, th, wb) in enumerate(cls_info):
    npos, nth, ncost, npar, ncl = [], [], [], [], []
    for dv in np.unique(dc):
        sel = np.nonzero(dc == dv)[0]
        keep = np.nonzero(ccost <= kcov - dv)[0]
        if len(keep) == 0: continue
        npos.append(((cpos[keep][:, None] + iw[sel][None, :]) % TT).ravel()); nth.append((cth[keep][:, None] + th[sel][None, :]).ravel())
        ncost.append(np.repeat(ccost[keep] + dv, len(sel))); npar.append(np.repeat(keep, len(sel))); ncl.append(np.tile(sel, len(keep)))
    if npos:
        cpos = np.concatenate([cpos] + npos); cth = np.concatenate([cth] + nth); ccost = np.concatenate([ccost] + ncost).astype(np.int16)
        add = sum(len(x) for x in npos)
        cpar = np.concatenate([cpar] + npar); ccoord = np.concatenate([ccoord, np.full(add, ci, dtype=np.int16)]); ccls = np.concatenate([ccls] + ncl).astype(np.int16)
ncover = len(cpos)
fr = cth - np.floor(cth); amb = int(((fr < 1e-9) | (fr > 1 - 1e-9)).sum())
wraps = np.floor(cth).astype(np.int64)
assert wraps.min() >= 0 and wraps.max() < 10 ** 6
ic = (((cpos + np.uint64(i0)) % TT) + (TT - wraps.astype(np.uint64))) % TT
assert ic.dtype == np.uint64 and pos.dtype == np.uint64
print(f"cover list (cost <= {kcov}): {ncover} class vectors; ambiguous wrap counts (recomputed exactly if matched): {amb}   [{time.time() - t0:.1f} s]")
def cover_classes(idx):
    ch = {}
    while idx > 0:
        r, a, cl, dc, iw, th, wb = cls_info[int(ccoord[idx])]; ch[r] = int(cl[int(ccls[idx])]); idx = int(cpar[idx])
    return ch
def cover_int_fast(idx):
    tot = N0
    while idx > 0:
        tot += cls_info[int(ccoord[idx])][6][int(ccls[idx])]; idx = int(cpar[idx])
    return tot % M
def cover_int(ch):
    return C.crt([(r, ch.get(r, a)) for r, a in C.cov])

# ---- match, one cost level at a time: covers of cost k against the later vectors of deficit <= sigma - k (sorted positions)
assert T > q + 1, "P <= X: no constraint (use real_w1.py)"
found = []; pairs_examined = 0
for kc in range(0, kcov + 1):
    if not PROD and sigma - kc > LCAP: continue          # scanned below
    cidx = np.nonzero(ccost == kc)[0]
    lsel = np.nonzero(dfc <= (sigma if PROD else sigma - kc))[0]
    if len(cidx) == 0 or len(lsel) == 0: continue
    lp = pos[lsel]; a = ic[cidx]; b = a + np.uint64(q)
    lo = np.searchsorted(lp, a, side="left"); hi = np.searchsorted(lp, np.minimum(b, TT - np.uint64(1)), side="right")
    hi2 = np.where(b >= TT, np.searchsorted(lp, np.where(b >= TT, b - TT, np.uint64(0)), side="right"), 0)
    for (st, en) in ((lo, hi), (np.zeros_like(hi2), hi2)):
        n = en - st; nz = np.nonzero(n > 0)[0]
        if len(nz) == 0: continue
        tot = int(n[nz].sum()); pairs_examined += tot
        rep = np.repeat(nz, n[nz]); off = np.arange(tot) - np.repeat(np.cumsum(n[nz]) - n[nz], n[nz])
        li = lsel[st[rep] + off]; ci = cidx[rep]
        found.extend(zip((kc + dfc[li]).tolist(), ci.tolist(), li.tolist()))
print(f"pairs in the arc examined (stratified by cost level, all are outputs up to the window's edge): {pairs_examined}; lists product * X/P = {ncover * nlater * math.exp(-D):.4g}   [{time.time() - t0:.1f} s]")

# ---- exact verification of every found pair with big integers
res = []; border = 0
for ex, ci, li in found:
    ch = cover_classes(ci); Nc = cover_int_fast(ci)
    k = (int(pos[li]) - (Nc * Minv) % T) % T
    x = Nc + k * M
    if x >= X: border += 1; continue                           # only possible at the last member of the window
    if len(res) < 3000: assert all(x % r == ch.get(r, a) for r, a in C.cov) and x % 2 == 0
    hits = sum(int(lt[s][x % s]) for s in js); cost = sum(int(ct[r][x % r]) for r, _ in C.cov)
    assert cost - (hits - Gmax) == ex, (cost, hits, ex)
    if len(res) > 200000: continue
    res.append((C.n0 + cost - hits, x, cost, len(ch)))
scanned = 0
if not PROD and sigma > LCAP:
    for ci in np.nonzero(ccost < sigma - LCAP)[0]:
        Nc = cover_int_fast(int(ci)); K = (X - 1 - Nc) // M + 1; cost = int(ccost[ci]); tot = np.zeros(K, dtype=np.int16)
        for s in js:
            pat = lt[s][(Nc % s + np.arange(s, dtype=np.int64) * (M % s)) % s].astype(np.int16); tot += np.resize(pat, K)
        for k in np.nonzero(Gmax - tot + cost <= sigma)[0]:
            x = Nc + int(k) * M; res.append((C.n0 + cost - int(tot[k]), x, cost, len(cover_classes(int(ci)))))
        scanned += K
    print(f"covers of cost < {sigma - LCAP} scanned window by window: {scanned} members")
res.sort()
print(f"verified below X: {len(res)} (dropped at the window's edge: {border})")
hist = {}
for s, x, cost, nch in res: hist[s] = hist.get(s, 0) + 1
print("feasible points by first-order score:", dict(sorted(hist.items())))
print(f"COST: list entries {ncover + nlater} (+ {scanned} members scanned) = {(ncover + nlater) / math.exp(D):.4g} e^D = {(ncover + nlater) / math.exp(D / 2):.4g} e^(D/2);  outputs {len(res)}")
def exact_rows(x): return len(C.rows_of([(r, x % r) for r, _ in C.cov] + [(s, x % s) for s in js]))
if res:
    best = res[0][0]
    print(f"{'BEST FOUND (not certified: product of two short lists)' if PROD else 'OPTIMUM of the first-order score over all N < X (certified: every point within sigma is listed)'}: {best}  = unconstrained + {best - (C.n0 - Gmax)}")
elif not PROD:
    print(f"CERTIFIED: no N < X has first-order score <= {C.n0 - Gmax + sigma} (unconstrained optimum + {sigma})")
if False:
    pass
    show = res[:12]
    for s, x, cost, nch in show:
        print(f"   first-order {s}  exact rows {exact_rows(x)}  cover cost {cost} ({nch} classes changed)  later hits {[int(lt[t][x % t]) for t in js]}  N = {str(x)[:12]}...{str(x)[-6:]} ({len(str(x))} digits)")
    top = res[:2000]; er = [exact_rows(x) for _, x, _, _ in top]
    print(f"   least exact rows among the {len(top)} best by first order: {min(er)} (first-order of that point {top[int(np.argmin(er))][0]})")
import pickle
if not PROD: pickle.dump([(s, x) for s, x, _, _ in res], open(f"mitm_j{j}_s{sigma}_k{kcov}.pkl", "wb"))

# ---- brute force over windows (covers of cost <= 1, or only the cover itself when kcov = 0)
if BF:
    tb = time.time(); bf = set(); nwin = 0; members = 0; own_best = None
    for ci in np.nonzero(ccost <= min(1, kcov))[0]:
        ch = cover_classes(int(ci)); Nc = cover_int(ch); K = (X - 1 - Nc) // M + 1; cost = int(ccost[ci])
        tot = np.zeros(K, dtype=np.int16)
        for s in js:
            pat = lt[s][(Nc % s + np.arange(s, dtype=np.int64) * (M % s)) % s].astype(np.int16)
            tot += np.resize(pat, K)
        if ci == 0: own_best = int(tot.max()); own_cnt = np.bincount(Gmax - tot.astype(np.int64))[:sigma + 1]
        for k in np.nonzero(Gmax - tot + cost <= sigma)[0]: bf.add(Nc + int(k) * M)
        nwin += 1; members += K
    mine = {x for s, x, cost, nch in res if cost <= min(1, kcov)}
    print(f"BRUTE FORCE over {nwin} windows ({members} members): points with excess <= {sigma}: {len(bf)}; meet in the middle restricted to the same covers: {len(mine)}; identical sets: {bf == mine}   [{time.time() - tb:.1f} s]")
    print(f"   the cover's own window: most hits {own_best} -> best first-order {C.n0 - own_best}; members by deficit 0..{sigma}: {own_cnt.tolist()}")
print(f"total time {time.time() - t0:.1f} s")
