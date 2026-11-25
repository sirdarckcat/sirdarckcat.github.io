import subprocess, re, sys, math, os, numpy as np
from lib import cost_levels
CS, CNB = 1.667, 0.96     # stream / neighbour calibration constants fixed at Q=1000 (assumption when extrapolating)
def run(X, Q, kmax, J, cmin, H=1000):
    fn = f'nbr5_{X}_{Q}_{kmax}_{J}_{cmin}.out'
    if not os.path.exists(fn):
        out = subprocess.run(['./nbr5w', str(X), str(Q), str(kmax), str(J), str(cmin), str(H), '0.5'], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='4')).stdout
        open(fn, 'w').write(out)
    return open(fn).read()
def parse(out):
    g = re.search(r'STREAM (\d+) SUCC (\d+) SEEDS (\d+) SCANS (\d+) NBOBS (\d+) STREAMMASS (\S+) NBMASS (\S+) NSHIFTS (\d+)', out)
    st, su, sd, sc, nbo, sm, nm, nsh = int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]), float(g[6]), float(g[7]), int(g[8])
    pop = {int(a): (int(b), float(c)) for a, b, c in re.findall(r'POP (\d+) (\d+) (\S+)', out)}
    return st, su, sd, sc, nbo, sm, nm, nsh, pop
def gain(X, Q, kmax, J, cmin, cnb=CNB):
    st, su, sd, sc, nbo, sm, nm, nsh, pop = parse(run(X, Q, kmax, J, cmin))
    ks = sorted(pop); n = np.array([pop[k][0] for k in ks], float); ms = np.array([CS * pop[k][1] for k in ks])
    Sp = CS * sm + cnb * nm; C = st + sc
    try: eb = cost_levels(n, ms, targets=(Sp,))[Sp]
    except Exception: eb = float('nan')
    return dict(stream=st, seeds=sd, scans=sc, units=C, Sp=Sp, S_stream_pred=CS * sm, S_nb_pred=cnb * nm, observed_stream=su, observed_nb=nbo, base=eb, gain=math.log(eb / C) if eb == eb else float('nan'), total_mass=ms.sum(), nsh=nsh, pop=(ks, n))
if __name__ == '__main__':
    X = int(sys.argv[1]); Q = int(sys.argv[2]); J = int(sys.argv[3]); cmin = int(sys.argv[4]); kmaxs = [int(v) for v in sys.argv[5].split(',')]
    for kmax in kmaxs:
        r = gain(X, Q, kmax, J, cmin)
        print(f'X={X} Q={Q} kmax={kmax} J<={J} cmin={cmin} ({r["nsh"]} shifts): stream {r["stream"]} + scans {r["scans"]} = {r["units"]} units; predicted successes stream {r["S_stream_pred"]:.1f} (obs {r["observed_stream"]}) + neighbours {r["S_nb_pred"]:.1f} (obs {r["observed_nb"]}) = {r["Sp"]:.1f}; cover-first needs {r["base"]:.0f} -> model gain {r["gain"]:+.2f} nats  (population predicted total {r["total_mass"]:.0f})', flush=True)
