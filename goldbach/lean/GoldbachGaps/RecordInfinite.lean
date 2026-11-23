import GoldbachGaps.RecordGen

/-!
# Does the generator go on forever? Exactly if Goldbach's conjecture is true

`RecordGen.mem_records` is a statement about every bound `X`: the generator is correct as far
as one cares to run it. Whether it keeps *producing* terms is another question, and this file
answers it without any computation.

* `exists_isFront`: **the front always exists.** For every striker `g` there is a smallest even
  number `≥ 4` that no prime below `g` has struck. (The multiples of a primorial give such
  numbers.) So the generator never fails to find a front.
* `goldbach_iff_records_unbounded`, `goldbach_iff_generator_never_stops`: **the sequence is
  infinite if and only if every even number from `4` on is a sum of two primes.** The terms of
  A025018 are unbounded, and `records X` grows beyond every length, exactly when Goldbach's
  conjecture holds.
* `isFront_of_counterexample`: if the conjecture fails, the front arrives at the smallest even
  number that is not a sum of two primes and stays there: no later striker can hit it.

So a proof that the generator runs forever would be a proof of Goldbach's conjecture, and any
term beyond the range where the conjecture has been verified by computation (`4 · 10^18`,
Oliveira e Silva, Herzog and Pardi) is out of reach of proof today. What a proof can reach is
every finite bound: below `2^25` the table is a kernel-checked theorem
(`RankSieve.isRecordHolder_iff`), and the same method goes on at a cost that grows with the
bound (`scripts/record_gen/README.md`).
-/

namespace GoldbachGaps

/-- Goldbach's conjecture: every even number from `4` on is a sum of two primes. -/
def GoldbachConjecture : Prop := ∀ N, Even N → 4 ≤ N → ∃ q, IsSummand N q

/-- For every `g` there are even numbers that no prime up to `g` strikes. -/
theorem exists_unstruck (g : ℕ) : ∃ N, Even N ∧ 4 ≤ N ∧ ∀ q ≤ g, ¬ IsSummand N q := by
  have hpos : 0 < primorial g := primorial_pos g
  have hle : 2 * g + 4 ≤ primorial g * (2 * g + 4) := Nat.le_mul_of_pos_left _ hpos
  refine ⟨primorial g * (2 * g + 4), Even.mul_left ⟨g + 2, by ring⟩ _, by omega, fun q hq =>
    not_isSummand_of_primorial_dvd (Dvd.intro _ rfl) (by omega) hq⟩

/-- **The front always exists**, whatever the striker. -/
theorem exists_isFront (g : ℕ) : ∃ N, IsFront g N := by
  classical
  have hex : ∃ N, Even N ∧ 4 ≤ N ∧ ∀ q < g, ¬ IsSummand N q := by
    obtain ⟨N, hE, h4, h⟩ := exists_unstruck g
    exact ⟨N, hE, h4, fun q hq => h q hq.le⟩
  refine ⟨Nat.find hex, (Nat.find_spec hex).1, (Nat.find_spec hex).2.1,
    (Nat.find_spec hex).2.2, fun M hE h4 hlt => ?_⟩
  have hmin := Nat.find_min hex hlt
  by_contra hno
  push Not at hno
  exact hmin ⟨hE, h4, fun q hq hs => hno q hq hs⟩

/-- A number with a Goldbach summand has a least one. -/
theorem exists_isLeastSummand_of_isSummand {N q : ℕ} (h : IsSummand N q) :
    ∃ g, IsLeastSummand N g := by
  classical
  have hex : ∃ p, IsSummand N p := ⟨q, h⟩
  exact ⟨Nat.find hex, Nat.find_spec hex, fun p hp => Nat.find_min' hex hp⟩

/-- Under Goldbach's conjecture there are terms with arbitrarily large values. -/
theorem exists_isRecord_gt (hG : GoldbachConjecture) (B : ℕ) :
    ∃ N g, B < g ∧ g < N ∧ IsRecord N g := by
  obtain ⟨N, hF⟩ := exists_isFront (B + 1)
  obtain ⟨q, hq⟩ := hG N hF.1 hF.2.1
  obtain ⟨g, hg⟩ := exists_isLeastSummand_of_isSummand hq
  have hBg : B < g := by
    by_contra hle
    exact hF.2.2.1 g (by omega) hg.1
  refine ⟨N, g, hBg, RecordGen.lt_of_isSummand hg.1, hF.1, hF.2.1, hg, fun M hE h4 hlt => ?_⟩
  obtain ⟨q', hq', hs⟩ := hF.2.2.2 M hE h4 hlt
  exact ⟨q', by omega, hs⟩

