# What a deeper sieve bound B is worth, for one card, as a function of the cost of one mark by a prime above 2^20.
# Model (checked against production: 15.6% of the hit mass in the emptiest 3% at B = 1e6, k = 1,011):
#   rows left after the sieve: normal, mean k*pi, sd = sqrt(k*pi*(1-pi)), pi = 8.92 / log2(B)   (measured law)
#   a member with R rows left succeeds with (1 - p_z)^R, p_z = e^gamma ln B / ln N
#   the emptiest fraction f of the members holds Phi(lambda + Phi^-1(f)) of the successes, lambda = -sd ln(1 - p_z)
#   cost per member = sieve + f * (tests per kept member) / (tests per second)
import math
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
def inv(f):
    lo, hi = -8.0, 8.0
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if Phi(m) < f else (lo, m)
    return lo
k = 1093; lnN = 200 * math.log(10); egam = math.exp(0.5772156649)
TESTS = 22.86e6          # kernel 28 on an RTX PRO 6000, tests per second
OVERHEAD = 1.34          # tests per kept member = OVERHEAD / p_z (25 at B = 1e6 in production)
SIEVE0 = 2.7             # ns per member for sieve + count + select at B = 2^20 (the all-GPU feeder)
ROOTS = 8e11             # modular products per second for the roots of the large primes
def model(log2B, cm, f=None):
    pi = 8.92 / log2B; pz = egam * log2B * math.log(2) / lnN
    sd = math.sqrt(k * pi * (1 - pi)); lam = -sd * math.log(1 - pz)
    tau = OVERHEAD / pz / TESTS * 1e9
    cs = SIEVE0 + (k * math.log(log2B / 20.0) * cm if log2B > 20 else 0) + k * (2 ** log2B / (log2B * math.log(2))) / 2 ** 32 / ROOTS * 1e9
    best = max((Phi(lam + inv(ff)) / (cs + ff * tau) * 1e9, ff) for ff in ([f] if f else [x / 1000 for x in range(2, 200)]))
    return best[0], best[1], pz, lam, cs
print("k = %d rows; full-weight members per second for one card" % k)
print("now, B = 2^20, 3%% kept: %.2fM" % (model(20, 0, 0.03)[0] / 1e6))
print("cost of a large-prime mark | " + " | ".join("B = 2^%d" % b for b in (20, 24, 28, 32, 36)) + "   (M/s, best keep fraction, sieve ns per member)")
for cm in (0.0033, 0.01, 0.03, 0.1):
    print("%.4f ns | " % cm + " | ".join("%.1f (%.1f%%, %.0f ns)" % (model(b, cm)[0] / 1e6, model(b, cm)[1] * 100, model(b, cm)[4]) for b in (20, 24, 28, 32, 36)))
