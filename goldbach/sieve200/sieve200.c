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
#if defined(__AVX512BW__) || defined(__AVX2__)
#include <immintrin.h>
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

typedef struct S200 {
    int nU; u32 *U;
    u32 B; int logK; u64 K, words;
    u32 nS; u32 *S, *Minv, *cS, *nmark; double *rinv;
    u32 nSmall; unsigned char **pat; u32 *inv8, *step;
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
static u32 mod_big(const u64 *a, int nl, u32 s) {
    u64 r = 0;
    for (int i = nl - 1; i >= 0; i--) r = (u64)((((u128)r << 64) | a[i]) % s);
    return (u32)r;
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
    for (u32 p = 0; p < c->nSmall; p++) free(c->pat[p]);
    free(c->pat); free(c->inv8); free(c->step); free(c->U); free(c->S); free(c->Minv); free(c->cS); free(c->nmark); free(c->rinv);
    free(c);
}

/* U: the residual primes in the order of the rows.  B: sieve primes are 3 <= s < B, without those s | M and without the nExcl
   primes of excl (search.init_spec leaves the cover primes out as well).  K = 2^logK members a block (512 <= K <= 2^26).
   Returns NULL on bad input: unparsable hex, nU < 1, B < 5, or a residual q with q * B >= 2^50 (the row start of a prime is
   computed in double precision). */
S200 *s200_new(const char *N0_hex, const char *M_hex, const u32 *U, int nU, u32 B, int logK, const u32 *excl, int nExcl) {
    u64 *N0, *M; int nN, nM;
    if (parse_hex(N0_hex, &N0, &nN) || parse_hex(M_hex, &M, &nM)) return NULL;
    if (logK < 9 || logK > 26 || nU < 1 || B < 5) { free(N0); free(M); return NULL; }
    for (int i = 0; i < nU; i++)
        if ((u64)U[i] * B >= (1ull << 50)) { free(N0); free(M); return NULL; }
    S200 *c = calloc(1, sizeof *c);
    c->nU = nU; c->U = malloc(4 * (size_t)nU); memcpy(c->U, U, 4 * (size_t)nU);
    c->B = B; c->logK = logK; c->K = 1ull << logK; c->words = c->K / 64;
    char *comp = calloc((size_t)B + 1, 1);
    for (int i = 0; i < nExcl; i++) if (excl[i] < B) comp[excl[i]] = 2;     /* 2: left out, but still sieves its multiples */
    u32 cap = 1024; c->S = malloc(4 * cap); c->Minv = malloc(4 * cap); c->cS = malloc(4 * cap); c->nmark = malloc(4 * cap); c->rinv = malloc(8 * cap);
    for (u64 s = 2; s < B; s++) {                              /* the primes 3 <= s < B, as numpy's primerange(3, B) */
        if (comp[s] == 1) continue;
        for (u64 j = s * s; j < B; j += s) comp[j] = 1;
        if (s == 2 || comp[s]) continue;
        u32 mm = mod_big(M, nM, (u32)s);
        if (!mm) continue;                                     /* s divides M: removed, as init_spec does */
        if (c->nS == cap) {
            cap *= 2;
            c->S = realloc(c->S, 4 * cap); c->Minv = realloc(c->Minv, 4 * cap); c->cS = realloc(c->cS, 4 * cap);
            c->nmark = realloc(c->nmark, 4 * cap); c->rinv = realloc(c->rinv, 8 * cap);
        }
        u32 mi = inv_mod(mm, (u32)s), n0 = mod_big(N0, nN, (u32)s);
        u32 i = c->nS++;
        c->S[i] = (u32)s; c->Minv[i] = mi;
        c->cS[i] = (u32)(((u64)(s - n0) % s) * mi % s);       /* -N0/M mod s */
        c->rinv[i] = 1.0 / (double)s;
        c->nmark[i] = (u32)((c->K - 1) / s + 1);              /* marks a row: positions j, j+s, ... below K, the last may fall beyond */
    }
    free(comp); free(N0); free(M);
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

int s200_nprimes(const S200 *c) { return (int)c->nS; }
int s200_nrows(const S200 *c) { return c->nU; }
int s200_block_log(const S200 *c) { return c->logK; }
u32 s200_prime(const S200 *c, int i) { return c->S[i]; }
size_t s200_bits_bytes(const S200 *c) { return (size_t)c->nU * c->words * 8; }   /* bytes of the bit matrix a block fills */

/* ---------------------------------------------------------------- counting: a vertical counter over the rows */

static inline void fa(u64 a, u64 b, u64 c, u64 *s, u64 *k) { u64 t = a ^ b; *s = t ^ c; *k = (a & b) | (t & c); }

/* counts[j] = number of rows whose bit j is set; planes: 10 * words u64 of scratch (counts up to 1023 rows) */
static void count_rows(const u64 *bits, int nU, u64 words, u16 *counts, u64 *planes) {
    memset(planes, 0, 10 * words * 8);
    u64 *P0 = planes, *P1 = P0 + words, *P2 = P1 + words, *P3 = P2 + words, *P4 = P3 + words;
    u64 *P5 = P4 + words, *P6 = P5 + words, *P7 = P6 + words, *P8 = P7 + words, *P9 = P8 + words;
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
            P9[w] ^= carry;
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
            P9[w] ^= carry;
        }
    }
    for (u64 w = 0; w < words; w++) {                       /* planes -> counts */
        u64 p0 = P0[w], p1 = P1[w], p2 = P2[w], p3 = P3[w], p4 = P4[w], p5 = P5[w], p6 = P6[w], p7 = P7[w], p8 = P8[w], p9 = P9[w];
        u16 *o = counts + 64 * w;
        for (int b = 0; b < 64; b++)
            o[b] = (u16)(((p0 >> b) & 1) | (((p1 >> b) & 1) << 1) | (((p2 >> b) & 1) << 2) | (((p3 >> b) & 1) << 3) | (((p4 >> b) & 1) << 4)
                       | (((p5 >> b) & 1) << 5) | (((p6 >> b) & 1) << 6) | (((p7 >> b) & 1) << 7) | (((p8 >> b) & 1) << 8) | (((p9 >> b) & 1) << 9));
    }
}

