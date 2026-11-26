#!/usr/bin/env python3
# python3 carry_refit.py   (CARRY_NEW=251904 for keep 0.75%)
"""Refit of the carry-over prediction on the GPU session's time_launch (gold-g4j, 19:40Z, s29_asm): t_min 1.499 ms, R 24.87M tests/s, 1.27x at T = 1e5.
Kernel time of a launch of T tests: t(T) = max(t_min, T/R (1 + a min(1, (W/T)^2))), W = one wave (188 SMs x 5 CTAs x 128 threads), a = 0.27 (fits all 7 points to 1.5%).
Production half-pool dynamics simulated as carry_sim.py (p 0.0714, target 2^18 a half, dmax 8, 423 rows); the two halves' rounds taken as concurrent (both start together):
a round's GPU time = t(2 T_i); its idle capacity = t(2 T_i) - 2 T_i / R (what the sieve or nothing fills)."""
import numpy as np, os
rng = np.random.default_rng(1)
t_min, R, W, a = 1.499e-3, 24.87e6, 188 * 5 * 128, 0.27
meas = [(8, 1.499), (1000, 1.501), (10000, 1.501), (100000, 5.116), (524288, 21.339), (1048576, 42.326), (2097152, 84.318)]
t = lambda T: max(t_min, T / R * (1 + a * min(1.0, (W / T) ** 2)))
print("model against time_launch:", "  ".join(f"{T}: {1e3 * t(T):.3f}/{m:.3f}" for T, m in meas))
p, target, dmax, CNT = 0.0714, 1 << 18, 8, 423
NEW = int(os.environ.get("CARRY_NEW", "503808"))
def pools(S, npool=14):
    cX = np.zeros(0, np.int64); cP = np.zeros(0, np.int64)
    out = []
    for b in range(npool):
        X = np.concatenate([cX, rng.geometric(p, NEW).astype(np.int64)]); C = np.full(X.size, CNT, np.int64)
        P = np.concatenate([cP, np.zeros(NEW, np.int64)]); act = np.arange(X.size); Ts = []; counted = 0
        last = S == 0 or b == npool - 1
        while act.size:
            if not last and act.size < S:
                break
            D = max(1, min(dmax, target // act.size)); rem = C[act] - P[act]; take = np.minimum(rem, D); T = int(take.sum()); Ts.append(T)
            hit = (X[act] > P[act]) & (X[act] <= P[act] + take)
            counted += int(np.where(hit, X[act] - P[act], take).sum())
            P[act] = np.where(hit, X[act], P[act] + take); done = hit | (P[act] == C[act]); act = act[~done]
        cX, cP = X[act], P[act]
        out.append((Ts, counted))
    return out[4:-1] if S else out[2:]
for S, name in ((0, "production (no carry)"), (131073, "carry-over, stop 131,073")):
    res = pools(S)
    rounds = np.mean([len(Ts) for Ts, _ in res]); comp = np.mean([sum(Ts) for Ts, _ in res]); cnt = np.mean([c for _, c in res])
    gpu = np.mean([sum(t(2 * T) for T in Ts) for Ts, _ in res]); work = 2 * comp / R; idle = gpu - work
    small = np.mean([sum(t(2 * T) - 2 * T / R for T in Ts if 2 * T < 2 * W) for Ts, _ in res])
    print(f"{name:26s}: {rounds:5.1f} rounds a half-pool, computed {comp / 1e6:.3f}M (counted {cnt / 1e6:.3f}M) a half; both halves: kernels {1e3 * gpu:6.1f} ms "
          f"(work at R {1e3 * work:6.1f} ms, idle capacity {1e3 * idle:5.1f} ms, of it in rounds under 2 waves {1e3 * small:5.1f} ms)", flush=True)
