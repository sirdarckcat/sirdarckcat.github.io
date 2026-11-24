# Wall or run length? For each finished x, run the 4 seeds at the smallest Q that every seed missed, with LONGER runs
# (factor times the sweeps of the search). Runs are logged to t2_runs.jsonl like every other run (resumable), with the
# first sweep at which each reached its best k (ptcover_fast2).   python3 t2_probe.py [factor] [procs] [x ...]
import sys
from concurrent.futures import ThreadPoolExecutor
import t2
from t2_firsthit import finished

if __name__ == "__main__":
    factor = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    only = {int(a) for a in sys.argv[3:]}
    t2.DONE = t2.logged()
    jobs = [(x, hi, s, factor * t2.sweeps_for(x)) for x, (lo, hi) in sorted(finished().items()) if not only or x in only for s in t2.SEEDS]
    with ThreadPoolExecutor(procs) as ex:
        rs = list(ex.map(lambda j: t2.one(*j), jobs))
    for x in sorted({j[0] for j in jobs}):
        R = [r for r, j in zip(rs, jobs) if j[0] == x]
        print(f"x={x} Q={R[0]['Q']} sweeps={R[0]['sweeps']}: best k per seed " +
              ", ".join(f"{r['seed']}: {r['k']} (first at sweep {r.get('first_le', {}).get(r['k'], '?')})" for r in R), flush=True)
