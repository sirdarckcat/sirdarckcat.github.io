"""How many windows of the miniature can no free bound exclude, as the number of primes beyond the line grows?

For a cell c (class vector modulo 3..23, left rows R_c) and the first b later primes:
  LB_b(c)  = the least number of rows any class vector of those primes leaves of R_c (no member of c does better);
  a cell with LB_b(c) < OPT_b cannot be excluded without looking at it.
LB is bracketed by  the relaxation  |R_c| - sum_s max_a K_s(a)  (each prime strikes its fullest class of R_c, overlaps
ignored)  <=  LB  <=  the greedy choice (each prime in turn takes the class with the most rows still left).
On a random sample of cells: the share of cells that cannot be excluded (between the greedy and the relaxed count).
OPT_b is read from miniature_full.txt (tiny.c)."""
import math, sys
import numpy as np
def primes_upto(m):
    s = np.ones(m + 1, dtype=bool); s[:2] = False
    for i in range(2, int(m ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
ROWS = [p for p in primes_upto(999) if p > 2]; SP = [p for p in primes_upto(199) if p > 2]; COVER = [p for p in SP if p <= 23]; DEEP = [p for p in SP if p > 23]
def mask(s):
    m = np.zeros((s, 3), dtype=np.uint64)
    for j, q in enumerate(ROWS): m[q % s, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
    return m
def pc(x): return np.bitwise_count(x).sum(axis=-1).astype(np.int64)
OPT = {}
for line in open("miniature_full.txt"):
    t = [x.strip() for x in line.split("|")]
    if len(t) > 3 and t[1].isdigit(): OPT[int(t[1])] = int(t[2].split()[0])
M0 = 223092870; rng = np.random.default_rng(31); ncell = 200000
N0 = 2 * rng.integers(0, M0 // 2, size=ncell, dtype=np.int64)
left = np.zeros((ncell, 3), dtype=np.uint64)
for j in range(len(ROWS)): left[:, j >> 6] |= np.uint64(1) << np.uint64(j & 63)
for s in COVER: left &= ~mask(s)[N0 % s]
L = pc(left); cur = left.copy(); relax = L.copy()
print(f"# {ncell:,d} random cells of the miniature (all class vectors modulo 3..23, zero classes included); rows left by the cover: mean {L.mean():.1f}")
print("primes beyond the line (depth) | OPT | share of cells with greedy score < OPT (cannot be excluded: lower count) | share with relaxed bound < OPT (upper count) | mean greedy score | mean relaxed bound")
for b, s in enumerate(DEEP, 1):
    m = mask(s); best = np.zeros(ncell, dtype=np.int64); bestc = np.zeros(ncell, dtype=np.int64); mx = np.zeros(ncell, dtype=np.int64)
    for a in range(s):
        k = pc(cur & m[a]); upd = k > best; best[upd] = k[upd]; bestc[upd] = a
        mx = np.maximum(mx, pc(left & m[a]))
    cur &= ~m[bestc]; relax = relax - mx; G = pc(cur)
    if b <= 12 or b in (15, 20, 25, 30, 37):
        print(f"{b} ({s}) | {OPT[b]} | {(G < OPT[b]).mean():.4f} | {(np.maximum(relax, 0) < OPT[b]).mean():.4f} | {G.mean():.2f} | {np.maximum(relax, 0).mean():.2f}", flush=True)
