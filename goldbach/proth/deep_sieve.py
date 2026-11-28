#!/usr/bin/env python3
"""Deepen a desert.py sieve with the C sieve (deepsieve.c), streaming.

    python3 deep_sieve.py spec.json survivors.json B0 B1 out.json
                          [--threads 10] [--bin ./deepsieve] [--every 300]

desert.py sieves P_t = 2^n (m0 + t Mc) + 1 by the primes below B (1e9 in
the runs here).  This runs deepsieve over the primes p in [B0, B1) and drops
every survivor t that some such p divides.  Nothing from the C code is
trusted: each reported pair is re-checked here by building P_t in gmpy2 and
testing P_t % p == 0 (with 1 < p < P_t, that alone proves P_t composite).
Every --every seconds, and at the end, the remaining survivors are written
atomically to out.json (same format as desert.py's survivors file, so a
gpu_search.py that reloads its survivors file picks them up mid-run), and
the eliminations, as [t, p] pairs, to out.json's ".kills.json" sibling.
The sieve is only an accelerator: a wrong kill could at worst skip a prime
t, never certify anything.
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

import gmpy2
from gmpy2 import mpz

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))


def limbs(x):
    x = int(x)
    b = x.to_bytes((x.bit_length() + 63) // 64 * 8, "little")
    return len(b) // 8, b


def atomic_json(obj, path):
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(obj, fh)
    os.replace(tmp, path)


def main():
    spec_path, surv_path, B0, B1, out = sys.argv[1:6]
    B0, B1 = int(float(B0)), int(float(B1))
    opt = sys.argv[6:]
    get = lambda k, d: opt[opt.index(k) + 1] if k in opt else d
    threads, exe, every = int(get("--threads", 10)), get("--bin", f"{HERE}/deepsieve"), float(get("--every", 300))
    spec = json.load(open(spec_path))
    n, m0, Mc = spec["n"], mpz(spec["m0"]), mpz(spec["Mc"])
    surv = sorted(int(t) for t in json.load(open(surv_path)))
    T = 1 << spec["tbits"]
    T = max(surv) + 1 if surv else 1                 # only t < T matter
    alive = set(surv)
    kills_path = out[:-5] + ".kills.json" if out.endswith(".json") else out + ".kills.json"
    kills = json.load(open(kills_path)) if os.path.exists(kills_path) else []
    for t, p in kills:
        alive.discard(t)
    La, ba = limbs(m0)
    Lc, bc = limbs(Mc)
    inp = os.path.join(os.path.dirname(os.path.abspath(out)), f".deepsieve_{os.getpid()}.bin")
    with open(inp, "wb") as fh:
        for v in (n, T, B0, B1, La, Lc):
            fh.write(int(v).to_bytes(8, "little"))
        fh.write(ba)
        fh.write(bc)
    print(f"deep sieve: {len(surv)} survivors (t < {T}), primes in [{B0:.3g}, {B1:.3g}), "
          f"{threads} threads", flush=True)
    proc = subprocess.Popen([exe, inp, str(threads)], stdout=subprocess.PIPE, text=True)
    pending, lock, bad = [], threading.Lock(), []

    def reader():
        for line in proc.stdout:
            t, p = map(int, line.split())
            with lock:
                pending.append((t, p))
    th = threading.Thread(target=reader, daemon=True)
    th.start()

    def flush(final=False):
        with lock:
            batch = pending[:]
            del pending[:]
        newk = 0
        for t, p in batch:
            if t not in alive:
                continue
            P = ((m0 + t * Mc) << n) + 1
            if 1 < p < P and P % p == 0:
                alive.discard(t)
                kills.append([t, p])
                newk += 1
            else:
                bad.append([t, p])
        atomic_json(sorted(alive), out)
        atomic_json(sorted(kills), kills_path)
        print(f"  {time.strftime('%H:%M:%S')} {'final' if final else 'flush'}: +{newk} kills "
              f"(checked {len(batch)} pairs), {len(alive)} survivors left, bad pairs {len(bad)}",
              flush=True)

    last = time.time()
    while proc.poll() is None:
        time.sleep(2)
        if time.time() - last >= every:
            flush()
            last = time.time()
    th.join()
    flush(final=True)
    os.remove(inp)
    if proc.returncode != 0 or bad:
        print(f"deepsieve exit {proc.returncode}; bad pairs: {bad[:10]}", flush=True)
        sys.exit(1)
    print(f"DONE: {len(surv)} -> {len(alive)} survivors after primes < {B1:.3g}", flush=True)


if __name__ == "__main__":
    main()
