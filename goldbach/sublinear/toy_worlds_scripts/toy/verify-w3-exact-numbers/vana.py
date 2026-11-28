# my own analysis of my own pass-2 statistics
import sys, math, collections
def load(q, n):
    D = dict(bins=collections.defaultdict(list), mg=collections.defaultdict(dict), jss=collections.defaultdict(list), thr={}, lev={}, lst=[])
    for line in open(f"out/w_{q}_{n}.txt"):
        t = line.split()
        if t[0] == "q": D["hdr"] = dict(zip(t[0::2], (int(x) for x in t[1::2])))
        elif t[0] == "NT": D["troom"] = int(t[3]); D["tlin"] = int(t[5]); D["tdeg2"] = int(t[7]); D["tdeg3"] = int(t[9]); D["roomdeg"] = int(t[11])
        elif t[0] == "THR": D["thr"][int(t[1])] = dict(K=int(t[3]), name=t[4], rough=int(t[6]), roughodd=int(t[8]))
        elif t[0] == "BIN": l, R, th, s, o, c, h, ta, to = map(int, t[1:]); D["lev"][l] = R; D["bins"][(l, th)].append((s, o, c, h, ta, to))
        elif t[0] == "MAXG": D["mg"][(int(t[1]), int(t[3]))][int(t[4])] = int(t[5])
        elif t[0] == "JSS": D["jss"][int(t[1])].append((int(t[3]), int(t[4]), int(t[5])))
        elif t[0] == "GH": D.setdefault("gh", {})[int(t[1])] = int(t[2])
        elif t[0] == "LIST": D["lst"].append(line.strip())
    return D
def capture(bl, keyidx, phi, tot):
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])
    for b in bl:
        a = agg[b[keyidx]]; a[0] += b[2]; a[1] += b[3]; a[2] += b[4]; a[3] += b[5]
    need = phi * tot; got = [0.0] * 4
    for kk in sorted(agg):
        a = agg[kk]; rem = need - got[0]
        if rem <= 0: break
        fr = min(1.0, rem / a[0])
        for j in range(4): got[j] += fr * a[j]
    return got   # members, hits, tests_all, tests_odd
def firsthit(bl, keyidx):
    agg = collections.Counter(); hit = collections.Counter()
    for b in bl: agg[b[keyidx]] += b[2]; hit[b[keyidx]] += b[3]
    cum = 0
    for kk in sorted(agg):
        if hit[kk]: return cum + (agg[kk] + 1) / (hit[kk] + 1), kk, cum, agg[kk], hit[kk]
        cum += agg[kk]
