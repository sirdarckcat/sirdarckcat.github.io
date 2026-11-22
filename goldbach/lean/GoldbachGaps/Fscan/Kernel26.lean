import GoldbachGaps.Fscan.Fermat26
import GoldbachGaps.Fscan.Kernel52

/-!
# One lane of the 26-bit (AVX2) Fermat kernel, end to end

The counterpart of `Kernel52` for `fermat26.h`: `F26.step_spec` (one `FM_STEP`) and
`Schedule.schedule_iff` combine into: the value a lane of `fm_run` ends with, after its
two conditional subtractions, is `1` exactly when `2^(n-1) ≡ 1 (mod n)`.

Modelled, for one lane: the start value of `fm_setup` split into four 26-bit limbs, `t`
iterations of `FM_STEP` (`F26.step`, wrapping 64-bit arithmetic) with shift count
`beta n t i` at iteration `i`, and the final two subtractions.

Assumed rather than modelled: the limbs satisfy `n = Σ n_j·2^(26j)` with `n_j < 2^26`;
`ni` satisfies `n0·ni ≡ -1 (mod 2^26)`; and the shift registers deliver the bits of `B` in
the stated order.
-/

namespace Fscan.F26

open Fscan.Schedule
open Fscan.F52 (finalReduce finalReduce_eq startVal startVal_spec)

local notation "W" => (2 ^ 26 : ℕ)
local notation "W2" => (2 ^ 52 : ℕ)
local notation "W3" => (2 ^ 78 : ℕ)

/-- The number four limbs stand for. -/
def val (a : ℕ × ℕ × ℕ × ℕ) : ℕ := a.1 + a.2.1 * W + a.2.2.1 * W2 + a.2.2.2 * W3

/-- The four 26-bit limbs `fm_setup` stores: `(y >> 26j) & M26`. -/
def limbs (y : ℕ) : ℕ × ℕ × ℕ × ℕ := (y % W, y / W % W, y / W2 % W, y / W3 % W)

/-- All four limbs are below `2^26`. -/
def Small (a : ℕ × ℕ × ℕ × ℕ) : Prop := a.1 < W ∧ a.2.1 < W ∧ a.2.2.1 < W ∧ a.2.2.2 < W

/-- `i` iterations of the loop of `fm_run` on one lane; iteration `j` (from `1`) runs
`FM_STEP` with shift count `β j`. -/
def iter (n0 n1 n2 n3 ni : ℕ) (β : ℕ → ℕ) : ℕ → ℕ × ℕ × ℕ × ℕ → ℕ × ℕ × ℕ × ℕ
  | 0, a => a
  | i + 1, a =>
    step (iter n0 n1 n2 n3 ni β i a).1 (iter n0 n1 n2 n3 ni β i a).2.1
      (iter n0 n1 n2 n3 ni β i a).2.2.1 (iter n0 n1 n2 n3 ni β i a).2.2.2 n0 n1 n2 n3 ni (β (i + 1))

theorem limbs_spec {y : ℕ} (hy : y < 2 ^ 104) : Small (limbs y) ∧ val (limbs y) = y := by
  refine ⟨⟨?_, ?_, ?_, ?_⟩, ?_⟩
  · show y % W < W
    omega
  · show y / W % W < W
    omega
  · show y / W2 % W < W
    omega
  · show y / W3 % W < W
    omega
  · show y % W + y / W % W * W + y / W2 % W * W2 + y / W3 % W * W3 = y
    omega

/-- One step, in the form the schedule needs. -/
theorem step_modEq {n n0 n1 n2 n3 ni b : ℕ} (hnd : n = n0 + n1 * W + n2 * W2 + n3 * W3)
    (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W) (hn3 : n3 < W) (hn : 16 * n ≤ 2 ^ 104)
    (hinv : (n0 * ni + 1) % W = 0) (hb : b ≤ 1) {a : ℕ × ℕ × ℕ × ℕ} (ha : Small a)
    (hA : val a < 4 * n) :
    Small (step a.1 a.2.1 a.2.2.1 a.2.2.2 n0 n1 n2 n3 ni b) ∧
      val (step a.1 a.2.1 a.2.2.1 a.2.2.2 n0 n1 n2 n3 ni b) < 4 * n ∧
      2 ^ 104 * val (step a.1 a.2.1 a.2.2.1 a.2.2.2 n0 n1 n2 n3 ni b) ≡
        2 ^ b * val a ^ 2 [MOD n] := by
  subst hnd
  obtain ⟨h1, ⟨M, -, hM⟩, h3⟩ :=
    step_spec ha.1 ha.2.1 ha.2.2.1 ha.2.2.2 hn0 hn1 hn2 hn3 hn hinv hA hb
  refine ⟨h1, h3, ?_⟩
  have e : 2 ^ b * ((a.1 + a.2.1 * W + a.2.2.1 * W2 + a.2.2.2 * W3) ^ 2 +
        M * (n0 + n1 * W + n2 * W2 + n3 * W3)) =
      2 ^ b * (a.1 + a.2.1 * W + a.2.2.1 * W2 + a.2.2.2 * W3) ^ 2 +
        2 ^ b * M * (n0 + n1 * W + n2 * W2 + n3 * W3) := by ring
  show 2 ^ 104 * val (step a.1 a.2.1 a.2.2.1 a.2.2.2 n0 n1 n2 n3 ni b) %
      (n0 + n1 * W + n2 * W2 + n3 * W3) =
    2 ^ b * (a.1 + a.2.1 * W + a.2.2.1 * W2 + a.2.2.2 * W3) ^ 2 %
      (n0 + n1 * W + n2 * W2 + n3 * W3)
  unfold val
  rw [hM, e, Nat.add_mul_mod_self_right]

