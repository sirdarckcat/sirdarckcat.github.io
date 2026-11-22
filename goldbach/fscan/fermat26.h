/* fermat26.h -- base-2 Fermat tests, 12 at a time, with AVX2 only.
 *
 * The same test as fermat52.h for CPUs without AVX-512 IFMA (for example Zen 2/3, Haswell to
 * Skylake): n odd, 2^40 < n < 2^100, returns bit i set when 2^(n_i - 1) = 1 (mod n_i).
 * The 32x32->64 multiply (vpmuludq) reads the low 32 bits of each 64-bit lane.
 *
 * Montgomery squaring with R = 2^Rb keeps the residue a plain power of two: if y = 2^u (mod n) then
 * y*y/R = 2^(2u - Rb), so with v = u - Rb a squaring doubles v and a doubling of y adds 1.  Starting
 * from y = 2^(Rb - c), v = -c, and feeding the t bits of B = c*2^t - (n + Rb - 1) gives
 * v = -(n + Rb - 1), u = 1 - n: the result is 2^(1-n), which is 1 exactly when n is a base-2 probable
 * prime.  All lanes run the same t (from the largest n of the batch: t = bits(max n) - 6).
 * Bounds: inputs < 4n, outputs of a squaring < 2n (needs 16n <= R), so no reduction inside the loop.
 *
 * Two kernels, chosen by t (so by the size of the largest n of the batch):
 *   3 limbs of 30 bits, R = 2^90, n < 2^86 (7.7e25):   18 multiplies and 30 other vector operations
 *       per squaring of 4 numbers.  Every operand is below 2^31 and every column sum below 2^62
 *       (worst case 2^62.0 by the bounds in the comments of FM3_STEP; the largest value seen in
 *       millions of random and adversarial steps is 2^61.9), so nothing overflows 64 bits.
 *   4 limbs of 26 bits, R = 2^104, n < 2^100:          30 multiplies and about 47 other operations;
 *       used only when the batch holds a number of 87 bits or more.
 * Measured on one Emerald Rapids core built with -march=haswell (min of repeated runs): 1.3 to 1.7 times
 * as fast per test as the 4-limb kernel.  Zen 2 was not measured: its model in llvm-mca (vpmuludq on one
 * pipe) predicts about 1.55 times.  Compile with -DFM_GROUPS=4 to run 16 numbers per round (about 10%
 * faster again on Intel, neutral in the Zen 2 model).
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

#define W3 30                          /* limb width of the 3-limb kernel */
#define M3 ((1ull << W3) - 1)
#define FM3_TMAX 80                    /* t = bits(max n) - 6 <= 80, i.e. n < 2^86: then 16 n <= R = 2^90 */

typedef struct { uint64_t a[4][4], n[4][4], ni[4], bh[4], bl[4]; } fm_lanes_t __attribute__((aligned(32)));

/* ---- shared setup helpers */
static inline uint64_t fm_inv_neg(uint64_t lo, int iters) {          /* -lo^-1 mod 2^64, correct to 5 * 2^iters bits */
    uint64_t x = (3 * lo) ^ 2;
    for (int i = 0; i < iters; i++) x *= 2 - lo * x;
    return 0 - x;
}
static inline void fm_exponent(fm_lanes_t *L, int i, u128 n, int t, int Rb, int *e) {
    u128 E = n + (Rb - 1);
    u128 c = (E + (((u128)1 << t) - 1)) >> t;            /* ceil(E / 2^t), 1 <= c <= Rb by the choice of t */
    u128 B = (c << t) - E;                               /* 0 <= B < 2^t */
    B <<= 128 - t;                                       /* first bit to use on top */
    L->bh[i] = (uint64_t)(B >> 64); L->bl[i] = (uint64_t)B;
    *e = Rb - (int)c;
}

/* ================================================================ 3 limbs of 30 bits */

static inline void fm3_setup(fm_lanes_t *L, int i, u128 n, int t) {
    L->ni[i] = fm_inv_neg((uint64_t)n, 3) & M3;          /* 3 Newton steps give 40 >= 30 bits */
    for (int j = 0; j < 3; j++) L->n[j][i] = (uint64_t)(n >> (W3 * j)) & M3;
    int e; fm_exponent(L, i, n, t, 3 * W3, &e);
    u128 y = (u128)1 << e;
    if (y >= 4 * n) y %= n;
    for (int j = 0; j < 3; j++) L->a[j][i] = (uint64_t)(y >> (W3 * j)) & M3;
}

