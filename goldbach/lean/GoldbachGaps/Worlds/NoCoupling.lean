import Mathlib

/-!
# World 1: a separable score with no coupling

The object of every "world" of the programme is a score `S(N) = ∑ r, f r (N mod r)` together with a constraint
that couples the coordinates (for the integers, `N < X`). This file is the base case, where there is no constraint:
the points are all of a product of finite sets.

* `sum_le_sum_of_forall_le`: the optimum is the coordinatewise optimum.
* After sorting each coordinate (so that a point is a vector of ranks and the score is antitone in each rank),
  the best points come out one at a time, each a neighbour of one already produced:
  * `exists_next_best`: if `A` is a lower set of rank vectors inside the box and not all of it, some point outside
    `A` is a best point outside `A` and leaves `A` a lower set when added;
  * `eq_zero_or_succ_of_lower`: such a point is the zero vector or `a + e_i` for some `a ∈ A`;
  * `card_candidates_le`: so it is one of at most `1 + |ι| · |A|` candidates;
  * `exists_best_list`: for every `k` up to the size of the box there is a list of `k` points of which every prefix
    is a lower set and consists of best points (every point of the prefix scores at least as much as every point of
    the box outside the prefix);
  * `pairwise_of_best_prefixes`, `getElem_eq_zero_or_succ`: the list is in non-increasing order of score, and its
    `n`-th point is zero or a successor of one of the first `n`.

So the `k` best points are found by looking at no more than `1 + |ι| · k` points in all: the cost is proportional to
the output. Whatever is hard in the other worlds is the coupling.
-/

namespace GoldbachGaps.Worlds

open Finset

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

omit [DecidableEq ι] in
/-- **The optimum is the coordinatewise optimum.** On a full product, a point that is best in every coordinate is
best for the sum. -/
theorem sum_le_sum_of_forall_le {α : ι → Type*} (A : ∀ i, Finset (α i)) (f : ∀ i, α i → ℝ) (a : ∀ i, α i)
    (ha : ∀ i, ∀ b ∈ A i, f i b ≤ f i (a i)) {x : ∀ i, α i} (hx : ∀ i, x i ∈ A i) :
    ∑ i, f i (x i) ≤ ∑ i, f i (a i) :=
  Finset.sum_le_sum fun i _ => ha i _ (hx i)

/-- The score of a vector of ranks. -/
def score (f : ι → ℕ → ℝ) (x : ι → ℕ) : ℝ := ∑ i, f i (x i)

/-- The box of rank vectors: coordinate `i` has `m i` values, ranked `0, 1, …, m i - 1`. -/
def box (m : ι → ℕ) : Finset (ι → ℕ) := Fintype.piFinset fun i => range (m i)

theorem mem_box {m : ι → ℕ} {x : ι → ℕ} : x ∈ box m ↔ ∀ i, x i < m i := by simp [box]

omit [DecidableEq ι] in
theorem score_antitone {f : ι → ℕ → ℝ} (hf : ∀ i, Antitone (f i)) : Antitone (score f) :=
  fun _ _ hxy => Finset.sum_le_sum fun i _ => hf i (hxy i)

theorem isLowerSet_box (m : ι → ℕ) : IsLowerSet (box m : Set (ι → ℕ)) := by
  intro a b hba ha
  rw [mem_coe, mem_box] at *
  exact fun i => lt_of_le_of_lt (hba i) (ha i)

