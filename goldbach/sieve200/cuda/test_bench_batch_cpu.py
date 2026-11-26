#!/usr/bin/env python3
"""bench_batch.py's own code (prime tables, check against the CPU feeder, the timed run with per-phase times) on the CPU: cupy replaced by numpy + the pthread emulation, on a tiny instance."""
import argparse, json, os, sys, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gbatch_cpu as TB

if __name__ == "__main__":
    cp = TG.install_fake_cupy()
    cp.RawModule = TB._RawModule
    cp.cuda.runtime = types.SimpleNamespace(memGetInfo=lambda: (8 << 30, 16 << 30), getDeviceProperties=lambda i: {"name": b"CPU emulation"})
    cp.get_default_memory_pool = lambda: types.SimpleNamespace(free_all_blocks=lambda: None)
    import bench_batch as bb
    spec = json.load(open(os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")))
    spec["residual"] = spec["residual"][:24]
    a = argparse.Namespace(B=1 << 15, ks=15, tile=12, llog=11, split=4096, f=0.9, rg=4, ppt=2, nthreads=64, gen_threads=32, tile_threads=64, reps=1,
                           check_rows=20, check_b=1 << 15, check_ks=14, staged=0, rcta=2, stage_cap=8192)
    ok = bb.check(spec, a)
    acc = bb.run(spec, a, a.rg, a.tile_threads)
    assert acc is not None and all(k in acc for k in ("prep", "sieve", "count", "select", "finalize", "wait1", "rows", "wait2", "host", "wall"))
    # the same with the staged large-prime kernel (2 rows a CTA, 512 marks staged a CTA)
    a.staged, a.stage_cap = 1, 512
    ok2 = bb.check(spec, a)
    acc2 = bb.run(spec, a, a.rg, a.tile_threads)
    assert acc2 is not None
    print("check", "ok" if (ok and ok2) else "FAILED")
    ok = ok and ok2
    sys.exit(0 if ok else 1)
