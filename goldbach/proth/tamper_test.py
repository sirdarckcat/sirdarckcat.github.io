"""Mutation test for verify.py: every tampered record must be REJECTED.

    python3 tamper_test.py ../records/<dir>/record.json

The untouched record must pass; each mutation below must fail, and for the
stated reason.  (The practice is taken from the independent BLS session on
branch ccr-8ffe9d7a-4ni11u, whose verifier ships with the same kind of
test; the cases marked * are theirs, the rest are additions.)
"""
import contextlib
import copy
import io
import json
import os
import sys
import tempfile

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify as V  # noqa: E402


def run(rec):
    """Return None if the record verifies, else the assertion message."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(rec, fh)
        path = fh.name
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            V.verify(path)
        return None
    except AssertionError as e:
        return str(e) or "assertion failed"
    finally:
        os.unlink(path)


def legendre(a, p):
    return pow(a % p, (p - 1) // 2, p)


def main(path):
    rec = json.load(open(path))
    N, g = int(rec["N"]), rec["g"]
    cover = rec["cover"]
    Mc = 1
    for r, _ in cover:
        if r != 2:
            Mc *= r
    P = N - g
    v = ((P - 1) & -(P - 1)).bit_length() - 1
    assert run(rec) is None, "the untouched record must verify"
    print("untouched record: PASS")

    def mut(**kw):
        m = copy.deepcopy(rec)
        m.update(kw)
        return m

    cases = []
    # * witness base replaced by a quadratic residue of P (Euler gives +1)
    qr = next(r for r, a in cover if r > 2 and legendre(a - g, r) == 1)
    cases.append(("base is a residue *", mut(base=qr), "Euler"))
    # * neighbouring member of the same progression: all congruences hold, P composite
    N2 = N + (Mc << v)
    cases.append(("next N in the progression *", mut(N=str(N2), digits=len(str(N2))), "Euler"))
    # * one congruence dropped (a late one, so some prime loses its only class)
    cases.append(("last congruence dropped *", mut(cover=cover[:-1]), "in no cover class"))
    # * class changed mod 3 / mod 17: N is no longer in the class
    for r0 in (3, 17):
        c2 = [[r, (a + 1) % r if r == r0 else a] for r, a in cover]
        cases.append((f"class changed mod {r0} *", mut(cover=c2), f"mod {r0}"))
    # * stale N: one decimal digit altered (kept even)
    s = rec["N"]
    k = len(s) // 2
    s2 = s[:k] + str((int(s[k]) + 1) % 10) + s[k + 1:]
    cases.append(("one digit of N altered *", mut(N=s2), "mod"))
    # claimed g replaced by the next prime: N - g' is not the proved prime
    g2 = g + 1
    while any(g2 % d == 0 for d in range(2, int(g2 ** 0.5) + 1)):
        g2 += 1
    cases.append(("g replaced by the next prime", mut(g=g2), "in no cover class"))
    # composite modulus smuggled in (class chosen so that N lies in it)
    cases.append(("composite modulus added", mut(cover=cover + [[15, N % 15]]), "not a prime"))
    # repeated modulus
    cases.append(("modulus repeated", mut(cover=cover + [cover[5]]), "repeated"))
    # parity class removed
    cases.append(("parity class removed", mut(cover=[c for c in cover if c[0] != 2]), "parity"))
    # digit count wrong
    cases.append(("digit count wrong", mut(digits=rec["digits"] + 1), "digit"))

    bad = 0
    for name, m, expect in cases:
        why = run(m)
        ok = why is not None and expect in why
        bad += not ok
        print(f"{'rejected' if why else 'ACCEPTED':9} {name:32} -> {why}{'' if ok else '   <-- UNEXPECTED'}")
    print(f"{len(cases) - bad}/{len(cases)} mutations rejected for the expected reason")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1])
