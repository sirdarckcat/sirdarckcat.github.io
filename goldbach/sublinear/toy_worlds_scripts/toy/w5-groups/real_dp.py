#!/usr/bin/env python3
"""The rounded dynamic programme over partial sums (Theorem 3) on the real 200,000 cover with j later primes.

    python3 real_dp.py j sigma [eps = 1] [frozen]

Lists every N < 10^200 whose first-order score is within sigma rows of the unconstrained optimum, over all class vectors
(cover classes of cost <= sigma, later classes of deficit <= sigma: no other class can occur in such a point).
State: sum of rho_i(c_i) mod B, rho_i(c) = floor(B * frac((c - base_i) u_i / r_i)), base = the residues of N0 (the cover's
first member), u_i = (P/r_i)^-1 mod r_i, P = M * T.  A point with at most E coordinates off the base has
B*(x - N0)/P - E < sum rho <= B*(x - N0)/P (mod B), so the targets are the integers in (-B N0/P - E, B (X - N0)/P).
E = sigma + z0 + j (z0 = cover primes with a second class at cost 0), B = ceil(E P / (eps X)).
`frozen`: cover classes fixed (the cover's own window), for the brute-force comparison.
Compares its output with the meet in the middle's (mitm_j{j}_s{sigma}_k{sigma}.pkl) when that file exists."""
import sys, math, time, pickle, os, numpy as np
from fractions import Fraction
import common as C
j = int(sys.argv[1]); sigma = int(sys.argv[2]); eps = Fraction(sys.argv[3]) if len(sys.argv) > 3 else Fraction(1)
frozen = len(sys.argv) > 4 and sys.argv[4] == "frozen"
t0 = time.time()
js = C.later_primes(j); T = math.prod(js); M = C.M; X = C.X; N0 = C.N0; P = M * T
D = math.log(P) - math.log(X)
ct = C.cover_tables(); lt = C.later_tables(js); Gmax = sum(int(lt[s].max()) for s in js)
z0 = 0 if frozen else sum(1 for r, a in C.cov if (ct[r] <= 0).sum() > 1)
E = (0 if frozen else sigma + z0) + j
B = int(math.ceil(Fraction(E * P, 1) / (eps * X)))
INF = sigma + 1
coords = []                                           # (modulus, classes, rho, cost, idempotent-difference big ints)
def add_coord(r, base, classes, costs):
    u = pow(P // r % r, -1, r); e = (P // r) * u      # idempotent of r in Z/P
    rho = np.array([(B * (((int(c) - base) * u) % r)) // r for c in classes], dtype=np.int64)
    coords.append((r, np.array(classes), rho, np.array(costs, dtype=np.int64), [((int(c) - base) * e) % P for c in classes]))
if not frozen:
    for r, a in C.cov:
        cl = [c for c in range(r) if ct[r][c] <= sigma]
        if len(cl) > 1: add_coord(r, a, cl, [int(ct[r][c]) for c in cl])
for s in js:
    d = lt[s].max() - lt[s]; cl = [c for c in range(s) if d[c] <= sigma]
    add_coord(s, N0 % s, cl, [int(d[c]) for c in cl])
ncls = sum(len(c[1]) for c in coords)
print(f"j = {j}, sigma = {sigma}, eps = {eps}{', cover frozen' if frozen else ''}: D = {D:.4f}, e^D = {math.exp(D):.4g}; E = {E}; states B = {B} = {B / math.exp(D):.2f} e^D; "
      f"coordinates with a choice {len(coords)}, classes kept {ncls}; transitions B * classes = {B * ncls:.4g}")
V = [np.full(B, INF, dtype=np.uint8)]; V[0][0] = 0
tmp = np.empty(B, dtype=np.uint8)
for (r, cl, rho, cost, eb) in coords:
    old = V[-1]; new = np.full(B, INF, dtype=np.uint8)
    for off, cs in zip(rho.tolist(), cost.tolist()):
        if off == 0:
            np.add(old, cs, out=tmp); np.minimum(new, tmp, out=new)
        else:
            np.add(old[:B - off], cs, out=tmp[:B - off]); np.minimum(new[off:], tmp[:B - off], out=new[off:])
            np.add(old[B - off:], cs, out=tmp[:off]); np.minimum(new[:off], tmp[:off], out=new[:off])
    np.minimum(new, INF, out=new); V.append(new)
tdp = time.time() - t0
lo = math.floor(Fraction(-B * N0, P) - E) + 1; hi = math.ceil(Fraction(B * (X - N0), P)) - 1
targets = sorted({n % B for n in range(lo, hi + 1)})
exact_arc = Fraction(B * X, P)
best_relaxed = min(int(V[-1][b]) for b in targets)
print(f"forward pass {tdp:.1f} s; target buckets {len(targets)} (the arc itself is {float(exact_arc):.2f} buckets); least excess over the relaxed set: {best_relaxed if best_relaxed < INF else '> sigma'}")
# ---- list every point of the relaxed set with excess <= sigma, backwards through the stored tables
sols = []; nodes = 0
def rec(t, b, budget, acc):
    global nodes
    nodes += 1
    if t == 0:
        if b == 0: sols.append(acc)
        return
    r, cl, rho, cost, eb = coords[t - 1]
    prev = (b - rho) % B
    ok = np.nonzero((cost <= budget) & (V[t - 1][prev] <= budget - cost))[0]
    for i in ok.tolist(): rec(t - 1, int(prev[i]), budget - int(cost[i]), acc + eb[i])
sys.setrecursionlimit(10000)
for b in targets:
    if V[-1][b] <= sigma: rec(len(coords), b, sigma, 0)
tl = time.time() - t0 - tdp
feas = []; outside = 0
for acc in sols:
    x = (N0 + acc) % P
    if x < X: feas.append(x)
    else: outside += 1
hist = {}
for x in feas:
    s = C.n0 + sum(int(ct[r][x % r]) for r, _ in C.cov) - sum(int(lt[s_][x % s_]) for s_ in js); hist[s] = hist.get(s, 0) + 1
print(f"listing {tl:.1f} s: relaxed points listed {len(sols)} ({nodes} nodes visited, {nodes / max(1, len(sols)):.1f} per point); below X {len(feas)}, outside {outside} (overhead {len(sols) / max(1, len(feas)):.3f})")
print("feasible points by first-order score:", dict(sorted(hist.items())))
assert len(set(feas)) == len(feas)
f = f"mitm_j{j}_s{sigma}_k{sigma}.pkl"
if os.path.exists(f) and not frozen:
    mm = {x for s, x in pickle.load(open(f, "rb"))}
    print(f"meet in the middle listed {len(mm)} points; identical sets: {mm == set(feas)}")
if frozen:
    print("deficit counts 0..sigma (compare with the brute force over the cover's own window):", [hist.get(C.n0 - Gmax + d, 0) for d in range(sigma + 1)])
print(f"COST: B * classes = {B * ncls:.4g} = {B * ncls / math.exp(D):.4g} e^D; outputs {len(feas)}; total time {time.time() - t0:.1f} s")
