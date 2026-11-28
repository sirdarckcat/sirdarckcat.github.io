# W2.1b: concentrated weightings on the integers. Weight ln Q on the j heaviest classes at each of the first n primes from 467.
# A member is returned when G(N) = sum of ln Q over the places where N lies in a weighted class is at least
# T = sqrt(ln K * sum over weighted classes of g^2/ln Q) = sqrt(ln K * j * Lambda_n), Lambda_n = sum of ln Q over the n places.
# In the CRT model the places are independent and N lies in a weighted class at Q with probability j/Q (a uniform member).
# A member deep in the score lies in the heaviest classes more often: the factor "tilt" multiplies that probability (4.5 is
# generous: the tilt of a member 5 standard deviations deep toward the heaviest class at 467).
# Expected number of members of a window of K = e^16.6 returned: K * P(G >= T), by a dynamic programme over the places on a grid
# of 1e-3 nats, run once over the places for each (j, tilt) and read off at every n.
#   python3 johnson_capacity.py > johnson_capacity.out
import math
import numpy as np

lnK = 16.6; K = math.exp(lnK)
def primes_from(a, count):
    out = []; x = a
    while len(out) < count:
        if all(x % d for d in range(2, int(x ** 0.5) + 1)): out.append(x)
        x += 1
    return out
NMAX = 80
PR = primes_from(467, NMAX); LQ = [math.log(q) for q in PR]
RES = 1e-3; NB = int(sum(LQ) / RES) + 3
SHOW = (1, 2, 3, 4, 5, 6, 8, 12, 20, 40, 80)

print(f"window K = e^{lnK}; places: the first n primes from 467; weight ln Q on the j heaviest classes of each")
print("j | tilt | n | Lambda_n | threshold T | expected members returned, K P(G >= T)")
for j in (1, 2, 3, 5, 10):
    for tilt in (1.0, 4.5):
        dist = np.zeros(NB); dist[0] = 1.0; lam = 0.0; best = (0.0, 0)
        for ns in range(1, NMAX + 1):
            q, l = PR[ns - 1], LQ[ns - 1]
            p = min(1.0, tilt * j / q); sh = int(round(l / RES))
            new = dist * (1 - p); new[sh:] += dist[:NB - sh] * p; dist = new
            lam += l; T = math.sqrt(lnK * j * lam)
            idx = int(math.ceil(T / RES - 1e-9)); e = K * float(dist[idx:].sum()) if idx < NB else 0.0
            if e > best[0]: best = (e, ns)
            if ns in SHOW: print(f"{j} | {tilt} | {ns} | {lam:.2f} | {T:.2f} | {e:.3e}")
        print(f"   j = {j}, tilt {tilt}: largest expected number returned {best[0]:.3e}, at n = {best[1]}")
