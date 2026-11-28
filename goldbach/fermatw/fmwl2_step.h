/* fmwl2_step.h -- the fmw step for large L as product scanning with register-resident column blocks.
 *
 * Output columns are produced 8 at a time; the 8 accumulators stay in registers while i runs over the rows, each i adding
 * 8 lo and 8 hi products of one register operand (a_i or m_i) with 9 consecutive memory operands: about 0.6 loads an IFMA and
 * no accumulator traffic.  A column c's sum is self-contained: lo terms of pairs with i + j = c and hi terms of i + j = c - 1.
 *   1. square: column c = sum over i < j of [lo(a_i a_j), i + j = c] + [hi(a_i a_j), i + j = c - 1], doubled, plus the diagonal.
 *   2. reduce, columns 0 .. L-1 in blocks: the multipliers m_i of earlier blocks in bulk; inside the block, column by column,
 *      m_k = lo52((T_k + carry) n'), then its terms on the block's later columns.  Columns L .. 2L-1: every m_i in bulk.
 *   3. Y = columns L .. 2L-1 with the carries, times 2^b, limbs below 2^52.
 * Bounds as fmwl_step.h. */
#define FMW_GROUPS 1
#define FMWL_B 8

/* acc[t] += lo(x * Y[o + t]) + hi(x * Y[o + t - 1]) for t = 0..7, every index valid (the bulk).  With FMWL_SPLIT the hi
   products go to a second set of accumulators accH (16 chains of one IFMA an i instead of 8 of two: the 4-cycle IFMA latency
   no longer limits a loop that issues 16 IFMAs in ~8 cycles); acc and accH are added at the end of the block. */
#ifndef FMWL_SPLIT
#define FMWL_SPLIT 1
#endif
#if FMWL_SPLIT
#define FMWL_HI(acc, accH) accH
#else
#define FMWL_HI(acc, accH) acc
#endif
#define FMWL_BULK(acc, accH, x, Yb) do { const __m512i *y_ = (Yb); \
    acc[0] = _mm512_madd52lo_epu64(acc[0], x, y_[0]); acc[1] = _mm512_madd52lo_epu64(acc[1], x, y_[1]); \
    acc[2] = _mm512_madd52lo_epu64(acc[2], x, y_[2]); acc[3] = _mm512_madd52lo_epu64(acc[3], x, y_[3]); \
    acc[4] = _mm512_madd52lo_epu64(acc[4], x, y_[4]); acc[5] = _mm512_madd52lo_epu64(acc[5], x, y_[5]); \
    acc[6] = _mm512_madd52lo_epu64(acc[6], x, y_[6]); acc[7] = _mm512_madd52lo_epu64(acc[7], x, y_[7]); \
    FMWL_HI(acc, accH)[0] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[0], x, y_[-1]); \
    FMWL_HI(acc, accH)[1] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[1], x, y_[0]); \
    FMWL_HI(acc, accH)[2] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[2], x, y_[1]); \
    FMWL_HI(acc, accH)[3] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[3], x, y_[2]); \
    FMWL_HI(acc, accH)[4] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[4], x, y_[3]); \
    FMWL_HI(acc, accH)[5] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[5], x, y_[4]); \
    FMWL_HI(acc, accH)[6] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[6], x, y_[5]); \
    FMWL_HI(acc, accH)[7] = _mm512_madd52hi_epu64(FMWL_HI(acc, accH)[7], x, y_[6]); } while (0)
#define FMWL_MERGE(acc, accH) do { if (FMWL_SPLIT) for (int t_ = 0; t_ < 8; t_++) { acc[t_] = _mm512_add_epi64(acc[t_], accH[t_]); accH[t_] = _mm512_setzero_si512(); } } while (0)

