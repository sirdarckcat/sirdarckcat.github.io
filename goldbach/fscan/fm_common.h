/* fm_common.h -- the part of the per-number setup of the Fermat kernels that does not depend on the limb size,
 * with 64-bit operations only (a variable 128-bit shift compiles to shld/shrd and compares, which are slow, and
 * microcoded on Zen 2).  Included by fermat52.h and fermat26.h.
 *
 * For an odd n and the batch constant t = bits(max n) - 6, with Rb the bit size of R = 2^Rb (104, or 90 for the 3-limb
 * kernel):  E = n + Rb - 1,  c = ceil(E / 2^t),  B = c 2^t - E = (-E) mod 2^t,  e = Rb - c.  The exponent bits are the
 * t bits of B, most significant first, stored top-aligned in 128 bits as (bh, bl); the start value is y = 2^e.
 */
#ifndef FM_COMMON_H
#define FM_COMMON_H
#include <stdint.h>
typedef unsigned __int128 u128;

static inline int fm_bitlen(u128 x) {                 /* number of bits of x (0 for 0) */
    uint64_t hi = (uint64_t)(x >> 64), lo = (uint64_t)x;
    return hi ? 128 - __builtin_clzll(hi) : lo ? 64 - __builtin_clzll(lo) : 0;
}

/* -lo^-1 mod 2^64, correct in the low 5 * 2^iters bits (so 3 steps give 40 bits, 4 steps 64) */
static inline uint64_t fm_inv_neg(uint64_t lo, int iters) {
    uint64_t x = (3 * lo) ^ 2;
    for (int i = 0; i < iters; i++) x *= 2 - lo * x;
    return 0 - x;
}

/* 1 <= t <= 126.  c is returned; bh, bl are the top-aligned bits of B. */
static inline int fm_exp_words(u128 n, int t, int Rb, uint64_t *bh, uint64_t *bl) {
    uint64_t nl = (uint64_t)n, nh = (uint64_t)(n >> 64);
    uint64_t El = nl + (uint64_t)(Rb - 1), Eh = nh + (El < nl);       /* E = n + Rb - 1 */
    uint64_t Bl = 0 - El, Bh = ~Eh + (El == 0);                         /* -E mod 2^128 */
    uint64_t c;
    if (t < 64) {
        uint64_t mask = (1ull << t) - 1;
        c = ((Eh << (64 - t)) | (El >> t)) + ((El & mask) != 0);       /* E >> t (E < 2^(t+7)), plus 1 if low bits are set */
        *bh = (Bl & mask) << (64 - t); *bl = 0;                         /* B << (128 - t), B < 2^t < 2^64 */
    } else {
        int s = t - 64;
        uint64_t mh = s ? (1ull << s) - 1 : 0;
        c = (Eh >> s) + ((El != 0) | ((Eh & mh) != 0));
        Bh &= mh;
        if (s) { *bh = (Bh << (64 - s)) | (Bl >> s); *bl = Bl << (64 - s); }   /* B << (128 - t) = B << (64 - s) */
        else   { *bh = Bl; *bl = 0; }
    }
    return (int)c;
}
#endif
