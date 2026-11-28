# Idea 9 of the brainstorm: which design threshold Q maximises the expected record of a campaign?
#   successes ~ Poisson(lam), lam = members * exp(-E(Q));  a success lands at Q + Exp(mean mu(Q));
#   the record is max(R0, Q + largest overshoot);  P(largest overshoot <= x) = exp(-lam exp(-x/mu)).
import math, sys
import numpy as np
R0 = 133981
pts = [(122000, 20.57), (130000, 22.33), (135000, 23.40), (140000, 24.36), (145000, 25.43), (150000, 26.57), (213070, 39.5)]
def E(Q): return float(np.interp(Q, [a for a, _ in pts], [b for _, b in pts]))
def mu(Q): return math.log(Q) / (0.1199 * 0.0242)          # mean overshoot in g: 1/(share uncovered * p) primes
def expected_record(Q, lnmembers):
    lam = math.exp(lnmembers - E(Q)); m = mu(Q)
    y = np.linspace(R0, R0 + 400000, 400001)
    surv = np.where(y < Q, 1 - math.exp(-lam), 1 - np.exp(-lam * np.exp(-np.maximum(y - Q, 0) / m)))
    return R0 + float(np.trapezoid(surv, y)), lam
rate = 3e6
for name, secs in (("one week", 604800), ("one month", 2629800), ("one year", 31557600), ("100 fleet-years", 3155760000)):
    ln = math.log(rate * secs); best = None; rows = []
    for Q in range(122000, 213001, 1000):
        r, lam = expected_record(Q, ln)
        rows.append((Q, r, lam))
        if best is None or r > best[1]: best = (Q, r, lam)
    flat = [q for q, r, _ in rows if r > best[1] - 500]
    print("%-16s ln(members) %.1f: best design Q %d, expected record %.0f (%.2f%% of 2,130,704), expected successes there %.1f; within 500 of the best for Q in [%d, %d]" % (
        name, ln, best[0], best[1], 100 * best[1] / 2130704, best[2], flat[0], flat[-1]))
    print("      " + "  ".join("Q=%dk: %.0f (%.2g hits)" % (q // 1000, r, lam) for q, r, lam in rows if q in (122000, 130000, 140000, 150000, 160000, 170000, 180000)))
