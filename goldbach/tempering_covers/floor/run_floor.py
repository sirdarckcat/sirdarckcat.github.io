# Where do complete covers END? For each x of T2, ln g0(Q) = ln(number of complete covers of the odd primes below Q by the
# odd primes up to x) from the research session's cover_floor (copied here from ccr-d4a17dd0-7uu03r, goldbach/sublinear,
# commit 29b8903), at four targets, about 60%, 75%, 85% and 93% of the tempered reach, two seeds each; then the straight-line
# end Q + ln g0(Q) / |slope| from the last interval.  Runs are single-threaded (OMP_NUM_THREADS=1: the result does not depend
# on the thread count, and one thread does not spin on a shared machine), several at a time; a run whose output exists is skipped.
#   python3 run_floor.py run [procs] [x ...]      the runs
#   python3 run_floor.py start [procs] [x ...] [--target i]   a target once more (default the 93% one), started from the best tempered cover
#   python3 run_floor.py all [procs] x [x ...]      per x: the 8 random-start runs, then cover starts at the 85% and 93% targets
#   python3 run_floor.py report [x ...]           ln g0 per target and seed, slopes, ends (floor_report.md, floor_points.json)
import json, math, os, subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); T2 = os.path.dirname(HERE)
sys.path.insert(0, T2)
from reach import first_unstruck
XS = (127, 149, 251, 349, 397, 599)
FRACS = (0.60, 0.75, 0.85, 0.93)
SEEDS = (1, 2)
SWEEPS, BURN = 400000, 100000

def tempered_reach():
    """x -> (reach of the best tempered vector, the Q it was found at), from t2_runs.jsonl (every run, probes included)"""
    best = {}
    for l in open(os.path.join(T2, "t2_runs.jsonl")):
        r = json.loads(l)
        if r["k"] == 0 and (r["x"] not in best or r["Q"] > best[r["x"]]["Q"]): best[r["x"]] = r
    return {x: (first_unstruck([tuple(map(int, t.split(":"))) for t in r["best"].split()]), r["Q"]) for x, r in best.items()}

def targets(reach): return [int(round(f * reach)) for f in FRACS]

def out_name(x, Q, s): return os.path.join(HERE, "runs", f"out_x{x}_Q{Q}_s{s}.txt")

def one(job):
    x, Q, s, Y = job
    out = out_name(x, Q, s)
    if os.path.exists(out): return out
    tmp = out + ".part"
    log = open(out.replace(".txt", ".log"), "w")
    subprocess.run([os.path.join(HERE, "cover_floor"), str(Q), f"odd<={x}", os.path.join(HERE, "cover_floor_betas_deep.txt"), str(SWEEPS), str(BURN), tmp, str(s)],
                   env=dict(os.environ, OMP_NUM_THREADS="1", COVER_FLOOR_REACH=str(Y)), stdout=log, stderr=subprocess.STDOUT, check=True)
    os.rename(tmp, out); print(f"done x={x} Q={Q} seed={s}", flush=True)
    return out

def best_vector(x):
    best = None
    for l in open(os.path.join(T2, "t2_runs.jsonl")):
        r = json.loads(l)
        if r["x"] == x and r["k"] == 0 and (best is None or r["Q"] > best["Q"]): best = r
    return best["best"]

def start_name(x, Q): return os.path.join(HERE, "runs", f"out_x{x}_Q{Q}_s1_start.txt")

def one_start(job):
    x, Q, Y = job
    out = start_name(x, Q)
    if os.path.exists(out): return out
    sf = os.path.join(HERE, "runs", f"start_x{x}.txt"); open(sf, "w").write(best_vector(x) + "\n")
    log = open(out.replace(".txt", ".log"), "w")
    subprocess.run([os.path.join(HERE, "cover_floor"), str(Q), f"odd<={x}", os.path.join(HERE, "cover_floor_betas_deep.txt"), str(SWEEPS), str(BURN), out + ".part", "1", sf],
                   env=dict(os.environ, OMP_NUM_THREADS="1", COVER_FLOOR_REACH=str(Y)), stdout=log, stderr=subprocess.STDOUT, check=True)
    os.rename(out + ".part", out); print(f"done x={x} Q={Q} start at the tempered cover", flush=True)
    return out

