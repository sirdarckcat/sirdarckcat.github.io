#!/usr/bin/env python3
"""The GPU sieve kernels (gsieve_kernels.cuh), run on the CPU by gsieve_cpu.cpp (pthreads, real barriers, atomics), against
sieve200.c and numpy: the bit matrix, the counts, the selection (np.argsort stable), the statistics and the survivor rows.

    python3 test_gsieve.py [--cover spec.json] [--rows N]
"""
import argparse, ctypes, json, math, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from sieve200 import Sieve200


def build(klog, llog, nthreads, maxsort=8192, unroll=1):
    out = os.path.join(HERE, f"libgsieve_cpu_{klog}_{llog}_{nthreads}_{maxsort}_u{unroll}.so")
    srcs = [os.path.join(HERE, f) for f in ("gsieve_cpu.cpp", "gsieve_kernels.cuh")]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in srcs):
        subprocess.check_call(["g++", "-O2", "-std=c++17", f"-DKLOG={klog}", f"-DLLOG={llog}", f"-DNTHREADS={nthreads}", f"-DMAXKEEP_SORT={maxsort}u", f"-DS200G_UNROLL={unroll}", "-Wno-unused-variable",
                               "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, srcs[0], "-lpthread"])
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
    lib.cpu_rows_nost.argtypes = [vp, ctypes.c_int, vp, vp, ctypes.c_int, vp]
    lib.cpu_rows_nold.argtypes = [vp, ctypes.c_int, vp, vp, ctypes.c_int, vp]
    lib.cpu_order.argtypes = [vp, ctypes.c_int, vp, ctypes.c_int]
    lib.cpu_rows_ord.argtypes = [vp, ctypes.c_int, vp, vp, vp, ctypes.c_int, vp]
    lib.cpu_rows_ord2.argtypes = [vp, ctypes.c_int, vp, vp, vp, ctypes.c_int, vp]
    lib.cpu_rows_ord_nost.argtypes = [vp, ctypes.c_int, vp, vp, vp, ctypes.c_int, vp]
    lib.cpu_rowmask.argtypes = [vp, ctypes.c_int, vp, ctypes.c_int, vp]
    lib.cpu_rowlist.argtypes = [vp, ctypes.c_int, vp, ctypes.c_int, vp]
    lib.cpu_fin_sums.argtypes = [vp, ctypes.c_int, vp, ctypes.c_int]
    lib.cpu_fin_main.argtypes = [vp, ctypes.c_int, ctypes.c_int, ctypes.c_uint64, vp, vp, vp, vp, vp, vp]
    lib.cpu_prep.argtypes = [vp, vp, vp, vp, ctypes.c_uint64, ctypes.c_int, vp]
    lib.cpu_sieve_sh.argtypes = [ctypes.c_int, vp, vp, ctypes.c_int, vp, ctypes.c_int]
    return lib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover", default=os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json"))
    ap.add_argument("--rows", type=int, default=100)
    a = ap.parse_args()
    spec = json.load(open(a.cover)); spec = spec[0] if isinstance(spec, list) else spec
    U = (spec["residual"] if isinstance(spec["residual"], list) else json.loads(spec["residual"]))[:a.rows]
    cover = [r for r, _ in spec["cover"]]
    N0, M = int(spec["N0"]), int(spec["M"])
    ok = True
    for B, klog, llog, nthreads, k0, maxsort in ((3001, 12, 11, 64, 777, 8192), (20011, 13, 11, 64, 2 ** 31 + 5, 8192),
                                                 (100003, 14, 12, 128, 4293885952 - 4293885952 % 16384, 8192), (20011, 12, 11, 64, 99, 64)):
        lib = build(klog, llog, nthreads, maxsort)
        K, L = 1 << klog, 1 << llog
        sv = Sieve200(N0, M, U, B, logK=klog, exclude=cover)
        S = sv.primes()
        INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
        MU = (np.uint64(2 ** 64 - 1) // S.astype(np.uint64)).astype(np.uint64)
        N0M = np.array([N0 % int(s) for s in S], dtype=np.uint32)
        KM = np.array([k0 % int(s) for s in S], dtype=np.uint32)
        Su = S.astype(np.uint32)
        Uu = np.array(U, dtype=np.uint32)
        KW = K // 32
        bits = np.zeros((len(U), KW), dtype=np.uint32)
        lib.cpu_sieve(len(U), Uu.ctypes.data, Su.ctypes.data, INV.ctypes.data, MU.ctypes.data, N0M.ctypes.data, KM.ctypes.data, len(S), bits.ctypes.data)
        cnt_ref, bits_ref = sv.block(k0)
        same_bits = np.array_equal(bits, bits_ref.view(np.uint32))
        # the Shoup sieve: the packed table against Python integers, then the bits with several CTA sizes (the kernel's block size is free)
        INVP = ((INV.astype(np.uint64) << 32) // S.astype(np.uint64)).astype(np.uint32)
        TAB = np.zeros((len(S), 4), dtype=np.uint32)
        lib.cpu_prep(Su.ctypes.data, INV.ctypes.data, INVP.ctypes.data, N0M.ctypes.data, k0, len(S), TAB.ctypes.data)
        c0_ref = np.array([(N0 * int(i) + k0) % int(s) for i, s in zip(INV, S)], dtype=np.uint32)
        same_tab = (np.array_equal(TAB[:, 0], Su) and np.array_equal(TAB[:, 1], INV) and np.array_equal(TAB[:, 2], INVP) and np.array_equal(TAB[:, 3], c0_ref))
        same_sh = True
        for threads in sorted({nthreads, 32, 96, 160}):
            bits_sh = np.zeros_like(bits)
            lib.cpu_sieve_sh(len(U), Uu.ctypes.data, TAB.ctypes.data, len(S), bits_sh.ctypes.data, threads)
            same_sh &= np.array_equal(bits_sh, bits)
        ok &= same_tab and same_sh
        counts = np.zeros(K, dtype=np.uint16)
        lib.cpu_count(bits.ctypes.data, len(U), counts.ctypes.data)
        same_cnt = np.array_equal(counts, cnt_ref)
        res = [f"B={B} K=2^{klog} L=2^{llog} maxsort={maxsort} rows={len(U)} primes={len(S)}: bits {'ok' if same_bits else 'MISMATCH'}, counts {'ok' if same_cnt else 'MISMATCH'}, "
               f"shoup table {'ok' if same_tab else 'MISMATCH'}, shoup bits {'ok' if same_sh else 'MISMATCH'}"]
        ok &= same_bits and same_cnt
        p_est = 0.055
        for nkeep in (0, 1, 3, 20, L // 4, L - 1, L):
            nb = K // L
            if nkeep == 0:
                continue
            keys = np.zeros(nb * nkeep, dtype=np.uint32); stats = np.zeros(nb * 3, dtype=np.float64)
            lib.cpu_select(counts.ctypes.data, len(U), nkeep, p_est, keys.ctypes.data, stats.ctypes.data)
            good = True
            for b in range(nb):
                cb = counts[b * L:(b + 1) * L].astype(np.int64)
                order = np.argsort(cb, kind="stable")[:nkeep]
                exp_keys = ((cb[order] << 20) | order).astype(np.uint32)
                w = (1 - p_est) ** cb.astype(np.float64)
                got = keys[b * nkeep:(b + 1) * nkeep]
                if nkeep > maxsort:
                    got = np.sort(got)                           # the caller sorts what the kernel could not
                good &= np.array_equal(got, exp_keys)
                good &= int(round(stats[3 * b])) == int(cb.sum()) and abs(stats[3 * b + 1] - w.sum()) <= 1e-12 * w.sum() and abs(stats[3 * b + 2] - w[order].sum()) <= 1e-12 * w[order].sum()
            res.append(f"select nkeep={nkeep}: {'ok' if good else 'MISMATCH'}")
            ok &= good
            if nkeep in (20, L // 4):                           # the rows of the kept members
                kk = np.sort(keys.reshape(nb, nkeep), axis=1) if nkeep > maxsort else keys.reshape(nb, nkeep)
                member = np.concatenate([(b * L + (kk[b] & 0xFFFFF)).astype(np.uint32) for b in range(nb)])
                cm = counts[member].astype(np.int64)
                offs = np.concatenate([[0], np.cumsum(cm)]).astype(np.int64)
                rows = np.zeros(int(offs[-1]) + 1, dtype=np.uint16)
                lib.cpu_rows(bits.ctypes.data, len(U), member.ctypes.data, offs.ctypes.data, len(member), rows.ctypes.data)
                alive = sv.alive(bits_ref)
                gr = all(np.array_equal(rows[offs[i]:offs[i + 1]], np.nonzero(alive[:, int(m)])[0]) for i, m in enumerate(member[:400]))
                res.append(f"rows {'ok' if gr else 'MISMATCH'}")
                ok &= gr
        n0l = np.frombuffer(N0.to_bytes(4 * 24, "little"), dtype=np.uint32).copy()
        n0got = np.zeros(len(S), dtype=np.uint32)
        lib.cpu_n0m(n0l.ctypes.data, 24, Su.ctypes.data, MU.ctypes.data, len(S), n0got.ctypes.data)
        res.append(f"n0m {'ok' if np.array_equal(n0got, N0M) else 'MISMATCH'}")
        ok &= np.array_equal(n0got, N0M)
        print("  " + "; ".join(res), flush=True)
    # the other mark-loop variants of the Shoup kernel (S200G_UNROLL 2 and 3) give the same bits
    for unroll in (2, 3):
        B, klog, llog, nthreads, k0 = 100003, 14, 12, 128, 4293885952 - 4293885952 % 16384
        lib = build(klog, llog, nthreads, 8192, unroll)
        sv = Sieve200(N0, M, U, B, logK=klog, exclude=cover)
        S = sv.primes(); Su = S.astype(np.uint32)
        INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
        INVP = ((INV.astype(np.uint64) << 32) // S.astype(np.uint64)).astype(np.uint32)
        N0M = np.array([N0 % int(s) for s in S], dtype=np.uint32)
        TAB = np.zeros((len(S), 4), dtype=np.uint32)
        lib.cpu_prep(Su.ctypes.data, INV.ctypes.data, INVP.ctypes.data, N0M.ctypes.data, k0, len(S), TAB.ctypes.data)
        Uu = np.array(U, dtype=np.uint32)
        _, bits_ref = sv.block(k0)
        good = True
        for threads in (128, 64, 224):
            bits_sh = np.zeros((len(U), (1 << klog) // 32), dtype=np.uint32)
            lib.cpu_sieve_sh(len(U), Uu.ctypes.data, TAB.ctypes.data, len(S), bits_sh.ctypes.data, threads)
            good &= np.array_equal(bits_sh, bits_ref.view(np.uint32))
        print(f"  S200G_UNROLL={unroll}, B={B}: shoup bits {'ok' if good else 'MISMATCH'}")
        ok &= good
    # rows with large q (up to 2^32 - 1): Shoup's bound holds for any 32-bit q, so the bits must still be identical
    rng = np.random.default_rng(5)
    Ubig = [int(v) for v in rng.integers(1 << 20, (1 << 32) - 1, 24)] + [(1 << 32) - 1, (1 << 31) + 1, 1 << 31]
    B, klog, llog, nthreads, k0 = 20011, 13, 11, 64, 12345
    lib = build(klog, llog, nthreads, 8192)
    sv = Sieve200(N0, M, Ubig, B, logK=klog, exclude=cover)
    S = sv.primes(); Su = S.astype(np.uint32)
    INV = np.array([pow(M % int(s), -1, int(s)) for s in S], dtype=np.uint32)
    INVP = ((INV.astype(np.uint64) << 32) // S.astype(np.uint64)).astype(np.uint32)
    N0M = np.array([N0 % int(s) for s in S], dtype=np.uint32)
    TAB = np.zeros((len(S), 4), dtype=np.uint32)
    lib.cpu_prep(Su.ctypes.data, INV.ctypes.data, INVP.ctypes.data, N0M.ctypes.data, k0, len(S), TAB.ctypes.data)
    Uu = np.array(Ubig, dtype=np.uint32)
    bits_sh = np.zeros((len(Ubig), (1 << klog) // 32), dtype=np.uint32)
    lib.cpu_sieve_sh(len(Ubig), Uu.ctypes.data, TAB.ctypes.data, len(S), bits_sh.ctypes.data, 64)
    _, bits_ref = sv.block(k0)
    same = np.array_equal(bits_sh, bits_ref.view(np.uint32))
    print(f"  large q (up to 2^32 - 1), B={B}: shoup bits {'ok' if same else 'MISMATCH'}")
    ok &= same
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
