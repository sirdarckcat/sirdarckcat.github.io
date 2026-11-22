import GoldbachGaps.Fscan.Fermat30
import GoldbachGaps.Fscan.Kernel52

/-!
# One lane of the 3-limb, 30-bit (AVX2) Fermat kernel, end to end

The counterpart of `Kernel52` / `Kernel26` for `fm3_setup` / `fm3_run` in
`goldbach/fscan/fermat26.h` at commit `1d8ab96` (branch `ccr-b8c25887-i6tn9f`), where
`R = 2^90`: `F30.step_spec` (one `FM3_STEP`) and `Schedule.schedule_iffR` with `Rb = 90`
combine into: the value a lane of `fm3_run` ends with, after its two conditional
subtractions, is `1` exactly when `2^(n-1) ≡ 1 (mod n)`.

Modelled, for one lane: the start value `2^(90 - c)` (reduced modulo `n` when it is `≥ 4n`)
split into three 30-bit limbs, `t` iterations of `FM3_STEP` (`F30.step`: 32-bit truncating
multiplies, wrapping 64-bit additions and shifts) with shift count `betaR 90 n t i` at
iteration `i`, and the final two subtractions.

Assumed rather than modelled: the limbs satisfy `n = n0 + n1·2^30 + n2·2^60` with
`n0, n1 < 2^30`, `n2 < 2^26`; `ni` satisfies `n0·ni ≡ -1 (mod 2^30)`; and the shift
registers deliver the bits of `B` in the stated order.
-/

namespace Fscan.F30

open Fscan.Schedule
open Fscan.F52 (finalReduce finalReduce_eq startVal startVal_spec)

local notation "B" => (2 ^ 30 : ℕ)
local notation "B2" => (2 ^ 60 : ℕ)

/-- The number three limbs stand for. -/
def val (a : ℕ × ℕ × ℕ) : ℕ := a.1 + a.2.1 * B + a.2.2 * B2

/-- The three 30-bit limbs `fm3_setup` stores: `(y >> 30j) & M3`. -/
def limbs (y : ℕ) : ℕ × ℕ × ℕ := (y % B, y / B % B, y / B2 % B)

/-- The limb sizes the step needs: `a0, a1 < 2^30`, `a2 < 2^28`. -/
def Small (a : ℕ × ℕ × ℕ) : Prop := a.1 < B ∧ a.2.1 < B ∧ a.2.2 < 2 ^ 28

/-- `i` iterations of the loop of `fm3_run` on one lane; iteration `j` (from `1`) runs
`FM3_STEP` with shift count `β j`. -/
def iter (n0 n1 n2 ni : ℕ) (β : ℕ → ℕ) : ℕ → ℕ × ℕ × ℕ → ℕ × ℕ × ℕ
  | 0, a => a
  | i + 1, a =>
    step (iter n0 n1 n2 ni β i a).1 (iter n0 n1 n2 ni β i a).2.1 (iter n0 n1 n2 ni β i a).2.2
      n0 n1 n2 ni (β (i + 1))

theorem limbs_spec {y : ℕ} (hy : y < 2 ^ 88) : Small (limbs y) ∧ val (limbs y) = y := by
  refine ⟨⟨?_, ?_, ?_⟩, ?_⟩
  · show y % B < B
    omega
  · show y / B % B < B
    omega
  · show y / B2 % B < 2 ^ 28
    omega
  · show y % B + y / B % B * B + y / B2 % B * B2 = y
    omega

/-- One step, in the form the schedule needs. -/
theorem step_modEq {n n0 n1 n2 ni b : ℕ} (hnd : n = n0 + n1 * B + n2 * B2) (hn0 : n0 < B)
    (hn1 : n1 < B) (hn2 : n2 < 2 ^ 26) (hn : 16 * n ≤ 2 ^ 90)
    (hinv : (n0 * ni + 1) % B = 0) (hb : b ≤ 1) {a : ℕ × ℕ × ℕ} (ha : Small a)
    (hA : val a < 4 * n) :
    Small (step a.1 a.2.1 a.2.2 n0 n1 n2 ni b) ∧
      val (step a.1 a.2.1 a.2.2 n0 n1 n2 ni b) < 4 * n ∧
      2 ^ 90 * val (step a.1 a.2.1 a.2.2 n0 n1 n2 ni b) ≡ 2 ^ b * val a ^ 2 [MOD n] := by
  subst hnd
  obtain ⟨-, h1, ⟨M, -, hM⟩, h3⟩ :=
    step_spec (ni := ni) ha.1 ha.2.1 ha.2.2 hn0 hn1 hn2 hn hinv hA hb
  refine ⟨h1, h3, ?_⟩
  have e : 2 ^ b * ((a.1 + a.2.1 * B + a.2.2 * B2) ^ 2 + M * (n0 + n1 * B + n2 * B2)) =
      2 ^ b * (a.1 + a.2.1 * B + a.2.2 * B2) ^ 2 + 2 ^ b * M * (n0 + n1 * B + n2 * B2) := by
    ring
  show 2 ^ 90 * val (step a.1 a.2.1 a.2.2 n0 n1 n2 ni b) % (n0 + n1 * B + n2 * B2) =
    2 ^ b * (a.1 + a.2.1 * B + a.2.2 * B2) ^ 2 % (n0 + n1 * B + n2 * B2)
  unfold val
  rw [hM, e, Nat.add_mul_mod_self_right]

