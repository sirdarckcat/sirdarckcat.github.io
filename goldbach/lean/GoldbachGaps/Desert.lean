import GoldbachGaps.Basic

/-!
# Kernel-checkable certificates that no prime in a range is a Goldbach summand of `N`

This is the "negative side" of a record in `goldbach/records/`: every prime `q < g` must
have `N - q` composite. The range `[0, g)` is cut into blocks, and each block is certified
by a Boolean test `desertBlockCheck` that the kernel evaluates (one block per theorem, so
that the kernel's memory use stays bounded).

A block test walks over all `q` in the block and discards
* `q < 2` and every `q` with a proper divisor in `smallPrimes` (so `q` is not prime);
* every `q` for which some modulus in `coverMods` divides `N - q` (the covering system).
What is left must be exactly the list `residuals`, and for each of those `N - q` must fail
the base-2 Fermat test. None of the lists is trusted: a wrong list makes a test return
`false`; it cannot make it return `true` for a false statement.
-/

namespace GoldbachGaps

open Mathlib.Tactic.Primality (powMod powMod_def)

/-- No `q` with `a ≤ q < b` is a Goldbach summand of `N`. -/
def NoSummandIn (N a b : ℕ) : Prop := ∀ q, a ≤ q → q < b → ¬ IsSummand N q

theorem NoSummandIn.append {N a b c : ℕ} (h₁ : NoSummandIn N a b) (h₂ : NoSummandIn N b c) :
    NoSummandIn N a c := fun q ha hc =>
  if h : q < b then h₁ q ha h else h₂ q (not_lt.mp h) hc

/-- Side conditions on the lists, checked once per record: the trial divisors and the
covering moduli are at least `2`, and `N` exceeds `g` by more than every modulus. -/
def desertListsCheck (N g : ℕ) (coverMods smallPrimes : List ℕ) : Bool :=
  decide (g + 2 < N) &&
  smallPrimes.all (fun d => decide (2 ≤ d)) &&
  coverMods.all (fun r => decide (2 ≤ r) && decide (r + g < N))

/-- The certificate check for the block `lo ≤ q < lo + len`. -/
def desertBlockCheck (N lo len : ℕ) (coverMods smallPrimes residuals : List ℕ) : Bool :=
  ((List.range' lo len).filter fun q =>
      decide (2 ≤ q) && !(smallPrimes.any fun d => decide (d < q) && q % d == 0) &&
        !(coverMods.any fun r => (N - q) % r == 0)) == residuals &&
  residuals.all fun q => powMod 2 (N - q - 1) (N - q) != 1

/-- A number that fails the base-2 Fermat test is not an odd prime. -/
theorem not_prime_of_powMod_ne_one {m : ℕ} (hm : 2 < m) (h : powMod 2 (m - 1) m ≠ 1) :
    ¬ m.Prime := by
  intro hp
  apply h
  have hcop : Nat.Coprime 2 m := (Nat.coprime_primes Nat.prime_two hp).mpr (by omega)
  have := Nat.ModEq.pow_totient hcop
  rw [Nat.totient_prime hp] at this
  rw [powMod_def]
  exact Eq.trans this (Nat.mod_eq_of_lt (by omega))

/-- Soundness of `desertBlockCheck`. -/
theorem noSummandIn_of_desertBlockCheck {N g lo len : ℕ}
    {coverMods smallPrimes residuals : List ℕ}
    (hlists : desertListsCheck N g coverMods smallPrimes = true)
    (h : desertBlockCheck N lo len coverMods smallPrimes residuals = true)
    (hg : lo + len ≤ g) : NoSummandIn N lo (lo + len) := by
  simp only [desertListsCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hlists
  obtain ⟨⟨hN, hsmall⟩, hcover⟩ := hlists
  simp only [desertBlockCheck, Bool.and_eq_true, List.all_eq_true, beq_iff_eq, bne_iff_ne] at h
  obtain ⟨hres, hfermat⟩ := h
  rintro q hlo hhi ⟨hqp, hNq⟩
  have hq2 := hqp.two_le
  -- a prime has no proper divisor among `smallPrimes`
  have hnodiv : (smallPrimes.any fun d => decide (d < q) && q % d == 0) = false := by
    rw [Bool.eq_false_iff]
    intro hany
    obtain ⟨d, hd, hdq⟩ := List.any_eq_true.mp hany
    simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hdq
    have hd2 := hsmall d hd
    rcases (Nat.dvd_prime hqp).mp (Nat.dvd_of_mod_eq_zero hdq.2) with h1 | h1 <;> omega
  by_cases hcov : (coverMods.any fun r => (N - q) % r == 0) = true
  · -- killed by a covering modulus
    obtain ⟨r, hr, hrq⟩ := List.any_eq_true.mp hcov
    have hr2 := hcover r hr
    rcases (Nat.dvd_prime hNq).mp (Nat.dvd_of_mod_eq_zero (beq_iff_eq.mp hrq)) with h1 | h1 <;>
      omega
  · -- a residual: `N - q` fails the Fermat test
    have hmem : q ∈ residuals := by
      rw [← hres, List.mem_filter]
      refine ⟨List.mem_range'_1.mpr ⟨hlo, hhi⟩, ?_⟩
      simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true']
      exact ⟨⟨hq2, hnodiv⟩, by simpa using hcov⟩
    exact not_prime_of_powMod_ne_one (by omega) (hfermat q hmem) hNq

/-- A complete certificate for `g(N) = g`: the negative side by block checks, the positive
side by the primality of `g` and of the complement `N - g`. -/
theorem isLeastSummand_of_noSummandIn {N g : ℕ} (h : NoSummandIn N 0 g) (hg : g.Prime)
    (hc : (N - g).Prime) : IsLeastSummand N g :=
  ⟨⟨hg, hc⟩, fun p hp => not_lt.mp fun hlt => h p (Nat.zero_le p) hlt hp⟩

end GoldbachGaps
