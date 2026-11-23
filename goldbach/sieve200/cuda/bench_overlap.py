#!/usr/bin/env python3
"""Can the sieve run BESIDE the Fermat kernel on one GPU?  The decisive co-residency test, without the campaign driver.

    python3 bench_overlap.py spec.json [--variant s1r_asm|s1r_asm_r80|s1rw] [--carveout 0|100] [--cta-sm 0] [--tests 67108864] [--B 100000000] [--reps 2]

A production batch of an RTX PRO 6000 is ~1.27 s of Fermat kernels (72%) and ~0.43 s of sieve (24%).  If the sieve could run on the SMs while the Fermat CTAs run (the sieve is bound by
shared-memory atomics and L2 traffic, the Fermat step by the integer multiplier, so they use different units), a batch would take ~1.35 s instead of 1.76 s: x1.3.  The first trial of
`search_gpu5 --overlap 1` (23 Nov 03:10Z) gave NOTHING: the numbers say the sieve ran serialized with the Fermat kernels.  Likely reasons, each testable here:
  * the SM's L1 / shared-memory split: the Fermat kernel asks for no shared memory, the sieve CTAs for 64 KB; NVIDIA lists "a switch between L1 / shared-memory configurations" among the things that stop
    two streams from running concurrently  ->  --carveout 100 (FERMAT_CARVEOUT / DEEP_CARVEOUT: every kernel asks for the largest shared-memory carve-out);
  * no room: 5 Fermat CTAs of 128 threads at 92 registers take 61k of the SM's 65k registers, a sieve CTA needs ~10k  ->  --variant s1r_asm_r80 (80 registers: 5 CTAs take 51k, 14k stay free) or
    --cta-sm 4 (the Fermat launch in chunks of 4 CTAs an SM; costs ~8% of the Fermat time).
What it does: (1) Fermat alone: one launch of --tests real candidates (events); (2) the sieve alone: one 2^25-member window of the production configuration (staged large primes, B = 1e8,
the spec's rows); (3) both: the Fermat launch on the default stream, the sieve windows back to back in a thread on a high-priority non-blocking stream until the Fermat launch is done.
It prints the Fermat slowdown under the overlap, the sieve slowdown, the windows completed, and a projection of a production batch (Fermat 1.27 s, sieve 0.43 s, other 0.06 s):
    sequential = F + S + O,  overlapped = max(F x slowdown_F, S x slowdown_S) + O   (slowdown_F against the production kernel's own one-launch time, --ref-variant).
Success = a projected batch clearly below the sequential 1.76 s (x1.15 or more).  Needs a GPU, cupy and the tree of sieve200/cuda + fermat661/cuda; ~3 minutes; stop production on that GPU first.
"""
import argparse
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "fermat661", "cuda"))

VARIANTS = {
    "s1r_asm": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True),                    # the RTX PRO 6000s' production kernel (92 registers)
    "s1r_asm_r80": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True, maxreg=80),     # 80 registers: 14k registers an SM stay free beside 5 CTAs
    "s1r_asm_r72": dict(step_file="fermat28_step_s1r.cuh", asm_mad=True, maxreg=72),
    "s1rw": dict(step_file="fermat28_step_s1rw.cuh"),                                    # the A100 / L4 kernel
}


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--variant", default="s1r_asm", choices=sorted(VARIANTS))
    ap.add_argument("--carveout", type=int, default=0, help="100: FERMAT_CARVEOUT=100 and DEEP_CARVEOUT=100 (every kernel asks for the largest shared-memory carve-out)")
    ap.add_argument("--cta-sm", type=int, default=0, help="launch the Fermat kernel in chunks of this many CTAs an SM (0: one launch)")
    ap.add_argument("--tests", type=int, default=1 << 26, help="Fermat tests in the timed launch (2^26 ~ 3 s)")
    ap.add_argument("--B", type=int, default=100_000_000)
    ap.add_argument("--ks", type=int, default=25)
    ap.add_argument("--tile", type=int, default=19)
    ap.add_argument("--rg", type=int, default=16)
    ap.add_argument("--tile-threads", type=int, default=256, dest="tile_threads")
    ap.add_argument("--gen-threads", type=int, default=256, dest="gen_threads")
    ap.add_argument("--ref-variant", default="s1r_asm", choices=sorted(VARIANTS), dest="ref_variant",
                    help="the production kernel of this GPU (s1r_asm on the RTX PRO 6000, s1rw on the L4 / T4 / A100): the projection compares the overlapped Fermat time with ITS unchunked launch, "
                         "so a variant or a chunked launch that is slower on its own is charged for it")
    ap.add_argument("--no-priority", action="store_true", help="the sieve stream without the highest priority (a plain non-blocking stream)")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--proj-fermat", type=float, default=1.27, help="seconds of Fermat kernels in a production batch (projection)")
    ap.add_argument("--proj-sieve", type=float, default=0.43, help="seconds of sieve in a production batch (projection)")
    ap.add_argument("--proj-other", type=float, default=0.06, help="seconds of host work not hidden in a production batch (projection)")
    return ap.parse_args()


