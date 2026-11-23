// count the numbers n <= X with no prime factor <= z (n > 1), and the primes among them
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    long X = atol(argv[1]); int z = atoi(argv[2]);
    unsigned char *rough = malloc(X + 1), *comp = malloc(X + 1); memset(rough, 1, X + 1); memset(comp, 0, X + 1);
    for (long p = 2; p * p <= X; p++) if (!comp[p]) for (long x = p * p; x <= X; x += p) comp[x] = 1;
    for (long p = 2; p <= z; p++) if (!comp[p]) for (long x = p; x <= X; x += p) rough[x] = 0;
    long r = 0, pr = 0;
    for (long n = 2; n <= X; n++) if (rough[n]) { r++; if (!comp[n]) pr++; }
    printf("X = %ld, z = %d: %ld rough numbers in [2, X], %ld of them prime, ratio %.5f\n", X, z, r, pr, (double)pr / r);
    return 0;
}
