# "luck replaced": mean number of irreducible N' - Q over the forced rows, N' random = 0 mod L_J of the same degree
import sys, random, time
from ff2 import W
k = int(sys.argv[1]); J = int(sys.argv[2]); n = int(sys.argv[3]); trials = int(sys.argv[4]); rng = random.Random(int(sys.argv[5]))
w = W(k); L = w.L(J)
if k == 4:
    rows = w.irreducibles(2) + w.irreducibles(3)
else:
    q4 = [Q for Q in w.irreducibles(4) if Q.coeffs()[3] == w.F(0)]
    rows = w.irreducibles(3) + w.irreducibles(5) + q4
    rows224 = len(rows) - len(q4)
print(f"F_{w.q}, J = {J}, n = {n}: rows {len(rows)}", flush=True)
tot = 0; tot224 = 0; t0 = time.time(); vals = []
for t in range(trials):
    T = w.rand_monic(n - L.degree(), rng)
    N = L * T
    c = 0
    for i, Q in enumerate(rows):
        if (N - Q).is_irreducible():
            c += 1
            if k != 4 and i < rows224: tot224 += 1
    vals.append(c); tot += c
import statistics
print(f"  {trials} random N' = 0 mod L_J: mean irreducible {tot/trials:.2f} (se {statistics.stdev(vals)/trials**0.5:.2f})" + (f"; over the 224 theorem-forced rows only: {tot224/trials:.2f}" if k != 4 else "") + f"; {time.time()-t0:.0f}s", flush=True)
