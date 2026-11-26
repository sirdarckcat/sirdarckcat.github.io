# Independent list-form meet in the middle (verifier).  usage: mitm.py j sig_cover sig_later sigma_total
# Lists: cover class vectors of cost <= sig_cover, later class vectors of deficit <= sig_later.  Every candidate pair in
# a widened arc is rebuilt exactly with big integers; kept iff 0 <= N < X and excess <= sigma_total.
import sys, time, math, numpy as np, pickle
from base import *
j, sc, sl, sig = map(int, sys.argv[1:5])
t0 = time.time()
later = LATER[:j]; T = prod(later); P = M * T
Minv = pow(M, -1, T)
dl = {r: dlt_table(r) for r in cprimes}
hit = {s: hit_table(s) for s in later}
gmax = sum(int(hit[s].max()) for s in later); unc = n0 - gmax
U64 = np.uint64; Tu = U64(T)
def addmod(a, b):          # a array uint64 < T, b scalar < T
    s = a + U64(b)         # < 2T < 2^64
    return np.where(s >= Tu, s - Tu, s)
# ---------- later list
lev = [[np.zeros(1, dtype=U64)]] + [[] for _ in range(sl)]
lev = [np.concatenate(x) if x else np.zeros(0, dtype=U64) for x in lev]
for s in later:
    Ts = T // s; es = Ts * pow(Ts, -1, s)            # idempotent mod T
    d = hit[s].max() - hit[s]
    new = [[] for _ in range(sl + 1)]
    for c in range(s):
        dc = int(d[c])
        if dc > sl: continue
        g = (c * es * Minv) % T
        for l in range(sl + 1 - dc):
            if len(lev[l]): new[l + dc].append(addmod(lev[l], g))
    lev = [np.concatenate(x) if x else np.zeros(0, dtype=U64) for x in new]
nlater = sum(len(x) for x in lev)
LP = np.concatenate(lev); del lev; LP.sort()
print(f"j={j} T={T} D={math.log(P) - 200 * math.log(10):.4f}; later list (deficit <= {sl}): {nlater}   [{time.time() - t0:.1f}s]", flush=True)
# ---------- cover list, level by level, with parent pointers
codes = []                       # code -> (r, c)
pos = [np.zeros(0, dtype=U64) for _ in range(sc + 1)]; frac = [np.zeros(0) for _ in range(sc + 1)]
par = [np.zeros(0, dtype=np.int32) for _ in range(sc + 1)]; cod = [np.zeros(0, dtype=np.int32) for _ in range(sc + 1)]
pos[0] = np.array([(N0 * Minv) % T], dtype=U64); frac[0] = np.array([N0 / M]); par[0] = np.array([-1], dtype=np.int32); cod[0] = np.array([-1], dtype=np.int32)
from fractions import Fraction
for r in cprimes:
    Mr = M // r; Er = Mr * pow(Mr, -1, r)
    snap = [len(pos[l]) for l in range(sc + 1)]
    add = [[] for _ in range(sc + 1)]
    for c in range(r):
        dc = int(dl[r][c])
        if c == cover[r] or dc > sc: continue
        dd = ((c - cover[r]) * Er) % M
        g = (dd * Minv) % T; f = float(Fraction(dd, M))
        code = len(codes); codes.append((r, c))
        for l in range(sc + 1 - dc):
            n = snap[l]
            if n == 0: continue
            add[l + dc].append((addmod(pos[l][:n], g), frac[l][:n] + f, np.arange(n, dtype=np.int32), np.full(n, code, dtype=np.int32), l))
    for l in range(sc + 1):
        if add[l]:
            pos[l] = np.concatenate([pos[l]] + [a[0] for a in add[l]]); frac[l] = np.concatenate([frac[l]] + [a[1] for a in add[l]])
            par[l] = np.concatenate([par[l]] + [a[2] for a in add[l]]); cod[l] = np.concatenate([cod[l]] + [a[3] for a in add[l]])
    # parent level is implied by cost: parent level = l - dlt(code)
ncover = sum(len(x) for x in pos)
print(f"cover list (cost <= {sc}): {ncover}; by cost {[len(x) for x in pos]}   [{time.time() - t0:.1f}s]", flush=True)
def rebuild(l, i):
    ch = {}
    while cod[l][i] >= 0:
        r, c = codes[cod[l][i]]; assert r not in ch; ch[r] = c
        i = int(par[l][i]); l -= int(dl[r][c])
    assert l == 0 and i == 0
    return ch
# ---------- match
W = K + 3
out = {}; ncand = 0
for l in range(sc + 1):
    if len(pos[l]) == 0: continue
    w = np.floor(frac[l]).astype(np.int64) + 1          # subtract w_est + 1  (range then covers k in [-1, K+1])
    lo = pos[l].copy()
    wu = w.astype(U64)
    lo = np.where(lo >= wu, lo - wu, lo + Tu - wu)
    hi = lo + U64(W)
    i1 = np.searchsorted(LP, lo, side="left"); i2 = np.searchsorted(LP, hi, side="right")
    wrap = hi >= Tu
    i3 = np.zeros(len(lo), dtype=np.int64)
    if wrap.any(): i3[wrap] = np.searchsorted(LP, hi[wrap] - Tu, side="right")
    idx = np.nonzero((i2 > i1) | (i3 > 0))[0]
    for i in idx:
        i = int(i)
        cands = list(LP[i1[i]:i2[i]]) + list(LP[:i3[i]])
        ch = rebuild(l, i)
        cls = dict(cover); cls.update(ch)
        na, mm = crt_pairs([(2, 0)] + [(r, cls[r]) for r in cprimes]); assert mm == M
        cost = sum(int(dl[r][c]) for r, c in ch.items()); assert cost == l
        for pb in cands:
            ncand += 1
            t = (int(pb) * M) % T
            k = ((t - na) * Minv) % T
            N = na + k * M
            if N >= X: continue
            defi = sum(int(hit[s].max() - hit[s][N % s]) for s in later)
            assert all(N % s == t % s for s in later)
            if cost + defi <= sig:
                out[N] = (cost, defi)
print(f"candidate pairs examined {ncand} (lists product * (K+3)/T = {ncover * nlater * W / T:.4g}); points below X with excess <= {sig}: {len(out)}   [{time.time() - t0:.1f}s]")
from collections import Counter
print("by first-order score:", dict(sorted(Counter(unc + c + d for c, d in out.values()).items())))
print("by (cover cost, later deficit):", dict(sorted(Counter(out.values()).items())))
print(f"list entries {ncover + nlater} = {(ncover + nlater) / math.exp(math.log(P) - 200 * math.log(10)):.4g} e^D = {(ncover + nlater) / math.exp((math.log(P) - 200 * math.log(10)) / 2):.4g} e^(D/2)")
# exact rows of every point
def exact_rows(N):
    keep = np.ones(len(allp), dtype=bool)
    for r in cprimes + later: keep &= (allp % r != N % r)
    return int(keep.sum())
pts = sorted(out)
if len(pts) <= 20000:
    ex = np.array([exact_rows(N) for N in pts]); fo = np.array([unc + sum(out[N]) for N in pts])
    d = ex - fo
    print(f"exact rows minus first-order over {len(pts)} points: mean {d.mean():+.2f} sd {d.std():.2f} min {d.min()} max {d.max()}; least exact rows {ex.min()}; exact rows of the first-order-best points: {sorted(ex[fo == fo.min()].tolist())}")
pickle.dump(out, open(f"out_j{j}_c{sc}_l{sl}_s{sig}.pkl", "wb"))
print(f"total {time.time() - t0:.1f}s")
