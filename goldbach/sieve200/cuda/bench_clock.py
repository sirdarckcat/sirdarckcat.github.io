#!/usr/bin/env python3
"""Is clock64() the SM clock?  Every cycle count of bench_pipes.py and bench_fm28_step.py is a difference of clock64(), so if clock64 ticks slower than the SM executes, every "cycles an
instruction costs" in them is too small by that factor.  (On the RTX PRO 6000 the real Fermat kernel runs 1.45-1.5x slower than the benchmark costs predict, at an SM clock of 2,422 MHz.)

    python3 bench_clock.py            # on a GPU (needs cupy): a few seconds
    python3 bench_clock.py --check sm_120    # no GPU: compile and print the SASS of the loop (needs sass.py's tools)

Two independent calibrations, on every SM at once (one warp an SM, ~0.3 s):
  1. clock64 ticks per nanosecond of %globaltimer: the tick rate in GHz, to compare with nvidia-smi's SM clock (nvidia-smi --query-gpu=clocks.sm --format=csv -lms 100 beside it);
  2. clock64 ticks per dependent IMAD of a chain x = x * a + c (the latency of a dependent IMAD is 4 cycles on sm_80 / 89 / 120: the stall count ptxas encodes for it): ticks / 4 should be 1.00
     if clock64 counts SM cycles.
"""
import argparse
import sys

KERNEL = r'''
extern "C" __global__ void spin(long long *ticks, unsigned long long *ns, unsigned long long *iters, unsigned int *sink, long long target_ns) {
    unsigned long long g0, g1;
    asm volatile("mov.u64 %0, %%globaltimer;" : "=l"(g0));
    const long long c0 = clock64();
    unsigned int x = threadIdx.x + 1u;
    unsigned long long n = 0;
    for (;;) {
        #pragma unroll 1
        for (int i = 0; i < 1024; i++) {
            asm volatile("mad.lo.u32 %0, %0, 1664525, 1013904223;" : "+r"(x));       // a dependent chain of IMADs
            asm volatile("mad.lo.u32 %0, %0, 1664525, 1013904223;" : "+r"(x));
            asm volatile("mad.lo.u32 %0, %0, 1664525, 1013904223;" : "+r"(x));
            asm volatile("mad.lo.u32 %0, %0, 1664525, 1013904223;" : "+r"(x));
        }
        n += 4096;
        asm volatile("mov.u64 %0, %%globaltimer;" : "=l"(g1));
        if ((long long)(g1 - g0) >= target_ns) break;
    }
    const long long c1 = clock64();
    if (threadIdx.x == 0) { ticks[blockIdx.x] = c1 - c0; ns[blockIdx.x] = g1 - g0; iters[blockIdx.x] = n; }
    sink[blockIdx.x * blockDim.x + threadIdx.x] = x;
}
'''


def run_check(arch):
    import collections
    sys.path.insert(0, ".")
    import sass as SS
    nv = SS.Nvrtc()
    funcs = SS.parse_sass(SS.disassemble(nv.compile(KERNEL, arch, [], "cubin")))
    instrs, labels = funcs["spin"]
    for s, e in sorted(set(SS.loops(instrs, labels)), key=lambda x: x[1] - x[0]):
        c = collections.Counter(SS.opcode(b) for _, b in instrs[s:e + 1])
        print(f"loop [{s},{e}] {e - s + 1} instructions: {dict(c)}")


def run_gpu():
    import cupy as cp
    import numpy as np
    dev = cp.cuda.Device()
    nsm = dev.attributes["MultiProcessorCount"]
    name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    k = cp.RawModule(code=KERNEL).get_function("spin")
    for warps in (1, 4):
        threads = 32 * warps
        ticks = cp.zeros(nsm, dtype=cp.int64)
        ns = cp.zeros(nsm, dtype=cp.uint64)
        iters = cp.zeros(nsm, dtype=cp.uint64)
        sink = cp.zeros(nsm * threads, dtype=cp.uint32)
        k((nsm,), (threads,), (ticks, ns, iters, sink, np.int64(20_000_000)))           # warm up (20 ms)
        cp.cuda.Device().synchronize()
        k((nsm,), (threads,), (ticks, ns, iters, sink, np.int64(300_000_000)))
        cp.cuda.Device().synchronize()
        t, n, it = ticks.get().astype(np.float64), ns.get().astype(np.float64), iters.get().astype(np.float64)
        ghz = t / n                                                                    # ticks per ns = GHz
        per_imad = t / it
        print(f"{name}, {warps} warp(s) an SM, {nsm} SMs, {n.mean() / 1e6:.0f} ms: clock64 ticks at {np.median(ghz):.3f} GHz (min {ghz.min():.3f}, max {ghz.max():.3f}); "
              f"{np.median(per_imad):.3f} ticks per dependent IMAD (4 expected if clock64 counts SM cycles: ratio {np.median(per_imad) / 4.0:.3f})", flush=True)
    print("compare the GHz with nvidia-smi's SM clock during the run (nvidia-smi --query-gpu=clocks.sm --format=csv -lms 100); a ratio well below 1 means clock64 ticks slower than the SM executes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", default=None, help="no GPU: compile for this arch and print the loop")
    a = ap.parse_args()
    if a.check:
        run_check(a.check)
    else:
        run_gpu()


if __name__ == "__main__":
    main()
