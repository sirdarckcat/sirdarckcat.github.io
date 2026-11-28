# "Crystal" covers: every modulus r takes the class alpha/beta (mod r) for one fixed rational alpha/beta.
# Row q is then covered exactly when beta*q - alpha has a prime factor among the moduli.
# Compare with random classes and with the sampled optimum.
import sys, math
import numpy as np
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
Q = int(sys.argv[1]); m = int(sys.argv[2])
P = primes_upto(max(Q, 5000))
rows = P[(P >= 3) & (P < Q)].astype(np.int64)
mods = [int(p) for p in P[1:m + 1]]
rnd = len(rows) * math.prod(1 - 1 / (r - 1) for r in mods)
res = []
for beta in range(1, 13):
    for alpha in range(-40, 41):
        if alpha == 0 or math.gcd(abs(alpha), beta) != 1: continue
        v = beta * rows - alpha
        unc = np.ones(len(rows), bool)
        zero = 0
        for r in mods:
            if beta % r == 0: continue          # class undefined: this modulus covers nothing
            unc &= (v % r != 0) | (rows == r)
        res.append((int(unc.sum()), alpha, beta))
res.sort()
print(f"Q={Q}, first {m} odd primes (to {mods[-1]}), {len(rows)} rows; random classes leave {rnd:.0f}")
print("best crystals (uncovered, alpha, beta):", res[:12])
print("worst:", res[-3:])
