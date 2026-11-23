#!/usr/bin/env python3
"""On a GPU: why does the survivor-list kernel (s200g_rows) take 6.4 ms for a matrix that s200g_count reads in 1.9 ms?  No sieve needed: a synthetic window (a random bit matrix of the production shape and density).

    python3 bench_rows.py [--klog 24] [--llog 15] [--rows 1248] [--f 0.985] [--reps 5] [--threads 256]

The window's tail runs once on random bits (count, select, finalize, then s200g_rows: the production numbers of the 'whole window' line), then every variant of the rows step runs alone on the same
inputs, best of --reps between two events:

  count (reference)      the whole matrix read in 16-row batches, a thread a word: the sequential rate
  rows                   production: a thread a kept member, one dependent load -> test -> store a row (SERIAL: the compiler cannot batch the loads past the stores)
  rows2                  16 loads in flight a thread (DEEP_REST2=1; measured slower than rows on the RTX PRO 6000)
  rows, no stores        rows with the stores replaced by a running sum (one store a thread): READS ONLY, the same loads in the same order (with no stores the compiler batches the loads: compare it with rows2)
  rows, no loads         rows with the loads replaced by a hash (the stores and tests stay): WRITES ONLY, the same scattered u16 stores
  rowmask                the matrix read once into 32-bit masks (a mask a (row group, kept member)), grid (member chunks, row groups), coalesced word stores: DEEP_ROWS3=1, step 1
  rowlist                the lists written from the masks (39 MB read, the same scattered u16 stores): step 2
  rowmask + rowlist      DEEP_ROWS3=1
  order / rows_ord       DEEP_ROWS_ORD=1: the kept members are listed by (count, index), so a warp's 32 lanes read 32 random words of the block's 4 KB slab of a row (~28 distinct sectors for 32 words);
                         s200g_order sorts a block's kept members by index once (0.05 ms) and rows_ord takes them in that order (8 sectors a warp, no sector fetched by two CTAs): the same lists
  rows_ord2              the same with 8 loads in flight a thread (DEEP_ROWS_ORD=2)
  rows_ord, no stores    reads only, in index order: rows-no-stores vs this is the effect of the order on the reads

Read it as: rows vs rows-no-stores = what the stores cost; rows vs rows-no-loads = what the loads cost; rowmask = the loads in the order count uses with no scattered writes; rowlist = the writes alone.
Nothing here changes the sieve.
"""
import argparse, os, sys, time
import numpy as np
import cupy as cp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from gpu_sieve import GpuFeeder


def timed(fn, reps):
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


