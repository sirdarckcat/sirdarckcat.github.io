/* test_fm_common.c -- fm_exp_words (64-bit operations, fm_common.h) against the 128-bit formulas it replaced:
 *     E = n + Rb - 1;  c = ceil(E / 2^t);  B = c * 2^t - E;  B <<= 128 - t;  (bh, bl) = (B >> 64, B)
 * for random and edge-case n of 41 to 100 bits (low word wrapping, B = 0, all ones, powers of two), t = bits - 6, Rb = 90 and 104.
 *     gcc -O2 -o test_fm_common test_fm_common.c && ./test_fm_common      (a few seconds; must print 0 mismatches)
 */
#include <stdio.h>
#include <stdlib.h>
#include "fm_common.h"
static uint64_t s = 88172645463325252ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static void old_exp(u128 n, int t, int Rb, uint64_t *bh, uint64_t *bl, int *c_out) {
    u128 E = n + (Rb - 1);
    u128 c = (E + (((u128)1 << t) - 1)) >> t;
    u128 B = (c << t) - E;
    B <<= 128 - t;
    *bh = (uint64_t)(B >> 64); *bl = (uint64_t)B; *c_out = (int)c;
}
int main(void) {
    long bad = 0, tot = 0, edge = 0; int tcount[130] = {0};
    for (long it = 0; it < 30000000; it++) {
        int bits = 41 + (int)(rnd() % 60);                       /* 41..100 */
        u128 n = ((u128)rnd() << 64) | rnd();
        n >>= 128 - bits; n |= (u128)1 << (bits - 1); n |= 1;
        int kind = (int)(rnd() % 8);
        if (kind == 1) n = (n & ~(u128)((1ull << 40) - 1)) | ((u128)0xFFFFFFFFFFull);                           /* low bits all ones */
        if (kind == 2) { uint64_t lo = 0 - (uint64_t)(rnd() % 200); n = (n & ~(u128)0xFFFFFFFFFFFFFFFFull) | lo; n |= 1; }   /* low word near 2^64: El wraps */
        if (kind == 3) { int t = bits - 6; u128 E = n; E &= ~(((u128)1 << t) - 1); E -= 1; /* make n + Rb - 1 a multiple of 2^t for Rb=104 */ if (E > 103) n = E - 103 + ((u128)1 << t); n |= 1; }
        if (kind == 4) n = ((u128)1 << (bits - 1)) | 1;
        if (kind == 5) n = (((u128)1 << bits) - 1);
        bits = fm_bitlen(n);
        if (bits < 41 || bits > 100) continue;
        int t = bits - 6;
        for (int Rb = 90; Rb <= 104; Rb += 14) {
            if (Rb == 90 && bits > 86) continue;
            uint64_t bh0, bl0, bh1, bl1; int c0, c1;
            old_exp(n, t, Rb, &bh0, &bl0, &c0);
            c1 = fm_exp_words(n, t, Rb, &bh1, &bl1);
            tot++; tcount[t]++;
            if (c0 != c1 || bh0 != bh1 || bl0 != bl1) { if (bad < 5) printf("MISMATCH n=%016llx%016llx t=%d Rb=%d: old c=%d bh=%llx bl=%llx  new c=%d bh=%llx bl=%llx\n", (unsigned long long)(n >> 64), (unsigned long long)n, t, Rb, c0, (unsigned long long)bh0, (unsigned long long)bl0, c1, (unsigned long long)bh1, (unsigned long long)bl1); bad++; }
            if (bh0 == 0 && bl0 == 0) edge++;
            if (c0 < 1 || c0 > Rb) { printf("c out of range %d (Rb %d t %d)\n", c0, Rb, t); bad++; }
        }
    }
    int lo_t = 999, hi_t = 0; for (int t = 0; t < 130; t++) if (tcount[t]) { if (t < lo_t) lo_t = t; if (t > hi_t) hi_t = t; }
    printf("%ld comparisons (t from %d to %d, all of them hit; B == 0 in %ld cases), %ld mismatches\n", tot, lo_t, hi_t, edge, bad);
    return bad != 0;
}
