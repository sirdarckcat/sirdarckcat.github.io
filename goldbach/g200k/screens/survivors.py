"""Real 200-digit survivors: the kept members (emptiest 1.5% of each 32,768-block, sieve to 1e8) of one window of the 1,502-row
cover, their alive rows N - q (no prime factor below 1e8), written as 'k q n_is_prp n' lines for the first `nmem` members."""
import sys, os, math, ctypes
GB = "/home/user/sirdarckcat.github.io/goldbach"
for p in ("sieve200", ""):
    sys.path.insert(0, os.path.join(GB, p))
import numpy as np, gmpy2
from sieve200 import Sieve200
from sympy import primerange
nmem = int(sys.argv[1]) if len(sys.argv) > 1 else 30
t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "q200000_m89.txt")).readline().split()
cov = [tuple(map(int, x.split(":"))) for x in t[2:]]
P = np.array(list(primerange(3, 200000)), dtype=np.int64)
alive = np.ones(len(P), bool)
for r, a in cov: alive &= (P % r) != a
U = P[alive].tolist()
M, N0 = 2, 0
for r, a in cov:
    tt = ((a - N0) * pow(M, -1, r)) % r; N0 += M * tt; M *= r
kmax = (10 ** 200 - N0) // M
sv = Sieve200(N0, M, U, 10 ** 8, logK=22, exclude=[r for r, _ in cov])
k0 = (kmax // 2) - (kmax // 2) % sv.K
cnt, bits = sv.block(k0)
BL = 32768
c = cnt[:BL].astype(np.int64)
sel = np.argsort(c, kind="stable")[:math.ceil(BL * 0.015)][:nmem]
rows, offs = sv.survivors(bits, np.ascontiguousarray(sel, dtype=np.uint32))
out = open("surv.txt", "w")
nt = npp = 0
for i, j in enumerate(sel.tolist()):
    N = N0 + (k0 + j) * M
    for r in rows[offs[i]:offs[i + 1]].tolist():
        q = U[r]; n = N - q
        prp = int(gmpy2.powmod(2, n - 1, n) == 1)
        out.write(f"{k0 + j} {q} {prp} {n}\n"); nt += 1; npp += prp
print(f"{len(sel)} members, {nt} survivors ({nt / len(sel):.0f} a member), {npp} PRP ({npp / nt:.4f}), N has {len(str(N))} digits")
