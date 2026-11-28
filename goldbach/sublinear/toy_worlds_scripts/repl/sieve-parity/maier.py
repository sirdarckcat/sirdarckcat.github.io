#!/usr/bin/env python3
"""(b) Maier / Buchstab: the real cover against the product of local densities, common-integer (Maier) covers by FFT,
   the Buchstab curve of common-integer covers, alignment of the real cover with a common integer, Erdos-Rankin hybrids."""
import sys, math, numpy as np
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
Q = 200000
f = cr.S + "q200000_m89.txt"
line = [x for x in open(f) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
mods = [r for r, a in cov]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
PR = primes_upto(Q - 1); PR = PR[PR > 2]            # odd primes below Q: the candidate rows
print("odd primes below Q:", len(PR))
# 1. product prediction and trajectory
alive = np.ones(len(PR), dtype=bool); pred = float(len(PR)); EG = math.exp(0.5772156649015329)
print("\n1. real cover, primes in ascending order: rows left | product prediction | ratio | this prime: struck, expected n/(r-1), z")
for r, a in cov:
    n0 = int(alive.sum()); hit = alive & (PR % r == a); alive &= ~hit
    # among rows not equal to r, classes 1..r-1 equally likely: expected n0/(r-1)
    exp = n0 / (r - 1); pred *= (1 - 1 / (r - 1))
    if r in (3, 5, 7, 11, 13, 23, 47, 97, 199, 293, 397, 463):
        print(f"   r={r:3d}: {int(alive.sum()):6d} | {pred:9.1f} | {alive.sum() / pred:.4f} | {int(hit.sum())}, {exp:.1f}, {(hit.sum() - exp) / math.sqrt(exp):+.2f}")
rows_real = int(alive.sum())
print(f"   final rows {rows_real}; product prediction pi(Q)*prod(1-1/(r-1)) = {pred:.1f}; ratio {rows_real / pred:.4f}; e^gamma/2 = {EG / 2:.4f}")
# excess decomposition: sum of z-scores
# 2. common-integer covers by FFT: count(R) = #{q odd prime < Q : R - q has no prime factor r <= 463 (odd)}
L = 1 << 24
def rough_indicator(lo, n, mods):
    """indicator for m in [lo, lo+n) that no odd prime in mods divides m"""
    ind = np.ones(n, dtype=bool)
    for r in mods:
        ind[(-lo) % r::r] = False
    return ind
def aligned_counts(Rlo, nR, Qx, mods, PRx):
    """counts for R in [Rlo, Rlo+nR): number of primes q in PRx with R - q rough"""
    lo = Rlo - Qx; n = nR + Qx
    ind = rough_indicator(lo, n, mods).astype(np.float64)       # m = lo + i
    pri = np.zeros(Qx, dtype=np.float64); pri[PRx] = 1
    size = 1 << int(math.ceil(math.log2(n + Qx)))
    F = np.fft.irfft(np.fft.rfft(ind, size) * np.fft.rfft(pri, size), size)
    # (ind * pri)[t] = sum_q ind[t - q] -> m = lo + t - q = R - q  => R = lo + t
    t = np.arange(nR) + Qx
    return np.rint(F[t]).astype(np.int64)
print("\n2. common-integer (Maier) covers: classes a_r = R mod r for all 89 primes")
best = (10 ** 9, None); tot = 0; cnt = 0; hist = []
for Rlo in range(-8_000_000, 8_000_000, 4_000_000):
    c = aligned_counts(Rlo, 4_000_000, Q, mods, PR)
    i = int(c.argmin()); tot += c.sum(); cnt += len(c); hist.append(c)
    if c[i] < best[0]: best = (int(c[i]), Rlo + i)
c = np.concatenate(hist); Rs = np.arange(-8_000_000, 8_000_000)
print(f"   R in [-8e6, 8e6): mean {c.mean():.1f}, sd {c.std():.1f}, min {best[0]} at R = {best[1]}")
# direct check of the best
R = best[1]; chk = sum(1 for q in PR if all((R - int(q)) % r for r in mods)); print("   direct recount of the minimum:", chk)
far = np.abs(Rs) > 2_000_000
print(f"   |R| > 2e6 only: mean {c[far].mean():.1f}, sd {c[far].std():.1f}, min {c[far].min()}  (z of min: {(c[far].min() - c[far].mean()) / c[far].std():.2f})")
for lo, hi in ((0, Q), (Q, 220000), (Q, 300000), (300000, 500000), (500000, 1000000)):
    s = (Rs >= lo) & (Rs < hi); print(f"   R in [{lo},{hi}): mean {c[s].mean():.1f}  min {c[s].min()} at {Rs[s][c[s].argmin()]}")
# 3. alignment of the real cover with a common integer: agreements #{r : a_r = R mod r}
print("\n3. is the real cover a Maier cover in disguise? agreements #{r: R = a_r mod r}, R in [-8e6, 8e6)")
ag = np.zeros(16_000_000, dtype=np.int8)
for r, a in cov: ag[(a + 8_000_000) % r::r] += 1
print(f"   real cover: mean {ag.mean():.3f} (sum 1/r = {sum(1 / r for r in mods):.3f}), max {ag.max()}, histogram of the top: {np.bincount(ag)[-4:]}")
rng = np.random.default_rng(5); mx = []
for t in range(10):
    ag2 = np.zeros(16_000_000, dtype=np.int8)
    for r in mods: ag2[int(rng.integers(r))::r] += 1
    mx.append(int(ag2.max()))
print("   10 random class vectors: max agreements", mx)
# weighted: rows of the Maier cover R that the real cover also strikes etc. is not needed.
# 4. Buchstab curve of the common-integer cover: rows(R, Q') / product prediction for R just above Q', y = 463 fixed
print("\n4. Buchstab curve: common-integer covers at other Q' (moduli: the 89 odd primes to 463), R in [Q', Q'+20000), R even with no prime factor <= 463 beyond 2")
print("   Q' | u = ln Q'/ln 463 | mean rows/product over such R | e^gamma*omega(u) | min ratio")
def omega(u):
    if u <= 2: return 1 / u
    if u <= 3: return (1 + math.log(u - 1)) / u
    return float("nan")
for Qx in (20000, 50000, 100000, 150000, 200000, 300000, 500000, 1000000, 3000000):
    PRx = primes_upto(Qx - 1); PRx = PRx[PRx > 2]
    predx = len(PRx)
    for r in mods: predx *= (1 - 1 / (r - 1))
    cx = aligned_counts(Qx, 20000, Qx, mods, PRx)
    Rx = np.arange(Qx, Qx + 20000)
    good = (Rx % 2 == 0)
    for r in mods: good &= (Rx % r != 0)
    u = math.log(Qx) / math.log(463)
    print(f"   {Qx:8d} | {u:.3f} | {cx[good].mean() / predx:.4f} | {EG * omega(u):.4f} | {cx.min() / predx:.4f}")
# 5. Erdos-Rankin hybrids: a common integer on a block of moduli, greedy on the others (ascending), against greedy on all
print("\n5. Erdos-Rankin hybrids against plain greedy (same greedy rule on the free moduli; no local search)")
def greedy(alive, free, order="asc"):
    alive = alive.copy()
    for r in (sorted(free) if order == "asc" else sorted(free, reverse=True)):
        q = PR[alive]; b = np.bincount(q % r, minlength=r); b[0] = 0
        a = int(b.argmax()); alive[alive] = (q % r) != a
    return int(alive.sum())
base = np.ones(len(PR), dtype=bool)
g_asc = greedy(base, mods, "asc"); g_desc = greedy(base, mods, "desc")
print(f"   plain greedy: ascending {g_asc}, descending {g_desc}; real cover {rows_real}")
rng = np.random.default_rng(11)
for lo, hi in ((100, 463), (200, 463), (300, 463), (30, 463), (30, 200), (100, 300)):
    block = [r for r in mods if lo < r <= hi]; free = [r for r in mods if not (lo < r <= hi)]
    res = []
    cand = np.concatenate([np.arange(Q, Q + 600, 2), rng.integers(Q, 4 * Q, 300) * 2 // 2])
    # stage 1: rows left by the block alone for many R (cheap), keep the 12 best R, then greedy
    left = []
    for R in cand:
        al = base.copy()
        for r in block: al &= (PR % r) != (int(R) % r)
        left.append(int(al.sum()))
    left = np.array(left); orderR = np.argsort(left)[:12]
    rand_block = len(PR) * math.prod(1 - 1 / (r - 1) for r in block)
    for i in orderR:
        R = int(cand[i]); al = base.copy()
        for r in block: al &= (PR % r) != (R % r)
        res.append((greedy(al, free, "asc"), R, left[i]))
    res.sort()
    print(f"   block ({lo},{hi}] ({len(block)} moduli): block alone leaves {left.min()} at best, {np.median(left):.0f} median (product {rand_block:.0f}); best hybrid total {res[0][0]} (R = {res[0][1]}), median of 12: {sorted(x[0] for x in res)[6]}")