def make_feeder(cp, spec, a):
    """the production sieve: staged large-prime kernel, tile kernel for the primes up to 1e6, the spec's rows"""
    import numpy as np
    from bench_batch import prime_tables
    from gbatch import BatchFeeder
    rows = [int(q) for q in spec["residual"]]
    S, INV, N0M = prime_tables(spec, a.B)
    bf = BatchFeeder(S, INV, rows, N0M, ks_log=a.ks, tile_log=a.tile, llog=15, f=0.97, nthreads=256, split=1_000_000, rg=a.rg, ppt=4, gen_threads=a.gen_threads,
                     tile_threads=a.tile_threads, staged=True, rcta=2, stage_cap=8192)
    return bf, len(rows)


def make_tester(cp, spec, a):
    """real candidates N0 - q + k M of the spec: random rows, k in [2^30, 2^32) as time_fermat28.py"""
    import numpy as np
    import gpu_fermat28 as g28
    from gmpy2 import mpz
    N0, M = mpz(spec["N0"]), mpz(spec["M"])
    U = spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"])
    kopts = VARIANTS[a.variant]
    T = g28.Tester(N0, M, U, kopts=kopts, kmin=1 << 30)
    rng = np.random.default_rng(1)
    idx = cp.asarray(rng.integers(0, len(U), a.tests).astype(np.int32))
    kv = cp.asarray(rng.integers(1 << 30, 1 << 32, a.tests, dtype=np.uint64).astype(np.uint32))
    attrs = g28.kernel(21, **kopts).attributes
    return T, idx, kv, attrs


def fermat_pass(cp, T, idx, kv, cta_sm, nsm):
    """one timed launch of all the tests (the chunked launch as search_gpu5 --fermat-cta-sm); returns (event start, event end)"""
    e0, e1 = cp.cuda.Event(), cp.cuda.Event()
    e0.record()
    if cta_sm:
        step = cta_sm * nsm * 128
        for lo in range(0, int(idx.size), step):
            T.test(idx[lo:lo + step], kv[lo:lo + step])
    else:
        T.test(idx, kv)
    e1.record()
    return e0, e1


