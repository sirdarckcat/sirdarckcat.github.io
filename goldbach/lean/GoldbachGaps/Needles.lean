import GoldbachGaps.CompleteCover

/-!
# What two needles have in common

A *needle* at level `Q` is an `N` with no Goldbach summand below `Q`: every `N - q`, `q < Q`
prime, is composite. The research session measured, on the exhaustive miniature (`X = 10^9`,
`Q = 1000`), that the best numbers look like independent draws. This file records what is
exactly true about two needles, in both directions.

Rows are numbers, and two needles that are close share them:

* `IsNeedle.not_isSummand_add`: if `N` is a needle at level `Q`, the rows `q'` of `N + h` with
  `q' - h` prime and below `Q` are composite for free, because `N + h - q' = N - (q' - h)` is a
  row of `N`.
* `IsNeedle.add_of_forall`: so `N + h` is a needle as soon as its *other* rows are composite.
  For `Q = 1000` and `h = 30` that is 71 rows out of 168 (`card_inherited_rows_30`).
* `row_ne_of_add_le`: two numbers at distance `Q` or more have no row in common.

So needles closer than `Q` are not independent, and needles further apart share no row. What
two needles can share beyond rows is residues, within a budget: `Cap.Brainstorm.shared_row_value`
(two numbers that share a row agree only modulo moduli of product below `Q`) and
`Cap.Brainstorm.move_budget` (two numbers below `X` agree modulo coprime moduli of product
below `X`).

Kernel-checked instances are in `NeedlePairs.lean`: four pairs of needles at level `1000` below
`10^9` at distances 30, 30, 126 and 210. An exhaustive enumeration (`scripts/mini_check`, not a
Lean theorem) finds 303 needles below `10^9`; if they were independent and uniform one would
expect 0.09 pairs closer than `1000`, and with the inherited rows counted as certain one
expects 2.7. There are these four.

Nothing here says that needles are random. They are a fixed set; their residues modulo small
primes and their sizes are biased in a way the campaign's model predicts; and the statement
that nothing else distinguishes them is a form of the prime tuples conjecture, which is open.
-/

namespace GoldbachGaps

/-- `N` is a needle at level `Q`: no `q < Q` is a Goldbach summand of `N`. -/
def IsNeedle (N Q : ℕ) : Prop := ∀ q < Q, ¬ IsSummand N q

theorem isNeedle_iff_noSummandIn {N Q : ℕ} : IsNeedle N Q ↔ NoSummandIn N 0 Q :=
  ⟨fun h q _ hq => h q hq, fun h q hq => h q (Nat.zero_le q) hq⟩

theorem IsNeedle.mono {N Q Q' : ℕ} (h : IsNeedle N Q) (hQ : Q' ≤ Q) : IsNeedle N Q' :=
  fun q hq => h q (lt_of_lt_of_le hq hQ)

