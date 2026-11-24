// topten.c -- evidence that no multiple of m in [lo, X) is ever among the ten largest least Goldbach summands.
// Scanning the even N upwards it cuts [lo, X) into pieces [A, B): on each piece every multiple of m has
// g(N) <= c, and ten even numbers below A (the ten largest so far when the piece starts) have g >= c.
// Output for gen_ranksieve.py; not trusted by the Lean proofs.
//
//   gcc -O2 -o topten topten.c && ./topten 33554432 6 1368 >> scan_2e25.txt
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    long X = atol(argv[1]), m = atol(argv[2]), lo = atol(argv[3]);
    char *c = calloc(X + 1, 1); c[0] = c[1] = 1;
    for (long i = 2; i * i <= X; i++) if (!c[i]) for (long j = i * i; j <= X; j += i) c[j] = 1;
    int nq = 0; int *qp = malloc(200000 * sizeof(int));
    for (long i = 3; i < 1000000 && i <= X; i++) if (!c[i]) qp[nq++] = (int)i;
    int tg[10] = {0}; long tn[10] = {0};            // the ten largest so far, decreasing in g
    int wg[10]; long wn[10]; int have = 0, wmin = 0, cmax = 0; long A = lo;
    for (long N = 6; N < X; N += 2) {
        int g = 0;
        for (int i = 0; i < nq; i++) { long r = N - qp[i]; if (r < 2) break; if (!c[r]) { g = qp[i]; break; } }
        if (!g) { fprintf(stderr, "no summand for %ld\n", N); return 1; }
        if (N >= lo && N % m == 0) {
            if (!have || g > wmin) {                  // new piece starts at N, with the ten largest below N
                if (have) { printf("piece %ld %ld %ld %d", m, A, N, cmax); for (int i = 0; i < 10; i++) printf(" %ld:%d", wn[i], wg[i]); printf("\n"); }
                memcpy(wg, tg, sizeof tg); memcpy(wn, tn, sizeof tn); wmin = wg[9]; have = 1; A = N; cmax = 0;
                if (tn[9] == 0 || g > wmin) { fprintf(stderr, "%ld (g = %d) is among the ten largest\n", N, g); return 1; }
            }
            if (g > cmax) cmax = g;
        }
        if (g > tg[9]) {                              // ties: the earlier number keeps its place
            int i = 9; while (i > 0 && tg[i - 1] < g) { tg[i] = tg[i - 1]; tn[i] = tn[i - 1]; i--; }
            tg[i] = g; tn[i] = N;
        }
    }
    printf("piece %ld %ld %ld %d", m, A, X, cmax); for (int i = 0; i < 10; i++) printf(" %ld:%d", wn[i], wg[i]); printf("\n");
    return 0;
}
