import Mathlib

/-!
# 32-bit limb arithmetic of the GPU Fermat kernel

The CuPy kernel `fermat2` of `goldbach/phd/campaign3_gpu/gpu_fermat.py` (commit `6ef621f`,
branch `ccr-8ffe9d7a-4ni11u`) works on little-endian arrays of `LIMBS` 32-bit words. This
file models its three row operations with the machine's wrapping arithmetic and proves what
they compute:

* `row a x t c` – the carry chain `s = (u64)t[j] + (u64)a * x[j] + c; out[j] = (u32)s;
  c = s >> 32`, used to build `n = cq + k·M` and in both inner loops of `mont_sqr`;
* `subRow t n br` – the borrow chain `d = (u64)t[j] - n[j] - br; out[j] = (u32)d;
  br = (d >> 63) & 1`;
* `shlRow x c` – the shift `out[j] = (v << 1) | carry; carry = v >> 31` of `dbl_mod`;
* `geTop` – the comparison loop that scans from the most significant limb.

`condSub` is the conditional subtraction that ends both `mont_sqr` and `dbl_mod`.
-/

namespace Gpu

local notation "B" => (2 ^ 32 : ℕ)

/-- The number a little-endian list of limbs stands for. -/
def val : List ℕ → ℕ
  | [] => 0
  | a :: l => a + B * val l

/-- All limbs are below `2^32`. -/
def Limbs (l : List ℕ) : Prop := ∀ a ∈ l, a < B

theorem Limbs.head {a : ℕ} {l : List ℕ} (h : Limbs (a :: l)) : a < B :=
  h a (List.mem_cons_self ..)

theorem Limbs.tail {a : ℕ} {l : List ℕ} (h : Limbs (a :: l)) : Limbs l :=
  fun b hb => h b (List.mem_cons_of_mem _ hb)

theorem Limbs.cons {a : ℕ} {l : List ℕ} (ha : a < B) (hl : Limbs l) : Limbs (a :: l) := by
  intro b hb
  rcases List.mem_cons.mp hb with rfl | h
  · exact ha
  · exact hl b h

theorem val_lt {l : List ℕ} (h : Limbs l) : val l < B ^ l.length := by
  induction l with
  | nil => simp [val]
  | cons a l ih =>
    have ha := h.head
    have := ih h.tail
    simp only [val, List.length_cons]
    rw [pow_succ (2 ^ 32) l.length]
    generalize B ^ l.length = P at this ⊢
    omega

theorem val_append (l : List ℕ) (a : ℕ) : val (l ++ [a]) = val l + B ^ l.length * a := by
  induction l with
  | nil => simp [val]
  | cons b l ih =>
    simp only [List.cons_append, val, ih, List.length_cons, pow_succ]
    ring

