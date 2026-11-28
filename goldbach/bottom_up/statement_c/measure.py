# Statement C, measured: members touched per member output at a given depth, on the toy of toy.py, for
#   scan    every member of the window (touched: K);
#   pin     Theorem B's class with P_I <= K: every sub-progression k = a_I (mod P_I) whose pinned score S_I(a_I) >= tau is
#           listed in full (touched: its members);
#   tries   Theorem B's class with P_I > K: every class vector a_I with S_I(a_I) >= tau is tried (touched: one a try, its CRT lift
#           checked against the window) and the members that land are evaluated (touched: one each);
#   MITM    the additive class: the primes split into A | B (both P_A, P_B > K), lists L_A = {x_A : S_A >= tA} and
#           L_B = {x_B : S_B >= tB} generated (touched: one an entry) and matched by the CRT (k = u_A + u_B mod P, k < K), every
#           match evaluated (touched: one each);
#   pin+list the same with one side small (P_A <= K): its list is a set of sub-progressions, and each is matched against the other
#           side's list by a range query (j = (v_B - v_A) mod P_B < K / P_A) instead of being scanned.
# I and A are prefixes of the later primes (they are alike). Outputs: the members of the window with S >= t; "harvest": the share
# of them an algorithm outputs. Every count is exact: list sizes and tries from the convolution of the per-prime weight
# histograms; members, matches and outputs from the joint histogram of (S_A, S_B) over the window's exact scan. The CRT matching
# finds exactly the window's members with S_A >= tA and S_B >= tB; mitm_run.py checks that by running it.
#   python3 measure.py [m,K ...]
import math, sys
import numpy as np
from toy import setup

def conv_hist(ws):                            # exact number of class vectors of each total weight (Python ints)
    h = np.array([1], dtype=object)
    for w in ws: h = np.convolve(h, np.bincount(w).astype(object))
    return h
def suffix(h):                                # suffix[t] = #{score >= t}
    return np.concatenate([np.cumsum(h[::-1])[::-1], np.array([0], dtype=object)])

def measure(m, K, fracs=(1e-2, 1e-3, 1e-4, 1e-5, 1e-6), out=sys.stdout):
    T = setup("../covers/q200000_m89.txt", m, K)
    later, W = T["later"], T["W"]; P = math.prod(later)
    k = np.arange(K, dtype=np.int64)
    parts = np.stack([w[k % s].astype(np.int16) for s, w in zip(later, W)])
    S = parts.sum(0); Smax = int(S.max())
    print(f"\n== m = {m} later primes {later[0]}..{later[-1]}, P = {P:.3e}, window K = 2^{int(math.log2(K))} = {K:,}; score mean "
          f"{S.mean():.2f}, sd {S.std():.2f}, window max {Smax} (max possible {sum(int(w.max()) for w in W)}); "
          f"ln(4P/K^2) = {math.log(4 * P / K ** 2):.2f}", file=out)
    ge = np.bincount(S, minlength=Smax + 2)[::-1].cumsum()[::-1]            # ge[t] = #{S >= t}
    ts = []
    for f in fracs:
        t = int(np.argmin(np.abs(np.log(np.maximum(ge[:Smax + 1], 0.5)) - math.log(max(K * f, 1)))))
        if t not in ts: ts.append(t)
    if Smax not in ts: ts.append(Smax)
    # per split j (A = first j primes): joint histogram of (S_A, S_B) over the window, and class-vector counts of each side
    split = []
    for j in range(1, m):
        SA = parts[:j].sum(0); SB = S - SA; mA, mB = int(SA.max()), int(SB.max())
        H2 = np.bincount(SA * (mB + 1) + SB, minlength=(mA + 1) * (mB + 1)).reshape(mA + 1, mB + 1).astype(np.int64)
        PA = math.prod(later[:j]); PB = P // PA
        split.append(dict(j=j, PA=PA, PB=PB, H2=H2, cA=suffix(conv_hist(W[:j])), cB=suffix(conv_hist(W[j:]))))
    print("members touched per member output: scan / pin / tries / MITM / pin+list, each the best over its sets, splits and thresholds that "
          "outputs at least the given share of the n(t) members with S >= t; (additive x: the best of MITM and pin+list against the best of "
          "scan, pin and tries)", file=out)
    print("depth t | outputs n(t) | kappa = ln(K/n) | harvest >= 1 member | >= 10% | >= 50% | all", file=out)
    rows = []
    for t in ts:
        n = int(ge[t]); opts = {"scan": [(K, n)], "pin": [], "tries": [], "mitm": [], "pinlist": []}
        for d in split:
            H2 = d["H2"]; mA, mB = H2.shape[0] - 1, H2.shape[1] - 1
            a_idx = np.arange(mA + 1)[:, None]; b_idx = np.arange(mB + 1)[None, :]
            Hout = np.where(a_idx + b_idx >= t, H2, 0)
            # 2D suffix sums: R[x, y] = sum over a >= x, b >= y
            R_all = H2[::-1, ::-1].cumsum(0).cumsum(1)[::-1, ::-1]; R_out = Hout[::-1, ::-1].cumsum(0).cumsum(1)[::-1, ::-1]
            # pins / tries with I = A: threshold tau on S_A, no threshold on S_B
            for tau in range(mA + 1):
                outs = int(R_out[tau, 0]); members = int(R_all[tau, 0])
                if outs == 0: continue
                if d["PA"] <= K: opts["pin"].append((members, outs))
                else: opts["tries"].append((members + int(d["cA"][tau]), outs))
            key = "mitm" if (d["PA"] > K and d["PB"] > K) else "pinlist"   # a side that fits in the window: its list is a set of pins
            for tA in range(mA + 1):
                for tB in range(mB + 1):
                    outs = int(R_out[tA, tB])
                    if outs == 0: continue
                    opts[key].append((int(d["cA"][tA]) + int(d["cB"][tB]) + int(R_all[tA, tB]), outs))
        def front(key, h):
            c = [cost / o for cost, o in opts[key] if o >= max(1, math.ceil(h * n))]
            return min(c) if c else None
        cells = []
        for h in (0.0, 0.1, 0.5, 1.0):
            v = {key: front(key, h) for key in ("scan", "pin", "tries", "mitm", "pinlist")}
            enum = min(v[x] for x in ("scan", "pin", "tries") if v[x] is not None)
            add = min(v[x] for x in ("mitm", "pinlist") if v[x] is not None)
            cells.append(" / ".join("-" if v[key] is None else f"{v[key]:,.0f}" for key in ("scan", "pin", "tries", "mitm", "pinlist")) +
                         f" (additive x{add / enum:.3g})")
        print(f"{t} | {n:,} | {math.log(K / n):.2f} | " + " | ".join(cells), file=out)
        rows.append((t, n, opts))
    return rows

if __name__ == "__main__":
    cases = [(6, 2 ** 20), (6, 2 ** 24), (8, 2 ** 20), (8, 2 ** 24), (10, 2 ** 20), (10, 2 ** 24)]
    if len(sys.argv) > 1: cases = [tuple(int(x) for x in a.split(",")) for a in sys.argv[1:]]
    for m, K in cases: measure(m, K)
