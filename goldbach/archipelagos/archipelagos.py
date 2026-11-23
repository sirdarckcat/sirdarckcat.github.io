# Archipelago anatomy.  An archipelago = a connected cluster of 'big' N (top 1% of g), two big N being linked
# when they are d apart for a lag d < G that shares at least a quarter of the row values
# (q and q + d both prime below G).  Compared with a null in which big labels are shuffled
# within each class mod 30030 (keeps every residue effect of 2..13, removes the shared rows).
# Also the dual 'prime' view: big(N) <=> every prime p in (N - G, N - 3] has N - p composite.
# usage: python3 archipelagos.py NAME
import sys, json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from lib import *

name = sys.argv[1]
meta, g, isp, spf = load(name)
L, N0, lo = meta["L"], meta["N0"], meta["lo"]
G1, G2, G3 = thresholds(g)
big, huge = g >= G1, g >= G3
rq = rows_below(G1); rset = set(int(q) for q in rq)
out = {"name": name, "G1": G1, "G3": G3}

# strong lags
lagsh = [(d, sum(1 for q in rq if q + d in rset)) for d in range(2, G1, 2)]
strong = [d for d, s in lagsh if s >= len(rq) / 4]
out["strong_lags"] = strong
print(f"{name}: big = g >= {G1} ({big.sum():,} N), huge = g >= {G3} ({huge.sum():,} N); {len(rq)} rows")
print(f"lags sharing >= 1/4 of the rows: {len(strong)} (all multiples of 6: {all(d % 6 == 0 for d in strong)}), e.g. {strong[:12]} ...")
best = sorted(lagsh, key=lambda t: -t[1])[:6]
print("most shared:", ", ".join(f"d={d}: {s}/{len(rq)}" for d, s in best))

def components(lab):
    idx = np.nonzero(lab)[0]
    pos = -np.ones(L, dtype=np.int64); pos[idx] = np.arange(idx.size)
    ei, ej = [], []
    for d in strong:
        j = d // 2
        m = lab[:-j] & lab[j:]
        a = np.nonzero(m)[0]
        ei.append(pos[a]); ej.append(pos[a + j])
    ei = np.concatenate(ei); ej = np.concatenate(ej)
    A = coo_matrix((np.ones(ei.size), (ei, ej)), shape=(idx.size, idx.size))
    nc, lbl = connected_components(A, directed=False)
    return idx, lbl, np.bincount(lbl)

idx, lbl, sizes = components(big)
# null: shuffle within classes mod 30030
cls = (N0 + 2 * np.arange(L, dtype=np.int64)) % 30030
rng = np.random.default_rng(7)
order = np.lexsort((rng.random(L), cls))          # random order inside each class
nb = np.empty(L, dtype=bool)
cs = np.bincount(cls, minlength=30030); starts = np.concatenate([[0], np.cumsum(cs)[:-1]])
# permute the labels among the members of each class
perm = order.copy()
for c in np.nonzero(cs)[0]:
    s, e = starts[c], starts[c] + cs[c]
    seg = order[s:e]
    perm[s:e] = seg[rng.permutation(e - s)]
nb[order] = big[perm]
_, _, sizes0 = components(nb)

def hist(sz):
    h = {}
    for k in (1, 2, 3, 4, 5, 6, 8, 10, 15, 20):
        h[k] = int((sz >= k).sum())
    return h
h, h0 = hist(sizes), hist(sizes0)
out["archipelagos"] = {"n_big": int(big.sum()), "n_archipelagos": int(sizes.size), "max_size": int(sizes.max()), "ge": h,
                 "null_n_archipelagos": int(sizes0.size), "null_max": int(sizes0.max()), "null_ge": h0}
print(f"\narchipelagos (clusters of big N): {sizes.size:,} from {big.sum():,} big N; largest has {sizes.max()} members")
print("  members >=      real   null(shuffled within mod 30030)")
for k in h: print(f"  {k:>9}  {h[k]:>8,}   {h0[k]:>8,}")
in_archipelago = sizes[lbl] >= 2
print(f"  share of big N in an archipelago of >= 2: real {in_archipelago.mean():.3f}, null {(sizes0 >= 2).sum() and ((np.repeat(sizes0, sizes0) >= 2).mean()):.3f}")

