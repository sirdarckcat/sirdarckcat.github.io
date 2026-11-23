# Model vs exhaustive truth.
# Model M_z: a row N - q with a prime factor <= z is composite; every other row is prime with the
# same probability c_z (the share of primes among z-rough numbers of the window), independently.
# Checks: (1) calibration of P(g >= G | u_z), u_z = rows below G with no factor <= z;
#         (2) the archipelago enrichment R(d) = P(big(N), big(N+d)) / P(big)^2 against the model,
#             which already contains every residue effect mod primes <= z and the shared rows.
# usage: python3 theory.py NAME
import sys, json
import numpy as np
from lib import *

name = sys.argv[1]
meta, g, isp, spf = load(name)
L = meta["L"]; G1, G2, G3 = thresholds(g)
big = g >= G1
out = {"name": name, "N0": meta["N0"], "G_top1": G1, "G_top0.1": G2, "G_top0.01": G3, "P_big": float(big.mean())}
print(f"{name}: N0 = {meta['N0']:.3g}, {L:,} even N; big := g >= {G1} ({100*big.mean():.3f}%); top 0.1%: g >= {G2}; top 0.01%: g >= {G3}")
rq = rows_below(G1)
W = meta["hi"] - meta["lo"]

# (1) calibration by depth
out["calib"] = {}
print("\n(1) P(big | u_z) against the model (1 - c_z)^u_z")
for z in (13, 97, 997, 9973, 65521):
    R = rough(spf, z)
    c = float(np.asarray(isp).sum() / R.sum())
    u = count_rows(R, meta, rq)
    pred = (1 - c) ** u.astype(np.float64)
    tot_pred, tot_obs = pred.sum(), big.sum()
    lines = []
    for lo_u, hi_u in [(0, 0), (1, 1), (2, 2), (3, 3), (4, 5), (6, 8), (9, 12), (13, 20), (21, 40), (41, 999)]:
        m = (u >= lo_u) & (u <= hi_u)
        if m.sum() < 100: continue
        lines.append((lo_u, hi_u, int(m.sum()), float(big[m].mean()), float(pred[m].mean())))
    out["calib"][z] = dict(c=c, mean_u=float(u.mean()), sd_u=float(u.std()), obs=int(tot_obs), pred=float(tot_pred), bins=lines)
    print(f"  z = {z:>5}: c_z = {c:.4f}, u mean {u.mean():.2f} sd {u.std():.2f}; big N observed {tot_obs:,}, model {tot_pred:,.0f} (ratio {tot_obs/tot_pred:.3f})")
    for lo_u, hi_u, n, ob, pr in lines:
        print(f"      u in [{lo_u:>2},{hi_u:>3}]: {n:>10,} N   P(big) observed {ob:.5f}  model {pr:.5f}  ratio {ob/pr if pr else float('nan'):.3f}")

# (2) archipelago enrichment R(d): measured on all N, model on the first 4e6 N
print("\n(2) archipelago enrichment R(d), measured vs model M_z")
rset = set(int(q) for q in rq)
lags = [2, 4, 6, 8, 10, 12, 18, 24, 30, 36, 42, 48, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 420, 630, 840, 2310, 30030]
LM = 4_000_000
models = {}
for z in (97, 9973, 65521):
    R = rough(spf, z); c = float(np.asarray(isp).sum() / R.sum())
    models[z] = (R, c, count_rows(R, meta, rq, LM + 20000))
out["lags"] = []
hdr = "  ".join(f"model z={z:<5}" for z in models)
print(f"  {'d':>6} {'shared rows':>11}   measured   {hdr}")
for d in lags:
    j = d // 2
    if j >= L // 4: continue
    meas = (big[:-j] & big[j:]).mean() / (big[:-j].mean() * big[j:].mean())
    sh_q = [q for q in rq if q + d in rset]
    row = {"d": d, "shared": len(sh_q), "measured": float(meas)}
    vals = []
    for z, (R, c, u) in models.items():
        lc = np.log1p(-c)
        if j < LM:
            sh = np.zeros(LM, dtype=np.int16)
            for q in sh_q: sh += row_view(R, meta, q, LM)
            uN, uD = u[:LM].astype(np.float64), u[j:j + LM].astype(np.float64)
            joint = np.exp(lc * (uN + uD - sh)); a = np.exp(lc * uN); b = np.exp(lc * uD)
            val = joint.mean() / (a.mean() * b.mean())
        else:  # far lags: no shared rows; pair N with N + d inside the full window
            uu = count_rows(R, meta, rq)
            a = np.exp(lc * uu[:-j].astype(np.float64)); b = np.exp(lc * uu[j:].astype(np.float64))
            val = (a * b).mean() / (a.mean() * b.mean())
        row[f"model_z{z}"] = float(val); vals.append(val)
    out["lags"].append(row)
    print(f"  {d:>6} {len(sh_q):>5} of {len(rq):<4} {meas:9.2f}   " + "  ".join(f"{v:11.2f}" for v in vals))
json.dump(out, open(f"theory_{name}.json", "w"), indent=1)
