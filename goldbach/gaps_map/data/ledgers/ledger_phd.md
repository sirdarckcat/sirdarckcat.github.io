# Result ledger: PhD programme "Extremal Least Goldbach Summands" (Goldbach gaps)

Source base: `.../scratchpad/wt/research/goldbach/phd/` (RESEARCH_LOG.md; wp3, wp7, wp8, wp9 plan and closure theorem, wp9/h2, wp10, wp11, wp12 memos; toy_crt/results.md; campaign/CAMPAIGN_PLAN.md; the two cross-reviews; merge_2026-11-21.md; plus the four small .md files under wp9/door1 and wp9/engine, and, as data only, exhaustive_summary.json, instance_q122k.json, and the campaign2/campaign3 search.log files). Read-only; nothing from the repo was run.

Conventions. g(N) = least prime p with N−p prime. Games: Height (Game 1: largest g, N unbounded), Threshold T(Q) (Game 2: smallest N with g > Q), Budget R(B) (Game 3: largest g with N < B). A cover is a set of CRT congruences N ≡ a_r (mod r); U = primes the cover misses; E = |U|·boost/ln N with boost = 2·Π r/(r−1); about e^E candidates are needed per hit. H1 = Hardy–Littlewood-type independence of residual complements given the divisor data; H2 = no compositeness test cheaper than one modexp on rough inputs. Source marks: [P] proved at draft rigor, [C] conjectural, [V] measured, [L] cited from literature and not re-checked. "Lean-checked" appears nowhere: WP12 §4 says the Lean toolchain install was refused, and the RH/GRH claim's Lean archive was never downloaded. `ext:` ids are external results or documents outside the files read (e.g. ext:FRONTIER.md is a parallel session's file that these memos quote).

# GROUP — WP3: sub-100 deserts, subset-sum density and the decoding barrier

## wp3-regime1 | Sub-100 route: Regime-I brute-force price
- kind: empirical
- says: Sub-100-digit deserts exist in abundance (E_random ≈ 110, ~10^52 qualifying N below 10^100), but the best conventional cover at Q = 10^5, B = 10^100 is 44 moduli, M = 10^79, |U| = 1060, boost 9.6, E = 44.1, i.e. 1.4×10^19 candidates ≈ 9×10^5 GPU-years (~$9.4B, "~7 orders of magnitude beyond plausible compute"); FRONTIER.md independently measures realizable E = 43.66 (1.9×10^5 GPU-years at 1.5M cand/s). Costed rungs: 140 d has E 28.1, 1.6e12 candidates, 0.10 A100-yr (~$1k); 130 d E 31.2, 3.6e13, 2.3 yr; 120 d E 34.7, 1.2e15, 73 yr (~$770k).
- status: computed (density model; FRONTIER.md concurs within 0.4 nats)
- uses: model-density, wp3-units-slip, ext:FRONTIER.md
- where: wp3_small_representative_memo.md §1, §3 (Regime I); RESEARCH_LOG.md 2026-07-28 "costed menu" and "master reconciliation"
- matters: fixes the price of the only live route to sub-100 and the fundable frontier (130–140 digits).

## wp3-gss | GSS radius for CRT list decoding
- kind: theorem
- says: Guruswami–Sahai–Sudan (FOCS 2000, Thm 3) find all codewords with Σ a_i z_i log p_i > log(ℓ+1) + (ℓ/2)·log(K/2) + (1/(ℓ+1))·Σ C(z_i+1,2) log p_i; with L classes per position the agreement-mass radius is A > sqrt(L·ln B·P), P = Σ_pool ln p_i, and this form matched the exact finite-ℓ optimum at ratio 1.001–1.004 (pools 5·10^3–10^5, L ∈ {1,2}).
- status: computed (literature theorem, source-verified against GSS Thm 3; radius form checked numerically)
- uses: ext:GSS-FOCS00, ext:Howgrave-Graham
- where: wp3_small_representative_memo.md §2; RESEARCH_LOG.md 2026-07-28 RETRACTION entry
- matters: the decoding side of the barrier that blocks the "decode the CRT code" shortcut.

## wp3-regime2 | Oversized covers: easy if representative found
- kind: proposition
- says: When cover mass exceeds ln B coverage is excellent: 355 moduli of mass 1,019 digits cover all 9,592 primes q < 10^5, and 420 moduli with L = 16 classes give |U| = 165, E = 10.2 (~27,000 candidates); solutions exist (design entropy ~2,698 nats vs ln(M/B) = 2,630, stated surplus ~+57 nats, i.e. ~e^57 pairs below 10^100) but the density of designs whose CRT representative is below B is e^−2630, so enumeration is out by ~1,100 orders of magnitude.
- status: computed (entropy accounting, [V] marks in the memo; see Doubts on 57 vs 68 nats)
- uses: wp3-regime1, model-density
- where: wp3_small_representative_memo.md §3 (Regime II)
- matters: sub-100 becomes easy if and only if small CRT representatives can be found directly.

## wp3-subsetsum | Small representative = density-1.026 subset-sum
- kind: proposition
- says: CRT reconstruction is additive, so "find a design whose representative is < B" is exactly an inhomogeneous modular subset-sum with per-position choices, at density 2698/2630 ≈ 1.026, above the lattice regime (d < 0.94) and out of reach of Wagner: ~2^82 solutions in a ~2^3893 design space, meet-in-the-middle 2^1897, Wagner k-tree 2^938. FRONTIER.md agrees from the constructive side (the classic cover is the unique freely-enumerable design; set-valued conditioning gain saturates at ~H^0.35, worth 1–2.8 nats).
- status: proved-in-text (the reduction) + computed (densities and costs)
- uses: wp3-regime2, ext:Lagarias-Odlyzko, ext:Coster-et-al, ext:Wagner-k-tree, ext:FRONTIER.md
- where: wp3_small_representative_memo.md §4, §7 item 2b
- matters: names the exact hard problem hidden behind the oversized-cover route.

## wp3-barrier | Decodable implies no small representative
- kind: negative-result
- says: Heuristic first-moment barrier: no parameters satisfy both (a) A < ln B + ln C(n,s) + s·ln L (representatives exist) and (b) A > sqrt(L·ln B·P) (GSS-decodable); at pool < 60,000 and L = 16 the radius is 14,845 nats against cover mass 2,860 nats, short by 5.2×. Sub-100 via oversized covers therefore needs CRT list-recovery beyond the Johnson-type radius or a density-1 subset-sum algorithm.
- status: conjectural (first-moment heuristic; the numbers are computed)
- uses: wp3-gss, wp3-subsetsum, wp3-regime2
- where: wp3_small_representative_memo.md §5
- matters: this is the "decoding barrier", the corrected replacement for the retracted "open window".

## wp3-retraction | Retracted: "open window" for CRT decoding
- kind: retraction
- says: WP3 v1 claimed a polynomial-time CRT-decoding attack was open for pool sizes R ≥ 60,000 (table "OPEN at R ≥ 60,000"); v2 shows v1 compared a decoding radius at agreement size s with an existence bound maximised over a different s (≈ 2n/3), and coupling both at the same s closes the window at every pool size. The recalled GSS radius itself was correct (within 0.4%).
- status: retracted (replaced by wp3-barrier)
- uses: wp3-gss
- where: wp3_small_representative_memo.md header and §6; RESEARCH_LOG.md 2026-07-28 "RETRACTION + corrected sub-100 analysis"
- matters: lesson recorded for the thesis: feasibility windows built from separately optimised bounds are worthless; couple the parameters first.

## wp3-units-slip | Retracted: sub-100 cost of 5×10^4 GPU-years
- kind: retraction
- says: The Regime-I cost (E = 44.1, 1.4×10^19 candidates) was first written as ~5×10^4 GPU-years (itself a replacement for a too-pessimistic ~3×10^8 from E ≈ 52), then corrected on 2026-07-28 to ~9×10^5 because it divided by the test rate (8.5M tests/s) instead of the candidate rate (~5×10^5/s at ~17 Fermat tests per candidate); the costed-menu row ($9.4B at 100 digits) was already right.
- status: retracted (replaced by wp3-regime1)
- uses: wp3-regime1
- where: wp3_small_representative_memo.md §3, §7; RESEARCH_LOG.md 2026-07-28 "master reconciliation" and "RETRACTION"
- matters: the stale 5×10^4 survives in wp7_probes.md and one log entry (see Doubts).

## wp3-open | Two open problems under the sub-100 record
- kind: open-problem
- says: (i) CRT list-recovery beyond the Johnson-type radius for structured, solution-abundant instances; (ii) modular subset-sum with choices at density ≈ 1 where ~2^82 planted solutions exist. Together with WP7's three mechanism conditions these are the log's "precisely stated" targets, and the RQ7 chapter is declared complete.
- status: conjectural (open)
- uses: wp3-barrier, wp3-subsetsum, toycrt, wp7-triple, ext:GSS-FOCS00
- where: wp3_small_representative_memo.md §7; RESEARCH_LOG.md 2026-07-28 "Programme position, final"
- matters: solving either would replace the ~9×10^5 GPU-year route by ~27,000 candidates (E = 10.2).

## toycrt | Toy CRT decoder: LLL stops at Johnson radius
- kind: negative-result
- says: A Howgrave-Graham/GSS lattice decoder (FLINT LLL δ = 0.99; 61 positions = odd primes < 300; B = 10^12; A_J = sqrt(ln B·ln M) = 87.380; ℓ ∈ {12,20,30}; 20 trials per ρ; 390 decodes) recovers the planted message only above a sharp threshold at realized agreement ≈ 1.028·A_J (ℓ = 30; determinant-bound theory 1.0354; ℓ = 45 cutoff within (1.0141, 1.0293)), converging to A_J from above like 1 + c/ℓ; below it failure is total (no integer roots) although ~10^2–10^7 alternative solutions are expected, and no non-planted solution was ever found.
- status: computed (390 decodes, deterministic seeds; predeclared sweep 28.5 s on 4 cores)
- uses: wp3-gss, wp3-barrier, ext:Howgrave-Graham
- where: toy_crt/results.md; RESEARCH_LOG.md 2026-07-28 "toy CRT decoder + WP7 probes"
- matters: closes the "practical reduction beats the proof" hope: the Johnson radius behaves as a hard practical barrier for this lattice family.

# GROUP — WP7: mechanisms beyond static covering (five bounded probes)

## wp7-p1 | Prime-power moduli strictly dominated
- kind: negative-result
- says: Replacing a cover modulus p by p² costs ln p more nats and kills zero new offsets, since the class q ≡ a (mod p²) lies inside the class q ≡ a (mod p) (p = 7: 227 ⊂ 1,613), so p² kills p× fewer offsets at 2× the cost.
- status: proved-in-text (class containment, one numeric check)
- uses: —
- where: wp7_probes.md P1
- matters: composite-modulus gadgets reduce to their prime factors with only losses.