#define FM_MUL(x, y) _mm256_mul_epu32(x, y)
#define FM_ADD(x, y) _mm256_add_epi64(x, y)

/* One Montgomery squaring of the 4 numbers of group g, then a doubling where the top bit of E is set.
 * a < 4n, limbs a0, a1 < 2^30 and a2 < 2^28.  Columns z0..z4 of the square, with the cross terms
 * doubled (d1 = 2 a1, d2 = 2 a2 < 2^31): z0 < 2^60, z1 < 2^61, z2 < 1.5 * 2^60, z3 < 2^59, z4 < 2^56.
 * Three reductions m_i = z_i * n' mod 2^30 add m_i * n_j (< 2^60 each, n2 < 2^26) into column i+j, then
 * the carry z_i >> 30 into column i+1: the largest column is z1 after round 1 (< 2^62), z2 and z3 (the
 * latter after the doubling) stay under 3.5 * 2^60 < 2^62. */
#define FM3_STEP(g) do {                                                        \
    __m256i a0 = A[g][0], a1 = A[g][1], a2 = A[g][2];                           \
    const __m256i n0 = N[g][0], n1 = N[g][1], n2 = N[g][2], ni = NI[g];         \
    __m256i b = _mm256_srli_epi64(E[g], 63);                                    \
    E[g] = FM_ADD(E[g], E[g]);                                                  \
    __m256i d1 = FM_ADD(a1, a1), d2 = FM_ADD(a2, a2);                           \
    __m256i z0 = FM_MUL(a0, a0);                                                \
    __m256i z1 = FM_MUL(a0, d1);                                                \
    __m256i z2 = FM_ADD(FM_MUL(a0, d2), FM_MUL(a1, a1));                        \
    __m256i z3 = FM_MUL(a1, d2);                                                \
    __m256i z4 = FM_MUL(a2, a2);                                                \
    __m256i m = _mm256_and_si256(FM_MUL(z0, ni), mask);                         \
    z0 = FM_ADD(z0, FM_MUL(m, n0)); z1 = FM_ADD(z1, FM_MUL(m, n1));             \
    z2 = FM_ADD(z2, FM_MUL(m, n2));                                             \
    z1 = FM_ADD(z1, _mm256_srli_epi64(z0, W3));                                 \
    m = _mm256_and_si256(FM_MUL(z1, ni), mask);                                 \
    z1 = FM_ADD(z1, FM_MUL(m, n0)); z2 = FM_ADD(z2, FM_MUL(m, n1));             \
    z3 = FM_ADD(z3, FM_MUL(m, n2));                                             \
    z2 = FM_ADD(z2, _mm256_srli_epi64(z1, W3));                                 \
    m = _mm256_and_si256(FM_MUL(z2, ni), mask);                                 \
    z2 = FM_ADD(z2, FM_MUL(m, n0)); z3 = FM_ADD(z3, FM_MUL(m, n1));             \
    z4 = FM_ADD(z4, FM_MUL(m, n2));                                             \
    z3 = FM_ADD(z3, _mm256_srli_epi64(z2, W3));                                 \
    z3 = _mm256_sllv_epi64(z3, b); z4 = _mm256_sllv_epi64(z4, b);               \
    z4 = FM_ADD(z4, _mm256_srli_epi64(z3, W3));                                 \
    A[g][0] = _mm256_and_si256(z3, mask); A[g][1] = _mm256_and_si256(z4, mask); \
    A[g][2] = _mm256_srli_epi64(z4, W3);                                        \
} while (0)

