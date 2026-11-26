#!/usr/bin/env python3
"""On a paused GPU: the production Fermat kernel timed on launches of T tests, to pin the launch constant of the round model
(g200k/costside/tail.py: a launch of T tests costs max(T / R, t_min) of kernel time, R = the kernel's full rate).

    python3 time_launch.py [--variant s1r_asm|s1rw|s29_asm|s29w] [--sizes 8 1000 10000 100000 524288 1048576 2097152] [--reps 20]

Kernel time only (cuda events around one launch), best and median of --reps launches for each T, on T random rows of a synthetic pool (661-bit odd numbers
with no prime factor below 20,000, as bench_persist.py).  Also the wall time of one launch followed by a stream synchronize, for the host's share of a round.
Prints, per T: kernel ms, tests/s, and the time a test would take at the full rate; then t_min (the smallest T's kernel time) and R (the largest T's rate),
and the model's prediction for every T so that the two can be compared line by line."""
import argparse, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main(argv=None, cp=None):
    if cp is None:
        import cupy as cp                                                        # noqa: F811
    import gpu_fermat28 as g28
    from bench_persist import VARIANTS, make_rows
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="s1r_asm", choices=sorted(VARIANTS))
    ap.add_argument("--sizes", type=int, nargs="+", default=[8, 1000, 10000, 100000, 1 << 19, 1 << 20, 1 << 21])
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--rows", type=int, default=20000)
    ap.add_argument("--threads", type=int, default=128)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    try:
        name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    except Exception:
        name = "?"
    rows = make_rows(a.rows, 20000, a.seed)
    CQ = cp.asarray(np.stack([g28.to_limbs(int(n)) for n in rows]))
    M = cp.zeros(21, dtype=cp.uint32)
    k = g28.kernel(21, **VARIANTS[a.variant])
    rng = np.random.default_rng(a.seed)
    print(f"device {name}, variant {a.variant}, {a.threads} threads a CTA, {a.rows} distinct rows; best / median of {a.reps} launches", flush=True)
    res = []
    for T in a.sizes:
        idx = cp.asarray(rng.integers(0, a.rows, T).astype(np.int32))
        kz = cp.zeros(T, dtype=cp.uint32)
        out = cp.empty(T, dtype=cp.uint8)
        grid = ((T + a.threads - 1) // a.threads,)
        launch = lambda: k(grid, (a.threads,), (CQ, M, idx, kz, out, np.int32(T)))
        launch()                                                                 # compile (first T) + warm up
        cp.cuda.Device().synchronize()
        ks, ws = [], []
        for _ in range(a.reps):
            e0, e1 = cp.cuda.Event(), cp.cuda.Event()
            t0 = time.perf_counter()
            e0.record()
            launch()
            e1.record()
            e1.synchronize()
            ws.append(1e3 * (time.perf_counter() - t0))
            ks.append(cp.cuda.get_elapsed_time(e0, e1))
        kb, km, wm = min(ks), float(np.median(ks)), float(np.median(ws))
        res.append((T, kb, km, wm))
        print(f"  T = {T:8d}: kernel {kb:9.3f} ms best, {km:9.3f} median; launch + sync {wm:9.3f} ms median; {T / kb / 1e3:8.3f}M tests/s", flush=True)
    t_min = res[0][1]
    R = res[-1][0] / res[-1][1] * 1e3                                           # tests a second at the largest T
    print(f"t_min (kernel time of the smallest launch) = {t_min:.3f} ms; R (rate of the largest) = {R / 1e6:.2f}M tests/s", flush=True)
    for T, kb, km, wm in res:
        pred = max(T / R * 1e3, t_min)
        print(f"  T = {T:8d}: measured {kb:9.3f} ms, model max(T / R, t_min) {pred:9.3f} ms ({kb / pred:.2f}x)", flush=True)
    print("TIME-LAUNCH-DONE", flush=True)
    return res


if __name__ == "__main__":
    main()
