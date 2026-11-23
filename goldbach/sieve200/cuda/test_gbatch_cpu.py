#!/usr/bin/env python3
"""gbatch.py's BatchFeeder (a batch of 2^ks_log members: the primes above `split` through gbig_gen, the rest in the tile kernel, then GpuFeeder's count / select / rows) run on the CPU:
cupy is replaced by numpy plus a RawModule whose kernels are the pthread emulation (gbatch_cpu.cpp).  The result must be identical to sieve200's CPU Feeder over the same primes
(counts, selected members, their rows, the statistics), for several geometries and keep fractions.

    python3 test_gbatch_cpu.py [--rows 40]
"""
import argparse, ctypes, json, os, re, subprocess, sys, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gsieve


def build(ks, llog, nth, tile, rg, ppt, stage_cap=8192, rcta=2, unroll=1, pack=0, hoist=0, gunroll=1, flush2=0, order=0, pipe=None, lean=(0, 0, 0)):
    out = os.path.join(HERE, f"libgbatch_cpu_{ks}_{llog}_{nth}_{tile}_{rg}_{ppt}_{stage_cap}_{rcta}" + (f"_u{unroll}" if unroll > 1 else "") + ("_pk" if pack else "") + ("_gh" if hoist else "") + (f"_gu{gunroll}" if gunroll > 1 else "") + ("_f2" if flush2 else "") + ("_go" if order else "") + (f"_tp{pipe[0]}x{pipe[1]}" if pipe else "") + ("_ln%d%d%d" % tuple(lean) if any(lean) else "") + ".so")
    srcs = [os.path.join(HERE, f) for f in ("gbatch_cpu.cpp", "gsieve_cpu.cpp", "gsieve_kernels.cuh", "gbig_kernels.cuh", "gbatch_kernels.cuh", "ghead_kernels.cuh")]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in srcs):
        subprocess.check_call(["g++", "-O2", "-std=c++17", f"-DKLOG={ks}", f"-DKS_LOG={ks}", f"-DTILE_LOG={tile}", f"-DLLOG={llog}", f"-DNTHREADS={nth}", f"-DRG={rg}", f"-DPPT={ppt}", f"-DSTAGE_CAP={stage_cap}", f"-DRCTA={rcta}", f"-DRCTA_LOG={rcta.bit_length() - 1}", f"-DTILE_UNROLL={unroll}", f"-DBIN_PACK={pack}", f"-DGEN_HOIST={hoist}", f"-DGEN_UNROLL={gunroll}", f"-DGEN_FLUSH2={flush2}", f"-DGEN_ORDER={order}", f"-DGEN_SCAN2={lean[0]}", f"-DGEN_RESV_LATE={lean[1]}", f"-DGEN_MINRED={lean[2]}", *((f"-DTILE_PIPE=1", f"-DTILE_PIPE_AT={pipe[0]}", f"-DTILE_PIPE_CH={pipe[1]}") if pipe else ()),
                               "-DMAXKEEP_SORT=8192u", "-DS200G_UNROLL=1", "-Wno-unused-variable", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, srcs[0], "-lpthread"])
    lib = ctypes.CDLL(out)
    vp = ctypes.c_void_p
    lib.cpu_sieve.argtypes = [ctypes.c_int, vp, vp, vp, vp, vp, vp, ctypes.c_int, vp]
    lib.cpu_count.argtypes = [vp, ctypes.c_int, vp]
    lib.cpu_select.argtypes = [vp, ctypes.c_int, ctypes.c_int, ctypes.c_double, vp, vp]
    lib.cpu_rows.argtypes = [vp, ctypes.c_int, vp, vp, ctypes.c_int, vp]
    lib.cpu_n0m.argtypes = [vp, ctypes.c_int, vp, vp, ctypes.c_int, vp]
    lib.cpu_km.argtypes = [vp, ctypes.c_uint64, ctypes.c_int, vp]
    lib.cpu_finalize.argtypes = [vp, ctypes.c_int, ctypes.c_int, ctypes.c_uint64, vp, vp, vp, vp, vp]
    lib.cpu_rows2.argtypes = [vp, ctypes.c_int, vp, vp, ctypes.c_int, vp]
    lib.cpu_fin_sums.argtypes = [vp, ctypes.c_int, vp, ctypes.c_int]
    lib.cpu_fin_main.argtypes = [vp, ctypes.c_int, ctypes.c_int, ctypes.c_uint64, vp, vp, vp, vp, vp, vp]
    lib.cpu_prep.argtypes = [vp, vp, vp, vp, ctypes.c_uint64, ctypes.c_int, vp]
    lib.cpu_prep_tiles.argtypes = [vp, vp, vp, vp, ctypes.c_uint64, ctypes.c_int, vp, ctypes.c_int]
    lib.cpu_tile.argtypes = [ctypes.c_int, vp, ctypes.c_int, vp, ctypes.c_int, vp, vp, ctypes.c_uint32, vp, ctypes.c_int]
    if pipe:
        lib.cpu_tile_pipe.argtypes = [ctypes.c_int, vp, ctypes.c_int, vp, ctypes.c_int, vp, vp, ctypes.c_uint32, vp, ctypes.c_int]
    lib.cpu_gen.argtypes = [vp, vp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, vp, vp, ctypes.c_int]
    lib.cpu_gen_st.argtypes = [vp, vp, vp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, vp, vp, ctypes.c_int]
    lib.cpu_head_gen.argtypes = [vp, vp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, vp, vp, ctypes.c_int]
    lib.cpu_head_apply.argtypes = [ctypes.c_int, ctypes.c_int, vp, vp, ctypes.c_uint32, vp, vp, vp, ctypes.c_int]
    return lib


