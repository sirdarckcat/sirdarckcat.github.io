import Mathlib

/-!
# `F52_STEP`: the Montgomery squaring step of the 52-bit Fermat kernel

This file models, one 64-bit lane at a time, the macro `F52_STEP` of
`goldbach/fscan/fermat52.h` (lines 40–61 at commit `a3ab69c`, branch
`ccr-d4a17dd0-7uu03r`) and proves the three claims its comment makes, plus the absence
of 64-bit overflow.

## The model

`stepG add shl` is the macro, line for line, with the 64-bit addition and the variable
left shift as parameters:

* `step = stepG add64 shl64` is the machine: additions and shifts wrap modulo `2^64`;
* `stepG (· + ·) (fun x k => x * 2 ^ k)` is the same program over `ℕ`, without wrapping.

`lo x y` and `hi x y` are the low and high 52 bits of the 104-bit product of the low 52
bits of `x` and of `y`, i.e. what `_mm512_madd52lo_epu64` / `_mm512_madd52hi_epu64` add
to their accumulator. `stepG` also returns the list of every value an addition or shift
produces, in program order, so that "no operation overflows" is a statement about it.

## Results

* `no_overflow`: if `a1 < 2^50` and `b ≤ 1` (nothing else is assumed), the wrapping run
  and the exact run agree on the outputs and on every intermediate value, and every such
  value is below `2^57`.
* `carry`: `z0 + lo(m0, n0)` is `2^52` when `z0 ≠ 0` and `0` when `z0 = 0`
  (why the macro may add `[z0 ≠ 0]` instead of computing the carry).
* `step_spec`: with `W = 2^52`, `n = n0 + n1·W`, `A = (a0 mod W) + a1·W` and
  `A' = (a0' mod W) + a1'·W`: there is `M < 2^104` with `2^104·A' = 2^b·(A² + M·n)`,
  and `A' < 4n`, `a1' < 2^50`, so the hypotheses hold again for the next step.

Hypotheses of `step_spec`: `n0, n1, ni < W`, `16·n ≤ 2^104`, `n0·ni ≡ -1 (mod W)`,
`a1 < 2^50`, `A < 4n`, `b ≤ 1`. Oddness of `n` is not assumed separately (it follows from
the congruence), and `a0` is unrestricted: only `a0 mod W` is ever read.
-/

namespace Fscan.F52

local notation "W" => (2 ^ 52 : ℕ)

/-- Low 52 bits of the product of the low 52 bits of `x` and `y`. -/
def lo (x y : ℕ) : ℕ := (x % W) * (y % W) % W

/-- High 52 bits of the product of the low 52 bits of `x` and `y`. -/
def hi (x y : ℕ) : ℕ := (x % W) * (y % W) / W

/-- `_mm512_add_epi64`: addition modulo `2^64`. -/
def add64 (x y : ℕ) : ℕ := (x + y) % 2 ^ 64

/-- `_mm512_sllv_epi64 x k` for a shift count `k < 64`: left shift modulo `2^64`. -/
def shl64 (x k : ℕ) : ℕ := x * 2 ^ k % 2 ^ 64

/-- `F52_STEP` on one lane, line for line, with the 64-bit addition `add` and the left
shift `shl` as parameters. `_mm512_madd52lo_epu64(acc, x, y)` is `add acc (lo x y)`,
`_mm512_madd52hi_epu64(acc, x, y)` is `add acc (hi x y)`, the masked increment is the `if`,
and `_mm512_srli_epi64(x, 52)` is `x / 2^52`.

