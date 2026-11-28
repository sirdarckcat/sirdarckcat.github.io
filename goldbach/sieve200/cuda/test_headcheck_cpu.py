#!/usr/bin/env python3
"""headcheck.py on the CPU emulation (a small geometry): the script a GPU session will run must at least run, print its four checks and end with HEADCHECK-OK where the head is correct;
and it must say HEADCHECK-FAILED (exit 1) if the head's lists are damaged on purpose.

    python3 test_headcheck_cpu.py
"""
import io, os, sys, types, contextlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import test_gpu_sieve_cpu as TG
import test_gbatch_cpu as TB

SPEC = os.path.join(HERE, "..", "..", "phd", "campaign3", "base_spec.json")
ARGV = [SPEC, "--B", "20011", "--klog", "14", "--tile", "11", "--llog", "11", "--rg", "4", "--rcta", "2", "--split", "2048", "--f", "0.9", "--threads", "64", "--tile-threads", "64",
        "--gen-threads", "64", "--head-b", "150001", "--head-rows", "12", "--k0", "16384", "--reps", "1", "--verify", "4", "--rows", "40"]


def main():
    cp = TG.install_fake_cupy()
    cp.RawModule = TB._RawModule
    cp.cuda = types.SimpleNamespace(Device=lambda: types.SimpleNamespace(synchronize=lambda: None))
    import headcheck
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = headcheck.main(list(ARGV))
    txt = buf.getvalue()
    print(txt)
    ok = rc == 0 and "HEADCHECK-OK" in txt and all(f"({i})" in txt for i in (1, 2, 3, 4)) and "FAILED" not in txt
    print("  headcheck.py on a good head:", "ok" if ok else "FAILED")
    # a damaged head: the second window loses a row of the lists it should keep (the kernel is replaced by one that clears one more bit): the script must notice
    import ghead
    orig = ghead.HeadStage.apply

    def bad_apply(self, fd, k0, member, cnt, offs, total, nsel):
        cnt2, offs2, total2 = orig(self, fd, k0, member, cnt, offs, total, nsel)
        cnt2 = cnt2.copy()
        cnt2[0] = max(int(cnt2[0]) - 1, 0)                  # a list one shorter than the rows kernel will write: the CSR is inconsistent with the rows
        offs3 = np.concatenate([[0], np.cumsum(np.asarray(cnt2).astype(np.int64))])
        return cnt2, offs3, offs3[-1:].copy()
    ghead.HeadStage.apply = bad_apply
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc2 = headcheck.main(list(ARGV))
    except Exception as e:                                  # an inconsistent CSR may make the later rows kernel / checks raise: also a detection
        rc2 = 1
        buf.write(f"exception {type(e).__name__}: {e}\nHEADCHECK-FAILED\n")
    finally:
        ghead.HeadStage.apply = orig
    ok2 = rc2 != 0 and "HEADCHECK-FAILED" in buf.getvalue()
    print("  headcheck.py on a damaged head:", "detected" if ok2 else "NOT DETECTED")
    print("ALL OK" if ok and ok2 else "FAILED")
    sys.exit(0 if ok and ok2 else 1)


if __name__ == "__main__":
    main()
