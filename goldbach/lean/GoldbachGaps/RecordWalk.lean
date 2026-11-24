import GoldbachGaps.RecordGenRun

/-!
# An N generator for A025018: walk the even numbers and say when a new record falls

`walk X` goes through `N = 4, 6, 8, …` below `X`. Its whole state is one number `G`, the
largest least Goldbach summand met so far. At each `N` it asks one question,

  *is the least Goldbach summand of `N` larger than `G`?*

and if so it announces `N` (and `G` becomes that summand). Nothing else: no list of primes is
swept, the loop variable is `N`.

* `mem_walk`: for every bound `X`, `N ∈ walk X ↔ N < X ∧ ∃ g, IsRecord N g`. The numbers
  announced are exactly the terms of A025018 below `X`.
* `walk_sorted`: they are announced in increasing order.
* `walk_eq_map_records`: `walk X` is the list of first components of `RecordGen.records X`.
  The walker (which answers its question for each `N` separately) and the sieve of
  `GoldbachGaps/RecordGen.lean` (which answers it for all `N` at once on bitmasks, and is the
  one to run for large `X`) are the same generator.
* `walk_two_pow_20`: below `2^20` the walker announces 21 numbers, `4, 6, 12, 30, 98, …,
  503222` (through the kernel run of the sieve, `RecordGen.records_two_pow_20`).
* `not_isSummand_iff_neighbours`: what the question looks at. "No prime `q ≤ G` is a summand
  of `N`" says the same as "no prime `p` with `N - G ≤ p < N` lies at a prime distance from
  `N`". So to tell whether `N` beats `G` it is enough to look at the primes within `G` below
  `N`; nothing about any other number is needed, given `G`.
* `beats_iff_wheels`: the same question asked of `N` alone. `N` beats `G` exactly when its
  residues modulo the primes `r ≤ √N` cover the strikers: every prime `q ≤ G` has such an `r`
  with `N ≡ q (mod r)`. No list of primes near `N` is needed, only the residues of `N` and the
  small primes. This is the condition the 200-digit certificates establish
  (`GoldbachGaps/CompleteCover.lean`: a cover of the strikers by residues); the terms of
  A025018 are the first `N` at which it holds for each `G`.

`scripts/record_gen/ngen.c` is this walker made fast: it keeps `G`, the primes up to `√N`
and a window of primes below `N`, and puts the question to 64 values of `N` at a time.

The question cannot be answered without primes: a "no" for `N` is a Goldbach partition
`N = q + p` with `q ≤ G`, and a walker that is right for every `N` supplies one for every `N`
that is not a term. If some even number has no partition at all, the walker stops announcing
there (`GoldbachGaps/RecordInfinite.lean`).
-/

namespace GoldbachGaps.RecordWalk

open RecordGen

/-- Search for the least Goldbach summand of `N` from `d` upwards (`0` if the fuel runs out). -/
def lgsAux (N : ℕ) : ℕ → ℕ → ℕ
  | 0, _ => 0
  | f + 1, d => if d.Prime ∧ (N - d).Prime then d else lgsAux N f (d + 1)

/-- The least Goldbach summand of `N`, or `0` if `N` is not a sum of two primes. -/
def lgs (N : ℕ) : ℕ := lgsAux N (N + 1) 0

theorem lgsAux_spec (N : ℕ) : ∀ f d : ℕ, (∀ q < d, ¬ IsSummand N q) →
    (lgsAux N f d = 0 ∧ ∀ q < d + f, ¬ IsSummand N q) ∨ IsLeastSummand N (lgsAux N f d)
  | 0, d, h => Or.inl ⟨rfl, by simpa using h⟩
  | f + 1, d, h => by
    simp only [lgsAux]
    split_ifs with hd
    · refine Or.inr ⟨hd, fun p hp => ?_⟩
      by_contra hlt
      exact h p (by omega) hp
    · have h' : ∀ q < d + 1, ¬ IsSummand N q := by
        intro q hq hs
        rcases Nat.lt_or_ge q d with hlt | hge
        · exact h q hlt hs
        · have e : q = d := by omega
          subst e
          exact hd hs
      rcases lgsAux_spec N f (d + 1) h' with ⟨h0, hno⟩ | hl
      · exact Or.inl ⟨h0, fun q hq => hno q (by omega)⟩
      · exact Or.inr hl

