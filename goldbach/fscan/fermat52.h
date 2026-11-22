/* fermat52.h -- base-2 Fermat tests, 24 at a time, with AVX-512 IFMA (52-bit limbs, 2 limbs).
 *
 * n odd, 2^40 < n < 2^100.  Returns bit i set when 2^(n_i - 1) = 1 (mod n_i).
 *
 * Montgomery squaring with R = 2^104 keeps the residue a plain power of two, as in tscan.c: if
 * y = 2^u (mod n) then y*y/R = 2^(2u - 104), so with v = u - 104 a squaring doubles v and a doubling
 * of y adds 1.  Starting from y = 2^(104 - c), v = -c, and feeding the t bits of B = c*2^t - (n + 103)
 * gives v = -(n + 103), u = 1 - n: the result is 2^(1-n), which is 1 exactly when n is a base-2
 * probable prime.  All 24 lanes run the same t (from the largest n of the batch).
 * Bounds: inputs < 4n, outputs of a squaring < 2n (needs 16n <= R), so no reduction inside the loop.
 * 26 vector operations per squaring of 8 numbers, 15 of them multiply-adds.
 * One squaring is a chain of about 40 cycles (each multiply-add waits for the previous one: z0 -> m0 -> z1 -> m1 -> carry),
 * while the 26 operations need only 13 cycles on two vector ports, so three independent groups of 8 leave the ports idle
 * a part of the time.  FM_GROUPS = 4 (32 numbers a round, the default) is about 12% faster per test than 3 on Sapphire
 * and Emerald Rapids; 5 and 6 gain nothing more.
 */
#include <immintrin.h>
#include <stdint.h>
#include "fm_common.h"
#define M52 ((1ull << 52) - 1)

#ifndef FM_GROUPS
#define FM_GROUPS 4                     /* independent groups of 8 numbers per round */
#endif
typedef struct { uint64_t a0[8], a1[8], n0[8], n1[8], ni[8], bh[8], bl[8]; } f52_lanes;

static inline void f52_setup(f52_lanes *L, int i, u128 n, int t) {
    uint64_t lo = (uint64_t)n, hi = (uint64_t)(n >> 64);
    L->n0[i] = lo & M52; L->n1[i] = (lo >> 52) | (hi << 12); L->ni[i] = fm_inv_neg(lo, 4) & M52;
    int e = 104 - fm_exp_words(n, t, 104, &L->bh[i], &L->bl[i]);
    if (e <= fm_bitlen(n)) {                             /* y = 2^e < 2n, no reduction: always for n of 71 bits or more (c >= 33), not always below */
        L->a0[i] = e < 52 ? 1ull << e : 0; L->a1[i] = e < 52 ? 0 : 1ull << (e - 52);
    } else {
        u128 y = (u128)1 << e;
        if (y >= 4 * n) y %= n;
        L->a0[i] = (uint64_t)y & M52; L->a1[i] = (uint64_t)(y >> 52);
    }
}

/* one Montgomery squaring with optional doubling (shift count b = 0 or 1 per lane).
 * a0 may carry garbage above bit 52: it is only ever used as a multiplicand, and the multiply-add
 * instructions read the low 52 bits.  a1 < 2^50, so 2*a1 fits.  The first reduction carry is 1
 * exactly when z0 is not zero, because z0 + lo(m0*n0) is 0 or 2^52. */
#define F52_STEP(a0, a1, n0, n1, ni, b) do {                                   \
    __m512i ad = _mm512_add_epi64(a1, a1);                                      \
    __m512i z0 = _mm512_madd52lo_epu64(zero, a0, a0);                           \
    __m512i z1 = _mm512_madd52hi_epu64(zero, a0, a0);                           \
    __m512i z2 = _mm512_madd52lo_epu64(zero, a1, a1);                           \
    __m512i z3 = _mm512_madd52hi_epu64(zero, a1, a1);                           \
    z1 = _mm512_madd52lo_epu64(z1, a0, ad);                                     \
    z2 = _mm512_madd52hi_epu64(z2, a0, ad);                                     \
    __m512i m0 = _mm512_madd52lo_epu64(zero, z0, ni);                           \
    z1 = _mm512_mask_add_epi64(z1, _mm512_test_epi64_mask(z0, z0), z1, one);    \
    z1 = _mm512_madd52hi_epu64(z1, m0, n0);                                     \
    z1 = _mm512_madd52lo_epu64(z1, m0, n1);                                     \
    z2 = _mm512_madd52hi_epu64(z2, m0, n1);                                     \
    __m512i m1 = _mm512_madd52lo_epu64(zero, z1, ni);                           \
    __m512i c1 = _mm512_srli_epi64(_mm512_madd52lo_epu64(z1, m1, n0), 52);      \
    z2 = _mm512_madd52hi_epu64(z2, m1, n0);                                     \
    z2 = _mm512_madd52lo_epu64(z2, m1, n1);                                     \
    z2 = _mm512_add_epi64(z2, c1);                                              \
    z3 = _mm512_madd52hi_epu64(z3, m1, n1);                                     \
    a0 = _mm512_sllv_epi64(z2, b); z3 = _mm512_sllv_epi64(z3, b);               \
    a1 = _mm512_add_epi64(z3, _mm512_srli_epi64(a0, 52));                       \
} while (0)

