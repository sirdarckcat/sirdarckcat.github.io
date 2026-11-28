import GoldbachGaps.RankinSmooth

/-!
# Iterated-log lower bound with Goldbach representation

This module formalises the bridge from:
1. the unconditional Rankin-upgraded two-layer pre-sieve in `GoldbachGaps/RankinSmooth.lean`
   (`eventually_exists_two_layer_classes`, `exists_base_even_of_classes`,
   `not_isSummand_of_partial_cover`),
2. the simultaneous-root lemma (`SimultaneousRootsStatement`, matching verbatim
   `LongGapsBetweenPrimes.eventually_simultaneous_roots` in `openai/LongGapsBetweenPrimes`,
   commit `03a1190d`, `LongGapsBetweenPrimes.lean#L3480-L3485`), and
3. the Montgomery–Vaughan (1975) Goldbach exceptional-set bound
   (`MontgomeryVaughanStatement`, *Acta Arith.* 27, Theorem 1: `E(X) ≪ X^{1 - δ}`),

to the headline theorem (`eventually_exists_goldbach_iterated_log`):
there exists `c > 0` such that for all sufficiently large `X`, there is an even integer
`N ∈ [X / 2, X]` **having a Goldbach representation** (`∃ p, IsSummand N p`) and no Goldbach
summand below
`c · log X · (log log X)³ · log log log log X / (log log log X)²`,
together with its `IsLeastSummand` corollary (`eventually_exists_isLeastSummand_iterated_log`).

Following the repository convention of `GoldbachGaps/Effective.lean` (`LinnikStatement`), both
external deep inputs are stated as explicit `Prop` hypothesis parameters using Mathlib primitives
only (zero custom declarations or unproved steps). All four bridge steps — (i) diameter vs.
auxiliary-prime pairwise distinctness and `ZMod p` linear-root lifting, (ii) pre-sieve survivor
capacity upgrade to `η y`, (iii) CRT disjoint-interval replication across `[X / 2, X]`, and
(iv) pigeonhole subtraction against `goldbachExceptions X` — are proved completely in Lean's kernel.
-/

namespace GoldbachGaps

open Finset Filter

/-! ### Part A: Explicit Mathlib-only hypothesis statements -/

/-- Auxiliary primes in `(Z, Y]`, matching `openai/LongGapsBetweenPrimes` (`L1183`). -/
def auxiliaryPrimes (Z Y : ℕ) : Finset ℕ := Y.primesLE \ Z.primesLE

/-- Product of auxiliary primes in `(Z, Y]`, matching `LongGapsBetweenPrimes.lean#L1186`. -/
def auxiliaryProduct (Z Y : ℕ) : ℕ := ∏ p ∈ auxiliaryPrimes Z Y, p

/-- Lower sieve cutoff `⌊x^6⌋` (`LongGapsBetweenPrimes.lean#L1667`). -/
noncomputable def sieveZ (x : ℝ) : ℕ := ⌊x ^ 6⌋₊

/-- Logarithmic upper cutoff `x / (log x)^5` (`LongGapsBetweenPrimes.lean#L1670`). -/
noncomputable def sieveUpperLog (x : ℝ) : ℝ := x / (Real.log x) ^ 5

/-- Upper sieve cutoff `⌊exp(x / (log x)^5)⌋` (`LongGapsBetweenPrimes.lean#L1673`). -/
noncomputable def sieveY (x : ℝ) : ℕ := ⌊Real.exp (sieveUpperLog x)⌋₊

/-- Product of auxiliary primes in `(sieveZ x, sieveY x]` (`LongGapsBetweenPrimes.lean#L1676`). -/
noncomputable def sieveP (x : ℝ) : ℕ := auxiliaryProduct (sieveZ x) (sieveY x)

/-- Translation interval length `⌊exp x⌋` (`LongGapsBetweenPrimes.lean#L3302`). -/
noncomputable def sieveT (x : ℝ) : ℕ := ⌊Real.exp x⌋₊

