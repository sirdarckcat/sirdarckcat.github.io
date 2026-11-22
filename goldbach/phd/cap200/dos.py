# Density of states of rows-left from tempering output, and what it implies for the capped game.
#   python3 dos.py boost Mdigits file1.json [file2.json ...]
import json, math, sys
boost, mdig = float(sys.argv[1]), float(sys.argv[2])
runs = [json.load(open(f)) for f in sys.argv[3:]]
lams = runs[0]["lams"]; lnvec = runs[0]["lnvec"]
mean = [sum(r["mean"][i] for r in runs) / len(runs) for i in range(len(lams))]
spread = [max(r["mean"][i] for r in runs) - min(r["mean"][i] for r in runs) for i in range(len(lams))]
var = [sum(r["sd"][i] ** 2 for r in runs) / len(runs) for i in range(len(lams))]
lnZ = [0.0]
for i in range(1, len(lams)):
    d = lams[i] - lams[i - 1]
    # trapezoid with the end-point correction; d<rows>/dlam = -Var(rows)
    integral = 0.5 * (mean[i] + mean[i - 1]) * d - d * d * (var[i - 1] - var[i]) / 12
    lnZ.append(lnZ[-1] - integral)
S = [lnvec + lnZ[i] + lams[i] * mean[i] for i in range(len(lams))]
print("best rows left found:", [r["best"] for r in runs], " ln(#vectors) = %.1f" % lnvec)
print("  lam   <rows left>  (spread between runs)   S = ln #vectors at that level")
for i in range(len(lams)):
    if i % 3 == 0 or i >= len(lams) - 8:
        print("%6.2f  %9.1f   %6.1f   %9.1f" % (lams[i], mean[i], spread[i], S[i]))
kc, Sc, lc = mean[-1], S[-1], lams[-1]
print("coldest level: rows %.1f, S %.1f nats, slope %.1f nats per row -> concavity floor for the optimum: %.1f rows" % (kc, Sc, lc, kc - Sc / lc))
# S as a function of rows (interpolation), and the cost per success under the cap
def S_of(k):
    for i in range(len(lams) - 1, 0, -1):
        if mean[i] <= k <= mean[i - 1]:
            f = (k - mean[i]) / (mean[i - 1] - mean[i]); return S[i] + f * (S[i - 1] - S[i])
    return None
for cap in (199, 200):
    LN = cap * math.log(10); p = boost / LN; lnK = LN - mdig * math.log(10)
    best = min(r["best"] for r in runs)
    print("cap 1e%d: p %.5f  ln(members per vector) %.2f  E at the best vector found (%d rows): %.2f nats" % (cap, p, lnK, best, -best * math.log(1 - p)))
    for extra in (5, 10, 20, 40, 80):
        k = mean[-1]
        while S_of(k) is not None and S_of(k) < extra: k += 0.25
        print("    e^%d vectors exist with at most about %.1f rows left (+%.2f nats of E over the best found)" % (extra, k, (k - best) * p))
