#!/usr/bin/env python3
"""Generate GoldbachGaps/Fscan/Fermat30.lean.

Usage: gen_fermat30.py GoldbachGaps/Fscan/Fermat30.lean

The model of FM3_STEP (goldbach/fscan/fermat26.h at commit 1d8ab96, the 3-limb, 30-bit
Montgomery step) is written once, as PROGRAM below, in program order. The Lean definition
`stepG`, the step-by-step proof of `machine_eq_exact` and the hypothesis list of
`spec_core` are derived from it, so the three cannot drift apart. Nothing here is trusted:
Lean checks the generated file like any other.
"""
import sys
import textwrap

X = 2**30 - 1          # a0, a1, m_i, n0, n1
Y2 = 2**28 - 1         # a2
N2 = 2**26 - 1         # n2
BOUND = {"a0": X, "a1": X, "a2": Y2, "d1": 2 * X, "d2": 2 * Y2, "m0": X, "m1": X, "m2": X,
         "n0": X, "n1": X, "n2": N2}


def M(p, q):
    return ("mul", p, q)


# (name, kind, operands, C source). kind: 'add' = 64-bit add of two operands, 'shl' = sllv,
# 'mul' = a bare vpmuludq product, 'red' = m = (z * ni) & mask.
PROGRAM = [
    ("d1", "add", ("a1", "a1"), "d1 = FM_ADD(a1, a1)"),
    ("d2", "add", ("a2", "a2"), "d2 = FM_ADD(a2, a2)"),
    ("z0", "mul", ("a0", "a0"), "z0 = FM_MUL(a0, a0)"),
    ("z1", "mul", ("a0", "d1"), "z1 = FM_MUL(a0, d1)"),
    ("z2", "add", (M("a0", "d2"), M("a1", "a1")), "z2 = FM_ADD(FM_MUL(a0, d2), FM_MUL(a1, a1))"),
    ("z3", "mul", ("a1", "d2"), "z3 = FM_MUL(a1, d2)"),
    ("z4", "mul", ("a2", "a2"), "z4 = FM_MUL(a2, a2)"),
    ("m0", "red", ("z0",), "m = FM_MUL(z0, ni) & mask"),
    ("y0", "add", ("z0", M("m0", "n0")), "z0 = FM_ADD(z0, FM_MUL(m, n0))"),
    ("z1a", "add", ("z1", M("m0", "n1")), "z1 = FM_ADD(z1, FM_MUL(m, n1))"),
    ("z2a", "add", ("z2", M("m0", "n2")), "z2 = FM_ADD(z2, FM_MUL(m, n2))"),
    ("z1b", "add", ("z1a", "y0 / B"), "z1 = FM_ADD(z1, srli(z0, 30))"),
    ("m1", "red", ("z1b",), "m = FM_MUL(z1, ni) & mask"),
    ("y1", "add", ("z1b", M("m1", "n0")), "z1 = FM_ADD(z1, FM_MUL(m, n0))"),
    ("z2b", "add", ("z2a", M("m1", "n1")), "z2 = FM_ADD(z2, FM_MUL(m, n1))"),
    ("z3a", "add", ("z3", M("m1", "n2")), "z3 = FM_ADD(z3, FM_MUL(m, n2))"),
    ("z2c", "add", ("z2b", "y1 / B"), "z2 = FM_ADD(z2, srli(z1, 30))"),
    ("m2", "red", ("z2c",), "m = FM_MUL(z2, ni) & mask"),
    ("y2", "add", ("z2c", M("m2", "n0")), "z2 = FM_ADD(z2, FM_MUL(m, n0))"),
    ("z3b", "add", ("z3a", M("m2", "n1")), "z3 = FM_ADD(z3, FM_MUL(m, n1))"),
    ("z4a", "add", ("z4", M("m2", "n2")), "z4 = FM_ADD(z4, FM_MUL(m, n2))"),
    ("z3c", "add", ("z3b", "y2 / B"), "z3 = FM_ADD(z3, srli(z2, 30))"),
    ("z3d", "shl", ("z3c", "b"), "z3 = sllv(z3, b)"),
    ("z4b", "shl", ("z4a", "b"), "z4 = sllv(z4, b)"),
    ("z4c", "add", ("z4b", "z3d / B"), "z4 = FM_ADD(z4, srli(z3, 30))"),
]
OUT = "((z3d % B, z4c % B, z4c / B),"
COLS = "(y0, y1, y2))"
TRACE = [n for (n, k, e, c) in PROGRAM if k in ("add", "shl")]


