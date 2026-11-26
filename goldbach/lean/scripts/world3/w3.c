// w3.c -- the Goldbach problem in F_q[t], exact enumeration over every monic polynomial of one degree.
//
// members : M monic of degree n over F_q (the number is N = lam*M, lam = 1/mu; mu = 1 is the monic problem)
// rows    : the monic irreducibles Q of degree 1, 2, ..., in order of degree and then of index
//           (index of a monic polynomial of degree d = sum of c_i q^i over i < d, c_i the label of the coefficient)
// a row succeeds for M when M - mu*Q is irreducible (that is, N - Q is irreducible)
// L(M)    : the number of rows before the first success
// depth   : a row is "left at depth z" when M - mu*Q has no irreducible factor among the first z irreducibles
//
// usage: w3 q n mu b OUT [cutoff ranks ... ] [-l line ...] [-t target ...] [-top K]
//   q in {3,5,7,9}; F_9 = F_3[i], i^2 = -1, label a + 3b for a + b i
//   b: rows of degree < b are used (block of the low b coefficients); b <= n
//   cutoffs: extra ranks at which the depth is recorded (the ends of the degrees up to n/2 are always there)
//   -l: ranks of the lines for the joint tables (at most 2); a line of rank r is the first r irreducibles
//   -t: targets (numbers of rows); default: chosen from the histogram of L (1e4, 1e3, 100, 10, 1 successes)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static int q, p, n, b;
static uint8_t ADD[9][9], MUL[9][9], NEG[9], INV[9], ISSQ[9];
static uint64_t pw[40];

static void field_init(void) {
  if (q == 9) {
    p = 3;
    for (int x = 0; x < 9; x++) for (int y = 0; y < 9; y++) {
      int a = x % 3, bb = x / 3, c = y % 3, d = y / 3;
      ADD[x][y] = (uint8_t)((a + c) % 3 + 3 * ((bb + d) % 3));
      int re = ((a * c - bb * d) % 3 + 3) % 3, im = (a * d + bb * c) % 3;
      MUL[x][y] = (uint8_t)(re + 3 * im);
    }
  } else {
    p = q;
    for (int x = 0; x < q; x++) for (int y = 0; y < q; y++) {
      ADD[x][y] = (uint8_t)((x + y) % q); MUL[x][y] = (uint8_t)((x * y) % q);
    }
  }
  for (int x = 0; x < q; x++) {
    for (int y = 0; y < q; y++) { if (ADD[x][y] == 0) NEG[x] = (uint8_t)y; if (x && MUL[x][y] == 1) INV[x] = (uint8_t)y; }
    ISSQ[x] = 0;
  }
  for (int x = 1; x < q; x++) ISSQ[MUL[x][x]] = 1;
}

// ---------- small degrees: the list of monic irreducibles ----------
typedef struct { uint8_t deg; uint32_t idx; } irr_t;
static irr_t *irr; static int nirr; static int upto[40];   // upto[d] = number of irreducibles of degree <= d
static int dsmall;

static void digits_of(uint64_t idx, int d, uint8_t *c) { for (int i = 0; i < d; i++) { c[i] = (uint8_t)(idx % q); idx /= q; } c[d] = 1; }
static uint64_t index_of(const uint8_t *c, int d) { uint64_t x = 0; for (int i = d - 1; i >= 0; i--) x = x * q + c[i]; return x; }

