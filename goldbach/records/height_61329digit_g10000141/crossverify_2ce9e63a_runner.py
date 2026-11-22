#!/usr/bin/env python3
"""Run goldbach/bls/xverify.py unchanged, except for how its one big modular
exponentiation is computed: a square-and-multiply loop on Python ints that
reduces with divmod() and checkpoints to disk, so it can span processes.

CPython's three-argument pow() reduces by schoolbook division; divmod() of
large ints goes through the subquadratic _pylong division instead, which is
about 4.5x faster per step at 200,000 bits.  Both are pure Python ints.

    python3 -I crossverify_2ce9e63a_runner.py <bls record.json> <checkpoint.json> <seconds>

<bls record.json> comes from `proth/interop.py to-bls record.json out.json`.  The run
stops with exit code 3 and a checkpoint after <seconds>; the same command resumes it.
This is the file used for crossverify_2ce9e63a.log, with the path to bls/ made relative.
"""
import hashlib, json, os, sys, time

sys.set_int_max_str_digits(0)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "bls"))
import xverify  # noqa: E402

T0 = time.time()


def rpow(b, e, m, ckpt=None, budget=None):
    ckpt = ckpt or sys.argv[2]
    budget = budget if budget is not None else float(sys.argv[3])
    key = hashlib.sha256(f"{b}:{e:x}:{m:x}".encode()).hexdigest()
    bits = bin(e)[2:]
    i, x, spent = 0, 1, 0.0
    if os.path.exists(ckpt):
        c = json.load(open(ckpt))
        assert c["key"] == key, "checkpoint belongs to another computation"
        i, x, spent = c["i"], int(c["x"], 16), c["seconds"]
        print(f"resuming at bit {i} of {len(bits)} ({spent:.0f}s spent so far)", flush=True)
    start = last = time.time()

    def save():
        json.dump({"key": key, "i": i, "of": len(bits), "x": hex(x),
                   "seconds": spent + time.time() - start}, open(ckpt + ".tmp", "w"))
        os.replace(ckpt + ".tmp", ckpt)

    while i < len(bits):
        x = divmod(x * x, m)[1]
        if bits[i] == "1":
            x = x * b % m
        i += 1
        if not i & 63:
            now = time.time()
            if now - last > 300:
                save(); last = now
            if now - T0 > budget:
                save()
                print(f"PAUSED at bit {i} of {len(bits)}, {spent + now - start:.0f}s spent", flush=True)
                sys.exit(3)
    save()
    print(f"modexp done: {len(bits)} squarings, {spent + time.time() - start:.0f}s in all "
          f"(python int, square-and-multiply, divmod reduction)", flush=True)
    return x


if __name__ == "__main__":
    xverify.pow = rpow
    xverify.main(sys.argv[1])
