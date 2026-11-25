"""Scoring against the exact enumeration of the miniature (truth.c): every method is judged by the members it puts
forward, examined in increasing order of the rows left at depth 200, exactly as toy_compare.py judges the two orders."""
import math, os
import numpy as np

DATA = os.environ.get("PPRIME_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
N = np.memmap(os.path.join(DATA, "N.u32"), dtype=np.uint32, mode="r")
K1 = np.memmap(os.path.join(DATA, "k1.u8"), dtype=np.uint8, mode="r")
K2 = np.memmap(os.path.join(DATA, "k2.u8"), dtype=np.uint8, mode="r")
SUCC = np.memmap(os.path.join(DATA, "succ.u8"), dtype=np.uint8, mode="r")
TARGETS = (1, 3, 10, 30)
COVER = {1: 2982.0, 3: 63350.0, 10: 253380.0, 30: 1205425.0}      # N examined, cover first (toy_compare_1e9_1000.txt)
IDEAL = {1: 13.0, 3: 401.0, 10: 10811.0, 30: 73849.0}              # N examined, ideal order to depth 200


def examined(k, s, targets=TARGETS):
    """N examined to collect t successes when the members (levels k, success flags s) are taken in increasing k,
    in random order inside a level (linear interpolation inside the level, as in toy_compare.py)"""
    k = np.asarray(k); s = np.asarray(s)
    kmax = int(k.max()) + 1 if len(k) else 1
    cn = np.bincount(k, minlength=kmax); cs = np.bincount(k, weights=s, minlength=kmax)
    out = {}
    for t in targets:
        pn = ps = 0.0; val = math.inf
        for lev in range(kmax):
            n2, s2 = pn + cn[lev], ps + cs[lev]
            if s2 >= t:
                val = pn + (n2 - pn) * (t - ps) / (s2 - ps); break
            pn, ps = n2, s2
        out[t] = val
    return out


def index_of(cand):
    cand = np.unique(np.asarray(cand, dtype=np.uint32))
    idx = np.searchsorted(N, cand)
    ok = (idx < len(N)); ok[ok] &= (N[idx[ok]] == cand[ok])
    return idx[ok], int((~ok).sum())


def evaluate(cand):
    """candidates (any integers): those that are members are scored at depth 200 and examined in that order"""
    idx, notmem = index_of(cand)
    idx = np.sort(idx)
    k = np.asarray(K2[idx]); s = np.asarray(SUCC[idx])
    ex = examined(k, s)
    return {"members": len(idx), "not_members": notmem, "successes": int(s.sum()), "examined": ex,
            "gain": {t: (math.log(COVER[t] / ex[t]) if math.isfinite(ex[t]) else -math.inf) for t in TARGETS}}


def fmt(res):
    g = res["gain"]; e = res["examined"]
    return (f"{res['members']:>10,d} | {res['successes']:>4d} | " +
            " | ".join((f"{e[t]:>11,.0f}" if math.isfinite(e[t]) else f"{'-':>11}") for t in TARGETS) + " | " +
            " | ".join((f"{g[t]:+6.2f}" if math.isfinite(g[t]) else f"{'-':>6}") for t in TARGETS))