/-- `lgs N` is `0` exactly when `N` has no Goldbach summand, and otherwise it is the least. -/
theorem lgs_spec (N : ℕ) :
    (lgs N = 0 ∧ ∀ q, ¬ IsSummand N q) ∨ (lgs N ≠ 0 ∧ IsLeastSummand N (lgs N)) := by
  rcases lgsAux_spec N (N + 1) 0 (fun q hq => by omega) with ⟨h0, hno⟩ | hl
  · refine Or.inl ⟨h0, fun q hs => hno q ?_ hs⟩
    have := lt_of_isSummand hs
    omega
  · refine Or.inr ⟨fun h0 => ?_, hl⟩
    have h2 := hl.1.1.two_le
    unfold lgs at h0
    omega

/-- **The walker.** State: the next even number `N` and the largest least summand `G` so far.
`N` is announced when its least summand exceeds `G`. -/
def walkAux (X : ℕ) : ℕ → ℕ → ℕ → List ℕ
  | 0, _, _ => []
  | f + 1, N, G =>
    if X ≤ N then []
    else if lgs N = 0 then []
    else if G < lgs N then N :: walkAux X f (N + 2) (lgs N)
    else walkAux X f (N + 2) G

/-- **The N generator.** The even numbers below `X` whose least Goldbach summand is larger
than that of every smaller even number from `4` on, in order. -/
def walk (X : ℕ) : List ℕ := walkAux X X 4 0

/-- What the state means when the walker arrives at `N`. -/
structure WInv (N G : ℕ) : Prop where
  even : Even N
  four : 4 ≤ N
  struck : ∀ M, Even M → 4 ≤ M → M < N → ∃ q, q ≤ G ∧ IsSummand M q
  attained : (N = 4 ∧ G = 0) ∨ ∃ N0, N0 < N ∧ Even N0 ∧ 4 ≤ N0 ∧ IsLeastSummand N0 G

theorem isLeastSummand_unique {N a b : ℕ} (ha : IsLeastSummand N a) (hb : IsLeastSummand N b) :
    a = b :=
  le_antisymm (ha.2 b hb.1) (hb.2 a ha.1)

