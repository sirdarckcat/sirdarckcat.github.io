"""E1 gate 1: GPU Montgomery base-2 Fermat kernel — exactness + throughput.

512-bit (16x32-bit limb) Montgomery CIOS arithmetic, one thread per
candidate n (odd). Computes 2^(n-1) mod n via a squaring-only chain
(square per exponent bit, modular doubling when the bit is set — for
base 2 the "multiply" step is a single add). Emits 1 iff the test
passes (probable prime => this k dies in the desert search).

Run on Colab:  colab run --gpu T4 fermat_t4.py
Validates against CPU pow() on random 500-bit odd integers plus edge
cases, then measures throughput on a large batch.
"""

import time

import numpy as np
import cupy as cp

L = 16  # 32-bit limbs => 512-bit capacity (150-digit N needs 499 bits)

KERNEL = r"""
typedef unsigned int u32;
typedef unsigned long long u64;
#define L 16

__device__ __forceinline__ void mont_sqr_mul(const u32* a, const u32* b,
                                             const u32* n, u32 np, u32* out) {
    u32 t[L + 2];
#pragma unroll
    for (int j = 0; j < L + 2; j++) t[j] = 0;
    for (int i = 0; i < L; i++) {
        u64 c = 0;
#pragma unroll
        for (int j = 0; j < L; j++) {
            u64 s = (u64)t[j] + (u64)a[i] * b[j] + c;
            t[j] = (u32)s;
            c = s >> 32;
        }
        u64 s = (u64)t[L] + c;
        t[L] = (u32)s;
        t[L + 1] += (u32)(s >> 32);
        u32 m = t[0] * np;
        c = ((u64)t[0] + (u64)m * n[0]) >> 32;
#pragma unroll
        for (int j = 1; j < L; j++) {
            u64 s2 = (u64)t[j] + (u64)m * n[j] + c;
            t[j - 1] = (u32)s2;
            c = s2 >> 32;
        }
        s = (u64)t[L] + c;
        t[L - 1] = (u32)s;
        t[L] = t[L + 1] + (u32)(s >> 32);
        t[L + 1] = 0;
    }
    // conditional subtract: if t >= n (including overflow limb) subtract n
    u32 ge = t[L] != 0;
    if (!ge) {
        ge = 1;
        for (int j = L - 1; j >= 0; j--) {
            if (t[j] != n[j]) { ge = t[j] > n[j]; break; }
        }
    }
    if (ge) {
        u64 br = 0;
        for (int j = 0; j < L; j++) {
            u64 d = (u64)t[j] - n[j] - br;
            out[j] = (u32)d;
            br = (d >> 63) & 1;
        }
    } else {
        for (int j = 0; j < L; j++) out[j] = t[j];
    }
}

__device__ __forceinline__ void mod_double(u32* a, const u32* n) {
    // a = 2a mod n  (a < n on entry)
    u32 hi = a[L - 1] >> 31;
    for (int j = L - 1; j > 0; j--) a[j] = (a[j] << 1) | (a[j - 1] >> 31);
    a[0] <<= 1;
    u32 ge = hi;
    if (!ge) {
        ge = 1;
        for (int j = L - 1; j >= 0; j--) {
            if (a[j] != n[j]) { ge = a[j] > n[j]; break; }
        }
    }
    if (ge) {
        u64 br = 0;
        for (int j = 0; j < L; j++) {
            u64 d = (u64)a[j] - n[j] - br;
            a[j] = (u32)d;
            br = (d >> 63) & 1;
        }
    }
}

extern "C" __global__ void fermat2(const u32* ns, unsigned char* out,
                                   int count) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= count) return;
    u32 n[L];
    for (int j = 0; j < L; j++) n[j] = ns[idx * L + j];
    // n' = -n^{-1} mod 2^32 (Newton)
    u32 x = n[0];
    for (int it = 0; it < 5; it++) x *= 2 - n[0] * x;
    u32 np = (u32)(0u - x);
    // e = n - 1
    u32 e[L];
    u64 br = 1;
    for (int j = 0; j < L; j++) {
        u64 d = (u64)n[j] - br;
        e[j] = (u32)d;
        br = (d >> 63) & 1;
    }
    // R mod n via 32*L modular doublings starting from 1
    u32 r[L];
    for (int j = 0; j < L; j++) r[j] = 0;
    r[0] = 1;
    for (int i = 0; i < 32 * L; i++) mod_double(r, n);
    // Montgomery form of 2: double(R mod n)
    u32 acc[L];
    for (int j = 0; j < L; j++) acc[j] = r[j];
    mod_double(acc, n);
    // top bit position of e
    int top = -1;
    for (int j = L - 1; j >= 0 && top < 0; j--)
        if (e[j]) { for (int b = 31; b >= 0; b--) if ((e[j] >> b) & 1) { top = j * 32 + b; break; } }
    // square-and-double, left to right, skipping the top bit
    u32 tmp[L];
    for (int i = top - 1; i >= 0; i--) {
        mont_sqr_mul(acc, acc, n, np, tmp);
        for (int j = 0; j < L; j++) acc[j] = tmp[j];
        if ((e[i / 32] >> (i % 32)) & 1) mod_double(acc, n);
    }
    // leave Montgomery domain: multiply by 1
    u32 one[L];
    for (int j = 0; j < L; j++) one[j] = 0;
    one[0] = 1;
    mont_sqr_mul(acc, one, n, np, tmp);
    // pass iff result == 1
    unsigned char ok = tmp[0] == 1;
    for (int j = 1; j < L; j++) ok &= (tmp[j] == 0);
    out[idx] = ok;
}
"""


