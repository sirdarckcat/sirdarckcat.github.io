#!/usr/bin/env python3
"""Wrap the CUDA source of gpu_fermat.py in a CPU test harness.

    mkharness.py path/to/gpu_fermat.py harness.c

The kernel text is embedded unchanged (only `extern "C"` is removed): the CUDA qualifiers are
defined away, `__clz` becomes `__builtin_clz`, and `blockIdx`, `blockDim`, `threadIdx` are
faked for one thread. The harness reads lines `fermat cq M k`, `sqr x n ninv`, `dbl x n 0`
(hexadecimal integers) and prints the kernel's answers.
"""
import sys
src = open(sys.argv[1]).read()
i = src.index("SRC = r'''") + len("SRC = r'''"); j = src.index("'''", i)
kernel = src[i:j].replace('extern "C" ', '')
pre = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#define LIMBS 21
#define __device__ static
#define __forceinline__ inline
#define __global__
#define __clz(x) __builtin_clz(x)
struct idx3 { unsigned x; };
static struct idx3 blockIdx = {0}, blockDim = {1}, threadIdx = {0};
'''
post = r'''
static void read_limbs(const char *hex, u32 *out) {
    size_t len = strlen(hex);
    for (int j = 0; j < L; j++) out[j] = 0;
    for (size_t p = 0; p < len; p++) {
        char ch = hex[len - 1 - p]; u32 v = (ch >= '0' && ch <= '9') ? ch - '0' : ch - 'a' + 10;
        out[p / 8] |= v << (4 * (p % 8));
    }
}
static void print_limbs(const u32 *x) { for (int j = L - 1; j >= 0; j--) printf("%08x", x[j]); }
int main(void) {
    static char op[16], a[400], b[400], c[400];
    while (scanf("%15s %399s %399s %399s", op, a, b, c) == 4) {
        if (!strcmp(op, "fermat")) {
            u32 cq[L], Mv[L]; read_limbs(a, cq); read_limbs(b, Mv);
            u32 k = (u32)strtoul(c, NULL, 16); int idx = 0; unsigned char out = 7;
            fermat2(cq, Mv, &idx, &k, &out, 1);
            printf("fermat %d\n", (int)out);
        } else if (!strcmp(op, "sqr")) {
            u32 x[L], n[L]; read_limbs(a, x); read_limbs(b, n);
            mont_sqr(x, n, (u32)strtoul(c, NULL, 16));
            printf("sqr "); print_limbs(x); printf("\n");
        } else if (!strcmp(op, "dbl")) {
            u32 x[L], n[L]; read_limbs(a, x); read_limbs(b, n);
            dbl_mod(x, n);
            printf("dbl "); print_limbs(x); printf("\n");
        }
    }
    return 0;
}
'''
open(sys.argv[2], "w").write(pre + kernel + post)
