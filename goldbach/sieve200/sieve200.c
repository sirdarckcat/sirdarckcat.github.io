/* sieve200.c -- block sieve for CRT progressions N = N0 + k*M with many residual primes (campaign3: 867 rows).
 *
 * The same sieve as search.py's run_block, as a library: alive[r][j] is false exactly when some sieve prime s divides
 * N0 + (k0 + j) M - U[r], where the sieve primes are the primes 3 <= s < B that do not divide M (search.init_spec's S).
 * A block is K = 2^logK consecutive members.  Output: the bit rows (bit j of row r set = row r alive for member k0 + j),
 * the number of alive rows of every member (u16, not saturating), and the survivor row ids of chosen members.
 *
 * Method (the idea and the pattern trick are those of tscan.c): for each row, the primes below SMALLP clear 512 (or 256, or
 * 64) bits at a time by ANDing slices of a periodic bit string, every other prime clears bits j = first, first + s, ... of the
 * row with a fixed trip count.  The marks beyond the block are masked out instead of landing in a padding area, so a row is
 * exactly K bits.  The counts are a vertical counter (carry-save adders over groups of 16 rows, portable code that the
 * compiler vectorizes).  The context is read-only after s200_new and every call has its own scratch, so any number of threads
 * or forked processes may sieve different blocks of one context.
 *
 *   gcc -O3 -march=native -shared -fPIC -o libsieve200.so sieve200.c
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#if defined(__AVX512BW__) || defined(__AVX2__)
#include <immintrin.h>
#endif
#if !defined(__BMI__)
#define _andn_u64(a, b) (~(a) & (b))
#endif
#ifdef __AVX512BW__
#define VBYTES 64
#elif defined(__AVX2__)
#define VBYTES 32
#else
#define VBYTES 8
#endif

typedef uint64_t u64;
typedef uint32_t u32;
typedef uint16_t u16;
typedef unsigned __int128 u128;

#ifndef SMALLP
#define SMALLP 384          /* primes below this use the pattern sieve */
#endif
#define CHUNK 64            /* primes whose first marks are computed together */
#ifndef TILE_LOG
#define TILE_LOG 17         /* the marks of the small primes are made one tile of 2^17 bits (16 KB) at a time, so the tile stays in L1 */
#endif
#ifndef TILE_PRIMES
#define TILE_PRIMES 16384   /* primes below this are tiled (those with many marks in a tile) */
#endif

typedef struct S200 {
    int nU; u32 *U;
    u32 B; int logK; u64 K, words;
    u32 nS; u32 *S, *Minv, *cS, *nf, *nt; double *rinv; u32 nP1; int logT;   /* nt = floor(T / s); primes below nP1 are tiled */   /* nf = floor(K / s): marks of a row that are certainly inside the window */
    u32 nSmall; unsigned char **pat; u32 *inv8, *step;
    int shared;                                      /* a variant of another context: the per-prime tables belong to that one */
} S200;

/* ---------------------------------------------------------------- big numbers (little-endian u64 limbs) */

static int parse_hex(const char *s, u64 **out, int *nl) {
    size_t len = strlen(s);
    while (len && (s[len - 1] == '\n' || s[len - 1] == '\r' || s[len - 1] == ' ')) len--;
    if (len >= 2 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) { s += 2; len -= 2; }
    if (!len) return -1;
    int n = (int)((len + 15) / 16);
    u64 *a = calloc(n, 8);
    for (size_t i = 0; i < len; i++) {
        char c = s[len - 1 - i];
        int d = (c >= '0' && c <= '9') ? c - '0' : (c >= 'a' && c <= 'f') ? c - 'a' + 10 : (c >= 'A' && c <= 'F') ? c - 'A' + 10 : -1;
        if (d < 0) { free(a); return -1; }
        a[i / 16] |= (u64)d << (4 * (i % 16));
    }
    *out = a; *nl = n;
    return 0;
}
/* out[i] = X mod S[i] for the number X = sum limbs[j] 2^(16 j) (n limbs of 16 bits), S[i] < 2^37.  Horner in steps of 16 bits: r * 2^16 + limb
   stays below 2^53, so the quotient comes from a double reciprocal (off by at most one: two conditional corrections); eight primes at a time with
   AVX-512, one at a time otherwise.  About 0.5 ms for the 78,409 primes below 10^6 and a number of 640 bits, 10 ms with Python ints. */
