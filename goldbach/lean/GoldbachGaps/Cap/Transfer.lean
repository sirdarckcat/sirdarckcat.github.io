import GoldbachGaps.Basic

/-!
# From prime deserts to Goldbach gaps

The "trivial" construction: if there is no prime strictly between `p` and `p'`, then
`N = p' + 1` has no Goldbach summand `q ≤ p' - p`, because each `N - q` lies strictly between
`p` and `p'`. If moreover `p` and `p' - p + 1` are prime, the least Goldbach summand of `N` is
exactly `p' - p + 1`. (`p'` itself does not have to be prime for either statement.)

So a prime gap of length `G` hands over a Goldbach gap of about `G`. Below `10^200` this is far
weaker than covering: a prime desert must kill every integer of an interval, a Goldbach gap
only the `N - q` with `q` prime.
-/

namespace GoldbachGaps.Cap

/-- **Prime-desert transfer.** No prime strictly between `p` and `p'` implies that
`p' + 1` has no Goldbach summand `q ≤ p' - p`. -/
theorem not_isSummand_of_desert {p p' q : ℕ} (hgap : ∀ n, p < n → n < p' → ¬ n.Prime)
    (hq : q ≤ p' - p) : ¬ IsSummand (p' + 1) q := by
  rintro ⟨hqp, hN⟩
  have h2 := hqp.two_le
  exact hgap (p' + 1 - q) (by omega) (by omega) hN

/-- If in addition `p` and `p' - p + 1` are prime, then `g(p' + 1) = p' - p + 1`. -/
theorem isLeastSummand_of_desert {p p' : ℕ} (hp : p.Prime) (hlt : p < p')
    (hgap : ∀ n, p < n → n < p' → ¬ n.Prime) (hG : (p' - p + 1).Prime) :
    IsLeastSummand (p' + 1) (p' - p + 1) := by
  refine ⟨⟨hG, ?_⟩, ?_⟩
  · have : p' + 1 - (p' - p + 1) = p := by omega
    rwa [this]
  · intro q hq
    by_contra hcon
    exact not_isSummand_of_desert hgap (by omega) hq

end GoldbachGaps.Cap
