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
