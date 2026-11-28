/* tscan.c -- scan a progression N = N0 + k*M for Goldbach deserts.
 *
 * A k is reported when N - q fails the base-2 Fermat test for EVERY prime q
 * in the residual list U, i.e. every such N - q is proved composite.  (The
 * primes below Q that are not in U are composite complements by the cover
 * congruences that define the progression.)  A k is dropped as soon as one
 * N - q passes the test: that q is almost surely a Goldbach summand.
 *
 * Per block of K consecutive k: a bit sieve over (q, k) by the primes s <= B
 * that do not divide M (for s < SMALLP by ANDing 512-bit slices of a periodic
 * bit pattern, for larger s one bit at a time), then a count a(k) of the q
 * whose N - q survived, then
 * Fermat tests on the survivors of the k with a(k) <= T, row by row, stopping
 * at the first probable prime.  A k succeeds with probability about
 * (1 - p)^a(k), p = chance that a survivor is prime, so the emptiest few
 * percent of the k carry most of the hits; T < 255 skips the rest untested.
 * The histogram of a(k) is printed so the caller can compute exactly which
 * share of the expected hits the tested k hold.
 *
 *   gcc -O3 -march=native -fopenmp -DNL=2 -o tscan2 tscan.c
 *   ./tscan2 job.txt kstart kend [B] [log2K] [T]    scan [kstart, kend)
 *   ./tscan2 --fermat < hexlines                     print 1/0 per number
 *
 * job.txt: three lines:  N0 in hex / M in hex / count followed by the primes of U.
 * NL = number of 64-bit limbs; every N - q must be below 2^(64*NL - 1).
 * Output: one line "S <k>" per reported k, then one "STATS ..." line.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <omp.h>
#ifdef __AVX512BW__
#include <immintrin.h>
#endif

#ifndef NL
#define NL 2
#endif
#define W (64 * NL)
#ifndef SMALLP
#define SMALLP 384            /* sieve primes below this use the pattern sieve (needs AVX-512) */
#endif

typedef uint64_t u64;
typedef uint32_t u32;
typedef unsigned __int128 u128;

static inline int bitlen(const u64 *a) {
    for (int i = NL - 1; i >= 0; i--)
        if (a[i]) return 64 * i + 64 - __builtin_clzll(a[i]);
    return 0;
}

static inline int ge(const u64 *a, const u64 *b) {
    for (int i = NL - 1; i >= 0; i--)
        if (a[i] != b[i]) return a[i] > b[i];
    return 1;
}

static inline void sub(u64 *r, const u64 *a, const u64 *b) {
    u64 br = 0;
    for (int i = 0; i < NL; i++) {
        u128 d = (u128)a[i] - b[i] - br;
        r[i] = (u64)d;
        br = (u64)(d >> 64) & 1;
    }
}

/* r = a + k*m; returns the carry out of the top limb */
static inline u64 addmul1(u64 *r, const u64 *a, const u64 *m, u64 k) {
    u128 c = 0;
    for (int i = 0; i < NL; i++) {
        c += (u128)m[i] * k + a[i];
        r[i] = (u64)c;
        c >>= 64;
    }
    return (u64)c;
}

/* r = a*b / 2^W mod n   (a, b < n < 2^(W-1), n odd, ninv = -1/n mod 2^64) */
static inline void montmul(u64 *r, const u64 *a, const u64 *b, const u64 *n, u64 ninv) {
    u64 t[NL + 2];
    for (int i = 0; i < NL + 2; i++) t[i] = 0;
    for (int i = 0; i < NL; i++) {
        u128 c = 0;
        for (int j = 0; j < NL; j++) {
            c += (u128)a[j] * b[i] + t[j];
            t[j] = (u64)c;
            c >>= 64;
        }
        c += t[NL];
        t[NL] = (u64)c;
        t[NL + 1] = (u64)(c >> 64);
        u64 m = t[0] * ninv;
        c = ((u128)m * n[0] + t[0]) >> 64;
        for (int j = 1; j < NL; j++) {
            c += (u128)m * n[j] + t[j];
            t[j - 1] = (u64)c;
            c >>= 64;
        }
        c += t[NL];
        t[NL - 1] = (u64)c;
        t[NL] = t[NL + 1] + (u64)(c >> 64);
    }
    if (t[NL] || ge(t, n)) sub(r, t, n);
    else for (int i = 0; i < NL; i++) r[i] = t[i];
}

/* v = 2v mod n   (v < n < 2^(W-1)) */
static inline void dbl(u64 *v, const u64 *n) {
    for (int i = NL - 1; i > 0; i--) v[i] = (v[i] << 1) | (v[i - 1] >> 63);
    v[0] <<= 1;
    if (ge(v, n)) sub(v, v, n);
}

