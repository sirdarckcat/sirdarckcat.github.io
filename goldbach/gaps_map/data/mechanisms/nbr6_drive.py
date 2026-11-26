import subprocess, re, sys, math, os, numpy as np
from lib import *
nm, X, Q = sys.argv[1], sys.argv[2], sys.argv[3]; kmaxs = [int(v) for v in sys.argv[4].split(',')]; thetas = [int(v) for v in sys.argv[5].split(',')]; Js = [int(v) for v in sys.argv[6].split(',')]; cmins = [int(v) for v in sys.argv[7].split(',')]
m = Mini(nm); k1 = np.asarray(m.k[:, 0]).astype(np.int64); s = np.asarray(m.s)
cnt = np.bincount(k1, minlength=64).astype(float); obs = np.bincount(k1[s == 1], minlength=64).astype(float); msk = cnt > 0
def E_base(S): return cost_levels(cnt[msk], obs[msk].astype(np.int64), targets=(S,))[S]
for kmax in kmaxs:
    for theta in thetas:
        for J in Js:
            for cmin in cmins:
                r = subprocess.run(['./nbr6', X, Q, str(kmax), str(theta), str(J), str(cmin), '1000'], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='4')).stdout
                g = re.search(r'STREAM (\d+) SUCC (\d+) CAND (\d+) VERIFYTESTS (\d+) SEEDS (\d+) SCANS (\d+) FOUND (\d+)', r)
                st, S, cand, vt, seeds, scans, found = map(int, g.groups()); Sp = S + found
                if Sp > obs.sum(): continue
                eb = E_base(int(Sp)); units = st + scans; gA = math.log(eb / units)
                costV = (st - cand) * 2.2 + vt + scans * 2.2; gV = math.log(eb * 2.2 / costV)
                print(f'{nm} kmax={kmax} theta={theta} J<={J} cmin={cmin}: stream {st}, seed candidates (k199<=theta) {cand} ({100 * cand / st:.1f}%), seeds {seeds}, scans {scans}, successes {S}+{found}={Sp}; (A) gain {gA:+.2f}; (V) cost {costV / 1e6:.1f}M vs cover-first {eb * 2.2 / 1e6:.1f}M -> (V) gain {gV:+.2f}', flush=True)
