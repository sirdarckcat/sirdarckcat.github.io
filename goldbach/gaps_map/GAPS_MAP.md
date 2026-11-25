# Goldbach-gap map: how the Lean proofs and the research results fit together

Companion to the interactive page `viz/goldbach_map.html` (also published as an artifact). The page has
187 results (95 from the Lean library, 92 from research documents) and 417 links; this note says what the structure shows.
Snapshot of 2026-11-25, about 09:00 UTC: Lean library read at `a1c77dc` (branch `ccr-36ca7b46-8twf14`), research at `48c73de`
(`ccr-d4a17dd0-7uu03r`), the exact-search session at `018b7ed` (`ccr-b8c25887-i6tn9f`), the campaign at `ebb6e1e`
(`ccr-8ffe9d7a-4ni11u`), the archipelago study at `d960f7f` (`ccr-c6e00296-3g7fp9`), the lead's merge at `43ab0b3`
(`ccr-2ce9e63a-hn0fuw`), the thesis at `85203b6`. The first map was the snapshot of 2026-11-23 (136 results, 260 links);
section 10 lists what changed since. Eight boxes tagged 'exhaustive test' add a statistical test of the model from the
archipelago study (`goldbach/archipelagos/`; section 9).

## 1. The picture in one paragraph

A record g(N) = g needs two things: every prime below g is not a summand of N, and N − g is prime. The first half
is made true by **covering** (choose N's residues so that N − q is divisible by a small prime for most primes q)
plus **luck** (the few rows left over happen to be composite); the second half by an elliptic-curve primality
chain. The Lean library proves that principle, the certificate checkers, the records, and then a large body of
exact laws about what covering and search can and cannot do. The research documents supply the cost model (how
many candidates a record costs), the engines that search, the cover optimisers, and the arguments that no
cleverer mechanism exists. Since 23 Nov a third theme has grown between them: the **cover depth** D(n), how far n moduli can
strike the primes with no luck at all, with exact values, certified covers, a counting law and a conjectured limit. The two
sides meet at about sixty points (section 3).

## 2. Layers

| Layer | Boxes | Where | What it holds |
|---|---|---|---|
| Records and certificates | 18 | Lean | g = 160,357 (200 digits, 24 Nov), g = 158,209, the earlier ladder, the pure covers (15,907 on 89 primes; up to 16,981 on 93), a family of 21,378,978 covered numbers, the record holders up to 10^12, a generator for A025018 proved correct, Goldbach and the 26 record holders below 2^25 by a kernel-run sieve; the certificate machinery: failed Fermat test ⇒ composite, block check, least-summand certificate, one elliptic-curve primality step and the group law it runs |
| Covering principle | 8 | Lean | primorial core, covering certificate, every cover is realised, prime moduli suffice, kills are residues, a cover gives a number below a cap |
| Cover depth and counting | 31 | Lean, docs, data | **new**: D(n) defined, exact in the kernel for up to nine moduli, certified covers up to 614,101 on 1,228 moduli, the count of covers and its exact pair-weight step (Lean); exact D(n) to 35, D(89) < 35,000, the measured law ln g0 = θ − Q/ln² x, its derivation, the limit 1.1275 conjectured on 24 Nov and withdrawn on 25 Nov (its referee check, the entropy of the small moduli that undoes it, the structured prefix that shows the replacement is not derived either, a check of mine whose verdict I withdrew), why 1.349 is not the truth (research, uarch, Lean scripts, archipelago) |
| Asymptotic bounds | 14 | Lean | every odd prime is a least summand; effective form under Linnik; counting bound; covering bounds 0.73, 1.2 and 1.349 times ln X·ln ln X, with Mertens' third theorem proved from Mathlib |
| Counting laws | 7 | Lean | budget law, first-moment pigeonhole, no free lunch, layered covers, value-set ceiling |
| Search limits | 16 | Lean | hit mass, selection and tilt identities, the thinning law, lattice and Johnson radius, black-box bound, population bound, merge cost, list gain (0.207 rows per nat above Q), needles, 21 settled ideas, finding a cover for arbitrary rows is as hard as SAT |
| Function-field model | 8 | Lean | Stickelberger–Swan, parity theorem, deserts N = λ·V^p, discriminant as a resultant |
| Search-code proofs | 11 | Lean | CPU vector kernels and GPU kernels compute exactly the base-2 Fermat test |
| Research: models and results | 54 | docs, data | cost model E, ceiling 2.13M, prices, closure theorem, three doors (door 1 now measured: a floor under every cover), rows above the design level, the design menu, rounding gap, decoding barrier, WP12 theorems, the sublinear programme and the function-field toy, a model of g(N) with no primes; eight tests of the model on exhaustive data near 10^12 to 10^18 (tagged 'exhaustive test') |
| Research: searches and records | 20 | docs, logs | the three games and the fixed-gap game, the fleet campaign and its state, how 160,357 was found, the 491 covers, the GPU sieve chain, IFMA Fermat tests, height records, megagap, engines, cover optimisers, verification legs |

## 3. Where the two sides meet

| Research says | Lean proves | Link |
|---|---|---|
| WP7 P1: prime-power moduli are dominated | `prime_moduli_suffice` | cited in `Rows.lean` |
| WP7 P2: polynomial identities kill at most O(√Q) rows | `card_le_sqrt_succ`, `not_prime_row_of_eval` | cited in `Poly.lean` |
| WP9 Lemma 2a: a shared divisor divides q₁ − q₂ | `lt_of_dvd_two_rows`, `row_unique_of_le` | same content, not cited |
| WP12 Theorem 1: covers reach 1.349·x·ln x | `eventually_exists_even_le_of_mul_lt_one` (no hypothesis), on `exists_even_le_of_layers`, PNT, `mertens_third` | cited in `Layers.lean`, `COVERBOUND_STATEMENTS.md` |
| Thesis ch. 2: primorial, cover, realisation, Dirichlet, transfer | `not_isSummand_of_primorial_dvd`, `not_isSummand_of_cover`, `exists_isLeastSummand_of_cover`, `exists_isLeastSummand` (+ Linnik form), `not_isSummand_of_desert` | the Lean docstrings use the thesis labels (lem:primcore, prop:cover, thm:coverdirichlet, thm:dirichlet) |
| Cost model, cap accounting | `card_residues_in_le`, `noFreeLunch`, `not_prime_sub_iff` | cited in `Budget.lean`, `FirstMoment.lean`, `Rows.lean` |
| Selection identity, hit mass | `expected_hits`, `selection_fraction`, `enrichment_at` | cited in `Selection.lean`, `Tilt.lean` |
| Independence of the leftover rows (H1); the prize table's step to depth 10^8 | `thinSum_le_of_lt`, `thinCount_zero_le_of_lt` (above Q, independence is an upper bound) | cited in `Thinning.lean` (added 2026-11-23 16:40) |
| Miniature: the best numbers are independent needles | `IsNeedle.add_of_forall`, `needle_pairs_lt_1000` (close needles share rows) | cited in `Needles.lean` |
| Exhaustive tests: every row composite, pairs of neighbours, archipelagos, records, scoring (section 9) | `expected_hits`, `thinSum_le_of_lt`, `IsNeedle.add_of_forall`, `shared_row_value`, the record table's Chebyshev check | the evidence boxes' links |
| Sublinear barriers (lattice, merge, black box, lists, CRT line) | `lattice_radius`, `johnson_leaves_the_cover`, `mitm_condition`, `blackbox_fraction`, `hitMass_selected_le`, `list_gain_above_Q`, `move_budget` | cited in `sublinear/README.md` |
| Function-field toy | Stickelberger–Swan, `parity_card_factors`, `desert`, any-degree extension | cited in `sublinear/README.md` |
| 100-idea brainstorm | `Cap/Brainstorm.lean` (21 ideas settled by theorem) | cited in both |
| Fermat kernels (fscan, CUDA) | `Fscan.*`, `Gpu.*`, `Gpu28.*` `lane_correct` / `fermat28_correct` | Lean headers name the code files |
| Cover depth D(n), exact values | `CoverDepth*.lean`: the search proved correct, D(0..9) in the kernel, one certified vector for every n up to 35 | headers cite the research session's `goldbach/sublinear`; the exact values to 35 and D(89) < 35,000 are the uarch session's search, not in Lean |
| Number of complete covers g0 | `CoverCount`: exact inclusion–exclusion formula, monotone lower bound from every certified cover, the range of the covering bound | the measured law ln g0 = θ − Q/ln² x is not proved; the headers say so |
| Derivation of the law (price per row, Hardy–Littlewood pairs) | `CoverPairs`: the pair weight has mean exactly 6s/(s − 1); `CoverPairSums`: product form, partial sums at most the mean, C₂ ≥ 1/2 | the headers quote the research session's messages; the second-order term (singular series average) is not formalised |
| Limit constant 1.1275 | none; the Lean session's referee check (`scripts/cover_limit_check`) and Λ(1) recomputed (`scripts/cover_count`) | withdrawn on 25 Nov by the research session (the small moduli lack the entropy the recursion gave them); the replacement, of order r ln² r/ln ln r, is not derived either (a structured prefix beats random classes: Lean referee read, 11:27 UTC); proved at paper level: D(n) ≥ c r ln² r ln₃r/(ln₂r)² |
| Covering bound in depth form | `eventually_exists_classes_of_mul_lt_one`, `Cap.exists_classes_of_layers` | the same cover that builds the asymptotic bound, stated for D(n) |
| Goldbach by covering; records are covers | `exists_isSummand_le_depth`, `exists_isSummand_of_lt_961`, `RecordWalk.beats_iff_wheels` | headers: depth below the next prime squared would give Goldbach |
| SAT-hardness of finding covers | `Cap/Hardness` | cited in `sublinear/README.md` |
| A model of g(N) without primes | `scripts/lgs_heuristic` (Lean session): one fitted constant reproduces the research cost figures | the research README cites it (Result 3, ceiling) |
| Records and complete covers | `Records.lean`, `Cover15907.lean` (generated from the fleet's and the sublinear programme's files) | file headers |
| Proof-carrying records (proposed in WP10, WP12) | `isLeastSummand_of_noSummandIn`, `Record200_g158209`, `Record200_g160357` | same idea, delivered for the budget game only |

## 4. What the record rests on

`Record200_g160357` → block checks (20) + elliptic-curve chain (21 steps) + the certificate theorem → failed-Fermat
soundness, point-count bound, group-law agreement → the definition of g(N). That is the whole chain; it uses
no research claim and none of the kernel proofs. (The first map said 27 steps for 158,209; counted as applications of the
step check it is 26, and 21 here.) The data (N, the cover, the witnesses) come from the fleet and are
not trusted: the Lean kernel re-evaluates them; the file was built 38 minutes after the find. A text search of the library finds
no `sorry`, `native_decide` or `axiom`; I did not run Lean.

## 5. What the plan rests on (unproved or heuristic)

* **H1**, independence of the leftover rows. Every cost forecast uses it. Lean's `expected_hits` states it as an
  assumption in its own header (“the independence itself is the model and not a theorem”). Since the snapshot, `Cap/Thinning.lean`
  proves that inside the residue model, for the primes above Q, independence is an upper bound, so there it is an inequality and not a
  premise; the residue model itself and the rows below Q stay heuristic. An exhaustive test on 60 million numbers near 10^12,
  10^15 and 10^18 (section 9) measures the joint probability that every row is composite: once the sieve passes the threshold
  it matches independence within about 1%, for pairs of neighbours as well, and up to each window's record. With shallower
  sieves independence overstates it by 2–9%. Evidence at these sizes, not a proof at 200 digits.
* **H2**, no compositeness test cheaper than one exponentiation. The closure theorem and the cost floor use it.
* **The ceiling 2,130,704** and the "10% = 213,070" target: a heuristic prediction, validated on 6×10^8 numbers near
  10^18 and on the records of exhaustive windows near 10^12, 10^15 and 10^18, not a bound.
* **The ideal-search prizes** (3.5 to 14.8 nats) assume numbers below 10^200 are a fair sample of residue vectors.
* **Closure theorem, WP12 Theorem 2**: draft-rigour or evidence, not Lean-checked.
* **Door 1** is now measured, not proved: the floor under every cover is 1,214 rows at Q = 170,000 against the best known 1,248
  (a measurement of the partition function by tempering). The only theorem is the exhaustive floor of 777 rows.
* **The counting law and the limit 1.1275** (section 10): measured at 14 sizes and derived by a recursion that rests on
  Hardy–Littlewood; the Lean pieces are exact identities and lower bounds. The limit 1.1275 was the recursion's and was
  withdrawn on 25 Nov (section 10).
* **The planning figures** (expected final record 175,000 to 176,000, the design menu) come from a model that the reading
  agents could not rerun; the horizon and rate differ between tables (8.5, 8.2, 8.0, 8.9 days; 29M and 52M members a second),
  and the fleet has shrunk since (section 10).

What *is* proved are the limits, but they are exact only inside their models: the first-moment law, the budget law,
the lattice radius, the black-box and population bounds, the list-gain bound.

## 6. Things I noticed

1. **The research documents lagged.** The research branch did not mention 158,209 (its ledgers found the number in no
   file); its July verdict that greedy's 867 rows are near-optimal was superseded by tempering (850–851 rows, found
   by both sessions independently); and `sublinear/README.md` said "about e^10 better" where its own table gives 27.5
   nats at depth 10^8. After this review the research session fixed these (commit `02564fb` on `ccr-d4a17dd0-7uu03r`):
   158,209 is named, the "e^10" sentence is corrected, the cost exponent between neighbouring targets is 1.2 to 2.3 (not 1.4
   to 1.8), and the F_25 check was rerun on all 300 quadratics.
