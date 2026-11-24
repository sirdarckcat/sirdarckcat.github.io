// classmax.c -- for the even N in [6, X): the record holders of the least Goldbach summand g(N), and the largest
// g(N) among the multiples of each modulus given on the command line.  Input for gen_ranksieve.py; nothing here is
// trusted by the Lean proofs (the kernel checks every statement again).
//
//   gcc -O2 -o classmax classmax.c && ./classmax 33554432 6 10 14 30 42 70 210 > scan_2e25.txt
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    long X = atol(argv[1]); int nm = argc - 2; long m[64]; int mx[64] = {0}; long arg[64] = {0};
    for (int i = 0; i < nm; i++) m[i] = atol(argv[i + 2]);
    char *c = calloc(X + 1, 1); c[0] = c[1] = 1;
    for (long i = 2; i * i <= X; i++) if (!c[i]) for (long j = i * i; j <= X; j += i) c[j] = 1;
    int nq = 0; int *qp = malloc(200000 * sizeof(int));
    for (long i = 3; i < 1000000 && i <= X; i++) if (!c[i]) qp[nq++] = (int)i;
    int rec = 0;
    printf("# X = %ld\n", X);
    for (long N = 6; N < X; N += 2) {
        int g = 0;
        for (int i = 0; i < nq; i++) { long r = N - qp[i]; if (r < 2) break; if (!c[r]) { g = qp[i]; break; } }
        if (!g) { fprintf(stderr, "no summand for %ld\n", N); return 1; }
        if (g > rec) { rec = g; printf("record %ld %d\n", N, g); }
        for (int i = 0; i < nm; i++) if (N % m[i] == 0 && g > mx[i]) { mx[i] = g; arg[i] = N; }
    }
    for (int i = 0; i < nm; i++) printf("class %ld %d %ld\n", m[i], mx[i], arg[i]);
    return 0;
}
