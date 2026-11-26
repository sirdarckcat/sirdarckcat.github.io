# World 2, Theorem W2.1 with exact prime sums. A Johnson-type soft decoder (Guruswami-Sudan / Koetter-Vardy / Guruswami-Sahai-Sudan)
# guarantees a member N iff  sum_p g_p(N mod p) >= sqrt(ln K * sum_p ||g_p||^2 / ln p).  Split each table into its mean and its
# deviation, g_p = gbar_p + d_p (the research session's decomposition, 26 Nov 01:12). The mean part is the same for every member;
# its cheapest weights (gbar_p ~ ln p / p) cost U^2 / M with Mertens mass M = sum ln p / p. The deviation part has variance at most
# max(ln p / p) * sum ||d_p||^2 / ln p. Cauchy-Schwarz on the two parts together gives the tight necessary condition
#     M + z^2 * ln p_min / p_min >= ln K,         z = sqrt(2 kappa) for a member at depth kappa,
# (the first version of W2.1 had the looser (sqrt ln K - z sqrt(ln p_min/p_min))^2, which bounded the mean and the deviation
# separately). The cheapest places for M (per unit of input, ln p / p^2 decreases) are all primes from p_min = 467 up. This prints,
# per window size K and depth kappa, the smallest prime range [467, y] meeting each condition, the decoder's input sum p over it
# (it reads every weight, so its time is at least this), and the ratio to scanning the K members.
#   python3 johnson_cost.py > johnson_cost.out
import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
pmin = 467; c1 = math.log(pmin) / pmin
def tight(lnK, kappa): return lnK - 2 * kappa * c1
def loose(lnK, kappa): return (math.sqrt(lnK) - math.sqrt(2 * kappa * c1)) ** 2
targets = []
for lnK in (math.log(2), 1, 2, 4, 8, 12.4, 16.6):
    for kap in sorted({lnK, lnK / 2, min(4.2, lnK)}):
        targets.append((lnK, kap))
need = sorted({(t, kind) for (lnK, kap) in targets for (t, kind) in ((tight(lnK, kap), "tight"), (loose(lnK, kap), "loose"))})
top = max(t for t, _ in need)
small = primes_upto(int(math.sqrt(pmin * math.exp(top + 0.5))) + 10)
lam = 0.0; inp = 0.0; lo = pmin; seg = 2 * 10 ** 7; found = {}
pend = [t for t, _ in need]
while pend:
    hi = lo + seg
    s = np.ones(hi - lo, bool)
    for p in small:
        if p * p >= hi: break
        st = max(p * p, (lo + p - 1) // p * p); s[st - lo::p] = False
    ps = np.nonzero(s)[0] + lo
    cl = lam + np.cumsum(np.log(ps) / ps); ci = inp + np.cumsum(ps.astype(float))
    while pend and pend[0] <= cl[-1]:
        t = pend.pop(0); j = int(np.searchsorted(cl, t)); found[t] = (int(ps[j]), float(ci[j]))
    lam = float(cl[-1]); inp = float(ci[-1]); lo = hi
print("window ln K | depth kappa | TIGHT: M needed | places 467..y | input | input / scan || first version (loose): M needed | y | input / scan")
for lnK, kap in targets:
    K = math.exp(lnK); t = tight(lnK, kap); l = loose(lnK, kap)
    yt, it = found[t]; yl, il = found[l]
    print(f"{lnK:5.2f} | {kap:5.2f} | {t:6.2f} | y = {yt:,} | {it:.3g} | {it / K:.3g} || {l:6.2f} | {yl:,} | {il / K:.3g}")
th = sum(math.log(p) for p in primes_upto(1999) if p >= 467)
print(f"\nWorld 5's precision for the places 467..1999: ln P = {th:.1f}, D = ln(P/K) = {th - 16.6:.1f} nats at ln K = 16.6")
