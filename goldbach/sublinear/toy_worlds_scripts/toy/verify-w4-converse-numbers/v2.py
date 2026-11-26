import math, numpy as np, sympy
from vlib import *
cov, rows = get(); n = len(rows); rng = np.random.default_rng(20261126)
# C1 identity check at a few primes: FFT coefficient == Phi(h/s) direct
for s in (467, 1009, 4759):
    t = tab(rows, s).astype(float); F = np.fft.fft(t)
    h = np.arange(s); d = max(abs(np.exp(-2j * np.pi * ((rows * hh) % s) / s).sum() - F[hh]) for hh in (1, 2, 7, s // 6, s - 1))
    print("C1 check s", s, "max |Phi(h/s)-F(h)| =", d)
def cand_table(s, D):
    q = np.arange(Q); ok = np.ones(Q, bool)
    if D % 2 == 0: ok &= q % 2 == 1
    for r in (3, 5, 7, 11):
        if D % r == 0: ok &= (q % r != 0) & (q % r != cov[r])
    c = np.zeros(s); np.add.at(c, q[ok] % s, 1); return c * (n / ok.sum())
def modD(t, D):
    s = len(t); best = None
    idx = np.arange(s) % D
    sm = np.bincount(idx, weights=t, minlength=D); ct = np.bincount(idx, minlength=D)
    mb = np.where(ct > 0, sm / np.maximum(ct, 1), -1e9); b = int(mb.argmax())
    g = mb[b] - t.mean(); return g, g / math.log(s / ct[b])
def run(pr, label):
    mr = []; ms = []; res = {D: [] for D in (6, 30, 210, 2310)}; arg = []
    for s in pr:
        t = tab(rows, s).astype(float); v = t.var()
        P = np.abs(np.fft.fft(t)) ** 2 / (s * v); mr.append(P[1:].max() / math.log(s - 1))
        u = rng.permutation(t); Pu = np.abs(np.fft.fft(u)) ** 2 / (s * v); ms.append(Pu[1:].max() / math.log(s - 1))
        for D in res:
            if D < s:
                ct = cand_table(s, D) if (s < 5000 and D in (6, 2310)) or s >= 5000 else None
                cc = np.corrcoef(t, ct)[0, 1] if ct is not None else float('nan')
                res[D].append(modD(t, D) + modD(u, D) + (modD(ct, D) if ct is not None else (float('nan'),) * 2) + (cc,))
    i = int(np.argmax(mr))
    print(label, len(pr), "primes: max power/ln(s-1) real %.3f (max %.2f at %d) shuffled %.3f" % (np.mean(mr), mr[i], pr[i], np.mean(ms)))
    for D in res:
        if res[D]:
            a = np.array(res[D]); print("   D=%d gain real %.4f shuf %.4f pred %.4f | rate real %.4f shuf %.4f pred %.4f | corr %.4f R2 %.4f" % (D, a[:,0].mean(), a[:,2].mean(), a[:,4].mean(), a[:,1].mean(), a[:,3].mean(), a[:,5].mean(), a[:,6].mean(), (a[:,6]**2).mean()))
run(lp(467, 5000), "[467,5000)")
for lo, hi, st in ((5000, 20000, 20), (20000, 60000, 60), (60000, 200000, 200), (200000, 600000, 400)):
    run(lp(lo, hi)[::st], "[%d,%d) every %d" % (lo, hi, st))
