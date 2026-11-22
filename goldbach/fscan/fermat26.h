/* fermat26.h -- base-2 Fermat tests, 12 at a time, with AVX2 only (26-bit limbs, 4 limbs).
 *
 * The same test as fermat52.h for CPUs without AVX-512 IFMA (for example Zen 2/3, Haswell to
 * Skylake): n odd, 2^40 < n < 2^100, returns bit i set when 2^(n_i - 1) = 1 (mod n_i).
 *
 * Montgomery squaring with R = 2^104 = (2^26)^4 keeps the residue a plain power of two: if
 * y = 2^u (mod n) then y*y/R = 2^(2u - 104), so with v = u - 104 a squaring doubles v and a doubling
 * of y adds 1.  Starting from y = 2^(104 - c), v = -c, and feeding the t bits of B = c*2^t - (n + 103)
 * gives v = -(n + 103), u = 1 - n: the result is 2^(1-n), which is 1 exactly when n is a base-2
 * probable prime.  All lanes run the same t (from the largest n of the batch).
 * Bounds: inputs < 4n, outputs of a squaring < 2n (needs 16n <= R), so no reduction inside the loop.
 * The 32x32->64 multiply reads the low 32 bits of each 64-bit lane; every operand is below 2^27,
 * except in m = z*n' mod 2^26 where only the low 26 bits of z matter.  Column sums stay below 2^56.
 * 30 multiplies and about 47 other vector operations per squaring of 4 numbers.
 */
#include <immintrin.h>
#include <stdint.h>
typedef unsigned __int128 u128;
#define M26 ((1ull << 26) - 1)
#define FM_W 4                         /* lanes per vector */
#ifndef FM_GROUPS
#define FM_GROUPS 3                    /* independent vectors per round */
#endif
#define FM_LANES (FM_W * FM_GROUPS)

typedef struct { uint64_t a[4][4], n[4][4], ni[4], bh[4], bl[4]; } fm_lanes_t __attribute__((aligned(32)));

static inline void fm_setup(fm_lanes_t *L, int i, u128 n, int t) {
    uint64_t lo = (uint64_t)n;
    uint64_t x = (3 * lo) ^ 2;                           /* inverse of n mod 2^64 by Newton */
    x *= 2 - lo * x; x *= 2 - lo * x; x *= 2 - lo * x; x *= 2 - lo * x;
    L->ni[i] = (0 - x) & M26;
    for (int j = 0; j < 4; j++) L->n[j][i] = (uint64_t)(n >> (26 * j)) & M26;
    u128 E = n + 103;
    u128 c = (E + (((u128)1 << t) - 1)) >> t;            /* ceil(E / 2^t), 1 <= c <= 104 by the choice of t */
    u128 B = (c << t) - E;                               /* 0 <= B < 2^t */
    B <<= 128 - t;                                       /* first bit to use on top */
    L->bh[i] = (uint64_t)(B >> 64); L->bl[i] = (uint64_t)B;
    int e = 104 - (int)c;
    u128 y = (u128)1 << e;
    if (y >= 4 * n) y %= n;
    for (int j = 0; j < 4; j++) L->a[j][i] = (uint64_t)(y >> (26 * j)) & M26;
}

#define FM_MUL(x, y) _mm256_mul_epu32(x, y)
#define FM_ADD(x, y) _mm256_add_epi64(x, y)
/* one reduction round: make column zi a multiple of 2^26 and carry it into the next column */
#define FM_RED(zi, zj, zk, zl, zm) do {                                         \
    __m256i m = _mm256_and_si256(FM_MUL(zi, ni), mask);                         \
    zi = FM_ADD(zi, FM_MUL(m, n0)); zj = FM_ADD(zj, FM_MUL(m, n1));             \
    zk = FM_ADD(zk, FM_MUL(m, n2)); zl = FM_ADD(zl, FM_MUL(m, n3));             \
    zj = FM_ADD(zj, _mm256_srli_epi64(zi, 26));                                 \
    (void)zm;                                                                   \
} while (0)