/-- Prime divisors of `P` as a finite index type (`LongGapsBetweenPrimes.lean#L2058`). -/
abbrev PrimeIndex (P : ℕ) := {p : ℕ // p ∈ P.primeFactors}

/-- Residue vector of `n` modulo the prime divisors of `P` (`LongGapsBetweenPrimes.lean#L2562`). -/
def residueVector (P n : ℕ) : (p : PrimeIndex P) → Fin p.val :=
  fun p => ⟨n % p.val, Nat.mod_lt n (Nat.mem_primeFactors.mp p.property).1.pos⟩

/-- Simultaneous-root lemma from *Improved Long Gaps Between Primes*
(`openai/LongGapsBetweenPrimes`, commit `03a1190d`, `LongGapsBetweenPrimes.lean#L3480-L3485`),
expressed purely in Mathlib primitives. -/
def SimultaneousRootsStatement : Prop :=
  ∃ η : ℝ, 0 < η ∧ ∀ᶠ x : ℝ in Filter.atTop,
    ∀ k : ℕ, ((k + 1 : ℕ) : ℝ) ≤ η * x →
    ∀ root : (p : PrimeIndex (sieveP x)) → Fin (k + 1) → Fin p.val,
    (∀ p, Function.Injective (root p)) →
    ∃ n < sieveT x, ∀ i : Fin (k + 1), ∃ p : PrimeIndex (sieveP x),
      residueVector (sieveP x) n p = root p i

open Classical in
/-- The Goldbach exceptional set up to `X`: even integers `4 ≤ N ≤ X` with no Goldbach
representation `N = p + q` with `p, q` prime. -/
noncomputable def goldbachExceptions (X : ℕ) : Finset ℕ :=
  (Finset.Icc 4 X).filter fun N => Even N ∧ ¬ ∃ p, IsSummand N p

/-- Montgomery–Vaughan (1975), *The exceptional set in Goldbach's problem*, Acta Arith. 27,
Theorem 1: there exist `δ > 0` and `C > 0` such that the number of even integers `4 ≤ N ≤ X`
not representable as a sum of two primes is at most `C · X^(1 - δ)` for all sufficiently large `X`. -/
def MontgomeryVaughanStatement : Prop :=
  ∃ δ C : ℝ, 0 < δ ∧ 0 < C ∧ ∀ᶠ X : ℕ in Filter.atTop,
    ((goldbachExceptions X).card : ℝ) ≤ C * (X : ℝ) ^ (1 - δ)

/-- Target desert bound in terms of the primorial scale `y`:
`⌊c₁ · y · (log y)³ · log₃ y / (log₂ y)²⌋`. -/
noncomputable def iteratedQ (c₁ : ℝ) (y : ℕ) : ℕ :=
  ⌊c₁ * (y : ℝ) * Real.log (y : ℝ) ^ 3 * Real.log (Real.log (Real.log (y : ℝ))) /
    Real.log (Real.log (y : ℝ)) ^ 2⌋₊

private theorem mem_primeFactors_sieveP {x : ℝ} {p : ℕ} (hp : p ∈ (sieveP x).primeFactors) :
    p.Prime ∧ sieveZ x < p ∧ p ≤ sieveY x := by
  obtain ⟨hp_prime, hdvd, -⟩ := Nat.mem_primeFactors.mp hp
  rw [sieveP, auxiliaryProduct] at hdvd
  obtain ⟨q, hq, hpq⟩ := (Prime.dvd_finsetProd_iff hp_prime.prime _).mp hdvd
  obtain ⟨hqY, hqnotZ⟩ := Finset.mem_sdiff.mp hq
  obtain ⟨hqleY, hq_prime⟩ := Nat.mem_primesLE.mp hqY
  have heq : p = q := (Nat.prime_dvd_prime_iff_eq hp_prime hq_prime).mp hpq
  subst heq
  have hpZ : sieveZ x < p := by
    by_contra hle
    exact hqnotZ (Nat.mem_primesLE.mpr ⟨by omega, hp_prime⟩)
  exact ⟨hp_prime, hpZ, hqleY⟩

private theorem sieveZ_natCast (y : ℕ) : sieveZ (y : ℝ) = y ^ 6 := by
  unfold sieveZ
  rw [← Nat.cast_pow, Nat.floor_natCast]

private theorem sieveT_pos_of_nonneg {x : ℝ} (hx : 0 ≤ x) : 0 < sieveT x :=
  Nat.floor_pos.mpr (Real.one_le_exp hx)

private theorem sieveY_le_exp {y : ℕ} (hL : 1 ≤ Real.log (y : ℝ)) :
    (sieveY (y : ℝ) : ℝ) ≤ Real.exp (y : ℝ) := by
  have hfl : (sieveY (y : ℝ) : ℝ) ≤ Real.exp (sieveUpperLog (y : ℝ)) :=
    Nat.floor_le (Real.exp_pos _).le
  refine hfl.trans (Real.exp_le_exp.mpr ?_)
  unfold sieveUpperLog
  exact div_le_self (Nat.cast_nonneg y) (one_le_pow₀ hL)

/-! ### Part B: Step (i) — Diameter vs. auxiliary-prime distinctness and `ZMod p` linear roots -/

/-- For a prime `p` coprime to `M₀` and injective shifts `q : Fin k → ℕ` all `< p`, there is an
injective root map `root : Fin k → Fin p` such that `n % p = (root i).val` forces
`p ∣ b + M₀ * (n + 1) - q i`. -/
theorem iterated_log_linear_roots_sub {p k M₀ b : ℕ} (hp : p.Prime) (hM : M₀.Coprime p)
    (q : Fin k → ℕ) (hq_inj : Function.Injective q) (hq_lt : ∀ i, q i < p) :
    ∃ root : Fin k → Fin p, Function.Injective root ∧
      ∀ n i, n % p = (root i).val → q i ≤ b + M₀ * (n + 1) →
        p ∣ b + M₀ * (n + 1) - q i := by
  have : Fact p.Prime := ⟨hp⟩
  have : NeZero p := ⟨hp.ne_zero⟩
  have hM' : (M₀ : ZMod p) ≠ 0 := by
    intro h0
    have hdvd : p ∣ M₀ := (ZMod.natCast_eq_zero_iff M₀ p).mp h0
    exact hp.ne_one (Nat.dvd_one.mp (hM.gcd_eq_one ▸ Nat.dvd_gcd hdvd dvd_rfl))
  let root (i : Fin k) : Fin p :=
    ⟨(((q i : ZMod p) - ((b + M₀ : ℕ) : ZMod p)) / (M₀ : ZMod p)).val, ZMod.val_lt _⟩
  refine ⟨root, ?_, ?_⟩
  · intro i j hij
    have hval : (root i).val = (root j).val := congrArg Fin.val hij
    have hz : (((q i : ZMod p) - ((b + M₀ : ℕ) : ZMod p)) / (M₀ : ZMod p)) =
        (((q j : ZMod p) - ((b + M₀ : ℕ) : ZMod p)) / (M₀ : ZMod p)) := by
      rw [← ZMod.natCast_zmod_val (((q i : ZMod p) - ((b + M₀ : ℕ) : ZMod p)) / (M₀ : ZMod p)),
        ← ZMod.natCast_zmod_val (((q j : ZMod p) - ((b + M₀ : ℕ) : ZMod p)) / (M₀ : ZMod p))]
      exact congrArg (fun a : ℕ => (a : ZMod p)) hval
    have hmul := congrArg (· * (M₀ : ZMod p)) hz
    rw [div_mul_cancel₀ _ hM', div_mul_cancel₀ _ hM'] at hmul
    have hqmod : (q i : ZMod p) = (q j : ZMod p) := sub_left_inj.mp hmul
    have hmeq : q i % p = q j % p := (ZMod.natCast_eq_natCast_iff (q i) (q j) p).mp hqmod
    rw [Nat.mod_eq_of_lt (hq_lt i), Nat.mod_eq_of_lt (hq_lt j)] at hmeq
    exact hq_inj hmeq
  · intro n i hn hle
    rw [← ZMod.natCast_eq_zero_iff, Nat.cast_sub hle]
    have hnz : (n : ZMod p) = ((q i : ZMod p) - ((b + M₀ : ℕ) : ZMod p)) / (M₀ : ZMod p) := by
      have h1 : (n : ZMod p) = ((n % p : ℕ) : ZMod p) :=
        (ZMod.natCast_eq_natCast_iff n (n % p) p).mpr (Nat.mod_modEq n p).symm
      rw [h1, hn]
      exact ZMod.natCast_zmod_val _
    push_cast
    rw [hnz, mul_add, mul_div_cancel₀ _ hM', mul_one]
    push_cast
    ring

/-- **Step (i): Survivor-killing translate via simultaneous roots.** Whenever all surviving shifts
`q ∈ U` satisfy `q < Qstar ≤ y^6` (so their diameter is strictly below every auxiliary prime
`p > sieveZ y = y^6`), `#U ≤ η y`, and `Qstar + sieveY y < b`, the simultaneous-root property at
scale `y` yields `n < sieveT y` such that `b + primorial y * (n + 1) - q` is composite for every
`q ∈ U`. -/
theorem iterated_log_translate_kill_survivors {y Qstar b : ℕ} {η : ℝ}
    (_hy2 : 2 ≤ y) (hQ : Qstar ≤ y ^ 6) (hb : Qstar + sieveY (y : ℝ) < b)
    {U : Finset ℕ} (hUQ : ∀ q ∈ U, q < Qstar) (hUcard : (U.card : ℝ) ≤ η * (y : ℝ))
    (hSR_y : ∀ k : ℕ, ((k + 1 : ℕ) : ℝ) ≤ η * (y : ℝ) →
      ∀ root : (p : PrimeIndex (sieveP (y : ℝ))) → Fin (k + 1) → Fin p.val,
      (∀ p, Function.Injective (root p)) →
      ∃ n < sieveT (y : ℝ), ∀ i : Fin (k + 1), ∃ p : PrimeIndex (sieveP (y : ℝ)),
        residueVector (sieveP (y : ℝ)) n p = root p i) :
    ∃ n < sieveT (y : ℝ), ∀ q ∈ U, ¬ (b + primorial y * (n + 1) - q).Prime := by
  classical
  by_cases hUempty : U = ∅
  · refine ⟨0, sieveT_pos_of_nonneg (Nat.cast_nonneg y), ?_⟩
    intro q hq
    rw [hUempty] at hq
    exact (Finset.notMem_empty q hq).elim
  · have hUne : U.Nonempty := Finset.ne_empty_iff_nonempty.mp hUempty
    obtain ⟨k, hk⟩ := Nat.exists_eq_succ_of_ne_zero hUne.card_pos.ne'
    let e : Fin (k + 1) ≃ ↥U := (U.equivFin.trans (finCongr hk)).symm
    let qf : Fin (k + 1) → ℕ := fun i => (e i).val
    have hqf_inj : Function.Injective qf := fun i j hij => e.injective (Subtype.ext hij)
    have hroots : ∀ p : PrimeIndex (sieveP (y : ℝ)),
        ∃ r : Fin (k + 1) → Fin p.val, Function.Injective r ∧
          ∀ n i, n % p.val = (r i).val → qf i ≤ b + primorial y * (n + 1) →
            p.val ∣ b + primorial y * (n + 1) - qf i := by
      intro p
      obtain ⟨hp, hpZ, -⟩ := mem_primeFactors_sieveP p.property
      rw [sieveZ_natCast] at hpZ
      have hylt : y < p.val := lt_of_le_of_lt (Nat.le_self_pow (by norm_num : 6 ≠ 0) y) hpZ
      have hcop : (primorial y).Coprime p.val := by
        refine (hp.coprime_iff_not_dvd.mpr fun hdvd => ?_).symm
        have := hp.dvd_primorial_iff.mp hdvd
        omega
      have hqlt : ∀ i, qf i < p.val := fun i =>
        lt_trans (lt_of_lt_of_le (hUQ (e i).val (e i).property) hQ) hpZ
      exact iterated_log_linear_roots_sub hp hcop qf hqf_inj hqlt
    let root : (p : PrimeIndex (sieveP (y : ℝ))) → Fin (k + 1) → Fin p.val :=
      fun p => Classical.choose (hroots p)
    have hinj : ∀ p, Function.Injective (root p) := fun p => (Classical.choose_spec (hroots p)).1
    have hdiv : ∀ p n i, n % p.val = (root p i).val → qf i ≤ b + primorial y * (n + 1) →
        p.val ∣ b + primorial y * (n + 1) - qf i :=
      fun p => (Classical.choose_spec (hroots p)).2
    have hkcard : ((k + 1 : ℕ) : ℝ) ≤ η * (y : ℝ) := by simpa [hk] using hUcard
    obtain ⟨n, hnT, hhit⟩ := hSR_y k hkcard root hinj
    refine ⟨n, hnT, fun q hq hprime => ?_⟩
    let i : Fin (k + 1) := e.symm ⟨q, hq⟩
    have hqfi : qf i = q := by simp [qf, i]
    obtain ⟨p, hpeq⟩ := hhit i
    obtain ⟨hp, -, hpY⟩ := mem_primeFactors_sieveP p.property
    have hmod : n % p.val = (root p i).val := congrArg Fin.val hpeq
    have hqQ : q < Qstar := hUQ q hq
    have hqle : qf i ≤ b + primorial y * (n + 1) := by omega
    have hdvd : p.val ∣ b + primorial y * (n + 1) - q := by
      simpa [hqfi] using hdiv p n i hmod hqle
    rcases (Nat.dvd_prime hprime).mp hdvd with h1 | hself
    · exact hp.ne_one h1
    · omega

/-! ### Part C: Step (ii) — Pre-sieve survivor capacity upgrade (`#U ≤ η y`) -/

/-- **Step (ii): Pre-sieve survivor capacity upgrade.** For every `η > 0` and all sufficiently
large `y`, the two-layer Rankin pre-sieve on `oddPrimesLE (y / 4)` produces an even residue
`A₀ < primorial y` and a survivor set `U ⊆ range (iteratedQ (η / 1040) y)` with `#U ≤ η y` such
that every `N ≡ A₀ [MOD primorial y]` above `Q* + y` eliminates all `q < Q*` outside `U`. -/
theorem iterated_log_presieve_small_survivors {η : ℝ} (hη : 0 < η) :
    ∀ᶠ y : ℕ in Filter.atTop,
      2 ≤ y ∧
      iteratedQ (η / 1040) y ≤ y ^ 6 ∧
      ∃ (A₀ : ℕ) (U : Finset ℕ),
        Even A₀ ∧ A₀ < primorial y ∧
        (∀ q ∈ U, q < iteratedQ (η / 1040) y) ∧
        (U.card : ℝ) ≤ η * (y : ℝ) ∧
        ∀ (N q : ℕ), N ≡ A₀ [MOD primorial y] →
          iteratedQ (η / 1040) y + y < N →
          q < iteratedQ (η / 1040) y → q ∉ U → ¬ IsSummand N q := by
  classical
  have hcast : Tendsto (fun y : ℕ => (y : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun y : ℕ => Real.log (y : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hL2 : Tendsto (fun y : ℕ => Real.log (Real.log (y : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hL3 : Tendsto (fun y : ℕ => Real.log (Real.log (Real.log (y : ℝ)))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL2
  have ho4 := (Real.isLittleO_pow_log_id_atTop (n := 4)).def (show (0 : ℝ) < 1 by norm_num)
  have ho2 := (Real.isLittleO_pow_log_id_atTop (n := 2)).def (show (0 : ℝ) < 1 by norm_num)
  filter_upwards [eventually_exists_two_layer_classes, eventually_ge_atTop 16,
    hcast.eventually ho4, hL.eventually ho2,
    hL.eventually_ge_atTop (max (max 100 (1 / (10 * η))) (2080 / η)),
    hL2.eventually_ge_atTop (max 4 (η / 1040)),
    hL3.eventually_ge_atTop 2] with
    y htwo hy16 h4 h2 hLbig hL2big hL3_2
  set L := Real.log (y : ℝ) with hLdef
  set L₂ := Real.log L with hL2def
  set L₃ := Real.log L₂ with hL3def
  set c₁ := η / 1040
  set R := c₁ * (y : ℝ) * L ^ 3 * L₃ / L₂ ^ 2
  set Qstar := iteratedQ c₁ y
  have hy0 : (0 : ℝ) < y := by exact_mod_cast (by omega : 0 < y)
  have hL100 : 100 ≤ L := ((le_max_left _ _).trans (le_max_left _ _)).trans hLbig
  have hLeta1 : 1 / (10 * η) ≤ L := ((le_max_right _ _).trans (le_max_left _ _)).trans hLbig
  have hLeta2 : 2080 / η ≤ L := (le_max_right _ _).trans hLbig
  have hL2_4 : 4 ≤ L₂ := (le_max_left _ _).trans hL2big
  have hL2_c1 : c₁ ≤ L₂ := (le_max_right _ _).trans hL2big
  have hL0 : 0 < L := by linarith
  have hL20 : 0 < L₂ := by linarith
  have hL30 : 0 < L₃ := by linarith
  have hc10 : 0 < c₁ := by positivity
  have hL4y : L ^ 4 ≤ (y : ℝ) := by
    simp only [id, Real.norm_eq_abs] at h4
    rw [abs_of_nonneg hy0.le, abs_of_nonneg (by positivity : 0 ≤ L ^ 4)] at h4
    linarith
  have hL2sqL : L₂ ^ 2 ≤ L := by
    simp only [id, Real.norm_eq_abs] at h2
    rw [abs_of_nonneg hL0.le, abs_of_nonneg (by positivity : 0 ≤ L₂ ^ 2)] at h2
    linarith
  have hL3leL2 : L₃ ≤ L₂ := by
    have := Real.log_le_sub_one_of_pos hL20
    linarith
  -- Show `y ≤ Qstar ≤ y * L^4 ≤ y^6`
  have hyQ : y ≤ Qstar := by
    rw [show Qstar = ⌊R⌋₊ from rfl]
    apply Nat.le_floor
    rw [le_div_iff₀ (by positivity : 0 < L₂ ^ 2)]
    have hcL : 2 ≤ c₁ * L := by
      have h1 : 2080 ≤ L * η := (div_le_iff₀ hη).mp hLeta2
      have heq : c₁ * L = (L * η) / 1040 := by simp only [c₁]; ring
      linarith
    have hL2mul : L₂ ^ 2 ≤ L ^ 2 * L₃ := by
      have hLsq : L ≤ L ^ 2 := le_self_pow₀ (by linarith) (by norm_num)
      nlinarith
    have h1 : (y : ℝ) * L₂ ^ 2 ≤ (y : ℝ) * (L ^ 2 * L₃) :=
      mul_le_mul_of_nonneg_left hL2mul hy0.le
    have h2 : (y : ℝ) * (L ^ 2 * L₃) ≤ c₁ * (y : ℝ) * L ^ 3 * L₃ := by
      have heq : c₁ * (y : ℝ) * L ^ 3 * L₃ = (c₁ * L) * ((y : ℝ) * (L ^ 2 * L₃)) := by ring
      rw [heq]
      nlinarith [mul_nonneg hy0.le (by positivity : 0 ≤ L ^ 2 * L₃)]
    linarith
  have hQleR : (Qstar : ℝ) ≤ R := Nat.floor_le (by positivity)
  have hQle : (Qstar : ℝ) ≤ (y : ℝ) * L ^ 4 := by
    have hRle : R ≤ (y : ℝ) * L ^ 4 := by
      rw [div_le_iff₀ (by positivity : 0 < L₂ ^ 2)]
      have h1 : c₁ * L₃ ≤ L₂ * L₂ := mul_le_mul hL2_c1 hL3leL2 hL30.le hL20.le
      have h2 : L₂ * L₂ ≤ L * L₂ ^ 2 := by
        have hsq : L₂ * L₂ = 1 * L₂ ^ 2 := by ring
        rw [hsq]
        exact mul_le_mul_of_nonneg_right (by linarith) (by positivity)
      have h3 : (y : ℝ) * L ^ 3 * (c₁ * L₃) ≤ (y : ℝ) * L ^ 3 * (L * L₂ ^ 2) :=
        mul_le_mul_of_nonneg_left (h1.trans h2) (by positivity)
      have heqL : c₁ * (y : ℝ) * L ^ 3 * L₃ = (y : ℝ) * L ^ 3 * (c₁ * L₃) := by ring
      have heqR : (y : ℝ) * L ^ 4 * L₂ ^ 2 = (y : ℝ) * L ^ 3 * (L * L₂ ^ 2) := by ring
      linarith
    exact hQleR.trans hRle
  have hQy6 : Qstar ≤ y ^ 6 := by
    have h1 : (Qstar : ℝ) ≤ ((y ^ 6 : ℕ) : ℝ) := by
      push_cast
      have hy2 : (y : ℝ) * L ^ 4 ≤ (y : ℝ) ^ 2 := by
        rw [sq]
        exact mul_le_mul_of_nonneg_left hL4y hy0.le
      have hy26 : (y : ℝ) ^ 2 ≤ (y : ℝ) ^ 6 :=
        pow_le_pow_right₀ (by exact_mod_cast (by omega : 1 ≤ y)) (by norm_num)
      linarith
    exact_mod_cast h1
  -- Apply the unified two-layer bound from `RankinSmooth`
  obtain ⟨a, ha⟩ := htwo Qstar hyQ hQle
  set w := y / 4
  set U := {q ∈ range Qstar | q.Prime ∧ q ≠ 2 ∧ ∀ r ∈ oddPrimesLE w, ¬ q ≡ a r [MOD r]}
  have hUr : (U.card : ℝ) ≤ η * (y : ℝ) := by
    have h1 : 520 * (Qstar : ℝ) * L₂ ^ 2 / (L ^ 3 * L₃) ≤
        520 * R * L₂ ^ 2 / (L ^ 3 * L₃) := by
      refine div_le_div_of_nonneg_right ?_ (by positivity)
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hQleR (by norm_num)) (by positivity)
    have h2 : 520 * R * L₂ ^ 2 / (L ^ 3 * L₃) = η / 2 * (y : ℝ) := by
      rw [div_eq_iff (by positivity : (L ^ 3 * L₃) ≠ 0)]
      have hRmul : R * L₂ ^ 2 = c₁ * (y : ℝ) * L ^ 3 * L₃ := div_mul_cancel₀ _ (by positivity)
      calc 520 * R * L₂ ^ 2 = 520 * (R * L₂ ^ 2) := by ring
        _ = 520 * (c₁ * (y : ℝ) * L ^ 3 * L₃) := by rw [hRmul]
        _ = η / 2 * (y : ℝ) * (L ^ 3 * L₃) := by simp only [c₁]; ring
    have h3 : (y : ℝ) / (20 * L) ≤ η / 2 * (y : ℝ) := by
      rw [div_le_iff₀ (by positivity : 0 < 20 * L)]
      have hmul : 1 ≤ 10 * η * L := by
        have := (div_le_iff₀ (by positivity : 0 < 10 * η)).mp hLeta1
        linarith
      have hmul2 : (y : ℝ) * 1 ≤ (y : ℝ) * (10 * η * L) :=
        mul_le_mul_of_nonneg_left hmul hy0.le
      have heq : η / 2 * (y : ℝ) * (20 * L) = (y : ℝ) * (10 * η * L) := by ring
      linarith
    linarith
  -- Extract even CRT base `A₀ < primorial y`
  have hRodd : ∀ r ∈ oddPrimesLE w, r.Prime ∧ r ≠ 2 := fun r hr => (mem_oddPrimesLE.mp hr).2
  have hRle : ∀ r ∈ oddPrimesLE w, r ≤ y := fun r hr => by
    have := (mem_oddPrimesLE.mp hr).1
    omega
  obtain ⟨A₀, hA0_even, hA0_lt, hA0_res⟩ := exists_base_even_of_classes (a := a) hRodd hRle (by omega)
  refine ⟨by omega, hQy6, A₀, U, hA0_even, hA0_lt,
    fun q hq => Finset.mem_range.mp (Finset.mem_filter.mp hq).1, hUr, ?_⟩
  intro N q hNmod hNbig hqQ hqnotU
  have hNeven : Even N := by
    have h2eq : N % 2 = A₀ % 2 := hNmod.of_dvd (Nat.prime_two.dvd_primorial_iff.mpr (by omega))
    have hA0mod : A₀ % 2 = 0 := Nat.even_iff.mp hA0_even
    exact Nat.even_iff.mpr (by omega)
  have hNres : ∀ r ∈ oddPrimesLE w, N ≡ a r [MOD r] := fun r hr =>
    (hNmod.of_dvd ((hRodd r hr).1.dvd_primorial_iff.mpr (hRle r hr))).trans (hA0_res r hr)
  by_cases hqp : q.Prime
  · by_cases hq2 : q = 2
    · exact not_isSummand_of_partial_cover hRodd hRle (by omega) hNres hNeven hNbig hqQ (Or.inl hq2)
    · have hcov : ∃ r ∈ oddPrimesLE w, q ≡ a r [MOD r] := by
        by_contra hno
        push Not at hno
        exact hqnotU (Finset.mem_filter.mpr ⟨Finset.mem_range.mpr hqQ, hqp, hq2, hno⟩)
      exact not_isSummand_of_partial_cover hRodd hRle (by omega) hNres hNeven hNbig hqQ (Or.inr hcov)
  · intro hsum
    exact hqp hsum.1

/-! ### Part D: Steps (iii) & (iv) — Disjoint-interval replication and Montgomery–Vaughan pigeonhole -/

/-- **Steps (iii)–(iv): Disjoint-interval CRT replication and pigeonhole subtraction.**
Given a pre-sieve base `A₀` and survivor set `U` at scale `y`, together with the simultaneous-root
property at `y`, if the number `J` of disjoint blocks of length `primorial y * sieveT y` inside
`(X / 2, X]` strictly exceeds `(goldbachExceptions X).card`, then at least one block yields a
genuine Goldbach integer `N ∈ [X / 2, X]` (`Even N ∧ ∃ p, IsSummand N p`) with no Goldbach summand
below `Qstar`. -/
theorem iterated_log_goldbach_of_disjoint_blocks
    {X y Qstar A₀ : ℕ} {U : Finset ℕ} {η : ℝ}
    (hX8 : 8 ≤ X) (hy2 : 2 ≤ y) (hQ : Qstar ≤ y ^ 6)
    (hQsieve : Qstar + sieveY (y : ℝ) < X / 2) (hQy : Qstar + y < X / 2)
    (hA0_even : Even A₀) (hA0_lt : A₀ < primorial y) (hM0_small : 2 * primorial y ≤ X / 4)
    (hUQ : ∀ q ∈ U, q < Qstar) (hUcard : (U.card : ℝ) ≤ η * (y : ℝ))
    (hpresieve : ∀ (N q : ℕ), N ≡ A₀ [MOD primorial y] → Qstar + y < N →
      q < Qstar → q ∉ U → ¬ IsSummand N q)
    (hSR_y : ∀ k : ℕ, ((k + 1 : ℕ) : ℝ) ≤ η * (y : ℝ) →
      ∀ root : (p : PrimeIndex (sieveP (y : ℝ))) → Fin (k + 1) → Fin p.val,
      (∀ p, Function.Injective (root p)) →
      ∃ n < sieveT (y : ℝ), ∀ i : Fin (k + 1), ∃ p : PrimeIndex (sieveP (y : ℝ)),
        residueVector (sieveP (y : ℝ)) n p = root p i)
    (hJ : (goldbachExceptions X).card <
      (X - (A₀ + primorial y * ((X / 2) / primorial y + 1))) / (primorial y * sieveT (y : ℝ))) :
    ∃ N : ℕ, X / 2 ≤ N ∧ N ≤ X ∧ Even N ∧ (∃ p : ℕ, IsSummand N p) ∧
      ∀ q < Qstar, ¬ IsSummand N q := by
  classical
  set M₀ := primorial y with hM₀def
  set T := sieveT (y : ℝ) with hTdef
  have hM₀pos : 0 < M₀ := primorial_pos y
  have hTpos : 0 < T := sieveT_pos_of_nonneg (Nat.cast_nonneg y)
  set B_start := A₀ + M₀ * ((X / 2) / M₀ + 1) with hBdef
  set J := (X - B_start) / (M₀ * T) with hJdef
  have hB_gt : X / 2 < B_start := by
    have h1 : X / 2 < M₀ * ((X / 2) / M₀ + 1) := Nat.lt_mul_div_succ (X / 2) hM₀pos
    omega
  have hB_le : B_start ≤ X := by
    have h1 : M₀ * ((X / 2) / M₀) ≤ X / 2 := Nat.mul_div_le (X / 2) M₀
    have h2 : M₀ * ((X / 2) / M₀ + 1) = M₀ * ((X / 2) / M₀) + M₀ := by ring
    omega
  -- Choose a survivor-killing translate in every block `j`
  let b : ℕ → ℕ := fun j => B_start + j * (M₀ * T)
  have hex_n : ∀ j : ℕ, ∃ n < T, ∀ q ∈ U, ¬ (b j + M₀ * (n + 1) - q).Prime := fun j =>
    iterated_log_translate_kill_survivors hy2 hQ (by simp only [b]; omega) hUQ hUcard hSR_y
  let n : ℕ → ℕ := fun j => Classical.choose (hex_n j)
  have hn_lt : ∀ j, n j < T := fun j => (Classical.choose_spec (hex_n j)).1
  have hn_kill : ∀ j, ∀ q ∈ U, ¬ (b j + M₀ * (n j + 1) - q).Prime :=
    fun j => (Classical.choose_spec (hex_n j)).2
  let cand : ℕ → ℕ := fun j => b j + M₀ * (n j + 1)
  have hM₀_even : Even M₀ := even_iff_two_dvd.mpr (Nat.prime_two.dvd_primorial_iff.mpr hy2)
  have hcand_eq : ∀ j, cand j = A₀ + M₀ * (((X / 2) / M₀ + 1) + j * T + (n j + 1)) := fun j => by
    simp only [cand, b, hBdef]
    ring
  have hcand_even : ∀ j, Even (cand j) := fun j => by
    rw [hcand_eq j]
    exact hA0_even.add (hM₀_even.mul_right _)
  have hcand_mod : ∀ j, cand j ≡ A₀ [MOD M₀] := fun j => by
    rw [hcand_eq j]
    show (A₀ + M₀ * _) % M₀ = A₀ % M₀
    rw [Nat.add_mul_mod_self_left]
  have hcand_mono : StrictMono cand := by
    intro j₁ j₂ hlt
    have hj : j₁ + 1 ≤ j₂ := hlt
    have hn1 : n j₁ + 1 ≤ T := hn_lt j₁
    have hstep1 : cand j₁ ≤ B_start + (j₁ + 1) * (M₀ * T) := by
      have hmul : M₀ * (n j₁ + 1) ≤ M₀ * T := Nat.mul_le_mul_left M₀ hn1
      have heq : B_start + j₁ * (M₀ * T) + M₀ * T = B_start + (j₁ + 1) * (M₀ * T) := by ring
      simp only [cand, b]
      omega
    have hstep2 : B_start + (j₁ + 1) * (M₀ * T) ≤ B_start + j₂ * (M₀ * T) :=
      Nat.add_le_add_left (Nat.mul_le_mul_right (M₀ * T) hj) B_start
    have hstep3 : 0 < M₀ * (n j₂ + 1) := Nat.mul_pos hM₀pos (Nat.succ_pos _)
    simp only [cand, b] at hstep1 ⊢
    omega
  have hcand_bounds : ∀ j < J, X / 2 ≤ cand j ∧ cand j ≤ X := by
    intro j hj
    have hlo : X / 2 ≤ cand j := by
      simp only [cand, b]
      omega
    have hhi : cand j ≤ X := by
      have hj1 : j + 1 ≤ J := hj
      have hn1 : n j + 1 ≤ T := hn_lt j
      have hmul1 : M₀ * (n j + 1) ≤ M₀ * T := Nat.mul_le_mul_left M₀ hn1
      have hmul2 : (j + 1) * (M₀ * T) ≤ J * (M₀ * T) := Nat.mul_le_mul_right (M₀ * T) hj1
      have hmul3 : J * (M₀ * T) ≤ X - B_start := by
        rw [mul_comm]
        exact Nat.mul_div_le (X - B_start) (M₀ * T)
      have heq : B_start + j * (M₀ * T) + M₀ * T = B_start + (j + 1) * (M₀ * T) := by ring
      simp only [cand, b]
      omega
    exact ⟨hlo, hhi⟩
  have hcand_desert : ∀ j, ∀ q < Qstar, ¬ IsSummand (cand j) q := by
    intro j q hqQ
    by_cases hqU : q ∈ U
    · intro hsum
      exact hn_kill j q hqU hsum.2
    · exact hpresieve (cand j) q (hcand_mod j) (by simp only [cand, b]; omega) hqQ hqU
  -- Pigeonhole against `goldbachExceptions X`
  set Cand := (Finset.range J).image cand
  have hCand_card : Cand.card = J := by
    rw [Finset.card_image_of_injective _ hcand_mono.injective, Finset.card_range]
  have hex_good : ∃ N ∈ Cand, ∃ p : ℕ, IsSummand N p := by
    by_contra hno
    push Not at hno
    have hsub : Cand ⊆ goldbachExceptions X := by
      intro N hN
      obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hN
      have hjJ : j < J := Finset.mem_range.mp hj
      obtain ⟨hlo, hhi⟩ := hcand_bounds j hjJ
      simp only [goldbachExceptions, Finset.mem_filter, Finset.mem_Icc]
      exact ⟨⟨by omega, hhi⟩, hcand_even j, fun ⟨p, hp⟩ => hno (cand j) hN p hp⟩
    have hle : J ≤ (goldbachExceptions X).card := hCand_card ▸ Finset.card_le_card hsub
    omega
  obtain ⟨N, hNCand, hgold⟩ := hex_good
  obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hNCand
  obtain ⟨hlo, hhi⟩ := hcand_bounds j (Finset.mem_range.mp hj)
  exact ⟨cand j, hlo, hhi, hcand_even j, hgold, hcand_desert j⟩

set_option maxHeartbeats 1200000 in
/-- **Headline iterated-log lower bound with Goldbach representation.**
Conditional on the explicit hypothesis parameters `SimultaneousRootsStatement` (from
`openai/LongGapsBetweenPrimes` `L3480-L3485`) and `MontgomeryVaughanStatement` (Montgomery–Vaughan
1975, `E(X) ≪ X^(1 - δ)`), there exists `c > 0` such that for all sufficiently large `X`, there is
an even integer `N ∈ [X / 2, X]` **having a Goldbach representation** (`∃ p, IsSummand N p`) and
no Goldbach summand below
`c · log X · (log log X)³ · log log log log X / (log log log X)²`. -/
theorem eventually_exists_goldbach_iterated_log
    (hSR : SimultaneousRootsStatement) (hMV : MontgomeryVaughanStatement) :
    ∃ c : ℝ, 0 < c ∧ ∀ᶠ X : ℕ in Filter.atTop,
      ∃ N : ℕ, X / 2 ≤ N ∧ N ≤ X ∧ Even N ∧ (∃ p : ℕ, IsSummand N p) ∧
        ∀ q : ℕ, (q : ℝ) <
          c * (Real.log (X : ℝ) * Real.log (Real.log (X : ℝ)) ^ 3 *
            Real.log (Real.log (Real.log (Real.log (X : ℝ)))) /
            Real.log (Real.log (Real.log (X : ℝ))) ^ 2) →
          ¬ IsSummand N q := by
  obtain ⟨η, hη, hSR_ev⟩ := hSR
  obtain ⟨δ, C_MV, hδ, hC_MV, hMV_ev⟩ := hMV
  set δ₁ := min δ (1 / 2)
  have hδ₁pos : 0 < δ₁ := lt_min hδ (by norm_num)
  have hδ₁leδ : δ₁ ≤ δ := min_le_left _ _
  have hδ₁lehalf : δ₁ ≤ 1 / 2 := min_le_right _ _
  set α := δ₁ / 5 with hαdef
  have hαpos : 0 < α := by positivity
  have hαle : α ≤ 1 / 10 := by linarith
  set c₁ := η / 1040
  have hc₁pos : 0 < c₁ := by positivity
  set c := c₁ * α / 64
  have hcpos : 0 < c := by positivity
  refine ⟨c, hcpos, ?_⟩
  have hcast : Tendsto (fun X : ℕ => (X : ℝ)) atTop atTop := tendsto_natCast_atTop_atTop
  have hL : Tendsto (fun X : ℕ => Real.log (X : ℝ)) atTop atTop :=
    Real.tendsto_log_atTop.comp hcast
  have hLL : Tendsto (fun X : ℕ => Real.log (Real.log (X : ℝ))) atTop atTop :=
    Real.tendsto_log_atTop.comp hL
  have hLLL : Tendsto (fun X : ℕ => Real.log (Real.log (Real.log (X : ℝ)))) atTop atTop :=
    Real.tendsto_log_atTop.comp hLL
  have hLLLL : Tendsto (fun X : ℕ => Real.log (Real.log (Real.log (Real.log (X : ℝ))))) atTop atTop :=
    Real.tendsto_log_atTop.comp hLLL
  have hy : Tendsto (fun X : ℕ => ⌊α * Real.log (X : ℝ)⌋₊) atTop atTop :=
    tendsto_nat_floor_atTop.comp (hL.const_mul_atTop hαpos)
  have ho6 := (Real.isLittleO_pow_log_id_atTop (n := 6)).def (show (0 : ℝ) < 1 / 8 by norm_num)
  set L_thr := max (max 20 (2 / α)) (max (1 / c) (200 * C_MV / (11 * δ₁)))
  set LL_thr := max 6 (2 * Real.log (2 / α))
  filter_upwards [hy.eventually (iterated_log_presieve_small_survivors hη),
    hy.eventually (tendsto_natCast_atTop_atTop.eventually hSR_ev),
    hy.eventually (eventually_primorial_le (show (0 : ℝ) < 1 / 4 by norm_num)),
    hMV_ev, hcast.eventually ho6,
    hL.eventually_ge_atTop L_thr, hLL.eventually_ge_atTop LL_thr,
    hLLL.eventually_ge_atTop 2, hLLLL.eventually_ge_atTop 2,
    eventually_ge_atTop 20] with
    X hpre hSR_y hpr hMV_X ho6_X hLbig hLLbig hLLL2 hLLLL2 hX20
  obtain ⟨hy2, hQy6, A₀, U, hA0_even, hA0_lt, hUQ, hUcard, hpresieve⟩ := hpre
  set L₁ := Real.log (X : ℝ) with hL1def
  set L₂ := Real.log L₁ with hL2def
  set L₃ := Real.log L₂ with hL3def
  set L₄ := Real.log L₃ with hL4def
  set y := ⌊α * L₁⌋₊ with hydef
  set Qstar := iteratedQ c₁ y with hQstardef
  have hXpos : (0 : ℝ) < X := by exact_mod_cast (by omega : 0 < X)
  have hX1r : (1 : ℝ) ≤ X := by exact_mod_cast (by omega : 1 ≤ X)
  have hL20 : 20 ≤ L₁ := ((le_max_left _ _).trans (le_max_left _ _)).trans hLbig
  have hLα : 2 / α ≤ L₁ := ((le_max_right _ _).trans (le_max_left _ _)).trans hLbig
  have hLc : 1 / c ≤ L₁ := ((le_max_left _ _).trans (le_max_right _ _)).trans hLbig
  have hLMV : 200 * C_MV / (11 * δ₁) ≤ L₁ := ((le_max_right _ _).trans (le_max_right _ _)).trans hLbig
  have hLL6 : 6 ≤ L₂ := (le_max_left _ _).trans hLLbig
  have hLLα : 2 * Real.log (2 / α) ≤ L₂ := (le_max_right _ _).trans hLLbig
  have hL1pos : 0 < L₁ := by linarith
  have hL2pos : 0 < L₂ := by linarith
  have hL3pos : 0 < L₃ := by linarith
  have hL4pos : 0 < L₄ := by linarith
  have hL3leL2 : L₃ ≤ L₂ := by linarith [Real.log_le_sub_one_of_pos hL2pos]
  -- Scale bounds for `y = ⌊α * L₁⌋` and its iterated logarithms
  have hyle : (y : ℝ) ≤ α * L₁ := Nat.floor_le (by positivity)
  have hyge : α / 2 * L₁ ≤ (y : ℝ) := by
    have h1 : α * L₁ - 1 < (y : ℝ) := Nat.sub_one_lt_floor (α * L₁)
    have h2 : 2 ≤ α * L₁ := by
      have := (div_le_iff₀ hαpos).mp hLα
      linarith
    linarith
  have hyleL1 : (y : ℝ) ≤ L₁ := by nlinarith
  have hypos : (0 : ℝ) < y := by positivity
  set ly := Real.log (y : ℝ)
  set lly := Real.log ly
  set llly := Real.log lly
  have hly_le : ly ≤ L₂ := Real.log_le_log hypos hyleL1
  have hly_ge : L₂ / 2 ≤ ly := by
    have h1 : Real.log (L₁ / (2 / α)) ≤ ly := by
      apply Real.log_le_log (by positivity)
      have heq : L₁ / (2 / α) = α / 2 * L₁ := by field_simp
      linarith
    rw [Real.log_div hL1pos.ne' (by positivity)] at h1
    linarith
  have hly3 : 3 ≤ ly := by linarith
  have hlly_le : lly ≤ L₃ := Real.log_le_log (by linarith) hly_le
  have hlly_ge : L₃ / 2 ≤ lly := by
    have h1 : Real.log (L₂ / 2) ≤ lly := Real.log_le_log (by positivity) hly_ge
    rw [Real.log_div hL2pos.ne' (by norm_num)] at h1
    have hlog2 : Real.log 2 ≤ 1 := by linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)]
    linarith
  have hlly1 : 1 ≤ lly := by linarith
  have hllly_ge : L₄ / 2 ≤ llly := by
    have h1 : Real.log (L₃ / 2) ≤ llly := Real.log_le_log (by positivity) hlly_ge
    rw [Real.log_div hL3pos.ne' (by norm_num)] at h1
    have hlog2 : Real.log 2 ≤ 1 := by linarith [Real.log_le_sub_one_of_pos (show (0 : ℝ) < 2 by norm_num)]
    linarith
  have hlypos : 0 < ly := by linarith
  have hllypos : 0 < lly := by linarith
  have hlllypos : 0 < llly := by linarith
  -- Compare target bound with `Qstar = iteratedQ c₁ y`
  set R := c₁ * (y : ℝ) * ly ^ 3 * llly / lly ^ 2
  set Target := c * (L₁ * L₂ ^ 3 * L₄ / L₃ ^ 2)
  have hTarget_le : Target + 1 ≤ R := by
    have hnum1 : (α / 2 * L₁) * (L₂ / 2) ^ 3 ≤ (y : ℝ) * ly ^ 3 :=
      mul_le_mul hyge (pow_le_pow_left₀ (by linarith) hly_ge 3) (by positivity) hypos.le
    have hnum : c₁ * ((α / 2 * L₁) * (L₂ / 2) ^ 3) * (L₄ / 2) ≤ c₁ * ((y : ℝ) * ly ^ 3) * llly :=
      mul_le_mul (mul_le_mul_of_nonneg_left hnum1 hc₁pos.le) hllly_ge (by positivity) (by positivity)
    have hden : lly ^ 2 ≤ L₃ ^ 2 := pow_le_pow_left₀ (by linarith) hlly_le 2
    have hdiv := div_le_div₀ (by positivity) hnum (by positivity : 0 < lly ^ 2) hden
    have heq2 : c₁ * ((α / 2 * L₁) * (L₂ / 2) ^ 3) * (L₄ / 2) / L₃ ^ 2 = 2 * Target := by
      simp only [Target, c]
      ring
    have heqR : c₁ * ((y : ℝ) * ly ^ 3) * llly / lly ^ 2 = R := by
      simp only [R]
      ring
    have h2T : 2 * Target ≤ R := by linarith
    have h1T : 1 ≤ Target := by
      have h1 : 1 ≤ c * L₁ := by
        have := (div_le_iff₀ hcpos).mp hLc
        linarith
      have h2 : L₃ ^ 2 ≤ L₂ ^ 3 := by
        have hsq : L₃ ^ 2 ≤ L₂ ^ 2 := pow_le_pow_left₀ (by linarith) hL3leL2 2
        have hcu : L₂ ^ 2 ≤ L₂ ^ 3 := pow_le_pow_right₀ (by linarith) (by norm_num)
        linarith
      have h3 : L₁ ≤ L₁ * L₂ ^ 3 * L₄ / L₃ ^ 2 := by
        rw [le_div_iff₀ (by positivity : 0 < L₃ ^ 2)]
        have hm1 : L₁ * L₃ ^ 2 ≤ L₁ * L₂ ^ 3 := mul_le_mul_of_nonneg_left h2 hL1pos.le
        have hm2 : (L₁ * L₂ ^ 3) * 1 ≤ (L₁ * L₂ ^ 3) * L₄ :=
          mul_le_mul_of_nonneg_left (by linarith) (by positivity)
        linarith
      have h4 : c * L₁ ≤ Target := by
        have := mul_le_mul_of_nonneg_left h3 hcpos.le
        simpa only [Target] using this
      linarith
    linarith
  -- Size bounds for `iterated_log_goldbach_of_disjoint_blocks`
  have hL6 : L₁ ^ 6 ≤ (X : ℝ) / 8 := by
    simp only [id, Real.norm_eq_abs] at ho6_X
    rw [abs_of_nonneg hXpos.le, abs_of_nonneg (by positivity : 0 ≤ L₁ ^ 6)] at ho6_X
    linarith
  have hQstar_le : (Qstar : ℝ) ≤ (X : ℝ) / 8 := by
    have h1 : (Qstar : ℝ) ≤ ((y ^ 6 : ℕ) : ℝ) := by exact_mod_cast hQy6
    have h2 : ((y ^ 6 : ℕ) : ℝ) ≤ L₁ ^ 6 := by
      push_cast
      exact pow_le_pow_left₀ hypos.le hyleL1 6
    linarith
  have hsieveY_le : (sieveY (y : ℝ) : ℝ) ≤ (X : ℝ) / 8 := by
    have h1 : (sieveY (y : ℝ) : ℝ) ≤ Real.exp (y : ℝ) := sieveY_le_exp (by linarith)
    have h2 : Real.exp (y : ℝ) ≤ Real.exp ((1 / 10) * L₁) :=
      Real.exp_le_exp.mpr (by nlinarith)
    have h3 : (8 : ℝ) ≤ Real.exp ((9 / 10) * L₁) := by
      linarith [Real.add_one_le_exp ((9 / 10) * L₁)]
    have hprod := mul_le_mul h3 h2 (Real.exp_pos _).le (Real.exp_pos _).le
    have hexpX : Real.exp ((9 / 10) * L₁) * Real.exp ((1 / 10) * L₁) = (X : ℝ) := by
      rw [← Real.exp_add, show (9 / 10) * L₁ + (1 / 10) * L₁ = L₁ by ring, hL1def, Real.exp_log hXpos]
    linarith
  have hQsieve : Qstar + sieveY (y : ℝ) < X / 2 := by
    have h1 : (4 : ℝ) * ((Qstar + sieveY (y : ℝ) : ℕ) : ℝ) ≤ (X : ℝ) := by
      push_cast
      linarith
    have h2 : 4 * (Qstar + sieveY (y : ℝ)) ≤ X := by exact_mod_cast h1
    omega
  have hQy : Qstar + y < X / 2 := by
    have hyX8 : (y : ℝ) ≤ (X : ℝ) / 8 := by
      have h1 : L₁ ≤ L₁ ^ 6 := le_self_pow₀ (by linarith) (by norm_num)
      linarith
    have h1 : (4 : ℝ) * ((Qstar + y : ℕ) : ℝ) ≤ (X : ℝ) := by
      push_cast
      linarith
    have h2 : 4 * (Qstar + y) ≤ X := by exact_mod_cast h1
    omega
  have hM0_small : 2 * primorial y ≤ X / 4 := by
    have h1 : (primorial y : ℝ) ≤ Real.exp ((1 / 8) * L₁) := by
      refine hpr.trans (Real.exp_le_exp.mpr ?_)
      nlinarith
    have h2 : (16 : ℝ) ≤ Real.exp ((7 / 8) * L₁) := by
      linarith [Real.add_one_le_exp ((7 / 8) * L₁)]
    have hprod := mul_le_mul h2 h1 (by positivity) (Real.exp_pos _).le
    have hexpX : Real.exp ((7 / 8) * L₁) * Real.exp ((1 / 8) * L₁) = (X : ℝ) := by
      rw [← Real.exp_add, show (7 / 8) * L₁ + (1 / 8) * L₁ = L₁ by ring, hL1def, Real.exp_log hXpos]
    have h16 : 16 * primorial y ≤ X := by
      have : (16 : ℝ) * (primorial y : ℝ) ≤ (X : ℝ) := by linarith
      exact_mod_cast this
    omega
  -- Disjoint block count beats `goldbachExceptions X`
  set M₀ := primorial y
  set T := sieveT (y : ℝ)
  set B_start := A₀ + M₀ * ((X / 2) / M₀ + 1)
  set J := (X - B_start) / (M₀ * T)
  have hJ : (goldbachExceptions X).card < J := by
    have hM₀pos : 0 < M₀ := primorial_pos y
    have hTpos : 0 < T := sieveT_pos_of_nonneg (Nat.cast_nonneg y)
    have hMTpos : (0 : ℝ) < ((M₀ * T : ℕ) : ℝ) := by exact_mod_cast Nat.mul_pos hM₀pos hTpos
    have hB_le : B_start ≤ X / 2 + X / 4 := by
      have h1 : M₀ * ((X / 2) / M₀) ≤ X / 2 := Nat.mul_div_le (X / 2) M₀
      have h2 : M₀ * ((X / 2) / M₀ + 1) = M₀ * ((X / 2) / M₀) + M₀ := by ring
      omega
    have hXsub : X / 4 ≤ X - B_start := by omega
    have hXsub_r : (X : ℝ) / 5 ≤ ((X - B_start : ℕ) : ℝ) := by
      have h1 : (X : ℝ) / 5 ≤ ((X / 4 : ℕ) : ℝ) := by
        have h4 : 5 * (X / 4) ≥ X := by omega
        have h4r : (X : ℝ) ≤ 5 * ((X / 4 : ℕ) : ℝ) := by exact_mod_cast h4
        linarith
      exact h1.trans (by exact_mod_cast hXsub)
    have hMT_le : ((M₀ * T : ℕ) : ℝ) ≤ Real.exp ((9 / 20) * δ₁ * L₁) := by
      have hTle : (T : ℝ) ≤ Real.exp (y : ℝ) := Nat.floor_le (Real.exp_pos _).le
      have hmul : (M₀ : ℝ) * (T : ℝ) ≤ Real.exp ((1 + 1 / 4) * (y : ℝ)) * Real.exp (y : ℝ) :=
        mul_le_mul hpr hTle (Nat.cast_nonneg T) (Real.exp_pos _).le
      rw [← Real.exp_add] at hmul
      push_cast
      refine hmul.trans (Real.exp_le_exp.mpr ?_)
      have h94 : (1 + 1 / 4) * (y : ℝ) + (y : ℝ) = (9 / 4) * (y : ℝ) := by ring
      have hαeq : (9 / 4) * (α * L₁) = (9 / 20) * δ₁ * L₁ := by
        simp only [α]
        ring
      linarith
    have hJgt : (1 / 5) * Real.exp ((1 - (9 / 20) * δ₁) * L₁) < (J : ℝ) + 1 := by
      have hdiv_lt : ((X - B_start : ℕ) : ℝ) / ((M₀ * T : ℕ) : ℝ) < (J : ℝ) + 1 := by
        rw [div_lt_iff₀ hMTpos]
        have hnat : X - B_start < (M₀ * T) * (J + 1) :=
          Nat.lt_mul_div_succ (X - B_start) (Nat.mul_pos hM₀pos hTpos)
        have hr : ((X - B_start : ℕ) : ℝ) < ((M₀ * T : ℕ) : ℝ) * ((J : ℝ) + 1) := by
          exact_mod_cast hnat
        linarith
      have hlo : (1 / 5) * Real.exp ((1 - (9 / 20) * δ₁) * L₁) ≤
          ((X - B_start : ℕ) : ℝ) / ((M₀ * T : ℕ) : ℝ) := by
        have h1 : ((X : ℝ) / 5) / Real.exp ((9 / 20) * δ₁ * L₁) ≤
            ((X - B_start : ℕ) : ℝ) / ((M₀ * T : ℕ) : ℝ) :=
          div_le_div₀ (by positivity) hXsub_r hMTpos hMT_le
        have h2 : ((X : ℝ) / 5) / Real.exp ((9 / 20) * δ₁ * L₁) =
            (1 / 5) * Real.exp ((1 - (9 / 20) * δ₁) * L₁) := by
          have hexpX : (X : ℝ) = Real.exp L₁ := (Real.exp_log hXpos).symm
          rw [hexpX, div_eq_mul_inv, div_eq_mul_inv, ← Real.exp_neg]
          calc Real.exp L₁ * 5⁻¹ * Real.exp (-((9 / 20) * δ₁ * L₁))
              = (1 / 5) * (Real.exp L₁ * Real.exp (-((9 / 20) * δ₁ * L₁))) := by ring
            _ = (1 / 5) * Real.exp (L₁ + -((9 / 20) * δ₁ * L₁)) := by rw [← Real.exp_add]
            _ = (1 / 5) * Real.exp ((1 - (9 / 20) * δ₁) * L₁) := by congr 2; ring
        linarith
      linarith
    have hMV_exp : ((goldbachExceptions X).card : ℝ) ≤ C_MV * Real.exp ((1 - δ₁) * L₁) := by
      have h1 : (X : ℝ) ^ (1 - δ) ≤ (X : ℝ) ^ (1 - δ₁) :=
        Real.rpow_le_rpow_of_exponent_le hX1r (by linarith)
      have h2 : (X : ℝ) ^ (1 - δ₁) = Real.exp ((1 - δ₁) * L₁) := by
        rw [Real.rpow_def_of_pos hXpos, hL1def, mul_comm]
      have h3 := mul_le_mul_of_nonneg_left h1 hC_MV.le
      rw [← h2]
      exact hMV_X.trans h3
    have hterm1 : C_MV * Real.exp ((1 - δ₁) * L₁) ≤
        (1 / 10) * Real.exp ((1 - (9 / 20) * δ₁) * L₁) := by
      have h10 : 10 * C_MV ≤ Real.exp ((11 / 20) * δ₁ * L₁) := by
        have hlin : 10 * C_MV ≤ (11 / 20) * δ₁ * L₁ := by
          have := (div_le_iff₀ (by positivity : 0 < 11 * δ₁)).mp hLMV
          linarith
        linarith [Real.add_one_le_exp ((11 / 20) * δ₁ * L₁)]
      have hmul := mul_le_mul_of_nonneg_right h10 (Real.exp_pos ((1 - δ₁) * L₁)).le
      rw [← Real.exp_add] at hmul
      have hexp : (11 / 20) * δ₁ * L₁ + (1 - δ₁) * L₁ = (1 - (9 / 20) * δ₁) * L₁ := by ring
      rw [hexp] at hmul
      linarith
    have hterm2 : (1 : ℝ) ≤ (1 / 10) * Real.exp ((1 - (9 / 20) * δ₁) * L₁) := by
      have h10 : (10 : ℝ) ≤ Real.exp ((1 - (9 / 20) * δ₁) * L₁) := by
        have hlin : (10 : ℝ) ≤ (1 - (9 / 20) * δ₁) * L₁ := by nlinarith
        linarith [Real.add_one_le_exp ((1 - (9 / 20) * δ₁) * L₁)]
      linarith
    have hlt_r : ((goldbachExceptions X).card : ℝ) < (J : ℝ) := by linarith
    exact_mod_cast hlt_r
  obtain ⟨N, hlo, hhi, heven, hgold, hdes⟩ :=
    iterated_log_goldbach_of_disjoint_blocks (by omega) hy2 hQy6 hQsieve hQy hA0_even hA0_lt
      hM0_small hUQ hUcard hpresieve hSR_y hJ
  refine ⟨N, hlo, hhi, heven, hgold, fun q hq => hdes q ?_⟩
  have hq1 : (q : ℝ) + 1 ≤ R := by linarith
  have hq2 : q + 1 ≤ Qstar := Nat.le_floor (by exact_mod_cast hq1)
  omega

/-- **Least-Goldbach-summand corollary of `eventually_exists_goldbach_iterated_log`.**
Under `SimultaneousRootsStatement` and `MontgomeryVaughanStatement`, there exists `c > 0` such
that for all sufficiently large `X`, there is an even `N ∈ [X / 2, X]` whose least Goldbach
summand `s` exists (`IsLeastSummand N s`) and satisfies
`s ≥ c · log X · (log log X)³ · log log log log X / (log log log X)²`. -/
theorem eventually_exists_isLeastSummand_iterated_log
    (hSR : SimultaneousRootsStatement) (hMV : MontgomeryVaughanStatement) :
    ∃ c : ℝ, 0 < c ∧ ∀ᶠ X : ℕ in Filter.atTop,
      ∃ N s : ℕ, X / 2 ≤ N ∧ N ≤ X ∧ Even N ∧ IsLeastSummand N s ∧
        c * (Real.log (X : ℝ) * Real.log (Real.log (X : ℝ)) ^ 3 *
          Real.log (Real.log (Real.log (Real.log (X : ℝ)))) /
          Real.log (Real.log (Real.log (X : ℝ))) ^ 2) ≤ (s : ℝ) := by
  classical
  obtain ⟨c, hcpos, hev⟩ := eventually_exists_goldbach_iterated_log hSR hMV
  refine ⟨c, hcpos, ?_⟩
  filter_upwards [hev] with X ⟨N, hlo, hhi, heven, hgold, hno⟩
  refine ⟨N, Nat.find hgold, hlo, hhi, heven,
    ⟨Nat.find_spec hgold, fun p hp => Nat.find_min' hgold hp⟩, ?_⟩
  exact le_of_not_gt fun hlt => hno (Nat.find hgold) hlt (Nat.find_spec hgold)

end GoldbachGaps
