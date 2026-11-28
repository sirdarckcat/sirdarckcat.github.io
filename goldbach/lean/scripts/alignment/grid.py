"""Runs tiny.c on a grid of small instances and tabulates, by the number of primes beyond the line:
  OPT          the true optimum below X;
  D            the best cover on the same primes with no bound on N (when enumerable);
  scan         the least score over the members of the best cells (pinning plus a full scan of the window);
  mean         the mean score over those members (pinning, no choice inside the window);
  depth        how many cells, in cover-first order, are at least as good as the best cell holding a true optimum."""
import subprocess, sys, json
PR = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
def run(Q, lidx, w, extra=4, full=None):
    M = 2
    for p in PR[:lidx]: M *= p
    X = M * w; k = lidx + extra
    fullj = full if full is not None else 0
    out = subprocess.run(["./tiny", str(Q), str(X), str(k), str(fullj)], capture_output=True, text=True, check=True).stdout.splitlines()
    head = out[0]; best = out[1]; rows = []
    for line in out[3:]:
        t = [x.strip() for x in line.split("|")]
        if t[1] == "-": continue
        rows.append({"prime": int(t[0]), "beyond": int(t[1]), "opt": int(t[2].split()[0]), "nopt": int(t[2].split("(")[1].rstrip(")")), "D": (int(t[3]) if t[3] != "?" else None),
                     "scan": int(t[4]), "mean": float(t[5]), "worst": int(t[6]), "dopt": int(t[7]), "cells": float(t[8]), "members": int(t[9])})
    Dl = int(best.split("=")[1].split(":")[0]); ncells = float(best.split("=")[2].split()[0])
    return {"Q": Q, "line": PR[lidx - 1], "w": w, "X": X, "Dl": Dl, "best_cells": ncells, "rows": rows}
res = []
for Q in (200, 300, 500, 1000):
    for lidx in (4, 5, 6, 7, 8):                       # line after 11, 13, 17, 19, 23
        nxt = PR[lidx]
        for w in sorted(set([2, 4, 8, nxt - 1])):
            if w >= nxt: continue
            M = 2
            for p in PR[:lidx]: M *= p
            if M * w > 2.5e9: continue
            fullj = lidx + (2 if lidx <= 5 else (1 if lidx <= 7 else 0))      # full torus where it is below about 1e10 class vectors
            r = run(Q, lidx, w, 4, fullj); res.append(r)
            print(f"Q={Q} line={r['line']} window={w} X={r['X']:,d} D_l={r['Dl']} best cells={r['best_cells']:.1f}: " +
                  "; ".join(f"+{x['beyond']} ({x['prime']}): OPT {x['opt']} D {x['D']} scan {x['scan']} mean {x['mean']:.2f} cell of optimum {x['dopt']} ({x['cells']:.0f} cells)" for x in r["rows"]), flush=True)
json.dump(res, open("grid.json", "w"))
