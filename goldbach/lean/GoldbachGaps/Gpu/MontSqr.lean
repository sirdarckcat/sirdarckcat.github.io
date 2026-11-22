import GoldbachGaps.Gpu.Limbs

/-!
# `mont_sqr` and `dbl_mod` of the GPU Fermat kernel

`mont_sqr(x, n, ninv)` of `gpu_fermat.py` is a coarsely integrated operand scanning (CIOS)
Montgomery multiplication of `x` by itself on `L` 32-bit limbs, followed by one conditional
subtraction; `dbl_mod(x, n)` doubles modulo `n`. With `R = 2^(32 L)`:

* `montSqr_spec` – for `x < n < R`, `n` odd and `ninv · n[0] ≡ -1 (mod 2^32)`, the result
  is below `n` and `R · result ≡ x² (mod n)`;
* `dblMod_spec` – for `x < n`, the result is `2x mod n`.

The model follows the C code statement by statement; the loop over the limbs of `x` is a
fold, and its invariant (`sqrLoop_spec`) is that the running value `T` of the `L + 1` words
`t[0..L]` satisfies `2^(32 i) · T = (low i limbs of x) · x + M · n` and `T < 2n`.
-/

namespace Gpu

local notation "B" => (2 ^ 32 : ℕ)

/-- One iteration of the outer loop of `mont_sqr`, on the state `(t[0..L-1], t[L])`:

    c = 0; for j: s = t[j] + ai * x[j] + c; t[j] = lo(s); c = hi(s)
    s = t[L] + c; t[L] = lo(s); t[L+1] = hi(s)
    m = t[0] * ninv
    s = t[0] + m * n[0]; c = hi(s); for j ≥ 1: s = t[j] + m * n[j] + c; t[j-1] = lo(s); c = hi(s)
    s = t[L] + c; t[L-1] = lo(s); t[L] = t[L+1] + hi(s)
-/
def sqrStep (x n : List ℕ) (ninv : ℕ) (st : List ℕ × ℕ) (ai : ℕ) : List ℕ × ℕ :=
  ((row (((row ai x st.1 0).1.headD 0 * ninv) % B) n (row ai x st.1 0).1 0).1.tail ++
      [(((st.2 + (row ai x st.1 0).2) % 2 ^ 64 % B +
          (row (((row ai x st.1 0).1.headD 0 * ninv) % B) n (row ai x st.1 0).1 0).2) % 2 ^ 64) % B],
    ((st.2 + (row ai x st.1 0).2) % 2 ^ 64 / B +
      (((st.2 + (row ai x st.1 0).2) % 2 ^ 64 % B +
          (row (((row ai x st.1 0).1.headD 0 * ninv) % B) n (row ai x st.1 0).1 0).2) % 2 ^ 64) / B) % B)

theorem val_headD_tail : ∀ l : List ℕ, val l = l.headD 0 + B * val l.tail
  | [] => by simp [val]
  | a :: l => by simp [val]

theorem headD_lt {l : List ℕ} (h : Limbs l) : l.headD 0 < B := by
  cases l with
  | nil => simp
  | cons a l => exact h.head

theorem Limbs_tail {l : List ℕ} (h : Limbs l) : Limbs l.tail := by
  cases l with
  | nil => exact h
  | cons a l => exact h.tail

