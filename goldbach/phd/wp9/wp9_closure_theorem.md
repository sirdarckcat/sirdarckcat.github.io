# WP9 — The Divisor-Paradigm Closure Theorem (draft v0.1)

Status: 2026-07-29, first formal draft. Companion: wp9_plan.md (Door 3),
wp8_beyond_covering.md §6 (the three-doors closure argument), wp7_probes.md
(the five probes this theorem is meant to subsume as corollaries).
Everything conjectural is marked [C]; everything proved at this draft's
level of rigor is marked [P]; empirical inputs are marked [V].

## 1. Setting and definitions

Fix the game parameters: bound B (here 10^200), threshold Q (here up to
2×10^5), lnN ≈ lnB. A **construction scheme** for Goldbach deserts is a
pair (F, C):

- **Candidate family** F: a parameter set Θ ⊆ Z^m with |Θ| ≤ poly-size
  description, and an evaluation map N: Θ → 2Z ∩ [1, B) computable in
  poly(log B) time. Its **design cost** is
  cost(F) = ln B − ln |N(Θ)| (nats of search freedom surrendered).
- **Certificate map** C: on input (θ, q), q prime < Q, outputs ⊥ or a
  divisor witness D(θ, q) with 1 < D(θ,q) < N(θ)−q and
  D(θ,q) | N(θ)−q, computable and verifiable in poly(log B).
  **Planted** means the identity D(θ,q) | N(θ)−q holds as an algebraic
  identity over the family (correctness checkable symbolically);
  **extracted** means C discovers the divisor per-instance.
- **Killed set** K(θ) = {q : C(θ,q) ≠ ⊥}; **residual set**
  U(θ) = {q prime < Q} \ K(θ).
- **Effective exponent** E_eff(F, C): the infimum over poly-time search
  procedures over Θ of ln(expected work / work-per-candidate) to find
  θ with all of U(θ)'s complements composite. For the classic cover,
  E_eff = E = |U|·boost/lnN [V: calibrated to ±0.1 over 1.2e9
  candidates].

The **covering frontier** E*(Q, B) is the minimum E over congruence
covers at the boost–kills equilibrium (wp8 §0(c); e.g. E*(122k, 10^199)
= 20.83, E*(200k, ~10^200) ≈ 37.7).

## 2. The theorem

**Closure Theorem [C, target statement].** Let (F, C) be a construction
scheme whose certificate map is planted and expressible in the schema
language L of §4. Assume:
(H1) Hardy–Littlewood-type heuristics for shifted primes in families
     (primality of distinct integers is independent conditional on all
     divisibility data);
(H2) no compositeness test with constant soundness on random rough
     inputs runs in o(one modexp).
Then E_eff(F, C) ≥ E*(Q, B) − o(1). Moreover, extracted certificates on
any window-dense family of targets are factoring-equivalent, and
certificate-free detection is already employed at its known-optimal cost
(one Fermat modexp) by the standard engine.

Informally: within L, nothing beats covering; outside planted-L, the
scheme must either factor or test, and both are at known-cost floors.

## 3. The three lemmas

### Lemma 1 (entropy accounting for planted certificates) [C, partial P]

Let (F, C) be planted. For each certificate "mechanism" in L define its
**certified sub-image density** δ_eff = (density, within a generic
window of width Q at height B, of integers m for which the scheme can
exhibit its planted divisor witness with poly-range parameters). Then
the amortized design cost per certified offset satisfies

  cost per offset ≥ ln(1/δ_eff) − O(ln ln B),

and for every family in L, ln(1/δ_eff) is at least the covering
marginal cost at equilibrium. Cases:

- **(a) Congruence classes** (N ≡ q mod d): δ_eff = 1/d, cost = ln d.
  Exactly the covering accounting. [P — this is the classic count]
- **(b) Univariate identity families** (N = f(m), N−q = A(m)·B(m),
  deg f ≥ 2): the offset value set below Q has ≤ O(Q^{1/deg}) members,
  so at most O(√Q) offsets are certifiable AT ANY PRICE; and the family
  confinement costs (1−1/deg)·lnB. [P at wp7-P2 rigor; the value-set
  bound is classical]