2. **Lean and research converge.** The BLS construction, the tempering optimiser, the 100-idea list and the parity
   theorem were each found by both sessions; agreement is evidence the numbers are right.
3. **Formalisation gaps.** The Erdős–Rankin style improvement is only a remark (research) plus the fixed-layer skeleton in
   Lean (`Layers`); Linnik is a hypothesis;
   BLS certificates (the height game) are not formalised; the closure theorem and Theorem 2 are paper-only.
4. **What would move the record.** Per the research models: a week of the fleet is worth about 167,000; the planning model now
   expects 175,000 to 176,000 at the measured rate with family-B designs (earlier: 169,000–172,500 from about 10 fleet-days at 29M
   members per second), before the fleet shrank to five GPUs; aiming at 213,070 needs about 5,600 times more. An ideal search to depth 5,000 would fit the budget, but every known method to find one costs more than
   scoring candidates one by one. No sublinear algorithm is known and none is ruled out.
5. **Hygiene.** Retractions (open window, units slip, "independent" searches, GRH's gain 2.5 → 1.2, fail-open scripts)
   all came from the team itself.
6. **Referee checks now run across sessions.** The Lean session rederived the four steps behind the limit 1.1275 and found that
   they establish the recursion's limit only (hours later the research session found what the caveat meant, the entropy of the small moduli, and withdrew the limit); the archipelago session measured the research session's sketch for beating 1.349
   (deletion keeps 9–14%, so about 1.5, not 2) and found its pair formula was zero at the prime 3. Both are on the map.
7. **Words that hide three meanings.** 'Floor' is a measured partition-function floor (1,214), a certified exhaustive floor (777)
   and a linear-programme floor for fixed small classes (1,170); the summaries use the first. 'Family' is both a split of covers
   by rows above the design level and the frame of the smallest classes (not always the same). 'Certified' (777) is 62% of the best cover.
8. **Things the readers could not settle.** Which statement of Lavrik's almost-all theorem covers shifts of the size needed for a
   pair-covering proof of a constant above 1.349 (asked of me by the research session; section 10). A stale sentence in
   `RESULTS.md` (all GPUs replaced at about 23 h) against the README (RTX cards replaced after Colab's end). Whether the older CPU
   Fermat path, which used the 13-limb kernel above its 664-bit limit, missed a hit in any CPU-share run (the commit that fixes it
   says it was wrong above 664 bits). The 3,028 rows of the first cover for g ≥ 10^6 against the recursion's 2,315 are a search deficit, not evidence.

## 7. How the map was built, and its limits

* Lean side: a text scan of the library source (`tools/keygraph.py`): declaration names, namespace and `open`
  tracking, comments ignored, docstrings attached to the declaration they document. 95 boxes; a box may stand for
  several theorems (listed under "Also covers"). It does not follow method syntax (`h.foo`), instances or relative `open`s, so a
  few links were added by hand (marked) and some may be missing.
* The Lean session's scripts are mapped where they carry a result about the models (`lgs_heuristic`, `cover_count`,
  `cover_depth`, `cover_limit_check`); `rank_records`, `thinning_check`, `gen_*` and the raw `cover_floor_runs` are not.
* Research side: three reading agents produced ledgers (`data/ledgers/`, about 200 entries) from the documents; I wrote the 52
  boxes from them and re-checked key numbers. On 25 Nov three more agents produced delta ledgers (research 34 entries, fleet and
  exact search 31, archipelago 21; `data/ledgers/ledger_*_delta.md`), each recomputing figures from the data where it could, and a
  fourth fact-checked the new boxes against them (`data/ledgers/qa_report_25nov.md`: 9 wrong, 15 overstated, 5 unsupported, all applied;
  the main defects were units (the largest prime x quoted as a number of moduli) and two over-claims about what Lean certifies). Links are the documents' own cross-references.
* The Lean branch's `phd/cap200/` is mapped as one box (the Lean session's cover experiments); its brainstorm
  experiments are not mapped individually.
