# Density of states of "rows left" over all nonzero residue vectors on a fixed modulus set,
# by Gibbs sampling with replica exchange and thermodynamic integration.
#   weight of a vector b at inverse temperature lam:  exp(-lam * rowsLeft(b))
#   S(lam) = ln(#vectors) + ln Z(lam) + lam * <k>_lam  = log-number of vectors with about <k>_lam rows left
import json, math, sys, time
import numpy as np

SPEC, SWEEPS, SEED = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
Qarg = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "-" else None
EXTRA = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 and sys.argv[5] != "-" else []
DROP = int(sys.argv[6]) if len(sys.argv) > 6 else 0
b = json.load(open(SPEC)); b = b[0] if isinstance(b, list) else b
Q = Qarg or b["Q"]; cover = [(int(r), int(a)) for r, a in b["cover"]]
mods = sorted([r for r, _ in cover])
if DROP: mods = mods[:-DROP]
mods = sorted(mods + EXTRA)

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

P = primes_upto(Q - 1); P = P[P >= 3].astype(np.int64)
res = [np.ascontiguousarray(P % r).astype(np.int32) for r in mods]
nm = len(mods)
lams = [0, .01, .02, .035, .05, .07, .09, .12, .15, .19, .24] + [round(0.30 + 0.06 * i, 2) for i in range(23)] + [1.75, 1.9, 2.1, 2.35, 2.65, 3.0, 3.5, 4.2, 5.2, 6.5, 8.5, 12.0]
nt = len(lams)
rng = np.random.default_rng(SEED)
state = [np.array([rng.integers(1, r) for r in mods]) for _ in range(nt)]
cnt = []
for t in range(nt):
    c = np.zeros(len(P), dtype=np.int16)
    for j in range(nm): c += (res[j] == state[t][j])
    cnt.append(c)
perm = list(range(nt))            # perm[i] = replica currently at temperature i
ksum = np.zeros(nt); k2sum = np.zeros(nt); nsamp = 0
best = (10 ** 9, None)
pool = {}
POOLWIN = 4
burn = SWEEPS // 4
t0 = time.time()
swaps = np.zeros(nt - 1); tries = 0
for sweep in range(SWEEPS):
    for i in range(nt):
        rep = perm[i]; lam = lams[i]; c = cnt[rep]; st = state[rep]
        for j in rng.permutation(nm):
            r = mods[j]; rj = res[j]
            c -= (rj == st[j])
            n = np.bincount(rj[c == 0], minlength=r)[1:].astype(np.float64)
            if lam == 0:
                new = int(rng.integers(1, r))
            else:
                w = np.exp(lam * (n - n.max())); w /= w.sum()
                new = 1 + int(rng.choice(r - 1, p=w))
            st[j] = new
            c += (rj == new)
    ks = [int((cnt[perm[i]] == 0).sum()) for i in range(nt)]
    for i in range(nt):
        if ks[i] < best[0]:
            best = (ks[i], state[perm[i]].copy())
    for i in range(nt - 20, nt):
        if ks[i] <= best[0] + POOLWIN:
            pool.setdefault(tuple(int(v) for v in state[perm[i]]), ks[i])
    if len(pool) > 4000:
        keep = sorted(pool.items(), key=lambda kv: kv[1])[:2000]; pool = dict(keep)
    # replica exchange between neighbours
    tries += 1
    for i in range(sweep % 2, nt - 1, 2):
        d = (lams[i] - lams[i + 1]) * (ks[i] - ks[i + 1])
        if d >= 0 or rng.random() < math.exp(d):
            perm[i], perm[i + 1] = perm[i + 1], perm[i]; ks[i], ks[i + 1] = ks[i + 1], ks[i]
            swaps[i] += 1
    if sweep >= burn:
        ksum += ks; k2sum += np.array(ks, dtype=float) ** 2; nsamp += 1
    if sweep % 200 == 0:
        print("sweep %d  %.0fs  best %d  k at lam=0/0.3/1/9: %d %d %d %d" % (sweep, time.time() - t0, best[0], ks[0], ks[11], ks[22], ks[-1]), flush=True)
mean = ksum / nsamp; sd = np.sqrt(np.maximum(k2sum / nsamp - mean ** 2, 0))
lnvec = sum(math.log(r - 1) for r in mods)
lnZ = np.zeros(nt)
for i in range(1, nt):
    lnZ[i] = lnZ[i - 1] - 0.5 * (mean[i] + mean[i - 1]) * (lams[i] - lams[i - 1])
print("ln(#vectors) = %.1f" % lnvec)
print(" lam    <k>     sd    S = ln#vec + lnZ + lam<k>   swap rate to next")
for i in range(nt):
    S = lnvec + lnZ[i] + lams[i] * mean[i]
    print("%5.3f %7.1f %6.2f %9.1f %s" % (lams[i], mean[i], sd[i], S, ("%.2f" % (swaps[i] / (tries / 2))) if i < nt - 1 else ""))
print("best rows left found: %d" % best[0])
top = sorted(pool.items(), key=lambda kv: kv[1])[:256]
print("pool: %d distinct vectors within %d rows of the best; counts of the top 256: %s" % (len(pool), POOLWIN, sorted(set(k for _, k in top))))
json.dump({"Q": Q, "mods": mods, "pool": [[k, list(v)] for v, k in top]}, open("pool_Q%d_m%d_seed%d.json" % (Q, len(mods), SEED), "w"))
json.dump({"Q": Q, "best": best[0], "cover": [[r, int(a)] for r, a in zip(mods, best[1])], "lams": lams, "mean": mean.tolist(), "sd": sd.tolist(), "lnvec": lnvec}, open("tempering_Q%d_m%d_seed%d.json" % (Q, len(mods), SEED), "w"))