/-- Loop invariant: the limbs keep their sizes and the value stays below `4n`. -/
theorem iter_inv {n n0 n1 n2 ni : ℕ} {β : ℕ → ℕ} (hnd : n = n0 + n1 * B + n2 * B2)
    (hn0 : n0 < B) (hn1 : n1 < B) (hn2 : n2 < 2 ^ 26) (hn : 16 * n ≤ 2 ^ 90)
    (hinv : (n0 * ni + 1) % B = 0) (hβ : ∀ i, β i ≤ 1) {a : ℕ × ℕ × ℕ} (ha : Small a)
    (hA : val a < 4 * n) (i : ℕ) :
    Small (iter n0 n1 n2 ni β i a) ∧ val (iter n0 n1 n2 ni β i a) < 4 * n := by
  induction i with
  | zero => exact ⟨ha, hA⟩
  | succ i ih =>
    obtain ⟨h1, h2, -⟩ := step_modEq hnd hn0 hn1 hn2 hn hinv (hβ (i + 1)) ih.1 ih.2
    exact ⟨h1, h2⟩

/-- Consecutive lane values are related by the Montgomery step of the schedule. -/
theorem iter_step {n n0 n1 n2 ni : ℕ} {β : ℕ → ℕ} (hnd : n = n0 + n1 * B + n2 * B2)
    (hn0 : n0 < B) (hn1 : n1 < B) (hn2 : n2 < 2 ^ 26) (hn : 16 * n ≤ 2 ^ 90)
    (hinv : (n0 * ni + 1) % B = 0) (hβ : ∀ i, β i ≤ 1) {a : ℕ × ℕ × ℕ} (ha : Small a)
    (hA : val a < 4 * n) (i : ℕ) :
    2 ^ 90 * val (iter n0 n1 n2 ni β (i + 1) a) ≡
      2 ^ β (i + 1) * val (iter n0 n1 n2 ni β i a) ^ 2 [MOD n] :=
  (step_modEq hnd hn0 hn1 hn2 hn hinv (hβ (i + 1))
    (iter_inv hnd hn0 hn1 hn2 hn hinv hβ ha hA i).1
    (iter_inv hnd hn0 hn1 hn2 hn hinv hβ ha hA i).2).2.2

/-- **One lane of the 3-limb kernel is a base-2 Fermat test.** Let
`n = n0 + n1·2^30 + n2·2^60 > 1` with `n0, n1 < 2^30`, `n2 < 2^26`, `16n ≤ 2^90` and
`n0·ni ≡ -1 (mod 2^30)`, and let `t` be such that `c = ⌈(n + 89)/2^t⌉ ≤ 90`. Start from
`y = startVal n (90 - c)` split into three limbs, run `t` steps of `FM3_STEP` fed with the
bits of `B`, and apply the two final subtractions. The result is `1` if and only if
`2^(n-1) mod n = 1`. -/
theorem lane_correct {n n0 n1 n2 ni t : ℕ} (hnd : n = n0 + n1 * B + n2 * B2) (hn0 : n0 < B)
    (hn1 : n1 < B) (hn2 : n2 < 2 ^ 26) (hn : 16 * n ≤ 2 ^ 90)
    (hinv : (n0 * ni + 1) % B = 0) (hn' : 1 < n) (hc : cOfR 90 n t ≤ 90) :
    finalReduce (val (iter n0 n1 n2 ni (betaR 90 n t) t
        (limbs (startVal n (90 - cOfR 90 n t))))) n = 1 ↔ 2 ^ (n - 1) % n = 1 := by
  obtain ⟨hy4, hymod⟩ := startVal_spec (n := n) (e := 90 - cOfR 90 n t) (by omega)
  generalize startVal n (90 - cOfR 90 n t) = y at hy4 hymod ⊢
  obtain ⟨ha, hval0⟩ := limbs_spec (y := y) (by omega)
  have hA : val (limbs y) < 4 * n := by
    rw [hval0]
    exact hy4
  have hβ : ∀ i, betaR 90 n t i ≤ 1 := betaR_le_one 90 n t
  have hodd : n % 2 = 1 := by
    have hp : Odd (n0 * ni) := Nat.odd_iff.mpr (by omega)
    have := Nat.odd_iff.mp (Nat.odd_mul.mp hp).1
    omega
  have hiff := schedule_iffR (Rb := 90) (by norm_num) hodd hc
    (fun i => val (iter n0 n1 n2 ni (betaR 90 n t) i (limbs y)))
    (by
      show val (limbs y) ≡ _ [MOD n]
      rw [hval0]
      exact hymod)
    (fun i _ => iter_step hnd hn0 hn1 hn2 hn hinv hβ ha hA i)
  rw [finalReduce_eq (iter_inv hnd hn0 hn1 hn2 hn hinv hβ ha hA t).2]
  have h1 : (1 : ℕ) % n = 1 := Nat.mod_eq_of_lt hn'
  constructor
  · intro h
    have := hiff.mp (show _ % n = 1 % n by rw [h, h1])
    exact (show _ % n = 1 % n from this).trans h1
  · intro h
    have := hiff.mpr (show _ % n = 1 % n by rw [h, h1])
    exact (show _ % n = 1 % n from this).trans h1

end Fscan.F30
