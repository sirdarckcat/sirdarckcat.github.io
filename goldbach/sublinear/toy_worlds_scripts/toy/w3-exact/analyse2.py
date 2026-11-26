# Analysis of a pass-2 file (gfgold with levels): first-moment models, parity enrichment, cover first, anatomy of the optimum.
# Everything here is exact arithmetic on complete counts over all q^n monic N (no sampling).
import sys, re, math, collections
fn = sys.argv[1]; q, n = (int(t) for t in re.findall(r"\d+", fn)[-2:]); tot = q ** n
thr = {}; bins = collections.defaultdict(list); maxG = collections.defaultdict(dict); jss = collections.defaultdict(list); jso = collections.defaultdict(list)
levels = {}; GH = collections.Counter()
for line in open(fn):
    t = line.split()
    if t[0] == "threshold":
        thr[int(t[1])] = dict(K=int(t[2].split("=")[1]), name=line.split("(")[1].split(")")[0], rho=float(t[-2].split("=")[1]), rhoo=float(t[-1].split("=")[1]))
    elif t[0] == "BIN":
        l, R, th, s, o, cnt, hits, tall, todd = (int(v) for v in t[1:]); levels[l] = R; bins[(l, th)].append((s, o, cnt, hits, tall, todd))
    elif t[0] == "MAXG": maxG[(int(t[1]), int(t[3]))][int(t[4])] = int(t[5])
    elif t[0] == "JSS": jss[int(t[1])].append((int(t[3]), int(t[4]), int(t[5])))
    elif t[0] == "JSO": jso[int(t[1])].append((int(t[3]), int(t[4]), int(t[5])))
    elif t[0] == "TROOM": troom, tdeep = int(t[1]), int(t[3])
    elif t[0] == "GH" and int(t[1]) <= n: GH[int(t[2])] += int(t[3])
    elif t[0] == "Gmax": Gmax = int(t[1])
NT = len(thr); L = len(levels)
def Asurv(g): return sum(v for gg, v in GH.items() if gg >= g)
print(f"=== q={q} n={n}: {tot} monic N, Gmax={Gmax}; thresholds: " + "; ".join(f"t{t}={thr[t]['name']} (first {thr[t]['K']} irreducibles; rho={thr[t]['rho']:.4f}, rho_odd={thr[t]['rhoo']:.4f})" for t in thr))
print("\n[1] first moment.  hits = #{N : first R rows all reducible} (exact).  model_s(t) = sum_N (1-rho_t)^s_t(N), model_o(t) = sum_N (1-rho_odd_t)^o_t(N);  shown: hits/model")
for l in range(L):
    R = levels[l]; H = sum(b[3] for b in bins[(l, 0)])
    s = f"  R={R:>4} hits={H:>9}  naive q^n(1-rho)^R: {H / (tot * (1 - thr[0]['rho']) ** R):8.3f} |"
    for t in range(NT):
        ms = sum(c * (1 - thr[t]['rho']) ** sv for sv, o, c, h, ta, to in bins[(l, t)])
        mo = sum(c * max(1 - thr[t]['rhoo'], 0) ** o for sv, o, c, h, ta, to in bins[(l, t)])
        s += f" t{t}: s {H / ms:7.3f} o {H / mo if mo > 0 else float('nan'):7.3f} |"
    print(s)
def select(bl, key, phis):
    # rank members by key (ascending); returns for each keep fraction phi: (captured hit fraction, tests_all, tests_odd, members) with the tie bin split pro rata
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])
    for s, o, c, h, ta, to in bl:
        a = agg[key(s, o)]; a[0] += c; a[1] += h; a[2] += ta; a[3] += to
    H = sum(a[1] for a in agg.values()); out = []
    for phi in phis:
        need = phi * tot; got = [0.0, 0.0, 0.0, 0.0]
        for k in sorted(agg):
            a = agg[k]; f = min(1.0, (need - got[0]) / a[0]) if a[0] else 0
            if f <= 0: break
            for j in range(4): got[j] += f * a[j]
        out.append((got[1] / H if H else 0, got[2], got[3], got[0], got[1]))
    return out
