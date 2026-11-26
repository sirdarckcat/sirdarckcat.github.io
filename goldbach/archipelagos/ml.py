# Can ML predict big g(N) better than the count of surviving rows?
# Information allowed: the residues of N modulo the primes <= Z (what a sieve to Z sees), i.e.
# which rows q < G have N - q free of primes <= Z, the counts at every shallower depth, N mod
# small primes, and the pair structure of the survivors.  No primality of any row.
# Train on the first half of the window, test on the second half (archipelagos never straddle).
# usage: python3 ml.py NAME Z [PCT=1.0] [NTRAIN=2500000]
import sys, json, time
import numpy as np
import lightgbm as lgb
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score
from lib import *

name, Z = sys.argv[1], int(sys.argv[2])
PCT = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
NTR = int(float(sys.argv[4])) if len(sys.argv) > 4 else 2_500_000
meta, g, isp, spf = load(name)
L, N0, lo = meta["L"], meta["N0"], meta["lo"]
G = int(np.percentile(g, 100 - PCT)) + 1
y_all = g >= G
rq = rows_below(G)
rng = np.random.default_rng(11)
tr = np.sort(rng.choice(L // 2 - 2000, NTR, replace=False))
te = np.sort(L // 2 + 2000 + rng.choice(L // 2 - 2000, NTR, replace=False))
idx = np.concatenate([tr, te]); ntr = tr.size
t0 = time.time()

# survivor bitmap at depth Z for the sampled N
RZ = np.asarray(rough(spf, Z))
base = N0 - lo
B = np.empty((idx.size, rq.size), dtype=np.int8)
for k, q in enumerate(rq):
    B[:, k] = RZ[base - int(q) + 2 * idx]
cZ = float(np.asarray(isp).sum() / RZ.sum())
u = B.sum(1).astype(np.int32)
feats = {f"bit_{int(q)}": B[:, k] for k, q in enumerate(rq)}
feats["u_Z"] = u
# counts at shallower depths
for z in [3, 5, 7, 11, 13, 31, 97, 997]:
    if z >= Z: continue
    Rz = np.asarray(rough(spf, z))
    uz = np.zeros(idx.size, dtype=np.int16)
    for q in rq: uz += Rz[base - int(q) + 2 * idx]
    feats[f"u_{z}"] = uz
# where the survivors sit
for k, (a, b) in enumerate([(0, G // 4), (G // 4, G // 2), (G // 2, 3 * G // 4), (3 * G // 4, G)]):
    m = (rq >= a) & (rq < b)
    feats[f"u_part{k}"] = B[:, m].sum(1)
# N mod small primes
Nmod = N0 + 2 * idx
for r in (3, 5, 7, 11, 13, 17, 19, 23):
    feats[f"Nmod{r}"] = (Nmod % r).astype(np.int16)
# pair structure: Hardy-Littlewood pair weight of the survivors w.r.t. primes s > Z
ps = primes_upto(4 * G); ps = ps[ps > Z]
D = np.abs(rq[:, None] - rq[None, :])
Wp = np.zeros_like(D, dtype=np.float64)
for s in ps: Wp += (D % s == 0) / (s - 1.0)
np.fill_diagonal(Wp, 0)
Bf = B.astype(np.float32)
feats["pair_w"] = (0.5 * ((Bf @ Wp.astype(np.float32)) * Bf).sum(1)).astype(np.float32)
feats["pairs_same_class"] = (0.5 * ((Bf @ (Wp > 0).astype(np.float32)) * Bf).sum(1)).astype(np.float32)
names = list(feats)
X = np.column_stack([np.asarray(feats[n], dtype=np.float32) for n in names])
y = y_all[idx].astype(np.int8)
print(f"{name} Z={Z} G={G} ({100*y_all.mean():.2f}% big), rows {rq.size}, features {len(names)}, train {ntr:,} test {idx.size-ntr:,}, c_Z={cZ:.4f}  [{time.time()-t0:.0f}s]")

def logloss(p, yy):
    p = np.clip(np.asarray(p, dtype=np.float64), 1e-12, 1 - 1e-12)
    return -(yy * np.log(p) + (1 - yy) * np.log(1 - p))

Xtr, Xte, ytr, yte = X[:ntr], X[ntr:], y[:ntr], y[ntr:]
res = {}
P = {}
P["base rate"] = np.full(yte.size, ytr.mean())
P["theory (1-c)^u, no fit"] = (1 - cZ) ** Xte[:, names.index("u_Z")].astype(np.float64)
iso = IsotonicRegression(increasing=False, out_of_bounds="clip").fit(Xtr[:, names.index("u_Z")], ytr)
P["count, calibrated"] = iso.predict(Xte[:, names.index("u_Z")])
params = dict(objective="binary", learning_rate=0.05, num_leaves=63, min_data_in_leaf=400, feature_fraction=0.8,
              bagging_fraction=0.8, bagging_freq=1, lambda_l2=10.0, verbose=-1, num_threads=4)
cnt_cols = [i for i, n in enumerate(names) if n.startswith("u_")]
for tag, cols in (("LightGBM, counts at all depths", cnt_cols), ("LightGBM, all features", list(range(len(names))))):
    dtr = lgb.Dataset(Xtr[:, cols], ytr, feature_name=[names[i] for i in cols], categorical_feature=[names[i] for i in cols if names[i].startswith("Nmod")] or "auto")
    nval = ntr // 10
    dva = lgb.Dataset(Xtr[-nval:, cols], ytr[-nval:], reference=dtr)
    dtr2 = lgb.Dataset(Xtr[:-nval, cols], ytr[:-nval], feature_name=[names[i] for i in cols], categorical_feature=[names[i] for i in cols if names[i].startswith("Nmod")] or "auto")
    bst = lgb.train(params, dtr2, num_boost_round=2000, valid_sets=[dva], callbacks=[lgb.early_stopping(50, verbose=False)])
    P[tag] = bst.predict(Xte[:, cols], num_iteration=bst.best_iteration)
    if tag.endswith("all features"):
        imp = bst.feature_importance("gain"); order = np.argsort(-imp)
        res["importance"] = [(names[cols[i]], float(imp[i] / imp.sum())) for i in order[:15]]
    print(f"  trained {tag}: {bst.best_iteration} rounds [{time.time()-t0:.0f}s]")

# block bootstrap (blocks of 20,000 consecutive test N) for the gain over the calibrated count
ref = logloss(P["count, calibrated"], yte)
blk = (np.arange(yte.size) // 20000)
nb = blk.max() + 1
print(f"\n  {'model':<34} {'log-loss':>9} {'gain vs count':>14} {'+-2se':>8} {'AUC':>7} {'top1%':>7} {'top3%':>7}")
for tag, p in P.items():
    ll = logloss(p, yte); diff = ref - ll
    sums = np.bincount(blk, weights=diff, minlength=nb); cnts = np.bincount(blk, minlength=nb)
    bs = [sums[s].sum() / cnts[s].sum() for s in (rng.integers(0, nb, nb) for _ in range(300))]
    o = np.argsort(-p, kind="stable")
    cap = [float(yte[o[:int(f * yte.size)]].sum() / yte.sum()) for f in (0.01, 0.03)]
    auc = roc_auc_score(yte, p)
    res[tag] = dict(logloss=float(ll.mean()), gain=float(diff.mean()), se2=float(2 * np.std(bs)), auc=float(auc), top1=cap[0], top3=cap[1])
    print(f"  {tag:<34} {ll.mean():9.5f} {diff.mean():14.6f} {2*np.std(bs):8.6f} {auc:7.4f} {cap[0]:7.3f} {cap[1]:7.3f}")
print("\n  gain is in nats per N; per big N multiply by", round(1 / yte.mean()))
print("  top features (share of gain):", ", ".join(f"{n} {s:.3f}" for n, s in res["importance"][:10]))
res.update(name=name, Z=Z, G=G, cZ=cZ, rows=int(rq.size))
json.dump(res, open(f"ml_{name}_Z{Z}_p{PCT}.json", "w"), indent=1)
