import GoldbachGaps.Basic

/-!
# The capped game: the budget law

Below a cap `X`, structure on the residues of `N` is paid for in candidates.

* `count_modEq_le` – one residue class modulo `M` has at most `X / M + 1` members below `X`.
* `card_residues_in_le` – if for every modulus `r` of a pairwise coprime family `S` the residue
  of `N` is only required to lie in a set `A r` (a "soft" or set-valued condition), the number
  of `N < X` satisfying all conditions is at most `(∏ |A r|) · (X / ∏ r + 1)`.

So fixing one class modulo `r` costs a factor `r`, and allowing `|A r|` classes costs a factor
`r / |A r|`: set-valued conditions follow the same accounting as single classes. In
particular, once `∏ r ≥ X` there is at most one candidate per choice of classes.
-/

namespace GoldbachGaps.Cap

open Finset

/-- A residue class modulo `M` has at most `X / M + 1` members below `X`. -/
theorem count_modEq_le {M : ℕ} (hM : 0 < M) (a X : ℕ) :
    Nat.count (· ≡ a [MOD M]) X ≤ X / M + 1 := by
  rw [Nat.count_modEq_card X hM a]
  split_ifs <;> omega

/-- Two numbers with the same residues modulo pairwise coprime moduli are congruent modulo
the product. -/
theorem modEq_prod_of_forall {S : Finset ℕ} (hcop : (S : Set ℕ).Pairwise Nat.Coprime)
    {x y : ℕ} (h : ∀ r ∈ S, x ≡ y [MOD r]) : x ≡ y [MOD ∏ r ∈ S, r] := by
  classical
  induction S using Finset.induction_on with
  | empty => simpa using Nat.modEq_one
  | insert r S hr ih =>
    rw [Finset.prod_insert hr]
    have hcop' : (S : Set ℕ).Pairwise Nat.Coprime :=
      hcop.mono (by intro x hx; exact Finset.mem_insert_of_mem hx)
    have hrS : r.Coprime (∏ t ∈ S, t) := by
      rw [Nat.coprime_prod_right_iff]
      intro t ht
      exact hcop (Finset.mem_insert_self r S) (Finset.mem_insert_of_mem ht)
        (by rintro rfl; exact hr ht)
    exact (Nat.modEq_and_modEq_iff_modEq_mul hrS).mp
      ⟨h r (Finset.mem_insert_self r S),
        ih hcop' fun t ht => h t (Finset.mem_insert_of_mem ht)⟩

/-- **The budget law with choice sets.** Let `S` be pairwise coprime positive moduli and let
`A r` be the set of residues allowed modulo `r`. The number of `N < X` whose residue modulo
every `r ∈ S` is allowed is at most `(∏ |A r|) · (X / ∏ r + 1)`. -/
theorem card_residues_in_le (S : Finset ℕ) (A : ℕ → Finset ℕ) (X : ℕ)
    (hpos : ∀ r ∈ S, 0 < r) (hcop : (S : Set ℕ).Pairwise Nat.Coprime) :
    #{N ∈ range X | ∀ r ∈ S, N % r ∈ A r} ≤ (∏ r ∈ S, #(A r)) * (X / (∏ r ∈ S, r) + 1) := by
  classical
  set M := ∏ r ∈ S, r with hM
  have hM0 : 0 < M := Finset.prod_pos hpos
  rw [← Finset.card_pi, ← Finset.card_range (X / M + 1), ← Finset.card_product]
  refine Finset.card_le_card_of_injOn (fun N => (fun r _ => N % r, N / M)) ?_ ?_
  · intro N hN
    rw [Finset.mem_coe, Finset.mem_filter, Finset.mem_range] at hN
    rw [Finset.mem_coe, Finset.mem_product, Finset.mem_pi, Finset.mem_range]
    exact ⟨fun r hr => hN.2 r hr, Nat.lt_succ_of_le (Nat.div_le_div_right hN.1.le)⟩
  · intro N _ N' _ heq
    simp only [Prod.mk.injEq] at heq
    obtain ⟨h1, h2⟩ := heq
    have hmod : N ≡ N' [MOD M] := modEq_prod_of_forall hcop fun r hr => by
      have := congrFun (congrFun h1 r) hr
      exact this
    have e1 := Nat.div_add_mod N M
    have e2 := Nat.div_add_mod N' M
    have hmod' : N % M = N' % M := hmod
    rw [h2, hmod'] at e1
    omega

end GoldbachGaps.Cap
