# The function-field statements, as they stand in Lean

Files: `Stickelberger.lean`, `ParityDesert.lean` and `Families.lean` in this directory, namespace
`GoldbachGaps.FunctionField`. Every theorem depends on `propext`, `Classical.choice` and
`Quot.sound` only. Notation in the paraphrases: `n = deg N`, `d = deg Q`, `λ` the leading
coefficient of `N`, `e = deg Q'`, `ℓ` the leading coefficient of `Q'`. "Every irreducible factor
of `Q'` divides `N`" is the hypothesis `∀ π, Irreducible π → π ∣ derivative Q → π ∣ N`. The
signatures below are the output of `#check`, unedited.

## Any field `F`

### `resultant_congr_of_roots`

If every irreducible factor of `g` divides `h₁ - h₂` (the two agree at every root of `g`), then `Res(g, h₁; deg g, n₁) = lc(g)^(n₁ - n₂) · Res(g, h₂; deg g, n₂)` for formal degrees `n₂ ≤ n₁` bounding the true ones.

```lean
@resultant_congr_of_roots : ∀ {F : Type u_1} [inst : Field F] {g h₁ h₂ : Polynomial F} {n₁ n₂ : ℕ},
  h₁.natDegree ≤ n₁ →
    h₂.natDegree ≤ n₂ →
      n₂ ≤ n₁ →
        (∀ (π : Polynomial F), Irreducible π → π ∣ g → π ∣ h₁ - h₂) →
          g.resultant h₁ g.natDegree n₁ = g.leadingCoeff ^ (n₁ - n₂) * g.resultant h₂ g.natDegree n₂
```

### `discr_sub`

`Q` monic, `N' = 0`, `d = deg Q ≠ 0` in `F`, `d < n = deg N`, every irreducible factor of `Q'` divides `N`. Then `discr (N - Q) = (-1)^(n(n-1)/2 + nd + (d-1) + d(d-1)/2) · λ^(n-d-1) · d^(n-d) · discr Q`, `λ` the leading coefficient of `N`.

```lean
@discr_sub : ∀ {F : Type u_1} [inst : Field F] {N Q : Polynomial F},
  Q.Monic →
    Polynomial.derivative N = 0 →
      ↑Q.natDegree ≠ 0 →
        Q.natDegree < N.natDegree →
          (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) →
            (N - Q).discr =
              (-1) ^
                      (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree * Q.natDegree + (Q.natDegree - 1) +
                        Q.natDegree * (Q.natDegree - 1) / 2) *
                    N.leadingCoeff ^ (N.natDegree - Q.natDegree - 1) *
                  ↑Q.natDegree ^ (N.natDegree - Q.natDegree) *
                Q.discr
```

### `discr_sub_general`

The same without `d ≠ 0`: `Q` monic with `Q' ≠ 0`, `e = deg Q'`, `ℓ = lc(Q')`. Then `discr (N - Q) = (-1)^(n(n-1)/2 + n + ne + e + ed + d(d-1)/2) · λ^(n-2-e) · ℓ^(n-d) · discr Q`.

```lean
@discr_sub_general : ∀ {F : Type u_1} [inst : Field F] {N Q : Polynomial F},
  Q.Monic →
    Polynomial.derivative N = 0 →
      Polynomial.derivative Q ≠ 0 →
        Q.natDegree < N.natDegree →
          (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) →
            (N - Q).discr =
              (-1) ^
                      (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree +
                              N.natDegree * (Polynomial.derivative Q).natDegree +
                            (Polynomial.derivative Q).natDegree +
                          (Polynomial.derivative Q).natDegree * Q.natDegree +
                        Q.natDegree * (Q.natDegree - 1) / 2) *
                    N.leadingCoeff ^ (N.natDegree - 2 - (Polynomial.derivative Q).natDegree) *
                  (Polynomial.derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree) *
                Q.discr
```

### `discr_sub_eq_resultant`

No condition on the roots of `Q'`. `N' = 0`, `Q' ≠ 0`, `deg Q < n = deg N`, `e = deg Q'`: `discr (N - Q) = (-1)^(n(n-1)/2 + n + ne) · λ^(n-2-e) · Res(Q', N - Q)`.

