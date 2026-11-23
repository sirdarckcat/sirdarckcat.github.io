#!/usr/bin/env python3
"""Micro-benchmarks of the instruction pipes and of shared-memory operations, to settle two design questions with numbers.

    python3 bench_pipes.py            # on a GPU (needs cupy): prints one table (--part3: only part 3)
    python3 bench_pipes.py --check sm_80     # on a machine without a GPU: compiles every kernel with NVRTC and prints the SASS
                                              # of its loop, to check that it contains the instruction it is meant to measure
                                              # (needs sass.py's tools, see its docstring)

Part 1, pipes: how many cycles a warp instruction occupies a scheduler for IMAD.WIDE.U32 (with and without the 64-bit addend),
IMAD (32-bit), IADD3, the carry pair IADD3 + IADD3.X, LOP3 and SHF, and how many IADD3 can run next to one IMAD.WIDE for free.
It decides whether a Fermat step with fewer multiplications and more adds (31-bit limbs, Karatsuba) can be faster than fermat28.
Part 2, shared memory: ATOMS.AND, plain stores of a word and of a byte, loads and a plain read-modify-write, with random addresses
(the sieve's marks) and with conflict-free addresses, at the shared-memory sizes (and so the occupancy) of klog 17, 18 and 19.
It decides whether the sieve's marks should be made with atomics at all.

Part 3, global memory (the large primes of a deep sieve): the cost of one scattered mark: `atomicAnd` / a plain store at random words of a 64 MB, 512 MB and 4 GB array,
and the write of a mark into one of 512 bins in runs of 32 (what a bucketed sieve does), as ns an operation and G operations a second over the whole GPU.

Every kernel is a loop of independent operations (8 chains a thread), 256 threads a CTA, timed with clock64() inside the kernel,
so the numbers are cycles per warp instruction per scheduler (an SM has 4), not seconds.  A value of 1.0 means one warp
instruction every cycle on each scheduler.
"""
import argparse
import sys

HEAD = "typedef unsigned int u32;\ntypedef unsigned long long u64;\n"
NCH = 8

# body templates: {c} is the chain index; every op is on its own chain.  Plain C, not asm: ptxas lowers an explicit mad.wide.u32 to
# IMAD.WIDE(no addend) + IADD3 pairs (and hoists a loop-invariant product out of the loop), whereas acc += (u64)a * b becomes
# one IMAD.WIDE.U32 with the 64-bit addend, which is what the Fermat kernels use.  b is bumped each iteration so that the product
# cannot be hoisted: that costs one IADD3 beside every IMAD.WIDE (counted: "+ operand bump").
PIPE_BODIES = {
    "IMAD.WIDE+acc, 1 bump":      "acc[{c}] += (u64)a[{c}] * b[{c}]; b[{c}] += 2u;",
    "IMAD.WIDE no acc, 1 bump":   "acc[{c}] ^= (u64)a[{c}] * b[{c}]; b[{c}] += 2u;",
    "IMAD.U32 (lo) +acc":         "asm volatile(\"mad.lo.u32 %0, %1, %2, %0;\" : \"+r\"(x[{c}]) : \"r\"(a[{c}]), \"r\"(b[{c}]));",
    "IADD3 (2 adds fused)":       "asm volatile(\"add.u32 %0, %0, %1; add.u32 %0, %0, %2;\" : \"+r\"(x[{c}]) : \"r\"(a[{c}]), \"r\"(b[{c}]));",
    "IADD3 + IADD3.X (64-bit add)": "asm volatile(\"add.cc.u32 %0, %0, %2; addc.u32 %1, %1, %3;\" : \"+r\"(x[{c}]), \"+r\"(y[{c}]) : \"r\"(a[{c}]), \"r\"(b[{c}]));",
    "LOP3":                       "asm volatile(\"and.b32 %0, %0, %1; xor.b32 %0, %0, %2;\" : \"+r\"(x[{c}]) : \"r\"(a[{c}]), \"r\"(b[{c}]));",
    "SHF":                        "asm volatile(\"shf.l.wrap.b32 %0, %0, %1, 5;\" : \"+r\"(x[{c}]) : \"r\"(a[{c}]));",
}
# one IMAD.WIDE with the addend, its operand bump, plus k further IADD3 on other chains
for _k in (1, 2, 3, 4):
    PIPE_BODIES[f"IMAD.WIDE+acc, 1 bump + {_k} IADD3"] = (
        "acc[{c}] += (u64)a[{c}] * b[{c}]; b[{c}] += 2u;\n"
        + "\n".join("asm volatile(\"add.u32 %0, %0, %1; add.u32 %0, %0, %2;\" : \"+r\"(x[{c}]) : \"r\"(a[{c}]), \"r\"(y[{c}]));" for _ in range(_k)))
