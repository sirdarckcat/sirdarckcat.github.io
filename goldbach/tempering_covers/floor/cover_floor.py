#!/usr/bin/env python3
"""A floor under every cover, from the samples of cover_floor.c.

    python3 cover_floor.py run.txt [run2.txt ...]          the floor from each run, and the runs side by side
    python3 cover_floor.py --exact Q moduli.txt betas.txt [weights.txt]   the same by enumerating every cover (small sets)
    python3 cover_floor.py --reach run.txt [run2.txt ...]  the number of complete covers as a function of the target, from
                                                           runs with COVER_FLOOR_REACH (see cover_floor.c)

Z(b) = sum over all covers of exp(-b k), k = rows left.  Z(0) is the number of covers (the product of the moduli).
Between neighbouring temperatures ln Z changes by an amount estimated from the two histograms (Bennett's acceptance
ratio, which uses nothing colder), so ln Z(b) at any b rests only on the replicas up to b.  Then, for every b,

    k_min >= floor(b) = -ln Z(b) / b = <k>_b - S(b)/b,          S(b) = ln Z(b) + b <k>_b.

The floor is valid as far as the samples up to b are in equilibrium.  Diagnostics printed for that: the mean of k in
the four quarters of the run (drift), the forward and the backward one-sided estimates of each step of ln Z (they
differ when the histograms do not overlap or are not stationary), and, with several runs (a random start and a start
from the best cover known), the differences between the runs.
"""
import math, sys
import numpy as np

def read(path):
    lines = open(path).read().split("\n"); par = dict(t.split("=") for t in lines[0].split()[1:])
    out = []
    for i, line in enumerate(lines):
        if line.startswith("BETA"):
            t = line.split(); q = t.index("quarters")
            h = np.array([[float(v) for v in u.split(":")] for u in lines[i + 1].split()[1:]])
            core = [float(v) for v in t[q + 6:q + 10]] if len(t) > q + 5 and t[q + 5].startswith("core") else None
            out.append(dict(beta=float(t[1]), n=int(t[3]), mean=float(t[5]), sd=float(t[7]), min=float(t[9]), swap=float(t[11]), acc=float(t[13]),
                            quarters=[float(v) for v in t[q + 1:q + 5]], core=core, E=h[:, 0], H=h[:, 1]))
    return par, out

def lse(a):
    m = np.max(a); return float(m + np.log(np.sum(np.exp(a - m))))

def bar(r0, r1):
    """ln(Z1/Z0) from the samples at beta0 (r0) and beta1 (r1): forward, backward and Bennett's estimate"""
    db = r1["beta"] - r0["beta"]
    fwd = lse(np.log(r0["H"]) - db * r0["E"]) - math.log(r0["n"])
    bwd = -(lse(np.log(r1["H"]) + db * r1["E"]) - math.log(r1["n"]))
    M = math.log(r1["n"] / r0["n"])
    def g(d):                                   # d = ln(Z1/Z0); zero of g is the estimate
        a = np.sum(r0["H"] / (1 + np.exp(np.clip(M + db * r0["E"] + d, -700, 700))))
        b = np.sum(r1["H"] / (1 + np.exp(np.clip(-M - db * r1["E"] - d, -700, 700))))
        return a - b
    lo, hi = min(fwd, bwd) - 5, max(fwd, bwd) + 5
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0: lo = mid
        else: hi = mid
    return fwd, bwd, 0.5 * (lo + hi)

def analyse(path):
    par, reps = read(path); lnZ = [float(par["ln(states)"])]; gap = [0.0]
    for i in range(len(reps) - 1):
        f, b, d = bar(reps[i], reps[i + 1]); lnZ.append(lnZ[-1] + d); gap.append(gap[-1] + abs(f - b))
    for r, z, g in zip(reps, lnZ, gap):
        r["lnZ"] = z; r["S"] = z + r["beta"] * r["mean"]; r["floor"] = -z / r["beta"] if r["beta"] > 0 else float("-inf"); r["gap"] = g
    return par, reps

