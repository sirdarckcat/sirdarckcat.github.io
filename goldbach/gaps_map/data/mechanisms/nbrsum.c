// nbrsum.c -- Research's identity: expected success mass held by ALL neighbours N+s (usable shifts) per unit of stream mass.
// R = sum_N sum_s P(N+s) / sum_N P(N),  P = (1-rho)^{k199}.   usage: ./nbrsum X Q kmax cmin H rho
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define NW 3
typedef struct { uint64_t w[NW]; } mask_t;
static inline int pc(const mask_t *m) { int s = 0; for (int i = 0; i < NW; i++) s += __builtin_popcountll(m->w[i]); return s; }
int main(int argc, char **argv) {
    long X = atol(argv[1]); int Q = atoi(argv[2]); int kmax = atoi(argv[3]); int cmin = atoi(argv[4]); int H = atoi(argv[5]); double rho = atof(argv[6]);
    int lim = 40000; char *c = calloc(lim, 1); int np = 0, *pr = malloc(lim * sizeof(int));
    for (int i = 2; i < lim; i++) { if (!c[i]) { pr[np++] = i; for (long j = (long)i * i; j < lim; j += i) c[j] = 1; } }
    int rows[300], nrows = 0; for (int i = 1; i < np && pr[i] < Q; i++) rows[nrows++] = pr[i];
    char *isr = calloc(Q + 2 * H + 10, 1); for (int j = 0; j < nrows; j++) isr[rows[j]] = 1;
    int ns = 0, sp[64]; for (int i = 1; i < np && pr[i] <= 199; i++) sp[ns++] = pr[i];
    int nsh23 = 0; while (nsh23 < ns && sp[nsh23] <= 23) nsh23++;
    mask_t **mk = malloc(ns * sizeof(mask_t *)); for (int i = 0; i < ns; i++) { mk[i] = calloc(sp[i], sizeof(mask_t)); for (int j = 0; j < nrows; j++) mk[i][rows[j] % sp[i]].w[j >> 6] |= 1ULL << (j & 63); }
    int small[9] = {3, 5, 7, 11, 13, 17, 19, 23, 29};
    static int shifts[8000]; int nsh = 0;
    for (int s = -H; s <= H; s += 2) { if (s == 0) continue; int cnt = 0; for (int j = 0; j < nrows; j++) { int q = rows[j] - s; if (q >= 3 && q < Q && isr[q]) cnt++; } if (cnt >= cmin) shifts[nsh++] = s; }
    double pw[512]; for (int k = 0; k < 512; k++) pw[k] = pow(1.0 - rho, k);
    long Nlo = (Q + 200 + 1) & ~1L, total = (X - Nlo) / 2 + 1; int nth = omp_get_max_threads();
    double *sm = calloc(nth, sizeof(double)), *nm_all = calloc(nth, sizeof(double)), *nm_out = calloc(nth, sizeof(double)); long *nst = calloc(nth, sizeof(long)), *npairs = calloc(nth, sizeof(long));
    #pragma omp parallel
    {
        int t = omp_get_thread_num();
        #pragma omp for schedule(dynamic, 1000000)
        for (long u = 0; u < total; u++) {
            long N = Nlo + 2 * u; int ok = 1; for (int i = 0; i < 9; i++) if (N % small[i] == 0) { ok = 0; break; } if (!ok) continue;
            mask_t m; memset(&m, 0, sizeof(m)); int k1 = 0;
            for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N % sp[i]]; for (int w = 0; w < NW; w++) m.w[w] |= e->w[w]; if (i + 1 == nsh23) k1 = nrows - pc(&m); }
            if (k1 > kmax) continue; nst[t]++; sm[t] += pw[nrows - pc(&m)];
            for (int si = 0; si < nsh; si++) { long N2 = N + shifts[si]; if (N2 < Nlo || N2 >= X) continue; int ok2 = 1; for (int i = 0; i < 9; i++) if (N2 % small[i] == 0) { ok2 = 0; break; } if (!ok2) continue;
                mask_t m2; memset(&m2, 0, sizeof(m2)); int k12 = 0; for (int i = 0; i < ns; i++) { const mask_t *e = &mk[i][N2 % sp[i]]; for (int w = 0; w < NW; w++) m2.w[w] |= e->w[w]; if (i + 1 == nsh23) k12 = nrows - pc(&m2); }
                double mass = pw[nrows - pc(&m2)]; npairs[t]++; nm_all[t] += mass; if (k12 > kmax) nm_out[t] += mass; }
        }
    }
    double S = 0, A = 0, O = 0; long n = 0, np2 = 0; for (int t = 0; t < nth; t++) { S += sm[t]; A += nm_all[t]; O += nm_out[t]; n += nst[t]; np2 += npairs[t]; }
    printf("kmax=%d shifts=%d stream_members=%ld stream_mass=%.6g pairs=%ld nb_mass_all=%.6g nb_mass_outside_stream=%.6g  R_all=%.3f R_outside=%.3f\n", kmax, nsh, n, S, np2, A, O, A / S, O / S);
    return 0;
}