/* 1 iff 2^(n-1) = 1 mod n.  n odd, 2^9 < n < 2^(W-1) (so that n - 1 - W > 0).
 *
 * The residue v is kept as a plain number 2^F mod n.  A Montgomery squaring
 * maps F to 2F - W and a doubling maps F to F + 1, so G = F - W follows the
 * ordinary binary ladder.  Running that ladder for the exponent n - 1 - W
 * ends at F = n - 1, and no conversion to or from Montgomery form is needed.
 * The start is v = 2^(b-2) < n (b = bit length of n), doubled up to G = 1.
 */
static inline int fermat2(const u64 *n) {
    int b = bitlen(n);
    u64 ninv = n[0];
    for (int i = 0; i < 5; i++) ninv *= 2 - n[0] * ninv;
    ninv = -ninv;
    u64 e[NL], w[NL], v[NL];
    for (int i = 0; i < NL; i++) { e[i] = n[i]; w[i] = 0; v[i] = 0; }
    w[0] = (u64)W + 1;                    /* e = n - 1 - W */
    sub(e, e, w);
    v[(b - 2) >> 6] = 1ull << ((b - 2) & 63);
    for (int i = 0; i < W - b + 3; i++) dbl(v, n);
    for (int i = bitlen(e) - 2; i >= 0; i--) {
        montmul(v, v, v, n, ninv);
        if ((e[i >> 6] >> (i & 63)) & 1) dbl(v, n);
    }
    if (v[0] != 1) return 0;
    for (int i = 1; i < NL; i++) if (v[i]) return 0;
    return 1;
}

static int parse_hex(const char *s, u64 *out) {
    for (int i = 0; i < NL; i++) out[i] = 0;
    size_t len = strlen(s);
    while (len && (s[len - 1] == '\n' || s[len - 1] == '\r' || s[len - 1] == ' ')) len--;
    if (len >= 2 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) { s += 2; len -= 2; }
    if (len == 0) return -1;
    for (size_t i = 0; i < len; i++) {
        char c = s[len - 1 - i];
        int d = (c >= '0' && c <= '9') ? c - '0' : (c >= 'a' && c <= 'f') ? c - 'a' + 10
              : (c >= 'A' && c <= 'F') ? c - 'A' + 10 : -1;
        if (d < 0) return -1;
        if (i / 16 >= NL) { if (d) return -2; continue; }
        out[i / 16] |= (u64)d << (4 * (i % 16));
    }
    return 0;
}

