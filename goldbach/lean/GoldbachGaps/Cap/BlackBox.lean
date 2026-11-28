import GoldbachGaps.Basic

/-!
# The black-box bound for the search problem

`K` members, of which an unknown set `G` of `g` is "good" (the members with the fewest rows
left). A method that learns about `G` only by asking, member by member, "is this one good?"
asks, until its first success, the fixed sequence of questions it would ask after an unbroken
run of "no": adaptivity is of no use before the first success. So `m` questions find a good
member for at most the fraction `m g / K` of all possible sets `G` (`blackbox_fraction`).
The same holds when each answer reveals the member's number of rows left, as long as the
unasked members remain exchangeable given the answers.

The real instance is not a black box: every class `(q - N₀)/M mod s` is computable, nothing is
hidden. The bound says what a method that beats enumeration cannot be: it cannot treat the
count of rows left as an oracle. It must use how the lists arise.
-/

namespace GoldbachGaps.Cap

open Finset

/-- At most `C(K-1, g-1)` of the `g`-subsets of `K` members contain a given member. -/
theorem card_subsets_containing_le (K g : ℕ) (a : Fin K) :
    (((univ : Finset (Fin K)).powersetCard g).filter (fun G => a ∈ G)).card ≤
      (K - 1).choose (g - 1) := by
  have h := Finset.card_le_card_of_injOn (fun G : Finset (Fin K) => G.erase a)
    (s := ((univ : Finset (Fin K)).powersetCard g).filter (fun G => a ∈ G))
    (t := ((univ : Finset (Fin K)).erase a).powersetCard (g - 1)) ?_ ?_
  · rwa [card_powersetCard, card_erase_of_mem (mem_univ a), card_univ, Fintype.card_fin] at h
  · intro G hG
    have hG' := Finset.mem_filter.mp (Finset.mem_coe.mp hG)
    have hcard := (Finset.mem_powersetCard.mp hG'.1).2
    refine Finset.mem_coe.mpr (Finset.mem_powersetCard.mpr
      ⟨Finset.erase_subset_erase a (Finset.subset_univ G), ?_⟩)
    rw [card_erase_of_mem hG'.2, hcard]
  · intro G₁ h₁ G₂ h₂ heq
    have ha₁ := (Finset.mem_filter.mp (Finset.mem_coe.mp h₁)).2
    have ha₂ := (Finset.mem_filter.mp (Finset.mem_coe.mp h₂)).2
    have heq' : G₁.erase a = G₂.erase a := heq
    rw [← Finset.insert_erase ha₁, ← Finset.insert_erase ha₂, heq']

/-- `m` questions `t 0, …, t (m-1)` hit at most `m · C(K-1, g-1)` of the `g`-subsets. -/
theorem blackbox_bound (K g m : ℕ) (t : Fin m → Fin K) :
    (((univ : Finset (Fin K)).powersetCard g).filter (fun G => ∃ j, t j ∈ G)).card ≤
      m * (K - 1).choose (g - 1) := by
  calc (((univ : Finset (Fin K)).powersetCard g).filter (fun G => ∃ j, t j ∈ G)).card
      ≤ ((univ : Finset (Fin m)).biUnion fun j =>
          ((univ : Finset (Fin K)).powersetCard g).filter (fun G => t j ∈ G)).card := by
        refine Finset.card_le_card fun G hG => ?_
        obtain ⟨hG1, j, hj⟩ := Finset.mem_filter.mp hG
        exact Finset.mem_biUnion.mpr ⟨j, Finset.mem_univ j, Finset.mem_filter.mpr ⟨hG1, hj⟩⟩
    _ ≤ ∑ j : Fin m, (((univ : Finset (Fin K)).powersetCard g).filter
          (fun G => t j ∈ G)).card := Finset.card_biUnion_le
    _ ≤ ∑ _j : Fin m, (K - 1).choose (g - 1) :=
        Finset.sum_le_sum fun j _ => card_subsets_containing_le K g (t j)
    _ = m * (K - 1).choose (g - 1) := by simp

/-- **The black-box bound.** Of the `C(K, g)` possible sets of `g` good members, `m` questions
find a good member for at most the fraction `m g / K`. -/
theorem blackbox_fraction (K g m : ℕ) (hK : 1 ≤ K) (hg : 1 ≤ g) (t : Fin m → Fin K) :
    (((univ : Finset (Fin K)).powersetCard g).filter (fun G => ∃ j, t j ∈ G)).card * K ≤
      m * g * K.choose g := by
  obtain ⟨n, rfl⟩ : ∃ n, K = n + 1 := ⟨K - 1, by omega⟩
  obtain ⟨k, rfl⟩ : ∃ k, g = k + 1 := ⟨g - 1, by omega⟩
  have h := blackbox_bound (n + 1) (k + 1) m t
  simp only [Nat.add_sub_cancel] at h
  have e := Nat.add_one_mul_choose_eq n k
  calc _ ≤ m * n.choose k * (n + 1) := Nat.mul_le_mul_right _ h
    _ = m * ((n + 1) * n.choose k) := by ring
    _ = m * ((n + 1).choose (k + 1) * (k + 1)) := by rw [e]
    _ = m * (k + 1) * (n + 1).choose (k + 1) := by ring

end GoldbachGaps.Cap
