#!/usr/bin/env python3
"""On a GPU: where the sieve time of a vector window (2^24 members, B = 1e8, 1,248 rows) goes, kernel by kernel, by taking pieces away from the production kernels.

    python3 bench_split.py spec.json [--ks 24] [--rg 32] [--rcta 2] [--gen-threads 256] [--tile-threads 512] [--stage-cap 8192] [--reps 3]

The window's sieve phase is a loop over row groups: gbig_gen_st (the large primes' marks into bins, two passes: A counts, B writes) and s200g_tile (a CTA a (row, tile): the bitmap set to ones,
the small primes' marks with ATOMS.AND, the bin applied, the tile written).  bench_batch.py reports the two together ("sieve (gen + tiles)").  Here every variant runs the whole window's groups
back to back inside one event pair (reps times, best kept):

    gen            the staged generate kernel, as in production
    gen pass A     the same with cap = 0: each CTA visits its (prime, row) pairs, counts the marks in shared memory, reserves, finds the room too small and returns: no pass B, no writes
    tile           the tile kernel as in production (bins of the last generate applied)
    tile, no bins  gcnt zeroed: nothing to apply
    tile, no small the small-prime loop skipped (nS = 0): tile init + apply + write
    tile, neither  tile init + write only: the floor of the kernel's memory traffic (2.4 GB of bit matrix written)

Differences: gen pass B = gen - gen pass A; small-prime marks = tile - (tile, no small); bin apply = tile - (tile, no bins); tile init + write = tile, neither.  The numbers answer where the ~88 ms of a
window are (the GPU session measured the atomic unit at ~12 marks a clock an SM, the tile kernel does ~0.8: so what is it?).  Nothing here changes the sieve.
"""
import argparse, json, os, sys, time
import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from gbatch import BatchFeeder
from bench_batch import prime_tables