/-- **Inherited rows.** If `N` is a needle at level `Q`, then `q'` is not a summand of `N + h`
whenever `q' - h` is a prime below `Q`: the number `N + h - q'` is the row `N - (q' - h)` of
`N`. -/
theorem IsNeedle.not_isSummand_add {N Q : ℕ} (hN : IsNeedle N Q) {h q' : ℕ} (hh : h ≤ q')
    (hq : (q' - h).Prime) (hlt : q' - h < Q) : ¬ IsSummand (N + h) q' := by
  rintro ⟨-, hp⟩
  have e : N + h - q' = N - (q' - h) := by omega
  rw [e] at hp
  exact hN (q' - h) hlt ⟨hq, hp⟩

/-- **A neighbour of a needle is a needle as soon as its rows that are not inherited are
composite.** The rows `q'` with `q' - h` prime need no test. -/
theorem IsNeedle.add_of_forall {N Q h : ℕ} (hN : IsNeedle N Q)
    (hrest : ∀ q' < Q, q'.Prime → ¬ (h ≤ q' ∧ (q' - h).Prime) → ¬ (N + h - q').Prime) :
    IsNeedle (N + h) Q := by
  intro q' hq' hs
  by_cases hin : h ≤ q' ∧ (q' - h).Prime
  · exact hN.not_isSummand_add hin.1 hin.2 (by omega) hs
  · exact hrest q' hq' hs.1 hin hs.2

/-- Two numbers at distance at least `Q` have no row in common: the rows of `N` are at most
`N`, the rows of `N'` below `Q` are above `N' - Q`. -/
theorem row_ne_of_add_le {N N' Q q q' : ℕ} (hfar : N + Q ≤ N') (hq' : q' < Q) :
    N - q ≠ N' - q' := by
  omega

/-! ### Counting the inherited rows below `1000` -/

/-- The primes below `32`. -/
def primesBelow32 : List ℕ := [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

/-- Trial division by the primes below `32`: a primality test for numbers below `1024` that the
kernel evaluates quickly. -/
def isPrimeBelow1024 (q : ℕ) : Bool :=
  decide (2 ≤ q) && primesBelow32.all fun d => decide (q ≤ d) || q % d != 0

theorem prime_iff_isPrimeBelow1024 {q : ℕ} (hq : q < 1024) :
    q.Prime ↔ isPrimeBelow1024 q = true := by
  simp only [isPrimeBelow1024, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    Bool.or_eq_true, bne_iff_ne, ne_eq]
  constructor
  · intro hp
    refine ⟨hp.two_le, fun d hd => ?_⟩
    by_cases hdq : q ≤ d
    · exact Or.inl hdq
    · refine Or.inr fun h0 => ?_
      have hd2 : 2 ≤ d := by
        simp only [primesBelow32, List.mem_cons, List.not_mem_nil, or_false] at hd
        omega
      rcases (Nat.dvd_prime hp).mp (Nat.dvd_of_mod_eq_zero h0) with h1 | h1 <;> omega
  · rintro ⟨h2, hall⟩
    by_contra hnp
    have hm := Nat.minFac_prime (show q ≠ 1 by omega)
    have hsq : q.minFac ^ 2 ≤ q := Nat.minFac_sq_le_self (by omega) hnp
    have hlt32 : q.minFac < 32 := by nlinarith [hm.two_le]
    have hmem : q.minFac ∈ primesBelow32 := by
      have key : ∀ p < 32, p.Prime → p ∈ primesBelow32 := by decide
      exact key _ hlt32 hm
    have hltq : q.minFac < q := by nlinarith [hm.two_le]
    rcases hall _ hmem with h | h
    · omega
    · exact h (Nat.mod_eq_zero_of_dvd (Nat.minFac_dvd q))

/-- The number of primes `q' < 1000` with `h ≤ q'` and `q' - h` prime: the rows of `N + h` that
are inherited from `N` at level `1000`. -/
def inheritedCount (h : ℕ) : ℕ :=
  ((List.range 1000).filter fun q' =>
    isPrimeBelow1024 q' && decide (h ≤ q') && isPrimeBelow1024 (q' - h)).length

theorem card_inherited_rows (h : ℕ) :
    ((Finset.range 1000).filter fun q' => q'.Prime ∧ h ≤ q' ∧ (q' - h).Prime).card
      = inheritedCount h := by
  have e : ((Finset.range 1000).filter fun q' => q'.Prime ∧ h ≤ q' ∧ (q' - h).Prime)
      = ((List.range 1000).filter fun q' =>
          isPrimeBelow1024 q' && decide (h ≤ q') && isPrimeBelow1024 (q' - h)).toFinset := by
    ext q'
    simp only [Finset.mem_filter, Finset.mem_range, List.mem_toFinset, List.mem_filter,
      List.mem_range, Bool.and_eq_true, decide_eq_true_eq]
    constructor
    · rintro ⟨hlt, hp, hh, hp'⟩
      exact ⟨hlt, ⟨(prime_iff_isPrimeBelow1024 (by omega)).mp hp, hh⟩,
        (prime_iff_isPrimeBelow1024 (by omega)).mp hp'⟩
    · rintro ⟨hlt, ⟨hp, hh⟩, hp'⟩
      exact ⟨hlt, (prime_iff_isPrimeBelow1024 (by omega)).mpr hp, hh,
        (prime_iff_isPrimeBelow1024 (by omega)).mpr hp'⟩
  rw [e, List.toFinset_card_of_nodup (List.Nodup.filter _ List.nodup_range), inheritedCount]

set_option maxRecDepth 100000 in
/-- There are 168 primes below `1000`; of the rows of `N + 30` at level `1000`, 97 are inherited
from `N`; of those of `N + 126`, 73; of those of `N + 210`, 87. -/
theorem card_primes_lt_1000 :
    ((Finset.range 1000).filter fun q' => q'.Prime ∧ 0 ≤ q' ∧ (q' - 0).Prime).card = 168 := by
  rw [card_inherited_rows]
  decide +kernel

set_option maxRecDepth 100000 in
theorem card_inherited_rows_30 :
    ((Finset.range 1000).filter fun q' => q'.Prime ∧ 30 ≤ q' ∧ (q' - 30).Prime).card = 97 := by
  rw [card_inherited_rows]
  decide +kernel

set_option maxRecDepth 100000 in
theorem card_inherited_rows_126 :
    ((Finset.range 1000).filter fun q' => q'.Prime ∧ 126 ≤ q' ∧ (q' - 126).Prime).card = 73 := by
  rw [card_inherited_rows]
  decide +kernel

set_option maxRecDepth 100000 in
theorem card_inherited_rows_210 :
    ((Finset.range 1000).filter fun q' => q'.Prime ∧ 210 ≤ q' ∧ (q' - 210).Prime).card = 87 := by
  rw [card_inherited_rows]
  decide +kernel

end GoldbachGaps