static void mods_of_primes(const u16 *limbs, int n, const u32 *S, u32 nS, u32 *out) {
    u32 p = 0;
#if defined(__AVX512F__) && defined(__AVX512DQ__)
    const __m512i zero = _mm512_setzero_si512();
    for (; p + 64 <= nS; p += 64) {                              /* eight vectors in flight: one step of the Horner scheme has a latency of ~30 cycles */
        __m512i vs[8], r[8];
        __m512d vr[8];
        #pragma GCC unroll 8
        for (int k = 0; k < 8; k++) {
            const __m256i s32 = _mm256_loadu_si256((const __m256i *)(S + p + 8 * k));
            vs[k] = _mm512_cvtepu32_epi64(s32);
            vr[k] = _mm512_div_pd(_mm512_set1_pd(1.0), _mm512_cvtepu32_pd(s32));
            r[k] = zero;
        }
        for (int i = n - 1; i >= 0; i--) {
            const __m512i limb = _mm512_set1_epi64(limbs[i]);
            #pragma GCC unroll 8
            for (int k = 0; k < 8; k++) {
                const __m512i x = _mm512_or_si512(_mm512_slli_epi64(r[k], 16), limb);
                const __m512i q = _mm512_cvttpd_epu64(_mm512_mul_pd(_mm512_cvtepu64_pd(x), vr[k]));
                __m512i t = _mm512_sub_epi64(x, _mm512_mul_epu32(q, vs[k]));
                t = _mm512_mask_add_epi64(t, _mm512_cmplt_epi64_mask(t, zero), t, vs[k]);
                r[k] = _mm512_mask_sub_epi64(t, _mm512_cmpge_epu64_mask(t, vs[k]), t, vs[k]);
            }
        }
        #pragma GCC unroll 8
        for (int k = 0; k < 8; k++) _mm256_storeu_si256((__m256i *)(out + p + 8 * k), _mm512_cvtepi64_epi32(r[k]));
    }
#endif
    for (; p < nS; p++) {
        const u64 s = S[p];
        const double rinv = 1.0 / (double)s;
        u64 r = 0;
        for (int i = n - 1; i >= 0; i--) {
            const u64 x = (r << 16) | limbs[i];
            u64 t = x - (u64)((double)x * rinv) * s;
            if ((int64_t)t < 0) t += s;
            if (t >= s) t -= s;
            r = t;
        }
        out[p] = (u32)r;
    }
}

/* a * b mod s for a, b < s < 2^26: the quotient from a double reciprocal (a b < 2^52 is exact), off by at most one */
static inline u32 mulmod32(u32 a, u32 b, u32 s) {
    const u64 x = (u64)a * b;
    u64 t = x - (u64)((double)x * (1.0 / (double)s)) * s;
    if ((int64_t)t < 0) t += s;
    if (t >= s) t -= s;
    return (u32)t;
}

/* 16-bit limbs (little endian) of a number given as 64-bit limbs; returns their count (trailing zero limbs trimmed, at least 1) */
static int split16(const u64 *a, int nl, u16 *out) {
    int n = 0;
    for (int i = 0; i < nl; i++) for (int j = 0; j < 4; j++) out[n++] = (u16)(a[i] >> (16 * j));
    while (n > 1 && !out[n - 1]) n--;
    return n;
}

/* N0 mod s for the primes S[0..nS): N0 as hex.  Returns 0, or -1 on a bad number. */
int s200_n0m(const char *N0_hex, const u32 *S, u32 nS, u32 *out) {
    u64 *N0; int nN;
    if (parse_hex(N0_hex, &N0, &nN)) return -1;
    u16 *l = malloc(2 * 4 * (size_t)nN);
    int n = split16(N0, nN, l);
    mods_of_primes(l, n, S, nS, out);
    free(l); free(N0);
    return 0;
}

static u32 inv_mod(u32 a, u32 s) {              /* a^-1 mod s, s prime, a != 0 */
    int64_t t = 0, nt = 1, r = s, nr = a;
    while (nr) {
        int64_t q = r / nr, x;
        x = t - q * nt; t = nt; nt = x;
        x = r - q * nr; r = nr; nr = x;
    }
    return (u32)(t < 0 ? t + s : t);
}

/* ---------------------------------------------------------------- context */

void s200_free(S200 *c) {
    if (!c) return;
    if (c->shared) { free(c->U); free(c->cS); free(c); return; }
    for (u32 p = 0; p < c->nSmall; p++) free(c->pat[p]);
    free(c->pat); free(c->inv8); free(c->step); free(c->U); free(c->S); free(c->Minv); free(c->cS); free(c->nf); free(c->nt); free(c->rinv);
    free(c);
}

/* U: the residual primes in the order of the rows.  B: sieve primes are 3 <= s < B, without those s | M and without the nExcl
   primes of excl (search.init_spec leaves the cover primes out as well).  K = 2^logK members a block (512 <= K <= 2^26).
   Returns NULL on bad input: unparsable hex, nU < 1, B < 5, or a residual q with q * B >= 2^50 (the row start of a prime is
   computed in double precision). */
