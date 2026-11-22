# Compare the sampler's thermodynamic integration with the exact density of states.
#   usage: python3 -I compare_small.py EXACT.json TEMPERING.json
import json, math, sys
import numpy as np
ex = json.load(open(sys.argv[1])); te = json.load(open(sys.argv[2]))
hist = np.array(ex["hist"], dtype=np.float64); k = np.arange(len(hist)); lnvec = math.log(hist.sum())
lams, mean = te["lams"], te["mean"]
lnZ = [0.0]
for i in range(1, len(lams)): lnZ.append(lnZ[-1] - 0.5 * (mean[i] + mean[i - 1]) * (lams[i] - lams[i - 1]))
print("exact minimum %d (%d vectors); sampler's best %d" % (ex["best"][0], int(hist[ex["best"][0]]), te["best"]))
print("  lam   <k> exact  <k> sampler   S exact   S sampler   (S = log-number of vectors at that level)")
worst = 0.0
for i, lam in enumerate(lams):
    kmin = k[hist > 0].min()
    w = np.where(hist > 0, hist * np.exp(-lam * np.maximum(k - kmin, 0)), 0.0); Z = w.sum()
    mk = float((w * k).sum() / Z)
    Sex = math.log(Z) - lam * k[hist > 0].min() + lam * mk          # ln sum exp(-lam k) + lam <k>
    Ssa = te["lnvec"] + lnZ[i] + lam * mean[i]
    worst = max(worst, abs(Sex - Ssa))
    if i % 3 == 0 or i == len(lams) - 1:
        print("%6.3f %9.2f %11.2f %10.2f %10.2f" % (lam, mk, mean[i], Sex, Ssa))
print("largest |S exact - S sampler| over the %d temperatures: %.2f nats (ln of the number of vectors: %.2f)" % (len(lams), worst, lnvec))
