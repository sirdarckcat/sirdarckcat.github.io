"""Record-format adapters between this directory and the independent second
verification stack in goldbach/bls/, so that each stack's verifier can check
every record.

    python3 interop.py to-bls   ../records/<dir>/record.json  out.json
    python3 interop.py from-bls <their record.json>        out.json

The two pipelines build the same kind of object.  The only structural
difference: theirs requires 2^n to divide P - 1 *exactly* and stores the
progression offset i, so a record from here is exported with n := v, the
full power of two in P - 1 (their verifier then rebuilds N from the
congruences by CRT and compares it with the stored decimal).
"""
import json
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def from_bls(src, dst):
    r = json.load(open(src))
    json.dump({"g": r["g"], "Q": r["Q"], "digits": r["digits_N"], "base": r["bls_base"],
               "cover": [[2, 0]] + [list(x) for x in r["cover"]], "N": r["N"],
               "proof": "BLS (imported from the goldbach/bls format)"}, open(dst, "w"))


def to_bls(src, dst):
    r = json.load(open(src))
    N, g = int(r["N"]), r["g"]
    P = N - g
    v = ((P - 1) & -(P - 1)).bit_length() - 1
    cover = [list(x) for x in r["cover"] if x[0] != 2]
    M = 1
    for m, _ in cover:
        M *= m
    L = (1 << (v + 1)) * M
    json.dump({"game": "exported from goldbach/proth", "Q": r["Q"], "g": g, "n": v,
               "i": P // L, "bls_base": r["base"], "digits_N": len(str(N)),
               "digits_P": len(str(P)), "congruences": len(cover) + 1,
               "r_max": max(m for m, _ in cover),
               "two_adic": [v + 1, g + 1 + (1 << v)], "cover": cover, "N": str(N)},
              open(dst, "w"))


if __name__ == "__main__":
    {"to-bls": to_bls, "from-bls": from_bls}[sys.argv[1]](sys.argv[2], sys.argv[3])
