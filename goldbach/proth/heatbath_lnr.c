/* heatbath_lnr.c -- Memory-bounded ln(r)-weighted full-cover optimizer (Features F12 & F17A).
 *
 * Conforms strictly to PROJECT.md Interface Contract #1:
 *   CLI:
 *     ./heatbath_lnr --Q <int> [--rmax <int>] [--init-cover <json|txt>]
 *                    [--steps <int>] [--hb-sweeps <int>] [--seed <u64>]
 *                    [--threads <int>] [--out <out.json>]
 *   Output JSON (written atomically to --out <path>, or to stdout if --out is omitted / "-"):
 *     {"Q": int, "classes": [[r,a],...], "num_classes": int,
 *      "sum_ln_r": float, "Mc_digits": float, "uncovered": 0,
 *      "seed": int, "steps": int}
 *
 * Architecture (peak RAM <= 200 MB at Q=16,045,849, rmax=1,500,000):
 *   - odd_to_idx[Q/2+1] + cov[nP] + owner_xor[nP] + uniq_cnt[n_cand] gives O(1)
 *     exact unique-coverage loss and O(nu) heatbath gain scans via Lemire fastmod_u32.
 *   - Small-modulus CSR cache ONLY for r <= 127 (<= 30 moduli); odd-stride scan for r > 127.
 *   - Calibrated ln(r)-banded heatbath (16 log-r bands) prevents large-r melting.
 *   - Efficiency-ordered (uniq_cnt[m] / ln(r)) Destroy-Heatbath-Repair (DHR) +
 *     Direct Lagrangian ln(r) Heatbath + portable OpenMP/pthread lazy-greedy repair +
 *     free-drop & 1/2-unique cheaper-prime swaps.
 *   - Independent final scratch verification asserting uncovered == 0 and 1 <= a < r
 *     for every odd prime 3 <= q < Q before atomic JSON write.
 *
 * Build (portable with or without -fopenmp):
 *   gcc -O3 -Wall -Wextra goldbach/proth/heatbath_lnr.c -lm -lpthread -o heatbath_lnr
 *   gcc -O3 -fopenmp -Wall -Wextra goldbach/proth/heatbath_lnr.c -lm -o heatbath_lnr
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#ifdef _OPENMP
#include <omp.h>
#else
#include <pthread.h>
#endif

static inline double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

#define SMALL_R_LIM 127
#define MAX_SMALL   32
#define NBANDS      16
#define BTAB_LEN    256

/* Deterministic xorshift64* PRNG */
typedef struct { uint64_t s; } rng_t;
static inline uint64_t rng_u64(rng_t *r) {
    uint64_t x = r->s;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    r->s = x;
    return x * 0x2545F4914F6CDD1DULL;
}
static inline double rng_f64(rng_t *r) {
    return (double)(rng_u64(r) >> 11) * (1.0 / 9007199254740992.0);
}

/* Exact Lemire 32-bit fastmod for odd d >= 3, a < 2^32 */
static inline uint64_t fastmod_inv(uint32_t d) {
    return (~0ULL / (uint64_t)d) + 1ULL;
}
static inline uint32_t fastmod_u32(uint32_t a, uint64_t M, uint32_t d) {
    uint64_t lowbits = M * (uint64_t)a;
    return (uint32_t)(((__uint128_t)lowbits * (uint64_t)d) >> 64);
}

/* Global prime universe & state */
static uint32_t  g_Q = 0;
static uint32_t  g_rmax = 0;
static uint32_t  g_nP = 0;
static uint32_t *g_prime = NULL;       /* [g_nP] odd primes 3 <= q < Q */
static int32_t  *g_odd_to_idx = NULL;  /* [Q/2 + 2] */

static uint16_t *g_cov = NULL;         /* [g_nP] */
static uint32_t *g_xor = NULL;         /* [g_nP] */
static int32_t  *g_ul = NULL;          /* [g_nP] */
static int32_t  *g_upos = NULL;        /* [g_nP] */
static int32_t   g_nu = 0;

static uint32_t  g_ncand = 0;
static uint32_t *g_r = NULL;           /* [g_ncand] */
static uint64_t *g_inv = NULL;         /* [g_ncand] */
static double   *g_lnr = NULL;         /* [g_ncand] */
static uint8_t  *g_band = NULL;        /* [g_ncand] log-r temperature band 0..NBANDS-1 */
static uint8_t  *g_active = NULL;      /* [g_ncand] */
static uint32_t *g_resa = NULL;        /* [g_ncand] */
static uint32_t *g_uniq = NULL;        /* [g_ncand] */
static uint32_t  g_nactive = 0;
static double    g_sum_lnr = 0.0;

/* Small-prime CSR cache for r <= SMALL_R_LIM */
static uint32_t  g_nsmall = 0;
static int32_t  *g_soff[MAX_SMALL];
static int32_t  *g_sidx[MAX_SMALL];

/* Saved cover snapshots */
typedef struct {
    uint32_t n;
    uint32_t *m_id;
    uint32_t *a_val;
    double sum_lnr;
} cover_snap_t;

/* Binary max-heap for lazy-greedy repair */
typedef struct {
    double score;
    uint32_t m;
    uint32_t a;
    uint32_t stamp;
} hnode_t;

static hnode_t *g_heap = NULL;
static uint32_t g_hsize = 0;

/* Reusable scratch */
static uint32_t *g_gcnt = NULL;
static uint32_t *g_touched = NULL;
static double   *g_hw = NULL;
static uint32_t *g_up_primes = NULL;

static double g_band_beta[NBANDS];
static double g_band_exp[NBANDS][BTAB_LEN];
static double g_band_lnr[NBANDS];

static void free_snap(cover_snap_t *S) {
    free(S->m_id);  S->m_id = NULL;
    free(S->a_val); S->a_val = NULL;
    S->n = 0;
}

static void free_all_globals(void) {
    for (uint32_t m = 0; m < g_nsmall; m++) {
        free(g_soff[m]); g_soff[m] = NULL;
        free(g_sidx[m]); g_sidx[m] = NULL;
    }
    g_nsmall = 0;
    free(g_prime);      g_prime = NULL;
    free(g_odd_to_idx); g_odd_to_idx = NULL;
    free(g_cov);        g_cov = NULL;
    free(g_xor);        g_xor = NULL;
    free(g_ul);         g_ul = NULL;
    free(g_upos);       g_upos = NULL;
    free(g_r);          g_r = NULL;
    free(g_inv);        g_inv = NULL;
    free(g_lnr);        g_lnr = NULL;
    free(g_band);       g_band = NULL;
    free(g_active);     g_active = NULL;
    free(g_resa);       g_resa = NULL;
    free(g_uniq);       g_uniq = NULL;
    free(g_heap);       g_heap = NULL;
    free(g_gcnt);       g_gcnt = NULL;
    free(g_touched);    g_touched = NULL;
    free(g_hw);         g_hw = NULL;
    free(g_up_primes);  g_up_primes = NULL;
}

static inline void ul_add(int32_t i) {
    g_upos[i] = g_nu;
    g_ul[g_nu++] = i;
}
static inline void ul_del(int32_t i) {
    int32_t p = g_upos[i];
    int32_t last = g_ul[--g_nu];
    g_ul[p] = last;
    g_upos[last] = p;
    g_upos[i] = -1;
}

static void reset_state(void) {
    memset(g_cov, 0, sizeof(uint16_t) * g_nP);
    memset(g_xor, 0, sizeof(uint32_t) * g_nP);
    for (uint32_t i = 0; i < g_nP; i++) {
        g_ul[i] = (int32_t)i;
        g_upos[i] = (int32_t)i;
    }
    g_nu = (int32_t)g_nP;
    memset(g_active, 0, sizeof(uint8_t) * g_ncand);
    memset(g_resa, 0, sizeof(uint32_t) * g_ncand);
    memset(g_uniq, 0, sizeof(uint32_t) * g_ncand);
    g_nactive = 0;
    g_sum_lnr = 0.0;
}