S200 *s200_new(const char *N0_hex, const char *M_hex, const u32 *U, int nU, u32 B, int logK, const u32 *excl, int nExcl) {
    u64 *N0, *M; int nN, nM;
    if (parse_hex(N0_hex, &N0, &nN) || parse_hex(M_hex, &M, &nM)) return NULL;
    if (logK < 9 || logK > 26 || nU < 1 || nU > 4095 || B < 5) { free(N0); free(M); return NULL; }
    for (int i = 0; i < nU; i++)
        if ((u64)U[i] * B >= (1ull << 50)) { free(N0); free(M); return NULL; }
    S200 *c = calloc(1, sizeof *c);
    c->nU = nU; c->U = malloc(4 * (size_t)nU); memcpy(c->U, U, 4 * (size_t)nU);
    c->B = B; c->logK = logK; c->K = 1ull << logK; c->words = c->K / 64;
    char *comp = calloc((size_t)B + 1, 1);
    for (int i = 0; i < nExcl; i++) if (excl[i] < B) comp[excl[i]] = 2;     /* 2: left out, but still sieves its multiples */
    /* the candidate primes 3 <= s < B (not excluded), then those that do not divide M, with M^-1 and -N0/M mod s */
    u32 ncand = 0, capc = 1024;
    u32 *P = malloc(4 * (size_t)capc);
    for (u64 s = 2; s < B; s++) {                              /* the primes 3 <= s < B, as numpy's primerange(3, B) */
        if (comp[s] == 1) continue;
        for (u64 j = s * s; j < B; j += s) comp[j] = 1;
        if (s == 2 || comp[s]) continue;
        if (ncand == capc) { capc *= 2; P = realloc(P, 4 * (size_t)capc); }
        P[ncand++] = (u32)s;
    }
    u16 *l16 = malloc(2 * 4 * (size_t)(nM > nN ? nM : nN));
    u32 *mmod = malloc(4 * (size_t)ncand + 4);
    int n16 = split16(M, nM, l16);
    mods_of_primes(l16, n16, P, ncand, mmod);
    u32 nk = 0;                                                 /* s divides M: removed, as init_spec does */
    for (u32 i = 0; i < ncand; i++) if (mmod[i]) { P[nk] = P[i]; mmod[nk] = mmod[i]; nk++; }
    u32 *n0mod = malloc(4 * (size_t)nk + 4);
    n16 = split16(N0, nN, l16);
    mods_of_primes(l16, n16, P, nk, n0mod);
    c->nS = nk;
    c->S = malloc(4 * ((size_t)nk + CHUNK)); c->Minv = malloc(4 * ((size_t)nk + CHUNK)); c->cS = malloc(4 * ((size_t)nk + CHUNK));
    c->nf = malloc(4 * ((size_t)nk + CHUNK)); c->rinv = malloc(8 * ((size_t)nk + CHUNK));
    for (u32 i = 0; i < nk; i++) {
        const u32 sp = P[i], mi = inv_mod(mmod[i], sp), n0 = n0mod[i];
        c->S[i] = sp; c->Minv[i] = mi;
        c->cS[i] = mulmod32(n0 ? sp - n0 : 0, mi, sp);         /* -N0/M mod s */
        c->rinv[i] = 1.0 / (double)sp;
        c->nf[i] = (u32)(c->K / sp);                           /* positions j, j+s, .. j+(nf-1)s are below K for j < s; one more may be */
    }
    free(P); free(mmod); free(n0mod); free(l16);
    free(comp); free(N0); free(M);
    {                                                           /* pad the per-prime arrays so that 64 primes can be read at a time */
        u32 n = c->nS + CHUNK;
        c->S = realloc(c->S, 4 * n); c->Minv = realloc(c->Minv, 4 * n); c->cS = realloc(c->cS, 4 * n);
        c->nf = realloc(c->nf, 4 * n); c->rinv = realloc(c->rinv, 8 * n);
        for (u32 i = c->nS; i < n; i++) { c->S[i] = 1; c->Minv[i] = 0; c->cS[i] = 0; c->nf[i] = 0; c->rinv[i] = 1.0; }
        c->nt = malloc(4 * (size_t)n);
        c->logT = TILE_LOG < logK ? TILE_LOG : logK;
        c->nP1 = 0;
        for (u32 i = 0; i < n; i++) c->nt[i] = (u32)((1ull << c->logT) / c->S[i]);
        while (c->nP1 < c->nS && c->S[c->nP1] < TILE_PRIMES) c->nP1++;
    }
    while (c->nSmall < c->nS && c->S[c->nSmall] < SMALLP) c->nSmall++;
    c->pat = malloc(sizeof(*c->pat) * (c->nSmall + 1)); c->inv8 = malloc(4 * (c->nSmall + 1)); c->step = malloc(4 * (c->nSmall + 1));
    for (u32 p = 0; p < c->nSmall; p++) {
        u32 sp = c->S[p];
        size_t bytes = ((sp + VBYTES + 63) / 64 + 1) * 64;
        c->pat[p] = aligned_alloc(64, bytes);
        memset(c->pat[p], 0xff, bytes);
        for (u64 i = 0; i < 8ull * (sp + VBYTES); i += sp) c->pat[p][i >> 3] &= (unsigned char)~(1u << (i & 7));
        c->inv8[p] = inv_mod(8 % sp, sp);
        c->step[p] = VBYTES % sp;
    }
    return c;
}