static void small_irreducibles(void) {
  int cap = 1 << 20; irr = malloc(sizeof(irr_t) * cap); nirr = 0; upto[0] = 0;
  for (int d = 1; d <= dsmall; d++) {
    uint64_t sz = pw[d]; uint8_t *comp = calloc(sz, 1);
    for (int r = 0; r < nirr && 2 * irr[r].deg <= d; r++) {
      int e = irr[r].deg; uint8_t A[40], B[40], C[80]; digits_of(irr[r].idx, e, A);
      for (uint64_t x = 0; x < pw[d - e]; x++) {
        digits_of(x, d - e, B); memset(C, 0, d + 1);
        for (int i = 0; i <= e; i++) if (A[i]) for (int j = 0; j <= d - e; j++) C[i + j] = ADD[C[i + j]][MUL[A[i]][B[j]]];
        comp[index_of(C, d)] = 1;
      }
    }
    for (uint64_t x = 0; x < sz; x++) if (!comp[x]) {
      if (nirr == cap) { cap *= 2; irr = realloc(irr, sizeof(irr_t) * cap); }
      irr[nirr].deg = (uint8_t)d; irr[nirr].idx = (uint32_t)x; nirr++;
    }
    free(comp); upto[d] = nirr;
  }
}

// ---------- the table for degree n ----------
#define ODD 0x40
#define NSQ 0x80
static uint8_t *T, *SD;
static uint8_t V[48]; static const uint8_t *PE; static int DEG, cur_d, cur_e; static uint8_t cur_cls;

static inline void visit(uint64_t idx) {
  SD[idx] = (uint8_t)(SD[idx] + cur_d);
  uint8_t t = T[idx] ^ ODD;
  if (cur_e >= 2) t |= NSQ; else if ((t & 15) == 15) t = (uint8_t)((t & 0xF0) | cur_cls);
  T[idx] = t;
}
static void rec(int j, uint64_t idx) {
  if (j < 0) { visit(idx); return; }
  rec(j - 1, idx);
  uint8_t save[48]; memcpy(save, V + j, DEG + 1);
  for (int c = 1; c < q; c++) {
    int64_t id2 = (int64_t)idx;
    for (int i = 0; i <= DEG; i++) {
      uint8_t nv = ADD[save[i]][MUL[c][PE[i]]];
      id2 += ((int64_t)nv - (int64_t)save[i]) * (int64_t)pw[j + i];
      V[j + i] = nv;
    }
    rec(j - 1, (uint64_t)id2);
  }
  memcpy(V + j, save, DEG + 1);
}

static int ncut; static int cutrank[16]; static uint8_t *cls_of_rank;

static void big_sieve(void) {
  uint64_t sz = pw[n]; T = malloc(sz); SD = calloc(sz, 1); memset(T, 15, sz);
  for (int r = 0; r < upto[n / 2]; r++) {
    int d = irr[r].deg; uint8_t P[48], Pe[48], tmp[96]; digits_of(irr[r].idx, d, P);
    memcpy(Pe, P, d + 1); int D = d;
    for (int e = 1; e * d <= n; e++) {
      PE = Pe; DEG = D; cur_d = d; cur_e = e; cur_cls = cls_of_rank[r];
      int m = n - D; memset(V, 0, sizeof V); for (int i = 0; i <= D; i++) V[m + i] = Pe[i];
      uint64_t idx0 = 0; for (int i = n - 1; i >= 0; i--) idx0 = idx0 * q + V[i];
      rec(m - 1, idx0);
      if ((e + 1) * d <= n) {
        memset(tmp, 0, D + d + 1);
        for (int i = 0; i <= D; i++) if (Pe[i]) for (int j = 0; j <= d; j++) tmp[i + j] = ADD[tmp[i + j]][MUL[Pe[i]][P[j]]];
        D += d; memcpy(Pe, tmp, D + 1);
      }
    }
  }
  for (uint64_t x = 0; x < sz; x++) if (SD[x] < n) T[x] ^= ODD;
}

// ---------- rows ----------
static int nrow; static uint16_t *sub; static uint64_t BS;   // block size q^b
static uint8_t mu;

