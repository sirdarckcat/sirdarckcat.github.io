#!/usr/bin/env python3
"""The price recursion with the entropy of the small moduli taken into account.

    python3 cover_price_prefix.py counts x Q[:lng0] ...   ln g0(x, Q) by the recursion as it was and with the constraint (against measured)
    python3 cover_price_prefix.py ends x ...              where complete covers end, both ways
    python3 cover_price_prefix.py levels x Q              the entropy of every level, both ways

The recursion of cover_price_hl.py is an annealed count: at modulus s it lets the chosen class hold e^{v t} times the
mean number of rows still alive, t the price after s.  The classes of s are only s - 1 in number, so a class that full
exists only if the smaller moduli have arranged it, and that costs entropy: with mu = alive/(s-1) rows a class,

    entropy of the level  =  ln(s-1) - mu (t e^{v t} - (e^{v t} - 1)/v).

The sum over all levels is ln g0.  But the sum over the moduli up to s (a prefix) is the log of the number of ways the
moduli up to s can be set as the count assumes, and it cannot be negative.  In the recursion as it was it is, near the
end of complete covers and more so at larger sizes (89 moduli at the end: -8 nats; 302 moduli at 93% of the reach:
-119), because a modulus far below x has classes with many rows each and next to no entropy of its own.

With the constraints "every prefix entropy >= 0" the count is a constrained maximum; in the dual it reads

    ln g0  =  min over weights w_s >= 1, non-increasing in s, of   sum_s w_s ln(s-1) - pi(Q) p_start(w),
    p_s = p_{s+} - (w_s/(s-1)) kappa_s(p_{s+}/w_s),      kappa_s(t) = (e^{v_s t} - 1)/v_s,

w = 1 being the recursion as it was and a constant w the freezing of a random-energy model; w_s = 1 + sum_{j>=s} lam_j,
lam_j >= 0 the multiplier of the prefix ending at j, and the derivative of the bound in lam_j is that prefix's entropy,
so a convex minimisation with bounds does it (L-BFGS-B, the gradient exact).  Moduli with w > 1 are frozen: their
classes are the same in nearly all complete covers (the families seen in the runs).

Dispersions v_s: the Hardy-Littlewood pair sum of cover_price_hl.py, cut to [COVER_VMIN, 1], COVER_VMIN = 1e-4 unless
set in the environment.  The cut matters at the moduli 3 to 17 only, where the pair sum returns values at or below zero
while the class counts do differ a little (variance over mean 0.05 to 0.3 on random vectors).  cover_price_hl.py's own
loss uses 0.02.  The results move with it by about 1%: where complete covers end on the 89 moduli is 15,907 / 16,063 /
16,218 with the constraint for a cut of 1e-4 / 0.02 / 0.06 (known: 15,907 found, one row left at 15,950), and on 238
moduli 78,186 / 78,541 / 78,997.  The reason is that a frozen level takes the largest of a few counts, which the
weighted recursion (like any large-deviation estimate) puts too high, by 18% of a standard deviation for two classes and
60% for four; a small cut makes up for it.  1e-4 is used because it reproduces the one end that is known.
"""
import sys, os, math, ctypes, subprocess
import numpy as np
from scipy.optimize import minimize
import cover_price as cp, cover_price_hl as hl

HERE = os.path.dirname(os.path.abspath(__file__))
_so = os.path.join(HERE, "libcover_price_prefix.so")
if not os.path.exists(_so) or os.path.getmtime(_so) < os.path.getmtime(os.path.join(HERE, "cover_price_prefix.c")):
    subprocess.check_call(["gcc", "-O2", "-shared", "-fPIC", "-o", _so, os.path.join(HERE, "cover_price_prefix.c"), "-lm"])
_lib = ctypes.CDLL(_so); _lib.passes.restype = ctypes.c_double
_dp = np.ctypeslib.ndpointer(dtype=np.float64, flags="C"); _ip = np.ctypeslib.ndpointer(dtype=np.int32, flags="C")
_lib.passes.argtypes = [ctypes.c_int, _ip, _dp, ctypes.c_double, ctypes.c_double, _dp, _dp, _dp, ctypes.POINTER(ctypes.c_double)]
BETA = 40.0            # the price of a row left at the end: large, so that complete covers are counted
VMIN = float(os.environ.get("COVER_VMIN", "1e-4"))   # lower cut of the dispersion (it matters at the moduli 3 to 17 only)

def passes(mods, vs, piQ, w, beta=BETA):
    n = len(mods); taus = np.empty(n); ents = np.empty(n); a = ctypes.c_double()
    D = _lib.passes(n, mods, vs, float(piQ), float(beta), np.ascontiguousarray(w, dtype=np.float64), taus, ents, ctypes.byref(a))
    return D, ents, taus, a.value

