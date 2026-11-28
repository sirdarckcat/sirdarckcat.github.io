"""The Fermat rounds of search_gpu5.run_pool (D = max(1, min(dmax, rem.max(), target // active)) rows a member a launch), simulated with
geometric first-PRP positions, against a carried pool (members that are not finished join the next pool's launches).
Kernel time model: a launch of T tests takes max(T / R, t_min) seconds plus a gap g (host bookkeeping)."""
import numpy as np
rng = np.random.default_rng(1)
def run_pool(cnt, firstprp, target, dmax=8):
    n = len(cnt); pos = np.zeros(n, np.int64); act = np.nonzero(cnt > 0)[0]
    launches = []; counted = 0
    while act.size:
        rem = cnt[act] - pos[act]
        D = int(max(1, min(dmax, rem.max(), target // act.size)))
        take = np.minimum(rem, D)
        T = int(take.sum())
        fp = firstprp[act] - pos[act]                 # offset of the first PRP from this launch's first row
        hit = fp < take
        counted += int(np.where(hit, fp + 1, take).sum())
        launches.append(T)
        pos[act] += take
        done = (~hit) & (pos[act] >= cnt[act])
        act = act[(~hit) & (~done)]
    return np.array(launches), counted
def times(L, R, tmin, g):
    return (np.maximum(L / R, tmin) + g).sum(), np.maximum(L / R, tmin).sum()
p, n, a = 0.0715, 2015232, 423
cnt = np.full(n, a)
firstprp = rng.geometric(p, n) - 1                     # offset of the first PRP row; >= cnt: no PRP (a success)
L, counted = run_pool(cnt, firstprp, 1 << 20)
print(f"pool {n} members, {a} rows, p {p}: {len(L)} launches, {L.sum()} tests computed, {counted} counted, waste {100 * (1 - counted / L.sum()):.1f}%")
print("launch sizes:", " ".join(str(x) for x in L[:3]), "...", " ".join(str(x) for x in L[-12:]))
R = 24.6e6
for tmin in (0.0, 0.002, 0.004, 0.008):
    for g in (0.0022,):
        tw, tk = times(L, R, tmin, g)
        print(f"  t_min {tmin * 1e3:.0f} ms, gap {g * 1e3:.1f} ms: kernels {tk:.3f} s ({L.sum() / tk / 1e6:.1f}M tests/s while a kernel runs), wall {tw:.3f} s "
              f"({counted / tw / 1e6:.1f}M counted tests/s)")
# carried: every launch is a full target of single-row tests (D = 1: no waste), the unfinished members carry over
nl = counted / (1 << 20)
for tmin in (0.0, 0.002, 0.004, 0.008):
    tw = nl * (max((1 << 20) / R, tmin) + 0.0022)
    print(f"  carried, t_min {tmin * 1e3:.0f} ms: {nl:.1f} launches of 2^20, wall {tw:.3f} s ({counted / tw / 1e6:.1f}M counted tests/s)")
