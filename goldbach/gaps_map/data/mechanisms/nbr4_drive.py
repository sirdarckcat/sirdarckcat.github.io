import subprocess, re, sys, math, os, numpy as np
from lib import *
nm, X, Q = sys.argv[1], sys.argv[2], sys.argv[3]; kmaxs = [int(v) for v in sys.argv[4].split(',')]; Js = [int(v) for v in sys.argv[5].split(',')]; cmins = [int(v) for v in sys.argv[6].split(',')]
m = Mini(nm); k1 = np.asarray(m.k[:, 0]).astype(np.int64); s = np.asarray(m.s)
cnt = np.bincount(k1, minlength=64).astype(float); obs = np.bincount(k1[s == 1], minlength=64).astype(float)
msk = cnt > 0
def E_base(S):
    lv = cost_levels(cnt[msk], obs[msk].astype(np.int64), targets=(S,)); return lv[S]
res = []
for kmax in kmaxs:
    for J in Js:
        for cmin in cmins:
            r = subprocess.run(['./nbr4', X, Q, str(kmax), str(J), str(cmin), '1000'], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='3')).stdout
            n_stream = int(re.search(r'members (\d+)', r).group(1)); S = int(re.search(r'successes (\d+)', r).group(1))
            seeds = scans = found = 0
            for line in r.splitlines()[1:]:
                mm = re.search(r'seeds (\d+) scans (\d+) succ_outside_stream (\d+)', line)
                if mm: a, b, c = map(int, mm.groups()); seeds += a; scans += b; found += c
            Sp = S + found; C = n_stream + scans
            eb = E_base(int(Sp)) if Sp <= obs.sum() else float('nan')
            print(f'{nm} kmax={kmax} J<={J} cmin={cmin}: stream {n_stream} (+{scans} neighbour scans = {C} units), successes {S} + {found} = {Sp}; cover-first needs {eb:.0f} units for {Sp} -> gain {math.log(eb / C):+.2f} nats', flush=True)