/-- Limb lists of the same length with the same value are equal. -/
theorem val_injective : ∀ {l l' : List ℕ}, Limbs l → Limbs l' → l.length = l'.length →
    val l = val l' → l = l'
  | [], [], _, _, _, _ => rfl
  | [], _ :: _, _, _, h, _ => by simp at h
  | _ :: _, [], _, _, h, _ => by simp at h
  | a :: l, a' :: l', h, h', hlen, hv => by
    have ha := h.head
    have ha' := h'.head
    simp only [val] at hv
    have e1 : a = a' := by omega
    have e2 : val l = val l' := by omega
    rw [e1, val_injective h.tail h'.tail (by simpa using hlen) e2]

/-! ### The carry chain -/

/-- One step of the chain: `s = (u64)t[j] + (u64)a * x[j] + c` with 64-bit wrapping. -/
def rowS (a xj tj c : ℕ) : ℕ := (tj + (a * xj) % 2 ^ 64 + c) % 2 ^ 64

/-- The carry chain over two arrays: returns the low words and the last carry. -/
def row (a : ℕ) : List ℕ → List ℕ → ℕ → List ℕ × ℕ
  | xj :: xs, tj :: ts, c =>
      (rowS a xj tj c % B :: (row a xs ts (rowS a xj tj c / B)).1,
        (row a xs ts (rowS a xj tj c / B)).2)
  | [], _, c => ([], c)
  | _ :: _, [], c => ([], c)

theorem rowS_eq {a xj tj c : ℕ} (ha : a < B) (hx : xj < B) (ht : tj < B) (hc : c < B) :
    rowS a xj tj c = tj + a * xj + c ∧ rowS a xj tj c / B < B := by
  have hp : a * xj ≤ (B - 1) * (B - 1) := Nat.mul_le_mul (by omega) (by omega)
  unfold rowS
  generalize a * xj = p at hp ⊢
  constructor <;> omega

/-- **The carry chain is exact**: for limbs and a carry below `2^32`,
`value(out) + 2^(32·len) · carry_out = value(t) + a · value(x) + carry_in`. -/
theorem row_spec {a : ℕ} (ha : a < B) : ∀ (x t : List ℕ) (c : ℕ), Limbs x → Limbs t →
    x.length = t.length → c < B →
    Limbs (row a x t c).1 ∧ (row a x t c).1.length = x.length ∧ (row a x t c).2 < B ∧
      val (row a x t c).1 + B ^ x.length * (row a x t c).2 = val t + a * val x + c
  | [], [], c, _, _, _, hc => by
    refine ⟨fun a ha => by simp [row] at ha, by simp [row], by simpa [row] using hc,
      by simp [row, val]⟩
  | [], _ :: _, _, _, _, h, _ => by simp at h
  | _ :: _, [], _, _, _, h, _ => by simp at h
  | xj :: xs, tj :: ts, c, hx, ht, hlen, hc => by
    obtain ⟨hs, hcar⟩ := rowS_eq ha hx.head ht.head hc
    obtain ⟨h1, h2, h3, h4⟩ := row_spec ha xs ts (rowS a xj tj c / B) hx.tail ht.tail
      (by simpa using hlen) hcar
    simp only [row]
    refine ⟨Limbs.cons (Nat.mod_lt _ (by norm_num)) h1, by simp only [List.length_cons, h2],
      h3, ?_⟩
    simp only [val, List.length_cons]
    rw [pow_succ (2 ^ 32) xs.length]
    have e : a * (xj + B * val xs) = a * xj + B * (a * val xs) := by ring
    rw [e]
    generalize rowS a xj tj c = s at hs h4 ⊢
    generalize (row a xs ts (s / B)).2 = c2 at h4 ⊢
    generalize val (row a xs ts (s / B)).1 = v at h4 ⊢
    generalize a * xj = p at hs ⊢
    generalize a * val xs = q at h4 ⊢
    generalize B ^ xs.length = P at h4 ⊢
    have hP : P * B * c2 = B * (P * c2) := by ring
    rw [hP]
    generalize P * c2 = w at h4 ⊢
    omega

/-! ### The borrow chain -/

/-- One step: `d = (u64)t[j] - n[j] - br` with 64-bit wrapping. -/
def subD (tj nj br : ℕ) : ℕ := (tj + 2 ^ 64 - nj - br) % 2 ^ 64

/-- The borrow chain: `out[j] = (u32)d`, `br = (d >> 63) & 1`. -/
def subRow : List ℕ → List ℕ → ℕ → List ℕ
  | tj :: ts, nj :: ns, br => subD tj nj br % B :: subRow ts ns (subD tj nj br / 2 ^ 63 % 2)
  | [], _, _ => []
  | _ :: _, [], _ => []

/-- **The borrow chain subtracts modulo `2^(32·len)`**: for some final borrow `b ≤ 1`,
`value(out) + value(n) + borrow_in = value(t) + 2^(32·len) · b`. -/
theorem subRow_spec : ∀ (t n : List ℕ) (br : ℕ), Limbs t → Limbs n → t.length = n.length →
    br ≤ 1 →
    Limbs (subRow t n br) ∧ (subRow t n br).length = t.length ∧
      ∃ b ≤ 1, val (subRow t n br) + val n + br = val t + B ^ t.length * b
  | [], [], br, _, _, _, hbr => by
    refine ⟨by simp [subRow, Limbs], by simp [subRow], br, hbr, by simp [subRow, val]⟩
  | [], _ :: _, _, _, _, h, _ => by simp at h
  | _ :: _, [], _, _, _, h, _ => by simp at h
  | tj :: ts, nj :: ns, br, ht, hn, hlen, hbr => by
    have htj := ht.head
    have hnj := hn.head
    have hbr' : subD tj nj br / 2 ^ 63 % 2 ≤ 1 := by omega
    obtain ⟨h1, h2, b, hb, h3⟩ := subRow_spec ts ns (subD tj nj br / 2 ^ 63 % 2) ht.tail hn.tail
      (by simpa using hlen) hbr'
    simp only [subRow]
    refine ⟨Limbs.cons (Nat.mod_lt _ (by norm_num)) h1, by simp only [List.length_cons, h2],
      b, hb, ?_⟩
    simp only [val, List.length_cons]
    rw [pow_succ (2 ^ 32) ts.length]
    have hd : subD tj nj br % B + nj + br = tj + B * (subD tj nj br / 2 ^ 63 % 2) := by
      unfold subD
      omega
    generalize subD tj nj br % B = d0 at hd ⊢
    generalize subD tj nj br / 2 ^ 63 % 2 = b1 at hd h3 ⊢
    generalize val (subRow ts ns b1) = v at h3 ⊢
    generalize B ^ ts.length = P at h3 ⊢
    have hP : P * B * b = B * (P * b) := by ring
    rw [hP]
    generalize P * b = w at h3 ⊢
    omega

/-! ### The comparison loop -/

/-- The loop `for j = L-1 downto 0: if (t[j] != n[j]) { ge = t[j] > n[j]; break; }` with
`ge = 1` initially, on the arrays listed from the most significant limb. -/
def geTop : List ℕ → List ℕ → Bool
  | a :: as, b :: bs => if a ≠ b then decide (b < a) else geTop as bs
  | [], _ => true
  | _ :: _, [] => true

/-- Value of a list of limbs given most significant first. -/
def valBE : List ℕ → ℕ
  | [] => 0
  | a :: l => a * B ^ l.length + valBE l

theorem valBE_lt : ∀ {l : List ℕ}, Limbs l → valBE l < B ^ l.length
  | [], _ => by simp [valBE]
  | a :: l, h => by
    have ha := h.head
    have := valBE_lt h.tail
    simp only [valBE, List.length_cons]
    rw [pow_succ (2 ^ 32) l.length]
    generalize B ^ l.length = P at this ⊢
    have h1 : a * P + P ≤ (B - 1) * P + P := by
      have := Nat.mul_le_mul_right P (show a ≤ B - 1 by omega)
      omega
    have h2 : (B - 1) * P + P = P * B := by ring
    omega

theorem valBE_reverse : ∀ l : List ℕ, valBE l.reverse = val l
  | [] => rfl
  | a :: l => by
    have key : ∀ (m : List ℕ) (a : ℕ), valBE (m ++ [a]) = valBE m * B + a := by
      intro m
      induction m with
      | nil => intro a; simp [valBE]
      | cons b m ih =>
        intro a
        simp only [List.cons_append, valBE, ih, List.length_append, List.length_cons,
          List.length_nil, pow_succ]
        ring
    rw [List.reverse_cons, key, valBE_reverse l]
    simp only [val]
    ring

theorem geTop_iff : ∀ (t n : List ℕ), Limbs t → Limbs n → t.length = n.length →
    (geTop t n = true ↔ valBE n ≤ valBE t)
  | [], [], _, _, _ => by simp [geTop, valBE]
  | [], _ :: _, _, _, h => by simp at h
  | _ :: _, [], _, _, h => by simp at h
  | a :: as, b :: bs, ht, hn, hlen => by
    have hl : as.length = bs.length := by simpa using hlen
    have h1 := valBE_lt ht.tail
    have h2 := valBE_lt hn.tail
    have ih := geTop_iff as bs ht.tail hn.tail hl
    simp only [geTop, valBE]
    rw [hl] at h1 ⊢
    generalize B ^ bs.length = P at h1 h2 ⊢
    by_cases hab : a = b
    · subst hab
      simp only [ne_eq, not_true_eq_false, ↓reduceIte, ih]
      omega
    · simp only [ne_eq, hab, not_false_eq_true, ↓reduceIte, decide_eq_true_eq]
      rcases Nat.lt_or_gt_of_ne hab with hlt | hgt
      · have : a * P + P ≤ b * P := by
          have := Nat.mul_le_mul_right P (show a + 1 ≤ b by omega)
          have e : (a + 1) * P = a * P + P := by ring
          omega
        constructor <;> intro h <;> omega
      · have : b * P + P ≤ a * P := by
          have := Nat.mul_le_mul_right P (show b + 1 ≤ a by omega)
          have e : (b + 1) * P = b * P + P := by ring
          omega
        constructor <;> intro h <;> omega

/-! ### The conditional subtraction -/

/-- `ge = top != 0 || (t >= n)`; if `ge` then `t - n` (modulo `2^(32·len)`) else `t`. -/
def condSub (t : List ℕ) (top : ℕ) (n : List ℕ) : List ℕ :=
  if top ≠ 0 ∨ geTop t.reverse n.reverse = true then subRow t n 0 else t

/-- **The conditional subtraction reduces modulo `n`** when the value
`T = value(t) + 2^(32·len) · top` is below `2n`. -/
theorem condSub_spec {t n : List ℕ} {top : ℕ} (ht : Limbs t) (hn : Limbs n)
    (hlen : t.length = n.length) (hT : val t + B ^ t.length * top < 2 * val n) :
    Limbs (condSub t top n) ∧ (condSub t top n).length = t.length ∧
      val (condSub t top n) = (val t + B ^ t.length * top) % val n := by
  have hvt := val_lt ht
  have hvn := val_lt hn
  rw [← hlen] at hvn
  obtain ⟨h1, h2, b, hb, h3⟩ := subRow_spec t n 0 ht hn hlen (by norm_num)
  have hvs := val_lt h1
  rw [h2] at hvs
  have hge : geTop t.reverse n.reverse = true ↔ val n ≤ val t := by
    rw [geTop_iff t.reverse n.reverse (fun a ha => ht a (List.mem_reverse.mp ha))
      (fun a ha => hn a (List.mem_reverse.mp ha)) (by simpa using hlen),
      valBE_reverse, valBE_reverse]
  unfold condSub
  generalize B ^ t.length = P at hT hvt hvn hvs h3 ⊢
  by_cases htop : top = 0
  · subst htop
    simp only [ne_eq, not_true_eq_false, false_or, mul_zero, add_zero] at hT ⊢
    by_cases hc : val n ≤ val t
    · simp only [hge.mpr hc, ↓reduceIte]
      refine ⟨h1, h2, ?_⟩
      have hb0 : b = 0 := by
        rcases Nat.le_one_iff_eq_zero_or_eq_one.mp hb with h | h
        · exact h
        · subst h; omega
      subst hb0
      have e : val (subRow t n 0) = val t - val n := by omega
      rw [e, Nat.mod_eq_sub_mod hc, Nat.mod_eq_of_lt (by omega)]
    · have hfalse : ¬ geTop t.reverse n.reverse = true := fun h => hc (hge.mp h)
      simp only [hfalse, Bool.false_eq_true, ↓reduceIte]
      exact ⟨ht, trivial, (Nat.mod_eq_of_lt (by omega)).symm⟩
  · simp only [ne_eq, htop, not_false_eq_true, true_or, ↓reduceIte]
    refine ⟨h1, h2, ?_⟩
    have htop1 : P ≤ P * top := Nat.le_mul_of_pos_right P (Nat.pos_of_ne_zero htop)
    have hlt : P * top < 2 * P := by omega
    have htop2 : top = 1 := by
      by_contra hne
      have : 2 ≤ top := by omega
      have := Nat.mul_le_mul_left P this
      omega
    subst htop2
    simp only [mul_one] at hT ⊢
    have hb1 : b = 1 := by
      rcases Nat.le_one_iff_eq_zero_or_eq_one.mp hb with h | h
      · subst h; omega
      · exact h
    subst hb1
    have e : val (subRow t n 0) = val t + P - val n := by omega
    rw [e, Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]

/-! ### The shift -/

/-- The loop of `dbl_mod`: `out[j] = (v << 1) | carry` in 32 bits, `carry = v >> 31`. -/
def shlRow : List ℕ → ℕ → List ℕ × ℕ
  | v :: vs, c => (((v <<< 1) % B ||| c) :: (shlRow vs (v >>> 31)).1, (shlRow vs (v >>> 31)).2)
  | [], c => ([], c)

theorem shl_or {v c : ℕ} (hc : c ≤ 1) : (v <<< 1) % B ||| c = (2 * v) % B + c := by
  have e : (v <<< 1) % B = (v % 2 ^ 31) <<< 1 := by
    simp only [Nat.shiftLeft_eq]
    omega
  rw [e, ← Nat.shiftLeft_add_eq_or_of_lt (by omega : c < 2 ^ 1), Nat.shiftLeft_eq]
  omega

/-- **The shift doubles**: `value(out) + 2^(32·len) · carry_out = 2 · value(x) + carry_in`. -/
theorem shlRow_spec : ∀ (x : List ℕ) (c : ℕ), Limbs x → c ≤ 1 →
    Limbs (shlRow x c).1 ∧ (shlRow x c).1.length = x.length ∧ (shlRow x c).2 ≤ 1 ∧
      val (shlRow x c).1 + B ^ x.length * (shlRow x c).2 = 2 * val x + c
  | [], c, _, hc => by simp [shlRow, val, Limbs, hc]
  | v :: vs, c, hx, hc => by
    have hv := hx.head
    have hcar : v >>> 31 ≤ 1 := by
      rw [Nat.shiftRight_eq_div_pow]
      omega
    obtain ⟨h1, h2, h3, h4⟩ := shlRow_spec vs (v >>> 31) hx.tail hcar
    simp only [shlRow]
    rw [shl_or hc]
    refine ⟨Limbs.cons (by omega) h1, by simp only [List.length_cons, h2], h3, ?_⟩
    simp only [val, List.length_cons]
    rw [pow_succ (2 ^ 32) vs.length]
    rw [Nat.shiftRight_eq_div_pow] at h4 ⊢
    generalize (shlRow vs (v / 2 ^ 31)).2 = c2 at h4 ⊢
    generalize val (shlRow vs (v / 2 ^ 31)).1 = w at h4 ⊢
    generalize B ^ vs.length = P at h4 ⊢
    have hP : P * B * c2 = B * (P * c2) := by ring
    rw [hP]
    generalize P * c2 = u at h4 ⊢
    omega

end Gpu