static inline void add_mod(uint32_t m, uint32_t a) {
    uint32_t r = g_r[m];
    if (m < g_nsmall) {
        const int32_t *idx = g_sidx[m];
        int32_t s0 = g_soff[m][a], s1 = g_soff[m][a + 1];
        for (int32_t k = s0; k < s1; k++) {
            int32_t i = idx[k];
            uint16_t old_c = g_cov[i];
            if (old_c == 1) g_uniq[g_xor[i]]--;
            g_cov[i] = (uint16_t)(old_c + 1);
            g_xor[i] ^= m;
            if (old_c == 0) { g_uniq[m]++; ul_del(i); }
        }
    } else {
        uint64_t x = (a & 1u) ? (uint64_t)a : (uint64_t)a + (uint64_t)r;
        uint64_t step = (uint64_t)r << 1;
        uint64_t Q64 = (uint64_t)g_Q;
        for (; x < Q64; x += step) {
            int32_t i = g_odd_to_idx[x >> 1];
            if (i < 0) continue;
            uint16_t old_c = g_cov[i];
            if (old_c == 1) g_uniq[g_xor[i]]--;
            g_cov[i] = (uint16_t)(old_c + 1);
            g_xor[i] ^= m;
            if (old_c == 0) { g_uniq[m]++; ul_del(i); }
        }
    }
    g_active[m] = 1;
    g_resa[m] = a;
    g_nactive++;
    g_sum_lnr += g_lnr[m];
}

static inline void remove_mod(uint32_t m) {
    uint32_t r = g_r[m];
    uint32_t a = g_resa[m];
    if (m < g_nsmall) {
        const int32_t *idx = g_sidx[m];
        int32_t s0 = g_soff[m][a], s1 = g_soff[m][a + 1];
        for (int32_t k = s0; k < s1; k++) {
            int32_t i = idx[k];
            uint16_t old_c = g_cov[i];
            g_cov[i] = (uint16_t)(old_c - 1);
            g_xor[i] ^= m;
            if (old_c == 1) { g_uniq[m]--; ul_add(i); }
            else if (old_c == 2) { g_uniq[g_xor[i]]++; }
        }
    } else {
        uint64_t x = (a & 1u) ? (uint64_t)a : (uint64_t)a + (uint64_t)r;
        uint64_t step = (uint64_t)r << 1;
        uint64_t Q64 = (uint64_t)g_Q;
        for (; x < Q64; x += step) {
            int32_t i = g_odd_to_idx[x >> 1];
            if (i < 0) continue;
            uint16_t old_c = g_cov[i];
            g_cov[i] = (uint16_t)(old_c - 1);
            g_xor[i] ^= m;
            if (old_c == 1) { g_uniq[m]--; ul_add(i); }
            else if (old_c == 2) { g_uniq[g_xor[i]]++; }
        }
    }
    g_active[m] = 0;
    g_resa[m] = 0;
    g_nactive--;
    g_sum_lnr -= g_lnr[m];
}

static void save_snap(cover_snap_t *S) {
    S->n = 0;
    S->sum_lnr = 0.0;
    for (uint32_t m = 0; m < g_ncand; m++) {
        if (g_active[m]) {
            S->m_id[S->n] = m;
            S->a_val[S->n] = g_resa[m];
            S->sum_lnr += g_lnr[m];
            S->n++;
        }
    }
}

static void restore_snap(const cover_snap_t *S) {
    reset_state();
    for (uint32_t k = 0; k < S->n; k++) {
        add_mod(S->m_id[k], S->a_val[k]);
    }
}

static inline void heap_sift_down(uint32_t idx) {
    hnode_t v = g_heap[idx];
    while (1) {
        uint32_t l = (idx << 1) + 1;
        if (l >= g_hsize) break;
        uint32_t r = l + 1;
        uint32_t best = l;
        if (r < g_hsize && (g_heap[r].score > g_heap[l].score ||
            (g_heap[r].score == g_heap[l].score && g_heap[r].m < g_heap[l].m))) {
            best = r;
        }
        if (v.score > g_heap[best].score ||
            (v.score == g_heap[best].score && v.m < g_heap[best].m)) break;
        g_heap[idx] = g_heap[best];
        idx = best;
    }
    g_heap[idx] = v;
}

static inline void heap_sift_up(uint32_t idx) {
    hnode_t v = g_heap[idx];
    while (idx > 0) {
        uint32_t p = (idx - 1) >> 1;
        if (g_heap[p].score > v.score ||
            (g_heap[p].score == v.score && g_heap[p].m < v.m)) break;
        g_heap[idx] = g_heap[p];
        idx = p;
    }
    g_heap[idx] = v;
}

static inline hnode_t heap_pop(void) {
    hnode_t top = g_heap[0];
    g_hsize--;
    if (g_hsize > 0) {
        g_heap[0] = g_heap[g_hsize];
        heap_sift_down(0);
    }
    return top;
}

static inline void heap_push(hnode_t v) {
    g_heap[g_hsize] = v;
    heap_sift_up(g_hsize);
    g_hsize++;
}

/* Score candidate m against contiguous prime list up[0..nu-1], strict 1 <= a < r */
static inline uint32_t score_cand_on_list(
    uint32_t m, const uint32_t *up, int32_t nu,
    uint32_t *cnt, uint32_t *touched, uint32_t *best_a_out
) {
    uint32_t r = g_r[m];
    uint64_t inv = g_inv[m];
    uint32_t nt = 0, best_h = 0, best_a = 1;
    for (int32_t u = 0; u < nu; u++) {
        uint32_t c = fastmod_u32(up[u], inv, r);
        if (c == 0) continue; /* STRICT: forbid a == 0 */
        uint32_t v = ++cnt[c];
        if (v == 1) touched[nt++] = c;
        if (v > best_h || (v == best_h && c < best_a)) {
            best_h = v;
            best_a = c;
        }
    }
    for (uint32_t t = 0; t < nt; t++) cnt[touched[t]] = 0;
    *best_a_out = best_a;
    return best_h;
}

#ifndef _OPENMP
typedef struct {
    const uint32_t *inact;
    uint32_t nin;
    int32_t nu0;
    hnode_t *tmp_nodes;
    uint8_t *valid_node;
    uint32_t next_idx;
} repair_ctx_t;

static void *repair_worker(void *arg) {
    repair_ctx_t *ctx = (repair_ctx_t *)arg;
    uint32_t *t_cnt = calloc((size_t)(g_rmax + 2), sizeof(uint32_t));
    uint32_t max_t = (uint32_t)ctx->nu0 < g_rmax ? (uint32_t)ctx->nu0 + 2 : g_rmax + 2;
    uint32_t *t_tch = malloc(sizeof(uint32_t) * max_t);
    while (1) {
        uint32_t start = __atomic_fetch_add(&ctx->next_idx, 64u, __ATOMIC_RELAXED);
        if (start >= ctx->nin) break;
        uint32_t end = start + 64u;
        if (end > ctx->nin) end = ctx->nin;
        for (uint32_t idx = start; idx < end; idx++) {
            uint32_t m = ctx->inact[idx];
            uint32_t best_a = 1;
            uint32_t h = score_cand_on_list(m, g_up_primes, ctx->nu0, t_cnt, t_tch, &best_a);
            if (h > 0) {
                ctx->tmp_nodes[idx].score = (double)h / g_lnr[m];
                ctx->tmp_nodes[idx].m = m;
                ctx->tmp_nodes[idx].a = best_a;
                ctx->tmp_nodes[idx].stamp = 0;
                ctx->valid_node[idx] = 1;
            }
        }
    }
    free(t_cnt);
    free(t_tch);
    return NULL;
}
#endif

