#!/usr/bin/env python3
"""Generate GoldbachGaps/Fscan/Fermat26.lean.

Usage: gen_fermat26.py GoldbachGaps/Fscan/Fermat26.lean

The model of FM_STEP (goldbach/fscan/fermat26.h) is written once, as PROGRAM below, in
program order. The Lean definition `stepG`, the step-by-step proof of `no_overflow` and
the hypothesis list of `spec_core` are derived from it, so the three cannot drift apart.
Nothing here is trusted: Lean checks the generated file like any other.
"""
import sys

# (name, kind, expr) in program order. kind: 'add' (64-bit add: expr = (x, y)),
# 'shl' (variable shift: expr = (x, 'b')), 'pure' (no 64-bit add/shift: expr is a string).
PROGRAM = [
 ("d1","add",("a1","a1"), "d1 = _mm256_add_epi64(a1, a1)"),
 ("d2","add",("a2","a2"), "d2 = _mm256_add_epi64(a2, a2)"),
 ("d3","add",("a3","a3"), "d3 = _mm256_add_epi64(a3, a3)"),
 ("z0","pure","mul a0 a0", "z0 = FM_MUL(a0, a0)"),
 ("z1","pure","mul a0 d1", "z1 = FM_MUL(a0, d1)"),
 ("z2","add",("mul a0 d2","mul a1 a1"), "z2 = FM_ADD(FM_MUL(a0, d2), FM_MUL(a1, a1))"),
 ("z3","add",("mul a0 d3","mul a1 d2"), "z3 = FM_ADD(FM_MUL(a0, d3), FM_MUL(a1, d2))"),
 ("z4","add",("mul a1 d3","mul a2 a2"), "z4 = FM_ADD(FM_MUL(a1, d3), FM_MUL(a2, a2))"),
 ("z5","pure","mul a2 d3", "z5 = FM_MUL(a2, d3)"),
 ("z6","pure","mul a3 a3", "z6 = FM_MUL(a3, a3)"),
 # FM_RED(z0, z1, z2, z3, z4)
 ("m0","pure","mul z0 ni % W", "FM_RED(z0, ..): m = FM_MUL(z0, ni) & mask"),
 ("y0","add",("z0","mul m0 n0"), "z0 = FM_ADD(z0, FM_MUL(m, n0))"),
 ("z1a","add",("z1","mul m0 n1"), "z1 = FM_ADD(z1, FM_MUL(m, n1))"),
 ("z2a","add",("z2","mul m0 n2"), "z2 = FM_ADD(z2, FM_MUL(m, n2))"),
 ("z3a","add",("z3","mul m0 n3"), "z3 = FM_ADD(z3, FM_MUL(m, n3))"),
 ("z1b","add",("z1a","y0 / W"), "z1 = FM_ADD(z1, srli(z0, 26))"),
 # FM_RED(z1, z2, z3, z4, z5)
 ("m1","pure","mul z1b ni % W", "FM_RED(z1, ..): m = FM_MUL(z1, ni) & mask"),
 ("y1","add",("z1b","mul m1 n0"), "z1 = FM_ADD(z1, FM_MUL(m, n0))"),
 ("z2b","add",("z2a","mul m1 n1"), "z2 = FM_ADD(z2, FM_MUL(m, n1))"),
 ("z3b","add",("z3a","mul m1 n2"), "z3 = FM_ADD(z3, FM_MUL(m, n2))"),
 ("z4a","add",("z4","mul m1 n3"), "z4 = FM_ADD(z4, FM_MUL(m, n3))"),
 ("z2c","add",("z2b","y1 / W"), "z2 = FM_ADD(z2, srli(z1, 26))"),
 # FM_RED(z2, z3, z4, z5, z6)
 ("m2","pure","mul z2c ni % W", "FM_RED(z2, ..): m = FM_MUL(z2, ni) & mask"),
 ("y2","add",("z2c","mul m2 n0"), "z2 = FM_ADD(z2, FM_MUL(m, n0))"),
 ("z3c","add",("z3b","mul m2 n1"), "z3 = FM_ADD(z3, FM_MUL(m, n1))"),
 ("z4b","add",("z4a","mul m2 n2"), "z4 = FM_ADD(z4, FM_MUL(m, n2))"),
 ("z5a","add",("z5","mul m2 n3"), "z5 = FM_ADD(z5, FM_MUL(m, n3))"),
 ("z3d","add",("z3c","y2 / W"), "z3 = FM_ADD(z3, srli(z2, 26))"),
 # FM_RED(z3, z4, z5, z6, z6)
 ("m3","pure","mul z3d ni % W", "FM_RED(z3, ..): m = FM_MUL(z3, ni) & mask"),
 ("y3","add",("z3d","mul m3 n0"), "z3 = FM_ADD(z3, FM_MUL(m, n0))"),
 ("z4c","add",("z4b","mul m3 n1"), "z4 = FM_ADD(z4, FM_MUL(m, n1))"),
 ("z5b","add",("z5a","mul m3 n2"), "z5 = FM_ADD(z5, FM_MUL(m, n2))"),
 ("z6a","add",("z6","mul m3 n3"), "z6 = FM_ADD(z6, FM_MUL(m, n3))"),
 ("z4d","add",("z4c","y3 / W"), "z4 = FM_ADD(z4, srli(z3, 26))"),
 # shift and renormalise
 ("z4e","shl",("z4d","b"), "z4 = sllv(z4, b)"),
 ("z5c","shl",("z5b","b"), "z5 = sllv(z5, b)"),
 ("z6b","shl",("z6a","b"), "z6 = sllv(z6, b)"),
 ("z5d","add",("z5c","z4e / W"), "z5 = FM_ADD(z5, srli(z4, 26))"),
 ("z6c","add",("z6b","z5d / W"), "z6 = FM_ADD(z6, srli(z5, 26))"),
]
OUT = "(z4e % W, z5d % W, z6c % W, z6c / W)"
TRACE = [n for (n,k,e,c) in PROGRAM if k != "pure"]