```lean
@discr_sub_eq_resultant : ∀ {F : Type u_1} [inst : Field F] {N Q : Polynomial F},
  Polynomial.derivative N = 0 →
    Polynomial.derivative Q ≠ 0 →
      Q.natDegree < N.natDegree →
        (N - Q).discr =
          (-1) ^
                (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree +
                  N.natDegree * (Polynomial.derivative Q).natDegree) *
              N.leadingCoeff ^ (N.natDegree - 2 - (Polynomial.derivative Q).natDegree) *
            (Polynomial.derivative Q).resultant (N - Q) (Polynomial.derivative Q).natDegree N.natDegree
```

### `discr_sub_congr`

For `N₁`, `N₂` with zero derivative, the same degree above `deg Q` and the same leading coefficient: if `Q'` divides `N₁ - N₂` then `discr (N₁ - Q) = discr (N₂ - Q)`. The discriminant depends on `N` only through its degree, its leading coefficient and its residue modulo `Q'`.

```lean
@discr_sub_congr : ∀ {F : Type u_1} [inst : Field F] {N₁ N₂ Q : Polynomial F},
  Polynomial.derivative N₁ = 0 →
    Polynomial.derivative N₂ = 0 →
      Polynomial.derivative Q ≠ 0 →
        Q.natDegree < N₁.natDegree →
          N₁.natDegree = N₂.natDegree →
            N₁.leadingCoeff = N₂.leadingCoeff → Polynomial.derivative Q ∣ N₁ - N₂ → (N₁ - Q).discr = (N₂ - Q).discr
```

### `squarefree_sub`

`Q` irreducible, `N' = 0`, `Q' ≠ 0`, every irreducible factor of `Q'` divides `N`: `N - Q` is squarefree.

```lean
@squarefree_sub : ∀ {F : Type u_1} [inst : Field F] {N Q : Polynomial F},
  Irreducible Q →
    Polynomial.derivative N = 0 →
      Polynomial.derivative Q ≠ 0 →
        (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) → Squarefree (N - Q)
```

### `discr_mul`

`discr (f g) = discr f · discr g · Res(f, g)²` for `f`, `g` of degree at least 1.

```lean
@discr_mul : ∀ {F : Type u_1} [inst : Field F] {f g : Polynomial F},
  1 ≤ f.natDegree → 1 ≤ g.natDegree → (f * g).discr = f.discr * g.discr * f.resultant g ^ 2
```

### `discr_C_mul`

`discr (c f) = c^(2 deg f - 2) · discr f` for `c ≠ 0`, `deg f ≥ 1`.

```lean
@discr_C_mul : ∀ {F : Type u_1} [inst : Field F] {c : F},
  c ≠ 0 → ∀ {f : Polynomial F}, 1 ≤ f.natDegree → (Polynomial.C c * f).discr = c ^ (2 * f.natDegree - 2) * f.discr
```

### `discr_nodal`

`discr (∏_{i<n} (X - r_i)) = (∏_{i<j} (r_j - r_i))²` for `n ≥ 1`.

```lean
@discr_nodal : ∀ {K : Type u_1} [inst : Field K] (n : ℕ),
  1 ≤ n → ∀ (r : Fin n → K), (Lagrange.nodal Finset.univ r).discr = (∏ i, ∏ j > i, (r j - r i)) ^ 2
```

### `frob_det_vandermonde`

If `x ↦ x^q` is a ring homomorphism of `K` and `β^(q^(n+1)) = β`, the Vandermonde determinant `δ` of `β, β^q, …, β^(q^n)` satisfies `δ^q = (-1)^n δ`.

```lean
@frob_det_vandermonde : ∀ {K : Type u_1} [inst : Field K] (φ : K →+* K) (q n : ℕ),
  (∀ (x : K), φ x = x ^ q) →
    ∀ (β : K),
      β ^ q ^ (n + 1) = β →
        (Matrix.vandermonde fun i ↦ β ^ q ^ ↑i).det ^ q = (-1) ^ n * (Matrix.vandermonde fun i ↦ β ^ q ^ ↑i).det
```

