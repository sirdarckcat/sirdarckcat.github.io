import GoldbachGaps.Gpu.Fermat
import GoldbachGaps.Gpu28.Final
import GoldbachGaps.Fscan.Schedule

/-!
# The `fermat28` kernel, one lane

`fermat28_kernel.cuh` (commit `560a2cf`, branch `ccr-b8c25887-i6tn9f`,
`goldbach/fermat661/cuda/`) tests an odd `n` held in 24 limbs of 28 bits:

    np = fm28_inv_neg28(n32[0])                     n[0] · np ≡ -1 (mod 2^28)
    e  = 672 - c;  x = 2^e                          one limb set
    t times:  x = fm28_step(x, n, np, bit)          (x² · 2^bit) / 2^672, kept below 4n
    n2 = 2n; if (x >= n2) x -= n2; if (x >= n) x -= n
    out = (x == 1)

with `t = bits(n) - 6`, `c = ⌈(n + 671) / 2^t⌉` and the bits of `c · 2^t - (n + 671)` fed
from the top. There is no `R mod n`: the start value is a power of two and the schedule
makes the final value `2^(1-n) mod n` (`Fscan.Schedule.schedule_iffR` with `R = 2^672`).

This file adds the inverse (`invNeg28_spec`) and the lane (`fermat28_lane`,
`fermat28_correct`): the flag is `1` exactly when `2^(n-1) ≡ 1 (mod n)`.

Modelled with the machine's arithmetic: the step (`Step`), the Newton iteration in 32-bit
words with its seed `(3·lo) xor 2`, the start limb, the doubling chain for `2n`, the
comparison loop, the borrow chain, the test against 1. Taken as hypotheses, as in the other
kernel files: the set-up that produces the limbs of `n`, the value `c` and the bits (the
conversion from 32-bit words, `n + 671`, the division by `2^t`, the borrow chain of
`c · 2^t - (n + 671)` and its shift into words), and the range check on the bit length.
-/

namespace Gpu28

open Finset Fscan.Schedule

local notation "B" => (2 ^ 28 : ℕ)

/-! ### The inverse modulo `2^28` -/

/-- `fm28_inv_neg28(lo)`: seed `(3·lo) ^ 2`, three Newton steps in 32-bit words, negate,
mask. The step `x *= 2u - lo * x` is `Gpu.invStep`. -/
def invNeg28 (lo : ℕ) : ℕ :=
  ((2 ^ 32 - (Gpu.invStep lo)^[3] (((3 * lo) % 2 ^ 32) ^^^ 2)) % 2 ^ 32) &&& 268435455

/-- The seed is an inverse of `lo` modulo 32. -/
theorem seed_spec {lo : ℕ} (hodd : lo % 2 = 1) :
    (lo * (((3 * lo) % 2 ^ 32) ^^^ 2)) % 32 = 1 := by
  have h32 : (((3 * lo) % 2 ^ 32) ^^^ 2) % 32 = ((3 * (lo % 32)) % 32) ^^^ 2 := by
    have h : (((3 * lo) % 2 ^ 32) ^^^ 2) % 2 ^ 5 = ((3 * lo) % 2 ^ 32 % 2 ^ 5) ^^^ (2 % 2 ^ 5) :=
      Nat.xor_mod_two_pow
    have e1 : (3 * lo) % 2 ^ 32 % 2 ^ 5 = (3 * (lo % 32)) % 32 := by omega
    have e2 : (2 : ℕ) % 2 ^ 5 = 2 := by norm_num
    rw [e1, e2] at h
    exact h
  rw [Nat.mul_mod, h32]
  have hr : lo % 32 < 32 := Nat.mod_lt _ (by norm_num)
  have ho : lo % 32 % 2 = 1 := by omega
  generalize lo % 32 = r at hr ho
  interval_cases r <;> omega

