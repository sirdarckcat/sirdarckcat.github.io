import GoldbachGaps.Needles

/-!
# Patterns in the largest least Goldbach summands, and what of them is provable

The experiment (`scripts/rank_records`): compute the least Goldbach summand `g(N)` of every even
`N` up to `10^11`, keep the ten largest values seen so far, and list the `N` that arrive at each
rank. The arrivals at every rank show the same patterns. This file proves the ones that are
exact, and for one that is statistical it proves the finite fact that explains its direction.

Exact relations (true for every `N`, visible on every arrival):

* `IsSummand.not_modEq`: a summand `p` of `N` is not congruent to `N` modulo a prime `r`, unless
  `N - p = r`. For `r = 3`: `IsSummand.three_dvd_add`, if `3 ∤ N` then `3 ∣ N + g(N)`
  (all 249 arrivals above `10^5`).
* `IsLeastSummand.sub_le`: `g(N) ≥ N - p` for every prime `p < N`; the least summand is at least
  the distance to the previous prime.
* The shift law. `IsLeastSummand.isSummand_add`: if `g(N) + h` is prime it is a summand of
  `N + h`, with the same prime `N - g(N)` behind it; so `g(N + h) ≤ g(N) + h`
  (`IsLeastSummand.le_add`). `IsLeastSummand.add_of_forall`: equality holds as soon as the rows
  of `N + h` that are not inherited from `N` are composite. `IsLeastSummand.le_sub`: an inherited
  row is never the least summand of `N + h` unless it is at least `g(N) + h`. The arrivals
  contain such pairs `(N, g)`, `(N + 30, g + 30)`; four are certified in `RankTable.lean`.

A statistical pattern, and the finite fact behind it:

