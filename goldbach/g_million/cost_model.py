# T5: expected CPU-hours to a hit, from the cover's rows, the size of N, the Fermat-test time and the sieve's measured throughput.
# The model was checked against both runs.
#   - Survivors per member S: binomial with mean mu = rows*c and variance mu*(1 - c), where c = prod over X < s <= B of (1 - 1/s),
#     about 1.0019*ln X/ln B. Measured: mu and sd within 0.5% in both runs.
#   - A member with S survivors is a hit with probability (1 - p')^S, where p' = e^gamma ln B / ln N. The fitted 1/p' is within
#     1.5% of this in both runs. A member costs about 1/p' tests.
#   - Pass 1 of the sieve costs about t_sieve * rows * (pi(B) + 1.9 K) thread-seconds, with t_sieve = 4.8 ns from the 1,997-digit
#     run (428 s on 4 threads for 2,825 rows and K = 4e7). Pass 2 costs about the same again; both are counted.
#   - Policy: sieve K members and test them in increasing order of S. The expected number tested to the first hit is
#     the integral of exp(-Lambda(n)) dn, where Lambda(n) is the expected number of hits among the n emptiest.
# Prints the best K (by total CPU-hours) for each case.
#   python3 cost_model.py
import math
from math import erf, exp, log, sqrt

GAMMA = 0.5772156649
def Phi(z): return 0.5 * (1 + erf(z / sqrt(2)))
def li_pi(x): return x / (log(x) - 1.08)                      # pi(x), close enough here

def expected_members(K, mu, var, p, step=0.25):
    """Expected members tested to the first hit when the K members are tested in increasing order of S:
    integral over n of exp(-Lambda(n)) dn, Lambda(n) = expected hits among the n emptiest. S ~ normal(mu, var)."""
    sd = sqrt(var); s = mu - 7 * sd; n = 0.0; lam = 0.0; E = 0.0
    while s < mu + 3 * sd:
        dn = K * (Phi((s + step - mu) / sd) - Phi((s - mu) / sd))
        h = exp(-p * (s + step / 2))
        if dn > 0:
            dl = dn * h                                      # expected hits in this slice
            E += exp(-lam) * (dn if dl < 1e-9 else (1 - exp(-dl)) / h)
            lam += dl
        n += dn; s += step
        if lam > 30: break
    return E, lam                                            # lam: expected hits among all K (P(none) = e^-lam)

def model(rows, X, digits, ms_test, B=1e9, t_sieve=4.8e-9, Ks=None, inv_p=None):
    c = 1.0019 * log(X) / log(B); mu = rows * c; var = mu * (1 - c); sd = sqrt(var)
    lnN = digits * log(10); p = 1 / inv_p if inv_p else exp(GAMMA) * log(B) / lnN
    best = None
    for K in Ks or [10 ** (e / 4) for e in range(28, 41)]:     # 1e7 .. 1e10
        members, lam = expected_members(K, mu, var, p)
        if lam < 1.0: continue                                 # under 63% chance of any hit among the K: sieve more
        test_h = members * (1 / p) * ms_test / 1000 / 3600
        sieve_h = 2 * t_sieve * rows * (li_pi(B) + 1.9 * K) / 3600
        tot = test_h + sieve_h
        if best is None or tot < best[0]:
            best = (tot, K, lam, members, test_h, sieve_h, mu, sd, 1 / p)
    return best

if __name__ == "__main__":
    print("check against the runs (expected CPU-hours of tests and sieve, with the run's own K; the hits came at members 3,615 and 4,606,"
          " with 3.18 and 0.99 expected by then):")
    measured = {"2,196 digits, gmpy2": 138.5, "1,997 digits, gmpy2": 122.8, "1,997 digits, kernel": 122.8}
    for name, rows, X, digits, ms, K in (("2,196 digits, gmpy2", 2563, 5113, 2196, 65.6, 2e7), ("1,997 digits, gmpy2", 2825, 4657, 1997, 54.0, 4e7),
                                         ("1,997 digits, kernel", 2825, 4657, 1997, 16.2, 4e7)):
        for ip in (None, measured[name]):
            b = model(rows, X, digits, ms, Ks=[K], inv_p=ip)
            print(f"  {name} (1/p' {'predicted' if ip is None else 'fitted %.1f' % ip}): K = {K:.0e}: {b[2]:.1f} hits expected among the K; "
                  f"about {b[3]:,.0f} members to the first hit; tests {b[4]:.1f} h, sieve {b[5]:.2f} h")
    print("next sizes (rows from the anneals; kernel ms per test measured here):")
    import sys, json
    cases = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
    for name, rows, X, digits, ms in cases:
        b = model(rows, X, digits, ms)
        if b is None: print(f"  {name}: no K up to 1e10 reaches {2} expected hits"); continue
        tot, K, lam, members, th, sh, mu, sd, inv = b
        print(f"  {name}: rows {rows}, mu {mu:.0f} sd {sd:.1f}, 1/p' {inv:.0f}; best K = {K:.1e} ({lam:.1f} hits expected among them), "
              f"about {members:,.0f} members to the first hit; tests {th:.1f} + sieve {sh:.1f} = {tot:.1f} CPU-hours ({tot / 4:.1f} h on 4 cores)")
