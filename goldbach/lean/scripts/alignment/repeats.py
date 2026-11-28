"""More strikes, or fewer repeated strikes?  (asked by the research session for the true optima)

For a member: L = rows its cover left (depth 23); for each later prime s, K_s = how many of those L rows lie in the
class of N modulo s (strikes of s on the left rows); I = sum of the K_s (incidences); U = distinct rows struck
(= k1 - k2); repeats = I - U.  If the K_s strikes of every prime fell on a random K_s-subset of the L rows,
independently for different primes, the expected number of distinct rows would be
   U0 = L (1 - prod_s (1 - K_s / L)).
The advantage of a tier over members with the same cover quality, U(tier) - U(controls), splits into
   more strikes        U0(tier) - U0(controls)          (what its incidences give with chance overlaps)
   fewer repeats       (U - U0)(tier) - (U - U0)(controls).
  python repeats.py"""
import math, os, sys
import numpy as np
D = os.environ.get("PPRIME_DATA", "../pprime_families/data")
N = np.memmap(f"{D}/N.u32", dtype=np.uint32, mode="r"); k1 = np.asarray(np.memmap(f"{D}/k1.u8", dtype=np.uint8, mode="r")); k2 = np.asarray(np.memmap(f"{D}/k2.u8", dtype=np.uint8, mode="r"))
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = [p for p in primes_upto(999) if p > 2]; SP = [p for p in primes_upto(199) if p > 2]; COVER = [p for p in SP if p <= 23]; DEEP = [p for p in SP if p > 23]
MASK = {}
for s in SP:
    m = np.zeros((s, 3), dtype=np.uint64)
    for j, q in enumerate(ROWS): m[q % s, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    MASK[s] = m
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.float64)
def stats(nn):
    left = np.zeros((len(nn), 3), dtype=np.uint64)
    for j in range(len(ROWS)): left[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    for s in COVER: left &= ~MASK[s][nn % s]
    L = pc(left); cur = left.copy(); I = np.zeros(len(nn)); logprod = np.zeros(len(nn))
    for s in DEEP:
        cm = MASK[s][nn % s]; K = pc(left & cm); I += K; logprod += np.log1p(-np.minimum(K / L, 1 - 1e-12)); cur &= ~cm
    U = L - pc(cur); U0 = L * (1 - np.exp(logprod))
    return L, I, U, U0
rng = np.random.default_rng(12)
print("set | members | rows left by the cover L | incidences I of the later classes on them | distinct rows struck U | repeats I - U | distinct expected with chance overlaps U0 | repeats expected | U - U0")
def line(name, nn):
    L, I, U, U0 = stats(nn)
    print(f"{name} | {len(nn):,d} | {L.mean():.2f} | {I.mean():.2f} | {U.mean():.2f} | {(I - U).mean():.2f} | {U0.mean():.2f} | {(I - U0).mean():.2f} | {(U - U0).mean():+.2f}", flush=True)
    return L.mean(), I.mean(), U.mean(), U0.mean()
out = {}
for t in (6, 7, 8, 9, 10, 12):
    idx = np.nonzero(k2 <= t)[0]; nt = np.asarray(N[idx]).astype(np.int64)
    a = line(f"tier k2 <= {t}", nt)
    h = np.bincount(k1[idx], minlength=64) / len(idx); ctrl = []
    for c in np.unique(k1[idx]):
        pool = np.nonzero(k1 == c)[0]; want = int(round(200000 * h[c]))
        if want: ctrl.append(rng.choice(pool, size=min(want, len(pool)), replace=False))
    c_ = line(f"  members with the same k1", np.asarray(N[np.sort(np.concatenate(ctrl))]).astype(np.int64))
    out[t] = (a, c_)
print("\ntier | advantage in distinct rows over members with the same cover | of which more strikes | fewer repeats | share of fewer repeats")
for t, (a, c) in out.items():
    adv = a[2] - c[2]; more = a[3] - c[3]; fewer = (a[2] - a[3]) - (c[2] - c[3])
    print(f"k2 <= {t} | {adv:.2f} | {more:.2f} | {fewer:.2f} | {fewer / adv:.2f}")
