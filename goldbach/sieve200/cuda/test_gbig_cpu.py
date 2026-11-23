#!/usr/bin/env python3
"""gbig.py and bench_bigprimes.py (the cupy side of the large-prime stage) run on the CPU: cupy is replaced by numpy plus a RawModule whose kernels are the pthread
emulation of gbig_kernels.cuh.  Checks the glue (capacity retry, shapes, events) and the bit matrix against numpy.

    python3 test_gbig_cpu.py
"""
import os, re, sys, types, runpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_gbig


class _Fn:
    def __init__(self, lib, name):
        self.lib, self.name = lib, name

    def __call__(self, grid, block, args, shared_mem=0):
        P = lambda a: a.ctypes.data
        if self.name == "gbig_gen":
            U, TAB, nP, row0, nrows, cap, gcnt, bins = args
            self.lib.cpu_gen(P(U), P(TAB), int(nP), int(row0), int(nrows), int(cap), P(gcnt), P(bins), int(block[0]))
        elif self.name == "gbig_gen_st":
            U, TAB, pstart, row0, nrows, cap, gcnt, bins = args
            self.lib.cpu_gen_st(P(U), P(TAB), P(pstart), int(grid[0]), int(row0), int(nrows), int(cap), P(gcnt), P(bins), int(block[0]))
        else:
            gcnt, bins, cap, out = args
            self.lib.cpu_apply(int(grid[0]), P(gcnt), P(bins), int(cap), P(out), int(block[0]))


class _RawModule:
    def __init__(self, code=None):
        tl, ks, rg, ppt, sc, rc = (int(re.search(rf"#define {n} (\d+)", code).group(1)) for n in ("TILE_LOG", "KS_LOG", "RG", "PPT", "STAGE_CAP", "RCTA"))
        self.lib = test_gbig.build(tl, ks, rg, ppt, sc, rc)

    def get_function(self, name):
        return _Fn(self.lib, name)


def install_fake_cupy():
    cp = types.ModuleType("cupy")
    cp.__dict__.update({k: getattr(np, k) for k in dir(np) if not k.startswith("__")})
    cp.asnumpy = np.asarray
    cp.RawModule = _RawModule
    class _Dev:
        def synchronize(self): pass
    class _Event:
        def record(self): self.t = __import__("time").perf_counter()
        def synchronize(self): pass
    cp.cuda = types.SimpleNamespace(Device=lambda: _Dev(), Event=_Event, get_elapsed_time=lambda a, b: 1e3 * (b.t - a.t),
                                    runtime=types.SimpleNamespace(getDeviceProperties=lambda i: {"name": b"CPU emulation"}))
    sys.modules["cupy"] = cp
    return cp


if __name__ == "__main__":
    install_fake_cupy()
    # a small instance: 40-bit... tiles of 2^10 bits, batches of 2^13, primes in (2^10, 2^13], 9 rows in groups of 4 (RG is a compile-time constant), a capacity too small
    # for the first attempt is provoked by the 6-sigma-free cap of expected_cap on a tiny bin (the retry path), and the result is checked against numpy
    sys.argv = ["bench_bigprimes.py", "--rows", "9", "--plo", "10", "--b", "13", "--ks", "13", "--tile", "10", "--rg", "4", "--ppt", "2", "--threads", "32", "--check"]
    try:
        runpy.run_path(os.path.join(HERE, "bench_bigprimes.py"), run_name="__main__")
    except SystemExit as e:                                    # the script ends with sys.exit(main())
        assert e.code in (0, None), "bench_bigprimes --check failed"
    # the staged kernel through the same glue (bench_bigprimes --staged 1, 2 rows a CTA, 512 marks staged a CTA), then its capacity retry
    sys.argv = ["bench_bigprimes.py", "--rows", "9", "--plo", "10", "--b", "13", "--ks", "13", "--tile", "10", "--rg", "4", "--ppt", "2", "--threads", "32", "--check",
                "--staged", "1", "--rcta", "2", "--stage-cap", "512"]
    try:
        runpy.run_path(os.path.join(HERE, "bench_bigprimes.py"), run_name="__main__")
    except SystemExit as e:
        assert e.code in (0, None), "bench_bigprimes --staged --check failed"
    # the capacity retry: an initial cap of 8 overflows, the demand of the fullest bin sizes the second attempt, the result is the same
    import gbig, bench_bigprimes as bb
    S = gbig.primes_between(1 << 10, 1 << 13)
    TAB = gbig.make_table(S, rng=np.random.default_rng(1))
    U = np.sort(np.random.default_rng(1).choice(np.arange(1, 150000), size=6, replace=False)).astype(np.uint32)
    st = gbig.BigStage(U, TAB, ks_log=13, tile_log=10, rg=4, ppt=2, threads=32, cap=8)
    out = np.array(st.run_group(0, 4))
    ref = bb.reference(U, TAB, 13, 4)
    bits = np.unpackbits(out.view(np.uint8), bitorder="little").reshape(4, 1 << 13).astype(bool)
    good = np.array_equal(bits, ref) and st.retries == 1 and st.cap >= 64
    print(f"capacity retry: cap 8 -> {st.cap}, retries {st.retries}, result {'identical to numpy' if good else 'WRONG'}")
    st2 = gbig.BigStage(U, TAB, ks_log=13, tile_log=10, rg=4, ppt=2, threads=32, cap=8, staged=True, rcta=2, stage_cap=512)
    out2 = np.array(st2.run_group(0, 4))
    bits2 = np.unpackbits(out2.view(np.uint8), bitorder="little").reshape(4, 1 << 13).astype(bool)
    good2 = np.array_equal(bits2, ref) and st2.retries == 1 and st2.cap >= 64
    print(f"staged capacity retry: cap 8 -> {st2.cap}, retries {st2.retries}, result {'identical to numpy' if good2 else 'WRONG'}")
    sys.exit(0 if (good and good2) else 1)