def wrapped(kind, e, add="add", shl="shl"):
    if kind == "pure": return e
    f = add if kind == "add" else shl
    def par(s): return s if s.replace("_","").isalnum() else f"({s})"
    return f"{f} {par(e[0])} {par(e[1])}"
def exact(kind, e):
    if kind == "pure": return e
    return f"{e[0]} + {e[1]}" if kind == "add" else f"{e[0]} * 2 ^ {e[1]}"

L = []
w = L.append
w('''import Mathlib

/-!
# `FM_STEP`: the Montgomery squaring step of the 26-bit (AVX2) Fermat kernel

This file models, one 64-bit lane at a time, the macros `FM_RED` and `FM_STEP` of
`goldbach/fscan/fermat26.h` (lines 48–79 at commit `a3ab69c`, branch
`ccr-d4a17dd0-7uu03r`) and proves that the step is a Montgomery squaring with `R = 2^104`
followed by an optional doubling, with no 64-bit overflow.

## The model

`stepG add shl` is `FM_STEP` with the four `FM_RED` expanded, line for line, with the
64-bit addition and the variable left shift as parameters:

* `step = stepG add64 shl64` is the machine: additions and shifts wrap modulo `2^64`;
* `stepG (· + ·) (fun x k => x * 2 ^ k)` is the same program over `ℕ`, without wrapping.

`mul x y = (x mod 2^32) · (y mod 2^32)` is `_mm256_mul_epu32`, which reads the low 32 bits
of each 64-bit lane and never overflows. `& mask` is `% 2^26` and `srli(·, 26)` is
`/ 2^26`. `stepG` also returns every value produced by an addition or a shift.

## Results (`W = 2^26`, four limbs)

* `no_overflow`: if all `a_j < W`, all `n_j < W` and `b ≤ 1`, the wrapping run and the
  exact run agree on the outputs and on every intermediate value, and every such value is
  below `2^58`.
* `step_spec`: if moreover `16·n ≤ 2^104`, `n0·ni ≡ -1 (mod W)` and `A < 4n`, where
  `n = Σ n_j W^j` and `A = Σ a_j W^j`, then the outputs `a'_j` are all `< W`, and
  `A' = Σ a'_j W^j` satisfies `2^104 · A' = 2^b · (A² + M·n)` for some `M < 2^104`, and
  `A' < 4n`.

Oddness of `n` is not assumed separately (it follows from the congruence), and `ni` is
unrestricted (only `ni mod 2^32` is read, and only its residue modulo `W` matters).

This file is generated by `scripts/gen_fermat26.py` from a single description of the
program: `stepG`, the proof of `no_overflow` and the hypotheses of `spec_core` follow the
program text mechanically. Lean checks it like any other file.
-/

namespace Fscan.F26

local notation "W" => (2 ^ 26 : ℕ)
local notation "W2" => (2 ^ 52 : ℕ)
local notation "W3" => (2 ^ 78 : ℕ)

/-- `_mm256_mul_epu32`: the product of the low 32 bits of two 64-bit lanes. -/
def mul (x y : ℕ) : ℕ := (x % 2 ^ 32) * (y % 2 ^ 32)

/-- `_mm256_add_epi64`: addition modulo `2^64`. -/
def add64 (x y : ℕ) : ℕ := (x + y) % 2 ^ 64

/-- `_mm256_sllv_epi64 x k` for a shift count `k < 64`: left shift modulo `2^64`. -/
def shl64 (x k : ℕ) : ℕ := x * 2 ^ k % 2 ^ 64

/-- `FM_STEP` on one lane, with the four `FM_RED` expanded, line for line; `add` is the
64-bit addition and `shl` the variable left shift. Returns the new limbs
`(a0, a1, a2, a3)` and the list of all values produced by additions and shifts. -/
def stepG (add shl : ℕ → ℕ → ℕ) (a0 a1 a2 a3 n0 n1 n2 n3 ni b : ℕ) :
    (ℕ × ℕ × ℕ × ℕ) × List ℕ :=''')
