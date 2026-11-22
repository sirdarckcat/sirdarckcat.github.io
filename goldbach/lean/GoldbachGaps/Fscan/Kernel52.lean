import GoldbachGaps.Fscan.Fermat52
import GoldbachGaps.Fscan.Schedule

/-!
# One lane of the 52-bit Fermat kernel, end to end

`F52.step_spec` (one `F52_STEP`) and `Schedule.schedule_iff` (the exponent schedule)
combine into: the value a lane of `f52_run` ends with, after its two conditional
subtractions, is `1` exactly when `2^(n-1) ≡ 1 (mod n)`.

What is modelled here, for one lane:
* the start value of `f52_setup`: `y = 2^(104 - c)`, reduced modulo `n` when `y ≥ 4n`,
  split as `a0 = y mod 2^52`, `a1 = y div 2^52`;
* `t` iterations of `F52_STEP` (`F52.step`, wrapping 64-bit arithmetic), the `i`-th with
  shift count `beta n t i` = bit `t - i` of `B`;
* the final `y -= 2n if y ≥ 2n; y -= n if y ≥ n; result = (y == 1)`.

What is assumed rather than modelled: the limbs satisfy `n = n0 + n1·2^52` with
`n0, n1 < 2^52`; `ni` satisfies `n0·ni ≡ -1 (mod 2^52)` (the code gets it by Newton
iteration); and the shift registers `bh`, `bl` deliver the bits of `B` in the stated order.
-/

namespace Fscan.F52

open Fscan.Schedule

local notation "W" => (2 ^ 52 : ℕ)

/-- The number a lane `(a0, a1)` stands for: `(a0 mod 2^52) + a1·2^52`. -/
def val (a : ℕ × ℕ) : ℕ := a.1 % W + a.2 * W

/-- `i` iterations of the loop of `f52_run` on one lane; iteration `j` (from `1`) runs
`F52_STEP` with shift count `β j`. -/
def iter (n0 n1 ni : ℕ) (β : ℕ → ℕ) : ℕ → ℕ × ℕ → ℕ × ℕ
  | 0, a => a
  | i + 1, a =>
    step (iter n0 n1 ni β i a).1 (iter n0 n1 ni β i a).2 n0 n1 ni (β (i + 1))

/-- The end of `f52_run`: `y -= 2n if y ≥ 2n; y -= n if y ≥ n`. -/
def finalReduce (y n : ℕ) : ℕ :=
  let y1 := if 2 * n ≤ y then y - 2 * n else y
  if n ≤ y1 then y1 - n else y1

theorem finalReduce_eq {y n : ℕ} (h : y < 4 * n) : finalReduce y n = y % n := by
  have key : ∀ r k : ℕ, r < n → y = r + k * n → y % n = r := fun r k hr hy => by
    rw [hy, Nat.add_mul_mod_self_right, Nat.mod_eq_of_lt hr]
  unfold finalReduce
  simp only
  split_ifs with h1 h2 h2
  · exact (key (y - 2 * n - n) 3 (by omega) (by omega)).symm
  · exact (key (y - 2 * n) 2 (by omega) (by omega)).symm
  · exact (key (y - n) 1 (by omega) (by omega)).symm
  · exact (key y 0 (by omega) (by omega)).symm

/-- The start value of `f52_setup`: `y = 1 << e; if (y >= 4n) y %= n`. -/
def startVal (n e : ℕ) : ℕ := if 4 * n ≤ 2 ^ e then 2 ^ e % n else 2 ^ e

theorem startVal_spec {n e : ℕ} (hn : 0 < n) :
    startVal n e < 4 * n ∧ startVal n e ≡ 2 ^ e [MOD n] := by
  unfold startVal
  split_ifs with h
  · exact ⟨lt_of_lt_of_le (Nat.mod_lt _ hn) (by omega), Nat.mod_modEq _ _⟩
  · exact ⟨by omega, Nat.ModEq.refl _⟩

/-- One step, in the form the schedule needs. -/
theorem step_modEq {n n0 n1 ni b : ℕ} (hnd : n = n0 + n1 * W) (hn0 : n0 < W) (hn1 : n1 < W)
    (hn : 16 * n ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0) (hb : b ≤ 1) {a : ℕ × ℕ}
    (ha1 : a.2 < 2 ^ 50) (hA : val a < 4 * n) :
    (step a.1 a.2 n0 n1 ni b).2 < 2 ^ 50 ∧ val (step a.1 a.2 n0 n1 ni b) < 4 * n ∧
      2 ^ 104 * val (step a.1 a.2 n0 n1 ni b) ≡ 2 ^ b * val a ^ 2 [MOD n] := by
  subst hnd
  obtain ⟨⟨M, -, hM⟩, h3, h4⟩ := step_spec hn0 hn1 hn hinv ha1 hA hb
  refine ⟨h4, h3, ?_⟩
  have e : 2 ^ b * ((a.1 % W + a.2 * W) ^ 2 + M * (n0 + n1 * W)) =
      2 ^ b * (a.1 % W + a.2 * W) ^ 2 + 2 ^ b * M * (n0 + n1 * W) := by ring
  show 2 ^ 104 * ((step a.1 a.2 n0 n1 ni b).1 % W + (step a.1 a.2 n0 n1 ni b).2 * W) %
      (n0 + n1 * W) = 2 ^ b * (a.1 % W + a.2 * W) ^ 2 % (n0 + n1 * W)
  rw [hM, e, Nat.add_mul_mod_self_right]