/-- **The greedy step.** Among the points of the box outside a lower set `A`, some best one can be added to `A`
keeping it a lower set. -/
theorem exists_next_best (f : ι → ℕ → ℝ) (hf : ∀ i, Antitone (f i)) (m : ι → ℕ) (A : Finset (ι → ℕ))
    (hA : IsLowerSet (A : Set (ι → ℕ))) (hAB : ¬ box m ⊆ A) :
    ∃ x ∈ box m \ A, (∀ y ∈ box m \ A, score f y ≤ score f x) ∧
      IsLowerSet ((insert x A : Finset (ι → ℕ)) : Set (ι → ℕ)) := by
  classical
  have hne : (box m \ A).Nonempty := sdiff_nonempty.mpr hAB
  obtain ⟨z, hz, hzmax⟩ := (box m \ A).exists_max_image (score f) hne
  have hMne : ((box m \ A).filter fun y => score f y = score f z).Nonempty := ⟨z, by simp [hz]⟩
  obtain ⟨x, hx, hxmin⟩ :=
    ((box m \ A).filter fun y => score f y = score f z).exists_min_image (fun y => ∑ i, y i) hMne
  obtain ⟨hxBA, hxz⟩ := mem_filter.mp hx
  refine ⟨x, hxBA, fun y hy => hxz ▸ hzmax y hy, ?_⟩
  intro a b hba ha
  rw [mem_coe, mem_insert] at ha ⊢
  rcases ha with rfl | ha
  · by_cases hbx : b = a
    · exact Or.inl hbx
    · right
      by_contra hbA
      have hb : b ∈ box m \ A := mem_sdiff.mpr ⟨isLowerSet_box m hba (mem_coe.mpr (mem_sdiff.mp hxBA).1), hbA⟩
      have h1 : score f a ≤ score f b := score_antitone hf hba
      have h2 : score f b ≤ score f z := hzmax b hb
      have hbM : b ∈ (box m \ A).filter fun y => score f y = score f z :=
        mem_filter.mpr ⟨hb, le_antisymm h2 (hxz ▸ h1)⟩
      have h3 : ∑ i, a i ≤ ∑ i, b i := hxmin b hbM
      have h4 : ∑ i, b i < ∑ i, a i := by
        apply Finset.sum_lt_sum (fun i _ => hba i)
        by_contra hcon
        push Not at hcon
        exact hbx (funext fun i => le_antisymm (hba i) (hcon i (mem_univ i)))
      omega
  · exact Or.inr (hA hba ha)

/-- A point whose addition to a set leaves a lower set is the zero vector or the successor of a point of the set in
one coordinate. -/
theorem eq_zero_or_succ_of_lower {A : Finset (ι → ℕ)} {x : ι → ℕ}
    (hlow : IsLowerSet ((insert x A : Finset (ι → ℕ)) : Set (ι → ℕ))) :
    x = 0 ∨ ∃ a ∈ A, ∃ i, x = a + Pi.single i 1 := by
  by_cases h0 : x = 0
  · exact Or.inl h0
  · right
    obtain ⟨i, hi⟩ : ∃ i, x i ≠ 0 := by
      by_contra hcon
      push Not at hcon
      exact h0 (funext hcon)
    have hyx : Function.update x i (x i - 1) ≤ x := by
      intro j
      by_cases hj : j = i
      · subst hj; simp
      · simp [Function.update_of_ne hj]
    have hyne : Function.update x i (x i - 1) ≠ x := fun h => by
      have := congrFun h i
      simp at this
      omega
    have hyA : Function.update x i (x i - 1) ∈ A := by
      have h := hlow hyx (by simp)
      rw [mem_coe, mem_insert] at h
      exact h.resolve_left hyne
    refine ⟨_, hyA, i, ?_⟩
    funext j
    by_cases hj : j = i
    · subst hj; simp; omega
    · simp [Function.update_of_ne hj, Pi.single_eq_of_ne hj]

/-- The candidates for the next point: the zero vector and the successors of the points already produced. -/
def candidates (A : Finset (ι → ℕ)) : Finset (ι → ℕ) :=
  insert 0 (A.biUnion fun a => univ.image fun i => a + Pi.single i 1)

/-- There are at most `1 + |ι| · |A|` candidates. -/
theorem card_candidates_le (A : Finset (ι → ℕ)) : (candidates A).card ≤ 1 + Fintype.card ι * A.card := by
  unfold candidates
  refine (card_insert_le _ _).trans ?_
  have h : (A.biUnion fun a => univ.image fun i : ι => a + Pi.single i 1).card ≤ A.card * Fintype.card ι := by
    refine card_biUnion_le_card_mul _ _ _ fun a _ => ?_
    exact card_image_le.trans (by simp)
  nlinarith [h]

