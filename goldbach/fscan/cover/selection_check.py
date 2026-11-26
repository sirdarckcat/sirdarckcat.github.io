# Check of the selection model for the 200-digit game on real members.
# One residue vector (a spec in campaign3 format), L consecutive members starting at t0: sieve every residual row
# N0 + t*M - q by all primes that are not moduli, up to several depths B, count the rows left per member, and compare
# with the model used for the campaign table: rows left ~ binomial, a row left is prime with probability p(B), hit mass
# of the emptiest fraction f = Phi(Phi^-1(f) + delta*sd).
import sys, json, math, time
import numpy as np
from statistics import NormalDist
nd = NormalDist()
spec = json.load(open(sys.argv[1]))[int(sys.argv[2]) if len(sys.argv) > 2 else 0]
L = int(float(sys.argv[3])) if len(sys.argv) > 3 else 1 << 17
t0 = int(float(sys.argv[4])) if len(sys.argv) > 4 else 3_000_000_000
depths = [1 << 17, 1 << 20, 1 << 23, 1 << 26]
if len(sys.argv) > 5: depths = [1 << int(x) for x in sys.argv[5].split(",")]
N0 = int(spec["N0"]); M = int(spec["M"]); rows = np.array(spec["residual"], dtype=np.int64); k = len(rows)
mods = {r for r, _ in spec["cover"]} | {2}
B = max(depths)
sv = np.ones(B + 1, bool); sv[:2] = False
for i in range(2, int(B ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
primes = [int(p) for p in np.nonzero(sv)[0] if int(p) not in mods]
del sv
alive = np.ones((k, L), bool)
base = N0 + t0 * M
lnN = math.log(base)
EG = 1.7810724179901979
out = {}
t_start = time.time(); di = 0
rowidx = np.arange(k)
def report(Bd):
    cnt = alive.sum(axis=0).astype(np.int64)
    mean, sd = cnt.mean(), cnt.std()
    # model: survival from the cover to depth Bd
    prod = 1.0
    for s in primes:
        if s > Bd: break
        prod *= 1 - 1 / s
    ps_model = prod                                   # a residual row survives each prime s with probability 1 - 1/s
    p_hat = float(spec["boost"]) / lnN / prod         # prime probability of a row left at depth Bd
    delta = -math.log(1 - p_hat)
    w = np.exp(-delta * cnt)                          # success probability of each member
    order = np.argsort(cnt, kind="stable")
    cw = np.cumsum(w[order]) / w.sum()
    line = (f"depth 2^{int(math.log2(Bd))}: rows left mean {mean:.1f} (model {k*ps_model:.1f}), sd {sd:.2f} (binomial {math.sqrt(k*ps_model*(1-ps_model)):.2f}), "
            f"skew {((cnt-mean)**3).mean()/sd**3:+.2f}; p = {p_hat:.4f}; mean success probability {w.mean():.3e} (e^-E with E = {k*float(spec['boost'])/lnN:.2f}: {math.exp(-k*float(spec['boost'])/lnN):.3e})")
    print(line)
    for f in (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.08, 0.2):
        m = max(1, int(round(f * L)))
        model = nd.cdf(nd.inv_cdf(f) + delta * math.sqrt(k * ps_model * (1 - ps_model)))
        model_sd = nd.cdf(nd.inv_cdf(f) + delta * sd)
        print(f"     emptiest {100*f:5.1f}% ({m:6d} members, rows left <= {cnt[order[m-1]]}): hit mass measured {100*cw[m-1]:5.1f}%   model {100*model:5.1f}%  (with the measured sd {100*model_sd:5.1f}%)")
    sys.stdout.flush()
for s in primes:
    while di < len(depths) and s > depths[di]:
        report(depths[di]); di += 1
    Minv = pow(M % s, -1, s); b = base % s
    root = ((rows % s - b) * Minv) % s
    if s < L:
        n = -(-L // s)
        idx = root[:, None] + s * np.arange(n, dtype=np.int64)[None, :]
        ok = idx < L
        alive[np.broadcast_to(rowidx[:, None], idx.shape)[ok], idx[ok]] = False
    else:
        h = root < L
        if h.any(): alive[rowidx[h], root[h]] = False
while di < len(depths):
    report(depths[di]); di += 1
print(f"{k} rows, {L} members from t0 = {t0}, {len(primes)} sieve primes, {time.time()-t_start:.0f} s")
