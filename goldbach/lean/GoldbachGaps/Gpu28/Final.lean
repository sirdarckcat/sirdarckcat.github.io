import GoldbachGaps.Gpu28.Step

/-!
# The end of the `fermat28` kernel: comparison, subtraction, the test against 1

After the step loop the kernel holds `y < 4n` in 24 limbs of 28 bits and does

    n2 = 2n                                   (the carry chain `(n[i] << 1) + cy`)
    if (fm28_ge(x, n2)) fm28_sub(x, n2);
    if (fm28_ge(x, n))  fm28_sub(x, n);
    one = (x[0] == 1) && x[1] == 0 && … && x[23] == 0

This file models `fm28_ge` (the scan from the top limb with its `decided` flag), `fm28_sub`
(the borrow chain `v = a[i] - b[i] - br; br = (v >> 31) & 1; a[i] = v & MASK28`) and the last
comparison, and proves (`flag_iff`) that for limbs below `2^28`, `y < 4n` and
`2n < 2^(28 L)` the flag is `1` exactly when `y mod n = 1`.
-/

namespace Gpu28

open Finset

local notation "B" => (2 ^ 28 : ℕ)

/-! ### Digits -/

theorem V_shift (Bs j : ℕ) (g : ℕ → ℕ) :
    V Bs (j + 1) g = g 0 + Bs * V Bs j (fun i => g (i + 1)) := by
  unfold V
  rw [Finset.sum_range_succ', Finset.mul_sum, pow_zero, mul_one, add_comm]
  congr 1
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [pow_succ]
  ring

/-- Limbs below the base are determined by the value. -/
theorem V_inj {Bs : ℕ} : ∀ (L : ℕ) (f g : ℕ → ℕ), (∀ i < L, f i < Bs) → (∀ i < L, g i < Bs) →
    V Bs L f = V Bs L g → ∀ i < L, f i = g i
  | 0, _, _, _, _, _ => fun i hi => absurd hi (Nat.not_lt_zero i)
  | L + 1, f, g, hf, hg, h => by
    have hfl := V_lt L fun i hi => hf i (by omega)
    have hgl := V_lt L fun i hi => hg i (by omega)
    rw [V_succ, V_succ] at h
    have htop : f L = g L := by
      rcases lt_trichotomy (f L) (g L) with hlt | heq | hgt
      · exfalso
        have := Nat.mul_le_mul_right (Bs ^ L) (show f L + 1 ≤ g L by omega)
        have e : (f L + 1) * Bs ^ L = f L * Bs ^ L + Bs ^ L := by ring
        rw [e] at this
        omega
      · exact heq
      · exfalso
        have := Nat.mul_le_mul_right (Bs ^ L) (show g L + 1 ≤ f L by omega)
        have e : (g L + 1) * Bs ^ L = g L * Bs ^ L + Bs ^ L := by ring
        rw [e] at this
        omega
    rw [htop] at h
    have hlow : V Bs L f = V Bs L g := by omega
    have ih := V_inj L f g (fun i hi => hf i (by omega)) (fun i hi => hg i (by omega)) hlow
    intro i hi
    by_cases hiL : i = L
    · rw [hiL]
      exact htop
    · exact ih i (by omega)

/-! ### `fm28_ge` -/

/-- The loop of `fm28_ge` after the `j` most significant limbs: `(ge, decided)`. -/
def geState (a b : ℕ → ℕ) (L : ℕ) : ℕ → Bool × Bool
  | 0 => (true, false)
  | j + 1 =>
    (if (geState a b L j).2 then (geState a b L j).1
      else if b (L - 1 - j) < a (L - 1 - j) then true
      else if a (L - 1 - j) < b (L - 1 - j) then false else true,
     (geState a b L j).2 || decide (b (L - 1 - j) < a (L - 1 - j)) ||
       decide (a (L - 1 - j) < b (L - 1 - j)))

/-- `fm28_ge(a, b)`. -/
def ge28 (a b : ℕ → ℕ) (L : ℕ) : Bool := (geState a b L L).1

/-- The value of the `j` most significant of `L` limbs. -/
def topV (f : ℕ → ℕ) (L j : ℕ) : ℕ := V B j (fun i => f (L - j + i))

theorem topV_succ (f : ℕ → ℕ) {L j : ℕ} (h : j + 1 ≤ L) :
    topV f L (j + 1) = f (L - 1 - j) + B * topV f L j := by
  unfold topV
  rw [V_shift]
  have e1 : L - (j + 1) + 0 = L - 1 - j := by omega
  have e2 : ∀ i, L - (j + 1) + (i + 1) = L - j + i := fun i => by omega
  simp only [e1, e2]

theorem geState_spec {a b : ℕ → ℕ} {L : ℕ} (ha : ∀ i, a i < B) (hb : ∀ i, b i < B) : ∀ j, j ≤ L →
    ((geState a b L j).1 = true ↔ topV b L j ≤ topV a L j) ∧
      ((geState a b L j).2 = false ↔ topV a L j = topV b L j)
  | 0, _ => by simp [geState, topV, V]
  | j + 1, hj => by
    obtain ⟨h1, h2⟩ := geState_spec (a := a) (b := b) (L := L) ha hb j (by omega)
    rw [topV_succ a hj, topV_succ b hj]
    show ((if (geState a b L j).2 = true then (geState a b L j).1
        else if b (L - 1 - j) < a (L - 1 - j) then true
        else if a (L - 1 - j) < b (L - 1 - j) then false else true) = true ↔ _) ∧
      (((geState a b L j).2 || decide (b (L - 1 - j) < a (L - 1 - j)) ||
        decide (a (L - 1 - j) < b (L - 1 - j))) = false ↔ _)
    have hα := ha (L - 1 - j)
    have hβ := hb (L - 1 - j)
    generalize a (L - 1 - j) = α at hα ⊢
    generalize b (L - 1 - j) = β at hβ ⊢
    generalize topV a L j = Ta at h1 h2 ⊢
    generalize topV b L j = Tb at h1 h2 ⊢
    generalize (geState a b L j).1 = g at h1 ⊢
    generalize (geState a b L j).2 = d at h2 ⊢
    cases d
    · -- not decided: the top parts are equal
      have hT : Ta = Tb := h2.mp rfl
      subst hT
      simp only [Bool.false_eq_true, ↓reduceIte, Bool.false_or, Bool.or_eq_false_iff,
        decide_eq_false_iff_not]
      constructor
      · split_ifs with h3 h4
        · simp only [true_iff]; omega
        · simp only [false_iff]; omega
        · simp only [true_iff]; omega
      · constructor
        · intro h; omega
        · intro h; omega
    · -- decided
      have hne : Ta ≠ Tb := fun h => by
        have := h2.mpr h
        exact Bool.noConfusion this
      simp only [↓reduceIte, Bool.true_or, Bool.true_eq_false, false_iff]
      constructor
      · rw [h1]
        constructor
        · intro h; omega
        · intro h; omega
      · omega

theorem topV_full (f : ℕ → ℕ) (L : ℕ) : topV f L L = V B L f := by
  unfold topV
  exact V_congr fun i _ => by rw [Nat.sub_self, zero_add]

/-- **`fm28_ge` compares the values.** -/
theorem ge28_iff {a b : ℕ → ℕ} {L : ℕ} (ha : ∀ i, a i < B) (hb : ∀ i, b i < B) :
    ge28 a b L = true ↔ V B L b ≤ V B L a := by
  have := (geState_spec ha hb L le_rfl).1
  rwa [topV_full, topV_full] at this

/-! ### `fm28_sub` -/

/-- The borrow into limb `i`. -/
def brAt (a b : ℕ → ℕ) : ℕ → ℕ
  | 0 => 0
  | i + 1 => (((a i + 2 ^ 32 - b i - brAt a b i) % 2 ^ 32) >>> 31) &&& 1

/-- Limb `i` written by `fm28_sub`. -/
def subLimb (a b : ℕ → ℕ) (i : ℕ) : ℕ :=
  ((a i + 2 ^ 32 - b i - brAt a b i) % 2 ^ 32) &&& 268435455

theorem sub_spec {a b : ℕ → ℕ} (ha : ∀ i, a i < B) (hb : ∀ i, b i < B) : ∀ i,
    brAt a b i ≤ 1 ∧ V B i (subLimb a b) + V B i b = V B i a + brAt a b i * B ^ i
  | 0 => by simp [brAt, V]
  | i + 1 => by
    obtain ⟨hbr, hV⟩ := sub_spec ha hb i
    have hα := ha i
    have hβ := hb i
    have hbr' : brAt a b (i + 1) = (a i + 2 ^ 32 - b i - brAt a b i) % 2 ^ 32 / 2 ^ 31 % 2 := by
      show (((a i + 2 ^ 32 - b i - brAt a b i) % 2 ^ 32) >>> 31) &&& 1 = _
      rw [Nat.and_one_is_mod, Nat.shiftRight_eq_div_pow]
    have hlimb : subLimb a b i = (a i + 2 ^ 32 - b i - brAt a b i) % 2 ^ 32 % B := by
      unfold subLimb
      rw [and_mask]
    have key : subLimb a b i + b i + brAt a b i = a i + brAt a b (i + 1) * B := by
      rw [hlimb, hbr']
      omega
    refine ⟨by rw [hbr']; omega, ?_⟩
    rw [V_succ, V_succ, V_succ, pow_succ (2 ^ 28) i]
    have e1 : (subLimb a b i + b i + brAt a b i) * B ^ i =
        (a i + brAt a b (i + 1) * B) * B ^ i := by rw [key]
    have e2 : (subLimb a b i + b i + brAt a b i) * B ^ i =
        subLimb a b i * B ^ i + b i * B ^ i + brAt a b i * B ^ i := by ring
    have e3 : (a i + brAt a b (i + 1) * B) * B ^ i =
        a i * B ^ i + brAt a b (i + 1) * (B ^ i * B) := by ring
    rw [e2, e3] at e1
    generalize subLimb a b i * B ^ i = s1 at e1 ⊢
    generalize b i * B ^ i = s2 at e1 ⊢
    generalize brAt a b i * B ^ i = s3 at e1 hV
    generalize a i * B ^ i = s4 at e1 ⊢
    generalize brAt a b (i + 1) * (B ^ i * B) = s5 at e1 ⊢
    omega

theorem subLimb_lt (a b : ℕ → ℕ) (i : ℕ) : subLimb a b i < B := by
  unfold subLimb
  rw [and_mask]
  exact Nat.mod_lt _ (by norm_num)

/-- **`fm28_sub` subtracts** when the subtrahend is not larger. -/
theorem V_subLimb {a b : ℕ → ℕ} {L : ℕ} (ha : ∀ i, a i < B) (hb : ∀ i, b i < B)
    (hle : V B L b ≤ V B L a) : V B L (subLimb a b) = V B L a - V B L b := by
  obtain ⟨hbr, hV⟩ := sub_spec ha hb L
  have hlt := V_lt (Bs := B) (f := subLimb a b) L fun i _ => subLimb_lt a b i
  have hbr0 : brAt a b L = 0 := by
    by_contra hne
    have h1 : brAt a b L = 1 := by omega
    rw [h1, one_mul] at hV
    omega
  rw [hbr0, zero_mul, add_zero] at hV
  omega

/-! ### The conditional subtraction and the flag -/

/-- `if (fm28_ge(x, m)) fm28_sub(x, m);` -/
def condSub28 (x m : ℕ → ℕ) (L : ℕ) : ℕ → ℕ := if ge28 x m L = true then subLimb x m else x

theorem condSub28_spec {x m : ℕ → ℕ} {L : ℕ} (hx : ∀ i, x i < B) (hm : ∀ i, m i < B) :
    (∀ i, condSub28 x m L i < B) ∧
      V B L (condSub28 x m L) = if V B L m ≤ V B L x then V B L x - V B L m else V B L x := by
  unfold condSub28
  by_cases h : V B L m ≤ V B L x
  · have hge : ge28 x m L = true := (ge28_iff hx hm).mpr h
    simp only [hge, ↓reduceIte, h]
    exact ⟨fun i => subLimb_lt x m i, V_subLimb hx hm h⟩
  · have hge : ge28 x m L = false := by
      cases hg : ge28 x m L with
      | false => rfl
      | true => exact absurd ((ge28_iff hx hm).mp hg) h
    rw [hge]
    simp only [Bool.false_eq_true, ↓reduceIte, h]
    exact ⟨hx, trivial⟩

/-- `one = (x[0] == 1); for i ≥ 1: one &= (x[i] == 0)`. -/
def isOne (x : ℕ → ℕ) (L : ℕ) : Bool :=
  decide (x 0 = 1) && (List.range (L - 1)).all fun i => decide (x (i + 1) = 0)

theorem isOne_iff {x : ℕ → ℕ} {L : ℕ} (hL : 1 ≤ L) (hx : ∀ i, x i < B) :
    isOne x L = true ↔ V B L x = 1 := by
  have hone : V B L (fun i => if i = 0 then 1 else 0) = 1 := by
    obtain ⟨L', rfl⟩ : ∃ L', L = L' + 1 := ⟨L - 1, by omega⟩
    rw [V_shift]
    have : V B L' (fun i => if i + 1 = 0 then 1 else 0) = 0 := by
      unfold V
      exact Finset.sum_eq_zero fun i _ => by simp
    rw [this]
    simp
  unfold isOne
  rw [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]
  constructor
  · rintro ⟨h0, hrest⟩
    rw [← hone]
    refine V_congr fun i hi => ?_
    by_cases hi0 : i = 0
    · rw [hi0, h0]
      simp
    · have := hrest (i - 1) (List.mem_range.mpr (by omega))
      rw [decide_eq_true_eq, show i - 1 + 1 = i by omega] at this
      simp [hi0, this]
  · intro h
    have hdig := V_inj L x (fun i => if i = 0 then 1 else 0) (fun i _ => hx i)
      (fun i _ => by split_ifs <;> norm_num) (h.trans hone.symm)
    refine ⟨by simpa using hdig 0 (by omega), fun i hi => ?_⟩
    have := hdig (i + 1) (by have := List.mem_range.mp hi; omega)
    rw [decide_eq_true_eq, this]
    simp

/-- The flag written by the kernel for the residue `x` and the modulus `n`. -/
def flag (x n : ℕ → ℕ) (L : ℕ) : Bool :=
  isOne (condSub28 (condSub28 x (chainLimb n 1) L) n L) L

/-- **The final test.** For limbs below `2^28`, `y < 4n` and `2n < 2^(28 L)`: the flag is
`1` exactly when `y mod n = 1`. -/
theorem flag_iff {x n : ℕ → ℕ} {L : ℕ} (hL : 1 ≤ L) (hx : ∀ i, x i < B) (hn : ∀ i, n i < B)
    (hX : V B L x < 4 * V B L n) (hN2 : 2 * V B L n < B ^ L) :
    flag x n L = true ↔ V B L x % V B L n = 1 := by
  -- n2 = 2n
  obtain ⟨hcy, hch⟩ := chain_spec hn (b := 1) (by norm_num) L
  have hn2lt : ∀ i, chainLimb n 1 i < B := fun i => by
    unfold chainLimb
    rw [and_mask]
    exact Nat.mod_lt _ (by norm_num)
  have hV2lt := V_lt (Bs := B) (f := chainLimb n 1) L fun i _ => hn2lt i
  have hcy0 : cyAt n 1 L = 0 := by
    by_contra hne
    have h1 : cyAt n 1 L = 1 := by omega
    rw [h1, one_mul] at hch
    omega
  rw [hcy0, zero_mul, add_zero, pow_one] at hch
  obtain ⟨h1lt, h1V⟩ := condSub28_spec (L := L) hx hn2lt
  obtain ⟨h2lt, h2V⟩ := condSub28_spec (L := L) h1lt hn
  unfold flag
  rw [isOne_iff hL h2lt, h2V, h1V, hch]
  generalize V B L x = X at hX ⊢
  generalize V B L n = N at hX ⊢
  have key : (if N ≤ (if 2 * N ≤ X then X - 2 * N else X)
      then (if 2 * N ≤ X then X - 2 * N else X) - N
      else (if 2 * N ≤ X then X - 2 * N else X)) = X % N := by
    by_cases h2 : 2 * N ≤ X
    · simp only [h2, ↓reduceIte]
      by_cases h3 : N ≤ X - 2 * N
      · simp only [h3, ↓reduceIte]
        have e : X = X - 2 * N - N + N * 3 := by omega
        conv_rhs => rw [e, Nat.add_mul_mod_self_left]
        exact (Nat.mod_eq_of_lt (by omega)).symm
      · simp only [h3, ↓reduceIte]
        have e : X = X - 2 * N + N * 2 := by omega
        conv_rhs => rw [e, Nat.add_mul_mod_self_left]
        exact (Nat.mod_eq_of_lt (by omega)).symm
    · simp only [h2, ↓reduceIte]
      by_cases h3 : N ≤ X
      · simp only [h3, ↓reduceIte]
        have e : X = X - N + N * 1 := by omega
        conv_rhs => rw [e, Nat.add_mul_mod_self_left]
        exact (Nat.mod_eq_of_lt (by omega)).symm
      · simp only [h3, ↓reduceIte]
        exact (Nat.mod_eq_of_lt (by omega)).symm
  rw [key]

end Gpu28
