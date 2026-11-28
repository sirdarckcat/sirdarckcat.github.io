#!/usr/bin/env python3
"""On a GPU: the deep head (ghead.py) on one real window of a vector, against the same window without it.

    python3 headcheck.py /content/m89_8.json [--klog 24] [--head-b 1000000000] [--head-rows 64] [--rg 32] [--rcta 8] [--tile-threads 512] [--gen-threads 256] [--reps 5] [--verify 8]

What it prints and checks:
  1. the window WITHOUT the head and WITH it (the same DeepSieve, the same k0 = the first 200-digit k of the vector): the kept members, alive_total, hm_all and hm_kept are IDENTICAL (the statistics stay on the B
     sieve); cnt_acc == the old cnt; every member's new row list is a SUBSET of the old one (the same rows, the removed ones missing) and nothing outside the first --head-rows rows is removed; the CSR is consistent;
  2. how many rows the head removed (head rows alive on the B sieve have a prime factor in (B, head-b] with probability 1 - ln B / ln head-b: 11.1% for 1e9) and the predicted fall of the Fermat tests
     (expected tests of a member: (1 - (1-p)^n) / p, with the head rows' higher p / (1 - c));
  3. --verify N: for N removed (member, row) pairs the number N0 - q + k M (a Python integer) has a prime factor in (B, head-b] (numpy over the head primes) and for N kept head rows it has none;
  4. the wall time of a window without and with the head (the cost of the head: the number the +4-6% depends on), the best and the mean of --reps, after a warm-up window each.
The first call builds the head's tables (numpy sieve to head-b: ~1 minute and ~1 GB of host memory; 46.8M primes: ~2 GB of device memory).
"""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--B", type=int, default=100_000_000)
    ap.add_argument("--klog", type=int, default=24)
    ap.add_argument("--tile", type=int, default=19)
    ap.add_argument("--llog", type=int, default=15)
    ap.add_argument("--f", type=float, default=0.97)
    ap.add_argument("--p-est", type=float, default=0.0715, dest="p_est")
    ap.add_argument("--head-b", type=int, default=1_000_000_000, dest="head_b")
    ap.add_argument("--head-rows", type=int, default=64, dest="head_rows")
    ap.add_argument("--rg", type=int, default=32)
    ap.add_argument("--rcta", type=int, default=8, help="generate-kernel CTAs a (row, tile) pair of the staged large-prime stage (DEEP_RCTA)")
    ap.add_argument("--split", type=int, default=1_000_000)
    ap.add_argument("--threads", type=int, default=256, help="CTA size of the count / select / rows kernels and of the head's kernels (the driver passes 256)")
    ap.add_argument("--tile-threads", type=int, default=512, dest="tile_threads", help="CTA size of the tile kernel (production: --deep-tile-threads 512)")
    ap.add_argument("--gen-threads", type=int, default=256, dest="gen_threads", help="CTA size of the large-prime generate kernel (production: --deep-gen-threads 256)")
    ap.add_argument("--staged", type=int, default=1)
    ap.add_argument("--k0", type=int, default=None, help="the window's first k (default: the first k with 200 digits)")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--verify", type=int, default=8)
    ap.add_argument("--rows", type=int, default=0, help="use only the first ROWS rows of the vector (0: all; for the CPU test)")
    a = ap.parse_args(argv)
    import cupy as cp
    import ghead
    from deep_feeder import DeepSieve, mod_big
    sp = json.load(open(a.spec))
    sp = sp[0] if isinstance(sp, list) else sp
    M, N0 = int(sp["M"]), int(sp["N0"])
    U = [int(q) for q in sp["residual"]]
    if a.rows:
        U = U[:a.rows]
    cover = [int(r) for r, _ in sp["cover"]]
    K = 1 << a.klog
    k0 = a.k0 if a.k0 is not None else -(-10 ** 199 // M)
    k0 -= k0 % 1                                                      # (a vector's window starts at its first 200-digit k, not at a multiple of 2^klog)
    t0 = time.time()
    ds = DeepSieve(M, cover, a.B, ks_log=a.klog, tile_log=a.tile, llog=a.llog, f=a.f, p_est=a.p_est, split=a.split, rg=a.rg, nthreads=a.threads, gen_threads=a.gen_threads, tile_threads=a.tile_threads,
                   max_rows=len(U) + 8, staged=bool(a.staged), rcta=a.rcta, head_b=a.head_b, head_rows=a.head_rows, log=lambda m: print("  " + m, flush=True))
    fd = ds.feeder(N0, U)
    head = fd.head
    print(f"{len(U)} rows, window 2^{a.klog} from k0 = {k0}, head rows {a.head_rows}, primes in ({a.B:,}, {a.head_b:,}]: {head.nP:,}; built in {time.time() - t0:.1f} s", flush=True)
    ok = True

    def window(with_head):
        fd.head = head if with_head else None
        cp.cuda.Device().synchronize()
        t = time.perf_counter()
        w = fd.window(k0)
        cp.cuda.Device().synchronize()
        return w, 1e3 * (time.perf_counter() - t)

    w0, _ = window(False)
    w1, _ = window(True)
    A = lambda x: np.asarray(x.get() if hasattr(x, "get") else x)
    k0a, k1a = A(w0.k), A(w1.k)
    c0, c1, ca = A(w0.cnt).astype(np.int64), A(w1.cnt).astype(np.int64), A(w1.cnt_acc).astype(np.int64)
    o0, o1 = A(w0.offs), A(w1.offs)
    r0, r1 = A(w0.rows), A(w1.rows)
    good = (np.array_equal(k0a, k1a) and np.array_equal(A(w0.alive_total), A(w1.alive_total)) and np.array_equal(A(w0.hm_all), A(w1.hm_all)) and np.array_equal(A(w0.hm_kept), A(w1.hm_kept))
            and np.array_equal(ca, c0) and bool(np.all(c1 <= c0)) and int(o1[-1]) == int(r1.size) and np.array_equal(np.diff(o1), c1))
    print(f"(1) {k0a.size:,} kept members; k, alive_total, hm_all, hm_kept identical with and without the head; cnt_acc == cnt without it; the new CSR consistent: {'OK' if good else 'FAILED'}", flush=True)
    ok &= good
    # subset check on a sample + removal only in the first head rows
    rng = np.random.default_rng(1)
    sample = rng.choice(k0a.size, size=min(3000, k0a.size), replace=False)
    sub, headonly = True, True
    for i in sample:
        a0, a1 = r0[o0[i]:o0[i + 1]], r1[o1[i]:o1[i + 1]]
        s1 = set(a1.tolist())
        sub &= s1 <= set(a0.tolist())
        headonly &= all((r in s1) or r < a.head_rows for r in a0.tolist())
    print(f"    the lists of {sample.size} sampled members: new list is a subset of the old: {sub}; every removed row is among the first {a.head_rows}: {headonly}", flush=True)
    ok &= sub and headonly
    rem = int((c0 - c1).sum())
    head_alive = int((r0 < a.head_rows).sum())
    c_emp = rem / max(head_alive, 1)
    print(f"(2) rows {int(c0.sum()):,} -> {int(c1.sum()):,}: the head removed {rem:,} of the {head_alive:,} head rows of the kept members = {100 * c_emp:.2f}% (model {100 * (1 - math.log(a.B) / math.log(a.head_b)):.2f}%)", flush=True)
    p0 = a.p_est
    ph = p0 / (1 - c_emp)
    e0 = ((1 - (1 - p0) ** c0) / p0).sum()
    hn = np.array([int((r1[o1[i]:o1[i + 1]] < a.head_rows).sum()) for i in range(k0a.size)]) if k0a.size <= 2_000_000 else None
    if hn is not None:
        e1 = ((1 - (1 - ph) ** hn) / ph + (1 - ph) ** hn * (1 - (1 - p0) ** (c1 - hn)) / p0).sum()
        print(f"    predicted Fermat tests of the window: {e0:,.0f} -> {e1:,.0f}: {100 * (1 - e1 / e0):.2f}% fewer", flush=True)
    # (3) factors
    if a.verify:
        S2 = np.asarray(head.S.get() if hasattr(head.S, "get") else head.S).astype(np.int64)
        removed_pairs, kept_pairs = [], []
        for i in sample:
            s0 = set(r0[o0[i]:o0[i + 1]].tolist())
            s1 = set(r1[o1[i]:o1[i + 1]].tolist())
            for r in sorted(s0):
                if r >= a.head_rows:
                    break
                (kept_pairs if r in s1 else removed_pairs).append((int(k0a[i]), r))
            if len(removed_pairs) >= a.verify and len(kept_pairs) >= a.verify:
                break
        bad = 0
        for kind, pairs in (("removed", removed_pairs[:a.verify]), ("kept", kept_pairs[:a.verify])):
            for k, r in pairs:
                n = N0 - U[r] + k * M
                has = bool((mod_big(n, S2) == 0).any())
                bad += (has != (kind == "removed"))
            print(f"(3) {len(pairs[:a.verify])} {kind} head rows: {'every one has' if kind == 'removed' else 'none has'} a prime factor in the head range: {'OK' if not bad else 'FAILED'}", flush=True)
        ok &= bad == 0
    # (4) time
    ts = {False: [], True: []}
    window(False)
    window(True)
    for _ in range(a.reps):
        for wh in (False, True):
            _, ms = window(wh)
            ts[wh].append(ms)
    m0, m1 = min(ts[False]), min(ts[True])
    print(f"(4) a window: {m0:.1f} ms without the head, {m1:.1f} ms with it (best of {a.reps}; means {np.mean(ts[False]):.1f} / {np.mean(ts[True]):.1f}): the head costs {m1 - m0:.1f} ms; "
          f"retries of the head's bins: {head.retries}", flush=True)
    print("HEADCHECK-OK" if ok else "HEADCHECK-FAILED", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