/-- Loop invariant: the limbs stay below `2^26` and the value below `4n`. -/
theorem iter_inv {n n0 n1 n2 n3 ni : ℕ} {β : ℕ → ℕ}
    (hnd : n = n0 + n1 * W + n2 * W2 + n3 * W3) (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W)
    (hn3 : n3 < W) (hn : 16 * n ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0)
    (hβ : ∀ i, β i ≤ 1) {a : ℕ × ℕ × ℕ × ℕ} (ha : Small a) (hA : val a < 4 * n) (i : ℕ) :
    Small (iter n0 n1 n2 n3 ni β i a) ∧ val (iter n0 n1 n2 n3 ni β i a) < 4 * n := by
  induction i with
  | zero => exact ⟨ha, hA⟩
  | succ i ih =>
    obtain ⟨h1, h2, -⟩ :=
      step_modEq hnd hn0 hn1 hn2 hn3 hn hinv (hβ (i + 1)) ih.1 ih.2
    exact ⟨h1, h2⟩

/-- Consecutive lane values are related by the Montgomery step of the schedule. -/
theorem iter_step {n n0 n1 n2 n3 ni : ℕ} {β : ℕ → ℕ}
    (hnd : n = n0 + n1 * W + n2 * W2 + n3 * W3) (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W)
    (hn3 : n3 < W) (hn : 16 * n ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0)
    (hβ : ∀ i, β i ≤ 1) {a : ℕ × ℕ × ℕ × ℕ} (ha : Small a) (hA : val a < 4 * n) (i : ℕ) :
    2 ^ 104 * val (iter n0 n1 n2 n3 ni β (i + 1) a) ≡
      2 ^ β (i + 1) * val (iter n0 n1 n2 n3 ni β i a) ^ 2 [MOD n] :=
  (step_modEq hnd hn0 hn1 hn2 hn3 hn hinv (hβ (i + 1))
    (iter_inv hnd hn0 hn1 hn2 hn3 hn hinv hβ ha hA i).1
    (iter_inv hnd hn0 hn1 hn2 hn3 hn hinv hβ ha hA i).2).2.2

/-- **One lane of the 26-bit kernel is a base-2 Fermat test.** Let
`n = n0 + n1·2^26 + n2·2^52 + n3·2^78 > 1` with all `n_j < 2^26`, `16n ≤ 2^104` and
`n0·ni ≡ -1 (mod 2^26)`, and let `t` be such that `c = ⌈(n + 103)/2^t⌉ ≤ 104`. Start from
`y = startVal n (104 - c)` split into four limbs, run `t` steps of `FM_STEP` fed with the
bits of `B`, and apply the two final subtractions. The result is `1` if and only if
`2^(n-1) mod n = 1`. -/
theorem lane_correct {n n0 n1 n2 n3 ni t : ℕ} (hnd : n = n0 + n1 * W + n2 * W2 + n3 * W3)
    (hn0 : n0 < W) (hn1 : n1 < W) (hn2 : n2 < W) (hn3 : n3 < W) (hn : 16 * n ≤ 2 ^ 104)
    (hinv : (n0 * ni + 1) % W = 0) (hn' : 1 < n) (hc : cOf n t ≤ 104) :
    finalReduce (val (iter n0 n1 n2 n3 ni (beta n t) t
        (limbs (startVal n (104 - cOf n t))))) n = 1 ↔ 2 ^ (n - 1) % n = 1 := by
  obtain ⟨hy4, hymod⟩ := startVal_spec (n := n) (e := 104 - cOf n t) (by omega)
  generalize startVal n (104 - cOf n t) = y at hy4 hymod ⊢
  obtain ⟨ha, hval0⟩ := limbs_spec (y := y) (by omega)
  have hA : val (limbs y) < 4 * n := by
    rw [hval0]
    exact hy4
  have hβ : ∀ i, beta n t i ≤ 1 := beta_le_one n t
  have hodd : n % 2 = 1 := by
    have hp : Odd (n0 * ni) := Nat.odd_iff.mpr (by omega)
    have := Nat.odd_iff.mp (Nat.odd_mul.mp hp).1
    omega
  have hiff := schedule_iff hodd hc
    (fun i => val (iter n0 n1 n2 n3 ni (beta n t) i (limbs y)))
    (by
      show val (limbs y) ≡ _ [MOD n]
      rw [hval0]
      exact hymod)
    (fun i _ => iter_step hnd hn0 hn1 hn2 hn3 hn hinv hβ ha hA i)
  rw [finalReduce_eq (iter_inv hnd hn0 hn1 hn2 hn3 hn hinv hβ ha hA t).2]
  have h1 : (1 : ℕ) % n = 1 := Nat.mod_eq_of_lt hn'
  constructor
  · intro h
    have := hiff.mp (show _ % n = 1 % n by rw [h, h1])
    exact (show _ % n = 1 % n from this).trans h1
  · intro h
    have := hiff.mpr (show _ % n = 1 % n by rw [h, h1])
    exact (show _ % n = 1 % n from this).trans h1

end Fscan.F26