def quarters_drift(path):
    """how far the run still moves: d(beta) = <k> in the 4th quarter minus the 2nd, at each temperature. Integrated over beta it is
    the change of ln Z (so of ln g0) between those quarters, in nats, with the sign of ln g0 (positive: still rising, the run
    underestimates). Also the largest |d| at the middle temperatures (0.5 <= beta <= 3) and at the cold ones (beta > 3), in rows."""
    B, D = [], []
    for line in open(path):
        if line.startswith("BETA"):
            t = line.split(); q = t.index("quarters")
            B.append(float(t[1])); D.append(float(t[q + 4]) - float(t[q + 2]))
    nats = -sum((D[i] + D[i + 1]) / 2 * (B[i + 1] - B[i]) for i in range(len(B) - 1))
    mid = max((abs(d) for b, d in zip(B, D) if 0.5 <= b <= 3.0), default=0.0)
    cold = max((abs(d) for b, d in zip(B, D) if b > 3.0), default=0.0)
    return nats, mid, cold

# the research session's figures for the loss theta - ln g0, written down before these runs (cover_price_hl.txt, commit 6d3ebdf on
# ccr-d4a17dd0-7uu03r): (pair sum, closed formula) per target
PRED = {797: [(434.0, 433.3), (535.5, 537.8), (601.6, 606.2), (656.3, 662.9)],
        1499: [(791.9, 796.1), (978.2, 987.7), (1104.9, 1118.7), (1200.9, 1216.5)],
        1999: [(1024.8, 1032.7), (1263.8, 1277.3), (1425.3, 1443.1), (1553.3, 1573.2)]}

def reach_points(paths):
    """run cover_floor.py --reach on the given outputs; returns [(y, ln g0, samples beyond, path)]"""
    txt = subprocess.run([sys.executable, os.path.join(HERE, "cover_floor.py"), "--reach"] + paths, capture_output=True, text=True, check=True).stdout
    pts = []
    for line in txt.splitlines():
        m = re.match(r"\s+(\d+)\s+(-?[\d.]+)\s+(\d*)\s+(\S+)$", line)
        if m: pts.append((int(m.group(1)), float(m.group(2)), int(m.group(3)) if m.group(3) else 0, m.group(4)))
    return txt, pts