def timed(fn, reps):
    """best of reps of fn() between two events, in ms (fn launches kernels only)"""
    best = None
    for _ in range(reps):
        e0, e1 = cp.cuda.Event(), cp.cuda.Event()
        e0.record()
        fn()
        e1.record()
        e1.synchronize()
        ms = cp.cuda.get_elapsed_time(e0, e1)
        best = ms if best is None else min(best, ms)
    return best


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--B", type=int, default=100_000_000)
    ap.add_argument("--ks", type=int, default=24)
    ap.add_argument("--tile", type=int, default=19)
    ap.add_argument("--llog", type=int, default=15)
    ap.add_argument("--split", type=int, default=1_000_000)
    ap.add_argument("--f", type=float, default=0.97)
    ap.add_argument("--rg", type=int, default=32)
    ap.add_argument("--ppt", type=int, default=4)
    ap.add_argument("--nthreads", type=int, default=256)
    ap.add_argument("--gen-threads", type=int, default=256, dest="gen_threads")
    ap.add_argument("--tile-threads", type=int, default=512, dest="tile_threads")
    ap.add_argument("--rcta", type=int, default=2)
    ap.add_argument("--stage-cap", type=int, default=8192, dest="stage_cap")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--rows", type=int, default=0, help="use the first N rows (0: all)")
    a = ap.parse_args(argv)
    spec = json.load(open(a.spec))
    spec = spec[0] if isinstance(spec, list) else spec
    for f in ("residual", "cover"):
        if isinstance(spec.get(f), str):
            spec[f] = json.loads(spec[f])
    rows = [int(q) for q in spec["residual"]]
    if a.rows:
        rows = rows[:a.rows]
    spec["residual"] = rows
    S, INV, N0M = prime_tables(spec, a.B)
    K = 1 << a.ks
    bf = BatchFeeder(S, INV, rows, N0M, ks_log=a.ks, tile_log=a.tile, llog=a.llog, f=a.f, nthreads=a.nthreads, split=a.split, rg=a.rg, ppt=a.ppt, gen_threads=a.gen_threads,
                     tile_threads=a.tile_threads, staged=True, rcta=a.rcta, stage_cap=a.stage_cap)
    print(f"{len(rows)} rows, {S.size:,} primes up to {a.B:,} ({bf.n_small:,} in the tile kernel, {bf.n_large:,} in the staged large-prime stage), window 2^{a.ks}, rg {a.rg}, tile threads {a.tile_threads}, "
          f"gen threads {a.gen_threads}, rcta {a.rcta}, stage cap {a.stage_cap}", flush=True)
    w = bf.window(K, timings=True)                                      # builds the tables (prep kernels) for this k0, compiles, warms up
    cp.cuda.Device().synchronize()
    tw = w.timings
    print(f"whole window (bench_batch's phases, ms): sieve {tw['sieve']:.1f}  count {tw['count']:.2f}  select {tw['select']:.2f}  finalize {tw['finalize']:.2f}  rows {tw['rows']:.2f}  wall {tw['wall']:.1f}", flush=True)
    groups = [(row0, min(a.rg, bf.nU - row0)) for row0 in range(0, bf.nU, a.rg)]
    big = bf.big
    nS = bf.n_small
    zero_gcnt = cp.zeros(big.nbins + 1, dtype=cp.uint32)

    def launch_gen(cap):
        bins = big._bins_for(max(big.cap, cap))
        for row0, nrows in groups:
            big.gcnt[:] = 0
            big.k["gbig_gen_st"](big.gen_grid(nrows), (big.threads,),
                                 (bf.U, big.TAB, big.pstart, np.int32(row0), np.int32(nrows), np.uint32(cap), big.gcnt, bins))

    def launch_tile(gcnt, ns):
        bins = big._bins_for(big.cap)
        for row0, nrows in groups:
            bf.k[bf.tile_kernel]((nrows, bf.ntiles), (bf.tile_threads,), (bf.U, np.int32(row0), bf.tabt, np.int32(ns), gcnt, bins, np.uint32(big.cap), bf.bits), shared_mem=bf.tile_smem)

    launch_gen(big.cap)                                                 # leaves valid counts and bins of the last group for the tile variants
    cp.cuda.Device().synchronize()
    valid_gcnt = big.gcnt.copy()
    t_gen = timed(lambda: launch_gen(big.cap), a.reps)
    t_gen_a = timed(lambda: launch_gen(0), a.reps)
    launch_gen(big.cap)
    cp.cuda.Device().synchronize()
    t_tile = timed(lambda: launch_tile(big.gcnt, nS), a.reps)
    t_tile_nb = timed(lambda: launch_tile(zero_gcnt, nS), a.reps)
    t_tile_ns = timed(lambda: launch_tile(big.gcnt, 0), a.reps)
    t_tile_nn = timed(lambda: launch_tile(zero_gcnt, 0), a.reps)
    marks_group = int(valid_gcnt[:big.nbins].astype(cp.uint64).sum())
    print(f"\nms a window ({len(groups)} groups of up to {a.rg} rows; every row, back to back):")
    print(f"  gen (staged large-prime kernel)      {t_gen:8.2f}")
    print(f"    pass A (visits + counting)         {t_gen_a:8.2f}")
    print(f"    pass B (stage, flush)              {t_gen - t_gen_a:8.2f}")
    print(f"  tile kernel                          {t_tile:8.2f}")
    print(f"    small-prime marks                  {t_tile - t_tile_ns:8.2f}   ({nS:,} primes; tile - tile without them)")
    print(f"    bin apply                          {t_tile - t_tile_nb:8.2f}   (tile - tile with empty bins)")
    print(f"    init + write of the tiles          {t_tile_nn:8.2f}   (tile with neither)")
    print(f"  gen + tile                           {t_gen + t_tile:8.2f}   (bench_batch's sieve phase: {tw['sieve']:.1f})")
    print(f"  per 2^{a.ks} members: marks of the last group's bins {marks_group:,} (all bins, {groups[-1][1]} rows)")
    print("SPLIT-DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