/* A variant of the context of the same M (and B, K, cover): another N0 and another list of rows.  It shares the per-prime tables with c
   (c must outlive it and must not be freed first); only -N0/M mod s per prime and the rows are its own, so it costs about a millisecond
   instead of the 30 ms of s200_new.  Returns NULL on bad input. */
S200 *s200_variant(const S200 *c, const char *N0_hex, const u32 *U, int nU) {
    u64 *N0; int nN;
    if (parse_hex(N0_hex, &N0, &nN)) return NULL;
    if (nU < 1 || nU > 4095) { free(N0); return NULL; }
    for (int i = 0; i < nU; i++) if ((u64)U[i] * c->B >= (1ull << 50)) { free(N0); return NULL; }
    S200 *v = malloc(sizeof *v);
    *v = *c;
    v->shared = 1;
    v->nU = nU; v->U = malloc(4 * (size_t)nU); memcpy(v->U, U, 4 * (size_t)nU);
    v->cS = malloc(4 * ((size_t)c->nS + CHUNK));
    u16 *l16 = malloc(2 * 4 * (size_t)nN);
    u32 *n0mod = malloc(4 * (size_t)c->nS + 4);
    int n16 = split16(N0, nN, l16);
    mods_of_primes(l16, n16, c->S, c->nS, n0mod);
    for (u32 i = 0; i < c->nS; i++) {
        const u32 sp = c->S[i];
        v->cS[i] = mulmod32(n0mod[i] ? sp - n0mod[i] : 0, c->Minv[i], sp);
    }
    for (u32 i = c->nS; i < c->nS + CHUNK; i++) v->cS[i] = 0;
    free(l16); free(n0mod); free(N0);
    return v;
}

int s200_nprimes(const S200 *c) { return (int)c->nS; }
void s200_primes(const S200 *c, u32 *out) { memcpy(out, c->S, 4 * (size_t)c->nS); }
int s200_nrows(const S200 *c) { return c->nU; }
int s200_block_log(const S200 *c) { return c->logK; }
u32 s200_prime(const S200 *c, int i) { return c->S[i]; }
size_t s200_bits_bytes(const S200 *c) { return (size_t)c->nU * c->words * 8; }   /* bytes of the bit matrix a block fills */

/* ---------------------------------------------------------------- counting: a vertical counter over the rows */

static inline void fa(u64 a, u64 b, u64 c, u64 *s, u64 *k) { u64 t = a ^ b; *s = t ^ c; *k = (a & b) | (t & c); }

