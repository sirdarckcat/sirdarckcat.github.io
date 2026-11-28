# covers re-measured in weighted rows: "COVER ceil(weighted rows) r:a ..." sorted best first; stats to stderr
#   python3 family_search/reweigh.py weights.txt covers.txt [more.txt ...] > out.txt
import sys, math
import numpy as np
W = np.loadtxt(sys.argv[1], dtype=np.int64); q, w = W[:, 0], W[:, 1]
rmod = {}; out = []; seen = set()
for f in sys.argv[2:]:
    for line in open(f):
        t = line.split()
        if not t or t[0] != "COVER" or len(t) < 3: continue
        key = " ".join(t[2:])
        if key in seen: continue
        seen.add(key)
        cov = np.zeros(len(q), dtype=bool)
        try:
            for x in t[2:]:
                r, a = map(int, x.split(":"))
                if r not in rmod: rmod[r] = q % r
                cov |= rmod[r] == a
        except ValueError: continue
        out.append((int(w[~cov].sum()), key))
out.sort()
for ws, key in out: print("COVER", -(-ws // 64), key)
v = np.array([o[0] for o in out]) / 64
print(f"{len(out)} covers; weighted rows min {v.min():.2f}, median {np.median(v):.2f}, max {v.max():.2f}", file=sys.stderr)
