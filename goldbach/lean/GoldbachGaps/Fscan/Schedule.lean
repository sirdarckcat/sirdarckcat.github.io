import Mathlib

/-!
# The exponent schedule of the Fermat kernels

`f52_setup` / `f52_run` in `goldbach/fscan/fermat52.h` (and `fm_setup` / `fm_run` in
`fermat26.h`; commit `a3ab69c`, branch `ccr-d4a17dd0-7uu03r`) test whether
`2^(n-1) ≡ 1 (mod n)` without ever forming the exponent `n - 1`. With `R = 2^104` they

* put `E = n + 103`, `c = ⌈E / 2^t⌉` (computed as `(E + (2^t - 1)) >> t`), `B = c·2^t - E`;
* start from `y₀ ≡ 2^(104 - c)`;
* repeat `t` times: Montgomery-square, then double when the next bit of `B` (most
  significant of its `t` bits first) is set, i.e. `R · yᵢ ≡ 2^βᵢ · yᵢ₋₁²` with
  `βᵢ = bit (t - i) of B`;
* report "probable prime" when `y_t ≡ 1`.

`schedule` proves `y_t · 2^(n-1) ≡ 1 (mod n)` for every odd `n`, so (`schedule_iff`)
`y_t ≡ 1` exactly when `2^(n-1) ≡ 1`. `c_bounds` gives `1 ≤ c ≤ 65` under the kernel's
choice of `t`, so in particular the hypothesis `c ≤ 104` holds.

The later revision of `fermat26.h` (commit `1d8ab96`, branch `ccr-b8c25887-i6tn9f`) uses
the same driver with `R = 2^Rb` for two values of `Rb` (`fm_exponent`: `E = n + Rb - 1`,
start `2^(Rb - c)`): `Rb = 104` and, for the 3-limb kernel, `Rb = 90`. Everything is
therefore proved for a general `Rb ≥ 1` (`cOfR`, `BOfR`, `betaR`, `scheduleR`, …); the
unsuffixed names are the case `Rb = 104`.

The statement is about residues only. That the vector code performs the step
`R · yᵢ ≡ 2^βᵢ · yᵢ₋₁²` is `Fscan.F52.step_spec` (and its 26-bit counterpart).
-/

namespace Fscan.Schedule

/-! ### General `Rb` -/

/-- `c = ⌈(n + Rb - 1) / 2^t⌉`, as the code computes it: `(E + ((1 << t) - 1)) >> t`. -/
def cOfR (Rb n t : ℕ) : ℕ := (n + (Rb - 1) + (2 ^ t - 1)) / 2 ^ t

/-- `B = c·2^t - (n + Rb - 1)`. -/
def BOfR (Rb n t : ℕ) : ℕ := cOfR Rb n t * 2 ^ t - (n + (Rb - 1))

/-- The bit fed at iteration `i` (counted from `1`): bit `t - i` of `B`. -/
def betaR (Rb n t i : ℕ) : ℕ := BOfR Rb n t / 2 ^ (t - i) % 2

theorem betaR_le_one (Rb n t i : ℕ) : betaR Rb n t i ≤ 1 := by
  unfold betaR
  omega

/-- `c·2^t ≥ n + Rb - 1` (so the subtraction defining `B` is exact) and `B < 2^t`. -/
theorem ceil_factsR (Rb n t : ℕ) :
    n + (Rb - 1) ≤ cOfR Rb n t * 2 ^ t ∧ BOfR Rb n t < 2 ^ t := by
  unfold BOfR cOfR
  have hP : 0 < 2 ^ t := by positivity
  have h1 := Nat.div_add_mod' (n + (Rb - 1) + (2 ^ t - 1)) (2 ^ t)
  have h2 := Nat.mod_lt (n + (Rb - 1) + (2 ^ t - 1)) hP
  generalize (n + (Rb - 1) + (2 ^ t - 1)) / 2 ^ t * 2 ^ t = q at h1 ⊢
  generalize (n + (Rb - 1) + (2 ^ t - 1)) % 2 ^ t = r at h1 h2
  generalize 2 ^ t = P at hP h1 h2 ⊢
  omega