## Finite field `F` of odd characteristic (`ringChar F ≠ 2`); `χ = quadraticChar F`

### `quadraticChar_discr_of_irreducible_of_monic`

`g` monic irreducible: `χ(discr g) = (-1)^(deg g + 1)`.

```lean
@quadraticChar_discr_of_irreducible_of_monic : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F]
  [inst_2 : DecidableEq F],
  ringChar F ≠ 2 → ∀ {g : Polynomial F}, Irreducible g → g.Monic → (quadraticChar F) g.discr = (-1) ^ (g.natDegree + 1)
```

### `stickelbergerSwan`

**Stickelberger's theorem in Swan's form (Pellet's formula).** `StickelbergerSwan F` is the statement: if `ringChar F ≠ 2`, then for every squarefree `g`, `χ(discr g) = (-1)^(deg g + r)`, `r` the number of normalized irreducible factors of `g`. `stickelbergerSwan F` proves it for every finite field.

```lean
stickelbergerSwan : ∀ (F : Type u_1) [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F], StickelbergerSwan F
```

### `parity_card_factors`

Hypotheses of `discr_sub` with `Q` irreducible. Then `N - Q` is squarefree and, with `r` the number of its irreducible factors, `(-1)^(n + r) = χ(-1)^(n(n-1)/2 + nd + (d-1) + d(d-1)/2) · χ(λ)^(n-d-1) · χ(d)^(n-d) · (-1)^(d+1)`.

```lean
@parity_card_factors : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {N Q : Polynomial F},
      Q.Monic →
        Irreducible Q →
          Polynomial.derivative N = 0 →
            ↑Q.natDegree ≠ 0 →
              Q.natDegree < N.natDegree →
                (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) →
                  Squarefree (N - Q) ∧
                    (-1) ^ (N.natDegree + (UniqueFactorizationMonoid.normalizedFactors (N - Q)).card) =
                      (quadraticChar F) (-1) ^
                              (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree * Q.natDegree + (Q.natDegree - 1) +
                                Q.natDegree * (Q.natDegree - 1) / 2) *
                            (quadraticChar F) N.leadingCoeff ^ (N.natDegree - Q.natDegree - 1) *
                          (quadraticChar F) ↑Q.natDegree ^ (N.natDegree - Q.natDegree) *
                        (-1) ^ (Q.natDegree + 1)
```

### `parity_card_factors_general`

Hypotheses of `discr_sub_general` with `Q` irreducible (then `Q' ≠ 0` is automatic). `(-1)^(n + r) = χ(-1)^(n(n-1)/2 + n + ne + e + ed + d(d-1)/2) · χ(λ)^(n-2-e) · χ(ℓ)^(n-d) · (-1)^(d+1)`.

```lean
@parity_card_factors_general : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {N Q : Polynomial F},
      Q.Monic →
        Irreducible Q →
          Polynomial.derivative N = 0 →
            Q.natDegree < N.natDegree →
              (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) →
                Squarefree (N - Q) ∧
                  (-1) ^ (N.natDegree + (UniqueFactorizationMonoid.normalizedFactors (N - Q)).card) =
                    (quadraticChar F) (-1) ^
                            (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree +
                                    N.natDegree * (Polynomial.derivative Q).natDegree +
                                  (Polynomial.derivative Q).natDegree +
                                (Polynomial.derivative Q).natDegree * Q.natDegree +
                              Q.natDegree * (Q.natDegree - 1) / 2) *
                          (quadraticChar F) N.leadingCoeff ^ (N.natDegree - 2 - (Polynomial.derivative Q).natDegree) *
                        (quadraticChar F) (Polynomial.derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree) *
                      (-1) ^ (Q.natDegree + 1)
```

### `parity_card_factors_resultant`

The parity for any `N` with `N' = 0`, with no condition on the roots of `Q'`: `Q' ≠ 0`, `deg Q < n`, `N - Q` squarefree. `(-1)^(n + r) = χ(-1)^(n(n-1)/2 + n + ne) · χ(λ)^(n-2-e) · χ(Res(Q', N - Q))`. The last factor is a quadratic symbol of `N - Q` modulo `Q'`.

```lean
@parity_card_factors_resultant : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {N Q : Polynomial F},
      Polynomial.derivative N = 0 →
        Polynomial.derivative Q ≠ 0 →
          Q.natDegree < N.natDegree →
            Squarefree (N - Q) →
              (-1) ^ (N.natDegree + (UniqueFactorizationMonoid.normalizedFactors (N - Q)).card) =
                (quadraticChar F) (-1) ^
                      (N.natDegree * (N.natDegree - 1) / 2 + N.natDegree +
                        N.natDegree * (Polynomial.derivative Q).natDegree) *
                    (quadraticChar F) N.leadingCoeff ^ (N.natDegree - 2 - (Polynomial.derivative Q).natDegree) *
                  (quadraticChar F)
                    ((Polynomial.derivative Q).resultant (N - Q) (Polynomial.derivative Q).natDegree N.natDegree)
```

### `parity_card_factors_congr`

`N₁`, `N₂` as in `discr_sub_congr`, both `N₁ - Q` and `N₂ - Q` squarefree: their numbers of irreducible factors have the same parity.

```lean
@parity_card_factors_congr : ∀ {F : Type u_1} [inst : Field F] [Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {N₁ N₂ Q : Polynomial F},
      Polynomial.derivative N₁ = 0 →
        Polynomial.derivative N₂ = 0 →
          Polynomial.derivative Q ≠ 0 →
            Q.natDegree < N₁.natDegree →
              N₁.natDegree = N₂.natDegree →
                N₁.leadingCoeff = N₂.leadingCoeff →
                  Polynomial.derivative Q ∣ N₁ - N₂ →
                    Squarefree (N₁ - Q) →
                      Squarefree (N₂ - Q) →
                        (-1) ^ (UniqueFactorizationMonoid.normalizedFactors (N₁ - Q)).card =
                          (-1) ^ (UniqueFactorizationMonoid.normalizedFactors (N₂ - Q)).card
```

### `isSquare_intCast_of_isSquare_card`

If `|F|` is a square, every element of the prime field (every integer cast) is a square in `F`.

```lean
@isSquare_intCast_of_isSquare_card : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [DecidableEq F],
  ringChar F ≠ 2 → IsSquare (Fintype.card F) → ∀ (c : ℤ), IsSquare ↑c
```

### `not_irreducible_sub_of_isSquare_card`

`|F|` a square, hypotheses of `parity_card_factors`, `λ` not a square: `N - Q` is not irreducible.

```lean
@not_irreducible_sub_of_isSquare_card : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {N Q : Polynomial F},
        Q.Monic →
          Irreducible Q →
            Polynomial.derivative N = 0 →
              ↑Q.natDegree ≠ 0 →
                Q.natDegree < N.natDegree →
                  (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) →
                    ¬IsSquare N.leadingCoeff → ¬Irreducible (N - Q)
```

### `even_card_factors_iff`

`|F|` a square, hypotheses of `parity_card_factors_general`, `λ` not a square: `r` is even if and only if `(-1)^(d + 1 + e) · χ(ℓ)^(n - d) = 1`.

```lean
@even_card_factors_iff : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {N Q : Polynomial F},
        Q.Monic →
          Irreducible Q →
            Polynomial.derivative N = 0 →
              Q.natDegree < N.natDegree →
                (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π ∣ N) →
                  ¬IsSquare N.leadingCoeff →
                    (Even (UniqueFactorizationMonoid.normalizedFactors (N - Q)).card ↔
                      (-1) ^ (Q.natDegree + 1 + (Polynomial.derivative Q).natDegree) *
                          (quadraticChar F) (Polynomial.derivative Q).leadingCoeff ^ (N.natDegree - Q.natDegree) =
                        1)
```

### `desert`

`|F|` a square, `p = ringChar F`, `V` monic and divisible by every irreducible polynomial of degree at most `J`, `c` not a square, `N = c · V^p`. For `Q` monic irreducible with `deg Q ≤ J + 1`, `deg Q < deg N`, and (`deg Q ≤ J` or `deg Q ≠ 0` in `F`): `N - Q` is not irreducible.

```lean
@desert : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {V : Polynomial F} {J : ℕ} {c : F},
        V.Monic →
          (∀ (π : Polynomial F), Irreducible π → π.natDegree ≤ J → π ∣ V) →
            ¬IsSquare c →
              ∀ {Q : Polynomial F},
                Q.Monic →
                  Irreducible Q →
                    Q.natDegree ≤ J + 1 →
                      Q.natDegree ≤ J ∨ ↑Q.natDegree ≠ 0 →
                        Q.natDegree < (Polynomial.C c * V ^ ringChar F).natDegree →
                          ¬Irreducible (Polynomial.C c * V ^ ringChar F - Q)
```

### `desert_of_one_le` (file `DesertDegree.lean`)

The same for `J ≥ 1` without the hypothesis `deg Q < deg N`, which is then automatic: `V` is divisible by `x^(q^J) - x`, so `deg N ≥ p · q^J > J + 1` (`card_pow_le_natDegree`, `natDegree_lt_natDegree_desert`). For `J = 0` the statement is false (`V = 1`, `N = c`, and `c - Q` is linear for `Q` linear).

```lean
@desert_of_one_le : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {V : Polynomial F} {J : ℕ} {c : F},
        1 ≤ J →
          V.Monic →
            (∀ (π : Polynomial F), Irreducible π → π.natDegree ≤ J → π ∣ V) →
              ¬IsSquare c →
                ∀ {Q : Polynomial F},
                  Q.Monic →
                    Irreducible Q →
                      Q.natDegree ≤ J + 1 →
                        Q.natDegree ≤ J ∨ ↑Q.natDegree ≠ 0 → ¬Irreducible (Polynomial.C c * V ^ ringChar F - Q)
```

### `desert_general`

The same with the sign criterion: `deg Q ≤ J + 1`, `deg Q < deg N`, and (`deg Q ≤ J` or `(-1)^(d+1+e) χ(ℓ)^(n-d) = 1`).

```lean
@desert_general : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {V : Polynomial F} {J : ℕ} {c : F},
        V.Monic →
          (∀ (π : Polynomial F), Irreducible π → π.natDegree ≤ J → π ∣ V) →
            ¬IsSquare c →
              ∀ {Q : Polynomial F},
                Q.Monic →
                  Irreducible Q →
                    Q.natDegree ≤ J + 1 →
                      Q.natDegree < (Polynomial.C c * V ^ ringChar F).natDegree →
                        Q.natDegree ≤ J ∨
                            (-1) ^ (Q.natDegree + 1 + (Polynomial.derivative Q).natDegree) *
                                (quadraticChar F) (Polynomial.derivative Q).leadingCoeff ^
                                  ((Polynomial.C c * V ^ ringChar F).natDegree - Q.natDegree) =
                              1 →
                          ¬Irreducible (Polynomial.C c * V ^ ringChar F - Q)
```

### `desert_smooth`

Any degree: `Q` monic irreducible, `deg Q ≠ 0` in `F`, `deg Q < deg N`, and every irreducible factor of `Q'` has degree at most `J`: `N - Q` is not irreducible.

```lean
@desert_smooth : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {V : Polynomial F} {J : ℕ} {c : F},
        V.Monic →
          (∀ (π : Polynomial F), Irreducible π → π.natDegree ≤ J → π ∣ V) →
            ¬IsSquare c →
              ∀ {Q : Polynomial F},
                Q.Monic →
                  Irreducible Q →
                    ↑Q.natDegree ≠ 0 →
                      Q.natDegree < (Polynomial.C c * V ^ ringChar F).natDegree →
                        (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π.natDegree ≤ J) →
                          ¬Irreducible (Polynomial.C c * V ^ ringChar F - Q)
```

### `desert_smooth_general`

Any degree, with the sign criterion `(-1)^(d+1+e) χ(ℓ)^(n-d) = 1` in place of `deg Q ≠ 0`.

```lean
@desert_smooth_general : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    IsSquare (Fintype.card F) →
      ∀ {V : Polynomial F} {J : ℕ} {c : F},
        V.Monic →
          (∀ (π : Polynomial F), Irreducible π → π.natDegree ≤ J → π ∣ V) →
            ¬IsSquare c →
              ∀ {Q : Polynomial F},
                Q.Monic →
                  Irreducible Q →
                    Q.natDegree < (Polynomial.C c * V ^ ringChar F).natDegree →
                      (∀ (π : Polynomial F), Irreducible π → π ∣ Polynomial.derivative Q → π.natDegree ≤ J) →
                        (-1) ^ (Q.natDegree + 1 + (Polynomial.derivative Q).natDegree) *
                              (quadraticChar F) (Polynomial.derivative Q).leadingCoeff ^
                                ((Polynomial.C c * V ^ ringChar F).natDegree - Q.natDegree) =
                            1 →
                          ¬Irreducible (Polynomial.C c * V ^ ringChar F - Q)
```

## File `Families.lean`: the mechanisms seen in the exhaustive enumerations (`scripts/world3/`)

Same namespace, same axioms. Cells first, then symmetry, then parity through the derivative.

### `card_monic_modByMonic_eq`

`P` monic of degree at most `n`, `deg r < deg P`: exactly `q^(n - deg P)` monic polynomials of degree `n` are `r` modulo `P`.

```lean
@card_monic_modByMonic_eq : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] {P : Polynomial F},
  P.Monic →
    ∀ (r : Polynomial F),
      r.degree < P.degree →
        ∀ {n : ℕ},
          P.natDegree ≤ n →
            Nat.card { M // M.Monic ∧ M.natDegree = n ∧ M %ₘ P = r } = Fintype.card F ^ (n - P.natDegree)
```

### `exists_forall_dvd_sub`

Chinese remainders (any field): for pairwise coprime `P i`, `i ∈ s`, some `r₀` is congruent to `r i` modulo `P i` for every `i ∈ s`.

```lean
@exists_forall_dvd_sub : ∀ {F : Type u_1} [inst : Field F] {ι : Type u_2} (s : Finset ι) (P r : ι → Polynomial F),
  ((↑s).Pairwise fun i j ↦ IsCoprime (P i) (P j)) → ∃ r₀, ∀ i ∈ s, P i ∣ r₀ - r i
```

### `card_monic_cell`

**Cells are exactly equidistributed.** Pairwise coprime monic moduli `P i` (`i ∈ s`) of total degree at most `n`, one residue `r i` of degree below `deg P i` for each: exactly `q^(n - ∑ deg P i)` monic polynomials of degree `n` have all these residues. (In the integers the same count is `X / ∏ r ± 1`, `Cap.card_good_sharing_le`.)

```lean
@card_monic_cell : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] {ι : Type u_2} (s : Finset ι)
  (P r : ι → Polynomial F),
  (∀ i ∈ s, (P i).Monic) →
    ((↑s).Pairwise fun i j ↦ IsCoprime (P i) (P j)) →
      (∀ i ∈ s, (r i).degree < (P i).degree) →
        ∀ {n : ℕ},
          ∑ i ∈ s, (P i).natDegree ≤ n →
            Nat.card { M // M.Monic ∧ M.natDegree = n ∧ ∀ i ∈ s, M %ₘ P i = r i } =
              Fintype.card F ^ (n - ∑ i ∈ s, (P i).natDegree)
```

### `irreducible_sub_apply_iff`

Any commutative ring: if a ring automorphism `φ` fixes `N`, then `N - φ Q` is irreducible exactly when `N - Q` is.

```lean
@irreducible_sub_apply_iff : ∀ {R : Type u_1} [inst : CommRing R] (φ : R ≃+* R) {N Q : R},
  φ N = N → (Irreducible (N - φ Q) ↔ Irreducible (N - Q))
```

### `irreducible_comp_X_add_C_iff`

The translate `Q(t + c)` is irreducible exactly when `Q` is.

```lean
@irreducible_comp_X_add_C_iff : ∀ {F : Type u_1} [inst : Field F] {Q : Polynomial F} (c : F),
  Irreducible (Q.comp (Polynomial.X + Polynomial.C c)) ↔ Irreducible Q
```

### `natDegree_comp_X_add_C`

… and has the same degree.

```lean
@natDegree_comp_X_add_C : ∀ {F : Type u_1} [inst : Field F] (Q : Polynomial F) (c : F),
  (Q.comp (Polynomial.X + Polynomial.C c)).natDegree = Q.natDegree
```

### `monic_comp_X_add_C`

… and is monic when `Q` is.

```lean
@monic_comp_X_add_C : ∀ {F : Type u_1} [inst : Field F] {Q : Polynomial F},
  Q.Monic → ∀ (c : F), (Q.comp (Polynomial.X + Polynomial.C c)).Monic
```

### `irreducible_sub_comp_X_add_C_iff`

**Rows succeed in orbits.** If `N(t + c) = N(t)`, then `N - Q(t + c)` is irreducible exactly when `N - Q` is.

```lean
@irreducible_sub_comp_X_add_C_iff : ∀ {F : Type u_1} [inst : Field F] {N Q : Polynomial F} (c : F),
  N.comp (Polynomial.X + Polynomial.C c) = N →
    (Irreducible (N - Q.comp (Polynomial.X + Polynomial.C c)) ↔ Irreducible (N - Q))
```

### `not_irreducible_of_derivative_eq_zero`

Perfect field: a polynomial with zero derivative is not irreducible.

```lean
@not_irreducible_of_derivative_eq_zero : ∀ {F : Type u_1} [inst : Field F] [PerfectField F] {f : Polynomial F},
  Polynomial.derivative f = 0 → ¬Irreducible f
```

### `not_irreducible_sub_of_derivative_eq`

Perfect field: a row with `Q' = N'` never succeeds.

```lean
@not_irreducible_sub_of_derivative_eq : ∀ {F : Type u_1} [inst : Field F] [PerfectField F] {N Q : Polynomial F},
  Polynomial.derivative Q = Polynomial.derivative N → ¬Irreducible (N - Q)
```

### `squarefree_of_derivative_eq_C`

If `f' = γ` is a non-zero constant, `f` is squarefree.

```lean
@squarefree_of_derivative_eq_C : ∀ {F : Type u_1} [inst : Field F] {f : Polynomial F} {γ : F},
  γ ≠ 0 → Polynomial.derivative f = Polynomial.C γ → Squarefree f
```

### `discr_of_derivative_eq_C`

**The discriminant when the derivative is a non-zero constant.** `f' = γ ≠ 0`, `n = deg f ≥ 2`: `discr f = (-1)^(n(n-1)/2) · lc(f)^(n-2) · γ^n`.

```lean
@discr_of_derivative_eq_C : ∀ {F : Type u_1} [inst : Field F] {f : Polynomial F} {γ : F},
  γ ≠ 0 →
    Polynomial.derivative f = Polynomial.C γ →
      2 ≤ f.natDegree →
        f.discr = (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) * f.leadingCoeff ^ (f.natDegree - 2) * γ ^ f.natDegree
```

### `parity_of_derivative_eq_C`

Finite field of odd characteristic, `f' = γ ≠ 0`, `n = deg f ≥ 2`, `r` the number of irreducible factors of `f`: `(-1)^(n + r) = χ(-1)^(n(n-1)/2) · χ(lc f)^(n-2) · χ(γ)^n`.

```lean
@parity_of_derivative_eq_C : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {f : Polynomial F} {γ : F},
      γ ≠ 0 →
        Polynomial.derivative f = Polynomial.C γ →
          2 ≤ f.natDegree →
            (-1) ^ (f.natDegree + (UniqueFactorizationMonoid.normalizedFactors f).card) =
              (quadraticChar F) (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) *
                  (quadraticChar F) f.leadingCoeff ^ (f.natDegree - 2) *
                (quadraticChar F) γ ^ f.natDegree
```

### `even_card_factors_of_derivative_eq_C`

If moreover `n` is even and `χ(-1)^(n(n-1)/2) = 1`, then `r` is even.

```lean
@even_card_factors_of_derivative_eq_C : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {f : Polynomial F} {γ : F},
      γ ≠ 0 →
        Polynomial.derivative f = Polynomial.C γ →
          2 ≤ f.natDegree →
            Even f.natDegree →
              (quadraticChar F) (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) = 1 →
                Even (UniqueFactorizationMonoid.normalizedFactors f).card
```

### `not_irreducible_of_derivative_eq_C`

… and `f` is not irreducible.

```lean
@not_irreducible_of_derivative_eq_C : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F] [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {f : Polynomial F} {γ : F},
      γ ≠ 0 →
        Polynomial.derivative f = Polynomial.C γ →
          2 ≤ f.natDegree →
            Even f.natDegree → (quadraticChar F) (-1) ^ (f.natDegree * (f.natDegree - 1) / 2) = 1 → ¬Irreducible f
```

### `not_irreducible_sub_of_derivative_sub_eq_C`

The same for a row: `N' - Q' = γ ≠ 0` constant, `deg (N - Q)` even and at least 2, `χ(-1)^(n(n-1)/2) = 1`: `N - Q` is not irreducible. For `N = G(t^p) + t² + ct + d` this is every monic quadratic `Q` with linear coefficient other than `c` (and those with linear coefficient `c` have `Q' = N'`).

```lean
@not_irreducible_sub_of_derivative_sub_eq_C : ∀ {F : Type u_1} [inst : Field F] [inst_1 : Fintype F]
  [inst_2 : DecidableEq F],
  ringChar F ≠ 2 →
    ∀ {N Q : Polynomial F} {γ : F},
      γ ≠ 0 →
        Polynomial.derivative N - Polynomial.derivative Q = Polynomial.C γ →
          2 ≤ (N - Q).natDegree →
            Even (N - Q).natDegree →
              (quadraticChar F) (-1) ^ ((N - Q).natDegree * ((N - Q).natDegree - 1) / 2) = 1 → ¬Irreducible (N - Q)
```

### `dvd_sub_iff_of_aligned`

Aligned classes (`N ≡ R` modulo `V`, the same `R` at every modulus): a divisor `π` of `V` divides `N - Q` exactly when it divides `R - Q`.

```lean
@dvd_sub_iff_of_aligned : ∀ {F : Type u_1} [inst : Field F] {N R Q V π : Polynomial F},
  π ∣ V → V ∣ N - R → (π ∣ N - Q ↔ π ∣ R - Q)
```

### `not_irreducible_sub_of_aligned`

**Aligned classes: the rows they strike.** `V` divisible by every irreducible of degree at most `J`, `N ≡ R` modulo `V`, `R - Q` not constant and of degree at most `J`, `deg (N - Q) > J`: `N - Q` is not irreducible. With `R` and `Q` monic of degree `J + 1` this is every `Q` but the `R - c`.

```lean
@not_irreducible_sub_of_aligned : ∀ {F : Type u_1} [inst : Field F] {N R Q V : Polynomial F} {J : ℕ},
  (∀ (π : Polynomial F), Irreducible π → π.natDegree ≤ J → π ∣ V) →
    V ∣ N - R → 0 < (R - Q).natDegree → (R - Q).natDegree ≤ J → J < (N - Q).natDegree → ¬Irreducible (N - Q)
```

## Checks by factorisation

`../../scripts/parity_check/gen_parity.py` (the general parity formula over `F_3`, `F_5`, `F_7`),
`../../scripts/parity_check/smooth_rows.py` (rows of higher degree with a smooth derivative), and
the research session's `goldbach/sublinear/parity_rule.py` on its branch (`even_card_factors_iff`
on all irreducible cubics over `F_9`, `desert_smooth` on the quartics over `F_9`): no
disagreement.