class Synth(GpuFeeder):
    """a GpuFeeder whose sieve phase fills the bit matrix with random words of density ~0.34 (what a vector window's alive bits look like)"""
    def _sieve_phase(self, k0, ev):
        if not hasattr(self, "_base"):                                                    # 64 random rows made on the host (no dependence on the device RNG API), rolled to make every row different
            rng = np.random.default_rng(1234)
            base = np.empty((64, self.K // 32), dtype=np.uint32)
            for r in range(64):
                a, b, c, d, e = (rng.integers(0, 1 << 32, size=self.K // 32, dtype=np.uint64).astype(np.uint32) for _ in range(5))
                base[r] = (a & b) | (c & d & e)
            self._base = cp.asarray(base)
        for r in range(self.nU):
            self.bits[r] = cp.roll(self._base[r % 64], 977 * r)
        if ev is not None:
            ev[1].record()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--klog", type=int, default=24)
    ap.add_argument("--llog", type=int, default=15)
    ap.add_argument("--rows", type=int, default=1248)
    ap.add_argument("--f", type=float, default=0.985)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--threads", type=int, default=256)
    a = ap.parse_args(argv)
    nU, nt = a.rows, a.threads
    fd = Synth(np.array([101], dtype=np.int64), np.array([1], dtype=np.uint32), np.arange(nU, dtype=np.uint32), np.array([0], dtype=np.uint32), klog=a.klog, llog=a.llog, f=a.f,
               nthreads=nt, plain_sieve=False)
    fd.fin2, fd.rows_mode = False, 1
    w = fd.window(0, timings=True)
    cp.cuda.Device().synchronize()
    tm = w.timings
    KW = fd.K // 32
    gb = nU * KW * 4 / 1e9
    nsel = int(w.k.size)
    member = (w.k.astype(cp.uint64) % np.uint64(1 << 32)).astype(cp.uint32)             # k0 = 0: the member index of every kept member
    offs, rows = w.offs, cp.empty(int(w.rows.size) + 8, dtype=cp.uint16)
    bits, k = fd.bits, fd.k
    ng = (nU + 31) // 32
    masks = cp.empty((ng, nsel), dtype=cp.uint32)
    grid = (((nsel + nt - 1) // nt),)
    print(f"synthetic window: 2^{a.klog} members, {nU} rows ({gb:.2f} GB of bits), {nsel:,} kept members (f = {a.f}), {int(w.rows.size):,} alive rows of them", flush=True)
    print(f"production tail (ms): count {tm['count']:.2f}  select {tm['select']:.2f}  finalize {tm['finalize']:.2f}  rows {tm['rows']:.2f}", flush=True)

    nkeep = nsel // (fd.K // fd.L)
    keys = (((w.cnt.astype(cp.uint32) << 20) | (member & np.uint32(fd.L - 1))).reshape(fd.K // fd.L, nkeep))       # the keys select wrote: count << 20 | index in the block, sorted by (count, index)
    ordr = cp.empty(nsel, dtype=cp.uint32)

    def v_order():
        k["s200g_order"]((fd.K // fd.L,), (nt,), (keys, np.int32(nkeep), ordr))

    def v_rows(name):
        return lambda: k[name](grid, (nt,), (bits, np.int32(nU), member, offs, np.int32(nsel), rows))

    def v_rows_ord(name):
        return lambda: k[name](grid, (nt,), (bits, np.int32(nU), member, offs, ordr, np.int32(nsel), rows))

    def v_mask():
        k["s200g_rowmask"](grid + (ng,), (nt,), (bits, np.int32(nU), member, np.int32(nsel), masks))

    def v_list():
        k["s200g_rowlist"](grid, (nt,), (masks, np.int32(nU), offs, np.int32(nsel), rows))

    def v_count():
        k["s200g_count"](((fd.K // 32 + nt - 1) // nt,), (nt,), (bits, np.int32(nU), fd.counts))
    v_mask()                                                                              # the masks for rowlist
    v_order()                                                                             # the permutation for rows_ord
    res = [("count (reference)", timed(v_count, a.reps)),
           ("rows (production, serial)", timed(v_rows("s200g_rows"), a.reps)),
           ("rows2 (16 loads in flight)", timed(v_rows("s200g_rows2"), a.reps)),
           ("rows, no stores (reads only)", timed(v_rows("s200g_rows_nost"), a.reps)),
           ("rows, no loads (writes only)", timed(v_rows("s200g_rows_nold"), a.reps)),
           ("order (the permutation, once)", timed(v_order, a.reps)),
           ("rows_ord (by index, serial)", timed(v_rows_ord("s200g_rows_ord"), a.reps)),
           ("rows_ord2 (by index, 8 in flight)", timed(v_rows_ord("s200g_rows_ord2"), a.reps)),
           ("rows_ord, no stores (reads only)", timed(v_rows_ord("s200g_rows_ord_nost"), a.reps)),
           ("rowmask (reads, coalesced masks)", timed(v_mask, a.reps)),
           ("rowlist (writes from masks)", timed(v_list, a.reps)),
           ("rowmask + rowlist", timed(lambda: (v_mask(), v_list()), a.reps))]
    print(f"\n{'variant':36s} {'ms':>8s} {'GB/s of the matrix':>20s}")
    for name, ms in res:
        print(f"{name:36s} {ms:8.2f} {gb / (ms / 1e3):20.0f}")
    # identical output check of the two-step lists against the production kernel
    r0 = cp.empty_like(rows)
    k["s200g_rows"](grid, (nt,), (bits, np.int32(nU), member, offs, np.int32(nsel), r0))
    v_mask()
    v_list()
    cp.cuda.Device().synchronize()
    tot = int(w.rows.size)
    same = bool((r0[:tot] == rows[:tot]).all())
    print(f"\nrowmask + rowlist lists identical to rows: {same}")
    for name in ("s200g_rows_ord", "s200g_rows_ord2"):
        r1 = cp.full_like(r0, 0xFFFF)
        k[name](grid, (nt,), (bits, np.int32(nU), member, offs, ordr, np.int32(nsel), r1))
        cp.cuda.Device().synchronize()
        ok1 = bool((r0[:tot] == r1[:tot]).all())
        print(f"{name} lists identical to rows: {ok1}")
        same = same and ok1
    print("ROWS-DONE", flush=True)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
