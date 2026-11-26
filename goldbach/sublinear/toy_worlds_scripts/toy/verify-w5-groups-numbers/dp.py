# Independent rounded dynamic programme (Theorem 3 as stated), verifier's implementation.  usage: dp.py j sigma eps_num eps_den
import sys, time, math, pickle, os, numpy as np
from fractions import Fraction
from base import *
j, sigma, en, ed = map(int, sys.argv[1:5]); eps = Fraction(en, ed)
t0 = time.time()
later = LATER[:j]; T = prod(later); P = M * T
dl = {r: dlt_table(r) for r in cprimes}; hit = {s: hit_table(s) for s in later}
unc = n0 - sum(int(hit[s].max()) for s in later)
ny = N0                                           # base point y = residues of N0 (N0 < M < P)
# coordinate list: (r, base class, [(class, cost)])
coords = []
for r in cprimes:
    cl = [(c, int(dl[r][c])) for c in range(r) if dl[r][c] <= sigma]
    if len(cl) > 1: coords.append((r, cover[r], cl))
zero_alt = sum(1 for r in cprimes if (dl[r] == 0).sum() > 1)
for s in later:
    d = hit[s].max() - hit[s]
    coords.append((s, N0 % s, [(c, int(d[c])) for c in range(s) if d[c] <= sigma]))
E = sigma + zero_alt + j
B = -((-E * P) // (eps.denominator * 0 + 1) * 0) if False else int(math.ceil(Fraction(E * P, X) / eps))
ncls = sum(len(c[2]) for c in coords)
rho = []
for r, b, cl in coords:
    u = pow((P // r) % r, -1, r)
    rho.append([(B * (((c - b) * u) % r)) // r for c, _ in cl])
INF = sigma + 1
V = [np.full(B, INF, dtype=np.uint8)]; V[0][0] = 0
for (r, b, cl), rh in zip(coords, rho):
    old = V[-1]; new = np.full(B, INF, dtype=np.uint8)
    for (c, cost), sh in zip(cl, rh):
        cand = np.roll(old, sh)                  # cand[b] = old[b - sh]
        cand = np.minimum(cand + np.uint8(cost), INF).astype(np.uint8)
        np.minimum(new, cand, out=new)
    V.append(new)
tf = time.time() - t0
# target set T: integers n with -B ny/P - E < n < B (X - ny)/P
lo = Fraction(-B * ny, P) - E; hi = Fraction(B * (X - ny), P)
nlo = math.floor(lo) + 1; nhi = math.ceil(hi) - 1
targets = sorted({n % B for n in range(nlo, nhi + 1)})
best = min(int(V[-1][b]) for b in targets)
print(f"j={j} sigma={sigma} eps={eps}: E={E} B={B} = {B * X / P:.3f} e^D; coordinates {len(coords)}, classes {ncls}, B*classes = {B * ncls:.4g} = {B * ncls * X / P:.4g} e^D; targets {len(targets)}; least excess on relaxed set {best if best < INF else '>sigma'}  [{tf:.1f}s]", flush=True)
# backward listing, iterative stack
listed = []; nodes = 0
stack = [(len(coords), b, sigma, ()) for b in targets if V[-1][b] <= sigma]
while stack:
    t, b, bud, acc = stack.pop(); nodes += 1
    if t == 0:
        if b == 0: listed.append(acc)
        continue
    r, bs, cl = coords[t - 1]; rh = rho[t - 1]; Vp = V[t - 1]
    for (c, cost), sh in zip(cl, rh):
        if cost <= bud:
            pb = (b - sh) % B
            if Vp[pb] <= bud - cost: stack.append((t - 1, pb, bud - cost, acc + ((r, c),)))
below = {}; outside = 0; outN = []
for acc in listed:
    cls = dict(cover); cls.update(dict(acc))
    N, mm = crt_pairs([(2, 0)] + [(r, cls[r]) for r in cprimes] + [(s, cls[s]) for s in later]); assert mm == P
    exc = sum(int(dl[r][cls[r]]) for r in cprimes) + sum(int(hit[s].max() - hit[s][cls[s]]) for s in later)
    assert exc <= sigma
    if N < X: below[N] = exc
    else:
        outside += 1; outN.append(N)
# check the sandwich: every listed point has N/P in (-E/B, X/P + E/B) mod 1
bad = sum(1 for N in outN if not (N * B < (X * B + E * P) or (N - P) * B > -E * P))
from collections import Counter
print(f"relaxed points listed {len(listed)} ({nodes} nodes, {nodes / max(1, len(listed)):.1f} per point); below X {len(below)}, outside {outside}, overhead {len(listed) / max(1, len(below)):.3f}; listed points violating the sandwich: {bad}")
print("below X by first-order score:", dict(sorted(Counter(unc + e for e in below.values()).items())))
# compare with my meet in the middle
import glob
for f in glob.glob(f"out_j{j}_c{sigma}_l{sigma}_s{sigma}.pkl"):
    mm = pickle.load(open(f, "rb"))
    print("my meet in the middle:", len(mm), "points; identical sets:", set(mm) == set(below))
print(f"total {time.time() - t0:.1f}s")
