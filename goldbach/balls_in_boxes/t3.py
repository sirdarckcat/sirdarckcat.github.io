# T3: where the all-greedy reach comes from (follow-up to T1, from the research session).
#   T3a  C*(x, theta): random nonzero classes for the odd primes up to w = x^theta, the fullest class of the remaining targets for
#        every prime above w in increasing order (theta = 0 is the all-greedy rule of greedy_cover.py).
#   T3b  profile of one all-greedy run (x = 10^4, 10^5, 10^6) with y = 0.72 x ln^2 x: per prime r the targets left T_r, lambda = T_r/(r-1),
#        the size m of the class it takes and m_max = E[fullest of r-1 independent Poisson(lambda) cells], in 40 logarithmic bins.
#   T3c  the same profile for the tempered 167-modulus cover (complete_cover_40111_167primes.txt), moduli in increasing order,
#        against the greedy vector on the same moduli.
#   python3 t3.py a [procs] | e [procs] [thetas] | b [x] | c | s   (e: x = 10^6 extension of a, thetas comma-separated)   (s: summary of the t3b_x*.json runs across x)
import sys, math, json, re, time
from multiprocessing import Pool
import numpy as np
from scipy.stats import poisson
import t1

def threshold_job(args):
    """per-draw bisection: largest C with nothing left (assumes monotone in C, checked on the bracket ends)"""
    x, theta, d, cmax, steps = args[:5]; cmin = args[5] if len(args) > 5 else 0.25   # bracket [cmin, cmax]
    lnx = math.log(x); w = x ** theta if theta > 0 else 1
    P = t1.primes_upto(int(cmax * x * lnx) + 2)
    A = P[P <= w]; B = np.ascontiguousarray(P[(P > w) & (P <= x)])
    rng = np.random.default_rng([x, int(round(100 * theta)), d])
    a = (rng.integers(0, A.astype(np.int64) - 1) + 1) if len(A) else np.zeros(0, np.int64)
    Smax = t1.survivors(P, A, a, int(cmax * x * lnx) + 1) if len(A) else P
    left = lambda C: t1.greedy_job((np.ascontiguousarray(Smax[Smax <= C * x * lnx]), B))[0]
    lo, hi = cmin, cmax
    if left(hi) == 0: return cmax, True                       # reached the top of the bracket
    if left(lo) > 0: return (0.0 if cmin == 0.25 else -cmin), False   # below the bracket (negative: below cmin)
    for _ in range(steps):
        mid = (lo + hi) / 2
        if left(mid) == 0: lo = mid
        else: hi = mid
    return lo, False

def part_a(procs):
    out = {}
    jobs = []
    for x in (10000, 100000):
        for th in (0.0, 0.2, 0.4, 0.6, 0.8, 0.9):
            for d in range(1 if th == 0 else 10):
                jobs.append((x, th, d, 12.0, 14))
    with Pool(procs) as pool:
        res = pool.map(threshold_job, jobs)
    for (x, th, d, _, _), (c, capped) in zip(jobs, res):
        out.setdefault(str(x), {}).setdefault(str(th), []).append(c)
    json.dump(out, open("t3a.json", "w"))
    G = {10000: 6.53, 100000: 8.38}
    for x in (10000, 100000):
        print(f"x = {x}: all-greedy G(x)/(x ln x) from greedy_cover.txt = {G[x]}")
        for th in (0.0, 0.2, 0.4, 0.6, 0.8, 0.9):
            v = np.array(out[str(x)][str(th)]); w = x ** th if th > 0 else 1
            print(f"  theta = {th}: w = {w:,.0f}; C* = {np.median(v):.3f} (draws {v.min():.2f} .. {v.max():.2f}); C*/ln x = reach/(x ln^2 x) = {np.median(v)/math.log(x):.3f}")

BRACKET_1E6 = {0.0: (9.9, 11.0), 0.6: (8.0, 10.5), 0.8: (5.0, 9.0), 0.9: (3.0, 6.0)}   # around the values the rule predicts