/* ---------------------------------------------------------------- the sieve */

/* Sieves the members k0 .. k0 + K - 1.  bits: caller's buffer of s200_bits_bytes() bytes (row r at bits + r * K / 64 words),
   counts: K u16.  Either may be NULL: with bits NULL only the counts are returned (the rows still need the same memory, so
   the context's scratch is used: pass bits whenever the survivors are wanted).  Returns 0, or -1 on allocation failure. */
int s200_block(const S200 *c, u64 k0, u16 *counts, u64 *bits) {
    const u64 K = c->K, words = c->words, wmask = words - 1;
    int own = 0;
    if (!bits) { bits = aligned_alloc(64, s200_bits_bytes(c)); own = 1; if (!bits) return -1; }
    u32 *d = malloc(4 * (size_t)c->nS);
    if (!d) { if (own) free(bits); return -1; }
    for (u32 p = 0; p < c->nS; p++) {
        u32 s = c->S[p];
        d[p] = (u32)((c->cS[p] + s - (u32)(k0 % s)) % s);      /* first member offset with s | N - q is (q * Minv + d) mod s */
    }
    const u32 nSmall = c->nSmall, nS = c->nS;
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
        for (u32 p = nSmall; p < nS; p++) {
            u64 s = c->S[p];
            u64 x = q * c->Minv[p] + d[p];
            u64 j = x - (u64)((double)x * c->rinv[p]) * s;
            if ((int64_t)j < 0) j += s;
            if (j >= s) j -= s;
            /* fixed trip count; positions >= K clear nothing (the shifted-in bit is 0) and hit a harmless word */
            for (u32 i = c->nmark[p]; i; i--, j += s) row[(j >> 6) & wmask] &= ~((u64)(j < K) << (j & 63));
        }
    }
    free(d);
    int rc = 0;
    if (counts) {
        u64 *planes = malloc(10 * words * 8);
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
