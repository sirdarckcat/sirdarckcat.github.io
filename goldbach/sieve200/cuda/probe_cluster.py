#!/usr/bin/env python3
"""Thread-block clusters on this GPU (the lead's question of 25 Nov 18:42Z): the largest cluster that launches with a given shared memory a CTA, and the rate of
random 32-bit AND reductions into a cluster's distributed shared memory, against the same into a CTA's own shared memory.  Together they say whether a bin-free
large-prime pass is possible: a cluster holding one row of a 2^24-member window (2 MB of bits) whose CTAs apply every mark straight into it, with no bins in DRAM.

    python3 probe_cluster.py [--threads 512] [--ms 30] [--reps 3]          # ~10-20 s on a paused G4

For CL in 1, 2, 4, 8, 16 (16 with the non-portable cluster size allowed) and shared memory of 32, 64, 96 KB and the device's per-block maximum:
  launch: does a grid of clusters of CL CTAs with that much dynamic shared memory each launch at all
  local : each thread ANDs a random bit of its own CTA's shared memory (red.shared::cta, what the tile kernel does today)
  remote: each thread ANDs a random bit of a random CTA of its cluster (mapa + red.shared::cluster: what a bin-free pass would do; 1/CL of them land locally)
  arith : the loop without the reduction (the xorshift and the address arithmetic: subtract it to read the memory side alone)
rates in G reductions a second for the whole GPU, grids of 4 clusters' worth of CTAs per SM's share (more than can be resident: the hardware decides how many run).
The random range is the largest power of two of words <= the shared memory a CTA.  Then the implication for a 2^24 window: the largest cluster memory that
launched, the window W a cluster can hold, and the bin-free pass's two costs (marks at the measured remote rate, pass A's visits scaled by 2^24 / W) against
today's large-prime stage (generate 22.2 ms + the tile kernel's bin reads ~12 ms a window, GPU session 25 Nov).
"""
import argparse, sys, time
import numpy as np

SRC = r"""
#ifndef CL
#define CL 1
#endif
extern "C" __global__ void __cluster_dims__(CL, 1, 1) probe(unsigned *out, int iters, unsigned seed, unsigned wmask, int mode) {
    extern __shared__ unsigned sm[];
    unsigned rank;
    asm volatile("mov.u32 %0, %%cluster_ctarank;" : "=r"(rank));
    for (unsigned i = threadIdx.x; i <= wmask; i += blockDim.x) sm[i] = 0xFFFFFFFFu;
    asm volatile("barrier.cluster.arrive.aligned;\n\tbarrier.cluster.wait.aligned;" ::: "memory");
    const unsigned base = (unsigned)__cvta_generic_to_shared(sm);
    unsigned x = (seed ^ (blockIdx.x * 0x9E3779B9u) ^ (threadIdx.x * 0x85EBCA6Bu)) | 1u, acc = 0;
    for (int i = 0; i < iters; i++) {
        x ^= x << 13; x ^= x >> 17; x ^= x << 5;
        const unsigned w = x & wmask, m = ~(1u << ((x >> 20) & 31u));
        if (mode == 0) {
            asm volatile("red.shared::cta.and.b32 [%0], %1;" :: "r"(base + 4u * w), "r"(m) : "memory");
        } else if (mode == 1) {
            const unsigned r = (x >> 27) & (CL - 1u);
            unsigned ra;
            asm volatile("mapa.shared::cluster.u32 %0, %1, %2;" : "=r"(ra) : "r"(base + 4u * w), "r"(r));
            asm volatile("red.relaxed.cluster.shared::cluster.and.b32 [%0], %1;" :: "r"(ra), "r"(m) : "memory");
        } else {
            acc += w ^ m;
        }
    }
    asm volatile("barrier.cluster.arrive.aligned;\n\tbarrier.cluster.wait.aligned;" ::: "memory");   /* no CTA leaves while others still write into it */
    if (threadIdx.x == 0) out[blockIdx.x] = sm[0] ^ sm[wmask] ^ acc;
}
"""