def exact(Q, moduli, betas, wfile=None):
    if wfile:                                   # weighted rows: "q weight" lines, 64 = a full row
        t = np.array([[int(v) for v in line.split()] for line in open(wfile) if line.strip()]); rows, w = t[:, 0], t[:, 1]
    else:
        s = np.ones(Q, dtype=bool); s[:2] = False
        for i in range(2, int(Q ** .5) + 1):
            if s[i]: s[i * i::i] = False
        rows = np.nonzero(s)[0]; rows = rows[rows > 2]; w = np.full(len(rows), 64)
    cov = [np.array([[q % m == a for q in rows] for a in range(m)]) for m in moduli]
    hist = np.zeros(int(w.sum()) + 1)           # energies in 64ths of a row
    def rec(i, covered):
        if i == len(moduli) - 1:
            k = (~(covered[None, :] | cov[i])) @ w
            np.add.at(hist, k, 1); return
        for a in range(moduli[i]): rec(i + 1, covered | cov[i][a])
    rec(0, np.zeros(len(rows), dtype=bool))
    E = np.nonzero(hist)[0]; lng = np.log(hist[E]); k0 = int(E[0]); E = E / 64.0; kmin = E[0]
    print(f"exact: Q={Q} rows={len(rows)} moduli={moduli} covers={int(hist.sum())} (ln {math.log(hist.sum()):.4f}); fewest rows left {kmin:g} ({int(hist[k0])} covers)")
    print("  beta    <k>      S(beta)    floor = -ln Z / beta")
    for b in betas:
        lz = lse(lng - b * E); mk = float(np.sum(np.exp(lng - b * E - lz) * E))
        print(f"  {b:5.2f} {mk:8.3f} {lz + b * mk:9.3f} " + (f"{-lz / b:9.3f}" if b > 0 else "     -inf"))

def reach(paths):
    """ln of the number of complete covers as a function of the target, from runs made with COVER_FLOOR_REACH"""
    print("# ln g0(y) = ln(number of class vectors that strike every odd prime below y); each run gives it at its own Q from ln Z at the")
    print("# coldest temperature and the share of samples with k = 0 there, and beyond Q from the reach of its complete covers")
    pts = []
    for path in paths:
        par, reps = analyse(path); Q = int(par["Q"]); cold = reps[-1]
        z = cold["H"][cold["E"] == 0].sum()
        line = [l for l in open(path) if l.startswith("REACH")]
        if z == 0 or not line: print(f"# {path}: Q={Q}: no complete cover sampled at the coldest temperature"); continue
        S0 = cold["lnZ"] + math.log(z / cold["n"])
        h = np.array([[int(v) for v in u.split(":")] for u in line[0].split()[1:]]); tot = h[:, 1].sum(); tail = np.cumsum(h[::-1, 1])[::-1]
        print(f"# {path}: Q={Q} moduli={par['moduli']} sweeps={par['sweeps']}: ln g0({Q}) = {S0:.2f}; {tot} samples of complete covers, reach up to {h[-1, 0]}")
        pts.append((Q, S0, 0, path))
        for y, c in zip(h[:, 0], tail):
            if y > Q and c >= 20: pts.append((int(y), S0 + math.log(c / tot), int(c), path))
    pts.sort()
    print("#      y   ln g0(y)   samples beyond   run")
    for y, s, c, path in pts: print(f"  {y:7d} {s:9.2f} {c if c else '':>12}   {path}")
    return pts

if __name__ == "__main__":
    if sys.argv[1] == "--reach":
        reach(sys.argv[2:]); sys.exit(0)
    if sys.argv[1] == "--exact":
        exact(int(sys.argv[2]), [int(v) for v in open(sys.argv[3]).read().split()], [float(v) for v in open(sys.argv[4]).read().split()], sys.argv[5] if len(sys.argv) > 5 else None)
        sys.exit(0)
    runs = [analyse(p) for p in sys.argv[1:]]
    for p, (par, reps) in zip(sys.argv[1:], runs):
        print(f"# {p}: " + " ".join(f"{k}={v}" for k, v in par.items()))
        print("  beta    <k>     sd   lowest  quarters of the run (mean k)             exchange  S(beta)   floor   forward/backward mismatch so far")
        for r in reps:
            print(f"  {r['beta']:5.2f} {r['mean']:8.2f} {r['sd']:5.1f} {r['min']:7.5g}   " + " ".join(f"{v:8.2f}" for v in r["quarters"]) + f"   {r['swap']:6.2f} {r['S']:9.2f} "
                  + (f"{r['floor']:8.2f}" if r["beta"] > 0 else "    -inf") + f" {r['gap']:7.3f}" + (("   same class as the start on the first moduli: " + " ".join(f"{v:5.2f}" for v in r["core"])) if r["core"] else ""))
        best = max(reps[1:], key=lambda r: r["floor"])
        print(f"  highest floor in this run: {best['floor']:.2f} at beta {best['beta']:.2f}; lowest k seen {min(r['min'] for r in reps):g}\n")
    if len(runs) > 1:
        print("# runs side by side: <k> and floor at each beta, and the spread between the runs")
        for i in range(len(runs[0][1])):
            rs = [reps[i] for _, reps in runs]
            if rs[0]["beta"] == 0: continue
            print(f"  {rs[0]['beta']:5.2f}  <k> " + " ".join(f"{r['mean']:8.2f}" for r in rs) + f"  (spread {max(r['mean'] for r in rs) - min(r['mean'] for r in rs):5.2f})   floor "
                  + " ".join(f"{r['floor']:8.2f}" for r in rs) + f"  (spread {max(r['floor'] for r in rs) - min(r['floor'] for r in rs):5.2f})")
