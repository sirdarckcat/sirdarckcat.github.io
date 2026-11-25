import GoldbachGaps.Cap.SoftLists

/-!
# The inspection game: how many windows must be looked at

The research session's question of 25 November 2026 (18:40): on instances small enough to be exact,
what is the cheapest procedure that finds the optimum, counting only the candidates whose full score
it computes? Read literally the game is empty, because a score is a function of residues and
residues are free. It becomes a game once something is hidden, and the natural choice is the one the
search itself makes: what depends on the cover alone is free (for every cell, the rows its classes
leave, and therefore the least score any classes of the later primes could give it, its *free
bound*); the classes of a cell's members modulo the later primes are hidden until the cell is looked
at.

* **Proving the optimum** (`mem_of_certifies`, `certifies_of`, `card_le_of_certifies`). Worlds are
  assignments of a hidden part to every cell, the hidden parts of different cells being unrelated.
  A set of cells *certifies* the value `v` when every world that agrees with the true one on those
  cells has optimum `v`. Then a certifying set contains every cell whose free bound is below `v`,
  and the cells whose free bound is below `v` together with one cell that attains `v` certify. So
  the value of the game is the number of cells whose free bound is below the optimum, plus at most
  one: no adaptive procedure does better, and looking at the cells in increasing order of their
  free bound until the best score seen is at most the next bound does it, up to the ties at the
  optimum.

* **Finding a member at least as good as a given target** (`searchCost_le_of_perm`). If the cells
  hold one independently with chances `p_c`, what is seen in one cell says nothing about another,
  every procedure is an order, the expected number of cells looked at in the order `l` is
  `searchCost l`, and the decreasing order of the chances is the best.

* **The smallest instance** (`Example840.cells_below_optimum`, `Example840.cells_at_optimum`). Rows
  the 36 odd primes below 160, cells the 105 even classes modulo 210 (the design 3, 5, 7, four
  candidates each), later primes 11 and 13. Three cells have a free bound below the optimum 6, and
  seven have it equal to 6, the optimum's own cell among them: 4 cells (16 candidates of 420) prove
  the optimum, and no procedure in the game proves it with fewer than 3.

* **All seven designs at once** (`Example840.free_bounds_optimum`, `free_bounds_all_but_two`,
  `tie_152`). If the free bounds of all seven maximal pinnable designs may be used, every candidate
  is excluded: each lies in some cell none of whose numbers could be left with fewer than 6 rows,
  and each except 152 and 578 in a cell none of whose numbers could be left with fewer than 7. One
  full score, of 578, then proves the optimum. The bounds are 1,497 cells' worth of work for 420
  candidates, and they are strong only because two or three moduli lie outside each design.

`scripts/alignment/` has the numbers for the other instances: with one to three primes beyond the
line the cells that must be looked at are at most a few percent, and the share rises with every
later prime, to between 93% and all of them at the full depth of the miniature.
-/

namespace GoldbachGaps.Cap

/-! ### Proving the optimum -/

section Certify

variable {ι H : Type*}

/-- `v` is the least score in the world `w`: some cell attains it and none does better. -/
def IsOpt (score : ι → H → ℕ) (w : ι → H) (v : ℕ) : Prop :=
  (∃ c, score c (w c) = v) ∧ ∀ c, v ≤ score c (w c)

/-- Having looked at the cells of `S` in the world `w` proves that the optimum is `v`: every world
that agrees with `w` on `S` has optimum `v`. -/
def Certifies (score : ι → H → ℕ) (w : ι → H) (S : Set ι) (v : ℕ) : Prop :=
  ∀ w' : ι → H, (∀ c ∈ S, w' c = w c) → IsOpt score w' v

/-- **What must be looked at.** A cell that some hidden part would take below `v` is in every set
that certifies `v`. -/
theorem mem_of_certifies {score : ι → H → ℕ} {w : ι → H} {S : Set ι} {v : ℕ}
    (hS : Certifies score w S v) {c : ι} {h : H} (hc : score c h < v) : c ∈ S := by
  classical
  by_contra hcS
  have h1 : ∀ c' ∈ S, Function.update w c h c' = w c' := fun c' hc' =>
    Function.update_of_ne (fun e : c' = c => hcS (e ▸ hc')) _ _
  have h2 := (hS _ h1).2 c
  rw [Function.update_self] at h2
  omega

