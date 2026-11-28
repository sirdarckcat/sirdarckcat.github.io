# (d) of the lead's split, for the research session (25 November): can soft-decision Chinese-remainder list decoding
# (Guruswami, Sahai and Sudan, FOCS 2000) enumerate the N < 10^200 with few rows left at depth z, as the ideal-order prize needs?
#
# The decoder is given weights w_{r,a} >= 0 on the residues a mod each prime r of a set R. It returns every k < K whose weighted
# agreement satisfies
#     sum_r w_{r, k mod r} ln r >= sqrt( ln K * sum_{r,a} w_{r,a}^2 ln r ).
# This is the GSS form, the CRT analogue of the Guruswami-Sudan weighted bound. It contains Boneh's CRT decoding and the
# Coppersmith / Howgrave-Graham bound on prod(N - q) as cases. The survey (Sudan, AAECC 2001) confirms the unweighted radius
# n - sqrt(n(k + eps)); the weighted inequality is as recalled, not quoted.
#
# Setting: the members N = N0 + kM of a cover (89 moduli up to 463, U = 1,502 rows left), k < K0 = 10^200/M, with ln K0 = 16.6.
# For a prime r in (463, z], the class counts c_r(a) = #{q in U: q = N0 + aM mod r} are about Poisson(m_r), with m_r = U/r. A target
# member kills beta times the typical number of rows: its residue is tilted by beta^c, and the ideal members at 1,116 rows have
# beta of about 2.
#
# With the best weights (the likelihood ratio, by Cauchy-Schwarz), E[agreement]^2 / (ln K0 * energy) = D(beta) / ln K0, where
#     D(beta) = sum_r (ln r / r) chi_r,   chi_r = E0[(P_t/P_0)^2] = exp(m_r (beta - 1)^2).
# So the decoder reaches targets with D(beta) >= ln K0. The members with multiplier beta are exp(-I(beta)) rare, with
# I(beta) = sum_r m_r (beta ln beta - beta + 1), the Poisson large deviation rate.
#
# Neutrality. Hand the decoder the residues of some cover primes as well (theta_d nats, so ln K = ln K0 + theta_d). Put weight alpha
# on the target's class there (agreement A, energy B per unit weight) and optimize alpha. The condition becomes
#     L^2 / E >= ln K0 + (theta_d - A^2/B),
# and theta_d - A^2/B >= 0 by Cauchy-Schwarz, with equality when all the weight sits on one class per prime. A longer progression
# therefore never lowers the bar on the primes above 463.
#   python3 d_decoding.py
from math import log, exp

def odd_primes(a, b):
    s = bytearray([1]) * (b + 1); s[0:2] = b"\x00\x00"
    for i in range(2, int(b ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(a + 1, b + 1) if s[i]]

U, lnK0 = 1502, 16.6
if __name__ == "__main__":
    for z in (2000, 5000, 20000):
        P = odd_primes(463, z); m = {r: U / r for r in P}; kills = sum(m.values())
        D = lambda beta: sum((log(r) / r) * exp(m[r] * (beta - 1) ** 2) for r in P)
        I = lambda beta: sum(m[r] * (beta * log(beta) - beta + 1) for r in P)
        lo, hi = 1.0, 6.0
        for _ in range(80):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if D(mid) < lnK0 else (lo, mid)
        print(f"z = {z:6d}: {len(P):5d} primes; typical first-order kills {kills:5.0f}; D(2) = {D(2.0):5.1f} < ln K0 = {lnK0}; "
              f"the decoder needs beta >= {hi:.2f}; members at that beta are e^-{I(hi):.0f} rare (the beta = 2 ones e^-{I(2.0):.0f}); "
              f"a progression holds e^{lnK0}, the campaign e^36")
