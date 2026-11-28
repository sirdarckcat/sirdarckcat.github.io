// cover_rank.c -- how much of each term of A025018 can be seen from residues modulo small primes.
//
// Between two consecutive terms N_k < N_k+1 the generator looks for the first even N with no summand
// among the strikers (odd primes) up to g_k.  Here every even N of the interval gets a score that uses
// only the primes up to z:   score_z(N) = number of strikers q with N - q free of prime factors <= z
// (the strikers that the residues of N modulo the primes up to z do not rule out).  The next term has
// score_z = (its strikers whose N - q has only prime factors above z).  The program reports, for each
// term and each z, the score of the term, the mean score in the interval, and the share of the interval
// whose score is at most the term's: a search that tries candidates in order of score would stop there.
//
//   gcc -O2 -o cover_rank cover_rank.c -lm && ./cover_rank terms.txt 120000000 3 7 13 31 101 1009 > cover_rank.txt
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
int main(int argc, char **argv) {
    long X = atol(argv[2]); int nz = argc - 3; int zs[32]; for (int i = 0; i < nz; i++) zs[i] = atoi(argv[i + 3]);
    long tN[128]; int tg[128], nt = 0; char line[256];
    FILE *f = fopen(argv[1], "r"); if (!f) { perror(argv[1]); return 1; }
    while (fgets(line, sizeof line, f)) { if (line[0] == '#') continue; long a; int b; if (sscanf(line, "%ld %d", &a, &b) == 2 && a <= X) { tN[nt] = a; tg[nt] = b; nt++; } }
    fclose(f);
    char *comp = calloc(X + 1, 1); comp[0] = comp[1] = 1;
    for (long i = 2; i * i <= X; i++) if (!comp[i]) for (long j = i * i; j <= X; j += i) comp[j] = 1;
    int nq = 0; static int qp[4096]; for (int i = 3; i < 20000 && nq < 4096; i++) if (!comp[i]) qp[nq++] = i;
    char *rough = malloc(X + 1);
    printf("# terms from %s up to %ld; score_z(N) = strikers q <= g_k with N - q free of prime factors <= z\n", argv[1], X);
    double *lg = calloc(nz, sizeof(double)); int used = 0;
    for (int zi = 0; zi < nz; zi++) {
        int z = zs[zi];
        memset(rough, 1, X + 1); rough[0] = rough[1] = 0;
        for (long p = 2; p <= z; p++) if (!comp[p]) for (long j = p; j <= X; j += p) rough[j] = 0;
        printf("\n## z = %d\n#  term N_k+1 (value)   strikers   interval (even N)   score of the term   mean score   share with score <= the term's\n", z);
        used = 0;
        for (int k = 0; k + 1 < nt; k++) {
            if (tN[k] < 40000) continue;
            int m = 0; while (m < nq && qp[m] <= tg[k]) m++;
            long lo = tN[k] + 2, hi = tN[k + 1]; long cnt = 0, le = 0, lt = 0; double sum = 0; int sstar = 0;
            for (int i = 0; i < m; i++) sstar += rough[hi - qp[i]];
            for (long N = lo; N <= hi; N += 2) {
                int s = 0; for (int i = 0; i < m; i++) s += rough[N - qp[i]];
                cnt++; sum += s; if (s <= sstar) le++; if (s < sstar) lt++;
            }
            double share = (lt + 0.5 * (le - lt)) / cnt;
            printf("   %12ld (%4d)   %4d   %12ld   %4d   %7.1f   %.5f\n", hi, tg[k + 1], m, cnt, sstar, sum / cnt, share);
            lg[zi] += log(share); used++;
        }
        printf("#  geometric mean of the share over %d terms: %.5f  (a search in order of score examines 1 in %.0f)\n", used, exp(lg[zi] / used), exp(-lg[zi] / used));
    }
    return 0;
}
