#!/usr/bin/env python3
"""(a) Does any cheap function of the sieve pattern predict which surviving rows are prime?
   usage: analyse_features.py rowsA.npz rowsB.npz ...   (outputs of gen_rows.py)"""
import sys, math, time, numpy as np, gmpy2
sys.path.insert(0, "/home/user/sirdarckcat.github.io/goldbach/sublinear")
import cover_record as cr
Q = 200000
f = cr.S + "q200000_m89.txt"
line = [x for x in open(f) if x.startswith("COVER")][0].split()
cov = [(int(t.split(":")[0]), int(t.split(":")[1])) for t in line if ":" in t]
M = 2
for r, a in cov: M *= r
N0 = 0; mod = 1
for r, a in [(2, 0)] + cov:
    t = ((a - N0) * pow(mod, -1, r)) % r; N0 += mod * t; mod *= r
D = [np.load(x) for x in sys.argv[1:] if x.endswith('.npz')]
rows = D[0]["rows"]; ks = np.concatenate([d["ks"] for d in D]); LPF = np.concatenate([d["LPF"] for d in D]); NF = np.concatenate([d["NF"] for d in D]); PRP = np.concatenate([d["PRP"] for d in D])
ks, ui = np.unique(ks, return_index=True); LPF = LPF[ui]; NF = NF[ui]; PRP = PRP[ui]
nm, nr = LPF.shape; surv = LPF == 0
print(f"members {nm}; rows {nr}; survivors {int(surv.sum())} ({surv.mean():.6f} of rows); probable primes {int(PRP.sum())} ({PRP.sum() / surv.sum():.5f} of survivors)")
# model rate: prod_{p <= 1e8} p/(p-1) / ln N
def primes_upto(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
PZ = primes_upto(10 ** 8).astype(np.float64); C = math.exp(-np.log1p(-1 / PZ).sum()); del PZ
lnN = np.array([math.log(N0 + int(k) * M) for k in ks])
pk = C / lnN
S = surv.sum(1); exp_pr = (S * pk).sum(); got = PRP.sum()
print(f"model C = prod p/(p-1) to 1e8 = {C:.5f}; expected primes {exp_pr:.1f}, found {got}: ratio {got / exp_pr:.4f} +- {1 / math.sqrt(got):.4f}")
pm = PRP.sum(1); var_binom = (S * pk * (1 - pk)).sum(); disp = ((pm - S * pk) ** 2).sum() / var_binom
print(f"dispersion of primes per member / binomial: {disp:.4f} +- {math.sqrt(2 / nm):.4f}")
# survivors count: mean, sd
w = 1.0
for p_ in primes_upto(10 ** 6):
    pass
print(f"survivors per member: mean {S.mean():.2f}, sd {S.std():.2f}, min {S.min()}, max {S.max()}; binomial sd would be {math.sqrt(nr * surv.mean() * (1 - surv.mean())):.2f}")
# ---------------- features per survivor ----------------
t0 = time.time()
SP = primes_upto(1000); SPo = SP[SP > 2]
CS = [-6, -4, -3, -2, -1, 1, 2, 3, 4, 6]
lnSP = np.log(SPo)
mi, ji = np.nonzero(surv); y = PRP[mi, ji].astype(np.float64); n = len(y)
feat = {}; cat = {}
qv = rows[ji]
feat["q (row value)"] = qv.astype(float)
feat["row index"] = ji.astype(float)
feat["member survivors S"] = S[mi].astype(float)
feat["k"] = ks[mi].astype(float)
cat["k mod 2"] = ks[mi] % 2; cat["k mod 3"] = ks[mi] % 3; cat["k mod 5"] = ks[mi] % 5; cat["k mod 7"] = ks[mi] % 7
cat["q mod 4"] = qv % 4; cat["q mod 8"] = qv % 8; cat["q mod 5"] = qv % 5; cat["q mod 7"] = qv % 7; cat["q mod 11"] = qv % 11; cat["q mod 13"] = qv % 13; cat["q mod 16"] = qv % 16
# row neighbours inside the member
pad = lambda A, s: np.pad(A, ((0, 0), (1, 1)), constant_values=-1)[:, s]
for name, sl in (("prev", slice(0, nr)), ("next", slice(2, nr + 2))):
    L = np.pad(LPF, ((0, 0), (1, 1)), constant_values=-1)[:, sl][mi, ji]
    cat[f"{name} row survives"] = (L == 0).astype(int)
    feat[f"ln lpf of {name} row (struck only; 0 else)"] = np.where(L > 0, np.log(np.maximum(L, 1)), 0.0)
    cat[f"{name} row struck by a prime < 2000"] = ((L > 0) & (L < 2000)).astype(int)
    cat[f"{name} row struck only by a prime > 1e6"] = (L > 10 ** 6).astype(int)
    F = np.pad(NF, ((0, 0), (1, 1)), constant_values=0)[:, sl][mi, ji]
    feat[f"number of sieve primes dividing {name} row"] = F.astype(float)
    P_ = np.pad(PRP, ((0, 0), (1, 1)), constant_values=0)[:, sl][mi, ji]
    cat[f"{name} row is a (probable) prime"] = P_.astype(int)
cs = np.cumsum(np.pad(surv.astype(np.int32), ((0, 0), (1, 0))), axis=1)
for h in (5, 20, 100):
    lo = np.maximum(ji - h, 0); hi = np.minimum(ji + h + 1, nr)
    feat[f"survivors among the {2 * h} nearest rows (share)"] = (cs[mi, hi] - cs[mi, lo] - 1) / (hi - lo - 1)
cp = np.cumsum(np.pad(PRP.astype(np.int32), ((0, 0), (1, 0))), axis=1)
feat["primes among earlier rows of the member"] = cp[mi, ji].astype(float)
feat["rank of the survivor in its member (share)"] = (cs[mi, ji]) / S[mi]
cat["an earlier row of the member is prime"] = (cp[mi, ji] > 0).astype(int)
for h in (5, 20):
    lo = np.maximum(ji - h, 0); hi = np.minimum(ji + h + 1, nr)
    feat[f"primes among the {2 * h} nearest rows (other than itself)"] = (cp[mi, hi] - cp[mi, lo] - PRP[mi, ji]).astype(float)
qprev = np.where(ji > 0, rows[np.maximum(ji - 1, 0)], 0); feat["gap to previous row"] = (qv - qprev).astype(float)
# struck-pattern statistics of the member that are not the count
big = (LPF > 10 ** 6).sum(1); small = ((LPF > 0) & (LPF < 5000)).sum(1); multi = (NF >= 2).sum(1); tot = NF.sum(1)
feat["member: rows struck first by a prime > 1e6"] = big[mi].astype(float)
feat["member: rows struck first by a prime < 5000"] = small[mi].astype(float)
feat["member: rows struck by two or more primes"] = multi[mi].astype(float)
feat["member: incidences (sum of NF)"] = tot[mi].astype(float)
# neighbours n + c: small prime factors to 1000 ; and digits of n
om = {c: np.zeros(n) for c in CS}; sm = {c: np.zeros(n) for c in CS}; lp = {c: np.zeros(n) for c in CS}
pop = np.zeros(n); v2m = np.zeros(n); v2p = np.zeros(n); n16 = np.zeros(n, dtype=np.int64); jq = np.zeros(n, dtype=np.int64); jd = np.zeros(n, dtype=np.int64); j3 = np.zeros(n, dtype=np.int64)
starts = np.concatenate([[0], np.cumsum(S)])
for m in range(nm):
    N = N0 + int(ks[m]) * M; a, b = starts[m], starts[m + 1]; q = qv[a:b]
    Nmod = np.array([N % int(p) for p in SPo], dtype=np.int64)
    for c in CS:
        dv = ((Nmod[None, :] - q[:, None] + c) % SPo[None, :]) == 0          # p | n + c
        om[c][a:b] = dv.sum(1); sm[c][a:b] = dv @ lnSP
        first = np.where(dv.any(1), SPo[dv.argmax(1)], 0); lp[c][a:b] = first
    gN = gmpy2.mpz(N); N64 = N % (1 << 40)
    nn = (N64 - q) % (1 << 40)
    v2m[a:b] = [((int(x) - 1) & -(int(x) - 1)).bit_length() - 1 for x in nn]
    v2p[a:b] = [((int(x) + 1) & -(int(x) + 1)).bit_length() - 1 for x in nn]
    n16[a:b] = nn % 16
    qp = qprev[a:b]
    for i in range(b - a):
        x = gN - int(q[i]); pop[a + i] = gmpy2.popcount(x); jq[a + i] = gmpy2.jacobi(int(q[i]), x)
        jd[a + i] = gmpy2.jacobi(int(q[i] - qp[i]) if qp[i] else 1, x); j3[a + i] = gmpy2.jacobi(x >> 332, x)
    if m % 1000 == 0: print("  features", m, "%.0f s" % (time.time() - t0), flush=True)
for c in CS:
    feat[f"n{c:+d}: number of primes <= 1000 dividing (odd)"] = om[c]; feat[f"n{c:+d}: ln of smooth part (primes <= 1000, odd)"] = sm[c]
    cat[f"n{c:+d}: has no odd prime factor <= 1000"] = (om[c] == 0).astype(int)
    cat[f"n{c:+d}: least odd prime factor in (463, 1000]"] = (lp[c] > 463).astype(int)
    cat[f"n{c:+d}: divisible by 3"] = (lp[c] == 3).astype(int)
feat["sum over c of number of small factors of n+c"] = sum(om[c] for c in CS)
feat["v2(n-1)"] = v2m; feat["v2(n+1)"] = v2p; cat["n mod 16"] = n16; cat["popcount(n) mod 2"] = pop.astype(np.int64) % 2; feat["popcount(n)"] = pop
cat["Jacobi(q | n)"] = jq; cat["Jacobi(q - q_prev | n)"] = jd; cat["Jacobi(top half of n | n)"] = j3
cat["v2(n-1) >= 3"] = (v2m >= 3).astype(int)
feat["smooth part of n-1 and n+1 together (ln)"] = sm[-1] + sm[1] + (v2m + v2p) * math.log(2)
if "--dump" in sys.argv:
    np.savez("features.npz", y=y.astype(np.int8), mi=mi.astype(np.int32), ji=ji.astype(np.int16),
             fnames=np.array(list(feat.keys())), cnames=np.array(list(cat.keys())),
             F=np.column_stack([np.asarray(feat[k], dtype=np.float32) for k in feat]), Cc=np.column_stack([np.asarray(cat[k], dtype=np.int32) for k in cat]))
    print("features dumped", flush=True); sys.exit(0)
# ---------------- tests ----------------
pbar = y.mean(); res = []
for name, x in feat.items():
    x = np.asarray(x, dtype=float); sd = x.std()
    if sd == 0: continue
    r = ((x - x.mean()) * (y - pbar)).mean() / (sd * math.sqrt(pbar * (1 - pbar))); res.append((r * math.sqrt(n), name, "corr %.5f" % r))
for name, x in cat.items():
    vals, inv = np.unique(x, return_inverse=True); cnt = np.bincount(inv); pr = np.bincount(inv, weights=y)
    keep = cnt >= 200
    if keep.sum() < 2: continue
    chi = (((pr - cnt * pbar) ** 2) / (cnt * pbar * (1 - pbar)))[keep].sum(); df = int(keep.sum()) - 1
    if df == 1:
        z = (pr[keep][1] / cnt[keep][1] - pr[keep][0] / cnt[keep][0]) / math.sqrt(pbar * (1 - pbar) * (1 / cnt[keep][0] + 1 / cnt[keep][1]))
        res.append((z, name, f"rates {pr[keep][0] / cnt[keep][0]:.5f} ({cnt[keep][0]}) vs {pr[keep][1] / cnt[keep][1]:.5f} ({cnt[keep][1]})"))
    else:
        res.append(((chi - df) / math.sqrt(2 * df), name, f"chi2 {chi:.1f} on {df} df"))
res.sort(key=lambda t: -abs(t[0]))
zs = np.array([t[0] for t in res])
print(f"\n{len(res)} features on {n} survivors (prime rate {pbar:.5f}); z-scores: max |z| = {abs(zs).max():.2f}, mean z^2 = {(zs ** 2).mean():.3f} (1.00 = no information)")
print("expected max |z| of %d independent normals: about %.2f" % (len(res), math.sqrt(2 * math.log(len(res))) ))
for z, name, extra in res: print(f"   z = {z:+6.2f} | {name} | {extra}")
# per-row heterogeneity
cnt = surv.sum(0); pr = PRP.sum(0); ok = cnt >= 50
chi = (((pr - cnt * pbar) ** 2) / (cnt * pbar * (1 - pbar)))[ok].sum(); df = int(ok.sum()) - 1
print(f"\nrows as categories: chi2 {chi:.1f} on {df} df, z = {(chi - df) / math.sqrt(2 * df):+.2f}")
# ---------------- any linear combination: logistic regression, train on half the members, test on the other half ----------------
names = [k for k in feat if np.asarray(feat[k]).std() > 0]
X = np.column_stack([np.asarray(feat[k], dtype=float) for k in names] + [np.asarray(cat[k] == np.unique(cat[k])[-1], dtype=float) for k in cat if len(np.unique(cat[k])) == 2])
X = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1); X = np.column_stack([np.ones(n), X])
tr = (mi % 2 == 0); te = ~tr
def fit(Xa, ya, lam=1.0):
    b = np.zeros(Xa.shape[1]); b[0] = math.log(ya.mean() / (1 - ya.mean()))
    for it in range(12):
        p_ = 1 / (1 + np.exp(-Xa @ b)); W = p_ * (1 - p_)
        H = (Xa * W[:, None]).T @ Xa + lam * np.eye(Xa.shape[1]); g = Xa.T @ (ya - p_) - lam * b * (np.arange(len(b)) > 0)
        b = b + np.linalg.solve(H, g)
    return b
