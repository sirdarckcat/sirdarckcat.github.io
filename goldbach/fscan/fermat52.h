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

/* run t squarings on three groups of 8 lanes (three independent dependency chains keep both vector
   ports busy); cnt = number of lanes in use (1..24), n[] their moduli */
#define F52_LANES 24
static inline unsigned f52_run(f52_lanes *LL, const u128 *n, int cnt, int t) {
    const __m512i zero = _mm512_setzero_si512(), one = _mm512_set1_epi64(1);
    __m512i a0 = _mm512_loadu_si512(LL[0].a0), a1 = _mm512_loadu_si512(LL[0].a1);
    __m512i n0 = _mm512_loadu_si512(LL[0].n0), n1 = _mm512_loadu_si512(LL[0].n1), ni = _mm512_loadu_si512(LL[0].ni);
    __m512i e0 = _mm512_loadu_si512(LL[1].a0), e1 = _mm512_loadu_si512(LL[1].a1);
    __m512i p0 = _mm512_loadu_si512(LL[1].n0), p1 = _mm512_loadu_si512(LL[1].n1), pi = _mm512_loadu_si512(LL[1].ni);
    __m512i g0 = _mm512_loadu_si512(LL[2].a0), g1 = _mm512_loadu_si512(LL[2].a1);
    __m512i q0 = _mm512_loadu_si512(LL[2].n0), q1 = _mm512_loadu_si512(LL[2].n1), qi = _mm512_loadu_si512(LL[2].ni);
    __m512i ba = _mm512_loadu_si512(LL[0].bh), bb = _mm512_loadu_si512(LL[1].bh), bc = _mm512_loadu_si512(LL[2].bh);
    int first = t < 64 ? t : 64;
    for (int phase = 0; phase < 2; phase++) {
        int it = phase == 0 ? first : t - first;
        for (int i = 0; i < it; i++) {
            __m512i sa = _mm512_srli_epi64(ba, 63), sb = _mm512_srli_epi64(bb, 63), sc = _mm512_srli_epi64(bc, 63);
            ba = _mm512_slli_epi64(ba, 1); bb = _mm512_slli_epi64(bb, 1); bc = _mm512_slli_epi64(bc, 1);
            F52_STEP(a0, a1, n0, n1, ni, sa);
            F52_STEP(e0, e1, p0, p1, pi, sb);
            F52_STEP(g0, g1, q0, q1, qi, sc);
        }
        ba = _mm512_loadu_si512(LL[0].bl); bb = _mm512_loadu_si512(LL[1].bl); bc = _mm512_loadu_si512(LL[2].bl);
    }
    uint64_t r0[24], r1[24];
    _mm512_storeu_si512(r0, a0); _mm512_storeu_si512(r1, a1);
    _mm512_storeu_si512(r0 + 8, e0); _mm512_storeu_si512(r1 + 8, e1);
    _mm512_storeu_si512(r0 + 16, g0); _mm512_storeu_si512(r1 + 16, g1);
    unsigned res = 0;
    for (int i = 0; i < cnt; i++) {
        u128 y = ((u128)r1[i] << 52) + (r0[i] & M52), m = n[i];      /* y < 4n */
        y -= (m << 1) & -(u128)(y >= (m << 1));
        y -= m & -(u128)(y >= m);
        res |= (unsigned)(y == 1) << i;
    }
    return res;
}

/* convenience: test cnt <= 24 numbers */
static inline unsigned f52_test(const u128 *n, int cnt) {
    f52_lanes LL[3];
    u128 mx = 0;
    for (int i = 0; i < cnt; i++) if (n[i] > mx) mx = n[i];
    int b = 0; for (u128 x = mx; x; x >>= 1) b++;
    int t = b - 6;
    for (int i = 0; i < F52_LANES; i++) f52_setup(&LL[i >> 3], i & 7, i < cnt ? n[i] : n[0], t);
    return f52_run(LL, n, cnt, t);
}

/* the names fscan.c and test_fermat.c use for whichever kernel is compiled in */
#define FM_W 8
#define FM_GROUPS 3
#define FM_LANES F52_LANES
typedef f52_lanes fm_lanes_t;
#define fm_setup f52_setup
#define fm_run f52_run
#define fm_test f52_test