MODES = ("local", "remote", "arith")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=512)
    ap.add_argument("--ms", type=float, default=30.0, help="target milliseconds a timed launch")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--cl", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    a = ap.parse_args(argv)
    import cupy as cp
    dev = cp.cuda.Device()
    attrs = dev.attributes
    nsm = attrs["MultiProcessorCount"]
    smem_block = attrs.get("MaxSharedMemoryPerBlockOptin", attrs.get("MaxSharedMemoryPerBlock"))
    smem_sm = attrs.get("MaxSharedMemoryPerMultiprocessor", 0)
    props = cp.cuda.runtime.getDeviceProperties(dev.id)
    name = props["name"].decode() if isinstance(props["name"], bytes) else props["name"]
    cc = f"{props['major']}.{props['minor']}"
    print(f"device {name} (cc {cc}), {nsm} SMs, shared memory {smem_sm // 1024} KB an SM, {smem_block // 1024} KB a block at most (opt-in); {a.threads} threads a CTA", flush=True)
    allocs = sorted({32 * 1024, 64 * 1024, 96 * 1024, int(smem_block)} - {x for x in (96 * 1024,) if x > smem_block})
    out = cp.zeros(1 << 16, dtype=cp.uint32)
    res = {}
    for CL in a.cl:
        try:
            mod = cp.RawModule(code=SRC, options=(f"-DCL={CL}", "-std=c++17"))
            k = mod.get_function("probe")
        except Exception as e:
            print(f"  CL {CL:2d}: compile/load FAILED: {str(e).splitlines()[0][:200]}", flush=True)
            continue
        if CL > 8:
            try:
                cp.cuda.driver.funcSetAttribute(getattr(k, "kernel", k).ptr, 14, 1)     # CU_FUNC_ATTRIBUTE_NON_PORTABLE_CLUSTER_SIZE_ALLOWED
            except Exception as e:
                print(f"  CL {CL:2d}: non-portable cluster size not set ({e})", flush=True)
        for alloc in allocs:
            words = 1 << (int(alloc // 4).bit_length() - 1)
            wmask = np.uint32(words - 1)
            try:
                k.max_dynamic_shared_size_bytes = int(alloc)
            except Exception as e:
                print(f"  CL {CL:2d}, {alloc // 1024:3d} KB: attribute FAILED ({e})", flush=True)
                continue
            nclus = max(1, (4 * nsm + CL - 1) // CL)
            grid = nclus * CL
            row = {}
            for mi, mode in enumerate(MODES):
                def launch(iters):
                    k((grid,), (a.threads,), (out, np.int32(iters), np.uint32(12345 + mi), wmask, np.int32(mi)), shared_mem=int(alloc))
                try:
                    launch(64)
                    cp.cuda.Device().synchronize()
                except Exception as e:
                    row[mode] = None
                    print(f"  CL {CL:2d}, {alloc // 1024:3d} KB: launch FAILED ({str(e).splitlines()[0][:160]})", flush=True)
                    break
                e0, e1 = cp.cuda.Event(), cp.cuda.Event()
                it = 256
                e0.record(); launch(it); e1.record(); e1.synchronize()
                t = cp.cuda.get_elapsed_time(e0, e1)
                it = int(max(256, min(1 << 22, it * a.ms / max(t, 1e-3))))
                best = 1e30
                for _ in range(a.reps):
                    e0.record(); launch(it); e1.record(); e1.synchronize()
                    best = min(best, cp.cuda.get_elapsed_time(e0, e1))
                row[mode] = grid * a.threads * it / (best * 1e-3) / 1e9           # G operations a second
            if row and all(row.get(m) is not None for m in MODES):
                res[(CL, alloc)] = row
                print(f"  CL {CL:2d}, {alloc // 1024:3d} KB a CTA ({CL * alloc // 1024:5d} KB a cluster, {words * 4 // 1024} KB random range): local {row['local']:8.1f} G/s, "
                      f"remote {row['remote']:8.1f} G/s, loop alone {row['arith']:8.1f} G/s", flush=True)
    if not res:
        print("no cluster configuration launched: no bin-free pass on this device", flush=True)
        print("PROBE-CLUSTER-DONE", flush=True)
        return res
    best_mem = max(CL * al for (CL, al) in res)
    win = lambda mem: min(1 << 24, (mem * 8) >> 15 << 15)                         # members of a row a cluster holds: whole 2^15 selection blocks, at most 2^24
    print(f"largest cluster memory that launched: {best_mem // 1024} KB = one row of a window of {win(best_mem)} members ({win(best_mem) / (1 << 24):.2f} x 2^24; a 2^24 row needs 2,048 KB)", flush=True)
    MARKS, VIS_MS, TODAY = 7.1e9, 13.8, 22.2 + 12.0                                  # a 2^24 window: large-prime marks, pass A's visits, today's large-prime cost (ms)
    for (CL, al), row in sorted(res.items()):
        Wc = win(CL * al)
        mem_rate = row["remote"]
        t_marks = MARKS / (mem_rate * 1e9) * 1e3
        t_vis = VIS_MS * (1 << 24) / Wc
        print(f"  CL {CL:2d} x {al // 1024:3d} KB: a window of {Wc / (1 << 24):.2f} x 2^24 a cluster: marks {t_marks:6.1f} ms + pass A {t_vis:6.1f} ms = {t_marks + t_vis:6.1f} ms "
              f"against today's ~{TODAY:.0f} ms a 2^24 window (marks and visits overlap at best: the max of the two, {max(t_marks, t_vis):.1f} ms)", flush=True)
    print("PROBE-CLUSTER-DONE", flush=True)
    return res


if __name__ == "__main__":
    main()