/* counts[j] = number of rows whose bit j is set; planes: 12 * words u64 of scratch (counts up to 4095 rows) */
static void count_rows(const u64 *bits, int nU, u64 words, u16 *counts, u64 *planes) {
    memset(planes, 0, 12 * words * 8);
    u64 *P0 = planes, *P1 = P0 + words, *P2 = P1 + words, *P3 = P2 + words, *P4 = P3 + words;
    u64 *P5 = P4 + words, *P6 = P5 + words, *P7 = P6 + words, *P8 = P7 + words, *P9 = P8 + words, *P10 = P9 + words, *P11 = P10 + words;
    int r = 0;
    for (; r + 16 <= nU; r += 16) {
        const u64 *R0 = bits + (size_t)r * words, *R1 = R0 + words, *R2 = R1 + words, *R3 = R2 + words, *R4 = R3 + words,
                  *R5 = R4 + words, *R6 = R5 + words, *R7 = R6 + words, *R8 = R7 + words, *R9 = R8 + words, *R10 = R9 + words,
                  *R11 = R10 + words, *R12 = R11 + words, *R13 = R12 + words, *R14 = R13 + words, *R15 = R14 + words;
        for (u64 w = 0; w < words; w++) {
            /* the 16 bits of a column added into a 5-bit number (a Wallace tree of full adders) */
            u64 sa, ca, sb, cb, sc, cc, sd, cd, se, ce, t1, u1, t2, u2, v, x1, y1, x2, y2, x3, y3, p, q;
            fa(R0[w], R1[w], R2[w], &sa, &ca); fa(R3[w], R4[w], R5[w], &sb, &cb); fa(R6[w], R7[w], R8[w], &sc, &cc);
            fa(R9[w], R10[w], R11[w], &sd, &cd); fa(R12[w], R13[w], R14[w], &se, &ce);
            fa(sa, sb, sc, &t1, &u1); fa(sd, se, R15[w], &t2, &u2);
            u64 ones = t1 ^ t2; v = t1 & t2;
            fa(ca, cb, cc, &x1, &y1); fa(cd, ce, u1, &x2, &y2); fa(u2, v, x1, &x3, &y3);
            u64 twos = x3 ^ x2, z = x3 & x2;
            fa(y1, y2, y3, &p, &q);
            u64 fours = p ^ z, rr = p & z;
            u64 eights = q ^ rr, sixteens = q & rr;
            /* add that number (ones .. sixteens) to the planes */
            u64 a, carry, s_;
            a = P0[w]; P0[w] = a ^ ones; carry = a & ones;
            fa(P1[w], twos, carry, &s_, &carry); P1[w] = s_;
            fa(P2[w], fours, carry, &s_, &carry); P2[w] = s_;
            fa(P3[w], eights, carry, &s_, &carry); P3[w] = s_;
            fa(P4[w], sixteens, carry, &s_, &carry); P4[w] = s_;
            a = P5[w]; P5[w] = a ^ carry; carry = a & carry;
            a = P6[w]; P6[w] = a ^ carry; carry = a & carry;
            a = P7[w]; P7[w] = a ^ carry; carry = a & carry;
            a = P8[w]; P8[w] = a ^ carry; carry = a & carry;
            a = P9[w]; P9[w] = a ^ carry; carry = a & carry;
            a = P10[w]; P10[w] = a ^ carry; carry = a & carry;
            P11[w] ^= carry;
        }
    }
    for (; r < nU; r++) {                                   /* the last rows, one at a time */
        const u64 *R = bits + (size_t)r * words;
        for (u64 w = 0; w < words; w++) {
            u64 carry = R[w], a;
            a = P0[w]; P0[w] = a ^ carry; carry = a & carry;
            a = P1[w]; P1[w] = a ^ carry; carry = a & carry;
            a = P2[w]; P2[w] = a ^ carry; carry = a & carry;
            a = P3[w]; P3[w] = a ^ carry; carry = a & carry;
            a = P4[w]; P4[w] = a ^ carry; carry = a & carry;
            a = P5[w]; P5[w] = a ^ carry; carry = a & carry;
            a = P6[w]; P6[w] = a ^ carry; carry = a & carry;
            a = P7[w]; P7[w] = a ^ carry; carry = a & carry;
            a = P8[w]; P8[w] = a ^ carry; carry = a & carry;
            a = P9[w]; P9[w] = a ^ carry; carry = a & carry;
            a = P10[w]; P10[w] = a ^ carry; carry = a & carry;
            P11[w] ^= carry;
        }
    }
    for (u64 w = 0; w < words; w++) {                       /* planes -> counts */
        u64 p0 = P0[w], p1 = P1[w], p2 = P2[w], p3 = P3[w], p4 = P4[w], p5 = P5[w], p6 = P6[w], p7 = P7[w], p8 = P8[w], p9 = P9[w], p10 = P10[w], p11 = P11[w];
        u16 *o = counts + 64 * w;
        for (int b = 0; b < 64; b++)
            o[b] = (u16)(((p0 >> b) & 1) | (((p1 >> b) & 1) << 1) | (((p2 >> b) & 1) << 2) | (((p3 >> b) & 1) << 3) | (((p4 >> b) & 1) << 4)
                       | (((p5 >> b) & 1) << 5) | (((p6 >> b) & 1) << 6) | (((p7 >> b) & 1) << 7) | (((p8 >> b) & 1) << 8) | (((p9 >> b) & 1) << 9)
                       | (((p10 >> b) & 1) << 10) | (((p11 >> b) & 1) << 11));
    }
}

/* ---------------------------------------------------------------- the sieve */

/* j after clearing the n bits j, j + s, ... j + (n-1) s of row: the loop of the sieve, 7 instructions a mark with BMI2 (the
   compiler's version has 9, with two register copies) */
