import Mathlib

/-!
# The residue computation of `exact_stage`

The first loop of `exact_stage` in `goldbach/fscan/fscan.c` (lines 212–219 at commit
`a3ab69c`, branch `ccr-d4a17dd0-7uu03r`) reduces 16-bit lanes `x` modulo small primes `s`
without a division, using the precomputed `rec = ⌊65536 / s⌋`:

    q = mulhi_epu16(x, rec);          // ⌊x · rec / 65536⌋
    x = sub_epi16(x, mullo_epi16(q, s));
    x = min_epu16(x, sub_epi16(x, s));

`classOf_eq` proves that the result is `x mod s` for every `0 < s < 2^16` and `x < 2^16`
(the code uses primes `47 ≤ s ≤ 1021` and `x < s + 512`), that `q · s ≤ x` (so the 16-bit
multiplication and subtraction do not wrap) and that the remainder before the final `min`
is below `2s`. For `s ≥ 2` the table entry `(u16)(65536 / s)` is not truncated
(`rec_lt`).
-/

namespace Fscan.ClassStage

/-- `_mm*_mulhi_epu16`: the high 16 bits of the product of two 16-bit lanes. -/
def mulhi16 (x y : ℕ) : ℕ := x * y / 2 ^ 16

/-- `_mm*_mullo_epi16`: the low 16 bits of the product. -/
def mullo16 (x y : ℕ) : ℕ := x * y % 2 ^ 16

/-- `_mm*_sub_epi16` on lanes below `2^16`: subtraction modulo `2^16`. -/
def sub16 (x y : ℕ) : ℕ := (x + (2 ^ 16 - y)) % 2 ^ 16

/-- One lane of the loop, given `x` (already `phi + d`) and the prime `s`. -/
def classOf (x s : ℕ) : ℕ :=
  let q := mulhi16 x (65536 / s)
  let r := sub16 x (mullo16 q s)
  min r (sub16 r s)

/-- For `s ≥ 2` the reciprocal fits in 16 bits. -/
theorem rec_lt {s : ℕ} (hs : 2 ≤ s) : 65536 / s < 2 ^ 16 := by
  rw [Nat.div_lt_iff_lt_mul (by omega)]
  omega

/-- The quotient estimate is never too large and at most one too small:
`q · s ≤ x < (q + 2) · s`. -/
theorem quotient_bounds {x s : ℕ} (hs : 0 < s) (hx : x < 2 ^ 16) :
    mulhi16 x (65536 / s) * s ≤ x ∧ x < (mulhi16 x (65536 / s) + 2) * s := by
  unfold mulhi16
  have h1 : 65536 / s * s ≤ 65536 := Nat.div_mul_le_self 65536 s
  have h2 : 65536 < s * (65536 / s + 1) := Nat.lt_mul_div_succ 65536 hs
  have h3 : x * (65536 / s) / 2 ^ 16 * 2 ^ 16 ≤ x * (65536 / s) := Nat.div_mul_le_self _ _
  have h4 : x * (65536 / s) < 2 ^ 16 * (x * (65536 / s) / 2 ^ 16 + 1) :=
    Nat.lt_mul_div_succ _ (by norm_num)
  generalize 65536 / s = R at h1 h2 h3 h4 ⊢
  generalize x * R / 2 ^ 16 = q at h3 h4 ⊢
  constructor
  · have : q * s * 2 ^ 16 ≤ x * 2 ^ 16 :=
      calc q * s * 2 ^ 16 = q * 2 ^ 16 * s := by ring
        _ ≤ x * R * s := Nat.mul_le_mul_right s h3
        _ = x * (R * s) := by ring
        _ ≤ x * 65536 := Nat.mul_le_mul_left x h1
        _ = x * 2 ^ 16 := by norm_num
    exact Nat.le_of_mul_le_mul_right this (by norm_num)
  · have : x * 2 ^ 16 < (q + 2) * s * 2 ^ 16 :=
      calc x * 2 ^ 16 = x * 65536 := by norm_num
        _ ≤ x * (s * (R + 1)) := Nat.mul_le_mul_left x h2.le
        _ = x * R * s + x * s := by ring
        _ < 2 ^ 16 * (q + 1) * s + 2 ^ 16 * s :=
          Nat.add_lt_add (Nat.mul_lt_mul_of_pos_right h4 hs) (Nat.mul_lt_mul_of_pos_right hx hs)
        _ = (q + 2) * s * 2 ^ 16 := by ring
    exact Nat.lt_of_mul_lt_mul_right this

/-- **The class computation is exact.** For `0 < s < 2^16` and `x < 2^16`:
`q · s ≤ x`, the first remainder `x - q · s` is below `2s`, and the value the code stores is
`x mod s`. -/
theorem classOf_eq {x s : ℕ} (hs : 0 < s) (hs' : s < 2 ^ 16) (hx : x < 2 ^ 16) :
    mulhi16 x (65536 / s) * s ≤ x ∧ x - mulhi16 x (65536 / s) * s < 2 * s ∧
      classOf x s = x % s := by
  obtain ⟨hA, hB⟩ := quotient_bounds hs hx
  unfold classOf
  simp only
  generalize mulhi16 x (65536 / s) = q at hA hB ⊢
  have hmul : mullo16 q s = q * s := Nat.mod_eq_of_lt (by omega)
  rw [hmul]
  have hB' : x < q * s + 2 * s := by
    have : (q + 2) * s = q * s + 2 * s := by ring
    omega
  generalize hP : q * s = P at hA hB' ⊢
  refine ⟨hA, by omega, ?_⟩
  -- the first remainder
  have hr : sub16 x P = x - P := by
    unfold sub16
    omega
  rw [hr]
  have hmod : x % s = (x - P) % s := by
    conv_lhs => rw [show x = x - P + q * s by omega]
    exact Nat.add_mul_mod_self_right _ _ _
  rw [hmod]
  by_cases hlt : x - P < s
  · rw [Nat.mod_eq_of_lt hlt]
    have : sub16 (x - P) s = x - P + 2 ^ 16 - s := by
      unfold sub16
      omega
    rw [this]
    omega
  · rw [Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]
    have : sub16 (x - P) s = x - P - s := by
      unfold sub16
      omega
    rw [this]
    omega

end Fscan.ClassStage
