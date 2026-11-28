#!/usr/bin/env python3
"""A learned predictor of 'this surviving row is prime' on real 200-digit rows (ml_data.npz), scored out of sample.
Three fits, each split BY MEMBER (60% train, 15% validation for early stopping, 25% test):
  MAIN     rows with no factor <= 10^6; features: bits of n, residues mod primes < 100, Jacobi symbols, row context.
  CONTROL1 rows sieved by all primes <= 10^6 except 25 control primes; features of MAIN + 25 indicators 'control prime divides n'
           (a linear signal of known size: can the pipeline see 10^-3 nats a row?)
  CONTROL2 MAIN + two planted bits whose XOR is a weak coin (P(c=1|prime)=0.75, 0.5 otherwise): a NON-linear signal of
           about 0.004 nats a row that no single feature carries.
Score: mean log-loss of the constant rate (fitted on train) minus mean log-loss of the model, on the test members,
in nats per row, with a bootstrap over test members.  The 'free parity' of the sieve lens would score 0.0385."""
import numpy as np, math, sys, time
d = np.load("ml_data.npz"); rng = np.random.default_rng(7)
mem, k, q, y, ctrl, lo, hi, res, jac, S, rank, sp = (d[x] for x in ("mem", "k", "q", "y", "ctrl", "lo", "hi", "res", "jac", "S", "rank", "sp"))
n = len(y); print("rows", n, "members", mem.max() + 1, "prime rate", y.mean(), "ctrl-divisible", ctrl.mean())
def bits(a): return ((a[:, None] >> np.arange(64, dtype=np.uint64)[None, :]) & np.uint64(1)).astype(np.float32)
F = [bits(lo)[:, 1:], bits(hi)]
ang = 2 * np.pi * res.astype(np.float32) / sp[None, :].astype(np.float32); F += [np.cos(ang), np.sin(ang)]
for i, p in enumerate(sp[:5]): F.append((res[:, i][:, None] == np.arange(1, p)[None, :]).astype(np.float32))
F.append(jac.astype(np.float32))
gap_prev = np.r_[0, np.diff(q)].astype(np.float64); gap_prev[rank == 0] = q[rank == 0]
gap_next = np.r_[np.diff(q), 0].astype(np.float64); last = np.r_[rank[1:] == 0, True]; gap_next[last] = 200000 - q[last]
pop = bits(lo).sum(1) + bits(hi).sum(1)
F.append(np.c_[q / 2e5, k / 2.14e7, S, rank / S, np.log(gap_prev + 1), np.log(gap_next + 1), pop].astype(np.float32))
X0 = np.concatenate(F, axis=1); print("features", X0.shape[1])
members = np.arange(mem.max() + 1); rng.shuffle(members)
ntr, nva = int(.6 * len(members)), int(.15 * len(members))
role = np.zeros(len(members), dtype=int); role[members[ntr:ntr + nva]] = 1; role[members[ntr + nva:]] = 2; rrow = role[mem]

def ll(p, yy): p = np.clip(p, 1e-7, 1 - 1e-7); return -(yy * np.log(p) + (1 - yy) * np.log(1 - p))