* Nothing from the archives was executed.
* Evidence layer: eight boxes written from the archipelago study (`viz/cur_tests.py`, loaded by `viz/cur_res.py`, which also
  appends one sentence to H1, the ceiling and the scoring barrier). Their numbers come from `goldbach/archipelagos/`, and each
  box links to its chart on the Goldbach Archipelagos page.

## 8. Rebuild

```
python3 -I tools/keygraph.py <lean_root> <cache_dir> direct viz/spec_lean.json viz/direct_lean.json   # links named in proofs
python3 -I tools/keygraph.py <lean_root> <cache_dir> build  viz/spec_lean.json viz/graph_lean.json    # chains of references
python3 -I viz/make_gb.py                                                                             # data + page
```
`viz/spec_lean.py` lists the Lean declarations per box; the curated text is in `viz/cur_lean1.py` to `cur_lean5.py` (Lean boxes),
`cur_edges_lean.py`, `cur_edges_lean5.py` (their links), `cur_res_a.py` to `cur_res_d.py` and `cur_tests.py` (research boxes),
`cur_res_edges.py` (their links) and `cur_patch.py` (changes to boxes that were already on the 23 Nov map, which mark them
'changed'); `viz/meta.py` holds the groups, lenses and page text.

## 9. The evidence layer: archipelagos and tests of the model