phis = [1.0, 0.1, 0.01]
def model_capture(bl, rhoo, phis):
    # the capture the model (1-rho_odd)^o predicts for ranking by o, from the exact distribution of o
    agg = collections.Counter()
    for s, o, c, h, ta, to in bl: agg[o] += c
    Wt = sum(c * max(1 - rhoo, 0) ** o for o, c in agg.items()); out = []
    for phi in phis:
        need = phi * tot; got = 0.0; cap = 0.0
        for o in sorted(agg):
            f = min(1.0, (need - got) / agg[o])
            if f <= 0: break
            got += f * agg[o]; cap += f * agg[o] * max(1 - rhoo, 0) ** o
        out.append(cap / Wt if Wt else float('nan'))
    return out
print("\n[2] parity as a selection variable (exact).  E_x(phi) = (share of the hits among the best phi of all N ranked by x)/phi, ties split pro rata.")
print("    s_t = rows among the first R with no factor among the first K_t irreducibles; o_t = those of them with mu = -1 (odd parity).  t0: no sieve, so o_0 is parity alone.")
print("    tests of a member = its listed rows up to and including its first irreducible one.  T = hits per test with (rank o_t, test odd rows) / hits per test with (rank s_t, test all rows left)")
print("    columns: R, hits, t | odd-only testing gain (no selection) | keep 10%: E_s, E_o, model E_o, T | keep 1%: E_s, E_o, model E_o, T")
for l in range(L):
    R = levels[l]; H = sum(b[3] for b in bins[(l, 0)])
    if H < 90: continue
    for t in range(NT):
        if thr[t]['rhoo'] > 0.95: continue
        rs = select(bins[(l, t)], lambda s, o: s, phis); ro = select(bins[(l, t)], lambda s, o: o, phis); mc = model_capture(bins[(l, t)], thr[t]['rhoo'], phis)
        line = f"  R={R:>4} hits={H:>8} t{t} ({thr[t]['name']:>14}) | x{rs[0][1] / rs[0][2]:5.2f} |"
        for j in (1, 2):
            phi = phis[j]; hs = rs[j][4] / rs[j][1]; ho = ro[j][4] / ro[j][2] if ro[j][2] else float('inf')
            line += f" {rs[j][0] / phi:6.2f} {ro[j][0] / phi:6.2f} {mc[j] / phi:6.2f} x{ho / hs:6.2f} |"
        print(line)
print("\n[3] anatomy of the optimum at R = Gmax (population = all N): rows left s_t and odd rows left o_t of the optimum against mean and sd over all N;")
print("    'tilt' = the mean of o_t over hits that the model (1-rho_odd_t)^o_t predicts")
l = L - 1; R = levels[l]
for t in range(NT):
    bl = bins[(l, t)]; c = sum(b[2] for b in bl)
    ms = sum(b[0] * b[2] for b in bl) / c; mo = sum(b[1] * b[2] for b in bl) / c
    ss = math.sqrt(sum((b[0] - ms) ** 2 * b[2] for b in bl) / c); so = math.sqrt(sum((b[1] - mo) ** 2 * b[2] for b in bl) / c)
    w = [(b[1], b[2] * max(1 - thr[t]['rhoo'], 0) ** b[1]) for b in bl]; tilt = sum(o * x for o, x in w) / sum(x for o, x in w) if sum(x for o, x in w) > 0 else float('nan')
    opt = [(b[0], b[1], b[3]) for b in bl if b[3]]
    print(f"  t{t} ({thr[t]['name']:>14}): s mean {ms:7.2f} sd {ss:5.2f}; o mean {mo:7.2f} sd {so:5.2f}; model tilt of o: {tilt:7.2f}; optimum (s,o,count): {opt}"
          + "".join(f"  z_s={(s - ms) / ss if ss else 0:+.2f} z_o={(o - mo) / so:+.2f}" for s, o, h in opt[:2]))
