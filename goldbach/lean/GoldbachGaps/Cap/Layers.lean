import GoldbachGaps.Covering
import GoldbachGaps.Cap.FirstMoment

/-!
# Layered covers below a cap: the finite skeleton of the lower bounds for `max g`

A cover of the rows (odd primes) below `Q` built in three layers:

* a *fixed layer* `F` with prescribed classes `a₀` (empty for the plain pigeonhole bound;
  `N ≡ 1 (mod p)` for the primes `p` of a middle range in the Erdős–Rankin adaptation);
* a *pigeonhole layer* `S`, where the first-moment law provides classes leaving at most the
  average number `|P₁| · ∏ (r - 2)/(r - 1)` of the rows `P₁` that survive the fixed layer;
* a *mop-up layer* `T`, one modulus for each row that is still left.

`exists_cover_of_layers` says that this works as soon as the counts allow it, and
`exists_even_le_of_layers` turns the cover into an even `N` in an explicit window of length
`2 ∏ r` with no Goldbach summand below `Q`.

These are the kernel-checked parts of two lower bounds for `max {g(N) : N ≤ X}` claimed by
the research session of 2026-11-22 (constant `e^γ / (2 C₂)` in front of `log X · log log X`,
and an Erdős–Rankin type improvement). What remains for either theorem is the estimation of
the three counts in the hypothesis `hcount`: the product `∏ (r - 2)/(r - 1)` (Mertens), the
number of mop-up primes (Chebyshev or the prime number theorem) and, for the second, the
number of rows surviving the fixed layer (an upper-bound sieve for prime pairs and a count
of smooth numbers). None of those is proved here.
-/

namespace GoldbachGaps.Cap

open Finset

/-- Mop-up: rows no more numerous than the moduli of `T` can each be given their own
modulus. -/
theorem exists_assignment_of_card_le (U T : Finset ℕ) (h : #U ≤ #T) :
    ∃ g : ℕ → ℕ, ∀ q ∈ U, ∃ t ∈ T, g t = q := by
  classical
  have hcard : Fintype.card ↥U ≤ Fintype.card ↥T := by simpa using h
  obtain ⟨e⟩ := Function.Embedding.nonempty_of_card_le hcard
  refine ⟨fun t => if h : ∃ q : ↥U, (e q : ℕ) = t then ((Classical.choose h : ↥U) : ℕ) else 0, ?_⟩
  intro q hq
  refine ⟨e ⟨q, hq⟩, (e ⟨q, hq⟩).2, ?_⟩
  have hex : ∃ q' : ↥U, (e q' : ℕ) = (e ⟨q, hq⟩ : ℕ) := ⟨⟨q, hq⟩, rfl⟩
  show (if h : ∃ q' : ↥U, (e q' : ℕ) = (e ⟨q, hq⟩ : ℕ) then ((Classical.choose h : ↥U) : ℕ)
    else 0) = q
  simp only [hex, ↓reduceDIte]
  have h2 : Classical.choose hex = ⟨q, hq⟩ :=
    e.injective (Subtype.ext (Classical.choose_spec hex))
  rw [h2]

/-- **Layered covers.** Let `F`, `S`, `T` be pairwise disjoint sets of moduli, the moduli of
`S` being at least `2`, and let classes `a₀` be given on `F`. Among the rows `P`, let `P₁` be
those not divisible by any modulus of `S` and not in the class `a₀ r` for any `r ∈ F`, and
let `Z` be those divisible by some modulus of `S`. If

  `|P₁| · ∏_{r ∈ S} (r - 2) + |Z| · ∏_{r ∈ S} (r - 1) ≤ |T| · ∏_{r ∈ S} (r - 1)`,