def par(s):
    return s if s.replace("_", "").isalnum() else f"({s})"


def gen_op(o):       # operand in the generic program
    return f"mulf {o[1]} {o[2]}" if isinstance(o, tuple) else o


def mach_op(o):      # operand in the machine program before rewriting
    return f"mul {o[1]} {o[2]}" if isinstance(o, tuple) else o


def ex_op(o):        # operand in the exact program
    return f"{o[1]} * {o[2]}" if isinstance(o, tuple) else o


def generic(kind, e):
    if kind == "add":
        return f"add {par(gen_op(e[0]))} {par(gen_op(e[1]))}"
    if kind == "shl":
        return f"shl {e[0]} {e[1]}"
    if kind == "mul":
        return f"mulf {e[0]} {e[1]}"
    return f"mred {e[0]} ni"


def exact(kind, e):
    if kind == "add":
        return f"{ex_op(e[0])} + {ex_op(e[1])}"
    if kind == "shl":
        return f"{e[0]} * 2 ^ {e[1]}"
    if kind == "mul":
        return f"{e[0]} * {e[1]}"
    return f"{e[0]} * ni % B"


L = []
w = L.append
w('''import Mathlib

/-!
# `FM3_STEP`: the Montgomery squaring step of the 3-limb, 30-bit (AVX2) Fermat kernel

This file models, one 64-bit lane at a time, the macro `FM3_STEP` of
`goldbach/fscan/fermat26.h` (lines 80–107 at commit `1d8ab96`, branch
`ccr-b8c25887-i6tn9f`) and proves the four claims of `goldbach/fscan/FERMAT26_STEP.md`
at that commit. The model was read from the macro, not from that note.

## The model

`stepG mulf mred add shl` is `FM3_STEP`, line for line, with four operations as parameters:
the limb product, the computation of the Montgomery multiplier `m`, the 64-bit addition
and the variable left shift.

* The machine is `stepG mul mulRed add64 shl64`: `mul x y = (x mod 2^32)·(y mod 2^32)`
  is `_mm256_mul_epu32`, `mulRed z k = mul z k % 2^30` is `FM_MUL(z, ni) & mask`, and
  additions and shifts wrap modulo `2^64`.
* The exact run is `stepG (· * ·) (fun z k => z * k % 2^30) (· + ·) (fun x k => x * 2 ^ k)`:
  true products and no wrapping.

`stepG` returns the new limbs, the list of every value produced by an addition or a shift,
and the three reduced columns (the values of `z0`, `z1`, `z2` right after
`z_i += m·n0`).

## Results (`B = 2^30`, `R = 2^90`, `n = n0 + n1·B + n2·B²`, `A = a0 + a1·B + a2·B²`)

* `machine_eq_exact` (claims C3 and C4): if `a0, a1 < B`, `a2 < 2^28`, `n0, n1 < B`,
  `n2 < 2^26` and `b ≤ 1`, the machine run equals the exact run (outputs, all intermediate
  values, reduced columns), and every value produced by an addition or a shift is below
  `2^62`. In particular every 32x32 multiply returns the true product and nothing wraps.
* `step_spec` (claims C1 and C2): if moreover `16·n ≤ 2^90`, `n0·ni ≡ -1 (mod B)` and
  `A < 4n`, then the three reduced columns are divisible by `B`; the output limbs satisfy
  `a0', a1' < B`, `a2' < 2^28`; `A' = a0' + a1'·B + a2'·B²` satisfies
  `2^90 · A' = 2^b · (A² + M·n)` for some `M < 2^90`; and `A' < 4n`.

Oddness of `n` is not assumed separately (it follows from the congruence), and `ni` is
unrestricted (only `ni mod 2^32` is read, and only its residue modulo `B` matters).

This file is generated by `scripts/gen_fermat30.py` from a single description of the
program. Lean checks it like any other file.
-/

namespace Fscan.F30

local notation "B" => (2 ^ 30 : ℕ)
local notation "B2" => (2 ^ 60 : ℕ)

/-- `_mm256_mul_epu32`: the product of the low 32 bits of two 64-bit lanes. -/
def mul (x y : ℕ) : ℕ := (x % 2 ^ 32) * (y % 2 ^ 32)

/-- `FM_MUL(z, k) & mask`: the low 30 bits of the 32x32 product. -/
def mulRed (z k : ℕ) : ℕ := mul z k % B

/-- `_mm256_add_epi64`: addition modulo `2^64`. -/
def add64 (x y : ℕ) : ℕ := (x + y) % 2 ^ 64

/-- `_mm256_sllv_epi64 x k` for a shift count `k < 64`: left shift modulo `2^64`. -/
def shl64 (x k : ℕ) : ℕ := x * 2 ^ k % 2 ^ 64

/-- `FM3_STEP` on one lane, line for line. `mulf` is the limb product, `mred z k` computes
`m = (z·k) & mask`, `add` is the 64-bit addition and `shl` the variable left shift.
Returns the new limbs `(a0, a1, a2)`, the list of all values produced by additions and
shifts, and the three reduced columns. -/
def stepG (mulf mred add shl : ℕ → ℕ → ℕ) (a0 a1 a2 n0 n1 n2 ni b : ℕ) :
    (ℕ × ℕ × ℕ) × List ℕ × (ℕ × ℕ × ℕ) :=''')
