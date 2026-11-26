"""Per-member alive-row counts of one 2^22 window of the 1,502-row cover at several depths, and the rows hit by the primes in (1e6, 1e8) alone:
   a6, a7, a8 (exact alive counts to 1e6, 1e7, 1e8) and L (rows divisible by some prime in (1e6, 1e8), whatever the small primes do)."""
import sys, os, time
GB = "/home/user/sirdarckcat.github.io/goldbach"
sys.path.insert(0, os.path.join(GB, "sieve200"))
import numpy as np
from sieve200 import Sieve200
from sympy import primerange
t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screens", "q200000_m89.txt")).readline().split()
cov = [tuple(map(int, x.split(":"))) for x in t[2:]]
P = np.array(list(primerange(3, 200000)), dtype=np.int64)
alive = np.ones(len(P), bool)
for r, a in cov: alive &= (P % r) != a
U = P[alive].tolist()
M, N0 = 2, 0
for r, a in cov:
    tt = ((a - N0) * pow(M, -1, r)) % r; N0 += M * tt; M *= r
kmax = (10 ** 200 - N0) // M
logK = 22
k0 = (kmax // 2) - (kmax // 2) % (1 << logK)
ex = [r for r, _ in cov]
out = {}
for name, B, extra in (("a6", 10**6, []), ("a7", 10**7, []), ("a8", 10**8, []), ("A8L", 10**8, list(primerange(3, 10**6)))):
    t0 = time.time()
    sv = Sieve200(N0, M, U, B, logK=logK, exclude=ex + extra)
    cnt, bits = sv.block(k0)
    out[name] = cnt.copy(); del bits, sv
    print(f"{name}: B={B:.0e}, {len(extra)} extra excluded, {time.time()-t0:.1f}s, mean {cnt.mean():.1f}", flush=True)
np.savez("counts.npz", a6=out["a6"], a7=out["a7"], a8=out["a8"], L=len(U) - out["A8L"].astype(np.int64), R=len(U), k0=k0)
