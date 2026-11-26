#!/usr/bin/env python3
"""time_launch.py's main() on a fake cupy (numpy arrays, Events, one device) whose kernel is the CPU build of the production kernel
(libfermat28_cpu_step_s1r.so, one test after the other): the pool, the launches, the timing code and the report run end to end on tiny
sizes, and the flags of one launch equal Python pow.  Nothing about speed.

    python3 test_time_launch_fake.py
"""
import ctypes, os, subprocess, sys, types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sieve200", "cuda"))
import test_gpu_sieve_cpu as TG

cp = TG.install_fake_cupy()
cp.cuda.Device = lambda: types.SimpleNamespace(attributes={"MultiProcessorCount": 2}, synchronize=lambda: None, id=0)
cp.cuda.get_current_stream = lambda: types.SimpleNamespace(synchronize=lambda: None)
import gpu_fermat28 as g28

step = "fermat28_step_s1r.cuh"
prod_so = os.path.join(HERE, "libfermat28_cpu_step_s1r.so")
deps = [os.path.join(HERE, f) for f in ("fermat28_cpu.cpp", step, "fermat28_kernel.cuh")]
if not os.path.exists(prod_so) or os.path.getmtime(prod_so) < max(os.path.getmtime(d) for d in deps):
    subprocess.check_call(["g++", "-O2", "-std=c++17", f'-DSTEP_FILE="{step}"', "-Wno-unused", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-I", HERE, "-o", prod_so, deps[0]])
prod = ctypes.CDLL(prod_so)
vp = ctypes.c_void_p
prod.run_cpu.argtypes = [vp, vp, vp, vp, vp, ctypes.c_int]
prod.set_dbg.argtypes = [vp]
DBG = np.zeros(4096 * 24, dtype=np.uint32)
prod.set_dbg(DBG.ctypes.data)
LAST = {}


class FakeKernel:
    def __call__(self, grid, block, args):
        cq, M, idx, kv, out, T = args
        prod.run_cpu(cq.ctypes.data, M.ctypes.data, idx.ctypes.data, kv.ctypes.data, out.ctypes.data, int(T))
        LAST.update(cq=cq, idx=idx, out=out)


g28.kernel = lambda limbs=21, **kw: FakeKernel()
import time_launch                                                               # noqa: E402

res = time_launch.main(["--sizes", "8", "100", "1000", "--reps", "2", "--rows", "300"], cp=cp)
assert [r[0] for r in res] == [8, 100, 1000]
cq, idx, out = LAST["cq"], LAST["idx"], LAST["out"]
ok = 0
for t in range(len(idx)):
    limbs = cq[idx[t]]
    n = sum(int(x) << (32 * i) for i, x in enumerate(limbs))
    assert out[t] == (pow(2, n - 1, n) == 1), (t, n)
    ok += 1
print(f"test_time_launch_fake: the report ran for {len(res)} sizes; the last launch's {ok} flags equal Python pow: OK")
