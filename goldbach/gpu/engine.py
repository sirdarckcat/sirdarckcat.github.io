"""GPU desert scanner: sieve + wave-Fermat, limb count sized from the spec.

Generalisation of engine150.py: L (32-bit limbs) is computed at runtime
from bitlength(N0 + kend*M), so one binary serves 150-digit (L=16) and
200-digit (L=21) campaigns. CUDA source is templated on L.

Per k-tile:
  1. sieve kernel — bit-matrix alive[|U|][tile] (bit-packed words), one
     thread per (residual, sieve-prime) pair doing strided clears;
  2. wave kernels — wave w: every still-alive k locates its next
     surviving residual, builds n = (N0 - q) + (k0+k)*M in registers,
     runs the Montgomery base-2 Fermat chain; a pass (probable prime)
     kills the k; a k that drains all survivors with no pass is a
     SUCCESS (every residual complement composite), matching search.py
     semantics exactly while keeping every batch dense.

Usage:
  python engine.py spec.json KSTART KEND [--tile 2097152]
      [--sieve-b 1000000] [--out hits.jsonl] [--validate]
"""

import argparse
import json
import time

import numpy as np
import cupy as cp

L = None  # set in main() from the spec

CUDA_TMPL = r"""
typedef unsigned int u32;
typedef unsigned long long u64;
#define L @L@

extern "C" __global__ void sieve(const int* rows, const u32* sp,
                                 const u32* pos0, u32* bits,
                                 const long long n_pairs,
                                 const int tile_words, const u32 tile) {
    long long i = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n_pairs) return;
    int row = rows[i];
    u32 s = sp[i];
    u32* base = bits + (u64)row * tile_words;
    for (u64 k = pos0[i]; k < tile; k += s)
        atomicAnd(&base[k >> 5], ~(1u << (k & 31)));
}

__device__ __forceinline__ void mont_mul(const u32* a, const u32* b,
                                         const u32* n, u32 np, u32* out) {
    u32 t[L + 2];
#pragma unroll
    for (int j = 0; j < L + 2; j++) t[j] = 0;
    for (int i = 0; i < L; i++) {
        u64 c = 0;
#pragma unroll
        for (int j = 0; j < L; j++) {
            u64 s = (u64)t[j] + (u64)a[i] * b[j] + c;
            t[j] = (u32)s; c = s >> 32;
        }
        u64 s = (u64)t[L] + c;
        t[L] = (u32)s;
        t[L + 1] += (u32)(s >> 32);
        u32 m = t[0] * np;
        c = ((u64)t[0] + (u64)m * n[0]) >> 32;
#pragma unroll
        for (int j = 1; j < L; j++) {
            u64 s2 = (u64)t[j] + (u64)m * n[j] + c;
            t[j - 1] = (u32)s2; c = s2 >> 32;
        }
        s = (u64)t[L] + c;
        t[L - 1] = (u32)s;
        t[L] = t[L + 1] + (u32)(s >> 32);
        t[L + 1] = 0;
    }
    u32 ge = t[L] != 0;
    if (!ge) {
        ge = 1;
        for (int j = L - 1; j >= 0; j--)
            if (t[j] != n[j]) { ge = t[j] > n[j]; break; }
    }
    if (ge) {
        u64 br = 0;
        for (int j = 0; j < L; j++) {
            u64 d = (u64)t[j] - n[j] - br;
            out[j] = (u32)d; br = (d >> 63) & 1;
        }
    } else for (int j = 0; j < L; j++) out[j] = t[j];
}

__device__ __forceinline__ void mod_double(u32* a, const u32* n) {
    u32 hi = a[L - 1] >> 31;
    for (int j = L - 1; j > 0; j--) a[j] = (a[j] << 1) | (a[j - 1] >> 31);
    a[0] <<= 1;
    u32 ge = hi;
    if (!ge) {
        ge = 1;
        for (int j = L - 1; j >= 0; j--)
            if (a[j] != n[j]) { ge = a[j] > n[j]; break; }
    }
    if (ge) {
        u64 br = 0;
        for (int j = 0; j < L; j++) {
            u64 d = (u64)a[j] - n[j] - br;
            a[j] = (u32)d; br = (d >> 63) & 1;
        }
    }
}

__device__ __forceinline__ int fermat_passes(const u32* n) {
    u32 x = n[0];
    for (int it = 0; it < 5; it++) x *= 2 - n[0] * x;
    u32 np = (u32)(0u - x);
    u32 e[L];
    u64 br = 1;
    for (int j = 0; j < L; j++) {
        u64 d = (u64)n[j] - br;
        e[j] = (u32)d; br = (d >> 63) & 1;
    }
    u32 r[L];
    for (int j = 0; j < L; j++) r[j] = 0;
    r[0] = 1;
    for (int i = 0; i < 32 * L; i++) mod_double(r, n);
    u32 acc[L];
    for (int j = 0; j < L; j++) acc[j] = r[j];
    mod_double(acc, n);
    int top = -1;
    for (int j = L - 1; j >= 0 && top < 0; j--)
        if (e[j]) {
            for (int b = 31; b >= 0; b--)
                if ((e[j] >> b) & 1) { top = j * 32 + b; break; }
        }
    u32 tmp[L];
    for (int i = top - 1; i >= 0; i--) {
        mont_mul(acc, acc, n, np, tmp);
        for (int j = 0; j < L; j++) acc[j] = tmp[j];
        if ((e[i / 32] >> (i % 32)) & 1) mod_double(acc, n);
    }
    u32 one[L];
    for (int j = 0; j < L; j++) one[j] = 0;
    one[0] = 1;
    mont_mul(acc, one, n, np, tmp);
    int ok = tmp[0] == 1;
    for (int j = 1; j < L; j++) ok &= (tmp[j] == 0);
    return ok;
}

// state[k]: 0 alive, 1 killed (prp found), 2 SUCCESS (drained clean)
extern "C" __global__ void wave(const u32* bits, const u32* baseq,
                                const u32* Ml, unsigned char* state,
                                u32* progress, u64* tests,
                                const u32* alive_idx, const int n_alive,
                                const int nres, const int tile_words,
                                const u32 tile, const u64 k0) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= n_alive) return;
    u32 k = alive_idx[tid];
    int done = 0;
    u32 my_tests = 0;
    for (int w = 0; w < 4 && !done; w++) {
    int q = -1;
    for (u32 i = progress[k]; i < (u32)nres; i++) {
        if ((bits[(u64)i * tile_words + (k >> 5)] >> (k & 31)) & 1) {
            q = i; break;
        }
    }
    if (q < 0) { state[k] = 2; break; }
    progress[k] = q + 1;
    my_tests++;
    // n = baseq[q] + kk*M  with kk = k0 + k  (kk = klo + 2^32*khi)
    u64 kk = k0 + k;
    u32 klo = (u32)kk, khi = (u32)(kk >> 32);
    u32 prod[L];
    u64 c = 0;
    for (int j = 0; j < L; j++) {
        u64 t = (u64)Ml[j] * klo + c;
        prod[j] = (u32)t;
        c = t >> 32;
    }
    if (khi) {
        c = 0;
        for (int j = 0; j < L - 1; j++) {
            u64 t = (u64)prod[j + 1] + (u64)Ml[j] * khi + c;
            prod[j + 1] = (u32)t;
            c = t >> 32;
        }
    }
    u32 n[L];
    c = 0;
    for (int j = 0; j < L; j++) {
        u64 t = (u64)baseq[(u64)q * L + j] + prod[j] + c;
        n[j] = (u32)t;
        c = t >> 32;
    }
    if (fermat_passes(n)) { state[k] = 1; done = 1; }
    }
    if (my_tests) atomicAdd(tests, (u64)my_tests);
}
"""