/-- **`n[0] · np ≡ -1 (mod 2^28)`** for every odd `n[0]`. -/
theorem invNeg28_spec {lo : ℕ} (hodd : lo % 2 = 1) : (lo * invNeg28 lo + 1) % B = 0 := by
  unfold invNeg28
  rw [and_mask]
  obtain ⟨t, ht⟩ : ∃ t, lo * (((3 * lo) % 2 ^ 32) ^^^ 2) = 32 * t + 1 :=
    ⟨lo * (((3 * lo) % 2 ^ 32) ^^^ 2) / 32, by have := seed_spec hodd; omega⟩
  generalize ((3 * lo) % 2 ^ 32) ^^^ 2 = x0 at ht ⊢
  have h2 : ((2 : ZMod (2 ^ 32))) ^ 32 = 0 := by
    have := ZMod.natCast_self (2 ^ 32)
    push_cast at this
    exact this
  have hsq : (1 - (lo : ZMod (2 ^ 32)) * (x0 : ZMod (2 ^ 32))) ^ 2 ^ 3 = 0 := by
    have e : (lo : ZMod (2 ^ 32)) * (x0 : ZMod (2 ^ 32)) = 32 * (t : ZMod (2 ^ 32)) + 1 := by
      have := congrArg (Nat.cast : ℕ → ZMod (2 ^ 32)) ht
      push_cast at this
      exact this
    rw [e]
    have : (1 - (32 * (t : ZMod (2 ^ 32)) + 1)) ^ 2 ^ 3 =
        (2 : ZMod (2 ^ 32)) ^ 32 * (2 ^ 8 * (t : ZMod (2 ^ 32)) ^ 8) := by ring
    rw [this, h2]
    ring
  have key := Gpu.one_sub_iterate lo 3 x0
  rw [hsq] at key
  have hx3 : (Gpu.invStep lo)^[3] x0 < 2 ^ 32 := by
    rw [Function.iterate_succ_apply']
    exact Nat.mod_lt _ (by norm_num)
  generalize (Gpu.invStep lo)^[3] x0 = x3 at key hx3 ⊢
  -- lo · x3 ≡ 1 modulo 2^32
  have h1 : lo * x3 ≡ 1 [MOD 2 ^ 32] := by
    have hz : ((lo * x3 : ℕ) : ZMod (2 ^ 32)) = ((1 : ℕ) : ZMod (2 ^ 32)) := by
      push_cast
      linear_combination -key
    exact (ZMod.natCast_eq_natCast_iff _ _ _).mp hz
  have h1' : lo * x3 ≡ 1 [MOD B] := h1.of_dvd (by norm_num)
  have hy : (2 ^ 32 - x3) % 2 ^ 32 + x3 ≡ 0 [MOD B] := by
    have : ((2 ^ 32 - x3) % 2 ^ 32 + x3) % 2 ^ 32 = 0 := by omega
    exact Nat.ModEq.of_dvd (by norm_num : (2 ^ 28 : ℕ) ∣ 2 ^ 32) this
  have hnp : (2 ^ 32 - x3) % 2 ^ 32 % B ≡ (2 ^ 32 - x3) % 2 ^ 32 [MOD B] := Nat.mod_modEq _ _
  generalize (2 ^ 32 - x3) % 2 ^ 32 = y at hy hnp ⊢
  have h0 : lo * (y % B) + 1 ≡ 0 [MOD B] :=
    calc lo * (y % B) + 1 ≡ lo * y + lo * x3 [MOD B] := (hnp.mul_left lo).add h1'.symm
      _ = lo * (y + x3) := by ring
      _ ≡ lo * 0 [MOD B] := hy.mul_left lo
      _ = 0 := by ring
  unfold Nat.ModEq at h0
  simpa using h0

/-! ### The start value -/

/-- `x[i] = (i == e / 28) ? (1u << (e % 28)) : 0u`. -/
def startLimbs (e : ℕ) (i : ℕ) : ℕ := if i = e / 28 then 1 <<< (e % 28) else 0

theorem startLimbs_lt (e i : ℕ) : startLimbs e i < B := by
  unfold startLimbs
  split_ifs
  · rw [Nat.one_shiftLeft]
    exact Nat.pow_lt_pow_right (by norm_num) (Nat.mod_lt _ (by norm_num))
  · norm_num

theorem V_startLimbs {e L : ℕ} (he : e < 28 * L) : V B L (startLimbs e) = 2 ^ e := by
  unfold V
  rw [Finset.sum_eq_single (e / 28)]
  · simp only [startLimbs, ↓reduceIte]
    rw [Nat.one_shiftLeft, ← pow_mul, ← pow_add, Nat.mod_add_div]
  · intro i _ hi
    simp only [startLimbs, hi, ↓reduceIte, zero_mul]
  · intro h
    exact absurd (Finset.mem_range.mpr (by omega)) h

/-! ### The loop -/

/-- The residue after `s` steps, the bit `b s` being fed at step `s`. -/
def lane (x0 n : ℕ → ℕ) (np : ℕ) (b : ℕ → ℕ) (L : ℕ) : ℕ → ℕ → ℕ
  | 0 => x0
  | s + 1 => stepF (lane x0 n np b L s) n np (b s) L

theorem lane_inv {x0 n : ℕ → ℕ} {np L t : ℕ} {b : ℕ → ℕ} (hL1 : 1 ≤ L) (hL : L ≤ 24)
    (hx0 : ∀ i, x0 i < B) (hn : ∀ i, n i < B) (hinv : (n 0 * np + 1) % B = 0)
    (hX0 : V B L x0 < 4 * V B L n) (hN : 16 * V B L n < B ^ L) (hb : ∀ s < t, b s ≤ 1) :
    ∀ s, s ≤ t → (∀ i, lane x0 n np b L s i < B) ∧ V B L (lane x0 n np b L s) < 4 * V B L n
  | 0, _ => ⟨hx0, hX0⟩
  | s + 1, hs => by
    obtain ⟨h1, h2⟩ := lane_inv hL1 hL hx0 hn hinv hX0 hN hb s (by omega)
    obtain ⟨h3, -, h5⟩ := step_spec (np := np) (b := b s) hL1 hL h1 hn hinv h2 hN (hb s hs)
    exact ⟨h3, h5⟩

/-- One step of the loop is `R · y' ≡ 2^bit · y²` modulo `n`, `R = 2^(28 L)`. -/
theorem lane_step {x0 n : ℕ → ℕ} {np L t : ℕ} {b : ℕ → ℕ} (hL1 : 1 ≤ L) (hL : L ≤ 24)
    (hx0 : ∀ i, x0 i < B) (hn : ∀ i, n i < B) (hinv : (n 0 * np + 1) % B = 0)
    (hX0 : V B L x0 < 4 * V B L n) (hN : 16 * V B L n < B ^ L) (hb : ∀ s < t, b s ≤ 1)
    {s : ℕ} (hs : s < t) :
    2 ^ (28 * L) * V B L (lane x0 n np b L (s + 1)) ≡
      2 ^ b s * V B L (lane x0 n np b L s) ^ 2 [MOD V B L n] := by
  obtain ⟨h1, h2⟩ := lane_inv hL1 hL hx0 hn hinv hX0 hN hb s hs.le
  obtain ⟨-, ⟨μ, -, hμ⟩, -⟩ := step_spec (np := np) (b := b s) hL1 hL h1 hn hinv h2 hN (hb s hs)
  have e : (2 : ℕ) ^ (28 * L) = B ^ L := pow_mul 2 28 L
  show 2 ^ (28 * L) * V B L (stepF (lane x0 n np b L s) n np (b s) L) ≡ _ [MOD _]
  rw [e, hμ]
  have e2 : 2 ^ b s * (V B L (lane x0 n np b L s) * V B L (lane x0 n np b L s) + μ * V B L n) =
      2 ^ b s * V B L (lane x0 n np b L s) ^ 2 + 2 ^ b s * μ * V B L n := by ring
  rw [e2]
  exact Nat.add_mul_mod_self_right _ _ _

/-! ### The lane -/

/-- **One lane of `fermat28`.** For limbs below `2^28`, `n` odd and greater than 1,
`16 n < 2^(28 L)`, an inverse `np`, a start exponent `28 L - c` with `1 ≤ c ≤ 28 L`,
`2^(28 L - c) < 4n`, and the bits of the schedule: the flag is `1` exactly when
`2^(n-1) ≡ 1 (mod n)`. -/
theorem fermat28_lane {n : ℕ → ℕ} {np L t : ℕ} {b : ℕ → ℕ} (hL1 : 1 ≤ L) (hL : L ≤ 24)
    (hn : ∀ i, n i < B) (hodd : V B L n % 2 = 1) (hN1 : 1 < V B L n)
    (hinv : (n 0 * np + 1) % B = 0) (hN : 16 * V B L n < B ^ L)
    (hc1 : 1 ≤ cOfR (28 * L) (V B L n) t) (hc : cOfR (28 * L) (V B L n) t ≤ 28 * L)
    (hstart : 2 ^ (28 * L - cOfR (28 * L) (V B L n) t) < 4 * V B L n)
    (hbits : ∀ s < t, b s = betaR (28 * L) (V B L n) t (s + 1)) :
    flag (lane (startLimbs (28 * L - cOfR (28 * L) (V B L n) t)) n np b L t) n L = true ↔
      2 ^ (V B L n - 1) ≡ 1 [MOD V B L n] := by
  have hb : ∀ s < t, b s ≤ 1 := fun s hs => by
    rw [hbits s hs]
    exact betaR_le_one _ _ _ _
  have hV0 : V B L (startLimbs (28 * L - cOfR (28 * L) (V B L n) t)) =
      2 ^ (28 * L - cOfR (28 * L) (V B L n) t) := V_startLimbs (by omega)
  have hX0 : V B L (startLimbs (28 * L - cOfR (28 * L) (V B L n) t)) < 4 * V B L n := by
    rw [hV0]
    exact hstart
  have hx0 := startLimbs_lt (28 * L - cOfR (28 * L) (V B L n) t)
  obtain ⟨hlim, hlt⟩ := lane_inv (np := np) hL1 hL hx0 hn hinv hX0 hN hb t le_rfl
  have hsched := schedule_iffR (Rb := 28 * L) (n := V B L n) (t := t) (by omega) hodd hc
    (fun s => V B L (lane (startLimbs (28 * L - cOfR (28 * L) (V B L n) t)) n np b L s))
    (by
      show V B L (startLimbs (28 * L - cOfR (28 * L) (V B L n) t)) ≡ _ [MOD _]
      rw [hV0])
    (fun i hi => by
      have := lane_step (np := np) hL1 hL hx0 hn hinv hX0 hN hb hi
      rwa [hbits i hi] at this)
  rw [flag_iff hL1 hlim hn hlt (by omega), ← hsched]
  show _ ↔ _ % _ = 1 % _
  rw [Nat.mod_eq_of_lt hN1]

/-! ### The production parameters -/

/-- For `2^(t+5) ≤ n < 2^(t+6)` and `2 ≤ Rb ≤ 2^t`: `33 ≤ c ≤ 65`. -/
theorem c_bounds28 {Rb n t : ℕ} (hRb : 2 ≤ Rb) (hRb' : Rb ≤ 2 ^ t) (hlo : 2 ^ (t + 5) ≤ n)
    (hhi : n < 2 ^ (t + 6)) : 33 ≤ cOfR Rb n t ∧ cOfR Rb n t ≤ 65 := by
  unfold cOfR
  have hT : 0 < 2 ^ t := Nat.pos_of_ne_zero (pow_ne_zero _ (by norm_num))
  have e5 : (2 : ℕ) ^ (t + 5) = 2 ^ t * 32 := by rw [pow_add]; norm_num
  have e6 : (2 : ℕ) ^ (t + 6) = 2 ^ t * 64 := by rw [pow_add]; norm_num
  rw [e5] at hlo
  rw [e6] at hhi
  generalize 2 ^ t = T at *
  constructor
  · rw [Nat.le_div_iff_mul_le hT]
    omega
  · have : (n + (Rb - 1) + (T - 1)) / T < 66 := by
      rw [Nat.div_lt_iff_lt_mul hT]
      omega
    omega

/-- The value of limbs is congruent to limb 0 modulo 2. -/
theorem V_mod_two (n : ℕ → ℕ) (L : ℕ) : V B (L + 1) n % 2 = n 0 % 2 := by
  rw [V_shift]
  have : (2 ^ 28 : ℕ) * V B L (fun i => n (i + 1)) = 2 * (2 ^ 27 * V B L (fun i => n (i + 1))) := by
    ring
  rw [this]
  omega

set_option exponentiation.threshold 700 in
/-- **`fermat28` as run** (24 limbs, `R = 2^672`): for an odd `n` with limbs below `2^28`,
`t = bits(n) - 6` between 633 and 662 (the kernel accepts bit lengths 642 to 668),
`np = fm28_inv_neg28(lo)` where `lo` is the low 32-bit word of `n` (so `lo mod 2^28 = n[0]`),
start value `2^(672 - c)` and the schedule's bits, the lane reports `1` exactly when
`2^(n-1) ≡ 1 (mod n)`. -/
theorem fermat28_correct {n : ℕ → ℕ} {t lo : ℕ} {b : ℕ → ℕ} (hn : ∀ i, n i < B)
    (hodd : V B 24 n % 2 = 1) (ht : 633 ≤ t) (ht' : t ≤ 662) (hlo : 2 ^ (t + 5) ≤ V B 24 n)
    (hhi : V B 24 n < 2 ^ (t + 6)) (hword : lo % B = n 0)
    (hbits : ∀ s < t, b s = betaR 672 (V B 24 n) t (s + 1)) :
    flag (lane (startLimbs (672 - cOfR 672 (V B 24 n) t)) n (invNeg28 lo) b 24 t) n 24 = true ↔
      2 ^ (V B 24 n - 1) ≡ 1 [MOD V B 24 n] := by
  have h672 : (672 : ℕ) ≤ 2 ^ t :=
    le_trans (by norm_num : (672 : ℕ) ≤ 2 ^ 10) (Nat.pow_le_pow_right (by norm_num) (by omega))
  obtain ⟨hc33, hc65⟩ := c_bounds28 (Rb := 672) (by norm_num) h672 hlo hhi
  have hn0 : n 0 % 2 = 1 := by rw [← V_mod_two n 23]; exact hodd
  have hlo2 : lo % 2 = 1 := by omega
  have hinv : (n 0 * invNeg28 lo + 1) % B = 0 := by
    have h1 := invNeg28_spec hlo2
    have h2 : n 0 * invNeg28 lo + 1 ≡ lo * invNeg28 lo + 1 [MOD B] := by
      rw [← hword]
      exact ((Nat.mod_modEq lo B).mul_right _).add_right 1
    have h3 : n 0 * invNeg28 lo + 1 ≡ 0 [MOD B] := h2.trans (show _ % _ = 0 % _ from h1)
    exact h3
  have hN1 : 1 < V B 24 n := lt_of_lt_of_le (Nat.one_lt_two_pow (by omega)) hlo
  have hN : 16 * V B 24 n < B ^ 24 := by
    have h1 : (2 : ℕ) ^ (t + 6) ≤ 2 ^ 668 := Nat.pow_le_pow_right Nat.zero_lt_two (by omega)
    have h2 : B ^ 24 = 16 * 2 ^ 668 := by
      rw [← pow_mul, show (16 : ℕ) = 2 ^ 4 by norm_num, ← pow_add]
    rw [h2]
    generalize (2 : ℕ) ^ 668 = W at h1 ⊢
    generalize (2 : ℕ) ^ (t + 6) = T at h1 hhi
    omega
  have hstart : 2 ^ (672 - cOfR 672 (V B 24 n) t) < 4 * V B 24 n := by
    have h1 : (2 : ℕ) ^ (672 - cOfR 672 (V B 24 n) t) ≤ 2 ^ (t + 6) :=
      Nat.pow_le_pow_right (by norm_num) (by omega)
    have h2 : (2 : ℕ) ^ (t + 6) = 2 * 2 ^ (t + 5) := by rw [pow_succ]; ring
    omega
  exact fermat28_lane (L := 24) (np := invNeg28 lo) (by norm_num) (by norm_num) hn hodd hN1
    hinv hN
    (show 1 ≤ cOfR (28 * 24) (V B 24 n) t from (by omega : 1 ≤ cOfR 672 (V B 24 n) t))
    (show cOfR (28 * 24) (V B 24 n) t ≤ 28 * 24 from (by omega : cOfR 672 (V B 24 n) t ≤ 672))
    hstart hbits

end Gpu28