/* Portable OpenMP/pthread lazy-greedy weighted set-cover repair until nu == 0 */
static int repair_to_zero(int nthreads) {
    if (g_nu == 0) return 0;

    int32_t nu0 = g_nu;
    for (int32_t u = 0; u < nu0; u++) g_up_primes[u] = g_prime[g_ul[u]];

    /* Collect inactive candidates */
    uint32_t *inact = malloc(sizeof(uint32_t) * g_ncand);
    uint32_t nin = 0;
    for (uint32_t m = 0; m < g_ncand; m++) if (!g_active[m]) inact[nin++] = m;
    if (nin == 0) { free(inact); return -1; }

    hnode_t *tmp_nodes = malloc(sizeof(hnode_t) * nin);
    uint8_t *valid_node = calloc(nin, sizeof(uint8_t));

    if (nthreads <= 1 || nin < 128) {
        for (uint32_t idx = 0; idx < nin; idx++) {
            uint32_t m = inact[idx];
            uint32_t best_a = 1;
            uint32_t h = score_cand_on_list(m, g_up_primes, nu0, g_gcnt, g_touched, &best_a);
            if (h > 0) {
                tmp_nodes[idx].score = (double)h / g_lnr[m];
                tmp_nodes[idx].m = m;
                tmp_nodes[idx].a = best_a;
                tmp_nodes[idx].stamp = 0;
                valid_node[idx] = 1;
            }
        }
    } else {
#ifdef _OPENMP
        #pragma omp parallel num_threads(nthreads)
        {
            uint32_t *t_cnt = calloc((size_t)(g_rmax + 2), sizeof(uint32_t));
            uint32_t max_t = (uint32_t)nu0 < g_rmax ? (uint32_t)nu0 + 2 : g_rmax + 2;
            uint32_t *t_tch = malloc(sizeof(uint32_t) * max_t);

            #pragma omp for schedule(dynamic, 64)
            for (uint32_t idx = 0; idx < nin; idx++) {
                uint32_t m = inact[idx];
                uint32_t best_a = 1;
                uint32_t h = score_cand_on_list(m, g_up_primes, nu0, t_cnt, t_tch, &best_a);
                if (h > 0) {
                    tmp_nodes[idx].score = (double)h / g_lnr[m];
                    tmp_nodes[idx].m = m;
                    tmp_nodes[idx].a = best_a;
                    tmp_nodes[idx].stamp = 0;
                    valid_node[idx] = 1;
                }
            }
            free(t_cnt);
            free(t_tch);
        }
#else
        int nt = nthreads > 64 ? 64 : nthreads;
        pthread_t th[64];
        repair_ctx_t ctx = { inact, nin, nu0, tmp_nodes, valid_node, 0u };
        int spawned = 0;
        for (int t = 0; t < nt; t++) {
            if (pthread_create(&th[spawned], NULL, repair_worker, &ctx) == 0) {
                spawned++;
            }
        }
        if (spawned == 0) {
            repair_worker(&ctx);
        } else {
            for (int t = 0; t < spawned; t++) {
                pthread_join(th[t], NULL);
            }
        }
#endif
    }

    g_hsize = 0;
    for (uint32_t idx = 0; idx < nin; idx++) {
        if (valid_node[idx]) g_heap[g_hsize++] = tmp_nodes[idx];
    }
    free(inact);
    free(tmp_nodes);
    free(valid_node);

    /* Bottom-up O(N) heapify */
    for (int64_t i = (int64_t)g_hsize / 2 - 1; i >= 0; i--) heap_sift_down((uint32_t)i);

    uint32_t stamp = 0;
    while (g_nu > 0) {
        if (g_hsize == 0) return -1;
        hnode_t top = heap_pop();
        uint32_t m = top.m;
        uint32_t a = top.a;
        if (g_active[m]) continue;

        if (top.stamp != stamp) {
            for (int32_t u = 0; u < g_nu; u++) g_up_primes[u] = g_prime[g_ul[u]];
            uint32_t best_a = 1;
            uint32_t h = score_cand_on_list(m, g_up_primes, g_nu, g_gcnt, g_touched, &best_a);
            if (h == 0) continue;
            double sc = (double)h / g_lnr[m];
            if (g_hsize > 0 && sc < g_heap[0].score) {
                top.score = sc;
                top.a = best_a;
                top.stamp = stamp;
                heap_push(top);
                continue;
            }
            a = best_a;
        }
        add_mod(m, a);
        stamp++;
    }
    return 0;
}

/* Drop any active modulus with uniq_cnt == 0, plus 1-unique & 2-unique cheaper-prime swaps */
static void polish_free_drops_and_swaps(void) {
    /* 1. Drop redundant moduli */
    int dropped = 1;
    while (dropped) {
        dropped = 0;
        for (uint32_t m = g_ncand; m > 0; m--) {
            uint32_t id = m - 1;
            if (g_active[id] && g_uniq[id] == 0) {
                remove_mod(id);
                dropped = 1;
            }
        }
    }

    /* 2. Exact 1-unique and 2-unique cheaper-prime swaps */
    uint32_t first_inactive = 0;
    for (uint32_t m = g_ncand; m > 0; m--) {
        uint32_t id = m - 1;
        if (!g_active[id]) continue;
        uint32_t uc = g_uniq[id];
        if (uc == 0) {
            remove_mod(id);
            continue;
        }
        if (uc > 2) continue;

        while (first_inactive < id && g_active[first_inactive]) first_inactive++;
        if (first_inactive >= id) continue;

        /* Find the 1 or 2 uniquely covered primes of id */
        uint32_t qs[2];
        uint32_t nq = 0;
        uint32_t r = g_r[id], a = g_resa[id];
        if (id < g_nsmall) {
            for (int32_t k = g_soff[id][a]; k < g_soff[id][a + 1]; k++) {
                int32_t i = g_sidx[id][k];
                if (g_cov[i] == 1 && g_xor[i] == id) {
                    qs[nq++] = g_prime[i];
                    if (nq == uc) break;
                }
            }
        } else {
            uint64_t x = (a & 1u) ? (uint64_t)a : (uint64_t)a + (uint64_t)r;
            uint64_t step = (uint64_t)r << 1;
            for (; x < (uint64_t)g_Q; x += step) {
                int32_t i = g_odd_to_idx[x >> 1];
                if (i >= 0 && g_cov[i] == 1 && g_xor[i] == id) {
                    qs[nq++] = g_prime[i];
                    if (nq == uc) break;
                }
            }
        }

        if (nq == 1) {
            /* Pick smallest inactive modulus < id with r_small != qs[0] */
            for (uint32_t cand = first_inactive; cand < id; cand++) {
                if (!g_active[cand] && g_r[cand] != qs[0]) {
                    uint32_t na = qs[0] % g_r[cand];
                    if (na >= 1) {
                        remove_mod(id);
                        add_mod(cand, na);
                        break;
                    }
                }
            }
        } else if (nq == 2) {
            /* Factor |qs[1] - qs[0]| to find any inactive prime divisor r_small < r */
            uint32_t diff = (qs[1] > qs[0]) ? (qs[1] - qs[0]) : (qs[0] - qs[1]);
            while ((diff & 1u) == 0) diff >>= 1;
            uint32_t tmp = diff;
            uint32_t best_cand = id;
            for (uint32_t d = 3; (uint64_t)d * d <= tmp && d < r; d += 2) {
                if (tmp % d == 0) {
                    while (tmp % d == 0) tmp /= d;
                    if (d != qs[0] && d != qs[1] && d <= g_rmax) {
                        int32_t p_idx = g_odd_to_idx[d >> 1];
                        if (p_idx >= 0 && (uint32_t)p_idx < best_cand && !g_active[p_idx]) {
                            best_cand = (uint32_t)p_idx;
                            break;
                        }
                    }
                }
            }
            if (best_cand == id && tmp >= 3 && tmp < r && tmp <= g_rmax && tmp != qs[0] && tmp != qs[1]) {
                int32_t p_idx = g_odd_to_idx[tmp >> 1];
                if (p_idx >= 0 && (uint32_t)p_idx < best_cand && !g_active[p_idx]) {
                    best_cand = (uint32_t)p_idx;
                }
            }
            if (best_cand < id) {
                uint32_t na = qs[0] % g_r[best_cand];
                if (na >= 1 && (qs[1] % g_r[best_cand]) == na) {
                    remove_mod(id);
                    add_mod(best_cand, na);
                }
            }
        }
    }
    /* Final free-drop pass if swaps created any uniq == 0 */
    for (uint32_t m = g_ncand; m > 0; m--) {
        uint32_t id = m - 1;
        if (g_active[id] && g_uniq[id] == 0) remove_mod(id);
    }
}

/* Setup 16 log-r temperature bands for calibrated heatbath */
static void setup_bands(double c_scale, double min_beta) {
    for (int b = 0; b < NBANDS; b++) {
        double beta = c_scale * g_band_lnr[b];
        if (beta < min_beta) beta = min_beta;
        g_band_beta[b] = beta;
        for (int d = 0; d < BTAB_LEN; d++) {
            g_band_exp[b][d] = exp(-beta * (double)d);
        }
    }
}

static inline double band_exp(int b, int32_t d) {
    if (d < BTAB_LEN) return g_band_exp[b][d];
    return exp(-g_band_beta[b] * (double)d);
}

