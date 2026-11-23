#!/usr/bin/env python3
"""On a GPU: the whole batch pipeline of a deeper sieve bound (gbatch.BatchFeeder) at production size, with the time of every phase.

    python3 bench_batch.py spec.json [--B 67108864] [--ks 25] [--tile 19] [--split 1000000] [--f 0.99] [--rg 16] [--check] [--sweep]

spec.json: a campaign spec ({"N0", "M", "residual": [...rows], "cover": [[prime, residue], ...]}, or a list of them: the first is used).  The prime tables (primes up to B except the cover
primes, M^-1 mod s, N0 mod s) are built here with numpy and sieve200's C helper (search.init_spec loops in Python and takes minutes at B = 2^26).
The primes up to --split go through the tile kernel (every 2^tile-member tile of the batch), the others through gbig_gen once per batch; count, select, finalize and rows then run on the whole
batch (2^ks members: 2^25 = a production batch of 32 slices, a bit matrix of rows x 4 MB).  Prints ms a phase, ns a member, the memory used, and with --check a comparison with sieve200's
CPU Feeder on a small instance (40 rows, B = 2^22, 2^21 members).  --sweep tries row-group sizes and CTA sizes.
Compare with the present sieve at B = 1e6 (test_gpu_sieve.py: ~2.3 ns a member on an RTX PRO 6000) and with the model of the research session: the sieve is worth it if the whole thing
(sieve + count + select + rows, at a keep fraction near 1%) costs less than the Fermat tests it saves.
"""
import argparse, json, math, os, sys, time
import numpy as np
import cupy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import gbig
from gbatch import BatchFeeder
from deep_feeder import mod_big, modinv_vec, prime_tables_M


def prime_tables(spec, B):
    """(S, INV, N0M) of a spec: the primes below B (as search.init_spec), M^-1 mod s and N0 mod s (deep_feeder.py's numpy tables)"""
    S, INV = prime_tables_M(int(spec["M"]), [int(r) for r, _ in spec.get("cover", [])], B)
    return S, INV, mod_big(int(spec["N0"]), S.astype(np.int64)).astype(np.uint32)


def window_equal(w, cb):
    pos, good = 0, True
    for b, fb in enumerate(cb):
        n = len(fb.k)
        good &= np.array_equal(cp.asnumpy(w.k)[pos:pos + n], fb.k) and np.array_equal(cp.asnumpy(w.cnt)[pos:pos + n], fb.cnt)
        offs = cp.asnumpy(w.offs)
        good &= np.array_equal(cp.asnumpy(w.rows)[offs[pos]:offs[pos + n]], fb.rows)
        good &= int(w.alive_total[b]) == fb.alive_total
        pos += n
    return bool(good) and pos == int(w.k.size)