/-- Under the kernels' choice of `t` (`n < 2^(t+6)`, i.e. `t = bitlength(n_max) - 6`, with
`t ≥ 7`) and `2 ≤ Rb ≤ 128`, one has `1 ≤ c ≤ 65`. -/
theorem c_boundsR {Rb n t : ℕ} (hRb : 2 ≤ Rb) (hRb' : Rb ≤ 128) (ht : 7 ≤ t)
    (hn : n < 2 ^ (t + 6)) : 1 ≤ cOfR Rb n t ∧ cOfR Rb n t ≤ 65 := by
  unfold cOfR
  have hP : 0 < 2 ^ t := by positivity
  have h128 : 2 ^ 7 ≤ 2 ^ t := Nat.pow_le_pow_right (by norm_num) ht
  have h64 : 2 ^ (t + 6) = 64 * 2 ^ t := by rw [pow_add]; ring
  rw [h64] at hn
  constructor
  · exact (Nat.one_le_div_iff hP).mpr (by omega)
  · have : (n + (Rb - 1) + (2 ^ t - 1)) / 2 ^ t < 66 := by
      rw [Nat.div_lt_iff_lt_mul hP]
      omega
    omega

/-- **The exponent schedule.** For odd `n` and `Rb ≥ 1`, if `y 0 ≡ 2^(Rb - c)` and each step
satisfies `2^Rb · y (i+1) ≡ 2^(β (i+1)) · (y i)²` modulo `n`, then
`y t · 2^(n-1) ≡ 1 (mod n)`. -/
theorem scheduleR {Rb n t : ℕ} (hRb : 1 ≤ Rb) (hodd : n % 2 = 1) (hc : cOfR Rb n t ≤ Rb)
    (y : ℕ → ℕ) (h0 : y 0 ≡ 2 ^ (Rb - cOfR Rb n t) [MOD n])
    (hstep : ∀ i < t, 2 ^ Rb * y (i + 1) ≡ 2 ^ betaR Rb n t (i + 1) * y i ^ 2 [MOD n]) :
    y t * 2 ^ (n - 1) ≡ 1 [MOD n] := by
  obtain ⟨hceil, hBlt⟩ := ceil_factsR Rb n t
  have hBdef : BOfR Rb n t = cOfR Rb n t * 2 ^ t - (n + (Rb - 1)) := rfl
  have hbeta : ∀ i, betaR Rb n t i = BOfR Rb n t / 2 ^ (t - i) % 2 := fun _ => rfl
  generalize cOfR Rb n t = c at *
  generalize BOfR Rb n t = B at *
  have hcop : ∀ k : ℕ, Nat.gcd n (2 ^ k) = 1 := fun k =>
    Nat.Coprime.pow_right k (Nat.coprime_two_right.mpr (Nat.odd_iff.mpr hodd))
  -- invariant: y i · 2^(c·2^i) ≡ 2^(Rb + (top i bits of B))
  have inv : ∀ i, i ≤ t → y i * 2 ^ (c * 2 ^ i) ≡ 2 ^ (Rb + B / 2 ^ (t - i)) [MOD n] := by
    intro i
    induction i with
    | zero =>
      intro _
      have h : B / 2 ^ (t - 0) = 0 := Nat.div_eq_of_lt (by simpa using hBlt)
      rw [h]
      simp only [pow_zero, mul_one, add_zero]
      calc y 0 * 2 ^ c ≡ 2 ^ (Rb - c) * 2 ^ c [MOD n] := h0.mul_right _
        _ = 2 ^ Rb := by rw [← pow_add, Nat.sub_add_cancel hc]
    | succ i ih =>
      intro hi
      have hi' : i < t := hi
      have ih' := ih hi'.le
      have hs := hstep i hi'
      have htop : B / 2 ^ (t - (i + 1)) = 2 * (B / 2 ^ (t - i)) + betaR Rb n t (i + 1) := by
        rw [hbeta]
        obtain ⟨k, hk⟩ : ∃ k, t - (i + 1) = k := ⟨_, rfl⟩
        rw [hk, show t - i = k + 1 by omega, pow_succ, ← Nat.div_div_eq_div_mul]
        omega
      refine Nat.ModEq.cancel_left_of_coprime (c := 2 ^ Rb) (hcop Rb) ?_
      calc 2 ^ Rb * (y (i + 1) * 2 ^ (c * 2 ^ (i + 1)))
          = 2 ^ Rb * y (i + 1) * (2 ^ (c * 2 ^ i)) ^ 2 := by
            rw [← pow_mul, show c * 2 ^ (i + 1) = c * 2 ^ i * 2 by ring]
            ring
        _ ≡ 2 ^ betaR Rb n t (i + 1) * y i ^ 2 * (2 ^ (c * 2 ^ i)) ^ 2 [MOD n] :=
            hs.mul_right _
        _ = 2 ^ betaR Rb n t (i + 1) * (y i * 2 ^ (c * 2 ^ i)) ^ 2 := by ring
        _ ≡ 2 ^ betaR Rb n t (i + 1) * (2 ^ (Rb + B / 2 ^ (t - i))) ^ 2 [MOD n] :=
            (ih'.pow 2).mul_left _
        _ = 2 ^ Rb * 2 ^ (Rb + B / 2 ^ (t - (i + 1))) := by
            rw [htop, ← pow_mul, ← pow_add, ← pow_add]
            congr 1
            omega
  have hfin := inv t le_rfl
  rw [Nat.sub_self, pow_zero, Nat.div_one] at hfin
  have hE : c * 2 ^ t = n - 1 + (Rb + B) := by omega
  rw [hE, pow_add, ← mul_assoc] at hfin
  refine Nat.ModEq.cancel_right_of_coprime (c := 2 ^ (Rb + B)) (hcop _) ?_
  rwa [one_mul]

/-- The test the code makes: `y t ≡ 1` exactly when `2^(n-1) ≡ 1 (mod n)`. -/
theorem schedule_iffR {Rb n t : ℕ} (hRb : 1 ≤ Rb) (hodd : n % 2 = 1) (hc : cOfR Rb n t ≤ Rb)
    (y : ℕ → ℕ) (h0 : y 0 ≡ 2 ^ (Rb - cOfR Rb n t) [MOD n])
    (hstep : ∀ i < t, 2 ^ Rb * y (i + 1) ≡ 2 ^ betaR Rb n t (i + 1) * y i ^ 2 [MOD n]) :
    y t ≡ 1 [MOD n] ↔ 2 ^ (n - 1) ≡ 1 [MOD n] := by
  have h := scheduleR hRb hodd hc y h0 hstep
  constructor
  · intro hy
    calc 2 ^ (n - 1) = 1 * 2 ^ (n - 1) := (one_mul _).symm
      _ ≡ y t * 2 ^ (n - 1) [MOD n] := hy.symm.mul_right _
      _ ≡ 1 [MOD n] := h
  · intro h2
    calc y t = y t * 1 := (mul_one _).symm
      _ ≡ y t * 2 ^ (n - 1) [MOD n] := h2.symm.mul_left _
      _ ≡ 1 [MOD n] := h

/-! ### The case `Rb = 104` (`fermat52.h` and the 4-limb kernel) -/

/-- `c = ⌈(n + 103) / 2^t⌉`, as the code computes it: `(E + ((1 << t) - 1)) >> t`. -/
def cOf (n t : ℕ) : ℕ := cOfR 104 n t

/-- `B = c·2^t - (n + 103)`. -/
def BOf (n t : ℕ) : ℕ := BOfR 104 n t

/-- The bit fed at iteration `i` (counted from `1`): bit `t - i` of `B`. -/
def beta (n t i : ℕ) : ℕ := betaR 104 n t i

theorem beta_le_one (n t i : ℕ) : beta n t i ≤ 1 := betaR_le_one 104 n t i

theorem cOf_eq (n t : ℕ) : cOf n t = (n + 103 + (2 ^ t - 1)) / 2 ^ t := rfl

theorem BOf_eq (n t : ℕ) : BOf n t = cOf n t * 2 ^ t - (n + 103) := rfl

theorem beta_eq (n t i : ℕ) : beta n t i = BOf n t / 2 ^ (t - i) % 2 := rfl

/-- `c·2^t ≥ n + 103` (so the subtraction defining `B` is exact) and `B < 2^t`. -/
theorem ceil_facts (n t : ℕ) : n + 103 ≤ cOf n t * 2 ^ t ∧ BOf n t < 2 ^ t :=
  ceil_factsR 104 n t

/-- Under the kernel's choice of `t` (`n < 2^(t+6)`, i.e. `t = bitlength(n_max) - 6`, and
`t ≥ 7`), one has `1 ≤ c ≤ 65`. -/
theorem c_bounds {n t : ℕ} (ht : 7 ≤ t) (hn : n < 2 ^ (t + 6)) : 1 ≤ cOf n t ∧ cOf n t ≤ 65 :=
  c_boundsR (by norm_num) (by norm_num) ht hn

/-- **The exponent schedule.** For odd `n`, if `y 0 ≡ 2^(104 - c)` and each step satisfies
`2^104 · y (i+1) ≡ 2^(β (i+1)) · (y i)²` modulo `n`, then `y t · 2^(n-1) ≡ 1 (mod n)`. -/
theorem schedule {n t : ℕ} (hodd : n % 2 = 1) (hc : cOf n t ≤ 104) (y : ℕ → ℕ)
    (h0 : y 0 ≡ 2 ^ (104 - cOf n t) [MOD n])
    (hstep : ∀ i < t, 2 ^ 104 * y (i + 1) ≡ 2 ^ beta n t (i + 1) * y i ^ 2 [MOD n]) :
    y t * 2 ^ (n - 1) ≡ 1 [MOD n] :=
  scheduleR (by norm_num) hodd hc y h0 hstep

/-- The test the code makes: `y t ≡ 1` exactly when `2^(n-1) ≡ 1 (mod n)`. -/
theorem schedule_iff {n t : ℕ} (hodd : n % 2 = 1) (hc : cOf n t ≤ 104) (y : ℕ → ℕ)
    (h0 : y 0 ≡ 2 ^ (104 - cOf n t) [MOD n])
    (hstep : ∀ i < t, 2 ^ 104 * y (i + 1) ≡ 2 ^ beta n t (i + 1) * y i ^ 2 [MOD n]) :
    y t ≡ 1 [MOD n] ↔ 2 ^ (n - 1) ≡ 1 [MOD n] :=
  schedule_iffR (by norm_num) hodd hc y h0 hstep

end Fscan.Schedule
