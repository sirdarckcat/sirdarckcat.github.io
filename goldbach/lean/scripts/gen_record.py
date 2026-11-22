#!/usr/bin/env python3
"""Generate a Lean certificate file for a least-Goldbach-summand record.

Usage:
    gen_record.py RECORD LEAN_NAMESPACE OUTPUT.lean [NAME_OF_SOURCE_TO_PRINT]

RECORD is either
  * a directory in the `goldbach/records/` layout: `record.json` (fields N, g, cover)
    plus `complement_cert.gp`, a PARI/GP `primecert` Atkin-Morain certificate for N - g; or
  * a JSON file in the `slop/goldbach/records/` layout (fields N, q, classes, ecpp_cert).

The output proves `IsLeastSummand N g` from kernel-evaluated Boolean tests:
`GoldbachGaps.desertBlockCheck` (no prime in a block of offsets is a summand; one
theorem per block of BLOCK offsets) and `GoldbachGaps.ECPP.stepCheck` (one per
certificate step, proving N - g prime).

Nothing computed here is trusted by Lean. This script only chooses the data the
tests run on, and replays both tests in Python first so that a failure shows up
here rather than as a kernel `decide` error.
"""
import json
import math
import os
import sys

sys.setrecursionlimit(1_000_000)

# Offsets per block theorem. Each block is one kernel evaluation; keeping blocks small
# keeps the kernel's memory use bounded (one evaluation over all of [0, g) needs >10 GB).
BLOCK = 8192


def primes_below(n):
    sieve = bytearray([1]) * n
    sieve[0:2] = b"\0\0"
    for i in range(2, math.isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i in range(n) if sieve[i]]


# --- reference semantics of GoldbachGaps.ECPP (affine, generic formulas only) ---


def inv_aux(a, m):
    if a <= 1:
        return a
    return m - (m * inv_aux(m % a, a) - 1) // a


def ec_dbl(N, a, P):
    x, y = P
    d = 2 * y % N
    i = inv_aux(d, N)
    if d * i % N != 1:
        return None
    lam = (3 * x * x + a) * i % N
    x3 = (lam * lam - 2 * x) % N
    return (x3, (lam * (x - x3) - y) % N)


def ec_add(N, P, Q):
    d = (P[0] - Q[0]) % N
    i = inv_aux(d, N)
    if d * i % N != 1:
        return None
    lam = (P[1] - Q[1]) * i % N
    x3 = (lam * lam - P[0] - Q[0]) % N
    return (x3, (lam * (P[0] - x3) - P[1]) % N)