def check(spec, a):
    from sieve200 import Feeder
    rows = [int(q) for q in spec["residual"][:a.check_rows]]
    B, ks = a.check_b, a.check_ks
    S, INV, N0M = prime_tables(spec, B)
    tile = min(a.tile, ks - 1)
    bf = BatchFeeder(S, INV, rows, N0M, ks_log=ks, tile_log=tile, llog=min(15, ks), f=a.f, nthreads=256, split=min(a.split, B // 2), rg=a.rg,
                     staged=bool(a.staged), rcta=a.rcta, stage_cap=a.stage_cap, gen_threads=256 if not a.staged else max(256, a.rcta * (1 << (ks - tile)) // 32 * 32))
    cover = [int(r) for r, _ in spec.get("cover", [])]
    cf = Feeder(int(spec["N0"]), int(spec["M"]), rows, B=B, L=1 << min(15, ks), logK=ks, f=a.f, exclude=cover)
    ok = True
    for t in range(2):
        k0 = (1 << 31) + t * (1 << ks)
        w = bf.window(k0)
        good = window_equal(w, cf.window(k0))
        print(f"check {len(rows)} rows, B={B}, 2^{ks} members, tile 2^{tile}, {bf.n_small} small + {bf.n_large} large primes, k0={k0}: {'identical to the CPU feeder' if good else 'DIFFERENT'}", flush=True)
        ok &= good
    return ok


def run(spec, a, rg, tile_threads, label=""):
    rows = [int(q) for q in spec["residual"]]
    t0 = time.time()
    S, INV, N0M = prime_tables(spec, a.B)
    tprep = time.time() - t0
    K = 1 << a.ks
    need = len(rows) * K // 8
    free, total = cp.cuda.runtime.memGetInfo()
    print(f"{label}{len(rows)} rows, {S.size:,} primes up to {a.B} ({np.sum(S <= a.split):,} through the tile kernel, {np.sum(S > a.split):,} through gbig), batch 2^{a.ks} members: "
          f"bit matrix {need / 2**30:.2f} GB of {free / 2**30:.1f} GB free (tables {tprep:.1f} s)", flush=True)
    if need > free - (2 << 30):
        print("  not enough GPU memory for this batch; use a smaller --ks or fewer rows")
        return None
    bf = BatchFeeder(S, INV, rows, N0M, ks_log=a.ks, tile_log=a.tile, llog=a.llog, f=a.f, nthreads=a.nthreads, split=a.split, rg=rg, ppt=a.ppt,
                     gen_threads=a.gen_threads, tile_threads=tile_threads, staged=bool(a.staged), rcta=a.rcta, stage_cap=a.stage_cap)
    bf.window(0, timings=True)                                         # compile + warm up
    cp.cuda.Device().synchronize()
    acc = {}
    kept = surv = 0
    for rep in range(a.reps):
        w = bf.window((rep + 1) * K, timings=True)
        for kk, v in w.timings.items():
            acc[kk] = acc.get(kk, 0.0) + v / a.reps
        kept += int(w.k.size) // a.reps
        surv += int(w.rows.size) // a.reps
    ns = 1e6 * acc["wall"] / K
    cap = bf.big.cap if bf.big else 0
    print(f"  rg={rg} tile threads={tile_threads} gen threads={a.gen_threads} ppt={a.ppt}: wall {acc['wall']:.1f} ms = {ns:.3f} ns a member ({K / acc['wall'] / 1e3:.1f} M members/s); "
          f"kept {kept:,} members, {surv:,} survivor rows; bin cap {cap:,}, gen retries {bf.big.retries if bf.big else 0}")
    print(f"    prep {acc['prep']:.2f}  sieve (gen + tiles) {acc['sieve']:.1f}  count {acc['count']:.2f}  select {acc['select']:.2f}  finalize {acc['finalize']:.2f}  "
          f"wait1 {acc['wait1']:.2f}  rows {acc['rows']:.2f}  wait2 {acc['wait2']:.2f}  host {acc['host']:.2f}   (ms a batch)", flush=True)
    del bf
    cp.get_default_memory_pool().free_all_blocks()
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--B", type=int, default=1 << 26)
    ap.add_argument("--ks", type=int, default=25)
    ap.add_argument("--tile", type=int, default=19)
    ap.add_argument("--llog", type=int, default=15)
    ap.add_argument("--split", type=int, default=1000000)
    ap.add_argument("--f", type=float, default=0.99)
    ap.add_argument("--rg", type=int, default=16)
    ap.add_argument("--ppt", type=int, default=4)
    ap.add_argument("--nthreads", type=int, default=256)
    ap.add_argument("--gen-threads", type=int, default=256, dest="gen_threads")
    ap.add_argument("--tile-threads", type=int, default=256, dest="tile_threads")
    ap.add_argument("--staged", type=int, default=0, help="1: the staged large-prime kernel (gbig_gen_st)")
    ap.add_argument("--rcta", type=int, default=2)
    ap.add_argument("--stage-cap", type=int, default=8192, dest="stage_cap")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--rows", type=int, default=None, help="use the first N rows (default all)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--check-rows", type=int, default=40, dest="check_rows")
    ap.add_argument("--check-b", type=int, default=1 << 22, dest="check_b")
    ap.add_argument("--check-ks", type=int, default=21, dest="check_ks")
    ap.add_argument("--sweep", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    spec = spec[0] if isinstance(spec, list) else spec
    for f in ("residual", "cover"):
        if isinstance(spec.get(f), str):
            spec[f] = json.loads(spec[f])
    if a.rows:
        spec["residual"] = spec["residual"][:a.rows]
    print(f"{cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}")
    ok = True
    if a.check:
        ok = check(spec, a)
    if a.sweep:
        for rg, tt in ((8, 256), (16, 256), (16, 1024), (32, 256), (32, 1024)):
            run(spec, a, rg, tt, label="sweep: ")
    else:
        run(spec, a, a.rg, a.tile_threads)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
