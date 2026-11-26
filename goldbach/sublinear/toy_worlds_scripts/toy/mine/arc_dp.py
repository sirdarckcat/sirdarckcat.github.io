#!/usr/bin/env python3
"""World 5 on the real data: the best N below 10^200 when j later primes are added to the 89 of the cover, by the dynamic
programme of the one-character constraint (x < X iff frac(sum_i x_i u_i / r_i) < X/P).

    python3 arc_dp.py j [eta_div = 4m]

Score (first order around the cover): rows left = 1502 + sum over cover primes of D_r(c) + sum over later primes of -hits_s(c),
D_r(c) = change in rows left when the class of r is changed from the cover's to c (exact for one change), hits_s(c) = rows of
the cover in class c of s.  The best points found are then scored exactly (true union) and compared with what the cover's own
window holds (brute force over all k)."""
import sys, math, re, numpy as np
from fractions import Fraction
F = "/home/user/sirdarckcat.github.io/goldbach/fscan/cover/starts/q200000_m89.txt"
j = int(sys.argv[1]); Q = 200000; X = 10 ** 200
cov = [(int(a), int(b)) for a, b in re.findall(r"(\d+):(\d+)", open(F).readline())]
sv = np.ones(Q, dtype=bool); sv[:2] = False
for i in range(2, int(Q ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
sv[2] = False; PR = np.nonzero(sv)[0]
allp = np.ones(2000, dtype=bool); allp[:2] = False
for i in range(2, 45):
    if allp[i]: allp[i * i::i] = False
later = [int(s) for s in np.nonzero(allp)[0] if s > 463][:j]
def rows_of(classes):
    alive = np.ones(len(PR), dtype=bool)
    for r, a in classes: alive &= (PR % r) != a
    return PR[alive]
R0 = rows_of(cov); n0 = len(R0)
# tables
coords = []          # (modulus, classes array, score array)
for idx, (r, a) in enumerate(cov):
    U = rows_of(cov[:idx] + cov[idx + 1:])
    cnt = np.bincount(U % r, minlength=r)
    delta = (len(U) - cnt) - n0                      # rows left if the class of r is c, minus rows left now
    assert delta[a] == 0
    coords.append((r, np.arange(r), delta.astype(np.int32)))
for s in later:
    cnt = np.bincount(R0 % s, minlength=s)
    coords.append((s, np.arange(s), (-cnt).astype(np.int32)))
mods = [2] + [r for r, _, _ in coords]
P = math.prod(mods); m = len(coords)
delta_arc = Fraction(X, P); D = -math.log(float(delta_arc))
print(f"j = {j} later primes {later}; P/X = e^{D:.3f}; arc {float(delta_arc):.3e}; cover rows {n0}")
# phi_r(c) = c * u_r / r mod 1, u_r = (P/r)^-1 mod r   (the modulus 2 has class 0: contributes 0)
phis = []
for (r, cl, sc) in coords:
    u = pow(P // r % r, -1, r)
    phis.append(((cl * u) % r) / r)
div = int(sys.argv[2]) if len(sys.argv) > 2 else 4 * m
eta = float(delta_arc) / div; B = int(math.ceil(1.0 / eta)); eta = 1.0 / B
print(f"buckets {B} (width arc/{float(delta_arc) / eta:.1f}); transitions {B * sum(len(c[1]) for c in coords):.3e}")
INF = 10 ** 6; CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 9
best = np.full(B, INF, dtype=np.int32); ssum = np.zeros(B); best[0] = 0
back_c = []; back_b = []
for t, ((r, cl, sc), ph) in enumerate(zip(coords, phis)):
    nb = np.full(B, INF, dtype=np.int32); ns = np.zeros(B); bc = np.full(B, -1, dtype=np.int16); bb = np.full(B, -1, dtype=np.int32)
    live = np.nonzero(best < INF)[0]
    # classes kept: every class of a later prime; for a cover prime those that cost at most CAP rows (a later prime gains at most 9)
    order = np.argsort(sc, kind="stable"); keep = order[sc[order] <= CAP] if t < len(cov) else order
    bl = best[live]; sl = ssum[live]
    for c in keep:
        s2 = sl + ph[c]; s2 -= np.floor(s2)
        b2 = np.minimum((s2 * B).astype(np.int64), B - 1); v = bl + sc[c]
        old = nb[b2]
        np.minimum.at(nb, b2, v)                 # the smallest value per target bucket, also when two sources collide
        win = (v == nb[b2]) & (v < old)          # a source that set the minimum and improved on what was there
        tb = b2[win]
        ns[tb] = s2[win]; bc[tb] = c; bb[tb] = live[win]
    best, ssum = nb, ns; back_c.append(bc); back_b.append(bb)
arc = float(delta_arc)
inarc = np.nonzero((best < INF) & (ssum < arc))[0]
print(f"buckets reached {int((best < INF).sum())}; in the arc {len(inarc)}; best first-order score {int(best[inarc].min()) + n0 if len(inarc) else None}")
def reconstruct(b):
    cls = []
    for t in range(m - 1, -1, -1):
        c = int(back_c[t][b]); cls.append(c); b = int(back_b[t][b])
    return cls[::-1]
def crt(classes):
    N = 0; Mm = 2
    for (r, c) in classes:
        tt = ((c - N) * pow(Mm, -1, r)) % r; N += Mm * tt; Mm *= r
    return N
cands = sorted(inarc, key=lambda b: best[b])[:12]
seen = set()
for b in cands:
    cls = reconstruct(b); full = [(r, c) for (r, _, _), c in zip(coords, cls)]
    N = crt(full)
    if N in seen: continue
    seen.add(N)
    changed = [(r, a, c) for (r, a), c in zip(cov, cls[:len(cov)]) if c != a]
    exact_rows = len(rows_of(full))
    cover_rows = len(rows_of(full[:len(cov)]))
    print(f"  N < 10^200: {N < X}, {len(str(N))} digits; first-order {int(best[b]) + n0}, exact rows left after all {len(full)} primes {exact_rows}; its cover has {cover_rows} rows, {len(changed)} classes changed {changed}; later classes hit {[int(-coords[len(cov) + i][2][cls[len(cov) + i]]) for i in range(j)]}")
# what the cover's own window holds: brute force over k
Mcov = 2 * math.prod(r for r, _ in cov); N0 = crt(cov); K = (X - 1 - N0) // Mcov + 1
k = np.arange(K, dtype=np.int64); tot = np.zeros(K, dtype=np.int32)
for i, s in enumerate(later):
    cnt = np.bincount(R0 % s, minlength=s).astype(np.int32)
    tot += cnt[(N0 % s + (k % s) * (Mcov % s)) % s]
print(f"the cover's window: {K} members; most rows hit by these {j} primes (with multiplicity): {int(tot.max())} -> at most {n0 - int(tot.max())} left to first order; mean {tot.mean():.2f}")