/-- **One outer iteration.** With `T = value(t) + R · t[L]` and the new value `T'`:
`2^32 · T' = T + ai · x + m · n` for some `m < 2^32`, and `T' < 2n` if `T < 2n` and `x < n`. -/
theorem sqrStep_spec {x n t : List ℕ} {tL ninv ai : ℕ} (hx : Limbs x) (hn : Limbs n)
    (ht : Limbs t) (hxl : x.length = n.length) (htl : t.length = n.length)
    (hL : 0 < n.length) (hai : ai < B)
    (hinv : (n.headD 0 * ninv + 1) % B = 0) (hxn : val x < val n)
    (hT : val t + B ^ n.length * tL < 2 * val n) :
    Limbs (sqrStep x n ninv (t, tL) ai).1 ∧ (sqrStep x n ninv (t, tL) ai).1.length = n.length ∧
      val (sqrStep x n ninv (t, tL) ai).1 + B ^ n.length * (sqrStep x n ninv (t, tL) ai).2 <
        2 * val n ∧
      ∃ m, B * (val (sqrStep x n ninv (t, tL) ai).1 +
          B ^ n.length * (sqrStep x n ninv (t, tL) ai).2) =
        val t + B ^ n.length * tL + ai * val x + m * val n := by
  have hvn := val_lt hn
  have hvt := val_lt ht
  rw [htl] at hvt
  -- first pass
  obtain ⟨a1, a2, a3, a4⟩ := row_spec hai x t 0 hx ht (hxl.trans htl.symm) (by norm_num)
  rw [hxl] at a2 a4
  -- the multiplier
  have hm : ((row ai x t 0).1.headD 0 * ninv) % B < B := Nat.mod_lt _ (by norm_num)
  -- second pass
  obtain ⟨b1, b2, b3, b4⟩ := row_spec hm n (row ai x t 0).1 0 hn a1 a2.symm (by norm_num)
  unfold sqrStep
  simp only []
  generalize hr1 : row ai x t 0 = r1 at a1 a2 a3 a4 hm b1 b2 b3 b4 ⊢
  generalize hmm : (r1.1.headD 0 * ninv) % B = m at hm b1 b2 b3 b4 ⊢
  generalize hr2 : row m n r1.1 0 = r2 at b1 b2 b3 b4 ⊢
  -- the low limb of the second pass vanishes
  have hu0 : r1.1.headD 0 < B := headD_lt a1
  have hv1 := val_headD_tail r1.1
  have hv2 := val_headD_tail r2.1
  have hvn0 := val_headD_tail n
  have hn0 : n.headD 0 < B := headD_lt hn
  have hzero : r2.1.headD 0 = 0 := by
    -- value(r2) ≡ value(r1) + m n ≡ u0 + m n0 ≡ u0 (1 + ninv n0) ≡ 0 (mod B)
    have h1 : (val r2.1) % B = (val r1.1 + m * val n) % B := by
      have : val r2.1 + B ^ n.length * r2.2 = val r1.1 + m * val n := by simpa using b4
      have hB : B ∣ B ^ n.length := dvd_pow_self _ (by omega)
      obtain ⟨c, hc⟩ := hB
      rw [← this, hc, mul_assoc, Nat.add_mul_mod_self_left]
    have h2 : (val r2.1) % B = r2.1.headD 0 := by
      rw [hv2, Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt (headD_lt b1)]
    have h3 : (val r1.1 + m * val n) % B = (r1.1.headD 0 + m * n.headD 0) % B := by
      rw [hv1, hvn0]
      have : r1.1.headD 0 + B * val r1.1.tail + m * (n.headD 0 + B * val n.tail) =
          r1.1.headD 0 + m * n.headD 0 + B * (val r1.1.tail + m * val n.tail) := by ring
      rw [this, Nat.add_mul_mod_self_left]
    have h4 : (r1.1.headD 0 + m * n.headD 0) % B = 0 := by
      have e1 : (r1.1.headD 0 + m * n.headD 0) % B =
          (r1.1.headD 0 + (r1.1.headD 0 * ninv) * n.headD 0) % B := by
        rw [← hmm]
        conv_lhs => rw [Nat.add_mod, Nat.mul_mod, Nat.mod_mod, ← Nat.mul_mod, ← Nat.add_mod]
      have e2 : r1.1.headD 0 + (r1.1.headD 0 * ninv) * n.headD 0 =
          r1.1.headD 0 * (n.headD 0 * ninv + 1) := by ring
      rw [e1, e2, Nat.mul_mod, hinv, mul_zero, Nat.zero_mod]
    rw [← h2, h1, h3, h4]
  rw [hzero, zero_add] at hv2
  -- sizes of the two top words
  have hc1 : (tL + r1.2) % 2 ^ 64 = tL + r1.2 := by
    apply Nat.mod_eq_of_lt
    have : B ^ n.length * tL < 2 * B ^ n.length := by omega
    have htL : tL < 2 := by
      by_contra hcon
      have := Nat.mul_le_mul_left (B ^ n.length) (show 2 ≤ tL by omega)
      omega
    omega
  rw [hc1]
  generalize htop : tL + r1.2 = top at hc1 ⊢
  have hc2 : (top % B + r2.2) % 2 ^ 64 = top % B + r2.2 := by
    apply Nat.mod_eq_of_lt
    omega
  rw [hc2]
  have htaillen : r2.1.tail.length = n.length - 1 := by simp [b2]
  have hlim : Limbs (r2.1.tail ++ [(top % B + r2.2) % B]) := by
    intro a ha
    rcases List.mem_append.mp ha with h | h
    · exact Limbs_tail b1 a h
    · simp only [List.mem_singleton] at h
      rw [h]
      exact Nat.mod_lt _ (by norm_num)
  have hlen : (r2.1.tail ++ [(top % B + r2.2) % B]).length = n.length := by
    simp only [List.length_append, htaillen, List.length_singleton]
    omega
  -- the exact relation before the last reduction modulo 2^32
  have hpow : B ^ n.length = B * B ^ (n.length - 1) := by
    conv_lhs => rw [show n.length = (n.length - 1) + 1 by omega, pow_succ]
    ring
  have key : B * (val (r2.1.tail ++ [(top % B + r2.2) % B]) +
      B ^ n.length * (top / B + (top % B + r2.2) / B)) =
      val t + B ^ n.length * tL + ai * val x + m * val n := by
    rw [val_append, htaillen]
    have e4 : val r1.1 + B ^ n.length * r1.2 = val t + ai * val x := by simpa using a4
    have e5 : val r2.1 + B ^ n.length * r2.2 = val r1.1 + m * val n := by simpa using b4
    have e6 : B * (val r2.1.tail + B ^ (n.length - 1) * ((top % B + r2.2) % B) +
        B ^ n.length * (top / B + (top % B + r2.2) / B)) =
        val r2.1 + B ^ n.length * ((top % B + r2.2) % B + B * ((top % B + r2.2) / B)) +
          B ^ n.length * (B * (top / B)) := by
      rw [hv2]
      conv_rhs => rw [hpow]
      conv_lhs => rw [hpow]
      ring
    rw [e6, Nat.mod_add_div]
    have e7 : B ^ n.length * (top % B + r2.2) + B ^ n.length * (B * (top / B)) =
        B ^ n.length * top + B ^ n.length * r2.2 := by
      have := Nat.mod_add_div top B
      calc B ^ n.length * (top % B + r2.2) + B ^ n.length * (B * (top / B))
          = B ^ n.length * (top % B + B * (top / B)) + B ^ n.length * r2.2 := by ring
        _ = B ^ n.length * top + B ^ n.length * r2.2 := by rw [this]
    have e8 : B ^ n.length * top = B ^ n.length * tL + B ^ n.length * r1.2 := by
      rw [← htop]; ring
    generalize val r2.1 = V2 at e5 e6 ⊢
    generalize val r1.1 = V1 at e4 e5 ⊢
    generalize B ^ n.length * (top % B + r2.2) = Z1 at e7 ⊢
    generalize B ^ n.length * (B * (top / B)) = Z2 at e7 ⊢
    generalize B ^ n.length * top = Z3 at e7 e8 ⊢
    generalize B ^ n.length * r2.2 = Z4 at e5 e7 ⊢
    generalize B ^ n.length * r1.2 = Z5 at e4 e8 ⊢
    generalize B ^ n.length * tL = Z6 at e8 ⊢
    generalize ai * val x = Q1 at e4 ⊢
    generalize m * val n = Q2 at e5 ⊢
    omega
  -- the new value is below 2n, hence the new top word is 0 or 1 and the last `% B` is void
  have hbound : val (r2.1.tail ++ [(top % B + r2.2) % B]) +
      B ^ n.length * (top / B + (top % B + r2.2) / B) < 2 * val n := by
    have h1 : ai * val x ≤ (B - 1) * val n := by
      calc ai * val x ≤ (B - 1) * val x := Nat.mul_le_mul_right _ (by omega)
        _ ≤ (B - 1) * val n := Nat.mul_le_mul_left _ hxn.le
    have h2 : m * val n ≤ (B - 1) * val n := Nat.mul_le_mul_right _ (by omega)
    generalize val (r2.1.tail ++ [(top % B + r2.2) % B]) +
      B ^ n.length * (top / B + (top % B + r2.2) / B) = T' at key ⊢
    generalize ai * val x = Q1 at key h1
    generalize m * val n = Q2 at key h2
    omega
  have hsmall : top / B + (top % B + r2.2) / B < B := by
    have hv := val_lt hlim
    rw [hlen] at hv
    by_contra hcon
    have h1 : 2 ≤ top / B + (top % B + r2.2) / B := by omega
    have h2 := Nat.mul_le_mul_left (B ^ n.length) h1
    omega
  rw [Nat.mod_eq_of_lt hsmall]
  exact ⟨hlim, hlen, hbound, m, key⟩

