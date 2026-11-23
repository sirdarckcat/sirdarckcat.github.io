# Goldbach-gap map: how the Lean proofs and the research results fit together

Companion to the interactive page `viz/goldbach_map.html` (also published as an artifact). The page has
124 results and 223 links; this note says what the structure shows. Snapshot of 2026-11-23: Lean library at
`8683c0b` (branch `ccr-36ca7b46-8twf14`), research at `eed2a7f` (`ccr-d4a17dd0-7uu03r`), lead merge `85aef81`
(`ccr-2ce9e63a-hn0fuw`), thesis `85203b6` (`claude/phd-research-delegation-rualo0`).

## 1. The picture in one paragraph

A record g(N) = g needs two things: every prime below g is not a summand of N, and N − g is prime. The first half
is made true by **covering** (choose N's residues so that N − q is divisible by a small prime for most primes q)
plus **luck** (the few rows left over happen to be composite); the second half by an elliptic-curve primality
chain. The Lean library proves that principle, the certificate checkers, the records, and then a large body of
exact laws about what covering and search can and cannot do. The research documents supply the cost model (how
many candidates a record costs), the engines that search, the cover optimisers, and the arguments that no
cleverer mechanism exists. The two sides meet at about fifty points (section 3).

## 2. Layers

| Layer | Boxes | Where | What it holds |
|---|---|---|---|
| Records | 4 | Lean | g = 158,209 (200 digits), the earlier ladder, the pure cover to 15,907 (no luck), and a family of 21,378,978 covered numbers |
| Checkers | 7 | Lean | failed Fermat test ⇒ composite; block check; least-summand certificate; one elliptic-curve primality step and the group law it runs |
| Covering principle | 8 | Lean | primorial core, covering certificate, every cover is realised, prime moduli suffice, kills are residues, a cover gives a number below a cap |
| Asymptotic bounds | 14 | Lean | every odd prime is a least summand; effective form under Linnik; counting bound; covering bounds 0.73, 1.2 and 1.349 times ln X·ln ln X, with Mertens' third theorem proved from Mathlib |
| Counting laws | 7 | Lean | budget law, first-moment pigeonhole, no free lunch, layered covers, value-set ceiling |
| Search limits | 13 | Lean | hit mass, selection and tilt identities, lattice and Johnson radius, black-box bound, population bound, merge cost, list gain (0.207 rows per nat above Q), 21 settled ideas |
| Function-field model | 8 | Lean | Stickelberger–Swan, parity theorem, deserts N = λ·V^p, discriminant as a resultant |
| Search-code proofs | 11 | Lean | CPU vector kernels and GPU kernels compute exactly the base-2 Fermat test |
| Research: models and results | 40 | docs | cost model E, ceiling 2.13M, prices, closure theorem, three doors, rounding gap, decoding barrier, WP12 theorems, the sublinear programme and the function-field toy |
| Research: searches and records | 12 | docs | the three games, fleet campaign, height records, megagap, engines, cover optimisers (both sessions), verification legs |

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
| Sublinear barriers (lattice, merge, black box, lists, CRT line) | `lattice_radius`, `johnson_leaves_the_cover`, `mitm_condition`, `blackbox_fraction`, `hitMass_selected_le`, `list_gain_above_Q`, `move_budget` | cited in `sublinear/README.md` |
| Function-field toy | Stickelberger–Swan, `parity_card_factors`, `desert`, any-degree extension | cited in `sublinear/README.md` |
| 100-idea brainstorm | `Cap/Brainstorm.lean` (21 ideas settled by theorem) | cited in both |
| Fermat kernels (fscan, CUDA) | `Fscan.*`, `Gpu.*`, `Gpu28.*` `lane_correct` / `fermat28_correct` | Lean headers name the code files |
| Records and complete covers | `Records.lean`, `Cover15907.lean` (generated from the fleet's and the sublinear programme's files) | file headers |
| Proof-carrying records (proposed in WP10, WP12) | `isLeastSummand_of_noSummandIn`, `Record200_g158209` | same idea, delivered for the budget game only |

## 4. What the record rests on

`Record200_g158209` → block checks (20) + elliptic-curve chain (27 steps) + the certificate theorem → failed-Fermat
soundness, point-count bound, group-law agreement → the definition of g(N). That is the whole chain; it uses
no research claim and none of the kernel proofs. The data (N, the cover, the witnesses) come from the fleet and are
not trusted: the Lean kernel re-evaluates them. A text search of the library finds no `sorry`, `native_decide` or
`axiom`; I did not run Lean.

## 5. What the plan rests on (unproved or heuristic)

* **H1**, independence of the leftover rows. Every cost forecast uses it. Lean's `expected_hits` states it as an
  assumption in its own header (“the independence itself is the model and not a theorem”).
* **H2**, no compositeness test cheaper than one exponentiation. The closure theorem and the cost floor use it.
* **The ceiling 2,130,704** and the "10% = 213,070" target: a heuristic prediction, validated on 6×10^8 numbers near
  10^18, not a bound.
* **The ideal-search prizes** (3.5 to 14.8 nats) assume numbers below 10^200 are a fair sample of residue vectors.
* **Closure theorem, Door 1, WP12 Theorem 2**: draft-rigour or evidence, not Lean-checked.

What *is* proved are the limits, but they are exact only inside their models: the first-moment law, the budget law,
the lattice radius, the black-box and population bounds, the list-gain bound.

## 6. Things I noticed

1. **The research documents lag.** The research branch does not mention 158,209 (its ledgers find the number in no
   file); its July verdict that greedy's 867 rows are near-optimal was superseded by tempering (850–851 rows, found
   by both sessions independently); and `sublinear/README.md` says "about e^10 better" where its own table gives 27.5
   nats at depth 10^8.
