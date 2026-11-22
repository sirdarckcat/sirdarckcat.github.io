/* gsample: the distribution of g(N) for random even N in [A, B), B < 2^63.
 *
 * g(N) is the least prime p with N - p prime.  For each sampled N the primes p = 3, 5, 7, ... are tried
 * in order (p = 2 never works for N > 4); N - p is first checked for a factor below 100 through
 * precomputed residues, then by a strong probable prime test to base 2, and a number that passes is
 * confirmed with the bases 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37 (deterministic below 2^64).
 *
 *   gcc -O3 -march=native -fopenmp -o gsample gsample.c
 *   ./gsample A B samples seed        -> lines "g count" for every g that occurred
 */
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint64_t u64;
typedef unsigned __int128 u128;

#define PMAX 60000
#define NSMALL 24
static const int SMALL[NSMALL] = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97};
static int nP;
static u64 Pr[8000];
static unsigned char pm[8000][NSMALL];

static inline u64 mont_inv(u64 n) { u64 x = n; for (int i = 0; i < 6; i++) x *= 2 - n * x; return x; }      /* n^-1 mod 2^64 */
static inline u64 redc(u128 t, u64 n, u64 ninv) {
    u64 m = (u64)t * ninv;
    u64 hi = (u64)(t >> 64), mh = (u64)(((u128)m * n) >> 64);
    return hi >= mh ? hi - mh : hi - mh + n;
}
static inline u64 mmul(u64 a, u64 b, u64 n, u64 ninv) { return redc((u128)a * b, n, ninv); }

/* strong probable prime test to base b for odd n > b */
static int sprp(u64 n, u64 b) {
    u64 ninv = mont_inv(n);
    u64 one = (u64)(((u128)1 << 64) % n), r2 = (u64)(((u128)one * one) % n);
    u64 d = n - 1; int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    u64 x = one, base = mmul(b % n, r2, n, ninv);
    for (u64 e = d; e; e >>= 1) { if (e & 1) x = mmul(x, base, n, ninv); base = mmul(base, base, n, ninv); }
    u64 minus1 = n - one;
    if (x == one || x == minus1) return 1;
    for (int i = 1; i < s; i++) { x = mmul(x, x, n, ninv); if (x == minus1) return 1; if (x == one) return 0; }
    return 0;
}
static int is_prime(u64 n) {
    static const u64 B[11] = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    if (!sprp(n, 2)) return 0;
    for (int i = 0; i < 11; i++) if (!sprp(n, B[i])) return 0;
    return 1;
}

static inline u64 rotl(u64 x, int k) { return (x << k) | (x >> (64 - k)); }
static inline u64 next(u64 *s) {
    u64 r = rotl(s[1] * 5, 7) * 9, t = s[1] << 17;
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= t; s[3] = rotl(s[3], 45);
    return r;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s A B samples seed\n", argv[0]); return 2; }
    u64 A = strtoull(argv[1], 0, 10), Bd = strtoull(argv[2], 0, 10), samples = strtoull(argv[3], 0, 10), seed = strtoull(argv[4], 0, 10);
    A += A & 1;
    u64 span = (Bd - A) / 2;
    static char comp[PMAX + 1];
    for (int i = 2; i <= PMAX; i++) {
        if (comp[i]) continue;
        for (long j = (long)i * i; j <= PMAX; j += i) comp[j] = 1;
        if (i > 2) { Pr[nP] = i; for (int q = 0; q < NSMALL; q++) pm[nP][q] = (unsigned char)(i % SMALL[q]); nP++; }
    }
    u64 *tot = calloc(nP + 1, 8);
    #pragma omp parallel
    {
        u64 *cnt = calloc(nP + 1, 8);
        u64 s[4];
        u64 z = seed * 0x9E3779B97F4A7C15ull + 0x1234567ull * (omp_get_thread_num() + 1);
        for (int i = 0; i < 4; i++) { z += 0x9E3779B97F4A7C15ull; u64 x = z; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull; x = (x ^ (x >> 27)) * 0x94D049BB133111EBull; s[i] = x ^ (x >> 31); }
        #pragma omp for schedule(static)
        for (u64 it = 0; it < samples; it++) {
            u64 N = A + 2 * (next(s) % span);
            unsigned char nq[NSMALL];
            for (int q = 0; q < NSMALL; q++) nq[q] = (unsigned char)(N % SMALL[q]);
            int i;
            for (i = 0; i < nP; i++) {
                const unsigned char *r = pm[i];
                int dead = 0;
                for (int q = 0; q < NSMALL; q++) if (r[q] == nq[q]) { dead = 1; break; }
                if (dead && N - Pr[i] > 97) continue;
                if (is_prime(N - Pr[i])) break;
            }
            cnt[i]++;
        }
        #pragma omp critical
        for (int i = 0; i <= nP; i++) tot[i] += cnt[i];
        free(cnt);
    }
    for (int i = 0; i < nP; i++) if (tot[i]) printf("%llu %llu\n", (unsigned long long)Pr[i], (unsigned long long)tot[i]);
    if (tot[nP]) printf("NONE %llu\n", (unsigned long long)tot[nP]);
    return 0;
}