theorem val_replicate_zero : ∀ k : ℕ, val (List.replicate k 0) = 0
  | 0 => rfl
  | k + 1 => by simp [List.replicate_succ, val, val_replicate_zero k]

theorem Limbs_replicate_zero (k : ℕ) : Limbs (List.replicate k 0) := by
  intro a ha
  rw [List.eq_of_mem_replicate ha]
  norm_num

/-- The invariant of the outer loop, for the limbs `as` processed so far:
`2^(32·|as|) · T' = T + value(as) · x + M · n` and `T' < 2n`. -/
theorem sqrFold_spec {x n : List ℕ} {ninv : ℕ} (hx : Limbs x) (hn : Limbs n)
    (hxl : x.length = n.length) (hL : 0 < n.length)
    (hinv : (n.headD 0 * ninv + 1) % B = 0) (hxn : val x < val n) :
    ∀ (as : List ℕ) (st : List ℕ × ℕ), Limbs as → Limbs st.1 → st.1.length = n.length →
      val st.1 + B ^ n.length * st.2 < 2 * val n →
      Limbs (as.foldl (sqrStep x n ninv) st).1 ∧
        (as.foldl (sqrStep x n ninv) st).1.length = n.length ∧
        val (as.foldl (sqrStep x n ninv) st).1 +
            B ^ n.length * (as.foldl (sqrStep x n ninv) st).2 < 2 * val n ∧
        ∃ M, B ^ as.length * (val (as.foldl (sqrStep x n ninv) st).1 +
            B ^ n.length * (as.foldl (sqrStep x n ninv) st).2) =
          val st.1 + B ^ n.length * st.2 + val as * val x + M * val n
  | [], st, _, h1, h2, h3 => ⟨h1, h2, h3, 0, by simp [val]⟩
  | a :: as, st, has, h1, h2, h3 => by
    obtain ⟨s1, s2, s3, m, s4⟩ := sqrStep_spec (ninv := ninv) (ai := a) hx hn h1 hxl h2 hL
      has.head hinv hxn h3
    obtain ⟨r1, r2, r3, M, r4⟩ := sqrFold_spec hx hn hxl hL hinv hxn as
      (sqrStep x n ninv (st.1, st.2) a) has.tail s1 s2 s3
    refine ⟨r1, r2, r3, m + B * M, ?_⟩
    simp only [List.foldl_cons, List.length_cons, val]
    rw [pow_succ (2 ^ 32) as.length]
    change B ^ as.length * B * (val (as.foldl (sqrStep x n ninv) (sqrStep x n ninv (st.1, st.2) a)).1 +
      B ^ n.length * (as.foldl (sqrStep x n ninv) (sqrStep x n ninv (st.1, st.2) a)).2) = _
    generalize val (as.foldl (sqrStep x n ninv) (sqrStep x n ninv (st.1, st.2) a)).1 +
      B ^ n.length * (as.foldl (sqrStep x n ninv) (sqrStep x n ninv (st.1, st.2) a)).2 = T2 at r4 ⊢
    generalize val (sqrStep x n ninv (st.1, st.2) a).1 +
      B ^ n.length * (sqrStep x n ninv (st.1, st.2) a).2 = T1 at s4 r4
    generalize val st.1 + B ^ n.length * st.2 = T0 at s4 ⊢
    calc B ^ as.length * B * T2 = B * (B ^ as.length * T2) := by ring
      _ = B * (T1 + val as * val x + M * val n) := by rw [r4]
      _ = B * T1 + B * (val as * val x) + B * (M * val n) := by ring
      _ = T0 + a * val x + m * val n + B * (val as * val x) + B * (M * val n) := by rw [s4]
      _ = T0 + (a + B * val as) * val x + (m + B * M) * val n := by ring

