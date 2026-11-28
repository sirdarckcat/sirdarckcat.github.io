#!/usr/bin/env python3
"""Standalone ECPP verifier soundness and tamper test suite.

Exercises all 5 active Python ECPP verifiers in the repository:
  1. goldbach/ecpp_check.py                (gmpy2 Jacobian projective)
  2. slop/goldbach/records/verify_record.py      (stdlib affine)
  3. slop/goldbach/records/work/verify_record.py (stdlib affine, duplicate)
  4. slop/goldbach/records/ecpp_verify.py        (stdlib affine)
  5. slop/goldbach/records/work/ecpp_verify.py   (stdlib affine, duplicate)

Verifies:
  - Positive regressions on real certified records (200-digit g160357 across all
    5 checkers + CLI subprocess test; 250-digit g201667 on ecpp_check.py).
  - Byte-for-byte duplicate parity between top-level and work/ slop verifiers.
  - Intact SHA-256 archive of historical slop/goldbach/records/g23/SHA256SUMS.
  - Adversarial composite forgeries & edge cases (V1..V6j) rejected across ALL 5
    active checkers, including the concrete composite numbers that fooled the
    pre-patch checkers (N=14279 via isqrt4 floor gap, N=889 via equal-x
    unequal-y addition, and N=1051 t=+-65 via Hasse off-by-one).
  - Regression tests R1..R6 covering strict PARI parse_cert & N_minus_g grammar,
    clean ecpp_verify.verify() malformed-shape rejection, strict JSON int/bool/float
    rejection & sub-second pre-bound modulus/negative-input rejection, PARI/GP
    crosscheck.gp tamper exit codes (R4) and code-injection/RCE hardening (R6),
    and gmpy2 vs pure-stdlib SPRP(2,3) parity when 3 | c (R5).

Usage:
  python3 -B goldbach/test_ecpp_soundness.py          # full suite
  python3 -B goldbach/test_ecpp_soundness.py --fast   # quick smoke
"""
import sys

# Must be set before importing modules under slop/ so no untracked __pycache__ is created.
sys.dont_write_bytecode = True

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import time