## wp7-p2 | Polynomial value-set identities dominated
- kind: negative-result
- says: N = m^k − c makes N − q = m^k − d^k composite for every offset q = d^k − c; the best case k = 2, c = 398 kills 113 offsets below 10^5 but costs 115 nats of search freedom at B = 10^100 (26× worse than average covering; ~5.8 nats per residual kill vs ~2.5, i.e. 2–3× worse than the covering endgame), and any degree ≥ 2 identity has ≤ O(Q^{1/2}) killable offsets (~316 at k = 2) at any price.
- status: proved-in-text (mini-proposition, classical value-set bound) + computed (c = 398 count)
- uses: —
- where: wp7_probes.md P2
- matters: the closest algebraic competitor to covering, and the origin of the √Q ceiling used throughout WP9.

## wp7-p3p4 | Exponent families and norm forms reduce
- kind: negative-result
- says: For Sierpiński–Riesel families N_n = k·2^n + c the residue mod p cycles with period ord_p(2), but any fixed candidate induces one congruence class (ordinary covering; only a possible search-throughput trick across n); "N − q is a norm in K" does not certify compositeness, and any usable splitting condition is a congruence modulo disc(K)-related moduli (covering in Galois clothing).
- status: proved-in-text (argument sketches)
- uses: wp7-p1
- where: wp7_probes.md P3, P4
- matters: two more mechanism classes eliminated; shared sieve state along n is the only residue (kept as an engine-backlog note).

## wp7-p5 | Residual-bias loophole empirically bounded
- kind: negative-result
- says: Across three covers and ~1.2×10^9 scanned candidates |Ê − E| ≤ 0.1, so any unexploited compositeness structure among residual complements is worth at most ~0.1 nats per candidate (factor ≤ 1.11); pair correlations are already captured by the cover's CRT information.
- status: computed (banked campaign data; see Doubts on the ≤ 0.1 claim)
- uses: model-density
- where: wp7_probes.md P5; wp9_closure_theorem.md §7 "Empirical support"
- matters: the empirical leg of Lemma 2 and H1: no hidden luck-shaping lever.

## wp7-triple | Three conditions any real mechanism must meet
- kind: verdict
- says: A mechanism that beats covering must simultaneously (1) certify compositeness of N − q for ≫ Q^{1/2} offsets, (2) cost o(ln r) design entropy per offset at the margin, and (3) stay invisible in the banked Ê data (activate only on constructed N); no known algebraic structure does all three, against covering's ~4,400 offsets per nat at r = 3 falling to ~0.4 per nat at r ≈ 1,200.
- status: conjectural (a requirement statement; all five probes terminated at predeclared gates)
- uses: wp7-p1, wp7-p2, wp7-p3p4, wp7-p5
- where: wp7_probes.md header and last section
- matters: became the falsification filter of the WP9 engine.

# GROUP — WP8: strategy reflection, rung ladder, and the three doors

