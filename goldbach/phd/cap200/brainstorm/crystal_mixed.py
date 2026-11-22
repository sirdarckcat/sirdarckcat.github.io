# Idea 1 of the brainstorm: "mixed crystals". One constant c for every modulus in (z, 461]
# (N = c there), free classes on the moduli <= z, chosen by coordinate descent from several starts.
#   usage: python3 -I crystal_mixed.py POOL.json CMAX
import json, sys, math
import numpy as np
d = json.load(open(sys.argv[1])); CMAX = int(sys.argv[2])
Q = d["Q"]; mods = sorted(int(r) for r in d["mods"]); kbest = d["pool"][0][0]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes_upto(Q - 1); P = P[P >= 3].astype(np.int64)
rng = np.random.default_rng(3)
def descend(U, small, starts=3):
    best = None
    for st in range(starts):
        cls = {r: int(rng.integers(1, r)) for r in small}
        res = {r: U % r for r in small}
        cnt = np.zeros(len(U), dtype=np.int16)
        for r in small: cnt += (res[r] == cls[r])
        improved = True
        while improved:
            improved = False
            for r in small:
                cnt -= (res[r] == cls[r])
                n = np.bincount(res[r][cnt == 0], minlength=r)[1:]
                new = 1 + int(n.argmax())
                if n[new - 1] > n[cls[r] - 1]: improved = True; cls[r] = new
                cnt += (res[r] == cls[r])
        k = int((cnt == 0).sum())
        if best is None or k < best: best = k
    return best
print("Q = %d, %d rows; sampler optimum on all %d moduli: %d rows; random classes: about %d" % (Q, len(P), len(mods), kbest, round(len(P) * math.prod(1 - 1 / (r - 1) for r in mods))))
for z in (13, 31, 61, 101):
    small = [r for r in mods if r <= z]; big = [r for r in mods if r > z]
    out = []
    for c in range(-CMAX, CMAX + 1):
        alive = np.ones(len(P), dtype=bool)
        for r in big: alive &= ((P - c) % r != 0)            # row q is covered iff r | q - c
        out.append((descend(P[alive], small), c, int(alive.sum())))
    out.sort()
    print("z = %3d (%d free moduli, %d crystal moduli): best %d rows at c = %d; next %s; median over c %d" % (
        z, len(small), len(big), out[0][0], out[0][1], [(k, c) for k, c, _ in out[1:4]], out[len(out) // 2][0]))
    sys.stdout.flush()
