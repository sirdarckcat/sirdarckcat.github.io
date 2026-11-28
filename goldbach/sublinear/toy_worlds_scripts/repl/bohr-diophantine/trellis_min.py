#!/usr/bin/env python3
"""(b) Theorem C in miniature: the smallest read-once trellis of the window [0, K) in ANY coordinates that carries every
score sum_s f_s(k mod s), s in T.  Two partial paths may share a state iff they have the same completions and, for every s,
their residues agree on every completion or are both already determined (the condition proved necessary and sufficient
for edge weights to exist for all tables).  Edges of the minimal trellis are counted; the theorem says >= K when prod T >= K^2."""
import math, random, itertools
def min_trellis(K, T, coords):
    words = [tuple(c(k) for c in coords) for k in range(K)]
    if len(set(words)) < K:                      # complete the system with the quotient by prod T (residue systems with prod T < K)
        P = math.prod(T); coords = list(coords) + [lambda k: k // P]; words = [tuple(c(k) for c in coords) for k in range(K)]
    n = len(coords)
    assert len(set(words)) == K, "coordinates must separate the members"
    def keys(i):
        groups = {}
        for k in range(K): groups.setdefault(words[k][:i], []).append(k)
        key = {}
        for u, ks in groups.items():
            comp = tuple(sorted((words[k][i:], k) for k in ks))
            sig = []
            for s in T:
                res = tuple(k % s for _, k in comp)
                sig.append("C" if len(set(res)) == 1 else res)
            key[u] = (tuple(w for w, _ in comp), tuple(sig))
        return key
    prev = keys(0); E = 0; width = 1
    for i in range(1, n + 1):
        cur = keys(i); edges = set()
        for k in range(K): edges.add((prev[words[k][:i - 1]], words[k][i - 1]))
        E += len(edges); width = max(width, len(set(cur.values()))); prev = cur
    return E, width
def systems(K, T, rng):
    out = {}
    out["residues, increasing"] = [lambda k, s=s: k % s for s in T]
    out["residues, decreasing"] = [lambda k, s=s: k % s for s in reversed(T)]
    if len(T) >= 2:
        bl = [T[i] * T[i + 1] if i + 1 < len(T) else T[i] for i in range(0, len(T), 2)]
        out["blocks (products of two)"] = [lambda k, s=s: k % s for s in bl]
    nb = K.bit_length()
    out["binary digits, high first"] = [lambda k, b=b: (k >> b) & 1 for b in reversed(range(nb))]
    out["binary digits, low first"] = [lambda k, b=b: (k >> b) & 1 for b in range(nb)]
    out["base 5 digits, high first"] = [lambda k, b=b: (k // 5 ** b) % 5 for b in reversed(range(4))]
    out[f"mixed radix (k mod {T[0]}, quotient)"] = [lambda k: k % T[0], lambda k: k // T[0]]
    out["one-hot residues"] = [lambda k, s=s, c=c: int(k % s == c) for s in T for c in range(s)]
    out["binary digits then residues (redundant)"] = out["binary digits, high first"] + out["residues, increasing"]
    out["residues then binary digits (redundant)"] = out["residues, increasing"] + out["binary digits, high first"]
    out["tree of moduli laid out (s1, s1 s2, s2, s2 s3, ...)"] = [f for i in range(len(T)) for f in ([lambda k, s=T[i]: k % s] + ([lambda k, s=T[i] * T[i + 1]: k % s] if i + 1 < len(T) else []))]
    for t in range(10):
        perm = list(range(K)); rng.shuffle(perm)
        out[f"random relabelling of the members, then base-5/8 digits #{t}"] = [lambda k, p=perm: p[k] % 5, lambda k, p=perm: (p[k] // 5) % 5, lambda k, p=perm: p[k] // 25]
    return out
if __name__ == "__main__":
    rng = random.Random(5); K = 200
    print(f"window K = {K}; K^2 = {K * K}")
    for T in ([7, 11], [7, 11, 13], [7, 11, 13, 17], [7, 11, 13, 17, 19], [11, 13, 17, 19, 23], [3, 5, 7, 11, 13, 17]):
        P = math.prod(T); res = []
        for name, co in systems(K, T, rng).items():
            E, w = min_trellis(K, T, co); res.append((E, w, name))
        res.sort()
        print(f"\nT = {T}: prod = {P} ({'>=' if P >= K * K else '<'} K^2); fewest edges over {len(res)} coordinate systems: {res[0][0]}; theorem demands >= K = {K}: {'holds' if res[0][0] >= K else ('NOT REQUIRED (prod < K^2)' if P < K * K else 'VIOLATED')}")
        for E, w, name in res[:4] + res[-1:]: print(f"   edges {E:6d}  width {w:4d}  {name}")
    # a second window, not a round number
    K = 331
    for T in ([7, 11, 13, 17, 19], [5, 7, 9, 11, 13, 16], [13, 17, 19]):
        P = math.prod(T); res = []
        for name, co in systems(K, T, rng).items():
            if "base 5" in name: continue
            E, w = min_trellis(K, T, co); res.append((E, w, name))
        res.sort()
        print(f"\nK = {K}, T = {T}: prod = {P} ({'>=' if P >= K * K else '<'} K^2 = {K * K}); fewest edges {res[0][0]} ({res[0][2]}); {'holds' if res[0][0] >= K else ('not required' if P < K * K else 'VIOLATED')}")
