import subprocess, re, sys, math, os, numpy as np
P = np.load('pop_A.npz'); cnt = P['cnt'].astype(float); obs = P['obs'].astype(float)
cumn = np.cumsum(cnt); cums = np.cumsum(obs)
def S_at(n):   # successes in the first n members of the cover-first stream (interpolated)
    return np.interp(n, np.concatenate([[0], cumn]), np.concatenate([[0], cums]))
out = open('nbr2_results.txt', 'w')
for kmax in (28, 30):
    for J, topm in ((2, 0), (4, 60), (6, 60), (8, 40)):
        r = subprocess.run(['./nbr2', '1000000000', '1000', str(kmax), str(J), '1000', str(topm)], capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='2')).stdout
        n_stream = int(re.search(r'members (\d+)', r).group(1)); S = int(re.search(r'successes (\d+)', r).group(1))
        seeds = scans = outside = inside = 0
        for line in r.splitlines()[1:]:
            m = re.search(r'seeds (\d+) scans (\d+) succ_outside_stream (\d+) succ_inside_stream (\d+)', line)
            if m: a, b, c, d = map(int, m.groups()); seeds += a; scans += b; outside += c; inside += d
        S_ext = S_at(n_stream + scans) - S_at(n_stream)       # successes from extending the stream by the same number of members
        gain = math.log((S + outside) / (S + S_ext)) if S > 0 else float('nan')
        line = f'kmax={kmax} J<={J} shifts={"all" if topm == 0 else "top%d" % topm}: stream {n_stream} members, {S} succ; seeds {seeds}, scans {scans} (+{100 * scans / n_stream:.0f}% work), new successes found outside stream {outside} (inside {inside}); stream-extension at equal work would add {S_ext:.1f}; net gain {gain:+.3f} nats'
        print(line, flush=True); out.write(line + '\n'); out.flush()