for (n, k, e, c) in PROGRAM:
    line = f"  let {n} := {generic(k, e)}"
    w(line + " " * max(1, 48 - len(line)) + f"-- {c}")
w(f"  {OUT}")
for t in textwrap.wrap("[" + ", ".join(TRACE) + "],", 90):
    w("    " + t)
w(f"    {COLS}")
w('''
/-- The machine step: new limbs, with 32-bit truncating multiplies and wrapping 64-bit
additions and shifts. -/
def step (a0 a1 a2 n0 n1 n2 ni b : ℕ) : ℕ × ℕ × ℕ :=
  (stepG mul mulRed add64 shl64 a0 a1 a2 n0 n1 n2 ni b).1

/-- The reduced columns of the machine step: `z0`, `z1`, `z2` right after `z_i += m·n0`. -/
def columns (a0 a1 a2 n0 n1 n2 ni b : ℕ) : ℕ × ℕ × ℕ :=
  (stepG mul mulRed add64 shl64 a0 a1 a2 n0 n1 n2 ni b).2.2

/-! ### Basic facts about the primitives -/

theorem mul_eq {x y : ℕ} (hx : x < 2 ^ 32) (hy : y < 2 ^ 32) : mul x y = x * y := by
  unfold mul
  rw [Nat.mod_eq_of_lt hx, Nat.mod_eq_of_lt hy]

theorem mul_modEq (x y : ℕ) : mul x y ≡ x * y [MOD B] :=
  Nat.ModEq.mul (Nat.mod_mod_of_dvd x (by norm_num)) (Nat.mod_mod_of_dvd y (by norm_num))

/-- Only the low 30 bits of `z` matter in `(z·k) & mask`, although the multiply truncates
`z` to 32 bits. -/
theorem mulRed_eq (z k : ℕ) : mulRed z k = z * k % B := mul_modEq z k

theorem add64_eq {x y : ℕ} (h : x + y < 2 ^ 64) : add64 x y = x + y := Nat.mod_eq_of_lt h

theorem shl64_eq {x k : ℕ} (h : x * 2 ^ k < 2 ^ 64) : shl64 x k = x * 2 ^ k := Nat.mod_eq_of_lt h

/-! ### Claims C3 and C4: exact multiplies, no overflow -/

/-- **The machine run is the exact run.** If `a0, a1 < 2^30`, `a2 < 2^28`, `n0, n1 < 2^30`,
`n2 < 2^26` and `b ≤ 1`, then `FM3_STEP` computed with 32-bit truncating multiplies and
wrapping 64-bit additions and shifts gives the same outputs, the same intermediate values
and the same reduced columns as the computation over `ℕ` with true products, and every
value produced by an addition or a shift is below `2^62`. -/
theorem machine_eq_exact {a0 a1 a2 n0 n1 n2 ni b : ℕ} (ha0 : a0 < B) (ha1 : a1 < B)
    (ha2 : a2 < 2 ^ 28) (hn0 : n0 < B) (hn1 : n1 < B) (hn2 : n2 < 2 ^ 26) (hb : b ≤ 1) :
    stepG mul mulRed add64 shl64 a0 a1 a2 n0 n1 n2 ni b =
        stepG (· * ·) (fun z k => z * k % B) (· + ·) (fun x k => x * 2 ^ k)
          a0 a1 a2 n0 n1 n2 ni b ∧
      ∀ v ∈ (stepG (· * ·) (fun z k => z * k % B) (· + ·) (fun x k => x * 2 ^ k)
          a0 a1 a2 n0 n1 n2 ni b).2.1, v < 2 ^ 62 := by
  have hb' : b = 0 ∨ b = 1 := by omega
  simp only [stepG]''')

