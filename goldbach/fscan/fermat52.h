/* fermat52.h -- base-2 Fermat tests, 16 at a time, with AVX-512 IFMA (52-bit limbs, 2 limbs).
 *
 * n odd, 2^40 < n < 2^100.  Returns bit i set when 2^(n_i - 1) = 1 (mod n_i).
 *
 * Montgomery squaring with R = 2^104 keeps the residue a plain power of two, as in tscan.c: if
 * y = 2^u (mod n) then y*y/R = 2^(2u - 104), so with v = u - 104 a squaring doubles v and a doubling
 * of y adds 1.  Starting from y = 2^(104 - c), v = -c, and feeding the t bits of B = c*2^t - (n + 103)
 * gives v = -(n + 103), u = 1 - n: the result is 2^(1-n), which is 1 exactly when n is a base-2
 * probable prime.  All 16 lanes run the same t (from the largest n of the batch).
 * Bounds: inputs < 4n, outputs of a squaring < 2n (needs 16n <= R), so no reduction inside the loop.
 */
#include <immintrin.h>
#include <stdint.h>
typedef unsigned __int128 u128;
#define M52 ((1ull << 52) - 1)

typedef struct { uint64_t a0[8], a1[8], n0[8], n1[8], ni[8], bh[8], bl[8]; } f52_lanes;

static inline void f52_setup(f52_lanes *L, int i, u128 n, int t) {
    uint64_t lo = (uint64_t)n;
    uint64_t x = (3 * lo) ^ 2;                           /* inverse of n mod 2^64 by Newton */
    x *= 2 - lo * x; x *= 2 - lo * x; x *= 2 - lo * x; x *= 2 - lo * x;
    L->n0[i] = lo & M52; L->n1[i] = (uint64_t)(n >> 52); L->ni[i] = (0 - x) & M52;
    u128 E = n + 103;
    u128 c = (E + (((u128)1 << t) - 1)) >> t;            /* ceil(E / 2^t), 1 <= c <= 104 by the choice of t */
    u128 B = (c << t) - E;                               /* 0 <= B < 2^t */
    B <<= 128 - t;                                       /* first bit to use on top */
    L->bh[i] = (uint64_t)(B >> 64); L->bl[i] = (uint64_t)B;
    int e = 104 - (int)c;
    u128 y = (u128)1 << e;
    if (y >= 4 * n) y %= n;
    L->a0[i] = (uint64_t)y & M52; L->a1[i] = (uint64_t)(y >> 52);
}

/* one Montgomery squaring with optional doubling (shift count b = 0 or 1 per lane) */
#define F52_STEP(a0, a1, n0, n1, ni, b) do {                                   \
    __m512i z0 = _mm512_madd52lo_epu64(zero, a0, a0);                           \
    __m512i z1 = _mm512_madd52hi_epu64(zero, a0, a0);                           \
    __m512i xl = _mm512_madd52lo_epu64(zero, a0, a1);                           \
    __m512i xh = _mm512_madd52hi_epu64(zero, a0, a1);                           \
    __m512i z2 = _mm512_madd52lo_epu64(_mm512_add_epi64(xh, xh), a1, a1);       \
    __m512i z3 = _mm512_madd52hi_epu64(zero, a1, a1);                           \
    z1 = _mm512_add_epi64(z1, _mm512_add_epi64(xl, xl));                        \
    __m512i m0 = _mm512_madd52lo_epu64(zero, z0, ni);                           \
    __m512i c0 = _mm512_srli_epi64(_mm512_madd52lo_epu64(z0, m0, n0), 52);      \
    z1 = _mm512_madd52hi_epu64(z1, m0, n0);                                     \
    z1 = _mm512_madd52lo_epu64(z1, m0, n1);                                     \
    z1 = _mm512_add_epi64(z1, c0);                                              \
    z2 = _mm512_madd52hi_epu64(z2, m0, n1);                                     \
    __m512i m1 = _mm512_madd52lo_epu64(zero, z1, ni);                           \
    __m512i c1 = _mm512_srli_epi64(_mm512_madd52lo_epu64(z1, m1, n0), 52);      \
    z2 = _mm512_madd52hi_epu64(z2, m1, n0);                                     \
    z2 = _mm512_madd52lo_epu64(z2, m1, n1);                                     \
    z2 = _mm512_add_epi64(z2, c1);                                              \
    z3 = _mm512_madd52hi_epu64(z3, m1, n1);                                     \
    z2 = _mm512_sllv_epi64(z2, b); z3 = _mm512_sllv_epi64(z3, b);               \
    a0 = _mm512_and_si512(z2, mask);                                            \
    a1 = _mm512_add_epi64(z3, _mm512_srli_epi64(z2, 52));                       \
} while (0)

/* run t squarings on two groups of 8 lanes; cnt = number of lanes in use (1..16), n[] their moduli */
static inline unsigned f52_run(f52_lanes *LA, f52_lanes *LB, const u128 *n, int cnt, int t) {
    const __m512i zero = _mm512_setzero_si512(), mask = _mm512_set1_epi64(M52);
    __m512i a0 = _mm512_loadu_si512(LA->a0), a1 = _mm512_loadu_si512(LA->a1);
    __m512i n0 = _mm512_loadu_si512(LA->n0), n1 = _mm512_loadu_si512(LA->n1), ni = _mm512_loadu_si512(LA->ni);
    __m512i e0 = _mm512_loadu_si512(LB->a0), e1 = _mm512_loadu_si512(LB->a1);
    __m512i p0 = _mm512_loadu_si512(LB->n0), p1 = _mm512_loadu_si512(LB->n1), pi = _mm512_loadu_si512(LB->ni);
    __m512i ba = _mm512_loadu_si512(LA->bh), bb = _mm512_loadu_si512(LB->bh);
    int first = t < 64 ? t : 64;
    for (int phase = 0; phase < 2; phase++) {
        int it = phase == 0 ? first : t - first;
        for (int i = 0; i < it; i++) {
            __m512i sa = _mm512_srli_epi64(ba, 63), sb = _mm512_srli_epi64(bb, 63);
            ba = _mm512_slli_epi64(ba, 1); bb = _mm512_slli_epi64(bb, 1);
            F52_STEP(a0, a1, n0, n1, ni, sa);
            F52_STEP(e0, e1, p0, p1, pi, sb);
        }
        ba = _mm512_loadu_si512(LA->bl); bb = _mm512_loadu_si512(LB->bl);
    }
    uint64_t r0[16], r1[16];
    _mm512_storeu_si512(r0, a0); _mm512_storeu_si512(r1, a1);
    _mm512_storeu_si512(r0 + 8, e0); _mm512_storeu_si512(r1 + 8, e1);
    unsigned res = 0;
    for (int i = 0; i < cnt; i++) {
        u128 y = ((u128)r1[i] << 52) + r0[i];
        while (y >= n[i]) y -= n[i];
        if (y == 1) res |= 1u << i;
    }
    return res;
}

/* convenience: test cnt <= 16 numbers */
static inline unsigned f52_test16(const u128 *n, int cnt) {
    f52_lanes LA, LB;
    u128 mx = 0;
    for (int i = 0; i < cnt; i++) if (n[i] > mx) mx = n[i];
    int b = 0; for (u128 x = mx; x; x >>= 1) b++;
    int t = b - 6;
    for (int i = 0; i < 16; i++) {
        u128 v = i < cnt ? n[i] : n[0];
        if (i < 8) f52_setup(&LA, i, v, t); else f52_setup(&LB, i - 8, v, t);
    }
    return f52_run(&LA, &LB, n, cnt, t);
}