import gmpy2
from gmpy2 import mpz

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKER_PATHS = {
    "ecpp_check": os.path.join(REPO_ROOT, "goldbach", "ecpp_check.py"),
    "slop_verify_record": os.path.join(REPO_ROOT, "slop", "goldbach", "records", "verify_record.py"),
    "work_verify_record": os.path.join(REPO_ROOT, "slop", "goldbach", "records", "work", "verify_record.py"),
    "slop_ecpp_verify": os.path.join(REPO_ROOT, "slop", "goldbach", "records", "ecpp_verify.py"),
    "work_ecpp_verify": os.path.join(REPO_ROOT, "slop", "goldbach", "records", "work", "ecpp_verify.py"),
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_checker_cert(name, mod, cert, expect_top):
    """Run a loaded verifier module on (cert, expect_top).

    Returns (accepted: bool, detail: str).
    """
    if name == "ecpp_check":
        try:
            assert len(cert) > 0, "empty certificate"
            assert mpz(cert[0][0]) == mpz(expect_top), "top-level binding mismatch"
            current = mpz(expect_top)
            for i, step in enumerate(cert):
                N, t, s, a4, pt = step
                x, y = pt
                assert mpz(N) == current, f"chain broken at step {i}"
                current = mod.verify_step(mpz(N), mpz(t), mpz(s), mpz(a4), mpz(x), mpz(y))
            assert current < 2 ** 64, f"final q >= 2^64 ({current})"
            assert gmpy2.is_prime(int(current)), f"final q={current} fails BPSW"
            return True, f"accepted (final q={current})"
        except (AssertionError, IndexError, ValueError, TypeError) as exc:
            return False, f"rejected: {exc}"

    if name in ("slop_verify_record", "work_verify_record"):
        try:
            ok = mod.ecpp_verify(cert, int(expect_top))
            return bool(ok), "accepted"
        except (AssertionError, IndexError, ValueError, TypeError, mod.CompositeFactor) as exc:
            return False, f"rejected: {exc}"

    if name in ("slop_ecpp_verify", "work_ecpp_verify"):
        try:
            ok, info = mod.verify(cert)
            if not ok:
                return False, f"rejected: {info}"
            if int(info) != int(expect_top):
                return False, f"rejected: top mismatch ({info} != {expect_top})"
            return True, f"accepted (top={info})"
        except (AssertionError, IndexError, ValueError, TypeError, mod.CompositeFactor) as exc:
            return False, f"rejected: {exc}"

    raise ValueError(f"unknown checker {name}")


def run_direct_ec_add(name, mod, P, Q, a, n):
    """Test direct point addition/doubling; returns (raised: bool, detail: str)."""
    if name == "ecpp_check":
        try:
            res = mod.jac_add(mpz(P[0]), mpz(P[1]), mpz(1),
                              mpz(Q[0]), mpz(Q[1]), mpz(1), mpz(a), mpz(n))
            return False, f"returned {res}"
        except AssertionError as exc:
            return True, str(exc)
    else:
        try:
            res = mod.ec_add(P, Q, a, n)
            return False, f"returned {res}"
        except mod.CompositeFactor as exc:
            return True, f"CompositeFactor({exc.args[0]})"
        except AssertionError as exc:
            return True, str(exc)


def run_direct_ec_dbl(name, mod, P, a, n):
    """Test direct point doubling; returns (raised: bool, detail: str)."""
    if name == "ecpp_check":
        try:
            res = mod.jac_dbl(mpz(P[0]), mpz(P[1]), mpz(1), mpz(a), mpz(n))
            return False, f"returned {res}"
        except AssertionError as exc:
            return True, str(exc)
    else:
        return run_direct_ec_add(name, mod, P, P, a, n)


def main():
    parser = argparse.ArgumentParser(description="ECPP verifier soundness & tamper test suite")
    parser.add_argument("--fast", action="store_true",
                        help="Run 77-digit 6-step real tail on pure-Python checkers (~2s vs ~22s)")
    args = parser.parse_args()

    t0 = time.monotonic()
    mods = {name: load_module(name, path) for name, path in CHECKER_PATHS.items()}
    failures = []
    passed = 0

    def record(ok, label, detail=""):
        nonlocal passed
        status = "PASS" if ok else "FAIL"
        suffix = f" ({detail})" if detail else ""
        print(f"[{status}] {label}{suffix}")
        if ok:
            passed += 1
        else:
            failures.append(f"{label}{suffix}")

    # ------------------------------------------------------------------
    # 1. Duplicate byte-parity & g23/ SHA256SUMS archival integrity
    # ------------------------------------------------------------------
    for pair_name, p1, p2 in [
        ("parity: verify_record.py == work/verify_record.py",
         CHECKER_PATHS["slop_verify_record"], CHECKER_PATHS["work_verify_record"]),
        ("parity: ecpp_verify.py == work/ecpp_verify.py",
         CHECKER_PATHS["slop_ecpp_verify"], CHECKER_PATHS["work_ecpp_verify"]),
    ]:
        b1 = open(p1, "rb").read()
        b2 = open(p2, "rb").read()
        record(b1 == b2, pair_name, f"{len(b1)} bytes")

    g23_dir = os.path.join(REPO_ROOT, "slop", "goldbach", "records", "g23")
    g23_sums_path = os.path.join(g23_dir, "SHA256SUMS")
    g23_entries = 0
    g23_ok = True
    for line in open(g23_sums_path):
        line = line.strip()
        if not line:
            continue
        expected_hash, fname = line.split(None, 1)
        actual_hash = hashlib.sha256(open(os.path.join(g23_dir, fname), "rb").read()).hexdigest()
        g23_entries += 1
        if actual_hash != expected_hash:
            g23_ok = False
    record(g23_ok and g23_entries == 6,
           "archive: slop/goldbach/records/g23/SHA256SUMS intact",
           f"{g23_entries}/6 files verified")

    # ------------------------------------------------------------------
    # 2. Positive regressions on real certified records
    # ------------------------------------------------------------------
    rec160_dir = os.path.join(REPO_ROOT, "goldbach", "records", "budget_1e200_200digit_g160357")
    pkg160 = json.load(open(os.path.join(rec160_dir, "package_stdlib.json")))
    cert160_full = pkg160["ecpp_cert"]
    top160_full = int(pkg160["N"]) - int(pkg160["q"])
    cert160_tail = cert160_full[-6:]
    top160_tail = int(cert160_tail[0][0])

    for name, mod in mods.items():
        if args.fast and name != "ecpp_check":
            cert_use, top_use, tag = cert160_tail, top160_tail, "g160357 tail (77d, 6 steps)"
        else:
            cert_use, top_use, tag = cert160_full, top160_full, "g160357 full (200d, 21 steps)"
        ts = time.monotonic()
        ok, detail = run_checker_cert(name, mod, cert_use, top_use)
        dt = time.monotonic() - ts
        record(ok, f"positive[{name}]: {tag}", f"{detail}, {dt:.2f}s")

    # CLI subprocess end-to-end tests of goldbach/ecpp_check.py (tests parse_cert + main)
    for rec_name in ("budget_1e200_200digit_g160357", "g200k_250digit_g201667"):
        rdir = os.path.join(REPO_ROOT, "goldbach", "records", rec_name)
        ts = time.monotonic()
        proc = subprocess.run(
            [sys.executable, "-B", CHECKER_PATHS["ecpp_check"],
             os.path.join(rdir, "complement_cert.gp"),
             os.path.join(rdir, "N_minus_g.txt")],
            capture_output=True, text=True,
        )
        dt = time.monotonic() - ts
        ok = proc.returncode == 0 and "INDEPENDENT ECPP CHECK PASSED" in proc.stdout
        record(ok, f"positive[ecpp_check CLI]: {rec_name}", f"rc={proc.returncode}, {dt:.2f}s")

    # ------------------------------------------------------------------
    # 3. Adversarial certificate-level vectors (ALL 5 active checkers)
    # ------------------------------------------------------------------
    # V1: Composite N = 14279 = 109 * 131 (isqrt4 floor boundary forgery:
    #     r4 = floor(14279^(1/4)) = 10, (10+1)^2 = 121 < 127 = q <= (14279^(1/4)+1)^2 ~= 142.36)
    v1_cert = [[14279, 56, 112, 13625, [13626, 6551]]]

    # V2a: Composite N = 889 = 7 * 127 equal-x unequal-y end-to-end forgery
    v2a_cert = [[889, -27, 7, 1, [744, 79]]]

    # V3a & V3b: Strict Hasse bound tight off-by-one |t| = isqrt(4N) + 1 = 65 on N = 1051
    v3a_cert = [[1051, 65, 21, 1, [28, 9]]]
    v3b_cert = [[1051, -65, 1, 1, [28, 9]]]

    # V6a: D < 0 trap (N=1009, q=2 => D=-992 < 0, D^2 = 984064 > 288)
    v6a_cert = [[1009, 2, 504, 1, [1, 1]]]

    # V6b: Exact equality D^2 == 16*q*(q+1)^2 (N=625=5^4, t=14, s=17, q=36 => D=888)
    v6b_cert = [[625, 14, 17, 1, [1, 1]]]

    # V6c: q = 1 (N=1009, t=0, s=1010 => q=1)
    v6c_cert = [[1009, 0, 1010, 1, [1, 1]]]

    # V6d: s <= 0 and m % s != 0
    v6d_s0 = [[1009, 0, 0, 1, [1, 1]]]
    v6d_sneg = [[1009, 0, -1, 1, [1, 1]]]
    v6d_mod = [[1009, 0, 3, 1, [1, 1]]]

    # V6e: Singular curve gcd(4*a^3 + 27*b^2, N) > 1 (a=0, x=0, y=0 => b=0, disc=0)
    v6e_cert = [[1051, 64, 1, 0, [0, 0]]]

    # V6f: gcd(N, 6) != 1 (even and divisible by 3)
    v6f_even = [[1050, 0, 1, 1, [1, 1]]]
    v6f_div3 = [[1053, 0, 1, 1, [1, 1]]]

    # V6g: Broken chain on real multi-step cert tail
    v6g_cert = copy.deepcopy(cert160_tail)
    v6g_cert[1][0] = str(int(v6g_cert[1][0]) + 2)

    # V6i: Composite terminal q where all curve & bound checks PASS:
    #   q = 91 = 7 * 13: [97, 7, 1, 1, [3, 32]]
    #   q = 561 = 3 * 11 * 17 (Carmichael): [563, 3, 1, 2, [1, 98]]
    #   Oversized terminal q > 3.317e24: truncated real tail cert160_tail[:2]
    v6i_q91 = [[97, 7, 1, 1, [3, 32]]]
    v6i_q561 = [[563, 3, 1, 2, [1, 98]]]
    v6i_oversized = copy.deepcopy(cert160_tail[:2])  # stops at ~50-digit q >> 3.317e24

    neg_cert_cases = [
        ("V1: composite N=14279 (isqrt4 floor boundary forgery)", v1_cert, 14279),
        ("V2a: composite N=889 (equal-x unequal-y end-to-end forgery)", v2a_cert, 889),
        ("V3a: Hasse off-by-one N=1051 t=+65", v3a_cert, 1051),
        ("V3b: Hasse off-by-one N=1051 t=-65", v3b_cert, 1051),
        ("V6a: GK D<0 trap (N=1009, q=2)", v6a_cert, 1009),
        ("V6b: GK exact equality D^2==16q(q+1)^2 (N=625, q=36)", v6b_cert, 625),
        ("V6c: q=1 rejected (N=1009, s=1010)", v6c_cert, 1009),
        ("V6d(s=0): s<=0 rejected", v6d_s0, 1009),
        ("V6d(s=-1): s<0 rejected", v6d_sneg, 1009),
        ("V6d(m%s!=0): s does not divide m", v6d_mod, 1009),
        ("V6e: singular curve gcd(disc, N)>1", v6e_cert, 1051),
        ("V6f(even): gcd(N, 6)!=1 (N=1050)", v6f_even, 1050),
        ("V6f(div3): gcd(N, 6)!=1 (N=1053)", v6f_div3, 1053),
        ("V6g: broken chain on real tail cert", v6g_cert, top160_tail),
        ("V6h: wrong expect_top binding", cert160_tail, top160_tail + 2),
        ("V6i(q=91): composite terminal q=91 (all curve checks pass)", v6i_q91, 97),
        ("V6i(q=561): Carmichael terminal q=561 (all curve checks pass)", v6i_q561, 563),
        ("V6i(large q): oversized terminal q > 3.317e24", v6i_oversized, top160_tail),
        ("V6i(empty): empty cert [] rejected", [], 1009),
    ]

    for label, cert, expect_top in neg_cert_cases:
        for name, mod in mods.items():
            accepted, detail = run_checker_cert(name, mod, cert, expect_top)
            record(not accepted, f"{label} [{name}]", detail)

    # Confirm V6i(q=91) and V6i(q=561) genuinely pass verify_step (so rejection is at terminal primality)
    ecpp_mod = mods["ecpp_check"]
    q91_out = int(ecpp_mod.verify_step(mpz(97), mpz(7), mpz(1), mpz(1), mpz(3), mpz(32)))
    q561_out = int(ecpp_mod.verify_step(mpz(563), mpz(3), mpz(1), mpz(2), mpz(1), mpz(98)))
    record(q91_out == 91 and q561_out == 561,
           "sanity: V6i composite-q vectors pass curve/bound checks and fail strictly at terminal primality",
           f"q={q91_out}, {q561_out}")

    # ------------------------------------------------------------------
    # 4. Direct EC arithmetic negative tests (ALL 5 active checkers)
    # ------------------------------------------------------------------
    # V2b: equal-x unequal-y over composite N = 889 = 7 * 127
    for name, mod in mods.items():
        raised, detail = run_direct_ec_add(name, mod, (233, 709), (233, 688), 1, 889)
        record(raised, f"V2b: direct equal-x unequal-y on N=889 [{name}]", detail)

    # V4a: composite 2-torsion doubling on N = 77 = 7 * 11 (gcd(2Y, 77) = 7)
    for name, mod in mods.items():
        raised, detail = run_direct_ec_dbl(name, mod, (35, 56), 1, 77)
        record(raised, f"V4a: direct composite 2-torsion doubling on N=77 [{name}]", detail)

    # V4b: composite inverse addition with mixed 2-torsion on N = 77 (gcd(y1 - y2, 77) = 7)
    for name, mod in mods.items():
        raised, detail = run_direct_ec_add(name, mod, (35, 56), (35, 21), 1, 77)
        record(raised, f"V4b: direct composite inverse-branch gcd(y1-y2, 77)=7 [{name}]", detail)

    # V5: secant denominator gcd(x2 - x1, 889) = 7
    for name, mod in mods.items():
        raised, detail = run_direct_ec_add(name, mod, (233, 709), (744, 79), 1, 889)
        record(raised, f"V5: direct secant gcd(x2-x1, 889)=7 [{name}]", detail)

    # ------------------------------------------------------------------
    # 5. V6j: Local-Z hardening & parse_cert tests in goldbach/ecpp_check.py
    # ------------------------------------------------------------------
    z_cases = [
        ("V6j(jac_dbl Y!=0, Z=7 mod 889)",
         lambda: ecpp_mod.jac_dbl(mpz(233), mpz(709), mpz(7), mpz(1), mpz(889))),
        ("V6j(jac_dbl Y==0, Z=7 mod 889)",
         lambda: ecpp_mod.jac_dbl(mpz(233), mpz(0), mpz(7), mpz(1), mpz(889))),
        ("V6j(jac_add Z1==0, Z2=7 mod 889)",
         lambda: ecpp_mod.jac_add(mpz(1), mpz(1), mpz(0), mpz(233), mpz(709), mpz(7), mpz(1), mpz(889))),
        ("V6j(jac_add Z2==0, Z1=7 mod 889)",
         lambda: ecpp_mod.jac_add(mpz(233), mpz(709), mpz(7), mpz(1), mpz(1), mpz(0), mpz(1), mpz(889))),
        ("V6j(jac_add U1==U2, Z1=7 mod 889)",
         lambda: ecpp_mod.jac_add(mpz(233), mpz(709), mpz(7), mpz(233), mpz(709), mpz(7), mpz(1), mpz(889))),
        ("V6j(jac_add U1!=U2, Z1=7 mod 889)",
         lambda: ecpp_mod.jac_add(mpz(233), mpz(709), mpz(7), mpz(10), mpz(20), mpz(1), mpz(1), mpz(889))),
    ]
    for label, fn in z_cases:
        try:
            res = fn()
            record(False, label, f"unexpectedly returned {res}")
        except AssertionError as exc:
            record(True, label, f"rejected: {exc}")

    # parse_cert unbalanced brackets & CLI empty-cert check
    for label, text in [
        ("V6j(parse_cert unclosed '[')", "[[1, 2]"),
        ("V6j(parse_cert extra ']')", "[[1, 2]]]"),
    ]:
        with tempfile.NamedTemporaryFile("w", suffix=".gp", delete=True) as tf:
            tf.write(text)
            tf.flush()
            try:
                res = ecpp_mod.parse_cert(tf.name)
                record(False, label, f"unexpectedly parsed {res}")
            except (AssertionError, IndexError, ValueError) as exc:
                record(True, label, f"rejected: {exc}")

    with tempfile.NamedTemporaryFile("w", suffix=".gp", delete=True) as cf, \
         tempfile.NamedTemporaryFile("w", suffix=".txt", delete=True) as nf:
        cf.write("[]\n")
        cf.flush()
        nf.write("1009\n")
        nf.flush()
        proc = subprocess.run(
            [sys.executable, "-B", CHECKER_PATHS["ecpp_check"], cf.name, nf.name],
            capture_output=True, text=True,
        )
        record(proc.returncode != 0, "V6j(ecpp_check CLI empty cert)", f"rc={proc.returncode}")

    # ------------------------------------------------------------------
    # 6. R1: Strict parse_cert & N_minus_g.txt smuggling regressions (BUG-C1-1)
    # ------------------------------------------------------------------
    valid_small_cert = "[[1009, -3, 1, 1, [1, 4]]]"
    with tempfile.TemporaryDirectory() as tmpdir:
        n_ok_path = os.path.join(tmpdir, "n_ok.txt")
        with open(n_ok_path, "w", encoding="utf-8") as fh:
            fh.write("1009\n")

        # Positive sanity: valid cert with and without single optional trailing ';'
        for tag, txt in [
            ("R1(pos: plain valid cert)", valid_small_cert + "\n"),
            ("R1(pos: single trailing semicolon)", valid_small_cert + ";\n"),
        ]:
            cpath = os.path.join(tmpdir, "cert.gp")
            with open(cpath, "w", encoding="utf-8") as fh:
                fh.write(txt)
            proc = subprocess.run(
                [sys.executable, "-B", CHECKER_PATHS["ecpp_check"], cpath, n_ok_path],
                capture_output=True, text=True,
            )
            ok = proc.returncode == 0 and "INDEPENDENT ECPP CHECK PASSED" in proc.stdout
            record(ok, tag, f"rc={proc.returncode}")

        # Negative smuggling cases (parse_cert + CLI must BOTH reject)
        r1_smuggle_cases = [
            ("R1(trailing GARBAGE)", valid_small_cert + "GARBAGE"),
            ("R1(trailing extra_junk 999)", valid_small_cert + " extra_junk 999"),
            ("R1(trailing int 999)", valid_small_cert + " 999"),
            ("R1(semicolon + GARBAGE)", valid_small_cert + "; GARBAGE"),
            ("R1(semicolon + x = 123)", valid_small_cert + "; x = 123"),
            ("R1(double semicolon)", valid_small_cert + ";;"),
            ("R1(trailing C comment)", valid_small_cert + " /* forged */"),
            ("R1(dangling token before '[')", "[[1009, -3, 1, 1, 0 [1, 4]]]"),
            ("R1(space splitting digits)", "[[10 09, -3, 1, 1, [1, 4]]]"),
            ("R1(tab splitting digits)", "[[10\t09, -3, 1, 1, [1, 4]]]"),
            ("R1(quoted split digits)", '[["10""09", -3, 1, 1, [1, 4]]]'),
            ("R1(leading empty comma slot)", "[, [1009, -3, 1, 1, [1, 4]]]"),
            ("R1(double comma slot)", "[[1009,, -3, 1, 1, [1, 4]]]"),
            ("R1(trailing comma slot)", "[[1009, -3, 1, 1, [1, 4]],]"),
            ("R1(non-list top-level scalar)", "1009\n"),
            ("R1(empty cert file)", "   \n"),
        ]
        for label, bad_txt in r1_smuggle_cases:
            cpath = os.path.join(tmpdir, "bad.gp")
            with open(cpath, "w", encoding="utf-8") as fh:
                fh.write(bad_txt)
            parse_rejected = False
            try:
                ecpp_mod.parse_cert(cpath)
            except (ValueError, AssertionError):
                parse_rejected = True
            proc = subprocess.run(
                [sys.executable, "-B", CHECKER_PATHS["ecpp_check"], cpath, n_ok_path],
                capture_output=True, text=True,
            )
            record(parse_rejected and proc.returncode != 0,
                   label, f"parse_rejected={parse_rejected}, cli_rc={proc.returncode}")

        # Negative N_minus_g.txt validation via CLI
        c_ok_path = os.path.join(tmpdir, "cert_ok.gp")
        with open(c_ok_path, "w", encoding="utf-8") as fh:
            fh.write(valid_small_cert + "\n")
        for label, bad_n in [
            ("R1(N_minus_g float)", "1009.0\n"),
            ("R1(N_minus_g trailing junk)", "1009 extra\n"),
            ("R1(N_minus_g multiple ints)", "1009\n1013\n"),
            ("R1(N_minus_g empty)", "   \n"),
        ]:
            npath = os.path.join(tmpdir, "bad_n.txt")
            with open(npath, "w", encoding="utf-8") as fh:
                fh.write(bad_n)
            proc = subprocess.run(
                [sys.executable, "-B", CHECKER_PATHS["ecpp_check"], c_ok_path, npath],
                capture_output=True, text=True,
            )
            record(proc.returncode != 0, label, f"cli_rc={proc.returncode}")

    # ------------------------------------------------------------------
    # 7. R2: Clean malformed-shape rejection in ecpp_verify & verify_record (BUG-C1-2)
    # ------------------------------------------------------------------
    r2_malformed_cases = [
        ("R2([[]])", [[]]),
        ("R2([123])", [123]),
        ("R2(short step)", [[1009, 0, 1]]),
        ("R2(1-elem point)", [[1009, -3, 1, 1, [1]]]),
        ("R2(3-elem point)", [[1009, -3, 1, 1, [1, 4, 1]]]),
        ("R2(scalar point)", [[1009, -3, 1, 1, 5]]),
        ("R2(non-numeric str)", [["abc", 0, 1, 1, [1, 1]]]),
        ("R2(float string)", [["1009.5", 0, 1, 1, [1, 1]]]),
        ("R2(None field)", [[None, 0, 1, 1, [1, 1]]]),
        ("R2(nested list point)", [[1009, 0, 1, 1, [[1], [1]]]]),
        ("R2(non-list int cert)", 123),
        ("R2(None cert)", None),
    ]
    for label, bad_cert in r2_malformed_cases:
        for name in ("slop_ecpp_verify", "work_ecpp_verify"):
            mod = mods[name]
            try:
                res = mod.verify(bad_cert)
                ok = (isinstance(res, tuple) and len(res) == 2
                      and res[0] is False and isinstance(res[1], str) and len(res[1]) > 0)
                record(ok, f"{label} [{name}]", f"returned {res!r}")
            except Exception as exc:
                record(False, f"{label} [{name}]", f"UNCAUGHT {type(exc).__name__}: {exc}")
        for name in ("slop_verify_record", "work_verify_record"):
            mod = mods[name]
            try:
                mod.ecpp_verify(bad_cert, 1009)
                record(False, f"{label} [{name}]", "unexpectedly accepted")
            except AssertionError as exc:
                record(True, f"{label} [{name}]", f"AssertionError: {exc}")
            except Exception as exc:
                record(False, f"{label} [{name}]", f"non-AssertionError {type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------
    # 8. R3: JSON float/bool rejection, pre-bound DoS & negative q/r (BUG-C1-3)
    # ------------------------------------------------------------------
    r3_cert_cases = [
        ("R3(cert float N=1009.9)", [[1009.9, -3, 1, 1, [1, 4]]]),
        ("R3(cert float N=1009.0)", [[1009.0, -3, 1, 1, [1, 4]]]),
        ("R3(cert float s=1.9)", [[1009, -3, 1.9, 1, [1, 4]]]),
        ("R3(cert bool s/a=True)", [[1009, -3, True, True, [1, 4]]]),
        ("R3(cert bool x=True)", [[1009, -3, 1, 1, [True, 4]]]),
        ("R3(cert float y=4.0)", [[1009, -3, 1, 1, [1, 4.0]]]),
    ]
    for label, bad_cert in r3_cert_cases:
        for name in ("slop_ecpp_verify", "work_ecpp_verify"):
            mod = mods[name]
            try:
                res = mod.verify(bad_cert)
                ok = isinstance(res, tuple) and len(res) == 2 and res[0] is False
                record(ok, f"{label} [{name}]", f"returned {res!r}")
            except Exception as exc:
                record(False, f"{label} [{name}]", f"UNCAUGHT {type(exc).__name__}: {exc}")
        for name in ("slop_verify_record", "work_verify_record"):
            mod = mods[name]
            try:
                mod.ecpp_verify(bad_cert, 1009)
                record(False, f"{label} [{name}]", "unexpectedly accepted")
            except AssertionError as exc:
                record(True, f"{label} [{name}]", f"AssertionError: {exc}")
            except Exception as exc:
                record(False, f"{label} [{name}]", f"non-AssertionError {type(exc).__name__}: {exc}")

    # Full verify_record.py package checks (toy baseline + float/bool + claims + negative q/r + 250d DoS)
    toy_pkg = {
        "N": "1014",
        "q": 5,
        "classes": [[3, 0]],
        "t": 169,
        "ecpp_cert": [[1009, -3, 1, 1, [1, 4]]],
        "claims": {"q_exceeds": 3, "N_below": "2000", "digits_at_most": 4},
    }
    rec250_pkg_path = os.path.join(
        REPO_ROOT, "goldbach", "records", "g200k_250digit_g201667", "package_stdlib.json"
    )
    with open(rec250_pkg_path, "r", encoding="utf-8") as fh:
        rec250_pkg = json.load(fh)
    N250 = int(rec250_pkg["N"])
    q250 = int(rec250_pkg["q"])

    with tempfile.TemporaryDirectory() as tmpdir:
        def run_vr_main(mod, pkg_obj):
            p = os.path.join(tmpdir, "pkg.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(pkg_obj, fh)
            buf = io.StringIO()
            t_start = time.monotonic()
            try:
                with contextlib.redirect_stdout(buf):
                    mod.main(p)
                return True, None, time.monotonic() - t_start
            except Exception as exc:
                return False, exc, time.monotonic() - t_start

        for name in ("slop_verify_record", "work_verify_record"):
            mod = mods[name]
            # Positive baseline toy package
            ok_pos, exc_pos, dt_pos = run_vr_main(mod, toy_pkg)
            record(ok_pos, f"R3(pos: toy package baseline) [{name}]",
                   f"exc={exc_pos!r}, {dt_pos:.3f}s")

            # Float / bool mutations across N, q, t, classes, claims
            pkg_mutations = [
                ("R3(pkg float N=1014.9)", {"N": 1014.9}),
                ("R3(pkg float q=5.9)", {"q": 5.9}),
                ("R3(pkg float t=169.9)", {"t": 169.9}),
                ("R3(pkg bool class residue)", {"classes": [[3, False]]}),
                ("R3(pkg float class modulus)", {"classes": [[3.0, 0]]}),
                ("R3(pkg float claims.q_exceeds)", {"claims": {"q_exceeds": 3.5}}),
                ("R3(pkg bool claims.q_exceeds)", {"claims": {"q_exceeds": True}}),
                ("R3(pkg float claims.N_below)", {"claims": {"N_below": 2000.5}}),
                ("R3(pkg float claims.digits_at_most)", {"claims": {"digits_at_most": 4.9}}),
                ("R3(pkg negative q=-5)", {"q": -5}),
                ("R3(pkg negative r=-3)", {"classes": [[-3, 0]]}),
            ]
            for label, patch in pkg_mutations:
                bad_pkg = copy.deepcopy(toy_pkg)
                bad_pkg.update(patch)
                ok_m, exc_m, dt_m = run_vr_main(mod, bad_pkg)
                is_clean_assert = (not ok_m) and isinstance(exc_m, AssertionError)
                record(is_clean_assert, f"{label} [{name}]",
                       f"{type(exc_m).__name__ if exc_m else 'ACCEPTED'}: {exc_m}, {dt_m:.3f}s")

            # 250-digit pre-bound trial-division DoS: r = N - q and r = N - q - 2 must reject < 1.0s
            for label, r_bad in [
                ("R3(250d DoS r=N-q < 1.0s)", N250 - q250),
                ("R3(250d DoS r=N-q-2 < 1.0s)", N250 - q250 - 2),
            ]:
                dos_pkg = copy.deepcopy(rec250_pkg)
                dos_pkg["classes"] = [[r_bad, N250 % r_bad]]
                ok_d, exc_d, dt_d = run_vr_main(mod, dos_pkg)
                is_fast_assert = (not ok_d) and isinstance(exc_d, AssertionError) and dt_d < 1.0
                record(is_fast_assert, f"{label} [{name}]",
                       f"{type(exc_d).__name__ if exc_d else 'ACCEPTED'}: {exc_d}, {dt_d:.3f}s")

    # ------------------------------------------------------------------
    # 9. R4: PARI/GP crosscheck.gp tamper exit codes (BUG-C2-1)
    # ------------------------------------------------------------------
    gp_bin = shutil.which("gp")
    if gp_bin is None:
        record(False, "R4(PARI gp binary present)", "gp not found on PATH")
    else:
        rec250_dir = os.path.join(REPO_ROOT, "goldbach", "records", "g200k_250digit_g201667")
        cc_src = os.path.join(rec250_dir, "crosscheck.gp")
        cert_src = os.path.join(rec250_dir, "complement_cert.gp")
        with open(cert_src, "r", encoding="utf-8") as fh:
            orig_cert_txt = fh.read()
        with open(os.path.join(rec250_dir, "N_minus_g.txt"), "r", encoding="utf-8") as fh:
            n_minus_g_250 = fh.read().strip()

        s_mut_txt = orig_cert_txt.replace(", 398777256,", ", 0,", 1)
        assert s_mut_txt != orig_cert_txt, "failed to locate step-1 cofactor s=398777256 in 250d cert"

        r4_cases = [
            ("R4(crosscheck.gp cert s->0)", s_mut_txt),
            ("R4(crosscheck.gp cert 1D [N-g])", f"[{n_minus_g_250}]\n"),
            ("R4(crosscheck.gp cert empty [[]])", "[[]]\n"),
            ("R4(crosscheck.gp cert zero-step [[N-g,0,0,0,[0,0]]])", f"[[{n_minus_g_250}, 0, 0, 0, [0, 0]]]\n"),
            ("R4(crosscheck.gp missing cert)", None),
        ]
        for label, cert_content in r4_cases:
            with tempfile.TemporaryDirectory() as tmpdir:
                shutil.copy2(cc_src, os.path.join(tmpdir, "crosscheck.gp"))
                if cert_content is not None:
                    with open(os.path.join(tmpdir, "complement_cert.gp"), "w", encoding="utf-8") as fh:
                        fh.write(cert_content)
                ts = time.monotonic()
                proc = subprocess.run(
                    [gp_bin, "-q", "--default", "colors=no", "crosscheck.gp"],
                    cwd=tmpdir,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                )
                dt = time.monotonic() - ts
                ok = proc.returncode == 1 and "FAIL:" in proc.stdout
                record(ok, label, f"rc={proc.returncode}, {dt:.2f}s, out={proc.stdout.strip()!r}")

    # ------------------------------------------------------------------
    # 10. R5: verify_record.py gmpy2 vs stdlib parity & 3 | c SPRP(2) (BUG-R2-1)
    # ------------------------------------------------------------------
    r5_ecpp_cert = [
        [6559395693020281343352747643, 38739166084520, 10671084, 0,
         [4057306548571436769405371960, 1967354677195334753291360985]],
        [614688788226223559311, -44581661276, 8703772, 0,
         [263532715364156632596, 219578260798592129835]],
    ]
    r5_valid_pkgs = [
        ("classes=[]", {
            "N": "6559395693020281343352747894",
            "q": 251,
            "classes": [],
            "t": 3279697846510140671676373947,
            "ecpp_cert": r5_ecpp_cert,
            "claims": {},
        }),
        ("classes=[[5,4]]", {
            "N": "6559395693020281343352747894",
            "q": 251,
            "classes": [[5, 4]],
            "t": 655939569302028134335274789,
            "ecpp_cert": r5_ecpp_cert,
            "claims": {},
        }),
    ]
    r5_edge_pkg = {
        "N": 6,
        "q": 5,
        "classes": [],
        "t": 3,
        "ecpp_cert": [[1009, -3, 1, 1, [1, 4]]],
        "claims": {},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        for vr_name in ("slop_verify_record", "work_verify_record"):
            vr_path = CHECKER_PATHS[vr_name]
            vr_mod = mods[vr_name]

            # Valid 28-digit record with 3 | (N - 3) base-2 SPRP in both gmpy2 & pure-stdlib CLI modes
            for pkg_tag, pkg_obj in r5_valid_pkgs:
                pkg_path = os.path.join(tmpdir, f"r5_{vr_name}_{pkg_tag.replace('[', '').replace(']', '').replace(',', '_')}.json")
                with open(pkg_path, "w", encoding="utf-8") as fh:
                    json.dump(pkg_obj, fh)
                for mode_name, block_gmpy2 in (("gmpy2", False), ("stdlib", True)):
                    if block_gmpy2:
                        cmd = [
                            sys.executable, "-B", "-c",
                            "import runpy, sys; sys.modules['gmpy2'] = None; "
                            "vr, pkg = sys.argv[1], sys.argv[2]; "
                            "sys.argv = [vr, pkg]; "
                            "runpy.run_path(vr, run_name='__main__')",
                            vr_path, pkg_path,
                        ]
                        expected_banner = "[info] pure stdlib mode"
                    else:
                        cmd = [sys.executable, "-B", vr_path, pkg_path]
                        expected_banner = "[info] gmpy2 acceleration available"
                    proc = subprocess.run(cmd, capture_output=True, text=True)
                    ok = (
                        proc.returncode == 0
                        and expected_banner in proc.stdout
                        and "[PASS] g(N) = 251" in proc.stdout
                    )
                    record(ok, f"R5(28d 3|c SPRP2 {pkg_tag}, {mode_name}) [{vr_name}]",
                           f"rc={proc.returncode}")

            # Invalid edge package N=6, q=5 (c = N - 3 = 3): must raise clean AssertionError in BOTH modes
            edge_path = os.path.join(tmpdir, f"r5_edge_{vr_name}.json")
            with open(edge_path, "w", encoding="utf-8") as fh:
                json.dump(r5_edge_pkg, fh)
            for mode_name, block_gmpy2 in (("gmpy2", False), ("stdlib", True)):
                saved_gmpy2 = sys.modules.get("gmpy2")
                buf = io.StringIO()
                exc_got = None
                try:
                    if block_gmpy2:
                        sys.modules["gmpy2"] = None
                    with contextlib.redirect_stdout(buf):
                        vr_mod.main(edge_path)
                except Exception as exc:
                    exc_got = exc
                finally:
                    if block_gmpy2:
                        if saved_gmpy2 is None:
                            sys.modules.pop("gmpy2", None)
                        else:
                            sys.modules["gmpy2"] = saved_gmpy2
                banner_ok = (
                    "[info] pure stdlib mode" if block_gmpy2 else "[info] gmpy2 acceleration available"
                ) in buf.getvalue()
                ok = isinstance(exc_got, AssertionError) and banner_ok
                record(ok, f"R5(N=6 q=5 clean AssertionError, {mode_name}) [{vr_name}]",
                       f"{type(exc_got).__name__ if exc_got else 'ACCEPTED'}: {exc_got}")

            # Exhaustive fast_comp_gmpy2 vs sprp_composite(2/3) parity for n=2..10000 + 3|c SPRP2 specials
            r5_specials = [6559395693020281343352747891, 73150641067251, 2047, 1373653, 341550071728321]
            r5_vals = list(range(2, 10001)) + r5_specials
            mismatch = None
            for n_val in r5_vals:
                a_res = vr_mod.fast_comp_gmpy2(n_val, gmpy2)
                b_res = vr_mod.sprp_composite(n_val, 2) or vr_mod.sprp_composite(n_val, 3)
                if a_res is not b_res:
                    mismatch = (n_val, a_res, b_res)
                    break
            n2_ok = (
                vr_mod.sprp_composite(2, 2) is False
                and vr_mod.sprp_composite(2, 3) is False
                and vr_mod.fast_comp_gmpy2(2, gmpy2) is False
            )
            record(mismatch is None and n2_ok,
                   f"R5(fast_comp_gmpy2 == sprp_composite(2/3) parity n=2..10000+specials) [{vr_name}]",
                   f"checked={len(r5_vals)}, mismatch={mismatch}")

    # ------------------------------------------------------------------
    # 11. R6: PARI/GP crosscheck.gp code-injection / side-effect / RCE attacks (BUG-C2-2)
    # ------------------------------------------------------------------
    if gp_bin is not None:
        rec250_dir = os.path.join(REPO_ROOT, "goldbach", "records", "g200k_250digit_g201667")
        rec266_dir = os.path.join(REPO_ROOT, "goldbach", "records", "g200k_266digit_g203659")
        cc250_src = os.path.join(rec250_dir, "crosscheck.gp")
        with open(os.path.join(rec250_dir, "complement_cert.gp"), "r", encoding="utf-8") as fh:
            cert250_txt = fh.read()
        with open(os.path.join(rec266_dir, "N.txt"), "r", encoding="utf-8") as fh:
            n266_txt = fh.read().strip()
        with open(os.path.join(rec266_dir, "complement_cert.gp"), "r", encoding="utf-8") as fh:
            cert266_txt = fh.read()

        with tempfile.TemporaryDirectory() as tmpdir:
            sentinel_path = os.path.join(tmpdir, "r6_rce_sentinel")
            r6_cases = [
                (
                    "R6(crosscheck.gp overwrite N/g + valid 266d cert)",
                    f"N = {n266_txt}; g = 203659; {cert266_txt}",
                    None,
                    None,
                ),
                (
                    "R6(crosscheck.gp early quit(0))",
                    "quit(0)\n",
                    None,
                    None,
                ),
                (
                    "R6(crosscheck.gp forged stdout + quit(0))",
                    'print("primes p < g checked: 18113; isprime(g) = 1; isprime(N - g) = 1; '
                    'primecertisvalid(cert) = 1; N even: 1; digits: 250"); quit(0);\n',
                    "primes p < g checked:",
                    None,
                ),
                (
                    "R6(crosscheck.gp system() RCE blocked)",
                    f'system("touch {sentinel_path}"); {cert250_txt}',
                    None,
                    sentinel_path,
                ),
            ]
            for idx, (label, payload, forbid_substr, check_no_file) in enumerate(r6_cases):
                case_dir = os.path.join(tmpdir, f"case_{idx}")
                os.makedirs(case_dir, exist_ok=True)
                shutil.copy2(cc250_src, os.path.join(case_dir, "crosscheck.gp"))
                with open(os.path.join(case_dir, "complement_cert.gp"), "w", encoding="utf-8") as fh:
                    fh.write(payload)
                ts = time.monotonic()
                proc = subprocess.run(
                    [gp_bin, "-q", "--default", "colors=no", "crosscheck.gp"],
                    cwd=case_dir,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                )
                dt = time.monotonic() - ts
                ok = proc.returncode == 1 and "FAIL:" in proc.stdout
                if forbid_substr is not None and forbid_substr in proc.stdout:
                    ok = False
                if check_no_file is not None and os.path.exists(check_no_file):
                    ok = False
                record(ok, label, f"rc={proc.returncode}, {dt:.2f}s, out={proc.stdout.strip()!r}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    elapsed = time.monotonic() - t0
    print(f"\nSUMMARY: {passed} passed, {len(failures)} failed in {elapsed:.2f}s")
    if failures:
        print("FAILURES:")
        for item in failures:
            print(f"  - {item}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
