import sys, collections
fn, q, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); tot = q ** n
bins = collections.defaultdict(list)
for line in open(fn):
    t = line.split()
    if t[0] == "BIN": bins[int(t[1])].append(tuple(int(v) for v in t[2:]))
def select(bl, key, phi):
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])
    for s, o, c, h, ta, to in bl:
        a = agg[key(s, o)]
        for j, v in enumerate((c, h, ta, to)): a[j] += v
    H = sum(a[1] for a in agg.values()); need = phi * tot; got = [0.0] * 4
    for k in sorted(agg):
        a = agg[k]; f = min(1.0, (need - got[0]) / a[0])
        if f <= 0: break
        for j in range(4): got[j] += f * a[j]
    return got, H
for t in (0, 1):
    bl = bins[t]; full, H = select(bl, lambda s, o: s, 1.0)
    out = f"t{t}: hits {H}  odd-only testing gain x{full[2] / full[3]:.2f} |"
    for phi in (0.1, 0.01):
        gs, _ = select(bl, lambda s, o: s, phi); go, _ = select(bl, lambda s, o: o, phi)
        Es = gs[1] / H / phi; Eo = go[1] / H / phi; T = (go[1] / go[3]) / (gs[1] / gs[2])
        out += f" keep {phi}: E_s {Es:.2f} E_o {Eo:.2f} T x{T:.2f} |"
    print(out)
