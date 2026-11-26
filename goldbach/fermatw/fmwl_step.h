/* fmwl_step.h -- the fmw step (Montgomery squaring times 2^b, 8 lanes, L limbs of 52 bits) as loops, for large L (32 .. 141):
 * the straight-line steps of gen_fmw.py stop paying above ~64 limbs (50,000 IFMAs of code at L = 128, accumulators spilled).
 *
 * Columns T[0 .. 2L] (64-bit lanes) live in a stack array.  Both phases go row by row and, inside a row, in blocks of BJ = 16
 * consecutive limbs j: the block's BJ + 1 columns are loaded into registers, take BJ lo and BJ hi products of one register operand
 * (a_i, or the Montgomery multiplier m_k) with BJ memory operands (a_j, or n_j), and are stored back: about 1.06 loads and 0.56
 * stores an IFMA.
 *   1. square: row i adds lo(a_i a_j) to T[i+j] and hi(a_i a_j) to T[i+j+1] for j > i; then T = 2 T + diagonal.
 *   2. reduce: row k: T[k] += T[k-1] >> 52; m = lo52(T[k] n'); T[k+j] += lo(m n_j), T[k+j+1] += hi(m n_j) for all j.
 *   3. Y = T[L .. 2L-1] (+ the carry of T[L-1]), doubled where b = 1, carry chain to limbs below 2^52.
 * Bounds as gen_fmw.py: A < 4n, n < 2^(52 L - 12); a column gets at most 2L doubled square terms, 2 diagonal, 2L reduction terms
 * and a carry: below (4L + 3) 2^52 < 2^62 for L <= 141, below 2^63 after the doubling. */
#define FMW_GROUPS 1
#ifndef FMWL_BJ
#define FMWL_BJ 16
#endif

/* T[c + t] += lo(x * Y[t]) and T[c + t + 1] += hi(x * Y[t]) for t = 0 .. n-1 (n <= FMWL_BJ), the n + 1 columns in registers */
static inline __attribute__((always_inline)) void fmwl_block(__m512i *T, int c, __m512i x, const __m512i *Y, int n) {
    if (n == FMWL_BJ) {
        __m512i acc[FMWL_BJ + 1];
#pragma GCC unroll 32
        for (int t = 0; t <= FMWL_BJ; t++) acc[t] = T[c + t];
#pragma GCC unroll 32
        for (int t = 0; t < FMWL_BJ; t++) acc[t] = _mm512_madd52lo_epu64(acc[t], x, Y[t]);
#pragma GCC unroll 32
        for (int t = 0; t < FMWL_BJ; t++) acc[t + 1] = _mm512_madd52hi_epu64(acc[t + 1], x, Y[t]);
#pragma GCC unroll 32
        for (int t = 0; t <= FMWL_BJ; t++) T[c + t] = acc[t];
    } else {
        for (int t = 0; t < n; t++) {
            T[c + t] = _mm512_madd52lo_epu64(T[c + t], x, Y[t]);
            T[c + t + 1] = _mm512_madd52hi_epu64(T[c + t + 1], x, Y[t]);
        }
    }
}

static void fmwl_step(__m512i *A, const __m512i *N, const __m512i ninv, const __mmask8 kb) {
    enum { L = FMW_L };
    __m512i T[2 * L + 2];
    const __m512i zero = _mm512_setzero_si512();
    for (int c = 0; c < 2 * L + 2; c++) T[c] = zero;
    /* 1. off-diagonal products, once */
    for (int i = 0; i < L - 1; i++) {
        const __m512i ai = A[i];
        int j = i + 1;
        for (; j + FMWL_BJ <= L; j += FMWL_BJ) fmwl_block(T, i + j, ai, A + j, FMWL_BJ);
        if (j < L) fmwl_block(T, i + j, ai, A + j, L - j);
    }
    /* doubled, plus the diagonal */
    for (int i = 0; i < L; i++) {
        T[2 * i] = _mm512_madd52lo_epu64(_mm512_add_epi64(T[2 * i], T[2 * i]), A[i], A[i]);
        T[2 * i + 1] = _mm512_madd52hi_epu64(_mm512_add_epi64(T[2 * i + 1], T[2 * i + 1]), A[i], A[i]);
    }
    /* 2. Montgomery reduction, row by row */
    for (int k = 0; k < L; k++) {
        if (k) T[k] = _mm512_add_epi64(T[k], _mm512_srli_epi64(T[k - 1], 52));
        const __m512i m = _mm512_madd52lo_epu64(zero, T[k], ninv);
        int j = 0;
        for (; j + FMWL_BJ <= L; j += FMWL_BJ) fmwl_block(T, k + j, m, N + j, FMWL_BJ);
        if (j < L) fmwl_block(T, k + j, m, N + j, L - j);
    }
    /* 3. Y = T[L .. 2L-1] with the carry of T[L-1], times 2^b, limbs below 2^52 */
    T[L] = _mm512_add_epi64(T[L], _mm512_srli_epi64(T[L - 1], 52));
    const __m512i mask = _mm512_set1_epi64(0xFFFFFFFFFFFFFULL);
    __m512i c = zero;
    for (int i = 0; i < L; i++) {
        __m512i v = _mm512_mask_add_epi64(T[L + i], kb, T[L + i], T[L + i]);
        v = _mm512_add_epi64(v, c);
        A[i] = _mm512_and_si512(v, mask);
        c = _mm512_srli_epi64(v, 52);
    }
}
#define FMW_STEP(A, N, NINV, KB) fmwl_step((A), (N), (NINV)[0], (KB)[0])
