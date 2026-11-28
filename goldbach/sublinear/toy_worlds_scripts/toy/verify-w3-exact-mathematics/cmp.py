import re, glob, collections
P = "../w3-exact/"
mine = {}
for fn in ("enum_small.txt", "enum_mid.txt", "enum_big.txt"):
    L = open(fn).read().split("\n")
    for i, s in enumerate(L):
        m = re.match(r"q (\d+) n (\d+) rows (\d+) Gmax (\d+) cnt (\d+) second (-?\d+) Dmax (\d+) cnt (\d+) exceptions (\d+) meanG ([\d.]+)", s)
        if m:
            g = m.groups(); mine[(int(g[0]), int(g[1]))] = tuple(int(v) for v in g[2:9]) + (float(g[9]),)
ok = 0; bad = []; hist_ok = 0
for s in open(P + "summary.txt"):
    t = re.match(r"\s*(\d+)\s+(\d+) \|\s*(\d+) \|\s*(\d+) \|\s*(\d+) \((\d+)\)\s+(\d+) \| (\d+) \((\d+)\) \| (\d+) \|\s*([\d.]+)", s)
    if not t: continue
    g = t.groups(); q, n = int(g[0]), int(g[1])
    theirs = (int(g[3]), int(g[4]), int(g[5]), int(g[6]), int(g[7]), int(g[8]), int(g[9]), float(g[10]))
    m = mine.get((q, n))
    same = m is not None and m[:7] == theirs[:7] and abs(m[7] - theirs[7]) < 0.006
    ok += same
    if not same: bad.append(((q, n), theirs, m))
    # full G histogram
    GH = collections.Counter()
    for line in open(P + f"out_{q}_{n}.txt"):
        u = line.split()
        if u and u[0] == "GH" and int(u[1]) <= n: GH[int(u[2])] += int(u[3])
    my = {int(a): int(b) for a, b in (l.split() for l in open(f"gh_{q}_{n}.txt"))}
    hist_ok += (dict(GH) == my)
print("instances in summary matched (rows, Gmax, count, second, Dmax, count, exceptions, mean G):", ok, "mismatches:", bad)
print("full G histograms identical:", hist_ok)