if __name__ == "__main__":
    mode = sys.argv[1]
    R = tempered_reach()
    if mode == "run":
        procs = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        xs = [int(a) for a in sys.argv[3:]] or list(XS)
        os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
        jobs = [(x, Q, s, 2 * R[x][0]) for x in xs for Q in targets(R[x][0]) for s in SEEDS]
        with ThreadPoolExecutor(procs) as ex: list(ex.map(one, jobs))
    elif mode == "all":                                  # per x in the given order: the 8 random-start runs, then cover starts at the 85% and 93% targets
        procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        xs = [int(a) for a in sys.argv[3:]]
        os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
        jobs = []
        for x in xs:
            Qs = targets(R[x][0]); Y = 2 * R[x][0]
            jobs += [(one, (x, Q, s, Y)) for Q in Qs for s in SEEDS] + [(one_start, (x, Qs[2], Y)), (one_start, (x, Qs[3], Y))]
        with ThreadPoolExecutor(procs) as ex: list(ex.map(lambda j: j[0](j[1]), jobs))
    elif mode == "start":
        procs = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        args = sys.argv[3:]; ti = -1
        if "--target" in args: i = args.index("--target"); ti = int(args[i + 1]); args = args[:i] + args[i + 2:]   # index into FRACS (default: the last, 93%)
        xs = [int(a) for a in args] or list(XS)
        with ThreadPoolExecutor(procs) as ex: list(ex.map(one_start, [(x, targets(R[x][0])[ti], 2 * R[x][0]) for x in xs]))
    elif mode == "report":
        xs = [int(a) for a in sys.argv[2:]] or list(XS)
        rep, allpts = [], {}
        for x in xs:
            reach, Qr = R[x]; Qs = targets(reach)
            paths = [out_name(x, Q, s) for Q in Qs for s in SEEDS if os.path.exists(out_name(x, Q, s))]
            if not paths: continue
            txt, pts = reach_points(paths)
            at = {}                                     # (Q, seed) -> ln g0(Q) from that run's own target
            for y, v, c, p in pts:
                m = re.search(r"_Q(\d+)_s(\d+)\.txt$", p)
                if m and int(m.group(1)) == y and c == 0: at[(y, int(m.group(2)))] = v
            mean = {Q: sum(at[(Q, s)] for s in SEEDS if (Q, s) in at) / max(1, sum((Q, s) in at for s in SEEDS)) for Q in Qs if any((Q, s) in at for s in SEEDS)}
            Qd = sorted(mean); slope = end = None
            if len(Qd) >= 2:
                q1, q2 = Qd[-2], Qd[-1]; slope = (mean[q2] - mean[q1]) / (q2 - q1) * 1000
                end = q2 + mean[q2] / (-slope / 1000) if slope < 0 else None
            tail = [(y, v, c) for y, v, c, p in pts if c > 0 and p.endswith(f"_Q{Qd[-1]}_s1.txt")] if Qd else []
            allpts[x] = dict(reach=reach, Q_found=Qr, targets=Qs, ln_g0={f"{Q}:{s}": at[(Q, s)] for (Q, s) in sorted(at)},
                             slope_per_1000=slope, straight_end=end, tail_last_target_seed1=tail)
            rep.append(f"### x = {x:,}: tempered reach {reach:,} (vector found at Q = {Qr:,})\n")
            rep.append("| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |")
            rep.append("|---|---|---|---|---|")
            for Q in Qs:
                v = [f"{at[(Q, s)]:.2f}" if (Q, s) in at else "–" for s in SEEDS]
                rep.append(f"| {Q:,} | {Q / reach:.2f} | {v[0]} | {v[1]} | {mean[Q]:.2f} |" if Q in mean else f"| {Q:,} | {Q / reach:.2f} | {v[0]} | {v[1]} | – |")
            if slope is not None:
                rep.append(f"\nSlope of the last interval: {slope:.2f} per 1,000. Straight-line end: " + (f"{end:,.0f} ({end / reach:.3f} × the tempered reach)." if end else "none (not falling)."))
            if tail:
                rep.append(f"Tail of the {Qd[-1]:,} run (seed 1): ln g0 = " + ", ".join(f"{v:.1f} at {y:,}" for y, v, c in tail[::max(1, len(tail) // 6)]) + ".")
            # the research session's line: ln g0(Q) = theta(x) - c Q / ln^2 x, theta(x) = sum of ln r over the odd primes r <= x
            L2 = math.log(x) ** 2; th = sum(math.log(p) for p in range(3, x + 1, 2) if all(p % d for d in range(3, int(p ** 0.5) + 1, 2)))
            cons = [(-(mean[b] - mean[a]) / (b - a) * L2) for a, b in zip(Qd, Qd[1:])]
            xs_, ys_ = [Q for (Q, s) in sorted(at)], [at[(Q, s)] for (Q, s) in sorted(at)]
            if len(set(xs_)) >= 2:
                n = len(xs_); mx = sum(xs_) / n; my = sum(ys_) / n
                b1 = sum((u - mx) * (v - my) for u, v in zip(xs_, ys_)) / sum((u - mx) ** 2 for u in xs_); b0 = my - b1 * mx
                c_fit = -b1 * L2; end_ls = -b0 / b1
                res = {Q: mean[Q] - (b0 + b1 * Q) for Q in Qd}
                sd = {Q: abs(at[(Q, 1)] - at[(Q, 2)]) for Q in Qd if (Q, 1) in at and (Q, 2) in at}
                allpts[x].update(theta=th, ln2x=L2, slopes_c=cons, ls_intercept=b0, ls_c=c_fit, ls_end=end_ls, residuals={str(k): v for k, v in res.items()},
                                 seed_diff={str(k): v for k, v in sd.items()}, c1_end=th * L2)
                rep.append(f"\nThe line ln g0 = θ(x) − c·Q/ln²x: θ({x}) = {th:.2f} (odd primes), ln²x = {L2:.2f}.")
                rep.append("- slope between consecutive targets, in units of 1/ln²x: " + ", ".join(f"{c:.3f} ({a:,}–{b:,})" for c, (a, b) in zip(cons, zip(Qd, Qd[1:]))))
                rep.append(f"- least-squares line through the {n} points: intercept {b0:.2f} against θ(x) = {th:.2f} ({b0 - th:+.2f}); c = {c_fit:.3f}; "
                           f"end {end_ls:,.0f} = {end_ls / reach:.3f} × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = {th * L2:,.0f} ({th * L2 / reach:.3f} × reach).")
                rep.append("- residuals of the mean from that line: " + ", ".join(f"{res[Q]:+.2f} at {Q:,}" for Q in Qd) +
                           "; seed-to-seed differences: " + ", ".join(f"{sd[Q]:.2f}" for Q in Qd if Q in sd))
                if len(Qd) == 4:
                    u = Qd[:3]; m3 = sum(u) / 3; v3 = [mean[q] for q in u]; mv = sum(v3) / 3
                    s3 = sum((a - m3) * (b - mv) for a, b in zip(u, v3)) / sum((a - m3) ** 2 for a in u); i3 = mv - s3 * m3
                    dev = mean[Qd[3]] - (i3 + s3 * Qd[3])
                    c060 = (th - mean[Qd[0]]) / Qd[0] * L2; end3 = -i3 / s3
                    allpts[x].update(dev93_from_3pt_line=dev, c_0_to_60=c060, end_line3=end3)
                    rep.append(f"- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: {c060:.3f} in units of 1/ln²x; the straight line through the 60, 75 and 85% "
                               f"points ends at {end3:,.0f} = {end3 / reach:.3f} × the tempered reach")
                    rep.append(f"- the 93% point against the line through the first three: {dev:+.2f} (seed difference there {sd.get(Qd[3], float('nan')):.2f})"
                               + (": below by more than the seed difference" if dev < -sd.get(Qd[3], 0) else ""))
                    st = start_name(x, Qd[3])
                    if os.path.exists(st):
                        _, sp = reach_points([st]); v = [w for y, w, c, p in sp if y == Qd[3] and c == 0]
                        if v:
                            allpts[x].update(start93=v[0])
                            rep.append(f"- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = {v[0]:.2f}, against "
                                       + " and ".join(f"{at[(Qd[3], s)]:.2f}" for s in SEEDS if (Qd[3], s) in at) + " from random starts")
                    st85 = start_name(x, Qd[2])
                    if os.path.exists(st85):
                        _, sp = reach_points([st85]); v = [w for y, w, c, p in sp if y == Qd[2] and c == 0]
                        if v:
                            allpts[x].update(start85=v[0])
                            rep.append(f"- the 85% target started from the best tempered cover: ln g0 = {v[0]:.2f}, against "
                                       + " and ".join(f"{at[(Qd[2], s)]:.2f}" for s in SEEDS if (Qd[2], s) in at) + " from random starts")
                    # independent check of the last interval: the reach tail of the 85% runs (uniform samples of the complete covers at
                    # that target) at the largest y it still resolves (>= 20 samples), against the two lines
                    tl = [(y, v, c, p) for y, v, c, p in pts if c > 0 and re.search(rf"_Q{Qd[2]}_s\d\.txt$", p) and Qd[2] < y <= Qd[3]]
                    if tl:
                        y, v, c, p = max(tl)
                        lin = mean[Qd[2]] + (mean[Qd[3]] - mean[Qd[2]]) * (y - Qd[2]) / (Qd[3] - Qd[2]); l3 = i3 + s3 * y
                        allpts[x].update(tail85=dict(y=y, ln_g0=v, samples=c, interp=lin, line3=l3))
                        rep.append(f"- independent check from the tail of the {Qd[2]:,} run: ln g0({y:,}) = {v:.2f} ({c} samples) against {lin:.2f} between the 85% "
                                   f"and 93% points and {l3:.2f} on the line through the first three")
            if x in PRED:
                rep.append(f"\nLoss θ − ln g0 against the research session's figures (pair sum / closed formula), and the drift of each run between "
                           "its 2nd and 4th quarters (nats, + = ln g0 still rising; largest change of <k> at the middle and the cold temperatures, rows):\n")
                rep.append("| target Q | run | ln g0 | loss | predicted (pair sum) | measured / predicted | predicted (closed) | measured / predicted | drift (nats) | middle | cold |")
                rep.append("|---|---|---|---|---|---|---|---|---|---|---|")
                for i, Q in enumerate(Qd):
                    ps, cf = PRED[x][i] if i < len(PRED[x]) else (float("nan"), float("nan"))
                    runs_ = [(f"seed {s}", out_name(x, Q, s), at.get((Q, s))) for s in SEEDS]
                    stp = start_name(x, Q)
                    if os.path.exists(stp):
                        _, sp = reach_points([stp]); v = [w for y, w, c, p in sp if y == Q and c == 0]
                        runs_.append(("cover start", stp, v[0] if v else None))
                    for tag, p, v in runs_:
                        if v is None or not os.path.exists(p): continue
                        dn, dm, dc = quarters_drift(p); loss = th - v
                        rep.append(f"| {Q:,} | {tag} | {v:.2f} | {loss:.1f} | {ps:.1f} | {loss / ps:.3f} | {cf:.1f} | {loss / cf:.3f} | {dn:+.2f} | {dm:.2f} | {dc:.2f} |")
            rep.append("")
        hdr = ["### Summary", "", "c = slope in units of 1/ln²x. Ends are where a line reaches ln g0 = 0, as multiples of the tempered reach.", "",
               "| x | tempered reach | θ(x) | c, 0 to 60% | c, 60–75% | c, 75–85% | c, 85–93% | least-squares intercept − θ(x) | least-squares c | end: least squares | end: line through 60–85% | end: last interval | end: θ(x)·ln²x (c = 1) | 93% point below the 60–85% line (seed difference) | 93% from the tempered cover / random starts |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in xs:
            d = allpts.get(x)
            if not d or "ls_c" not in d or "end_line3" not in d: continue
            r = d["reach"]; Q4 = str(d["targets"][-1]); sd4 = d["seed_diff"].get(Q4, float("nan"))
            rs = [d["ln_g0"].get(f"{Q4}:{s}") for s in SEEDS]; st = d.get("start93")
            stx = (f"{st:.2f} / " + ", ".join(f"{v:.2f}" for v in rs if v is not None)) if st is not None else "–"
            hdr.append(f"| {x:,} | {r:,} | {d['theta']:.1f} | {d['c_0_to_60']:.3f} | " + " | ".join(f"{c:.3f}" for c in d["slopes_c"]) +
                       f" | {d['ls_intercept'] - d['theta']:+.1f} | {d['ls_c']:.3f} | {d['ls_end'] / r:.3f} | {d['end_line3'] / r:.3f} | {d['straight_end'] / r:.3f} | {d['c1_end'] / r:.3f} | "
                       f"{-d['dev93_from_3pt_line']:.2f} ({sd4:.2f}) | {stx} |")
        rep = hdr + [""] + rep
        open(os.path.join(HERE, "floor_report.md"), "w").write("\n".join(rep) + "\n")
        json.dump(allpts, open(os.path.join(HERE, "floor_points.json"), "w"), indent=1)
        print("\n".join(rep))
