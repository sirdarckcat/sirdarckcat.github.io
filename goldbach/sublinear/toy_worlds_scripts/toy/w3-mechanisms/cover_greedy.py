# A greedy cover over F_q (q = 2^k) for comparison with the desert: moduli = the monic irreducibles in increasing degree
# until their total degree reaches n; classes greedy (then `passes` rounds of one-at-a-time improvement).
# Rows = monic irreducible of degree <= D.  Output: rows left by degree; then, on members N0 + M*T of the cover,
# a direct check: the number of rows with N - Q irreducible among ALL rows (the struck ones must give 0).
#   python3 cover_greedy.py k D n passes nmembers seed
import itertools, random, sys, math
import numpy as np
from flint import fq_default_ctx, fq_default_poly_ctx
k, D, n, passes, nmem, seed = (int(v) for v in sys.argv[1:7]); q = 2 ** k; random.seed(seed)
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; one = F(1)
eidx = {str(e_): i for i, e_ in enumerate(els)}
def irr(d): return [R(list(c) + [one]) for c in itertools.product(els, repeat=d) if R(list(c) + [one]).is_irreducible()]
byd = {d: irr(d) for d in range(1, D + 1)}
rows = [Q for d in range(1, D + 1) for Q in byd[d]]; rdeg = np.array([Q.degree() for Q in rows])
def ridx(f):
    v = 0
    for c in reversed(f.coeffs()): v = v * q + eidx[str(c)]
    return v
def unidx(v, dP):
    co = []
    for _ in range(dP): co.append(els[v % q]); v //= q
    return R(co)
primes = []; totdeg = 0; d = 1
while totdeg < n:
    stop = False
    for P in (byd[d] if d in byd else irr(d)):
        if totdeg + d > n: stop = True; break
        primes.append(P); totdeg += d
    if stop: break
    d += 1
alive = np.ones(len(rows), dtype=bool); cls = []; res = []
for P in primes:
    rv = np.array([ridx(Q % P) for Q in rows]); res.append(rv)
    cnts = np.bincount(rv[alive], minlength=q ** P.degree()); c = int(np.argmax(cnts)); cls.append(c); alive &= rv != c
for _ in range(passes):
    for j, P in enumerate(primes):
        others = np.ones(len(rows), dtype=bool)
        for i in range(len(primes)):
            if i != j: others &= res[i] != cls[i]
        cnts = np.bincount(res[j][others], minlength=q ** P.degree()); cls[j] = int(np.argmax(cnts))
alive = np.ones(len(rows), dtype=bool)
for j in range(len(primes)): alive &= res[j] != cls[j]
rough = math.prod((1 - q ** (-P.degree())) ** (-1) for P in primes); Lc = int(alive.sum())
print(f"F_{q}: rows of degree <= {D}: {len(rows)}; cover: {len(primes)} moduli of total degree {totdeg} (degrees up to {primes[-1].degree()}), "
      f"{sum(1 for c in cls if c == 0)} zero classes; rows left {Lc} (" + ", ".join(f"{d_}:{int((alive & (rdeg == d_)).sum())}/{len(byd[d_])}" for d_ in byd)
      + f"); model exponent {Lc} * {rough:.3f} / {n} = {Lc * rough / n:.2f} nats")
M = R(1); N0 = R(0)
for P, c in zip(primes, cls):
    a_ = unidx(c, P.degree()); g_, s_, _t = (M % P).xgcd(P); assert g_.degree() == 0
    t = ((a_ - N0) * s_ * (1 / g_.coeffs()[0])) % P
    N0 = N0 + M * t; M = M * P
for P, c in zip(primes, cls): assert ridx(N0 % P) == c
free = n - M.degree(); tot = 0; hits = 0; bad = 0
for _ in range(nmem):
    Nm = N0 + M * R([random.choice(els) for _ in range(free)] + [random.choice(els[1:])])
    irrc = 0
    for Q, al in zip(rows, alive):
        if (Nm - Q).is_irreducible():
            irrc += 1
            if not al: bad += 1
    tot += irrc; hits += (irrc == 0)
print(f"  {nmem} random members of degree {n} ({'%d distinct exist' % (q - 1) if free == 0 else 'deg T = %d' % free}): mean number of irreducible N - Q over all rows {tot / nmem:.2f}, "
      f"members with none {hits}, irreducible on a struck row {bad}")
