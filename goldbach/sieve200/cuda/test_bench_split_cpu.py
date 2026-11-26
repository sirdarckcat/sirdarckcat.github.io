#!/usr/bin/env python3
"""bench_split.py on the CPU emulation (a small geometry, fake events): it must run every variant (gen, gen pass A, tile, tile without bins / small primes / both) and print its table.

    python3 test_bench_split_cpu.py
"""
import io, os, sys, time, types, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gbatch_cpu as TB

SPEC = os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")
ARGV = [SPEC, "--B", "20011", "--ks", "14", "--tile", "11", "--llog", "11", "--split", "2048", "--f", "0.9", "--rg", "4", "--rcta", "2", "--nthreads", "64", "--gen-threads", "64",
        "--tile-threads", "64", "--stage-cap", "512", "--ppt", "2", "--reps", "1", "--rows", "12"]


class Event:
    def record(self):
        self.t = time.perf_counter()

    def synchronize(self):
        pass


def main():
    cp = TG.install_fake_cupy()
    cp.RawModule = TB._RawModule
    cp.cuda = types.SimpleNamespace(Device=lambda: types.SimpleNamespace(synchronize=lambda: None), Event=Event, get_elapsed_time=lambda a, b: 1e3 * (b.t - a.t))
    import bench_split
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = bench_split.main(list(ARGV))
    txt = buf.getvalue()
    print(txt)
    need = ("gen (staged large-prime kernel)", "pass A (visits + counting)", "pass B (stage, flush)", "tile kernel", "small-prime marks", "bin apply", "init + write of the tiles", "SPLIT-DONE")
    ok = rc == 0 and all(s in txt for s in need)
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
