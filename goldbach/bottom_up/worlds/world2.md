# World 2: linear coupling (list recovery of polynomial CRT codes)

This page answers the research session's request of 26 Nov, 00:15 UTC, for Worlds 2 and 4. Marks: **[P]** proved, **[M]** measured,
**[O]** opinion. Here "the room" means the window of members, measured in nats.

## The dictionary

| our problem (Z) | F_q[t] | coding |
|---|---|---|
| the window N0 + kM, k < K; room ln K = 16.6 | deg N < n; room n ln q | dimension n |
| the later primes s > 463, residue field Z/s | monic irreducibles π of degree d, residue field F_{q^d}, norm Q = q^d | positions; with degree-1 places, Reed–Solomon of length m ≤ q |
| the weights w_s(a): rows killed at N ≡ a (Poisson, mean \|U\|/s, \|U\| = 1,502) | soft weights g_π | soft information |
| the heaviest fraction ρ of the classes | hard lists L_π, \|L_π\| = ρQ | list recovery |
| rate: 16.6 / 1,496 = 0.011 for the places 467–1,999; about 10⁻⁷ for the places to 10⁸ | n / Σ deg π | R |
| target: the top e^−κ (κ ≤ room), e^(room − κ) outputs | the same | an exponential output, not a short list |

**What the members we want look like.** They agree with the lists at a rate ρ(1 + δ), with
δ ≈ √(2(1 − ρ)κ / (ρ m_eff)). For example, δ = 0.39 at ρ = 1/2, κ = 16.6, with the 213 places below 2,000.

## W2.1: Johnson-type decoding loses to scanning at every window size [P, given the decoding radius]

**The decoders.** These are Guruswami–Sudan, Koetter–Vardy, and Guruswami–Sahai–Sudan (GSS) for CRT codes.

**The decoders' guarantee.** They return every N with G(N) = Σ_π g_π(N mod π) ≥ √(ln K · Σ_π ‖g_π‖² / ln Q_π). In F_q[t], replace
ln by the degree.

**The theorem.** Suppose such an N exists at depth κ of G. Take residues at distinct places as independent and uniform (the CRT
idealization) and the tail as Gaussian. Then

    Λ := Σ_π (ln Q_π)/Q_π  ≥  ( √(ln K) − √(2κ · ln Q_min / Q_min) )².

**Proof.** Write m2_π = ‖g_π‖²/Q_π and u_π = √(Q_π m2_π / ln Q_π). The mean of g_π is at most √m2_π = u_π √(ln Q_π/Q_π).

- So E G + z·sd G ≤ ‖u‖ (√Λ + z √(ln Q_min/Q_min)), by Cauchy–Schwarz twice.
- The right-hand side of the guarantee is √(ln K)·‖u‖.
- Set z = √(2κ). ∎

**Weights restricted to a fraction ρ of the classes.** The mean bound becomes √ρ_π·√m2_π, so Λ_ρ = Σ ρ_π ln Q/Q.

- Λ per unit of input is ln Q / Q² whatever the density.
- So the cheapest places are full tables on all primes from 467 up.
- The decoder reads every weight it uses, so its time is at least Σ p over those places.

**Exact prime sums (`johnson_cost.py`, `johnson_cost.out`).**

| window ln K | depth κ | places 467..y | decoder input | ÷ scan of the window |
|---|---|---|---|---|
| 16.6 | 16.6 | y = 5.7·10⁷ | 9.5·10¹³ | 5.8·10⁶ |
| 16.6 | 8.3 | y = 2.2·10⁸ | 1.3·10¹⁵ | 8.2·10⁷ |
| 16.6 | 4.2 | y = 6.0·10⁸ | 9.2·10¹⁵ | 5.7·10⁸ |
| 12.4 | 12.4 | y = 3.0·10⁶ | 3.1·10¹¹ | 1.3·10⁶ |
| 4 (about the window left by two pins) | 4 | y = 8,191 | 3.9·10⁶ | 7.1·10⁴ |
| ln 2 | ln 2 | y = 773 | 2.9·10⁴ | 1.5·10⁴ |

**In F_q[t].** The places of degree d have Σ d/q^d ≤ 1, so Λ is at most the number of degree layers used.

- The places must therefore span about n(1 − ε)² degrees, with ε = √(2 ln Q_min/Q_min)·√(κ/room) ≤ 0.162 at Q_min = 467.
- The input is then at least (q^n)^(2(1−ε)²), that is members^1.40.

**Your Guruswami–Sudan statement [P].**

- **Full agreement.** With degree-1 places, list recovery needs agreement τ > √(nρq/m) ≥ √(nρ), so full agreement needs n < 1/ρ. The
  same holds for any places, since Σ_{deg π = d} d ≤ q^d. Confirmed.
- **The agreement our members have.** At τ = ρ(1 + δ), GS needs n < ρ(1 + δ)², so it returns no member of degree ≥ 1. At q = 467 and
  ρ = 1/2, the region GS guarantees and the region where members exist (n ln q ≥ m·KL(τ‖ρ)) are disjoint.
- **The weighted Johnson radius on the primes 467..y** is √(ρ ln K / 2) = 2.88√ρ. That is at least 2.9 times the random agreement at
  every ρ, and above 1 (unreachable) for ρ > 0.12.