def solve(mods, vs, piQ, lam0=None, beta=BETA, maxiter=4000):
    n = len(mods)
    def f(lam):
        D, ents, _, _ = passes(mods, vs, piQ, 1.0 + np.cumsum(lam[::-1])[::-1], beta)
        return D, np.cumsum(ents)
    r = minimize(f, np.zeros(n) if lam0 is None else lam0, jac=True, method="L-BFGS-B", bounds=[(0, None)] * n,
                 options={"maxiter": maxiter, "maxfun": 4 * maxiter, "ftol": 1e-14, "gtol": 1e-8})
    w = 1.0 + np.cumsum(r.x[::-1])[::-1]; D, ents, taus, k = passes(mods, vs, piQ, w, beta)
    return D, r.x, w, ents, taus

class Setup:
    def __init__(self, x, qmax):
        self.ps = hl.PairSums(x, int(qmax)); self.mods = np.array(self.ps.mods, dtype=np.int32)
        self.theta = float(sum(math.log(s) for s in self.ps.mods))
    def at(self, Q):
        vs, _ = self.ps.dispersions(Q); return np.clip(np.array(vs, dtype=np.float64), VMIN, 1.0), float(cp.odd_primes_below(Q))

def frozen_up_to(mods, w): return max([int(m) for m, ww in zip(mods, w) if ww > 1.001], default=0)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "counts":
        x = int(sys.argv[2]); tg = [(int(a.split(":")[0]), float(a.split(":")[1]) if ":" in a else None) for a in sys.argv[3:]]
        st = Setup(x, max(q for q, _ in tg)); n = len(st.mods)
        print(f"x = {x}, {n} moduli, theta = {st.theta:.1f}\nQ | loss, recursion as it was | lowest prefix entropy there, at modulus | loss with the constraint | moduli frozen up to | weight at 3 | loss measured | measured / as it was | measured / constrained")
        for Q, g in tg:
            vs, piQ = st.at(Q); D0, e0, _, _ = passes(st.mods, vs, piQ, np.ones(n)); P0 = np.cumsum(e0)[:-1]
            D, lam, w, ents, _ = solve(st.mods, vs, piQ)
            print(f"{Q} | {st.theta - D0:.1f} | {P0.min():.1f}, {int(st.mods[int(P0.argmin())])} | {st.theta - D:.1f} | {frozen_up_to(st.mods, w)} | {w[0]:.3f}"
                  + (f" | {st.theta - g:.1f} | {(st.theta - g) / (st.theta - D0):.3f} | {(st.theta - g) / (st.theta - D):.3f}" if g is not None else ""), flush=True)
    elif mode == "ends":
        print("x | moduli | end, recursion as it was | / (x ln^2 x) | end with the constraint | / (x ln^2 x) | moduli frozen up to (at the end), weight at 3", flush=True)
        for x in [int(a) for a in sys.argv[2:]]:
            sc = x * math.log(x) ** 2; st = Setup(x, 1.3 * sc + 1000); n = len(st.mods)
            lo, hi = 0.6 * sc, 1.3 * sc
            for _ in range(15):
                mid = math.sqrt(lo * hi); vs, piQ = st.at(int(mid))
                if passes(st.mods, vs, piQ, np.ones(n))[0] > 0: lo = mid
                else: hi = mid
            e0 = lo; lo, hi = 0.6 * sc, e0 * 1.001; lam = None; info = (0, 1.0)
            for _ in range(15):
                mid = math.sqrt(lo * hi); vs, piQ = st.at(int(mid)); D, lam, w, _, _ = solve(st.mods, vs, piQ, lam)
                if D > 0: lo = mid; info = (frozen_up_to(st.mods, w), float(w[0]))
                else: hi = mid
            print(f"{x} | {n} | {e0:,.0f} | {e0 / sc:.3f} | {lo:,.0f} | {lo / sc:.3f} | {info[0]}, {info[1]:.2f}", flush=True)
    elif mode == "levels":
        x, Q = int(sys.argv[2]), int(sys.argv[3]); st = Setup(x, Q); n = len(st.mods); vs, piQ = st.at(Q)
        D0, e0, t0, _ = passes(st.mods, vs, piQ, np.ones(n)); D, lam, w, e1, t1 = solve(st.mods, vs, piQ)
        print(f"x = {x}, Q = {Q}: ln g0 {D0:.1f} as it was, {D:.1f} with the constraint\nmodulus | dispersion | as it was: tilt e^(v t), entropy of the level, of the prefix | with the constraint: weight, tilt, level, prefix")
        P0 = np.cumsum(e0); P1 = np.cumsum(e1); step = max(1, n // 40)
        for i in list(range(0, n, step)) + [n - 1]:
            print(f"{int(st.mods[i])} | {vs[i]:.3f} | {math.exp(vs[i] * t0[i]):.2f}, {e0[i]:.2f}, {P0[i]:.1f} | {w[i]:.3f}, {math.exp(vs[i] * t1[i]):.2f}, {e1[i]:.2f}, {P1[i]:.1f}")