/-- **What is enough.** The cells that some hidden part would take below the optimum, together
with one cell that attains it, certify it. -/
theorem certifies_of {score : ι → H → ℕ} {w : ι → H} {S : Set ι} {v : ℕ}
    (hopt : ∀ c, v ≤ score c (w c)) {c₀ : ι} (hc₀ : c₀ ∈ S) (hv : score c₀ (w c₀) = v)
    (hS : ∀ c h, score c h < v → c ∈ S) : Certifies score w S v := by
  intro w' hw'
  refine ⟨⟨c₀, by rw [hw' c₀ hc₀, hv]⟩, fun c => ?_⟩
  by_cases hc : c ∈ S
  · rw [hw' c hc]
    exact hopt c
  · by_contra hlt
    exact hc (hS c (w' c) (not_le.mp hlt))

/-- The value of the game from below: a certifying set is at least as large as any set of cells
whose free bound is below the optimum. -/
theorem card_le_of_certifies {score : ι → H → ℕ} {w : ι → H} {S : Finset ι} {v : ℕ}
    (hS : Certifies score w (S : Set ι) v) (T : Finset ι) (hT : ∀ c ∈ T, ∃ h, score c h < v) :
    T.card ≤ S.card :=
  Finset.card_le_card fun c hc => by
    obtain ⟨h, hh⟩ := hT c hc
    exact Finset.mem_coe.mp (mem_of_certifies hS hh)

/-- The value of the game from above: one more cell than those whose free bound is below the
optimum is enough. -/
theorem exists_certifies_card_le [DecidableEq ι] {score : ι → H → ℕ} {w : ι → H} {v : ℕ}
    (hopt : IsOpt score w v) (T : Finset ι) (hT : ∀ c h, score c h < v → c ∈ T) :
    ∃ S : Finset ι, Certifies score w (S : Set ι) v ∧ S.card ≤ T.card + 1 := by
  obtain ⟨⟨c₀, hc₀⟩, hmin⟩ := hopt
  refine ⟨insert c₀ T, certifies_of hmin (by simp) hc₀ fun c h hc => ?_, Finset.card_insert_le _ _⟩
  simp [hT c h hc]

end Certify

/-! ### Finding a member at least as good as a target -/

/-- The expected number of cells looked at when they are taken in the order of the list, each holds
what is sought with the chance listed, independently of the others, and the search stops at the
first that does. -/
def searchCost : List ℝ → ℝ
  | [] => 0
  | p :: l => 1 + (1 - p) * searchCost l

theorem searchCost_swap (a b : ℝ) (l : List ℝ) (hab : b ≤ a) :
    searchCost (a :: b :: l) ≤ searchCost (b :: a :: l) := by
  have h : (1 + (1 - b) * (1 + (1 - a) * searchCost l)) -
      (1 + (1 - a) * (1 + (1 - b) * searchCost l)) = a - b := by ring
  simp only [searchCost]
  linarith

/-- Moving a cell of the largest chance to the front does not lengthen the search. -/
theorem searchCost_cons_erase_le {l : List ℝ} {m : ℝ} (hm : m ∈ l) (hmax : ∀ p ∈ l, p ≤ m)
    (h1 : ∀ p ∈ l, p ≤ 1) : searchCost (m :: l.erase m) ≤ searchCost l := by
  induction l with
  | nil => simp at hm
  | cons x t ih =>
    by_cases hx : x = m
    · subst hx
      simp
    · have hmt : m ∈ t := by
        rcases List.mem_cons.mp hm with h | h
        · exact absurd h.symm hx
        · exact h
      have ih' := ih hmt (fun p hp => hmax p (List.mem_cons_of_mem _ hp))
        (fun p hp => h1 p (List.mem_cons_of_mem _ hp))
      have hx0 : 0 ≤ 1 - x := sub_nonneg.mpr (h1 x List.mem_cons_self)
      have herase : (x :: t).erase m = x :: t.erase m := List.erase_cons_tail (by simpa using hx)
      rw [herase]
      calc searchCost (m :: x :: t.erase m) ≤ searchCost (x :: m :: t.erase m) :=
            searchCost_swap m x _ (hmax x List.mem_cons_self)
        _ = 1 + (1 - x) * searchCost (m :: t.erase m) := rfl
        _ ≤ 1 + (1 - x) * searchCost t := by
            have := mul_le_mul_of_nonneg_left ih' hx0
            linarith
        _ = searchCost (x :: t) := rfl

/-- **Chance first is the best order.** Among all orders of the same cells, the decreasing order of
their chances has the least expected number of cells looked at. -/
theorem searchCost_le_of_perm {l l' : List ℝ} (hperm : l.Perm l') (hsorted : l.Pairwise (· ≥ ·))
    (h1 : ∀ p ∈ l, p ≤ 1) : searchCost l ≤ searchCost l' := by
  induction l generalizing l' with
  | nil => rw [List.nil_perm.mp hperm]
  | cons a t ih =>
    have ha : a ∈ l' := hperm.subset List.mem_cons_self
    have hmax : ∀ p ∈ l', p ≤ a := fun p hp => by
      rcases List.mem_cons.mp (hperm.symm.subset hp) with rfl | hpt
      · exact le_rfl
      · exact (List.pairwise_cons.mp hsorted).1 p hpt
    have h1' : ∀ p ∈ l', p ≤ 1 := fun p hp => h1 p (hperm.symm.subset hp)
    have hperm' : t.Perm (l'.erase a) := by
      have := hperm.erase a
      simpa using this
    have iht := ih hperm' (List.pairwise_cons.mp hsorted).2
      (fun p hp => h1 p (List.mem_cons_of_mem _ hp))
    have ha0 : 0 ≤ 1 - a := sub_nonneg.mpr (h1 a List.mem_cons_self)
    calc searchCost (a :: t) = 1 + (1 - a) * searchCost t := rfl
      _ ≤ 1 + (1 - a) * searchCost (l'.erase a) := by
          have := mul_le_mul_of_nonneg_left iht ha0
          linarith
      _ = searchCost (a :: l'.erase a) := rfl
      _ ≤ searchCost l' := searchCost_cons_erase_le ha hmax h1'

/-! ### The smallest instance -/

namespace Example840

/-- Evaluate a list to the end before handing it on (the kernel would otherwise evaluate it again
at every use). -/
def forceList : List ℕ → (List ℕ → Bool) → Bool
  | [], k => k []
  | x :: xs, k => forceList xs fun ys => k (x :: ys)

theorem forceList_eq : ∀ (l : List ℕ) (k : List ℕ → Bool), forceList l k = k l
  | [], _ => rfl
  | x :: xs, k => by rw [forceList, forceList_eq xs]

/-- All class vectors of the moduli of `rest` leave at least `v` of the rows of `R`. -/
def boundGo : List ℕ → List ℕ → ℕ → Bool
  | [], R, v => decide (v ≤ R.length)
  | r :: rest, R, v =>
    (List.range r).all fun a => forceList (R.filter fun q => q % r != a) fun R' => boundGo rest R' v

theorem boundGo_sound : ∀ (rest R : List ℕ) (v : ℕ), (∀ r ∈ rest, 0 < r) →
    boundGo rest R v = true →
    ∀ M : ℕ, v ≤ (R.filter fun q => rest.all fun r => q % r != M % r).length
  | [], R, v, _, h, M => by
    simpa [boundGo] using h
  | r :: rest, R, v, hpos, h, M => by
    have hr : 0 < r := hpos r List.mem_cons_self
    rw [boundGo, List.all_eq_true] at h
    have h0 := h (M % r) (List.mem_range.mpr (Nat.mod_lt _ hr))
    rw [forceList_eq] at h0
    have h1 := boundGo_sound rest _ v (fun r' hr' => hpos r' (List.mem_cons_of_mem _ hr')) h0 M
    rw [List.filter_filter] at h1
    have h2 : (fun q => (rest.all fun r' => q % r' != M % r') && (q % r != M % r)) =
        fun q => (r :: rest).all fun r' => q % r' != M % r' := by
      funext q
      rw [List.all_cons, Bool.and_comm]
    rwa [h2] at h1

/-- The free bound of the cell of `N` in the design `T` is at least `v`: whatever classes the
moduli outside `T` take, at least `v` rows are left. -/
def boundHolds (T : List ℕ) (N v : ℕ) : Bool :=
  forceList (rows.filter fun q => T.all fun r => q % r != N % r) fun R =>
    boundGo (moduli.filter fun r => !T.contains r) R v

/-- What the check means: every number in the cell of `N` is left with at least `v` rows. -/
theorem le_left_of_boundHolds {T : List ℕ} {N v : ℕ} (h : boundHolds T N v = true) {M : ℕ}
    (hM : ∀ r ∈ T, M % r = N % r) : v ≤ left moduli M := by
  have h0 : ∀ r ∈ moduli, 0 < r := by decide
  have hpos : ∀ r ∈ moduli.filter (fun r => !T.contains r), 0 < r := fun r hr =>
    h0 r (List.mem_filter.mp hr).1
  rw [boundHolds, forceList_eq] at h
  have h1 := boundGo_sound _ _ v hpos h M
  rw [List.filter_filter] at h1
  unfold left
  refine h1.trans (List.Sublist.length_le (List.monotone_filter_right _ fun q hq => ?_))
  rw [Bool.and_eq_true, List.all_eq_true, List.all_eq_true] at hq
  rw [List.all_eq_true]
  intro r hr
  by_cases hrT : r ∈ T
  · have h3 := hq.2 r hrT
    rw [bne_iff_ne] at h3
    rw [decide_eq_true_eq, hM r hrT]
    exact h3
  · have h3 := hq.1 r (List.mem_filter.mpr ⟨hr, by simpa using hrT⟩)
    rw [bne_iff_ne] at h3
    rw [decide_eq_true_eq]
    exact h3

/-! #### The design 3, 5, 7 -/

/-- The cells of the design 3, 5, 7: the 105 even classes modulo 210, four candidates in each. -/
def cells : List ℕ := (List.range 105).map (2 * ·)

theorem mod_mem_cells : ∀ N ∈ cands, N % 210 ∈ cells := by decide +kernel

/-- The cells in three parts: the kernel evaluation of all 105 at once takes several gigabytes. -/
def cellsPart (k : ℕ) : List ℕ := (List.range 35).map fun i => 2 * (35 * k + i)

theorem cells_eq : cells = cellsPart 0 ++ cellsPart 1 ++ cellsPart 2 := by decide +kernel

theorem cell_bounds_six_0 :
    ∀ c ∈ cellsPart 0, c ∉ [122, 152, 166] → boundHolds [3, 5, 7] c 6 = true := by
  decide +kernel

theorem cell_bounds_six_1 :
    ∀ c ∈ cellsPart 1, c ∉ [122, 152, 166] → boundHolds [3, 5, 7] c 6 = true := by
  decide +kernel

theorem cell_bounds_six_2 :
    ∀ c ∈ cellsPart 2, c ∉ [122, 152, 166] → boundHolds [3, 5, 7] c 6 = true := by
  decide +kernel

/-- All cells but three have a free bound of at least 6. -/
theorem cell_bounds_six :
    ∀ c ∈ cells, c ∉ [122, 152, 166] → boundHolds [3, 5, 7] c 6 = true := by
  intro c hc
  rw [cells_eq, List.mem_append, List.mem_append] at hc
  rcases hc with (hc | hc) | hc
  exacts [cell_bounds_six_0 c hc, cell_bounds_six_1 c hc, cell_bounds_six_2 c hc]

theorem cell_bounds_seven_0 :
    ∀ c ∈ cellsPart 0, c ∉ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208] →
      boundHolds [3, 5, 7] c 7 = true := by
  decide +kernel

theorem cell_bounds_seven_1 :
    ∀ c ∈ cellsPart 1, c ∉ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208] →
      boundHolds [3, 5, 7] c 7 = true := by
  decide +kernel

theorem cell_bounds_seven_2 :
    ∀ c ∈ cellsPart 2, c ∉ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208] →
      boundHolds [3, 5, 7] c 7 = true := by
  decide +kernel

/-- All cells but ten have a free bound of at least 7. -/
theorem cell_bounds_seven :
    ∀ c ∈ cells, c ∉ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208] →
      boundHolds [3, 5, 7] c 7 = true := by
  intro c hc
  rw [cells_eq, List.mem_append, List.mem_append] at hc
  rcases hc with (hc | hc) | hc
  exacts [cell_bounds_seven_0 c hc, cell_bounds_seven_1 c hc, cell_bounds_seven_2 c hc]

/-- Numbers with the classes of the three cells modulo 3, 5, 7 and only 5 rows left (they are not
candidates: the least is 3,526), and numbers with the classes of seven more cells and 6 rows left
(`578` is the optimum itself). -/
theorem cell_witnesses :
    (∀ p ∈ [(122, 14192), (152, 7922), (166, 3526)], p.2 % 210 = p.1 ∧ left moduli p.2 = 5) ∧
    ∀ p ∈ [(16, 11146), (32, 9902), (46, 7816), (62, 5312), (158, 578), (178, 3118), (208, 9028)],
      p.2 % 210 = p.1 ∧ left moduli p.2 = 6 := by
  decide +kernel

/-- **The cells that must be looked at.** In the design 3, 5, 7 a cell could hold a number with
fewer than 6 rows left, if its classes modulo 11 and 13 were free, exactly when it is one of the
three cells 122, 152, 166. (None of the three does hold one: by `optimum` every candidate is left
with at least 6.) -/
theorem cells_below_optimum : ∀ c ∈ cells,
    (∃ M : ℕ, M % 210 = c ∧ left moduli M < 6) ↔ c ∈ [122, 152, 166] := by
  intro c hc
  constructor
  · rintro ⟨M, rfl, hM⟩
    by_contra hnot
    have := le_left_of_boundHolds (cell_bounds_six _ hc hnot) (M := M) fun r hr => by
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hr
      rcases hr with rfl | rfl | rfl <;> omega
    omega
  · intro h
    simp only [List.mem_cons, List.not_mem_nil, or_false] at h
    rcases h with rfl | rfl | rfl
    · exact ⟨14192, by decide +kernel⟩
    · exact ⟨7922, by decide +kernel⟩
    · exact ⟨3526, by decide +kernel⟩

/-- Seven more cells could hold a number with exactly 6 rows left; the cell of the optimum `578`
is one of them (`578 = 158 + 2 · 210`), so the optimum has the best classes modulo 11 and 13 that
its cover allows. -/
theorem cells_at_optimum : ∀ c ∈ cells,
    (∃ M : ℕ, M % 210 = c ∧ left moduli M ≤ 6) ↔
      c ∈ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208] := by
  intro c hc
  constructor
  · rintro ⟨M, rfl, hM⟩
    by_contra hnot
    have := le_left_of_boundHolds (cell_bounds_seven _ hc hnot) (M := M) fun r hr => by
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hr
      rcases hr with rfl | rfl | rfl <;> omega
    omega
  · intro h
    simp only [List.mem_cons, List.not_mem_nil, or_false] at h
    rcases h with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    · exact ⟨11146, by decide +kernel⟩
    · exact ⟨9902, by decide +kernel⟩
    · exact ⟨7816, by decide +kernel⟩
    · exact ⟨5312, by decide +kernel⟩
    · exact ⟨14192, by decide +kernel⟩
    · exact ⟨7922, by decide +kernel⟩
    · exact ⟨578, by decide +kernel⟩
    · exact ⟨3526, by decide +kernel⟩
    · exact ⟨3118, by decide +kernel⟩
    · exact ⟨9028, by decide +kernel⟩

/-! #### All seven designs at once

A candidate lies in one cell of each of the seven designs, and each of those cells has its own free
bound. Taken together the seven bounds leave nothing: every candidate is in some cell none of whose
numbers could have fewer than 6 rows left, and every candidate except 152 and 578 is in some cell
none of whose numbers could have fewer than 7. So scoring 578 alone (or 152 and 578, in the order of
the bounds) proves the optimum. This is special to an instance in which two or three moduli lie
outside each design: a free bound lets every outside modulus take its best class, and with many
moduli outside it is zero. -/

/-- The twelve candidates of the three cells that the design 3, 5, 7 does not exclude, each with
a design that does. -/
def others6 : List (ℕ × List ℕ) :=
  [(122, [5, 7, 11]), (152, [5, 7, 11]), (166, [5, 7, 11]), (332, [3, 7, 13]), (362, [3, 7, 13]),
   (376, [5, 7, 11]), (542, [5, 7, 11]), (572, [5, 7, 11]), (586, [5, 7, 11]), (752, [5, 7, 11]),
   (782, [5, 7, 11]), (796, [5, 7, 11])]

/-- The 38 candidates other than 152 and 578 in the ten cells whose free bound in the design
3, 5, 7 is at most 6, each with a design in which the free bound of its cell is at least 7. -/
def others7 : List (ℕ × List ℕ) :=
  [(16, [5, 7, 11]), (32, [5, 7, 11]), (46, [5, 7, 11]), (62, [5, 7, 11]), (122, [5, 7, 11]),
   (158, [5, 7, 11]), (166, [5, 7, 11]), (178, [5, 7, 11]), (208, [5, 7, 11]), (226, [5, 7, 11]),
   (242, [5, 7, 11]), (256, [5, 7, 11]), (272, [3, 7, 13]), (332, [3, 7, 13]), (362, [3, 7, 13]),
   (368, [5, 7, 11]), (376, [5, 7, 11]), (388, [5, 7, 11]), (418, [5, 7, 11]), (436, [5, 7, 11]),
   (452, [5, 7, 11]), (466, [5, 7, 11]), (482, [5, 7, 11]), (542, [5, 7, 11]), (572, [5, 7, 11]),
   (586, [5, 7, 11]), (598, [5, 7, 11]), (628, [5, 7, 11]), (646, [5, 7, 11]), (662, [3, 7, 13]),
   (676, [5, 7, 11]), (692, [3, 7, 13]), (752, [3, 7, 13]), (782, [5, 7, 11]), (788, [3, 7, 13]),
   (796, [5, 7, 11]), (808, [3, 7, 13]), (838, [5, 7, 11])]

theorem others6_bounds :
    ∀ p ∈ others6, p.2 ∈ designs.map Prod.fst ∧ boundHolds p.2 p.1 6 = true := by
  decide +kernel

theorem others6_complete :
    ∀ N ∈ cands, N % 210 ∈ [122, 152, 166] → N ∈ others6.map Prod.fst := by
  decide +kernel

theorem others7_bounds :
    ∀ p ∈ others7, p.2 ∈ designs.map Prod.fst ∧ boundHolds p.2 p.1 7 = true := by
  decide +kernel

theorem others7_complete :
    ∀ N ∈ cands, N % 210 ∈ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208] →
      N = 152 ∨ N = 578 ∨ N ∈ others7.map Prod.fst := by
  decide +kernel