/-- The outer loop of `mont_sqr`, from `t = 0`. -/
def sqrLoop (x n : List ℕ) (ninv : ℕ) : List ℕ × ℕ :=
  x.foldl (sqrStep x n ninv) (List.replicate n.length 0, 0)

/-- `mont_sqr`: the loop and the conditional subtraction. -/
def montSqr (x n : List ℕ) (ninv : ℕ) : List ℕ :=
  condSub (sqrLoop x n ninv).1 (sqrLoop x n ninv).2 n

/-- **`mont_sqr` is a Montgomery squaring.** For limb arrays `x`, `n` of the same positive
length `L` with `x < n` and `n[0] · ninv ≡ -1 (mod 2^32)`: the result is a limb array of
length `L`, below `n`, and `2^(32 L) · result ≡ x² (mod n)`. -/
theorem montSqr_spec {x n : List ℕ} {ninv : ℕ} (hx : Limbs x) (hn : Limbs n)
    (hxl : x.length = n.length) (hL : 0 < n.length)
    (hinv : (n.headD 0 * ninv + 1) % B = 0) (hxn : val x < val n) :
    Limbs (montSqr x n ninv) ∧ (montSqr x n ninv).length = n.length ∧
      val (montSqr x n ninv) < val n ∧
      (B ^ n.length * val (montSqr x n ninv)) % val n = (val x * val x) % val n := by
  obtain ⟨r1, r2, r3, M, r4⟩ := sqrFold_spec hx hn hxl hL hinv hxn x
    (List.replicate n.length 0, 0) hx (Limbs_replicate_zero _) (by simp)
    (by simp only [val_replicate_zero]; omega)
  simp only [val_replicate_zero, mul_zero, add_zero, zero_add] at r4
  rw [hxl] at r4
  have hT : val (sqrLoop x n ninv).1 + B ^ (sqrLoop x n ninv).1.length * (sqrLoop x n ninv).2 <
      2 * val n := by
    show val (x.foldl (sqrStep x n ninv) (List.replicate n.length 0, 0)).1 +
      B ^ (x.foldl (sqrStep x n ninv) (List.replicate n.length 0, 0)).1.length *
        (x.foldl (sqrStep x n ninv) (List.replicate n.length 0, 0)).2 < 2 * val n
    rw [r2]
    exact r3
  obtain ⟨c1, c2, c3⟩ := condSub_spec (t := (sqrLoop x n ninv).1) (top := (sqrLoop x n ninv).2)
    r1 hn r2 hT
  have hlen : (sqrLoop x n ninv).1.length = n.length := r2
  rw [hlen] at c2 c3
  have hpos : 0 < val n := by omega
  refine ⟨c1, c2, ?_, ?_⟩
  · show val (condSub (sqrLoop x n ninv).1 (sqrLoop x n ninv).2 n) < val n
    rw [c3]
    exact Nat.mod_lt _ hpos
  · show (B ^ n.length * val (condSub (sqrLoop x n ninv).1 (sqrLoop x n ninv).2 n)) % val n = _
    rw [c3, Nat.mul_mod, Nat.mod_mod, ← Nat.mul_mod]
    show (B ^ n.length * (val (x.foldl (sqrStep x n ninv) (List.replicate n.length 0, 0)).1 +
      B ^ n.length * (x.foldl (sqrStep x n ninv) (List.replicate n.length 0, 0)).2)) % val n = _
    rw [r4, Nat.add_mul_mod_self_right]

/-- `dbl_mod`: shift left by one bit, then the conditional subtraction. -/
def dblMod (x n : List ℕ) : List ℕ :=
  condSub (shlRow x 0).1 (shlRow x 0).2 n

/-- **`dbl_mod` doubles modulo `n`**: for `x < n` the result is the limb array of
`2x mod n`. -/
theorem dblMod_spec {x n : List ℕ} (hx : Limbs x) (hn : Limbs n) (hxl : x.length = n.length)
    (hxn : val x < val n) :
    Limbs (dblMod x n) ∧ (dblMod x n).length = n.length ∧
      val (dblMod x n) = (2 * val x) % val n := by
  obtain ⟨s1, s2, -, s4⟩ := shlRow_spec x 0 hx (by norm_num)
  have hT : val (shlRow x 0).1 + B ^ (shlRow x 0).1.length * (shlRow x 0).2 < 2 * val n := by
    rw [s2]
    omega
  obtain ⟨c1, c2, c3⟩ := condSub_spec s1 hn (s2.trans hxl) hT
  rw [s2] at c2 c3
  refine ⟨c1, c2.trans hxl, ?_⟩
  show val (condSub (shlRow x 0).1 (shlRow x 0).2 n) = _
  rw [c3]
  congr 1

end Gpu
