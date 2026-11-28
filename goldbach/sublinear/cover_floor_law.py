# cover_floor_law.py x1 file [file ...] -- x2 file ... : measurements of ln g0 (the number of complete covers) from runs of
# cover_floor.c made with COVER_FLOOR_REACH, against the line theta(x) - Q/ln^2 x.  Groups of files for one set of moduli
# (the odd primes up to x) are separated by "--"; Q is read from each file's header.
import math, sys
from cover_floor import analyse
def theta_odd(r):
    s = bytearray([1]) * (r + 1)
    for i in range(2, int(r ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return sum(math.log(p) for p in range(3, r + 1) if s[p])
def S0(f):
    par, reps = analyse(f); cold = reps[-1]; z = cold["H"][cold["E"] == 0].sum()
    return (int(par["Q"]), cold["lnZ"] + math.log(z / cold["n"]), z / cold["n"], int(par["sweeps"])) if z > 0 else None
groups = [[]]
for a in sys.argv[1:]:
    if a == "--": groups.append([])
    else: groups[-1].append(a)
for g in groups:
    if not g: continue
    x = int(g[0]); th = theta_odd(x); l2 = math.log(x) ** 2; byQ = {}
    for f in g[1:]:
        v = S0(f)
        if v: byQ.setdefault(v[0], []).append(v)
        else: print(f"    {f}: no complete cover sampled at the coldest temperature")
    pts = [(Q, sum(v[1] for v in vs) / len(vs), max(v[1] for v in vs) - min(v[1] for v in vs), len(vs), min(v[2] for v in vs)) for Q, vs in sorted(byQ.items())]
    print(f"x = {x}: theta = {th:.1f}, 1/ln^2 x = {1 / l2:.6f}, theta ln^2 x = {th * l2:.0f}")
    for i, (Q, S, sp, nv, sh) in enumerate(pts):
        loc = f"; slope from the previous target {(pts[i-1][1] - S) / (Q - pts[i-1][0]) * l2:.3f}" if i else ""
        print(f"    Q = {Q:7d}: ln g0 = {S:8.1f} ({nv} run{'s' if nv > 1 else ''}, spread {sp:.1f}, share of complete samples >= {sh:.2f}); line {th - Q / l2:8.1f}; (theta - ln g0) ln^2 x / Q = {(th - S) * l2 / Q:.3f}{loc}")
    if len(pts) > 1:
        n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
        b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts); a = my - b * mx
        print(f"    least squares: slope {-b * l2:.3f} / ln^2 x, value at Q = 0 {a:.1f} (theta {th:.1f}), end of the line {-a / b:.0f}")
