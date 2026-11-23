import GoldbachGaps.Basic

/-!
# An effective form of "every odd prime is a least Goldbach summand"

`Basic.exists_isLeastSummand` uses Dirichlet's theorem: for an odd prime `s` there are
arbitrarily large even `N` with `g(N) = s`. It gives no bound on the smallest such `N`.
Linnik's theorem (the least prime `p ≡ a (mod q)` is at most `C q^L`) gives one:

  some even `N ≤ C · (primorial (s - 1))^L + s` has `g(N) = s`,

and so, with `primorial n ≤ 4^n`, some even `N ≤ C · 4^(L (s - 1)) + s`.

Linnik's theorem is not in Mathlib. It is taken here as a hypothesis, `LinnikStatement`,
which mentions only Mathlib notions. A kernel-checked proof of exactly this statement exists
in the Lean archive linked from `https://alpo.ge/remark.pdf` (theorem `UpperTheory.Lit.linnik`
with `GlobalTheory.Published.linnik_iff_exists_prime`; Lean 4.33.1, Mathlib `0df444a`): its
517 files were compiled on 2026-11-23 and depend on `propext`, `Classical.choice` and
`Quot.sound` only. That archive is not a dependency of this library.

The bound is far from what the search finds (`g = 157837` at 200 digits, against a bound
with tens of thousands of digits for that `s`); its interest is that it is a theorem.
-/

namespace GoldbachGaps

/-- Linnik's theorem: there are `C, L > 0` such that every reduced class `a` modulo `q`
contains a prime `p ≤ C q^L`. -/
def LinnikStatement : Prop :=
  ∃ C L : ℝ, 0 < C ∧ 0 < L ∧ ∀ a q : ℕ, 1 ≤ a → 1 ≤ q → a.Coprime q →
    ∃ p : ℕ, p.Prime ∧ p ≡ a [MOD q] ∧ (p : ℝ) ≤ C * (q : ℝ) ^ L

/-- **Effective form of paper Theorem `thm:dirichlet`.** Under Linnik's theorem, with its
constants `C`, `L`: every odd prime `s` is the least Goldbach summand of an even
`N ≤ C · (primorial (s - 1))^L + s`. -/
theorem exists_isLeastSummand_le_of_linnik (h : LinnikStatement) :
    ∃ C L : ℝ, 0 < C ∧ 0 < L ∧ ∀ s : ℕ, s.Prime → s ≠ 2 →
      ∃ N : ℕ, Even N ∧ IsLeastSummand N s ∧
        (N : ℝ) ≤ C * (primorial (s - 1) : ℝ) ^ L + s := by
  obtain ⟨C, L, hC, hL, hlin⟩ := h
  refine ⟨C, L, hC, hL, fun s hs hs2 => ?_⟩
  have hs3 : 3 ≤ s := by
    have := hs.two_le
    omega
  set M := primorial (s - 1) with hM
  have hMpos : 0 < M := primorial_pos _
  have h2M : 2 ∣ M := by
    rw [hM, Nat.prime_two.dvd_primorial_iff]
    omega
  have hcop : s.Coprime M := by
    rw [hs.coprime_iff_not_dvd, hM, hs.dvd_primorial_iff]
    omega
  have hM2 : 2 ≤ M := Nat.le_of_dvd hMpos h2M
  -- the class of `-s` modulo `M`, as a positive number coprime to `M`
  have h1 : Nat.Coprime (M - 1) M := by
    have h := (Nat.coprime_self_add_right (m := M - 1) (n := 1)).mpr (Nat.coprime_one_right _)
    rwa [Nat.sub_add_cancel (by omega : 1 ≤ M)] at h
  have hacop : (s * (M - 1)).Coprime M := Nat.coprime_mul_iff_left.mpr ⟨hcop, h1⟩
  have hapos : 1 ≤ s * (M - 1) := Nat.mul_pos (by omega) (by omega)
  obtain ⟨t, ht, htmod, htle⟩ := hlin (s * (M - 1)) M hapos hMpos hacop
  -- `M ∣ s + t`
  have e : s + s * (M - 1) = s * M := by
    have h2 := Nat.le_mul_of_pos_right s hMpos
    rw [Nat.mul_sub_one]
    omega
  have hmod : (s + t) % M = 0 := by
    have h := Nat.ModEq.add_left s htmod
    rw [e] at h
    rw [h]
    exact Nat.mul_mod_left s M
  have hMN : M ∣ s + t := Nat.dvd_of_mod_eq_zero hmod
  -- `t` is not one of the primes below `s`: such a prime divides `M`, hence `s + t`, hence `s`
  have htbig : s - 1 < t := by
    by_contra hcon
    have htM : t ∣ M := by
      rw [hM]
      exact ht.dvd_primorial_iff.mpr (by omega)
    have hts : t ∣ s := by
      have h3 : t ∣ s + t - t := Nat.dvd_sub (htM.trans hMN) (dvd_refl t)
      rwa [Nat.add_sub_cancel] at h3
    have := (Nat.prime_dvd_prime_iff_eq ht hs).mp hts
    omega
  refine ⟨s + t, even_iff_two_dvd.mpr (h2M.trans hMN), ⟨⟨hs, ?_⟩, ?_⟩, ?_⟩
  · rwa [Nat.add_sub_cancel_left]
  · intro p hp
    by_contra hlt
    exact not_isSummand_of_primorial_dvd hMN (by omega) (by omega) hp
  · push_cast
    linarith

/-- The same with `primorial n ≤ 4^n`: some even `N ≤ C · (4^(s - 1))^L + s` has `g(N) = s`.
In particular `g(N) ≥ c · log N` for these `N`, with an absolute `c > 0`. -/
theorem exists_isLeastSummand_le_four_pow_of_linnik (h : LinnikStatement) :
    ∃ C L : ℝ, 0 < C ∧ 0 < L ∧ ∀ s : ℕ, s.Prime → s ≠ 2 →
      ∃ N : ℕ, Even N ∧ IsLeastSummand N s ∧ (N : ℝ) ≤ C * ((4 : ℝ) ^ (s - 1)) ^ L + s := by
  obtain ⟨C, L, hC, hL, hall⟩ := exists_isLeastSummand_le_of_linnik h
  refine ⟨C, L, hC, hL, fun s hs hs2 => ?_⟩
  obtain ⟨N, hNe, hN, hle⟩ := hall s hs hs2
  refine ⟨N, hNe, hN, hle.trans ?_⟩
  have h4 : (primorial (s - 1) : ℝ) ≤ (4 : ℝ) ^ (s - 1) := by
    exact_mod_cast primorial_le_four_pow (s - 1)
  have hpow : (primorial (s - 1) : ℝ) ^ L ≤ ((4 : ℝ) ^ (s - 1)) ^ L :=
    Real.rpow_le_rpow (Nat.cast_nonneg _) h4 hL.le
  have := mul_le_mul_of_nonneg_left hpow hC.le
  linarith

end GoldbachGaps
