# Second-order (pair) term of the Hardy-Littlewood model for the campaign-3 rows.
#   ln P(no prime row) = sum_q ln(1 - p_q) + (1/2) sum_{q != q'} p_q p_q' (S(q,q') - 1) + (third order)
#   S(q,q') = prod over primes s not dividing M of (1 - nu_s/s)/(1 - 1/s)^2, nu_s = 1 if s | q - q' else 2
import json, math, sys
import numpy as np
b = json.load(open(sys.argv[1])); b = b[0] if isinstance(b, list) else b
mods = sorted(int(r) for r, _ in b["cover"]); R = np.array(sorted(int(x) for x in b["residual"]), dtype=np.int64)
k = len(R); LN = 199 * math.log(10)
boost = 2 * math.prod(r / (r - 1) for r in mods); p = boost / LN
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return [int(x) for x in np.nonzero(s)[0]]
allp = primes_upto(122000)
free = [s for s in allp if s > 2 and s not in set(mods)]          # primes not in the cover
print("rows", k, "p", round(p, 5), "lambda", round(k * p, 3), "primes below Q outside the cover:", len(free), "smallest:", free[:12])
# constant part: all free primes with nu = 2
lnC = sum(math.log((1 - 2 / s) / (1 - 1 / s) ** 2) for s in free)
# tail over primes above 122000 (never divide q - q'): prod (1 - 1/(s-1)^2), about -sum 1/s^2 ~ -1/(x ln x)
lnC += -1 / (122000 * math.log(122000))
D = np.abs(R[:, None] - R[None, :])
lnS = np.full((k, k), lnC)
tot_extra = 0.0
for s in free:
    m = (D % s == 0) & (D > 0)
    c = int(m.sum())
    if c:
        lnS[m] += math.log((s - 1) / (s - 2))
        tot_extra += c * math.log((s - 1) / (s - 2))
off = ~np.eye(k, dtype=bool)
S = np.exp(lnS[off])
corr = 0.5 * p * p * float((S - 1).sum())
print("ln of the common factor (all nu = 2): %.6f" % lnC)
print("mean of S - 1 over ordered pairs: %.3e ; max S %.4f" % (float((S - 1).mean()), float(S.max())))
print("pair correction to ln P(no prime row): %+.5f nats   (first order: %.3f nats)" % (corr, k * math.log(1 - p)))
# how over- or under-dispersed are the rows modulo the first primes outside the cover
for s in free[:8] + [1009, 2003]:
    c = np.bincount(R % s, minlength=s)
    print("  s=%5d: sum n(n-1) = %6d, Poisson expectation k^2/(s-1) = %8.1f, contribution to the correction %+.5f" % (s, int((c * (c - 1)).sum()), k * k / (s - 1), 0.5 * p * p * (int((c * (c - 1)).sum()) * math.log((s - 1) / (s - 2)) + k * (k - 1) * math.log((1 - 2 / s) / (1 - 1 / s) ** 2))))
# the best a design could do with ONE prime: all rows in one class modulo s
s = free[0]
print("for comparison, if every row were in one class modulo %d: %+.3f nats" % (s, 0.5 * p * p * k * (k - 1) * math.log((s - 1) / (s - 2))))