* The arrivals avoid `N ≡ 0` modulo 3, 5, 7 and prefer the classes that are quadratic
  non-residues (174 against 75 modulo 3, 165 against 83 modulo 5). A class `a` of `N` modulo `r`
  kills exactly the rows `q ≡ a`, and below `x` the non-residue classes hold more primes
  (Chebyshev's bias). `card_rows_mod_three_le` and `card_rows_mod_five_le` check this in the
  kernel for every level up to `4096` and `3528`, which covers every value of `g` that occurs
  below `10^12`: the class `2` modulo `3` never holds fewer rows than the class `1`, and each of
  the classes `2, 3` modulo `5` never holds fewer than each of `1, 4`. That the record holders
  therefore prefer those classes is the model's prediction; it is not a theorem.
-/

namespace GoldbachGaps

/-! ### Exact relations -/

/-- A summand of `N` is not congruent to `N` modulo a prime `r`, unless the other part is `r`. -/
theorem IsSummand.not_modEq {N p r : ℕ} (h : IsSummand N p) (hr : r.Prime) (hne : N - p ≠ r) :
    ¬ p ≡ N [MOD r] := by
  intro hmod
  have hle : p ≤ N := by
    have := h.2.two_le
    omega
  have hdvd : r ∣ N - p := (Nat.modEq_iff_dvd' hle).mp hmod
  rcases (Nat.dvd_prime h.2).mp hdvd with h1 | h1
  · exact hr.one_lt.ne' h1
  · exact hne h1.symm

/-- If `3 ∤ N`, a summand `p > 3` of `N` with `N - p > 3` has `3 ∣ N + p`: the two parts of the
partition are in the same class modulo `3`. -/
theorem IsSummand.three_dvd_add {N p : ℕ} (h : IsSummand N p) (hN : ¬ 3 ∣ N) (hp : 3 < p)
    (hq : 3 < N - p) : 3 ∣ N + p := by
  have h1 : ¬ 3 ∣ p := fun hd => by
    rcases (Nat.dvd_prime h.1).mp hd with h3 | h3 <;> omega
  have h2 : ¬ 3 ∣ N - p := fun hd => by
    rcases (Nat.dvd_prime h.2).mp hd with h3 | h3 <;> omega
  have hp3 : p % 3 = 1 ∨ p % 3 = 2 := by omega
  have hq3 : (N - p) % 3 = 1 ∨ (N - p) % 3 = 2 := by omega
  rcases hp3 with h3 | h3 <;> rcases hq3 with h4 | h4 <;> omega

/-- Every prime `p` strictly between `N - g(N)` and `N` is at a composite distance from `N`
(or at distance `1`): otherwise `N - p` would be a smaller summand. -/
theorem IsLeastSummand.not_prime_sub {N g p : ℕ} (hN : IsLeastSummand N g) (hp : p.Prime)
    (hlo : N - g < p) (hlt : p < N) : ¬ (N - p).Prime := by
  intro hq
  have hs : IsSummand N (N - p) := ⟨hq, by rwa [Nat.sub_sub_self hlt.le]⟩
  have := hN.2 _ hs
  omega

/-- The least summand is at least the distance from `N` to the largest prime below `N`: if no
prime lies in `(p₁, N)`, then `g(N) ≥ N - p₁`. So a prime gap of length `G` ending above `N`
forces `g(N) ≥ N - p₁`. -/
theorem IsLeastSummand.sub_le {N g p₁ : ℕ} (hN : IsLeastSummand N g)
    (hgap : ∀ p, p₁ < p → p < N → ¬ p.Prime) : N - p₁ ≤ g := by
  by_contra hlt
  have hg := hN.1.1.two_le
  have hq := hN.1.2
  exact hgap (N - g) (by omega) (by omega) hq

/-- **The shift law.** If `g` is the least summand of `N` and `g + h` is prime, then `g + h` is a
summand of `N + h`: the prime behind it is the same, `N + h - (g + h) = N - g`. -/
theorem IsLeastSummand.isSummand_add {N g h : ℕ} (hN : IsLeastSummand N g)
    (hp : (g + h).Prime) : IsSummand (N + h) (g + h) := by
  refine ⟨hp, ?_⟩
  have e : N + h - (g + h) = N - g := by omega
  rw [e]
  exact hN.1.2

/-- So `g(N + h) ≤ g(N) + h` whenever `g(N) + h` is prime. -/
theorem IsLeastSummand.le_add {N g h g' : ℕ} (hN : IsLeastSummand N g)
    (hN' : IsLeastSummand (N + h) g') (hp : (g + h).Prime) : g' ≤ g + h :=
  hN'.2 _ (hN.isSummand_add hp)

/-- An inherited row is the least summand of `N + h` only if it is at least `g(N) + h`: if
`g' - h` is prime then `g(N) ≤ g' - h`. -/
theorem IsLeastSummand.le_sub {N g h g' : ℕ} (hN : IsLeastSummand N g)
    (hN' : IsLeastSummand (N + h) g') (hh : h ≤ g') (hp : (g' - h).Prime) : g ≤ g' - h := by
  refine hN.2 _ ⟨hp, ?_⟩
  have e : N - (g' - h) = N + h - g' := by omega
  rw [e]
  exact hN'.1.2

/-- **When the shift is exact.** If `g` is the least summand of `N`, `g + h` is prime, and every
row `q' < g + h` of `N + h` that is not inherited from `N` (that is, with `q' < h` or `q' - h`
not prime) is composite, then `g + h` is the least summand of `N + h`. -/
theorem IsLeastSummand.add_of_forall {N g h : ℕ} (hN : IsLeastSummand N g) (hp : (g + h).Prime)
    (hrest : ∀ q' < g + h, q'.Prime → ¬ (h ≤ q' ∧ (q' - h).Prime) → ¬ (N + h - q').Prime) :
    IsLeastSummand (N + h) (g + h) := by
  refine ⟨hN.isSummand_add hp, fun p' hs => ?_⟩
  by_contra hlt
  have hlt' : p' < g + h := not_le.mp hlt
  by_cases hin : h ≤ p' ∧ (p' - h).Prime
  · have hs' : IsSummand N (p' - h) := by
      refine ⟨hin.2, ?_⟩
      have e : N - (p' - h) = N + h - p' := by omega
      rw [e]
      exact hs.2
    have := hN.2 _ hs'
    omega
  · exact hrest p' hlt' hs.1 hin hs.2

/-! ### The prime race behind the residue bias -/

/-- The primes below `64`. -/
def primesBelow64 : List ℕ := [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]

/-- Trial division by the primes below `64`: a primality test for numbers below `4096`. -/
def isPrimeBelow4096 (q : ℕ) : Bool :=
  decide (2 ≤ q) && primesBelow64.all fun d => decide (q ≤ d) || q % d != 0

theorem prime_iff_isPrimeBelow4096 {q : ℕ} (hq : q < 4096) :
    q.Prime ↔ isPrimeBelow4096 q = true := by
  simp only [isPrimeBelow4096, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    Bool.or_eq_true, bne_iff_ne, ne_eq]
  constructor
  · intro hp
    refine ⟨hp.two_le, fun d hd => ?_⟩
    by_cases hdq : q ≤ d
    · exact Or.inl hdq
    · refine Or.inr fun h0 => ?_
      have hd2 : 2 ≤ d := by
        simp only [primesBelow64, List.mem_cons, List.not_mem_nil, or_false] at hd
        omega
      rcases (Nat.dvd_prime hp).mp (Nat.dvd_of_mod_eq_zero h0) with h1 | h1 <;> omega
  · rintro ⟨h2, hall⟩
    by_contra hnp
    have hm := Nat.minFac_prime (show q ≠ 1 by omega)
    have hsq : q.minFac ^ 2 ≤ q := Nat.minFac_sq_le_self (by omega) hnp
    have hlt64 : q.minFac < 64 := by nlinarith [hm.two_le]
    have hmem : q.minFac ∈ primesBelow64 := by
      have key : ∀ p < 64, p.Prime → p ∈ primesBelow64 := by decide
      exact key _ hlt64 hm
    have hltq : q.minFac < q := by nlinarith [hm.two_le]
    rcases hall _ hmem with h | h
    · omega
    · exact h (Nat.mod_eq_zero_of_dvd (Nat.minFac_dvd q))

/-- A linear scan: along the list, the count of `fa` never exceeds the count of `fb`. -/
def leadScan (fa fb : ℕ → Bool) : List ℕ → ℕ → ℕ → Bool
  | [], _, _ => true
  | x :: xs, ca, cb =>
    decide ((if fa x then ca + 1 else ca) ≤ (if fb x then cb + 1 else cb)) &&
      leadScan fa fb xs (if fa x then ca + 1 else ca) (if fb x then cb + 1 else cb)

theorem leadScan_sound (fa fb : ℕ → Bool) :
    ∀ (l : List ℕ) (ca cb : ℕ), ca ≤ cb → leadScan fa fb l ca cb = true →
      ∀ k, ca + ((l.take k).filter fa).length ≤ cb + ((l.take k).filter fb).length := by
  intro l
  induction l with
  | nil => intro ca cb h _ k; simpa using h
  | cons x xs ih =>
    intro ca cb h hs k
    rw [leadScan, Bool.and_eq_true, decide_eq_true_eq] at hs
    cases k with
    | zero => simpa using h
    | succ k =>
      have := ih _ _ hs.1 hs.2 k
      rw [List.take_succ_cons, List.filter_cons, List.filter_cons]
      by_cases ha : fa x <;> by_cases hb : fb x <;> simp only [ha, hb, ↓reduceIte,
        List.length_cons, Bool.false_eq_true] at this ⊢ <;> omega

/-- The rows in the class `a` modulo `r` below `Q`, counted with the fast test. -/
def rowsIn (r a : ℕ) (q : ℕ) : Bool := isPrimeBelow4096 q && decide (2 < q) && q % r == a

theorem card_rows_eq {r a Q : ℕ} (hQ : Q ≤ 4096) :
    ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % r = a).card
      = ((List.range Q).filter (rowsIn r a)).length := by
  have e : ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % r = a)
      = ((List.range Q).filter (rowsIn r a)).toFinset := by
    ext q
    simp only [Finset.mem_filter, Finset.mem_range, List.mem_toFinset, List.mem_filter,
      List.mem_range, rowsIn, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq]
    constructor
    · rintro ⟨hlt, hp, h2, hm⟩
      exact ⟨hlt, ⟨(prime_iff_isPrimeBelow4096 (by omega)).mp hp, h2⟩, hm⟩
    · rintro ⟨hlt, ⟨hp, h2⟩, hm⟩
      exact ⟨hlt, (prime_iff_isPrimeBelow4096 (by omega)).mpr hp, h2, hm⟩
  rw [e, List.toFinset_card_of_nodup (List.Nodup.filter _ List.nodup_range)]

/-- If the scan succeeds up to `B ≤ 4096`, the class `a` never leads the class `b` below `B`. -/
theorem card_rows_le_of_leadScan {r a b B : ℕ} (hB : B ≤ 4096)
    (h : leadScan (rowsIn r a) (rowsIn r b) (List.range B) 0 0 = true) {Q : ℕ} (hQ : Q ≤ B) :
    ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % r = a).card
      ≤ ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % r = b).card := by
  rw [card_rows_eq (hQ.trans hB), card_rows_eq (hQ.trans hB)]
  have := leadScan_sound _ _ _ 0 0 le_rfl h Q
  rwa [zero_add, zero_add, List.take_range, min_eq_left hQ] at this