/-- **The sequence is unbounded exactly if Goldbach's conjecture holds.** -/
theorem goldbach_iff_records_unbounded :
    GoldbachConjecture ↔ ∀ B, ∃ N g, B ≤ N ∧ IsRecord N g := by
  constructor
  · intro hG B
    obtain ⟨N, g, hBg, hgN, hr⟩ := exists_isRecord_gt hG B
    exact ⟨N, g, by omega, hr⟩
  · intro h N hE h4
    obtain ⟨N', g, hB, hr⟩ := h (N + 1)
    obtain ⟨q, _, hs⟩ := hr.2.2.2 N hE h4 (by omega)
    exact ⟨q, hs⟩

/-- `records X` has no repetitions. -/
theorem RecordGen.nodup_records (X : ℕ) : (RecordGen.records X).Nodup :=
  (RecordGen.records_sorted X).imp fun h => by
    rintro rfl
    omega

/-- **The generator never stops producing exactly if Goldbach's conjecture holds:** the list
`records X` exceeds every length for suitable `X`. -/
theorem goldbach_iff_generator_never_stops :
    GoldbachConjecture ↔ ∀ n, ∃ X, n ≤ (RecordGen.records X).length := by
  constructor
  · intro hG n
    induction n with
    | zero => exact ⟨0, Nat.zero_le _⟩
    | succ n ih =>
      obtain ⟨X, hX⟩ := ih
      obtain ⟨N, g, hBg, hgN, hr⟩ := exists_isRecord_gt hG X
      refine ⟨N + 1, ?_⟩
      have hsub : (N, g) :: RecordGen.records X ⊆ RecordGen.records (N + 1) := by
        intro a ha
        rcases List.mem_cons.mp ha with rfl | ha
        · exact RecordGen.mem_records.mpr ⟨by omega, hr⟩
        · obtain ⟨N', g'⟩ := a
          have h := RecordGen.mem_records.mp ha
          exact RecordGen.mem_records.mpr ⟨by omega, h.2⟩
      have hnd : ((N, g) :: RecordGen.records X).Nodup := by
        refine List.nodup_cons.mpr ⟨fun hmem => ?_, RecordGen.nodup_records X⟩
        have := (RecordGen.mem_records.mp hmem).1
        omega
      have := (hnd.subperm hsub).length_le
      rw [List.length_cons] at this
      omega
  · intro h N hE h4
    obtain ⟨X, hX⟩ := h ((RecordGen.records (N + 1)).length + 1)
    have hex : ∃ a ∈ RecordGen.records X, a ∉ RecordGen.records (N + 1) := by
      by_contra hno
      push Not at hno
      have := ((RecordGen.nodup_records X).subperm hno).length_le
      omega
    obtain ⟨⟨N', g⟩, ha, hna⟩ := hex
    have h1 := RecordGen.mem_records.mp ha
    have hN' : N + 1 ≤ N' := by
      by_contra hlt
      exact hna (RecordGen.mem_records.mpr ⟨by omega, h1.2⟩)
    obtain ⟨q, _, hs⟩ := h1.2.2.2.2 N hE h4 (by omega)
    exact ⟨q, hs⟩

/-- **Where the generator would stop.** If `N₀` is the smallest even number from `4` on that is
not a sum of two primes, then `N₀` is the front for every striker from `N₀` on: the front
arrives there and no striker ever hits it. -/
theorem isFront_of_counterexample {N₀ : ℕ} (hE : Even N₀) (h4 : 4 ≤ N₀)
    (hno : ∀ q, ¬ IsSummand N₀ q)
    (hmin : ∀ M, Even M → 4 ≤ M → M < N₀ → ∃ q, IsSummand M q) :
    ∀ g, N₀ ≤ g → IsFront g N₀ := fun g hg =>
  ⟨hE, h4, fun q _ => hno q, fun M hM hM4 hlt => by
    obtain ⟨q, hs⟩ := hmin M hM hM4 hlt
    exact ⟨q, by have := RecordGen.lt_of_isSummand hs; omega, hs⟩⟩

end GoldbachGaps