- **(c) Multivariate identity families** (N−q = A(u)·B(u), u ∈ Z^v):
  the REPRESENTABLE set can be window-dense (e.g. products of two
  2-variable quadratic forms reach ~9,300 of the 17,983 prime offsets
  at Q=200k [V, wp8 §6]), BUT the certificate requires exhibiting u,
  and the **balanced-representation principle** [C, the hard case]
  states: parameters enumerable in poly range concentrate on
  divisor-balanced representations (both factors within e^{o(lnB)} of
  each other's scale... precisely: the enumerable slice of the
  representation variety {A(u)·B(u) ∈ window} has density
  δ_eff ≤ e^{−c·lnB} for generic windows), because the fibers over a
  window of relative width Q/B ≈ e^{−(1−o(1))lnB} are Diophantine
  slivers: locating integer points requires either factoring window
  elements (Cornacchia-type algorithms need square roots mod composite
  targets) or exhaustive parameter scans of length e^{Θ(lnB)}.
  Evidence at small scale: §6 scaling study (engine tier-0, measured
  δ_eff(height) for x²−y² windows). Proving (c) in useful generality
  is the open core of WP9; wp9_plan.md carries the fallback (restrict
  L, state (c) as a conjecture with the tier-0 measurements).

### Lemma 2 (correlation exhaustion / independence) [P + H1 + V]