class _Fn(TG._Fn):
    order = False                                                       # GEN_ORDER: gbig_gen_st's grid is (row slices, chunks)

    def __call__(self, grid, block, args, shared_mem=0):
        P = lambda a: a.ctypes.data
        L = self.lib
        if self.name == "s200g_prep_tiles":
            S, INV, INVP, N0M, k0, nS, tab = args
            L.cpu_prep_tiles(P(S), P(INV), P(INVP), P(N0M), int(k0), int(nS), P(tab), int(block[0]))
        elif self.name == "s200g_tile":
            U, row0, tabt, nS, gcnt, bins, cap, bits = args
            L.cpu_tile(int(grid[0]), P(U), int(row0), P(tabt), int(nS), P(gcnt), P(bins), int(cap), P(bits), int(block[0]))
        elif self.name == "s200g_tile_pipe":
            U, row0, tabt, nS, gcnt, bins, cap, bits = args
            L.cpu_tile_pipe(int(grid[0]), P(U), int(row0), P(tabt), int(nS), P(gcnt), P(bins), int(cap), P(bits), int(block[0]))
        elif self.name == "gbig_gen":
            U, TAB, nP, row0, nrows, cap, gcnt, bins = args
            L.cpu_gen(P(U), P(TAB), int(nP), int(row0), int(nrows), int(cap), P(gcnt), P(bins), int(block[0]))
        elif self.name == "gbig_gen_st":
            U, TAB, pstart, row0, nrows, cap, gcnt, bins = args
            L.cpu_gen_st(P(U), P(TAB), P(pstart), int(grid[1] if self.order else grid[0]), int(row0), int(nrows), int(cap), P(gcnt), P(bins), int(block[0]))
        elif self.name == "ghead_gen":
            U, TAB, nP, row0, nrows, cap, gcnt, bins = args
            L.cpu_head_gen(P(U), P(TAB), int(nP), int(row0), int(nrows), int(cap), P(gcnt), P(bins), int(block[0]))
        elif self.name == "ghead_apply":
            row0, gcnt, bins, cap, bits, slot_of, dcnt = args
            L.cpu_head_apply(int(grid[0]), int(row0), P(gcnt), P(bins), int(cap), P(bits), P(slot_of), P(dcnt), int(block[0]))
        else:
            super().__call__(grid, block, args, shared_mem)


