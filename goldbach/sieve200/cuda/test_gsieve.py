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


def build(klog, llog, nthreads):
    out = os.path.join(HERE, f"libgsieve_cpu_{klog}_{llog}_{nthreads}.so")
    srcs = [os.path.join(HERE, f) for f in ("gsieve_cpu.cpp", "gsieve_kernels.cuh")]
    if not os.path.exists(out) or os.path.getmtime(out) < max(os.path.getmtime(s) for s in srcs):
        subprocess.check_call(["g++", "-O2", "-std=c++17", f"-DKLOG={klog}", f"-DLLOG={llog}", f"-DNTHREADS={nthreads}", "-Wno-unused-variable",
                               "-Wno-unknown-pragmas", "-shared", "-fPIC", "-o", out, srcs[0], "-lpthread"])
    lib = ctypes.CDLL(out)
    vp = ctypes.c_void_p
    lib.cpu_sieve.argtypes = [ctypes.c_int, vp, vp, vp, vp, vp, vp, ctypes.c_int, vp]
    lib.cpu_count.argtypes = [vp, ctypes.c_int, vp]
    lib.cpu_select.argtypes = [vp, ctypes.c_int, ctypes.c_int, ctypes.c_double, vp, vp]
    lib.cpu_rows.argtypes = [vp, ctypes.c_int, vp, vp, ctypes.c_int, vp]
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
    for B, klog, llog, nthreads, k0 in ((3001, 12, 11, 64, 777), (20011, 13, 11, 64, 2 ** 31 + 5), (100003, 14, 12, 128, 4293885952 - 4293885952 % 16384)):
        lib = build(klog, llog, nthreads)
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
        counts = np.zeros(K, dtype=np.uint16)
        lib.cpu_count(bits.ctypes.data, len(U), counts.ctypes.data)
        same_cnt = np.array_equal(counts, cnt_ref)
        res = [f"B={B} K=2^{klog} L=2^{llog} rows={len(U)} primes={len(S)}: bits {'ok' if same_bits else 'MISMATCH'}, counts {'ok' if same_cnt else 'MISMATCH'}"]
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
                good &= np.array_equal(keys[b * nkeep:(b + 1) * nkeep], exp_keys)
                good &= int(round(stats[3 * b])) == int(cb.sum()) and abs(stats[3 * b + 1] - w.sum()) <= 1e-12 * w.sum() and abs(stats[3 * b + 2] - w[order].sum()) <= 1e-12 * w[order].sum()
            res.append(f"select nkeep={nkeep}: {'ok' if good else 'MISMATCH'}")
            ok &= good
            if nkeep in (20, L // 4):                           # the rows of the kept members
                member = np.concatenate([(b * L + (keys[b * nkeep:(b + 1) * nkeep] & 0xFFFFF)).astype(np.uint32) for b in range(nb)])
                cm = counts[member].astype(np.int64)
                offs = np.concatenate([[0], np.cumsum(cm)]).astype(np.int64)
                rows = np.zeros(int(offs[-1]) + 1, dtype=np.uint16)
                lib.cpu_rows(bits.ctypes.data, len(U), member.ctypes.data, offs.ctypes.data, len(member), rows.ctypes.data)
                alive = sv.alive(bits_ref)
                gr = all(np.array_equal(rows[offs[i]:offs[i + 1]], np.nonzero(alive[:, int(m)])[0]) for i, m in enumerate(member[:400]))
                res.append(f"rows {'ok' if gr else 'MISMATCH'}")
                ok &= gr
        print("  " + "; ".join(res), flush=True)
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