static inline unsigned fm3_run(fm_lanes_t *LL, const u128 *n, int cnt, int t) {
    const __m256i mask = _mm256_set1_epi64x(M3);
    __m256i A[FM_GROUPS][3], N[FM_GROUPS][3], NI[FM_GROUPS], E[FM_GROUPS];
    for (int g = 0; g < FM_GROUPS; g++) {
        for (int j = 0; j < 3; j++) { A[g][j] = _mm256_load_si256((const __m256i *)LL[g].a[j]); N[g][j] = _mm256_load_si256((const __m256i *)LL[g].n[j]); }
        NI[g] = _mm256_load_si256((const __m256i *)LL[g].ni); E[g] = _mm256_load_si256((const __m256i *)LL[g].bh);
    }
    int first = t < 64 ? t : 64;
    for (int phase = 0; phase < 2; phase++) {
        int it = phase == 0 ? first : t - first;
        for (int i = 0; i < it; i++)
            for (int g = 0; g < FM_GROUPS; g++) FM3_STEP(g);
        for (int g = 0; g < FM_GROUPS; g++) E[g] = _mm256_load_si256((const __m256i *)LL[g].bl);
    }
    unsigned res = 0;
    for (int g = 0; g < FM_GROUPS; g++) {
        uint64_t r[3][4] __attribute__((aligned(32)));
        for (int j = 0; j < 3; j++) _mm256_store_si256((__m256i *)r[j], A[g][j]);
        for (int l = 0; l < FM_W; l++) {
            int i = g * FM_W + l;
            if (i >= cnt) break;
            u128 y = (u128)r[0][l] + ((u128)r[1][l] << W3) + ((u128)r[2][l] << (2 * W3)), m = n[i];   /* y < 4n */
            y -= (m << 1) & -(u128)(y >= (m << 1));
            y -= m & -(u128)(y >= m);
            res |= (unsigned)(y == 1) << i;
        }
    }
    return res;
}

/* ================================================================ 4 limbs of 26 bits (numbers of 87 to 100 bits) */

static inline void fm4_setup(fm_lanes_t *L, int i, u128 n, int t) {
    L->ni[i] = fm_inv_neg((uint64_t)n, 3) & M26;
    for (int j = 0; j < 4; j++) L->n[j][i] = (uint64_t)(n >> (26 * j)) & M26;
    int e; fm_exponent(L, i, n, t, 104, &e);
    u128 y = (u128)1 << e;
    if (y >= 4 * n) y %= n;
    for (int j = 0; j < 4; j++) L->a[j][i] = (uint64_t)(y >> (26 * j)) & M26;
}

/* one reduction round: make column zi a multiple of 2^26 and carry it into the next column */
#define FM_RED(zi, zj, zk, zl, zm) do {                                         \
    __m256i m = _mm256_and_si256(FM_MUL(zi, ni), mask);                         \
    zi = FM_ADD(zi, FM_MUL(m, n0)); zj = FM_ADD(zj, FM_MUL(m, n1));             \
    zk = FM_ADD(zk, FM_MUL(m, n2)); zl = FM_ADD(zl, FM_MUL(m, n3));             \
    zj = FM_ADD(zj, _mm256_srli_epi64(zi, 26));                                 \
    (void)zm;                                                                   \
} while (0)

#define FM4_STEP(g) do {                                                        \
    __m256i a0 = A[g][0], a1 = A[g][1], a2 = A[g][2], a3 = A[g][3];             \
    const __m256i n0 = N[g][0], n1 = N[g][1], n2 = N[g][2], n3 = N[g][3], ni = NI[g]; \
    __m256i b = _mm256_srli_epi64(E[g], 63);                                    \
    E[g] = FM_ADD(E[g], E[g]);                                                  \
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

static inline unsigned fm4_run(fm_lanes_t *LL, const u128 *n, int cnt, int t) {
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
            for (int g = 0; g < FM_GROUPS; g++) FM4_STEP(g);
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

/* ================================================================ interface (t = bits(max n of the batch) - 6) */

static inline void fm_setup(fm_lanes_t *L, int i, u128 n, int t) {
    if (t <= FM3_TMAX) fm3_setup(L, i, n, t); else fm4_setup(L, i, n, t);
}
/* run t squarings on FM_GROUPS groups of 4 lanes; cnt = number of lanes in use, n[] their moduli */
static inline unsigned fm_run(fm_lanes_t *LL, const u128 *n, int cnt, int t) {
    return t <= FM3_TMAX ? fm3_run(LL, n, cnt, t) : fm4_run(LL, n, cnt, t);
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
