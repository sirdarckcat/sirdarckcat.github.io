# Independent recomputation (python-flint) of G and D for the best 5 N of every instance listed by the C program,
# and of the anatomy numbers (s_t, o_t at R = Gmax) of the optimum where a pass-2 file exists.
import sys, re, glob, os
from gfcommon import World, ftype
files = sorted(glob.glob("out_*_*.txt"), key=lambda s: tuple(int(t) for t in re.findall(r"\d+", s)[-2:]))
cache = {}
for fn in files:
    q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:])
    if n < 5: continue
    W = World(q); top = []; rb = None
    for line in open(fn):
        t = line.split()
        if t[0] == "TOP" and len(top) < 5: top.append((int(t[1]), int(t[2])))
        if t[0] == "rows_below:": rb = [0] + [int(v) for v in t[1:]]
        if t[0] == "Gmax": Dmax = int(t[3])
    md = min(n - 1, Dmax + 1)
    if (q, md) not in cache: cache[(q, md)] = W.rows(md)
    rows = cache[(q, md)]; ok = True
    for v, G in top:
        N = W.poly(v, n); g = next((i for i, Q in enumerate(rows) if (N - Q).is_irreducible()), len(rows))
        ok &= (g == G)
    msg = f"q={q} n={n}: top 5 G values {[g for v, g in top]} recomputed with flint: {'agree' if ok else 'DISAGREE'}"
    lf = f"lev_{q}_{n}.txt"
    if os.path.exists(lf):
        K = {}; opt = {}; R = top[0][1]
        for line in open(lf):
            t = line.split()
            if t[0] == "threshold": K[int(t[1])] = int(t[2].split("=")[1])
            if t[0] == "BIN" and int(t[2]) == R and int(t[7]) > 0: opt.setdefault(int(t[3]), []).append((int(t[4]), int(t[5])))
        irr = W.rows(3)      # ordered irreducibles, enough for all thresholds
        for v, G in top:
            if G != R or not opt: continue
            N = W.poly(v, n); agree = True
            for t, k in K.items():
                s = o = 0
                for Q in rows[:R]:
                    f = N - Q
                    if any((f % P).is_zero() for P in irr[:k]): continue
                    typ, sqf = ftype(f); s += 1; o += (sqf and len(typ) % 2 == 1)
                agree &= (s, o) in opt[t]
            msg += f"; anatomy (s_t, o_t) of optimum v={v} {'agrees' if agree else 'DISAGREES'} with pass 2"
    print(msg)
