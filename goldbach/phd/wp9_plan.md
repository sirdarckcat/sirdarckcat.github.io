# WP9 plan — Door 1 (rounding gap) and Door 3 (closure theorem) in execution detail

Status: 2026-07-29, proposal. Companion to wp8_beyond_covering.md §6.

## Door 1 — the rounding-gap attack

**Problem (exact).** Fixed moduli R = the 88 primes 3..457 (set by the
boost–kills equilibrium); universe P = odd primes < Q. Choose one class
a_r ∈ Z/r per r. Minimize |U(a)| = #{q ∈ P : ∀r, q ≢ a_r}. Worth
0.0240 nats of E per prime saved (boost/lnN at 199d). Landmarks at
Q=122k: random μ=1377 (σ=21.0), greedy/1-opt 867, annealed threshold
≈758 (measured-σ Gaussian), LP fractional 0.

**D1.0 Benchmark + landscape diagnostics (1 day).** Instance files per
rung + scorer. Measure: regret distribution at random vs greedy points;
overlap/backbone between independent ascent solutions (clustering
diagnostic); |U| autocorrelation under single-class moves.

**D1.1 Exact large-neighborhood search (first real test, ~1 week).**
Freeze all but a window W of 8–15 moduli (chosen by regret / kill-set
overlap); re-solve the window EXACTLY with CP-SAT over the critical
sub-universe (currently-uncovered + singly-covered primes only, a few
thousand elements); iterate windows. Strictly stronger than 1-opt (the
current plateau) and than random kicks. Gate: any improvement over 867;
CPU-cost per nat.

**D1.2 Global methods (2–4 weeks, parallel across sessions).**
(a) LP-guided randomized rounding of the fractional optimum + LNS
repair; (b) parallel tempering, 32–64 replicas, exact per-modulus Gibbs
conditionals; (c) population crossover: greedy merge of parent
assignments by marginal coverage + repair; (d) focused Moser–Tardos
resampling: pick uncovered q, set a_r := q mod r for a random eligible
r, repair (WalkSAT-for-coverage); (e) lower-bound track: branch-and-
bound with LP bounds on modulus subsets → first nontrivial certified
floor above 0. Gate: distance to annealed threshold 758.

