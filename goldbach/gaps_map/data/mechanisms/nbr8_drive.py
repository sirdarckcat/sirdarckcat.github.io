import subprocess, re, sys, math, os, json, numpy as np
nm, X, Q, cmin = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
SIEVE = 1 / 139.0
def run(kmax, theta, thf, thn):
    r = subprocess.run(['./nbr8', X, Q, str(kmax), str(theta), '99', cmin, '1000', str(thf), str(thn)], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='4')).stdout
    g = re.search(r'STREAM (\d+) VERIFIED (\d+) SUCC (\d+) CAND (\d+) VERIFYTESTS (\d+) SEEDS (\d+) SCANS (\d+) FOUND (\d+) VERN (\d+)', r)
    st, ver, S, cand, vt, seeds, scans, found, vern = map(int, g.groups())
    cost = st * SIEVE + (ver - cand) * 2.2 + vt + scans * SIEVE + vern * 2.2
    return dict(stream=st, ver=ver, cand=cand, S=S + found, S_stream=S, scans=scans, vern=vern, cost=cost)
cache = 'nbr8_F_cache.json'
if os.path.exists(cache): F = {int(k): v for k, v in json.load(open(cache)).items()}
else:
    F = {}
    for thf in (16, 18, 20):
        F[thf] = []
        for kmax in (27, 28, 29, 30, 31, 32, 33, 34, 35):
            r = run(kmax, 0, thf, 0); F[thf].append((r['S'], r['cost']))
    json.dump(F, open(cache, 'w'))
for thf, pts in F.items(): print('funnel baseline thf', thf, [(s, round(c / 1e6, 2)) for s, c in pts], flush=True)
def F_cost(S):
    best = float('inf')
    for pts in F.values():
        xs = np.log([max(p[0], 1) for p in pts]); ys = np.log([p[1] for p in pts])
        if S < pts[0][0] or S > pts[-1][0]: continue
        best = min(best, math.exp(np.interp(math.log(S), xs, ys)))
    return best
cfgs = [(30, th, thf, thn) for th in (14, 16, 18) for thf in (18, 20) for thn in (10, 12, 14, 16) if th <= thf] + [(29, 16, 20, 12), (31, 16, 20, 12), (29, 16, 18, 12), (31, 16, 18, 12)]
for kmax, theta, thf, thn in cfgs:
    r = run(kmax, theta, thf, thn); fc = F_cost(r['S'])
    gain = math.log(fc / r['cost']) if fc < float('inf') else float('nan')
    print(f'{nm} kmax={kmax} seeds k199<={theta}, stream verified k199<={thf}, neighbours verified fresh<={thn}: stream {r["stream"]}, verified {r["ver"]}, seeds {r["cand"]}, neighbours sieved {r["scans"]} verified {r["vern"]}; successes {r["S_stream"]} + {r["S"] - r["S_stream"]} = {r["S"]}; cost {r["cost"] / 1e6:.2f}M; funnel-only at equal successes {fc / 1e6:.2f}M -> {gain:+.2f} nats', flush=True)
