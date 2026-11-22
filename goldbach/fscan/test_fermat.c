/* test_fermat.c -- fermat52.h from the command line.   gcc -O3 -march=native -o test_fermat test_fermat.c
 *   ./test_fermat < hexlines      one line of 0/1 per batch of up to 24 numbers (a blank line ends a batch)
 *   ./test_fermat --time bits     cycles per test
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <x86intrin.h>
#include "fermat52.h"
static uint64_t s = 88172645463325252ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static u128 hex(const char *p) { u128 v = 0; for (; *p; p++) { int c = *p; int d = c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : -1; if (d < 0) break; v = v * 16 + d; } return v; }
int main(int argc, char **argv) {
    if (argc > 2 && !strcmp(argv[1], "--time")) {
        int bits = atoi(argv[2]);
        u128 n[F52_LANES]; unsigned acc = 0;
        for (int i = 0; i < F52_LANES; i++) { u128 v = ((u128)rnd() << 64) | rnd(); v >>= 128 - bits; v |= (u128)1 << (bits - 1); v |= 1; n[i] = v; }
        int R = 300000;
        unsigned long long c0 = __rdtsc(); clock_t w0 = clock();
        for (int r = 0; r < R; r++) { n[r % F52_LANES] += 2; acc += f52_test(n, F52_LANES); }
        unsigned long long c1 = __rdtsc(); clock_t w1 = clock();
        printf("%d-bit numbers: %.1f TSC cycles per test, %.1f ns per test, setup included [%u]\n", bits,
               (double)(c1 - c0) / R / F52_LANES, (double)(w1 - w0) / CLOCKS_PER_SEC * 1e9 / R / F52_LANES, acc);
        return 0;
    }
    char line[256]; u128 n[F52_LANES]; int cnt = 0;
    while (1) {
        char *ok = fgets(line, sizeof line, stdin);
        int blank = !ok || line[0] == '\n';
        if (!blank) n[cnt++] = hex(line);
        if ((blank || cnt == F52_LANES) && cnt) {
            unsigned r = f52_test(n, cnt);
            for (int i = 0; i < cnt; i++) putchar('0' + ((r >> i) & 1));
            putchar('\n'); cnt = 0;
        }
        if (!ok) break;
    }
    return 0;
}
