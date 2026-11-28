# T1: the ball-and-box mechanism behind "why 1.349 is not the truth" (goldbach/sublinear/README.md on ccr-d4a17dd0-7uu03r).
# Small primes A = odd primes <= w take one nonzero class each, uniformly and independently; S = odd primes <= y = C x ln x
# in none of these classes. Report A measures how S sits in the classes of the large primes B = primes in (w, x];
# report B lets the primes of B take, one by one, the class with the most remaining survivors.
#   python3 t1.py x [draws] [threads]      -> t1_x<x>.json and a text summary on stdout
import sys, math, json, time, ctypes
from multiprocessing import Pool
import numpy as np

HERE = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
import os
CGRID = [float(v) for v in os.environ.get("T1_CGRID", "1.0,1.35,2.0,3.0,4.0,6.0,8.0").split(",")]
THETAS = [0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0]
CBIS_MAX = float(os.environ.get("T1_CBIS_MAX", "24"))   # largest C tried by the per-draw bisection of report B
BIS_STEPS = int(os.environ.get("T1_BIS_STEPS", "14"))
SKIP_EXACT = os.environ.get("T1_SKIP_EXACT") == "1"   # skip the sampled exact expectation and N3 (for x = 10^6)
ORDERS = os.environ.get("T1_ORDERS", "increasing,decreasing,random").split(",")
NPAIRS = 200             # random pairs (r1, r2) for the conflict count
MEXACT = 48              # sampled target pairs per r for the exact expectation of E_r

U32P, F64P, I32P, I64P = (np.ctypeslib.ndpointer(t, flags="C_CONTIGUOUS") for t in (np.uint32, np.float64, np.int32, np.int64))
def lib():
    L = ctypes.CDLL(HERE + "/t1lib.so")
    L.occupancy.argtypes = [U32P, ctypes.c_int64, U32P, ctypes.c_int64, F64P, I32P, I32P, I32P, ctypes.c_int]
    L.conflicts.argtypes = [U32P, ctypes.c_int64, U32P, U32P, ctypes.c_int64, F64P, ctypes.c_int]
    L.exact_pairs.argtypes = [U32P, ctypes.c_int64, U32P, ctypes.c_int64, U32P, ctypes.c_int64, ctypes.c_int, ctypes.c_uint64, F64P, F64P, ctypes.c_int]
    L.deletion.argtypes = [U32P, ctypes.c_int64, U32P, ctypes.c_int64, F64P, F64P, ctypes.c_int, ctypes.c_uint64, I64P, I64P, I64P, ctypes.c_int]
    L.greedy.argtypes = [U32P, ctypes.c_int64, U32P, ctypes.c_int64, I32P]; L.greedy.restype = ctypes.c_int64
    return L
LIB = None
def L_():
    global LIB
    if LIB is None: LIB = lib()
    return LIB

