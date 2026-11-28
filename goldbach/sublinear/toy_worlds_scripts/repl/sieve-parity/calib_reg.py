#!/usr/bin/env python3
"""Any linear combination of the pattern features: logistic regression fitted on half of the members and scored on the other half (both ways)."""
import math, numpy as np
d = np.load("features.npz"); y = d["y"].astype(np.float64); mi = d["mi"]; F = d["F"]; Cc = d["Cc"]; fn = list(d["fnames"]); cn = list(d["cnames"]); n = len(y); nm = int(mi.max()) + 1
leak = lambda name: ("(probable) prime" in name) or ("primes among" in name) or ("is prime" in name)
member_level = lambda name: name.startswith("member") or name in ("k", "k mod 2", "k mod 3", "k mod 5", "k mod 7")
for label, drop_member in (("all 69 pattern features", False), ("row-level pattern features only (member-level ones dropped)", True)):
    cols = [F[:, j] for j, name in enumerate(fn) if not leak(name) and F[:, j].std() > 0 and not (drop_member and member_level(name))]
    cols += [(Cc[:, j] == Cc[:, j].max()).astype(np.float32) for j, name in enumerate(cn) if not leak(name) and len(np.unique(Cc[:, j])) == 2 and not (drop_member and member_level(name))]
    X = np.column_stack(cols).astype(np.float32); X = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1); X = np.column_stack([np.ones(n, dtype=np.float32), X]); kf = X.shape[1] - 1
    def fit(Xa, ya, lam=1.0):
        Xa = Xa.astype(np.float64); b = np.zeros(Xa.shape[1]); b[0] = math.log(ya.mean() / (1 - ya.mean()))
        for it in range(8):
            p_ = 1 / (1 + np.exp(-Xa @ b)); Wt = p_ * (1 - p_)
            H = (Xa * Wt[:, None]).T @ Xa + lam * np.eye(Xa.shape[1]); g = Xa.T @ (ya - p_) - lam * b * (np.arange(len(b)) > 0); b = b + np.linalg.solve(H, g)
        return b
    ll = lambda p_, ya: (ya * np.log(p_) + (1 - ya) * np.log(1 - p_)).sum()
    tr = (mi % 2 == 0); te = ~tr
    for A, B, nm_ in ((tr, te, "fit on even-numbered members, score on odd"), (te, tr, "fit on odd, score on even")):
        b = fit(X[A], y[A]); pt = 1 / (1 + np.exp(-(X[B].astype(np.float64) @ b))); p0 = y[A].mean()
        gin = ll(1 / (1 + np.exp(-(X[A].astype(np.float64) @ b))), y[A]) - ll(np.full(int(A.sum()), p0), y[A]); gain = ll(pt, y[B]) - ll(np.full(int(B.sum()), p0), y[B])
        mem = mi[B]; um = np.unique(mem)
        ex = np.bincount(mem, weights=-np.log1p(-pt), minlength=nm)[um]; cnt = np.bincount(mem, minlength=nm)[um]; prm = np.bincount(mem, weights=y[B], minlength=nm)[um]
        resid = ex - cnt * (-math.log1p(-p0)); cc = np.corrcoef(resid, prm - cnt * p0)[0, 1]
        o = np.argsort(resid); fifth = len(o) // 5
        lo = prm[o[:fifth]].sum() / cnt[o[:fifth]].sum(); hi = prm[o[-fifth:]].sum() / cnt[o[-fifth:]].sum()
        print(f"{label}, {kf} features, {nm_}: gain in sample {gin:+.1f} nats (+{kf / 2:.0f} expected from fitting noise); out of sample {gain:+.1f} nats on {int(B.sum())} rows (-{kf / 2:.0f} expected if there is nothing); "
              f"sd over members of the fitted exponent beyond the count {resid.std():.4f} nats, correlation with the primes found beyond the count {cc:+.4f} +- {1 / math.sqrt(len(um)):.4f}; "
              f"prime rate in the fifth of members fitted emptiest {lo:.5f}, fullest {hi:.5f} (difference {lo - hi:+.5f} +- {math.sqrt(2 * p0 * (1 - p0) / cnt[o[:fifth]].sum()):.5f})", flush=True)
    del X