def fit(X, yy, sel, name, hidden=(64, 32), epochs=10, seed=0):
    X = X[sel]; yy = yy[sel].astype(np.float32); r = rrow[sel]; mm = mem[sel]
    mu, sd = X[r == 0].mean(0), X[r == 0].std(0) + 1e-6; X = (X - mu) / sd
    Xt, yt, Xv, yv, Xs, ys = X[r == 0], yy[r == 0], X[r == 1], yy[r == 1], X[r == 2], yy[r == 2]
    g = np.random.default_rng(seed); sizes = (X.shape[1],) + hidden + (1,)
    W = [g.normal(0, math.sqrt(2 / a), (a, b)).astype(np.float32) for a, b in zip(sizes[:-1], sizes[1:])]
    B = [np.zeros(b, dtype=np.float32) for b in sizes[1:]]; B[-1][:] = math.log(yt.mean() / (1 - yt.mean()))
    W[-1] *= 0.01
    mW = [np.zeros_like(w) for w in W]; vW = [np.zeros_like(w) for w in W]; mB = [np.zeros_like(b) for b in B]; vB = [np.zeros_like(b) for b in B]
    def fwd(Z):
        acts = [Z]
        for i in range(len(W)):
            Z = Z @ W[i] + B[i]
            if i < len(W) - 1: Z = np.maximum(Z, 0)
            acts.append(Z)
        return acts
    def pred(Z): return 1 / (1 + np.exp(-fwd(Z)[-1][:, 0]))
    best = (1e9, None); t = 0; lr = 1e-3; bs = 2048; wd = 1e-4; bad = 0; traj = []; base0 = yt.mean()
    for ep in range(epochs):
        perm = g.permutation(len(yt))
        for s in range(0, len(perm), bs):
            ix = perm[s:s + bs]; acts = fwd(Xt[ix]); p = 1 / (1 + np.exp(-acts[-1][:, 0]))
            delta = ((p - yt[ix]) / len(ix))[:, None]; t += 1
            for i in range(len(W) - 1, -1, -1):
                gW = acts[i].T @ delta + wd * W[i]; gB = delta.sum(0)
                if i > 0: delta = (delta @ W[i].T) * (acts[i] > 0)
                for (par, grad, m_, v_) in ((W[i], gW, mW[i], vW[i]), (B[i], gB, mB[i], vB[i])):
                    m_ *= 0.9; m_ += 0.1 * grad; v_ *= 0.999; v_ += 0.001 * grad * grad
                    par -= lr * (m_ / (1 - 0.9 ** t)) / (np.sqrt(v_ / (1 - 0.999 ** t)) + 1e-8)
        lv = ll(pred(Xv), yv).mean()
        traj.append((ll(np.full(len(yv), base0), yv).mean() - lv, (ll(np.full(len(ys), base0), ys) - ll(pred(Xs), ys)).mean()))
        if lv < best[0] - 1e-6: best = (lv, ([w.copy() for w in W], [b.copy() for b in B])); bad = 0
        else:
            bad += 1
            if bad >= 3: break
    W, B = best[1]
    base = yt.mean(); ps = pred(Xs)
    dl = ll(np.full(len(ys), base), ys) - ll(ps, ys)
    tm = mm[r == 2]; um = np.unique(tm); sums = np.array([dl[tm == u].sum() for u in um]); cnts = np.array([(tm == u).sum() for u in um])
    bo = [];
    for _ in range(400):
        ix = g.integers(0, len(um), len(um)); bo.append(sums[ix].sum() / cnts[ix].sum())
    # top-decile lift: prime rate among the 10% of test rows the model likes least / most
    o = np.argsort(ps); m10 = len(o) // 10
    print(f"{name}: train rows {len(yt)}, test rows {len(ys)}, epochs run {ep + 1}; validation gain {ll(np.full(len(yv), base), yv).mean() - best[0]:+.6f};"
          f" TEST gain {dl.mean():+.6f} +- {np.std(bo):.6f} nats/row; prime rate bottom/top decile by score {ys[o[:m10]].mean():.4f} / {ys[o[-m10:]].mean():.4f} (all {ys.mean():.4f})", flush=True)
    print('     per epoch (validation gain, test gain), units of 1e-6 nats/row: ' + ' '.join(f'({a * 1e6:+.0f},{b * 1e6:+.0f})' for a, b in traj), flush=True)
    return dl.mean(), np.std(bo)

clean = ~ctrl
fit(X0, y, clean, 'MAIN (MLP 64-32)', seed=0)
fit(X0, y, clean, 'MAIN logistic (no hidden layer)', hidden=())
# control 1: unsieved control primes, with indicators
d2 = np.load("ml_ctrl.npz") if False else None
fit(np.c_[X0, d["ctrlind"].astype(np.float32)] if "ctrlind" in d else np.c_[X0, ctrl.astype(np.float32)], y, np.ones(n, bool), "CONTROL1 (one indicator: a control prime divides n)")
yy = y.astype(bool); pb = y.mean()
f = ctrl.mean(); r1 = y[~ctrl].mean()
print(f"   the information available in CONTROL1: {(-pb*math.log(pb)-(1-pb)*math.log(1-pb)) - (1-f)*(-r1*math.log(r1)-(1-r1)*math.log(1-r1)):.6f} nats/row")
# control 2: planted XOR coin
c = np.where(yy, rng.random(n) < 0.75, rng.random(n) < 0.5); b1 = rng.random(n) < 0.5; b2 = b1 ^ c
pc1 = c[clean].mean(); info = 0
for cv in (0, 1):
    w = (c[clean] == cv).mean(); rr = y[clean][c[clean] == cv].mean(); info += w * (-rr * math.log(rr) - (1 - rr) * math.log(1 - rr))
r0 = y[clean].mean()
print(f"   the information planted in CONTROL2: {(-r0*math.log(r0)-(1-r0)*math.log(1-r0)) - info:.6f} nats/row")
fit(np.c_[X0, b1.astype(np.float32), b2.astype(np.float32)], y, clean, "CONTROL2 (planted XOR of two bits)")
fit(np.c_[X0, b1.astype(np.float32), b2.astype(np.float32)], y, clean, "CONTROL2 logistic (cannot see an XOR)", hidden=())
