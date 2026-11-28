# World 2, Theorem W2.1 with exact prime sums, corrected (research session, 26 Nov 03:43 UTC): a decoder may weight only the classes
# the window's members occupy. At a place Q the window N0 + kM (k < K) occupies min(Q, K) classes; above K each occupied class is a
# single member, labelled by its own index k (k mod Q = k). In the mean/deviation split over the occupied classes the mean part costs
# min(Q, K) * gbar^2, so the Mertens mass becomes
#     M' = sum_Q ln Q / min(Q, K),
# and the necessary condition (CRT independence, Gaussian tail, a member at depth kappa, z = sqrt(2 kappa)) is
#     M' + 2 kappa * a >= ln K,        a = max over the places used of ln Q / min(Q, K)   (= ln 467/467 when K >= 467).
# A weight on a fraction of a place's occupied classes gives mass ln Q / min(Q, K)^2 per weighted class: decreasing in Q up to K,
# then ln Q / K^2, increasing. This prints, per window ln K and depth kappa:
#   (A) consecutive primes 467..y (research's figures): y, weighted classes sum min(p, K), and classes per member;
#   (B) the cheapest place set while no place has a larger coefficient ln Q / min(Q, K) than 467 (the Gaussian model's own
#       condition): the primes 467..y0 in full, plus n places above K of size ln Q = K ln 467/467, each carrying the whole window;
#   (C) without that cap: one place above K carrying the window (K classes), ln Q >= K ln K with no credit for information.
# The previous version of this script weighted every class (mass sum ln p / p, input sum p); its per-member figures are quoted.
#   python3 johnson_cost.py > johnson_cost.out
import numpy as np, math
def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
pmin = 467; c = math.log(pmin) / pmin
rows = [(16.88, 16.88), (16.6, 16.6), (16.6, 8.3), (16.6, 4.2), (12.4, 12.4), (12.4, 6.2), (8.0, 8.0), (4.0, 4.0), (math.log(2), math.log(2))]
old = {(16.6, 16.6): 3.85e10, (16.6, 8.3): 5.9e10, (16.6, 4.2): 7.29e10, (12.4, 12.4): 8.86e8, (12.4, 6.2): 1.22e9, (8.0, 8.0): 1.8e7,
       (4.0, 4.0): 5.65e5, (math.log(2), math.log(2)): 2.51e4}
YMAX = int(8.5 * math.exp(16.88))
P = primes_upto(YMAX); P = P[P >= pmin]; lnP = np.log(P)
print("window ln K | depth kappa | K | (A) consecutive primes 467..y: y | y/K | weighted classes | per member || "
      "(B) capped: primes 467..y0 | places above K | weighted classes | per member || (C) uncapped: per member, ln Q || "
      "previous version (all classes): per member")
for lnK, kap in rows:
    K = math.exp(lnK)
    w = np.minimum(P.astype(float), K)
    Mp = np.cumsum(lnP / w); cls = np.cumsum(w)
    if K >= pmin:
        a = np.maximum(c, lnP / K)                          # running max of ln Q/min(Q,K): c until ln y > cK
    else:
        a = lnP / K                                          # every place is above K; the largest used sets a
    lhs = Mp + 2 * kap * np.maximum.accumulate(a)
    j = int(np.argmax(lhs >= lnK)); assert lhs[j] >= lnK
    yA, cA = int(P[j]), float(cls[j])
    if K >= pmin:
        need = lnK - 2 * kap * c
        small = P[P <= K]; Ms = np.concatenate(([0.0], np.cumsum(np.log(small) / small))); Ss = np.concatenate(([0.0], np.cumsum(small.astype(float))))
        n = np.maximum(0, np.ceil((need - Ms) / c - 1e-12))
        tot = Ss + n * K; i = int(np.argmin(tot))
        y0 = int(small[i - 1]) if i > 0 else 0
        B = f"y0 = {y0:,} | {int(n[i]):,} | {tot[i]:.3g} | {tot[i] / K:.3g}"
    else:
        B = "(no place has coefficient <= ln 467/467: every place is above K) | - | - | -"
    C = f"1 | ln Q = {K * lnK:.3g}"
    o = old.get((lnK, kap)); o = f"{o:.3g}" if o else "-"
    print(f"{lnK:5.2f} | {kap:5.2f} | {K:.4g} | y = {yA:,} | {yA / K:.3g} | {cA:.3g} | {cA / K:.3g} || {B} || {C} || {o}")
