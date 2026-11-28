import GoldbachGaps.CoverDepth

/-!
# The number of complete covers

`GoldbachGaps/CoverDepth.lean` asks whether *some* class vector on a list of moduli covers every
odd prime below `y`. This file counts them. A **class vector** on a finite set of moduli gives
every modulus `r` one residue class `a r < r`; it **covers** a row `q` when `q` lies in the class
of some modulus. `coverCount mods rows` is the number of class vectors on `mods` that cover every
row. With the odd primes up to `x` as moduli and the odd primes below `Q` as rows this is the
quantity `g0(x, Q)` of the research session (`goldbach/sublinear/README.md`, branch
`ccr-d4a17dd0-7uu03r`, "How many complete covers there are"), whose logarithm it measures to be
`θ(x) - c·Q/ln² x` with `c` near `1`. Nothing about that law is proved here. What is proved:

* `coverCount_eq_sum`, `coverCount_div_prod_eq_sum`: **the exact identity** behind the count,
  inclusion–exclusion over the sets `T` of rows that are left uncovered:

      coverCount mods rows / ∏ r  =  ∑ over T ⊆ rows of (-1)^|T| · ∏ r (1 - ν_r(T) / r),

  `ν_r(T)` (`nu r T`) being the number of residue classes modulo `r` that the rows of `T` occupy.
  The class vectors that cover no row of `T` are exactly those that avoid these classes, so
  there are `∏ r (r - ν_r(T))` of them (`card_uncovered`).
* `coverCount_empty`: with no row to cover the count is `∏ r` (this is `g0(x, 0) = e^θ(x)`).
* `coverCount_anti`: more rows, fewer covers.
* `coverCount_pos_iff`, `coversBelow_iff_coverCount_pos`, `isDepth_iff_coverCount`: the count is
  positive exactly when a cover exists, so the cover depth `D` of `CoverDepth.lean` is where the
  count reaches zero: positive for the odd primes below `D`, zero for those below `D + 1`.
