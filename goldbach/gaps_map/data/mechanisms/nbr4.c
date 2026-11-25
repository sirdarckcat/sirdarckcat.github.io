// nbr3.c -- neighbour search seeded by near-successes, with per-seed "clean shift" selection.
// For a stream member N (cover-first prefix k1<=kmax) with j<=J prime rows Pr(N):
//   shift s (even, |s|<=H) is used iff inh[s] >= cmin (many rows of N+s coincide with rows of N: q' prime and q'-s prime in [3,Q))
//   and clean: no prime row q0 of N lands on a prime row of N+s (q0+s prime, 3<=q0+s<Q).
// usage: ./nbr3 X Q kmax J cmin H
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { uint64_t w[3]; } mask_t;
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); int kmax = atoi(argv[3]); int J = atoi(argv[4]); int cmin = atoi(argv[5]); int H = atoi(argv[6]);
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8); bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i]; for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    char *isr = calloc(Q + 2 * H + 10, 1); for (int j = 0; j < nrows; j++) isr[rows[j]] = 1;
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 23; i++) sp[ns++] = pr[i];
    int small[9] = {3, 5, 7, 11, 13, 17, 19, 23, 29};
    mask_t *mk[16]; for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int nsh = 0; int shifts[4000]; int inhs[4000];
    for (int s = -H; s <= H; s += 2) { if (s == 0) continue; int cnt = 0; for (int j = 0; j < nrows; j++) { int q = rows[j] - s; if (q >= 3 && q < Q && isr[q]) cnt++; } if (cnt >= cmin) { shifts[nsh] = s; inhs[nsh] = cnt; nsh++; } }
    long Nlo = (Q + 200 + 1) & ~1L, total = (X - Nlo) / 2 + 1; uint64_t *scn = calloc((X >> 7) + 2, 8);
    int nth = omp_get_max_threads(); long (*acc)[16][4] = calloc(nth, sizeof(long[16][4])); long *nstream = calloc(nth, sizeof(long)), *sstream = calloc(nth, sizeof(long));
    #pragma omp parallel
    {
        int t = omp_get_thread_num();
        #pragma omp for schedule(dynamic, 1000000)
        for (long u = 0; u < total; u++) {
            long N = Nlo + 2 * u; int ok = 1; for (int i = 0; i < 9; i++) if (N % small[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m = {{0, 0, 0}}; for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; m.w[0] |= e->w[0]; m.w[1] |= e->w[1]; m.w[2] |= e->w[2]; }
            int k1 = nrows - (__builtin_popcountll(m.w[0]) + __builtin_popcountll(m.w[1]) + __builtin_popcountll(m.w[2])); if (k1 > kmax) continue;
            nstream[t]++; int Pr[16], jp = 0; for (int j = 0; j < nrows && jp <= J; j++) { long v = N - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) Pr[jp++] = rows[j]; }
            if (jp == 0) sstream[t]++; if (jp > J) continue; acc[t][jp][0]++;
            for (int si = 0; si < nsh; si++) { int s = shifts[si]; int clean = 1; for (int a = 0; a < jp; a++) { int q = Pr[a] + s; if (q >= 3 && q < Q && isr[q]) { clean = 0; break; } } if (!clean) continue;
                long N2 = N + s; if (N2 < Nlo || N2 >= X) continue; int ok2 = 1; for (int i = 0; i < 9; i++) if (N2 % small[i] == 0) { ok2 = 0; break; } if (!ok2) continue;
                mask_t m2 = {{0, 0, 0}}; for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N2 % sp[i]]; m2.w[0] |= e->w[0]; m2.w[1] |= e->w[1]; m2.w[2] |= e->w[2]; }
                int k12 = nrows - (__builtin_popcountll(m2.w[0]) + __builtin_popcountll(m2.w[1]) + __builtin_popcountll(m2.w[2])); if (k12 <= kmax) continue;   // inside the stream: scored anyway
                long ix = N2 >> 1; uint64_t bit = 1ULL << (ix & 63); uint64_t was = __atomic_fetch_or(&scn[ix >> 6], bit, __ATOMIC_RELAXED); if (was & bit) continue;      // already scored from another seed
                acc[t][jp][1]++; int pf = 0; for (int j = 0; j < nrows; j++) { long v = N2 - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) { pf = 1; break; } }
                if (!pf) { acc[t][jp][2]++; 

 } }
        }
    }
    long ns_ = 0, ss_ = 0; for (int t = 0; t < nth; t++) { ns_ += nstream[t]; ss_ += sstream[t]; }
    printf("stream(k1<=%d): members %ld successes %ld ; shifts available %d (inherit>=%d)\n", kmax, ns_, ss_, nsh, cmin);
    for (int j = 0; j <= J; j++) { long a[4] = {0, 0, 0, 0}; for (int t = 0; t < nth; t++) for (int q = 0; q < 4; q++) a[q] += acc[t][j][q];
        printf(" j=%d seeds %ld scans %ld succ_outside_stream %ld succ_inside_stream %ld\n", j, a[0], a[1], a[2], a[3]); }
    return 0;
}
