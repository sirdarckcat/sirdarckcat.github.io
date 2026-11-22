#!/usr/bin/env python3
"""Run one of the bls/ verifiers unchanged, except for its modular exponentiation.

    python3 divmod_pow_run.py xverify|verify_bls_record record.json [--ckdir DIR]

The module's global name `pow` is bound to `dpow` below; the builtin is
untouched everywhere else. `dpow` is still pure Python ints, but it reduces
with divmod(), which on CPython >= 3.12 goes through _pylong's subquadratic
division. Python's 3-arg pow and `x % P` use schoolbook division. On a
203,731-bit P this was 20.6 ms per step against 79.6 ms here (the other
session measured 15.2 against 68.2), so a ~4.5 h leg takes ~1.3 h.

Moduli under 4,096 bits, negative exponents (inverses) and 2-arg calls go
to the builtin. Large exponentiations save (bit index, x) to a checkpoint
file in --ckdir every 10 minutes, keyed by a hash of (b, e, m), so a run
killed with its runtime resumes where it stopped.
"""
import builtins
import hashlib
import importlib
import json
import os
import sys
import time

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
_bpow = builtins.pow
CKDIR = "."
EVERY = float(os.environ.get("DPOW_CKPT_SECONDS", 600))


def dpow(b, e, m=None):
    if m is None or e < 0 or m.bit_length() < 4096:
        return _bpow(b, e) if m is None else _bpow(b, e, m)
    if e == 0:
        return 1 % m
    key = hashlib.sha256(b"%x|%x|%x" % (b, e, m)).hexdigest()[:24]
    ck = os.path.join(CKDIR, f"dpow_{key}.json")
    bits = bin(e)[3:]                      # the bits after the leading 1
    b %= m
    x, i = b, 0
    if os.path.exists(ck):
        d = json.load(open(ck))
        x, i = int(d["x"], 16), d["i"]
        print(f"[dpow] resumed at bit {i}/{len(bits)} from {ck}", file=sys.stderr, flush=True)
    t0 = last = time.time()
    while i < len(bits):
        x = divmod(x * x, m)[1]
        if bits[i] == "1":
            x = divmod(x * b, m)[1]
        i += 1
        if time.time() - last >= EVERY:
            with open(ck + ".tmp", "w") as fh:
                json.dump({"i": i, "x": "%x" % x}, fh)
            os.replace(ck + ".tmp", ck)
            last = time.time()
            print(f"[dpow] bit {i}/{len(bits)}, {last - t0:.0f}s", file=sys.stderr, flush=True)
    return x


def main():
    global CKDIR
    name, path = sys.argv[1], sys.argv[2]
    if "--ckdir" in sys.argv:
        CKDIR = sys.argv[sys.argv.index("--ckdir") + 1]
    if name not in ("xverify", "verify_bls_record"):
        sys.exit("verifier must be xverify or verify_bls_record")
    sys.path.insert(0, os.path.join(HERE, "..", "bls"))
    mod = importlib.import_module(name)
    mod.pow = dpow                         # shadows the builtin inside that module only
    mod.main(path)


if __name__ == "__main__":
    main()
