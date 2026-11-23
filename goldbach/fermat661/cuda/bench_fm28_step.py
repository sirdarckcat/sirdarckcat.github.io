#!/usr/bin/env python3
"""Cost experiments INSIDE the real fermat28 step (not a micro-benchmark of one instruction), to find out why the step costs what it costs.

    python3 bench_fm28_step.py [--style s1r_asm|s1rw|s1w] [--steps 3000]         # on a GPU (needs cupy); a few minutes
    python3 bench_fm28_step.py --check sm_80 [--style ...]                        # no GPU: compile every configuration with NVRTC and print the loop's instruction counts

The kernel loads x and n (24 limbs of 28 bits, random) and runs `steps` fm28_step calls in a loop (not unrolled), timing the loop with clock64(); no flags, no exponent: only the
step's own instructions, as gen_fermat28.generate makes them.  The cycles are per warp-step per scheduler: (loop cycles) / steps / (CTAs an SM), because an SM runs 4 schedulers and
a CTA of 128 threads is one warp on each.  Style: s1r_asm = the RTX PRO 6000s' production step (redundant limbs, PTX mad.wide), s1rw = the A100 / L4's (redundant limbs,
plain C products, mul.wide for m * n), s1w = carry-chain step with mul.wide.

  E1  size of the loop body.  The same generator with 8 .. 24 limbs (the products, the carries and the structure are the same, so the body is 5 KB .. 19 KB of code) at a fixed
      occupancy: cycles per IMAD.WIDE.  If it rises with the body size, the instruction cache (or register pressure) is what costs.
  E2  extra instructions.  24 limbs plus K dummy IADD3 (two adds into a private register) or K dummy IMAD.WIDE (x_a * x_b into a private 64-bit accumulator) spread over the
      columns: the cycles each one adds inside the real step, to compare with bench_pipes.py's benchmark rows and with costmodel.py's two-pipe model.
  E3  occupancy.  24 limbs at 1 .. 6 CTAs an SM (limited with dynamic shared memory): if cycles per warp-step fall with more warps, the step is latency bound.

Compare the cycles per IMAD.WIDE with bench_pipes.py's part 1 (IMAD.WIDE alone: 2.5 RTX PRO 6000, 4.15 A100, 4.5 L4).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sieve200", "cuda"))
import gen_fermat28 as gen

HEAD = "typedef unsigned int u32;\ntypedef unsigned long long u64;\n"
KERNEL = r'''
#define NL %(NL)d
#ifndef MASK28
#define MASK28 0x0FFFFFFFu
#endif
extern "C" __global__ void bench(const u32 *init, u32 *out, long long *cyc, int steps) {
    u32 x[NL], n[NL];
    const int t = blockIdx.x * blockDim.x + threadIdx.x;
    const u32 *p = init + (size_t)(t & 1023) * (2 * NL + 1);
    #pragma unroll
    for (int i = 0; i < NL; i++) { x[i] = p[i] & MASK28; n[i] = (p[NL + i] & MASK28) | (i == 0 ? 1u : 0u); }
    const u32 np = p[2 * NL] | 1u;
    __syncthreads();
    const long long t0 = clock64();
    #pragma unroll 1
    for (int s = 0; s < steps; s++) fm28_step(x, n, np, (u32)(s & 1));
    const long long t1 = clock64();
    u32 r = 0;
    #pragma unroll
    for (int i = 0; i < NL; i++) r = r * 31u + x[i];
    out[t] = r;
    if (threadIdx.x == 0) cyc[blockIdx.x] = t1 - t0;
}
'''
STYLES = {                       # S, redundant, mulw, extra nvrtc options
    "s1r_asm": (1, True, False, ["-DFM28_ASM=1"]),
    "s1rw": (1, True, True, []),
    "s1w": (1, False, True, []),
}


def n_wide(NL):
    return NL * (NL + 1) // 2 + NL * NL            # squaring products (incl. diagonal) + reduction products m_i n_j (the last m_k n_0 counted in NL^2)


def source(NL, style, extra_alu=0, extra_mul=0):
    S, red, mulw, opts = STYLES[style]
    return HEAD + gen.generate(NL, S, red, mulw, extra_alu, extra_mul) + KERNEL % dict(NL=NL), list(opts)


def run_check(arch, style):
    import collections
    import sass as SS
    nv = SS.Nvrtc()
    print(f"{style}, {arch}: instructions in the step loop (the biggest loop of the kernel)")
    print(f"{'config':26s} {'loop':>6s} {'IMAD.WIDE':>9s} {'IADD3':>6s} {'(+.X)':>6s} {'SHF':>5s} {'LOP3':>5s} {'IMAD':>5s}")
    cfgs = [(NL, 0, 0) for NL in (8, 12, 16, 20, 24)] + [(24, a, 0) for a in (96, 192, 384)] + [(24, 0, m) for m in (96, 192, 384)]
    for NL, ea, em in cfgs:
        src, opts = source(NL, style, ea, em)
        funcs = SS.parse_sass(SS.disassemble(nv.compile(src, arch, opts, "cubin")))
        instrs, labels = funcs["bench"]
        lp = sorted(set(SS.loops(instrs, labels)), key=lambda x: x[1] - x[0], reverse=True)[0]
        body = instrs[lp[0]:lp[1] + 1]
        c = collections.Counter(SS.opcode(b) for _, b in body)
        wide = sum(v for k, v in c.items() if k.startswith("IMAD.WIDE"))
        iadd3x = sum(v for k, v in c.items() if k.startswith("IADD3.X"))
        iadd3 = sum(v for k, v in c.items() if k.startswith("IADD3") and not k.startswith("IADD3.X"))
        other = lambda name: sum(v for k, v in c.items() if k == name or k.startswith(name + "."))
        label = f"NL={NL}" + (f" +{ea} IADD3" if ea else "") + (f" +{em} IMAD.WIDE" if em else "")
        print(f"{label:26s} {len(body):6d} {wide:9d} {iadd3:6d} {iadd3x:6d} {other('SHF'):5d} {other('LOP3'):5d} {other('IMAD') - wide:5d}")


def run_gpu(a):
    import cupy as cp
    import numpy as np
    dev = cp.cuda.Device()
    props = cp.cuda.runtime.getDeviceProperties(0)
    nsm = dev.attributes["MultiProcessorCount"]
    smem_sm = int(props.get("sharedMemPerMultiprocessor", 100 * 1024))
    max_opt = int(props["sharedMemPerBlockOptin"])
    regs_sm = int(props["regsPerMultiprocessor"])
    print(f"{props['name'].decode()}: {nsm} SMs, style {a.style}, {a.steps} steps a launch, 128 threads a CTA")
    rng = np.random.default_rng(1)
    init = cp.asarray(rng.integers(0, 1 << 32, 1024 * 49, dtype=np.uint64).astype(np.uint32))
    cache = {}

    def measure(NL, ea, em, c):
        key = (NL, ea, em)
        if key not in cache:
            src, opts = source(NL, a.style, ea, em)
            cache[key] = cp.RawModule(code=src, options=tuple(opts)).get_function("bench")
        k = cache[key]
        regs = int(k.attributes["num_regs"])
        per_cta = -(-regs * 32 // 256) * 256 * 4                          # registers a CTA of 4 warps allocates (256-register granules)
        cap = regs_sm // per_cta
        if c is None:
            c = min(5, cap)
        if c > cap:
            return None
        shared = max(0, min(max_opt, smem_sm // c - 1024))
        if shared > 48 * 1024:
            k.max_dynamic_shared_size_bytes = shared
        grid = nsm * c
        out = cp.empty(grid * 128, dtype=cp.uint32)
        cyc = cp.zeros(grid, dtype=cp.int64)
        k((grid,), (128,), (init, out, cyc, np.int32(50)), shared_mem=shared)
        best = None
        for _ in range(3):
            k((grid,), (128,), (init, out, cyc, np.int32(a.steps)), shared_mem=shared)
            cp.cuda.Device().synchronize()
            m = int(cyc.get().max())
            best = m if best is None else min(best, m)
        return best / a.steps / c, regs, c

    print("\nE1  loop-body size (cycles per warp-step per scheduler; the last column divides by the IMAD.WIDE of the step)")
    print(f"{'limbs':>6s} {'IMAD.WIDE':>9s} {'~code KB':>9s} {'regs':>5s} {'CTAs/SM':>8s} {'cycles/step':>12s} {'cyc/IMAD.WIDE':>14s}")
    for NL in (8, 12, 16, 20, 24):
        r = measure(NL, 0, 0, None)
        if r:
            print(f"{NL:6d} {n_wide(NL):9d} {1.35 * 16 * n_wide(NL) / 1024:9.1f} {r[1]:5d} {r[2]:8d} {r[0]:12.0f} {r[0] / n_wide(NL):14.2f}", flush=True)
    print("\nE2  extra instructions inside the 24-limb step (cycles a warp-step, difference to the first row, per added instruction)")
    print(f"{'config':22s} {'regs':>5s} {'CTAs/SM':>8s} {'cycles/step':>12s} {'added':>8s} {'per instruction':>16s}")
    base = measure(24, 0, 0, None)
    print(f"{'baseline':22s} {base[1]:5d} {base[2]:8d} {base[0]:12.0f}", flush=True)
    for kind, vals in (("alu", (96, 192, 384)), ("mul", (96, 192, 384))):
        for K in vals:
            r = measure(24, K if kind == "alu" else 0, K if kind == "mul" else 0, base[2])
            if r:
                print(f"{'+' + str(K) + (' IADD3' if kind == 'alu' else ' IMAD.WIDE'):22s} {r[1]:5d} {r[2]:8d} {r[0]:12.0f} {r[0] - base[0]:8.0f} {(r[0] - base[0]) / K:16.2f}", flush=True)
    print("\nE3  occupancy (24 limbs)")
    print(f"{'CTAs/SM':>8s} {'warps/scheduler':>16s} {'cycles/step':>12s} {'cyc/IMAD.WIDE':>14s}")
    for c in range(1, 7):
        r = measure(24, 0, 0, c)
        if r:
            print(f"{c:8d} {c:16d} {r[0]:12.0f} {r[0] / n_wide(24):14.2f}", flush=True)
        else:
            print(f"{c:8d}  (the registers do not allow it)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="s1r_asm", choices=sorted(STYLES))
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--check", default=None, help="no GPU: compile for this arch (sm_80, sm_89, sm_120) and print the loop's instruction counts")
    a = ap.parse_args()
    if a.check:
        run_check(a.check, a.style)
    else:
        run_gpu(a)


if __name__ == "__main__":
    main()