fi = 0


def mul_rewrite(p, q):
    """Rewrite the truncating product `mul p q` as `p * q` and record a tight bound."""
    global fi
    fi += 1
    lit = BOUND[p] * BOUND[q]
    w(f"  have e : mul {p} {q} = {p} * {q} := mul_eq (by omega) (by omega)")
    w("  simp only [e]; clear e")
    w(f"  have f{fi} : {p} * {q} ≤ {lit} :=")
    w(f"    (Nat.mul_le_mul (show {p} ≤ {BOUND[p]} by omega) (show {q} ≤ {BOUND[q]} by omega)).trans")
    w("      (by norm_num)")


for (n, k, e, c) in PROGRAM:
    if k == "mul":
        mul_rewrite(*e)
        w(f"  set {n} := {e[0]} * {e[1]} with h{n}")
    elif k == "red":
        w(f"  have e : mulRed {e[0]} ni = {e[0]} * ni % B := mulRed_eq {e[0]} ni")
        w("  simp only [e]; clear e")
        w(f"  set {n} := {e[0]} * ni % B with h{n}")
        w(f"  have h{n}lt : {n} < B := by omega")
    elif k == "add":
        for o in e:
            if isinstance(o, tuple):
                mul_rewrite(o[1], o[2])
        x, y = ex_op(e[0]), ex_op(e[1])
        w(f"  have e : add64 {par(x)} {par(y)} = {x} + {y} := add64_eq (by omega)")
        w("  simp only [e]; clear e")
        w(f"  set {n} := {x} + {y} with h{n}")
    else:
        x = e[0]
        w(f"  have g{n} : {x} * 2 ^ b ≤ 2 * {x} := by")
        w("    rcases hb' with rfl | rfl <;> omega")
        w(f"  have e : shl64 {x} b = {x} * 2 ^ b := shl64_eq (by omega)")
        w("  simp only [e]; clear e")
        w(f"  set {n} := {x} * 2 ^ b with h{n}")