# the pattern ptxas itself makes on sm_80/89 from an explicit mad.wide: a product without addend and a carry pair
PIPE_BODIES["IMAD.WIDE no acc + carry pair"] = (
    "{{ const u64 p = (u64)a[{c}] * b[{c}]; b[{c}] += 2u;\n"
    "asm volatile(\"add.cc.u32 %0, %0, %2; addc.u32 %1, %1, %3;\" : \"+r\"(x[{c}]), \"+r\"(y[{c}]) : \"r\"((u32)p), \"r\"((u32)(p >> 32))); }}")


def pipe_kernel(name, body):
    stmts = "\n".join(body.replace("{c}", str(c)) for c in range(NCH))
    return HEAD + f"""
extern "C" __global__ void k(u32 *out, long long *cyc, int iters) {{
    u32 a[{NCH}], b[{NCH}], x[{NCH}], y[{NCH}];
    u64 acc[{NCH}];
    const int t = blockIdx.x * blockDim.x + threadIdx.x;
    #pragma unroll
    for (int c = 0; c < {NCH}; c++) {{ a[c] = (t + c * 7919) | 1; b[c] = (t * 31 + c * 104729) | 1; x[c] = t + c; y[c] = c; acc[c] = t + c; }}
    __syncthreads();
    const long long t0 = clock64();
    for (int it = 0; it < iters; it++) {{
{stmts}
    }}
    const long long t1 = clock64();
    u64 r = 0;
    #pragma unroll
    for (int c = 0; c < {NCH}; c++) r ^= acc[c] + x[c] + ((u64)y[c] << 7);
    out[t] = (u32)r ^ (u32)(r >> 32);
    if (threadIdx.x == 0) cyc[blockIdx.x] = t1 - t0;
}}
"""


# shared memory kernels: dynamic shared memory of `bytes`, addresses from an LCG, loop of 8 independent ops per iteration
SMEM_BODIES = {
    # name: statement with {c} (chain), `s` = state array, SM = word pointer, SB = byte pointer, MASKW / MASKB
    "address generation only":       "r[{c}] ^= s[{c}] >> 11;",
    "ATOMS.AND random word":         "atomicAnd(&SM[(s[{c}] >> 7) & MASKW], ~(1u << (s[{c}] & 31)));",
    "STS.32 random word":            "SM[(s[{c}] >> 7) & MASKW] = r[{c}];",
    "STS.U8 random byte":            "SB[(s[{c}] >> 7) & MASKB] = 0;",
    "LDS.32 random word":            "r[{c}] += SM[(s[{c}] >> 7) & MASKW];",
    "plain RMW random word":         "{{ const u32 w = (s[{c}] >> 7) & MASKW; SM[w] = SM[w] & ~(1u << (s[{c}] & 31)); }}",
    "ATOMS.AND conflict-free":       "atomicAnd(&SM[(((s[{c}] >> 7) & ~31u) + (threadIdx.x & 31)) & MASKW], ~(1u << (s[{c}] & 31)));",
    "STS.U8 conflict-free":          "SB[(((s[{c}] >> 7) & ~127u) + (threadIdx.x & 31) * 4) & MASKB] = 0;",
}


def smem_kernel(name, body, nbytes):
    stmts = "\n".join(f"s[{c}] = s[{c}] * 1664525u + 1013904223u + {c};\n" + body.replace("{c}", str(c)) for c in range(NCH))
    return HEAD + f"""
#define MASKW {nbytes // 4 - 1}u
#define MASKB {nbytes - 1}u
extern "C" __global__ void k(u32 *out, long long *cyc, int iters) {{
    extern __shared__ u32 SM[];
    unsigned char *SB = (unsigned char *)SM;
    for (int i = threadIdx.x; i < {nbytes // 4}; i += blockDim.x) SM[i] = 0xFFFFFFFFu;
    u32 s[{NCH}], r[{NCH}];
    const int t = blockIdx.x * blockDim.x + threadIdx.x;
    #pragma unroll
    for (int c = 0; c < {NCH}; c++) {{ s[c] = t * 2654435761u + c * 40503u; r[c] = t + c; }}
    __syncthreads();
    const long long t0 = clock64();
    for (int it = 0; it < iters; it++) {{
{stmts}
    }}
    const long long t1 = clock64();
    __syncthreads();
    u32 acc = 0;
    #pragma unroll
    for (int c = 0; c < {NCH}; c++) acc ^= r[c] + s[c];
    out[t] = acc ^ SM[threadIdx.x % {nbytes // 4}];
    if (threadIdx.x == 0) cyc[blockIdx.x] = t1 - t0;
}}
"""


