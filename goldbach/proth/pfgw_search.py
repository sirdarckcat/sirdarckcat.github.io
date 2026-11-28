#!/usr/bin/env python3
"""CPU fleet search with OpenPFGW: cpu_search.py with each probable-prime test run by PFGW
(gwnum FFT arithmetic) instead of GMP.

    python3 pfgw_search.py spec.json survivors.json out_dir --pfgw /path/to/pfgw64
                           [--procs 4] [--slice j/k] [--reload 600] [--done tests.jsonl ...]

Machine j of k takes the survivors t with t % k == j, in decreasing order, skipping t already
in out_dir/tests.jsonl or a --done file and t in any <survivors without .json>*.kills.json
(re-read every --reload seconds, as in cpu_search.py and gpu_search.py). It keeps --procs PFGW
processes in flight, each in its own directory out_dir/w<i>/: PFGW keeps a resume file,
pfgw.ini, in its working directory, and it is deleted before every test so that a reused
input file is never "resumed" past its only line. PFGW tests P_t = (m0 + t Mc) 2^n + 1 for
base-3 Fermat probable primality. Results go to out_dir/tests.jsonl in the format of
cpu_search.py, with "src": "pfgw j/k".

PFGW is only a screen. A PRP verdict is re-checked here with GMP: desert.bls_prove(P, base)
runs the spec's Euler test base^((P-1)/2) = -1 and the BLS N-1 proof; only if both pass does
the t go to out_dir/hits.jsonl, and the run stops. PFGW output that is neither "composite"
nor "PRP" is retried once with the next larger FFT (-a1); if that fails too, the t goes to
out_dir/errors.jsonl and is not counted as tested.
"""
import json
import os
import re
import subprocess
import sys
import time

from gmpy2 import mpz

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desert  # noqa: E402
from gpu_search import kill_files, load_done, load_kills  # noqa: E402


def start(pfgw, wdir, spec, t, extra=()):
    for f in ("pfgw.ini", "pfgw.log", "pfgw-prime.log", "out.txt"):
        if os.path.exists(f"{wdir}/{f}"):
            os.remove(f"{wdir}/{f}")
    m = mpz(spec["m0"]) + t * mpz(spec["Mc"])
    with open(f"{wdir}/in.txt", "w") as fh:
        fh.write(f"{m}*2^{spec['n']}+1\n")
    out = open(f"{wdir}/out.txt", "wb")
    return subprocess.Popen([pfgw, "-f0", *extra, "in.txt"], cwd=wdir, stdout=out,
                            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)


def verdict(wdir):
    """(True for PRP / False for composite / None, tail of the verdict line, PFGW's seconds)."""
    txt = open(f"{wdir}/out.txt", "rb").read().decode("latin-1").replace("\r", "\n")
    lines = [ln for ln in txt.split("\n") if ln.strip()]
    for ln in reversed(lines):
        tail = ln[-160:]
        sec = re.search(r"\(([\d.]+)s\+", tail)
        sec = float(sec.group(1)) if sec else None
        if "composite" in tail:
            return False, tail, sec
        if "PRP!" in tail:
            return True, tail, sec
    return None, (lines[-1][-160:] if lines else "(no output)"), None


def main():
    spec_path, surv_path, out_dir = sys.argv[1:4]
    opt = sys.argv[4:]
    get = lambda k, d: opt[opt.index(k) + 1] if k in opt else d
    pfgw = get("--pfgw", None)
    if not pfgw or not os.access(pfgw, os.X_OK):
        sys.exit("--pfgw must name the pfgw64 executable")
    procs, reload_s = int(get("--procs", 4)), float(get("--reload", 600))
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
    print(f"slice {j}/{k}: {len(todo)} survivors to test top-down, {procs} PFGW processes",
          flush=True)
    t_start, last_reload = time.time(), time.time()
    inflight, free = {}, list(range(procs))          # worker -> (t, process, start, tries)
    with open(log_path, "a") as log:
        while todo or inflight:
            while todo and free:
                w, t = free.pop(), todo.pop(0)
                os.makedirs(f"{out_dir}/w{w}", exist_ok=True)
                inflight[w] = (t, start(pfgw, f"{out_dir}/w{w}", spec, t), time.time(), 1)
            time.sleep(1)
            for w in [w for w, v in inflight.items() if v[1].poll() is not None]:
                t, _, t0, tries = inflight.pop(w)
                ok, tail, sec = verdict(f"{out_dir}/w{w}")
                if ok is None and tries == 1:
                    print(f"  t={t}: no verdict ({tail!r}); retrying with -a1", flush=True)
                    inflight[w] = (t, start(pfgw, f"{out_dir}/w{w}", spec, t, ["-a1"]),
                                   time.time(), 2)
                    continue
                free.append(w)
                if ok is None:
                    print(f"  t={t}: no verdict twice; logged as an error, not as tested", flush=True)
                    with open(f"{out_dir}/errors.jsonl", "a") as fh:
                        fh.write(json.dumps({"t": t, "tail": tail}) + "\n")
                    continue
                dt = sec if sec is not None else time.time() - t0
                if ok:
                    print(f"  t={t}: PFGW says PRP ({tail!r}); proving with GMP", flush=True)
                    m = mpz(spec["m0"]) + t * mpz(spec["Mc"])
                    P = (m << spec["n"]) + 1
                    try:
                        how = desert.bls_prove(P, spec["base"])
                    except AssertionError as e:
                        print(f"  t={t}: GMP check failed ({e}); composite after all", flush=True)
                        ok = False
                    else:
                        log.write(json.dumps({"t": t, "ok": True, "sec": round(dt, 2),
                                              "src": f"pfgw {j}/{k}"}) + "\n")
                        log.flush()
                        for _, p, _, _ in inflight.values():
                            p.kill()
                        with open(f"{out_dir}/hits.jsonl", "a") as fh:
                            fh.write(json.dumps({"t": t, "proof": how, "src": f"pfgw {j}/{k}"}) + "\n")
                        print(f"HIT t={t}: {how}", flush=True)
                        return
                done[t] = ok
                log.write(json.dumps({"t": t, "ok": ok, "sec": round(dt, 2),
                                      "src": f"pfgw {j}/{k}"}) + "\n")
                log.flush()
                print(f"  t={t} ok={ok} {dt:.0f}s ({len(done)} logged, "
                      f"{time.time() - t_start:.0f}s elapsed)", flush=True)
            if time.time() - last_reload >= reload_s:
                last_reload = time.time()
                try:
                    if os.path.getmtime(surv_path) != smt or kill_files(surv_path) != kseen:
                        before = len(todo)
                        new, smt, kseen = current()
                        busy = {v[0] for v in inflight.values()}
                        todo = [t for t in new if t not in busy]
                        print(f"reloaded: {before} -> {len(todo)} queued", flush=True)
                except (OSError, ValueError) as e:
                    print(f"reload failed ({e}); keeping the queue", flush=True)
    print("NO HIT in this slice", flush=True)


if __name__ == "__main__":
    main()
