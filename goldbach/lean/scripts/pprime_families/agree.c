// What exists, for the lattice decoders: over every even N < X = 1e9 (and over the members alone), the agreement of N
// with the class lists of the 37 primes 29..199.  Lists: the best class of each prime, the best 2, the best 3, the
// best third (classes ranked by the rows they strike).  For each list size: the largest number of agreeing primes, the
// largest agreement amplitude (sum of ln s over the agreeing primes), and the histogram of the number of agreements.
// Also the largest incidence sum (rows struck by the classes of N, counted with multiplicity).
//   gcc -O3 -march=native -o agree agree.c -lm && ./agree
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define X_BOUND 1000000000L
int main(void) {
    char c[1000] = {0}; int pr[200], np = 0; for (int i = 2; i < 1000; i++) { if (!c[i]) { pr[np++] = i; for (int j = i * i; j < 1000; j += i) c[j] = 1; } }
    int rows[200], nrows = 0; for (int i = 1; i < np; i++) rows[nrows++] = pr[i];
    int deep[64], nd = 0; for (int i = 0; i < np; i++) if (pr[i] >= 29 && pr[i] <= 199) deep[nd++] = pr[i];
    static uint8_t rank[64][200], wt[64][200]; double lg[64];
    for (int i = 0; i < nd; i++) { int s = deep[i], w[200] = {0}, used[200] = {0}; lg[i] = log((double)s);
        for (int j = 0; j < nrows; j++) w[rows[j] % s]++;
        for (int a = 0; a < s; a++) wt[i][a] = w[a];
        for (int k = 0; k < s; k++) { int best = -1; for (int a = 0; a < s; a++) if (!used[a] && (best < 0 || w[a] > w[best])) best = a; used[best] = 1; rank[i][best] = k; } }
    int small[] = {3, 5, 7, 11, 13, 17, 19, 23, 29}, rs[9], r[64];
    // four list sizes x {all even N, members}
    static long hist[4][2][40]; int maxc[4][2] = {{0}}; double maxa[4][2] = {{0}}; long argc_[4][2] = {{0}}, arga[4][2] = {{0}}; int maxinc[2] = {0, 0}; long arginc[2] = {0, 0};
    for (int i = 0; i < nd; i++) r[i] = 0;
    for (int i = 0; i < 9; i++) rs[i] = 0;
    for (long N = 0; N < X_BOUND; N += 2) {
        int cnt[4] = {0, 0, 0, 0}, inc = 0; double amp[4] = {0, 0, 0, 0};
        for (int i = 0; i < nd; i++) { int k = rank[i][r[i]]; inc += wt[i][r[i]];
            if (k < 1) { cnt[0]++; amp[0] += lg[i]; } if (k < 2) { cnt[1]++; amp[1] += lg[i]; } if (k < 3) { cnt[2]++; amp[2] += lg[i]; } if (k < deep[i] / 3) { cnt[3]++; amp[3] += lg[i]; } }
        int member = N >= 1202; for (int i = 0; i < 9; i++) if (rs[i] == 0) member = 0;
        for (int m = 0; m <= member; m++) {
            for (int l = 0; l < 4; l++) { hist[l][m][cnt[l]]++; if (cnt[l] > maxc[l][m]) { maxc[l][m] = cnt[l]; argc_[l][m] = N; } if (amp[l] > maxa[l][m]) { maxa[l][m] = amp[l]; arga[l][m] = N; } }
            if (inc > maxinc[m]) { maxinc[m] = inc; arginc[m] = N; } }
        for (int i = 0; i < nd; i++) { r[i] += 2; if (r[i] >= deep[i]) r[i] -= deep[i]; }
        for (int i = 0; i < 9; i++) { rs[i] += 2; if (rs[i] >= small[i]) rs[i] -= small[i]; }
    }
    const char *nm[4] = {"best class", "best 2 classes", "best 3 classes", "best third of the classes"}, *pop[2] = {"all even N < 1e9", "members"};
    for (int l = 0; l < 4; l++) for (int m = 0; m < 2; m++) {
        printf("%s | %s | most agreeing primes %d (N = %ld) | largest amplitude %.2f nats (N = %ld) | histogram of the number of agreeing primes:", nm[l], pop[m], maxc[l][m], argc_[l][m], maxa[l][m], arga[l][m]);
        for (int k = 0; k < 40; k++) if (hist[l][m][k]) printf(" %d:%ld", k, hist[l][m][k]);
        printf("\n"); }
    for (int m = 0; m < 2; m++) printf("largest incidence sum with the primes 29..199 | %s | %d (N = %ld)\n", pop[m], maxinc[m], arginc[m]);
    return 0;
}
