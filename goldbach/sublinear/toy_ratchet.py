#!/usr/bin/env python3
"""Pin the luck: an adaptive search on a small exact instance of the alignment problem, against cover first at equal work.

    python3 toy_ratchet.py log10(X) Q z budget [seed] [largest cover prime for the comparison]
    e.g. python3 toy_ratchet.py 15 3000 1000 4e5 1 31

Even N < X; rows = the odd primes q < Q; a row is struck when a prime s <= z divides N - q; the score of N is the rows
left at depth z.  A, cover first: the best class vectors on the smallest primes, each with its whole window.  B, the
ratchet: from the best member A found with half the budget, pin the primes where that number's class is worth most
per nat (any primes up to z, chosen greedily by marginal rows struck beyond a random class), score J numbers that
agree with it on them, move to the best, repeat: the pins follow the luck instead of the size of the prime.
"""
import sys, math, random
import numpy as np
X = 10 ** int(sys.argv[1]); Q = int(sys.argv[2]); z = int(sys.argv[3]); BUDGET = int(float(sys.argv[4])); seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rng = random.Random(seed); nprng = np.random.default_rng(seed)
def primes(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
rows = [q for q in primes(Q - 1) if q > 2]; nrows = len(rows); S = [s for s in primes(z) if s > 2]
NW = (nrows + 63) // 64
# mask[s][c] = bitmask (NW words) of rows q with q = c (mod s)
masks = {}
for s in S:
    m = np.zeros((s, NW), dtype=np.uint64)
    for i, q in enumerate(rows): m[q % s, i // 64] |= np.uint64(1) << np.uint64(i % 64)
    masks[s] = m
POP = np.array([bin(i).count("1") for i in range(65536)], dtype=np.int32)
def popcount(a):
    a = a.copy(); c = np.zeros(a.shape[:-1], dtype=np.int32)
    for sh in (0, 16, 32, 48): c += POP[((a >> np.uint64(sh)) & np.uint64(0xFFFF)).astype(np.int64)].sum(axis=-1)
    return c
def score_many(base, step, J):
    """rows left at depth z for N = base + j*step, j < J (python ints for base and step)"""
    killed = np.zeros((J, NW), dtype=np.uint64); j = np.arange(J, dtype=np.int64)
    for s in S:
        r = (base % s + j * (step % s)) % s
        killed |= masks[s][r]
    return nrows - popcount(killed)
def classes(N): return {s: N % s for s in S}
def exclusive(N):
    """for each prime s: rows struck by s and by no other prime <= z"""
    cnt = np.zeros(nrows, dtype=np.int32); per = {}
    for s in S:
        b = np.array([(int(masks[s][N % s, i // 64]) >> (i % 64)) & 1 for i in range(nrows)], dtype=np.int32); per[s] = b; cnt += b
    return {s: int(((cnt == 1) & (per[s] == 1)).sum()) for s in S}, {s: int(per[s].sum()) for s in S}
# ---------- A: cover first ----------
def cover_first(budget, pc):
    Sc = [s for s in S if s <= pc]; M = 2
    for s in Sc: M *= s
    W = X // M
    if W < 1: return None
    # exhaustive/greedy+random-restart search for good class vectors on Sc (rows left at depth pc)
    best = []
    def left(cl):
        k = np.zeros(NW, dtype=np.uint64)
        for s, c in cl.items(): k |= masks[s][c]
        return nrows - int(popcount(k[None, :])[0])
    for rest in range(200):
        cl = {s: rng.randrange(1, s) for s in Sc}; cur = left(cl); improved = True
        while improved:
            improved = False
            for s in Sc:
                for c in range(1, s):
                    if c == cl[s]: continue
                    old = cl[s]; cl[s] = c; v = left(cl)
                    if v < cur: cur = v; improved = True
                    else: cl[s] = old
        best.append((cur, tuple(sorted(cl.items()))))
    best = sorted(set(best)); used = 0; res = []; ci = 0
    while used < budget and ci < len(best):
        cur, cl = best[ci]; ci += 1
        # CRT
        N0 = 0; mod = 2
        for s, c in cl:
            t = ((c - N0) * pow(mod, -1, s)) % s; N0 += t * mod; mod *= s
        J = int(min(W, budget - used)); sc = score_many(N0, M, J); used += J; res.append(sc)
    allsc = np.sort(np.concatenate(res)); return pc, len(Sc), W, best[0][0], used, allsc
# ---------- B: ratchet from the best member cover-first found ----------
def rowbits(N, s): return masks[s][N % s]
def pinset(N, J):
    """greedy: add the prime whose class at N strikes the most not-yet-struck rows beyond what a random class would, per nat"""
    struck = np.zeros(NW, dtype=np.uint64); M = 2; T = []; cand = set(S)
    while True:
        alive = nrows - int(popcount(struck[None, :])[0]); best = None
        for s in cand:
            if M * s * J > X: continue
            new = int(popcount((rowbits(N, s) & ~struck)[None, :])[0]); val = (new - alive / s) / math.log(s)
            if best is None or val > best[0]: best = (val, s)
        if best is None or best[0] <= 0: break
        s = best[1]; struck |= rowbits(N, s); M *= s; T.append(s); cand.discard(s)
    return M, T
def ratchet_from(N0, s0, budget, J):
    used = 0; bestN, bests = N0, s0; scores = []; stall = 0; trail = []
    while used < budget and stall < 40:
        M, T = pinset(bestN, J); base = bestN % M; Jr = int(min(X // M, max(J, 1), budget - used))
        if Jr < 2: break
        off = rng.randrange(0, max(1, X // M - Jr + 1)) if X // M > Jr else 0
        sc = score_many(base + off * M, M, Jr); used += Jr; scores.append(sc); i = int(np.argmin(sc))
        if sc[i] < bests: bests = int(sc[i]); bestN = base + (off + i) * M; stall = 0; trail.append((used, bests, len(T), max(T)))
        else: stall += 1
    allsc = np.sort(np.concatenate(scores)) if scores else np.array([s0]); return bests, used, allsc, trail
print(f"X = 10^{sys.argv[1]}, Q = {Q} ({nrows} rows), depth {z} ({len(S)} primes), budget {BUDGET} scored candidates, seed {seed}")
print("A cover first: primes pinned up to | moduli | window | best cover's rows at its own depth | scored | best, 10th best, 100th best rows left at depth z")
for pc in (19, 23, 29, 31, 37, 41):
    r = cover_first(BUDGET, pc)
    if r is None: continue
    pc_, n, W, b0, used, a = r
    print(f"  {pc_} | {n} | {W} | {b0} | {used} | {a[0]}, {a[min(9, len(a) - 1)]}, {a[min(99, len(a) - 1)]}", flush=True)
# equal total work: A alone with the whole budget against A with half followed by the ratchet from its best member
pc = int(sys.argv[6]) if len(sys.argv) > 6 else 31
rA = cover_first(BUDGET, pc); rH = cover_first(BUDGET // 2, pc)
print(f"A alone, {rA[4]} scored: best {rA[5][0]}, 10th {rA[5][9]}, 100th {rA[5][99]}")
# recover the best member of the half-budget scan: rescan to find it
Sc = [x for x in S if x <= pc]; M = 2
for x in Sc: M *= x
def best_member(budget):
    best = (10 ** 9, None)
    # same covers as cover_first would use: recompute quickly with a fresh search
    rr = random.Random(seed)
    def left(cl):
        k = np.zeros(NW, dtype=np.uint64)
        for ss, c in cl.items(): k |= masks[ss][c]
        return nrows - int(popcount(k[None, :])[0])
    cands = []
    for rest in range(60):
        cl = {x: rr.randrange(1, x) for x in Sc}; cur = left(cl); imp = True
        while imp:
            imp = False
            for x in Sc:
                for c in range(1, x):
                    if c == cl[x]: continue
                    old = cl[x]; cl[x] = c; v = left(cl)
                    if v < cur: cur = v; imp = True
                    else: cl[x] = old
        cands.append((cur, tuple(sorted(cl.items()))))
    cands = sorted(set(cands)); used = 0
    for cur, cl in cands:
        if used >= budget: break
        N0 = 0; mod = 2
        for x, c in cl:
            t = ((c - N0) * pow(mod, -1, x)) % x; N0 += t * mod; mod *= x
        J = int(min(X // M, budget - used)); sc = score_many(N0, M, J); used += J; i = int(np.argmin(sc))
        if sc[i] < best[0]: best = (int(sc[i]), N0 + i * M)
    return best
b0, N0 = best_member(BUDGET // 2)
print(f"A with half the budget: best member has {b0} rows left")
for J in (256, 2048, 16384):
    b, used, a, trail = ratchet_from(N0, b0, BUDGET // 2, J)
    print(f"  then the ratchet, {J} candidates a step, {used} scored: best {b}; improvements (scored so far, rows, primes pinned, largest pinned): {trail[:6]}", flush=True)
