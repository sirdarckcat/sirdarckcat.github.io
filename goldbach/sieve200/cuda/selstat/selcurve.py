"""Gain of selecting by c_G over selecting by c_total, against the near-miss threshold G (one real window of the production vector, B and K given)."""
import sys, json, time, math
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))          # sieve200.py
SPEC = os.environ.get("SPEC", os.path.join(HERE, "..", "..", "..", "phd", "campaign3_gpu", "v89", "knowncase_spec.json"))     # a Q = 170,000 vector spec (origin/ccr-8ffe9d7a-4ni11u)
import numpy as np
from sieve200 import Sieve200
B = int(float(sys.argv[1])); logK = int(sys.argv[2]); k0_off = int(sys.argv[3]) if len(sys.argv) > 3 else 0
sp = json.load(open(SPEC)); sp = sp[0] if isinstance(sp, list) else sp
U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
N0, M = int(sp["N0"]), int(sp["M"])
cover = [int(r) for r, _ in sp["cover"]]
k0 = -(-10 ** 199 // M) + k0_off * (1 << logK)
sv = Sieve200(N0, M, U, B, logK=logK, exclude=cover)
cnt, bits = sv.block(k0, counts=True)
K = sv.K
b8 = bits.view(np.uint8).reshape(len(U), K // 8)
# cumulative alive counts by row index at the rows we need
Gs = [30000, 63097, 100000, 130000, 146191, 150000, 157837, 160000, 165000, 170000]
rows_below = {G: sum(1 for q in U if q < G) for G in Gs}
cum = {}
acc = np.zeros(K, dtype=np.int32)
need = sorted(set(rows_below.values()))
r_done = 0
for r_stop in need:
    for r0 in range(r_done, r_stop, 64):
        blk = np.unpackbits(b8[r0:min(r0 + 64, r_stop)], axis=1, bitorder="little")
        acc += blk.sum(axis=0, dtype=np.int32)
    r_done = r_stop
    cum[r_stop] = acc.copy()
ct = cnt.astype(np.int32)
p = math.exp(0.5772156649) * math.log(B) / math.log(10 ** 199.7)
L, f = 1 << 15, 0.985
nkeep = int(math.ceil(L * (1 - f)))
print(f"B={B:,} K=2^{logK} p-hat {p:.4f}: gain of selecting by c_G over c_total, expected near-misses >= G (sum (1-p)^c_G over the kept)")
for G in Gs:
    r = rows_below[G]
    cG = cum[r]
    def y(st):
        return sum(((1 - p) ** cG[b * L:(b + 1) * L][np.argsort(st[b * L:(b + 1) * L], kind="stable")[:nkeep]].astype(np.float64)).sum() for b in range(K // L))
    print(f"  G = {G:>7,}: rows below {r:>4} of {len(U)} ({100 * (len(U) - r) / len(U):4.1f}% above): x{y(cG) / y(ct):.4f}")
