/* sieve.c -- T5: sieve the members N_k = N0 + k*D (D = 2M, k = 0 .. K-1) on the rows left by the cover.
 * A row q survives for member k when N_k - q has no prime factor s in (X, B]; N_k - q is already coprime to 2M. For a prime s
 * and a row q, the members with s | N_k - q are k = k0 (mod s), k0 = (q - N0) * D^-1 (mod s): rows are processed one at a time
 * with a bitmap over the members, so a member is counted once per row whatever the number of primes dividing it.
 *
 *   setup file (written by members.py): int32 u, int32 nlimbs, then u int32 rows, then N0 and D as nlimbs uint64 limbs each
 *   (little endian, least significant limb first)
 *   ./sieve setup.bin X B K counts.u16                 pass 1: survivors per member -> counts (uint16[K])
 *   ./sieve setup.bin X B K counts.u16 cand.txt out.txt  pass 2: for the members listed in cand.txt (one k per line), their
 *                                                        surviving rows -> out.txt ("k S q1 q2 ...")
 *   gcc -O3 -march=native -fopenmp -o sieve sieve.c -lm
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

static uint32_t mod_limbs(const uint64_t *L, int n, uint32_t s) {           /* (sum L[i] 2^(64 i)) mod s */
    unsigned __int128 r = 0;
    for (int i = n - 1; i >= 0; i--) r = ((r << 64) | L[i]) % s;
    return (uint32_t)r;
}
static uint32_t inv_mod(uint32_t a, uint32_t m) {                            /* a^-1 mod m, a != 0 */
    int64_t t = 0, nt = 1, r = m, nr = a;
    while (nr) { int64_t q = r / nr, x; x = t - q * nt; t = nt; nt = x; x = r - q * nr; r = nr; nr = x; }
    return (uint32_t)(t < 0 ? t + m : t);
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: sieve setup.bin X B K counts.u16 [cand.txt out.txt]\n"); return 1; }
    uint32_t X = (uint32_t)atol(argv[2]); uint64_t B = (uint64_t)atoll(argv[3]); int64_t K = atoll(argv[4]);
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 1; }
    int32_t u, nl; if (fread(&u, 4, 1, f) != 1 || fread(&nl, 4, 1, f) != 1) return 1;
    int32_t *rows = malloc(4 * (size_t)u); uint64_t *N0 = malloc(8 * (size_t)nl), *D = malloc(8 * (size_t)nl);
    if (fread(rows, 4, u, f) != (size_t)u || fread(N0, 8, nl, f) != (size_t)nl || fread(D, 8, nl, f) != (size_t)nl) { fprintf(stderr, "short setup\n"); return 1; }
    fclose(f);
    /* primes in (X, B] by a sieve of Eratosthenes on odd numbers */
    uint64_t nodd = B / 2 + 1; uint8_t *comp = calloc(nodd, 1);
    for (uint64_t i = 3; i * i <= B; i += 2) if (!comp[i / 2]) for (uint64_t j = i * i; j <= B; j += 2 * i) comp[j / 2] = 1;
    int64_t np = 0; for (uint64_t i = X + 1 + ((X + 1) % 2 == 0); i <= B; i += 2) if (!comp[i / 2]) np++;
    uint32_t *P = malloc(4 * np), *n0 = malloc(4 * np), *iv = malloc(4 * np);
    np = 0; for (uint64_t i = X + 1 + ((X + 1) % 2 == 0); i <= B; i += 2) if (!comp[i / 2]) P[np++] = (uint32_t)i;
    free(comp);
    double t0 = omp_get_wtime();
    #pragma omp parallel for schedule(static)
    for (int64_t j = 0; j < np; j++) { uint32_t s = P[j]; n0[j] = mod_limbs(N0, nl, s); iv[j] = inv_mod(mod_limbs(D, nl, s), s); }
    fprintf(stderr, "%lld primes in (%u, %llu]; residues of N0 and D in %.1f s\n", (long long)np, X, (unsigned long long)B, omp_get_wtime() - t0);
    int pass2 = argc >= 8;
    int64_t ncand = 0, *cand = NULL; char **surv = NULL; int *slen = NULL, *scap = NULL;
    if (pass2) {
        FILE *c = fopen(argv[6], "r"); if (!c) { perror(argv[6]); return 1; }
        int64_t cap = 1024; cand = malloc(8 * cap); long long v;
        while (fscanf(c, "%lld", &v) == 1) { if (ncand == cap) { cap *= 2; cand = realloc(cand, 8 * cap); } cand[ncand++] = v; }
        fclose(c);
        surv = calloc(ncand, sizeof(char *)); slen = calloc(ncand, sizeof(int)); scap = calloc(ncand, sizeof(int));
    }
    size_t words = (size_t)(K + 63) / 64;
    int nth = omp_get_max_threads();
    uint16_t **cnt = calloc(nth, sizeof(uint16_t *));
    t0 = omp_get_wtime();
    #pragma omp parallel
    {
        int th = omp_get_thread_num();
        uint64_t *bm = malloc(8 * words);
        uint16_t *c = pass2 ? NULL : calloc((size_t)K, 2); cnt[th] = c;
        #pragma omp for schedule(dynamic, 4)
        for (int i = 0; i < u; i++) {
            uint32_t q = (uint32_t)rows[i];
            memset(bm, 0, 8 * words);
            for (int64_t j = 0; j < np; j++) {
                uint32_t s = P[j];
                uint64_t t = (q % s + (uint64_t)s - n0[j]) % s;
                uint64_t k0 = t * iv[j] % s;
                for (uint64_t k = k0; k < (uint64_t)K; k += s) bm[k >> 6] |= 1ull << (k & 63);
            }
            if (!pass2) {
                for (int64_t k = 0; k < K; k++) c[k] += !((bm[k >> 6] >> (k & 63)) & 1);
            } else {
                for (int64_t a = 0; a < ncand; a++) {
                    int64_t k = cand[a];
                    if (!((bm[k >> 6] >> (k & 63)) & 1)) {
                        #pragma omp critical
                        {
                            if (slen[a] + 12 >= scap[a]) { scap[a] = scap[a] ? 2 * scap[a] : 4096; surv[a] = realloc(surv[a], scap[a]); }
                            slen[a] += sprintf(surv[a] + slen[a], " %u", q);
                        }
                    }
                }
            }
            if (th == 0 && i % 200 == 0) fprintf(stderr, "  row %d of %d (%.0f s)\n", i, u, omp_get_wtime() - t0);
        }
        free(bm);
    }
    if (!pass2) {
        uint16_t *tot = calloc((size_t)K, 2);
        for (int th = 0; th < nth; th++) if (cnt[th]) { for (int64_t k = 0; k < K; k++) tot[k] += cnt[th][k]; free(cnt[th]); }
        FILE *o = fopen(argv[5], "wb"); fwrite(tot, 2, (size_t)K, o); fclose(o);
        double m = 0, m2 = 0; uint16_t lo = 65535; for (int64_t k = 0; k < K; k++) { m += tot[k]; m2 += (double)tot[k] * tot[k]; if (tot[k] < lo) lo = tot[k]; }
        m /= K; fprintf(stderr, "pass 1: %lld members, survivors mean %.2f sd %.2f min %u (%.0f s)\n", (long long)K, m, __builtin_sqrt(m2 / K - m * m), lo, omp_get_wtime() - t0);
    } else {
        FILE *o = fopen(argv[7], "w");
        for (int64_t a = 0; a < ncand; a++) {
            int n = 0; for (int i = 0; i < slen[a]; i++) n += surv[a][i] == ' ';
            fprintf(o, "%lld %d%s\n", (long long)cand[a], n, surv[a] ? surv[a] : "");
        }
        fclose(o); fprintf(stderr, "pass 2: survivor rows of %lld members (%.0f s)\n", (long long)ncand, omp_get_wtime() - t0);
    }
    return 0;
}