static void build_rows(void) {
  nrow = upto[b - 1]; BS = pw[b]; sub = malloc(sizeof(uint16_t) * (size_t)nrow * BS);
  for (int j = 0; j < nrow; j++) {
    int d = irr[j].deg; uint8_t Q[48]; digits_of(irr[j].idx, d, Q);
    uint64_t lowsz = pw[d + 1]; uint16_t *sj = sub + (size_t)j * BS;
    for (uint64_t lo = 0; lo < lowsz; lo++) {
      uint64_t x = lo, y = 0;
      for (int i = 0; i <= d; i++) { uint8_t c = (uint8_t)(x % q); x /= q; y += (uint64_t)ADD[c][NEG[MUL[mu][Q[i]]]] * pw[i]; }
      for (uint64_t hi = 0; hi < BS; hi += lowsz) sj[hi + lo] = (uint16_t)(hi + y);
    }
  }
}

typedef struct { uint64_t idx; uint32_t L; } top_t;
static top_t *top; static size_t ntop, captop; static uint32_t thr;
static int cmp_top(const void *a, const void *bb) {
  const top_t *x = a, *y = bb; if (x->L != y->L) return x->L > y->L ? -1 : 1; return x->idx < y->idx ? -1 : (x->idx > y->idx);
}
static void record(uint64_t idx, uint32_t L) {
  if (ntop == captop) {
    qsort(top, ntop, sizeof(top_t), cmp_top);
    size_t keep = captop / 2; uint32_t newthr = top[keep].L + 1;      // drop everything with L <= top[keep].L
    while (keep > 0 && top[keep - 1].L < newthr) keep--;
    ntop = keep; thr = newthr;
    if (L < thr) return;
  }
  top[ntop].idx = idx; top[ntop].L = L; ntop++;
}

static uint64_t *histL; static uint64_t nexhaust;

static void pass1(void) {
  histL = calloc(nrow + 1, sizeof(uint64_t)); nexhaust = 0;
  uint16_t *alive = malloc(sizeof(uint16_t) * BS);
  uint64_t nblocks = pw[n - b];
  for (uint64_t hi = 0; hi < nblocks; hi++) {
    uint64_t base = hi * BS; const uint8_t *TB = T + base; uint64_t na = BS;
    for (uint64_t i = 0; i < BS; i++) alive[i] = (uint16_t)i;
    for (int j = 0; j < nrow && na; j++) {
      const uint16_t *sj = sub + (size_t)j * BS; uint64_t m = 0;
      for (uint64_t i = 0; i < na; i++) {
        uint16_t L = alive[i];
        if ((TB[sj[L]] & 15) == 15) { histL[j]++; if ((uint32_t)j >= thr) record(base + L, (uint32_t)j); }
        else alive[m++] = L;
      }
      na = m;
    }
    for (uint64_t i = 0; i < na; i++) { histL[nrow]++; nexhaust++; record(base + alive[i], (uint32_t)nrow); }
  }
  free(alive);
}

// ---------- pass 2: fixed targets ----------
#define MAXT 10
#define MAXL 2
static int nt; static int target[MAXT]; static int nline; static int line[MAXL];
static uint64_t *Hk[MAXT], *Sk[MAXT], *Ho[MAXT], *So[MAXT];      // [(z+1)*(R+1) + k], z = -1 .. ncut-1
static uint32_t *minK[MAXT][MAXL]; static uint64_t *sumK[MAXT][MAXL];   // [k_line*ncut + z]
static uint64_t *Hjo[MAXT][MAXL], *Sjo[MAXT][MAXL];              // [k*(R+1) + o]