def main():
    a = parse()
    if a.carveout:
        os.environ["FERMAT_CARVEOUT"] = str(a.carveout)
        os.environ["DEEP_CARVEOUT"] = str(a.carveout)
    import cupy as cp
    from overlap import sieve_stream
    specs = json.load(open(a.spec))
    spec = specs[0] if isinstance(specs, list) else specs
    dev = cp.cuda.Device()
    nsm = dev.attributes["MultiProcessorCount"]
    print(f"{cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}: {nsm} SMs, Fermat {a.variant}, {a.tests:,} tests a launch{f' in chunks of {a.cta_sm} CTAs an SM' if a.cta_sm else ''}, "
          f"carve-out {a.carveout or 'default'}, sieve stream {'plain non-blocking' if a.no_priority else 'highest priority'}", flush=True)
    bf, nrows = make_feeder(cp, spec, a)
    T, idx, kv, attrs = make_tester(cp, spec, a)
    K = 1 << a.ks
    print(f"  Fermat kernel: {attrs['num_regs']} registers, {attrs['local_size_bytes']} B local; sieve: {nrows} rows, window 2^{a.ks} members, B = {a.B:,}, tile CTAs {a.tile_threads} threads, gen CTAs {a.gen_threads}", flush=True)
    regs_cta = -(-attrs["num_regs"] * 32 // 256) * 256 * 4
    print(f"  one Fermat CTA takes {regs_cta:,} of 65,536 registers: {65536 // regs_cta} CTAs an SM leave {65536 - (65536 // regs_cta) * regs_cta:,} registers free for a sieve CTA", flush=True)

    # warm up (compile every kernel)
    bf.window(0)
    T.test(idx[:8192], kv[:8192])
    dev.synchronize()

    # 1. Fermat alone, 2. sieve alone
    f_alone = []
    for _ in range(a.reps):
        dev.synchronize()
        e0, e1 = fermat_pass(cp, T, idx, kv, a.cta_sm, nsm)
        e1.synchronize()
        f_alone.append(cp.cuda.get_elapsed_time(e0, e1) / 1e3)          # (cupy has no Event.elapsed_time: the module function)
    s_alone = []
    for j in range(a.reps + 1):
        t0 = time.perf_counter()
        bf.window((j + 1) * K)
        dev.synchronize()
        s_alone.append(time.perf_counter() - t0)
    F, S = min(f_alone), min(s_alone[1:])
    print(f"alone:      Fermat {F:.3f} s ({a.tests / F / 1e6:.1f}M tests/s)   sieve window {S * 1e3:.1f} ms", flush=True)
    # the reference of the projection: the production kernel in one launch (a chunked launch or another variant is slower on its own, and that cost belongs to the configuration)
    if a.variant == a.ref_variant and not a.cta_sm:
        F_ref = F
    else:
        ra = argparse.Namespace(**vars(a))
        ra.variant = a.ref_variant
        Tr, idxr, kvr, _ = make_tester(cp, spec, ra)
        Tr.test(idxr[:8192], kvr[:8192])
        dev.synchronize()
        f_ref = []
        for _ in range(a.reps):
            dev.synchronize()
            e0, e1 = fermat_pass(cp, Tr, idxr, kvr, 0, nsm)
            e1.synchronize()
            f_ref.append(cp.cuda.get_elapsed_time(e0, e1) / 1e3)
        F_ref = min(f_ref)
        del Tr, idxr, kvr
        print(f"            production kernel ({a.ref_variant}, one launch) alone: {F_ref:.3f} s ({a.tests / F_ref / 1e6:.1f}M tests/s): this configuration alone is x{F / F_ref:.3f} of it", flush=True)

    # 3. both
    results = []
    for rep in range(a.reps):
        stop = threading.Event()
        durs, stamps = [], []
        errs = []

        def work():
            try:
                cp.cuda.Device(dev.id).use()
                st = cp.cuda.Stream(non_blocking=True) if a.no_priority else sieve_stream(cp)
                j = 20
                with st:
                    while not stop.is_set():
                        t0 = time.perf_counter()
                        bf.window((j + 1) * K)
                        st.synchronize()
                        t1 = time.perf_counter()
                        durs.append(t1 - t0)
                        stamps.append(t1)
                        j += 1
            except BaseException as e:                                  # reported below
                errs.append(e)
        th = threading.Thread(target=work, daemon=True)
        dev.synchronize()
        th.start()
        time.sleep(0.05)                                                # the sieve thread is running when the Fermat launch starts
        tw0 = time.perf_counter()
        e0, e1 = fermat_pass(cp, T, idx, kv, a.cta_sm, nsm)
        e1.synchronize()
        tw1 = time.perf_counter()
        fc = cp.cuda.get_elapsed_time(e0, e1) / 1e3
        stop.set()
        th.join()
        if errs:
            raise errs[0]
        done = [d for d, t in zip(durs, stamps) if tw0 <= t <= tw1]
        results.append((fc, tw1 - tw0, len(done), sum(done) / max(len(done), 1)))
    fc, wall, nwin, sc = min(results, key=lambda r: r[0])
    slow_f = fc / F
    slow_fp = fc / F_ref                                                # against the production kernel's own launch: what a production batch would pay
    # the sieve's rate under load: windows completed inside the Fermat launch (the one in flight when it ends is not counted, so it is a slight under-estimate)
    rate_alone = 1.0 / S
    rate_conc = nwin / wall
    slow_s = rate_alone / rate_conc if rate_conc > 0 else float("inf")
    work_seq = F + nwin * S
    print(f"concurrent: Fermat {fc:.3f} s (x{slow_f:.3f} against alone), {nwin} sieve windows completed meanwhile "
          f"(mean {sc * 1e3:.0f} ms a window: x{sc / S:.2f}; {rate_conc:.2f} windows/s against {rate_alone:.2f} alone: sieve slowdown x{slow_s:.2f})", flush=True)
    print(f"  the same work one after the other: {work_seq:.3f} s;  overlapped: {fc:.3f} s  ->  x{work_seq / fc:.2f}")
    # projection of a production batch
    seq = a.proj_fermat + a.proj_sieve + a.proj_other
    ov = max(a.proj_fermat * slow_fp, a.proj_sieve * slow_s) + a.proj_other
    if F_ref != F:
        print(f"  Fermat under overlap against the production kernel alone: x{slow_fp:.3f} (against this configuration alone: x{slow_f:.3f})")
    print(f"production batch (Fermat {a.proj_fermat} s, sieve {a.proj_sieve} s, other {a.proj_other} s): sequential {seq:.2f} s, overlapped {ov:.2f} s -> x{seq / ov:.2f}")
    verdict = ("OVERLAP WORKS: worth building the cross-batch sieve thread (search_gpu5 --overlap with this configuration)" if seq / ov >= 1.15 else
               "no useful overlap in this configuration: try --carveout 100, --variant s1r_asm_r80, --cta-sm 4, --no-priority" if seq / ov < 1.05 else "partial overlap: compare the other configurations")
    print(verdict)


if __name__ == "__main__":
    main()
