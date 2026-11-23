# Information budget: how much of the uncertainty about big(N) (top 1%) each kind of information
# removes, measured as held-out log-loss against the base rate (second half of the window).
# usage: python3 budget.py NAME
import sys, json
import numpy as np
from lib import *
name = sys.argv[1]
meta, g, isp, spf = load(name)
L, N0 = meta["L"], meta["N0"]
G = thresholds(g)[0]; y = g >= G; rq = rows_below(G)
h = L // 2; te = slice(h + 2000, L)
def ll(p, yy):
    p = np.clip(p.astype(np.float64), 1e-12, 1 - 1e-12); return -(yy * np.log(p) + (1 - yy) * np.log(1 - p))
H = ll(np.full(L - h - 2000, y[:h].mean()), y[te]).mean()
out = {"name": name, "G": G, "H": float(H), "rows": []}
def report(tag, p):
    l = ll(p[te], y[te]).mean(); o = np.argsort(-p[te], kind="stable"); yt = y[te]
    cap1 = yt[o[:len(o) // 100]].sum() / yt.sum(); cap3 = yt[o[:3 * len(o) // 100]].sum() / yt.sum()
    out["rows"].append(dict(info=tag, explained=float(1 - l / H), top1=float(cap1), top3=float(cap3)))
    print(f"  {tag:<44} explains {100*(1-l/H):5.1f}% of the uncertainty; top 1% holds {100*cap1:5.1f}%, top 3% {100*cap3:5.1f}% of big N")
print(f"{name}: big = g >= {G}; base uncertainty {H:.5f} nats per N")
cls = (N0 + 2 * np.arange(L, dtype=np.int64)) % 30030
rate = np.bincount(cls[:h], weights=y[:h], minlength=30030) / np.maximum(np.bincount(cls[:h], minlength=30030), 1)
report("N mod 30030 (residues of 2..13, cover-like)", rate[cls])
for z in (97, 997, 9973, 65521):
    R = rough(spf, z); c = float(np.asarray(isp).sum() / R.sum()); u = count_rows(R, meta, rq)
    report(f"sieve to {z} (count of surviving rows)", (1 - c) ** u.astype(np.float64))
# archipelago information on top of the sieve to 997: the outcomes of the 6 strongest neighbours
R = rough(spf, 997); c = float(np.asarray(isp).sum() / R.sum()); u = count_rows(R, meta, rq)
nb = np.zeros(L, dtype=np.int8)
for d in (6, 30, 60):
    j = d // 2
    nb[j:] += y[:-j]; nb[:-j] += y[j:]
key = np.minimum(u, 40).astype(np.int64) * 7 + nb
tab = np.bincount(key[:h], weights=y[:h], minlength=41 * 7) / np.maximum(np.bincount(key[:h], minlength=41 * 7), 1)
report("sieve to 997 + outcomes of N+-6, +-30, +-60", tab[key])
json.dump(out, open(f"budget_{name}.json", "w"), indent=1)
