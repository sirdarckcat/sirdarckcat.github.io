# World 2, Theorem W2.1 with exact prime sums: a Johnson-type soft decoder (Guruswami-Sudan / Koetter-Vardy / Guruswami-Sahai-Sudan)
# can return a member at depth kappa of its weighted score only if the places carry Mertens mass
#   Lambda = sum ln p / p >= (sqrt(ln K) - sqrt(2 kappa ln p_min / p_min))^2,
# and the cheapest places for that (per unit of input, ln p / p^2 decreases) are all primes from p_min = 467 up. This prints, per
# window size K and depth kappa, the smallest such prime range [467, y], the input sum p over it (the decoder reads every weight, so
# its time is at least this), and the ratio to scanning the K members.
#   python3 johnson_cost.py > johnson_cost.out
import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

pmin = 467
def needed(lnK, kappa):
    return (math.sqrt(lnK) - math.sqrt(2 * kappa * math.log(pmin) / pmin)) ** 2
# cumulative Lambda and input over primes from 467, by a segmented sieve, until Lambda reaches the largest target
targets = []
for lnK in (math.log(2), 1, 2, 4, 8, 12.4, 16.6):
    for kap in sorted({lnK, lnK / 2, min(4.2, lnK)}):
        targets.append((lnK, kap, needed(lnK, kap)))
need_max = max(t[2] for t in targets)
small = primes_upto(50000)
lam = 0.0; inp = 0.0; lo = pmin; seg = 10 ** 7; results = {}
pending = sorted(targets, key=lambda t: t[2])
while pending:
    hi = lo + seg
    s = np.ones(hi - lo, bool)
    for p in small:
        if p * p >= hi: break
        st = max(p * p, (lo + p - 1) // p * p); s[st - lo::p] = False
    ps = np.nonzero(s)[0] + lo
    cl = lam + np.cumsum(np.log(ps) / ps); ci = inp + np.cumsum(ps.astype(float))
    while pending and pending[0][2] <= cl[-1]:
        lnK, kap, nd = pending.pop(0)
        j = int(np.searchsorted(cl, nd))
        results[(lnK, kap)] = (int(ps[j]), float(ci[j]), nd)
    lam = float(cl[-1]); inp = float(ci[-1]); lo = hi
print("window ln K | depth kappa | Lambda needed | places 467..y | decoder input (sum p) | scan K | input / scan")
for lnK, kap, nd in targets:
    y, ii, nd = results[(lnK, kap)]
    K = math.exp(lnK)
    print(f"{lnK:5.2f} | {kap:5.2f} | {nd:6.2f} | y = {y:,} | {ii:.3g} | {K:.3g} | {ii / K:.3g}")
th = sum(math.log(p) for p in primes_upto(1999) if p >= 467)
print(f"\nWorld 5's precision for the places 467..1999: ln P = {th:.1f}, D = ln(P/K) = {th - 16.6:.1f} nats at ln K = 16.6")