/* one Montgomery squaring of the 4 numbers of group g, then a doubling where the top bit of e is set */
#define FM_STEP(g) do {                                                         \
    __m256i a0 = A[g][0], a1 = A[g][1], a2 = A[g][2], a3 = A[g][3];             \
    const __m256i n0 = N[g][0], n1 = N[g][1], n2 = N[g][2], n3 = N[g][3], ni = NI[g]; \
    __m256i b = _mm256_srli_epi64(E[g], 63);                                    \
    E[g] = _mm256_slli_epi64(E[g], 1);                                          \
    __m256i d1 = FM_ADD(a1, a1), d2 = FM_ADD(a2, a2), d3 = FM_ADD(a3, a3);      \
    __m256i z0 = FM_MUL(a0, a0);                                                \
    __m256i z1 = FM_MUL(a0, d1);                                                \
    __m256i z2 = FM_ADD(FM_MUL(a0, d2), FM_MUL(a1, a1));                        \
    __m256i z3 = FM_ADD(FM_MUL(a0, d3), FM_MUL(a1, d2));                        \
    __m256i z4 = FM_ADD(FM_MUL(a1, d3), FM_MUL(a2, a2));                        \
    __m256i z5 = FM_MUL(a2, d3);                                                \
    __m256i z6 = FM_MUL(a3, a3);                                                \
    FM_RED(z0, z1, z2, z3, z4);                                                 \
    FM_RED(z1, z2, z3, z4, z5);                                                 \
    FM_RED(z2, z3, z4, z5, z6);                                                 \
    FM_RED(z3, z4, z5, z6, z6);                                                 \
    z4 = _mm256_sllv_epi64(z4, b); z5 = _mm256_sllv_epi64(z5, b); z6 = _mm256_sllv_epi64(z6, b); \
    z5 = FM_ADD(z5, _mm256_srli_epi64(z4, 26));                                 \
    z6 = FM_ADD(z6, _mm256_srli_epi64(z5, 26));                                 \
    A[g][0] = _mm256_and_si256(z4, mask); A[g][1] = _mm256_and_si256(z5, mask); \
    A[g][2] = _mm256_and_si256(z6, mask); A[g][3] = _mm256_srli_epi64(z6, 26);  \
} while (0)

/* run t squarings on FM_GROUPS groups of 4 lanes; cnt = number of lanes in use, n[] their moduli */
static inline unsigned fm_run(fm_lanes_t *LL, const u128 *n, int cnt, int t) {
    const __m256i mask = _mm256_set1_epi64x(M26);
    __m256i A[FM_GROUPS][4], N[FM_GROUPS][4], NI[FM_GROUPS], E[FM_GROUPS];
    for (int g = 0; g < FM_GROUPS; g++) {
        for (int j = 0; j < 4; j++) { A[g][j] = _mm256_load_si256((const __m256i *)LL[g].a[j]); N[g][j] = _mm256_load_si256((const __m256i *)LL[g].n[j]); }
        NI[g] = _mm256_load_si256((const __m256i *)LL[g].ni); E[g] = _mm256_load_si256((const __m256i *)LL[g].bh);
    }
    int first = t < 64 ? t : 64;
    for (int phase = 0; phase < 2; phase++) {
        int it = phase == 0 ? first : t - first;
        for (int i = 0; i < it; i++)
            for (int g = 0; g < FM_GROUPS; g++) FM_STEP(g);
        for (int g = 0; g < FM_GROUPS; g++) E[g] = _mm256_load_si256((const __m256i *)LL[g].bl);
    }
    unsigned res = 0;
    for (int g = 0; g < FM_GROUPS; g++) {
        uint64_t r[4][4] __attribute__((aligned(32)));
        for (int j = 0; j < 4; j++) _mm256_store_si256((__m256i *)r[j], A[g][j]);
        for (int l = 0; l < FM_W; l++) {
            int i = g * FM_W + l;
            if (i >= cnt) break;
            u128 y = (u128)r[0][l] + ((u128)r[1][l] << 26) + ((u128)r[2][l] << 52) + ((u128)r[3][l] << 78), m = n[i];   /* y < 4n */
            y -= (m << 1) & -(u128)(y >= (m << 1));
            y -= m & -(u128)(y >= m);
            res |= (unsigned)(y == 1) << i;
        }
    }
    return res;
}

/* convenience: test cnt <= FM_LANES numbers */
static inline unsigned fm_test(const u128 *n, int cnt) {
    fm_lanes_t LL[FM_GROUPS];
    u128 mx = 0;
    for (int i = 0; i < cnt; i++) if (n[i] > mx) mx = n[i];
    int b = 0; for (u128 x = mx; x; x >>= 1) b++;
    int t = b - 6;
    for (int i = 0; i < FM_LANES; i++) fm_setup(&LL[i / FM_W], i % FM_W, i < cnt ? n[i] : n[0], t);
    return fm_run(LL, n, cnt, t);
}