for (n,k,e,c) in PROGRAM:
    line = f"  let {n} := {wrapped(k,e)}"
    w(line + " " * max(1, 46 - len(line)) + f"-- {c}")
w(f"  ({OUT},")
tr = ", ".join(TRACE)
# wrap trace
import textwrap
tl = textwrap.wrap("[" + tr + "])", 90)
for t in tl: w("    " + t)
w('''
/-- The machine step: new limbs with wrapping 64-bit arithmetic. -/
def step (a0 a1 a2 a3 n0 n1 n2 n3 ni b : ℕ) : ℕ × ℕ × ℕ × ℕ :=
  (stepG add64 shl64 a0 a1 a2 a3 n0 n1 n2 n3 ni b).1

/-! ### Basic facts about the primitives -/

theorem mul_eq {x y : ℕ} (hx : x < 2 ^ 32) (hy : y < 2 ^ 32) : mul x y = x * y := by
  unfold mul
  rw [Nat.mod_eq_of_lt hx, Nat.mod_eq_of_lt hy]

theorem mul_lt52 {x y : ℕ} (hx : x < 2 ^ 26) (hy : y < 2 ^ 26) : mul x y < 2 ^ 52 := by
  rw [mul_eq (by omega) (by omega)]
  calc x * y < 2 ^ 26 * 2 ^ 26 := Nat.mul_lt_mul'' hx hy
    _ = 2 ^ 52 := by norm_num

theorem mul_lt53 {x y : ℕ} (hx : x < 2 ^ 26) (hy : y < 2 ^ 27) : mul x y < 2 ^ 53 := by
  rw [mul_eq (by omega) (by omega)]
  calc x * y < 2 ^ 26 * 2 ^ 27 := Nat.mul_lt_mul'' hx hy
    _ = 2 ^ 53 := by norm_num

theorem mul_modEq (x y : ℕ) : mul x y ≡ x * y [MOD W] :=
  Nat.ModEq.mul (Nat.mod_mod_of_dvd x (by norm_num)) (Nat.mod_mod_of_dvd y (by norm_num))

theorem add64_eq {x y : ℕ} (h : x + y < 2 ^ 64) : add64 x y = x + y := Nat.mod_eq_of_lt h

theorem shl64_eq {x k : ℕ} (h : x * 2 ^ k < 2 ^ 64) : shl64 x k = x * 2 ^ k := Nat.mod_eq_of_lt h

/-! ### No overflow -/

/-- **No 64-bit operation overflows.** If all limbs `a_j` and `n_j` are below `2^26` and
`b ≤ 1`, then running `FM_STEP` with wrapping 64-bit arithmetic gives the same outputs and
the same intermediate values as running it over `ℕ`, and every value produced by an
addition or a shift is below `2^58`. -/
theorem no_overflow {a0 a1 a2 a3 n0 n1 n2 n3 ni b : ℕ} (ha0 : a0 < W) (ha1 : a1 < W)
    (ha2 : a2 < W) (ha3 : a3 < W) (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W) (hn3 : n3 < W)
    (hb : b ≤ 1) :
    stepG add64 shl64 a0 a1 a2 a3 n0 n1 n2 n3 ni b =
        stepG (· + ·) (fun x k => x * 2 ^ k) a0 a1 a2 a3 n0 n1 n2 n3 ni b ∧
      ∀ v ∈ (stepG (· + ·) (fun x k => x * 2 ^ k) a0 a1 a2 a3 n0 n1 n2 n3 ni b).2,
        v < 2 ^ 58 := by
  have hb' : b = 0 ∨ b = 1 := by omega
  simp only [stepG]''')

