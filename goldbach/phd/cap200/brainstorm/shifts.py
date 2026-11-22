# Ideas 27 and 53 of the brainstorm: how good is a class vector for the shifted numbers N + d,
# and how many row values does N + d share with N (N + d - q = N - (q - d), q - d a prime row)?
#   usage: python3 -I shifts.py POOL.json d1,d2,...
import json, sys, math
import numpy as np
d = json.load(open(sys.argv[1])); shifts = [int(x) for x in sys.argv[2].split(",")]
Q = d["Q"]; mods = d["mods"]; k0, cls = d["pool"][0]
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes_upto(Q - 1); P = P[P >= 3].astype(np.int64); isp = np.zeros(Q + 1, dtype=bool); isp[P] = True
p = 2 * math.prod(r / (r - 1) for r in mods) / (200 * math.log(10)); c = -math.log(1 - p)
def unc(shift):          # rows q of N + shift that the classes of N leave: q - shift avoids every class
    a = np.ones(len(P), dtype=bool)
    for r, cl in zip(mods, cls): a &= ((P - shift) % r != cl)
    return P[a]
U0 = unc(0)
print("N itself: %d rows left of %d, E = %.2f" % (len(U0), len(P), len(U0) * c))
for dd in shifts:
    U = unc(dd); src = U - dd; ok = (src >= 3) & (src < Q); shared = int(isp[src[ok]].sum())
    print("N + %7d: %d rows left (%+.0f%%), E = %.2f; %d of them are row values of N (%.0f%%); new rows %d, E of the new rows %.2f" % (
        dd, len(U), 100 * (len(U) / len(U0) - 1), len(U) * c, shared, 100 * shared / len(U), len(U) - shared, (len(U) - shared) * c))
