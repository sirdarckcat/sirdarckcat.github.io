"""Single top-level verifier for the prime-gap domination record.

Rebuilds everything from the committed artifacts and checks:
  1. N = N0 + k*M, its digit count, and every cover congruence.
  2. Every prime q < g has a valid compositeness witness for N - q
     (parity, congruence divisor, trial divisor, or strong base-2
     failure) -- witnesses.npz supplies the claimed type, each one is
     re-verified here from scratch.
  3. g is prime and exceeds the certified prime-gap record 1113106.
  4. The ECPP certificate binds: its top-level candidate equals N - g
     exactly, and PARI revalidates it (primecertisvalid = 1).  Run
     ecpp_check.py separately for the PARI-independent projective check.
  5. Local-gap audit: every interior number of the containing ordinary
     prime interval (N - 7329, N + 1641) is deterministically composite;
     endpoint ECPP certificates are bound and revalidated when present.
  6. Writes MANIFEST.sha256 over the record artifacts.

Usage: verify_megagap.py records/megagap_2692digit_g1134871
"""

import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import gmpy2
from gmpy2 import mpz, is_prime, is_strong_prp
from sympy import primerange

from ecpp_check import parse_cert

GAP_RECORD = 1113106
PREV_OFF, NEXT_OFF = 7329, 1641


def gp_validate(cert_path, expected):
    cert = parse_cert(cert_path)
    assert mpz(cert[0][0]) == expected, f"BINDING FAILURE for {cert_path}"
    # NB: default(parisize,...) reallocates the stack and discards the
    # rest of its input line, so every statement needs its own line.
    r = subprocess.run(
        ["gp", "-q"],
        input=f'default(parisize,3000000000);\n'
              f'c=read("{cert_path}");\nprint(primecertisvalid(c));\n',
        capture_output=True, text=True, timeout=36000)
    assert r.stdout.strip().splitlines()[-1] == "1", f"PARI rejects {cert_path}"


def main():
    outdir = sys.argv[1].rstrip("/")
    rec = json.load(open(f"{outdir}/record.json"))
    N = mpz(rec["N0"]) + rec["k"] * mpz(rec["M"])
    assert str(N) == rec["N"] and len(str(N)) == rec["digits"] == 2692
    g = rec["g"]
    for r, a in rec["cover"]:
        assert (N - a) % r == 0, f"cover congruence {r} fails"
    print(f"[1] N rebuilt: {rec['digits']} digits, {len(rec['cover'])} "
          f"congruences hold")

    w = np.load(f"{outdir}/witnesses.npz")
    qs, wtype, wval = w["q"], w["wtype"], w["wval"]
    expect = np.array(list(primerange(3, g)), dtype=np.int64)
    assert np.array_equal(qs, expect), "witness table misses primes"
    assert (N - 2) % 2 == 0
    n_mr = 0
    for q, t, v in zip(qs.tolist(), wtype.tolist(), wval.tolist()):
        m = N - q
        if t in (1, 2):
            assert v > 1 and m % v == 0 and m != v, f"bad divisor for q={q}"
        elif t == 3:
            n_mr += 1
            assert not is_strong_prp(m, 2), f"q={q}: strong-2 passes"
        elif t == 4:
            assert is_strong_prp(m, 2) and not is_prime(m)
        else:
            raise AssertionError(f"q={q}: no witness")
    print(f"[2] all {len(qs) + 1} prime offsets < g are non-summands "
          f"({n_mr} via strong base-2)")

    assert is_prime(g) and g > GAP_RECORD
    print(f"[3] g = {g} is prime and beats the certified gap record "
          f"{GAP_RECORD} by {g - GAP_RECORD}")

    gp_validate(f"{outdir}/complement_cert.gp", N - g)
    print(f"[4] ECPP certificate binds to N - g and PARI revalidates it")

    small = list(primerange(3, 100000))
    for x in range(int(N) - PREV_OFF + 1, int(N) + NEXT_OFF):
        if x % 2 == 0:
            continue
        m = mpz(x)
        if any(m % s == 0 for s in small):
            continue
        assert not is_strong_prp(m, 2), f"interior {x - int(N):+d} not composite"
    for ep, off in (("prev", -PREV_OFF), ("next", NEXT_OFF)):
        p = f"{outdir}/localgap_{ep}_cert.gp"
        if os.path.exists(p):
            gp_validate(p, N + off)
            print(f"[5] local-gap {ep} endpoint N{off:+d} ECPP-certified")
        else:
            assert is_prime(N + off)
            print(f"[5] local-gap {ep} endpoint N{off:+d} is a BPSW PRP "
                  f"(certificate pending)")
    print(f"[5] interior of ({-PREV_OFF}, +{NEXT_OFF}) around N is "
          f"deterministically composite: local gap = {PREV_OFF + NEXT_OFF}, "
          f"g/gap = {g / (PREV_OFF + NEXT_OFF):.1f}")

    manifest = []
    for f in sorted(os.listdir(outdir)):
        if f == "MANIFEST.sha256":
            continue
        h = hashlib.sha256(open(f"{outdir}/{f}", "rb").read()).hexdigest()
        manifest.append(f"{h}  {f}")
    open(f"{outdir}/MANIFEST.sha256", "w").write("\n".join(manifest) + "\n")
    print(f"[6] MANIFEST.sha256 written ({len(manifest)} files)")
    print("ALL CHECKS PASSED: g(N) = %d > %d" % (g, GAP_RECORD))


if __name__ == "__main__":
    main()