Returns the new `(a0, a1)` and the list of all values produced by additions and shifts. -/
def stepG (add shl : ℕ → ℕ → ℕ) (a0 a1 n0 n1 ni b : ℕ) : (ℕ × ℕ) × List ℕ :=
  let ad := add a1 a1                                 -- ad = _mm512_add_epi64(a1, a1)
  let z0 := add 0 (lo a0 a0)                          -- z0 = madd52lo(zero, a0, a0)
  let z1 := add 0 (hi a0 a0)                          -- z1 = madd52hi(zero, a0, a0)
  let z2 := add 0 (lo a1 a1)                          -- z2 = madd52lo(zero, a1, a1)
  let z3 := add 0 (hi a1 a1)                          -- z3 = madd52hi(zero, a1, a1)
  let z1b := add z1 (lo a0 ad)                        -- z1 = madd52lo(z1, a0, ad)
  let z2b := add z2 (hi a0 ad)                        -- z2 = madd52hi(z2, a0, ad)
  let m0 := add 0 (lo z0 ni)                          -- m0 = madd52lo(zero, z0, ni)
  let z1c := if z0 ≠ 0 then add z1b 1 else z1b        -- z1 = mask_add(z1, test(z0, z0), z1, one)
  let z1d := add z1c (hi m0 n0)                       -- z1 = madd52hi(z1, m0, n0)
  let z1e := add z1d (lo m0 n1)                       -- z1 = madd52lo(z1, m0, n1)
  let z2c := add z2b (hi m0 n1)                       -- z2 = madd52hi(z2, m0, n1)
  let m1 := add 0 (lo z1e ni)                         -- m1 = madd52lo(zero, z1, ni)
  let s1 := add z1e (lo m1 n0)                        -- madd52lo(z1, m1, n0), then
  let z2d := add z2c (hi m1 n0)                       -- z2 = madd52hi(z2, m1, n0)
  let z2e := add z2d (lo m1 n1)                       -- z2 = madd52lo(z2, m1, n1)
  let z2f := add z2e (s1 / W)                         -- z2 = add(z2, c1), c1 = srli(.., 52)
  let z3b := add z3 (hi m1 n1)                        -- z3 = madd52hi(z3, m1, n1)
  let a0' := shl z2f b                                -- a0 = sllv(z2, b)
  let z3c := shl z3b b                                -- z3 = sllv(z3, b)
  let a1' := add z3c (a0' / W)                        -- a1 = add(z3, srli(a0, 52))
  ((a0', a1'),
    [ad, z0, z1, z2, z3, z1b, z2b, m0, z1c, z1d, z1e, z2c, m1, s1, z2d, z2e, z2f, z3b, a0', z3c,
      a1'])

/-- The machine step: `(a0, a1) ↦ (a0', a1')` with wrapping 64-bit arithmetic. -/
def step (a0 a1 n0 n1 ni b : ℕ) : ℕ × ℕ := (stepG add64 shl64 a0 a1 n0 n1 ni b).1

/-! ### Basic facts about the primitives -/

theorem lo_lt (x y : ℕ) : lo x y < W := Nat.mod_lt _ (by norm_num)

theorem hi_lt (x y : ℕ) : hi x y < W := by
  unfold hi
  rw [Nat.div_lt_iff_lt_mul (by norm_num)]
  exact Nat.mul_lt_mul'' (Nat.mod_lt _ (by norm_num)) (Nat.mod_lt _ (by norm_num))

theorem lo_add_hi (x y : ℕ) : (x % W) * (y % W) = W * hi x y + lo x y :=
  (Nat.div_add_mod _ _).symm

theorem lo_modEq (x y : ℕ) : lo x y ≡ x * y [MOD W] :=
  (Nat.mod_modEq _ _).trans ((Nat.mod_modEq x _).mul (Nat.mod_modEq y _))

theorem add64_eq {x y : ℕ} (h : x + y < 2 ^ 64) : add64 x y = x + y := Nat.mod_eq_of_lt h

theorem shl64_eq {x k : ℕ} (h : x * 2 ^ k < 2 ^ 64) : shl64 x k = x * 2 ^ k := Nat.mod_eq_of_lt h

/-! ### No overflow -/

/-- **No 64-bit operation overflows.** If `a1 < 2^50` and `b ≤ 1`, then running `F52_STEP`
with wrapping 64-bit arithmetic gives the same outputs and the same intermediate values as
running it over `ℕ`, and every value produced by an addition or a shift is below `2^57`. -/
theorem no_overflow {a0 a1 n0 n1 ni b : ℕ} (ha1 : a1 < 2 ^ 50) (hb : b ≤ 1) :
    stepG add64 shl64 a0 a1 n0 n1 ni b =
        stepG (· + ·) (fun x k => x * 2 ^ k) a0 a1 n0 n1 ni b ∧
      ∀ v ∈ (stepG (· + ·) (fun x k => x * 2 ^ k) a0 a1 n0 n1 ni b).2, v < 2 ^ 57 := by
  have hb' : b = 0 ∨ b = 1 := by omega
  simp only [stepG]
  -- walk through the program, replacing each wrapping operation by the exact one
  have e : add64 a1 a1 = a1 + a1 := add64_eq (by omega)
  simp only [e]; clear e
  set ad := a1 + a1 with had
  have b1 := lo_lt a0 a0
  have e : add64 0 (lo a0 a0) = 0 + lo a0 a0 := add64_eq (by omega)
  simp only [e]; clear e
  set z0 := 0 + lo a0 a0 with hz0
  have b2 := hi_lt a0 a0
  have e : add64 0 (hi a0 a0) = 0 + hi a0 a0 := add64_eq (by omega)
  simp only [e]; clear e
  set z1 := 0 + hi a0 a0 with hz1
  have b3 := lo_lt a1 a1
  have e : add64 0 (lo a1 a1) = 0 + lo a1 a1 := add64_eq (by omega)
  simp only [e]; clear e
  set z2 := 0 + lo a1 a1 with hz2
  have b4 := hi_lt a1 a1
  have e : add64 0 (hi a1 a1) = 0 + hi a1 a1 := add64_eq (by omega)
  simp only [e]; clear e
  set z3 := 0 + hi a1 a1 with hz3
  have b5 := lo_lt a0 ad
  have e : add64 z1 (lo a0 ad) = z1 + lo a0 ad := add64_eq (by omega)
  simp only [e]; clear e
  set z1b := z1 + lo a0 ad with hz1b
  have b6 := hi_lt a0 ad
  have e : add64 z2 (hi a0 ad) = z2 + hi a0 ad := add64_eq (by omega)
  simp only [e]; clear e
  set z2b := z2 + hi a0 ad with hz2b
  have b7 := lo_lt z0 ni
  have e : add64 0 (lo z0 ni) = 0 + lo z0 ni := add64_eq (by omega)
  simp only [e]; clear e
  set m0 := 0 + lo z0 ni with hm0
  have e : (if z0 ≠ 0 then add64 z1b 1 else z1b) = if z0 ≠ 0 then z1b + 1 else z1b := by
    split_ifs
    · exact add64_eq (by omega)
    · rfl
  simp only [e]; clear e
  set z1c := (if z0 ≠ 0 then z1b + 1 else z1b) with hz1c
  have b8 : z1c ≤ z1b + 1 := by
    rw [hz1c]
    split_ifs <;> omega
  have b9 := hi_lt m0 n0
  have e : add64 z1c (hi m0 n0) = z1c + hi m0 n0 := add64_eq (by omega)
  simp only [e]; clear e
  set z1d := z1c + hi m0 n0 with hz1d
  have b10 := lo_lt m0 n1
  have e : add64 z1d (lo m0 n1) = z1d + lo m0 n1 := add64_eq (by omega)
  simp only [e]; clear e
  set z1e := z1d + lo m0 n1 with hz1e
  have b11 := hi_lt m0 n1
  have e : add64 z2b (hi m0 n1) = z2b + hi m0 n1 := add64_eq (by omega)
  simp only [e]; clear e
  set z2c := z2b + hi m0 n1 with hz2c
  have b12 := lo_lt z1e ni
  have e : add64 0 (lo z1e ni) = 0 + lo z1e ni := add64_eq (by omega)
  simp only [e]; clear e
  set m1 := 0 + lo z1e ni with hm1
  have b13 := lo_lt m1 n0
  have e : add64 z1e (lo m1 n0) = z1e + lo m1 n0 := add64_eq (by omega)
  simp only [e]; clear e
  set s1 := z1e + lo m1 n0 with hs1
  have b14 := hi_lt m1 n0
  have e : add64 z2c (hi m1 n0) = z2c + hi m1 n0 := add64_eq (by omega)
  simp only [e]; clear e
  set z2d := z2c + hi m1 n0 with hz2d
  have b15 := lo_lt m1 n1
  have e : add64 z2d (lo m1 n1) = z2d + lo m1 n1 := add64_eq (by omega)
  simp only [e]; clear e
  set z2e := z2d + lo m1 n1 with hz2e
  have e : add64 z2e (s1 / W) = z2e + s1 / W := add64_eq (by omega)
  simp only [e]; clear e
  set z2f := z2e + s1 / W with hz2f
  have b16 := hi_lt m1 n1
  have e : add64 z3 (hi m1 n1) = z3 + hi m1 n1 := add64_eq (by omega)
  simp only [e]; clear e
  set z3b := z3 + hi m1 n1 with hz3b
  have b17 : z2f * 2 ^ b ≤ 2 * z2f := by
    rcases hb' with rfl | rfl <;> omega
  have e : shl64 z2f b = z2f * 2 ^ b := shl64_eq (by omega)
  simp only [e]; clear e
  set a0' := z2f * 2 ^ b with ha0'
  have b18 : z3b * 2 ^ b ≤ 2 * z3b := by
    rcases hb' with rfl | rfl <;> omega
  have e : shl64 z3b b = z3b * 2 ^ b := shl64_eq (by omega)
  simp only [e]; clear e
  set z3c := z3b * 2 ^ b with hz3c
  have e : add64 z3c (a0' / W) = z3c + a0' / W := add64_eq (by omega)
  simp only [e]; clear e
  set a1' := z3c + a0' / W with ha1'
  refine ⟨trivial, ?_⟩
  intro v hv
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hv
  rcases hv with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
    rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> omega

/-! ### The Montgomery relation -/

/-- `z + m·n0` is divisible by `W` when `m = lo z ni` and `n0·ni ≡ -1 (mod W)`. -/
theorem mont_dvd (z n0 ni : ℕ) (hinv : (n0 * ni + 1) % W = 0) : W ∣ z + lo (lo z ni) n0 := by
  rw [← Nat.modEq_zero_iff_dvd]
  have h1 : lo (lo z ni) n0 ≡ z * ni * n0 [MOD W] :=
    (lo_modEq _ _).trans ((lo_modEq z ni).mul_right n0)
  have h3 : n0 * ni + 1 ≡ 0 [MOD W] := by
    show (n0 * ni + 1) % W = 0 % W
    rw [hinv, Nat.zero_mod]
  calc z + lo (lo z ni) n0 ≡ z + z * ni * n0 [MOD W] := (Nat.ModEq.refl z).add h1
    _ = z * (n0 * ni + 1) := by ring
    _ ≡ z * 0 [MOD W] := h3.mul_left z
    _ = 0 := by simp

/-- **Claim (i): the first reduction carry.** With `z0 < 2^52` and `m0 = lo z0 ni`, the sum
`z0 + lo m0 n0` is `2^52` if `z0 ≠ 0` and `0` if `z0 = 0`. -/
theorem carry (z n0 ni : ℕ) (hz : z < W) (hinv : (n0 * ni + 1) % W = 0) :
    z + lo (lo z ni) n0 = if z ≠ 0 then W else 0 := by
  obtain ⟨k, hk⟩ := mont_dvd z n0 ni hinv
  have h1 := lo_lt (lo z ni) n0
  split_ifs with h
  · omega
  · obtain rfl : z = 0 := by omega
    simp [lo]

/-- Claim (i) for the values `z0`, `m0` of the step itself. -/
theorem first_carry (a0 n0 ni : ℕ) (hinv : (n0 * ni + 1) % W = 0) :
    lo a0 a0 + lo (lo (lo a0 a0) ni) n0 = if lo a0 a0 ≠ 0 then W else 0 :=
  carry _ _ _ (lo_lt a0 a0) hinv

/-- The algebraic core: the limb identities of one Montgomery squaring add up. -/
theorem mont_algebra {V x y z0 h00 l01 h01 l11 h11 m0 lmn0 hmn0 k0 l0n1 h0n1 m1 l1n0 h1n0 c1
    l1n1 h1n1 n0 n1 : ℕ}
    (E1 : x * x = V * h00 + z0) (E2 : x * (2 * y) = V * h01 + l01) (E3 : y * y = V * h11 + l11)
    (E4 : m0 * n0 = V * hmn0 + lmn0) (E5 : z0 + lmn0 = V * k0)
    (E6 : m0 * n1 = V * h0n1 + l0n1) (E7 : m1 * n0 = V * h1n0 + l1n0)
    (E8 : h00 + l01 + k0 + hmn0 + l0n1 + l1n0 = V * c1) (E9 : m1 * n1 = V * h1n1 + l1n1) :
    (x + y * V) ^ 2 + (m0 + m1 * V) * (n0 + n1 * V) =
      V ^ 2 * (l11 + h01 + h0n1 + h1n0 + l1n1 + c1 + (h11 + h1n1) * V) := by
  zify at *
  linear_combination E1 + V * E2 + V ^ 2 * E3 + E4 + E5 + V * E6 + V * E7 + V * E8 + V ^ 2 * E9

/-- The specification of the exact run, with every intermediate value named. -/
theorem spec_core {a0 a1 n0 n1 ni b ad z0 z1 z2 z3 z1b z2b m0 z1c z1d z1e z2c m1 s1 z2d z2e z2f
    z3b a0' z3c a1' : ℕ}
    (h_ad : ad = a1 + a1) (h_z0 : z0 = 0 + lo a0 a0) (h_z1 : z1 = 0 + hi a0 a0)
    (h_z2 : z2 = 0 + lo a1 a1) (h_z3 : z3 = 0 + hi a1 a1) (h_z1b : z1b = z1 + lo a0 ad)
    (h_z2b : z2b = z2 + hi a0 ad) (h_m0 : m0 = 0 + lo z0 ni)
    (h_z1c : z1c = if z0 ≠ 0 then z1b + 1 else z1b) (h_z1d : z1d = z1c + hi m0 n0)
    (h_z1e : z1e = z1d + lo m0 n1) (h_z2c : z2c = z2b + hi m0 n1) (h_m1 : m1 = 0 + lo z1e ni)
    (h_s1 : s1 = z1e + lo m1 n0) (h_z2d : z2d = z2c + hi m1 n0) (h_z2e : z2e = z2d + lo m1 n1)
    (h_z2f : z2f = z2e + s1 / W) (h_z3b : z3b = z3 + hi m1 n1) (h_a0' : a0' = z2f * 2 ^ b)
    (h_z3c : z3c = z3b * 2 ^ b) (h_a1' : a1' = z3c + a0' / W)
    (hn0 : n0 < W) (hn1 : n1 < W) (hn : 16 * (n0 + n1 * W) ≤ 2 ^ 104)
    (hinv : (n0 * ni + 1) % W = 0) (ha1 : a1 < 2 ^ 50)
    (hA : a0 % W + a1 * W < 4 * (n0 + n1 * W)) (hb : b ≤ 1) :
    (∃ M < 2 ^ 104, 2 ^ 104 * (a0' % W + a1' * W) =
        2 ^ b * ((a0 % W + a1 * W) ^ 2 + M * (n0 + n1 * W))) ∧
      a0' % W + a1' * W < 4 * (n0 + n1 * W) ∧ a1' < 2 ^ 50 := by
  rw [Nat.zero_add] at h_z0 h_z1 h_z2 h_z3 h_m0 h_m1
  -- sizes of the limbs
  have hz0W : z0 < W := h_z0 ▸ lo_lt a0 a0
  have hm0W : m0 < W := h_m0 ▸ lo_lt z0 ni
  have hm1W : m1 < W := h_m1 ▸ lo_lt z1e ni
  -- the seven products, split into low and high halves
  have P1 := lo_add_hi a0 a0
  have P2 := lo_add_hi a0 ad
  have P3 := lo_add_hi a1 a1
  have P4 := lo_add_hi m0 n0
  have P6 := lo_add_hi m0 n1
  have P7 := lo_add_hi m1 n0
  have P9 := lo_add_hi m1 n1
  rw [show ad % W = 2 * a1 by omega] at P2
  rw [show a1 % W = a1 by omega] at P3
  rw [Nat.mod_eq_of_lt hm0W, Nat.mod_eq_of_lt hn0] at P4
  rw [Nat.mod_eq_of_lt hm0W, Nat.mod_eq_of_lt hn1] at P6
  rw [Nat.mod_eq_of_lt hm1W, Nat.mod_eq_of_lt hn0] at P7
  rw [Nat.mod_eq_of_lt hm1W, Nat.mod_eq_of_lt hn1] at P9
  -- the two reduction carries
  obtain ⟨k0, hk0⟩ : ∃ k0 : ℕ, k0 = if z0 ≠ 0 then 1 else 0 := ⟨_, rfl⟩
  have E5 : z0 + lo m0 n0 = W * k0 := by
    have := carry z0 n0 ni hz0W hinv
    rw [← h_m0] at this
    rw [this, hk0]
    split_ifs <;> rfl
  have hz1c : z1c = z1b + k0 := by
    rw [h_z1c, hk0]
    split_ifs <;> rfl
  have E8 : s1 = W * (s1 / W) := by
    have hd := mont_dvd z1e n0 ni hinv
    rw [← h_m1, ← h_s1] at hd
    exact (Nat.mul_div_cancel' hd).symm
  -- the squaring identity
  have key : (a0 % W + a1 * W) ^ 2 + (m0 + m1 * W) * (n0 + n1 * W) =
      W ^ 2 * (z2f + z3b * W) := by
    have halg := mont_algebra (V := W) (x := a0 % W) (y := a1) (z0 := z0) (k0 := k0)
      (c1 := s1 / W) (n1 := n1) (h_z0 ▸ P1) P2 P3 P4 E5 P6 P7 (by omega) P9
    rw [show z2f = lo a1 a1 + hi a0 ad + hi m0 n1 + hi m1 n0 + lo m1 n1 + s1 / W by omega,
      show z3b = hi a1 a1 + hi m1 n1 by omega]
    exact halg
  -- the output, as a number
  have hA' : a0' % W + a1' * W = 2 ^ b * (z2f + z3b * W) := by
    interval_cases b <;> omega
  have hM : m0 + m1 * W < 2 ^ 104 := by omega
  have hR : z2f + z3b * W < 2 * (n0 + n1 * W) := by
    have key' : (a0 % W + a1 * W) ^ 2 + (m0 + m1 * W) * (n0 + n1 * W) =
        2 ^ 104 * (z2f + z3b * W) := by
      rw [key]
      norm_num
    generalize a0 % W + a1 * W = A at hA key'
    generalize n0 + n1 * W = n at hA hn key' ⊢
    generalize m0 + m1 * W = M at hM key'
    generalize z2f + z3b * W = R at key' ⊢
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
  have hA'lt : a0' % W + a1' * W < 4 * (n0 + n1 * W) := by
    rw [hA']
    interval_cases b <;> omega
  refine ⟨⟨m0 + m1 * W, hM, ?_⟩, hA'lt, by omega⟩
  rw [hA', key]
  ring

/-- **Claims (ii) and (iii): one step of the kernel.** Let `W = 2^52`, `n = n0 + n1·W`,
`A = (a0 mod W) + a1·W` and let `(a0', a1') = step a0 a1 n0 n1 ni b` be the output of
`F52_STEP` computed with wrapping 64-bit arithmetic, `A' = (a0' mod W) + a1'·W`. If
`n0, n1 < W`, `16·n ≤ 2^104`, `n0·ni ≡ -1 (mod W)`, `a1 < 2^50`, `A < 4n` and `b ≤ 1`, then

* `2^104 · A' = 2^b · (A² + M·n)` for some `M < 2^104`;
* `A' < 4n` and `a1' < 2^50`, so the same hypotheses hold for the next step. -/
theorem step_spec {a0 a1 n0 n1 ni b : ℕ} (hn0 : n0 < W) (hn1 : n1 < W)
    (hn : 16 * (n0 + n1 * W) ≤ 2 ^ 104) (hinv : (n0 * ni + 1) % W = 0) (ha1 : a1 < 2 ^ 50)
    (hA : a0 % W + a1 * W < 4 * (n0 + n1 * W)) (hb : b ≤ 1) :
    (∃ M < 2 ^ 104,
        2 ^ 104 * ((step a0 a1 n0 n1 ni b).1 % W + (step a0 a1 n0 n1 ni b).2 * W) =
          2 ^ b * ((a0 % W + a1 * W) ^ 2 + M * (n0 + n1 * W))) ∧
      (step a0 a1 n0 n1 ni b).1 % W + (step a0 a1 n0 n1 ni b).2 * W < 4 * (n0 + n1 * W) ∧
      (step a0 a1 n0 n1 ni b).2 < 2 ^ 50 := by
  rw [step, (no_overflow ha1 hb).1]
  simp only [stepG]
  exact spec_core rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl rfl
    rfl hn0 hn1 hn hinv ha1 hA hb

end Fscan.F52