static void pass2(void) {
  int Rmax = target[nt - 1];
  for (int ti = 0; ti < nt; ti++) {
    size_t R1 = (size_t)target[ti] + 1;
    Hk[ti] = calloc((ncut + 1) * R1, 8); Sk[ti] = calloc((ncut + 1) * R1, 8);
    Ho[ti] = calloc((ncut + 1) * R1, 8); So[ti] = calloc((ncut + 1) * R1, 8);
    for (int li = 0; li < nline; li++) {
      minK[ti][li] = malloc(R1 * ncut * 4); memset(minK[ti][li], 0xFF, R1 * ncut * 4);
      sumK[ti][li] = calloc(R1 * ncut, 8);
      Hjo[ti][li] = calloc(R1 * R1, 8); Sjo[ti][li] = calloc(R1 * R1, 8);
    }
  }
  uint16_t *cnt = malloc(sizeof(uint16_t) * BS * 16), *cno = malloc(sizeof(uint16_t) * BS * 16);
  uint8_t *won = malloc(BS);
  uint64_t nblocks = pw[n - b];
  for (uint64_t hi = 0; hi < nblocks; hi++) {
    uint64_t base = hi * BS; const uint8_t *TB = T + base;
    memset(cnt, 0, sizeof(uint16_t) * BS * 16); memset(cno, 0, sizeof(uint16_t) * BS * 16); memset(won, 0, BS);
    int ti = 0;
    for (int j = 0; j < Rmax; j++) {
      const uint16_t *sj = sub + (size_t)j * BS;
      for (uint64_t L = 0; L < BS; L++) {
        uint8_t e = TB[sj[L]]; int c = e & 15;
        cnt[L * 16 + c]++;
        if ((e & 0xC0) == ODD) cno[L * 16 + c]++;
        if (c == 15) won[L] = 1;
      }
      while (ti < nt && j + 1 == target[ti]) {
        size_t R1 = (size_t)target[ti] + 1;
        for (uint64_t L = 0; L < BS; L++) {
          const uint16_t *ck = cnt + L * 16, *co = cno + L * 16; uint32_t kz[16], oz[16];
          uint32_t k = ck[15], o = co[15];
          for (int z = ncut - 1; z >= 0; z--) { kz[z] = k; oz[z] = o; k += ck[z]; o += co[z]; }
          uint64_t s = won[L] ? 0 : 1;
          Hk[ti][k]++; Sk[ti][k] += s; Ho[ti][o]++; So[ti][o] += s;          // z = -1: no sieve
          for (int z = 0; z < ncut; z++) {
            Hk[ti][(z + 1) * R1 + kz[z]]++; Sk[ti][(z + 1) * R1 + kz[z]] += s;
            Ho[ti][(z + 1) * R1 + oz[z]]++; So[ti][(z + 1) * R1 + oz[z]] += s;
          }
          for (int li = 0; li < nline; li++) {
            int zl = line[li]; uint32_t kl = kz[zl];
            uint32_t *mk = minK[ti][li] + (size_t)kl * ncut; uint64_t *sk = sumK[ti][li] + (size_t)kl * ncut;
            for (int z = 0; z < ncut; z++) { if (kz[z] < mk[z]) mk[z] = kz[z]; sk[z] += kz[z]; }
            Hjo[ti][li][(size_t)kl * R1 + oz[zl]]++; Sjo[ti][li][(size_t)kl * R1 + oz[zl]] += s;
          }
        }
        ti++;
      }
    }
  }
  free(cnt); free(cno); free(won);
}

static void flags(FILE *f, const uint8_t *c);
// ---------- detail of one member ----------
static uint8_t entry_of(uint64_t idx, int j) {    // table entry of M - mu*Q_j
  uint64_t low = idx % BS; return T[idx - low + sub[(size_t)j * BS + low]];
}
static void detail(FILE *f, uint64_t idx, uint32_t L) {
  uint8_t c[48]; digits_of(idx, n, c);
  int insep = 1; for (int i = 1; i <= n; i++) if (c[i] && (i % p)) insep = 0;
  fprintf(f, "TOP L=%u D=%d idx=%llu insep=%d M=", L, L < (uint32_t)nrow ? irr[L].deg : 99, (unsigned long long)idx, insep);
  for (int i = n; i >= 0; i--) fprintf(f, "%d", c[i]);
  fprintf(f, " values=");
  for (int a = 0; a < q; a++) { uint8_t v = 0; for (int i = n; i >= 0; i--) v = ADD[MUL[v][a]][c[i]]; fprintf(f, "%d", v); }
  uint32_t ck[16] = {0}, co[16] = {0};
  for (uint32_t j = 0; j < L && j < (uint32_t)nrow; j++) { uint8_t e = entry_of(idx, (int)j); ck[e & 15]++; if ((e & 0xC0) == ODD) co[e & 15]++; }
  uint32_t k = ck[15], o = co[15]; uint32_t kz[16], oz[16];
  for (int z = ncut - 1; z >= 0; z--) { kz[z] = k; oz[z] = o; k += ck[z]; o += co[z]; }
  flags(f, c);
  fprintf(f, " odd=%u k=", o); for (int z = 0; z < ncut; z++) fprintf(f, "%u%s", kz[z], z + 1 < ncut ? "," : "");
  fprintf(f, " o="); for (int z = 0; z < ncut; z++) fprintf(f, "%u%s", oz[z], z + 1 < ncut ? "," : "");
  fprintf(f, "\n");
}

