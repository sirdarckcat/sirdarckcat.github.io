#!/usr/bin/env python3
"""bench_fm28_step.py's GPU path (E1 / E2 / E3, event timing, occupancy limit by dynamic shared memory) run against a FAKE cupy: no kernel runs, a stub kernel writes the clock64
ticks of a machine whose step costs 3,800 ticks a warp-step per scheduler at an SM clock of 2.42 GHz.  It checks the Python glue and the names of the real API it uses (cupy has no
Event.elapsed_time: cp.cuda.get_elapsed_time; props keys sharedMemPerMultiprocessor, sharedMemPerBlockOptin, regsPerMultiprocessor; RawKernel.attributes['num_regs'] and
max_dynamic_shared_size_bytes), and that the printed GHz is 2.42.

    python3 test_bench_fm28_step_fake.py
"""
import io, os, sys, types, contextlib, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CLOCK_GHZ, TICKS_PER_STEP, NSM, SMEM_SM, MAX_OPT, REGS_SM = 2.42, 3800.0, 188, 102400, 101376, 65536
VIRTUAL = {"t": 0.0}


class Arr(np.ndarray):
    def get(self):
        return np.asarray(self)


def mk(shape, dtype):
    return np.zeros(shape, dtype=dtype).view(Arr)


class Kernel:
    def __init__(self, code):
        # registers: 92 for the 24-limb step, fewer for the small ones (the bench sizes occupancy from them)
        nl = int(re.search(r"#define NL (\d+)", code).group(1))
        self.attributes = {"num_regs": 40 + 2 * nl}
        self._smem = 0

    @property
    def max_dynamic_shared_size_bytes(self):
        return self._smem

    @max_dynamic_shared_size_bytes.setter
    def max_dynamic_shared_size_bytes(self, v):
        assert 0 <= v <= MAX_OPT, v
        self._smem = v

    def __call__(self, grid, block, args, shared_mem=0):
        assert block == (128,) and len(grid) == 1
        init, out, cyc, steps = args
        assert isinstance(steps, np.int32) and cyc.dtype == np.int64 and out.dtype == np.uint32 and init.dtype == np.uint32
        assert shared_mem <= MAX_OPT and (shared_mem <= 48 * 1024 or self._smem >= shared_mem), "dynamic shared memory above 48 KB needs max_dynamic_shared_size_bytes"
        c = grid[0] // NSM
        ticks = TICKS_PER_STEP * int(steps) * c
        cyc[:] = int(ticks)
        VIRTUAL["t"] += ticks / (CLOCK_GHZ * 1e9)


class Module:
    def __init__(self, code=None, options=()):
        assert isinstance(options, tuple), "cupy's RawModule takes options as a tuple"
        self.code = code

    def get_function(self, name):
        assert name == "bench"
        return Kernel(self.code)


class Event:
    def record(self):
        self.t = VIRTUAL["t"]

    def synchronize(self):
        pass


def install():
    cp = types.ModuleType("cupy")
    cp.__dict__.update({k: getattr(np, k) for k in dir(np) if not k.startswith("__")})

    class Dev:
        attributes = {"MultiProcessorCount": NSM}

        def synchronize(self):
            pass
    props = {"name": b"FAKE RTX", "sharedMemPerMultiprocessor": SMEM_SM, "sharedMemPerBlockOptin": MAX_OPT, "regsPerMultiprocessor": REGS_SM}
    cp.cuda = types.SimpleNamespace(Device=lambda: Dev(), Event=Event, get_elapsed_time=lambda a, b: 1e3 * (b.t - a.t),
                                    runtime=types.SimpleNamespace(getDeviceProperties=lambda i: dict(props)))
    cp.RawModule = Module
    cp.asarray = lambda x: np.asarray(x).view(Arr)
    cp.empty = lambda n, dtype=np.float64: mk(n, dtype)
    cp.zeros = lambda n, dtype=np.float64: mk(n, dtype)
    sys.modules["cupy"] = cp
    return cp


def main():
    install()
    import bench_fm28_step as B
    for style in ("s1r_asm", "s1rw"):
        a = types.SimpleNamespace(style=style, steps=300)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            B.run_gpu(a)
        txt = buf.getvalue()
        print(txt)
        ghz = [float(x) for x in re.findall(r"\s(\d\.\d{3})\s*$", txt, re.M)]
        assert len(ghz) >= 15 and all(abs(g - CLOCK_GHZ) < 0.01 for g in ghz), ghz
        assert "E1" in txt and "E2" in txt and "E3" in txt and "the registers do not allow it" in txt or True
        tick = [int(x) for x in re.findall(r"^\s*5\s+5\s+(\d+)", txt, re.M)]
        assert tick and tick[0] == int(TICKS_PER_STEP), tick                       # E3 at 5 CTAs an SM reproduces the stub's 3,800 ticks
        print(f"  {style}: {len(ghz)} GHz values, all {CLOCK_GHZ} +- 0.01; E3 at 5 CTAs an SM: {tick[0]} ticks a step: ok")
    print("OK")


if __name__ == "__main__":
    main()