def part_e(procs, thetas=(0.0, 0.6, 0.8)):
    """x = 10^6, fewer draws and a known bracket: theta = 0 (one run), the others 2 draws each, 8 bisection steps; merged into t3a_x1000000.json"""
    x = 1000000
    jobs = [(x, th, d, BRACKET_1E6[th][1], 8, BRACKET_1E6[th][0]) for th in thetas for d in range(1 if th == 0 else 2)]
    with Pool(procs) as pool:
        res = pool.map(threshold_job, jobs)
    try: out = json.load(open("t3a_x1000000.json"))
    except FileNotFoundError: out = {}
    for th in thetas: out[str(th)] = []
    for j, (c, capped) in zip(jobs, res):
        out[str(j[1])].append(dict(C=c, capped=capped, bracket=[j[5], j[3]], steps=j[4]))
        print(f"x = {x:,} theta = {j[1]} draw {j[2]}: C* = {c:.3f}{' (top of bracket)' if capped else ''}{' (below the bracket)' if c < 0 else ''}", flush=True)
    json.dump(out, open("t3a_x1000000.json", "w"))

def emax_poisson(lam, n):
    """E[max of n iid Poisson(lam)] = sum_k P(max > k) = sum_k (1 - F(k)^n)"""
    if lam <= 0: return 0.0
    k0 = max(0, int(lam - 12 * math.sqrt(lam) - 20)); k1 = int(lam + 12 * math.sqrt(lam) + 60)
    k = np.arange(k0, k1)
    sf = poisson.sf(k, lam)                                    # P(X > k)
    tail = -np.expm1(n * np.log1p(-np.minimum(sf, 1 - 1e-16)))  # 1 - F(k)^n
    return float(k0 + tail.sum())

def profile(moduli, struck, nT, nbins, lo, hi):
    """per-modulus T_r, lambda, m, m_max; binned logarithmically in r.  Ratios are over the primes that still had targets
    (T_r > 0); 'idle' counts the primes that came after every target was struck.  The excess m - lambda is what a prime
    strikes beyond the lambda that a random nonzero class would strike on average."""
    T_before = nT - np.concatenate([[0], np.cumsum(struck)[:-1]])
    lam = T_before / (moduli - 1.0)
    mmax = np.array([emax_poisson(l, int(r) - 1) for l, r in zip(lam, moduli)])
    edges = np.geomspace(lo, hi + 1, nbins + 1)
    rows = []
    tot = struck.sum(); exc_tot = float((struck - lam).sum())
    for b in range(nbins):
        sel = (moduli >= edges[b]) & (moduli < edges[b + 1])
        if not sel.any(): continue
        act = sel & (T_before > 0)
        m, l, mx = struck[act], lam[act], mmax[act]
        rows.append(dict(r_lo=int(moduli[sel].min()), r_hi=int(moduli[sel].max()), primes=int(sel.sum()), idle=int((sel & (T_before <= 0)).sum()),
                         lam=float(l.mean()) if act.any() else 0.0, m=float(struck[sel].mean()),
                         m_over_lam=float((m / l).mean()) if act.any() else float("nan"), m_over_mmax=float((m / mx).mean()) if act.any() else float("nan"),
                         excess_sd=float(((m - l) / np.sqrt(l)).mean()) if act.any() else float("nan"),
                         share=float(struck[sel].sum() / tot), excess_share=float((struck[sel] - lam[sel]).sum() / exc_tot)))
    return rows, dict(T_before=T_before.tolist(), lam=lam.tolist(), mmax=mmax.tolist(), excess_total=exc_tot)

