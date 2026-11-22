# Idea 53 of the brainstorm: given that N is a success (every row composite), what is the chance
# that one of the 7,000 nearest shifts N + 30 j is a success too?  The rows of N + d whose value
# is a row value of N are known composite; the others are new numbers, prime with probability p
# when no cover modulus divides them.
#   usage: python3 -I neighbours_of_hit.py POOL.json
import json, sys, math
import numpy as np
d = json.load(open(sys.argv[1])); Q = d["Q"]; mods = d["mods"]; k0, cls = d["pool"][0]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes_upto(Q - 1); P = P[P >= 3].astype(np.int64); isp = np.zeros(Q + 1, dtype=bool); isp[P] = True
p = 2 * math.prod(r / (r - 1) for r in mods) / (200 * math.log(10)); c = -math.log(1 - p)
res = [(P % r).astype(np.int32) for r in mods]
out = []
for j in range(-3500, 3501):
    if j == 0: continue
    dd = 30 * j
    a = np.ones(len(P), dtype=bool)
    for r, cl, rs in zip(mods, cls, res): a &= (rs != (cl + dd) % r)
    U = P[a]; src = U - dd; ok = (src >= 3) & (src < Q)
    new = len(U) - int(isp[src[ok]].sum())
    out.append((new, dd, len(U)))
out.sort()
tot = sum(math.exp(-n * c) for n, _, _ in out)
print("7,000 shifts d = 30 j: fewest new rows %d at d = %d (%d rows in all); next %s" % (out[0][0], out[0][1], out[0][2], [(n, dd) for n, dd, _ in out[1:5]]))
print("sum over the shifts of P(success | N is a success) = %.2e  (best single shift %.2e); a fresh member of the best cover: %.2e" % (tot, math.exp(-out[0][0] * c), math.exp(-k0 * c)))