/* Single heatbath Gibbs move on active modulus m (strict 1 <= a < r) */
static void heatbath_move_active(uint32_t m, int deterministic, rng_t *rng) {
    uint32_t r = g_r[m];
    uint32_t a = g_resa[m];
    uint32_t loss = g_uniq[m];
    if (g_nu == 0 && deterministic) return;

    int b = g_band[m];
    double beta = g_band_beta[b];

    /* Exact frozen short-circuit */
    if (!deterministic && beta * ((double)loss - (double)g_nu) > g_lnr[m] + 38.0) return;

    uint64_t inv = g_inv[m];
    uint32_t nt = 0, gmax = 0;
    for (int32_t u = 0; u < g_nu; u++) {
        uint32_t c = fastmod_u32(g_prime[g_ul[u]], inv, r);
        if (c == 0 || c == a) continue; /* STRICT: forbid a==0 and skip current a */
        uint32_t v = ++g_gcnt[c];
        if (v == 1) g_touched[nt++] = c;
        if (v > gmax) gmax = v;
    }

    uint32_t new_a = a;
    if (deterministic) {
        if (gmax > loss) {
            uint32_t nbest = 0;
            for (uint32_t t = 0; t < nt; t++) {
                uint32_t c = g_touched[t];
                if (g_gcnt[c] == gmax) {
                    nbest++;
                    if (nbest == 1 || (rng_u64(rng) % nbest) == 0) new_a = c;
                }
            }
        }
    } else {
        int32_t dmin = (loss > gmax) ? 0 : (int32_t)loss - (int32_t)gmax;
        double wstay = band_exp(b, -dmin);
        double tot = wstay;
        for (uint32_t t = 0; t < nt; t++) {
            uint32_t c = g_touched[t];
            int32_t dd = (int32_t)loss - (int32_t)g_gcnt[c] - dmin;
            g_hw[t] = band_exp(b, dd);
            tot += g_hw[t];
        }
        int32_t n0 = (int32_t)(r - 2) - (int32_t)nt;
        double w0 = (n0 > 0) ? (double)n0 * band_exp(b, (int32_t)loss - dmin) : 0.0;
        tot += w0;

        double u = rng_f64(rng) * tot;
        if (u >= wstay) {
            u -= wstay;
            uint32_t t = 0;
            for (; t < nt; t++) {
                if (u < g_hw[t]) break;
                u -= g_hw[t];
            }
            if (t < nt) {
                new_a = g_touched[t];
            } else if (n0 > 0) {
                if (4 * n0 >= (int32_t)r) {
                    do { new_a = 1u + (uint32_t)(rng_u64(rng) % (uint64_t)(r - 1)); }
                    while (new_a == a || g_gcnt[new_a] != 0);
                } else {
                    int32_t pick = (int32_t)(rng_u64(rng) % (uint64_t)n0);
                    for (uint32_t c = 1; c < r; c++) {
                        if (c != a && g_gcnt[c] == 0 && pick-- == 0) { new_a = c; break; }
                    }
                }
            }
        }
    }

    for (uint32_t t = 0; t < nt; t++) g_gcnt[g_touched[t]] = 0;

    if (new_a != a) {
        remove_mod(m);
        add_mod(m, new_a);
    }
}

/* Direct Lagrangian ln(r)-weighted heatbath sweep (active ON/OFF + residue + inactive ON) */
static void lagrangian_hb_sweep(double lambda, double beta_lag, uint32_t n_inact_sample, rng_t *rng) {
    /* 1. Visit active moduli in random order */
    uint32_t *act = malloc(sizeof(uint32_t) * (g_nactive + 1));
    uint32_t na = 0;
    for (uint32_t m = 0; m < g_ncand; m++) if (g_active[m]) act[na++] = m;
    for (uint32_t i = na; i > 1; i--) {
        uint32_t j = (uint32_t)(rng_u64(rng) % i);
        uint32_t t = act[i - 1]; act[i - 1] = act[j]; act[j] = t;
    }

    for (uint32_t idx = 0; idx < na; idx++) {
        uint32_t m = act[idx];
        if (!g_active[m]) continue;
        uint32_t r = g_r[m], a = g_resa[m], loss = g_uniq[m];
        double lnr = g_lnr[m];

        /* Skip super-locked small moduli with huge loss */
        if (lambda * ((double)loss - (double)g_nu) > lnr + 30.0 / beta_lag) continue;

        uint64_t inv = g_inv[m];
        uint32_t nt = 0, gmax = 0;
        for (int32_t u = 0; u < g_nu; u++) {
            uint32_t c = fastmod_u32(g_prime[g_ul[u]], inv, r);
            if (c == 0 || c == a) continue;
            uint32_t v = ++g_gcnt[c];
            if (v == 1) g_touched[nt++] = c;
            if (v > gmax) gmax = v;
        }

        double e_stay = 0.0;
        double e_off  = -lnr + lambda * (double)loss;
        double e_min  = (e_off < e_stay) ? e_off : e_stay;
        if (nt > 0) {
            double e_best_c = lambda * ((double)loss - (double)gmax);
            if (e_best_c < e_min) e_min = e_best_c;
        }

        double w_stay = exp(-beta_lag * (e_stay - e_min));
        double w_off  = exp(-beta_lag * (e_off  - e_min));
        double tot = w_stay + w_off;
        for (uint32_t t = 0; t < nt; t++) {
            double ec = lambda * ((double)loss - (double)g_gcnt[g_touched[t]]);
            g_hw[t] = exp(-beta_lag * (ec - e_min));
            tot += g_hw[t];
        }
        int32_t n0 = (int32_t)(r - 2) - (int32_t)nt;
        double w0 = (n0 > 0) ? (double)n0 * exp(-beta_lag * (lambda * (double)loss - e_min)) : 0.0;
        tot += w0;

        double u = rng_f64(rng) * tot;
        int action = 0; /* 0=stay, 1=off, 2=change */
        uint32_t new_a = a;
        if (u < w_stay) {
            action = 0;
        } else if (u < w_stay + w_off) {
            action = 1;
        } else {
            u -= (w_stay + w_off);
            uint32_t t = 0;
            for (; t < nt; t++) {
                if (u < g_hw[t]) break;
                u -= g_hw[t];
            }
            if (t < nt) {
                action = 2; new_a = g_touched[t];
            } else if (n0 > 0) {
                action = 2;
                if (4 * n0 >= (int32_t)r) {
                    do { new_a = 1u + (uint32_t)(rng_u64(rng) % (uint64_t)(r - 1)); }
                    while (new_a == a || g_gcnt[new_a] != 0);
                } else {
                    int32_t pick = (int32_t)(rng_u64(rng) % (uint64_t)n0);
                    for (uint32_t c = 1; c < r; c++) {
                        if (c != a && g_gcnt[c] == 0 && pick-- == 0) { new_a = c; break; }
                    }
                }
            }
        }
        for (uint32_t t = 0; t < nt; t++) g_gcnt[g_touched[t]] = 0;

        if (action == 1) {
            remove_mod(m);
        } else if (action == 2 && new_a != a) {
            remove_mod(m);
            add_mod(m, new_a);
        }
    }
    free(act);

    /* 2. Propose turning ON a sample of inactive moduli when g_nu > 0 */
    if (g_nu == 0 || g_nactive >= g_ncand) return;
    for (uint32_t s = 0; s < n_inact_sample && g_nu > 0; s++) {
        uint32_t m = (uint32_t)(rng_u64(rng) % g_ncand);
        if (g_active[m]) continue;
        uint32_t r = g_r[m];
        uint64_t inv = g_inv[m];
        double lnr = g_lnr[m];

        uint32_t nt = 0, gmax = 0;
        for (int32_t u = 0; u < g_nu; u++) {
            uint32_t c = fastmod_u32(g_prime[g_ul[u]], inv, r);
            if (c == 0) continue;
            uint32_t v = ++g_gcnt[c];
            if (v == 1) g_touched[nt++] = c;
            if (v > gmax) gmax = v;
        }
        if (gmax == 0) {
            for (uint32_t t = 0; t < nt; t++) g_gcnt[g_touched[t]] = 0;
            continue;
        }
        double e_best = lnr - lambda * (double)gmax;
        double e_min = (e_best < 0.0) ? e_best : 0.0;
        double w_off = exp(-beta_lag * (0.0 - e_min));
        double tot = w_off;
        for (uint32_t t = 0; t < nt; t++) {
            double ec = lnr - lambda * (double)g_gcnt[g_touched[t]];
            g_hw[t] = exp(-beta_lag * (ec - e_min));
            tot += g_hw[t];
        }
        double u = rng_f64(rng) * tot;
        uint32_t pick_a = 0;
        if (u >= w_off) {
            u -= w_off;
            for (uint32_t t = 0; t < nt; t++) {
                if (u < g_hw[t]) { pick_a = g_touched[t]; break; }
                u -= g_hw[t];
            }
        }
        for (uint32_t t = 0; t < nt; t++) g_gcnt[g_touched[t]] = 0;
        if (pick_a >= 1) add_mod(m, pick_a);
    }
}

