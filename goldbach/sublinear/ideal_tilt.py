#!/usr/bin/env python3
"""What would a perfect search be worth?  From the histograms of ideal_tilt.c to the cost of an ideal search.

    python3 ideal_tilt.py out.txt [B=1e8] [digits=200] [budget_nats=30.75] [beta_max]

ideal_tilt.c samples residue vectors (a class of N for every odd prime s <= z) at many temperatures; the energy k is
the number of rows q < Q for which N - q has no prime factor <= z.  Here:

1. ln g(k), the number of residue vectors with k rows left, by multi-histogram reweighting (WHAM), normalised so that
   the total is the number of states.  The number of even N below 10^digits with k rows left is
   n(k) = g(k) * (10^digits / 2) / prod s.
2. Ideal search to depth z: test the N in increasing order of k.  A member with k rows left succeeds with probability
   (1 - p_z)^k, p_z = 2 prod_{s<=z} s/(s-1) / ln N.  The cost is the number X of N tested when the expected number
   of successes reaches 1; printed as x = ln X.
3. Ideal search to depth B > z: beyond z every row left survives the primes in (z, B] independently with probability
   sigma = prod_{z<s<=B} (1 - 1/s) (independent rows: exact in the limit of large z), so the rows left at depth B are
   binomial; test the N in increasing order of the rows left at depth B.

beta_max: use only the replicas with beta <= beta_max (the coldest ones may not be in equilibrium).
"""
import math, sys
import numpy as np

def logsumexp(a, axis=None):
    m = np.max(a, axis=axis, keepdims=True); m = np.where(np.isfinite(m), m, 0.0)
    r = m + np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True))
    return r.reshape(()) if axis is None else np.squeeze(r, axis=axis)

def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

def read(path, beta_max=None):
    head = open(path).readline().split(); par = dict(t.split("=") for t in head[1:])
    betas, hists, info = [], [], []
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        if line.startswith("BETA"):
            t = line.split(); b = float(t[1])
            if beta_max is not None and b > beta_max + 1e-12: continue
            h = {int(u.split(":")[0]): int(u.split(":")[1]) for u in lines[i + 1].split()[1:]}
            betas.append(b); hists.append(h); info.append(dict(mean=float(t[5]), sd=float(t[7]), min=int(t[9]), swap=float(t[11]), acc=[float(v) for v in t[13:]]))
    return par, np.array(betas), hists, info

def wham(betas, hists, lnstates, iters=20000, tol=1e-10):
    lo = min(min(h) for h in hists); hi = max(max(h) for h in hists); E = np.arange(lo, hi + 1, dtype=float)
    H = np.zeros((len(betas), len(E)))
    for i, h in enumerate(hists):
        for e, c in h.items(): H[i, e - lo] = c
    Nn = H.sum(axis=1); tot = H.sum(axis=0); ok = tot > 0
    with np.errstate(divide="ignore"): lnH = np.log(H); lntot = np.log(tot)
    # start: free-energy perturbation between neighbours (mean of the two directions)
    lnZ = np.zeros(len(betas))
    for i in range(len(betas) - 1):
        db = betas[i + 1] - betas[i]
        fwd = logsumexp(lnH[i] - db * E) - math.log(Nn[i]); bwd = -(logsumexp(lnH[i + 1] + db * E) - math.log(Nn[i + 1]))
        lnZ[i + 1] = lnZ[i] + 0.5 * (fwd + bwd)
    for it in range(iters):
        den = logsumexp(np.log(Nn)[:, None] - lnZ[:, None] - betas[:, None] * E[None, :], axis=0)
        lng = np.where(ok, lntot - den, -np.inf)
        new = logsumexp(lng[None, :] - betas[:, None] * E[None, :], axis=1); new -= new[0]
        d = np.max(np.abs(new - lnZ)); lnZ = new
        if d < tol: break
    lng = lng - logsumexp(lng) + lnstates              # beta = 0 is in the ladder: the total is the number of states
    return E.astype(int), lng, lnZ, it + 1, tot

def lgamma_arr(x):
    return np.array([math.lgamma(v) for v in np.ravel(x)]).reshape(np.shape(x))