## W2.2: folding and multiplicities buy nothing for separable scores [P]

**What a separable score gives.** A score that is a sum over places gives product lists for folded symbols (L_a1 × … × L_as). It
gives cylinder lists for multiplicities: the value in L_a, every derivative allowed.

**Folding.** Take the Guruswami–Rudra / Parvaresh–Vardy interpolation with s-folding, r variables and multiplicity μ.

- The constraints are N_f (s − r + 1)(ρq)^r C(μ + r, r + 1); the monomials of weighted degree D are D^(r+1) / ((r+1)! (k − 1)^r).
- Decoding needs the agreeing windows to exceed D/μ. That is, a per-place agreement

      β > ( ρ(k − 1) · s/(s − r + 1) )^(1/(r+1)).

- This grows with r when ρ(k − 1) < 1, and is impossible when ρ(k − 1) ≥ 1. So the best is r = 1, which is plain Guruswami–Sudan.
- The linear-algebraic version (Guruswami–Wang) needs the window agreement above (ρq)^r/(r + 1), which is worse.

**Average-case lists.** These conditions depend only on the list sizes. So random product lists fare exactly as worst-case product
lists, and the subfield counterexamples do not enter.

**Multiplicity codes.** With cylinder lists, membership ignores the derivatives. List recovery of the multiplicity code is then
exactly RS list recovery at the same points.

**So** every beyond-Johnson decoder needs lists that correlate coordinates. Separable scores never produce them, in F_q[t] or
anywhere else.

## (b) What folding uses, and prime powers

**Folding uses three things.**
1. A ring automorphism, f(X) ↦ f(γX). It preserves the room and permutes places whose residue fields are isomorphic.
2. The identity f(γX) ≡ f(X)^q (mod X^(q−1) − γ). This bounds the number of solutions of Q(X, f, f∘σ, …) = 0.
3. Lists that correlate the folded coordinates.

**On Z [P].**
- Aut(Z) = {1}. The residue fields Z/p have pairwise different sizes, so no symmetry can permute places. The maps that keep the
  window an interval, x ↦ ±x + c, fix every place.
- So (1) and (2) are absent. (3) is absent in both worlds for separable scores (W2.2), so their absence costs nothing here.

**The nearest substitute for (1) [P/O].**
- Gal(K/Q), for a Galois number field K, permutes the primes above p, which have isomorphic residue fields.
- But a rational N is Galois-fixed, so its conjugate residues coincide and carry no information.
- Members in O_K would be a different problem.

**Multiplicities on Z [P].**
- N mod p² ≅ (N mod p, δ_p N mod p), where δ_p N = (N − N^p)/p is Buium's p-derivation. It is a bijection, since
  δ_p(N + pt) ≡ δ_p N + t.
- But δ_p is not a derivation (δ(ab) = a^p δb + b^p δa + p δa δb), and it differs for each p. So the chain rule that the multiplicity
  decoders use does not exist.
- And a score of N mod s gives cylinder lists in it anyway.

**Prime-power accounting [P].**
- A modulus s^e contributes e ln s/s^e to Λ and costs s^e of input. Λ falls by e/s^(e−1) per place (1/233 at s = 467, e = 2), and by
  e/s^(2(e−1)) per unit of input.
- The hard-list GS condition worsens by √(2/s) per place.
- The extra digits of N are redundancy that a score of N mod s cannot constrain. So prime powers never help decoding here.

## (a) Which known algorithms are output-priced in our regime

- **Interpolation through places of total norm at most the room.** This is pinning (Theorem B): n places of degree 1 in F_q[t], two
  primes ≥ 467 in Z. It is the only one.
- **Johnson-type decoders.** For random lists the guarantee region lies beyond the room unless the input exceeds the scan by ×1.5·10⁴
  or more (W2.1).
- **Folded RS, multiplicity and subspace-design codes.** They need sparse lists (ℓ ≤ |Σ|^O(ε)) that correlate coordinates. Our lists
  are dense and product (W2.2).
- **Bleichenbacher–Nguyen noisy polynomial interpolation and noisy Chinese remaindering [O].** These have full agreement and a single
  planted solution, which a lattice finds as an unusually short vector. Our problem has e^(room − κ) partial-agreement solutions and
  nothing planted.

So the obstruction in this world is the integers' obstruction. It is not the missing automorphism; it is dense product lists at
near-random agreement with an exponential output.

| ingredient | used by | on Z? | substitute and its cost |
|---|---|---|---|
| CRT and interpolation through places of norm ≤ room | pins | yes | — |
| interpolation with multiplicities, then root finding | GS, KV | yes: Coppersmith/Howgrave-Graham lattices (Boneh; GSS) | same radius, at lattice-reduction cost |
| degree as the size of a residue | the radius | yes (ln) | — |
| a place-permuting automorphism that preserves the room | folding | no: Aut Z = 1, residue fields of different sizes | Galois conjugates in O_K; rational N are fixed, so nothing is gained |
| f(γX) ≡ f(X)^q mod E | folding's list bound | no | none |
| derivatives with a chain rule | multiplicity codes | partly: δ_p on Z/p², not a derivation, one per prime | irrelevant here (cylinder lists) |
| lists that correlate coordinates | every beyond-Johnson decoder | no, and not in F_q[t] for separable scores | — |