// ---------- symmetries and families ----------
static uint32_t L_of(uint64_t idx) {             // rows before the first success, by direct lookups
  uint64_t low = idx % BS; const uint8_t *TB = T + (idx - low);
  for (int j = 0; j < nrow; j++) if ((TB[sub[(size_t)j * BS + low]] & 15) == 15) return (uint32_t)j;
  return (uint32_t)nrow;
}
static void shift_poly(const uint8_t *c, int d, uint8_t s, uint8_t a, uint8_t *out) {   // out(t) = c(a t + s), degree d
  uint8_t acc[48]; memset(acc, 0, sizeof acc); int da = 0; acc[0] = c[d];
  for (int i = d - 1; i >= 0; i--) {             // acc = acc * (a t + s) + c[i]
    uint8_t nw[48]; memset(nw, 0, sizeof nw);
    for (int k = 0; k <= da; k++) { nw[k + 1] = ADD[nw[k + 1]][MUL[acc[k]][a]]; nw[k] = ADD[nw[k]][MUL[acc[k]][s]]; }
    da++; nw[0] = ADD[nw[0]][c[i]]; memcpy(acc, nw, da + 1);
  }
  memcpy(out, acc, d + 1);
}
static void flags(FILE *f, const uint8_t *c) {
  int dd = -1; for (int i = 1; i <= n; i++) if (c[i] && (i % p)) dd = i - 1;
  fprintf(f, " dM=%d trans=", dd);
  int any = 0;
  for (int s = 1; s < q; s++) { uint8_t o[48]; shift_poly(c, n, (uint8_t)s, 1, o); if (!memcmp(o, c, n + 1)) { fprintf(f, "%d", s); any = 1; } }
  if (!any) fprintf(f, "-");
  fprintf(f, " scal="); any = 0;
  for (int a = 2; a < q; a++) {                   // M(a t) = a^n M(t)
    uint8_t o[48]; shift_poly(c, n, 0, (uint8_t)a, o); uint8_t an = o[n]; int ok = 1;
    for (int i = 0; i <= n; i++) if (o[i] != MUL[an][c[i]]) ok = 0;
    if (ok) { fprintf(f, "%d", a); any = 1; }
  }
  if (!any) fprintf(f, "-");
}
static void family_out(FILE *f, const char *name, uint64_t size, const uint64_t *h) {
  fprintf(f, "FAMILY %s size=%llu HISTL", name, (unsigned long long)size);
  for (int j = 0; j <= nrow; j++) if (h[j]) fprintf(f, " %d:%llu", j, (unsigned long long)h[j]);
  fprintf(f, "\n");
}
static void family_mask(FILE *f, const char *name, const uint8_t *freepos) {   // members whose digits vanish off freepos
  int pos[48], np = 0; for (int i = 0; i < n; i++) if (freepos[i]) pos[np++] = i;
  double sz = 1; for (int i = 0; i < np; i++) sz *= q;
  if (sz > 6e7) { fprintf(f, "FAMILY %s size=%.0f (not enumerated)\n", name, sz); return; }
  uint64_t size = (uint64_t)sz, *h = calloc(nrow + 1, 8);
  for (uint64_t x = 0; x < size; x++) {
    uint64_t y = x, idx = 0; for (int i = 0; i < np; i++) { idx += (y % q) * pw[pos[i]]; y /= q; }
    h[L_of(idx)]++;
  }
  family_out(f, name, size, h); free(h);
}
static void family_trans(FILE *f, uint8_t s) {    // members g(t^p - s^(p-1) t), g monic of degree n/p
  if (n % p) return;
  int m = n / p; uint8_t u[48]; memset(u, 0, sizeof u); u[p] = 1;
  uint8_t sp = 1; for (int i = 0; i < p - 1; i++) sp = MUL[sp][s];
  u[1] = NEG[sp];
  uint64_t size = pw[m], *h = calloc(nrow + 1, 8);
  for (uint64_t x = 0; x < size; x++) {
    uint8_t g[48]; digits_of(x, m, g);
    uint8_t acc[64]; memset(acc, 0, sizeof acc); int da = 0; acc[0] = 1;
    for (int i = m - 1; i >= 0; i--) {             // acc = acc * u + g[i]
      uint8_t nw[64]; memset(nw, 0, sizeof nw);
      for (int k = 0; k <= da; k++) if (acc[k]) { nw[k + p] = ADD[nw[k + p]][acc[k]]; nw[k + 1] = ADD[nw[k + 1]][MUL[acc[k]][u[1]]]; }
      da += p; nw[0] = ADD[nw[0]][g[i]]; memcpy(acc, nw, da + 1);
    }
    h[L_of(index_of(acc, n))]++;
  }
  char name[32]; snprintf(name, sizeof name, "trans%d", s);
  family_out(f, name, size, h); free(h);
}
static void family_frob(FILE *f) {               // q = 9: the members with every coefficient in F_3 (fixed by the Frobenius)
  uint64_t size = 1; for (int i = 0; i < n; i++) size *= 3;
  uint64_t *h = calloc(nrow + 1, 8);
  for (uint64_t x = 0; x < size; x++) {
    uint64_t y = x, idx = 0; for (int i = 0; i < n; i++) { idx += (y % 3) * pw[i]; y /= 3; }
    h[L_of(idx)]++;
  }
  family_out(f, "frobenius", size, h); free(h);
}
static void families(FILE *f) {
  uint8_t fp[48];
  if (n % p == 0) { for (int i = 0; i < n; i++) fp[i] = (i % p == 0); family_mask(f, "insep", fp); }
  for (int e = 0; e <= 2; e++) { for (int i = 0; i < n; i++) fp[i] = (i % p == 0) || (i <= e + 1); char nm[32]; snprintf(nm, sizeof nm, "derivdeg<=%d", e); family_mask(f, nm, fp); }
  for (int i = 0; i < n; i++) fp[i] = ((n - i) % 2 == 0);
  family_mask(f, "scal-1", fp);
  if (q > 3) { for (int i = 0; i < n; i++) fp[i] = ((n - i) % (q - 1) == 0); family_mask(f, "scalall", fp); }
  if (q == 9) { for (int i = 0; i < n; i++) fp[i] = ((n - i) % 4 == 0); family_mask(f, "scal4", fp); }
  if (q == 9) { family_frob(f); family_trans(f, 1); family_trans(f, 3); family_trans(f, 4); family_trans(f, 7); }
  else family_trans(f, 1);
}

