// The fermat28 kernel source compiled for the CPU, driven by test lines on stdin.
//   g++ -O2 -DSTEPFILE='"fermat28_step_s1.cuh"' -I path/to/goldbach/fermat661/cuda -o harness harness.cpp
// Lines:  step X N b     -> "step Y"     x = limbs of X, n = limbs of N, np = fm28_inv_neg28(low word of N)
//         inv LO         -> "inv NP"
//         fermat N       -> "fermat F"   the whole kernel on cq = N, M = 0, k = 0
// Numbers in hexadecimal.
#include <cstdint>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
typedef unsigned int u32;
typedef unsigned long long u64;
#define __device__
#define __forceinline__ inline __attribute__((always_inline))
#define __global__
static inline int __clz(u32 x) { return __builtin_clz(x); }
struct { unsigned x; } blockIdx, blockDim, threadIdx;
#include STEPFILE
#include "fermat28_kernel.cuh"

static int hexdig(char c) { return c <= '9' ? c - '0' : c - 'a' + 10; }
// bits [lo, lo + width) of the hexadecimal number s
static u32 bits_of(const std::string &s, int lo, int width) {
    u32 v = 0;
    for (int b = 0; b < width; b++) {
        int pos = lo + b, d = pos / 4;
        if (d < (int)s.size() && ((hexdig(s[s.size() - 1 - d]) >> (pos % 4)) & 1)) v |= 1u << b;
    }
    return v;
}
int main() {
    char op[16], a[400], b[400]; unsigned bb;
    blockDim.x = 1; blockIdx.x = 0; threadIdx.x = 0;
    while (scanf("%15s", op) == 1) {
        if (!strcmp(op, "step")) {
            if (scanf("%399s %399s %u", a, b, &bb) != 3) return 1;
            std::string X(a), N(b);
            u32 x[NL], n[NL];
            for (int i = 0; i < NL; i++) { x[i] = bits_of(X, 28 * i, 28); n[i] = bits_of(N, 28 * i, 28); }
            fm28_step(x, n, fm28_inv_neg28(bits_of(N, 0, 32)), bb);
            printf("step ");
            for (int i = NL - 1; i >= 0; i--) printf("%07x", x[i]);
            printf("\n");
        } else if (!strcmp(op, "inv")) {
            if (scanf("%399s", a) != 1) return 1;
            printf("inv %07x\n", fm28_inv_neg28((u32)strtoul(a, 0, 16)));
        } else if (!strcmp(op, "fermat")) {
            if (scanf("%399s", a) != 1) return 1;
            std::string N(a);
            u32 cq[L32], Mv[L32]; int idx = 0; u32 k = 0; unsigned char out = 9;
            for (int j = 0; j < L32; j++) { cq[j] = bits_of(N, 32 * j, 32); Mv[j] = 0; }
            fermat28(cq, Mv, &idx, &k, &out, 1);
            printf("fermat %d\n", (int)out);
        } else return 1;
    }
    return 0;
}
