# independent normal-model recomputation of the "free parity" value at 200 digits
import math
from statistics import NormalDist
N = NormalDist()
rows, p, S, sd = 1502, 0.0243, 500.0, 18.0
rho = rows * p / S                      # chance that a surviving row is prime
lam = -math.log(1 - rho); tilt_s = lam * sd
So = S / 2; sdo = math.sqrt(S / 4 + sd * sd / 4); rhoo = 2 * rho; lamo = -math.log(1 - rhoo); tilt_o = lamo * sdo
print(f"rho {rho:.4f} tilt_s {tilt_s:.3f} sd; odd: mean {So} sd {sdo:.2f} rho_odd {rhoo:.4f} tilt_o {tilt_o:.3f} sd")
for keep in (0.015, 0.008, 0.001):
    z = N.inv_cdf(keep); cs = N.cdf(z + tilt_s); co = N.cdf(z + tilt_o)
    ts, to = 1 / rho, 1 / rhoo
    print(f"keep {keep}: capture s {cs:.3f} o {co:.3f}; tests/member {ts:.1f} -> {to:.1f}; hits per test x{(co / to) / (cs / ts):.2f} = {math.log((co / to) / (cs / ts)):.2f} nats")
# (7,21): root-law inversion against the naive first moment
q, n = 7, 21
def mu(k):
    r = 1; d = 2
    while d * d <= k:
        if k % d == 0:
            k //= d
            if k % d == 0: return 0
            r = -r
        d += 1
    return -r if k > 1 else r
irr = sum(mu(d) * q ** (n // d) for d in range(1, n + 1) if n % d == 0) // n; rho = irr / q ** n
naive = (1 - rho) ** 728
print(f"(7,21): naive rate of D>=5 = (1-rho)^728 = {naive:.3g}; root-law inversion (4/343)^7 = {(4 / 343) ** 7:.3g}; family expectation from naive 343*naive^(1/7) = {343 * naive ** (1 / 7):.2f} (observed 4); inversion range for Poisson 4 +- 2: {(2 / 343) ** 7:.2g} .. {(6 / 343) ** 7:.2g}")
