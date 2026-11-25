// Three of the four families for problem P' on the miniature (X = 1e9, Q = 1000), as algorithms that put forward
// candidates N < X from class lists modulo primes beyond the Chinese-remainder line.  All three work on the same
// object: for a set T of primes beyond the line and for every s in T a list L_s of classes (the classes that strike
// the most rows, best first), the even N < X with N mod s in L_s for every s in T.
//
//   mitm    meet in the middle on the Chinese-remainder form: N = x + y mod P, P = 2 prod T, x from the lists of half
//           of T, y from the other half; y sorted, for every x the y with (x + y) mod P < X found by binary search.
//   ktree   Wagner's tree with four lists: pairs (x1, x2) with (x1 + x2) mod P in a window [c, c + A), pairs (x3, x4)
//           with (x3 + x4) mod P in [-c - A, -c + X), then the two pair lists joined on the final interval; one
//           window finds the share A/P of the solutions, and successive windows find them all.
//   prefix  N = N1 + k M0 with sorted lists: N1 runs over a file of residues modulo M0 = 2 3 5 ... 23 (the best covers,
//           i.e. the cover-first prefix), sorted by N1 mod P, P = prod T; for every k < X / M0 and every tuple of listed
//           classes the matching N1 are read off by binary search.
//   bucket  many small tables: for each table a random subset of t primes beyond the line; the bucket of an N is its
//           residue vector on the subset; the buckets whose key is a tuple of listed classes are read out (they are
//           arithmetic progressions) and the union over the tables is put forward.
//
// Output: the candidates as uint32 (binary), and on stdout the operation counts.  Units: one "op" is one modular
// reduction or multiplication, one comparison of a sort or binary search, or one candidate written.
//
//   gcc -O3 -march=native -o families families.c
//   ./families mitm   OUT LSPEC s1 s2 ...          LSPEC: 1, 2, 3 (that many classes), f3, f2 (floor(s/3), floor(s/2))
//   ./families ktree  OUT LSPEC WINDOWS s1 s2 ...  WINDOWS: number of windows to run (0 = all)
//   ./families prefix OUT LSPEC FILE s1 s2 ...     FILE: residues modulo M0 as uint32
//   ./families bucket OUT LSPEC t TABLES SEED POOL (POOL: the subsets are drawn from the POOL smallest primes beyond the line)
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef uint64_t u64;
#define X_BOUND 1000000000ULL
static int rows[200], nrows, deep[64], ndeep;
static int rankcls[200][200];           // rankcls[s][i] = the i-th best class of s
static u64 ops_arith, ops_cmp, ops_out;
static FILE *fout;
static void setup(void) {
    char c[1000] = {0}; int pr[200], np = 0;
    for (int i = 2; i < 1000; i++) { if (!c[i]) { pr[np++] = i; for (int j = i * i; j < 1000; j += i) c[j] = 1; } }
    for (int i = 1; i < np; i++) rows[nrows++] = pr[i];
    for (int i = 0; i < np; i++) if (pr[i] >= 29 && pr[i] <= 199) deep[ndeep++] = pr[i];
    for (int i = 0; i < ndeep; i++) { int s = deep[i], w[200] = {0}, used[200] = {0};
        for (int j = 0; j < nrows; j++) w[rows[j] % s]++;
        for (int k = 0; k < s; k++) { int best = -1; for (int a = 0; a < s; a++) if (!used[a] && (best < 0 || w[a] > w[best])) best = a; used[best] = 1; rankcls[s][k] = best; } }
}
static int listsize(const char *spec, int s) { if (spec[0] == 'f') return s / atoi(spec + 1); return atoi(spec); }
static u64 inv_mod(u64 a, u64 m) { long long t = 0, nt = 1, r = m, nr = a % m; while (nr) { long long q = r / nr, x = t - q * nt; t = nt; nt = x; x = r - q * nr; r = nr; nr = x; } return (u64)((t % (long long)m + m) % m); }
static int cmp128(const void *a, const void *b) { u128 x = *(const u128 *)a, y = *(const u128 *)b; ops_cmp++; return x < y ? -1 : x > y; }
// all sums of one listed class per prime of the group, as residues mod P
static u128 *group_values(const int *T, int nT, const char *spec, u128 P, long *count) {
    long n = 1; for (int i = 0; i < nT; i++) n *= listsize(spec, T[i]);
    u128 *v = malloc((n ? n : 1) * sizeof(u128)); long m = 1; v[0] = 0;
    for (int i = 0; i < nT; i++) { int s = T[i], l = listsize(spec, s); u128 Ps = P / s; u64 inv = inv_mod((u64)(Ps % s), s);
        u128 E = Ps * inv % P;                          // E = 1 mod s, 0 mod P/s
        for (long j = m - 1; j >= 0; j--) for (int k = l - 1; k >= 0; k--) { v[j * l + k] = (v[j] + (u128)rankcls[s][k] * E) % P; ops_arith++; }
        m *= l; }
    *count = n; return v;
}
static long lower_bound(const u128 *a, long n, u128 x) { long lo = 0, hi = n; while (lo < hi) { long mid = (lo + hi) / 2; ops_cmp++; if (a[mid] < x) lo = mid + 1; else hi = mid; } return lo; }
// for every x in A: every y in sorted B with (x + y - lo) mod P < width; calls emit((x + y) mod P)
typedef void (*emit_t)(u128);
static void join_interval(const u128 *A, long nA, const u128 *B, long nB, u128 P, u128 lo, u128 width, emit_t emit) {
    for (long i = 0; i < nA; i++) { u128 start = (lo + P - A[i] % P) % P;          // y in [start, start + width) mod P
        u128 end = start + width; ops_arith++;
        if (end <= P) { for (long j = lower_bound(B, nB, start); j < nB && B[j] < end; j++) emit((A[i] + B[j]) % P); }
        else { for (long j = lower_bound(B, nB, start); j < nB; j++) emit((A[i] + B[j]) % P);
               u128 e2 = end - P; for (long j = 0; j < nB && B[j] < e2; j++) emit((A[i] + B[j]) % P); } }
}
static void emit_out(u128 n) { uint32_t v = (uint32_t)n; fwrite(&v, 4, 1, fout); ops_out++; }
static u128 *acc; static long nacc, cap;
static void emit_acc(u128 n) { if (nacc == cap) { cap = cap ? 2 * cap : 1024; acc = realloc(acc, cap * sizeof(u128)); } acc[nacc++] = n; ops_out++; }

