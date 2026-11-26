# The page's 14 real-window instances (same RNG draw order to get the same lists), verifier's own counting and search.
import math, random, sys, numpy as np, flint
from collections import deque
from vlib import *
cov, rows = get(); N0, M, K = win(cov); P = lp(467, 5000)
random.seed(5)
inst = []
for m, f in ((1, 40), (2, 30), (3, 8), (3, 20), (4, 4), (4, 8), (5, 3), (5, 4), (6, 2), (6, 3), (8, 2), (10, 2), (12, 1.5), (16, 1.3)):
    sl = P[:m]; inst.append((m, f, sl, [(random.randrange(s), random.randrange(1, s), int(round(s / f))) for s in sl]))
kk = np.arange(K, dtype=np.int64)
def lll_basis(sl, el, ell):
    n = len(ell); big = max(ell) << 40; w = [big // l for l in ell]
    rowsB = [[w[0]] + [e * w[i + 1] for i, e in enumerate(el)]] + [[0] * (i + 1) + [s * w[i + 1]] + [0] * (len(sl) - i - 1) for i, s in enumerate(sl)]
    A = flint.fmpz_mat(rowsB).lll(); B = [[int(A[i, j]) for j in range(n)] for i in range(n)]
    assert all(B[i][j] % w[j] == 0 for i in range(n) for j in range(n))
    return [[B[i][j] // w[j] for j in range(n)] for i in range(n)]
for m, f, sl, lists in inst:
    n = m + 1; el = [pow(d, -1, s) for s, (a, d, L) in zip(sl, lists)]; ell = [K] + [L for a, d, L in lists]
    o = [0] + [(e * a) % s for s, e, (a, d, L) in zip(sl, el, lists)]
    # brute force by the ORIGINAL definition: k mod s in {a + d t : t < L}
    ok = np.ones(K, dtype=bool)
    for s, (a, d, L) in zip(sl, lists):
        member = np.zeros(s, dtype=bool); member[(a + d * np.arange(L)) % s] = True; ok &= member[kk % s]
    Zb = int(ok.sum()); E = K * math.prod(L / s for s, (a, d, L) in zip(sl, lists))
    B = lll_basis(sl, el, ell)
    wp = [sum(max(B[i][j], 0) for i in range(n)) for j in range(n)]; wm = [sum(max(-B[i][j], 0) for i in range(n)) for j in range(n)]
    tau = [(wp[j] + wm[j]) / ell[j] for j in range(n)]
    lowb = E * math.prod(max(0, 1 - t) for t in tau); upb = E * math.prod(1 + t for t in tau); wb = E * math.prod(1 + 2 * t for t in tau)
    # |W| exactly, by counting: k in [-wp0, K + wm0], and for each i the number of j with e k - s j - o_i in [-wp_i, L_i + wm_i]
    k2 = np.arange(-wp[0], K + wm[0] + 1, dtype=np.int64); cntW = np.ones(len(k2), dtype=np.int64)
    for i, (s, e) in enumerate(zip(sl, el)):
        r = (e * (k2 % s) - o[i + 1]) % s            # representatives r + s t ; count t with -wp <= r + s t <= L + wm
        loT = np.ceil((-wp[i + 1] - r) / s).astype(np.int64); hiT = np.floor((ell[i + 1] + wm[i + 1] - r) / s).astype(np.int64)
        cntW *= np.maximum(hiT - loT + 1, 0)
    Wsize = int(cntW.sum())
    line = "m=%d 1/%s E=%.1f low=%.1f Zbrute=%d up=%.1f |W|=%d Wbound=%.1f taumax=%.3f KL=%.2f" % (m, f, E, lowb, Zb, upb, Wsize, wb, max(tau), sum(math.log(s / L) for s, (a, d, L) in zip(sl, lists)))
    ok_bounds = lowb <= Zb <= upb and Wsize <= wb
    vis = None
    if Wsize <= 700000:
        Bq = flint.fmpq_mat(flint.fmpz_mat(B)); y = flint.fmpq_mat([[flint.fmpq(2 * o[j] + ell[j], 2) for j in range(n)]]); tc = y * Bq.inv()
        x0 = tuple(sum(int(tc[0, i].p // tc[0, i].q) * B[i][j] for i in range(n)) for j in range(n))
        lo = [o[j] - wp[j] for j in range(n)]; hi = [o[j] + ell[j] + wm[j] for j in range(n)]
        steps = [tuple(b) for b in B] + [tuple(-v for v in b) for b in B]
        seen = {x0}; dq = deque([x0]); found = []
        while dq:
            x = dq.popleft()
            if 0 <= x[0] < K and all(0 <= x[j] - o[j] < ell[j] for j in range(1, n)): found.append(x[0])
            for b in steps:
                zz = tuple(u + v for u, v in zip(x, b))
                if zz not in seen and all(l <= u <= h for l, u, h in zip(lo, zz, hi)): seen.add(zz); dq.append(zz)
        vis = len(seen); same = np.array_equal(np.sort(np.array(found)), np.nonzero(ok)[0])
        line += " visited=%d visited/Z=%.2f identical=%s W_connected=%s" % (vis, vis / Zb, same, vis == Wsize)
    print(line, "bounds_ok=%s" % ok_bounds, flush=True)