* `coverCount_mul_prod_le`: **a lower bound from fewer moduli.** A cover on a subset of the moduli
  stays a cover whatever classes the other moduli take, so

      coverCount mods' rows · ∏ of the moduli in mods \ mods'  ≤  coverCount mods rows.

  In the research session's notation: if the odd primes up to `x'` can cover the odd primes below
  `Q`, then `ln g0(x, Q) ≥ θ(x) - θ(x')` for every `x ≥ x'`
  (`prod_le_coverCount_of_coversBelow`). `GoldbachGaps/CoverCountRun.lean` applies this to the
  certified covers.
-/

namespace GoldbachGaps.CoverCount

open Finset GoldbachGaps.CoverDepth

/-- A class vector on a finite set of moduli: one residue class `a r`, a number below `r`, for
every modulus `r`. -/
abbrev ClassVector (mods : Finset ℕ) : Type := (r : mods) → Fin r.1

/-- The class vector `a` covers the row `q`: `q` lies in the class of some modulus. -/
def Covers {mods : Finset ℕ} (a : ClassVector mods) (q : ℕ) : Prop :=
  ∃ r : mods, q % r.1 = (a r).1

instance {mods : Finset ℕ} (a : ClassVector mods) (q : ℕ) : Decidable (Covers a q) := by
  unfold Covers; infer_instance

/-- **The number of complete covers**: the class vectors on `mods` that cover every row. -/
def coverCount (mods rows : Finset ℕ) : ℕ :=
  #{a : ClassVector mods | ∀ q ∈ rows, Covers a q}

/-- The number of residue classes modulo `r` that the rows of `T` occupy. -/
def nu (r : ℕ) (T : Finset ℕ) : ℕ := #(T.image (· % r))

theorem nu_le {r : ℕ} (hr : 0 < r) (T : Finset ℕ) : nu r T ≤ r := by
  have h : T.image (· % r) ⊆ range r := fun x hx => by
    obtain ⟨q, -, rfl⟩ := mem_image.1 hx
    exact mem_range.2 (Nat.mod_lt _ hr)
  simpa [nu] using card_le_card h

/-- The classes modulo `r` that contain no row of `T`: there are `r - ν_r(T)` of them. -/
theorem card_free_classes (r : ℕ) (T : Finset ℕ) :
    #{c : Fin r | ∀ q ∈ T, q % r ≠ c.1} = r - nu r T := by
  rcases Nat.eq_zero_or_pos r with rfl | hr
  · simp
  · have h1 : #{c : Fin r | ∀ q ∈ T, q % r ≠ c.1} = #(range r \ T.image (· % r)) := by
      rw [← card_map Fin.valEmbedding]
      congr 1
      ext x
      simp only [mem_map, mem_filter, mem_univ, true_and, Fin.valEmbedding_apply, mem_sdiff,
        mem_range, mem_image, not_exists, not_and]
      constructor
      · rintro ⟨c, hc, rfl⟩
        exact ⟨c.2, fun q hq => hc q hq⟩
      · rintro ⟨hx, h⟩
        exact ⟨⟨x, hx⟩, fun q hq => h q hq, rfl⟩
    have h2 : T.image (· % r) ⊆ range r := fun x hx => by
      obtain ⟨q, -, rfl⟩ := mem_image.1 hx
      exact mem_range.2 (Nat.mod_lt _ hr)
    rw [h1, card_sdiff_of_subset h2, card_range]
    rfl

/-- The class vectors that cover no row of `T` are those that avoid, modulo every `r`, the
classes of the rows of `T`: there are `∏ r (r - ν_r(T))` of them. -/
theorem card_uncovered (mods T : Finset ℕ) :
    #{a : ClassVector mods | ∀ q ∈ T, ¬ Covers a q} = ∏ r ∈ mods, (r - nu r T) := by
  have h : ({a : ClassVector mods | ∀ q ∈ T, ¬ Covers a q} : Finset (ClassVector mods)) =
      Fintype.piFinset fun r : mods => {c : Fin r.1 | ∀ q ∈ T, q % r.1 ≠ c.1} := by
    ext a
    simp only [mem_filter, mem_univ, true_and, Fintype.mem_piFinset, Covers, not_exists]
    exact ⟨fun h r q hq => h q hq r, fun h q hq r => h r q hq⟩
  rw [h, Fintype.card_piFinset]
  simp only [card_free_classes]
  exact prod_coe_sort mods fun r => r - nu r T

/-- **The number of complete covers, by inclusion–exclusion** over the sets `T` of rows left
uncovered. (The subtraction is that of natural numbers; `ν_r(T) ≤ r` for a positive modulus.) -/
theorem coverCount_eq_sum (mods rows : Finset ℕ) :
    (coverCount mods rows : ℤ) =
      ∑ T ∈ rows.powerset, (-1) ^ #T * ∏ r ∈ mods, ((r - nu r T : ℕ) : ℤ) := by
  have h := inclusion_exclusion_card_inf_compl rows
    fun q => ({a : ClassVector mods | ¬ Covers a q} : Finset (ClassVector mods))
  have h1 : (rows.inf fun q =>
      ({a : ClassVector mods | ¬ Covers a q} : Finset (ClassVector mods))ᶜ) =
      ({a : ClassVector mods | ∀ q ∈ rows, Covers a q} : Finset (ClassVector mods)) := by
    ext a; simp [Finset.mem_inf]
  have h2 : ∀ T : Finset ℕ, (T.inf fun q =>
      ({a : ClassVector mods | ¬ Covers a q} : Finset (ClassVector mods))) =
      ({a : ClassVector mods | ∀ q ∈ T, ¬ Covers a q} : Finset (ClassVector mods)) := by
    intro T; ext a; simp [Finset.mem_inf]
  rw [h1] at h
  unfold coverCount
  rw [h]
  refine sum_congr rfl fun T _ => ?_
  rw [h2, card_uncovered, Nat.cast_prod]

/-- **The identity as the research session states it**: the fraction of class vectors that are
complete covers is `∑ over T ⊆ rows of (-1)^|T| ∏ r (1 - ν_r(T)/r)`. -/
theorem coverCount_div_prod_eq_sum (mods rows : Finset ℕ) (hpos : ∀ r ∈ mods, 0 < r) :
    (coverCount mods rows : ℚ) / ∏ r ∈ mods, (r : ℚ) =
      ∑ T ∈ rows.powerset, (-1) ^ #T * ∏ r ∈ mods, (1 - (nu r T : ℚ) / r) := by
  have h := congrArg (fun z : ℤ => (z : ℚ)) (coverCount_eq_sum mods rows)
  simp only [Int.cast_natCast, Int.cast_sum, Int.cast_mul, Int.cast_pow, Int.cast_neg,
    Int.cast_one, Int.cast_prod] at h
  rw [h, sum_div]
  refine sum_congr rfl fun T _ => ?_
  rw [mul_div_assoc, ← prod_div_distrib]
  congr 1
  refine prod_congr rfl fun r hr => ?_
  have hr0 : (r : ℚ) ≠ 0 := by exact_mod_cast (hpos r hr).ne'
  rw [Nat.cast_sub (nu_le (hpos r hr) T)]
  field_simp

/-- With no row to cover, every class vector counts: `∏ r` of them. -/
theorem coverCount_empty (mods : Finset ℕ) : coverCount mods ∅ = ∏ r ∈ mods, r := by
  have h := card_uncovered mods ∅
  simp only [notMem_empty, false_imp_iff, implies_true, filter_true, nu, image_empty,
    card_empty, Nat.sub_zero] at h
  simpa [coverCount] using h

/-- More rows, fewer covers. -/
theorem coverCount_anti (mods : Finset ℕ) {rows rows' : Finset ℕ} (h : rows ⊆ rows') :
    coverCount mods rows' ≤ coverCount mods rows :=
  card_le_card fun a ha => by
    simp only [mem_filter, mem_univ, true_and] at ha ⊢
    exact fun q hq => ha q (h hq)

theorem coverCount_le_prod (mods rows : Finset ℕ) : coverCount mods rows ≤ ∏ r ∈ mods, r :=
  (coverCount_anti mods (empty_subset rows)).trans_eq (coverCount_empty mods)

/-- The count is positive exactly when some residue vector covers every row, in the sense of
`CoverDepth.CoversList`. -/
theorem coverCount_pos_iff (mods rows : Finset ℕ) (hpos : ∀ r ∈ mods, 0 < r) :
    0 < coverCount mods rows ↔ ∃ a : ℕ → ℕ, ∀ q ∈ rows, ∃ r ∈ mods, q ≡ a r [MOD r] := by
  unfold coverCount
  rw [card_pos]
  constructor
  · rintro ⟨a, ha⟩
    have ha' := (mem_filter.1 ha).2
    refine ⟨fun r => if h : r ∈ mods then (a ⟨r, h⟩).1 else 0, fun q hq => ?_⟩
    obtain ⟨r, hr⟩ := ha' q hq
    refine ⟨r.1, r.2, ?_⟩
    simp only [r.2, dite_true]
    unfold Nat.ModEq
    rw [hr, Nat.mod_eq_of_lt (a r).2]
  · rintro ⟨a, ha⟩
    refine ⟨fun r => ⟨a r.1 % r.1, Nat.mod_lt _ (hpos r.1 r.2)⟩,
      mem_filter.2 ⟨mem_univ _, fun q hq => ?_⟩⟩
    obtain ⟨r, hr, h⟩ := ha q hq
    exact ⟨⟨r, hr⟩, h⟩

/-- The rows of the depth problem: the odd primes below `y`. -/
def rowsBelow (y : ℕ) : Finset ℕ := {q ∈ range y | q.Prime ∧ q ≠ 2}

theorem mem_rowsBelow {y q : ℕ} : q ∈ rowsBelow y ↔ q.Prime ∧ q ≠ 2 ∧ q < y := by
  simp only [rowsBelow, mem_filter, mem_range]
  tauto

theorem rowsBelow_mono {y y' : ℕ} (h : y ≤ y') : rowsBelow y ⊆ rowsBelow y' := fun q hq => by
  rw [mem_rowsBelow] at hq ⊢
  exact ⟨hq.1, hq.2.1, by omega⟩

/-- `CoversBelow mods y` of `CoverDepth.lean` says that the count is positive. -/
theorem coversBelow_iff_coverCount_pos {mods : List ℕ} (hpos : ∀ r ∈ mods, 0 < r) (y : ℕ) :
    CoversBelow mods y ↔ 0 < coverCount mods.toFinset (rowsBelow y) := by
  rw [coverCount_pos_iff _ _ (fun r hr => hpos r (List.mem_toFinset.1 hr))]
  constructor
  · rintro ⟨a, ha⟩
    refine ⟨a, fun q hq => ?_⟩
    obtain ⟨hp, h2, hlt⟩ := mem_rowsBelow.1 hq
    obtain ⟨r, hr, h⟩ := ha q hp h2 hlt
    exact ⟨r, List.mem_toFinset.2 hr, h⟩
  · rintro ⟨a, ha⟩
    refine ⟨a, fun q hp h2 hlt => ?_⟩
    obtain ⟨r, hr, h⟩ := ha q (mem_rowsBelow.2 ⟨hp, h2, hlt⟩)
    exact ⟨r, List.mem_toFinset.1 hr, h⟩

/-- **The depth is where the count reaches zero.** -/
theorem isDepth_iff_coverCount {mods : List ℕ} (hpos : ∀ r ∈ mods, 0 < r) (D : ℕ) :
    IsDepth mods D ↔
      0 < coverCount mods.toFinset (rowsBelow D) ∧
        coverCount mods.toFinset (rowsBelow (D + 1)) = 0 := by
  unfold IsDepth
  rw [coversBelow_iff_coverCount_pos hpos, coversBelow_iff_coverCount_pos hpos,
    Nat.pos_iff_ne_zero (n := coverCount _ (rowsBelow (D + 1))), not_not]

/-- **A lower bound from fewer moduli.** A cover on `mods' ⊆ mods` remains a cover whatever
classes the remaining moduli take. -/
theorem coverCount_mul_prod_le {mods' mods : Finset ℕ} (hsub : mods' ⊆ mods) (rows : Finset ℕ) :
    coverCount mods' rows * ∏ r ∈ mods \ mods', r ≤ coverCount mods rows := by
  classical
  -- glue a class vector on `mods'` and one on `mods \ mods'`
  let glue : ClassVector mods' × ClassVector (mods \ mods') → ClassVector mods := fun p r =>
    if h : r.1 ∈ mods' then p.1 ⟨r.1, h⟩ else p.2 ⟨r.1, mem_sdiff.2 ⟨r.2, h⟩⟩
  have hcard : #(({b : ClassVector mods' | ∀ q ∈ rows, Covers b q} : Finset _) ×ˢ
      (univ : Finset (ClassVector (mods \ mods')))) =
      coverCount mods' rows * ∏ r ∈ mods \ mods', r := by
    rw [card_product, card_univ, Fintype.card_pi]
    simp only [Fintype.card_fin]
    rw [prod_coe_sort (mods \ mods') fun r => r]
    rfl
  rw [← hcard]
  refine card_le_card_of_injOn glue (fun p hp => ?_) (fun p hp p' hp' hpp' => ?_)
  · -- the glued vector is a cover
    have hp1 := (mem_filter.1 (mem_product.1 hp).1).2
    refine mem_filter.2 ⟨mem_univ _, fun q hq => ?_⟩
    obtain ⟨r, hr⟩ := hp1 q hq
    refine ⟨⟨r.1, hsub r.2⟩, ?_⟩
    simp only [glue, r.2, dite_true]
    exact hr
  · -- gluing is injective
    refine Prod.ext (funext fun r => ?_) (funext fun r => ?_)
    · have h := congrFun hpp' ⟨r.1, hsub r.2⟩
      simpa only [glue, r.2, dite_true] using h
    · have hr := mem_sdiff.1 r.2
      have h := congrFun hpp' ⟨r.1, hr.1⟩
      simpa only [glue, hr.2, dite_false] using h

/-- **`ln g0(x, Q) ≥ θ(x) - θ(x')`.** If the moduli `mods'` can cover the odd primes below `y`,
then every larger set of moduli has at least as many complete covers of them as the product of
its other moduli. -/
theorem prod_le_coverCount_of_coversBelow {mods' : List ℕ} (hpos : ∀ r ∈ mods', 0 < r) {y : ℕ}
    (h : CoversBelow mods' y) {mods : Finset ℕ} (hsub : mods'.toFinset ⊆ mods) :
    ∏ r ∈ mods \ mods'.toFinset, r ≤ coverCount mods (rowsBelow y) := by
  have h1 := (coversBelow_iff_coverCount_pos hpos y).1 h
  calc ∏ r ∈ mods \ mods'.toFinset, r
      ≤ coverCount mods'.toFinset (rowsBelow y) * ∏ r ∈ mods \ mods'.toFinset, r :=
        Nat.le_mul_of_pos_left _ h1
    _ ≤ coverCount mods (rowsBelow y) := coverCount_mul_prod_le hsub _

/-! ### The research session's `g0(x, Q)` -/

/-- `g0 x Q`: the number of class vectors modulo the odd primes up to `x` that cover every odd
prime below `Q`. -/
def g0 (x Q : ℕ) : ℕ := coverCount (rowsBelow (x + 1)) (rowsBelow Q)

/-- `g0(x, 0)` is the product of the odd primes up to `x`. -/
theorem g0_zero (x : ℕ) : g0 x 0 = ∏ r ∈ rowsBelow (x + 1), r := by
  have h : rowsBelow 0 = ∅ := by
    ext q; simp [mem_rowsBelow]
  rw [g0, h, coverCount_empty]

theorem g0_anti (x : ℕ) {Q Q' : ℕ} (h : Q ≤ Q') : g0 x Q' ≤ g0 x Q :=
  coverCount_anti _ (rowsBelow_mono h)

/-- The identity for `g0`: the fraction of class vectors modulo the odd primes up to `x` that
cover every odd prime below `Q`. -/
theorem g0_div_prod_eq_sum (x Q : ℕ) :
    (g0 x Q : ℚ) / ∏ r ∈ rowsBelow (x + 1), (r : ℚ) =
      ∑ T ∈ (rowsBelow Q).powerset,
        (-1) ^ #T * ∏ r ∈ rowsBelow (x + 1), (1 - (nu r T : ℚ) / r) :=
  coverCount_div_prod_eq_sum _ _ fun _ hr => (mem_rowsBelow.1 hr).1.pos

/-- `g0(x', Q)` times the product of the odd primes in `(x', x]` is at most `g0(x, Q)`. -/
theorem g0_mul_prod_le {x' x : ℕ} (h : x' ≤ x) (Q : ℕ) :
    g0 x' Q * ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (x' + 1), r ≤ g0 x Q :=
  coverCount_mul_prod_le (rowsBelow_mono (by omega)) _

/-- **`ln g0(x, Q) ≥ θ(x) - θ(x')`** as soon as the odd primes up to `x'` can cover the odd
primes below `Q`: the product of the odd primes in `(x', x]` is at most `g0(x, Q)`. -/
theorem prod_le_g0 {x' x Q : ℕ} (h : x' ≤ x) (hpos : 0 < g0 x' Q) :
    ∏ r ∈ rowsBelow (x + 1) \ rowsBelow (x' + 1), r ≤ g0 x Q :=
  (Nat.le_mul_of_pos_left _ hpos).trans (g0_mul_prod_le h Q)

/-- `g0 x Q` is positive exactly when the odd primes up to `x` can cover the odd primes below
`Q`. -/
theorem g0_pos_iff {mods : List ℕ} {x : ℕ} (hm : ∀ r, r ∈ mods ↔ r.Prime ∧ r ≠ 2 ∧ r < x + 1)
    (Q : ℕ) : 0 < g0 x Q ↔ CoversBelow mods Q := by
  have h : mods.toFinset = rowsBelow (x + 1) := by
    ext r; rw [List.mem_toFinset, hm, mem_rowsBelow]
  rw [coversBelow_iff_coverCount_pos (fun r hr => ((hm r).1 hr).1.pos), h, g0]

/-- The depth of the odd primes up to `x` is where `g0(x, ·)` reaches zero. -/
theorem isDepth_iff_g0 {mods : List ℕ} {x : ℕ} (hm : ∀ r, r ∈ mods ↔ r.Prime ∧ r ≠ 2 ∧ r < x + 1)
    (D : ℕ) : IsDepth mods D ↔ 0 < g0 x D ∧ g0 x (D + 1) = 0 := by
  unfold IsDepth
  rw [← g0_pos_iff hm, ← g0_pos_iff hm, Nat.pos_iff_ne_zero (n := g0 x (D + 1)), not_not]

/-- Two moduli, two rows, by hand: of the `15` class vectors on `3, 5` exactly two cover both `3`
and `5` (`(0, 0)` and `(2, 3)`), and none covers `3, 5, 7`: the depth of `3, 5` is `7`. -/
example : coverCount {3, 5} {3, 5} = 2 ∧ coverCount {3, 5} {3, 5, 7} = 0 := by
  decide

end GoldbachGaps.CoverCount
