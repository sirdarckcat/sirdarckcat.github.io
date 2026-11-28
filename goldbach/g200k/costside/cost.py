"""Cost per unit of captured hit mass on the G4 (research's figures: Fermat 40.6 ns a test, sieve 3.06 ns a member at 1e8 for 2^24 windows,
of which tile 20.9 ms, generate 22.2 ms (pass A 13.8, pass B 8.4) and 8.2 ms of the rest a 2^24 window), from the measured capture curves."""
import numpy as np
d = np.load("counts.npz")
a6, a8 = d["a6"].astype(np.int64), d["a8"].astype(np.int64)
p8 = 0.0716; lq = np.log1p(-p8)
h = np.exp(lq * (a8 - a8.min())); H = h.sum()
BL = 32768; nb = len(a8) // BL
def cap(score, f, second=None, X=None):
    keep = int(np.ceil(f * BL))
    if second is None:
        idx = np.argsort(score.reshape(nb, BL), axis=1, kind="stable")[:, :keep] + (np.arange(nb) * BL)[:, None]
    else:
        c = np.argsort(score.reshape(nb, BL), axis=1, kind="stable")[:, :int(np.ceil(X * BL))] + (np.arange(nb) * BL)[:, None]
        o = np.argsort(second[c], axis=1, kind="stable")[:, :keep]
        idx = np.take_along_axis(c, o, axis=1)
    k = idx.ravel()
    return h[k].sum() / H, ((1 - (1 - p8) ** a8[k]) / p8).mean()
T = 40.6
W24 = 2 ** 24
tile, gen, passA, passB, rest = 20.9, 22.2, 13.8, 8.4, 8.2
binapply = 0.58 * tile                      # the share of the tile kernel that applies the large-prime bins (23 Nov split: 19.9 of 34.5 ms)
S8 = (tile + gen + rest) / W24 * 1e6        # ns a member
fs = [0.002, 0.003, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02, 0.03]
def best(S, curve, label):
    rows = []
    for f in fs:
        m, t = curve(f)
        rows.append((f, (S + f * t * T) / m, m, t))
    fb, cb, mb, tb = min(rows, key=lambda r: r[1])
    at15 = [r for r in rows if r[0] == 0.015][0][1]
    print(f"{label:58s} sieve {S:5.2f} ns: best keep {fb * 100:.2f}% -> {cb:6.1f} ns a unit (capture {mb:.3f}, {tb:.1f} tests); at 1.5%: {at15:6.1f}")
    return cb
base = best(S8, lambda f: cap(a8, f), "today: exact counts to 1e8 for every member")
for X, frac in ((0.20, 0.20), (0.10, 0.10)):
    S = (tile - binapply * (1 - frac) + passA + passB * frac + rest + 1.0) / W24 * 1e6
    c = best(S, lambda f, X=X: cap(a6, f, a8, X), f"two-stage: exact to 1e6 for all, to 1e8 for the top {X:.0%}")
    print(f"{'':58s} gain against today's best: x{base / c:.3f} = {np.log(base / c):.3f} nats")
for X in (0.20,):
    S = (tile - binapply * (1 - X) + passA / 4 + passB * X + rest + 1.0) / W24 * 1e6
    c = best(S, lambda f, X=X: cap(a6, f, a8, X), f"  ... and pass A at 4x fewer ps a visit")
    print(f"{'':58s} gain against today's best: x{base / c:.3f} = {np.log(base / c):.3f} nats")
print("for reference: sieve free and every member tested: %.2f ns a unit (the floor of today's tests: %.2f nats)" % (0.0 + 1.0 * 14.0 * T * 0, 0))