# where do the huge N live?
hz = huge[idx]
print(f"  huge N: {hz.sum():,}; in an archipelago of >= 2: {(sizes[lbl][hz] >= 2).mean():.3f}; median archipelago size of a huge N: {np.median(sizes[lbl][hz]):.0f} (of a big N: {np.median(sizes[lbl]):.0f})")
# largest archipelagos
top = np.argsort(-sizes)[:5]
print("  five largest archipelagos:")
for c in top:
    mem = idx[lbl == c]
    Ns = N0 + 2 * mem
    print(f"    {sizes[c]:>3} members, span {int(Ns.max() - Ns.min()):>6}, N from {int(Ns.min())}, max g {int(g[mem].max())}")
out["largest"] = [dict(size=int(sizes[c]), N_min=int(N0 + 2 * idx[lbl == c].min()), span=int(2 * (idx[lbl == c].max() - idx[lbl == c].min())), gmax=int(g[idx[lbl == c]].max())) for c in top]

# extremal index (runs declustering, run length G1) at three levels
print("\nextremal index theta = clusters / exceedances (run length G1), real vs class-shuffled null")
out["theta"] = {}
for lev, G in (("top 1%", G1), ("top 0.1%", G2), ("top 0.01%", G3)):
    for tag, lab in (("real", g >= G), ("null", None)):
        if lab is None:
            lab = np.empty(L, dtype=bool); lab[order] = (g >= G)[perm]
        e = np.nonzero(lab)[0]
        nclu = 1 + int((np.diff(e) > G1 // 2).sum()) if e.size else 0
        th = nclu / max(e.size, 1)
        out["theta"][f"{lev} {tag}"] = th
        print(f"  {lev:>9} {tag}: {e.size:>8,} exceedances, {nclu:>8,} clusters, theta = {th:.3f}")

# the dual view: primes just below N
cs_p = np.concatenate([[0], np.cumsum(np.asarray(isp), dtype=np.int64)])
a_hi = N0 - lo - 3 + 2 * np.arange(L, dtype=np.int64)       # index of N - 3
a_lo = N0 - lo - G1 + 2 * np.arange(L, dtype=np.int64)      # index of N - G1
P_w = (cs_p[a_hi + 1] - cs_p[a_lo]).astype(np.int32)         # primes in [N - G1, N - 3]
print(f"\nprimes in [N - {G1}, N - 3]: mean {P_w.mean():.2f} for all N, {P_w[big].mean():.2f} for big N, {P_w[huge].mean():.2f} for huge N")
out["primes_below"] = {"all": float(P_w.mean()), "big": float(P_w[big].mean()), "huge": float(P_w[huge].mean()), "table": []}
print("  k primes  share of N   P(big | k)   P(huge | k)")
for k in range(0, int(P_w.max()) + 1):
    m = P_w == k
    if m.sum() < 1000: continue
    out["primes_below"]["table"].append((k, float(m.mean()), float(big[m].mean()), float(huge[m].mean())))
    print(f"  {k:>8}  {m.mean():9.5f}   {big[m].mean():10.5f}   {huge[m].mean():11.6f}")

# residues of big N
print("\nresidue profile (share of N in each class; big N vs all N)")
out["residues"] = {}
for r in (3, 5, 7, 11, 13):
    Nr = (N0 + 2 * np.arange(L, dtype=np.int64)) % r
    allc = np.bincount(Nr, minlength=r) / L; bigc = np.bincount(Nr[big], minlength=r) / big.sum()
    out["residues"][r] = {"all": allc.tolist(), "big": bigc.tolist()}
    print(f"  mod {r:>2}: " + "  ".join(f"{c}: {100*bigc[c]:5.1f}% (all {100*allc[c]:4.1f}%)" for c in range(r)))
json.dump(out, open(f"archipelagos_{name}.json", "w"), indent=1)
