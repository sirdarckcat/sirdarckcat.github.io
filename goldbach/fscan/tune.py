#!/usr/bin/env python3
"""Expected successes per core-second for a grid of (L, theta, Ta) on one slice of one residual class.

    python3 tune.py R slice Xmax "L:theta,theta,...:Ta,Ta,..." ...
"""
import subprocess, sys, time, resource
R, sl, X = sys.argv[1], sys.argv[2], sys.argv[3]
best = None
for spec in sys.argv[4:]:
    L, ths, tas = spec.split(":")
    for th in ths.split(","):
        for ta in tas.split(","):
            r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
            out = subprocess.run(["./fscan", "10007", L, R, R, "4e18", X, th, ta, f"rref={R}", f"slice={sl}", "sample=10", "threads=1"],
                                 capture_output=True, text=True, check=True).stdout
            r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu = r1.ru_utime - r0.ru_utime
            st = dict(kv.split("=") for kv in out.strip().splitlines()[-1].split(" | ")[1].split())
            e, m, mem = float(st["expected"]), float(st["mass_all"]), int(st["members"])
            eff = e / cpu
            line = (f"L={L:>4} theta={th:>3} Ta={ta:>3}: {cpu:6.2f}s  {cpu * 2.3e9 / mem:5.2f} cyc/member  sel {100 * int(st['selected']) / mem:.3f}% "
                    f"kept {100 * int(st['kept']) / mem:.3f}%  share {100 * e / m:5.2f}%  expected/core-s {eff:.3e}")
            print(line, flush=True)
            if best is None or eff > best[0]:
                best = (eff, line)
print("best:", best[1])
