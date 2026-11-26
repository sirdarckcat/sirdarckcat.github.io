#!/usr/bin/env python3
"""The GPU Fermat kernels (the CUDA source compiled for the CPU, test_fermat28.py's harness) on the 665-bit numbers below 10^200.

    python3 test_k28_665.py STEP[,STEP...] [count] [record.json]
    e.g. python3 test_k28_665.py fermat29_step_s1.cuh,fermat29_step_s1w.cuh,fermat28_step_s1r.cuh,fermat28_step_s1rw.cuh 20000 rec.json

Random odd n in [2^664, 10^200), 1,000 primes there, and (with a record.json: N, Q, g) every N - q for the odd primes q < Q
and N - g: verdicts against gmpy2 and the residue y = 2^(1-n) mod n (y < 4n).  25 Nov 2026: 0 wrong for all four steps.
The CPU build uses the portable multiply-add, not the inline PTX of the asm variants."""
import ctypes, json, os, random, sys, time
import numpy as np, gmpy2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fm_geom import geometry
rec = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
N, Q, g = (int(rec['N']), int(rec['Q']), int(rec['g'])) if rec else (0, 0, 0)
rng = random.Random(29)
lo, hi = 1 << 664, 10 ** 200
rnds = [rng.randrange(lo, hi) | 1 for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 20000)]
ps = []
while len(ps) < 1000:
    p = int(gmpy2.next_prime(rng.randrange(lo, hi - 10 ** 190)))
    if p < hi: ps.append(p)
qs = [q for q in range(3, Q) if gmpy2.is_prime(q)]
recn = [N - q for q in qs]
sets = [("random odd n in [2^664, 10^200)", rnds), ("primes in [2^664, 10^200)", ps)] + ([(f"record g = {g}: N - q, odd primes q < {Q}", recn), ("record: N - g", [N - g])] if rec else [])
def to_limbs(x, limbs=21):
    return np.frombuffer(int(x).to_bytes(4 * limbs, 'little'), dtype=np.uint32)
for step in sys.argv[1].split(','):
    W, NLIMB, NMAX = geometry(step)
    tag = os.path.splitext(step)[0].replace('fermat28_', '')
    so = os.path.join(HERE, f'libfermat28_cpu_{tag}.so')
    srcs = [os.path.join(HERE, f) for f in ('fermat28_cpu.cpp', step, 'fermat28_kernel.cuh')]
    if not os.path.exists(so) or os.path.getmtime(so) < max(os.path.getmtime(s) for s in srcs):
        import subprocess
        subprocess.check_call(['g++', '-O2', f'-DSTEP_FILE="{step}"', '-Wno-unused', '-Wno-unknown-pragmas', '-shared', '-fPIC', '-o', so, srcs[0]])
    lib = ctypes.CDLL(so); lib.run_cpu.argtypes = [ctypes.c_void_p] * 5 + [ctypes.c_int]; lib.set_dbg.argtypes = [ctypes.c_void_p]
    def run(ns):
        dbg = np.zeros((len(ns), NLIMB), dtype=np.uint32); lib.set_dbg(dbg.ctypes.data); run.dbg = dbg
        CQ = np.ascontiguousarray(np.stack([to_limbs(n) for n in ns]), dtype=np.uint32); Mv = np.ascontiguousarray(to_limbs(0), dtype=np.uint32)
        idx = np.ascontiguousarray(np.arange(len(ns)), dtype=np.int32); kv = np.zeros(len(ns), dtype=np.uint32); out = np.zeros(len(ns), dtype=np.uint8)
        lib.run_cpu(CQ.ctypes.data, Mv.ctypes.data, idx.ctypes.data, kv.ctypes.data, out.ctypes.data, len(ns))
        return out
    print(f"{step}: W={W} limbs={NLIMB} NMAX={NMAX} (flag 2 at n >= 2^{NMAX})", flush=True)
    for name, ns in sets:
        t = time.time(); got = run(ns)
        bad = fp = fn = fl = pos = badres = 0
        for n, v, row in zip(ns, got.tolist(), run.dbg):
            y = sum(int(x) << (W * i) for i, x in enumerate(row))
            badres += (y >= 4 * n) or (y % n != pow(2, 1 - n, n))
            ref = 1 if gmpy2.powmod(2, n - 1, n) == 1 else 0
            pos += ref
            if v == 2: fl += 1
            elif v != ref:
                bad += 1; fp += v == 1; fn += v == 0
        print(f"  {name}: {len(ns)} numbers ({pos} PRP), wrong {bad} (false PRP {fp}, false composite {fn}), flagged out of range {fl}, residues wrong {badres}  [{time.time() - t:.0f}s]", flush=True)