Added on 2026-11-23 from a separate statistical study, `goldbach/archipelagos/` on `ccr-c6e00296-3g7fp9`, with charts on the
Goldbach Archipelagos page (https://claude.ai/artifact/PjRwM5XGzjkMwWTsPMw3YR). It computes g(N) exactly for 20 million consecutive even N near 10^12, 10^15 and
10^18 and compares the truth with the model behind every forecast: rows with a prime factor up to the sieve depth are composite,
every other row is prime with one fixed probability, independently.

* **Every row composite (H1).** Grouped by the rows a sieve leaves, the share of big numbers (top 1% of g) matches the
  model within about 1% over five orders of magnitude once the sieve passes the threshold; totals at three depths are 0.993 to
  1.005 of the prediction. Shallower sieves overstate it by 2–9%, the pair term of the fscan notes.
* **Pairs of neighbours.** N + d is up to about 18 times likelier to be big when N is (d = 30). The model predicts every even lag
  up to 732 from shared rows and residues alone, within the block-bootstrap error bars.
* **Archipelagos.** 86–91% of big numbers sit in clusters linked by shared rows (Lean's needles in bulk). The largest, 176
  numbers near 10^18, sits on the largest prime gap in its window. A neighbour of a covered number leaves the cover
  (`shared_row_value`), so clusters cannot help the 200-digit search.
* **Records.** Each window's record is where the model's tail puts it (near 10^18, g ≥ 3,137 expected 1.2 times, seen once).
  Clustering fades toward the top, so it does not distort the ceiling.
* **Scoring.** A gradient-boosted model with 133 features of the same residues predicts big numbers no better than
  (1 − c)^rows with nothing fitted, in three held-out runs: the count of rows left is a sufficient statistic.
* **What a sieve can know.** Near 10^18 a sieve to 65,521 removes 27% of the uncertainty about which numbers are big; the rest is
  whether the surviving rows are prime.

Rebuild: `python3 gdata.py 1e18 2e7 e18` (and 1e12, 1e15), then `theory.py`, `archipelagos.py`, `ml.py`, `budget.py`, `tail.py`,
`viz_data.py`, `amap.py` and `build_page.py` in `goldbach/archipelagos/` (see its README).

## 10. Update of 2026-11-25

Built from the heads listed at the top. 51 boxes are new (19 Lean theorems, 32 research or computation, two of them my own: a draft proof and a check of the limit), 33 existing boxes
were changed, and the page gained a lens, **New**, that colours boxes new (red), changed (ochre) or unchanged; the 'what
changed' list at the top of the reading panel links to the main items. The groups 'Records' and 'Checkers' were merged and a
group 'Cover depth and counting' was added.

What the new material says:

* **The record is 160,357** (24 Nov 17:11:16 UTC), a near-miss of a Q = 170,000 design on the cover with 491 as the 89th prime,
  found on a Colab RTX card and proved in the kernel 38 minutes later. It exists only because of the top-of-range windows deployed on 23 Nov.
* **Cover depth** (Lean `CoverDepth*`, `CoverCount*`, `CoverPairs*`; the uarch session's exact search; the research session's law).
  D(n) is exact for 35 moduli (3,079); at 89 moduli 15,907 ≤ D(89) < 35,000, and the measured end of complete covers is near
  16,000. Complete covers are counted by ln g0 = θ(x) − c·Q/ln² x with c near 1; a recursion with the Hardy–Littlewood pair
  spread derives it with nothing fitted and predicts the loss to about 5% (and, stated in advance, the runs at x = 797,
  1,499 and 1,999, that is 138 to 302 moduli, to 4%). Its limit as first written gave D(n) ≈ 1.1275·r ln² r, withdrawn on 25 Nov (section 10). Tempering finds complete covers at 0.78 to 0.88 · x ln² x up to 302 moduli (98,731), and plain greedy reaches
  0.72 · x ln² x, one logarithm above the proved constant 1.349.
* **Door 1 is measured.** A floor under every cover (partition function by tempering) is 1,214 rows at 170,000 against the best
  known 1,248, so better covers are not a way to the 10% target; the rigorous floor is 777. Rows above the design level
  split near-optimal covers into families A and B; B is worth about +1,000 expected record.
* **The plan and the fleet.** The planning model expects 175,000 to 176,000 (8.2%) with a chance of 10% below 0.01%, but Colab
  now limits G4 and L4 runtimes to two each and the fleet is down to five GPUs. The GPU sieve chain raised the rate by 1.29 in a day.
* **A second game**, a fixed gap with the fewest digits, is priced (a gap of 200,000 at about 225 digits costs what 170,000
  costs at 200) and a first cover (629 moduli, g ≥ 10^6) exists; the predictions are untested far from 200 digits.
* **In Lean beyond depth**: a generator for A025018 proved correct and infinite exactly if Goldbach holds, `beats_iff_wheels`
  (a record is a cover), Goldbach and the 26 record holders below 2^25 by a kernel-run bitmask sieve, the record holders up to
  10^12, and the reduction of SAT to finding covers for arbitrary rows.
* **A model of g(N) with no primes** (Lean session) reproduces the research team's prize counts to 0.1 nats with one fitted
  constant and gives a ceiling of 2,133,689 against 2,130,704.

A request from the research session on 25 Nov, at the user's standing instruction to act as its helper: check whether the
deletion argument behind 'why 1.349 is not the truth' can be made rigorous. Short answer: yes with classical inputs
(Lavrik-type almost-all Hardy–Littlewood for shifts of size ≍ x, Selberg's upper bound for triples), giving a constant of about
1.352 against 1.349 (about 1.48 if every second moment had its predicted value); the write-up is `PAIR_COVER.md`, with two inputs named as unchecked, and a box on the map (status: paper, not checked by anyone else).

A second request, later the same morning (10:04 UTC): the research session doubted its own limit 1.1275 and, in the same hours, withdrew it
(its README, “The entropy of the small moduli: the limit does not hold”): the recursion let the small moduli choose classes they have not the entropy to
choose. With that entropy put in, D(x)/(x ln² x) stays between 0.91 and 1.01 from 89 to 3,244 moduli, turns down after about a thousand (0.98 at 9,591
moduli and 0.96 at 25,996, the last two computed by a contractor session) and, it argued, is in the limit of order r ln² r/ln ln r. It asked me to attack
that argument. **My first answer was wrong in its asymptotic half.** I confirmed that the ratio tends to 0 (a capacity bound: a prime near x can strike only
about ln x/ln ln x rows) and recorded two corrections to the route; the measurements of that check stand (greedy plateau 0.72 up to 10⁵, bulk gain 0.72–0.74,
top phase within 10% of a Poisson model). Then the Lean session's second referee read (11:27 UTC) showed that the premise, that the small moduli can do no
better than random classes, is false: giving every modulus of a block (z, x/4] the class of one common integer N₁ near Q leaves O(ln ln x/ln x) of the rows
against ln z/ln x (Erdős–Rankin). I checked it on real primes (0.93, 0.86, 0.72, 0.57 of the random count at x = 10⁴ to 3.75·10⁶) and wrote the consequence
out line by line: a rigorous depth D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)², above every constant times r ln r (it supersedes the proved 1.349 and my own draft
1.352). So neither 1.1275 nor its replacement is a limit of D(n); the order of D(n) is open between that bound and r^(4+ε). At the sizes that can be
computed nothing changes: a cover built from the block reaches 0.39 to 0.48·x ln² x at x = 10⁴ against 0.71 for plain greedy. The write-ups are
`COHERENT_BLOCK.md` and `LIMIT_CHECK.md` (corrected; scripts and outputs in `data/limit_check/`); the map has a box for the block, one for the Lean
referee read, one for the recursion with the entropy put in and one for my check (status: heuristic, verdict withdrawn). The lesson for the structure: a
count of typical covers (the entropy law) and the existence threshold D(n) are different things once structured families exist, and I tested the wrong
structured family before the Lean session found the right one.