w("  refine ⟨trivial, ?_⟩")
w("  intro v hv")
w("  simp only [List.mem_cons, List.not_mem_nil, or_false] at hv")
pats = " | ".join(["rfl"] * len(TRACE))
for i, t in enumerate(textwrap.wrap("rcases hv with " + pats + " <;> omega", 92)):
    w(("  " if i == 0 else "    ") + t)

w('''
/-! ### Claims C1 and C2: the Montgomery relation and the range -/

/-- `z + m·n0` is divisible by `B` when `m = (z·ni) mod B` and `n0·ni ≡ -1 (mod B)`. -/
theorem mont_dvd (z n0 ni : ℕ) (hinv : (n0 * ni + 1) % B = 0) : B ∣ z + z * ni % B * n0 := by
  rw [← Nat.modEq_zero_iff_dvd]
  have h1 : z * ni % B * n0 ≡ z * ni * n0 [MOD B] := (Nat.mod_modEq _ _).mul_right n0
  have h3 : n0 * ni + 1 ≡ 0 [MOD B] := by
    show (n0 * ni + 1) % B = 0 % B
    rw [hinv, Nat.zero_mod]
  calc z + z * ni % B * n0 ≡ z + z * ni * n0 [MOD B] := (Nat.ModEq.refl z).add h1
    _ = z * (n0 * ni + 1) := by ring
    _ ≡ z * 0 [MOD B] := h3.mul_left z
    _ = 0 := by simp

/-- The algebraic core: the three reduction rounds add up. -/
theorem mont_algebra {V a0 a1 a2 n0 n1 n2 m0 m1 m2 c0 c1 c2 : ℕ}
    (E0 : a0 * a0 + m0 * n0 = V * c0)
    (E1 : a0 * (a1 + a1) + m0 * n1 + c0 + m1 * n0 = V * c1)
    (E2 : a0 * (a2 + a2) + a1 * a1 + m0 * n2 + m1 * n1 + c1 + m2 * n0 = V * c2) :
    (a0 + a1 * V + a2 * V ^ 2) ^ 2 + (m0 + m1 * V + m2 * V ^ 2) * (n0 + n1 * V + n2 * V ^ 2) =
      V ^ 3 * (a1 * (a2 + a2) + m1 * n2 + m2 * n1 + c2 + (a2 * a2 + m2 * n2) * V) := by
  zify at *
  linear_combination E0 + V * E1 + V ^ 2 * E2
''')

names = [n for (n, k, e, c) in PROGRAM]
w("/-- The specification of the exact run, with every intermediate value named. The limb\nsizes are not needed here: they are what makes the machine run equal to the exact one. -/")
for i, t in enumerate(textwrap.wrap("theorem spec_core {a0 a1 a2 n0 n1 n2 ni b " + " ".join(names) + " : ℕ}", 96)):
    w(("" if i == 0 else "    ") + t)
cur = "   "
for (n, k, e, c) in PROGRAM:
    h = f"(h_{n} : {n} = {exact(k, e)})"
    if len(cur) + len(h) + 1 > 98:
        w(cur)
        cur = "   "
    cur += " " + h
