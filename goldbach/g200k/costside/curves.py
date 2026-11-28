import numpy as np
d = np.load("counts.npz")
a6, a7, a8, L = (d[k].astype(np.int64) for k in ("a6", "a7", "a8", "L"))
p8 = 0.0716; p7 = p8 * 7 / 8; p6 = p8 * 6 / 8
lq = np.log1p(-p8)
h = np.exp(lq * (a8 - a8.min()))              # hit probability up to a common factor
H = h.sum()
BL = 32768
nb = len(a8) // BL
def sel(score, f):
    """per 32,768-block: the ceil(f BL) members with the lowest score (ties by index)"""
    keep = int(np.ceil(f * BL))
    s = score.reshape(nb, BL)
    idx = np.argsort(s, axis=1, kind="stable")[:, :keep]
    return (idx + (np.arange(nb) * BL)[:, None]).ravel()
def tests(a, p):
    return (1 - (1 - p) ** a) / p
print(f"{len(a8)} members; mean a6 {a6.mean():.1f}, a7 {a7.mean():.1f}, a8 {a8.mean():.1f}, L {L.mean():.1f}")
print("captured hit mass (of all members' hit mass, h = (1 - p8)^a8) and tests a kept member, by score and keep fraction")
fs = (0.002, 0.005, 0.01, 0.015, 0.03, 0.06)
rows = []
for name, score, tp in (("a8 (exact to 1e8)", a8, ("a8", p8)), ("a7 (exact to 1e7)", a7, ("a7", p7)), ("a6 (exact to 1e6)", a6, ("a6", p6)),
                        ("a6 - L (no dedup)", a6 - L, ("a6", p6))):
    line = [name]
    for f in fs:
        k = sel(score, f)
        aT = {"a8": a8, "a7": a7, "a6": a6}[tp[0]][k]
        line.append(f"{h[k].sum() / H:.4f}/{tests(aT, tp[1]).mean():.1f}")
    rows.append(line)
for X in (0.03, 0.05, 0.10, 0.20):
    line = [f"two-stage: top {X:.0%} by a6, then a8"]
    for f in fs:
        if f > X: line.append("-"); continue
        c = sel(a6, X)
        # among the candidates of each block, the f BL lowest a8
        cb = c.reshape(nb, -1)
        s8 = a8[cb]
        keep = int(np.ceil(f * BL))
        o = np.argsort(s8, axis=1, kind="stable")[:, :keep]
        k = np.take_along_axis(cb, o, axis=1).ravel()
        line.append(f"{h[k].sum() / H:.4f}/{tests(a8[k], p8).mean():.1f}")
    rows.append(line)
print(f"{'score':40s} " + " ".join(f"{'keep ' + str(f * 100) + '%':>14s}" for f in fs))
for r in rows:
    print(f"{r[0]:40s} " + " ".join(f"{x:>14s}" for x in r[1:]))
# correlations
print("corr(a6, a8) %.4f, corr(a7, a8) %.4f, corr(a6 - L, a8) %.4f" % (np.corrcoef(a6, a8)[0, 1], np.corrcoef(a7, a8)[0, 1], np.corrcoef(a6 - L, a8)[0, 1]))