theorem design_357_mem : [3, 5, 7] ∈ designs.map Prod.fst := by decide

/-- **The free bounds of the seven designs prove the optimum.** Every candidate lies, in one of
the seven designs, in a cell none of whose numbers is left with fewer than 6 rows, whatever their
classes modulo the moduli outside the design. -/
theorem free_bounds_optimum : ∀ N ∈ cands, ∃ T ∈ designs.map Prod.fst,
    ∀ M : ℕ, (∀ r ∈ T, M % r = N % r) → 6 ≤ left moduli M := by
  intro N hN
  by_cases h : N % 210 ∈ [122, 152, 166]
  · obtain ⟨p, hp, rfl⟩ := List.mem_map.mp (others6_complete N hN h)
    exact ⟨p.2, (others6_bounds p hp).1, fun M hM =>
      le_left_of_boundHolds (others6_bounds p hp).2 hM⟩
  · refine ⟨[3, 5, 7], design_357_mem, fun M hM =>
      le_left_of_boundHolds (cell_bounds_six _ (mod_mem_cells N hN) h) fun r hr => ?_⟩
    have := hM r hr
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hr
    rcases hr with rfl | rfl | rfl <;> omega

/-- Every candidate except 152 and 578 lies in a cell none of whose numbers is left with fewer
than 7 rows: in the order of the free bounds only these two are scored. -/
theorem free_bounds_all_but_two : ∀ N ∈ cands, N ≠ 152 → N ≠ 578 → ∃ T ∈ designs.map Prod.fst,
    ∀ M : ℕ, (∀ r ∈ T, M % r = N % r) → 7 ≤ left moduli M := by
  intro N hN h1 h2
  by_cases h : N % 210 ∈ [16, 32, 46, 62, 122, 152, 158, 166, 178, 208]
  · rcases others7_complete N hN h with h | h | h
    · exact absurd h h1
    · exact absurd h h2
    · obtain ⟨p, hp, rfl⟩ := List.mem_map.mp h
      exact ⟨p.2, (others7_bounds p hp).1, fun M hM =>
        le_left_of_boundHolds (others7_bounds p hp).2 hM⟩
  · refine ⟨[3, 5, 7], design_357_mem, fun M hM =>
      le_left_of_boundHolds (cell_bounds_seven _ (mod_mem_cells N hN) h) fun r hr => ?_⟩
    have := hM r hr
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hr
    rcases hr with rfl | rfl | rfl <;> omega

/-- The two that remain are not told apart by any free bound: in every design the cell of 152
could hold a number with 6 rows left. (152 itself is left with 7.) -/
theorem tie_152 : (∀ d ∈ designs, boundHolds d.1 152 7 = false) ∧ left moduli 152 = 7 := by
  decide +kernel

end Example840

end GoldbachGaps.Cap