2. **Lean and research converge.** The BLS construction, the tempering optimiser, the 100-idea list and the parity
   theorem were each found by both sessions; agreement is evidence the numbers are right.
3. **Formalisation gaps.** The Erdős–Rankin style improvement is only partly in Lean (`Layers`); Linnik is a hypothesis;
   BLS certificates (the height game) are not formalised; the closure theorem and Theorem 2 are paper-only.
4. **What would move the record.** Per the research models: a week of the fleet is worth about 167,000, the remaining
   budget (about 10 fleet-days at 29M members per second) about 169,000–172,500 expected; aiming at 213,070 needs about
   5,600 times more. An ideal search to depth 5,000 would fit the budget, but every known method to find one costs more than
   scoring candidates one by one. No sublinear algorithm is known and none is ruled out.
5. **Hygiene.** Retractions (open window, units slip, "independent" searches, GRH's gain 2.5 → 1.2, fail-open scripts)
   all came from the team itself.

## 7. How the map was built, and its limits

* Lean side: a text scan of the library source (`tools/keygraph.py`): declaration names, namespace and `open`
  tracking, comments ignored, docstrings attached to the declaration they document. 72 boxes; a box may stand for
  several theorems (listed under "Also covers"). It does not follow method syntax (`h.foo`) or instances, so six links
  were added by hand (marked) and some may be missing.
* Research side: three reading agents produced ledgers (`data/ledgers/`, about 200 entries) from the documents; I wrote the 52
  boxes from them and re-checked key numbers. Links are the documents' own cross-references.
* The Lean branch's `phd/cap200/` is mapped as one box (the Lean session's cover experiments); its brainstorm
  experiments are not mapped individually.
* Nothing from the archives was executed.

## 8. Rebuild

```
python3 -I tools/keygraph.py <lean_root> <cache_dir> build viz/spec_lean.json viz/graph_lean.json   # Lean links
python3 -I viz/make_gb.py                                                                            # data + page
```
`viz/spec_lean.py` lists the Lean declarations per box, `viz/cur_*.py` the curated text, `viz/meta.py` groups,
lenses and page text.
