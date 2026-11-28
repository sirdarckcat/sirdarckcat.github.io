import GoldbachGaps.Basic

/-!
# Covering systems force large least Goldbach summands

Formalises Section 4 of `slop/goldbach/paper.tex`: Proposition `prop:cover`
(the covering certificate) and Theorem `thm:coverdirichlet` (every covering is
realised by an even number that actually has a Goldbach partition).
-/

namespace GoldbachGaps

/-- Paper Proposition `prop:cover` (covering certificate). If every odd prime `q < Q`
lies in the class `a r` modulo some `r ∈ R`, and `N` is an even number in all of those
classes that is larger than `Q + r` for every `r ∈ R`, then no prime below `Q` is a
Goldbach summand of `N`. (The moduli need not even be prime for this direction.) -/
theorem not_isSummand_of_cover {R : Finset ℕ} {a : ℕ → ℕ} {N Q : ℕ}
    (hR : ∀ r ∈ R, 2 ≤ r)
    (hcover : ∀ q, q.Prime → q ≠ 2 → q < Q → ∃ r ∈ R, q ≡ a r [MOD r])
    (hN : ∀ r ∈ R, N ≡ a r [MOD r]) (heven : Even N)
    (hbig : ∀ r ∈ R, Q + r < N) (hbig2 : Q + 2 < N)
    {q : ℕ} (hqQ : q < Q) : ¬ IsSummand N q := by
  rintro ⟨hq, hNq⟩
  by_cases hq2 : q = 2
  · subst hq2
    have h2 : 2 ∣ N - 2 := Nat.dvd_sub (even_iff_two_dvd.mp heven) dvd_rfl
    have := (Nat.prime_dvd_prime_iff_eq Nat.prime_two hNq).mp h2
    omega
  · obtain ⟨r, hr, hqr⟩ := hcover q hq hq2 hqQ
    have hle : q ≤ N := by
      have := hbig r hr
      omega
    have hdvd : r ∣ N - q := (Nat.modEq_iff_dvd' hle).mp (hqr.trans (hN r hr).symm)
    rcases (Nat.dvd_prime hNq).mp hdvd with h1 | h1
    · have := hR r hr
      omega
    · have := hbig r hr
      omega

/-- Paper Theorem `thm:coverdirichlet` (unconditional realisation). Any covering of the
odd primes below `Q` by classes modulo distinct odd primes is realised by arbitrarily
large even numbers `N` that have a Goldbach partition; for each of them the least
Goldbach summand `g` exists and satisfies `Q ≤ g`. The proof applies Dirichlet's theorem
twice, as in the paper. -/
theorem exists_isLeastSummand_of_cover {R : Finset ℕ} {a : ℕ → ℕ} {Q : ℕ}
    (hR : ∀ r ∈ R, r.Prime ∧ r ≠ 2)
    (hcover : ∀ q, q.Prime → q ≠ 2 → q < Q → ∃ r ∈ R, q ≡ a r [MOD r]) (n : ℕ) :
    ∃ N > n, Even N ∧ (∀ r ∈ R, N ≡ a r [MOD r]) ∧ ∃ g, IsLeastSummand N g ∧ Q ≤ g := by
  classical
  have hr3 : ∀ r ∈ R, 3 ≤ r := fun r hr => by
    have h1 := (hR r hr).1.two_le
    have h2 := (hR r hr).2
    omega
  set M := ∏ r ∈ R, r with hM
  have hM0 : M ≠ 0 := Finset.prod_ne_zero_iff.mpr fun r hr => by
    have := hr3 r hr
    omega
  have hrM : ∀ r ∈ R, r ∣ M := fun r hr => Finset.dvd_prod_of_mem (fun r => r) hr
  have hpp : Set.Pairwise (R : Set ℕ) (Function.onFun Nat.Coprime fun r : ℕ => r) :=
    fun r hr r' hr' hne => (Nat.coprime_primes (hR r hr).1 (hR r' hr').1).mpr hne
  have hs0 : ∀ r ∈ R, (fun r : ℕ => r) r ≠ 0 := fun r hr => by
    have := hr3 r hr
    show r ≠ 0
    omega
  -- anything congruent to a nonzero class modulo every `r ∈ R` is coprime to `M`
  have hcop : ∀ (f : ℕ → ℕ) (x : ℕ), (∀ r ∈ R, x ≡ f r [MOD r]) → (∀ r ∈ R, ¬ r ∣ f r) →
      x.Coprime M := by
    intro f x hx hf
    rw [hM, Nat.coprime_prod_right_iff]
    intro r hr
    refine (((hR r hr).1.coprime_iff_not_dvd).mpr fun hdvd => hf r hr ?_).symm
    exact Nat.modEq_zero_iff_dvd.mp ((hx r hr).symm.trans (Nat.modEq_zero_iff_dvd.mpr hdvd))
  -- Step 1: a prime `s` avoiding the classes `0` and `a r` modulo every `r ∈ R`
  let b : ℕ → ℕ := fun r => if a r % r = 1 then 2 else 1
  have hb0 : ∀ r ∈ R, ¬ r ∣ b r := fun r hr hdvd => by
    have h3 := hr3 r hr
    have hle : r ≤ b r := Nat.le_of_dvd (by simp only [b]; split_ifs <;> norm_num) hdvd
    have : b r ≤ 2 := by simp only [b]; split_ifs <;> norm_num
    omega
  have hba : ∀ r ∈ R, ¬ b r ≡ a r [MOD r] := fun r hr h => by
    have h3 := hr3 r hr
    unfold Nat.ModEq at h
    simp only [b] at h
    split_ifs at h with h1
    · rw [Nat.mod_eq_of_lt (by omega)] at h
      omega
    · rw [Nat.mod_eq_of_lt (by omega)] at h
      omega
  obtain ⟨b₀, hb₀⟩ := Nat.chineseRemainderOfFinset b (fun r => r) R hs0 hpp
  obtain ⟨s, hsbig, hs, hsmod⟩ :=
    Nat.forall_exists_prime_gt_and_modEq 2 hM0 (hcop b b₀ hb₀ hb0)
  have hs_r : ∀ r ∈ R, s ≡ b r [MOD r] := fun r hr =>
    (Nat.ModEq.of_dvd (hrM r hr) hsmod).trans (hb₀ r hr)
  -- Step 2: a prime `t` with `s + t ≡ a r` modulo every `r ∈ R`
  let c : ℕ → ℕ := fun r => a r + (r - 1) * s
  have hc_sum : ∀ r ∈ R, s + c r ≡ a r [MOD r] := fun r hr => by
    have h3 := hr3 r hr
    have hrs : (r - 1) * s + s = r * s := by
      rw [← Nat.succ_mul, Nat.succ_eq_add_one, Nat.sub_add_cancel (by omega)]
    have : s + c r = a r + r * s := by
      simp only [c]
      omega
    show (s + c r) % r = a r % r
    rw [this, Nat.add_mul_mod_self_left]
  have hc0 : ∀ r ∈ R, ¬ r ∣ c r := fun r hr hdvd => by
    have h1 : s + c r ≡ s + 0 [MOD r] :=
      (Nat.ModEq.refl s).add (Nat.modEq_zero_iff_dvd.mpr hdvd)
    rw [add_zero] at h1
    exact hba r hr ((hs_r r hr).symm.trans (h1.symm.trans (hc_sum r hr)))
  obtain ⟨c₀, hc₀⟩ := Nat.chineseRemainderOfFinset c (fun r => r) R hs0 hpp
  obtain ⟨t, htbig, ht, htmod⟩ :=
    Nat.forall_exists_prime_gt_and_modEq (n + Q + M + 2) hM0 (hcop c c₀ hc₀ hc0)
  -- Step 3: `N = s + t`
  have hNmod : ∀ r ∈ R, s + t ≡ a r [MOD r] := fun r hr =>
    ((Nat.ModEq.refl s).add ((Nat.ModEq.of_dvd (hrM r hr) htmod).trans (hc₀ r hr))).trans
      (hc_sum r hr)
  have heven : Even (s + t) :=
    (hs.odd_of_ne_two (by omega)).add_odd (ht.odd_of_ne_two (by omega))
  have hsum : IsSummand (s + t) s := ⟨hs, by rwa [Nat.add_sub_cancel_left]⟩
  have hex : ∃ p, IsSummand (s + t) p := ⟨s, hsum⟩
  refine ⟨s + t, by omega, heven, hNmod, Nat.find hex,
    ⟨Nat.find_spec hex, fun p hp => Nat.find_min' hex hp⟩, ?_⟩
  by_contra hlt
  refine not_isSummand_of_cover (fun r hr => by have := hr3 r hr; omega) hcover hNmod heven
    (fun r hr => ?_) (by omega) (not_le.mp hlt) (Nat.find_spec hex)
  have := Nat.le_of_dvd (Nat.pos_of_ne_zero hM0) (hrM r hr)
  omega

end GoldbachGaps
