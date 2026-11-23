/* CPU build of the batch kernels: gsieve_cpu.cpp's runtime and wrappers (count, select, rows, finalize ...), gbig_kernels.cuh and gbatch_kernels.cuh on top.
   Compile with -DKLOG=<KS_LOG> -DKS_LOG=<same> -DTILE_LOG -DLLOG -DNTHREADS -DRG -DPPT. */
#include "gsieve_cpu.cpp"
#include "gbig_kernels.cuh"
#include "gbatch_kernels.cuh"
#include "ghead_kernels.cuh"

struct gen_args { const u32 *U; const uint4 *TAB; int nP, row0, nrows; u32 cap; u32 *gcnt; u32 *bins; };
static void gen_tramp(void *a) { gen_args *x = (gen_args *)a; gbig_gen(x->U, x->TAB, x->nP, x->row0, x->nrows, x->cap, x->gcnt, x->bins); }
extern "C" void cpu_gen(const u32 *U, const uint4 *TAB, int nP, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins, int threads) {
    gen_args a{U, TAB, nP, row0, nrows, cap, gcnt, bins};
    const int per = threads * PPT;
    run_grid((nP + per - 1) / per, threads, 0, gen_tramp, &a);
}
struct gen_st_args { const u32 *U; const uint4 *TAB; const int *pstart; int row0, nrows; u32 cap; u32 *gcnt; u32 *bins; };
static void gen_st_tramp(void *a) { gen_st_args *x = (gen_st_args *)a; gbig_gen_st(x->U, x->TAB, x->pstart, x->row0, x->nrows, x->cap, x->gcnt, x->bins); }
extern "C" void cpu_gen_st(const u32 *U, const uint4 *TAB, const int *pstart, int nchunks, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins, int threads) {
    gen_st_args a{U, TAB, pstart, row0, nrows, cap, gcnt, bins};
    const int ny = (nrows + RCTA - 1) / RCTA;
#if GEN_ORDER
    for (int c = 0; c < nchunks; c++) {                                 /* grid (row slices, chunks): blockIdx.x = slice, blockIdx.y = chunk */
        blockIdx.y = c;
        run_grid(ny, threads, 0, gen_st_tramp, &a);
    }
#else
    for (int y = 0; y < ny; y++) {
        blockIdx.y = y;
        run_grid(nchunks, threads, 0, gen_st_tramp, &a);
    }
#endif
}
struct ptiles_args { const u32 *S, *INV, *INVP, *N0M; u64 k0; int nS; uint4 *TABT; };
static void ptiles_tramp(void *a) { ptiles_args *x = (ptiles_args *)a; s200g_prep_tiles(x->S, x->INV, x->INVP, x->N0M, x->k0, x->nS, x->TABT); }
extern "C" void cpu_prep_tiles(const u32 *S, const u32 *INV, const u32 *INVP, const u32 *N0M, u64 k0, int nS, uint4 *TABT, int threads) {
    ptiles_args a{S, INV, INVP, N0M, k0, nS, TABT};
    run_grid((nS + threads - 1) / threads, threads, 0, ptiles_tramp, &a);
}
/* the tile kernel has a 2-D grid: the emulation runs the CTAs one after the other */
struct tile_args { const u32 *U; int row0; const uint4 *TABT; int nS; const u32 *gcnt, *bins; u32 cap; u32 *bits; };
static void tile_tramp(void *a) { tile_args *x = (tile_args *)a; s200g_tile(x->U, x->row0, x->TABT, x->nS, x->gcnt, x->bins, x->cap, x->bits); }
extern "C" void cpu_tile(int nrows, const u32 *U, int row0, const uint4 *TABT, int nS, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits, int threads) {
    tile_args a{U, row0, TABT, nS, gcnt, bins, cap, bits};
    for (unsigned ty = 0; ty < NTILES; ty++) {
        blockIdx.y = ty;
        run_grid(nrows, threads, (size_t)TILE_WORDS * 4, tile_tramp, &a);
    }
}
#if TILE_PIPE
static void tile_pipe_tramp(void *a) { tile_args *x = (tile_args *)a; s200g_tile_pipe(x->U, x->row0, x->TABT, x->nS, x->gcnt, x->bins, x->cap, x->bits); }
extern "C" void cpu_tile_pipe(int nrows, const u32 *U, int row0, const uint4 *TABT, int nS, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits, int threads) {
    tile_args a{U, row0, TABT, nS, gcnt, bins, cap, bits};
    g_bar1_n = TILE_PIPE_AT;
    for (unsigned ty = 0; ty < NTILES; ty++) {
        blockIdx.y = ty;
        run_grid(nrows, threads, (size_t)(TILE_WORDS + 2 * TILE_PIPE_CH) * 4, tile_pipe_tramp, &a);
    }
    g_bar1_n = 0;
}
#endif
extern "C" int cpu_ntiles() { return NTILES; }
extern "C" int cpu_tile_words() { return TILE_WORDS; }
extern "C" int cpu_nbins() { return NBINS; }
struct hgen_args { const u32 *U; const uint4 *TAB; int nP, row0, nrows; u32 cap; u32 *gcnt; u32 *bins; };
static void hgen_tramp(void *a) { hgen_args *x = (hgen_args *)a; ghead_gen(x->U, x->TAB, x->nP, x->row0, x->nrows, x->cap, x->gcnt, x->bins); }
extern "C" void cpu_head_gen(const u32 *U, const uint4 *TAB, int nP, int row0, int nrows, u32 cap, u32 *gcnt, u32 *bins, int threads) {
    hgen_args a{U, TAB, nP, row0, nrows, cap, gcnt, bins};
    const int per = threads * HEAD_PPT;
    run_grid((nP + per - 1) / per, threads, 0, hgen_tramp, &a);
}
struct happly_args { int row0; const u32 *gcnt, *bins; u32 cap; u32 *bits; const int *slot_of; u32 *dcnt; };
static void happly_tramp(void *a) { happly_args *x = (happly_args *)a; ghead_apply(x->row0, x->gcnt, x->bins, x->cap, x->bits, x->slot_of, x->dcnt); }
/* grid (nrows, NTILES): the emulation runs the tiles one after the other, like the tile kernel's */
extern "C" void cpu_head_apply(int nrows, int row0, const u32 *gcnt, const u32 *bins, u32 cap, u32 *bits, const int *slot_of, u32 *dcnt, int threads) {
    happly_args a{row0, gcnt, bins, cap, bits, slot_of, dcnt};
    for (unsigned ty = 0; ty < NTILES; ty++) {
        blockIdx.y = ty;
        run_grid(nrows, threads, (size_t)TILE_WORDS * 4, happly_tramp, &a);
    }
}