/* run t squarings on FM_GROUPS independent groups of 8 lanes (independent dependency chains keep both vector ports
   busy); cnt = number of lanes in use (1..F52_LANES), n[] their moduli */
#define F52_LANES (8 * FM_GROUPS)
#if F52_LANES > 32
#error "FM_GROUPS > 4: the result of f52_run is a 32-bit mask, one bit per lane"
#endif
static inline unsigned f52_run(f52_lanes *LL, const u128 *n, int cnt, int t) {
    const __m512i zero = _mm512_setzero_si512(), one = _mm512_set1_epi64(1);
    __m512i A0[FM_GROUPS], A1[FM_GROUPS], N0[FM_GROUPS], N1[FM_GROUPS], NI[FM_GROUPS], BB[FM_GROUPS];
    for (int g = 0; g < FM_GROUPS; g++) {
        A0[g] = _mm512_loadu_si512(LL[g].a0); A1[g] = _mm512_loadu_si512(LL[g].a1);
        N0[g] = _mm512_loadu_si512(LL[g].n0); N1[g] = _mm512_loadu_si512(LL[g].n1); NI[g] = _mm512_loadu_si512(LL[g].ni);
        BB[g] = _mm512_loadu_si512(LL[g].bh);
    }
    int first = t < 64 ? t : 64;
    for (int phase = 0; phase < 2; phase++) {
        int it = phase == 0 ? first : t - first;
        for (int i = 0; i < it; i++) {
            for (int g = 0; g < FM_GROUPS; g++) {
                __m512i sb = _mm512_srli_epi64(BB[g], 63);
                BB[g] = _mm512_slli_epi64(BB[g], 1);
                F52_STEP(A0[g], A1[g], N0[g], N1[g], NI[g], sb);
            }
        }
        for (int g = 0; g < FM_GROUPS; g++) BB[g] = _mm512_loadu_si512(LL[g].bl);
    }
    unsigned res = 0;
    for (int g = 0; g < FM_GROUPS; g++) {
        uint64_t r0[8], r1[8];
        _mm512_storeu_si512(r0, A0[g]); _mm512_storeu_si512(r1, A1[g]);
        for (int l = 0; l < 8; l++) {
            int i = g * 8 + l;
            if (i >= cnt) break;
            u128 y = ((u128)r1[l] << 52) + (r0[l] & M52), m = n[i];      /* y < 4n */
            y -= (m << 1) & -(u128)(y >= (m << 1));
            y -= m & -(u128)(y >= m);
            res |= (unsigned)(y == 1) << i;
        }
    }
    return res;
}

/* convenience: test cnt <= F52_LANES numbers */
static inline unsigned f52_test(const u128 *n, int cnt) {
    f52_lanes LL[FM_GROUPS];
    u128 mx = 0;
    for (int i = 0; i < cnt; i++) if (n[i] > mx) mx = n[i];
    int t = fm_bitlen(mx) - 6;
    for (int i = 0; i < F52_LANES; i++) f52_setup(&LL[i >> 3], i & 7, i < cnt ? n[i] : n[0], t);
    return f52_run(LL, n, cnt, t);
}

/* the names fscan.c and test_fermat.c use for whichever kernel is compiled in */
#define FM_W 8
#define FM_LANES F52_LANES
typedef f52_lanes fm_lanes_t;
#define fm_setup f52_setup
#define fm_run f52_run
#define fm_test f52_test
