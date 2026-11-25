"""Expected hits a second on a G4 for the three approved items and their combinations, with the GPU session's measured pipeline (a2, depth 2):
while sieve and Fermat both run, Fermat at 0.735 and sieve at 0.43 of their solo speed; Fermat-only flush 1.318 s and sieve 0.434 s a batch of 2^26
members at keep 1.5%.  Fermat time scales with the keep (the tail does not: 0.175 s a pool at t_min = 4 ms, 0.09 s at t_min = 0, gone with carry-over);
the two-stage sieve takes 2.0-2.3 / 3.06 of the sieve's time; hits a batch from the measured capture curves (costside/cost.py)."""
import numpy as np
d = np.load("counts.npz")
a6, a8 = d["a6"].astype(np.int64), d["a8"].astype(np.int64)
p8 = 0.0716; h = np.exp(np.log1p(-p8) * (a8 - a8.min())); H = h.sum()
BL = 32768; nb = len(a8) // BL
def cap(f, two=None):
    keep = int(np.ceil(f * BL))
    if two is None:
        idx = np.argsort(a8.reshape(nb, BL), axis=1, kind="stable")[:, :keep] + (np.arange(nb) * BL)[:, None]
    else:
        c = np.argsort(a6.reshape(nb, BL), axis=1, kind="stable")[:, :int(np.ceil(two * BL))] + (np.arange(nb) * BL)[:, None]
        idx = np.take_along_axis(c, np.argsort(a8[c], axis=1, kind="stable")[:, :keep], axis=1)
    return h[idx.ravel()].sum() / H
def batch(F, S, rf=0.735, rs=0.43):
    ts, tf = S / rs, F / rf                    # time each needs while both run
    if ts <= tf:                               # the sieve finishes first, the Fermat rounds go on alone
        return ts + (F - ts * rf)
    return tf + (S - tf * rs)
F15, S0 = 1.318, 0.434
base = cap(0.015) / batch(F15, S0)
print(f"today (keep 1.5%, no carry): batch {batch(F15, S0):.3f} s, capture {cap(0.015):.4f}")
rows = []
for tail, tname in ((0.175, "t_min 4 ms"), (0.09, "t_min 0")):
    for carry in (False, True):
        for two, S in ((None, S0), (0.2, S0 * 2.3 / 3.06), (0.1, S0 * 2.0 / 3.06)):
            for f in (0.015, 0.0075, 0.005, 0.003):
                bulk = (F15 - tail) * f / 0.015
                F = bulk if carry else bulk + tail
                c = cap(f, two)
                rows.append((tname, carry, two, f, batch(F, S), c, c / batch(F, S) / base))
for tname in ("t_min 4 ms", "t_min 0"):
    print(f"\n{tname}: expected hits a second against today (x)")
    print(f"{'':28s} {'keep 1.5%':>10s} {'0.75%':>10s} {'0.5%':>10s} {'0.3%':>10s}")
    for carry in (False, True):
        for two in (None, 0.2, 0.1):
            r = [x for x in rows if x[0] == tname and x[1] == carry and x[2] == two]
            lab = ("carry-over" if carry else "rounds as now") + (", two-stage top %d%%" % (two * 100) if two else ", one-stage")
            print(f"{lab:28s} " + " ".join(f"{x[6]:10.3f}" for x in r))