static inline u64 clear_marks(u64 *row, u64 j, const u64 s, u32 n) {
#if defined(__x86_64__) && defined(__BMI2__) && defined(__BMI__) && !defined(S200_NO_ASM)
    if (!n) return j;
    u64 six = 6, one = 1, w, m, t;
    __asm__("1:\n\t"
            "shrx %[six], %[j], %[w]\n\t"
            "shlx %[j], %[one], %[m]\n\t"
            "andn (%[row],%[w],8), %[m], %[t]\n\t"
            "mov %[t], (%[row],%[w],8)\n\t"
            "add %[s], %[j]\n\t"
            "dec %[n]\n\t"
            "jnz 1b\n\t"
            : [j] "+r"(j), [n] "+r"(n), [w] "=&r"(w), [m] "=&r"(m), [t] "=&r"(t)
            : [row] "r"(row), [s] "r"(s), [six] "r"(six), [one] "r"(one)
            : "memory", "cc");
    return j;
#else
    for (; n; n--, j += s) {
        const u64 w = j >> 6;
        row[w] = _andn_u64(1ull << (j & 63), row[w]);
    }
    return j;
#endif
}

/* jb[i] = (q Minv[p] + d[p]) mod S[p] for p = p0 .. p0 + 63: the first member offset (>= 0) of the row q that s = S[p] divides.
   x < (q + 1) s stays below 2^50 (s_new checks q B < 2^50), the quotient is found with a double reciprocal and is off by at most one. */
static inline void first_offsets(const S200 *c, const u64 *d, u32 p0, u64 q, u32 *jb) {
#if defined(__AVX512F__) && defined(__AVX512DQ__)
    const __m512i vq = _mm512_set1_epi64((long long)q), zero = _mm512_setzero_si512();
    for (int v = 0; v < CHUNK / 8; v++) {
        const u32 p = p0 + 8 * v;
        const __m512i minv = _mm512_cvtepu32_epi64(_mm256_loadu_si256((const __m256i *)(c->Minv + p)));
        const __m512i vs = _mm512_cvtepu32_epi64(_mm256_loadu_si256((const __m256i *)(c->S + p)));
        const __m512i x = _mm512_add_epi64(_mm512_mul_epu32(vq, minv), _mm512_loadu_si512((const void *)(d + p)));
        const __m512i qi = _mm512_cvttpd_epu64(_mm512_mul_pd(_mm512_cvtepu64_pd(x), _mm512_loadu_pd(c->rinv + p)));
        __m512i j = _mm512_sub_epi64(x, _mm512_mul_epu32(qi, vs));              /* in (-s, 2s) */
        j = _mm512_mask_add_epi64(j, _mm512_cmplt_epi64_mask(j, zero), j, vs);
        j = _mm512_mask_sub_epi64(j, _mm512_cmpge_epu64_mask(j, vs), j, vs);
        _mm256_storeu_si256((__m256i *)(jb + 8 * v), _mm512_cvtepi64_epi32(j));
    }
#else
    for (int i = 0; i < CHUNK; i++) {
        const u32 p = p0 + i;
        const u64 s = c->S[p];
        const u64 x = q * c->Minv[p] + d[p];
        u64 j = x - (u64)((double)x * c->rinv[p]) * s;
        if ((int64_t)j < 0) j += s;
        if (j >= s) j -= s;
        jb[i] = (u32)j;
    }
#endif
}

/* Sieves the members k0 .. k0 + K - 1.  bits: caller's buffer of s200_bits_bytes() bytes (row r at bits + r * K / 64 words),
   counts: K u16.  Either may be NULL: with bits NULL only the counts are returned (the rows still need the same memory, so
   the context's scratch is used: pass bits whenever the survivors are wanted).  Returns 0, or -1 on allocation failure. */