// the even N < X in the product of the lists of the primes T: progressions when P = 2 prod T <= X, otherwise the
// meet in the middle (two halves of T, one sorted, binary search for the sums that fall below X).  Returns 1 if joined.
static int product_set(const int *T, int nT, const char *spec, long *vectors, long *memory) {
    u128 P = 2; long double listprod = 1;
    for (int i = 0; i < nT; i++) { P *= T[i]; listprod *= listsize(spec, T[i]); }
    if (P <= X_BOUND) {
        long n; u128 *v = group_values(T, nT, spec, P, &n);
        for (long i = 0; i < n; i++) for (u128 N = v[i]; N < X_BOUND; N += P) emit_out(N);
        free(v); *vectors = n; *memory = n; return 0; }
    int A[64], B[64], nA = 0, nB = 0; long pa = 1, pb = 1;        // split to balance the two list products
    for (int i = nT - 1; i >= 0; i--) { int l = listsize(spec, T[i]); if (pa <= pb) { A[nA++] = T[i]; pa *= l; } else { B[nB++] = T[i]; pb *= l; } }
    long na, nb; u128 *va = group_values(A, nA, spec, P, &na), *vb = group_values(B, nB, spec, P, &nb);
    qsort(vb, nb, sizeof(u128), cmp128);
    join_interval(va, na, vb, nb, P, 0, X_BOUND, emit_out);
    free(va); free(vb); *vectors = (long)listprod; *memory = na + nb; return 1;
}

