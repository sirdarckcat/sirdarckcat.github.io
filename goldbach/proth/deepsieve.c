/* deepsieve.c -- extend desert.py's sieve of the progression
 *
 *     P_t = 2^n (m0 + t Mc) + 1,   0 <= t < T,
 *
 * to the primes p in [B0, B1), for B1 up to ~2^62.  For each prime p it
 * computes a = m0 mod p and c = Mc mod p (GMP's mpn_mod_1 on the limbs),
 * e = 2^n mod p, and the unique root
 *
 *     t0 = -(1 + e a) (e c)^-1  (mod p)
 *
 * (the same formula as desert._sieve_chunk); since p >= B0 > T, t0 is the
 * only t < T that p can kill.  Every (t0, p) with t0 < T is printed as
 * "t p".  Nothing here is trusted downstream: deep_sieve.py re-checks
 * p | P_t for every printed pair with gmpy2 before dropping t.
 *
 * Build (only the runtime libgmp.so.10 is needed, no GMP headers):
 *     gcc -O3 -march=native -o deepsieve deepsieve.c -l:libgmp.so.10 -lpthread
 * Input (written by deep_sieve.py), little-endian u64s:
 *     n, T, B0, B1, L_m0, L_Mc, m0 limbs (L_m0), Mc limbs (L_Mc)
 * Usage: deepsieve input.bin nthreads > pairs.txt   (progress on stderr)
 */
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;
typedef unsigned __int128 u128;
extern u64 __gmpn_mod_1(const u64 *up, long n, u64 d);   /* mpn_mod_1 */

static u64 *m0, *Mc, n_exp, T, B0, B1, Lm0, LMc;
static u64 *bp;            /* odd base primes up to sqrt(B1) */
static long nbp;
#define SEG (1ULL << 24)   /* numbers per segment; odd ones stored */
static u64 next_lo, nseg_done, nseg_total, nprimes, npairs;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static double t_start;

static double now(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + 1e-9 * ts.tv_nsec;
}
static inline u64 mulmod(u64 a, u64 b, u64 p) { return (u64)((u128)a * b % p); }
static u64 powmod2(u64 e, u64 p) {
    u64 r = 1, b = 2 % p;
    while (e) { if (e & 1) r = mulmod(r, b, p); b = mulmod(b, b, p); e >>= 1; }
    return r;
}
static u64 invmod(u64 a, u64 p) {          /* p prime, 0 < a < p < 2^62 */
    __int128 t = 0, nt = 1; u64 r = p, nr = a;
    while (nr) {
        u64 q = r / nr, tr = r - q * nr;
        __int128 tt = t - (__int128)q * nt;
        t = nt; nt = tt; r = nr; nr = tr;
    }
    if (t < 0) t += p;
    return (u64)t;
}

