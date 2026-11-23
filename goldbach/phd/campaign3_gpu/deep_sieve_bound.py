"""Selection power of a deeper sieve bound B for campaign3 (Q = 150,000): for one vector and windows of K members, the alive
count c_B of every member at several B (uarch sieve200.Sieve200), then, at f = 0.97 blocks of L = 2^15 (production rule:
keep the ceil(L(1-f)) lowest counts, stable), the share of the hit mass kept and the tests per kept member.

Model: row alive at B is prime with p_B; sum_k c_B p_B is the same for every B (the expected number of primes among the rows
does not depend on how far one sieves), so p_B = p_B0 * sum c_B0 / sum c_B with p_B0 = 0.0536 measured at B0 = 10^6.
A member's success probability is best estimated with the deepest bound: w = (1 - p_Bmax)^c_Bmax. Tests per kept member
until its first PRP: (1 - (1 - p_B)^c) / p_B.

    python3 deep_sieve_bound.py SPECS.json NAME K0 LOGK NWIN B1,B2,... [SIEVE200_DIR]   (the uarch goldbach/sieve200)
"""
import json, math, sys, time
import numpy as np
sys.path.insert(0, sys.argv[7] if len(sys.argv) > 7 else "../lib")
from sieve200 import Sieve200
L = lambda x: json.loads(x) if isinstance(x, str) else x
specs = {v["name"]: v for v in json.load(open(sys.argv[1]))}
sp = specs[sys.argv[2]]; K0 = int(sys.argv[3]); logK = int(sys.argv[4]); NW = int(sys.argv[5]); Bs = [int(float(b)) for b in sys.argv[6].split(",")]
U = L(sp["residual"]); cover = L(sp["cover"]); N0, M = int(sp["N0"]), int(sp["M"])
ex = [int(r) for r, a in cover]
C = {}
for B in Bs:
    t0 = time.time(); sv = Sieve200(N0, M, U, B, logK=logK, exclude=ex); t1 = time.time()
    cs = []
    for w in range(NW):
        c, _ = sv.block(K0 + w * (1 << logK)); cs.append(c.astype(np.int64))
    t2 = time.time()
    C[B] = np.concatenate(cs)
    print(f"B={B:.0e}: {sv.nS} primes, setup {t1-t0:.1f}s, {NW} windows of 2^{logK} in {t2-t1:.1f}s ({(t2-t1)/(NW << logK)*1e9:.1f} ns/member, 1 thread); "
          f"alive/k {C[B].mean():.2f}, sd {C[B].std():.2f}", flush=True)
B0, Bm = Bs[0], Bs[-1]
p = {B: 0.0536 * C[B0].sum() / C[B].sum() for B in Bs}
lw = C[Bm] * math.log1p(-p[Bm]); lw -= lw.max(); w = np.exp(lw); W = w.sum()
Lb = 1 << 15; nb = len(w) // Lb
print(f"members {len(w)}, p_B: " + ", ".join(f"{B:.0e}: {p[B]:.4f}" for B in Bs))
print("hit mass kept (weights from B = %.0e) and tests per kept member, by selection bound and f:" % Bm)
for f in (0.95, 0.97, 0.98, 0.99, 0.995):
    keep = int(math.ceil(Lb * (1 - f))); row = []
    for B in Bs:
        hm = 0.0; tests = 0.0
        for b in range(nb):
            cb = C[B][b * Lb:(b + 1) * Lb]; sel = np.argsort(cb, kind="stable")[:keep] + b * Lb
            hm += w[sel].sum(); tests += ((1 - (1 - p[B]) ** C[B][sel]) / p[B]).sum()
        row.append((hm / W, tests / (keep * nb)))
    base = row[0][0] / row[0][1]
    print(f"  f={f}: " + " | ".join(f"B={B:.0e} kept {h*100:5.2f}% tests {t:5.2f} -> mass/test x{(h/t)/base:.3f}" for B, (h, t) in zip(Bs, row)), flush=True)
