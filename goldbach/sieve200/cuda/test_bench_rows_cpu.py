#!/usr/bin/env python3
"""bench_rows.py on the CPU emulation (a small geometry, fake events): every variant of the survivor-list step must run and the two-step lists must equal the production kernel's.

    python3 test_bench_rows_cpu.py
"""
import io, os, sys, time, types, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG

ARGV = ["--klog", "13", "--llog", "11", "--rows", "70", "--f", "0.9", "--reps", "1", "--threads", "64"]


class Event:
    def record(self):
        self.t = time.perf_counter()

    def synchronize(self):
        pass


def main():
    cp = TG.install_fake_cupy()
    cp.cuda = types.SimpleNamespace(Device=lambda: types.SimpleNamespace(synchronize=lambda: None), Event=Event, get_elapsed_time=lambda a, b: 1e3 * (b.t - a.t))
    cp.empty_like = lambda a: cp.empty(a.shape, a.dtype)
    cp.full_like = lambda a, v: __import__('numpy').full(a.shape, v, a.dtype)
    import bench_rows
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = bench_rows.main(list(ARGV))
    txt = buf.getvalue()
    print(txt)
    need = ("count (reference)", "rows (production, serial)", "rows2 (16 loads in flight)", "rows, no stores (reads only)", "rows, no loads (writes only)", "rowmask (reads, coalesced masks)", "rowlist (writes from masks)",
            "rowmask + rowlist", "rows_ord (by index, serial)", "rows_ord2 (by index, 8 in flight)", "rows_ord, no stores (reads only)", "s200g_rows_ord lists identical to rows: True",
            "s200g_rows_ord2 lists identical to rows: True", "rowmask + rowlist lists identical to rows: True", "ROWS-DONE")
    ok = rc == 0 and all(s in txt for s in need)
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
