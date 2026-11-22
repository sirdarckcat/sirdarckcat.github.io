import Mathlib

/-!
# Least Goldbach summands: definitions and the unboundedness theorem

Formalises Section 3 of `slop/goldbach/paper.tex` ("Primorial deserts, made
unconditional"): Lemma `lem:primcore` and Theorem `thm:dirichlet`.
-/

namespace GoldbachGaps

/-- `p` is a Goldbach summand of `N`: both `p` and `N - p` are prime.
(Truncated subtraction is harmless here: `N - p` prime forces `p + 2 ≤ N`.) -/
def IsSummand (N p : ℕ) : Prop := p.Prime ∧ (N - p).Prime

/-- `s` is the least Goldbach summand of `N`, the paper's `g(N) = s`. -/
def IsLeastSummand (N s : ℕ) : Prop := IsSummand N s ∧ ∀ p, IsSummand N p → s ≤ p

theorem IsSummand.add_two_le {N p : ℕ} (h : IsSummand N p) : p + 2 ≤ N := by
  have := h.2.two_le
  omega

/-- Paper Lemma `lem:primcore` (primorial core): if the primorial of `P` divides `N`
and `N > 2P`, then no prime `≤ P` is a Goldbach summand of `N`. -/
theorem not_isSummand_of_primorial_dvd {N P p : ℕ} (hN : primorial P ∣ N) (hbig : 2 * P < N)
    (hpP : p ≤ P) : ¬ IsSummand N p := by
  rintro ⟨hp, hq⟩
  have hpN : p ∣ N := (hp.dvd_primorial_iff.mpr hpP).trans hN
  have hdiv : p ∣ N - p := Nat.dvd_sub hpN dvd_rfl
  have heq : p = N - p := (Nat.prime_dvd_prime_iff_eq hp hq).mp hdiv
  have := hq.two_le
  omega

/-- Paper Theorem `thm:dirichlet`, in its sharp form: every odd prime `s` is the least
Goldbach summand of arbitrarily large even numbers. The proof is the paper's:
Dirichlet's theorem gives a prime `t ≡ -s` modulo the primorial of `s - 1`,
and `N = s + t` works. -/
theorem exists_isLeastSummand {s : ℕ} (hs : s.Prime) (hs2 : s ≠ 2) (n : ℕ) :
    ∃ N > n, Even N ∧ IsLeastSummand N s := by
  have hs3 : 3 ≤ s := by
    have := hs.two_le
    omega
  set M := primorial (s - 1) with hM
  have hM0 : M ≠ 0 := primorial_ne_zero _
  have : NeZero M := ⟨hM0⟩
  have hcop : s.Coprime M := by
    rw [hs.coprime_iff_not_dvd, hM, hs.dvd_primorial_iff]
    omega
  have hunit : IsUnit (-(s : ZMod M)) := ((ZMod.isUnit_iff_coprime s M).mpr hcop).neg
  obtain ⟨t, htbig, ht, htmod⟩ := Nat.forall_exists_prime_gt_and_eq_mod hunit (n + s)
  have hMN : M ∣ s + t := by
    rw [← ZMod.natCast_eq_zero_iff]
    push_cast
    rw [htmod]
    ring
  have h2M : 2 ∣ M := by
    rw [hM, Nat.prime_two.dvd_primorial_iff]
    omega
  refine ⟨s + t, by omega, even_iff_two_dvd.mpr (h2M.trans hMN), ⟨hs, ?_⟩, ?_⟩
  · rwa [Nat.add_sub_cancel_left]
  · intro p hp
    by_contra hlt
    exact not_isSummand_of_primorial_dvd hMN (by omega) (by omega) hp

/-- The least Goldbach summand is unbounded: for every bound `B` there is an even `N`
that has a Goldbach partition, all of whose Goldbach summands exceed `B`. -/
theorem least_summand_unbounded (B : ℕ) :
    ∃ N s, Even N ∧ IsLeastSummand N s ∧ B < s := by
  obtain ⟨s, hsB, hs⟩ := Nat.exists_infinite_primes (B + 3)
  obtain ⟨N, -, hNeven, hN⟩ := exists_isLeastSummand hs (by omega) 0
  exact ⟨N, s, hNeven, hN, by omega⟩

end GoldbachGaps
