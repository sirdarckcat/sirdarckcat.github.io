# All vectors that differ from a given cover in one class (and, among those found, in two) and leave
# at most `best + win` rows.  Output in the pool format of tempering.py.
#   python3 neighbours.py tempering.json win out_pool.json
import json, sys, itertools
import numpy as np
t = json.load(open(sys.argv[1])); win = int(sys.argv[2]); out = sys.argv[3]
Q = t["Q"]; cover = sorted((int(r), int(a)) for r, a in t["cover"]); mods = [r for r, _ in cover]; base = [a for _, a in cover]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes_upto(Q - 1); P = P[P >= 3].astype(np.int64)
res = [P % r for r in mods]
cnt = np.zeros(len(P), dtype=np.int16)
for j, a in enumerate(base): cnt += (res[j] == a)
k0 = int((cnt == 0).sum())
pool = {tuple(base): k0}
single = []
for j, r in enumerate(mods):
    c = cnt - (res[j] == base[j])
    free = (c == 0)
    n = np.bincount(res[j][free], minlength=r)
    tot = int(free.sum())
    for a in range(1, r):
        if a != base[j] and tot - int(n[a]) <= k0 + win:
            v = list(base); v[j] = a; pool[tuple(v)] = tot - int(n[a]); single.append((j, a))
print("base", k0, "single swaps within", win, ":", len(single))
for (j1, a1), (j2, a2) in itertools.combinations(single, 2):
    if j1 == j2: continue
    c = cnt - (res[j1] == base[j1]) - (res[j2] == base[j2]) + (res[j1] == a1) + (res[j2] == a2)
    k = int((c == 0).sum())
    if k <= k0 + win:
        v = list(base); v[j1] = a1; v[j2] = a2; pool[tuple(v)] = k
top = sorted(pool.items(), key=lambda kv: (kv[1], kv[0]))
from collections import Counter
print("vectors:", len(top), "by rows left:", sorted(Counter(k for _, k in top).items()))
json.dump({"Q": Q, "mods": mods, "pool": [[k, list(v)] for v, k in top[:4000]]}, open(out, "w"))
