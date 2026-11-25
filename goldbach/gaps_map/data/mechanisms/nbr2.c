// nbr2.c -- neighbour search seeded by NEAR-successes (members of the cover-first stream with j <= J prime rows).
// usage: ./nbr2 X Q kmax J H topm     (topm=0: all shifts |h|<=H; else the topm shifts with the most inherited rows)
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { uint64_t w[3]; } mask_t;
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); int kmax = atoi(argv[3]); int J = atoi(argv[4]); int H = atoi(argv[5]); int topm = atoi(argv[6]);
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    size_t nb = (X >> 1) + 1; uint64_t *bm = malloc((nb / 64 + 1) * 8); memset(bm, 0xff, (nb / 64 + 1) * 8); bm[0] &= ~1ULL;
    for (int i = 1; i < np && (long)pr[i] * pr[i] <= X; i++) { long p = pr[i]; for (long x = p * p; x <= X; x += 2 * p) bm[(x >> 1) >> 6] &= ~(1ULL << ((x >> 1) & 63)); }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    char isr[40000]; memset(isr, 0, sizeof(isr)); for (int j = 0; j < nrows; j++) isr[rows[j]] = 1;
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 23; i++) sp[ns++] = pr[i];
    int small[9] = {3, 5, 7, 11, 13, 17, 19, 23, 29};
    mask_t *mk[16]; for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    // shifts
    int nsh = 0; int *shifts = malloc(sizeof(int) * 2 * H); int *score = calloc(H + 2, sizeof(int));
    for (int h = 2; h <= H; h += 2) { int cnt = 0; for (int j = 0; j < nrows; j++) if (rows[j] + h < Q && isr[rows[j] + h]) cnt++; score[h] = cnt; }
    int chosen[4000]; int nch = 0;
    if (topm > 0) { for (int t = 0; t < topm; t++) { int best = -1, bh = 0; for (int h = 2; h <= H; h += 2) if (score[h] > best) { int used = 0; for (int u = 0; u < nch; u++) if (chosen[u] == h) used = 1; if (!used) { best = score[h]; bh = h; } } chosen[nch++] = bh; } }
    else { for (int h = 2; h <= H; h += 2) chosen[nch++] = h; }
    for (int u = 0; u < nch; u++) { shifts[nsh++] = chosen[u]; shifts[nsh++] = -chosen[u]; }
    long Nlo = (Q + 200 + 1) & ~1L, total = (X - Nlo) / 2 + 1;
    int nth = omp_get_max_threads(); long (*acc)[8][8] = calloc(nth, sizeof(long[8][8])); // per thread: [j][stat]: 0 seeds,1 scans,2 succ outside stream,3 succ inside stream
    long *nstream = calloc(nth, sizeof(long)), *sstream = calloc(nth, sizeof(long));
    #pragma omp parallel
    {
        int t = omp_get_thread_num();
        #pragma omp for schedule(dynamic, 1000000)
        for (long u = 0; u < total; u++) {
            long N = Nlo + 2 * u; int ok = 1; for (int i = 0; i < 9; i++) if (N % small[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m = {{0, 0, 0}}; for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; m.w[0] |= e->w[0]; m.w[1] |= e->w[1]; m.w[2] |= e->w[2]; }
            int k1 = nrows - (__builtin_popcountll(m.w[0]) + __builtin_popcountll(m.w[1]) + __builtin_popcountll(m.w[2])); if (k1 > kmax) continue;
            nstream[t]++; int jp = 0; for (int j = 0; j < nrows && jp <= J; j++) { long v = N - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) jp++; }
            if (jp == 0) sstream[t]++;
            if (jp > J) continue; acc[t][jp][0]++;
            for (int si = 0; si < nsh; si++) { long N2 = N + shifts[si]; if (N2 < Nlo || N2 >= X) continue; int ok2 = 1; for (int i = 0; i < 9; i++) if (N2 % small[i] == 0) { ok2 = 0; break; } if (!ok2) continue;
                acc[t][jp][1]++; int pf = 0; for (int j = 0; j < nrows; j++) { long v = N2 - rows[j]; if ((bm[(v >> 1) >> 6] >> ((v >> 1) & 63)) & 1) { pf = 1; break; } }
                if (pf) continue; mask_t m2 = {{0, 0, 0}}; for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N2 % sp[i]]; m2.w[0] |= e->w[0]; m2.w[1] |= e->w[1]; m2.w[2] |= e->w[2]; }
                int k12 = nrows - (__builtin_popcountll(m2.w[0]) + __builtin_popcountll(m2.w[1]) + __builtin_popcountll(m2.w[2])); if (k12 > kmax) acc[t][jp][2]++; else acc[t][jp][3]++; }
        }
    }
    long ns_ = 0, ss_ = 0; for (int t = 0; t < nth; t++) { ns_ += nstream[t]; ss_ += sstream[t]; }
    printf("stream(k1<=%d): members %ld successes %ld ; shifts per seed %d\n", kmax, ns_, ss_, nsh);
    for (int j = 0; j <= J; j++) { long a[4] = {0, 0, 0, 0}; for (int t = 0; t < nth; t++) for (int q = 0; q < 4; q++) a[q] += acc[t][j][q];
        printf(" j=%d seeds %ld scans %ld succ_outside_stream %ld succ_inside_stream %ld\n", j, a[0], a[1], a[2], a[3]); }
    return 0;
}