/-- The next best point of `exists_next_best` is a candidate. -/
theorem mem_candidates_of_lower {A : Finset (ι → ℕ)} {x : ι → ℕ}
    (hlow : IsLowerSet ((insert x A : Finset (ι → ℕ)) : Set (ι → ℕ))) : x ∈ candidates A := by
  unfold candidates
  rcases eq_zero_or_succ_of_lower hlow with rfl | ⟨a, ha, i, rfl⟩
  · exact mem_insert_self _ _
  · exact mem_insert_of_mem (mem_biUnion.mpr ⟨a, ha, mem_image.mpr ⟨i, mem_univ _, rfl⟩⟩)

/-- **The best points in order.** For every `k` up to the size of the box there is a list of `k` distinct points
of the box every prefix of which is a lower set made of best points. -/
theorem exists_best_list (f : ι → ℕ → ℝ) (hf : ∀ i, Antitone (f i)) (m : ι → ℕ) (k : ℕ)
    (hk : k ≤ (box m).card) :
    ∃ l : List (ι → ℕ), l.length = k ∧ l.Nodup ∧ (∀ x ∈ l, x ∈ box m) ∧
      ∀ n, IsLowerSet {x | x ∈ l.take n} ∧
        ∀ x ∈ l.take n, ∀ y ∈ box m, y ∉ l.take n → score f y ≤ score f x := by
  classical
  induction k with
  | zero =>
    exact ⟨[], rfl, List.nodup_nil, by simp, fun n => ⟨by intro a b _ ha; simp at ha, by simp⟩⟩
  | succ k ih =>
    obtain ⟨l, hlen, hnd, hbox, hpre⟩ := ih (Nat.le_of_succ_le hk)
    have hall := hpre l.length
    rw [List.take_length] at hall
    have hsub : ¬ box m ⊆ l.toFinset := by
      intro h
      have := card_le_card h
      have h2 : l.toFinset.card ≤ l.length := List.toFinset_card_le l
      omega
    have hlow : IsLowerSet ((l.toFinset : Finset (ι → ℕ)) : Set (ι → ℕ)) := by
      intro a b hba ha
      rw [mem_coe, List.mem_toFinset] at ha ⊢
      exact hall.1 hba ha
    obtain ⟨x, hx, hxmax, hxlow⟩ := exists_next_best f hf m l.toFinset hlow hsub
    obtain ⟨hxbox, hxl⟩ := mem_sdiff.mp hx
    rw [List.mem_toFinset] at hxl
    refine ⟨l ++ [x], by simp [hlen], ?_, ?_, ?_⟩
    · exact List.nodup_append.mpr ⟨hnd, List.nodup_singleton x, by
        intro a ha b hb
        rw [List.mem_singleton] at hb
        subst hb
        exact fun h => hxl (h ▸ ha)⟩
    · intro y hy
      rcases List.mem_append.mp hy with h | h
      · exact hbox y h
      · rw [List.mem_singleton] at h; exact h ▸ hxbox
    · intro n
      by_cases hn : n ≤ l.length
      · rw [List.take_append_of_le_length hn]
        exact hpre n
      · have hn' : (l ++ [x]).length ≤ n := by simp; omega
        rw [List.take_of_length_le hn']
        refine ⟨?_, ?_⟩
        · intro a b hba ha
          have ha' : a ∈ ((insert x l.toFinset : Finset (ι → ℕ)) : Set (ι → ℕ)) := by
            rw [mem_coe, mem_insert, List.mem_toFinset]
            rcases List.mem_append.mp ha with h | h
            · exact Or.inr h
            · exact Or.inl (List.mem_singleton.mp h)
          have hb' := hxlow hba ha'
          rw [mem_coe, mem_insert, List.mem_toFinset] at hb'
          rcases hb' with h | h
          · exact List.mem_append.mpr (Or.inr (List.mem_singleton.mpr h))
          · exact List.mem_append.mpr (Or.inl h)
        · intro a ha y hy hyl
          have hyl' : y ∉ l := fun h => hyl (List.mem_append.mpr (Or.inl h))
          rcases List.mem_append.mp ha with h | h
          · exact hall.2 a h y hy hyl'
          · rw [List.mem_singleton] at h
            subst h
            exact hxmax y (mem_sdiff.mpr ⟨hy, by rwa [List.mem_toFinset]⟩)

/-- A list all of whose prefixes consist of best points is in non-increasing order of score. -/
theorem pairwise_of_best_prefixes {f : ι → ℕ → ℝ} {m : ι → ℕ} {l : List (ι → ℕ)} (hnd : l.Nodup)
    (hbox : ∀ x ∈ l, x ∈ box m)
    (hbest : ∀ n, ∀ x ∈ l.take n, ∀ y ∈ box m, y ∉ l.take n → score f y ≤ score f x) :
    l.Pairwise fun x y => score f y ≤ score f x := by
  rw [List.pairwise_iff_getElem]
  intro i j hi hj hij
  have hxi : l[i] ∈ l.take (i + 1) := by
    rw [List.mem_take_iff_getElem]
    exact ⟨i, by omega, rfl⟩
  have hyj : l[j] ∉ l.take (i + 1) := by
    rw [List.mem_take_iff_getElem]
    rintro ⟨a, ha, hEq⟩
    have := (List.Nodup.getElem_inj_iff hnd).mp hEq
    omega
  exact hbest (i + 1) _ hxi _ (hbox _ (List.getElem_mem hj)) hyj

/-- In a list all of whose prefixes are lower sets, the `n`-th point is the zero vector or a
successor, in one coordinate, of one of the first `n` points: it is a candidate. -/
theorem getElem_mem_candidates {l : List (ι → ℕ)}
    (hlow : ∀ n, IsLowerSet {x | x ∈ l.take n}) (n : ℕ) (hn : n < l.length) :
    l[n] ∈ candidates (l.take n).toFinset := by
  refine mem_candidates_of_lower ?_
  have h := hlow (n + 1)
  have htake : l.take (n + 1) = l.take n ++ [l[n]] := (List.take_append_getElem hn).symm
  intro a b hba ha
  rw [mem_coe, mem_insert, List.mem_toFinset] at ha ⊢
  have ha' : a ∈ l.take (n + 1) := by
    rw [htake]
    rcases ha with h | h
    · exact List.mem_append.mpr (Or.inr (List.mem_singleton.mpr h))
    · exact List.mem_append.mpr (Or.inl h)
  have hb' : b ∈ l.take (n + 1) := h hba ha'
  rw [htake] at hb'
  rcases List.mem_append.mp hb' with h | h
  · exact Or.inr h
  · exact Or.inl (List.mem_singleton.mp h)

/-- **The cost is proportional to the output.** The `k` best points of the box, in non-increasing order of score,
each found among at most `1 + |ι| · n` candidates determined by the `n` points before it. -/
theorem exists_best_list_candidates (f : ι → ℕ → ℝ) (hf : ∀ i, Antitone (f i)) (m : ι → ℕ) (k : ℕ)
    (hk : k ≤ (box m).card) :
    ∃ l : List (ι → ℕ), l.length = k ∧ l.Nodup ∧ (∀ x ∈ l, x ∈ box m) ∧
      (∀ x ∈ l, ∀ y ∈ box m, y ∉ l → score f y ≤ score f x) ∧
      (l.Pairwise fun x y => score f y ≤ score f x) ∧
      ∀ (n : ℕ) (hn : n < l.length), l[n] ∈ candidates (l.take n).toFinset ∧
        (candidates (l.take n).toFinset).card ≤ 1 + Fintype.card ι * n := by
  obtain ⟨l, hlen, hnd, hbox, hpre⟩ := exists_best_list f hf m k hk
  refine ⟨l, hlen, hnd, hbox, ?_, pairwise_of_best_prefixes hnd hbox fun n => (hpre n).2, ?_⟩
  · have h := (hpre l.length).2
    rwa [List.take_length] at h
  · intro n hn
    refine ⟨getElem_mem_candidates (fun n => (hpre n).1) n hn, ?_⟩
    refine (card_candidates_le _).trans ?_
    have h1 : (l.take n).toFinset.card ≤ (l.take n).length := List.toFinset_card_le _
    have h2 : (l.take n).length ≤ n := by simp
    have := Nat.mul_le_mul_left (Fintype.card ι) (h1.trans h2)
    omega

end GoldbachGaps.Worlds