int main(int argc, char **argv) {
    setup(); const char *mode = argv[1]; fout = fopen(argv[2], "wb"); const char *spec = argv[3];
    if (!strcmp(mode, "mitm")) {
        int T[64], nT = argc - 4; for (int i = 0; i < nT; i++) T[i] = atoi(argv[4 + i]);
        long vectors, mem; int joined = product_set(T, nT, spec, &vectors, &mem);
        printf("mitm%s lists=%s primes=%d residue_vectors=%ld ops_arith=%llu ops_cmp=%llu outputs=%llu memory=%ld\n", joined ? "" : " (progressions, P <= X)", spec, nT, vectors,
               (unsigned long long)ops_arith, (unsigned long long)ops_cmp, (unsigned long long)ops_out, mem);
    } else if (!strcmp(mode, "ktree")) {
        long windows = atol(argv[4]); int T[64], nT = argc - 5; u128 P = 2;
        for (int i = 0; i < nT; i++) { T[i] = atoi(argv[5 + i]); P *= T[i]; }
        int G[4][64], nG[4] = {0, 0, 0, 0}; long pg[4] = {1, 1, 1, 1};
        for (int i = nT - 1; i >= 0; i--) { int g = 0; for (int k = 1; k < 4; k++) if (pg[k] < pg[g]) g = k; G[g][nG[g]++] = T[i]; pg[g] *= listsize(spec, T[i]); }
        long n[4]; u128 *v[4]; for (int g = 0; g < 4; g++) v[g] = group_values(G[g], nG[g], spec, P, &n[g]);
        qsort(v[1], n[1], sizeof(u128), cmp128); qsort(v[3], n[3], sizeof(u128), cmp128);
        long mmax = 1; for (int g = 0; g < 4; g++) if (n[g] > mmax) mmax = n[g];
        // window width A: the pair list (x1, x2) has about mmax entries
        u128 A = (u128)((long double)P * (long double)mmax / ((long double)n[0] * (long double)n[1]));
        if (A < 1) A = 1; if (A > P) A = P;
        u128 nwin = (P + A - 1) / A; if (windows <= 0 || (u128)windows > nwin) windows = (long)nwin;
        u64 pairs12 = 0, pairs34 = 0; long peak = 0;
        for (long r = 0; r < windows; r++) { u128 c = (u128)r * A; u128 wA = (c + A <= P) ? A : P - c;
            nacc = 0; join_interval(v[0], n[0], v[1], n[1], P, c, wA, emit_acc); long n12 = nacc; u128 *L12 = malloc((n12 ? n12 : 1) * sizeof(u128)); memcpy(L12, acc, n12 * sizeof(u128));
            // (x3 + x4) mod P in [P - c - wA, P - c + X): the sums z12 + z34 that can land in [0, X)
            u128 lo = (2 * P - c - wA) % P, width = wA + X_BOUND; if (width > P) width = P;
            nacc = 0; join_interval(v[2], n[2], v[3], n[3], P, lo, width, emit_acc); long n34 = nacc;
            ops_out -= (u64)(n12 + n34); pairs12 += n12; pairs34 += n34; if (n12 + n34 > peak) peak = n12 + n34;
            qsort(acc, n34, sizeof(u128), cmp128);
            join_interval(L12, n12, acc, n34, P, 0, X_BOUND, emit_out); free(L12); }
        printf("ktree lists=%s primes=%d lists_sizes=%ld,%ld,%ld,%ld windows_run=%ld of %llu pairs12=%llu pairs34=%llu ops_arith=%llu ops_cmp=%llu outputs=%llu memory=%ld\n",
               spec, nT, n[0], n[1], n[2], n[3], windows, (unsigned long long)nwin, (unsigned long long)pairs12, (unsigned long long)pairs34,
               (unsigned long long)(ops_arith + pairs12 + pairs34), (unsigned long long)ops_cmp, (unsigned long long)ops_out, n[0] + n[1] + n[2] + n[3] + peak);
    } else if (!strcmp(mode, "prefix")) {
        const u64 M0 = 223092870ULL; int T[64], nT = argc - 5; u128 P = 1;
        for (int i = 0; i < nT; i++) { T[i] = atoi(argv[5 + i]); P *= T[i]; }
        FILE *f = fopen(argv[4], "rb"); fseek(f, 0, SEEK_END); long R = ftell(f) / 4; fseek(f, 0, SEEK_SET);
        uint32_t *r = malloc((R ? R : 1) * 4); if (fread(r, 4, R, f) != (size_t)R) return 1; fclose(f);
        long n; u128 *v = group_values(T, nT, spec, P, &n);
        if (P <= (1ULL << 27)) {                         // table indexed by N1 mod P (counting sort): start[key] .. start[key + 1]
            u64 Pm = (u64)P; uint32_t *start = calloc(Pm + 2, 4), *sorted = malloc((R ? R : 1) * 4);
            for (long i = 0; i < R; i++) { start[r[i] % Pm + 2]++; ops_arith++; }
            for (u64 k = 2; k < Pm + 2; k++) start[k] += start[k - 1];
            ops_arith += Pm;
            for (long i = 0; i < R; i++) { sorted[start[r[i] % Pm + 1]++] = r[i]; ops_arith++; }
            for (u64 k = 0; k * M0 < X_BOUND; k++) { u64 shift = (u64)((u128)k * M0 % P);
                for (long i = 0; i < n; i++) { u64 target = (u64)((v[i] + P - shift) % P); ops_arith++;
                    for (uint32_t j = start[target]; j < start[target + 1]; j++) { u64 N = (u64)sorted[j] + k * M0; if (N < X_BOUND) emit_out(N); } } }
            printf("prefix (table) lists=%s primes=%d residues=%ld residue_vectors=%ld ops_arith=%llu ops_cmp=%llu outputs=%llu memory=%llu\n", spec, nT, R, n,
                   (unsigned long long)ops_arith, (unsigned long long)ops_cmp, (unsigned long long)ops_out, (unsigned long long)(R + Pm + n));
        } else {                                         // sorted list of (N1 mod P, N1), binary search
            u128 *e = malloc((R ? R : 1) * sizeof(u128));
            for (long i = 0; i < R; i++) { e[i] = ((u128)(r[i] % (u64)P) << 32) | r[i]; ops_arith++; }
            qsort(e, R, sizeof(u128), cmp128);
            for (u64 k = 0; k * M0 < X_BOUND; k++) { u64 shift = (u64)((u128)k * M0 % P);
                for (long i = 0; i < n; i++) { u128 target = ((v[i] + P - shift) % P) << 32; ops_arith++;
                    for (long j = lower_bound(e, R, target); j < R && (e[j] >> 32) == (target >> 32); j++) { u64 N = (u64)(uint32_t)e[j] + k * M0; if (N < X_BOUND) emit_out(N); } } }
            printf("prefix (sorted) lists=%s primes=%d residues=%ld residue_vectors=%ld ops_arith=%llu ops_cmp=%llu outputs=%llu memory=%ld\n", spec, nT, R, n,
                   (unsigned long long)ops_arith, (unsigned long long)ops_cmp, (unsigned long long)ops_out, R + n);
        }
    } else if (!strcmp(mode, "bucket")) {
        int t = atoi(argv[4]); long tables = atol(argv[5]); u64 seed = strtoull(argv[6], 0, 10); int pool = atoi(argv[7]); long double vectors = 0; long peak = 0;
        for (long tb = 0; tb < tables; tb++) { int T[16], used[64] = {0};
            for (int i = 0; i < t; ) { seed = seed * 6364136223846793005ULL + 1442695040888963407ULL; int j = (int)((seed >> 33) % pool); if (!used[j]) { used[j] = 1; T[i++] = deep[j]; } }
            for (int i = 0; i < t; i++) for (int j = i + 1; j < t; j++) if (T[j] < T[i]) { int x = T[i]; T[i] = T[j]; T[j] = x; }
            long v, mem; product_set(T, t, spec, &v, &mem); vectors += v; if (mem > peak) peak = mem; }
        printf("bucket lists=%s subset=%d tables=%ld pool=%d residue_vectors=%.0Lf ops_arith=%llu ops_cmp=%llu outputs=%llu memory=%ld\n", spec, t, tables, pool,
               vectors, (unsigned long long)ops_arith, (unsigned long long)ops_cmp, (unsigned long long)ops_out, peak);
    }
    fclose(fout); return 0;
}