GLOBAL_BODIES = {
    # name: statement; s = LCG state, A = the array (u32 words, a power of two of them), NWm = words - 1.  Plain C masks, no modulo (which compiles to a loop of branches)
    "scattered atomicAnd (random word)": "atomicAnd(&A[(s[{c}] >> 2) & NWm], ~(1u << (s[{c}] & 31)));",
    "scattered plain store (random word)": "A[(s[{c}] >> 2) & NWm] = s[{c}];",
    "scattered load (random word)": "r[{c}] += A[(s[{c}] >> 2) & NWm];",
    "128 B runs at random places (bin writes)": "{{ const u32 sb = __shfl_sync(0xffffffffu, s[{c}], 0); A[(((sb >> 2) & NWm) & ~31u) + (threadIdx.x & 31)] = s[{c}]; }}",
}


def global_kernel(name, body):
    stmts = "\n".join(f"s[{c}] = s[{c}] * 1664525u + 1013904223u + {c};\n" + body.replace("{c}", str(c)) for c in range(NCH))
    return HEAD + f"""
extern "C" __global__ void k(u32 *A, u32 *out, u32 NWm, int iters) {{
    u32 s[{NCH}], r[{NCH}];
    const unsigned tid = blockIdx.x * blockDim.x + threadIdx.x;
    #pragma unroll
    for (int c = 0; c < {NCH}; c++) {{ s[c] = tid * 2654435761u + c * 40503u; r[c] = tid + c; }}
    for (int it = 0; it < iters; it++) {{
{stmts}
    }}
    u32 acc = 0;
    #pragma unroll
    for (int c = 0; c < {NCH}; c++) acc ^= r[c] + s[c];
    out[tid] = acc;
}}
"""


def run_check(arch):
    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    import sass as S
    import re, collections
    nv = S.Nvrtc()
    cases = [(n, pipe_kernel(n, b)) for n, b in PIPE_BODIES.items()] + [(n, smem_kernel(n, b, 65536)) for n, b in SMEM_BODIES.items()] \
        + [(n, global_kernel(n, b)) for n, b in GLOBAL_BODIES.items()]
    for name, src in cases:
        funcs = S.parse_sass(S.disassemble(nv.compile(src, arch, [], "cubin")))
        instrs, labels = funcs["k"]
        lp = sorted(set(S.loops(instrs, labels)), key=lambda x: x[1] - x[0], reverse=True)
        s, e = lp[0] if lp else (0, len(instrs) - 1)
        c = collections.Counter(S.opcode(b) for _, b in instrs[s:e + 1])
        print(f"{name:34s} loop of {e - s + 1:3d}: " + "  ".join(f"{k} {v}" for k, v in c.most_common(7)))