/* Sorting helpers */
typedef struct { uint32_t m; double eff; } meff_t;
static int cmp_meff_asc(const void *p1, const void *p2) {
    double a = ((const meff_t *)p1)->eff;
    double b = ((const meff_t *)p2)->eff;
    return (a < b) ? -1 : (a > b) ? 1 : 0;
}
static int cmp_dbl_asc(const void *p1, const void *p2) {
    double a = *(const double *)p1, b = *(const double *)p2;
    return (a < b) ? -1 : (a > b) ? 1 : 0;
}

/* Fast C increasing_full_cover to compute default rmax = min(Q-1, 3 * rmax_inc) */
static uint32_t compute_default_rmax(uint32_t Q, const uint32_t *primes, uint32_t nP) {
    uint32_t *alive = malloc(sizeof(uint32_t) * nP);
    uint32_t nal = nP;
    memcpy(alive, primes, sizeof(uint32_t) * nP);
    uint32_t max_r_used = 3;
    uint32_t cnt_cap = 4096;
    uint32_t *cnt = calloc(cnt_cap, sizeof(uint32_t));
    for (uint32_t idx = 0; idx < nP && nal > 0; idx++) {
        uint32_t r = primes[idx];
        if (r >= cnt_cap) {
            while (cnt_cap <= r) cnt_cap *= 2;
            free(cnt);
            cnt = calloc(cnt_cap, sizeof(uint32_t));
        }
        uint64_t inv = fastmod_inv(r);
        uint32_t best_h = 0, best_a = 1;
        for (uint32_t i = 0; i < nal; i++) {
            uint32_t c = fastmod_u32(alive[i], inv, r);
            if (c == 0) continue;
            uint32_t v = ++cnt[c];
            if (v > best_h || (v == best_h && c < best_a)) { best_h = v; best_a = c; }
        }
        memset(cnt, 0, sizeof(uint32_t) * r);
        uint32_t nw = 0;
        for (uint32_t i = 0; i < nal; i++) {
            if (fastmod_u32(alive[i], inv, r) != best_a) alive[nw++] = alive[i];
        }
        nal = nw;
        max_r_used = r;
    }
    free(alive);
    free(cnt);
    uint64_t rmax = 3ULL * (uint64_t)max_r_used;
    if (rmax >= (uint64_t)Q) rmax = (uint64_t)(Q - 1);
    return (uint32_t)rmax;
}

static int parse_u32_tok(const char *s, char **end_out, uint32_t *val_out) {
    if (!s || *s == '-' || *s == '+' || !isdigit((unsigned char)*s)) return -1;
    errno = 0;
    char *ep = NULL;
    unsigned long v = strtoul(s, &ep, 10);
    if (ep == s || errno == ERANGE || v > (unsigned long)UINT32_MAX) return -1;
    if (end_out) *end_out = ep;
    *val_out = (uint32_t)v;
    return 0;
}

/* Load init cover from JSON ("classes" or "cover", skipping only parity [2, 0..1]) or text (r:a / r a).
 * Also extracts "Q": <int> into *json_Q_out if present and *json_Q_out == 0. */
static int load_init_cover(
    const char *path, uint32_t **out_r, uint32_t **out_a, uint32_t *out_n, uint32_t *json_Q_out
) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return -1; }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return -1; }
    fseek(f, 0, SEEK_SET);
    char *buf = malloc((size_t)sz + 2);
    size_t nr = fread(buf, 1, (size_t)sz, f);
    buf[nr] = '\0';
    fclose(f);

    uint32_t cap = 4096, n = 0;
    uint32_t *rs = malloc(sizeof(uint32_t) * cap);
    uint32_t *as = malloc(sizeof(uint32_t) * cap);

    char *p = buf;
    while (*p && isspace((unsigned char)*p)) p++;
    if (*p == '{' || *p == '[') {
        if (json_Q_out && *json_Q_out == 0 && *p == '{') {
            char *qk = strstr(p, "\"Q\"");
            if (qk) {
                char *col = strchr(qk + 3, ':');
                if (col) {
                    col++;
                    while (*col && isspace((unsigned char)*col)) col++;
                    if (*col == '-' || isdigit((unsigned char)*col)) {
                        uint32_t qv = 0;
                        if (parse_u32_tok(col, NULL, &qv) != 0) {
                            fprintf(stderr, "ERROR: invalid/out-of-range Q in %s\n", path);
                            free(buf); free(rs); free(as);
                            return -1;
                        }
                        *json_Q_out = qv;
                    }
                }
            }
        }
        char *key = strstr(p, "\"classes\"");
        if (!key) key = strstr(p, "\"cover\"");
        char *arr = key ? strchr(key, '[') : p;
        if (!arr) {
            fprintf(stderr, "ERROR: no classes/cover array in %s\n", path);
            free(buf); free(rs); free(as);
            return -1;
        }
        int depth = 0;
        char *q = arr;
        while (*q) {
            if (*q == '[') {
                depth++;
                if (depth == 2) {
                    q++;
                    while (*q && isspace((unsigned char)*q)) q++;
                    uint32_t rv = 0, av = 0;
                    if (parse_u32_tok(q, &q, &rv) != 0 || (*q != ',' && !isspace((unsigned char)*q))) {
                        fprintf(stderr, "ERROR: invalid/out-of-range modulus token in %s\n", path);
                        free(buf); free(rs); free(as);
                        return -1;
                    }
                    while (*q && (*q == ',' || isspace((unsigned char)*q))) q++;
                    if (parse_u32_tok(q, &q, &av) != 0 || (*q != ']' && *q != ',' && !isspace((unsigned char)*q))) {
                        fprintf(stderr, "ERROR: invalid/out-of-range residue token in %s\n", path);
                        free(buf); free(rs); free(as);
                        return -1;
                    }
                    if (!(rv == 2u && av < 2u)) {
                        if (n == cap) {
                            cap *= 2;
                            rs = realloc(rs, sizeof(uint32_t) * cap);
                            as = realloc(as, sizeof(uint32_t) * cap);
                        }
                        rs[n] = rv;
                        as[n] = av;
                        n++;
                    }
                    continue;
                }
            } else if (*q == ']') {
                depth--;
                if (depth == 0) break;
            }
            q++;
        }
    } else {
        char *tok = strtok(buf, " \t\r\n");
        while (tok) {
            if (strcmp(tok, "COVER") == 0) {
                tok = strtok(NULL, " \t\r\n");
                tok = strtok(NULL, " \t\r\n");
                continue;
            }
            if (strcmp(tok, "BEST") == 0) {
                tok = strtok(NULL, " \t\r\n");
                continue;
            }
            uint32_t rv = 0, av = 0;
            char *colon = strchr(tok, ':');
            if (colon) {
                if (tok[0] == '-' || isdigit((unsigned char)tok[0])) {
                    char *ep1 = NULL, *ep2 = NULL;
                    if (parse_u32_tok(tok, &ep1, &rv) != 0 || ep1 != colon ||
                        parse_u32_tok(colon + 1, &ep2, &av) != 0 || *ep2 != '\0') {
                        fprintf(stderr, "ERROR: invalid/out-of-range r:a token in %s\n", path);
                        free(buf); free(rs); free(as);
                        return -1;
                    }
                    if (!(rv == 2u && av < 2u)) {
                        if (n == cap) {
                            cap *= 2;
                            rs = realloc(rs, sizeof(uint32_t) * cap);
                            as = realloc(as, sizeof(uint32_t) * cap);
                        }
                        rs[n] = rv;
                        as[n] = av;
                        n++;
                    }
                }
            } else if (tok[0] == '-' || isdigit((unsigned char)tok[0])) {
                char *ep1 = NULL, *ep2 = NULL;
                char *tok2 = strtok(NULL, " \t\r\n");
                if (parse_u32_tok(tok, &ep1, &rv) != 0 || *ep1 != '\0' ||
                    !tok2 || parse_u32_tok(tok2, &ep2, &av) != 0 || *ep2 != '\0') {
                    fprintf(stderr, "ERROR: invalid/out-of-range numeric cover pair in %s\n", path);
                    free(buf); free(rs); free(as);
                    return -1;
                }
                if (!(rv == 2u && av < 2u)) {
                    if (n == cap) {
                        cap *= 2;
                        rs = realloc(rs, sizeof(uint32_t) * cap);
                        as = realloc(as, sizeof(uint32_t) * cap);
                    }
                    rs[n] = rv;
                    as[n] = av;
                    n++;
                }
            }
            tok = strtok(NULL, " \t\r\n");
        }
    }
    free(buf);
    *out_r = rs;
    *out_a = as;
    *out_n = n;
    return 0;
}