w(cur)
w('''    (hn : 16 * (n0 + n1 * B + n2 * B2) ≤ 2 ^ 90) (hinv : (n0 * ni + 1) % B = 0)
    (hA : a0 + a1 * B + a2 * B2 < 4 * (n0 + n1 * B + n2 * B2)) (hb : b ≤ 1) :
    (y0 % B = 0 ∧ y1 % B = 0 ∧ y2 % B = 0) ∧
      (∃ M < 2 ^ 90, 2 ^ 90 * (z3d % B + z4c % B * B + z4c / B * B2) =
        2 ^ b * ((a0 + a1 * B + a2 * B2) ^ 2 + M * (n0 + n1 * B + n2 * B2))) ∧
      z3d % B + z4c % B * B + z4c / B * B2 < 4 * (n0 + n1 * B + n2 * B2) ∧
      z4c / B < 2 ^ 28 := by
  -- the multipliers `m_i` are limbs
  have hm0 : m0 < B := h_m0 ▸ Nat.mod_lt _ (by norm_num)
  have hm1 : m1 < B := h_m1 ▸ Nat.mod_lt _ (by norm_num)
  have hm2 : m2 < B := h_m2 ▸ Nat.mod_lt _ (by norm_num)
  -- each reduction round makes its column a multiple of `B`
  have D0 : y0 = B * (y0 / B) := by
    have hd := mont_dvd z0 n0 ni hinv
    rw [← h_m0, ← h_y0] at hd
    exact (Nat.mul_div_cancel' hd).symm
  have D1 : y1 = B * (y1 / B) := by
    have hd := mont_dvd z1b n0 ni hinv
    rw [← h_m1, ← h_y1] at hd
    exact (Nat.mul_div_cancel' hd).symm
  have D2 : y2 = B * (y2 / B) := by
    have hd := mont_dvd z2c n0 ni hinv
    rw [← h_m2, ← h_y2] at hd
    exact (Nat.mul_div_cancel' hd).symm
  have hcols : y0 % B = 0 ∧ y1 % B = 0 ∧ y2 % B = 0 := by omega
  -- the squaring identity
  subst h_d1 h_d2
  have key : (a0 + a1 * B + a2 * B2) ^ 2 +
      (m0 + m1 * B + m2 * B2) * (n0 + n1 * B + n2 * B2) = 2 ^ 90 * (z3c + z4a * B) := by
    have halg := mont_algebra (V := B) (a0 := a0) (a1 := a1) (a2 := a2) (n0 := n0) (n1 := n1)
      (n2 := n2) (m0 := m0) (m1 := m1) (m2 := m2) (c0 := y0 / B) (c1 := y1 / B) (c2 := y2 / B)
      (by rw [← D0, h_y0, h_z0]) (by rw [← D1, h_y1, h_z1b, h_z1a, h_z1])
      (by rw [← D2, h_y2, h_z2c, h_z2b, h_z2a, h_z2])
    rw [show (B : ℕ) ^ 2 = B2 by norm_num, show (B : ℕ) ^ 3 = 2 ^ 90 by norm_num] at halg
    rw [h_z3c, h_z3b, h_z3a, h_z3, h_z4a, h_z4]
    exact halg
  -- the output, as a number
  have hA' : z3d % B + z4c % B * B + z4c / B * B2 = 2 ^ b * (z3c + z4a * B) := by
    interval_cases b <;> omega
  have hM : m0 + m1 * B + m2 * B2 < 2 ^ 90 := by omega
  have hR : z3c + z4a * B < 2 * (n0 + n1 * B + n2 * B2) := by
    have key' := key
    generalize a0 + a1 * B + a2 * B2 = A at hA key'
    generalize n0 + n1 * B + n2 * B2 = n at hA hn key' ⊢
    generalize m0 + m1 * B + m2 * B2 = M at hM key'
    generalize z3c + z4a * B = R at key' ⊢
    have h1 : A ^ 2 < 16 * n * n :=
      calc A ^ 2 = A * A := sq A
        _ < 4 * n * (4 * n) := Nat.mul_lt_mul'' hA hA
        _ = 16 * n * n := by ring
    have h2 : M * n ≤ 2 ^ 90 * n := Nat.mul_le_mul_right n hM.le
    have h3 : 16 * n * n ≤ 2 ^ 90 * n := Nat.mul_le_mul_right n hn
    have h4 : 2 ^ 90 * R < 2 ^ 90 * (2 * n) := by
      rw [← key']
      linarith
    exact Nat.lt_of_mul_lt_mul_left h4
  have hA'lt : z3d % B + z4c % B * B + z4c / B * B2 < 4 * (n0 + n1 * B + n2 * B2) := by
    rw [hA']
    interval_cases b <;> omega
  refine ⟨hcols, ⟨m0 + m1 * B + m2 * B2, hM, ?_⟩, hA'lt, by omega⟩
  rw [hA', key]
  ring

/-- **One step of the 3-limb kernel (claims C1 and C2).** Let `B = 2^30`,
`n = n0 + n1·B + n2·B²`, `A = a0 + a1·B + a2·B²`, and let `(a0', a1', a2') = step …` be the
output of `FM3_STEP` computed by the machine, `A' = a0' + a1'·B + a2'·B²`. If
`a0, a1 < B`, `a2 < 2^28`, `n0, n1 < B`, `n2 < 2^26`, `16·n ≤ 2^90`,
`n0·ni ≡ -1 (mod B)`, `A < 4n` and `b ≤ 1`, then

* the three reduced columns are multiples of `B` (the carries `z_i >> 30` are exact);
* `a0', a1' < B` and `a2' < 2^28`;
* `2^90 · A' = 2^b · (A² + M·n)` for some `M < 2^90`;
* `A' < 4n`, so the same hypotheses hold for the next step. -/
theorem step_spec {a0 a1 a2 n0 n1 n2 ni b : ℕ} (ha0 : a0 < B) (ha1 : a1 < B) (ha2 : a2 < 2 ^ 28)
    (hn0 : n0 < B) (hn1 : n1 < B) (hn2 : n2 < 2 ^ 26)
    (hn : 16 * (n0 + n1 * B + n2 * B2) ≤ 2 ^ 90) (hinv : (n0 * ni + 1) % B = 0)
    (hA : a0 + a1 * B + a2 * B2 < 4 * (n0 + n1 * B + n2 * B2)) (hb : b ≤ 1) :
    let r := step a0 a1 a2 n0 n1 n2 ni b
    let c := columns a0 a1 a2 n0 n1 n2 ni b
    (c.1 % B = 0 ∧ c.2.1 % B = 0 ∧ c.2.2 % B = 0) ∧
      (r.1 < B ∧ r.2.1 < B ∧ r.2.2 < 2 ^ 28) ∧
      (∃ M < 2 ^ 90, 2 ^ 90 * (r.1 + r.2.1 * B + r.2.2 * B2) =
        2 ^ b * ((a0 + a1 * B + a2 * B2) ^ 2 + M * (n0 + n1 * B + n2 * B2))) ∧
      r.1 + r.2.1 * B + r.2.2 * B2 < 4 * (n0 + n1 * B + n2 * B2) := by
  intro r c
  have hm := (machine_eq_exact (ni := ni) ha0 ha1 ha2 hn0 hn1 hn2 hb).1
  have hr : r = (stepG (· * ·) (fun z k => z * k % B) (· + ·) (fun x k => x * 2 ^ k)
      a0 a1 a2 n0 n1 n2 ni b).1 := by
    show step a0 a1 a2 n0 n1 n2 ni b = _
    rw [step, hm]
  have hc : c = (stepG (· * ·) (fun z k => z * k % B) (· + ·) (fun x k => x * 2 ^ k)
      a0 a1 a2 n0 n1 n2 ni b).2.2 := by
    show columns a0 a1 a2 n0 n1 n2 ni b = _
    rw [columns, hm]
  rw [hr, hc]
  simp only [stepG]''')
rfls = " ".join(["rfl"] * len(PROGRAM))
w("  obtain ⟨h0, h1, h2, h3⟩ := spec_core (ni := ni) (b := b)")
for t in textwrap.wrap(rfls, 92):
    w("    " + t)
w('''    hn hinv hA hb
  exact ⟨h0, ⟨Nat.mod_lt _ (by norm_num), Nat.mod_lt _ (by norm_num), h3⟩, h1, h2⟩

end Fscan.F30''')
open(sys.argv[1], "w").write("\n".join(L) + "\n")
print("wrote", sys.argv[1], "-", len(TRACE), "add/shift values")