def run_gpu(args):
    import cupy as cp
    import numpy as np
    dev = cp.cuda.Device()
    nsm = dev.attributes["MultiProcessorCount"]
    name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    cc = dev.compute_capability
    print(f"{name}  (sm_{cc})  {nsm} SMs   cycles per warp instruction per scheduler (lower is faster; 1.0 = full issue rate)")
    ctas_per_sm = 4
    threads = 256
    iters = 4000
    print("\npart 1: pipes, 4 CTAs of 256 threads an SM")
    print(f"{'chain-op (see --check for its SASS)':38s} {'sched cycles/op':>13s}")
    for nm, body in PIPE_BODIES.items():
        mod = cp.RawModule(code=pipe_kernel(nm, body))
        k = mod.get_function("k")
        grid = nsm * ctas_per_sm
        out = cp.empty(grid * threads, dtype=cp.uint32)
        cyc = cp.zeros(grid, dtype=cp.int64)
        k((grid,), (threads,), (out, cyc, np.int32(200)))
        best = None
        for _ in range(3):
            k((grid,), (threads,), (out, cyc, np.int32(iters)))
            cp.cuda.Device().synchronize()
            c = int(cyc.get().max())
            best = c if best is None else min(best, c)
        warps_per_sm = ctas_per_sm * threads // 32
        per_op = best / (NCH * iters * warps_per_sm / 4)          # scheduler cycles per warp-level chain-op
        print(f"{nm:38s} {per_op:13.2f}")
    print("\n(a chain-op is one warp-level operation of the row; the '+ k IADD3' rows add k adds per IMAD.WIDE: if the cycles stay flat as k grows, the adds are free)")
    print("\npart 2: shared memory, 256 threads a CTA, as many CTAs an SM as fit; cycles per warp-level operation per SM")
    props = cp.cuda.runtime.getDeviceProperties(0)
    max_smem = props["sharedMemPerBlockOptin"]
    for nbytes in (1 << 16, 1 << 15, 1 << 14):
        if nbytes + 1024 > max_smem:
            continue
        per_sm_smem = props.get("sharedMemPerMultiprocessor", 100 * 1024)
        fit = max(1, min(8, per_sm_smem // (nbytes + 1024)))
        print(f"\n  bitmap of {nbytes // 1024} KB a CTA ({fit} CTAs an SM)")
        print(f"  {'operation':34s} {'cycles/warp-op/SM':>18s}")
        ref = None
        for nm, body in SMEM_BODIES.items():
            mod = cp.RawModule(code=smem_kernel(nm, body, nbytes))
            k = mod.get_function("k")
            if nbytes + 0 > 48 * 1024:
                k.max_dynamic_shared_size_bytes = nbytes
            grid = nsm * fit
            out = cp.empty(grid * threads, dtype=cp.uint32)
            cyc = cp.zeros(grid, dtype=cp.int64)
            k((grid,), (threads,), (out, cyc, np.int32(200)), shared_mem=nbytes)
            best = None
            for _ in range(3):
                k((grid,), (threads,), (out, cyc, np.int32(2000)), shared_mem=nbytes)
                cp.cuda.Device().synchronize()
                c = int(cyc.get().max())
                best = c if best is None else min(best, c)
            warp_ops = NCH * 2000 * fit * threads // 32          # per SM
            v = best / warp_ops
            if nm == "address generation only":
                ref = v
                print(f"  {nm:34s} {v:18.2f}")
            else:
                print(f"  {nm:34s} {v:18.2f}   (minus address generation: {max(v - (ref or 0), 0):.2f})")


def run_gpu_global(args):
    import cupy as cp
    import numpy as np
    dev = cp.cuda.Device()
    nsm = dev.attributes["MultiProcessorCount"]
    free, total = cp.cuda.runtime.memGetInfo()
    print("\npart 3: global memory, scattered marks.  G ops/s over the whole GPU (1 / that = ns an operation); 8 chains x 256 threads x 8 CTAs an SM")
    print(f"  {'operation':42s} " + " ".join(f"{s:>12s}" for s in ("64 MB", "512 MB", "4 GB")))
    threads, ctas = 256, nsm * 8
    iters = 200
    for nm, body in GLOBAL_BODIES.items():
        mod = cp.RawModule(code=global_kernel(nm, body))
        k = mod.get_function("k")
        row = []
        for nbytes in (64 << 20, 512 << 20, 4 << 30):
            if nbytes + (256 << 20) > free:
                row.append("(no memory)")
                continue
            A = cp.zeros(nbytes // 4, dtype=cp.uint32)
            out = cp.empty(ctas * threads, dtype=cp.uint32)
            k((ctas,), (threads,), (A, out, np.uint32(nbytes // 4 - 1), np.int32(4)))
            best = None
            for _ in range(3):
                cp.cuda.Device().synchronize()
                e0, e1 = cp.cuda.Event(), cp.cuda.Event()
                e0.record()
                k((ctas,), (threads,), (A, out, np.uint32(nbytes // 4 - 1), np.int32(iters)))
                e1.record(); e1.synchronize()
                ms = cp.cuda.get_elapsed_time(e0, e1)
                best = ms if best is None else min(best, ms)
            ops = ctas * threads * NCH * iters
            row.append(f"{ops / best / 1e6:9.1f} G/s")
            del A
        print(f"  {nm:42s} " + " ".join(f"{x:>12s}" for x in row), flush=True)
    nb = 1 << 30
    if nb * 2 + (256 << 20) < free:
        X = cp.zeros(nb // 4, dtype=cp.uint32); Y = cp.empty_like(X)
        Y[:] = X
        e0, e1 = cp.cuda.Event(), cp.cuda.Event()
        cp.cuda.Device().synchronize(); e0.record()
        for _ in range(5):
            Y[:] = X
        e1.record(); e1.synchronize()
        ms = cp.cuda.get_elapsed_time(e0, e1) / 5
        print(f"  reference: device copy of 1 GB (read + write): {2 * nb / ms / 1e6:.0f} GB/s; a 32-byte sector of it is {32 / (2 * nb / ms / 1e6):.3f} ns")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", default=None, help="no GPU: compile for this arch (sm_80, sm_89, sm_120) and print each kernel's loop")
    ap.add_argument("--part3", action="store_true", help="only part 3 (global memory, scattered marks; needs ~5 GB free)")
    a = ap.parse_args()
    if a.check:
        run_check(a.check)
    elif a.part3:
        run_gpu_global(a)
    else:
        run_gpu(a)
        run_gpu_global(a)


if __name__ == "__main__":
    main()
