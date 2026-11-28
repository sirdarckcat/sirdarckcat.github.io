import numpy as np, itertools, sys, time
from f3int import *
D = 8; J = 3
irr = irreducibles(D)
print("irreducibles by degree", {d: len(v) for d, v in irr.items()})
primes = [f for d in range(1, J + 1) for f in irr[d]]
rows = [f for d in range(1, D + 1) for f in irr[d]]
rowdeg = np.array([len(f) - 1 for f in rows])
print("primes", len(primes), "total degree", sum(len(f) - 1 for f in primes), "rows", len(rows))
# residue of each row modulo each prime, coded as integer
rowres = np.array([[toint(pmod(Q, pi)) for pi in primes] for Q in rows])   # rows x 14
sizes = [3 ** (len(pi) - 1) for pi in primes]
# mask[pi][c] = boolean vector over rows: row == c mod pi
masks = [np.array([(rowres[:, i] == c) for c in range(sizes[i])]) for i in range(len(primes))]
def left_for_residues(res):   # res: array (m, 14) of class codes -> rows left (m,)
    st = np.zeros((res.shape[0], len(rows)), dtype=bool)
    for i in range(len(primes)):
        st |= masks[i][res[:, i]]
    return st
# x^j mod pi tables, to reduce R fast
maxdeg = 10
xpow = [[toint(pmod([0] * j + [1], pi)) for j in range(maxdeg + 1)] for pi in primes]
def addcode(a, b, size):  # coefficientwise addition mod 3 of base-3 codes (vectorised)
    r = np.zeros_like(a); m = 1
    while m < size:
        r += ((a // m % 3 + b // m % 3) % 3) * m; m *= 3
    return r
for dR in range(4, 11):
    coefs = np.array(list(itertools.product(range(3), repeat=dR)), dtype=np.int64)   # low..high, then monic
    res = np.zeros((len(coefs), len(primes)), dtype=np.int64)
    for i, pi in enumerate(primes):
        acc = np.full(len(coefs), xpow[i][dR], dtype=np.int64)
        for j in range(dR):
            for c in (1, 2):
                term = toint([(c * t) % 3 for t in tolist(xpow[i][j])] ) if xpow[i][j] else 0
                sel = coefs[:, j] == c
                acc[sel] = addcode(acc[sel], np.full(sel.sum(), term, dtype=np.int64), sizes[i])
        res[:, i] = acc
    best = None; tot = 0
    for s in range(0, len(coefs), 4096):
        st = left_for_residues(res[s:s + 4096])
        cnt = (~st).sum(axis=1)
        tot += cnt.sum()
        k = int(cnt.argmin())
        if best is None or cnt[k] < best[0]:
            best = (int(cnt[k]), coefs[s + k].tolist() + [1], [int(((~st[k]) & (rowdeg == d)).sum()) for d in range(1, D + 1)])
    print(f"aligned R monic degree {dR} ({len(coefs)}): mean left {tot/len(coefs):.1f}, best {best[0]}, R (low..high) {best[1]}, left by row degree {best[2]}", flush=True)
    if dR == 4:
        # Proposition 4: rows of degree 4 left are exactly irreducible R - c, c = 1, 2 ; and count R striking all rows of degree <= 4
        exc = 0; allstruck = 0
        st = left_for_residues(res)
        rowcode = {toint(Q): i for i, Q in enumerate(rows)}
        for k in range(len(coefs)):
            R = coefs[k].tolist() + [1]
            leftset = set(np.nonzero((~st[k]) & (rowdeg == 4))[0].tolist())
            pred = set()
            for c in (1, 2):
                Rc = R[:]; Rc[0] = (Rc[0] - c) % 3
                if toint(Rc) in rowcode: pred.add(rowcode[toint(Rc)])
            if leftset != pred: exc += 1
            if not ((~st[k]) & (rowdeg <= 4)).any(): allstruck += 1
        print(f"   Proposition 4 at degree 4 over all 81 R: exceptions {exc}; R striking every row of degree <= 4: {allstruck}")
rng = np.random.default_rng(11)
res = np.stack([rng.integers(1, s, size=2000) for s in sizes], axis=1)
cnt = (~left_for_residues(res)).sum(axis=1)
print(f"random nonzero classes (2000): mean {cnt.mean():.1f}, sd {cnt.std(ddof=1):.1f}, min {cnt.min()}")
# greedy with improvement passes (my own): start from best single choices in order, then coordinate descent
def greedy(order, passes=6):
    cls = [None] * len(primes)
    struck = np.zeros(len(rows), dtype=bool)
    for i in order:
        gains = (masks[i] & ~struck).sum(axis=1)
        cls[i] = int(gains.argmax()); struck |= masks[i][cls[i]]
    for ps in range(passes):
        ch = False
        for i in order:
            others = np.zeros(len(rows), dtype=bool)
            for j in range(len(primes)):
                if j != i: others |= masks[j][cls[j]]
            gains = (masks[i] & ~others).sum(axis=1)
            b = int(gains.argmax())
            if gains[b] > gains[cls[i]]: cls[i] = b; ch = True
        if not ch: break
    st = np.zeros(len(rows), dtype=bool)
    for j in range(len(primes)): st |= masks[j][cls[j]]
    return int((~st).sum())
g1 = greedy(list(range(len(primes))))
g2 = greedy(list(range(len(primes)))[::-1])
gs = [greedy(list(rng.permutation(len(primes)))) for _ in range(200)]
print(f"greedy (small primes first) {g1}; (large first) {g2}; 200 random orders: min {min(gs)}, mean {np.mean(gs):.1f}")
