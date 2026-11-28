#!/usr/bin/env python3
"""bench_persist.py's main() on a fake cupy (numpy arrays, Events, a device with 2 SMs) whose kernels are the CPU builds of the production kernel (libfermat28_cpu_step_s1r.so, one test after the
other) and of the persistent kernel (fermat28_persist_cpu.cpp, 16 real threads): the pool generation, the launches, the timing code, the correctness check against the production kernel's flags
and the report run end to end on tiny sizes.  What it cannot say is anything about speed.

    python3 test_bench_persist_fake.py
"""
import ctypes, os, subprocess, sys, types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sieve200", "cuda"))
import test_gpu_sieve_cpu as TG

cp = TG.install_fake_cupy()
cp.cuda.Device = lambda: types.SimpleNamespace(attributes={"MultiProcessorCount": 2, "MaxRegistersPerMultiprocessor": 65536, "MaxThreadsPerMultiProcessor": 1536}, synchronize=lambda: None, id=0)
cp.cuda.get_current_stream = lambda: types.SimpleNamespace(synchronize=lambda: None)
import gpu_fermat28 as g28
from test_fermat28_persist import build

step = "fermat28_step_s1r.cuh"
prod_so = os.path.join(HERE, "libfermat28_cpu_step_s1r.so")
deps = [os.path.join(HERE, f) for f in ("fermat28_cpu.cpp", step, "fermat28_kernel.cuh")]
if not os.path.exists(prod_so) or os.path.getmtime(prod_so) < max(os.path.getmtime(d) for d in deps):
    subprocess.check_call(["g++", "-O2", "-std=c++17", f'-DSTEP_FILE="{step}"', "-Wno-unused", "-Wno-unknown-pragmas", "-shared", "-fPIC", "-I", HERE, "-o", prod_so, deps[0]])
prod = ctypes.CDLL(prod_so)
pers = ctypes.CDLL(build(step))
vp = ctypes.c_void_p
prod.run_cpu.argtypes = [vp, vp, vp, vp, vp, ctypes.c_int]
prod.set_dbg.argtypes = [vp]
DBG = np.zeros(8192 * 24, dtype=np.uint32)                  # the CPU build of the production kernel writes the residue before the reduction of every test here (debug aid)
prod.set_dbg(DBG.ctypes.data)
pers.run_persist_cpu.argtypes = [vp, vp, vp, vp, vp, vp, ctypes.c_int, vp, vp, vp, vp, ctypes.c_int]


def conv(args):
    return [a.ctypes.data if isinstance(a, np.ndarray) else int(a) for a in args]


class FakeKernel:
    def __init__(self, fn, regs):
        self.fn, self.attributes = fn, {"num_regs": regs}

    def __call__(self, grid, block, args):
        self.fn(*conv(args))


g28.kernel = lambda limbs=21, **kw: FakeKernel(prod.run_cpu, 88)
g28.persist_kernel = lambda limbs=21, **kw: FakeKernel(lambda *a: pers.run_persist_cpu(*a, 16), 96)
import bench_persist as B

rc = B.main(["--members", "60", "--list", "30", "--rows", "300", "--sieve", "2000", "--check", "60", "--reps", "1", "--prod-tests", "100", "--sync", "0", "1"])
print("OK" if rc == 0 else "FAILED")
sys.exit(rc)
