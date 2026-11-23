import GoldbachGaps.Desert

/-!
# Complete covers: least Goldbach summands bounded below by divisibility alone

A *complete cover* of the rows below `Q` for an even `N`: every prime `q < Q` has `N - q`
divisible by one of finitely many moduli `r` (each with `r + Q < N`, so that `r` is a proper
divisor). Then no prime below `Q` is a Goldbach summand of `N`, and the proof involves no
primality or compositeness test, only divisions.

The certificate is the block test of `Desert.lean` with an empty list of residuals:
`covered_of_desertBlockCheck_nil` reads it as divisibility, `CoveredIn.noSummandIn` passes to
Goldbach summands, and `CoveredIn.add_mul` extends a cover of `N` to every `N + t M`, `M` the
product of the moduli. Generated instances (`scripts/gen_cover.py`) live in their own files.
-/

namespace GoldbachGaps

/-- Every prime `q` with `a ≤ q < b` has `N - q` divisible by a modulus of the list. -/
def CoveredIn (N : ℕ) (coverMods : List ℕ) (a b : ℕ) : Prop :=
  ∀ q, a ≤ q → q < b → q.Prime → ∃ r ∈ coverMods, r ∣ N - q

theorem CoveredIn.append {N a b c : ℕ} {coverMods : List ℕ} (h₁ : CoveredIn N coverMods a b)
    (h₂ : CoveredIn N coverMods b c) : CoveredIn N coverMods a c := fun q ha hc hq =>
  if h : q < b then h₁ q ha h hq else h₂ q (not_lt.mp h) hc hq

/-- A block test with no residuals certifies that the block is covered. -/
theorem covered_of_desertBlockCheck_nil {N g lo len : ℕ} {coverMods smallPrimes : List ℕ}
    (hlists : desertListsCheck N g coverMods smallPrimes = true)
    (h : desertBlockCheck N lo len coverMods smallPrimes [] = true) :
    CoveredIn N coverMods lo (lo + len) := by
  simp only [desertListsCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hlists
  obtain ⟨⟨-, hsmall⟩, -⟩ := hlists
  simp only [desertBlockCheck, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at h
  obtain ⟨hres, -⟩ := h
  intro q hlo hhi hqp
  have hq2 := hqp.two_le
  have hnodiv : (smallPrimes.any fun d => decide (d < q) && q % d == 0) = false := by
    rw [Bool.eq_false_iff]
    intro hany
    obtain ⟨d, hd, hdq⟩ := List.any_eq_true.mp hany
    simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hdq
    have hd2 := hsmall d hd
    rcases (Nat.dvd_prime hqp).mp (Nat.dvd_of_mod_eq_zero hdq.2) with h1 | h1 <;> omega
  by_contra hcon
  have hcov : (coverMods.any fun r => (N - q) % r == 0) = false := by
    rw [Bool.eq_false_iff]
    intro hany
    obtain ⟨r, hr, hrq⟩ := List.any_eq_true.mp hany
    exact hcon ⟨r, hr, Nat.dvd_of_mod_eq_zero (beq_iff_eq.mp hrq)⟩
  have hmem : q ∈ ([] : List ℕ) := by
    rw [← hres, List.mem_filter]
    refine ⟨List.mem_range'_1.mpr ⟨hlo, hhi⟩, ?_⟩
    simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true']
    exact ⟨⟨hq2, hnodiv⟩, hcov⟩
  exact absurd hmem (List.not_mem_nil)

/-- A covered range has no Goldbach summand: each `N - q` has the proper divisor `r`. -/
theorem CoveredIn.noSummandIn {N g a b : ℕ} {coverMods smallPrimes : List ℕ}
    (hlists : desertListsCheck N g coverMods smallPrimes = true)
    (h : CoveredIn N coverMods a b) (hb : b ≤ g) : NoSummandIn N a b := by
  simp only [desertListsCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hlists
  obtain ⟨-, hcover⟩ := hlists
  rintro q ha hb' ⟨hqp, hNq⟩
  obtain ⟨r, hr, hrq⟩ := h q ha hb' hqp
  have hr2 := hcover r hr
  rcases (Nat.dvd_prime hNq).mp hrq with h1 | h1 <;> omega

/-- A covered range has no Goldbach summand, with the side conditions stated directly: every
modulus is at least `2` and `r + b < N`. -/
theorem CoveredIn.noSummandIn_of_lt {N a b : ℕ} {coverMods : List ℕ}
    (h : CoveredIn N coverMods a b) (hmods : ∀ r ∈ coverMods, 2 ≤ r ∧ r + b < N) :
    NoSummandIn N a b := by
  rintro q ha hb ⟨hqp, hNq⟩
  obtain ⟨r, hr, hrq⟩ := h q ha hb hqp
  have hr2 := hmods r hr
  rcases (Nat.dvd_prime hNq).mp hrq with h1 | h1 <;> omega

/-- **The whole progression is covered.** If `N` is covered below `b ≤ N`, so is `N + t M` for
every `t`, `M` the product of the moduli: the divisor of `N - q` also divides `N + t M - q`. -/
theorem CoveredIn.add_mul {N a b : ℕ} {coverMods : List ℕ} (h : CoveredIn N coverMods a b)
    (hb : b ≤ N) (t : ℕ) : CoveredIn (N + t * coverMods.prod) coverMods a b := by
  intro q ha hq hqp
  obtain ⟨r, hr, hrq⟩ := h q ha hq hqp
  refine ⟨r, hr, ?_⟩
  have e : N + t * coverMods.prod - q = (N - q) + t * coverMods.prod := by omega
  rw [e]
  exact dvd_add hrq (Dvd.dvd.mul_left (List.dvd_prod hr) t)

end GoldbachGaps