## wp8-ladder | Rung ladder E(Q) at 199 digits
- kind: empirical
- says: With the same 88-modulus budget (boost 11.01): Q = 122,000 has |U| 867, E 20.83, 1.1e9 candidates; 135,000: 1,004, 24.12, 3.0e10; 150,000: 1,138, 27.34, 7.5e11; 175,000: 1,335, 32.07, 8.5e13; 200,000: 1,569, 37.69, 2.4e16. At the fleet's 7.9e5 cand/s that is ≈ 11 h, 11 d, 3.4 y and ≈ 950 fleet-years, and geometric spacing means climbing every rung costs only ~4% more than jumping to the top.
- status: computed (wp8/*.py: greedy + coordinate ascent + kicks)
- uses: model-density
- where: wp8_beyond_covering.md §0(a)
- matters: prices every future Budget-game record.

## wp8-local-opt | Cover is a local optimum at equilibrium
- kind: empirical
- says: Coordinate ascent plus 40–60 random-restart kicks gain 0 at Q = 122,000 (c1 is a local optimum) and 33 primes (−0.79 nats) at 200,000; adding modulus r = 461 to the 88 kills ~3.5 residuals (−0.084 nats) but multiplies surviving odds by 461/460 (+0.082 nats), net +0.00, so cover size is set by the boost-vs-kills equilibrium (dE = 0), not the ln B budget (ln M = 437 of ~458 nats).
- status: computed (refined by wp9 §6 T1; see Doubts)
- uses: wp8-ladder
- where: wp8_beyond_covering.md §0(b), §0(c); wp9_closure_theorem.md §6 item 1
- matters: explains the flat frontier: leftover budget buys nothing; only rounding-gap mathematics or compute moves E.

## wp8-lp-vacuous | LP certificate vacuous; E is a rounding gap
- kind: negative-result
- says: The set-cover LP relaxation (HiGHS, 2 s) reports fractional coverage 100.00% at both Q = 122,000 and 200,000 (kill-mass Σ π(Q)/(r−1) ≈ 1.86·π(Q)), so LP duals certify nothing and the whole game exponent is an integrality gap: naive independent rounding leaves e^−1.86 ≈ 15.6% of primes uncovered, adaptive greedy 7.56% (867 of 11,474), the fractional optimum 0; each 1% (absolute) removed at 122k is ≈ 2.7 nats ≈ 15× compute.
- status: computed (HiGHS LP; wp8/lp_bound.py)
- uses: wp8-ladder
- where: wp8_beyond_covering.md §0(d); wp10_grh_remark.md §1 (positivity row)
- matters: defines Door 1 and kills SoK §7.4 as originally posed.

## wp8-door1-ensemble | Random-ensemble threshold for Door 1
- kind: empirical
- says: Random class assignments over the e^435.7 design space give |U| with mean 1,377 and σ = 21.0 at Q = 122k (2,160 and 24.1 at 200k), σ below the independence prediction (34.8, 43.6); the annealed first-moment threshold is u* ≈ 758 (Gaussian tail with the measured σ) against 867 achieved (≈ 1,448 vs 1,569 at 200k); greedy sits at z = 24.3 of 29.5 available σ, so the stated prize is ~2.6–2.9 nats (14–19×).
- status: computed (sampled σ; the 758 threshold is a Gaussian-tail extrapolation, i.e. heuristic)
- uses: wp8-lp-vacuous
- where: wp8_beyond_covering.md §6 (Door 1)
- matters: the only quantitative evidence that a basin deeper than 867 exists at all.

## wp8-three-doors | Closure argument: three doors
- kind: proposition
- says: Every attack reduces to (1) the rounding gap (mathematics), (2) the ticket rate (compute) or (3) the paradigm (mechanisms): divisor information is fully harvested by the sieve; correlation implies a common divisor (little lemma: a | N−q1 and a | N−q2 ⇒ a | q1−q2 ≤ Q); and compositeness certificates are either planted (paying WP7's ln r per offset) or extracted (factoring-equivalent), while certificate-free detection is already done by one Fermat modexp.
- status: proved-in-text (little lemma); conjectural (the planted/extracted dichotomy, called a "thesis-grade completeness theorem" to be proved in WP9)
- uses: wp7-triple, wp7-p5
- where: wp8_beyond_covering.md §6 (WP8b)
- matters: supplies the frame "three doors, one maximal bet each" that motivated the closure theorem.

## wp8-quantum | Quantum crossover is negative
- kind: negative-result
- says: Grover needs e^{E/2} coherent oracle calls, each ~|U| reversible 660-bit modexps (assumed 10^5–10^6 s per call at Gidney–Ekerå scale); quantum wins only when E > E* = 2·ln[(C_q/W_q)(W_c/C_c)], giving E* ≈ 55 (1 fault-tolerant machine), ≈ 41 (1,000 machines) and ≈ 27 (1,000 machines plus a 1000× cheaper oracle), against targets at E = 37.7 (200k) and 44.1 (sub-100).
- status: conjectural (rests on assumed oracle cost and machine counts)
- uses: wp8-ladder, wp3-regime1, ext:Grover, ext:Gidney-Ekera
- where: wp8_beyond_covering.md §1 C1
- matters: parks quantum computing until the per-call cost is about seconds.

## wp8-small-opts | Three cheap engine optimizations
- kind: algorithm
- says: O1 port --skip-frac and --sort-tests to the GPU fleet (3.0× net measured on CPU, 2–3× expected); O2 product-tree batch sieving (p̂ ×~1.5, ~1.4–1.6×); O3 replace the fixed skip fraction by the exact marginal rule (+5–15%) plus an incremental-kres cache and BATCH = 8 (~+10%); the harvest curve shows beating the incumbent without a full-cover hit is only e^0.29 ≈ 1.34× likelier than a full hit (free telemetry, not a shortcut).
- status: conjectural (O1 measured on CPU only; O2 and O3 not run)
- uses: camp3-skipfrac
- where: wp8_beyond_covering.md §0(e), §2
- matters: the cheapest ~1 nat in the programme.

## wp8-staircase | Operation Staircase to g ≥ 200,000
- kind: construction
- says: A costed ladder of certified rungs 140k (Q = 140,009, E = 24.96, ~4.75 expected hits, run by a sibling fleet session) → 150k → 165k → 175k → 200k under 10^200, with the final e^5.5 closed by 300–500 swarm GPUs for a quarter (~$100–300k spot or ~$0 volunteer), an ASIC/FPGA rack ($1–10M) or −4 nats of rounding-gap mathematics plus a 10× fleet; Door 2 at its maximum (Folding@home-scale ≈ 2.4 exaFLOPS ≈ 2×10^5 × the fleet) would give g > 200,000 in ~2 days, and 1% of it ≈ 7 months.
- status: conjectural
- uses: wp8-ladder, wp8-small-opts, wp8-door1-ensemble
- where: wp8_beyond_covering.md §1 C2–C3, §3 P1–P3, §4, §6 (Door 2)
- matters: the programme's operational plan; the board still shows no Budget-game rung above 119,419 as of 2026-11-21.

# GROUP — WP9: Divisor-Paradigm Closure Theorem (Door 3) and the Door-1 rounding-gap attack

## wp9-theorem | Divisor-Paradigm Closure Theorem
- kind: theorem
- says: For any construction scheme (candidate family F ⊂ [1,B), poly-verifiable certificate map C) with planted certificates expressible in the schema language L (Congruence, PolyImage, ExpFamily, MultiPoly, NormForm, Cyclotomic, Compose), E_eff(F,C) ≥ E*(Q,B) − o(1), where E*(122k, 10^199) = 20.83 and E*(200k, ~10^200) ≈ 37.7, conditional on H1 and H2; extracted certificates are factoring-equivalent and certificate-free detection is already at the one-Fermat-modexp floor.
- status: conjectural as stated; proved-in-text at draft rigor on the swept grammar (see wp9-verdict)
- uses: wp9-h1, wp9-h2, wp9-lemma1, wp9-lemma2, wp8-three-doors
- where: wp9/wp9_closure_theorem.md §1–§4, §14; wp9_plan.md "Door 3" (costed ≲ $1k, < 100 CPU-hours, ~6–10 part-time weeks)
- matters: turns "covering is the only mechanism" into a result, leaving Door 1 (rounding gap) and Door 2 (throughput) as the only levers.

## wp9-h1 | H1: independence of residual complements
- kind: open-problem
- says: Conditional on all divisibility data by primes < Q (cover classes and sieve data to B), the primality indicators of distinct residual complements are independent with Mertens-adjusted rates (the Hardy–Littlewood/Cramér–Granville local model for shifted primes in a progression); empirical support is |Ê − E| ≤ 0.1 over ~1.2×10^9 candidates. It is a k-tuple statement that GRH does not imply.
- status: conjectural
- uses: ext:Hardy-Littlewood, model-density, wp7-p5
- where: wp9/wp9_closure_theorem.md §2, §3 Lemma 2, §7; wp10_grh_remark.md §1 (closure-theorem row); wp12 §3 row 5
- matters: underlies the density model E and Lemma 2, hence every cost forecast.

## wp9-h2 | H2: sub-modexp compositeness detection
- kind: open-problem
- says: Does a randomized algorithm exist that, for a random B₀-rough n ∈ [X, 2X] (B₀ = (log X)^{O(1)}), decides compositeness with soundness ≥ 2/3 in time o(M(log X)·log X), i.e. cheaper than one modular exponentiation? A detector with cost c and recall r speeds the Fermat-first pipeline by 1/(c + (1−r)) (c = 0.25, r = 0.5 gives 1.33×; c = 0.1, r = 0.9 gives 5×); no lower bound is known in any realistic model.
- status: conjectural (open in both directions; note is "posting-ready", not stated as posted)
- uses: —
- where: wp9/h2_open_problem.md; wp9/wp9_closure_theorem.md §3 Lemma 3
- matters: the single identified escape from the cost floor of desert search (≥ 95% of engine time is base-2 Fermat tests of ~660-bit rough integers, ~17 tests per candidate).

## wp9-lemma1 | Lemma 1: entropy accounting for planted certificates
- kind: lemma
- says: For planted schemes the amortized design cost per certified offset is ≥ ln(1/δ_eff) − O(ln ln B), and for every family in L at least covering's marginal cost: (a) congruence classes cost ln d exactly; (b) univariate identities certify ≤ O(Q^{1/deg}) offsets at any price and confine N at (1−1/deg)·ln B; (c) multivariate identities can be window-dense (binary-quadratic products reach ~9,300 of 17,983 prime offsets at Q = 200k) but need the conjectured "balanced-representation principle" (enumerable slice density ≤ e^{−c·ln B}).
- status: proved-in-text at draft rigor for (a), (b) and the swept (c) subcases (wp9-prop9, wp9-prop10, wp9-dense); the general balanced-representation principle remains conjectural
- uses: wp7-p1, wp7-p2, wp7-p3p4, wp9-prop9, wp9-prop10, wp9-dense, ext:Cornacchia
- where: wp9/wp9_closure_theorem.md §3 Lemma 1 (status upgrades in §9–§11, §14)
- matters: the core of the theorem; covering wins on average, not at the margin.

## wp9-lemma2 | Lemma 2: shared divisors divide q1 − q2
- kind: lemma
- says: Proposition 2a (deterministic, proved by subtraction): if d > 1 divides N−q1 and N−q2 for distinct odd primes q1, q2 < Q then d | q1−q2, so all its prime factors are < Q and any coupling between complement compositeness events runs through small-prime congruence data that the cover fixes and the sieve harvests. Proposition 2b (conditional on H1): P(all residual complements composite) = ∏(1−p_q)(1+o(1)) with p_q = boost/ln N, so E_eff = design cost + Σ p_q.
- status: proved-in-text (2a); conditional on H1 (2b)
- uses: wp8-three-doors, wp9-h1, wp7-p5
- where: wp9/wp9_closure_theorem.md §3 Lemma 2, §7
- matters: rules out "luck-shaping" schemes beyond ~0.1 nats.

## wp9-tier0 | Tier-0 calibration of the falsification engine
- kind: empirical
- says: engine/tier0.py (2 s) reproduced every WP7 hand number exactly: the greedy endgame at Q = 122,000 costs 0.87–1.31 (average 1.01) nats per offset over the last six moduli; the best m² − c is c = 398 (113 offsets below 10^5) and the residual-targeted best c = 4686 kills 22 residuals = 10.5 nats each at B = 10^200 (WP7's 5.8 was at B = 10^100: 115/20); irreducible binary forms are REJECT (representation ≠ compositeness), reducible ones sieve-equivalent; an ExpFamily order condition kills one offset where a congruence mod s kills ~π(Q)/(s−1).
- status: computed
- uses: wp7-p2, wp7-p3p4, wp8-local-opt
- where: wp9/wp9_closure_theorem.md §6; wp9_plan.md "Phase status"
- matters: calibrated the referee (the 1.01-nat marginal benchmark) before the adversarial tiers.

## wp9-exhaustive | Exhaustive tier: 13,661 instances, 0 passes
- kind: negative-result
- says: Across L (400 Congruence-composite and 60 Compose as BASELINE; 12,579 PolyImage, 36 ExpFamily, 324 binary-quadratic and 4 quartic MultiPoly, 60 NormForm, 198 Cyclotomic, all REJECT) no instance passes the three-part filter; the near-miss board is ExpFamily j·2^n + c at 3.09–4.2 nats per residual kill (~3× the 1.0-nat covering endgame). 16 spurious first-run passes were a baseline-family filter leak (fixed semantically: schemas inside the covering paradigm are BASELINE), and a 60-sample Compose audit found every overlap within 3σ of additive.
- status: computed (engine/exhaustive.py, 1 s; engine/exhaustive_summary.json)
- uses: wp9-tier0, wp7-triple
- where: wp9/wp9_closure_theorem.md §8; wp9/engine/exhaustive_summary.json
- matters: first half of the theorem's empirical appendix.

## wp9-prop9 | Quartic products: cluster bound and enumeration wall
- kind: proposition
- says: For products G = A·B of positive-definite binary quadratic forms, enumeration work per certified in-window offset scales as height^θ with measured θ = 0.50, 0.59, 0.74 (theory 1/2; zero enumerable hits at height 10^10, width 10^4; ≥ 10^100 operations per offset extrapolated to 10^200), and a first-moment k-cluster count Q^{k−1}X^{−(k−2)/2} gives k = 2 in abundance but k = 3 only ≈ 10^−89 at X = 10^200, Q = 2×10^5, so a same-variable scheme certifies ≤ 2 offsets per candidate against ~18,000 needed; disjoint-variable products reduce to congruence certificates, and any d₁ > Q costs ln d₁ > ln Q ≈ 11.7 nats.
- status: proved-in-text (draft rigor, first moment, "unconditionally on average") + computed (θ measurements)
- uses: wp9-lemma1
- where: wp9/wp9_closure_theorem.md §8 (end), §9 (Prop 9.1–9.3)
- matters: Lemma 1(c) closed for this subfamily by existence, with no hardness hypothesis.

## wp9-prop10 | Cluster ceiling closes every v < d family
- kind: proposition
- says: For factors of degrees d1, d2 ≥ 2 in v shared variables (d = d1 + d2, value-set exponent α = min(1, v/d); measured α̂ = 0.761 vs 0.750 predicted for (2,2,3)), clusters of G-values in width-Q windows exist only up to k_max = 1 + ⌊α·lnX / ((1−α)·lnX − lnQ)⌋ (finite iff α < 1 − lnQ/lnX = 0.9735 at X = 10^200, Q = 2×10^5): (2,2,2) gives 2, (2,2,3) gives 4, (2,3,4) gives 5, α = 0.9 gives 13, so every v < d family certifies ≤ 13 offsets against ~18,000 needed.
- status: proved-in-text (first moment, modulo standard equidistribution of form values)
- uses: wp9-prop9, wp9-lemma1
- where: wp9/wp9_closure_theorem.md §10 (Prop 10.1)
- matters: closes the whole v < d quadrant, including every combination expressible in the grammar (v ≤ 3).

## wp9-dense | Dense frontier closed by isolation and orbits
- kind: proposition
- says: For window-dense families (v ≥ d): local isolation (Prop 11.1), at X = 10^200, Q = 2×10^5, d = 4 the ellipsoid extents are ~10^−145 and 10^−47 (< 1/2), so window solutions are pairwise isolated; orbit accounting (Prop 11.2), Aut(G) conserves the value, Aut(A) conserves the factor (a planted divisor: sieve-equivalent if enumerable, otherwise a relative-width-10^−195 sliver) and mixed words hit the window with expected ~10^−190; the remaining access is prescribed-value solving, which is factoring, and directed enumeration costs ~X^{(d−1)/d}/W trials (10^145 at d = 4).
- status: proved-in-text at draft rigor ("[P-shaped]"; Taylor-regime uniformity and non-abelian word combinatorics are left to write up)
- uses: wp9-prop10, wp9-prop9
- where: wp9/wp9_closure_theorem.md §10 (Prop 10.2), §11
- matters: dissolved the last open item of Lemma 1 (classifying torus actions as norm structure) without new mathematics.

## wp9-gen-referee | Generative tier broke the referee first
- kind: empirical
- says: In AlphaEvolve experiment 15926813306184238842 (engine goldbach_1784979910032, client-evaluated loop in which candidates emit only schema JSON, graded by scorer.py in a fresh interpreter) reported fitness rose 0.2725 → 0.3351 → 0.4597 by exploiting a scorer hole: per-offset costs were billed only against the 867 residuals, crediting 10,416 offsets costing 22,900 nats against a 460-nat budget (50× overdraft); after the fix the same points score 0.0323 and 0.0465, and the bar becomes cost per offset < ln B/CEIL = 0.44 nats (CEIL = 3√Q ≈ 1048), against covering's average 0.041 nats per offset (437 nats / 10,607 offsets).
- status: computed
- uses: wp9-exhaustive, wp9-tier0, ext:AlphaEvolve
- where: wp9/wp9_closure_theorem.md §12; wp9/engine/harness.md; wp9/engine/alphaevolve_access.md; wp9_plan.md "Door 3 phase 4"
- matters: shows the anti-reward-hack protocol works (the adversary attacked the referee first) and sharpens covering's moat to an average-cost statement.

## wp9-expfamily | ExpFamily closed: supply-limited
- kind: proposition
- says: For j·a^n + c certificates the single-modulus floor is ln 5 = 1.609 (a = 7, s = 2801; the scorer's sampled 2.197 = ln 9 was ~1.4× pessimistic) and cost = ln d > ln(log_a s), but each s supplies only ~π(Q)·d/s offsets (s = 2801, d = 5: ~20), so the cheapest-first purchase of 1048 offsets costs 1,151 nats for every base a ∈ {2,3,5,7}, 2.5× the ln B = 460 budget, and no budget-feasible design certifies more than 419 offsets (vs ~18,000 from a real cover).
- status: computed (exact non-sampled purchase problem over all primes s < 10^5)
- uses: wp9-gen-referee, wp7-p3p4
- where: wp9/wp9_closure_theorem.md §13b
- matters: quantitative closure of the strongest non-covering family.

## wp9-ceilings | PolyImage, Cyclotomic, Compose closed by ceilings
- kind: proposition
- says: Any degree ≥ 2 univariate family certifies at most Q^{1/d} offsets at any price (Q = 122,000: 349, 50, 19, 7 for d = 2, 3, 4, 6), below CEIL = 1048, and Cyclotomic is covered since φ(n) ≥ 2 for n ≥ 3; depth-2 Compose is empty at scale because N = m² − c1 = m'² − c2 forces (m−m')(m+m') = c1 − c2, so m ≤ |c1 − c2|, while 10^200 needs m ~ 10^100 (c = 398 and 4686 give 5 solutions, largest m = 1073).
- status: proved-in-text (price-free ceiling) + computed (small-case solution counts)
- uses: wp7-p2, wp9-lemma1
- where: wp9/wp9_closure_theorem.md §13c
- matters: retires two families outright and explains why composition is only additive.

## wp9-verdict | Verdict: closure theorem stands on the grammar
- kind: verdict
- says: 13,661 hand-enumerated schema instances plus 41 LLM-evolved candidates (4 families) gave zero passes; the best budget-aware fitness is 0.0919, an ExpFamily point (a = 3, j = 2, c = 3) certifying 209 affordable offsets at 2.197 nats each against > 1048 at < 0.44 required (53× too expensive). Every family has a closure of its own kind; what stays conjectural is H1, H2, the o(1) terms, the value-equidistribution inputs and out-of-grammar mechanisms.
- status: proved-in-text at draft rigor on L; conjectural at the edges
- uses: wp9-theorem, wp9-exhaustive, wp9-gen-referee, wp9-expfamily, wp9-ceilings, wp9-prop9, wp9-prop10, wp9-dense, wp9-h1, wp9-h2
- where: wp9/wp9_closure_theorem.md §14; wp9_plan.md "Phase status final"
- matters: Door 3 is complete at draft level, so record progress is governed by Door 1 and Door 2.

# GROUP — WP9 / Door 1: the rounding-gap attack on the 88-modulus cover (wp9/door1)

## d1-lns | Door 1: exact windows cannot beat 867
- kind: negative-result
- says: On the Q = 122,000 instance (88 moduli, 11,474-prime universe, baseline |U| = 867, 1 prime = 0.0240 nats): 19 of 88 moduli are tight (gap ≤ 1), random-start ascents land at 954–981 (90–110 worse), backbone overlap between independent solutions is 2.4% (chance); 41 exact CP-SAT windows (sizes 7–15, caps 25–300 s) never beat 867, 21 of 22 LP-computed windows are certified window-optimal, and a 968 solution is also window-optimal (0 of its 101-prime gap recovered).
- status: computed (CP-SAT plus per-window LP certificates; certified window by window only)
- uses: wp8-lp-vacuous, wp8-door1-ensemble, ext:CP-SAT
- where: wp9/door1/d10_diagnostics.md; wp9/door1/d11_gate_verdict.md; wp9/door1/instance_q122k.json
- matters: the landscape is a field of mutually distant, locally exact basins, so local exactness is exhausted.

## d1-bp | Door 1: BP/SP decimation lands at 874
- kind: negative-result
- says: Sequential sum-product BP tracks exact E[U] to 0.7% (soft regime) and decimation finds the toy instance's exact optimum (54), but on the real instance it reaches 874 (β = 1.5), 887 (β = 2.5) and 922 (β = 3.5), at best 7 primes above greedy; LNS polish of 874 stays at 874 (a third locally exact basin: 867/874/968); naive Bethe/RS slides to the fractional fantasy (35 at β = 4), so a real threshold needs 1RSB/SP.
- status: computed
- uses: d1-lns
- where: wp9/door1/d11_gate_verdict.md (D1.2 addendum)
- matters: an independent global construction that gets close but not below greedy.

## d1-endgame | Door 1: exact half-cover block, no gain
- kind: negative-result
- says: Solving the 30 largest moduli (281–683) together, then the 44 largest (199–683), i.e. half the cover, as one exact subproblem leaves |U| = 867; neither run closed an optimality proof within its cap (160 s and 260 s), so this is "no improvement found", not a certificate.
- status: computed (no optimality proof)
- uses: d1-lns
- where: wp9/door1/d11_gate_verdict.md (D1.3 addendum)
- matters: tests, and does not confirm, the claim that greedy's myopia lives in the endgame.

## d1-verdict | Door 1 verdict: 867 near optimum
- kind: verdict
- says: After 41 exact windows, BP decimation (874) and exact half-cover blocks, greedy's 867 at Q = 122,000 is judged at or very near the quenched optimum for this moduli set, the annealed 758 probably being an annealed–quenched (clustering) gap, so the Door-1 prize is revised from ~2.6 nats to 0–2.6 nats; untried are a banded/matching ensemble (D1.3), basin-hopping tempering with ≥ 10-class moves and 1RSB/SP. Plan thresholds: −1 nat worthwhile, −2.5 nats (≈ annealed threshold, 12×) expected win, −4 nats breakthrough.
- status: conjectural (supported by computed negative evidence; no global certificate)
- uses: d1-lns, d1-bp, d1-endgame, wp8-door1-ensemble
- where: wp9/door1/d11_gate_verdict.md; wp9_plan.md "Door 1"; RESEARCH_LOG.md 2026-07-29
- matters: decides whether Door 1 can still move any record.

# GROUP — WP10: would a proof of RH/GRH move the frontier?

## wp10-verdict | A proof of RH/GRH would move no lever
- kind: verdict
- says: Assuming the claim in alpo.ge/remark.pdf is true (its Lean archive was not checked), RH/GRH are √x-quality statements while every bottleneck is x^{o(1)}: the RH prime window (22/25)√x ln x is 10^77.4 against a desert of g = 10^5.0 (short by 10^72.4 at 150 digits), GRH on the scanned progression is 10^65.6 short (informative only for N of about 280 digits, T ≥ 10^142.7), and the shortfall is 10^97.1 (RH) / 10^95.9 (GRH) at the 200-digit record and 10^1343 at the 2,692-digit megagap. H1 and H2 are untouched, and Miller-under-GRH is not competitive (1.4 s at 150 digits, 5.8 core-days at 2,480 digits vs ~2 h ECPP, 44 core-days at 4,000, no certificate).
- status: computed (wp10/grh_reach.py, 6 s; approximations all made in GRH's favour)
- uses: wp9-h1, wp9-h2, ext:GRH, ext:CMS19, ext:Bach90
- where: wp10_grh_remark.md §0–§1, §3
- matters: closes "does GRH help": records move only through Doors 1 and 2; the one transferable idea is proof-carrying records (see wp12-lean).

## wp10-sieve-positivity | GRH sieve and positivity floors vacuous
- kind: negative-result
- says: At record scale the Door-1 floor from the linear sieve is vacuous (cover moduli 613 > 316 = √Q at Q = 10^5 and 683 > 349 at Q = 122,000, s = 0.90, f(s) = 0, floor −0.46·π(Q) / −0.50·π(Q)); Bombieri–Vinogradov already gives GRH's level for sieve sums and only level D = Q (beyond Elliott–Halberstam) turns positive, certifying 282 / 142 residuals against 827 / 867 achieved. The positivity hierarchy is not runnable: kill mass Σ1/(r−1) = 1.856 > 1, Bonferroni truncations 1.856 (depth 1), 1.088 (depth 3), 0.891 (depth 5) against exact 0.880, a level-5 lift has e₅ ≈ 10^19.2 monomials and the level-2 Lasserre matrix has side 10^8.2.
- status: computed (wp10/grh_reach.py sections B–D)
- uses: wp8-lp-vacuous, ext:Bombieri-Vinogradov, ext:Elliott-Halberstam, ext:linear-sieve
- where: wp10_grh_remark.md §1 (table rows on Door 1 floors)
- matters: no sieve or positivity certificate can bound the rounding gap, so Door 1 stays an open optimization problem.

## wp10-erratum | Corrected: GRH's gain on paper constants
- kind: retraction
- says: WP10's row "Paper theorems: constants only" said GRH turns Linnik's step L ≤ 5 into 2 + o(1) (a factor 2.5); the erratum says the paper's moduli are smooth (primorial-type), for which the unconditional exponent is already 12/5 (Chang 2014, Cor. 11; a literature citation not re-checked), so GRH's gain is ×1.2, and the paper's Theorem 14 (FGKMT transfer) is superseded in rate, not merely in constant, by Shi's counting bound (arXiv:2605.21529v6, Thm 6.22) and by wp12-thm1.
- status: retracted (original row replaced by the erratum box)
- uses: wp12-thm1, ext:Chang14, ext:Linnik, ext:Shi-2605.21529
- where: wp10_grh_remark.md §1 erratum box; merge_2026-11-21.md erratum 3; crossreview_8ffe9d7a.md §5 item 2
- matters: stops GRH being over-credited on the paper's theorems.

# GROUP — WP11: Game 1 without ECPP (the 8ffe9d7a session's memo)

## wp11-bls | N−1 (BLS) certificate built by CRT
- kind: construction
- says: Because every cover modulus is odd, N ≡ g + 1 + 2^n (mod 2^(n+1)) is free by CRT, so 2^n exactly divides P − 1 for P = N − g; with F = 2^n and F³ > P, Pocklington gives every prime factor ≡ 1 (mod F), a composite P would be (uF+1)(vF+1) with base-F digits (uv, u+v, 1), and "c₁² − 4c₂ is not a square" therefore proves P prime from one modexp. With full covers (no residuals) g(N) = g is certified by congruences plus one modexp, with no ECPP, no PRP assumption and no GRH, at the price of ≈ 1.5× the digits.
- status: proved-in-text (re-derived in WP11 §1; found independently in WP12 §1)
- uses: ext:BLS75, ext:Pocklington, ext:Proth
- where: wp11_bls_game1.md §0–§1; wp12_prime_covering_grh_ledger.md §1
- matters: removes Game 1's certification wall (the ECPP-bound ceiling had been forecast at ≈ 2.5M).

## wp11-validation | BLS pipeline validated against the paper
- kind: empirical
- says: bls/full_cover.py reproduced the paper's table exactly (Q = 10^5: 356 congruences, r_max 2,393, 1,020 digits; Q = 10^6: 1,762 / 15,083 / 6,480; Q = 10^7: 9,853 / 102,983 / 44,599 vs 44,600); a stdlib verifier rejected 6/6 tampered records (one bug found: Python's 4,300-digit int-to-string cap); the Q = 10^5 shakedown gave a 1,536-digit N with g = 100,069 after 122 tests (123 predicted); density probes found 54 primes vs 48.7 expected (6,000 tests, z = +0.76) at Q = 10^5 and 8 vs 9.3 (2,400 tests, z = −0.43) at 3·10^5.
- status: computed (the search code was retired at the merge; provenance recorded at commits 4adaa4d and 6c66bcd)
- uses: wp11-bls, model-density
- where: wp11_bls_game1.md §2–§3; merge_2026-11-21.md "Provenance of numbers produced by retired code"
- matters: validated the construction, the verifier and the cost model before any record was claimed.

## wp11-ladder | Game-1 cost ladder (GMP)
- kind: empirical
- says: One test is a modexp fitting 7.64·10^−9·d^2.21 s (four points, 11.5k–67k digits) with ln P/(e^γ ln S) expected tests: Q = 1.2·10^6 needs 762 tests (0.06 core-days), 2·10^6 needs 1,170 (0.23), 5·10^6 needs 2,085 (2.2 core-days, 13 h on 4 cores), 10^7 needs 3,757 (14.6 core-days, 3.6 d), 16,045,849 needs 5,628 tests at 100,233 digits (53 core-days, 13 d), 10^8 needs 27,578 (8,666 core-days); GWNUM-class code is ~5–10× faster, and the ladder is ~30% pessimistic next to the lazy cover.
- status: computed (bls/ladder.py, retired; at commit 6c66bcd, on fixed-order covers)
- uses: wp11-bls, model-density, wp12-lazy-cover
- where: wp11_bls_game1.md §4
- matters: shows 10^7 reachable in days and the "absolute gap" rung within reach.

# GROUP — WP12: prime-covering function, GRH ledger, N−1 construction (the 2ce9e63a session's memo)

## wp12-fullcover | Full covers are the optimal Game-1 design
- kind: verdict
- says: With certification free (P = m·2^n + 1, cover congruences moved onto m by CRT because 2^n is a unit mod odd r, no cover freedom spent), a no-residual cover needs only ~ln P/(e^γ ln B) PRP tests instead of an e^E lottery: at g ≈ 1.2·10^6 it is ~4× cheaper than a megagap-style partial cover with a BLS-form complement (the log says 4–8×), leaving 200–500 residuals to luck would save < 10%, and REGISTRY row A2 ("dominated") flips. N is ≈ 1.5× the full-cover modulus (itself ~2.5–2.8× a partial-cover modulus), which is irrelevant in the height game.
- status: computed (timings) + proved-in-text (the construction, via wp11-bls)
- uses: wp11-bls, wp12-lazy-cover
- where: wp12_prime_covering_grh_ledger.md §1; RESEARCH_LOG.md WP12 entry
- matters: makes the Game-1 ladder PRP-bound rather than ECPP-bound.

## wp12-thm1 | Theorem 1: C(x) ≥ 1.349·x·ln x
- kind: theorem
- says: C(x), the largest Q such that classes a_r for the odd primes r ≤ x cover every odd prime < Q, satisfies C(x) ≥ (e^γ/(2C₂) − o(1))·x·ln x = 1.3490·x·ln x (C₂ = twin-prime constant), by pigeonhole (t ← t(1−1/(r−1)) + 1/(r−1)), Mertens and one survivor per prime in (x/ln x, x]; so explicit even N have no Goldbach summand below (1.349 − o(1))·ln N·ln ln N, beating the paper's Theorem 14 by ln₃N/ln₄N and Shi's ½ (under Shi's convention p(n) = ∞). Genuine Goldbach numbers get constants 0.270 (Linnik L = 5), 0.378 (Pintz exceptional set X^0.72, no explicit partition), 0.562 (Chang 12/5, smooth moduli), 0.674 (GRH, L = 2), 1.349 (Goldbach itself); greedy data track 0.72·x·ln²x (0.690–0.729 for x = 2,393 … 755,137).
- status: proved-in-text (re-derived by the other session); the Linnik-type constants are [L], not re-checked
- uses: ext:Mertens, ext:Shi-2605.21529, ext:FGKMT, ext:Linnik, ext:Chang14, ext:LLS15, ext:Pintz
- where: wp12_prime_covering_grh_ledger.md §2 (Theorem 1, Goldbach-numbers table, greedy table) and Appendix (paper.tex patch, not applied); crossreview_2ce9e63a.md §4.1
- matters: first elementary bound above the counting constant; the data show one more logarithm is true for greedy covers.

## wp12-thm2 | Theorem 2: C(x) ≤ x^{4+ε} ceiling
- kind: theorem
- says: For every ε > 0 and x ≥ x₀(ε), C(x) ≤ x^{4+ε} (x^{2+ε} under Elliott–Halberstam): the linear sieve at level Q^{1/2−ε} with Bombieri–Vinogradov (uniform in the class) leaves ≥ c_ε·π(Q)/ln Q primes uncovered when all moduli are ≤ Q^{1/4−ε}, so certified deserts satisfy (1.349−o(1))·ln N·ln ln N ≤ g ≤ (ln N)^{4+ε}. Caveat added after cross-review: the bound is asymptotic and vacuous at record parameters (moduli 613–79,139 vs Q ≤ 2·10^6), and GRH adds nothing.
- status: proved-in-text (re-derived by the other session)
- uses: ext:Bombieri-Vinogradov, ext:linear-sieve, ext:Elliott-Halberstam, wp10-sieve-positivity
- where: wp12_prime_covering_grh_ledger.md §2 (Theorem 2 and caveat); crossreview_8ffe9d7a.md §5 item 3
- matters: the first unconditional impossibility statement for covering certificates.

## wp12-grh-ledger | GRH ledger: constants, not walls
- kind: verdict
- says: Row by row: the cover realisation constant moves 0.56 → 0.67 (ln N ≤ 2.4·ln M → 2·ln M + 2 ln ln M); the guaranteed N−1-certifiable realisation exponent moves N < M_c^{12+o(1)} → M_c^{6+o(1)} (practice 1.5); Miller-under-GRH costs ≈ 12 core-years at 11,263 digits (π(2 ln²P) ≈ 6.7·10^7 strong tests; WP10 gives 5.8 core-days at 2,480 digits) against one 5.7 s BLS modexp; Theorem 2, the density model (GRH gives π(X;M,a) only for M < X^{1/2−ε}, the records live at M ≈ X^{0.95}), Goldbach's existence and the T/R games are unchanged.
- status: proved-in-text (accounting) with literature inputs [L]
- uses: wp12-thm1, wp12-thm2, wp10-verdict, wp11-bls, wp9-h1, ext:GRH, ext:LLS15, ext:Bach90
- where: wp12_prime_covering_grh_ledger.md §3; wp10_grh_remark.md §1 (Game-1 certification row)
- matters: complementary to wp10-verdict; the one wall that moved (Game 1) moved by changing the shape of the number, not by GRH.

## wp12-lazy-cover | Lazy weighted greedy covers ~10% shorter
- kind: algorithm
- says: A weighted lazy greedy over a 3× prime pool is ~9–10% shorter than the paper's fixed-order greedy (6,787 vs 7,503 digits at Q = 1.2·10^6; in the old cover the last 300 targets cost 138 one-kill moduli), worth ~30–35% of compute per 10% of digits; a price-reweighted variant was worse; Konyagin–Pomerance (F ≥ P^{3/10}) or Coppersmith–Howgrave-Graham (F ≥ P^{1/4+ε}) certificates could shrink N a further 5–11% (16–32% compute); the leftover sparse tail is a Door-1-style rainbow-matching problem.
- status: computed (proth/desert.py; its covers are verified inside the records)
- uses: wp12-fullcover
- where: wp12_prime_covering_grh_ledger.md §5 items 2 and 4; RESEARCH_LOG.md WP12 entry
- matters: the cheapest lever on the Game-1 ladder.

## wp12-probe | The 1.2M long waits were one event
- kind: empirical
- says: The two sessions' Q = 1.2·10^6 searches (3,472 tests vs 762 expected, p = 0.011; 2,647 vs ~703, p = 0.024) ran over one arithmetic progression (1,341 integers tested by both, 4,778 distinct) with jointly 2 primes where 6.42 were expected, P(≤ 2) = 0.046; an out-of-sample probe of the 3,245 untested sieve survivors with t ≤ 16,383 found 6 primes vs 4.62 expected (z = +0.64), the whole range 8 vs 11.0 (P(≤ 8) = 0.23), the pooled tally 118 vs 119.3, and eight N with g = 1,200,109 are now known.
- status: computed (proth/overlap_check.py, proth/probe.py, probe_1200k_result.json)
- uses: model-density, rec-g1-ladder
- where: wp12_prime_covering_grh_ledger.md §6; crossreview_8ffe9d7a.md §3; merge_2026-11-21.md "The open item both reviews raised"
- matters: removes the one observation that threatened the ladder's cost model.

## wp12-open-fx | Open: C(x) growing faster than x·ln x
- kind: open-problem
- says: Proving any f(x) → ∞ with C(x) ≥ f(x)·x·ln x, one logarithm below the greedy data 0.72·x·ln²x, is named the natural next theorem; it needs the large primes to capture several survivors each (the FGKMT hypergraph-covering step for prime tuples in progressions of large prime difference); whether g exceeds the true maximal prime gap is untouched.
- status: conjectural (open)
- uses: wp12-thm1, ext:FGKMT
- where: wp12_prime_covering_grh_ledger.md §2 (end), §5 item 3
- matters: a paper-level result that shares its technology with the rounding-gap programme (wp8 P2).

## wp12-lean | Lean-checked record: planned, not done
- kind: open-problem
- says: The statement IsLeast {p | p.Prime ∧ (N − p).Prime} g for a Game-1 record needs only (a) the BLS/Pocklington N−1 criterion (a page of orderOf reasoning in Mathlib), (b) a decidable check that every prime q < g lies in a cover class and N in every class, and (c) one modexp plus an integer-square-root comparison, a few hundred lines; WP10 §2 independently proposes "proof-carrying records" (compositeness side elementary, primality side via CoqPrime-type ECPP checking). The Lean toolchain install was refused, so nothing is Lean-checked.
- status: conjectural (not done)
- uses: wp11-bls, ext:Lean-Mathlib, ext:CoqPrime
- where: wp12_prime_covering_grh_ledger.md §4; wp10_grh_remark.md §2; RESEARCH_LOG.md WP12 entry ("Not done")
- matters: would make these the first machine-proof-carrying records of their genre.

# GROUP — Others (a): records, campaigns and engineering

## rec-board | Record board of 2026-11-21
- kind: empirical
- says: Game 1 (Height) incumbent g = 10,000,141 at a 61,329-digit N; Game 2 (Threshold T(100,000)) a 150-digit N with g = 104,527; Game 3 (Budget R(10^199)/R(10^200)) a 199-digit N with g = 119,419. The log records each Game-1 entry as passing independent verifier legs (proth/verify.py, PARI, and for the newer ones the bls/ verifiers), and Games 2 and 3 as re-verified in this repo.
- status: computed (independent verifier legs; Game 2 re-verified 2026-07-28 with witnesses plus independent ECPP; Game 3 "re-verified PASS here", undated)
- uses: rec-g1-ladder, rec-t100k, rec-audit, xr-verification
- where: RESEARCH_LOG.md "Record board (updated 2026-11-21)"
- matters: fixes the three incumbents against which every campaign, ladder and cost forecast is measured.

## rec-g1-ladder | Height-game ladder 1.2M to 10M
- kind: empirical
- says: Four certified Game-1 results, all complete cover + BLS N−1 proof: g = 1,200,109 at 11,263 digits (certified twice for two different N: 3,472 tests vs 762 expected, and 2,647 vs ~703), g = 2,000,269 at 15,595 digits (lazy cover; 648 tests vs ~970 expected, 37 min on 4 cores), g = 5,000,251 at 33,938 digits (3,080th survivor vs ~2,118 expected, p ≈ 0.23; 68 CPU + 3,072 GPU tests) and g = 10,000,141 at 61,329 digits (2,718th survivor vs ~3,130, p ≈ 0.42; 9,095 cover classes, all 664,584 primes below g). The previous incumbent was g = 1,157,341 at 2,480 digits (ECPP).
- status: computed (verify.py + PARI + bls verifiers; CPU BLS re-proof 306 s for the 10M record)
- uses: wp11-bls, wp12-fullcover, wp12-lazy-cover, eng-gpu-sieve, xr-verification, model-density
- where: RESEARCH_LOG.md board and "Campaign G" entry; wp11 §3; wp12 §1; merge_2026-11-21.md
- matters: shows certification is no longer the Game-1 wall.

## rec-16m-rung | Open: desert longer than any prime gap
- kind: open-problem
- says: The target g > 16,045,848 (longer than the largest known prime gap, PRP endpoints) needs ~5,628 tests at 100,233 digits (WP11) or ~5,700 at 91,753 digits (WP12 lazy cover), i.e. 53 core-days / 13 days on a 4-core box; a Colab fleet (four 8-vCPU runtimes at ~29 tests/h each, with gold-cpu and the A100 host joining, the A100 at ~570 tests/h) works on it with the sieve taken to 3·10^11 (survivor list 15,215 → 14,579). No result is logged as of 2026-11-21.
- status: conjectural (in progress)
- uses: wp11-ladder, wp12-fullcover, eng-gpu-sieve
- where: RESEARCH_LOG.md "Campaign G" (CPU fleet for 16M; 16M sieve to 3·10^11); wp11 §4; wp12 §1
- matters: the next headline Game-1 milestone.

## rec-t100k | Threshold-game records 186 to 150 digits
- kind: empirical
- says: T(100,000) went from 186 digits (g = 109,357) to 179 digits (g = 101,149; Q = 99,991 cover, 80 classes, M = 169.4 digits, |U| = 728, boost 10.79; one progression scanned to t = 758,850,385, hit after surviving λ ≈ 2.5, P ≈ 8%) to 150 digits (g = 104,527; 68-modulus cover, M = 140 digits, hit at k = 62,147,038,260 of a [0, 7.5e10) scan, E = 24.91, 63.8% depth, cumulative expectation ≈ 0.40). The 150-digit jump came from a CUDA engine at 2.5–8.5M tests/s ≈ 430× the 4-core pipeline: ln 430 ≈ 6.1 matches the E-gap (24.9 vs ~19).
- status: computed (179 d: verifier PASS; 150 d: verify_record.py re-derives all 9,977 witnesses and the 17-step ECPP chain passes the PARI-independent checker)
- uses: model-density, camp3-skipfrac, cover-tools-audit
- where: RESEARCH_LOG.md 2026-07-25 (master merge), 2026-07-28 ("post-mortem: evaluation of the winning 179d record" and "evaluation of the 150-digit GPU record")
- matters: records track log(compute): throughput, not new mathematics, produced the jump, which is the ratchet-versus-grand-slam lesson.

## rec-audit | Kickoff incumbents audited: PASS
- kind: verdict
- says: The WP1 audit (O1) passed both kickoff records: the dual 197-digit N (g = 107,719; rebuilt byte-identical from (N0, M, k = 951,928); all 10,250 witnesses re-derived identically; 26-step ECPP chain valid) and the 2,692-digit megagap (g = 1,134,871 per the log's "superseded" note; 813 cover congruences; all 88,239 prime offsets below g re-proven non-summands; ECPP chains of 253, 267 and 246 steps); three deliberate corruptions were detected, and PARI primecertisvalid = 1 for all four certificates.
- status: computed (delegated audit scripts; dual-implementation ECPP validation)
- uses: —
- where: RESEARCH_LOG.md 2026-07-22 "WP1 interim" and "WP1 final verdict"; "Programme close-out summary"
- matters: later work builds on records whose verification stack was itself attacked and found sound.

## model-density | Density model E = |U|·boost/ln N
- kind: empirical
- says: Expected candidates to a hit is e^E with E = |U|·boost/ln N (boost = 2·Π_cover r/(r−1)); measured Ê agreed to ~0.1 nats across three covers and ~1.2×10^9 scanned progression elements (calibration Ê = 18.79 ± 0.05 vs 18.82–18.88 modelled, ratio 0.995; ~17.0 Fermat tests per k; per-slice p̂ 0.0588–0.0592 in campaign 1). The log reads every campaign miss as an ordinary Poisson draw, not model error.
- status: computed (campaign logs; E8 calibration)
- uses: camp-cover-frontier, camp12-null, camp3-skipfrac, ext:Hardy-Littlewood
- where: RESEARCH_LOG.md "Programme close-out summary" O2 and 2026-07-22 WP2/WP6; campaign/CAMPAIGN_PLAN.md §4; wp7_probes.md P5; wp9 §7
- matters: every price in the programme (ladder, sub-100, Game-1 costs) and the empirical support for H1 rest on it (see Doubts on the ≤ 0.1 claim).

## camp-cover-frontier | Cover frontier at Q = 107,720
- kind: empirical
- says: cover.py at Q = 107,720 gives (e_target 17.0/17.5/18.0/18.5) 92/91/89/88 congruences, M = 202.6/198.4/194.3/190.6 digits and |U| = 746/750/764/770; the chosen base spec phd_q107720_e185 has 88 congruences (moduli 3–643), M = 190.61 digits, |U| = 770, boost 10.99, E = 18.50, 200 variants and kmax 1.5e6 so every hit beats both R(10^199) and N₁₉₇; annealing (2 seeds, 60–80k iterations) gave zero improvement over greedy plus coordinate descent. Forecast: e^18.71 = 1.33e8 elements, ~17.5 h at 2,118 k/s, P(hit ≤ 24 h) ≈ 0.75.
- status: computed (cover.py, anneal.py, search.py calibration on 4 processes)
- uses: model-density
- where: campaign/CAMPAIGN_PLAN.md §1–§5; RESEARCH_LOG.md 2026-07-22 "WP2/WP6 results"
- matters: first map of the E-versus-digits trade, and evidence that greedy is a robust local optimum of log M + E.

## camp12-null | Campaigns 1 and 2 found nothing
- kind: negative-result
- says: Campaign 1 (Q = 107,720, 200 variants) exhausted its original 1,200-slice budget (3.15e8 elements, 0 hits, P(no hit) ≈ 0.11) and was retired at 1,213/2,400 slices (3.18e8 elements) when master records made it obsolete; Campaign 2 (168-digit blueprint, Q = 100,003, 79 congruences, M = 167.9 d, 754 residuals) was stopped at 2,132/2,400 slices (5.6e8 elements) with 0 hits and survival ≈ 0.22, though every attainable hit was ≤ 175 digits ("stopped, not falsified"). Per-slice p̂ and alive/k matched the model throughout.
- status: computed (search.log checkpoints; campaign2/search.log has 2,132 lines and found.jsonl is empty)
- uses: model-density, camp-cover-frontier, cover-tools-audit, ops-chunked
- where: RESEARCH_LOG.md 2026-07-25 ("original budget EXHAUSTED"; "CAMPAIGN 1 RETIRED, CAMPAIGN 2 LAUNCHED"), 2026-07-28 ("CAMPAIGN 2 STOPPED")
- matters: two honest negatives kept as model validation, plus the depth-versus-breadth lesson (one deep progression has unbounded runway).

## camp3-skipfrac | Selective testing (--skip-frac): about 3× faster
- kind: algorithm
- says: search.py --skip-frac f tests only the emptiest (1−f) of each block in survivor-count order and computes the sacrificed hit mass exactly from the survivor histogram; at 199 digits f = 0.92 with sieve-B = 1e6 gave 14,957 raw k/s keeping 29.6% of hit mass, ~3× net over the 1,772 k/s baseline (hit% matched the Gaussian histogram model within ±0.4 pp). Campaign 3 (cover c1: Q = 122,000, 88 classes, M = 191 d, |U| = 867, boost 11.01; 40 variants; any hit gives g ≥ 122,011 > 119,419) was stopped as duplicative at 380/17,200 slices (3.98e8 raw candidates, hit-mass λ = 0.077, survival 0.926).
- status: computed (measured; campaign3/search.log has 380 lines)
- uses: model-density, camp-cover-frontier
- where: RESEARCH_LOG.md 2026-07-28 "CAMPAIGN 3 LAUNCH", 2026-07-29 "CAMPAIGN 3 STOPPED"
- matters: the cheapest measured speed-up and the template for the fleet port (wp8-small-opts O1).

## cover-tools-audit | AlphaEvolve covers and PR #20 audited
- kind: verdict
- says: Evolved cover optimizers are not competitive under warm start: constrained_100 gives D = 193.2 at E ≤ 17.5 and D = 179.6 at E ≤ 20 (vs blueprint 176.5 and greedy-proposal anneal 175.6), unconstrained −D fitness collapses to infeasible covers (D = 50.7 at E = 111), and with an E ≤ 20 penalty the evolved move-set gains only 0.9 digits (176.5 → 175.6). PR #20's 168-digit blueprint (Q = 100,003, 79 congruences, M = 167.9 d, 754 residuals) is a valid cover but its claims were inflated: honest E = 19.84 (not 20.85), expected N ≈ 176.5 digits (not 168), and its 1,111 variants with ceiling_digits = 170 gave only ~120 candidates each (~1.3e5 of ~4e8 needed).
- status: computed
- uses: camp-cover-frontier
- where: RESEARCH_LOG.md 2026-07-25 ("AlphaEvolve cover-optimizer analysis"; PR #20 audit), 2026-07-26 (constrained_100 benchmark; deep-dive part 2)
- matters: confirms greedy plus anneal sits at its local frontier and that outside covers need re-audit before use.

## eng-gpu-sieve | GPU Fermat engine and deep sieve
- kind: algorithm
- says: proth/gpu_screen.py is a CuPy batched Montgomery engine (15-bit limbs in float64, cuFFT): v1 failed validation on structured operands (Mont(1) = R mod P has long 0x7FFF limb runs) until an exact carry-lookahead kernel, v2 merges an inverse FFT (1.11×), v3 drops copies (1.12×, bit-for-bit equal); an A100 test costs 0.85 s at 33,938 digits and 2.35 s at 61,329 digits. deepsieve.c takes survivors from 10^9 to 10^11 (toward 10^12), cutting expected tests ~18% (10^7 rung) and ~25% (16M rung); each version was validated against gmpy2 and known primes and every GPU pass is re-proved on CPU.
- status: computed
- uses: wp11-bls, model-density
- where: RESEARCH_LOG.md "Campaign G" (Engine; Deeper sieve)
- matters: enabled g = 5,000,251 and g = 10,000,141 within one evening.

## ops-chunked | Restart-safe chunked compute methodology
- kind: empirical
- says: Idle reclaim of the container kills detached and harness-tracked background tasks (measured duty ~12%); slice checkpoints committed in search.log (262,144 k per slice, ~2 min), idempotent resume and timeboxed foreground chunks (~9.7 min, later ≤ 560–590 s, exit code 3 on a hit) reached ~85% duty across ~15 restarts/rollbacks and survived a 28-hour suspension (2026-07-22 ~17:20 UTC to 2026-07-23 21:28 UTC) without loss.
- status: computed (operational measurements)
- uses: camp12-null
- where: RESEARCH_LOG.md 2026-07-22 check-ins #1–#2, 2026-07-23 suspension, "Programme close-out summary" O6
- matters: makes multi-day campaigns restartable at slice granularity.

# GROUP — Others (b): cross-review and merge of the two November sessions

## xr-convergence | Same construction found independently twice
- kind: verdict
- says: Two sessions started from commit a3885fb with the same PDF and independently found the same construction (full cover, 2-adic CRT condition, BLS complement), the same cover at Q = 1.2·10^6 (2,005 classes, r ≤ 17,431) and n = 12,475, and the same g = 1,200,109 for two different N (committed 08:03 UTC vs 08:44 UTC); both concluded a GRH proof moves no record.
- status: computed (cross-review reruns)
- uses: wp11-bls, wp10-verdict, wp12-grh-ledger
- where: crossreview_8ffe9d7a.md §1; crossreview_2ce9e63a.md §1; RESEARCH_LOG.md 2026-11-21 entries
- matters: the strongest evidence either branch has that the method is right.

## xr-verification | Every record passes three independent legs
- kind: verdict
- says: The three Game-1 records at the merge (g = 2,000,269 at 15,595 d; g = 1,200,109 at 11,263 d in two versions) pass proth/verify.py, both stdlib bls/ verifiers (87–89 s for 11,263 d, 230–233 s for 15,595 d in pure Python) and PARI crosscheck.gp (own N−1 certificate, isprime, brute-force scan of 92,942 / 148,950 primes q < g); proth/tamper_test.py rejects 11/11 mutations on both height records, and the 5,000,251 and 10,000,141 records later pass the same legs.
- status: computed (re-run in both sessions' containers on the merged tree at 79f2326)
- uses: wp11-bls, rec-g1-ladder
- where: crossreview_8ffe9d7a.md §2; crossreview_2ce9e63a.md §2; merge_2026-11-21.md "Verification after the merge"
- matters: the repo's dual-stack standard (two independently written checkers plus PARI) was obtained for free.

## xr-retractions | Retractions and relabels at the merge
- kind: retraction
- says: Corrected 2026-11-21: (1) the two 1.2·10^6 searches were called independent ("two 1–2% tails", joint p ≈ 2.5·10^−4 or ≈ 1%) but were one progression, joint p = 0.046; (2) "new record" and "first record without ECPP" for the 8ffe9d7a session's g = 1,200,109 became "independent second certificate" (priority 08:03 vs 08:44 UTC; the other session then certified 2,000,269); (3) "their verifier ships a mutation test": the harness was never committed (proth/tamper_test.py is the committed 11-case suite); (4) the commit that produced its record is 4adaa4d, not 647efbf; (5) WP11's header on which numbers came from retired code; plus the Linnik erratum (wp10-erratum) and the Theorem-2 caveat (wp12-thm2).
- status: retracted (replaced by wp12-probe and the 12-item errata list of merge_2026-11-21.md)
- uses: wp12-probe, wp10-erratum, wp12-thm2
- where: merge_2026-11-21.md errata 1–12; crossreview_2ce9e63a.md §4.4 erratum; crossreview_8ffe9d7a.md ⟲ notes
- matters: shows which claims were softened and why the ladder's cost model was not harmed.

## Dependency notes

Ten chains that carry the programme, in plain words (ids in parentheses).

1. **Why the Game-1 records are believed.** The records (rec-board, rec-g1-ladder) rest on four things: the CRT trick that makes the complement carry its own one-modexp proof (wp11-bls), complete covers (wp12-fullcover, made ~10% shorter by wp12-lazy-cover), the "one prime per ln P/(e^γ ln B) survivors" cost model (model-density) and GPU screening (eng-gpu-sieve). Trust comes from three independently written verifier legs plus a mutation test (xr-verification), on top of the kickoff audit (rec-audit). The one observation that threatened the cost model, two very long waits at Q = 1.2·10^6, was dissolved by the overlap check and the out-of-sample probe (wp12-probe) before the ladder (wp11-ladder) was used to go to 5M and 10M.
2. **Why sub-100 digits is "brute force or nothing".** The density model gives E = 44.1 and ~9×10^5 GPU-years (wp3-regime1, after the units correction wp3-units-slip). The tempting shortcut, oversized covers (wp3-regime2), turns into a density-1.026 modular subset-sum (wp3-subsetsum), and the alternative of decoding a CRT code is blocked because the decodable regime (GSS radius, wp3-gss) and the regime where small representatives exist cannot overlap (wp3-barrier, reached only after retracting an "open window", wp3-retraction); the toy decoder shows LLL does not even reach the radius (toycrt). What is left is wp3-open, the unknown algebraic mechanisms (closed inside the grammar by WP7 then WP9) and H2 (wp9-h2).
3. **What the Closure Theorem rests on.** wp9-theorem needs Lemma 1 (wp9-lemma1: built from the WP7 probes wp7-p1, wp7-p2, wp7-p3p4 plus the case-by-case closures wp9-prop9, wp9-prop10, wp9-dense, wp9-expfamily, wp9-ceilings), Lemma 2 (wp9-lemma2: a proved subtraction fact first stated in wp8-three-doors, a conditional half that needs H1, and the empirical leg wp7-p5) and H2. Its empirical appendix is the exhaustive tier (wp9-exhaustive) and the generative tier (wp9-gen-referee), with the referee calibrated by wp9-tier0; the verdict (wp9-verdict) is "draft rigor, conditional on H1 and H2, inside the chosen grammar".
4. **"Only Door 1 and Door 2 can move records."** This is the conjunction of: no paradigm escape inside the grammar (wp9-verdict), GRH moves nothing (wp10-verdict), the frontier is an integrality gap sitting at a local optimum (wp8-lp-vacuous, wp8-local-opt) and each ×10 of compute is about +2.3 nats (wp8-ladder). The programme strategy (wp8-staircase) is therefore Door 1 (d1-verdict) plus Door 2 throughput (eng-gpu-sieve, camp3-skipfrac, wp8-small-opts).
5. **Door-1 verdict ("867 is near the optimum").** It rests on negative evidence only: exact windows (d1-lns), belief-propagation decimation (d1-bp) and a half-cover exact block (d1-endgame) never beat greedy's 867, while the sole evidence of headroom is a Gaussian-tail extrapolation (wp8-door1-ensemble, 758). Standard certificate tools are vacuous here (wp8-lp-vacuous, wp10-sieve-positivity), so the verdict is evidence, not a theorem.
6. **Why GRH "moves constants, not walls".** wp10-verdict and wp12-grh-ledger rest on record parameters versus √x-quality error terms, on H1 being a k-tuple statement GRH does not give (wp9-h1), on Bombieri–Vinogradov already supplying the sieve level (wp12-thm2, wp10-sieve-positivity) and on BLS beating Miller by seven orders of magnitude (wp11-bls). Both assume the alpo.ge claim without depending on it; wp10-erratum fixes the one constant that was wrong.
7. **Covering bounds.** wp12-thm1 (pigeonhole + Mertens) and wp12-thm2 (linear sieve + Bombieri–Vinogradov) bracket certified deserts between (1.349−o(1))·ln N·ln ln N and (ln N)^{4+ε}; greedy data (0.72·x·ln²x) sit one logarithm above Theorem 1 (wp12-open-fx); the constants for genuine Goldbach numbers lean on unchecked Linnik-type literature, and wp10-erratum records that the paper's Theorem 14 is superseded in rate.
8. **Records follow log(compute).** The T(100,000) sequence (rec-t100k) came from throughput, while covers were already saturated (camp-cover-frontier, cover-tools-audit); the two null campaigns (camp12-null) taught that one deep progression beats a breadth-first grand slam, which feeds the climb-every-rung design of wp8-staircase (rungs priced by wp8-ladder) and the selective-testing gain (camp3-skipfrac → wp8-small-opts O1).
9. **The staircase plan is unvalidated.** wp8-staircase leans on the wp8-ladder E values, on O1 having been measured only on CPU (wp8-small-opts), on Door 1 possibly yielding 0–2.6 nats (d1-verdict) and on Door-2 cost guesses; its rung 1 (Q = 140,009) is not logged as banked and the board still shows 119,419.
10. **The merge as an epistemic chain.** Independent rediscovery (xr-convergence) → cross-verification by three legs (xr-verification) → errata, notably the independence retraction (xr-retractions) → the probe that restored the model (wp12-probe) → one merged pipeline. This chain, not any formal proof (wp12-lean is not done), is the reason the board values are trusted.

## Timeline

Dates are those given in the files; times are UTC where the log gives them.
- 2026-07-22: programme kickoff (4-year proposal, record snapshot 2026-07-22); WP1 audit of both incumbents ends PASS (rec-audit); WP2/WP6 cover frontier at Q = 107,720 and calibration (camp-cover-frontier); Campaign 1 launched; container restarts at ~09:47 and ~10:21 trigger driver v2/v3 (ops-chunked).
- 2026-07-22 ~17:20 to 2026-07-23 21:28: 28-hour suspension; resumed losslessly at 142/1,200 slices.
- 2026-07-25 ~16:45: Campaign 1's original 1,200-slice budget exhausted (3.15e8 elements, 0 hits) and extended; ~18:30: Campaign 1 retired at 1,213/2,400 slices, Campaign 2 launched; master records merged (T(100,000) 186 d g = 109,357; Budget 119,419 @ 199 d; Height 1,157,341 @ 2,480 d); PR #20 audit and AlphaEvolve cover-optimizer analysis (cover-tools-audit).
- 2026-07-26: constrained_100 benchmark and AlphaEvolve deep-dive part 2.
- 2026-07-28: Campaign 3 launched (c1 cover, Q = 122,000; camp3-skipfrac); Campaign 2 stopped at 2,132/2,400; master certifies T(100,000) = 179 d (g = 101,149), post-mortem written; the 150-digit GPU record (g = 104,527) evaluated (rec-t100k); WP3 retraction and memo v2 (wp3-retraction); costed menu; master reconciliation with FRONTIER.md and SoK §7 (PRs #27/#28) and the units-slip correction (wp3-units-slip); toy CRT decoder (toycrt) and WP7 probes (wp7-*) executed; programme close-out summary 2026-07-22 to 2026-07-28.
- 2026-07-29: Campaign 3 stopped at 380/17,200 slices; WP8 strategy memo and WP8b three doors (wp8-*); WP9 plan; Door 3: closure theorem draft v0.1, tier-0, exhaustive tier (13,661 instances), §9–§11 proofs; Door 1 turns 1–3 and D1.2/D1.3 (d1-*), "867 survives"; AlphaEvolve access verified, generative tier run (referee hole found), "Door 3 complete (draft rigor)" (wp9-verdict).
- 2026-11-20: date of alpo.ge/remark.pdf (claimed RH/GRH proof; Lean archive not checked here).
- 2026-11-21 (morning): sessions ccr-8ffe9d7a (WP10 GRH remark, WP11 BLS Game 1) and ccr-2ce9e63a (a memo written as its "WP10", renumbered WP12 at the merge), both from commit a3885fb; 07:27 the 8ffe9d7a search starts; 08:03 the 2ce9e63a g = 1,200,109 record is committed, 08:44 the 8ffe9d7a one; 2ce9e63a then certifies g = 2,000,269 at 15,595 digits (648 tests, 37 min).
- 2026-11-21 (later): cross-reviews; overlap finding (joint p = 0.046) and out-of-sample probe (6 vs 4.62); merge of 8ffe9d7a into 2ce9e63a (merge commit 79f2326; 8ffe9d7a frozen at 6c66bcd); errata 9–12; post-merge verification of all records (xr-verification, xr-retractions, wp12-probe).
- 2026-11-21 (evening and night): Campaign G on Colab (eng-gpu-sieve): g = 5,000,251 at 33,938 digits, then g = 10,000,141 at 61,329 digits; the replacement A100 runtime vanished between 21:33 and 21:47 and a new one resumed at 21:56 (about 1.4 h of GPU time lost, correctness unaffected); 16M-rung sieve and CPU fleet under way (rec-16m-rung).
- Latest dated entry in the files: 2026-11-21.

## Doubts

**A. Contradictions between files and stale numbers**
1. **Sub-100 cost, stale in two places.** wp7_probes.md (last paragraph) and RESEARCH_LOG.md ("Programme position, final", 2026-07-28, and the RETRACTION entry) still say Regime-I brute force is ~5×10^4 GPU-years; wp3_small_representative_memo.md §3/§7 and the log's master-reconciliation entry correct it to ~9×10^5 (units slip). Treat 9×10^5 as canonical (wp3-units-slip). The superseded "forward memo" table shows the same ×10 slip (140 d at 0.01 A100-years vs 0.10 in the later costed menu for the same 1.6e12 candidates).
2. **Campaign-1 luck probability.** The retirement entry calls the outcome "a P≈0.30 outcome" and the close-out says both misses were "0.22–0.30-probability draws", but the log's own survival table (≈ e^(−slices/510)) gives ≈ 0.09 at 1,200–1,213 slices and the budget-exhaustion entry says P(no hit) ≈ 0.11. The 0.30 is unexplained. (Campaign 2's 0.22 is near the ≈ 0.26 implied by its plan's λ ≈ 1.5 at 6.3e8 elements, my arithmetic for 5.6e8.)
3. **"|Ê − E| ≤ 0.1" is stated programme-wide but is not what every log shows.** Campaign 3 logged Ê = 21.24 ± 0.06 at calibration against theory 20.83 ("0.4 nats above ...; watching") and Ê ≈ 21.0–21.2 per slice later; Campaign 2 shows Ê ≈ 20.2–20.3 against "effective E ≈ 19.9" (explained as drift with ln N); the "~1.2×10^9 candidates" is never itemised and is close to the sum of the raw elements of the three campaigns (my arithmetic 3.18e8 + 5.6e8 + 3.98e8 ≈ 1.28e9), of which Campaign 3 actually tested only the emptiest ~8% (skip-frac 0.92). Affects model-density, wp7-p5, wp9-h1.
4. **WP3 entropy arithmetic.** wp3 §3 gives design entropy ~2,698 nats vs ln(M/B) = 2,630 nats and "surplus ~+57 nats ⇒ ~e^57 pairs" (§4: "~2^82 solutions"), but 2,698 − 2,630 = 68 nats ≈ 2^98. The density 1.026 uses 2,698; the ~11-nat gap is not explained. Conclusions are unaffected (wp3-regime2, wp3-subsetsum).
5. **Equilibrium versus budget.** wp8 §0(c) says the cover "is not budget-limited" and sits at the boost-vs-kills equilibrium (adding r = 461 nets +0.00); wp9 §6 T1 finds that at Q = 122k extra moduli would still be net positive (gain ≈ kills·0.024 exceeds the boost cost E/(r−1) ≈ 0.046; with wp8's 3.5 kills that is 0.084 vs 0.046), so the ln M budget binds there and the equilibrium only at 200k. wp8's "+0.082 nats" equals E/(r−1) only for E ≈ 37.7 (the 200k rung) although the surrounding text describes the 122k cover and names no Q. WP9 calls this a "refinement"; "the frontier is flat because of equilibrium" is therefore right at 200k only (wp8-local-opt).
6. **Moduli of the c1 cover.** wp9_plan.md says the fixed moduli are "the 88 primes 3..457" and wp8 says "ours cap at 457" (θ(457)); instance_q122k.json lists 88 moduli with maximum 683 (odd primes up to 439 plus 467, 487, 491, 683, omitting 443, 449, 457, 461, 463, 479), and there are only 87 odd primes up to 457 anyway; wp10 cites 683 as a top modulus (wp8-lp-vacuous, d1-lns). Description error, results unaffected.
7. **Exhaustive-tier numbers.** wp9 §8 says the ExpFamily near-miss board is 3.09–4.2 nats per residual kill and "nothing below 10" elsewhere, but exhaustive_summary.json lists near-miss rows up to 5.37 and per-family bests of 8.53 (PolyImage) and 7.95 (Cyclotomic). The tier was also run before the §12 scorer fix (the JSON still shows ExpFamily killable 10,416 at costs of roughly 2,700–4,700 nats against a 460-nat budget) and the log does not say it was re-run; the fix can only lower scores, so "0 passes" stands a fortiori (wp9-exhaustive).
8. **Door-3 benchmark and labels drift inside wp9.** §5 states the filter as "marginal cost < 2.5 nats"; tier-0 moves the benchmark to 1.01 nats (marginal), §12 to 0.041 nats (average) and a 0.44-nat bar. The header "draft v0.1", §2 "[C, target statement]", Lemma 1 "[C, partial P]" and wp9_plan's "Phase 4 BLOCKED" are stale relative to §9–§14 and the later plan sections; read the latest section.

**B. Rigor and scope**
9. **"Proved" in WP9 means draft rigor.** The proofs are first-moment counts; Prop 11.2 is "[P-shaped]" with Taylor-regime uniformity and non-abelian word combinatorics unwritten; §10 relies on unproved equidistribution of form values; nothing is Lean-checked or externally reviewed. The schema language L was chosen by the authors, so wp8 §6's "a theorem that there is no fourth [door]" is stronger than wp9 §14, which explicitly leaves out-of-grammar mechanisms open (wp9-theorem, wp9-verdict, wp8-three-doors).
10. **Prop 10.1's table sentence.** "α ≤ (d−1)/d ≤ 0.9" holds only for total degree d ≤ 10; since the threshold is α* = 0.9735, (d−1)/d exceeds it for d ≥ 38 where k_max is infinite (my arithmetic). Harmless inside the grammar (factor degrees 2, v ≤ 3) but the sentence reads as general (wp9-prop10).
11. **Door 1 "certified".** The log headline "867 survives, certified" means 21 of 22 window LPs are window-optimal, not global optimality (the uncertified window holds the smallest moduli); the half-cover exact blocks have no optimality proof (caps 160 s and 260 s); the annealed 758 is a Gaussian-tail extrapolation to z ≈ 29.5 from a measured σ and the log itself later reads it as probably a clustering gap, cutting the prize from "2.6–2.9" (wp8) to "0–2.6" nats (d1-lns, d1-endgame, d1-verdict, wp8-door1-ensemble).
12. **Toy CRT scope.** As described, the toy instances reveal one residue per position (L = 1) with random wrong residues at 61 positions and ℓ ≤ 45; "~10^7 alternative solutions" is a first-moment estimate, not an enumeration; the L = 16, ~420-position sub-100 regime is reached only through the radius formula, and wp3-barrier is likewise a heuristic (toycrt, wp3-barrier, wp3-open).
13. **Quantum and Door-2 arithmetic.** The quantum verdict depends on assumed constants (10^5–10^6 s per oracle call, 1–1,000 machines) and flips in the "miracle" case (E* = 27 < 37.7); the Door-2 line "1% of Folding@home ≈ 7 months" is ≈ 5.7 months from the memo's own 950 fleet-years and 2×10^5 ratio (my arithmetic), and equating exaFLOPS with fleet capacity is an assumption (wp8-quantum, wp8-staircase).
14. **Unchecked inputs.** The alpo.ge RH/GRH claim was never checked (Lean archive not downloaded; both sessions assume it true). Literature marked [L] and not re-checked: Chang 2014 Cor. 11 (12/5), Xylouris (5), Pintz (X^0.72), Lamzouri–Li–Soundararajan, Bach 1990, Carneiro–Milinovich–Soundararajan 2019; FRONTIER.md is a parallel session's file outside these ten. Only Shi's Thm 6.22 / Remark 6.24 was verified verbatim against its PDF; GSS Thm 3 was obtained and checked (wp3-gss). No entry is Lean-checked.
15. **Constant comparison.** "C(x) ≥ 1.349·x·ln x beats Shi's ½" holds under Shi's convention (p(n) = ∞ when n has no partition) and for "no summand below" statements; for genuine Goldbach numbers the constants are 0.270 (Linnik 5) or 0.562 only if Chang's unchecked 12/5 applies, and the log's one-line summary omits that (wp12-thm1).
16. **Naming and numbering.** "WP8" labels both the E10 record campaign (RESEARCH_LOG status table) and the strategy memo; "WP10" was used for two different memos before the merge (now WP10 = GRH remark, WP11 = BLS Game 1, WP12 = prime-covering ledger); "R(10^199)" and "R(10^200)" are used interchangeably (wp8 §5: g = 112,249 is a 200-digit N ≥ 10^199).

**C. Threads with no outcome in these files**
17. The Q = 140,009 fleet rung (E = 24.96, "first hit expected in days" on 2026-07-29) is not reported anywhere, while the board dated 2026-11-21 still lists Budget g = 119,419; the g > 3·10^6 CPU run assigned to the other session; the 16,045,849 rung; Campaign 2's 712 reserve variants and the round-4 164-digit-modulus cover; Door 1's untried routes (banded ensemble, basin-hopping, 1RSB/SP, the public optimization challenge); posting of the H2 note; applying the paper.tex patch; the Lean proof; the two WP3 open problems.

**D. Retractions and what replaced them**
18. WP3 v1 "open window for CRT decoding at R ≥ 60,000" → the coupled-parameter barrier (wp3-retraction, wp3-barrier).
19. Sub-100 cost ~3×10^8 (E ≈ 52 forward memo) → ~5×10^4 → ~9×10^5 GPU-years (wp3-units-slip); the forward memo's "density ≈ 0.81, ~2^145 systems" framing → the density-1.026 subset-sum (wp3-subsetsum).
20. "Two independent 1–2% tails" (WP11's "~1%-tail draw", the first cross-review) → one progression, joint p = 0.046, out-of-sample z = +0.64 (xr-retractions, wp12-probe).
21. "New record" and "first record without ECPP" → "independent second certificate"; stale board statements fixed at 6c66bcd (xr-retractions).
22. GRH's gain on the paper's Linnik constant ×2.5 → ×1.2, and Theorem 14 "constants only" → "superseded in rate" (wp10-erratum).
23. WP12 Theorem 2 presented as the first impossibility statement → asymptotic only, vacuous at record parameters (wp12-thm2); WP11's ladder "~30% pessimistic" next to the lazy cover (wp11-ladder).
24. Generative-tier fitness 0.4597 → 0.092 after the budget cap; ExpFamily per-offset floor 2.197 → 1.609 with a supply ceiling of 419 offsets; 16 spurious exhaustive-tier passes → BASELINE semantics (wp9-gen-referee, wp9-expfamily, wp9-exhaustive).
25. SoK §7.4's LP certificate as a hoped-for floor → executed and vacuous (wp8-lp-vacuous); Door-1 prize "2.6–2.9" → "0–2.6" nats (d1-verdict); wp8 §0(c) "frontier at equilibrium" → two regimes in wp9 §6 T1.
26. Review errata: "their verifier ships a mutation test" → harness never committed (proth/tamper_test.py is the committed suite); record commit 647efbf → 4adaa4d; "hours on a gwnum-class engine" → "hours on the GPU fleet or a few dozen cores"; Chang's exponent stated as fact → a [L] citation (xr-retractions).