(i) [P] If d > 1 divides N−q₁ and N−q₂ (q₁ ≠ q₂ primes < Q) then
d | q₁−q₂, hence every prime factor of d is < Q. Consequently ANY
mechanism coupling the compositeness of two complements acts through
divisors supported on primes < Q — i.e., through congruence information
mod small primes, which the cover fixes and the sieve harvests
completely (the k-side information-completeness observation, wp8 §6).
(ii) [H1] Conditional on all divisibility data by primes < Q (and the
sieve's B_sieve), the primality indicators of the residual complements
are independent with the Mertens-adjusted rates.
(iii) [V] Empirical support: across three covers and 1.2×10⁹ banked
candidates, |Ê − E| ≤ 0.1 nats (wp7 P5); no residual pairwise structure
is measurable at current scale.

Corollary: "luck-shaping" schemes (choosing N to make residual events
favorably dependent) have no purchase beyond ≤ 0.1 nats: dependence
requires shared small divisors, which is covering by definition.

### Lemma 3 (detector floor — the explicit conditional H2) [open problem]

Statement to be posted: *Does there exist a randomized algorithm which,
given a uniformly random integer n ∈ [X, 2X] with no prime factor
< B₀ = ln^{O(1)} X, decides compositeness with soundness ≥ 2/3 in time
o(M(log X)·log X) (i.e., asymptotically cheaper than one modular
exponentiation)?* Known art: all sub-modexp tests (trial division,
gcd-batches, Jacobi symbols) have soundness o(1) on rough inputs;
Fermat/Miller–Rabin cost exactly one modexp. Any 2×-cheaper detector
with 50% recall halves the cost of every desert search (and much else);
this is the single legitimate cost-floor escape identified by the
closure analysis. Downstream consumer quantified in wp8 §6.

## 4. The schema language L (v0.1)

Grammar over certificate mechanisms (each compiles to: offset
enumerator, symbolic divisor witness, design-cost term):

  L ::= Congruence(d, a)                          # N ≡ a (mod d)
      | PolyImage(f ∈ Z[m], deg ≤ 4; identity N−q = A(m)·B(m))
      | ExpFamily(N = j·aⁿ + c; per-offset order conditions)
      | MultiPoly(A, B ∈ Z[u₁..u_v], deg ≤ 2, v ≤ 3)
      | NormForm(K number field, disc ≤ 10⁴; N−q = Norm_K(α) with
                 exhibited non-unit factorization in O_K)
      | Cyclotomic/Aurifeuillian(Φ_n splittings, n ≤ 200)
      | Compose(L, L)  # depth ≤ 2, e.g. congruence-restricted images

Exclusions by construction: mechanisms whose "certificate" requires a
primality/compositeness decision to define membership (circular), and
per-instance divisor discovery (extraction — handled by the second horn
of the theorem, not by L).

## 5. Falsification protocol (the engine)

A schema instance PASSES (= threatens the theorem) iff simultaneously:
(1) it certifies ≥ c₁·√Q·polylog DISTINCT prime offsets below Q
    (clears the univariate ceiling), with factor-nontriviality checked
    on samples;
(2) its marginal design cost per RESIDUAL kill (against the live cover
    c1 at Q=122k / the 200k rung cover) is < 2.5 nats (beats the
    covering endgame);
(3) its predicted effect would be invisible in banked Ê data (P5
    consistency) — i.e., it activates only on the constructed family.
Any pass is audited by hand and, if it survives, the theorem is false
and the programme pivots to the new mechanism. Engine reports negative
results as (schema, measured kills, measured cost, margin) rows; the
full table is the theorem's empirical appendix.

## 6. Tier-0 calibration — RUN 2026-07-29, all targets green (engine/tier0.py, 2 s)

1. **T1 congruence anchor**: greedy endgame at Q=122,000 measures
   0.87–1.31 (avg 1.01) nats/offset over the last six moduli.
   Refinement surfaced: wp7's 2.5-nat endgame figure is context-bound
   (Q=10⁵ cover); and at Q=122k additional moduli would still be
   net-positive (gain ≈ kills·0.024 > boost cost E/(r−1) ≈ 0.046) —
   there the LNM BUDGET binds, while at Q=200k the boost–kills
   EQUILIBRIUM binds (wp8 §0(c) refined: two regimes, crossover where
   |U|·boost/lnN ≈ (r−1)·kills·boost/lnN i.e. kills ≈ |U|/(r−1)).
2. **T2 wp7-P2 reproduction — EXACT**: best m²−c family below Q=10⁵ is
   c=398 with 113 killable offsets (wp7's hand numbers). Residual-
   targeted sweep vs the live c1 cover: best c=4686 kills 22 residuals
   → 10.5 nats/residual at B=10^200; wp7's quoted 5.8 was at B=10^100
   (115/20) — the two agree exactly once the B-context is aligned.
   Verdict unchanged: dominated by covering's ~1.0-nat endgame.
3. **T3 MultiPoly classification**: irreducible forms (x²+y², x²+3y²,
   x²−2y², x²+xy+y²) → REJECT, representation ≠ compositeness;
   reducible forms (x²−y², 4x²−9y²) → linear factors, so enumerable
   parameters give divisors O(range) → sieve-equivalent; the balanced
   slice is the Fermat-factorization sliver. This mechanizes Lemma
   1(c)'s two rejection horns for the degree-2 case.
4. **T4 ExpFamily accounting**: ord₂(s) | s−1 gives ≤0.69 nats of
   apparent per-condition saving, but the order-condition kills ONE
   offset where the plain congruence class mod the same s kills
   ~π(Q)/(s−1); wp7-P3's "reduces to covering" is now an inequality
   the engine checks per schema.

Zero passes at tier 0, as the theorem predicts. Next: the exhaustive
tier (~10⁴ schemas over the full L grammar, delegated), then the
generative tier — fitness = the §5 filter — for which AlphaEvolve
access has been offered; the harness contract is: proposal = schema in
L-extended grammar, score = (distinct residual kills, marginal
nats/kill margin vs benchmark, P5-consistency), any PASS audited by
hand before it counts.

## 7. Lemma 2, rigorous form (drafted 2026-07-29)

**Proposition 2a (deterministic; proved).** Let N be even, q₁ ≠ q₂ odd
primes < Q, and d > 1 with d | N−q₁ and d | N−q₂. Then d | q₁−q₂, so
every prime factor of d is ≤ |q₁−q₂| < Q. ∎ (Subtraction.)

**Consequence.** Define F_<Q = the σ-algebra generated by the events
{s | N−q : s prime < Q, q prime < Q} over any candidate ensemble.
Proposition 2a says: every divisor event involving TWO complements is
F_<Q-measurable. Hence any construction scheme's leverage over the
JOINT distribution of complement compositeness, beyond what it exerts
through F_<Q, is empty — and F_<Q is exactly the information the cover
fixes (classes) and the sieve harvests (k-residues); the engine
consumes all of it (wp8 §6, information-completeness).

**Hypothesis H1 (stated).** Conditional on F_<Q ∨ (sieve data to B),
the primality indicators of distinct residual complements are
independent, with the Mertens-adjusted rates; formally the standard
Hardy–Littlewood/Cramér–Granville local model for shifted primes in a
fixed progression.

**Proposition 2b (conditional on H1).** For any planted scheme, the
residual lottery factorizes: P(all residual complements composite) =
∏_q (1 − p_q)(1 + o(1)), p_q = boost/lnN. Hence E_eff decomposes as
design cost + Σ p_q, which is the covering objective. ∎ (Immediate.)

**Empirical support [V].** Three covers, 1.2×10⁹ banked candidates:
|Ê − E| ≤ 0.1 nats (wp7-P5); per-slice Ê stable across 500+ logged
slices of campaigns 1–3 (p̂ within ±2% of model throughout). Any
H1-violation exploitable at our scales is bounded by ≤ 0.1 nats.

## 8. Exhaustive tier — RUN 2026-07-29 (engine/exhaustive.py, 13,661 instances, 1 s)

**Result: 0 passes.** Verdict distribution: 400 Congruence-composite
(BASELINE — inside the paradigm; every composite d dominated by its
prime factor at cost ratio ln d/ln p for equal-or-fewer kills, wp7-P1
mechanized), 12,579 PolyImage (REJECT — value-set ceiling; best
instance remains k=2, c=398), 36 ExpFamily (REJECT), 324
MultiPoly-binquad (REJECT — irreducible ⇒ representation ≠
compositeness; reducible ⇒ sieve-equivalent), 4 MultiPoly-quartic
(REJECT — measured), 60 NormForm (REJECT — reduces to quartic case),
198 Cyclotomic (REJECT — degree-φ(n) ceiling), 60 Compose (BASELINE;
super-additivity audit: all joint overlaps within 3σ Poisson of the
additive prediction — no interaction found in 60 samples).

**Filter-audit note (methodological, kept for honesty).** The first run
produced 16 spurious PASSes: congruence-containing schemas leaked
through the escape filter with fresh-universe kill counts. The fix is
semantic, not numeric: schemas inside the covering paradigm are
BASELINE (the filter measures escapes FROM the paradigm, and the
paradigm cannot escape itself); Compose passes only on statistically
significant super-additivity. Zero real passes before and after.

**Near-miss board (all REJECT, ranked by nats per residual kill):**
ExpFamily j·2ⁿ+c at 3.09–4.2 (one offset per order-condition; 3× the
1.0-nat covering endgame — the closest non-covering family, exactly as
wp7-P3 predicted), then nothing below 10. PolyImage's best residual-
targeted instance: 10.5 (B=10^200 accounting).

**Lemma 1(c) first data — the enumeration wall, measured.** For quartic
products A(u,v)·B(u,v) (two irreducible quadratic factors, the
certificate-bearing case), enumeration work per certified in-window
offset scales as height^θ with measured θ = 0.50, 0.59, 0.74 across
three forms (theory for the balanced sliver: θ = 1/2), and windows at
height 10^10 already contain ZERO enumerable hits at width 10^4.
Extrapolated to B = 10^200: ≥ 10^100 operations per certified offset.
The balanced-representation principle now has numbers; formalizing the
θ ≥ 1/2 lower bound for L's multivariate families is the remaining
mathematical core of Lemma 1.

## 9. Lemma 1(c) for products of two quadratic forms — proof draft (2026-07-29)

Let A, B be positive-definite integral binary quadratic forms and
G = A·B (the certificate-bearing quartic case: G(u,v) = N − q exhibits
the factorization). Window width W ~ Q = X^{o(1)} at height X = B.

**Prop 9.1 (value density) [P].** Area{G ≤ t} = c_G·t^{1/2}, so the
number of parameter points with G ∈ [t, t+W], averaged over window
position, is Θ(W·t^{−1/2}); and the number of representations of any
single integer m is O(m^ε) (each representation induces a divisor
splitting m = A(u,v)·B(u,v), and r_A, r_B = O(m^ε) classically). This
is the measured θ = 1/2 (§8): work per certified offset in black-box
enumeration ~ X^{1/2}.

**Prop 9.2 (cluster bound — the adversarial-window case) [P,
first-moment].** The scheme chooses N, hence the window; can it center
the window on a CLUSTER of G-values? Distinct G-values below X number
~c·X^{1/2}; a first-moment count of k-clusters within a width-Q window
gives E[#k-clusters] ≈ X^{1/2}·(Q·X^{−1/2})^{k−1} = Q^{k−1}X^{−(k−2)/2}.
At X = 10^200, Q = 2×10^5: k = 2 clusters exist in abundance (~Q of
them), but k = 3 already has expected count Q²·X^{−1/2} ≈ 10^{−89}.
**Conclusion: a same-variable quartic-product scheme certifies at most
2 offsets per candidate below 10^200** (whp over any construction
ensemble; up to the O(m^ε) multiplicity of Prop 9.1) — versus the
~18,000 required. Lemma 1(c) holds for this subfamily UNCONDITIONALLY
on average — not because enumeration is hard, but because the
certificates almost never exist: δ_eff = Θ(X^{−1/2}) is an existence
statement, with the enumeration wall (§8 measurements) as its
algorithmic shadow.

**Prop 9.3 (disjoint-variable products) [P, economics].** If A(u) and
B(u′) use disjoint variables, the certificate is m = d₁·d₂ with
d₁ ∈ Im(A), d₂ ∈ Im(B) freely chosen. Enumerable small d₁ ≤ T:
the certified offsets are exactly q ≡ N (mod d₁) — a CONGRUENCE
certificate, already inside the covering accounting (and Im(A)
membership adds nothing: the divisor does the work). Genuinely
non-congruence mass needs d₁ > Q, where each d₁ certifies < 1 expected
offset and the construction must spend ln d₁ > ln Q ≈ 11.7 nats to
plant it — the large-prime endgame, dominated (tier-0 T1: covering
endgame ≈ 1.0 nats/offset). So disjoint-variable products reduce to
covering economics entirely.

**Status after §9.** Lemma 1 is now [P] for: congruence classes (a),
univariate identities (b), same-variable quadratic products (9.2),
disjoint-variable products (9.3), with (9.2) the strongest form —
existence-based, needing no hardness hypothesis. Remaining [C]: degree
> 2 factors, > 3 variables with shared support, and non-polynomial
planted families (the L grammar's outer edge); the general
balanced-representation principle stays a conjecture with §8's
measurements as evidence. The theorem's overall status upgrades from
"conditional sketch" to "proved on the swept grammar, conjectural at
the grammar's boundary".

## 10. Lemma 1(c) at the outer edge: the (d₁, d₂, v) landscape (2026-07-29)

Factors of degrees d₁, d₂ ≥ 2 (degree-1 factors are sieve-equivalent,
§8) in v shared variables; d = d₁+d₂; value-set density exponent
α = min(1, v/d) (measured for (2,2,3): α̂ = 0.761 vs 0.750 predicted,
windows of width 10⁴ at heights 10⁶–10¹⁰; engine log in git).

**Prop 10.1 (cluster ceiling — closes every v < d combo)** [P modulo
standard equidistribution of form values]. The first-moment count of
k-clusters of G-values in width-Q windows below X is
X^α·(X^{α−1}Q)^{k−1}, so clusters exist only up to

  k_max(α) = 1 + ⌊α·lnX / ((1−α)·lnX − lnQ)⌋   (finite iff α < 1 − lnQ/lnX).

At X = 10^200, Q = 2×10^5 (threshold α* = 0.9735): every v < d combo
has α ≤ (d−1)/d ≤ 0.9 < α*, hence k_max = O(1):

| combo | α | k_max | | combo | α | k_max |
|---|---|---|---|---|---|---|
| (2,2,2) | 0.500 | 2 | | (2,2,3) | 0.750 | 4 |
| (2,3,3) | 0.600 | 2 | | (2,3,4) | 0.800 | 5 |
| (2,4,4),(3,3,4) | 0.667 | 3 | | (2,4,5),(3,3,5) | 0.833 | 6 |
| (3,4,5) | 0.714 | 3 | | any v<d | ≤0.9 | ≤ 13 |

A scheme needs ~π(Q) ≈ 18,000 certified offsets per candidate; k_max ≤ 13
means every shared-variable identity family with v < d certifies O(1)
offsets — **negligible at any price**. This subsumes §9's k=3 argument
(the (2,2,2) row) and closes the entire v < d quadrant, including all
combos expressible in the current grammar (v ≤ 3 admits no v ≥ d case
with both degrees ≥ 2). **Within-grammar, Lemma 1(c) is now closed by
first-moment counting alone.**

**Prop 10.2 (the dense frontier v ≥ d — out of grammar, two horns)**
[C, quantified + structural sketch]. For v ≥ d the value set is
window-dense (α = 1) and existence no longer obstructs; the closure
must come from access:
(i) *Finite-symmetry pairs*: solutions in the window shell form a
    codimension-1 sliver; directed (fiber) enumeration costs
    ~X^{(d−1)/d}/W trials per certified offset (10^{145} at d=4,
    B=10^200, W=Q) — the §8-measured wall generalizes; no orbit
    machinery exists because Aut(A, B) is generically finite.
(ii) *Infinite-symmetry pairs*: a torus action preserving both factors
    forces norm-form structure (the pair is equivalent to relative
    norms through a subfield); then certified factorizations come from
    element factorizations α = β·γ, the parameterization splits into
    independent (β, γ) — the DISJOINT-variable case — and Prop 9.3
    applies: small-norm slice = congruence covering, balanced slice =
    sliver. Unit orbits move representations of the SAME m, never
    multiply distinct certified offsets.
Classifying (ii) rigorously (torus action ⇒ norm structure) is the one
remaining piece of mathematics in Lemma 1; it is a recognizable
algebraic-groups statement, not a heuristic.

**Lemma 1 status after §10: [P] on the entire grammar L (v ≤ 3) modulo
standard value-equidistribution; [C] only for out-of-grammar dense
families (v ≥ d), where the two-horn access argument is quantified but
the symmetry classification is a sketch.** Any grammar extension to
v ≥ 4 must ship with Prop 10.2 hardened first — noted in harness.md's
grammar-extension rule.

## 11. The dense frontier closed: isolation + orbit accounting (2026-07-29)

The v ≥ d case (window-dense values) was left in §10 as a dichotomy
needing a symmetry classification. It does not: two elementary
propositions close it, and the feared "structured access" reduces to
horns the theorem already has.

**Prop 11.1 (local isolation) [P].** Let u₀ solve G(u₀) ∈ window at
height X, G = A·B homogeneous of degree d. Any δ ∈ Z^v with
G(u₀+δ) in a width-2Q window around G(u₀), within the Taylor regime,
satisfies |∇G(u₀)·δ| ≲ Q and |δᵀH(u₀)δ| ≲ Q. The solution set of
these is an ellipsoid slab with principal extents Q·X^{−(d−1)/d}
(gradient direction) and Q^{1/2}·X^{−(d−2)/(2d)} (Hessian directions)
— at X = 10^200, Q = 2×10^5, d = 4: 10^{−145} and 10^{−47}. Every
extent < 1/2, so the only lattice point is δ = 0: **window solutions
are pairwise isolated; there is no local navigation between certified
offsets.** Dense existence is non-constructive by geometry, not by
hardness.

**Prop 11.2 (orbit accounting — symmetry cannot multiply offsets)
[P-shaped].** Let Γ ⊆ GL_v(Z) be any infinite group of structured
moves available to the scheme. Three exhaustive cases:
(i) Γ ⊆ Aut(G): navigation conserves the value m — one offset per
    orbit, harmless.
(ii) Γ ⊆ Aut(A) (wlog): navigation conserves the FACTOR a₀ = A(u₀).
    Every certified value reachable from u₀ carries the planted
    divisor a₀. If base points are enumerable (a₀ ≤ T, poly range),
    the certificate exhibits a divisor ≤ T — sieve-equivalent (§8
    rule). If a₀ ~ X^{1/2} (balanced), base points with B-value
    landing in the width-(Q/a₀) target are a sliver (rel. width
    Q/X ≈ 10^{−195}): Prop 11.1's regime again.
(iii) Mixed words (generators from Aut(A) and Aut(B) alternating):
    reachable (log A, log B) pairs form a coarse 2-generator log
    lattice with steps ~2 log λ ≥ Θ(1); pairs with both coordinates
    ≤ log X number ~(log X)² ≈ 2×10^5, versus a target window of
    relative width 10^{−195} in log A + log B — expected hits
    ~10^{−190}. No alternating-orbit access.
Any remaining access route must solve G(u) = m for PRESCRIBED m — but
a product-form representation IS a nontrivial factorization of m, so
a prescribed-value solver factors the scheme's own rough complements:
that is the theorem's existing EXTRACTION horn (factoring-equivalent),
not a new hypothesis.

**Consequence.** Lemma 1(c) now closes the dense frontier v ≥ d with
no symmetry classification: certified-offset counts are bounded by
(enumerable-small-divisor slice = covering/sieve economics) +
(isolated-sliver slice = X^{(d−1)/d}/W access cost) + (prescribed-value
solving = extraction horn). Combined with §9–§10:

> **Lemma 1 status: [P at draft rigor] on all of L AND its v ≥ d
> extension, modulo (a) standard value-equidistribution inputs,
> (b) H1, and (c) the extraction/factoring horn.** The "1–2 month
> classification item" (wp9_plan phase 5) is dissolved — what remains
> for Lemma 1 is write-up rigor (Taylor-regime uniformity in 11.1;
> the word-combinatorics in 11.2(iii) for non-abelian Γ), not new
> mathematics.