# facts about mul terms: decide which lemma applies from operand names
def mulfact(term, idx):
    # term like "mul a0 d2"
    _, x, y = term.split()
    def bound(v):
        if v.startswith("a") and len(v)==2: return ("26", f"h{v}")
        if v.startswith("n") and len(v)==2 and v[1].isdigit(): return ("26", f"h{v}")
        if v.startswith("d"): return ("27", "(by omega)")
        if v.startswith("m"): return ("26", f"h{v}lt")
        raise ValueError(v)
    bx, px = bound(x); by, py = bound(y)
    assert bx == "26"
    lem = "mul_lt52" if by == "26" else "mul_lt53"
    return f"  have f{idx} := {lem} (x := {x}) (y := {y}) {px} {py}"

fi = 0
for (n,k,e,c) in PROGRAM:
    if k == "pure":
        # name it; add facts
        if n.startswith("m"):
            w(f"  set {n} := {e} with h{n}")
            w(f"  have h{n}lt : {n} < W := by omega")
        else:
            fi += 1
            w(mulfact(e, fi))
            w(f"  set {n} := {e} with h{n}")
        continue
    x, y = e
    for t in (x, y):
        if t.startswith("mul "):
            fi += 1
            w(mulfact(t, fi))
    if k == "add":
        def par(s): return s if s.replace("_","").isalnum() else f"({s})"
        w(f"  have e : add64 {par(x)} {par(y)} = {x} + {y} := add64_eq (by omega)")
        w(f"  simp only [e]; clear e")
        w(f"  set {n} := {x} + {y} with h{n}")
    else:
        w(f"  have g{n} : {x} * 2 ^ b ≤ 2 * {x} := by")
        w(f"    rcases hb' with rfl | rfl <;> omega")
        w(f"  have e : shl64 {x} b = {x} * 2 ^ b := shl64_eq (by omega)")
        w(f"  simp only [e]; clear e")
        w(f"  set {n} := {x} * 2 ^ b with h{n}")
w("  refine ⟨trivial, ?_⟩")
w("  intro v hv")
w("  simp only [List.mem_cons, List.not_mem_nil, or_false] at hv")
pats = " | ".join(["rfl"] * len(TRACE))
for i, t in enumerate(textwrap.wrap("rcases hv with " + pats + " <;> omega", 92)):
    w(("  " if i == 0 else "    ") + t)

