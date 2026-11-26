"""Does selecting the kept members by c_G (alive rows below the near-miss threshold) instead of c_total raise the expected near-miss yield?
Real sieve (sieve200 CPU, the production spec: Q = 170,000, 1,248 rows), one window per call."""
import sys, json, time, math
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))          # sieve200.py
SPEC = os.environ.get("SPEC", os.path.join(HERE, "..", "..", "..", "phd", "campaign3_gpu", "v89", "knowncase_spec.json"))     # a Q = 170,000 vector spec (origin/ccr-8ffe9d7a-4ni11u)
import numpy as np
from sieve200 import Sieve200

B = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10_000_000
logK = int(sys.argv[2]) if len(sys.argv) > 2 else 19
k0_off = int(sys.argv[3]) if len(sys.argv) > 3 else 0
G = 157837
sp = json.load(open(SPEC)); sp = sp[0] if isinstance(sp, list) else sp
U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
N0, M = int(sp["N0"]), int(sp["M"])
cover = [int(r) for r, _ in sp["cover"]]
k0 = -(-10 ** 199 // M) + k0_off * (1 << logK)
thr_row = sum(1 for q in U if q < G)
t0 = time.time()
sv = Sieve200(N0, M, U, B, logK=logK, exclude=cover)
print(f"B={B:,} K=2^{logK} rows {len(U)} (rows below G: {thr_row}), primes {sv.nS:,}; built in {time.time() - t0:.1f} s", flush=True)
t0 = time.time()
cnt, bits = sv.block(k0, counts=True)
print(f"block sieved in {time.time() - t0:.1f} s; mean alive rows {cnt.mean():.1f}", flush=True)
K = sv.K
# c_below: alive rows with index < thr_row  (bit matrix rows are in U order)
b8 = bits.view(np.uint8).reshape(len(U), K // 8)
cG = np.zeros(K, dtype=np.int32)
for r0 in range(0, thr_row, 64):
    blk = np.unpackbits(b8[r0:min(r0 + 64, thr_row)], axis=1, bitorder="little")
    cG += blk.sum(axis=0, dtype=np.int32)
ct = cnt.astype(np.int32)
assert (cG <= ct).all()
# p-hat: the prime probability of an alive row at depth B for 200-digit numbers: e^gamma ln B / ln N
p = math.exp(0.5772156649) * math.log(B) / math.log(10 ** 199.7)
L = 1 << 15
f = 0.985
nkeep = int(math.ceil(L * (1 - f)))
print(f"p-hat {p:.4f}; blocks of {L}, keep {nkeep} (f = {f})", flush=True)

def yield_of(sel_stat):
    tot = 0.0
    for b in range(K // L):
        s = sel_stat[b * L:(b + 1) * L]
        order = np.argsort(s, kind="stable")[:nkeep]
        tot += ((1 - p) ** cG[b * L:(b + 1) * L][order].astype(np.float64)).sum()
    return tot

def design_of(sel_stat):                                   # design hits: all rows composite, sum (1-p)^c_total over the kept
    tot = 0.0
    for b in range(K // L):
        st_ = sel_stat[b * L:(b + 1) * L]
        order = np.argsort(st_, kind="stable")[:nkeep]
        tot += ((1 - p) ** ct[b * L:(b + 1) * L][order].astype(np.float64)).sum()
    return tot
d_tot, d_g = design_of(ct), design_of(cG)
print(f"expected DESIGN hits (all rows composite, sum (1-p)^c_total over the kept): select by c_total {d_tot:.4e}, by c_G {d_g:.4e}  ->  x{d_g / d_tot:.4f}", flush=True)
y_tot = yield_of(ct)
y_g = yield_of(cG)
ideal = sum(((1 - p) ** np.sort(cG[b * L:(b + 1) * L])[:nkeep].astype(np.float64)).sum() for b in range(K // L))
print(f"expected near-misses (sum (1-p)^c_G over the kept): select by c_total {y_tot:.4e}, by c_G {y_g:.4e}  ->  x{y_g / y_tot:.4f}", flush=True)
print(f"c_total: mean {ct.mean():.1f} sd {ct.std():.1f}; c_G: mean {cG.mean():.1f} sd {cG.std():.1f}; c_above: mean {(ct - cG).mean():.1f} sd {(ct - cG).std():.1f}; corr(c_total, c_G) {np.corrcoef(ct, cG)[0, 1]:.4f}", flush=True)
# what the kept members look like
for name, st in (("c_total", ct), ("c_G", cG)):
    sel = np.concatenate([b * L + np.argsort(st[b * L:(b + 1) * L], kind="stable")[:nkeep] for b in range(K // L)])
    print(f"  kept by {name}: mean c_G {cG[sel].mean():.1f}, mean c_total {ct[sel].mean():.1f}, mean c_above {(ct - cG)[sel].mean():.2f}", flush=True)