print(f"\n[4] cover first.  Members ranked by s_room = rows among the first R left by the pinned prefix (t{troom}: the first {thr[troom]['K']} irreducibles, total degree <= n), best cells first.")
for l in range(L):
    R = levels[l]; bl = bins[(l, troom)]; agg = collections.Counter(); hit = collections.Counter()
    for s, o, c, h, ta, to in bl: agg[s] += c; hit[s] += h
    H = sum(hit.values()); mg = maxG[(l, troom)]
    cum = 0; line = f"  R={R:>4} hits={H:>8}:"
    first = None; rows = []
    for s in sorted(agg):
        lo = cum; cum += agg[s]
        rows.append((s, lo, cum, max(mg[k] for k in mg if k <= s)))
        if first is None and hit[s]: first = (s, lo, cum, hit[s])
    s, lo, hi, h = first
    # expected work to the first hit: all better cells, then the tie bin at random: (c+1)/(h+1)
    w = lo + (hi - lo + 1) / (h + 1)
    line += f" first hit in bin s={s} (bin holds {hi - lo} members, {h} hits; {lo} members in better bins): expected work {w:.0f} against blind {(tot + 1) / (H + 1):.0f}: gain {((tot + 1) / (H + 1)) / w:.2f} ({math.log(((tot + 1) / (H + 1)) / w):+.2f} nats);"
    # work to all hits
    last = max(s for s in hit if hit[s]); whi = sum(agg[k] for k in agg if k <= last)
    line += f" last hit in bin s={last}: {whi} members ({whi / tot:.3f} of all)"
    print(line)
    if l == L - 1:
        print("    best G found by cover first after W members (whole bins), and the blind work for the same G (q^n / #{N: G >= that}):")
        for s, lo, hi, g in rows:
            if hi / tot > 3e-7 and (hi / tot < 0.6): print(f"      s<={s:>3}: W={hi:>10} ({hi / tot:.2e})  best G={g:>4}  #N with G>=best: {Asurv(g):>8}  blind work {tot / Asurv(g):.3g}  ratio {tot / Asurv(g) / hi:.2f}")
print("\n[4b] expected work (members examined) to the first hit when all N are ranked by a variable, ties at random; gain over blind in nats.  Variables: s_t (rows left) and o_t (odd rows left)")
for l in range(L):
    R = levels[l]; H = sum(b[3] for b in bins[(l, 0)]); blind = (tot + 1) / (H + 1); line = f"  R={R:>4} hits={H:>8} blind {blind:10.0f} |"
    for t in range(NT):
        for nm, key in (("s", 0), ("o", 1)):
            if t == 0 and nm == "s": continue
            agg = collections.Counter(); hit = collections.Counter()
            for b in bins[(l, t)]: agg[b[key]] += b[2]; hit[b[key]] += b[3]
            cum = 0
            for k in sorted(agg):
                if hit[k]: w = cum + (agg[k] + 1) / (hit[k] + 1); break
                cum += agg[k]
            line += f" {nm}{t}: {w:9.0f} ({math.log(blind / w):+5.2f})"
    print(line)
print(f"\n[5] the soft score.  s_deep = rows left after sieving by every irreducible of the deepest threshold (t{tdeep}); cover first ranks by s_room.")
for l in (L - 1,):
    R = levels[l]; J = jss[l]; allmin = min(b for a, b, c in J); nmin = sum(c for a, b, c in J if b == allmin)
    amin = sorted(a for a, b, c in J if b == allmin)
    aggA = collections.Counter();
    for a, b, c in J: aggA[a] += c
    print(f"  R={R}: min s_deep over all N = {allmin} ({nmin} N); they sit in s_room bins {amin}; ")
    cum = 0
    for a in sorted(aggA):
        cum += aggA[a]; best = min(b for aa, b, c in J if aa <= a)
        if cum / tot < 0.5: print(f"      s_room<={a:>3}: W={cum:>10} ({cum / tot:.2e})  best s_deep found {best}  (true best {allmin})")