names = [n for (n,k,e,c) in PROGRAM]
w('''
/-! ### The Montgomery relation -/

/-- `z + m·n0` is divisible by `W` when `m = (z·ni) mod W` and `n0·ni ≡ -1 (mod W)`. -/
theorem mont_dvd (z n0 ni : ℕ) (hinv : (n0 * ni + 1) % W = 0) : W ∣ z + mul z ni % W * n0 := by
  rw [← Nat.modEq_zero_iff_dvd]
  have h1 : mul z ni % W * n0 ≡ z * ni * n0 [MOD W] :=
    ((Nat.mod_modEq _ _).trans (mul_modEq z ni)).mul_right n0
  have h3 : n0 * ni + 1 ≡ 0 [MOD W] := by
    show (n0 * ni + 1) % W = 0 % W
    rw [hinv, Nat.zero_mod]
  calc z + mul z ni % W * n0 ≡ z + z * ni * n0 [MOD W] := (Nat.ModEq.refl z).add h1
    _ = z * (n0 * ni + 1) := by ring
    _ ≡ z * 0 [MOD W] := h3.mul_left z
    _ = 0 := by simp

/-- The algebraic core: the four reduction rounds add up. -/
theorem mont_algebra {V a0 a1 a2 a3 n0 n1 n2 n3 m0 m1 m2 m3 c0 c1 c2 c3 : ℕ}
    (E0 : a0 * a0 + m0 * n0 = V * c0)
    (E1 : a0 * (a1 + a1) + m0 * n1 + c0 + m1 * n0 = V * c1)
    (E2 : a0 * (a2 + a2) + a1 * a1 + m0 * n2 + m1 * n1 + c1 + m2 * n0 = V * c2)
    (E3 : a0 * (a3 + a3) + a1 * (a2 + a2) + m0 * n3 + m1 * n2 + m2 * n1 + c2 + m3 * n0 =
      V * c3) :
    (a0 + a1 * V + a2 * V ^ 2 + a3 * V ^ 3) ^ 2 +
        (m0 + m1 * V + m2 * V ^ 2 + m3 * V ^ 3) * (n0 + n1 * V + n2 * V ^ 2 + n3 * V ^ 3) =
      V ^ 4 * (a1 * (a3 + a3) + a2 * a2 + m1 * n3 + m2 * n2 + m3 * n1 + c3 +
        (a2 * (a3 + a3) + m2 * n3 + m3 * n2) * V + (a3 * a3 + m3 * n3) * V ^ 2) := by
  zify at *
  linear_combination E0 + V * E1 + V ^ 2 * E2 + V ^ 3 * E3
''')

# spec_core
w("/-- The specification of the exact run, with every intermediate value named. -/")
vars_ = " ".join(names)
for i, t in enumerate(textwrap.wrap("theorem spec_core {a0 a1 a2 a3 n0 n1 n2 n3 ni b " + vars_ + " : ℕ}", 96)):
    w(("" if i == 0 else "    ") + t)
hyps = []
for (n,k,e,c) in PROGRAM:
    hyps.append(f"(h_{n} : {n} = {exact(k,e)})")
cur = "   "
for h in hyps:
    if len(cur) + len(h) + 1 > 98:
        w(cur); cur = "   "
    cur += " " + h
w(cur)
w('''    (ha0 : a0 < W) (ha1 : a1 < W) (ha2 : a2 < W) (ha3 : a3 < W)
    (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W) (hn3 : n3 < W)
    (hn : 16 * (n0 + n1 * W + n2 * W2 + n3 * W3) ≤ 2 ^ 104)
    (hinv : (n0 * ni + 1) % W = 0)
    (hA : a0 + a1 * W + a2 * W2 + a3 * W3 < 4 * (n0 + n1 * W + n2 * W2 + n3 * W3))
    (hb : b ≤ 1) :
    (∃ M < 2 ^ 104, 2 ^ 104 * (z4e % W + z5d % W * W + z6c % W * W2 + z6c / W * W3) =
        2 ^ b * ((a0 + a1 * W + a2 * W2 + a3 * W3) ^ 2 +
          M * (n0 + n1 * W + n2 * W2 + n3 * W3))) ∧
      z4e % W + z5d % W * W + z6c % W * W2 + z6c / W * W3 <
        4 * (n0 + n1 * W + n2 * W2 + n3 * W3) ∧
      z6c / W < W := by
  -- the multipliers `m_i` are limbs
  have hm0 : m0 < W := h_m0 ▸ Nat.mod_lt _ (by norm_num)
  have hm1 : m1 < W := h_m1 ▸ Nat.mod_lt _ (by norm_num)
  have hm2 : m2 < W := h_m2 ▸ Nat.mod_lt _ (by norm_num)
  have hm3 : m3 < W := h_m3 ▸ Nat.mod_lt _ (by norm_num)
  -- every 32x32 multiply is exact
  have hd1 : d1 < 2 ^ 32 := by omega
  have hd2 : d2 < 2 ^ 32 := by omega
  have hd3 : d3 < 2 ^ 32 := by omega''')