def to_limbs(vals):
    arr = np.zeros((len(vals), L), dtype=np.uint32)
    for i, v in enumerate(vals):
        for j in range(L):
            arr[i, j] = (v >> (32 * j)) & 0xFFFFFFFF
    return arr


def main():
    mod = cp.RawModule(code=KERNEL)
    kern = mod.get_function("fermat2")
    rng = np.random.default_rng(42)

    # ---- correctness: random 500-bit odd n + edge cases ----
    cases = []
    for _ in range(20000):
        v = int.from_bytes(rng.bytes(63), "little") | (1 << 498) | 1
        cases.append(v)
    # known primes / carmichael / small structure near 2^498
    p = (1 << 498) + 12629  # make some near-power-of-two odd numbers
    cases += [p, p + 2, p + 4, (1 << 400) + 1 | (1 << 498), 3 | (1 << 498)]
    limbs = cp.asarray(to_limbs(cases))
    out = cp.zeros(len(cases), dtype=cp.uint8)
    kern(((len(cases) + 255) // 256,), (256,), (limbs, out, len(cases)))
    got = cp.asnumpy(out)
    bad = 0
    for i, v in enumerate(cases):
        want = pow(2, v - 1, v) == 1
        if bool(got[i]) != want:
            bad += 1
            if bad < 5:
                print("MISMATCH", hex(v), bool(got[i]), want)
    print(f"correctness: {len(cases)} cases, {bad} mismatches")
    assert bad == 0, "kernel wrong"

    # ---- throughput ----
    for batch in (1 << 18, 1 << 20):
        vals = [int.from_bytes(rng.bytes(63), "little") | (1 << 498) | 1
                for _ in range(4096)]
        base = cp.asarray(to_limbs(vals))
        limbs = cp.tile(base, (batch // 4096, 1))
        out = cp.zeros(batch, dtype=cp.uint8)
        cp.cuda.runtime.deviceSynchronize()
        t0 = time.time()
        kern(((batch + 255) // 256,), (256,), (limbs, out, batch))
        cp.cuda.runtime.deviceSynchronize()
        dt = time.time() - t0
        print(f"throughput: {batch} tests in {dt:.3f}s = "
              f"{batch / dt:,.0f} tests/s")


if __name__ == "__main__":
    main()
