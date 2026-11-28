#!/usr/bin/env python3
"""The gate of the deep head (search_gpu5_head.patch): two runs of the SAME windows, with and without --deep-head-b, dump per-member results (--dump-members); this compares them.

    python3 compare_dumps.py PREFIX_BASE PREFIX_HEAD          # PREFIX.<n>.npz, n = 0, 1, 2 ... of each run

Per flush file n (the flush boundaries depend on the number of kept members only, so they are the same in both runs): the members (sid = the variant of the batch, k) must be the same set, and for every member
the first-PRP row (a local row index of the variant), the success flag must be IDENTICAL; only the counted tests may differ (fewer with the head: the composite head rows are gone from the lists).
Prints the counted tests of both runs and the fall, the successes and the near-miss candidates (first-PRP rows at or beyond --near-row) of each run.  Exit status 0 only if every file matches.
"""
import argparse, glob, os, sys
import numpy as np


def load(prefix, n):
    p = f"{prefix}.{n}.npz"
    if not os.path.exists(p):
        return None
    z = np.load(p)
    o = np.lexsort((z["k"], z["sid"]))
    return {name: z[name][o] for name in ("sid", "k", "frow", "succ", "tests")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("head")
    ap.add_argument("--near-row", type=int, default=1000, help="local row index from which a first-PRP row counts as a near-miss candidate (report only)")
    a = ap.parse_args()
    nb = len(glob.glob(f"{a.base}.*.npz"))
    nh = len(glob.glob(f"{a.head}.*.npz"))
    print(f"{nb} flush files in the base run, {nh} in the head run")
    ok = nb == nh and nb > 0
    n_members = n_succ_b = n_succ_h = n_near_b = n_near_h = 0
    tests_b = tests_h = 0
    bad_files = 0
    for n in range(min(nb, nh)):
        b, h = load(a.base, n), load(a.head, n)
        same = (b["sid"].size == h["sid"].size and np.array_equal(b["sid"], h["sid"]) and np.array_equal(b["k"], h["k"]) and np.array_equal(b["frow"], h["frow"]) and np.array_equal(b["succ"], h["succ"]))
        if not same:
            bad_files += 1
            if bad_files <= 5:
                if b["sid"].size != h["sid"].size or not np.array_equal(b["k"], h["k"]) or not np.array_equal(b["sid"], h["sid"]):
                    print(f"  flush {n}: DIFFERENT MEMBERS ({b['sid'].size} against {h['sid'].size}); the runs did not test the same windows")
                else:
                    d = np.nonzero((b["frow"] != h["frow"]) | (b["succ"] != h["succ"]))[0]
                    print(f"  flush {n}: {d.size} members differ in first-PRP row / success, e.g. sid {b['sid'][d[0]]} k {b['k'][d[0]]}: frow {b['frow'][d[0]]} against {h['frow'][d[0]]}, succ {bool(b['succ'][d[0]])} against {bool(h['succ'][d[0]])}")
        n_members += b["sid"].size
        n_succ_b += int(b["succ"].sum())
        n_succ_h += int(h["succ"].sum())
        n_near_b += int((b["frow"] >= a.near_row).sum())
        n_near_h += int((h["frow"] >= a.near_row).sum())
        tests_b += int(b["tests"].sum(dtype=np.int64))
        tests_h += int(h["tests"].sum(dtype=np.int64))
    ok &= bad_files == 0
    print(f"{n_members:,} members in {min(nb, nh)} files; successes {n_succ_b} / {n_succ_h}; first-PRP row >= {a.near_row}: {n_near_b} / {n_near_h} (base / head)")
    if tests_b:
        print(f"counted tests {tests_b:,} (base) -> {tests_h:,} (head): {100 * (1 - tests_h / tests_b):.2f}% fewer")
    print("DUMPS-IDENTICAL" if ok else f"DUMPS-DIFFER ({bad_files} files)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
