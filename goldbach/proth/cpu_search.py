#!/usr/bin/env python3
"""CPU fleet search: PRP-test sieve survivors from the top down, one slice
per machine, alongside the GPU search (which goes up from the bottom).

    python3 cpu_search.py spec.json survivors.json out_dir [--procs 8]
                          [--slice j/k] [--reload 600] [--done tests.jsonl ...]

Machine j of k takes the survivors t with t % k == j, in decreasing order,
and keeps --procs GMP Euler tests in flight (desert._test: base^((P-1)/2)
= -1 with the spec's non-residue base). Results go to out_dir/tests.jsonl
in desert.py's format plus "src": "cpu j/k". Every --reload seconds the
survivors file and the kill lists <survivors without .json>*.kills.json
are re-read (as gpu_search.py does), so deep-sieve kills relayed to this
machine drop candidates that are still queued. On a pass, desert.bls_prove
proves P here; the proof string goes to out_dir/hits.jsonl, and the run
stops. The record is then packaged elsewhere (gpu_hit.py re-proves it).
"""
import json
import os
import sys
import time
from multiprocessing import Pool

from gmpy2 import mpz

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desert  # noqa: E402
from gpu_search import kill_files, load_done, load_kills  # noqa: E402


def main():
    spec_path, surv_path, out_dir = sys.argv[1:4]
    opt = sys.argv[4:]
    get = lambda k, d: opt[opt.index(k) + 1] if k in opt else d
    procs, reload_s = int(get("--procs", 8)), float(get("--reload", 600))
    j, k = map(int, get("--slice", "0/1").split("/"))
    extra = [opt[i + 1] for i, a in enumerate(opt) if a == "--done"]
    os.makedirs(out_dir, exist_ok=True)
    log_path = f"{out_dir}/tests.jsonl"
    spec = json.load(open(spec_path))
    done = load_done([log_path] + extra)
    if any(done.values()):
        print("a hit is already recorded; nothing to do", flush=True)
        return

    def current():
        surv = json.load(open(surv_path))
        kills, seen = load_kills(kill_files(surv_path))
        todo = sorted((int(t) for t in surv if int(t) % k == j and int(t) not in done
                       and int(t) not in kills), reverse=True)
        return todo, os.path.getmtime(surv_path), seen

    todo, smt, kseen = current()
    print(f"slice {j}/{k}: {len(todo)} survivors to test top-down, {procs} procs", flush=True)
    t_start, last_reload = time.time(), time.time()
    inflight = {}
    with Pool(procs, initializer=desert._init_test,
              initargs=(spec["n"], spec["m0"], spec["Mc"], spec["base"])) as pool, \
            open(log_path, "a") as log:
        while todo or inflight:
            while todo and len(inflight) < procs:
                t = todo.pop(0)
                inflight[t] = pool.apply_async(desert._test, (t,))
            time.sleep(1)
            for t in [t for t, r in inflight.items() if r.ready()]:
                t_, ok, dt = inflight.pop(t).get()
                done[t_] = ok
                log.write(json.dumps({"t": t_, "ok": ok, "sec": round(dt, 2),
                                      "src": f"cpu {j}/{k}"}) + "\n")
                log.flush()
                print(f"  t={t_} ok={ok} {dt:.0f}s ({len(done)} logged, "
                      f"{time.time() - t_start:.0f}s elapsed)", flush=True)
                if ok:
                    pool.terminate()
                    m = mpz(spec["m0"]) + t_ * mpz(spec["Mc"])
                    P = (m << spec["n"]) + 1
                    how = desert.bls_prove(P, spec["base"])
                    with open(f"{out_dir}/hits.jsonl", "a") as fh:
                        fh.write(json.dumps({"t": t_, "proof": how, "src": f"cpu {j}/{k}"}) + "\n")
                    print(f"HIT t={t_}: {how}", flush=True)
                    return
            if time.time() - last_reload >= reload_s:
                last_reload = time.time()
                try:
                    if os.path.getmtime(surv_path) != smt or kill_files(surv_path) != kseen:
                        before = len(todo)
                        new, smt, kseen = current()
                        todo = [t for t in new if t not in inflight]
                        print(f"reloaded: {before} -> {len(todo)} queued", flush=True)
                except (OSError, ValueError) as e:
                    print(f"reload failed ({e}); keeping the queue", flush=True)
    print("NO HIT in this slice", flush=True)


if __name__ == "__main__":
    main()