def to_limbs(v):
    return [(v >> (32 * j)) & 0xFFFFFFFF for j in range(L)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("kstart", type=int)
    ap.add_argument("kend", type=int)
    ap.add_argument("--tile", type=int, default=1 << 21)
    ap.add_argument("--sieve-b", type=int, default=1000000)
    ap.add_argument("--out", default="hits.jsonl")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    N0, M = int(spec["N0"]), int(spec["M"])
    U = [int(q) for q in spec["residual"]]
    global L
    nmax = N0 + args.kend * M
    L = max(16, (nmax.bit_length() + 31) // 32)
    print(f"limbs L={L} ({32 * L} bits) for {len(str(nmax))}-digit N",
          flush=True)
    nres = len(U)
    from sympy import primerange
    cover_primes = set(r for r, _ in spec.get("cover", []))
    sp_list = [s for s in primerange(3, args.sieve_b)
               if s not in cover_primes and M % s != 0]
    sp = np.array(sp_list, dtype=np.uint32)
    inv = np.array([pow(int(M % s), -1, int(s)) for s in sp_list],
                   dtype=np.int64)
    n0m = np.array([int(N0 % s) for s in sp_list], dtype=np.int64)
    # base kill residue r_{q,s} = (q - N0) * M^{-1} mod s
    rmat = np.empty((nres, len(sp_list)), dtype=np.int64)
    for i, q in enumerate(U):
        rmat[i] = ((q - n0m) * inv) % sp

    rows = np.repeat(np.arange(nres, dtype=np.int32), len(sp_list))
    sp_all = np.tile(sp, nres)
    r_all = rmat.reshape(-1).astype(np.int64)
    d_rows = cp.asarray(rows)
    d_sp = cp.asarray(sp_all)
    d_r = cp.asarray(r_all)
    n_pairs = len(rows)

    baseq = np.zeros((nres, L), dtype=np.uint32)
    for i, q in enumerate(U):
        baseq[i] = to_limbs(N0 - q)
    d_baseq = cp.asarray(baseq.reshape(-1))
    d_M = cp.asarray(np.array(to_limbs(M), dtype=np.uint32))

    mod = cp.RawModule(code=CUDA_TMPL.replace("@L@", str(L)))
    k_sieve = mod.get_function("sieve")
    k_wave = mod.get_function("wave")

    tile = args.tile
    tile_words = tile // 32
    d_bits = cp.empty(nres * tile_words, dtype=cp.uint32)
    out = open(args.out, "a")
    total_tests = 0
    total_k = 0
    t_start = time.time()

    for k0 in range(args.kstart, args.kend, tile):
        cur = min(tile, args.kend - k0)
        d_bits[:] = 0xFFFFFFFF
        pos0 = ((d_r - k0) % d_sp.astype(cp.int64)).astype(cp.uint32)
        k_sieve(((n_pairs + 255) // 256,), (256,),
                (d_rows, d_sp, pos0, d_bits, np.int64(n_pairs),
                 np.int32(tile_words), np.uint32(cur)))
        state = cp.zeros(tile, dtype=cp.uint8)
        if cur < tile:
            state[cur:] = 1
        progress = cp.zeros(tile, dtype=cp.uint32)
        d_tests = cp.zeros(1, dtype=cp.uint64)
        waves = 0
        while True:
            alive_idx = cp.nonzero(state == 0)[0].astype(cp.uint32)
            n_alive = int(alive_idx.size)
            if n_alive == 0:
                break
            k_wave(((n_alive + 255) // 256,), (256,),
                   (d_bits, d_baseq, d_M, state, progress, d_tests,
                    alive_idx, np.int32(n_alive),
                    np.int32(nres), np.int32(tile_words), np.uint32(tile),
                    np.uint64(k0)))
            waves += 1
        succ = cp.asnumpy(cp.nonzero(state == 2)[0])
        tests = int(d_tests[0])
        total_tests += tests
        total_k += cur
        for kk in succ:
            k = int(k0 + kk)
            rec = {"k": k, "name": spec.get("name", "gpu"),
                   "kind": "gpu-candidate"}
            print(f"CANDIDATE k={k}", flush=True)
            out.write(json.dumps(rec) + "\n")
            out.flush()
        dt = time.time() - t_start
        print(f"tile k0={k0}: waves={waves} tests={tests} "
              f"succ={len(succ)} | cum {total_k} k in {dt:.0f}s "
              f"({total_k/dt:.0f} k/s, {total_tests/dt:,.0f} tests/s)",
              flush=True)

        if args.validate and k0 == args.kstart:
            rng = np.random.default_rng(0)
            sample = rng.integers(0, cur, 12)
            bits_h = cp.asnumpy(d_bits).reshape(nres, tile_words)
            ok = True
            for k in sample:
                k = int(k)
                surv_gpu = [i for i in range(nres)
                            if (bits_h[i][k >> 5] >> (k & 31)) & 1]
                surv_ref = [i for i in range(nres)
                            if not ((r_all[i * len(sp_list):(i + 1) * len(sp_list)] - (k0 + k)) % sp == 0).any()]
                if surv_gpu != surv_ref:
                    print(f"VALIDATE FAIL sieve k={k}")
                    ok = False
                # fermat verdicts along the tested prefix
                pr = int(cp.asnumpy(progress[k]))
                st = int(cp.asnumpy(state[k]))
                tested = [i for i in surv_gpu if i < pr]
                for idx, i in enumerate(tested):
                    n = N0 - U[i] + (k0 + k) * M
                    want = pow(2, n - 1, n) == 1
                    last = idx == len(tested) - 1
                    expect = (st == 1) if last else False
                    if want != expect and st != 2:
                        print(f"VALIDATE FAIL fermat k={k} i={i}")
                        ok = False
            print("VALIDATION:", "PASS" if ok else "FAIL", flush=True)
            if not ok:
                return
    print(f"DONE k=[{args.kstart},{args.kend}) tests={total_tests}",
          flush=True)


if __name__ == "__main__":
    main()