static void fmwl2_step(__m512i *A, const __m512i *N, const __m512i ninv, const __mmask8 kb) {
    enum { L = FMW_L, B = FMWL_B };
    __m512i T[2 * L + B], Mm[L];
    const __m512i zero = _mm512_setzero_si512();
    /* 1. the square, column blocks c0 .. c0+7 */
    for (int c0 = 0; c0 < 2 * L; c0 += B) {
        __m512i acc[B], accH[B];
        for (int t = 0; t < B; t++) acc[t] = accH[t] = zero;
        /* pairs i < j: lo for j = c - i, hi for j = c - 1 - i, 0 <= i < j <= L - 1 */
        int ilo = c0 - L; if (ilo < 0) ilo = 0;                  /* smallest i with some valid j */
        int ihi = (c0 + B - 1) / 2;                              /* largest i with some valid j (j > i) */
        int blo = c0 + B - L; if (blo < 0) blo = 0;              /* bulk: every j <= L - 1 (lo: c0+7-i, hi: c0+6-i) and */
        int bhi = (c0 - 2) / 2;                                  /* every j > i (hi of t = 0: c0 - 1 - i > i) */
        if (c0 < 2) bhi = -1;
        for (int i = ilo; i <= ihi; i++) {
            const __m512i ai = A[i];
            if (i >= blo && i <= bhi) { FMWL_BULK(acc, accH, ai, A + (c0 - i)); continue; }
            for (int t = 0; t < B; t++) {
                int j = c0 + t - i;
                if (j > i && j < L) acc[t] = _mm512_madd52lo_epu64(acc[t], ai, A[j]);
                j--;
                if (j > i && j < L) acc[t] = _mm512_madd52hi_epu64(acc[t], ai, A[j]);
            }
        }
        FMWL_MERGE(acc, accH);
        for (int t = 0; t < B; t++) {
            int c = c0 + t;
            __m512i v = _mm512_add_epi64(acc[t], acc[t]);
            if (!(c & 1) && c / 2 < L) v = _mm512_madd52lo_epu64(v, A[c / 2], A[c / 2]);
            if ((c & 1) && (c - 1) / 2 < L) v = _mm512_madd52hi_epu64(v, A[(c - 1) / 2], A[(c - 1) / 2]);
            T[c] = v;
        }
    }
    /* 2a. reduction, columns 0 .. L-1 (only those: the upper columns are all done in 2b) */
    __m512i carry = zero;
    for (int c0 = 0; c0 < L; c0 += B) {
        __m512i acc[B], accH[B];
        const int nb = L - c0 < B ? L - c0 : B;              /* columns of this block below L */
        for (int t = 0; t < nb; t++) acc[t] = T[c0 + t];
        for (int t = nb; t < B; t++) acc[t] = zero;
        for (int t = 0; t < B; t++) accH[t] = zero;
        /* multipliers of earlier blocks, i < c0: lo(m_i n_{c-i}), hi(m_i n_{c-1-i}) */
        int blo = c0 + B - L; if (blo < 0) blo = 0;          /* bulk: every index c0 + t - i (t <= 7) at most L - 1 */
        for (int i = 0; i < c0; i++) {
            const __m512i mi = Mm[i];
            if (nb == B && i >= blo) { FMWL_BULK(acc, accH, mi, N + (c0 - i)); continue; }
            for (int t = 0; t < nb; t++) {
                int j = c0 + t - i;
                if (j < L) acc[t] = _mm512_madd52lo_epu64(acc[t], mi, N[j]);
                j--;
                if (j < L) acc[t] = _mm512_madd52hi_epu64(acc[t], mi, N[j]);
            }
        }
        FMWL_MERGE(acc, accH);
        /* inside the block, column by column */
        for (int t = 0; t < nb; t++) {
            const int k = c0 + t;
            acc[t] = _mm512_add_epi64(acc[t], carry);
            const __m512i m = _mm512_madd52lo_epu64(zero, acc[t], ninv);
            Mm[k] = m;
            acc[t] = _mm512_madd52lo_epu64(acc[t], m, N[0]);
            carry = _mm512_srli_epi64(acc[t], 52);
            for (int u = t + 1; u < nb; u++) {                   /* m_k on the block's later columns k + (u - t) */
                acc[u] = _mm512_madd52lo_epu64(acc[u], m, N[u - t]);
                acc[u] = _mm512_madd52hi_epu64(acc[u], m, N[u - t - 1]);
            }
        }
    }
    /* 2b. columns L .. 2L-1: every multiplier m_i, i < L; the carry out of column L - 1 into column L */
    T[L] = _mm512_add_epi64(T[L], carry);
    for (int c0 = L; c0 < 2 * L; c0 += B) {
        __m512i acc[B], accH[B];
        const int nb = 2 * L - c0 < B ? 2 * L - c0 : B;
        for (int t = 0; t < nb; t++) acc[t] = T[c0 + t];
        for (int t = nb; t < B; t++) acc[t] = zero;
        for (int t = 0; t < B; t++) accH[t] = zero;
        int blo = c0 + B - L; if (blo < 0) blo = 0;          /* bulk: lo index c0 + 7 - i <= L - 1; hi index c0 - 1 - i >= 0 holds */
        int ilo = c0 - L; if (ilo < 0) ilo = 0;              /* hi of t = 0: c0 - 1 - i <= L - 1 */
        for (int i = ilo; i < L; i++) {
            const __m512i mi = Mm[i];
            if (nb == B && i >= blo) { FMWL_BULK(acc, accH, mi, N + (c0 - i)); continue; }
            for (int t = 0; t < nb; t++) {
                int j = c0 + t - i;
                if (j >= 0 && j < L) acc[t] = _mm512_madd52lo_epu64(acc[t], mi, N[j]);
                j--;
                if (j >= 0 && j < L) acc[t] = _mm512_madd52hi_epu64(acc[t], mi, N[j]);
            }
        }
        FMWL_MERGE(acc, accH);
        for (int t = 0; t < nb; t++) T[c0 + t] = acc[t];
    }
    /* Y = T[L .. 2L-1], times 2^b, carry chain to limbs below 2^52 */
    const __m512i mask = _mm512_set1_epi64(0xFFFFFFFFFFFFFULL);
    __m512i cy = zero;
    for (int i = 0; i < L; i++) {
        __m512i v = _mm512_mask_add_epi64(T[L + i], kb, T[L + i], T[L + i]);
        v = _mm512_add_epi64(v, cy);
        A[i] = _mm512_and_si512(v, mask);
        cy = _mm512_srli_epi64(v, 52);
    }
}
#define FMW_STEP(A, N, NINV, KB) fmwl2_step((A), (N), (NINV)[0], (KB)[0])
