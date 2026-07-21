"""Full verification + evidence bundle for a Goldbach-desert record N.

For a claimed record (N, g):
  1. For every prime q < g: prove N - q composite.  Evidence recorded per
     offset: "parity" (q = 2), a congruence divisor r | N - q from the
     cover, a small trial divisor, or a strong base-2 Miller-Rabin
     witness (a prime can never fail this test, so failure is an
     unconditional compositeness proof).
  2. Check g is prime and N - g is a BPSW probable prime (certificate
     generated separately with PARI/GP primecert).
Writes a machine-readable JSON evidence file.

Usage: verify_record.py record.json evidence_out.json
  record.json: {"N": "...", "g": ..., "cover": [[r,a],...]}  (cover optional)
"""

import json
import sys

import gmpy2
from gmpy2 import mpz, is_prime, is_strong_prp
from sympy import primerange

TRIAL_LIMIT = 100000


def verify(N, g, cover=None):
    N = mpz(N)
    assert N % 2 == 0
    evidence = {}
    cover = [(int(r), int(a)) for r, a in (cover or [])]
    small_primes = list(primerange(2, TRIAL_LIMIT))
    n_cong = n_trial = n_mr = 0
    for q in primerange(2, g):
        m = N - q
        if q == 2:
            evidence[q] = ["parity", 2]
            continue
        # congruence divisor from the cover
        witness = None
        for r, a in cover:
            if q % r == a % r and m % r == 0:
                witness = ["congruence", r]
                n_cong += 1
                break
        if witness is None:
            for s in small_primes:
                if m % s == 0:
                    witness = ["trial", s]
                    n_trial += 1
                    break
        if witness is None:
            if not is_strong_prp(m, 2):
                witness = ["strong_base2", 2]
                n_mr += 1
            else:
                raise AssertionError(
                    f"N - {q} is a base-2 strong probable prime: claim FALSE")
        evidence[q] = witness
    assert is_prime(g), "g is not prime"
    assert is_prime(N - g), "N - g is not a BPSW probable prime"
    return {
        "N": str(N), "digits": len(str(N)), "g": int(g),
        "offsets_checked": len(evidence),
        "by_congruence": n_cong, "by_trial_division": n_trial,
        "by_strong_base2": n_mr,
        "complement_status": "BPSW probable prime (see ECPP certificate)",
        "witnesses": {str(q): w for q, w in evidence.items()},
    }


def main():
    rec = json.load(open(sys.argv[1]))
    out = verify(rec["N"], rec["g"], rec.get("cover"))
    with open(sys.argv[2], "w") as f:
        json.dump(out, f, indent=1)
    print(f"VERIFIED N ({out['digits']} digits): g(N) = {out['g']}")
    print(f"  offsets: {out['offsets_checked']} "
          f"(congruence {out['by_congruence']}, trial {out['by_trial_division']}, "
          f"strong-base-2 {out['by_strong_base2']})")


if __name__ == "__main__":
    main()
