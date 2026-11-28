"""Design-hit yield of the kept members against the sieve bound B and the keep fraction f, on the same windows (real sieve counts, sieve200's C sieve).

    python3 bsweep.py B1,B2,... k0_offset [k0_offset ...]        prints, per B, Y(f) = sum over the kept of (1 - p_B)^c per member sieved
"""
import os, sys, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
SPEC = os.environ.get("SPEC", os.path.join(HERE, "..", "..", "..", "phd", "campaign3_gpu", "v89", "knowncase_spec.json"))
import numpy as np
from sieve200 import Sieve200

Bs = [int(float(x)) for x in sys.argv[1].split(",")]
offs = [int(x) for x in sys.argv[2:]] or [60]
logK = int(os.environ.get("LOGK", "19"))
sp = json.load(open(SPEC)); sp = sp[0] if isinstance(sp, list) else sp
U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
N0, M = int(sp["N0"]), int(sp["M"]); cover = [int(r) for r, _ in sp["cover"]]
L = 1 << 15
fs = [0.975, 0.98, 0.9825, 0.985, 0.9875, 0.99, 0.9925]
out = {}
for B in Bs:
    t0 = time.time()
    sv = Sieve200(N0, M, U, B, logK=logK, exclude=cover)
    p = math.exp(0.5772156649) * math.log(B) / math.log(10 ** 199.8)
    cs = []
    for o in offs:
        k0 = -(-10 ** 199 // M) + o * (1 << logK)
        cnt, _ = sv.block(k0, counts=True)
        cs.append(cnt.astype(np.int64))
    c = np.concatenate(cs); nb = c.size // L
    srt = [np.sort(c[b * L:(b + 1) * L]) for b in range(nb)]
    Y = {}
    for f in fs:
        nkeep = int(math.ceil(L * (1 - f)))
        Y[f] = sum(((1 - p) ** s[:nkeep].astype(np.float64)).sum() for s in srt) / c.size
    out[B] = (p, Y, float(c.mean()))
    print(f"B={B:.3g}: p {p:.5f}, mean alive {c.mean():.1f}, primes {sv.nS:,}, {time.time() - t0:.0f} s; Y(f): " + "  ".join(f"{f}:{Y[f]:.4e}" for f in fs), flush=True)
print("JSON " + json.dumps({str(B): {"p": v[0], "mean": v[2], "Y": {str(f): y for f, y in v[1].items()}} for B, v in out.items()}))
