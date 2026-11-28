# What a perfect, free solver of the search problem would be worth, from the selection identity
# (Lean: Cap/Tilt.lean, selection_fraction and enrichment_at).
#
# Model: the number R of rows left after the sieve is N(mu, v) over the members; a member with R
# rows left succeeds with chance (1 - p_z)^R; lam = sqrt(v) * (-ln(1 - p_z)).
#   - the members with R <= mu - z sqrt(v) are the fraction Phi(-z) of all members and hold the
#     fraction Phi(lam - z) of the successes ("tail" below: ln of the ratio);
#   - a member exactly z standard deviations below the mean is e^(lam z - lam^2/2) times as likely
#     to succeed as an average member ("point" below).
# Crude inputs, to be replaced by measured ones: survival through the sieve s = ln 683 / ln z,
# p_z = p / s, v = rows * s * (1 - s), p = 0.02390.
#   usage: python3 -I ceiling.py
import math

def Phi(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))

def Phinv(pr):
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if Phi(mid) < pr:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

p = 0.02390
print("columns: threshold, rows left by the cover, sieve bound | survival, p_z, mean and sd of rows left, lam |")
print("         then for each ln K: z of the best member among K, tail and point enrichment in nats")
for (Q, rho) in ((150000, 1092), (213070, 1623)):
    for lnz, name in ((26 * math.log(2), "2^26"), (28 * math.log(2), "2^28"), (40 * math.log(2), "2^40")):
        s = math.log(683.0) / lnz
        pz = p / s
        v = rho * s * (1 - s)
        lam = math.sqrt(v) * (-math.log(1 - pz))
        out = []
        for lnK in (-math.log(0.03), 22.18, 44.36, 100.0, 200.0):
            z = -Phinv(math.exp(-lnK))
            tail = math.log(Phi(lam - z)) + lnK
            point = lam * z - lam * lam / 2
            out.append("lnK=%.1f z=%.2f tail=%.2f point=%.2f" % (lnK, z, tail, point))
        print("Q=%d rows=%d sieve to %s | s=%.3f p_z=%.4f mean=%.0f sd=%.1f lam=%.3f | %s" % (
            Q, rho, name, s, pz, rho * s, math.sqrt(v), lam, " ; ".join(out)))