static u32 mod_u32(const u64 *a, u32 s) {
    u64 r = 0;
    for (int i = NL - 1; i >= 0; i--) r = (u64)((((u128)r << 64) | a[i]) % s);
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

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

int main(int argc, char **argv) {
    static char line[1 << 16];
    if (argc == 2 && !strcmp(argv[1], "--fermat")) {
        while (fgets(line, sizeof line, stdin)) {
            u64 n[NL];
            if (parse_hex(line, n)) { puts("?"); continue; }
            if (!(n[0] & 1) || bitlen(n) < 10 || bitlen(n) > W - 1) { puts("?"); continue; }
            puts(fermat2(n) ? "1" : "0");
        }
        return 0;
    }
    if (argc < 4) {
        fprintf(stderr, "usage: %s job.txt kstart kend [B] [log2K] [T]\n", argv[0]);
        return 2;
    }
    u64 k0 = strtoull(argv[2], 0, 10), k1 = strtoull(argv[3], 0, 10);
    u32 B = argc > 4 ? (u32)strtoul(argv[4], 0, 10) : 1u << 17;
    int logK = argc > 5 ? atoi(argv[5]) : 17;
    int T = argc > 6 ? atoi(argv[6]) : 255;
    u64 K = 1ull << logK, words = K / 64;
    u64 stride = ((K + B) / 64 + 8) & ~7ull;         /* row length in words: K bits + B bits of padding */

    FILE *f = fopen(argv[1], "r");
    if (!f) { perror(argv[1]); return 2; }
    u64 N0[NL], M[NL];
    if (!fgets(line, sizeof line, f) || parse_hex(line, N0)) { fprintf(stderr, "bad N0\n"); return 2; }
    if (!fgets(line, sizeof line, f) || parse_hex(line, M)) { fprintf(stderr, "bad M\n"); return 2; }
    int nU;
    if (fscanf(f, "%d", &nU) != 1 || nU < 1 || nU > 100000) { fprintf(stderr, "bad U count\n"); return 2; }
    u32 *U = malloc(sizeof(u32) * nU);
    for (int i = 0; i < nU; i++) {
        if (fscanf(f, "%u", &U[i]) != 1 || !(U[i] & 1)) { fprintf(stderr, "bad U entry\n"); return 2; }
    }
    fclose(f);
    if (N0[0] & 1 || M[0] & 1) { fprintf(stderr, "N0 and M must be even\n"); return 2; }
    {   /* every N in range must leave the top bit free */
        u64 top[NL];
        if (k1 <= k0 || addmul1(top, N0, M, k1) || bitlen(top) > W - 1) {
            fprintf(stderr, "range empty or N too large for NL=%d\n", NL);
            return 2;
        }
        u64 lo[NL];
        addmul1(lo, N0, M, k0);
        if (bitlen(lo) < 40) { fprintf(stderr, "N too small\n"); return 2; }
    }

    /* sieve primes: 3 <= s <= B, s not dividing M */
    char *comp = calloc(B + 1, 1);
    u32 nS = 0, cap = 1024;
    u32 *S = malloc(4 * cap), *Minv = malloc(4 * cap), *cS = malloc(4 * cap);
    double *rinv = malloc(8 * cap);
    u32 *nmark = malloc(4 * cap);
    for (u64 s = 2; s <= B; s++) {
        if (comp[s]) continue;
        for (u64 j = s * s; j <= B; j += s) comp[j] = 1;
        if (s == 2) continue;
        u32 mm = mod_u32(M, (u32)s);
        if (!mm) continue;
        if (nS == cap) {
            cap *= 2;
            S = realloc(S, 4 * cap); Minv = realloc(Minv, 4 * cap); cS = realloc(cS, 4 * cap);
            rinv = realloc(rinv, 8 * cap); nmark = realloc(nmark, 4 * cap);
        }
        u32 mi = inv_mod(mm, (u32)s);
        u32 n0 = mod_u32(N0, (u32)s);
        S[nS] = (u32)s; Minv[nS] = mi;
        cS[nS] = (u32)(((u64)(s - n0) % s) * mi % s);   /* -N0/M mod s */
        rinv[nS] = 1.0 / (double)s;
        nmark[nS] = (u32)((K - 1) / s + 1);          /* marks per row and block, the last may fall in the padding */
        nS++;
    }
    free(comp);

    /* Pattern sieve tables.  For a small prime s, pat is a bit string (bit i of byte i/8, least
     * significant bit first) with a 0 exactly where i = 0 mod s.  Loading 64 bytes at byte offset t
     * gives a 512-bit mask whose zeros sit at b = -8t mod s, so the offset for "first zero at f" is
     * t = -f/8 mod s, and the next 512-bit slice is at t + 64 mod s. */
    u32 nSmall = 0;
#ifdef __AVX512BW__
    while (nSmall < nS && S[nSmall] < SMALLP) nSmall++;
    if (logK < 9) nSmall = 0;
#endif
    unsigned char **pat = malloc(sizeof(*pat) * (nSmall + 1));
    u32 *inv8 = malloc(4 * (nSmall + 1)), *step = malloc(4 * (nSmall + 1));
    for (u32 p = 0; p < nSmall; p++) {
        u32 sp = S[p];
        pat[p] = aligned_alloc(64, ((sp + 64 + 63) / 64 + 1) * 64);
        memset(pat[p], 0xff, ((sp + 64 + 63) / 64 + 1) * 64);
        for (u64 i = 0; i < 8ull * (sp + 64); i += sp) pat[p][i >> 3] &= (unsigned char)~(1u << (i & 7));
        inv8[p] = inv_mod(8 % sp, sp);
        step[p] = 64 % sp;
    }

    u64 nblocks = (k1 - k0 + K - 1) / K;
    u64 tot_tests = 0, tot_prps = 0, tot_found = 0, tot_sel = 0, tot_hist[256];
    memset(tot_hist, 0, sizeof tot_hist);
    double t0 = now();

    #pragma omp parallel
    {
        u64 *bits = aligned_alloc(64, (size_t)nU * stride * 8);
        u32 *d = malloc(4 * (size_t)nS);
        unsigned char *cnt = aligned_alloc(64, K);
        u64 tests = 0, prps = 0, found = 0, sel = 0, hist[256];
        memset(hist, 0, sizeof hist);
        #pragma omp for schedule(dynamic, 1) nowait
        for (u64 blk = 0; blk < nblocks; blk++) {
            u64 kb = k0 + blk * K;
            u64 len = k1 - kb < K ? k1 - kb : K;
            for (u32 p = 0; p < nS; p++) {
                u32 s = S[p];
                d[p] = (u32)((cS[p] + s - (u32)(kb % s)) % s);
            }
            for (int r = 0; r < nU; r++) {
                u64 *row = bits + (size_t)r * stride;
                u64 q = U[r];
#ifdef __AVX512BW__
                if (nSmall) {
                    u32 tt[SMALLP];
                    for (u32 p = 0; p < nSmall; p++) {
                        u64 s = S[p];
                        u64 x = q * Minv[p] + d[p];
                        u64 f = x % s;                              /* first k offset with s | N - q */
                        tt[p] = (u32)((s - f) % s * inv8[p] % s);
                    }
                    for (u64 c = 0; c < words; c += 8) {
                        __m512i acc = _mm512_set1_epi64(-1);
                        for (u32 p = 0; p < nSmall; p++) {
                            acc = _mm512_and_si512(acc, _mm512_loadu_si512((const void *)(pat[p] + tt[p])));
                            u32 t = tt[p] + step[p];
                            tt[p] = t >= S[p] ? t - S[p] : t;
                        }
                        _mm512_store_si512((void *)(row + c), acc);
                    }
                } else
#endif
                memset(row, 0xff, words * 8);
                for (u32 p = nSmall; p < nS; p++) {
                    u64 s = S[p];
                    u64 x = q * Minv[p] + d[p];
                    u64 j = x - (u64)((double)x * rinv[p]) * s;
                    if ((int64_t)j < 0) j += s;
                    if (j >= s) j -= s;
                    /* fixed trip count: positions >= K land in the padding and are ignored */
                    for (u32 i = nmark[p]; i; i--, j += s) row[j >> 6] &= ~(1ull << (j & 63));
                }
            }
            memset(cnt, 0, K);                       /* a(k) = survivors in column k, saturating at 255 */
            for (int r = 0; r < nU; r++) {
                const u64 *row = bits + (size_t)r * stride;
#ifdef __AVX512BW__
                const __m512i one = _mm512_set1_epi8(1);
                for (u64 wd = 0; wd < words; wd++) {
                    __m512i c = _mm512_load_si512((const void *)(cnt + 64 * wd));
                    _mm512_store_si512((void *)(cnt + 64 * wd), _mm512_mask_adds_epu8(c, (__mmask64)row[wd], c, one));
                }
#else
                for (u64 j = 0; j < K; j++) cnt[j] += ((row[j >> 6] >> (j & 63)) & 1) & (cnt[j] != 255);
#endif
            }
            u64 Nb[NL];
            addmul1(Nb, N0, M, kb);
            for (u64 j = 0; j < len; j++) {
                u64 Nk[NL], n[NL], qq[NL];
                int have = 0, killed = 0;
                hist[cnt[j]]++;
                if (cnt[j] > T) continue;
                sel++;
                for (int r = 0; r < nU; r++) {
                    if (!((bits[(size_t)r * stride + (j >> 6)] >> (j & 63)) & 1)) continue;
                    if (!have) { addmul1(Nk, Nb, M, j); have = 1; }
                    for (int i = 1; i < NL; i++) qq[i] = 0;
                    qq[0] = U[r];
                    sub(n, Nk, qq);
                    tests++;
                    if (fermat2(n)) { prps++; killed = 1; break; }
                }
                if (!killed) {
                    found++;
                    #pragma omp critical
                    { printf("S %llu\n", (unsigned long long)(kb + j)); fflush(stdout); }
                }
            }
        }
        #pragma omp critical
        {
            tot_tests += tests; tot_prps += prps; tot_found += found; tot_sel += sel;
            for (int i = 0; i < 256; i++) tot_hist[i] += hist[i];
        }
        free(bits); free(d); free(cnt);
    }
    double dt = now() - t0;
    u64 tot_alive = 0;
    for (int i = 0; i < 256; i++) tot_alive += i * tot_hist[i];
    printf("STATS k0=%llu k1=%llu nU=%d sieve_primes=%u B=%u K=%llu T=%d selected=%llu tests=%llu prps=%llu "
           "alive=%llu found=%llu seconds=%.1f rate=%.0f threads=%d hist=",
           (unsigned long long)k0, (unsigned long long)k1, nU, nS, B, (unsigned long long)K, T,
           (unsigned long long)tot_sel, (unsigned long long)tot_tests, (unsigned long long)tot_prps,
           (unsigned long long)tot_alive, (unsigned long long)tot_found,
           dt, (k1 - k0) / dt, omp_get_max_threads());
    for (int i = 0, first = 1; i < 256; i++)
        if (tot_hist[i]) { printf("%s%d:%llu", first ? "" : ",", i, (unsigned long long)tot_hist[i]); first = 0; }
    printf("\n");
    return 0;
}
