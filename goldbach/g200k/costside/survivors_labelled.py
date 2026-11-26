"""Kept members of one window (the emptiest 1.5% of the first blocks), their alive rows to 1e8, a base-2 Fermat verdict for every row:
   rows.npz with member, position, q, prp, a8 (the member's alive count), Nmod (N mod small m) for predictor tests."""
import sys, os, math, multiprocessing as mp
GB = "/home/user/sirdarckcat.github.io/goldbach"
sys.path.insert(0, os.path.join(GB, "sieve200"))
import numpy as np, gmpy2
from sieve200 import Sieve200
from sympy import primerange
NMEM = int(sys.argv[1]) if len(sys.argv) > 1 else 300
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
sv = Sieve200(N0, M, U, 10 ** 8, logK=22, exclude=[r for r, _ in cov])
k0 = (kmax // 2) - (kmax // 2) % sv.K
cnt, bits = sv.block(k0)
BL = 32768
sel = []
for b in range(0, sv.K, BL):
    c = cnt[b:b + BL].astype(np.int64)
    sel += (np.argsort(c, kind="stable")[:math.ceil(BL * 0.015)] + b).tolist()
    if len(sel) >= NMEM: break
sel = np.array(sel[:NMEM], dtype=np.uint32)
rows, offs = sv.survivors(bits, sel)
jobs = []
for i, j in enumerate(sel.tolist()):
    N = N0 + (k0 + j) * M
    for pos, r in enumerate(rows[offs[i]:offs[i + 1]].tolist()):
        jobs.append((i, pos, U[r], int(cnt[j]), str(N - U[r])))
def fermat(job):
    i, pos, q, a, n = job
    n = gmpy2.mpz(n)
    return int(gmpy2.powmod(2, n - 1, n) == 1)
if __name__ == "__main__":
    with mp.Pool(4) as pool:
        prp = pool.map(fermat, jobs, chunksize=256)
    mem = np.array([j[0] for j in jobs]); pos = np.array([j[1] for j in jobs]); q = np.array([j[2] for j in jobs]); a = np.array([j[3] for j in jobs])
    Nmods = {m: np.array([int(j[4]) % m for j in jobs]) for m in (3, 4, 5, 7, 8, 9, 11, 12, 13, 16, 24, 30, 64)}
    np.savez("rows.npz", mem=mem, pos=pos, q=q, a=a, prp=np.array(prp), **{f"n{m}": v for m, v in Nmods.items()})
    print(f"{NMEM} members, {len(jobs)} rows, {sum(prp)} PRP ({sum(prp) / len(jobs):.4f})")
