"""Reference curves at a given amount of work W (members scored at depth 200):
  r2(W): the first W members in cover-first order (rows left at depth 23, random inside a level), scored at depth 200
  r1(W): a random sample of W members, scored at depth 200 (median over 20 samples of the examined counts)
The cover-first order is computed once and kept in data/cover_order.npy."""
import math, os
import numpy as np
import pp

_ORDER = None
def cover_order():
    global _ORDER
    if _ORDER is None:
        path = os.path.join(pp.DATA, "cover_order.npy")
        if not os.path.exists(path):
            rng = np.random.default_rng(1)
            k1 = np.asarray(pp.K1)
            np.save(path, np.lexsort((rng.random(len(k1)), k1)).astype(np.int32))
        _ORDER = np.load(path, mmap_mode="r")
    return _ORDER

def gains(ex):
    return {t: (math.log(pp.COVER[t] / ex[t]) if math.isfinite(ex[t]) else -math.inf) for t in pp.TARGETS}

def r2(W):
    W = int(min(max(W, 1), len(pp.K1)))
    idx = np.sort(np.asarray(cover_order()[:W]))
    ex = pp.examined(np.asarray(pp.K2[idx]), np.asarray(pp.SUCC[idx]))
    return {"members": W, "successes": int(np.asarray(pp.SUCC[idx]).sum()), "examined": ex, "gain": gains(ex)}

def r1(W, reps=20, seed=7):
    W = int(min(max(W, 1), len(pp.K1)))
    rng = np.random.default_rng(seed); exs = {t: [] for t in pp.TARGETS}; sc = []
    for _ in range(reps):
        idx = np.sort(rng.choice(len(pp.K1), size=W, replace=False))
        s = np.asarray(pp.SUCC[idx]); ex = pp.examined(np.asarray(pp.K2[idx]), s); sc.append(int(s.sum()))
        for t in pp.TARGETS: exs[t].append(ex[t])
    med = {t: float(np.median(exs[t])) for t in pp.TARGETS}
    return {"members": W, "successes": float(np.mean(sc)), "examined": med, "gain": gains(med)}

def direct(members, successes):
    """candidates examined as they come, in random order: expected number examined for t successes"""
    ex = {t: ((members + 1) * t / (successes + 1) if successes >= t else math.inf) for t in pp.TARGETS}
    return {"examined": ex, "gain": gains(ex)}

def cells(d, key="examined", f="{:,.0f}"):
    return " | ".join((f.format(d[key][t]) if math.isfinite(d[key][t]) else "-") for t in pp.TARGETS)

if __name__ == "__main__":
    for W in (10000, 1000000):
        a = r2(W); print(W, a["successes"], cells(a), cells(a, "gain", "{:+.2f}"))