/* Independent scratch verification before writing output JSON */
static int scratch_verify_snap(const cover_snap_t *S, double *out_sum_lnr) {
    uint8_t *hit = calloc(g_Q, sizeof(uint8_t));
    uint8_t *seen = calloc(g_ncand, sizeof(uint8_t));
    double sum_lnr = 0.0;
    for (uint32_t k = 0; k < S->n; k++) {
        uint32_t m = S->m_id[k];
        uint32_t a = S->a_val[k];
        if (m >= g_ncand || seen[m]) {
            fprintf(stderr, "SCRATCH VERIFY FAIL: bad/duplicate modulus id %u\n", m);
            free(hit); free(seen); return -1;
        }
        seen[m] = 1;
        uint32_t r = g_r[m];
        if (r < 3 || r >= g_Q || a < 1 || a >= r) {
            fprintf(stderr, "SCRATCH VERIFY FAIL: invalid class [%u, %u]\n", r, a);
            free(hit); free(seen); return -1;
        }
        sum_lnr += log((double)r);
        for (uint64_t x = a; x < (uint64_t)g_Q; x += r) hit[x] = 1;
    }
    uint32_t uncov = 0;
    for (uint32_t i = 0; i < g_nP; i++) {
        if (!hit[g_prime[i]]) uncov++;
    }
    free(hit);
    free(seen);
    if (uncov != 0) {
        fprintf(stderr, "SCRATCH VERIFY FAIL: %u odd primes < %u uncovered!\n", uncov, g_Q);
        return -1;
    }
    *out_sum_lnr = sum_lnr;
    return 0;
}

static void format_json_stream(FILE *f, const cover_snap_t *S, double sum_lnr, uint64_t seed, int steps) {
    double mc_digits = sum_lnr / log(10.0);
    fprintf(f, "{\n");
    fprintf(f, "  \"Q\": %u,\n", g_Q);
    fprintf(f, "  \"classes\": [");
    for (uint32_t k = 0; k < S->n; k++) {
        fprintf(f, "%s[%u, %u]", k ? ", " : "", g_r[S->m_id[k]], S->a_val[k]);
    }
    fprintf(f, "],\n");
    fprintf(f, "  \"num_classes\": %u,\n", S->n);
    fprintf(f, "  \"sum_ln_r\": %.9f,\n", sum_lnr);
    fprintf(f, "  \"Mc_digits\": %.6f,\n", mc_digits);
    fprintf(f, "  \"uncovered\": 0,\n");
    fprintf(f, "  \"seed\": %llu,\n", (unsigned long long)seed);
    fprintf(f, "  \"steps\": %d\n", steps);
    fprintf(f, "}\n");
}

static int write_output_json(const char *out_path, const cover_snap_t *S, double sum_lnr, uint64_t seed, int steps) {
    if (!out_path || strcmp(out_path, "-") == 0) {
        format_json_stream(stdout, S, sum_lnr, seed, steps);
        fflush(stdout);
        return 0;
    }
    size_t tlen = strlen(out_path) + 32;
    char *tmp_path = malloc(tlen);
    snprintf(tmp_path, tlen, "%s.tmp.%ld", out_path, (long)getpid());
    FILE *f = fopen(tmp_path, "w");
    if (!f) { perror(tmp_path); free(tmp_path); return -1; }
    format_json_stream(f, S, sum_lnr, seed, steps);
    if (fclose(f) != 0) { perror("fclose"); free(tmp_path); return -1; }
    if (rename(tmp_path, out_path) != 0) { perror("rename"); free(tmp_path); return -1; }
    free(tmp_path);
    return 0;
}

static void print_usage(const char *prog, FILE *stream) {
    fprintf(stream,
        "Usage: %s --Q <int> [--rmax <int>] [--init-cover <path>] [--steps <int>]\n"
        "          [--hb-sweeps <int>] [--seed <u64>] [--threads <int>] [--out <out.json>]\n",
        prog);
}