/-- Loop invariant: after any number of iterations the lane still satisfies the
hypotheses of `step_spec`. -/
theorem iter_inv {n n0 n1 ni : ℕ} {β : ℕ → ℕ} (hnd : n = n0 + n1 * W) (hn0 : n0 < W)
    (hn1 : n1 < W) (hn : 16 * n ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0) (hβ : ∀ i, β i ≤ 1)
    {a : ℕ × ℕ} (ha1 : a.2 < 2 ^ 50) (hA : val a < 4 * n) (i : ℕ) :
    (iter n0 n1 ni β i a).2 < 2 ^ 50 ∧ val (iter n0 n1 ni β i a) < 4 * n := by
  induction i with
  | zero => exact ⟨ha1, hA⟩
  | succ i ih =>
    obtain ⟨h1, h2, -⟩ := step_modEq hnd hn0 hn1 hn hinv (hβ (i + 1)) ih.1 ih.2
    exact ⟨h1, h2⟩

/-- Consecutive lane values are related by the Montgomery step of the schedule. -/
theorem iter_step {n n0 n1 ni : ℕ} {β : ℕ → ℕ} (hnd : n = n0 + n1 * W) (hn0 : n0 < W)
    (hn1 : n1 < W) (hn : 16 * n ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0) (hβ : ∀ i, β i ≤ 1)
    {a : ℕ × ℕ} (ha1 : a.2 < 2 ^ 50) (hA : val a < 4 * n) (i : ℕ) :
    2 ^ 104 * val (iter n0 n1 ni β (i + 1) a) ≡
      2 ^ β (i + 1) * val (iter n0 n1 ni β i a) ^ 2 [MOD n] :=
  (step_modEq hnd hn0 hn1 hn hinv (hβ (i + 1)) (iter_inv hnd hn0 hn1 hn hinv hβ ha1 hA i).1
    (iter_inv hnd hn0 hn1 hn hinv hβ ha1 hA i).2).2.2

/-- **One lane of the kernel is a base-2 Fermat test.** Let `n = n0 + n1·2^52 > 1` with
`n0, n1 < 2^52`, `16n ≤ 2^104` and `n0·ni ≡ -1 (mod 2^52)`, and let `t` be such that
`c = ⌈(n + 103)/2^t⌉ ≤ 104`. Start from `y = startVal n (104 - c)` split into two limbs,
run `t` steps of `F52_STEP` fed with the bits of `B`, and apply the two final
subtractions. The result is `1` if and only if `2^(n-1) mod n = 1`. -/
theorem lane_correct {n n0 n1 ni t : ℕ} (hnd : n = n0 + n1 * W) (hn0 : n0 < W) (hn1 : n1 < W)
    (hn : 16 * n ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0) (hn2 : 1 < n)
    (hc : cOf n t ≤ 104) :
    finalReduce (val (iter n0 n1 ni (beta n t) t
        (startVal n (104 - cOf n t) % W, startVal n (104 - cOf n t) / W))) n = 1 ↔
      2 ^ (n - 1) % n = 1 := by
  obtain ⟨hy4, hymod⟩ := startVal_spec (n := n) (e := 104 - cOf n t) (by omega)
  generalize startVal n (104 - cOf n t) = y at hy4 hymod ⊢
  -- the start lane
  have hval0 : val (y % W, y / W) = y := by
    unfold val
    simp only [Nat.mod_mod]
    exact Nat.mod_add_div' y W
  have ha1 : (y % W, y / W).2 < 2 ^ 50 := by
    show y / W < 2 ^ 50
    omega
  have hA : val (y % W, y / W) < 4 * n := by
    rw [hval0]
    exact hy4
  have hβ : ∀ i, beta n t i ≤ 1 := fun i => by
    unfold beta
    omega
  -- `n` is odd
  have hodd : n % 2 = 1 := by
    have hp : Odd (n0 * ni) := Nat.odd_iff.mpr (by omega)
    have := Nat.odd_iff.mp (Nat.odd_mul.mp hp).1
    omega
  -- the schedule, applied to the sequence of lane values
  have hiff := schedule_iff hodd hc (fun i => val (iter n0 n1 ni (beta n t) i (y % W, y / W)))
    (by
      show val (y % W, y / W) ≡ _ [MOD n]
      rw [hval0]
      exact hymod)
    (fun i _ => iter_step hnd hn0 hn1 hn hinv hβ ha1 hA i)
  rw [finalReduce_eq (iter_inv hnd hn0 hn1 hn hinv hβ ha1 hA t).2]
  have h1 : (1 : ℕ) % n = 1 := Nat.mod_eq_of_lt hn2
  constructor
  · intro h
    have := hiff.mp (show _ % n = 1 % n by rw [h, h1])
    exact (show _ % n = 1 % n from this).trans h1
  · intro h
    have := hiff.mpr (show _ % n = 1 % n by rw [h, h1])
    exact (show _ % n = 1 % n from this).trans h1

end Fscan.F52
