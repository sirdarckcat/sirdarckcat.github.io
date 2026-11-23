"""Validate a time model against the GPU session's measured keep-fraction sweep (old engine), then predict today's optimum."""
import sys, json, math
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))          # sieve200.py
SPEC = os.environ.get("SPEC", os.path.join(HERE, "..", "..", "..", "phd", "campaign3_gpu", "v89", "knowncase_spec.json"))     # a Q = 170,000 vector spec (origin/ccr-8ffe9d7a-4ni11u)
import numpy as np
from sieve200 import Sieve200
B = 10 ** 8; logK = 19
sp = json.load(open(SPEC)); sp = sp[0] if isinstance(sp, list) else sp
U = sp["residual"] if isinstance(sp["residual"], list) else json.loads(sp["residual"])
N0, M = int(sp["N0"]), int(sp["M"]); cover = [int(r) for r, _ in sp["cover"]]
sv = Sieve200(N0, M, U, B, logK=logK, exclude=cover)
p = math.exp(0.5772156649) * math.log(B) / math.log(10 ** 199.7)
L = 1 << 15
cs = []
for o in (50, 51, 52, 53):
    k0 = -(-10 ** 199 // M) + o * (1 << logK)
    cnt, _ = sv.block(k0, counts=True)
    cs.append(cnt.astype(np.int64))
c = np.concatenate(cs); nb = c.size // L
def Yf(f):
    nkeep = int(math.ceil(L * (1 - f)))
    tot = sum(((1 - p) ** np.sort(c[b * L:(b + 1) * L])[:nkeep].astype(np.float64)).sum() for b in range(nb))
    return tot / c.size
fs_old = [0.96, 0.965, 0.97, 0.975, 0.98, 0.985, 0.99]
meas_batch = [1.890, 1.692, 1.508, 1.324, 1.134, 0.939, 0.751]
meas_design = [0.934, 0.971, 1.0, 1.032, 1.067, 1.102, 1.079]
Y = {f: Yf(f) for f in fs_old + [0.9875, 0.9925, 0.995]}
print("old engine: measured batch (s) -> fixed + slope (1 - f):")
sl = (meas_batch[0] - meas_batch[-1]) / ((1 - fs_old[0]) - (1 - fs_old[-1])); fx = meas_batch[-1] - sl * (1 - fs_old[-1])
print(f"  linear fit: batch = {fx:.3f} + {sl:.2f} (1 - f)   [residuals " + ", ".join(f"{b - (fx + sl * (1 - f)):+.3f}" for f, b in zip(fs_old, meas_batch)) + "]")
print("model: design hits a second against f = 0.97 (batch time from the fit), against the measured sweep:")
ref = Y[0.97] / (fx + sl * 0.03)
for f, md in zip(fs_old, meas_design):
    print(f"  f = {f:6.3f}: model x{Y[f] / (fx + sl * (1 - f)) / ref:.3f}   measured x{md:.3f}")
# today: fixed = 4 windows alone, Fermat slope from the production batch 0.755 s at f = 0.985
for Sw_ms, name in ((60.7, "today (49.6 sieve + 10.6 tail + host, alone)"), (54.6, "today with DEEP_FIN2 (-2.1 ms) and rows 3 ms faster"), (50.0, "tail halved")):
    fixed = 4 * Sw_ms * 1e-3
    slope = (0.755 - fixed) / 0.015
    r = {f: Y[f] / (fixed + slope * (1 - f)) for f in fs_old[-3:] + [0.9875, 0.9925, 0.995]}
    best = max(r, key=r.get)
    print(f"{name}: fixed {fixed:.3f} s, Fermat {slope:.1f} s per unit of (1-f) (0.755 s at 0.985): " + ", ".join(f"f={f}: x{r[f] / r[0.985]:.3f}" for f in sorted(r)) + f"  -> best {best}")
