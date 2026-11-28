#!/usr/bin/env python3
# python3 carry_sim.py 32768 65536 131072 262144   (the stop thresholds; 0 = no carry-over is always run first)
"""Half-pool round dynamics of fround.run_pool_fused at production settings, with and without carry-over (stop_below = S):
per member a first-PRP position X ~ Geometric(p) (success if X > cnt); per round D = clamp(target // nact, 1, dmax), take = min(D, rem).
Steady state over pools: rounds, tests computed / counted (waste), launches under target/2 and under 2^16, carried members and rows, and the
deferral of the slice lines (pools until the last member of a slice is decided; two slices a half-pool)."""
import numpy as np, sys
rng = np.random.default_rng(1)
import os
p, target, dmax, CNT = 0.0714, 1 << 18, 8, 423
NEW = int(os.environ.get("CARRY_NEW", "503808"))      # kept members a half-pool a batch (keep 1.5%: 503,808; 0.75%: 251,904)
NP = 14
def run(S):
    # carried state: X (first-PRP pos), cnt, pos, slice id
    cX = np.zeros(0, np.int64); cC = np.zeros(0, np.int64); cP = np.zeros(0, np.int64); cS = np.zeros(0, np.int64)
    out = []
    finish_pool = {}          # slice -> last pool in which one of its members was decided
    for b in range(NP):
        X = rng.geometric(p, NEW).astype(np.int64); C = np.full(NEW, CNT, np.int64)
        sl = np.where(np.arange(NEW) < NEW // 2, 2 * b, 2 * b + 1)
        X = np.concatenate([cX, X]); C = np.concatenate([cC, C]); P = np.concatenate([cP, np.zeros(NEW, np.int64)]); SL = np.concatenate([cS, sl])
        act = np.arange(X.size)
        rounds = comp = small = tiny = 0; Tmin = 1 << 62; counted = 0
        last = S == 0 or b == NP - 1
        while act.size:
            nact = act.size
            if not last and nact < S:
                break
            D = max(1, min(dmax, target // nact))
            rem = C[act] - P[act]
            take = np.minimum(rem, D)
            T = int(take.sum())
            rounds += 1; comp += T; Tmin = min(Tmin, T); small += T < target // 2; tiny += T < (1 << 16)
            # a PRP inside this block?  X in (P, P + take]
            hit = (X[act] > P[act]) & (X[act] <= P[act] + take)
            counted += int(np.where(hit, X[act] - P[act], take).sum())
            P[act] = np.where(hit, X[act], P[act] + take)
            done = hit | (P[act] == C[act])
            for s in np.unique(SL[act[done]]):
                finish_pool[int(s)] = b
            act = act[~done]
        cX, cC, cP, cS = X[act], C[act], P[act], SL[act]
        out.append((rounds, comp, counted, small, tiny, Tmin, act.size, int((C[act] - P[act]).sum())))
    st = out[4:-1] if S else out
    m = np.mean(np.array(st, dtype=float), axis=0)
    defer = [finish_pool[s] - s // 2 for s in range(2 * 4, 2 * (NP - 1))]
    print(f"S = {S:7d}: {m[0]:5.1f} rounds a pool, {m[1] / 1e6:5.3f}M computed, {m[2] / 1e6:5.3f}M counted (waste {100 * (1 - m[2] / m[1]):.2f}%), launches < target/2: {m[3]:4.1f}, < 2^16: {m[4]:4.1f}, "
          f"smallest {int(m[5]):7d}; carried {int(m[6]):7d} members / {m[7] / 1e6:5.2f}M rows; slice lines deferred by {min(defer)}..{max(defer)} batches (mean {np.mean(defer):.2f})", flush=True)
for S in [0] + [int(x) for x in sys.argv[1:]]:
    run(S)