set_option maxRecDepth 100000 in
/-- **The prime race modulo 3, up to 4096.** At every level `Q ≤ 4096` the class `2` modulo `3`
holds at least as many rows (odd primes below `Q`) as the class `1`. So a number `N ≡ 2 (mod 3)`
never has fewer rows divisible by `3` than a number `N ≡ 1 (mod 3)`, at any level that occurs
among the records below `10^12`. (By Bays and Hudson the first reversal is beyond `6 · 10^11`.) -/
theorem card_rows_mod_three_le {Q : ℕ} (hQ : Q ≤ 4096) :
    ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % 3 = 1).card
      ≤ ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % 3 = 2).card :=
  card_rows_le_of_leadScan le_rfl (by decide +kernel) hQ

set_option maxRecDepth 100000 in
/-- **The prime race modulo 5, up to 3528.** At every level `Q ≤ 3528` each of the non-residue
classes `2`, `3` modulo `5` holds at least as many rows as each of the residue classes `1`, `4`.
(The first exception is at the prime `3529`.) -/
theorem card_rows_mod_five_le {Q a b : ℕ} (hQ : Q ≤ 3528) (ha : a = 1 ∨ a = 4)
    (hb : b = 2 ∨ b = 3) :
    ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % 5 = a).card
      ≤ ((Finset.range Q).filter fun q => q.Prime ∧ 2 < q ∧ q % 5 = b).card := by
  rcases ha with rfl | rfl <;> rcases hb with rfl | rfl <;>
    exact card_rows_le_of_leadScan (by norm_num) (by decide +kernel) hQ

end GoldbachGaps
