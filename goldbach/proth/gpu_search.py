#!/usr/bin/env python3
"""GPU search driver: screen desert.py sieve survivors in batches.

    python3 gpu_search.py spec.json survivors.json out_dir [--batch 512]
                          [--done tests.jsonl ...]

Takes the survivors (from desert.sieve_candidates) in increasing t, skipping
any t already recorded in out_dir/tests.jsonl or in a --done log (e.g. the
CPU search's), and screens a batch at a time on the GPU (gpu_screen.py). Every
result is appended to out_dir/tests.jsonl in desert.py's format, plus
"src": "gpu". A GPU pass means 2^((P-1)/2) = 1 (mod P), a probable prime; it
is written to out_dir/hits.jsonl, and the run stops after that batch. The
proof is always redone on the CPU with desert.bls_prove before anything is
called a record.

The survivors file is re-read between batches whenever its mtime changes,
so deep_sieve.py can keep deepening the sieve while the search runs (it
rewrites the file atomically); the next batch is always the smallest
untested t of the current list. Kill lists ([t, p] pairs, deep_sieve.py's
.kills.json format) named <survivors without .json>*.kills.json are
subtracted too, and re-read the same way: that is how a sieve run on
another machine reaches this search.
"""
import glob
import json
import os
import sys
import time

import gmpy2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpu_screen as gs  # noqa: E402


def load_done(paths):
    done = {}
    for p in paths:
        if os.path.exists(p):
            for line in open(p):
                if line.strip():
                    d = json.loads(line)
                    done[int(d["t"])] = bool(d["ok"])
    return done


def kill_files(surv_path):
    base = surv_path[:-5] if surv_path.endswith(".json") else surv_path
    return {p: os.path.getmtime(p) for p in sorted(glob.glob(base + "*.kills.json"))}


def load_kills(files):
    """Union of the kill lists; returns (kills, files seen). A list that cannot
    be read is recorded with mtime None, so the next scan retries it."""
    ks, seen = set(), {}
    for p, mt in files.items():
        try:
            ks.update(int(t) for t, _ in json.load(open(p)))
            seen[p] = mt
        except (OSError, ValueError, TypeError) as e:
            print(f"kill list {p} unreadable ({e}); will retry", flush=True)
            seen[p] = None
    return ks, seen


def main():
    spec_path, surv_path, out_dir = sys.argv[1:4]
    opt = sys.argv[4:]
    batch = int(opt[opt.index("--batch") + 1]) if "--batch" in opt else 512
    extra = [opt[i + 1] for i, a in enumerate(opt) if a == "--done"]
    os.makedirs(out_dir, exist_ok=True)
    log_path = f"{out_dir}/tests.jsonl"
    spec = json.load(open(spec_path))
    surv_mtime = os.path.getmtime(surv_path)
    surv = sorted(int(t) for t in json.load(open(surv_path)))
    done = load_done([log_path] + extra)
    if any(done.values()):
        print("a hit is already recorded; nothing to do", flush=True)
        return
    tested = set(done)
    kills, kfiles = load_kills(kill_files(surv_path))
    todo = [t for t in surv if t not in tested and t not in kills]
    print(f"{len(surv)} survivors, {len(kills)} sieve kills listed, {len(done)} already "
          f"tested, {len(todo)} to go; batch {batch}", flush=True)
    while todo:
        ts = todo[:batch]
        t0 = time.time()

        def progress(k, K, err):
            print(f"  batch t={ts[0]}..{ts[-1]}: step {k}/{K}, "
                  f"{time.time() - t0:.0f}s, max err {err:.1e}", flush=True)

        flags, err, _ = gs.screen(spec, ts, gmpy2, progress=progress)
        per = (time.time() - t0) / len(ts)
        hits = [t for t in ts if flags[t]]
        with open(log_path, "a") as fh:
            for t in ts:
                fh.write(json.dumps({"t": t, "ok": flags[t], "sec": round(per, 3),
                                     "src": "gpu"}) + "\n")
        print(f"batch done: {len(ts)} tests in {time.time() - t0:.0f}s "
              f"({per:.2f} s/test), max err {err:.1e}, hits {hits}", flush=True)
        if hits:
            with open(f"{out_dir}/hits.jsonl", "a") as fh:
                for t in hits:
                    fh.write(json.dumps({"t": t, "screen": "2^((P-1)/2)=1"}) + "\n")
            print(f"HIT {hits}", flush=True)
            return
        tested.update(ts)
        try:
            mt = os.path.getmtime(surv_path)
            if mt != surv_mtime:
                new = sorted(int(t) for t in json.load(open(surv_path)))
                surv, surv_mtime = new, mt
                print(f"survivors file changed: now {len(surv)} survivors", flush=True)
        except (OSError, ValueError) as e:
            print(f"survivors reload failed ({e}); keeping the current list", flush=True)
        try:
            kf = kill_files(surv_path)
            if kf != kfiles:
                kills, kfiles = load_kills(kf)
                print(f"kill lists changed: {len(kills)} kills from {len(kf)} files", flush=True)
        except OSError as e:
            print(f"kill list scan failed ({e}); keeping the current kills", flush=True)
        todo = [t for t in surv if t not in tested and t not in kills]
    print("NO HIT in survivors; extend T", flush=True)


if __name__ == "__main__":
    main()
