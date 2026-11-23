"""Combine bsweep.py's Y(B, f) with a time model of the current engine (RTX PRO 6000) and print design hits a second against (B, f), relative to production (B = 1e8, f = 0.985).

Time per 2^24 window: T = S(B) + c * F1(B) * (1 - f), S = sieve + tail alone, F1 = Fermat seconds per unit of (1 - f).
  S(1e8) = 60.7 ms: generate 27.5 (62% of its instructions are visits ~ primes in (1e6, B] x rows, 38% marks ~ ln ln B - ln ln 1e6), bin apply 9.0 (~ marks), the rest (24.2) independent of B.
  F1(1e8) = 8.53 s (0.512 s of Fermat for 4 windows at f = 0.985), F1(B) ~ 1 / p(B) (tests per kept member).
The serial-sum model (batch = sieve alone + Fermat) reproduced the measured keep-fraction sweep within 3%; 'sieve x0.6' shows the case where only 60% of the sieve's alone time lands on the batch.
"""
import sys, json, math, glob
runs = [json.loads(l[5:]) for f in sys.argv[1:] for l in open(f) if l.startswith("JSON ")]
Bs = sorted(runs[0].keys(), key=float)
fs = sorted(runs[0][Bs[0]]["Y"].keys(), key=float)
Y = {B: {f: sum(r[B]["Y"][f] for r in runs) / len(runs) for f in fs} for B in Bs}
p = {B: runs[0][B]["p"] for B in Bs}

def pi(x):
    l = math.log(x)
    return x / l * (1 + 1 / l + 2 / l ** 2)
V0 = pi(1e8) - pi(1e6); MK0 = math.log(math.log(1e8) / math.log(1e6))
def S(B):
    B = float(B)
    v = (pi(B) - pi(1e6)) / V0
    mk = math.log(math.log(B) / math.log(1e6)) / MK0
    return 27.5 * (0.62 * v + 0.38 * mk) + 9.0 * mk + 24.2          # ms
def F1(B):
    return 8.53 * p["100000000"] / p[B]
for scale, name in ((1.0, "serial-sum"), (0.6, "sieve x0.6")):
    base = Y["100000000"]["0.985"] / (scale * S(1e8) * 1e-3 + F1("100000000") * 0.015)
    print(f"--- {name}: design hits a second relative to B = 1e8, f = 0.985 (S(1e8) = {S(1e8):.1f} ms) ---")
    best = (None, 0)
    for B in Bs:
        row = []
        for f in fs:
            r = Y[B][f] / (scale * S(B) * 1e-3 + F1(B) * (1 - float(f))) / base
            row.append(f"{f}:{r:.3f}")
            if r > best[1]:
                best = ((B, f), r)
        print(f"  B={float(B):.3g} (S {S(B):.1f} ms, p {p[B]:.4f}): " + "  ".join(row))
    print(f"  best: B={float(best[0][0]):.3g}, f={best[0][1]}: x{best[1]:.3f}")