theorem walkAux_spec (X : ℕ) : ∀ (f N G : ℕ), WInv N G → X ≤ N + 2 * f →
    (∀ K, K ∈ walkAux X f N G ↔ N ≤ K ∧ K < X ∧ ∃ g, IsRecord K g) ∧
      (walkAux X f N G).Pairwise (· < ·) := by
  intro f
  induction f with
  | zero =>
    intro N G _ hX
    simp only [walkAux]
    exact ⟨fun K => ⟨fun h => absurd h (by simp), fun h => by omega⟩, List.Pairwise.nil⟩
  | succ f ih =>
    intro N G I hX
    simp only [walkAux]
    split_ifs with hXN h0 hG
    · exact ⟨fun K => ⟨fun h => absurd h (by simp), fun h => by omega⟩, List.Pairwise.nil⟩
    · -- `N` is not a sum of two primes: nothing from here on is a term
      rcases lgs_spec N with ⟨_, hno⟩ | ⟨hne, _⟩
      · refine ⟨fun K => ⟨fun h => absurd h (by simp), ?_⟩, List.Pairwise.nil⟩
        rintro ⟨hNK, _, g, hE, h4, hl, hall⟩
        rcases Nat.eq_or_lt_of_le hNK with rfl | hlt
        · exact (hno g hl.1).elim
        · obtain ⟨q, _, hs⟩ := hall N I.even I.four hlt
          exact (hno q hs).elim
      · exact absurd h0 hne
    · -- the least summand of `N` exceeds `G`: `N` is a term
      rcases lgs_spec N with ⟨h00, _⟩ | ⟨_, hl⟩
      · exact absurd h00 h0
      have hrec : IsRecord N (lgs N) := ⟨I.even, I.four, hl, fun M hE h4 hM => by
        obtain ⟨q, hq, hs⟩ := I.struck M hE h4 hM
        exact ⟨q, by omega, hs⟩⟩
      have I' : WInv (N + 2) (lgs N) := by
        refine ⟨Even.add I.even even_two, by have := I.four; omega, fun M hE h4 hM => ?_,
          Or.inr ⟨N, by omega, I.even, I.four, hl⟩⟩
        rcases Nat.lt_or_ge M N with hlt | hge
        · obtain ⟨q, hq, hs⟩ := I.struck M hE h4 hlt
          exact ⟨q, by omega, hs⟩
        · have e : M = N := by
            obtain ⟨a, ha⟩ := hE
            obtain ⟨b, hb⟩ := I.even
            omega
          subst e
          exact ⟨lgs M, le_rfl, hl.1⟩
      obtain ⟨hmem, hsorted⟩ := ih (N + 2) (lgs N) I' (by omega)
      refine ⟨fun K => ?_, List.pairwise_cons.mpr ⟨fun K hK => ?_, hsorted⟩⟩
      · rw [List.mem_cons, hmem]
        constructor
        · rintro (rfl | ⟨h1, h2, h3⟩)
          · exact ⟨le_rfl, by omega, lgs K, hrec⟩
          · exact ⟨by omega, h2, h3⟩
        · rintro ⟨h1, h2, g, hr⟩
          rcases Nat.eq_or_lt_of_le h1 with rfl | hlt
          · exact Or.inl rfl
          · refine Or.inr ⟨?_, h2, g, hr⟩
            obtain ⟨a, ha⟩ := hr.1
            obtain ⟨b, hb⟩ := I.even
            omega
      · have := (hmem K).mp hK
        omega
    · -- `N` has a summand at most `G`: not a term
      rcases lgs_spec N with ⟨h00, _⟩ | ⟨_, hl⟩
      · exact absurd h00 h0
      have hnot : ∀ g, ¬ IsRecord N g := by
        rintro g ⟨_, _, hlg, hall⟩
        have e := isLeastSummand_unique hlg hl
        subst e
        rcases I.attained with ⟨_, hG0⟩ | ⟨N0, hN0, hE0, h40, hl0⟩
        · omega
        · obtain ⟨q, hq, hs⟩ := hall N0 hE0 h40 hN0
          have := hl0.2 q hs
          omega
      have I' : WInv (N + 2) G := by
        refine ⟨Even.add I.even even_two, by have := I.four; omega, fun M hE h4 hM => ?_, ?_⟩
        · rcases Nat.lt_or_ge M N with hlt | hge
          · exact I.struck M hE h4 hlt
          · have e : M = N := by
              obtain ⟨a, ha⟩ := hE
              obtain ⟨b, hb⟩ := I.even
              omega
            subst e
            exact ⟨lgs M, by omega, hl.1⟩
        · rcases I.attained with ⟨h4', hG0⟩ | ⟨N0, hN0, hE0, h40, hl0⟩
          · omega
          · exact Or.inr ⟨N0, by omega, hE0, h40, hl0⟩
      obtain ⟨hmem, hsorted⟩ := ih (N + 2) G I' (by omega)
      refine ⟨fun K => ?_, hsorted⟩
      rw [hmem]
      constructor
      · rintro ⟨h1, h2, h3⟩
        exact ⟨by omega, h2, h3⟩
      · rintro ⟨h1, h2, g, hr⟩
        refine ⟨?_, h2, g, hr⟩
        rcases Nat.eq_or_lt_of_le h1 with rfl | hlt
        · exact absurd hr (hnot g)
        · obtain ⟨a, ha⟩ := hr.1
          obtain ⟨b, hb⟩ := I.even
          omega

/-- The state before the first number. -/
theorem winv_init : WInv 4 0 :=
  ⟨⟨2, rfl⟩, le_rfl, fun M _ h4 hM => by omega, Or.inl ⟨rfl, rfl⟩⟩

/-- **The N generator is correct.** For every bound `X`, the walker announces `N` exactly when
`N < X` is a term of A025018: its least Goldbach summand is larger than that of every smaller
even number from `4` on. -/
theorem mem_walk {X N : ℕ} : N ∈ walk X ↔ N < X ∧ ∃ g, IsRecord N g := by
  rw [walk, (walkAux_spec X X 4 0 winv_init (by omega)).1 N]
  constructor
  · rintro ⟨_, h2, h3⟩
    exact ⟨h2, h3⟩
  · rintro ⟨h2, g, hr⟩
    exact ⟨hr.2.1, h2, g, hr⟩

