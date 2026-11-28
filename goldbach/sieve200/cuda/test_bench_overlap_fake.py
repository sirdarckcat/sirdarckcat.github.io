#!/usr/bin/env python3
"""bench_overlap.py's control flow and arithmetic against stubs: a fake cupy (events, streams, device), a feeder whose window() takes 20 ms, a tester whose launch takes 0.3 s; the sieve
thread runs beside the launch, so ~15 windows complete and the report must say the overlap works.  No GPU, no kernels: it checks the Python (names of the cupy API it uses, thread handling,
the projection arithmetic), not the hardware.

    python3 test_bench_overlap_fake.py
"""
import io, os, sys, time, types, contextlib, json, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


class Ev:
    def record(self): self.t = time.perf_counter()
    def synchronize(self): pass


class Stream:
    def __init__(self, non_blocking=False): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def synchronize(self): pass


class Dev:
    id = 0
    attributes = {"MultiProcessorCount": 188}
    def __init__(self, i=0): pass
    def use(self): pass
    def synchronize(self): pass


def install():
    cp = types.ModuleType("cupy")
    cp.asarray = np.asarray
    cp.cuda = types.SimpleNamespace(Event=Ev, get_elapsed_time=lambda a, b: 1e3 * (b.t - a.t), Device=Dev, Stream=Stream,
                                    runtime=types.SimpleNamespace(getDeviceProperties=lambda i: {"name": b"FAKE GPU"}))
    sys.modules["cupy"] = cp
    return cp


class Feeder:
    def window(self, k0): time.sleep(0.02)


class Tester:
    def __init__(self, fermat_s): self.fermat_s = fermat_s
    def test(self, idx, kv): time.sleep(self.fermat_s)


def main():
    install()
    import bench_overlap as B
    B.make_feeder = lambda cp, spec, a: (Feeder(), 1262)
    B.make_tester = lambda cp, spec, a: (Tester(0.3), np.zeros(1 << 10, np.int32), np.zeros(1 << 10, np.uint32), {"num_regs": 92, "local_size_bytes": 0})
    spec = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump([{"N0": 1, "M": 1, "residual": [3, 5]}], spec); spec.close()
    for extra in ([], ["--carveout", "100", "--variant", "s1r_asm_r80", "--cta-sm", "4", "--no-priority"]):
        sys.argv = ["bench_overlap.py", spec.name, "--reps", "2", "--tests", "1024"] + extra
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            B.main()
        txt = buf.getvalue()
        print(txt)
        assert "alone:" in txt and "concurrent:" in txt and "production batch" in txt
        assert "OVERLAP WORKS" in txt, "the fake overlap (a sleeping launch and a sleeping sieve) must be reported as working"
        if extra:
            assert os.environ.get("FERMAT_CARVEOUT") == "100" and os.environ.get("DEEP_CARVEOUT") == "100"
    os.unlink(spec.name)
    print("OK")


if __name__ == "__main__":
    main()
