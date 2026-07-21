"""Evidence + local-gap audit for a mega Goldbach-desert record.

For every prime q < g: assign a compositeness witness for N - q
  - parity (q = 2)
  - congruence divisor r from the cover (r | N - q since q = N mod r)
  - small trial divisor s (q = N mod s for a sieve prime s)
  - strong base-2 Miller-Rabin witness (unconditional compositeness)
  - bpsw (rare: strong-2 pseudoprime caught by the Lucas half)
Then audit the ordinary prime gap around N: the point of the record is
that g(N) vastly exceeds the local prime-free interval, proving the
desert comes from covering prime offsets only.

Usage: mega_verify.py found.json spec.json outdir/
"""

import json
import math
import os
import sys

import numpy as np
import gmpy2
from gmpy2 import mpz, is_prime, is_strong_prp, powmod
from sympy import primerange

TRIAL_B = 2_000_000


def main():
    found = json.load(open(sys.argv[1]))
    spec = json.load(open(sys.argv[2]))
    outdir = sys.argv[3]
    os.makedirs(outdir, exist_ok=True)

    N = mpz(found["N"])
    g = found["g"]
    assert N % 2 == 0
    assert mpz(spec["N0"]) + found["k"] * mpz(spec["M"]) == N

    qs = np.array(list(primerange(3, g)), dtype=np.int64)
    wtype = np.zeros(len(qs), dtype=np.int8)     # 0=none 1=cong 2=trial 3=mr2 4=bpsw
    wval = np.zeros(len(qs), dtype=np.int64)

    # congruence witnesses from the cover
    for r, a in spec["cover"]:
        hit = (wtype == 0) & (qs % r == a % r)
        # r | N - q for those q by construction; spot-check one
        idx = np.nonzero(hit)[0]
        if len(idx):
            assert (N - int(qs[idx[0]])) % r == 0
            wtype[hit] = 1
            wval[hit] = r
    # trial-division witnesses: s | N - q  <=>  q == N (mod s)
    cover_primes = {r for r, _ in spec["cover"]}
    for s in primerange(3, TRIAL_B):
        if s in cover_primes:
            continue
        rem = int(N % s)
        hit = (wtype == 0) & (qs % s == rem) & (qs != rem)
        if hit.any():
            wtype[hit] = 2
            wval[hit] = s
    # remaining: strong base-2 (or BPSW/Lucas fallback)
    rest = np.nonzero(wtype == 0)[0]
    print(f"cong={int((wtype==1).sum())} trial={int((wtype==2).sum())} "
          f"direct tests needed={len(rest)}", flush=True)
    for i in rest:
        m = N - int(qs[i])
        if not is_strong_prp(m, 2):
            wtype[i] = 3
            wval[i] = 2
        elif not is_prime(m):
            wtype[i] = 4
        else:
            raise AssertionError(f"N - {int(qs[i])} is prime: claim FALSE")

    assert is_prime(g) and is_prime(N - g)

    # ---- local ordinary prime-gap audit ----
    def near_prime(start, step):
        x = start
        smalls = list(primerange(3, 100000))
        while True:
            if x % 2 and not any(x % s == 0 for s in smalls):
                if powmod(2, x - 1, x) == 1 and is_prime(x):
                    return x
            x += step

    prev_p = near_prime(N - 1, -2)
    next_p = near_prime(N + 1, 2)
    audit = {
        "prev_prime_offset": int(N - prev_p),
        "next_prime_offset": int(next_p - N),
        "containing_gap": int(next_p - prev_p),
        "g": int(g),
        "ratio_g_over_gap": float(g) / float(next_p - prev_p),
    }
    print("audit:", audit, flush=True)

    summary = {
        "N_digits": len(str(N)), "g": int(g), "k": found["k"],
        "offsets_checked": len(qs) + 1,
        "by_parity": 1,
        "by_congruence": int((wtype == 1).sum()),
        "by_trial_division": int((wtype == 2).sum()),
        "by_strong_base2": int((wtype == 3).sum()),
        "by_bpsw_lucas": int((wtype == 4).sum()),
        "complement_status": "BPSW probable prime (ECPP certificate separate)",
        "local_gap_audit": audit,
    }
    json.dump(summary, open(f"{outdir}/evidence_summary.json", "w"), indent=1)
    np.savez_compressed(f"{outdir}/witnesses.npz", q=qs, wtype=wtype, wval=wval)
    record = {"name": found["name"], "N": str(N), "digits": len(str(N)),
              "g": int(g), "k": found["k"], "N0": spec["N0"], "M": spec["M"],
              "Q": spec["Q"], "cover": spec["cover"],
              "residual": spec["residual"]}
    json.dump(record, open(f"{outdir}/record.json", "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