def print_profile(rows, title):
    print(f"\n{title}\n| primes r | count (idle) | mean lambda | mean m | m / lambda | m / m_max(indep) | (m - lambda)/sqrt(lambda) | share of strikes | cumulative | share of excess m - lambda | cumulative |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    cum = cx = 0
    for r in rows:
        cum += r["share"]; cx += r["excess_share"]
        idle = f" ({r['idle']} idle)" if r["idle"] else ""
        print(f"| {r['r_lo']:,}–{r['r_hi']:,} | {r['primes']}{idle} | {r['lam']:.4g} | {r['m']:.4g} | {r['m_over_lam']:.3f} | {r['m_over_mmax']:.3f} | {r['excess_sd']:.2f} | {r['share']:.4f} | {cum:.3f} | {r['excess_share']:.4f} | {cx:.3f} |")

U_EDGES = (0.0, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0001)

def part_b(x=100000):
    """one all-greedy run with targets the odd primes below y = 0.72 x ln^2 x; per-prime profile, 40 logarithmic bins in r,
    and a coarser summary in u = ln r / ln x that can be compared across x"""
    y = int(0.72 * x * math.log(x) ** 2)
    P = t1.primes_upto(y); T = P[P < y]; M = np.ascontiguousarray(P[P <= x])
    left, st = t1.greedy_job((np.ascontiguousarray(T), M))
    Mf, sf = M.astype(float), st.astype(float)
    rows, raw = profile(Mf, sf, len(T), 40, 3, x)
    Tb, lam, mmax = (np.array(raw[k]) for k in ("T_before", "lam", "mmax"))
    act = Tb > 0
    # excess against independent cells, and the Montgomery-Hooley guess sqrt(ln r / ln y) for it (see the reading)
    exr = np.where(act & (mmax > lam), (sf - lam) / np.where(mmax > lam, mmax - lam, 1), np.nan)
    for r in rows:
        sel = (Mf >= r["r_lo"]) & (Mf <= r["r_hi"]) & act
        r["excess_ratio"] = float(np.nanmean(exr[sel])) if sel.any() else float("nan")
        r["hooley"] = float(np.mean(np.sqrt(np.log(Mf[sel]) / math.log(y)))) if sel.any() else float("nan")
    # random nonzero classes at every prime: E[T_r] = T * prod_{p < r} (1 - 1/(p - 1))
    Trand = len(T) * np.concatenate([[1.0], np.cumprod(1 - 1 / (Mf - 1))[:-1]])
    u = np.log(Mf) / math.log(x); exc = sf - lam; Etot = float(exc.sum())
    ub = []
    for lo, hi in zip(U_EDGES[:-1], U_EDGES[1:]):
        sel = (u >= lo) & (u < hi)
        if not sel.any(): continue
        i0 = int(np.argmax(sel))
        ub.append(dict(u_lo=lo, u_hi=min(hi, 1.0), primes=int(sel.sum()), strikes=float(sf[sel].sum() / sf.sum()),
                       excess=float(exc[sel].sum() / Etot), excess_per_prime=float(exc[sel].mean()),
                       left_before=float(Tb[i0] / len(T)), left_before_random=float(Trand[i0] / len(T)), gain=float(Tb[i0] / Trand[i0])))
    below = {str(th): float(exc[Mf <= x ** th].sum() / Etot) for th in (0.2, 0.4, 0.6, 0.8, 0.9)}
    out = dict(x=x, y=y, targets=int(len(T)), left=int(left), excess_total=Etot, excess_share_below=below, random_left_after_all=float(Trand[-1] * (1 - 1 / (Mf[-1] - 1))),
               primes=int(len(M)), rows=rows, ubins=ub)
    json.dump(out, open(f"t3b_x{x}.json", "w"))
    print(f"T3b: all-greedy, x = {x:,}, y = 0.72 x ln^2 x = {y:,}: {len(T):,} targets, {left} left after all {len(M):,} primes")
    print(f"total strikes {int(st.sum()):,} = sum over the run of lambda (the mean class size at each step) {st.sum() - Etot:,.0f} + the excess sum(m - lambda) "
          f"{Etot:,.0f} ({Etot / st.sum():.1%} of the targets; {Etot / len(M):.2f} per prime = {Etot / len(M) / math.log(x):.3f} ln x). "
          f"Random nonzero classes at every prime would leave {out['random_left_after_all']:,.0f} ({out['random_left_after_all'] / len(T):.1%}).")
    print_profile(rows, "Profile (40 logarithmic bins in r)")
    print("\n| primes r | excess ratio (m - lambda)/(m_max - lambda) | sqrt(ln r / ln y) |")
    print("|---|---|---|")
    for r in rows: print(f"| {r['r_lo']:,}–{r['r_hi']:,} | {r['excess_ratio']:.3f} | {r['hooley']:.3f} |")
    print_ubins(out)

def print_ubins(d):
    x = d["x"]
    print(f"\nBy u = ln r / ln x (x = {x:,}): share of strikes and of the excess, and the targets left when the bin starts (greedy, and random classes at every prime)")
    print("| u | primes | share of strikes | share of excess | excess per prime | excess per prime / ln x | left before (greedy) | left before (random) | greedy / random |")
    print("|---|---|---|---|---|---|---|---|---|")
    for b in d["ubins"]:
        print(f"| {b['u_lo']:.1f}–{b['u_hi']:.1f} | {b['primes']:,} | {b['strikes']:.3f} | {b['excess']:.3f} | {b['excess_per_prime']:.2f} | {b['excess_per_prime'] / math.log(x):.3f} | "
              f"{b['left_before']:.4f} | {b['left_before_random']:.4f} | {b['gain']:.3f} |")

def part_s():
    import glob
    ds = sorted((json.load(open(f)) for f in glob.glob("t3b_x*.json")), key=lambda d: d["x"])
    print("| x | y | targets | left | excess / targets | random would leave | excess per prime / ln x |")
    print("|---|---|---|---|---|---|---|")
    for d in ds:
        print(f"| {d['x']:,} | {d['y']:,} | {d['targets']:,} | {d['left']} | {d['excess_total'] / d['targets']:.3f} | {d['random_left_after_all'] / d['targets']:.3f} | "
              f"{d['excess_total'] / d['primes'] / math.log(d['x']):.3f} |")
    for d in ds: print_ubins(d)

def part_c():
    txt = open("../tempering_covers/complete_cover_40111_167primes.txt").read()
    pairs = sorted((int(a), int(b)) for a, b in re.findall(r"(\d+):(\d+)", txt))
    M = np.array([r for r, _ in pairs], dtype=np.uint32); cls = np.array([a for _, a in pairs], dtype=np.int64)
    out = {}
    for y in (40111, 32971):
        P = t1.primes_upto(y); T = P[P < y].astype(np.int64)
        # tempered vector, moduli in increasing order
        rem = T.copy(); st_t = []; full_t = []                # full_t: the fullest nonzero class of what is left, on the tempered path
        for r, a in zip(M.tolist(), cls.tolist()):
            c = np.bincount(rem % r, minlength=r); c[0] = 0; full_t.append(int(c.max()))
            hit = rem % r == a; st_t.append(int(hit.sum())); rem = rem[~hit]
        left_g, st_g = t1.greedy_job((np.ascontiguousarray(T.astype(np.uint32)), M))
        rows_t, _ = profile(M.astype(float), np.array(st_t, float), len(T), 12, 3, 997)
        rows_g, _ = profile(M.astype(float), st_g.astype(float), len(T), 12, 3, 997)
        st_a, fu_a = np.array(st_t, float), np.array(full_t, float)
        for row in rows_t:
            sel = (M >= row["r_lo"]) & (M <= row["r_hi"])
            row["taken_over_fullest"] = float((st_a[sel] / np.maximum(fu_a[sel], 1)).mean()); row["fullest_taken"] = float((st_a[sel] == fu_a[sel]).mean())
        out[str(y)] = dict(targets=int(len(T)), left_tempered=int(len(rem)), left_greedy=int(left_g), tempered=rows_t, greedy=rows_g,
                           per_modulus=[(int(r), int(a), int(b), int(f)) for r, a, b, f in zip(M.tolist(), st_t, st_g.tolist(), full_t)])
        print(f"\nT3c: targets = odd primes below {y:,} ({len(T):,}); left by the tempered vector {len(rem)}, by greedy {left_g}")
        print_profile(rows_t, f"Tempered 40,111 vector, moduli in increasing order (targets below {y:,})")
        print_profile(rows_g, f"Greedy on the same 167 moduli (targets below {y:,})")
        print(f"\nTempered path (targets below {y:,}): the class it takes against the fullest nonzero class of the targets still left")
        print("| primes r | count | taken / fullest | fullest taken |"); print("|---|---|---|---|")
        for row in rows_t: print(f"| {row['r_lo']:,}–{row['r_hi']:,} | {row['primes']} | {row['taken_over_fullest']:.3f} | {row['fullest_taken']:.0%} |")
        print(f"all 167: taken / fullest {float((st_a / np.maximum(fu_a, 1)).mean()):.3f}, fullest taken {float((st_a == fu_a).mean()):.0%}; "
              f"total taken {int(st_a.sum()):,} against {int(fu_a.sum()):,} for the fullest at every step")
    json.dump(out, open("t3c.json", "w"))

if __name__ == "__main__":
    part = sys.argv[1]; procs = int(sys.argv[2]) if len(sys.argv) > 2 and part in "ae" else 2
    t0 = time.time()
    {"a": lambda: part_a(procs), "e": lambda: part_e(procs, tuple(float(t) for t in sys.argv[3].split(",")) if len(sys.argv) > 3 else (0.0, 0.6, 0.8)), "b": lambda: part_b(int(sys.argv[2]) if len(sys.argv) > 2 else 100000), "c": part_c, "s": part_s}[part]()
    print(f"[{time.time() - t0:.0f} s]")