def run(q, n):
    D = load(q, n); tot = q ** n; irr = D["hdr"]["irr_n"]; thr = D["thr"]; NT = len(thr); L = len(D["lev"]); bins = D["bins"]
    rho = {t: irr / thr[t]["rough"] for t in thr}; rhoo = {t: irr / thr[t]["roughodd"] for t in thr}
    tr = D["troom"]; t2 = D["tdeg2"]; t3 = D["tdeg3"]; tl = D["tlin"]
    print(f"\n===== q={q} n={n}; thresholds " + ", ".join(f"t{t}:{thr[t]['name']}(K={thr[t]['K']})" for t in thr) + f"; room total degree {D['roomdeg']} -> cell size {q ** (n - D['roomdeg'])}")
    print(" first moment (hits/model) per level: naive | room s-model | room o-model | deg2 o-model | deg3 o-model | deg2 s | deg3 s")
    for l in range(L):
        R = D["lev"][l]; H = sum(b[3] for b in bins[(l, 0)])
        def ms(t): return H / sum(b[2] * (1 - rho[t]) ** b[0] for b in bins[(l, t)])
        def mo(t):
            m = sum(b[2] * max(1 - rhoo[t], 0) ** b[1] for b in bins[(l, t)]); return H / m if m > 0 else float("nan")
        print(f"   R={R:4d} hits={H:9d}: {H / (tot * (1 - rho[0]) ** R):10.3f} | {ms(tr):.3f} | {mo(tr):.3f} | {mo(t2):.3f} | {mo(t3):.3f} | {ms(t2):.3f} | {ms(t3):.3f}")
    print(" parity selection: level | t | odd-only gain | 10%: E_s E_o modelE_o T | 1%: E_s E_o modelE_o T")
    for l in range(L):
        R = D["lev"][l]; H = sum(b[3] for b in bins[(l, 0)])
        if H < 90: continue
        for t in sorted({0, tl, tr}):
            bl = bins[(l, t)]; full = capture(bl, 0, 1.0, tot); line = f"   R={R:4d} H={H:8d} t{t}({thr[t]['name']:>8}) x{full[2] / full[3]:.2f} |"
            for phi in (0.1, 0.01):
                cs = capture(bl, 0, phi, tot); co = capture(bl, 1, phi, tot)
                Es = cs[1] / H / phi; Eo = co[1] / H / phi; T = (co[1] / co[3]) / (cs[1] / cs[2]) if co[3] else float("inf")
                # model capture from the exact distribution of o
                agg = collections.Counter()
                for b in bl: agg[b[1]] += b[2]
                Wt = sum(c * max(1 - rhoo[t], 0) ** o for o, c in agg.items()); need = phi * tot; got = 0; cap = 0
                for o in sorted(agg):
                    fr = min(1.0, (need - got) / agg[o])
                    if fr <= 0: break
                    got += fr * agg[o]; cap += fr * agg[o] * max(1 - rhoo[t], 0) ** o
                line += f" {Es:6.2f} {Eo:6.2f} {cap / Wt / phi:6.2f} T{T:6.2f} |"
            print(line)
    l = L - 1; R = D["lev"][l]
    print(f" anatomy at R={R}:")
    for t in range(NT):
        bl = bins[(l, t)]; c = sum(b[2] for b in bl); ms_ = sum(b[0] * b[2] for b in bl) / c; mo_ = sum(b[1] * b[2] for b in bl) / c
        ss = math.sqrt(sum((b[0] - ms_) ** 2 * b[2] for b in bl) / c); so = math.sqrt(sum((b[1] - mo_) ** 2 * b[2] for b in bl) / c)
        wts = [(b[1], b[2] * max(1 - rhoo[t], 0) ** b[1]) for b in bl]; sw = sum(x for o, x in wts); tilt = sum(o * x for o, x in wts) / sw if sw > 0 else float("nan")
        opt = [(b[0], b[1], b[3]) for b in bl if b[3]]
        print(f"   t{t}({thr[t]['name']:>8}): s {ms_:.2f}+-{ss:.2f}  o {mo_:.2f}+-{so:.2f}  model mean o for a hit {tilt:.2f}  optimum (s,o,#): {opt}  z_s {[round((s - ms_) / ss, 2) if ss else 0 for s, o, h in opt]} z_o {[round((o - mo_) / so, 2) for s, o, h in opt]}")
    H = sum(b[3] for b in bins[(l, 0)]); blind = (tot + 1) / (H + 1)
    ws = firsthit(bins[(l, tr)], 0); wo = firsthit(bins[(l, tr)], 1)
    print(f" cover first at R=Gmax: expected work by s_room {ws[0]:.0f} (bin s={ws[1]}, {ws[2]} better, bin {ws[3]}, hits {ws[4]}) blind {blind:.0f} gain {math.log(blind / ws[0]):.2f} nats = {100 * math.log(blind / ws[0]) / math.log(tot):.1f}% of ln q^n ({math.log(tot):.2f}); by o_room {wo[0]:.0f} gain {math.log(blind / wo[0]):.2f} nats")
    # equal work
    agg = collections.Counter()
    for b in bins[(l, tr)]: agg[b[0]] += b[2]
    mg = D["mg"][(l, tr)]; cum = 0; line = " equal work (W members -> best G): "; best = -1
    for s in sorted(agg):
        cum += agg[s]; best = max(best, mg[s])
        if cum / tot < 0.08: line += f"{cum}->{best}; "
    print(line)
    J = D["jss"][l]; allmin = min(b for a, b, c in J); aggA = collections.Counter()
    for a, b, c in J: aggA[a] += c
    cum = 0; line = f" soft score: true min s_deep {allmin}; cover first (W -> best s_deep): "
    for a in sorted(aggA):
        cum += aggA[a]; b_ = min(b for aa, b, c in J if aa <= a); line += f"{cum}->{b_}; "
        if b_ == allmin: line += f"(reached at W={cum}, {100 * cum / tot:.2g}% of all)"; break
    print(line)
    for s in D["lst"][:2]: print("   ", s)
if __name__ == "__main__":
    for a in sys.argv[1:]:
        q, n = map(int, a.split(",")); run(q, n)
