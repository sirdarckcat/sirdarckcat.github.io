// brute force over ALL residue vectors (every class of every modulus, class 0 included) on the first n odd primes:
// the maximum of the least unstruck odd prime, and how many vectors attain it.  Independent of the desert_fast* code.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>
#define NPB 256
#define WB 4
static int pr[NPB], nm, md[16];
static uint64_t mk[16][64][WB];
static int least(const uint64_t *s) { for (int w = 0; w < WB; w++) if (~s[w]) return pr[w * 64 + __builtin_ctzll(~s[w])]; return 1 << 30; }
static void rec(int d, const uint64_t *s, int *bestv, long *cnt) {
    if (d == nm) { int q = least(s); if (q > *bestv) { *bestv = q; *cnt = 1; } else if (q == *bestv) (*cnt)++; return; }
    for (int c = 0; c < md[d]; c++) { uint64_t t[WB]; for (int w = 0; w < WB; w++) t[w] = s[w] | mk[d][c][w]; rec(d + 1, t, bestv, cnt); }
}
int main(int argc, char **argv) {
    nm = atoi(argv[1]);
    static char comp[4000]; int np = 0;
    for (int i = 2; i < 4000 && np < NPB; i++) if (!comp[i]) { if (i > 2) pr[np++] = i; for (int j = i * i; j < 4000; j += i) comp[j] = 1; }
    for (int m = 0; m < nm; m++) { md[m] = pr[m]; for (int i = 0; i < NPB; i++) mk[m][pr[i] % md[m]][i >> 6] |= 1ull << (i & 63); }
    int gb = 0; long gc = 0;
    #pragma omp parallel for schedule(dynamic, 1)
    for (int c0 = 0; c0 < md[0] * md[1]; c0++) {                      /* the first two moduli's classes split over threads */
        int a = c0 / md[1], b = c0 % md[1]; uint64_t s[WB]; for (int w = 0; w < WB; w++) s[w] = mk[0][a][w] | mk[1][b][w];
        int bv = 0; long ct = 0; rec(2, s, &bv, &ct);
        #pragma omp critical
        { if (bv > gb) { gb = bv; gc = ct; } else if (bv == gb) gc += ct; }
    }
    printf("brute n=%d D=%d optimal vectors=%ld\n", nm, gb, gc);
    return 0;
}
