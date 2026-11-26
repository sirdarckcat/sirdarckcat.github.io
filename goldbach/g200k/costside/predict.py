import numpy as np
from math import erfc, sqrt

def chi2_contingency(tab):
    tab = np.asarray(tab, dtype=float)
    E = tab.sum(axis=1, keepdims=True) * tab.sum(axis=0, keepdims=True) / tab.sum()
    chi2 = float(((tab - E) ** 2 / E).sum()); k = (tab.shape[0] - 1) * (tab.shape[1] - 1)
    z = ((chi2 / k) ** (1 / 3) - (1 - 2 / (9 * k))) / sqrt(2 / (9 * k))          # Wilson-Hilferty
    return chi2, 0.5 * erfc(z / sqrt(2)), k, E
d = np.load("rows.npz")
prp = d["prp"].astype(np.int64); pos = d["pos"]; q = d["q"]; a = d["a"]; mem = d["mem"]
base = prp.mean()
print(f"{len(prp)} rows, {prp.sum()} PRP, rate {base:.5f}")
def report(name, cat):
    cats = np.unique(cat)
    tab = np.array([[int(((cat == c) & (prp == 1)).sum()), int(((cat == c) & (prp == 0)).sum())] for c in cats])
    keep = tab.sum(axis=1) >= 200
    tab = tab[keep]; cs = cats[keep]
    if len(cs) < 2:
        print(f"{name:42s} one class only (the cover fixes it)"); return
    chi2, pv, dof, _ = chi2_contingency(tab)
    rates = tab[:, 0] / tab.sum(axis=1)
    i = np.argmax(np.abs(rates - base))
    print(f"{name:42s} {len(cs):3d} classes  chi2 {chi2:8.1f} dof {dof:3d}  p-value {pv:.3f}  rates {rates.min() / base:.3f}..{rates.max() / base:.3f} x base")
report("position among the member's rows, bins of 50", np.minimum(pos // 50, 9))
report("position, first 14 rows vs the rest", (pos < 14).astype(int))
for m in (3, 4, 5, 7, 8, 9, 11, 12, 13, 16, 24, 30):
    report(f"q mod {m}", q % m)
for m in (4, 8, 16, 64, 12, 24, 30):
    report(f"n = N - q mod {m}", d[f"n{m}"])
report("member's alive count a8, deciles", np.digitize(a, np.quantile(a, np.linspace(0.1, 0.9, 9))))
gap = np.where(pos > 0, q - np.roll(q, 1), -1)
report("gap to the previous alive row mod 6 (rows after the first)", np.where(pos > 0, gap % 6, -1)[pos > 0] if False else np.where(pos > 0, gap % 6, 99))
report("gap to the previous alive row, size bins", np.where(pos > 0, np.minimum(np.log2(np.maximum(gap, 1)).astype(int), 12), 99))
prevp = np.where(pos > 0, np.roll(prp, 1), -1)
report("the previous row of the member is PRP / not / first", prevp)
# pairs in the same member: PRP rate of a row given another row of the member is PRP (whole member)
nprp_mem = np.bincount(mem, weights=prp)
others = nprp_mem[mem] - prp
nrow_mem = np.bincount(mem)
report("other PRP rows in the member: 0..3, 4..6, 7..9, 10+", np.digitize(others / np.maximum(nrow_mem[mem] - 1, 1) * 140, [3.5, 6.5, 9.5]))