static void *worker(void *arg) {
    (void)arg;
    uint8_t *s = malloc(SEG / 2);
    for (;;) {
        pthread_mutex_lock(&mu);
        u64 lo = next_lo; next_lo += SEG;
        pthread_mutex_unlock(&mu);
        if (lo >= B1) break;
        u64 hi = lo + SEG < B1 ? lo + SEG : B1;   /* numbers in [lo, hi); lo even */
        memset(s, 1, SEG / 2);                    /* s[i] <-> lo + 2i + 1 */
        for (long k = 0; k < nbp; k++) {
            u64 p = bp[k];
            if (p * p >= hi) break;
            u64 st = p * p;
            if (st < lo) { st = ((lo + p - 1) / p) * p; if (!(st & 1)) st += p; }
            for (u64 x = st; x < hi; x += 2 * p) s[(x - lo) >> 1] = 0;
        }
        u64 cnt = 0, local_pairs = 0;
        char buf[1 << 16]; size_t blen = 0;
        for (u64 i = 0; i < (hi - lo) / 2; i++) {
            if (!s[i]) continue;
            u64 p = lo + 2 * i + 1;
            if (p < B0 || p >= B1 || p < 3) continue;
            cnt++;
            u64 a = __gmpn_mod_1(m0, (long)Lm0, p), c = __gmpn_mod_1(Mc, (long)LMc, p);
            u64 e = powmod2(n_exp, p);
            u64 den = mulmod(e, c, p);
            if (!den) continue;                   /* p | Mc: a cover modulus */
            u64 num = (p - (1 + mulmod(e, a, p)) % p) % p;
            u64 t = mulmod(num, invmod(den, p), p);
            if (t < T) {
                blen += snprintf(buf + blen, sizeof buf - blen, "%llu %llu\n",
                                 (unsigned long long)t, (unsigned long long)p);
                local_pairs++;
                if (blen > sizeof buf - 64) {
                    pthread_mutex_lock(&mu); fwrite(buf, 1, blen, stdout); fflush(stdout);
                    pthread_mutex_unlock(&mu); blen = 0;
                }
            }
        }
        pthread_mutex_lock(&mu);
        if (blen) { fwrite(buf, 1, blen, stdout); fflush(stdout); }
        nprimes += cnt; npairs += local_pairs; nseg_done++;
        if (nseg_done % 64 == 0 || nseg_done == nseg_total)
            fprintf(stderr, "  %llu/%llu segments, up to ~%.4g, %llu primes, %llu pairs, %.0fs\n",
                    (unsigned long long)nseg_done, (unsigned long long)nseg_total, (double)hi,
                    (unsigned long long)nprimes, (unsigned long long)npairs, now() - t_start);
        pthread_mutex_unlock(&mu);
    }
    free(s);
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: deepsieve input.bin nthreads\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    u64 h[6];
    if (!f || fread(h, 8, 6, f) != 6) { fprintf(stderr, "bad input\n"); return 2; }
    n_exp = h[0]; T = h[1]; B0 = h[2]; B1 = h[3]; Lm0 = h[4]; LMc = h[5];
    m0 = malloc(8 * Lm0); Mc = malloc(8 * LMc);
    if (fread(m0, 8, Lm0, f) != Lm0 || fread(Mc, 8, LMc, f) != LMc) { fprintf(stderr, "short input\n"); return 2; }
    fclose(f);
    if (B0 <= T || B1 > (1ULL << 62)) { fprintf(stderr, "need T < B0 and B1 <= 2^62\n"); return 2; }
    int nth = atoi(argv[2]);
    /* base primes up to sqrt(B1) */
    u64 R = 2; while (R * R < B1) R++;
    uint8_t *c = calloc(R + 1, 1);
    bp = malloc(sizeof(u64) * (R / 2 + 16)); nbp = 0;
    for (u64 i = 3; i <= R; i += 2) if (!c[i]) { bp[nbp++] = i; for (u64 j = i * i; j <= R; j += 2 * i) c[j] = 1; }
    free(c);
    next_lo = B0 & ~1ULL;
    nseg_total = (B1 - next_lo + SEG - 1) / SEG;
    t_start = now();
    fprintf(stderr, "deepsieve: n=%llu T=%llu primes in [%.4g, %.4g), %llu+%llu limbs, %d threads, %llu segments\n",
            (unsigned long long)n_exp, (unsigned long long)T, (double)B0, (double)B1,
            (unsigned long long)Lm0, (unsigned long long)LMc, nth, (unsigned long long)nseg_total);
    pthread_t *th = malloc(sizeof(pthread_t) * nth);
    for (int i = 0; i < nth; i++) pthread_create(&th[i], NULL, worker, NULL);
    for (int i = 0; i < nth; i++) pthread_join(th[i], NULL);
    fprintf(stderr, "done: %llu primes, %llu pairs, %.0fs\n",
            (unsigned long long)nprimes, (unsigned long long)npairs, now() - t_start);
    return 0;
}