/-- The terms are announced in increasing order. -/
theorem walk_sorted (X : ℕ) : (walk X).Pairwise (· < ·) :=
  (walkAux_spec X X 4 0 winv_init (by omega)).2

/-- **The walker and the sieve are the same generator:** `walk X` is the list of the numbers
produced by `RecordGen.records X`. -/
theorem walk_eq_map_records (X : ℕ) : walk X = (records X).map Prod.fst := by
  refine List.Pairwise.eq_of_mem_iff (walk_sorted X) ?_ fun N => ?_
  · rw [List.pairwise_map]
    exact (records_sorted X).imp fun h => h.1
  · rw [mem_walk, mem_map_fst_records]

/-- **What the question looks at.** "No prime `q ≤ G` is a Goldbach summand of `N`" is the same
as "no prime `p < N` within `G` of `N` lies at a prime distance from `N`". -/
theorem not_isSummand_iff_neighbours {G N : ℕ} :
    (∀ q ≤ G, ¬ IsSummand N q) ↔ ∀ p, p.Prime → p < N → N - p ≤ G → ¬ (N - p).Prime := by
  constructor
  · intro h p hp hpN hG hd
    refine h (N - p) hG ⟨hd, ?_⟩
    have e : N - (N - p) = p := by omega
    rwa [e]
  · intro h q hq hs
    have hqN := lt_of_isSummand hs
    have h2 := hs.1.two_le
    refine h (N - q) hs.2 (by omega) (by omega) ?_
    have e : N - (N - q) = q := by omega
    rw [e]
    exact hs.1

/-- A number from `2` on is composite exactly when a prime `r` with `r * r ≤ n` divides it. -/
theorem not_prime_iff_exists_wheel {n : ℕ} (h : 2 ≤ n) :
    ¬ n.Prime ↔ ∃ r, r.Prime ∧ r * r ≤ n ∧ r ∣ n := by
  constructor
  · intro hn
    refine ⟨n.minFac, Nat.minFac_prime (by omega), ?_, Nat.minFac_dvd n⟩
    have := Nat.minFac_sq_le_self (by omega) hn
    rwa [sq] at this
  · rintro ⟨r, hr, hsq, hdvd⟩ hn
    have e : r = n := (Nat.prime_dvd_prime_iff_eq hr hn).mp hdvd
    subst e
    have := hr.two_le
    nlinarith

/-- **The question, asked of `N` alone.** `N` has no Goldbach summand up to `G` exactly when
its residues modulo the small primes cover the strikers: for every prime `q ≤ G` there is a
prime `r` with `r² ≤ N - q` and `N ≡ q (mod r)`. -/
theorem beats_iff_wheels {N G : ℕ} (hG : G + 2 ≤ N) :
    (∀ q ≤ G, ¬ IsSummand N q) ↔
      ∀ q ≤ G, q.Prime → ∃ r, r.Prime ∧ r * r ≤ N - q ∧ N % r = q % r := by
  constructor
  · intro h q hq hqp
    have hnp : ¬ (N - q).Prime := fun hp => h q hq ⟨hqp, hp⟩
    obtain ⟨r, hr, hsq, hdvd⟩ := (not_prime_iff_exists_wheel (by omega)).mp hnp
    exact ⟨r, hr, hsq, ((Nat.modEq_iff_dvd' (by omega)).mpr hdvd).symm⟩
  · intro h q hq hs
    obtain ⟨r, hr, hsq, hmod⟩ := h q hq hs.1
    have hdvd : r ∣ N - q := (Nat.modEq_iff_dvd' (by omega)).mp (Eq.symm hmod)
    exact (not_prime_iff_exists_wheel (by omega)).mpr ⟨r, hr, hsq, hdvd⟩ hs.2

/-- **The walker below `2^20`**: it announces these 21 numbers and no others. -/
theorem walk_two_pow_20 : walk (2 ^ 20) =
    [4, 6, 12, 30, 98, 220, 308, 556, 992, 2642, 5372, 7426, 43532, 54244, 63274, 113672,
      128168, 194428, 194470, 413572, 503222] := by
  rw [walk_eq_map_records, records_two_pow_20]
  rfl

end GoldbachGaps.RecordWalk