int main(int argc, char **argv) {
    uint32_t Q = 0, rmax_arg = 0;
    const char *init_path = NULL;
    const char *out_path = NULL;
    int steps = 20, hb_sweeps = 20;
    int nthreads = 2;
    const char *env_omp = getenv("OMP_NUM_THREADS");
    if (env_omp && atoi(env_omp) >= 1) nthreads = atoi(env_omp);
    uint64_t seed = 1ULL;

    for (int i = 1; i < argc; i++) {
        if ((strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0)) {
            print_usage(argv[0], stdout);
            return 0;
        } else if ((strcmp(argv[i], "--Q") == 0 || strcmp(argv[i], "-Q") == 0) && i + 1 < argc) {
            char *ep = NULL;
            if (parse_u32_tok(argv[++i], &ep, &Q) != 0 || *ep != '\0') {
                fprintf(stderr, "Invalid/out-of-range --Q value: %s\n", argv[i]);
                return 1;
            }
        } else if (strcmp(argv[i], "--rmax") == 0 && i + 1 < argc) {
            char *ep = NULL;
            if (parse_u32_tok(argv[++i], &ep, &rmax_arg) != 0 || *ep != '\0') {
                fprintf(stderr, "Invalid/out-of-range --rmax value: %s\n", argv[i]);
                return 1;
            }
        } else if (strcmp(argv[i], "--init-cover") == 0 && i + 1 < argc) {
            init_path = argv[++i];
        } else if (strcmp(argv[i], "--steps") == 0 && i + 1 < argc) {
            steps = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--hb-sweeps") == 0 && i + 1 < argc) {
            hb_sweeps = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            seed = strtoull(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--threads") == 0 && i + 1 < argc) {
            nthreads = atoi(argv[++i]);
        } else if ((strcmp(argv[i], "--out") == 0 || strcmp(argv[i], "-o") == 0 ||
                    strcmp(argv[i], "--output") == 0 || strcmp(argv[i], "--json-out") == 0) && i + 1 < argc) {
            out_path = argv[++i];
        } else {
            fprintf(stderr, "Unknown/incomplete arg: %s\n", argv[i]);
            print_usage(argv[0], stderr);
            return 1;
        }
    }

    /* Load init cover early if given (also allows extracting Q if --Q omitted) */
    uint32_t *init_r = NULL, *init_a = NULL, init_n = 0, init_max_r = 0;
    if (init_path) {
        if (load_init_cover(init_path, &init_r, &init_a, &init_n, &Q) != 0) {
            return 1;
        }
    }

    if (Q < 6 || steps < 0) {
        free(init_r); free(init_a);
        print_usage(argv[0], stderr);
        return 1;
    }
    if (nthreads < 1) nthreads = 1;
#ifdef _OPENMP
    omp_set_num_threads(nthreads);
#endif

    double t_start = now_sec();
    g_Q = Q;

    /* 1. Sieve odd primes 3 <= q < Q */
    uint8_t *comp = calloc((size_t)Q + 1, sizeof(uint8_t));
    comp[0] = comp[1] = 1;
    for (uint64_t i = 2; i * i < (uint64_t)Q; i++) {
        if (!comp[i]) {
            for (uint64_t j = i * i; j < (uint64_t)Q; j += i) comp[j] = 1;
        }
    }
    g_odd_to_idx = malloc(sizeof(int32_t) * ((size_t)(Q / 2) + 2));
    for (size_t i = 0; i < (size_t)(Q / 2) + 2; i++) g_odd_to_idx[i] = -1;
    double denom = log((double)Q) - 1.2;
    if (denom < 0.5) denom = 0.5;
    uint32_t p_cap = (uint32_t)(Q / denom) + 1024;
    if (p_cap > Q) p_cap = Q;
    g_prime = malloc(sizeof(uint32_t) * p_cap);
    g_nP = 0;
    for (uint32_t q = 3; q < Q; q += 2) {
        if (!comp[q]) {
            if (g_nP == p_cap) { p_cap *= 2; g_prime = realloc(g_prime, sizeof(uint32_t) * p_cap); }
            g_odd_to_idx[q >> 1] = (int32_t)g_nP;
            g_prime[g_nP++] = q;
        }
    }
    free(comp);

    /* Validate init cover moduli strictly (reject even, <3, >=Q, composite, bad residue) */
    if (init_path) {
        for (uint32_t k = 0; k < init_n; k++) {
            uint32_t rv = init_r[k], av = init_a[k];
            if (rv < 3u || (rv & 1u) == 0) {
                fprintf(stderr, "ERROR: init modulus %u is not an odd prime >= 3\n", rv);
                free(init_r); free(init_a); free_all_globals();
                return 1;
            }
            if (rv >= Q) {
                fprintf(stderr, "ERROR: init modulus %u >= Q=%u\n", rv, Q);
                free(init_r); free(init_a); free_all_globals();
                return 1;
            }
            if (g_odd_to_idx[rv >> 1] < 0) {
                fprintf(stderr, "ERROR: init modulus %u is composite (not prime)\n", rv);
                free(init_r); free(init_a); free_all_globals();
                return 1;
            }
            if (av >= rv) {
                fprintf(stderr, "ERROR: init residue %u out of range for modulus %u\n", av, rv);
                free(init_r); free(init_a); free_all_globals();
                return 1;
            }
            if (rv > init_max_r) init_max_r = rv;
        }
    }

    if (rmax_arg == 0) {
        g_rmax = compute_default_rmax(Q, g_prime, g_nP);
    } else {
        g_rmax = (rmax_arg >= Q) ? (Q - 1) : rmax_arg;
    }
    if (init_max_r > g_rmax) g_rmax = init_max_r;

    /* Candidate moduli = all odd primes 3 <= r <= g_rmax (strictly < Q) */
    g_ncand = 0;
    while (g_ncand < g_nP && g_prime[g_ncand] <= g_rmax) g_ncand++;
    if (g_ncand == 0) {
        fprintf(stderr, "ERROR: zero candidate moduli <= rmax=%u for Q=%u\n", g_rmax, Q);
        free(init_r); free(init_a); free_all_globals();
        return 1;
    }

    g_r      = malloc(sizeof(uint32_t) * g_ncand);
    g_inv    = malloc(sizeof(uint64_t) * g_ncand);
    g_lnr    = malloc(sizeof(double)   * g_ncand);
    g_band   = malloc(sizeof(uint8_t)  * g_ncand);
    g_active = calloc(g_ncand, sizeof(uint8_t));
    g_resa   = calloc(g_ncand, sizeof(uint32_t));
    g_uniq   = calloc(g_ncand, sizeof(uint32_t));

    double lnr_min = log(3.0);
    double lnr_max = log((double)g_prime[g_ncand - 1]);
    double lnr_span = (lnr_max > lnr_min) ? (lnr_max - lnr_min) : 1.0;
    for (int b = 0; b < NBANDS; b++) {
        g_band_lnr[b] = lnr_min + ((double)b + 0.5) * lnr_span / (double)NBANDS;
    }

    g_nsmall = 0;
    for (uint32_t m = 0; m < g_ncand; m++) {
        uint32_t r = g_prime[m];
        g_r[m] = r;
        g_inv[m] = fastmod_inv(r);
        g_lnr[m] = log((double)r);
        int b = (int)(((g_lnr[m] - lnr_min) / lnr_span) * (double)NBANDS);
        if (b < 0) b = 0;
        if (b >= NBANDS) b = NBANDS - 1;
        g_band[m] = (uint8_t)b;
        if (r <= SMALL_R_LIM && g_nsmall < MAX_SMALL) g_nsmall++;
    }

    /* Build small-prime CSR cache for r <= 127 */
    for (uint32_t m = 0; m < g_nsmall; m++) {
        uint32_t r = g_r[m];
        uint64_t inv = g_inv[m];
        g_soff[m] = calloc((size_t)(r + 2), sizeof(int32_t));
        g_sidx[m] = malloc(sizeof(int32_t) * g_nP);
        for (uint32_t i = 0; i < g_nP; i++) g_soff[m][fastmod_u32(g_prime[i], inv, r) + 1]++;
        for (uint32_t c = 0; c <= r; c++) g_soff[m][c + 1] += g_soff[m][c];
        int32_t *pos = malloc(sizeof(int32_t) * (r + 1));
        memcpy(pos, g_soff[m], sizeof(int32_t) * (r + 1));
        for (uint32_t i = 0; i < g_nP; i++) {
            uint32_t rem = fastmod_u32(g_prime[i], inv, r);
            g_sidx[m][pos[rem]++] = (int32_t)i;
        }
        free(pos);
    }

    /* Allocate core tracking & scratch arrays */
    g_cov       = malloc(sizeof(uint16_t) * g_nP);
    g_xor       = malloc(sizeof(uint32_t) * g_nP);
    g_ul        = malloc(sizeof(int32_t)  * g_nP);
    g_upos      = malloc(sizeof(int32_t)  * g_nP);
    g_up_primes = malloc(sizeof(uint32_t) * g_nP);
    g_heap      = malloc(sizeof(hnode_t)  * (g_ncand + 1));
    g_gcnt      = calloc((size_t)(g_rmax + 2), sizeof(uint32_t));
    g_touched   = malloc(sizeof(uint32_t) * (size_t)(g_rmax + 2));
    g_hw        = malloc(sizeof(double)   * (size_t)(g_rmax + 2));

    cover_snap_t best_snap = { 0, malloc(sizeof(uint32_t) * g_ncand), malloc(sizeof(uint32_t) * g_ncand), 1e30 };
    cover_snap_t work_snap = { 0, malloc(sizeof(uint32_t) * g_ncand), malloc(sizeof(uint32_t) * g_ncand), 1e30 };
    cover_snap_t hb_min_snap = { 0, malloc(sizeof(uint32_t) * g_ncand), malloc(sizeof(uint32_t) * g_ncand), 1e30 };

    /* Stage 0: Initialize cover */
    reset_state();
    if (init_path) {
        for (uint32_t k = 0; k < init_n; k++) {
            int32_t m_idx = g_odd_to_idx[init_r[k] >> 1];
            if (m_idx < 0 || (uint32_t)m_idx >= g_ncand) {
                fprintf(stderr, "ERROR: init modulus %u is not an odd prime <= rmax=%u\n", init_r[k], g_rmax);
                free(init_r); free(init_a);
                free_snap(&best_snap); free_snap(&work_snap); free_snap(&hb_min_snap);
                free_all_globals();
                return 1;
            }
            if (g_active[m_idx]) {
                fprintf(stderr, "ERROR: duplicate init modulus %u\n", init_r[k]);
                free(init_r); free(init_a);
                free_snap(&best_snap); free_snap(&work_snap); free_snap(&hb_min_snap);
                free_all_globals();
                return 1;
            }
            uint32_t a = init_a[k];
            if (a < 1 || a >= init_r[k]) a = 1u; /* repair tiny-Q desert.py a==0 into strict 1 <= a < r */
            add_mod((uint32_t)m_idx, a);
        }
        free(init_r); init_r = NULL;
        free(init_a); init_a = NULL;
        if (g_nu > 0) {
            if (repair_to_zero(nthreads) != 0) {
                fprintf(stderr, "ERROR: failed to repair init cover with rmax=%u\n", g_rmax);
                free_snap(&best_snap); free_snap(&work_snap); free_snap(&hb_min_snap);
                free_all_globals();
                return 1;
            }
        }
    } else {
        if (repair_to_zero(nthreads) != 0) {
            fprintf(stderr, "ERROR: failed to build initial cover with rmax=%u\n", g_rmax);
            free_snap(&best_snap); free_snap(&work_snap); free_snap(&hb_min_snap);
            free_all_globals();
            return 1;
        }
    }
    polish_free_drops_and_swaps();
    save_snap(&best_snap);
    save_snap(&work_snap);

    double init_digits = best_snap.sum_lnr / log(10.0);
    fprintf(stderr, "[INIT] Q=%u nP=%u rmax=%u n_cand=%u | classes=%u sum_ln_r=%.4f Mc_digits=%.4f (%.2fs)\n",
            g_Q, g_nP, g_rmax, g_ncand, best_snap.n, best_snap.sum_lnr, init_digits, now_sec() - t_start);

    rng_t rng = { seed ? seed * 0x9E3779B97F4A7C15ULL : 0xDEADBEEFCAFEBABEULL };
    for (int i = 0; i < 16; i++) rng_u64(&rng);

    meff_t *meff = malloc(sizeof(meff_t) * g_ncand);
    uint32_t *act_list = malloc(sizeof(uint32_t) * g_ncand);
    double *ratios = malloc(sizeof(double) * g_ncand);

    /* Stage 2: Main Outer Optimization Loop (DHR + Lagrangian ln(r) Heatbath) */
    for (int step = 0; step < steps; step++) {
        double t_step = now_sec();
        restore_snap(&best_snap);

        int is_lagrangian = (steps >= 4) && ((step % 4) == 3);
        if (!is_lagrangian) {
            /* Efficiency-ordered Destroy-Heatbath-Repair (DHR) */
            uint32_t na = 0;
            for (uint32_t m = 0; m < g_ncand; m++) {
                if (g_active[m]) {
                    double jitter = 0.75 * rng_f64(&rng);
                    meff[na].m = m;
                    meff[na].eff = ((double)g_uniq[m] + jitter) / g_lnr[m];
                    na++;
                }
            }
            if (na == 0) continue;
            qsort(meff, na, sizeof(meff_t), cmp_meff_asc);

            double frac_lo = (step < steps / 2) ? 0.14 : 0.05;
            double frac_hi = (step < steps / 2) ? 0.34 : 0.24;
            double frac = frac_lo + (frac_hi - frac_lo) * rng_f64(&rng);
            uint32_t K = (uint32_t)(frac * (double)na);
            if (K < 5) K = 5;
            if (K >= na) K = na / 2;
            if (K == 0) K = 1;

            for (uint32_t k = 0; k < K; k++) remove_mod(meff[k].m);

            /* Build list of remaining active moduli for heatbath */
            uint32_t rem_na = 0;
            for (uint32_t m = 0; m < g_ncand; m++) if (g_active[m]) act_list[rem_na++] = m;

            int32_t min_nu = g_nu;
            save_snap(&hb_min_snap);

            double c0 = 0.38, c1 = 1.32;
            int ns = hb_sweeps > 0 ? hb_sweeps : 1;
            for (int sw = 0; sw < ns + 2; sw++) {
                int det = (sw >= ns);
                if (!det) {
                    double t_frac = (ns > 1) ? (double)sw / (double)(ns - 1) : 1.0;
                    double c_scale = c0 * pow(c1 / c0, t_frac);
                    double min_b = 2.0 + 6.0 * t_frac;
                    setup_bands(c_scale, min_b);
                }
                for (uint32_t i = rem_na; i > 1; i--) {
                    uint32_t j = (uint32_t)(rng_u64(&rng) % i);
                    uint32_t t = act_list[i - 1]; act_list[i - 1] = act_list[j]; act_list[j] = t;
                }
                for (uint32_t i = 0; i < rem_na; i++) {
                    heatbath_move_active(act_list[i], det, &rng);
                }
                if (g_nu < min_nu) {
                    min_nu = g_nu;
                    save_snap(&hb_min_snap);
                }
            }

            restore_snap(&hb_min_snap);
            for (uint32_t m = 0; m < g_ncand; m++) if (g_active[m] && g_uniq[m] == 0) remove_mod(m);
            int32_t pre_rep_nu = g_nu;
            if (repair_to_zero(nthreads) != 0) {
                fprintf(stderr, "WARN: repair failed at step %d, restoring best\n", step);
                continue;
            }
            polish_free_drops_and_swaps();

            if (g_sum_lnr < best_snap.sum_lnr - 1e-9) {
                save_snap(&best_snap);
                fprintf(stderr, "[STEP %2d/%d DHR  K=%4u] NEW BEST! pre_nu=%d -> classes=%u Mc_digits=%.4f (delta=%.2fd, %.2fs)\n",
                        step + 1, steps, K, pre_rep_nu, best_snap.n, best_snap.sum_lnr / log(10.0),
                        (best_snap.sum_lnr / log(10.0)) - init_digits, now_sec() - t_step);
            } else {
                fprintf(stderr, "[STEP %2d/%d DHR  K=%4u] cur=%.4fd (best=%.4fd, pre_nu=%d, %.2fs)\n",
                        step + 1, steps, K, g_sum_lnr / log(10.0), best_snap.sum_lnr / log(10.0),
                        pre_rep_nu, now_sec() - t_step);
            }
        } else {
            /* Direct Lagrangian ln(r)-weighted heatbath */
            uint32_t nr = 0;
            for (uint32_t m = 0; m < g_ncand; m++) {
                if (g_active[m]) {
                    uint32_t uc = g_uniq[m] ? g_uniq[m] : 1;
                    ratios[nr++] = g_lnr[m] / (double)uc;
                }
            }
            if (nr == 0) continue;
            qsort(ratios, nr, sizeof(double), cmp_dbl_asc);
            uint32_t lo_idx = (uint32_t)(0.85 * (double)nr);
            uint32_t mid_idx = lo_idx + (nr - lo_idx) / 2;
            if (mid_idx >= nr) mid_idx = nr - 1;
            double lam_bar = ratios[mid_idx];
            double alpha = 0.88 + 0.16 * rng_f64(&rng);
            double lambda = alpha * lam_bar;

            int n_lag_sw = 3;
            uint32_t sample_inact = (g_ncand - g_nactive) < 2500 ? (g_ncand - g_nactive) : 2500;
            for (int sw = 0; sw < n_lag_sw; sw++) {
                double beta_lag = 0.90 + 0.40 * (double)sw;
                lagrangian_hb_sweep(lambda, beta_lag, sample_inact, &rng);
            }
            uint32_t rem_na = 0;
            for (uint32_t m = 0; m < g_ncand; m++) if (g_active[m]) act_list[rem_na++] = m;
            for (int sw = 0; sw < 2; sw++) {
                for (uint32_t i = 0; i < rem_na; i++) heatbath_move_active(act_list[i], 1, &rng);
            }
            int32_t pre_rep_nu = g_nu;
            if (repair_to_zero(nthreads) != 0) continue;
            polish_free_drops_and_swaps();

            if (g_sum_lnr < best_snap.sum_lnr - 1e-9) {
                save_snap(&best_snap);
                fprintf(stderr, "[STEP %2d/%d LAG lam=%.2f] NEW BEST! pre_nu=%d -> classes=%u Mc_digits=%.4f (delta=%.2fd, %.2fs)\n",
                        step + 1, steps, lambda, pre_rep_nu, best_snap.n, best_snap.sum_lnr / log(10.0),
                        (best_snap.sum_lnr / log(10.0)) - init_digits, now_sec() - t_step);
            } else {
                fprintf(stderr, "[STEP %2d/%d LAG lam=%.2f] cur=%.4fd (best=%.4fd, pre_nu=%d, %.2fs)\n",
                        step + 1, steps, lambda, g_sum_lnr / log(10.0), best_snap.sum_lnr / log(10.0),
                        pre_rep_nu, now_sec() - t_step);
            }
        }
    }

    /* Stage 3: Independent final scratch verification & atomic JSON output */
    double verified_sum_lnr = 0.0;
    if (scratch_verify_snap(&best_snap, &verified_sum_lnr) != 0) {
        fprintf(stderr, "FATAL: final scratch verification failed!\n");
        free(meff); free(act_list); free(ratios);
        free_snap(&best_snap); free_snap(&work_snap); free_snap(&hb_min_snap);
        free_all_globals();
        return 3;
    }

    if (write_output_json(out_path, &best_snap, verified_sum_lnr, seed, steps) != 0) {
        free(meff); free(act_list); free(ratios);
        free_snap(&best_snap); free_snap(&work_snap); free_snap(&hb_min_snap);
        free_all_globals();
        return 2;
    }

    double total_sec = now_sec() - t_start;
    double final_digits = verified_sum_lnr / log(10.0);
    FILE *done_stream = (!out_path || strcmp(out_path, "-") == 0) ? stderr : stdout;
    fprintf(done_stream,
            "DONE Q=%u rmax=%u classes=%u sum_ln_r=%.6f Mc_digits=%.4f (init=%.4f, delta=%.4f, %.2f%%) uncovered=0 elapsed=%.2fs out=%s\n",
            g_Q, g_rmax, best_snap.n, verified_sum_lnr, final_digits, init_digits,
            final_digits - init_digits, 100.0 * (final_digits - init_digits) / init_digits,
            total_sec, out_path ? out_path : "-");

    free(meff);
    free(act_list);
    free(ratios);
    free_snap(&best_snap);
    free_snap(&work_snap);
    free_snap(&hb_min_snap);
    free_all_globals();
    return 0;
}