def ec_mul(N, a, P, k):
    if k <= 1:
        return P
    Q = ec_mul(N, a, P, k // 2)
    if Q is None:
        return None
    D = ec_dbl(N, a, Q)
    if D is None or k % 2 == 0:
        return D
    return ec_add(N, D, P)


def step_check(N, a, x, y, s, q):
    if not (1 < N and 1 <= s and 4 * N < (q - 1) ** 2):
        return False
    if 2 * y % N * inv_aux(2 * y % N, N) % N != 1:
        return False
    R = ec_mul(N, a, (x, y), s)
    if R is None:
        return False
    Z = ec_mul(N, a, R, q - 1)
    return Z is not None and Z[0] % N == R[0] % N and (Z[1] + R[1]) % N == 0


def lean_list(xs, indent="  ", width=96):
    lines, cur = [], indent + "["
    for i, x in enumerate(xs):
        tok = str(x) + ("," if i + 1 < len(xs) else "]")
        if len(cur) + len(tok) + 1 > width:
            lines.append(cur)
            cur = indent + " " + tok
        else:
            cur += ("" if cur.endswith("[") else " ") + tok
    if not xs:
        cur += "]"
    lines.append(cur)
    return "\n".join(lines)


def load_record(path):
    """Return (N, g, covering moduli, ECPP certificate) from either record layout."""
    if os.path.isdir(path):
        rec = json.load(open(f"{path}/record.json"))
        cert = json.loads(open(f"{path}/complement_cert.gp").read().strip().rstrip(";"))
        return int(rec["N"]), int(rec["g"]), [int(c[0]) for c in rec["cover"]], cert
    rec = json.load(open(path))
    return int(rec["N"]), int(rec["q"]), [int(c[0]) for c in rec["classes"]], rec["ecpp_cert"]


def main():
    record_dir, namespace, out_path = sys.argv[1:4]
    # Name of the source as printed in the Lean file (optional 4th argument). Lean block
    # comments nest, so a path containing `/-` or `-/` must not be copied verbatim.
    label = sys.argv[4] if len(sys.argv) > 4 else record_dir
    label = label.replace("/-", "/ -").replace("-/", "- /")
    N, g, cover_mods, cert = load_record(record_dir)
    cover_mods = sorted(set(cover_mods))

    # --- negative side: replay desertListsCheck / desertBlockCheck ---
    small_primes = primes_below(math.isqrt(g) + 1)
    assert g + 2 < N and all(r >= 2 and r + g < N for r in cover_mods)
    residuals = []
    for q in range(2, g):
        if any(d < q and q % d == 0 for d in small_primes):
            continue
        if any((N - q) % r == 0 for r in cover_mods):
            continue
        residuals.append(q)
    for q in residuals:
        m = N - q
        assert pow(2, m - 1, m) != 1, f"N - {q} passes the base-2 Fermat test"

    # --- positive side: replay the ECPP chain ---
    steps = []
    expect = N - g
    for Ni, t, s, a, (x, y) in cert:
        assert Ni == expect, "certificate chain does not start at N - g / is broken"
        m = Ni + 1 - t
        assert m % s == 0
        q = m // s
        args = (Ni, a % Ni, x % Ni, y % Ni, s, q)
        assert step_check(*args), "step rejected by the affine reference checker"
        steps.append(args)
        expect = q
    final_q = expect

    L = []
    L.append("import GoldbachGaps.Desert")
    L.append("import GoldbachGaps.ECPP")
    L.append("")
    L.append("/-!")
    L.append(f"# Kernel-checked record: the least Goldbach summand of a {len(str(N))}-digit `N` is `{g}`")
    L.append("")
    L.append(f"Generated by `scripts/gen_record.py` from `{label}`; do not edit by hand.")
    L.append("The data below (covering moduli, residual offsets, ECPP certificate) is not trusted:")
    L.append("Lean's kernel re-evaluates every `desertBlockCheck` and every `stepCheck`.")
    L.append("-/")
    L.append("")
    L.append(f"namespace GoldbachGaps.{namespace}")
    L.append("")
    L.append("open GoldbachGaps.ECPP")
    L.append("")
    L.append("/-- The record integer. -/")
    L.append(f"def N : ℕ :=\n  {N}")
    L.append("")
    L.append("/-- Its least Goldbach summand. -/")
    L.append(f"def g : ℕ := {g}")
    L.append("")
    L.append(f"/-- `N` has {len(str(N))} digits. -/")
    L.append(f"theorem N_lt : N < 10 ^ {len(str(N))} := by decide +kernel")
    L.append("")
    L.append(f"/-- The {len(cover_mods)} moduli of the covering system. -/")
    L.append("def coverMods : List ℕ :=\n" + lean_list(cover_mods))
    L.append("")
    L.append("/-- Trial divisors, enough to discard every composite `q < g`. -/")
    L.append("def smallPrimes : List ℕ :=\n" + lean_list(small_primes))
    L.append("")
    L.append("theorem lists : desertListsCheck N g coverMods smallPrimes = true := by")
    L.append("  decide +kernel")
    L.append("")
    L.append(f"/-! ### Negative side: the {len(residuals)} residual offsets, block by block -/")
    L.append("")
    blocks = []
    for k, lo in enumerate(range(0, g, BLOCK)):
        hi = min(lo + BLOCK, g)
        res = [q for q in residuals if lo <= q < hi]
        blocks.append(k)
        L.append(f"/-- The primes `q` in `[{lo}, {hi})` not handled by the covering system. -/")
        L.append(f"def res{k} : List ℕ :=\n" + lean_list(res))
        L.append("")
        L.append("set_option maxRecDepth 1000000 in")
        L.append(f"theorem block{k} : NoSummandIn N {lo} {hi} :=")
        L.append(f"  noSummandIn_of_desertBlockCheck (g := g) (lo := {lo}) (len := {hi - lo})")
        L.append(f"    (residuals := res{k}) lists (by decide +kernel) (by decide)")
        L.append("")
    L.append("/-- No `q < g` is a Goldbach summand of `N`. -/")
    L.append("theorem noSummand : NoSummandIn N 0 g :=")
    L.append("  " + " <|\n  ".join(f"block{k}.append" for k in blocks[:-1]) + f" <|\n  block{blocks[-1]}")
    L.append("")
    L.append("theorem prime_g : g.Prime := by norm_num [g]")
    L.append("")
    L.append("/-! ### Positive side: the Atkin–Morain certificate for `N - g` -/")
    L.append("")
    n = len(steps)
    L.append(f"theorem prime_c{n} : Nat.Prime {final_q} := by primality")
    L.append("")
    for i in range(n - 1, -1, -1):
        Ni, a, x, y, s, q = steps[i]
        L.append("set_option maxRecDepth 100000 in")
        L.append(f"theorem prime_c{i} : Nat.Prime\n    {Ni} :=")
        L.append("  prime_of_stepCheck")
        L.append(f"    (a := {a})")
        L.append(f"    (x := {x})")
        L.append(f"    (y := {y})")
        L.append(f"    (s := {s})")
        L.append(f"    (q := {q})")
        L.append(f"    prime_c{i + 1} (by decide +kernel)")
        L.append("")
    L.append("theorem prime_complement : (N - g).Prime := by")
    L.append(f"  have h : N - g =\n      {N - g} := by")
    L.append("    decide +kernel")
    L.append("  rw [h]")
    L.append("  exact prime_c0")
    L.append("")
    L.append(f"/-- **The record.** `{g}` is the least Goldbach summand of `N`. -/")
    L.append("theorem isLeastSummand : IsLeastSummand N g :=")
    L.append("  isLeastSummand_of_noSummandIn noSummand prime_g prime_complement")
    L.append("")
    L.append("/-- The same statement with the definitions unfolded. -/")
    L.append("theorem record :")
    L.append(f"    Nat.Prime {g} ∧ Nat.Prime (N - {g}) ∧")
    L.append(f"      ∀ p : ℕ, p.Prime → (N - p).Prime → {g} ≤ p :=")
    L.append("  ⟨isLeastSummand.1.1, isLeastSummand.1.2, fun p hp hq => isLeastSummand.2 p ⟨hp, hq⟩⟩")
    L.append("")
    L.append(f"end GoldbachGaps.{namespace}")
    L.append("")
    open(out_path, "w").write("\n".join(L))
    print(
        f"wrote {out_path}: N has {len(str(N))} digits, g = {g}, {len(cover_mods)} moduli, "
        f"{len(residuals)} residuals, {n} ECPP steps, final prime {final_q}"
    )


if __name__ == "__main__":
    main()
