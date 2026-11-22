#!/usr/bin/env python3
"""On a GPU: what one mark by a prime above the tile costs in a bucketed layout (gbig_kernels.cuh), with the breakdown.

    python3 bench_bigprimes.py [--rows 1093] [--plo 20] [--b 24] [--ks 25] [--rg 16] [--groups N] [--check]

Primes in (2^plo, 2^b] (every prime above the 2^19-bit tile of the small-prime kernel), a batch of 2^ks members (2^25: 4.6 GB of bit matrix for 1,093 rows, of which
only one group of rg rows is ever resident), `rows` rows.  The roots are random (they are uniform in [0, s) for the true tables too), so no cover is needed.
For every group of rg rows: gbig_gen (each (row, prime) pair once: count the marks of every (row, tile) bin, reserve, write the 19-bit offsets) and gbig_apply (a CTA a bin:
the tile's shared bitmap, every entry clears its bit).  --groups N times only N groups and scales to all rows.  --check compares the first rows' bit matrix with numpy.
Prints ns a mark for the whole stage, which is the number a deep sieve bound needs (it pays below ~0.03 ns, see the research session's table).
"""
import argparse, math, sys, time
import numpy as np
import cupy as cp
from gbig import BigStage, make_table, primes_between


def reference(U, TAB, ks, nrows):
    S, INV, C0 = TAB[:, 0].astype(np.int64), TAB[:, 1].astype(np.int64), TAB[:, 3].astype(np.int64)
    K = 1 << ks
    ref = np.ones((nrows, K), dtype=bool)
    for r in range(nrows):
        q = int(U[r])
        for s, inv, c0 in zip(S.tolist(), INV.tolist(), C0.tolist()):
            ref[r, (q * inv - c0) % s::s] = False
    return ref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=1093)
    ap.add_argument("--plo", type=int, default=20)
    ap.add_argument("--b", type=int, default=24)
    ap.add_argument("--ks", type=int, default=25)
    ap.add_argument("--tile", type=int, default=19)
    ap.add_argument("--rg", type=int, default=16)
    ap.add_argument("--ppt", type=int, default=4)
    ap.add_argument("--threads", type=int, default=256)
    ap.add_argument("--groups", type=int, default=None)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    S = primes_between(1 << a.plo, 1 << a.b)
    rng = np.random.default_rng(1)
    TAB = make_table(S, rng=rng)
    U = np.sort(rng.choice(np.arange(1, 150000), size=a.rows, replace=False)).astype(np.uint32)
    K = 1 << a.ks
    st = BigStage(U, TAB, ks_log=a.ks, tile_log=a.tile, rg=a.rg, ppt=a.ppt, threads=a.threads)
    exp_marks_row = K * float(np.sum(1.0 / S.astype(np.float64)))
    ngroups = (a.rows + a.rg - 1) // a.rg
    run_groups = min(ngroups, a.groups or ngroups)
    print(f"{cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}: {a.rows} rows, primes in (2^{a.plo}, 2^{a.b}]: {S.size:,} of them, batch 2^{a.ks} members "
          f"({st.ntiles} tiles of 2^{a.tile} bits), groups of {a.rg} rows, cap {st.cap:,} entries a bin ({st.nbins * st.cap * 4 / 1e6:.0f} MB of bins)   (setup {time.time() - t0:.1f} s)")
    print(f"expected marks a row {exp_marks_row:,.0f} = {exp_marks_row / K:.1f} a member; pair visits a row {S.size:,}")
    st.run_group(0, min(a.rg, a.rows))                                    # compile + warm up
    cp.cuda.Device().synchronize()
    tm = {}
    marks = 0
    nr = 0
    t0 = time.time()
    for g in range(run_groups):
        row0 = g * a.rg
        nrows = min(a.rg, a.rows - row0)
        st.run_group(row0, nrows, tm)
        marks += st.marks(nrows)
        nr += nrows
    cp.cuda.Device().synchronize()
    wall = time.time() - t0
    scale = a.rows / nr
    gen, app = tm.get("gen", 0) * scale, tm.get("apply", 0) * scale
    total_marks = marks * scale
    print(f"{nr} rows timed ({run_groups} groups), scaled to {a.rows} rows: gen {gen:.1f} ms, apply {app:.1f} ms, total {gen + app:.1f} ms; marks {total_marks / 1e9:.2f} G "
          f"({marks / nr:,.0f} a row = {marks / nr / K:.1f} a member); capacity retries {st.retries}; wall {1e3 * wall * scale:.1f} ms")
    ns_mark = 1e6 * (gen + app) / total_marks
    print(f"  ns a mark: gen {1e6 * gen / total_marks:.4f}   apply {1e6 * app / total_marks:.4f}   TOTAL {ns_mark:.4f}   <- the cost of one mark by a prime above the tile")
    print(f"  ns a member of the batch: {1e6 * (gen + app) / K:.3f}  ({a.rows} rows, {S.size * a.rows / K:.1f} pair visits a member: {1e6 * gen / (S.size * a.rows):.5f} ns a visit in gen)")
    pa = st.pass_a_ms(0, min(a.rg, a.rows)) * (a.rows / min(a.rg, a.rows))
    print(f"  of gen: pass A (visits + counting, no writes) {pa:.1f} ms = {1e6 * pa / total_marks:.4f} ns a mark, {1e6 * pa / (S.size * a.rows):.5f} ns a pair visit; pass B (the writes) ~ {gen - pa:.1f} ms = {1e6 * (gen - pa) / total_marks:.4f} ns a mark")
    traffic = total_marks * 8 / 1e9
    print(f"  bins written + read: {traffic:.1f} GB in {gen + app:.1f} ms = {traffic / ((gen + app) / 1e3):.0f} GB/s; bit tiles written: {a.rows * K / 8 / 1e9:.1f} GB")
    if a.check:
        nrows = min(2, a.rows)
        out = st.run_group(0, nrows)
        ref = reference(U, TAB, a.ks, nrows)
        bits = np.unpackbits(cp.asnumpy(out).view(np.uint8), bitorder="little").reshape(nrows, K).astype(bool)
        print("  check against numpy (first %d rows): %s" % (nrows, "identical" if np.array_equal(bits, ref) else "DIFFERENT"))
        return 0 if np.array_equal(bits, ref) else 1


if __name__ == "__main__":
    sys.exit(main())
