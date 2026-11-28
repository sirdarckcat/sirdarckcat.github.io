# Exact density of states of "rows left" on a small instance, for checking the sampler
# (idea 2 of the brainstorm: can the entropy estimate miss a rare ordered minimum?).
#   rows = odd primes below Q0, moduli = the first NM odd primes, all nonzero residue vectors.
#   usage: python3 -I exact_small.py Q0 NM OUT.json
import sys, math, json, itertools, time
import numpy as np
Q0, NM, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
allp = [int(x) for x in primes_upto(max(Q0, 200)) if x >= 3]
P = np.array([q for q in allp if q < Q0], dtype=np.int64); n = len(P); W = (n + 63) // 64
mods = allp[:NM]
def pack(mask):
    b = np.zeros(W * 64, dtype=np.uint8); b[:n] = mask
    return np.packbits(b.reshape(W, 64), axis=1, bitorder="little").view(np.uint64).reshape(W)
tab = {r: np.array([pack(P % r != c) for c in range(1, r)]) for r in mods}      # survivors of class c
head, tail = mods[:-3], mods[-3:]
T = (tab[tail[0]][:, None, None, :] & tab[tail[1]][None, :, None, :] & tab[tail[2]][None, None, :, :]).reshape(-1, W)
hist = np.zeros(n + 1, dtype=np.int64); best = (n + 1, None); t0 = time.time()
shape_tail = (tail[0] - 1, tail[1] - 1, tail[2] - 1)
for combo in itertools.product(*[range(r - 1) for r in head]):
    m = tab[head[0]][combo[0]].copy()
    for r, c in zip(head[1:], combo[1:]): m &= tab[r][c]
    cnt = np.bitwise_count(T & m).sum(axis=1)
    hist += np.bincount(cnt, minlength=n + 1)
    j = int(cnt.argmin())
    if cnt[j] < best[0]:
        tl = np.unravel_index(j, shape_tail)
        best = (int(cnt[j]), [c + 1 for c in combo] + [int(x) + 1 for x in tl])
tot = int(hist.sum()); ks = np.nonzero(hist)[0]
print("Q0 = %d, %d rows, moduli %s, %d vectors, %.0f s" % (Q0, n, mods, tot, time.time() - t0))
print("exact minimum of rows left: %d at classes %s; number of vectors at the minimum: %d" % (best[0], best[1], int(hist[best[0]])))
print("exact mean %.2f, sd %.2f" % ((hist * np.arange(n + 1)).sum() / tot, math.sqrt((hist * np.arange(n + 1) ** 2).sum() / tot - ((hist * np.arange(n + 1)).sum() / tot) ** 2)))
cum = np.cumsum(hist)
print("k : number of vectors with exactly k rows : ln(number with at most k)")
for k in ks[:14]: print("  %4d : %10d : %7.3f" % (k, hist[k], math.log(cum[k])))
json.dump({"Q": Q0, "mods": mods, "hist": hist.tolist(), "best": best, "cover": [[r, c] for r, c in zip(mods, best[1])]}, open(OUT, "w"))