class _RawModule:
    def __init__(self, code=None):
        ks, llog, nth, tile, rg, ppt, sc, rc = (int(re.search(rf"#define {n} (\d+)", code).group(1)) for n in ("KS_LOG", "LLOG", "NTHREADS", "TILE_LOG", "RG", "PPT", "STAGE_CAP", "RCTA"))
        m = re.search(r"#define TILE_UNROLL (\d+)", code)
        self.lib = build(ks, llog, nth, tile, rg, ppt, sc, rc, int(m.group(1)) if m else 1, 1 if "#define BIN_PACK 1" in code else 0, 1 if "#define GEN_HOIST 1" in code else 0, int(re.search(r"#define GEN_UNROLL (\d+)", code).group(1)) if "#define GEN_UNROLL" in code else 1,
                         1 if "#define GEN_FLUSH2 1" in code else 0, 1 if "#define GEN_ORDER 1" in code else 0,
                         (int(re.search(r"#define TILE_PIPE_AT (\d+)", code).group(1)), int(re.search(r"#define TILE_PIPE_CH (\d+)", code).group(1))) if "#define TILE_PIPE 1" in code else None,
                         tuple(1 if f"#define {n} 1" in code else 0 for n in ("GEN_SCAN2", "GEN_RESV_LATE", "GEN_MINRED")))
        self.order = "#define GEN_ORDER 1" in code

    def get_function(self, name):
        fn = _Fn(self.lib, name)
        fn.order = self.order
        return fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=40)
    ap.add_argument("--big", action="store_true", help="also B = 500,009 against batches of 2^12 / 2^13 members: primes 100x the batch, at most one mark a row (the regime of B = 1e9)")
    a = ap.parse_args()
    cp = TG.install_fake_cupy()
    cp.RawModule = _RawModule
    import gpu_sieve, gbatch, search
    from sieve200 import Feeder
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    spec["residual"] = spec["residual"][:a.rows]
    cover = [r for r, _ in spec["cover"]]
    ok = True
    BIG = ((500009, 12, 11, 11, 4, 2048, 0.8, False, 2, 8192), (500009, 12, 11, 11, 4, 2048, 0.8, True, 2, 512), (500009, 13, 12, 11, 8, 4096, 0.9, True, 1, 1024),
           (20011, 14, 11, 11, 16, 2048, 0.5, True, 8, 512), (20011, 14, 11, 11, 16, 2048, 0.5, True, 16, 256)) if a.big else ()      # the last two: 8 and 16 rows a CTA (DEEP_RCTA=8 / 16)
    # (B, ks_log, tile_log, llog, rg, split, f): primes up to B; a batch of 2^ks members in 2^(ks - tile) tiles; the primes above `split` through gbig
    for B, ks, tile, llog, rg, split, f, staged, rcta, stage_cap in ((32768, 15, 12, 11, 4, 4096, 0.9, False, 2, 8192), (20011, 14, 11, 11, 3, 2048, 0.5, False, 2, 8192),
                                                                      (9001, 13, 11, 11, 16, 9001, 0.0, False, 2, 8192), (32768, 14, 12, 11, 7, 0, 0.8, False, 2, 8192),
                                                                      (32768, 15, 12, 11, 4, 4096, 0.9, True, 2, 512), (32768, 14, 12, 11, 7, 0, 0.8, True, 1, 768),
                                                                      (20011, 14, 11, 11, 3, 2048, 0.5, True, 4, 256)) + BIG:
        if os.environ.get("DEEP_BIN_PACK", "0") == "1" and not staged:
            continue                                                    # packed bins exist for the staged kernel only
        search.G.clear(); search._SIEVE_CACHE.clear()
        search.init_spec(spec, B, 1 << llog)
        bf = gbatch.BatchFeeder.from_search_G(search.G, ks_log=ks, tile_log=tile, llog=llog, f=f, nthreads=64, split=split, rg=rg, ppt=2, gen_threads=max(32, -(-rcta * (1 << (ks - tile)) // 32) * 32), tile_threads=64, staged=staged, rcta=rcta, stage_cap=stage_cap)
        cf = Feeder(int(spec["N0"]), int(spec["M"]), spec["residual"], B=B, L=1 << llog, logK=ks, f=f, exclude=cover)
        for k0 in (1 << ks, 2 ** 31 + (1 << ks), 4293885952 - 4293885952 % (1 << ks)):
            w = bf.window(k0, timings=(k0 == 1 << ks))
            cb = cf.window(k0)
            pos, good = 0, True
            for b, fb in enumerate(cb):
                n = len(fb.k)
                good &= np.array_equal(w.k[pos:pos + n], fb.k) and np.array_equal(w.cnt[pos:pos + n], fb.cnt)
                good &= np.array_equal(w.rows[w.offs[pos]:w.offs[pos + n]], fb.rows) and np.all(w.block[pos:pos + n] == b)
                good &= int(w.alive_total[b]) == fb.alive_total and abs(w.hm_all[b] - fb.hm_all) <= 1e-9 * fb.hm_all
                good &= abs(w.hm_kept[b] - fb.hm_kept) <= 1e-9 * max(fb.hm_kept, 1e-300)
                pos += n
            good &= pos == len(w.k)
            print(f"  B={B} batch 2^{ks} tile 2^{tile} L=2^{llog} rg={rg} split={split} ({bf.n_small} small + {bf.n_large} large primes){' STAGED rcta ' + str(rcta) + ' stage ' + str(stage_cap) if staged else ''} f={f} k0={k0}: {len(cb)} blocks, {pos} members: "
                  f"{'identical to the CPU feeder' if good else 'DIFFERENT'}   gen retries so far {bf.big.retries if bf.big else 0}", flush=True)
            ok &= good
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