# list all distinct mul terms except those with z*ni
mults = []
for (n,k,e,c) in PROGRAM:
    terms = [e] if k == "pure" else list(e)
    for t in terms:
        if t.startswith("mul ") and " ni" not in t and t not in mults:
            mults.append(t)
for i, t in enumerate(mults):
    _, x, y = t.split()
    w(f"  have q{i} : mul {x} {y} = {x} * {y} := mul_eq (by omega) (by omega)")
for (n,k,e,c) in PROGRAM:
    terms = [e] if k == "pure" else list(e)
    used = [f"q{mults.index(t)}" for t in terms if t in mults]
    if used:
        w(f"  rw [{', '.join(used)}] at h_{n}")
w('''  -- each reduction round makes its column a multiple of `W`
  have D0 : y0 = W * (y0 / W) := by
    have hd := mont_dvd z0 n0 ni hinv
    rw [← h_m0, ← h_y0] at hd
    exact (Nat.mul_div_cancel' hd).symm
  have D1 : y1 = W * (y1 / W) := by
    have hd := mont_dvd z1b n0 ni hinv
    rw [← h_m1, ← h_y1] at hd
    exact (Nat.mul_div_cancel' hd).symm
  have D2 : y2 = W * (y2 / W) := by
    have hd := mont_dvd z2c n0 ni hinv
    rw [← h_m2, ← h_y2] at hd
    exact (Nat.mul_div_cancel' hd).symm
  have D3 : y3 = W * (y3 / W) := by
    have hd := mont_dvd z3d n0 ni hinv
    rw [← h_m3, ← h_y3] at hd
    exact (Nat.mul_div_cancel' hd).symm
  -- the squaring identity
  subst h_d1 h_d2 h_d3
  have key : (a0 + a1 * W + a2 * W2 + a3 * W3) ^ 2 +
      (m0 + m1 * W + m2 * W2 + m3 * W3) * (n0 + n1 * W + n2 * W2 + n3 * W3) =
      2 ^ 104 * (z4d + z5b * W + z6a * W2) := by
    have halg := mont_algebra (V := W) (a0 := a0) (a1 := a1) (a2 := a2) (a3 := a3) (n0 := n0)
      (n1 := n1) (n2 := n2) (n3 := n3) (m0 := m0) (m1 := m1) (m2 := m2) (m3 := m3)
      (c0 := y0 / W) (c1 := y1 / W) (c2 := y2 / W) (c3 := y3 / W)
      (by rw [← D0, h_y0, h_z0]) (by rw [← D1, h_y1, h_z1b, h_z1a, h_z1])
      (by rw [← D2, h_y2, h_z2c, h_z2b, h_z2a, h_z2])
      (by rw [← D3, h_y3, h_z3d, h_z3c, h_z3b, h_z3a, h_z3])
    rw [show (W : ℕ) ^ 2 = W2 by norm_num, show (W : ℕ) ^ 3 = W3 by norm_num,
      show (W : ℕ) ^ 4 = 2 ^ 104 by norm_num] at halg
    rw [h_z4d, h_z4c, h_z4b, h_z4a, h_z4, h_z5b, h_z5a, h_z5, h_z6a, h_z6]
    exact halg
  -- the output, as a number
  have hA' : z4e % W + z5d % W * W + z6c % W * W2 + z6c / W * W3 =
      2 ^ b * (z4d + z5b * W + z6a * W2) := by
    interval_cases b <;> omega
  have hM : m0 + m1 * W + m2 * W2 + m3 * W3 < 2 ^ 104 := by omega
  have hR : z4d + z5b * W + z6a * W2 < 2 * (n0 + n1 * W + n2 * W2 + n3 * W3) := by
    have key' := key
    generalize a0 + a1 * W + a2 * W2 + a3 * W3 = A at hA key'
    generalize n0 + n1 * W + n2 * W2 + n3 * W3 = n at hA hn key' ⊢
    generalize m0 + m1 * W + m2 * W2 + m3 * W3 = M at hM key'
    generalize z4d + z5b * W + z6a * W2 = R at key' ⊢
    have h1 : A ^ 2 < 16 * n * n :=
      calc A ^ 2 = A * A := sq A
        _ < 4 * n * (4 * n) := Nat.mul_lt_mul'' hA hA
        _ = 16 * n * n := by ring
    have h2 : M * n ≤ 2 ^ 104 * n := Nat.mul_le_mul_right n hM.le
    have h3 : 16 * n * n ≤ 2 ^ 104 * n := Nat.mul_le_mul_right n hn
    have h4 : 2 ^ 104 * R < 2 ^ 104 * (2 * n) := by
      rw [← key']
      linarith
    exact Nat.lt_of_mul_lt_mul_left h4
  have hA'lt : z4e % W + z5d % W * W + z6c % W * W2 + z6c / W * W3 <
      4 * (n0 + n1 * W + n2 * W2 + n3 * W3) := by
    rw [hA']
    interval_cases b <;> omega
  refine ⟨⟨m0 + m1 * W + m2 * W2 + m3 * W3, hM, ?_⟩, hA'lt, by omega⟩
  rw [hA', key]
  ring

/-- **One step of the 26-bit kernel.** Let `W = 2^26`, `n = Σ n_j W^j`, `A = Σ a_j W^j`,
and let `(a0', a1', a2', a3') = step …` be the output of `FM_STEP` computed with wrapping
64-bit arithmetic, `A' = Σ a'_j W^j`. If all `a_j, n_j < W`, `16·n ≤ 2^104`,
`n0·ni ≡ -1 (mod W)`, `A < 4n` and `b ≤ 1`, then

* all four output limbs are below `W`;
* `2^104 · A' = 2^b · (A² + M·n)` for some `M < 2^104`;
* `A' < 4n`, so the same hypotheses hold for the next step. -/
theorem step_spec {a0 a1 a2 a3 n0 n1 n2 n3 ni b : ℕ} (ha0 : a0 < W) (ha1 : a1 < W)
    (ha2 : a2 < W) (ha3 : a3 < W) (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W) (hn3 : n3 < W)
    (hn : 16 * (n0 + n1 * W + n2 * W2 + n3 * W3) ≤ 2 ^ 104)
    (hinv : (n0 * ni + 1) % W = 0)
    (hA : a0 + a1 * W + a2 * W2 + a3 * W3 < 4 * (n0 + n1 * W + n2 * W2 + n3 * W3))
    (hb : b ≤ 1) :
    let r := step a0 a1 a2 a3 n0 n1 n2 n3 ni b
    (r.1 < W ∧ r.2.1 < W ∧ r.2.2.1 < W ∧ r.2.2.2 < W) ∧
      (∃ M < 2 ^ 104, 2 ^ 104 * (r.1 + r.2.1 * W + r.2.2.1 * W2 + r.2.2.2 * W3) =
        2 ^ b * ((a0 + a1 * W + a2 * W2 + a3 * W3) ^ 2 +
          M * (n0 + n1 * W + n2 * W2 + n3 * W3))) ∧
      r.1 + r.2.1 * W + r.2.2.1 * W2 + r.2.2.2 * W3 <
        4 * (n0 + n1 * W + n2 * W2 + n3 * W3) := by
  intro r
  have hr : r = (stepG (· + ·) (fun x k => x * 2 ^ k) a0 a1 a2 a3 n0 n1 n2 n3 ni b).1 := by
    show step a0 a1 a2 a3 n0 n1 n2 n3 ni b = _
    rw [step, (no_overflow ha0 ha1 ha2 ha3 hn0 hn1 hn2 hn3 hb).1]
  rw [hr]
  simp only [stepG]''')
rfls = " ".join(["rfl"] * len(PROGRAM))
w("  obtain ⟨h1, h2, h3⟩ := spec_core (ni := ni) (b := b)")
for i, t in enumerate(textwrap.wrap(rfls, 92)):
    w("    " + t)
w('''    ha0 ha1 ha2 ha3 hn0 hn1 hn2 hn3 hn hinv hA hb
  exact ⟨⟨Nat.mod_lt _ (by norm_num), Nat.mod_lt _ (by norm_num), Nat.mod_lt _ (by norm_num), h3⟩,
    h1, h2⟩

end Fscan.F26''')
open(sys.argv[1], "w").write("\n".join(L) + "\n")
print("wrote", sys.argv[1], len(L), "lines;", len(TRACE), "add/shift values")
