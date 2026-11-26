import subprocess, re, sys, math, os, numpy as np
nm = sys.argv[1]; X = sys.argv[2]; Q = sys.argv[3]; kmaxs = [int(v) for v in sys.argv[4].split(',')]; Js = [int(v) for v in sys.argv[5].split(',')]; cmins = [int(v) for v in sys.argv[6].split(',')]
# population stream (cover-first by k1) from the per-k1 counts of this miniature
from lib import *
m = Mini(nm); k1 = np.asarray(m.k[:, 0]).astype(np.int64); s = np.asarray(m.s)
cnt = np.bincount(k1, minlength=64).astype(float); obs = np.bincount(k1[s == 1], minlength=64).astype(float)
cumn = np.cumsum(cnt); cums = np.cumsum(obs)
def S_at(n): return np.interp(n, np.concatenate([[0], cumn]), np.concatenate([[0], cums]))
for kmax in kmaxs:
    for J in Js:
        for cmin in cmins:
            r = subprocess.run(['./nbr3', X, Q, str(kmax), str(J), str(cmin), '1000'], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='2')).stdout
            n_stream = int(re.search(r'members (\d+)', r).group(1)); S = int(re.search(r'successes (\d+)', r).group(1)); nsh = int(re.search(r'shifts available (\d+)', r).group(1))
            seeds = scans = outside = inside = 0
            for line in r.splitlines()[1:]:
                mm = re.search(r'seeds (\d+) scans (\d+) succ_outside_stream (\d+) succ_inside_stream (\d+)', line)
                if mm: a, b, c, d = map(int, mm.groups()); seeds += a; scans += b; outside += c; inside += d
            S_ext = S_at(n_stream + scans) - S_at(n_stream); gain = math.log((S + outside) / (S + S_ext)) if S > 0 else float('nan')
            print(f'{nm} kmax={kmax} J<={J} cmin={cmin} ({nsh} shifts): stream {n_stream} members, {S} succ; seeds {seeds}, scans {scans} (+{100 * scans / n_stream:.0f}% work), new succ outside stream {outside}; stream extension at equal work adds {S_ext:.1f}; net {gain:+.3f} nats', flush=True)
