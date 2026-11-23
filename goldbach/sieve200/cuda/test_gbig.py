#!/usr/bin/env python3
"""The large-prime stage (gbig_kernels.cuh), run on the CPU by gbig_cpu.cpp (pthreads, real barriers, atomics), against a brute-force reference:
the bit matrix of (row, member) pairs killed by primes above the tile, for several row groups, CTA sizes, a window start k0 and a bin capacity too small
(the overflow flag must be set) and then large enough.

    python3 test_gbig.py
"""
import ctypes, os, subprocess, sys
import numpy as np

HERE0 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE0)
from bigchunks import make_chunks

HERE = os.path.dirname(os.path.abspath(__file__))


def build(tile_log, ks_log, rg, ppt, stage_cap=8192, rcta=2, pack=0, hoist=0, gunroll=1, flush2=0, order=0):
    out = os.path.join(HERE, f"libgbig_cpu_{tile_log}_{ks_log}_{rg}_{ppt}_{stage_cap}_{rcta}" + ("_pk" if pack else "") + ("_gh" if hoist else "") + (f"_gu{gunroll}" if gunroll > 1 else "") + ("_f2" if flush2 else "") + ("_go" if order else "") + ".so")
    srcs = [os.path.join(HERE, f) for f in ("gbig_cpu.cpp", "gbig_kernels.cuh")]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in srcs):
        subprocess.check_call(["g++", "-O2", "-std=c++17", f"-DTILE_LOG={tile_log}", f"-DKS_LOG={ks_log}", f"-DRG={rg}", f"-DPPT={ppt}", f"-DSTAGE_CAP={stage_cap}", f"-DRCTA={rcta}",
                               f"-DRCTA_LOG={rcta.bit_length() - 1}", f"-DBIN_PACK={pack}", f"-DGEN_HOIST={hoist}", f"-DGEN_UNROLL={gunroll}", f"-DGEN_FLUSH2={flush2}", f"-DGEN_ORDER={order}", "-Wno-unused-variable", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, srcs[0], "-lpthread"])
    lib = ctypes.CDLL(out)
    vp = ctypes.c_void_p
    lib.cpu_gen_st.argtypes = [vp, vp, vp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, vp, vp, ctypes.c_int]
    lib.cpu_gen.argtypes = [vp, vp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, vp, vp, ctypes.c_int]
    lib.cpu_apply.argtypes = [ctypes.c_int, vp, vp, ctypes.c_uint32, vp, ctypes.c_int]
    return lib


