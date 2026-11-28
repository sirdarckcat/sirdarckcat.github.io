# per instance: for each derivative class (0: N'=0; k+1: deg N' = k; n+1: N' = 1), count and max G, max D
import sys, glob, re, collections
for fn in sorted(glob.glob("out_*_*.txt"), key=lambda s: tuple(int(t) for t in re.findall(r"\d+", s)[-2:])):
    q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:])
    cnt = collections.Counter(); mx = {}; dmx = {}; allG = collections.Counter()
    for line in open(fn):
        t = line.split()
        if t[0] == "GH":
            c, g, k = int(t[1]), int(t[2]), int(t[3]); cnt[c] += k; mx[c] = max(mx.get(c, -1), g)
            if c <= n: allG[g] += k
        if t[0] == "DH":
            c, d = int(t[1]), int(t[2]); dmx[c] = max(dmx.get(c, 0), d)
    gs = sorted(allG, reverse=True)
    print(f"q={q} n={n}: top G values {[(g, allG[g]) for g in gs[:4]]}")
    print("    class:count:maxG:maxD  " + "  ".join(f"{('N1' if c == n + 1 else c - 1 if c else 'insep')}:{cnt[c]}:{mx[c]}:{dmx[c]}" for c in sorted(cnt)))