int s200_block(const S200 *c, u64 k0, u16 *counts, u64 *bits) {
    const u64 K = c->K, words = c->words, wmask = words - 1;
    int own = 0;
    if (!bits) { bits = aligned_alloc(64, s200_bits_bytes(c)); own = 1; if (!bits) return -1; }
    u64 *d = aligned_alloc(64, ((8 * ((size_t)c->nS + CHUNK)) + 63) / 64 * 64);
    if (!d) { if (own) free(bits); return -1; }
    for (u32 p = 0; p < c->nS; p++) {
        u32 s = c->S[p];
        d[p] = (u32)((c->cS[p] + s - (u32)(k0 % s)) % s);      /* first member offset with s | N - q is (q * Minv + d) mod s */
    }
    for (u32 p = c->nS; p < c->nS + CHUNK; p++) d[p] = 0;
    u32 *nxt = aligned_alloc(64, ((4 * ((size_t)c->nP1 + 2 * CHUNK)) + 63) / 64 * 64);   /* next mark of each tiled prime */
    if (!nxt) { free(d); if (own) free(bits); return -1; }
    const u32 nSmall = c->nSmall, nS = c->nS, nP1 = c->nP1;
    for (int r = 0; r < c->nU; r++) {
        u64 *row = bits + (size_t)r * words;
        const u64 q = c->U[r];
        u32 tt[SMALLP];
        for (u32 p = 0; p < nSmall; p++) {                      /* where in its pattern each small prime starts for this row */
            u64 s = c->S[p];
            u64 x = q * c->Minv[p] + d[p];
            u64 f = x % s;                                      /* first offset j with s | N - q */
            tt[p] = (u32)((s - f) % s * c->inv8[p] % s);
        }
#if defined(__AVX512BW__)
        for (u64 w = 0; w < words; w += 8) {
            __m512i acc = _mm512_set1_epi64(-1);
            for (u32 p = 0; p < nSmall; p++) {
                acc = _mm512_and_si512(acc, _mm512_loadu_si512((const void *)(c->pat[p] + tt[p])));
                u32 t = tt[p] + c->step[p];
                tt[p] = t >= c->S[p] ? t - c->S[p] : t;
            }
            _mm512_storeu_si512((void *)(row + w), acc);
        }
#elif defined(__AVX2__)
        for (u64 w = 0; w < words; w += 4) {
            __m256i acc = _mm256_set1_epi64x(-1);
            for (u32 p = 0; p < nSmall; p++) {
                acc = _mm256_and_si256(acc, _mm256_loadu_si256((const __m256i *)(c->pat[p] + tt[p])));
                u32 t = tt[p] + c->step[p];
                tt[p] = t >= c->S[p] ? t - c->S[p] : t;
            }
            _mm256_storeu_si256((__m256i *)(row + w), acc);
        }
#else
        for (u64 w = 0; w < words; w++) {
            u64 acc = ~0ull;
            for (u32 p = 0; p < nSmall; p++) {
                u64 x; memcpy(&x, c->pat[p] + tt[p], 8);
                acc &= x;
                u32 t = tt[p] + c->step[p];
                tt[p] = t >= c->S[p] ? t - c->S[p] : t;
            }
            row[w] = acc;
        }
#endif
        if (nP1 > nSmall) {                                       /* the small primes tile by tile: the tile stays in L1 */
            const u32 n1 = nP1 - nSmall;
            for (u32 p0 = nSmall; p0 < nP1; p0 += CHUNK) first_offsets(c, d, p0, q, nxt + (p0 - nSmall));
            const u32 *S1 = c->S + nSmall, *nt1 = c->nt + nSmall;
            const u32 ntiles = (u32)(K >> c->logT);
            for (u32 tile = 0; tile < ntiles; tile++) {
                const u64 hi = (u64)(tile + 1) << c->logT;
                for (u32 i = 0; i < n1; i++) {
                    u64 j = nxt[i];
                    const u64 s = S1[i];
                    j = clear_marks(row, j, s, nt1[i]);               /* T / s marks inside the tile: j in [lo, lo + s) */
                    const u64 inside = j < hi;                         /* and one more, sometimes */
                    row[(j >> 6) & wmask] &= ~(inside << (j & 63));
                    nxt[i] = (u32)(j + (s & (0 - inside)));
                }
            }
        }
        for (u32 p0 = nP1; p0 < nS; p0 += CHUNK) {
            u32 jb[CHUNK] __attribute__((aligned(64)));
            first_offsets(c, d, p0, q, jb);                       /* the first offset j < s of 64 primes */
            const u32 pe = nS - p0 < CHUNK ? nS - p0 : CHUNK;
            for (u32 ci = 0; ci < pe; ci++) {
                const u32 p = p0 + ci;
                u64 j = jb[ci];
                const u64 s = c->S[p];
                /* nf marks that are certainly inside the window, with no mask: j + (nf - 1) s < s + K - s */
                j = clear_marks(row, j, s, c->nf[p]);
                /* and one more that is inside only sometimes; outside it clears nothing, in a harmless word */
                row[(j >> 6) & wmask] &= ~((u64)(j < K) << (j & 63));
            }
        }
    }
    free(d); free(nxt);
    int rc = 0;
    if (counts) {
        u64 *planes = malloc(12 * words * 8);
        if (!planes) rc = -1; else { count_rows(bits, c->nU, words, counts, planes); free(planes); }
    }
    if (own) free(bits);
    return rc;
}

/* The survivors of chosen members: for member j = js[i] (an offset inside the block) the ids of its alive rows go to rows_out
   in increasing order; offsets[i] is where member i starts (offsets has nj + 1 entries).  Returns the total, or -1 if it would
   exceed cap. */
long s200_extract(const S200 *c, const u64 *bits, const u32 *js, int nj, u16 *rows_out, long cap, long *offsets) {
    long n = 0;
    const u64 words = c->words;
    for (int i = 0; i < nj; i++) {
        offsets[i] = n;
        u64 j = js[i], wd = j >> 6, sh = j & 63;
        for (int r = 0; r < c->nU; r++)
            if ((bits[(size_t)r * words + wd] >> sh) & 1) {
                if (n >= cap) return -1;
                rows_out[n++] = (u16)r;
            }
    }
    offsets[nj] = n;
    return n;
}