def ll(p_, ya): return (ya * np.log(p_) + (1 - ya) * np.log(1 - p_)).sum()
for A, B, nm_ in ((tr, te, "train even members, test odd"), (te, tr, "train odd members, test even")):
    b = fit(X[A], y[A]); pt = 1 / (1 + np.exp(-X[B] @ b)); p0 = np.full(B.sum(), y[A].mean())
    gain = ll(pt, y[B]) - ll(p0, y[B]); gin = ll(1 / (1 + np.exp(-X[A] @ b)), y[A]) - ll(np.full(A.sum(), y[A].mean()), y[A])
    # what the fitted score would be worth as a selection statistic: sd over members of the predicted exponent beyond the count
    hz = -np.log1p(-pt); mem = mi[B]; ex = np.bincount(mem, weights=hz, minlength=nm)[np.unique(mem)]; cntm = np.bincount(mem, minlength=nm)[np.unique(mem)]
    resid = ex - cntm * (-math.log1p(-y[A].mean()))
    # realised: do members with low predicted exponent (at given count) have fewer primes?
    prm = np.bincount(mem, weights=y[B], minlength=nm)[np.unique(mem)]
    cc = np.corrcoef(resid, prm - cntm * y[A].mean())[0, 1]
    print(f"logistic regression, {X.shape[1] - 1} features, {nm_}: log-likelihood gain in sample {gin:+.1f} nats (expected about +{(X.shape[1] - 1) / 2:.0f} from fitting noise), out of sample {gain:+.1f} nats on {int(B.sum())} rows ({gain / B.sum():+.2e} per row); sd over members of the predicted exponent beyond the count {resid.std():.4f} nats; correlation of that with the primes actually found beyond the count {cc:+.4f} +- {1 / math.sqrt(len(prm)):.4f}")