def primes_upto(n):
    s = np.ones(n // 2 + 1, dtype=bool); s[0] = False                     # index i <-> 2i + 1
    for i in range(1, (math.isqrt(n) - 1) // 2 + 1):
        if s[i]: s[(2 * i + 1) ** 2 // 2::2 * i + 1] = False
    p = 2 * np.nonzero(s)[0] + 1
    return p[p <= n].astype(np.uint32)                                    # odd primes only

def occupancy(S, B, threads):
    n = len(B); E = np.zeros(n); c2 = np.zeros(n, np.int32); c3 = np.zeros(n, np.int32); c4 = np.zeros(n, np.int32)
    L_().occupancy(S, len(S), B, n, E, c2, c3, c4, threads)
    return E, c2, c3, c4

def greedy_job(args):
    S, Border = args
    st = np.zeros(len(Border), np.int32)
    left = L_().greedy(S, len(S), Border, len(Border), st)
    return int(left), st

def survivors(T_all, A, a, ymax):
    mark = np.zeros(int(ymax) + 1, dtype=bool)
    for r, ar in zip(A.tolist(), a.tolist()):
        mark[ar::r] = True
    return T_all[~mark[T_all]]

def poisson_tail(lam, k):                                                 # P(Poisson(lam) >= k), vectorised
    p = np.exp(-lam); s = p.copy()
    for j in range(1, k):
        p = p * lam / j; s += p
    return 1 - s

def run(x, draws, threads):
    t0 = time.time(); lnx = math.log(x)
    ymax = int(CBIS_MAX * x * lnx) + 2
    T_all = primes_upto(ymax)
    out = {"x": x, "draws": draws, "settings": dict(CBIS_MAX=CBIS_MAX, BIS_STEPS=BIS_STEPS, SKIP_EXACT=SKIP_EXACT, ORDERS=ORDERS, NPAIRS=NPAIRS, MEXACT=MEXACT), "Cgrid": CGRID, "thetas": THETAS, "ln_x_over_lnln_x": lnx / math.log(lnx), "w": {}}
    pool = Pool(threads)
    for wtag, w in (("x/2", x // 2), ("x^0.9", int(round(x ** 0.9)))):
        A = T_all[T_all <= w]; B = T_all[(T_all > w) & (T_all <= x)]
        prodA1 = float(np.prod(1 - 1 / (A.astype(float) - 1)))
        prodA2_5 = float(np.prod(1 - 2 / (A[A >= 5].astype(float) - 1)))
        rng0 = np.random.default_rng([x, 1 if wtag == "x/2" else 2, 2026])
        Smax = []
        for d in range(draws):
            rng = np.random.default_rng([x, 1 if wtag == "x/2" else 2, d])
            a = (rng.integers(0, A.astype(np.int64) - 1) + 1).astype(np.int64)      # uniform in 1 .. r-1
            Smax.append(survivors(T_all, A, a, ymax))
        prs = np.array(sorted({tuple(sorted(rng0.choice(len(B), 2, replace=False))) for _ in range(3 * NPAIRS)})[:NPAIRS])
        R1 = np.ascontiguousarray(B[prs[:, 0]]); R2 = np.ascontiguousarray(B[prs[:, 1]])
        W = {"w": w, "nA": int(len(A)), "nB": int(len(B)), "prod_A_1": prodA1, "prod_A5_2": prodA2_5, "A": {}, "B": {}}
        # ---------------- report A
        for C in CGRID:
            y = C * x * lnx
            T = T_all[T_all <= y]
            Nr, _, _, _ = occupancy(T, B, threads)
            Nx = np.zeros(len(B)); Pb = np.zeros(len(B)); N3 = np.full(len(B), np.nan)
            if not SKIP_EXACT:
                B3 = (3 * B).astype(np.uint32)
                N3, _, _, _ = occupancy(T, B3, threads)                 # pairs in a common class of r and of 3
                L_().exact_pairs(T, len(T), B, len(B), A, len(A), MEXACT, 12345 + int(10 * C), Nx, Pb, threads)
            Es, C2, C3, C4, nS, Xs = [], [], [], [], [], []
            for d in range(draws):
                S = Smax[d][Smax[d] <= y]
                E, c2, c3, c4 = occupancy(S, B, threads)
                X = np.zeros(len(prs)); L_().conflicts(S, len(S), R1, R2, len(prs), X, threads)
                Es.append(E); C2.append(c2); C3.append(c3); C4.append(c4); nS.append(len(S)); Xs.append(X)
            Es = np.array(Es); nS = np.array(nS, float); Xs = np.array(Xs)
            mE = Es.mean(0); m2 = (Es ** 2).mean(0)
            iB = {int(r): i for i, r in enumerate(B.tolist())}
            Xr = Xs.mean(0) / (mE[[iB[int(r)] for r in R1]] * mE[[iB[int(r)] for r in R2]]) * nS.mean()
            good = np.zeros((draws, len(THETAS))); one = np.zeros_like(good); mk = np.zeros_like(good)
            for d in range(draws):
                S = Smax[d][Smax[d] <= y]
                g = np.zeros(len(THETAS), np.int64); o = np.zeros_like(g); m = np.zeros_like(g)
                L_().deletion(S, len(S), B, len(B), np.ascontiguousarray(mE), np.array(THETAS), len(THETAS), 777 + d, g, o, m, threads)
                good[d] = g; one[d] = o; mk[d] = m
            lam = nS.mean() / (B.astype(float) - 1)
            pois = {k: float(((B.astype(float) - 1) * poisson_tail(lam, k)).sum()) for k in (2, 3, 4)}
            fg = good.mean(0) / len(B)
            W["A"][str(C)] = dict(
                nT=int(len(T)), S_mean=float(nS.mean()), S_sd=float(nS.std()), S_pred=float(len(T) * prodA1),
                E_mean=float(mE.sum()), E_naive_as_written=0.0, N=float(Nr.sum()), N_convexity=float(((B - 1.0) * (len(T) / (B - 1.0)) * (len(T) / (B - 1.0) - 1) / 2).sum()),
                N3=float(N3.sum()), E_naive_r3_exact=float(0.5 * N3.sum() * prodA2_5), E_exact=float((Nx * Pb).sum()),
                E_balls=float((nS.mean() * (nS.mean() - 1) / 2 / (B - 1.0)).sum()),
                c2=float(np.mean([c.sum() for c in C2])), c3=float(np.mean([c.sum() for c in C3])), c4=float(np.mean([c.sum() for c in C4])),
                c2_pois=pois[2], c3_pois=pois[3], c4_pois=pois[4],
                second_moment_mean=float(np.mean(m2 / mE ** 2)), second_moment_q=[float(v) for v in np.quantile(m2 / mE ** 2, [0.1, 0.5, 0.9])],
                conflict_ratio_mean=float(Xr.mean()), conflict_ratio_q=[float(v) for v in np.quantile(Xr, [0.1, 0.5, 0.9])],
                good_frac=[float(v) for v in fg], good_max=float(fg.max()), good_argmax_theta=THETAS[int(fg.argmax())],
                one_frac=[float(v) for v in one.mean(0) / len(B)], marked_per_prime=[float(v) for v in mk.mean(0) / len(B)])
            print(f"x={x} w={wtag} C={C}: |S| {nS.mean():.0f} (pred {len(T)*prodA1:.0f}); E {mE.sum():.4g} exact {(Nx*Pb).sum():.4g} balls {W['A'][str(C)]['E_balls']:.4g}; "
                  f"2nd {W['A'][str(C)]['second_moment_mean']:.3f}; confl {Xr.mean():.3f}; good max {fg.max():.4f} at {THETAS[int(fg.argmax())]}  [{time.time()-t0:.0f}s]", flush=True)
        # ---------------- report B
        orders = {"increasing": B, "decreasing": B[::-1].copy(), "random": B[np.random.default_rng([x, 99]).permutation(len(B))].copy()}
        orders = {k: v for k, v in orders.items() if k in ORDERS}
        for oname, Bo in orders.items():
            Bo = np.ascontiguousarray(Bo)
            res = {}
            jobs = [(np.ascontiguousarray(Smax[d][Smax[d] <= C * x * lnx]), Bo) for C in CGRID for d in range(draws)]
            outs = pool.map(greedy_job, jobs)
            k = 0
            for C in CGRID:
                lefts, hist = [], np.zeros(12)
                for d in range(draws):
                    left, st = outs[k]; k += 1
                    lefts.append(left); hist += np.bincount(np.minimum(st, 11), minlength=12)
                res[str(C)] = dict(left_mean=float(np.mean(lefts)), nothing_left_frac=float(np.mean(np.array(lefts) == 0)), hist=[float(v) for v in hist / draws])
            # per-draw threshold by bisection (assumes 'nothing left' is monotone in C, which is checked on the grid above)
            lo = np.full(draws, 0.5); hi = np.full(draws, CBIS_MAX)
            ok_hi = pool.map(greedy_job, [(np.ascontiguousarray(Smax[d][Smax[d] <= CBIS_MAX * x * lnx]), Bo) for d in range(draws)])
            capped = np.array([o[0] == 0 for o in ok_hi])
            for it in range(BIS_STEPS):
                mid = (lo + hi) / 2
                outs2 = pool.map(greedy_job, [(np.ascontiguousarray(Smax[d][Smax[d] <= mid[d] * x * lnx]), Bo) for d in range(draws)])
                okm = np.array([o[0] == 0 for o in outs2])
                lo = np.where(okm, mid, lo); hi = np.where(okm, hi, mid)
            thr = np.where(capped, CBIS_MAX, lo)
            res["threshold_per_draw"] = [float(v) for v in thr]
            res["C_star"] = float(np.median(thr)); res["capped"] = int(capped.sum())
            W["B"][oname] = res
            print(f"x={x} w={wtag} order={oname}: C* = {np.median(thr):.3f} (per-draw {np.min(thr):.2f}..{np.max(thr):.2f}); "
                  f"nothing-left fraction on the grid {[res[str(C)]['nothing_left_frac'] for C in CGRID]}  [{time.time()-t0:.0f}s]", flush=True)
        out["w"][wtag] = W
    pool.close()
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(f"{HERE}/t1_x{x}.json", "w"))
    return out

if __name__ == "__main__":
    x = int(float(sys.argv[1])); draws = int(sys.argv[2]) if len(sys.argv) > 2 else 20; threads = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    run(x, draws, threads)