/* The same as bitmaps: member i gets nwords = ceil(nU / 64) words, bit r set when row r is alive */
void s200_extract_bitmaps(const S200 *c, const u64 *bits, const u32 *js, int nj, u64 *out) {
    const u64 words = c->words;
    const int nw = (c->nU + 63) / 64;
    for (int i = 0; i < nj; i++) {
        u64 j = js[i], wd = j >> 6, sh = j & 63;
        u64 *o = out + (size_t)i * nw;
        for (int w = 0; w < nw; w++) o[w] = 0;
        for (int r = 0; r < c->nU; r++) o[r >> 6] |= ((bits[(size_t)r * words + wd] >> sh) & 1) << (r & 63);
    }
}

/* ---------------------------------------------------------------- the feeder: selection and survivor lists of a block */

/* The nkeep emptiest members of a block of L members with counts counts[0..L): order[0..nkeep) = their indices, by ascending count,
   ties by ascending index (np.argsort(counts, kind="stable")[:nkeep]).  Also: alive_total = sum of all counts, hm_all = sum over
   all members of (1 - p_est)^count, hm_kept = the same over the selected (the hit mass of search.run_block).  hist: scratch of
   maxc + 2 u32, maxc >= the largest count.  Returns nkeep, or -1 if a count exceeds maxc. */
int s200_select(const u16 *counts, u32 L, u32 nkeep, u32 maxc, double p_est, u32 *order, double *hm_all, double *hm_kept,
                int64_t *alive_total, u32 *hist) {
    if (nkeep > L) nkeep = L;
    memset(hist, 0, 4 * ((size_t)maxc + 2));
    for (u32 i = 0; i < L; i++) { if (counts[i] > maxc) return -1; hist[counts[i]]++; }
    int64_t at = 0;
    double ha = 0, hk = 0;
    u64 cum = 0;
    u32 cth = maxc + 1, need = 0;
    const double q = 1.0 - p_est;
    for (u32 c = 0; c <= maxc; c++) {
        const double w = pow(q, (double)c);
        at += (int64_t)c * hist[c];
        ha += hist[c] * w;
        if (cth > maxc && cum + hist[c] >= nkeep) { cth = c; need = (u32)(nkeep - cum); hk += need * w; }
        else if (cth > maxc) { cum += hist[c]; hk += hist[c] * w; }
    }
    *alive_total = at; *hm_all = ha; *hm_kept = hk;
    if (nkeep == 0) return 0;
    /* hist[c] -> the first position of class c in order (classes below cth are kept whole, class cth partly) */
    u32 pos = 0;
    for (u32 c = 0; c <= cth; c++) { u32 h = hist[c]; hist[c] = pos; pos += h; }
    u32 taken = 0;
    for (u32 i = 0; i < L; i++) {
        const u32 c = counts[i];
        if (c < cth) order[hist[c]++] = i;
        else if (c == cth && taken < need) { order[hist[c]++] = i; taken++; }
    }
    return (int)nkeep;
}

/* The alive rows of the members order[0..nsel) of the block of L members that starts at word w0 of every row of bits:
   member order[i]'s rows (ascending) go to rows_out[offs[i] .. offs[i+1]).  counts: the block's counts.  Scratch: rank (L u32),
   sel (L / 64 u64), cursor (nsel i64).  Returns the total number of rows, or -1 if it exceeds cap. */
int64_t s200_csr(const S200 *c, const u64 *bits, u64 w0, u32 L, const u32 *order, u32 nsel, const u16 *counts, u32 *rank,
                 u64 *sel, int64_t *cursor, int64_t *offs, u16 *rows_out, int64_t cap) {
    const u32 wb = L / 64;
    memset(sel, 0, 8 * (size_t)wb);
    offs[0] = 0;
    for (u32 i = 0; i < nsel; i++) {
        const u32 j = order[i];
        sel[j >> 6] |= 1ull << (j & 63);
        rank[j] = i;
        offs[i + 1] = offs[i] + counts[j];
        cursor[i] = offs[i];
    }
    if (offs[nsel] > cap) return -1;
    for (int r = 0; r < c->nU; r++) {
        const u64 *row = bits + (size_t)r * c->words + w0;
        for (u32 w = 0; w < wb; w++) {
            u64 v = row[w] & sel[w];
            while (v) {
                const u32 j = (w << 6) + (u32)__builtin_ctzll(v);
                rows_out[cursor[rank[j]]++] = (u16)r;
                v &= v - 1;
            }
        }
    }
    return offs[nsel];
}
