/* Kernels for the ball-and-box measurements (T1).  Values are odd primes below 2^32.
   fastmod: Lemire, Kaser, Kurz (2019), exact for 32-bit operands.                      */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>
typedef unsigned __int128 u128;
static inline uint64_t M_of(uint32_t d) { return UINT64_C(0xFFFFFFFFFFFFFFFF) / d + 1; }
static inline uint32_t fmod32(uint32_t a, uint64_t M, uint32_t d) { return (uint32_t)(((u128)(M * a) * d) >> 64); }
static inline uint64_t sm64(uint64_t *s) { uint64_t z = (*s += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static inline double u01(uint64_t *s) { return (sm64(s) >> 11) * (1.0 / 9007199254740992.0); }
static inline uint64_t below(uint64_t *s, uint64_t n) { return (uint64_t)(((u128)sm64(s) * n) >> 64); }
static uint32_t maxof(const uint32_t *B, int64_t nB) { uint32_t m = 0; for (int64_t i = 0; i < nB; i++) if (B[i] > m) m = B[i]; return m; }

/* For each r in B: E = sum_c C(n_c,2) over the classes of r, and the number of classes with n_c >= 2, 3, 4. */
void occupancy(const uint32_t *S, int64_t nS, const uint32_t *B, int64_t nB, double *E, int32_t *c2, int32_t *c3, int32_t *c4, int threads) {
    uint32_t mx = maxof(B, nB);
    #pragma omp parallel num_threads(threads)
    {
        uint32_t *cnt = calloc(mx + 1, sizeof(uint32_t));
        #pragma omp for schedule(dynamic, 16)
        for (int64_t i = 0; i < nB; i++) {
            uint32_t r = B[i]; uint64_t M = M_of(r);
            for (int64_t j = 0; j < nS; j++) cnt[fmod32(S[j], M, r)]++;
            double e = 0; int32_t a2 = 0, a3 = 0, a4 = 0;
            for (uint32_t c = 0; c < r; c++) { uint32_t n = cnt[c]; cnt[c] = 0; if (n >= 2) { e += 0.5 * n * (n - 1); a2++; if (n >= 3) a3++; if (n >= 4) a4++; } }
            E[i] = e; c2[i] = a2; c3[i] = a3; c4[i] = a4;
        }
        free(cnt);
    }
}

/* X = number of (pair for r1, pair for r2) sharing a survivor = sum_s (n1(s) - 1)(n2(s) - 1); pairs sharing both
   survivors cannot occur when r1*r2 exceeds every value. */
void conflicts(const uint32_t *S, int64_t nS, const uint32_t *R1, const uint32_t *R2, int64_t np, double *X, int threads) {
    uint32_t mx = maxof(R1, np), m2 = maxof(R2, np); if (m2 > mx) mx = m2;
    #pragma omp parallel num_threads(threads)
    {
        uint32_t *a = calloc(mx + 1, sizeof(uint32_t)), *b = calloc(mx + 1, sizeof(uint32_t));
        #pragma omp for schedule(dynamic, 4)
        for (int64_t i = 0; i < np; i++) {
            uint32_t r1 = R1[i], r2 = R2[i]; uint64_t M1 = M_of(r1), M2 = M_of(r2);
            for (int64_t j = 0; j < nS; j++) { a[fmod32(S[j], M1, r1)]++; b[fmod32(S[j], M2, r2)]++; }
            double x = 0;
            for (int64_t j = 0; j < nS; j++) x += (double)(a[fmod32(S[j], M1, r1)] - 1) * (double)(b[fmod32(S[j], M2, r2)] - 1);
            X[i] = x;
            for (int64_t j = 0; j < nS; j++) { a[fmod32(S[j], M1, r1)] = 0; b[fmod32(S[j], M2, r2)] = 0; }
        }
        free(a); free(b);
    }
}

/* Exact expectation of E_r over random nonzero classes of the small primes A, estimated by sampling m pairs of
   targets in a common class of r (uniform over all such pairs): E_exact = N_r * mean over pairs of prod_{a in A} p_a,
   p_a = 1 - 1/(a-1) if a divides q1 - q2 or a is q1 or q2, else 1 - 2/(a-1) (zero for a = 3).                   */
void exact_pairs(const uint32_t *T, int64_t nT, const uint32_t *B, int64_t nB, const uint32_t *A, int64_t nA, int m, uint64_t seed, double *Nr, double *Pbar, int threads) {
    uint32_t mx = maxof(B, nB);
    #pragma omp parallel num_threads(threads)
    {
        uint32_t *cnt = calloc(mx + 2, sizeof(uint32_t)); int64_t *off = malloc((mx + 2) * sizeof(int64_t));
        uint32_t *mem = malloc(nT * sizeof(uint32_t)); double *cum = malloc((mx + 1) * sizeof(double));
        #pragma omp for schedule(dynamic, 8)
        for (int64_t i = 0; i < nB; i++) {
            uint32_t r = B[i]; uint64_t M = M_of(r), rng = seed ^ (0x51ED2701ULL * (uint64_t)(i + 1));
            for (int64_t j = 0; j < nT; j++) cnt[fmod32(T[j], M, r)]++;
            off[0] = 0; for (uint32_t c = 0; c < r; c++) off[c + 1] = off[c] + cnt[c];
            for (uint32_t c = 0; c < r; c++) cnt[c] = 0;
            for (int64_t j = 0; j < nT; j++) { uint32_t c = fmod32(T[j], M, r); mem[off[c] + cnt[c]++] = T[j]; }
            double tot = 0; for (uint32_t c = 0; c < r; c++) { double n = cnt[c]; tot += 0.5 * n * (n - 1); cum[c] = tot; }
            Nr[i] = tot; double acc = 0;
            if (tot > 0) for (int k = 0; k < m; k++) {
                double u = u01(&rng) * tot; uint32_t lo = 0, hi = r - 1;
                while (lo < hi) { uint32_t mid = (lo + hi) / 2; if (cum[mid] > u) hi = mid; else lo = mid + 1; }
                uint32_t n = cnt[lo]; uint64_t x1 = below(&rng, n), x2 = below(&rng, n - 1); if (x2 >= x1) x2++;
                uint32_t q1 = mem[off[lo] + x1], q2 = mem[off[lo] + x2], d = q1 > q2 ? q1 - q2 : q2 - q1;
                double lp = 0;
                for (int64_t t = 0; t < nA; t++) {
                    uint32_t a = A[t];
                    if (d % a == 0 || q1 == a || q2 == a) lp += log1p(-1.0 / (a - 1));
                    else { if (a == 3) { lp = -INFINITY; break; } lp += log1p(-2.0 / (a - 1)); }
                }
                acc += exp(lp);
            }
            Pbar[i] = tot > 0 ? acc / m : 0;
            for (uint32_t c = 0; c < r; c++) cnt[c] = 0;
        }
        free(cnt); free(off); free(mem); free(cum);
    }
}

/* Deletion: for each theta, mark every colliding pair of r (r in B) with probability theta / meanE[r]; a prime is good
   if it has exactly one marked pair and neither survivor of that pair lies in a marked pair of another prime.     */
void deletion(const uint32_t *S, int64_t nS, const uint32_t *B, int64_t nB, const double *meanE, const double *th, int nth, uint64_t seed, int64_t *good, int64_t *one, int64_t *marked, int threads) {
    uint32_t mx = maxof(B, nB);
    int64_t cap = 64 + 16 * nB;                                     /* per-theta storage: at most 16 marked pairs a prime */
    int32_t *pp = malloc((size_t)nth * cap * sizeof(int32_t)); int64_t *pa = malloc((size_t)nth * cap * sizeof(int64_t)), *pb = malloc((size_t)nth * cap * sizeof(int64_t));
    int64_t *npairs = calloc(nth, sizeof(int64_t));
    #pragma omp parallel num_threads(threads)
    {
        uint32_t *cnt = calloc(mx + 2, sizeof(uint32_t)); int64_t *off = malloc((mx + 2) * sizeof(int64_t));
        int64_t *mem = malloc(nS * sizeof(int64_t)); double *cum = malloc((mx + 1) * sizeof(double));
        #pragma omp for schedule(dynamic, 8)
        for (int64_t i = 0; i < nB; i++) {
            uint32_t r = B[i]; uint64_t M = M_of(r);
            for (int64_t j = 0; j < nS; j++) cnt[fmod32(S[j], M, r)]++;
            off[0] = 0; for (uint32_t c = 0; c < r; c++) off[c + 1] = off[c] + cnt[c];
            for (uint32_t c = 0; c < r; c++) cnt[c] = 0;
            for (int64_t j = 0; j < nS; j++) { uint32_t c = fmod32(S[j], M, r); mem[off[c] + cnt[c]++] = j; }
            double tot = 0; for (uint32_t c = 0; c < r; c++) { double n = cnt[c]; tot += 0.5 * n * (n - 1); cum[c] = tot; }
            for (int t = 0; t < nth; t++) {
                uint64_t rng = seed ^ (0xA24BAED4963EE407ULL * (uint64_t)(i + 1)) ^ (0x9FB21C651E98DF25ULL * (uint64_t)(t + 1));
                if (tot <= 0 || meanE[i] <= 0) continue;
                double rho = th[t] / meanE[i]; if (rho > 1) rho = 1;
                /* k ~ Binomial(tot, rho) by inversion (the mean is small) */
                double n = tot, q = 1 - rho, pk = exp(n * log1p(-rho)), u = u01(&rng), F = pk; int64_t k = 0;
                while (u > F && k < (int64_t)n) { pk *= (n - k) / (k + 1.0) * rho / q; k++; F += pk; if (pk < 1e-300 && F < u) break; }
                int64_t ka[16], kb[16]; int got = 0;
                for (int64_t s = 0; s < k && got < 16; s++) {
                    double v = u01(&rng) * tot; uint32_t lo = 0, hi = r - 1;
                    while (lo < hi) { uint32_t mid = (lo + hi) / 2; if (cum[mid] > v) hi = mid; else lo = mid + 1; }
                    uint32_t m = cnt[lo]; uint64_t x1 = below(&rng, m), x2 = below(&rng, m - 1); if (x2 >= x1) x2++;
                    int64_t a = mem[off[lo] + x1], b = mem[off[lo] + x2]; if (a > b) { int64_t z = a; a = b; b = z; }
                    int dup = 0; for (int g = 0; g < got; g++) if (ka[g] == a && kb[g] == b) dup = 1;
                    if (dup) { s--; continue; }
                    ka[got] = a; kb[got] = b; got++;
                }
                #pragma omp critical
                {
                    for (int g = 0; g < got; g++) { int64_t z = t * cap + npairs[t]++; pp[z] = (int32_t)(k == 1 ? i : -1 - i); pa[z] = ka[g]; pb[z] = kb[g]; }
                }
            }
            for (uint32_t c = 0; c < r; c++) cnt[c] = 0;
        }
        free(cnt); free(off); free(mem); free(cum);
    }
    int32_t *deg = malloc(nS * sizeof(int32_t));
    for (int t = 0; t < nth; t++) {
        memset(deg, 0, nS * sizeof(int32_t));
        int64_t base = t * cap, g = 0, o = 0;
        for (int64_t z = 0; z < npairs[t]; z++) { deg[pa[base + z]]++; deg[pb[base + z]]++; }
        for (int64_t z = 0; z < npairs[t]; z++) if (pp[base + z] >= 0) { o++; if (deg[pa[base + z]] == 1 && deg[pb[base + z]] == 1) g++; }
        good[t] = g; one[t] = o; marked[t] = npairs[t];
    }
    free(deg); free(pp); free(pa); free(pb); free(npairs);
}

/* Greedy: the primes of B in the given order each take the nonzero class with the most remaining survivors
   (ties: the smallest class).  struck[i] = survivors struck by B[i]; returns the number left.                 */
int64_t greedy(const uint32_t *S0, int64_t nS, const uint32_t *B, int64_t nB, int32_t *struck) {
    uint32_t mx = maxof(B, nB);
    uint32_t *S = malloc(nS * sizeof(uint32_t)); memcpy(S, S0, nS * sizeof(uint32_t));
    uint32_t *cnt = calloc(mx + 1, sizeof(uint32_t)); int64_t n = nS;
    for (int64_t i = 0; i < nB; i++) {
        uint32_t r = B[i]; uint64_t M = M_of(r);
        if (n == 0) { struck[i] = 0; continue; }
        for (int64_t j = 0; j < n; j++) cnt[fmod32(S[j], M, r)]++;
        uint32_t best = 1, bc = 0;
        for (uint32_t c = 1; c < r; c++) if (cnt[c] > bc) { bc = cnt[c]; best = c; }
        int64_t w = 0;
        for (int64_t j = 0; j < n; j++) { uint32_t c = fmod32(S[j], M, r); cnt[c] = 0; if (c != best) S[w++] = S[j]; }
        cnt[0] = 0; struck[i] = (int32_t)(n - w); n = w;
    }
    free(S); free(cnt);
    return n;
}