def primes_between(lo, hi):
    s = np.ones(hi + 1, dtype=bool); s[:2] = False
    for i in range(2, int(hi ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0][np.searchsorted(np.nonzero(s)[0], lo, side="right"):].astype(np.uint32)


def reference(U, S, INV, C0, KS):
    """bits[row][KS // 32]: 0 where a prime of S kills the member: j = ((q M^-1) - c0) mod s, j, j + s, ... < KS"""
    ref = np.ones((len(U), KS), dtype=bool)
    for r, q in enumerate(U.tolist()):                                  # Python integers: a numpy uint32 product would wrap
        for s, inv, c0 in zip(S.tolist(), INV.tolist(), C0.tolist()):
            j = (q * inv - c0) % s
            ref[r, j::s] = False
    return ref


def pack(bits_bool):
    n = bits_bool.shape[1]
    w = np.packbits(bits_bool.reshape(bits_bool.shape[0], n // 32, 32)[:, :, ::-1], axis=2).view(">u4")[:, :, 0].astype(np.uint32)   # bit b of word w = member 32 w + b
    return w


def main():
    ok = True
    rng = np.random.default_rng(3)
    for tile_log, ks_log, rg, ppt, threads in ((10, 13, 4, 2, 32), (9, 12, 3, 3, 16), (11, 14, 4, 1, 64)):
        lib = build(tile_log, ks_log, rg, ppt)
        NB, NT, TW = lib.cpu_nbins(), lib.cpu_ntiles(), lib.cpu_tile_words()
        KS = 1 << ks_log
        S = primes_between(1 << tile_log, 1 << (ks_log + 2))               # primes above the tile, some above the batch width too
        M = 1
        for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43):
            M *= p
        N0 = int(rng.integers(1, 1 << 60)) * M + 12345
        k0 = int(rng.integers(0, 1 << 40))
        U = np.sort(rng.choice(np.arange(1, 150000), size=7, replace=False)).astype(np.uint32)
        INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
        INVP = ((INV.astype(np.uint64) << 32) // S.astype(np.uint64)).astype(np.uint32)
        C0 = np.array([(N0 * int(i) + k0) % int(s) for i, s in zip(INV, S)], dtype=np.uint32)
        TAB = np.ascontiguousarray(np.stack([S, INV, INVP, C0], axis=1).astype(np.uint32))
        ref = reference(U, S, INV, C0, KS)
        refw = pack(ref)
        for row0 in range(0, len(U), rg):
            nrows = min(rg, len(U) - row0)
            # the true number of marks of every bin (several primes may kill the same bit, so this is more than the number of killed bits)
            cnt = np.zeros(NB, dtype=np.int64)
            for r in range(nrows):
                for s, inv, c0 in zip(S.tolist(), INV.tolist(), C0.tolist()):
                    j = (int(U[row0 + r]) * inv - c0) % s
                    while j < KS:
                        cnt[r * NT + (j >> tile_log)] += 1
                        j += s
            for cap, expect_overflow in ((8, True), (int(cnt.max()) + 2, False)):   # a real run uses a statistical bound for cap plus the overflow check
                gcnt = np.zeros(NB + 1, dtype=np.uint32)
                bins = np.zeros(NB * cap, dtype=np.uint32)
                lib.cpu_gen(U.ctypes.data, TAB.ctypes.data, len(S), row0, nrows, cap, gcnt.ctypes.data, bins.ctypes.data, threads)
                over = bool(gcnt[NB])
                good = over == expect_overflow
                if not expect_overflow:
                    out = np.zeros(NB * TW, dtype=np.uint32)
                    lib.cpu_apply(nrows * NT, gcnt.ctypes.data, bins.ctypes.data, cap, out.ctypes.data, threads)
                    got = out[:nrows * NT * TW].reshape(nrows, NT * TW)
                    good &= np.array_equal(got, refw[row0:row0 + nrows])
                    good &= np.array_equal(gcnt[:nrows * NT].astype(np.int64), cnt[:nrows * NT])
                    print(f"  TILE_LOG={tile_log} KS_LOG={ks_log} RG={rg} PPT={ppt} threads={threads} rows {row0}..{row0 + nrows - 1} cap {cap}: {len(S)} primes, "
                          f"{int(cnt.sum())} marks, bits and bin counts {'identical to the reference' if good else 'DIFFERENT'}", flush=True)
                else:
                    print(f"  TILE_LOG={tile_log} KS_LOG={ks_log} rows {row0}..{row0 + nrows - 1} cap {cap}: overflow flag {'set' if over else 'NOT SET'}", flush=True)
                ok &= good
    ok &= staged_tests(rng)
    print("ALL IDENTICAL" if ok else "FAILED")
    sys.exit(0 if ok else 1)


def staged_tests_v(rng, hoist=0, gunroll=1, flush2=0, order=0):
    """gbig_gen_st (the staged kernel) against the same reference: normal chunks (most CTAs stage their marks), chunks far over the buffer (every CTA falls back to one store a mark),
    rows that do not fill the last row group of CTAs, and a bin capacity too small (the flag) and then large enough"""
    ok = True
    # (tile_log, ks_log, rg, ppt (unused), threads, rcta, stage_cap, chunk target as a fraction of the buffer per CTA)
    for tile_log, ks_log, rg, threads, rcta, stage_cap, frac in ((10, 13, 4, 32, 2, 512, 0.75), (9, 12, 3, 32, 4, 256, 0.75), (11, 14, 4, 64, 1, 1024, 0.75),
                                                                    (10, 13, 4, 32, 2, 512, 3.0), (9, 12, 3, 32, 4, 256, 1.0)):
        lib = build(tile_log, ks_log, rg, 1, stage_cap, rcta, 0, hoist, gunroll, flush2, order)
        NB, NT, TW = lib.cpu_nbins(), lib.cpu_ntiles(), lib.cpu_tile_words()
        KS = 1 << ks_log
        S = primes_between(1 << tile_log, 1 << (ks_log + 2))
        M = 1
        for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43):
            M *= p
        N0 = int(rng.integers(1, 1 << 60)) * M + 12345
        k0 = int(rng.integers(0, 1 << 40))
        U = np.sort(rng.choice(np.arange(1, 150000), size=7, replace=False)).astype(np.uint32)
        INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
        INVP = ((INV.astype(np.uint64) << 32) // S.astype(np.uint64)).astype(np.uint32)
        C0 = np.array([(N0 * int(i) + k0) % int(s) for i, s in zip(INV, S)], dtype=np.uint32)
        TAB = np.ascontiguousarray(np.stack([S, INV, INVP, C0], axis=1).astype(np.uint32))
        ps = make_chunks(S, ks_log, frac * stage_cap / rcta).astype(np.int32)
        refw = pack(reference(U, S, INV, C0, KS))
        for row0 in range(0, len(U), rg):
            nrows = min(rg, len(U) - row0)
            cnt = np.zeros(NB, dtype=np.int64)
            for r in range(nrows):
                for s, inv, c0 in zip(S.tolist(), INV.tolist(), C0.tolist()):
                    j = (int(U[row0 + r]) * inv - c0) % s
                    while j < KS:
                        cnt[r * NT + (j >> tile_log)] += 1
                        j += s
            for cap, expect_overflow in ((8, True), (int(cnt.max()) + 2, False)):
                gcnt = np.zeros(NB + 1, dtype=np.uint32)
                bins = np.zeros(NB * cap, dtype=np.uint32)
                lib.cpu_gen_st(U.ctypes.data, TAB.ctypes.data, ps.ctypes.data, len(ps) - 1, row0, nrows, cap, gcnt.ctypes.data, bins.ctypes.data, threads)
                over = bool(gcnt[NB])
                good = over == expect_overflow
                if not expect_overflow:
                    out = np.zeros(NB * TW, dtype=np.uint32)
                    lib.cpu_apply(nrows * NT, gcnt.ctypes.data, bins.ctypes.data, cap, out.ctypes.data, threads)
                    got = out[:nrows * NT * TW].reshape(nrows, NT * TW)
                    good &= np.array_equal(got, refw[row0:row0 + nrows])
                    good &= np.array_equal(gcnt[:nrows * NT].astype(np.int64), cnt[:nrows * NT])
                    # how many CTAs staged: chunks with marks <= buffer (a CTA's total is the sum over its rows)
                    print(f"  STAGED{' hoist' if hoist else ''}{' unroll ' + str(gunroll) if gunroll > 1 else ''}{' FLAT-FLUSH' if flush2 else ''}{' ORDER' if order else ''} TILE_LOG={tile_log} KS_LOG={ks_log} RG={rg} RCTA={rcta} STAGE_CAP={stage_cap} chunk x{frac} threads={threads} rows {row0}..{row0 + nrows - 1} cap {cap}: "
                          f"{len(ps) - 1} chunks, {int(cnt.sum())} marks, bits and bin counts {'identical to the reference' if good else 'DIFFERENT'}", flush=True)
                else:
                    print(f"  STAGED TILE_LOG={tile_log} KS_LOG={ks_log} rows {row0}..{row0 + nrows - 1} cap {cap}: overflow flag {'set' if over else 'NOT SET'}", flush=True)
                ok &= good
    return ok


def staged_tests(rng):
    """the staged kernel's default build and its opt-in variants: hoisted visit loops (+ unroll), the flat flush, the grid order (every one must give the same bit matrix and bin demands)"""
    ok = True
    for hoist, gunroll, flush2, order in ((0, 1, 0, 0), (1, 1, 1, 0), (0, 1, 1, 1), (1, 2, 0, 1), (1, 4, 1, 1)):
        ok &= staged_tests_v(rng, hoist, gunroll, flush2, order)
    return ok


if __name__ == "__main__":
    main()
