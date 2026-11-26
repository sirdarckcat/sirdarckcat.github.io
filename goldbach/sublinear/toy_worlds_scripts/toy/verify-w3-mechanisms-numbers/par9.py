# F_9, J = 2: rows = monic irreducible quartics with 2-smooth derivative; N = lam (V_2 B)^3, deg B = 2 (n = 249)
import random, time, sys
from ffg import FF
rng = random.Random(8)
K = FF(3, 2); x = K.x
V1 = x**9 - x; V2 = (x**81 - x)
assert V2.degree() == 81
quart = K.irreducibles(4)
def smooth2(g):
    if g.is_zero(): return False
    lead, fs = g.factor()
    return all(h.degree() <= 2 for h, m in fs)
rows = [Q for Q in quart if smooth2(Q.derivative())]
print("irreducible quartics", len(quart), "with 2-smooth derivative", len(rows), flush=True)
nonsq = [c for c in K.els if c != K.zero and not c.is_square()][0]
import collections
for lam, lab in ((K.one, "lam = 1"), (nonsq, "lam = nonsquare")):
    B = K.rand_monic(2, rng)
    N = lam * (V2 * B)**3
    t0 = time.time()
    hist = collections.Counter(); irr = 0
    sample = rows if lab == "lam = 1" else rows[::4]
    for Q in sample:
        r = K.nfac(N - Q); hist[r] += 1
    print(f"{lab}, B = {B}, n = {N.degree()}: rows {len(sample)}, r odd {sum(v for r, v in hist.items() if r % 2)}, r = 1: {hist[1]}, histogram {sorted(hist.items())}, mean r {sum(r*v for r, v in hist.items())/len(sample):.3f}; {time.time()-t0:.0f}s", flush=True)
# rows NOT 2-smooth (derivative an irreducible cubic): parity is not forced?
other = [Q for Q in quart if not smooth2(Q.derivative())]
B = K.rand_monic(2, rng); N = (V2 * B)**3
hist = collections.Counter()
for Q in other[::3]:
    hist[K.nfac(N - Q) % 2] += 1
print("rows with non-smooth derivative (every 3rd):", dict(hist))
