"""Exhaustive prime count over sieve survivors (no early stop), against the
density model  1 prime per  ln P / (e^gamma ln B)  tests.

    python3 probe.py spec.json out.jsonl [--T 16384] [--sieve 1e9]
                     [--exclude tested.json] [--limit K] [--procs 4]

`--exclude` is a JSON list of offsets t already tested elsewhere, so the
probe can be made out-of-sample.  Resumable: results append to out.jsonl.
(Successor of the independent session's bls/density_probe.py, which measured
the same thing on its own progression and is in the history at 6c66bcd.)
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desert  # noqa: E402

EG = math.exp(0.5772156649015329)


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    T = int(opt.get("--T", 16384))
    B = int(float(opt.get("--sieve", 1e9)))
    procs = int(opt.get("--procs", os.cpu_count()))
    excl = set(json.load(open(opt["--exclude"]))) if "--exclude" in opt else set()
    surv = [int(t) for t in desert.sieve_candidates(spec, T, B, procs)]
    cand = [t for t in surv if t not in excl]
    if "--limit" in opt:
        cand = cand[: int(opt["--limit"])]
    done = {}
    if os.path.exists(out):
        for line in open(out):
            d = json.loads(line)
            done[d["t"]] = d["ok"]
    todo = [t for t in cand if t not in done]
    rate = EG * math.log(B) / (spec["P_bits_est"] * math.log(2))
    print(f"{len(surv)} survivors of {T} (sieve {B:.0e}); {len(excl & set(surv))} excluded; "
          f"{len(cand)} to probe, {len(done)} already done; model: 1 prime per {1 / rate:.0f}", flush=True)
    t0 = time.time()
    with Pool(procs, initializer=desert._init_test,
              initargs=(spec["n"], spec["m0"], spec["Mc"], spec["base"])) as pool, open(out, "a") as log:
        for k, (t, ok, dt) in enumerate(pool.imap_unordered(desert._test, todo, chunksize=1), 1):
            done[t] = ok
            log.write(json.dumps({"t": t, "ok": ok, "sec": round(dt, 2)}) + "\n")
            log.flush()
            if k % 100 == 0 or ok:
                print(f"  {k}/{len(todo)}  primes so far {sum(done.values())}  "
                      f"{'PRIME at t=%d  ' % t if ok else ''}{time.time() - t0:.0f}s", flush=True)
    n = sum(1 for t in cand if t in done)
    hits = sorted(t for t in cand if done.get(t))
    exp = n * rate
    z = (len(hits) - exp) / math.sqrt(exp) if exp else float("nan")
    print(f"probed {n} candidates: {len(hits)} primes at t = {hits}; model {exp:.2f}; z = {z:+.2f}")


if __name__ == "__main__":
    main()
