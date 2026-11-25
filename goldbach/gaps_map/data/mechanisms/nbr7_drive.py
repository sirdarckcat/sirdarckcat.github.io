import subprocess, re, sys, math, os, numpy as np
from lib import *
nm, X, Q, cmin = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
SIEVE = 1 / 139.0     # one member sieved to depth 199 = 1 unit = 1/139 modexp
def run(kmax, theta, thf):
    r = subprocess.run(['./nbr7', X, Q, str(kmax), str(theta), '99', cmin, '1000', str(thf)], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='4')).stdout
    g = re.search(r'STREAM (\d+) VERIFIED (\d+) SUCC (\d+) CAND (\d+) VERIFYTESTS (\d+) SEEDS (\d+) SCANS (\d+) FOUND (\d+)', r)
    st, ver, S, cand, vt, seeds, scans, found = map(int, g.groups())
    cost = st * SIEVE + (ver - cand) * 2.2 + vt + scans * (2.2 + SIEVE)
    return dict(stream=st, ver=ver, cand=cand, S=S + found, S_stream=S, scans=scans, cost=cost)
# funnel baselines: no seeds (theta = 0), verify members with k199 <= thf, several prefixes
F = {}
for thf in (18, 20, 22, 99):
    pts = []
    for kmax in (28, 29, 30, 31, 32, 33):
        r = run(kmax, 0, thf); pts.append((r['S'], r['cost']))
    F[thf] = pts; print('funnel baseline thf', thf, [(s, round(c / 1e6, 2)) for s, c in pts], flush=True)
def F_cost(S):
    best = float('inf')
    for pts in F.values():
        xs = np.log([p[0] for p in pts]); ys = np.log([p[1] for p in pts])
        if S < pts[0][0] or S > pts[-1][0]: continue
        best = min(best, math.exp(np.interp(math.log(S), xs, ys)))
    return best
for kmax, theta, thf in [(30, 14, 18), (30, 16, 18), (30, 16, 20), (30, 18, 20), (30, 16, 22), (30, 18, 22), (29, 16, 20), (31, 16, 20), (31, 18, 20), (29, 18, 20)]:
    r = run(kmax, theta, thf); fc = F_cost(r['S'])
    print(f'{nm} kmax={kmax} seeds k199<={theta}, verify k199<={thf}: stream {r["stream"]}, verified {r["ver"]} (seed candidates {r["cand"]}), scans {r["scans"]}, successes {r["S_stream"]} + {r["S"] - r["S_stream"]} = {r["S"]}; cost {r["cost"] / 1e6:.2f}M tests; best funnel-only at equal successes {fc / 1e6:.2f}M -> gain {math.log(fc / r["cost"]):+.2f} nats', flush=True)
