#!/usr/bin/env python3
"""The window's tail kernels, restructured (DEEP_REST2=1): s200g_rows2 and s200g_fin_sums + s200g_fin_main against the originals s200g_rows / s200g_finalize and against numpy, on the CPU emulation.

    python3 test_rest2_cpu.py

Random bit matrices and random kept-key lists (the keys select writes: count << 20 | index in the block, block by block), over geometries that hit every branch: nU below, at and above the 16-row batch of
rows2 (and not a multiple of it), one selection block or several, nkeep 1, below, at and above the CTA size (partial last chunk), counts 0 and the maximum, offsets from a first block with no rows.
Compared: member, k, counts, CSR offsets, total (finalize); the lists (rows).
"""
import ctypes, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_gsieve


def run_case(lib, klog, llog, nth, nU, nkeep, rng, k0, zero_blocks=()):
    KW = (1 << klog) // 32
    nb = 1 << (klog - llog)
    L = 1 << llog
    bits = rng.integers(0, 1 << 32, (nU, KW), dtype=np.uint64).astype(np.uint32)
    bits = bits & (rng.integers(0, 1 << 32, (nU, KW), dtype=np.uint64).astype(np.uint32) | rng.integers(0, 1 << 32, (nU, KW), dtype=np.uint64).astype(np.uint32))      # density 3/8
    # the keys of every block: nkeep distinct indices of the block, the count of each member = the number of set bits of its column (what select would have computed), sorted by (count, index)
    keys = np.zeros((nb, nkeep), dtype=np.uint32)
    for b in range(nb):
        idx = np.sort(rng.choice(L, nkeep, replace=False)).astype(np.int64)
        m = (b << llog) + idx
        if b in zero_blocks:
            for mm in m:                                        # every kept member of this block has no alive row (one by one: members share words)
                bits[:, int(mm) >> 5] &= np.uint32(~(1 << (int(mm) & 31)) & 0xFFFFFFFF)
        col = ((bits[:, m >> 5] >> (m & 31).astype(np.uint32)) & 1).sum(axis=0).astype(np.int64)
        order = np.lexsort((idx, col))
        keys[b] = ((col[order] << 20) | idx[order]).astype(np.uint32)
    nsel = nb * nkeep
    vp = ctypes.c_void_p
    P = lambda a: a.ctypes.data

    def outs():
        return (np.zeros(nsel, np.uint16), np.zeros(nsel, np.uint32), np.zeros(nsel, np.uint64), np.full(nsel + 1, -7, np.int64), np.full(1, -7, np.int64))
    c0, m0, k_0, o0, t0 = outs()
    lib.cpu_finalize(P(keys), nsel, nkeep, k0, P(c0), P(m0), P(k_0), P(o0), P(t0))
    c1, m1, k_1, o1, t1 = outs()
    btot = np.zeros(nb, np.uint32)
    lib.cpu_fin_sums(P(keys), nkeep, P(btot), nb)
    lib.cpu_fin_main(P(keys), nkeep, nb, k0, P(btot), P(c1), P(m1), P(k_1), P(o1), P(t1))
    ok_fin = (np.array_equal(c0, c1) and np.array_equal(m0, m1) and np.array_equal(k_0, k_1) and np.array_equal(o0, o1) and int(t0[0]) == int(t1[0])
              and np.array_equal(btot, (keys >> 20).astype(np.uint64).sum(axis=1).astype(np.uint32)))
    # the lists: numpy, rows, rows2
    tot = int(t0[0])
    exp = [np.nonzero((bits[:, int(m) >> 5] >> np.uint32(int(m) & 31)) & 1)[0].astype(np.uint16) for m in m0]
    r_np = np.concatenate(exp) if exp else np.zeros(0, np.uint16)
    r0 = np.full(max(tot, 1), 0xFFFF, np.uint16)
    r1 = np.full(max(tot, 1), 0xFFFF, np.uint16)
    lib.cpu_rows(P(bits), nU, P(m0), P(o0), nsel, P(r0))
    lib.cpu_rows2(P(bits), nU, P(m0), P(o0), nsel, P(r1))
    ok_rows = np.array_equal(r0[:tot], r_np) and np.array_equal(r1[:tot], r_np) and int(np.diff(o0).sum()) == tot == int(sum(len(e) for e in exp))
    return ok_fin, ok_rows, nsel, tot


def main():
    rng = np.random.default_rng(11)
    ok = True
    # (klog, llog, nthreads, nU, nkeep, zero_blocks)
    cases = [(11, 11, 64, 37, 5, ()),                          # one selection block, nU = 2 batches + 5
             (11, 11, 64, 16, 64, ()),                         # nU = exactly one batch, nkeep = the CTA size
             (11, 11, 64, 15, 1, ()),                          # nU below a batch, one key
             (12, 10, 64, 33, 150, ()),                        # 4 blocks, nkeep = 2 chunks + 22
             (12, 10, 64, 48, 64, (0,)),                       # nkeep = the CTA size; block 0 without a single alive row
             (13, 11, 64, 100, 129, (3,)),                     # 4 blocks, 3 chunks (last one has 1 key), a block of zero counts
             (12, 12, 64, 20, 200, ()),                        # a single block, 4 chunks
             (12, 9, 128, 17, 31, (2, 7))]                     # 8 blocks, nkeep below the CTA size
    for klog, llog, nth, nU, nkeep, zb in cases:
        lib = test_gsieve.build(klog, llog, nth, 8192, 1)
        ok_fin, ok_rows, nsel, tot = run_case(lib, klog, llog, nth, nU, nkeep, rng, k0=int(rng.integers(0, 1 << 40)), zero_blocks=zb)
        print(f"  K=2^{klog} L=2^{llog} CTA {nth}: {nU} rows, {nkeep} kept a block ({nsel} keys, {tot} alive rows): finalize == fin_sums + fin_main {'ok' if ok_fin else 'DIFFERENT'}; "
              f"rows == rows2 == numpy {'ok' if ok_rows else 'DIFFERENT'}", flush=True)
        ok &= ok_fin and ok_rows
    print("REST2 OK" if ok else "REST2 FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
