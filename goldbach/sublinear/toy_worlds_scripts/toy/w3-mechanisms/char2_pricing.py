# What the characteristic-2 desert is worth, against luck and against a cover of the same degree.
#   python3 char2_pricing.py k J D bdeg trials seed [T2 T4]
# q = 2^k.  Rows: monic irreducible Q of degree <= D.  Desert members: N = (L_J * B)^4, B random monic of degree bdeg
# (n = 4 deg L_J + 4 bdeg).  Reported:
#  (1) rows forced (r even for every member, counted on 3 members; rows of degree <= J divide N - Q... they are struck);
#  (2) luck replaced: mean number of irreducible N' - Q over the forced rows for random N' of the same degree with
#      N' = 0 mod L_J that are not 4th powers (the same absence of small factors, no parity control);
#  (3) the desert's own exponent: mean number of irreducible N - Q over all rows (only unforced rows can contribute),
#      and the fraction of members with none (a hit: N - Q reducible for every row of degree <= D);
#  (4) a cover of the same degree n: greedy classes modulo the monic irreducibles in increasing degree until their total
#      degree reaches n; rows left; estimated exponent = rows left * (1/n) * prod (1 - 1/|pi|)^-1 over the cover's primes
#      (the chance that a polynomial of degree n with no factor among them is irreducible), and, measured, the mean number
#      of irreducible N'' - Q over the rows left for random members N'' of that cover.
import itertools, random, sys, math
import numpy as np
from flint import fq_default_ctx, fq_default_poly_ctx
k, J, D, bdeg, trials, seed = (int(v) for v in sys.argv[1:7]); q = 2 ** k; random.seed(seed)
F = fq_default_ctx(2, k); R = fq_default_poly_ctx(F); x = R.gen()
els = [F(list(c)) for c in itertools.product(range(2), repeat=k)]; one = F(1)
eidx = {str(e_): i for i, e_ in enumerate(els)}
def V(j):
    v = R(1)
    for i in range(1, j + 1):
        g = pow(x, q ** i, None) - x; v = v * (g // v.gcd(g))
    return v
L = R(1)
for m in range(1, J + 1): L = L * V(J // m)
def irr(d): return [R(list(c) + [one]) for c in itertools.product(els, repeat=d) if R(list(c) + [one]).is_irreducible()]
byd = {d: irr(d) for d in range(1, D + 1)}
rows = [Q for d in range(1, D + 1) for Q in byd[d]]; rdeg = np.array([Q.degree() for Q in rows])
n = 4 * (L.degree() + bdeg)
print(f"F_{q}, J = {J}: deg L_J = {L.degree()}, members N = (L_J*B)^4, deg B = {bdeg}, n = {n}; rows of degree <= {D}: {len(rows)} ("
      + ", ".join(f"{d}:{len(byd[d])}" for d in byd) + ")")
def randB(): return R([random.choice(els) for _ in range(bdeg)] + [one])
def nfac(f): return sum(m for _, m in f.factor()[1])
# (1) forced rows
forced = np.ones(len(rows), dtype=bool)
for _ in range(3):
    N = (L * randB()) ** 4
    forced &= np.array([nfac(N - Q) % 2 == 0 for Q in rows])
print("(1) rows with r(N - Q) even on 3 random members, by degree: " + ", ".join(f"{d}:{int((forced & (rdeg == d)).sum())}/{len(byd[d])}" for d in byd)
      + f"; total {int(forced.sum())} of {len(rows)}")
unf = [Q for Q, f_ in zip(rows, forced) if not f_]; frc = [Q for Q, f_ in zip(rows, forced) if f_ and Q.degree() > J]
# (2) luck replaced
tot = 0; T2 = max(3, int(sys.argv[7]) if len(sys.argv) > 7 else trials // 200)
for _ in range(T2):
    Np = L * R([random.choice(els) for _ in range(n - L.degree())] + [one])
    tot += sum(1 for Q in frc if (Np - Q).is_irreducible())
rough = math.prod((1 - q ** (-d)) ** (-len(irr(d))) for d in range(1, J + 1))
print(f"(2) forced rows of degree > J: {len(frc)}; random N' = 0 mod L_J of degree {n}: mean number of irreducible N' - Q over them = {tot/T2:.2f} "
      f"({T2} N'); model {len(frc)} * {rough:.3f} / {n} = {len(frc)*rough/n:.2f} nats of luck replaced")
# (3) the desert's own exponent
hits = 0; tot = 0
allB = [R(list(c) + [one]) for c in itertools.product(els, repeat=bdeg)] if q ** bdeg <= trials else None
if allB is not None: trials = len(allB); print(f"    (every one of the {trials} members with B monic of degree {bdeg} is tried)")
for it_ in range(trials):
    N = (L * (allB[it_] if allB is not None else randB())) ** 4
    c = sum(1 for Q in unf if (N - Q).is_irreducible()); tot += c; hits += (c == 0)
print(f"(3) unforced rows: {len(unf)}; desert members: mean number of irreducible N - Q = {tot/trials:.3f}, hits {hits} of {trials}"
      + (f" (exponent {-math.log(hits/trials):.2f})" if hits else "") + f"; model 2 * {len(unf)} * {rough:.3f} / {n} = {2*len(unf)*rough/n:.2f}")
# (4) greedy cover of the same degree
def ridx(f, dP):
    v = 0
    co = f.coeffs()
    for c in reversed(co): v = v * q + eidx[str(c)]
    return v
primes = []; totdeg = 0; d = 1
while totdeg < n:
    for P in (byd[d] if d in byd else irr(d)):
        if totdeg + d > n: break
        primes.append(P); totdeg += d
    else:
        d += 1; continue
    break
alive = np.ones(len(rows), dtype=bool); cls = []; res = []
for P in primes:
    rv = np.array([ridx(Q % P, P.degree()) for Q in rows]); res.append(rv)
    cnts = np.bincount(rv[alive], minlength=q ** P.degree()); cnts[0] = -1          # class 0 strikes only P itself
    c = int(np.argmax(cnts)); cls.append(c); alive &= rv != c
for _ in range(2):
    for j, P in enumerate(primes):
        others = np.ones(len(rows), dtype=bool)
        for i in range(len(primes)):
            if i != j: others &= res[i] != cls[i]
        cnts = np.bincount(res[j][others], minlength=q ** P.degree()); cls[j] = int(np.argmax(cnts))
alive = np.ones(len(rows), dtype=bool)
for j in range(len(primes)): alive &= res[j] != cls[j]
rough_c = math.prod((1 - q ** (-P.degree())) ** (-1) for P in primes)
Lc = int(alive.sum())
print(f"(4) cover: {len(primes)} primes of total degree {totdeg} (degrees up to {primes[-1].degree()}), greedy classes: {Lc} rows left ("
      + ", ".join(f"{d_}:{int((alive & (rdeg == d_)).sum())}" for d_ in byd) + f"); estimated exponent {Lc} * {rough_c:.3f} / {n} = {Lc*rough_c/n:.2f} nats")
# measured: members of the cover (CRT) of degree n
def unidx(v, dP):
    co = []
    for _ in range(dP): co.append(els[v % q]); v //= q
    return R(co)
M = R(1); N0 = R(0)
for P, c in zip(primes, cls):
    a_ = unidx(c, P.degree())
    # CRT step: N0 + M * t = a_ mod P
    g_, s_, _t = (M % P).xgcd(P); assert g_.degree() == 0
    t = ((a_ - N0) * s_ * (1 / g_.coeffs()[0])) % P
    N0 = N0 + M * t; M = M * P
left = [Q for Q, al in zip(rows, alive) if al]
for P, c in zip(primes, cls): assert ridx(N0 % P, P.degree()) == c
tot = 0; T4 = max(3, int(sys.argv[8]) if len(sys.argv) > 8 else trials // 100); h4 = 0
free = n - M.degree()
for _ in range(T4):
    Npp = N0 + M * R([random.choice(els) for _ in range(free)] + [random.choice(els[1:])])      # any nonzero leading coefficient
    c = sum(1 for Q in left if (Npp - Q).is_irreducible()); tot += c; h4 += (c == 0)
print(f"    measured on {T4} random members N0 + M*T of the cover, deg T = {free} (degree {M.degree() + max(free,0)}; {q-1 if free == 0 else 'many'} distinct members exist): mean number of irreducible N'' - Q over the rows left = {tot/T4:.2f}, members with none: {h4}")
