# Item 2 (research, 25 Nov): carrying a member's unfinished rows from one test pool to the next. A model written from the round
# rule alone (not from uarch's tail.py / carry_sim.py): a pool of P kept members; member i needs X_i tests to reach its first
# probable prime, X_i geometric with p = 1/mean (each surviving row prime with probability p'); a launch gives every active member
# D = max(1, min(dmax, rows left, floor(T / active))) tests; tests after a member's first PRP within a launch are wasted.
# A launch costs max(tests / R, t_min) + gap.  Without carry-over a pool runs until its last member is decided; with carry-over
# (stop at T active members) the undecided members join the next pool, so in the steady state every launch has D = 1 (no waste)
# and no launch is small.  Exact expected-value recursion over the active count (a member's remaining need is geometric whatever
# it has done, so the active count is a sum of independent Bernoullis per round); Monte Carlo of the same rule as a check.
#   python3 item2_carry.py
import math
import numpy as np

R = 24.6e6; GAP = 2.2e-3; TMIN = 4e-3; DMAX = 8; ROWS = 423

def pool_no_carry(P, T, p, tmin=TMIN, gap=GAP, mc=False, rng=None):
    """expected computed tests, useful tests, launches, time of one pool run to completion."""
    q = 1 - p
    if mc:
        X = rng.geometric(p, size=P); X = np.minimum(X, ROWS); left = X.copy(); done_rows = np.zeros(P, int)
        active = np.ones(P, bool); comp = use = 0; launches = 0; time = 0.0
        while active.any():
            A = int(active.sum()); D = max(1, min(DMAX, T // A))
            idx = np.nonzero(active)[0]; rows_left = ROWS - done_rows[idx]; d = np.minimum(D, rows_left)
            fin = left[idx] <= d
            comp += int(d.sum()); use += int(np.where(fin, left[idx], d).sum())
            left[idx] -= d; done_rows[idx] += d; active[idx[fin | (done_rows[idx] >= ROWS)]] = False
            launches += 1; time += max(d.sum() / R, tmin) + gap
        return comp, use, launches, time
    A = float(P); comp = use = 0.0; launches = 0; time = 0.0
    while A >= 0.5:
        D = max(1, min(DMAX, int(T // A)))
        # each active member: computed D, useful E[min(X', D)] = (1 - q^D)/p, finishes with probability 1 - q^D
        comp += A * D; use += A * (1 - q ** D) / p
        launches += 1; time += max(A * D / R, tmin) + gap
        A *= q ** D
    return comp, use, launches, time

def pool_carry(P, T, p, gap=GAP):
    """steady state with carry-over and stop at T: launches of D = 1 over P + C active, C the carried members (= T)."""
    q = 1 - p
    use = P / p                                   # every member's tests count
    A0 = P + T                                    # new members plus the carried ones
    launches = math.log(A0 / T) / -math.log(q)    # rounds of D = 1 until the active count is down to T
    time = use / R + launches * gap
    return use, use, launches, time

if __name__ == "__main__":
    rng = np.random.default_rng(1)
    print("check of the recursion against a Monte Carlo of the same rule (P = 503,808, T = 2^18, p = 0.0715):")
    for mc in (False, True):
        c, u, L, t = pool_no_carry(503808, 2 ** 18, 0.0715, mc=mc, rng=rng)
        print(f"  {'Monte Carlo' if mc else 'recursion  '}: computed {c / 1e6:.3f}M, useful {u / 1e6:.3f}M, waste {100 * (c - u) / c:.2f}%, launches {L:.0f}, time {t:.3f} s")
    print()
    print("gain in tests that count per second from carry-over, by pool size P (kept members a pool) and mean tests a member (1/p);")
    print("target T = 2^18 a launch; columns: waste without carry-over | launches without / with | gain with gaps 2.2 ms and t_min 4 ms | gaps hidden, t_min 4 ms | gaps hidden, t_min 0 (waste only)")
    for mean in (10, 14, 20):
        p = 1 / mean
        for P in (125952, 251904, 503808, 1007616, 2015232):
            c, u, L, t = pool_no_carry(P, 2 ** 18, p)
            _, _, Lc, tc = pool_carry(P, 2 ** 18, p)
            _, _, _, t_h = pool_no_carry(P, 2 ** 18, p, gap=0.0)
            _, _, _, tc_h = pool_carry(P, 2 ** 18, p, gap=0.0)
            _, _, _, t_0 = pool_no_carry(P, 2 ** 18, p, gap=0.0, tmin=0.0)
            print(f"  mean {mean}, P = {P:>9,} (P/T = {P / 2 ** 18:.2f}): waste {100 * (c - u) / c:5.2f}% | launches {L:3d} / {Lc:4.1f} | "
                  f"+{100 * (t / tc - 1):5.1f}% | +{100 * (t_h / tc_h - 1):5.1f}% | +{100 * (t_0 / tc_h - 1):5.1f}%")
    print()
    print("the full pool of uarch's first model (P = 2,015,232, T = 2^20, p = 0.0715):")
    c, u, L, t = pool_no_carry(2015232, 2 ** 20, 0.0715); _, _, Lc, tc = pool_carry(2015232, 2 ** 20, 0.0715)
    print(f"  without: computed {c / 1e6:.2f}M, waste {100 * (c - u) / c:.2f}%, {L} launches, {t:.3f} s ({u / t / 1e6:.1f}M counted tests/s); "
          f"with: {Lc:.1f} launches, {tc:.3f} s ({u / tc / 1e6:.1f}M/s): +{100 * (t / tc - 1):.1f}%")