if __name__ == "__main__":
    path = sys.argv[1]; B = float(sys.argv[2]) if len(sys.argv) > 2 else 1e8
    digits = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 30.75
    beta_max = float(sys.argv[5]) if len(sys.argv) > 5 else None
    par, betas, hists, info = read(path, beta_max)
    Q, z, lnstates = int(par["Q"]), int(par["z"]), float(par["ln(states)"])
    E, lng, lnZ, its, tot = wham(betas, hists, lnstates)
    odd = primes_upto(z)[1:].astype(float)
    lnP = float(np.sum(np.log(odd))); lnN = digits * math.log(10); lnX2 = lnN - math.log(2)
    boost_z = 2 * float(np.prod(odd / (odd - 1))); p_z = boost_z / lnN
    gam = 0.5772156649015329
    surv_B = math.exp(-gam) / math.log(B) * (1 + 1 / (2 * math.log(B) ** 2))      # prod_{s<=B} (1 - 1/s), Mertens with Rosser-Schoenfeld size of error
    surv_z = 0.5 * float(np.prod(1 - 1 / odd)); sigma = min(1.0, surv_B / surv_z); p_B = 1 / (surv_B * lnN)
    lnn = lng + lnX2 - lnP                                                         # ln of the number of even N < 10^digits with k rows left
    print(f"# {path}: Q={Q} z={z} moduli={par['moduli']} betas={len(betas)} (to {betas[-1]:.2f}) sweeps={par['sweeps']} WHAM iterations={its}")
    print(f"# states ln={lnstates:.3f}; ln prod s={lnP:.3f}; even N < 10^{digits} per residue vector: e^{lnX2 - lnP:.3f}; boost_z={boost_z:.4f} p_z={p_z:.5f}; "
          f"to B={B:.0e}: sigma={sigma:.4f} p_B={p_B:.5f}")
    cold = info[-1]; print(f"# coldest beta used {betas[-1]:.2f}: mean k {cold['mean']:.1f}, sd {cold['sd']:.1f}, lowest k seen {cold['min']}, exchange acceptance to the next {info[-2]['swap']:.2f}")
    # thermodynamic table
    print("# beta   <k>     sd    S(beta)=ln(effective number of states)   ln(number of N)   acceptance of class changes by modulus size")
    for i in range(0, len(betas), max(1, len(betas) // 27)):
        w = lng - betas[i] * E; lz = logsumexp(w); pk = np.exp(w - lz); mk = float(np.sum(pk * E))
        S = float(lz + betas[i] * mk)
        print(f"  {betas[i]:5.2f} {mk:8.1f} {info[i]['sd']:6.1f} {S:9.2f} {S + lnX2 - lnP:9.2f}    " + " ".join(f"{a:.3f}" for a in info[i]['acc'] if a >= 0))
    good = np.isfinite(lnn)
    # 2. ideal search to depth z
    q_z = math.log1p(-p_z)
    lnX = np.logaddexp.accumulate(np.where(good, lnn, -np.inf)); lnY = np.logaddexp.accumulate(np.where(good, lnn + q_z * E, -np.inf))
    def crossing(lnXc, lnYc, label):
        j = int(np.argmax(lnYc >= 0)) if np.any(lnYc >= 0) else -1
        if j <= 0: print(f"  {label}: expected successes never reach 1 in the sampled range (ln Y max {float(np.max(lnYc)):.2f})"); return None
        t = (0 - lnYc[j - 1]) / (lnYc[j] - lnYc[j - 1]) if np.isfinite(lnYc[j - 1]) else 1.0
        return float(lnXc[j - 1] + t * (lnXc[j] - lnXc[j - 1])) if np.isfinite(lnXc[j - 1]) else float(lnXc[j]), j
    r = crossing(lnX, lnY, "depth z")
    print(f"\nIdeal search to depth z = {z} (N tested in increasing order of the rows left at depth z):")
    if r:
        x, j = r; print(f"  one expected success after e^{x:.2f} tested N, down to k = {E[j]} rows left (success per N there e^{q_z * E[j]:.2f})")
    jb = int(np.argmax(lnX >= budget)) if np.any(lnX >= budget) else len(E) - 1
    print(f"  with a budget of e^{budget:.2f} N: k up to {E[jb]}, expected successes e^{float(lnY[jb]) if lnX[jb] <= budget + 1e-9 else float(lnY[jb - 1] + (budget - lnX[jb - 1]) / (lnX[jb] - lnX[jb - 1]) * (lnY[jb] - lnY[jb - 1])):.2f}")
    # 3. ideal search to depth B with a binomial tail
    if sigma < 1:
        q_B = math.log1p(-p_B); ks = E[good]; ln_nk = lnn[good]; Rmax = int(ks.max())
        lf = np.array([math.lgamma(v + 1) for v in range(Rmax + 2)])
        Rs = np.arange(0, Rmax + 1)
        # ln of n(k) * Bin(R; k, sigma) on a grid (k, R)
        K2, R2 = np.meshgrid(ks, Rs, indexing="ij"); valid = R2 <= K2
        with np.errstate(invalid="ignore"):
            lb = np.where(valid, lf[K2] - lf[np.minimum(R2, K2)] - lf[np.maximum(K2 - R2, 0)] + R2 * math.log(sigma) + (K2 - R2) * math.log1p(-sigma), -np.inf)
        joint = ln_nk[:, None] + lb
        lnx_R = logsumexp(joint, axis=0); lny_R = lnx_R + q_B * Rs
        lnXR = np.logaddexp.accumulate(lnx_R); lnYR = np.logaddexp.accumulate(lny_R)
        print(f"\nIdeal search to depth B = {B:.0e}, rows beyond z = {z} independent (N tested in increasing order of the rows left at depth B):")
        r = crossing(lnXR, lnYR, "depth B")
        if r:
            x, j = r
            wk = joint[:, j] - logsumexp(joint[:, j]); kbar = float(np.sum(np.exp(wk) * ks))
            print(f"  one expected success after e^{x:.2f} tested N, down to R = {Rs[j]} rows left at depth B (success per N there e^{q_B * Rs[j]:.2f}); "
                  f"those N have {kbar:.0f} rows left at depth z on average, of which {Rs[j] / kbar:.3f} survive to B (unselected: {sigma:.3f})")
        jb = int(np.argmax(lnXR >= budget)) if np.any(lnXR >= budget) else len(Rs) - 1
        if 0 < jb:
            t = (budget - lnXR[jb - 1]) / (lnXR[jb] - lnXR[jb - 1]) if np.isfinite(lnXR[jb - 1]) else 1.0
            print(f"  with a budget of e^{budget:.2f} N: R up to {Rs[jb]}, expected successes e^{float(lnYR[jb - 1] + t * (lnYR[jb] - lnYR[jb - 1])) if np.isfinite(lnYR[jb - 1]) else float(lnYR[jb]):.2f}")
        # for reference: no selection at all beyond z (every N with k rows at depth z tested): same as depth z
    # low end of the density of states
    print("\n# low end: k, ln g(k), ln(number of N), samples")
    idx = np.nonzero(good)[0][:12]
    for i in idx: print(f"  {E[i]:6d} {lng[i]:9.2f} {lnn[i]:9.2f} {int(tot[i])}")