then the classes on `F` extend to `F ∪ S ∪ T` so that every row of `P` is in the class of
some modulus. -/
theorem exists_cover_of_layers (F S T P : Finset ℕ) (a₀ : ℕ → ℕ) (hS : ∀ r ∈ S, 2 ≤ r)
    (hFS : Disjoint F S) (hFT : Disjoint F T) (hST : Disjoint S T)
    (hcount : #{q ∈ P | (∀ r ∈ S, ¬ r ∣ q) ∧ ∀ r ∈ F, ¬ q ≡ a₀ r [MOD r]} * ∏ r ∈ S, (r - 2) +
        #{q ∈ P | ∃ r ∈ S, r ∣ q} * ∏ r ∈ S, (r - 1) ≤ #T * ∏ r ∈ S, (r - 1)) :
    ∃ a : ℕ → ℕ, (∀ r ∈ F, a r = a₀ r) ∧ ∀ q ∈ P, ∃ r ∈ F ∪ S ∪ T, q ≡ a r [MOD r] := by
  classical
  set P₁ := {q ∈ P | (∀ r ∈ S, ¬ r ∣ q) ∧ ∀ r ∈ F, ¬ q ≡ a₀ r [MOD r]} with hP₁
  set Z := {q ∈ P | ∃ r ∈ S, r ∣ q} with hZ
  have hP₁' : ∀ q ∈ P₁, ∀ r ∈ S, ¬ r ∣ q := fun q hq => (Finset.mem_filter.mp hq).2.1
  obtain ⟨b, hb, hle⟩ := exists_rowsLeft_le S P₁ hS hP₁'
  have hV : 0 < ∏ r ∈ S, (r - 1) := Finset.prod_pos fun r hr => by
    have := hS r hr
    omega
  have hUT : #(rowsLeft S P₁ b ∪ Z) ≤ #T := by
    refine Nat.le_of_mul_le_mul_right ?_ hV
    calc #(rowsLeft S P₁ b ∪ Z) * ∏ r ∈ S, (r - 1)
        ≤ (#(rowsLeft S P₁ b) + #Z) * ∏ r ∈ S, (r - 1) :=
          Nat.mul_le_mul_right _ (Finset.card_union_le _ _)
      _ = #(rowsLeft S P₁ b) * ∏ r ∈ S, (r - 1) + #Z * ∏ r ∈ S, (r - 1) := by ring
      _ ≤ #P₁ * ∏ r ∈ S, (r - 2) + #Z * ∏ r ∈ S, (r - 1) := Nat.add_le_add_right hle _
      _ ≤ #T * ∏ r ∈ S, (r - 1) := hcount
  obtain ⟨g, hg⟩ := exists_assignment_of_card_le _ T hUT
  refine ⟨fun r => if r ∈ F then a₀ r else if h : r ∈ S then b r h else g r, ?_, ?_⟩
  · intro r hr
    simp only [hr, ↓reduceIte]
  · intro q hq
    -- rows that the mop-up layer takes
    have mop : q ∈ rowsLeft S P₁ b ∪ Z → ∃ r ∈ F ∪ S ∪ T,
        q ≡ (if r ∈ F then a₀ r else if h : r ∈ S then b r h else g r) [MOD r] := by
      intro hU
      obtain ⟨t, ht, hgt⟩ := hg q hU
      have htF : t ∉ F := fun h => Finset.disjoint_left.mp hFT h ht
      have htS : t ∉ S := fun h => Finset.disjoint_left.mp hST h ht
      refine ⟨t, Finset.mem_union_right _ ht, ?_⟩
      simp only [htF, ↓reduceIte, htS, ↓reduceDIte, hgt]
      exact Nat.ModEq.refl q
    by_cases hZq : ∃ r ∈ S, r ∣ q
    · exact mop (Finset.mem_union_right _ (Finset.mem_filter.mpr ⟨hq, hZq⟩))
    · have hZq' : ∀ r ∈ S, ¬ r ∣ q := fun r hr h => hZq ⟨r, hr, h⟩
      by_cases hF : ∀ r ∈ F, ¬ q ≡ a₀ r [MOD r]
      · have hq₁ : q ∈ P₁ := Finset.mem_filter.mpr ⟨hq, hZq', hF⟩
        by_cases hleft : q ∈ rowsLeft S P₁ b
        · exact mop (Finset.mem_union_left _ hleft)
        · have hex : ∃ r, ∃ h : r ∈ S, q % r = b r h := by
            by_contra hcon
            exact hleft (Finset.mem_filter.mpr ⟨hq₁, fun r h heq => hcon ⟨r, h, heq⟩⟩)
          obtain ⟨r, hr, hqr⟩ := hex
          have hrF : r ∉ F := fun h => Finset.disjoint_left.mp hFS h hr
          refine ⟨r, Finset.mem_union_left _ (Finset.mem_union_right _ hr), ?_⟩
          simp only [hrF, ↓reduceIte, hr, ↓reduceDIte]
          have hbr : b r hr < r := (Finset.mem_Ico.mp ((Finset.mem_pi.mp hb) r hr)).2
          show q % r = b r hr % r
          rw [Nat.mod_eq_of_lt hbr, hqr]
      · have hex : ∃ r ∈ F, q ≡ a₀ r [MOD r] := by
          by_contra hcon
          exact hF fun r hr h => hcon ⟨r, hr, h⟩
        obtain ⟨r, hr, hqr⟩ := hex
        refine ⟨r, Finset.mem_union_left _ (Finset.mem_union_left _ hr), ?_⟩
        simp only [hr, ↓reduceIte]
        exact hqr

/-- **From a cover to a number below a cap.** If the classes `a r` modulo the odd primes
`r ∈ R` (all at most `B`) cover the odd primes below `Q`, then some even `N` with
`Q + B < N ≤ Q + B + 2 ∏ r` lies in all the classes and has no Goldbach summand below `Q`. -/
theorem exists_even_le_of_cover {R : Finset ℕ} {a : ℕ → ℕ} {Q B : ℕ}
    (hR : ∀ r ∈ R, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ R, r ≤ B) (hB2 : 2 ≤ B)
    (hcover : ∀ q, q.Prime → q ≠ 2 → q < Q → ∃ r ∈ R, q ≡ a r [MOD r]) :
    ∃ N, Even N ∧ Q + B < N ∧ N ≤ Q + B + 2 * ∏ r ∈ R, r ∧ (∀ r ∈ R, N ≡ a r [MOD r]) ∧
      ∀ q < Q, ¬ IsSummand N q := by
  classical
  have hr3 : ∀ r ∈ R, 3 ≤ r := fun r hr => by
    have h1 := (hR r hr).1.two_le
    have h2 := (hR r hr).2
    omega
  set M := ∏ r ∈ R, r with hM
  have hM0 : 0 < M := Finset.prod_pos fun r hr => by
    have := hr3 r hr
    omega
  have hrM : ∀ r ∈ R, r ∣ M := fun r hr => Finset.dvd_prod_of_mem (fun r => r) hr
  have hpp : Set.Pairwise (R : Set ℕ) (Function.onFun Nat.Coprime fun r : ℕ => r) :=
    fun r hr r' hr' hne => (Nat.coprime_primes (hR r hr).1 (hR r' hr').1).mpr hne
  have hs0 : ∀ r ∈ R, (fun r : ℕ => r) r ≠ 0 := fun r hr => by
    have := hr3 r hr
    show r ≠ 0
    omega
  obtain ⟨x₀, hx₀⟩ := Nat.chineseRemainderOfFinset a (fun r => r) R hs0 hpp
  have hModd : M % 2 = 1 := by
    rcases Nat.mod_two_eq_zero_or_one M with h | h
    · exfalso
      have h2 : 2 ∣ M := Nat.dvd_of_mod_eq_zero h
      obtain ⟨r, hr, h2r⟩ := (Prime.dvd_finsetProd_iff Nat.prime_two.prime _).mp h2
      exact (hR r hr).2 ((Nat.prime_dvd_prime_iff_eq Nat.prime_two (hR r hr).1).mp h2r).symm
    · exact h
  -- an even number with the same residues
  obtain ⟨x, hxeven, hx⟩ : ∃ x, x % 2 = 0 ∧ ∀ r ∈ R, x ≡ a r [MOD r] := by
    rcases Nat.mod_two_eq_zero_or_one x₀ with h | h
    · exact ⟨x₀, h, hx₀⟩
    · refine ⟨x₀ + M, by omega, fun r hr => ?_⟩
      have h1 : x₀ + M ≡ x₀ [MOD r] := by
        obtain ⟨c, hc⟩ := hrM r hr
        show (x₀ + M) % r = x₀ % r
        rw [hc, Nat.add_mul_mod_self_left]
      exact h1.trans (hx₀ r hr)
  -- move it into the window `(Q + B, Q + B + 2M]`
  set m := 2 * M with hm
  have hm0 : 0 < m := by omega
  set y := x % m with hy
  have hylt : y < m := Nat.mod_lt _ hm0
  set D := (Q + B + m - y) / m with hD
  have hNx : y + m * D ≡ x [MOD m] := by
    show (y + m * D) % m = x % m
    rw [Nat.add_mul_mod_self_left, hy, Nat.mod_mod]
  have h1 : m * D ≤ Q + B + m - y := Nat.mul_div_le _ _
  have h2 : Q + B + m - y < m * (D + 1) := Nat.lt_mul_div_succ _ hm0
  rw [Nat.mul_succ] at h2
  have hres : ∀ r ∈ R, y + m * D ≡ a r [MOD r] := fun r hr =>
    (hNx.of_dvd ((hrM r hr).trans (Dvd.intro_left 2 rfl))).trans (hx r hr)
  have heven : Even (y + m * D) := by
    have h3 : y + m * D ≡ x [MOD 2] := hNx.of_dvd (Dvd.intro M rfl)
    have h4 : (y + m * D) % 2 = x % 2 := h3
    exact Nat.even_iff.mpr (by omega)
  generalize m * D = E at h1 h2 hres heven ⊢
  refine ⟨y + E, heven, by omega, by omega, hres, fun q hqQ => ?_⟩
  exact not_isSummand_of_cover (fun r hr => by
      have := hr3 r hr
      omega) hcover hres heven (fun r hr => by
      have := hB r hr
      omega) (by omega) hqQ

/-- **The finite form of the layered lower bounds.** Let `F`, `S`, `T` be pairwise disjoint
sets of odd primes, all at most `B`, with classes `a₀` on `F`. Among the odd primes `q < Q`
let `P₁` be those outside `S` that no class of `F` contains, and `Z` those in `S`. If
`|P₁| · ∏_{r ∈ S} (r - 2) + |Z| · ∏_{r ∈ S} (r - 1) ≤ |T| · ∏_{r ∈ S} (r - 1)`, then there is
an even `N` with `Q + B < N ≤ Q + B + 2 ∏_{r ∈ F ∪ S ∪ T} r` that has no Goldbach summand
below `Q`. -/
theorem exists_even_le_of_layers (F S T : Finset ℕ) (a₀ : ℕ → ℕ) (Q B : ℕ)
    (hF : ∀ r ∈ F, r.Prime ∧ r ≠ 2) (hS : ∀ r ∈ S, r.Prime ∧ r ≠ 2)
    (hT : ∀ r ∈ T, r.Prime ∧ r ≠ 2) (hB : ∀ r ∈ F ∪ S ∪ T, r ≤ B) (hB2 : 2 ≤ B)
    (hFS : Disjoint F S) (hFT : Disjoint F T) (hST : Disjoint S T)
    (hcount : #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧ ∀ r ∈ F, ¬ q ≡ a₀ r [MOD r]} *
          ∏ r ∈ S, (r - 2) +
        #{q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} * ∏ r ∈ S, (r - 1) ≤
        #T * ∏ r ∈ S, (r - 1)) :
    ∃ N, Even N ∧ Q + B < N ∧ N ≤ Q + B + 2 * ∏ r ∈ F ∪ S ∪ T, r ∧ ∀ q < Q, ¬ IsSummand N q := by
  classical
  set P := {q ∈ range Q | q.Prime ∧ q ≠ 2} with hPdef
  -- for a prime row, "divisible by a modulus of `S`" means "belongs to `S`"
  have hdiv : ∀ q ∈ P, ((∃ r ∈ S, r ∣ q) ↔ q ∈ S) := by
    intro q hq
    have hqp : q.Prime := (Finset.mem_filter.mp hq).2.1
    constructor
    · rintro ⟨r, hr, hrq⟩
      have := (Nat.prime_dvd_prime_iff_eq (hS r hr).1 hqp).mp hrq
      rwa [← this]
    · intro h
      exact ⟨q, h, dvd_rfl⟩
  have e1 : {q ∈ P | (∀ r ∈ S, ¬ r ∣ q) ∧ ∀ r ∈ F, ¬ q ≡ a₀ r [MOD r]} =
      {q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∉ S ∧ ∀ r ∈ F, ¬ q ≡ a₀ r [MOD r]} := by
    ext q
    simp only [hPdef, Finset.mem_filter]
    constructor
    · rintro ⟨hq, h1, h2⟩
      exact ⟨hq.1, hq.2, fun h => h1 q h dvd_rfl, h2⟩
    · rintro ⟨hq, hq', h1, h2⟩
      refine ⟨⟨hq, hq'⟩, fun r hr hrq => h1 ?_, h2⟩
      exact (hdiv q (Finset.mem_filter.mpr ⟨hq, hq'⟩)).mp ⟨r, hr, hrq⟩
  have e2 : {q ∈ P | ∃ r ∈ S, r ∣ q} = {q ∈ range Q | (q.Prime ∧ q ≠ 2) ∧ q ∈ S} := by
    ext q
    simp only [hPdef, Finset.mem_filter]
    constructor
    · rintro ⟨hq, h⟩
      exact ⟨hq.1, hq.2, (hdiv q (Finset.mem_filter.mpr hq)).mp h⟩
    · rintro ⟨hq, hq', h⟩
      exact ⟨⟨hq, hq'⟩, (hdiv q (Finset.mem_filter.mpr ⟨hq, hq'⟩)).mpr h⟩
  obtain ⟨a, -, ha⟩ := exists_cover_of_layers F S T P a₀
    (fun r hr => (hS r hr).1.two_le) hFS hFT hST (by rw [e1, e2]; exact hcount)
  have hR : ∀ r ∈ F ∪ S ∪ T, r.Prime ∧ r ≠ 2 := by
    intro r hr
    rcases Finset.mem_union.mp hr with h | h
    · rcases Finset.mem_union.mp h with h | h
      · exact hF r h
      · exact hS r h
    · exact hT r h
  obtain ⟨N, h1, h2, h3, -, h5⟩ := exists_even_le_of_cover (a := a) hR hB hB2
    (fun q hq hq2 hqQ => ha q (Finset.mem_filter.mpr ⟨Finset.mem_range.mpr hqQ, hq, hq2⟩))
  exact ⟨N, h1, h2, h3, h5⟩

end GoldbachGaps.Cap