**D1.3 Beyond the uniform ensemble (the upside, 1–2 months, theory+code).**
(i) Banded construction: exact core for r ≤ 13; middle band random with
second-moment (pairwise-overlap) control; top band r ~ 300–457 solved as
an exact weighted b-matching against the current uncovered set (max-flow
— the greedy endgame's overlap waste is provably avoidable). (ii) Belief
propagation on the factor graph (moduli variables, soft prime factors,
weight e^{−β·uncovered}) → survey-propagation-style decimation; also
yields the quenched threshold prediction for this CSP. Publishable
either way ("message-passing for prime-residue covering").

**D1.4 Deployment + community.** Regenerate all rung covers with the
best method; re-solve the equilibrium (smaller |U| shifts optimal R*
slightly upward). In parallel: package the Q=200k instance + scorer as a
public optimization challenge (Al Zimmermann format) with a small
bounty; we keep verification.

**Success criteria.** −1 nat = worthwhile; −2.5 nats (≈ annealed
threshold, 12×) = expected win; −4+ nats = ensemble/theory breakthrough.
Universal plateau at 867 is also a result: evidence the greedy point IS
the quenched threshold → the D1.2e floor certifies it, write it up.
Cost: CPU only. Every nat multiplies every future rung.

## Door 3 — the closure theorem and its falsification engine

**Target statement (Divisor-Paradigm Closure, conditional).** A
construction scheme is (F, C): a poly-samplable candidate family
{N(θ) < B} plus a poly-verifiable compositeness-certificate map for
offsets. Claim: any scheme whose certificates are expressible in the
schema language L (below) has effective exponent ≥ the covering frontier
− o(1), conditional on (H1) Hardy–Littlewood heuristics for shifted
primes and (H2) no sub-modexp compositeness detector. Proof skeleton:

- **Lemma 1 (entropy accounting for planted certificates).** If the
  certified divisor is a function of the design, the certified offset
  set lies in a union of congruence families (cost ln d each) and
  value-set families; unified inequality: #distinct certified primes ≤
  design entropy / marginal certificate cost. P1–P4 of wp7 become
  corollaries. Research meat: the multivariable case — dense value sets
  exist (binary quadratic forms cover ~9,300/18,000 offsets at Q=200k)
  but factor-nontrivial parameterizations either thin the density or
  make enumeration Diophantine-hard (Cornacchia-mod-composite); this is
  the lemma's hard case and where the theorem could break.
- **Lemma 2 (independence).** Shared divisor of N−q₁, N−q₂ divides
  q₁−q₂ < Q ⇒ any inter-offset correlation is small-modulus covering;
  conditioned on all divisor data ≤ B, residual PRP events are
  independent up to o(1) under H1. (P5's |Ê−E| ≤ 0.1 over 1.2e9
  candidates as empirical support.)
- **Lemma 3 (detector optimality, the explicit conditional).** State H2
  precisely: no randomized test with constant soundness on random rough
  inputs at cost o(one modexp). Cite state of the art; any 2× cheaper
  50%-recall detector would halve search cost — a complexity question
  with a live downstream consumer.

**The engine (falsification arm).** A DSL over schemas: linear
progressions; k·aⁿ ± c families; polynomial images deg ≤ 4, ≤ 3
variables; norm forms disc ≤ 10^4; cyclotomic/Aurifeuillian splittings;
compositions to depth 2. Compiler: schema → (offset enumerator,
certificate, design-entropy cost). Automated WP7-triple filter:
(1) distinct killable primes < Q vs the √Q/value-set ceilings;
(2) marginal nats per new residual kill vs the 2.5-nat covering endgame;
(3) P5-invisibility. Exhaustive tier: ~10^4 schemas, seconds each,
subagent-parallel. Generative tier: LLM-proposed grammar extensions —
reward hacking is auditable here because a "pass" is a checkable numeric
claim, unlike evolved-optimizer fitness. Output: a counterexample
(jackpot: paradigm broken, rebuild everything) or a machine-checked
exhaustion certificate that becomes the theorem's empirical appendix.

**Deliverables + order.** (1) WP9 statement + Lemma 2 write-up: ~1 week.
(2) DSL + exhaustive tier: ~2 weeks, mostly delegated. (3) Lemma 1
restricted-L proof: 1–2 months, the chapter's core. (4) The H2 open
problem posted publicly. Door 3 certifying "no fourth door" is what
makes Door 1's investment safe; Door 1's results feed every rung of the
ladder immediately.

## Door 3 costing (added on request, 2026-07-29)

| component | researcher attention | compute / cash | calendar |
|---|---|---|---|
| WP9 statement + Lemma 2 write-up | 2–3 sessions | ~0 (reuses banked campaign data) | ~1 week |
| DSL + compiler (schema → enumerator, certificate, entropy cost) | the careful part: 1–2 weeks | ~0 | 1–2 weeks |
| Exhaustive tier (~10^4 schemas) | supervision only | 10–30 CPU-h + ~$50–200 of agent tokens | 2–3 days, delegated |
| Generative tier (~10^3 LLM-proposed schemas + audits) | audit passes only | ~$100–500 of agent tokens | 1 week, delegated |
| Lemma 1 (entropy accounting, multivariable case) | THE cost: 1–2 months part-time | ~0 | 1–2 months |
| H2 open-problem note + posting | 1 day | 0 | 1 day |

Total: ≲ $1k cash-equivalent, < 100 CPU-hours, ~6–10 part-time weeks of
attention run alongside Door 1 and the ladder. Cheapest door by 2–3
orders of magnitude (Door 2 is $10^5–10^6-scale; the fleet burns more
CPU per day than the whole engine needs in total). The real currency is
researcher attention, and most of Lemma 1's cost is already owed to the
thesis anyway (WP7 → theorem is the natural chapter); the marginal cost
of Door 3 over "write the thesis properly" is roughly the engine:
~2 weeks + a few hundred dollars of tokens. Abort structure: if Lemma 1
resists, scope shrinks to restricted-L theorem + conjecture (cost capped,
still a chapter); if the engine finds a pass, cost explodes joyfully into
a new research programme, which is the outcome we would pay the most for.
