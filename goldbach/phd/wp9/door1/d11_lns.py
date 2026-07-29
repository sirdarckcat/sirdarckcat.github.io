"""Door 1, D1.1: exact large-neighborhood search over the c1 assignment.

Freeze all but a window W of moduli; re-solve the window EXACTLY with
CP-SAT over the free primes (those uncovered by the frozen part);
accept improvements; rotate windows. Gate: does anything beat |U|=867?

Usage: d11_lns.py [n_windows] [window_size] [seed] [time_cap_s]
State: best assignment persisted to d11_best.json (resumable).
"""
import json
import os
import sys
import time

import numpy as np
from ortools.sat.python import cp_model
from sympy import primerange

HERE = os.path.dirname(os.path.abspath(__file__))
INST = json.load(open(os.path.join(HERE, 'instance_q122k.json')))
BEST = os.path.join(HERE, 'd11_best.json')
Q = INST['Q']
moduli = [int(r) for r in INST['moduli']]
P = np.array(list(primerange(3, Q)), dtype=np.int64)
RES = {r: (P % r).astype(np.int32) for r in moduli}


def ucount(assign):
    cc = np.zeros(len(P), dtype=np.int16)
    for r in moduli:
        cc += (RES[r] == assign[r])
    return int((cc == 0).sum()), cc


def stability_order(assign, cc):
    gaps = []
    for r in moduli:
        m = RES[r] == assign[r]
        cc2 = cc - m
        hist = np.bincount(RES[r][cc2 == 0], minlength=r)
        cur = hist[assign[r]]
        hist[assign[r]] = -1
        gaps.append((int(cur - hist.max()), r))
    gaps.sort()
    return [r for _, r in gaps]


def solve_window(assign, W, time_cap):
    cc = np.zeros(len(P), dtype=np.int16)
    for r in moduli:
        if r not in W:
            cc += (RES[r] == assign[r])
    free = np.nonzero(cc == 0)[0]
    m = cp_model.CpModel()
    x = {}
    for r in W:
        xs = [m.NewBoolVar(f'x{r}_{a}') for a in range(r)]
        m.AddExactlyOne(xs)
        x[r] = xs
    z = [m.NewBoolVar(f'z{j}') for j in range(len(free))]
    for i, j in enumerate(free):
        m.AddBoolOr([x[r][int(RES[r][j])] for r in W] + [z[i].Not()])
    m.Maximize(sum(z))
    # incumbent coverage as a hard floor: solver can only match or improve
    inc_cov = 0
    for j in free:
        if any(RES[r][j] == assign[r] for r in W):
            inc_cov += 1
    m.Add(sum(z) >= inc_cov)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_cap
    sol.parameters.num_search_workers = 4
    for r in W:
        for a in range(r):
            m.AddHint(x[r][a], 1 if a == assign[r] else 0)
    st = sol.Solve(m)
    covered = int(sol.ObjectiveValue()) if st in (cp_model.OPTIMAL,
                                                  cp_model.FEASIBLE) else -1
    newU = len(free) - covered
    opt = st == cp_model.OPTIMAL
    if covered >= 0:
        na = dict(assign)
        for r in W:
            for a in range(r):
                if sol.Value(x[r][a]):
                    na[r] = a
                    break
        return na, newU, opt
    return assign, 10**9, False


def main():
    nwin = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    wsize = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    cap = float(sys.argv[4]) if len(sys.argv) > 4 else 25.0
    rng = np.random.default_rng(seed)
    if os.path.exists(BEST):
        assign = {int(r): int(a) for r, a in json.load(open(BEST)).items()}
    else:
        assign = {int(r): int(a) for r, a in INST['c1_assignment'].items()}
    u, cc = ucount(assign)
    print(f"start |U|={u}", flush=True)
    tight = stability_order(assign, cc)
    t0 = time.time()
    chunk = 0
    for w in range(nwin):
        if w % 3 == 0:                              # rotate tight chunks
            W = tight[chunk * wsize:(chunk + 1) * wsize]
            chunk = (chunk + 1) % max(1, len(tight) // wsize)
            if len(W) < wsize:
                W = tight[:wsize]
        elif w % 3 == 1:
            W = list(rng.choice(tight[:40], size=wsize, replace=False))
        else:
            W = list(rng.choice(moduli, size=wsize, replace=False))
        W = [int(r) for r in W]
        na, nu, opt = solve_window(assign, W, cap)
        u2, cc2 = ucount(na)
        tag = 'OPT' if opt else 'feas'
        if u2 < u:
            print(f"  win{w} [{tag}] IMPROVED: {u} -> {u2} "
                  f"(window {sorted(W)[:5]}...)", flush=True)
            assign, u, cc = na, u2, cc2
            tight = stability_order(assign, cc)
            json.dump({str(r): a for r, a in assign.items()},
                      open(BEST, 'w'))
        else:
            print(f"  win{w} [{tag}] no gain (window best {u2})", flush=True)
    print(f"final |U|={u} after {nwin} windows in {time.time()-t0:.0f}s",
          flush=True)
    json.dump({str(r): a for r, a in assign.items()}, open(BEST, 'w'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
