import GoldbachGaps.Covering
import GoldbachGaps.BitSieve
import GoldbachGaps.RecordWalk

/-!
# The cover depth: how far a set of moduli can strike the primes with no luck

Give every modulus `r` of a list one residue class `a r`. The vector *strikes* an odd prime `q`
when `q ≡ a r (mod r)` for some `r`: then every `N ≡ a r (mod r)` has `r ∣ N - q`. The **cover
depth** `D` of the list is the first odd prime that no vector strikes together with all smaller
odd primes: `IsDepth mods D` says that some vector strikes every odd prime below `D` and none
strikes every odd prime up to `D`. For the first `n` odd primes this is the function `D(n)` of
the research session (`goldbach/sublinear`, branch `ccr-d4a17dd0-7uu03r`).

* `search`, `search_iff`: a depth-first search ("which modulus strikes the least unstruck
  prime?") decides whether a list of primes can be struck, and is proved correct.
* `isDepth_0` … `isDepth_7`: **the exact values** `D = 3, 5, 7, 19, 31, 43, 67, 103` for the
  first `0, 1, …, 7` odd primes, by running the search in the kernel (the upper bound is the
  exhaustive part). `GoldbachGaps/CoverDepthRun.lean` adds `163` for eight moduli, `181` for
  nine, and lower bounds beyond.
* `IsDepth.unique`, `IsDepth.prime`, `IsDepth.lt_cons`: the depth is unique, it is an odd prime,
  and **a new modulus always increases it** (it can strike the first unstruck prime).

What the depth says about the least Goldbach summand:

* `least_summand_le_depth`: **an upper bound.** The least summand of an even `N` is at most the
  depth of the odd primes up to `√N`: every odd prime below the least summand is struck by the
  residues of `N` itself.
* `exists_isSummand_le_depth`: **Goldbach by covering.** If the depth `D` of the odd primes up
  to `√N` is at most `N - 3`, then `N` is a sum of two primes, one of them at most `D`. No
  primality test of any `N - q` is involved. "The odd primes below `y` cannot strike every odd
  prime below `y² - 2`", for all `y`, would be Goldbach's conjecture, and the exact values show
  how much room there is: depth `163` against `29² = 841` for eight moduli.
* `exists_isLeastSummand_ge_depth`: **a lower bound**, from Dirichlet's theorem
  (`exists_isLeastSummand_of_cover`): arbitrarily large even numbers have least summand at
  least the depth.
* `isRecord_and_isDepth`: the terms `6, 12, 30, 98` of A025018 **attain** the depth of their
  own small primes (`3, 5, 7, 19`): they are the best residue vectors on no modulus, on `3`, on
  `3, 5` and on `3, 5, 7`. From `220` on a term stays below the depth
  (`isRecord_220_and_isDepth`: `g(220) = 23` against `43` for `3, 5, 7, 11, 13`). The reason is
  a count: an even `N` below the next prime square carries one residue vector, and from four
  moduli on there are far more vectors (`2·3·5·7·11 = 2310`) than such `N` (below `13² = 169`),
  so the best vector does not occur in time and the record is the best among those that do.
* `coversBelow_of_complete_cover`: a complete cover in the sense of
  `GoldbachGaps/CompleteCover.lean` is a lower bound for the depth of the odd primes it uses.
-/

set_option Elab.async false

namespace GoldbachGaps.CoverDepth

open BitSieve

/-- Some residue vector on `mods` strikes every member of `qs`. -/
def CoversList (mods qs : List ℕ) : Prop :=
  ∃ a : ℕ → ℕ, ∀ q ∈ qs, ∃ r ∈ mods, q ≡ a r [MOD r]

/-- Some residue vector on `mods` strikes every odd prime below `y`. -/
def CoversBelow (mods : List ℕ) (y : ℕ) : Prop :=
  ∃ a : ℕ → ℕ, ∀ q, q.Prime → q ≠ 2 → q < y → ∃ r ∈ mods, q ≡ a r [MOD r]

/-- `D` is the cover depth of `mods`: every odd prime below `D` can be struck by one vector,
and no vector strikes every odd prime up to `D`. -/
def IsDepth (mods : List ℕ) (D : ℕ) : Prop :=
  CoversBelow mods D ∧ ¬ CoversBelow mods (D + 1)

theorem CoversBelow.mono {mods : List ℕ} {y y' : ℕ} (h : CoversBelow mods y) (hy : y' ≤ y) :
    CoversBelow mods y' := by
  obtain ⟨a, ha⟩ := h
  exact ⟨a, fun q hq h2 hlt => ha q hq h2 (by omega)⟩

/-- The depth is unique. -/
theorem IsDepth.unique {mods : List ℕ} {D D' : ℕ} (h : IsDepth mods D) (h' : IsDepth mods D') :
    D = D' := by
  by_contra hne
  rcases Nat.lt_or_gt_of_ne hne with hlt | hlt
  · exact h.2 (h'.1.mono (by omega))
  · exact h'.2 (h.1.mono (by omega))

/-- The depth is an odd prime. -/
theorem IsDepth.prime {mods : List ℕ} {D : ℕ} (h : IsDepth mods D) : D.Prime ∧ D ≠ 2 := by
  by_contra hno
  obtain ⟨a, ha⟩ := h.1
  refine h.2 ⟨a, fun q hq h2 hlt => ?_⟩
  rcases Nat.lt_or_ge q D with hlt' | hge
  · exact ha q hq h2 hlt'
  · have e : q = D := by omega
    subst e
    exact absurd ⟨hq, h2⟩ hno

/-- A new modulus strikes the first unstruck prime. -/
theorem CoversBelow.cons {mods : List ℕ} {y r : ℕ} (h : CoversBelow mods y) (hr : r ∉ mods) :
    CoversBelow (r :: mods) (y + 1) := by
  obtain ⟨a, ha⟩ := h
  refine ⟨Function.update a r y, fun q hq h2 hlt => ?_⟩
  rcases Nat.lt_or_ge q y with hlt' | hge
  · obtain ⟨r', hr', hmod⟩ := ha q hq h2 hlt'
    have hne : r' ≠ r := fun e => hr (e ▸ hr')
    exact ⟨r', List.mem_cons_of_mem _ hr', by rw [Function.update_of_ne hne]; exact hmod⟩
  · have e : q = y := by omega
    subst e
    exact ⟨r, List.mem_cons_self, by rw [Function.update_self]⟩

/-- **The depth is strictly increasing in the moduli.** -/
theorem IsDepth.lt_cons {mods : List ℕ} {D D' r : ℕ} (h : IsDepth mods D) (hr : r ∉ mods)
    (h' : IsDepth (r :: mods) D') : D < D' := by
  by_contra hle
  exact h'.2 ((h.1.cons hr).mono (by omega))

/-! ### The search -/

/-- Can the primes of the list all be struck, one class per modulus? Depth first: the least
unstruck prime must be struck by one of the moduli left. -/
def search : ℕ → List ℕ → List ℕ → Bool
  | _, _, [] => true
  | 0, _, _ :: _ => false
  | f + 1, mods, q :: qs =>
    mods.any fun r => search f (mods.erase r) (qs.filter fun p => p % r != q % r)

theorem search_nil (f : ℕ) (mods : List ℕ) : search f mods [] = true := by
  cases f <;> rfl

/-- **The search is correct.** -/
theorem search_iff : ∀ (f : ℕ) (mods qs : List ℕ), mods.Nodup → mods.length ≤ f →
    (search f mods qs = true ↔ CoversList mods qs)
  | f, mods, [], _, _ => by
    rw [search_nil]
    exact ⟨fun _ => ⟨fun _ => 0, fun q hq => absurd hq (by simp)⟩, fun _ => rfl⟩
  | 0, mods, q :: qs, _, hlen => by
    have hm : mods = [] := List.length_eq_zero_iff.mp (by omega)
    subst hm
    simp only [search]
    constructor
    · intro h
      exact absurd h (by simp)
    · rintro ⟨a, ha⟩
      obtain ⟨r, hr, _⟩ := ha q List.mem_cons_self
      exact absurd hr (by simp)
  | f + 1, mods, q :: qs, hnd, hlen => by
    simp only [search, List.any_eq_true]
    constructor
    · rintro ⟨r, hr, hs⟩
      have hlen' : (mods.erase r).length ≤ f := by
        rw [List.length_erase_of_mem hr]
        omega
      obtain ⟨a, ha⟩ := (search_iff f _ _ (hnd.erase r) hlen').mp hs
      refine ⟨Function.update a r q, fun p hp => ?_⟩
      by_cases hpr : p % r = q % r
      · exact ⟨r, hr, by rw [Function.update_self]; exact hpr⟩
      · have hp' : p ∈ qs.filter fun p => p % r != q % r := by
          rcases List.mem_cons.mp hp with rfl | hp
          · exact absurd rfl hpr
          · exact List.mem_filter.mpr ⟨hp, by simpa using hpr⟩
        obtain ⟨r', hr', hmod⟩ := ha p hp'
        have hmem := hnd.mem_erase_iff.mp hr'
        exact ⟨r', hmem.2, by rw [Function.update_of_ne hmem.1]; exact hmod⟩
    · rintro ⟨a, ha⟩
      obtain ⟨r, hr, hq⟩ := ha q List.mem_cons_self
      have hlen' : (mods.erase r).length ≤ f := by
        rw [List.length_erase_of_mem hr]
        omega
      refine ⟨r, hr, (search_iff f _ _ (hnd.erase r) hlen').mpr ⟨a, fun p hp => ?_⟩⟩
      obtain ⟨hp1, hp2⟩ := List.mem_filter.mp hp
      have hpr : p % r ≠ q % r := by simpa using hp2
      obtain ⟨r', hr', hmod⟩ := ha p (List.mem_cons_of_mem _ hp1)
      have hne : r' ≠ r := by
        rintro rfl
        exact hpr (hmod.trans hq.symm)
      exact ⟨r', hnd.mem_erase_iff.mpr ⟨hne, hr'⟩, hmod⟩

/-- The odd primes below `y` (correct for `y ≤ 5929`). -/
def oddPrimesBelow (y : ℕ) : List ℕ := (sievePrimesBelow y).filter fun p => p != 2

theorem mem_oddPrimesBelow {y p : ℕ} (hy : y ≤ 5929) :
    p ∈ oddPrimesBelow y ↔ p.Prime ∧ p ≠ 2 ∧ p < y := by
  simp only [oddPrimesBelow, List.mem_filter, mem_sievePrimesBelow hy, bne_iff_ne, ne_eq]
  tauto

theorem coversBelow_iff_search {mods : List ℕ} {y : ℕ} (hy : y ≤ 5929) (hnd : mods.Nodup) :
    CoversBelow mods y ↔ search mods.length mods (oddPrimesBelow y) = true := by
  rw [search_iff _ _ _ hnd le_rfl]
  constructor
  · rintro ⟨a, ha⟩
    refine ⟨a, fun q hq => ?_⟩
    obtain ⟨h1, h2, h3⟩ := (mem_oddPrimesBelow hy).mp hq
    exact ha q h1 h2 h3
  · rintro ⟨a, ha⟩
    exact ⟨a, fun q h1 h2 h3 => ha q ((mem_oddPrimesBelow hy).mpr ⟨h1, h2, h3⟩)⟩

/-- The depth from two runs of the search. -/
theorem isDepth_of_search {mods : List ℕ} {D : ℕ} (hD : D + 1 ≤ 5929) (hnd : mods.Nodup)
    (h1 : search mods.length mods (oddPrimesBelow D) = true)
    (h2 : search mods.length mods (oddPrimesBelow (D + 1)) = false) : IsDepth mods D := by
  refine ⟨(coversBelow_iff_search (by omega) hnd).mpr h1, fun h => ?_⟩
  rw [coversBelow_iff_search hD hnd, h2] at h
  exact absurd h (by simp)

/-- A cover from an explicit residue vector. -/
theorem coversBelow_of_check {mods : List ℕ} {y : ℕ} (hy : y ≤ 5929) (a : ℕ → ℕ)
    (h : ((oddPrimesBelow y).all fun q => mods.any fun r => q % r == a r % r) = true) :
    CoversBelow mods y := by
  refine ⟨a, fun q hq h2 hlt => ?_⟩
  have h1 := List.all_eq_true.mp h q ((mem_oddPrimesBelow hy).mpr ⟨hq, h2, hlt⟩)
  obtain ⟨r, hr, hqr⟩ := List.any_eq_true.mp h1
  exact ⟨r, hr, beq_iff_eq.mp hqr⟩

/-- The depth from a cover and one run of the search. -/
theorem isDepth_of_cover {mods : List ℕ} {D : ℕ} (hD : D + 1 ≤ 5929) (hnd : mods.Nodup)
    (h1 : CoversBelow mods D)
    (h2 : search mods.length mods (oddPrimesBelow (D + 1)) = false) : IsDepth mods D := by
  refine ⟨h1, fun h => ?_⟩
  rw [coversBelow_iff_search hD hnd, h2] at h
  exact absurd h (by simp)

/-! ### Splitting a long search into several kernel checks

The kernel keeps every intermediate term of a reduction, about 45 kB per node of this search,
so the search for eight moduli (`109,601` nodes) is cut after the first step and each of the
eight pieces is checked on its own, and the search for nine moduli after the second step, in
72 pieces (`GoldbachGaps/CoverDepthRun.lean`). -/

/-- One branch of the search: the modulus `r` strikes the first prime `q`. -/
def branch (f : ℕ) (mods : List ℕ) (q : ℕ) (qs : List ℕ) (r : ℕ) : Bool :=
  search f (mods.erase r) (qs.filter fun p => p % r != q % r)

theorem search_cons_eq_false {f : ℕ} {mods : List ℕ} {q : ℕ} {qs : List ℕ}
    (h : ∀ r ∈ mods, branch f mods q qs r = false) : search (f + 1) mods (q :: qs) = false := by
  show (mods.any fun r => search f (mods.erase r) (qs.filter fun p => p % r != q % r)) = false
  rw [List.any_eq_false]
  intro r hr hs
  have h1 := h r hr
  unfold branch at h1
  rw [h1] at hs
  exact absurd hs (by simp)

/-- Two steps of the search: `r₁` takes the first row and `r₂` the next row still left. -/
def branch2 (f : ℕ) (mods : List ℕ) (q : ℕ) (qs : List ℕ) (r₁ r₂ : ℕ) : Bool :=
  match qs.filter (fun p => p % r₁ != q % r₁) with
  | [] => true
  | q₂ :: qs₂ => branch f (mods.erase r₁) q₂ qs₂ r₂

theorem branch_eq_false {f : ℕ} {mods : List ℕ} {q : ℕ} {qs : List ℕ} {r₁ : ℕ} (r₀ : ℕ)
    (h0 : r₀ ∈ mods.erase r₁)
    (h : ∀ r₂ ∈ mods.erase r₁, branch2 f mods q qs r₁ r₂ = false) :
    branch (f + 1) mods q qs r₁ = false := by
  unfold branch
  have h1 := h r₀ h0
  unfold branch2 at h1
  cases hq : qs.filter (fun p => p % r₁ != q % r₁) with
  | nil =>
    rw [hq] at h1
    exact absurd h1 (by simp)
  | cons q₂ qs₂ =>
    refine search_cons_eq_false fun r₂ hr₂ => ?_
    have h2 := h r₂ hr₂
    unfold branch2 at h2
    rw [hq] at h2
    exact h2

/-! ### The exact values for the first seven odd primes -/

theorem isDepth_0 : IsDepth [] 3 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_1 : IsDepth [3] 5 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_2 : IsDepth [3, 5] 7 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_3 : IsDepth [3, 5, 7] 19 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_4 : IsDepth [3, 5, 7, 11] 31 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_5 : IsDepth [3, 5, 7, 11, 13] 43 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_6 : IsDepth [3, 5, 7, 11, 13, 17] 67 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

theorem isDepth_7 : IsDepth [3, 5, 7, 11, 13, 17, 19] 103 :=
  isDepth_of_search (by norm_num) (by decide) (by decide +kernel) (by decide +kernel)

/-! ### What the depth says about the least Goldbach summand -/

/-- The residues of an even `N` modulo the odd primes up to `√N` strike every odd prime `q`
for which `N - q` is composite. -/
theorem strikes_of_not_prime {N q : ℕ} {mods : List ℕ} (hE : Even N)
    (hmods : ∀ r, r.Prime → r ≠ 2 → r * r ≤ N → r ∈ mods)
    (hq : q.Prime) (h2 : q ≠ 2) (hqN : q + 2 ≤ N) (hnp : ¬ (N - q).Prime) :
    ∃ r ∈ mods, q ≡ N [MOD r] := by
  obtain ⟨r, hr, hsq, hdvd⟩ := (RecordWalk.not_prime_iff_exists_wheel (by omega)).mp hnp
  have hr2 : r ≠ 2 := by
    rintro rfl
    have hqodd := hq.eq_two_or_odd.resolve_left h2
    obtain ⟨k, hk⟩ := hE
    omega
  exact ⟨r, hmods r hr hr2 (le_trans hsq (Nat.sub_le N q)),
    (Nat.modEq_iff_dvd' (by omega)).mpr hdvd⟩

/-- The residues of an even `N` modulo the odd primes up to `√N` strike every odd prime below
its least Goldbach summand. -/
theorem coversBelow_of_isLeastSummand {N g : ℕ} {mods : List ℕ} (hE : Even N)
    (hmods : ∀ r, r.Prime → r ≠ 2 → r * r ≤ N → r ∈ mods) (hl : IsLeastSummand N g) :
    CoversBelow mods g := by
  have hNg : 2 ≤ N - g := hl.1.2.two_le
  refine ⟨fun _ => N, fun q hq h2 hlt => ?_⟩
  exact strikes_of_not_prime hE hmods hq h2 (by omega) fun hp => by
    have := hl.2 q ⟨hq, hp⟩
    omega

/-- **An upper bound for the least Goldbach summand:** it is at most the cover depth of the
odd primes up to `√N`. -/
theorem least_summand_le_depth {N g D : ℕ} {mods : List ℕ} (hE : Even N)
    (hmods : ∀ r, r.Prime → r ≠ 2 → r * r ≤ N → r ∈ mods) (hl : IsLeastSummand N g)
    (hD : IsDepth mods D) : g ≤ D := by
  by_contra hlt
  exact hD.2 ((coversBelow_of_isLeastSummand hE hmods hl).mono (by omega))

/-- **Goldbach by covering.** If the cover depth `D` of the odd primes up to `√N` is at most
`N - 3`, then `N` is a sum of two primes, one of them at most `D`. -/
theorem exists_isSummand_le_depth {N D : ℕ} {mods : List ℕ} (hE : Even N)
    (hmods : ∀ r, r.Prime → r ≠ 2 → r * r ≤ N → r ∈ mods) (hD : IsDepth mods D)
    (hN : D + 3 ≤ N) : ∃ q ≤ D, IsSummand N q := by
  by_contra hno
  push Not at hno
  refine hD.2 ⟨fun _ => N, fun q hq h2 hlt => ?_⟩
  exact strikes_of_not_prime hE hmods hq h2 (by omega) fun hp => hno q (by omega) ⟨hq, hp⟩

/-- The same with the moduli given as the odd primes below `y`, for `N < y²`. -/
theorem exists_isSummand_of_lt_sq {N D y : ℕ} (hy : y ≤ 5929) (hE : Even N)
    (hD : IsDepth (oddPrimesBelow y) D) (hDN : D + 3 ≤ N) (hN : N < y * y) :
    ∃ q ≤ D, IsSummand N q :=
  exists_isSummand_le_depth hE (fun r hr h2 hsq => (mem_oddPrimesBelow hy).mpr ⟨hr, h2, by
    by_contra hge
    have := Nat.mul_le_mul (not_lt.mp hge) (not_lt.mp hge)
    omega⟩) hD hDN

/-- **A lower bound for the least Goldbach summand** (Dirichlet's theorem, through
`exists_isLeastSummand_of_cover`): if distinct odd primes strike every odd prime below `D`,
arbitrarily large even numbers have least summand at least `D`. -/
theorem exists_isLeastSummand_ge_depth {mods : List ℕ} {D : ℕ}
    (hmods : ∀ r ∈ mods, r.Prime ∧ r ≠ 2) (hD : CoversBelow mods D) (n : ℕ) :
    ∃ N > n, Even N ∧ ∃ g, IsLeastSummand N g ∧ D ≤ g := by
  obtain ⟨a, ha⟩ := hD
  obtain ⟨N, hN, hE, -, g, hg, hDg⟩ :=
    exists_isLeastSummand_of_cover (R := mods.toFinset) (a := a) (Q := D)
      (fun r hr => hmods r (List.mem_toFinset.mp hr))
      (fun q hq h2 hlt => by
        obtain ⟨r, hr, hmod⟩ := ha q hq h2 hlt
        exact ⟨r, List.mem_toFinset.mpr hr, hmod⟩) n
  exact ⟨N, hN, hE, g, hg, hDg⟩

/-- A complete cover with divisors up to `R` is a cover by the odd primes up to `R`. -/
theorem coversBelow_of_complete_cover {N Q R : ℕ} (hR : R + 1 ≤ 5929) (hE : Even N)
    (h : ∀ q < Q, q.Prime → ∃ r, 2 ≤ r ∧ r ≤ R ∧ r < N - q ∧ r ∣ N - q) :
    CoversBelow (oddPrimesBelow (R + 1)) Q := by
  refine ⟨fun _ => N, fun q hq h2 hlt => ?_⟩
  obtain ⟨r, hr2, hrR, hrlt, hdvd⟩ := h q hlt hq
  have hp : r.minFac.Prime := Nat.minFac_prime (by omega)
  have hpdvd : r.minFac ∣ N - q := (Nat.minFac_dvd r).trans hdvd
  have hple : r.minFac ≤ r := Nat.minFac_le (by omega)
  have hp2 : r.minFac ≠ 2 := by
    intro e
    rw [e] at hpdvd
    have hqodd := hq.eq_two_or_odd.resolve_left h2
    obtain ⟨k, hk⟩ := hE
    omega
  exact ⟨r.minFac, (mem_oddPrimesBelow hR).mpr ⟨hp, hp2, by omega⟩,
    (Nat.modEq_iff_dvd' (show q ≤ N by omega)).mpr hpdvd⟩

/-! ### The first terms of A025018 attain the depth -/

/-- **The terms `6`, `12`, `30`, `98` of A025018 attain the cover depth of the odd primes up to
their square roots** (none, `3`, `3, 5`, `3, 5, 7`): their values `3, 5, 7, 19` are the
largest that those primes can force, and by `least_summand_le_depth` no even number below the
next square does better. -/
theorem isRecord_and_isDepth :
    (IsRecord 6 3 ∧ IsDepth [] 3) ∧ (IsRecord 12 5 ∧ IsDepth [3] 5) ∧
      (IsRecord 30 7 ∧ IsDepth [3, 5] 7) ∧ (IsRecord 98 19 ∧ IsDepth [3, 5, 7] 19) := by
  refine ⟨⟨?_, isDepth_0⟩, ⟨?_, isDepth_1⟩, ⟨?_, isDepth_2⟩, ⟨?_, isDepth_3⟩⟩ <;>
    · rw [RecordGen.isRecord_iff_mem_terms20 (by norm_num)]
      decide

/-- From the sixth term on a term stays below the depth of its small primes: `220` has value
`23`, and `3, 5, 7, 11, 13` (the odd primes up to `√220`) could force `43`, with a residue
vector that no even number below `17² = 289` carries. -/
theorem isRecord_220_and_isDepth : IsRecord 220 23 ∧ IsDepth [3, 5, 7, 11, 13] 43 := by
  refine ⟨?_, isDepth_5⟩
  rw [RecordGen.isRecord_iff_mem_terms20 (by norm_num)]
  decide

end GoldbachGaps.CoverDepth