static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }
static int cmp_int(const void *a, const void *bb) { return *(const int *)a - *(const int *)bb; }

int main(int argc, char **argv) {
  if (argc < 6) { fprintf(stderr, "usage: w3 q n mu b OUT [cutoff ranks] [-l lines] [-t targets] [-top K]\n"); return 1; }
  q = atoi(argv[1]); n = atoi(argv[2]); mu = (uint8_t)atoi(argv[3]); b = atoi(argv[4]); const char *outname = argv[5];
  int extra[16], nextra = 0, topK = 40, mode = 0; nline = 0; nt = 0;
  for (int i = 6; i < argc; i++) {
    if (!strcmp(argv[i], "-l")) { mode = 1; continue; }
    if (!strcmp(argv[i], "-t")) { mode = 2; continue; }
    if (!strcmp(argv[i], "-top")) { mode = 3; continue; }
    int v = atoi(argv[i]);
    if (mode == 0) extra[nextra++] = v; else if (mode == 1) line[nline++] = v; else if (mode == 2) target[nt++] = v; else topK = v;
  }
  if (b > n) b = n;
  field_init(); pw[0] = 1; for (int i = 1; i < 40; i++) pw[i] = pw[i - 1] * (uint64_t)q;
  if (pw[b] > 65536) { fprintf(stderr, "block too large\n"); return 1; }
  double t0 = now();
  dsmall = n / 2 > b - 1 ? n / 2 : b - 1; small_irreducibles();
  // cutoffs: the ends of the degrees up to n/2, and the extra ranks
  ncut = 0; for (int d = 1; d <= n / 2; d++) cutrank[ncut++] = upto[d];
  for (int i = 0; i < nline; i++) extra[nextra++] = line[i];
  for (int i = 0; i < nextra; i++) { int dup = 0; for (int k = 0; k < ncut; k++) if (cutrank[k] == extra[i]) dup = 1; if (!dup && extra[i] < upto[n / 2]) cutrank[ncut++] = extra[i]; }
  qsort(cutrank, ncut, sizeof(int), cmp_int);
  if (ncut > 15) { fprintf(stderr, "too many cutoffs\n"); return 1; }
  cls_of_rank = malloc(upto[n / 2] + 1);
  for (int r = 0, z = 0; r < upto[n / 2]; r++) { while (r >= cutrank[z]) z++; cls_of_rank[r] = (uint8_t)z; }
  FILE *f = fopen(outname, "w");
  fprintf(f, "# q=%d n=%d mu=%d (mu a square: %d) b=%d members=%llu\n", q, n, mu, ISSQ[mu], b, (unsigned long long)pw[n]);
  fprintf(f, "IRRED"); for (int d = 1; d <= dsmall; d++) fprintf(f, " deg%d:%d", d, upto[d] - upto[d - 1]); fprintf(f, "\n");
  fprintf(f, "CUTOFFS (index:rank:total degree)");
  for (int z = 0; z < ncut; z++) { int td = 0; for (int r = 0; r < cutrank[z]; r++) td += irr[r].deg; fprintf(f, " %d:%d:%d", z, cutrank[z], td); }
  fprintf(f, "\n");
  big_sieve(); double t1 = now();
  uint64_t nir = 0, nsqf = 0; int64_t msum = 0;
  for (uint64_t x = 0; x < pw[n]; x++) { uint8_t e = T[x]; if ((e & 15) == 15) nir++; if (!(e & NSQ)) { nsqf++; msum += (e & ODD) ? -1 : 1; } if ((SD[x] == 0) != ((e & 15) == 15)) { fprintf(stderr, "inconsistent table\n"); return 1; } }
  free(SD);
  fprintf(f, "CHECK irreducible=%llu squarefree=%llu (q^n-q^(n-1)=%llu) sum_mobius=%lld\n", (unsigned long long)nir, (unsigned long long)nsqf, (unsigned long long)(pw[n] - pw[n - 1]), (long long)msum);
  build_rows();
  captop = 1 << 20; top = malloc(sizeof(top_t) * captop); ntop = 0; thr = 0;
  pass1(); double t2 = now();
  fprintf(f, "ROWS %d (degree < %d); members with no success among them: %llu\n", nrow, b, (unsigned long long)nexhaust);
  fprintf(f, "HISTL (L:members)"); for (int j = 0; j <= nrow; j++) if (histL[j]) fprintf(f, " %d:%llu", j, (unsigned long long)histL[j]); fprintf(f, "\n");
  qsort(top, ntop, sizeof(top_t), cmp_top);
  if (nt == 0) {                               // targets: the largest R with at least S members having L >= R
    double want[8] = {1e4, 3e3, 1e3, 3e2, 1e2, 30, 10, 1};
    for (int w = 0; w < 8; w++) {
      uint64_t acc = 0; int R = 0;
      for (int j = nrow; j >= 1; j--) { acc += histL[j]; if ((double)acc >= want[w]) { R = j; break; } }
      if (R > 0 && R < nrow && (nt == 0 || target[nt - 1] != R)) target[nt++] = R;
    }
  }
  qsort(target, nt, sizeof(int), cmp_int);
  for (int i = 0; i < nline; i++) {            // lines are given as ranks; turn them into indices of the cutoff list
    int z = -1; for (int k = 0; k < ncut; k++) if (cutrank[k] == line[i]) z = k;
    if (z < 0) { fprintf(stderr, "line %d is not a cutoff\n", line[i]); return 1; }
    line[i] = z;
  }
  if (nline == 0) { nline = 1; line[0] = 0; }
  fprintf(f, "TARGETS"); for (int i = 0; i < nt; i++) { uint64_t acc = 0; for (int j = target[i]; j <= nrow; j++) acc += histL[j]; fprintf(f, " %d:%llu", target[i], (unsigned long long)acc); } fprintf(f, "\n");
  fprintf(f, "LINES"); for (int i = 0; i < nline; i++) fprintf(f, " %d", line[i]); fprintf(f, "\n");
  for (size_t i = 0; i < ntop && i < (size_t)topK; i++) detail(f, top[i].idx, top[i].L);
  families(f);
  fflush(f);
  if (nt > 0) {
    pass2(); double t3 = now();
    for (int ti = 0; ti < nt; ti++) {
      size_t R1 = (size_t)target[ti] + 1;
      for (int z = -1; z < ncut; z++) {
        fprintf(f, "HK target=%d z=%d", target[ti], z);
        for (size_t k = 0; k < R1; k++) if (Hk[ti][(z + 1) * R1 + k]) fprintf(f, " %zu:%llu:%llu", k, (unsigned long long)Hk[ti][(z + 1) * R1 + k], (unsigned long long)Sk[ti][(z + 1) * R1 + k]);
        fprintf(f, "\nHO target=%d z=%d", target[ti], z);
        for (size_t k = 0; k < R1; k++) if (Ho[ti][(z + 1) * R1 + k]) fprintf(f, " %zu:%llu:%llu", k, (unsigned long long)Ho[ti][(z + 1) * R1 + k], (unsigned long long)So[ti][(z + 1) * R1 + k]);
        fprintf(f, "\n");
      }
      for (int li = 0; li < nline; li++) {
        int zl = line[li];
        for (size_t k = 0; k < R1; k++) {
          uint64_t h = Hk[ti][(zl + 1) * R1 + k]; if (!h) continue;
          fprintf(f, "LINE target=%d line=%d k=%zu members=%llu min", target[ti], zl, k, (unsigned long long)h);
          for (int z = 0; z < ncut; z++) fprintf(f, " %u", minK[ti][li][k * ncut + z]);
          fprintf(f, " mean"); for (int z = 0; z < ncut; z++) fprintf(f, " %.3f", (double)sumK[ti][li][k * ncut + z] / (double)h);
          fprintf(f, "\n");
        }
        fprintf(f, "JOINT target=%d line=%d (k:o:members:successes)", target[ti], zl);
        for (size_t k = 0; k < R1; k++) for (size_t o = 0; o < R1; o++) if (Hjo[ti][li][k * R1 + o]) fprintf(f, " %zu:%zu:%llu:%llu", k, o, (unsigned long long)Hjo[ti][li][k * R1 + o], (unsigned long long)Sjo[ti][li][k * R1 + o]);
        fprintf(f, "\n");
      }
    }
    fprintf(f, "TIME sieve %.1f pass1 %.1f pass2 %.1f\n", t1 - t0, t2 - t1, t3 - t2);
  } else fprintf(f, "TIME sieve %.1f pass1 %.1f\n", t1 - t0, t2 - t1);
  fclose(f);
  return 0;
}
