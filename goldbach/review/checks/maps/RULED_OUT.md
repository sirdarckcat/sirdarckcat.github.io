# RULED OUT: merged catalogue of every idea, method or direction declared dead (or parked) anywhere in the 21 maps

Synthesis only. No new ideas. Written 2026-11-25 about 14:30Z; newest evidence used is about 13:50Z.

How to read an entry: **Idea**. *Who.* Reason with numbers. **Strength** = one of: `LEAN` (kernel theorem, inside the model named), `PAPER` (written proof, draft rigour), `MEASURED` (with size), `COST` (cost estimate or model output), `ARGUED`, `ASSERTED` (no test shown), `DECISION` (a choice, not a refutation), `BLOCKED` (tooling or permission, not merit), `WITHDRAWN`. **Scope** = the exact restriction of the ruling and any loophole the authors name themselves.

Abbreviations: Q = target (rows are the odd primes below Q); "89 moduli" = odd primes 3..463 unless "491 set" (3..461 and 491); CRT line = the point (about 460.5 nats at 10^200) beyond which residues of N can no longer be prescribed; miniature = all even N < 10^9 coprime to 3..29, Q = 1,000, 256 successes among 157,947,020.
Map keys in brackets say where the detail is: [lead] [res-traj] [cons-traj] [others] [fleet] [uarch] [archip] [phd] [spy] [cons-narr] [cons-box] [l-phd] [l-search] [l-fleet] [rr1..rr4] [cover] [lean] [ideas].

---

## A. Verdicts about the target itself

**RO-1. Reaching 10% (g >= 213,070) at 200 digits with cover-plus-luck on the remaining units.** *Research, Lean, lead, consultant, spy.* One success per e^39.3 members (1,609 rows on the first 89 primes) against a budget of e^30.75 full-weight members: 50,749 fleet-days or 400,099 card-days per expected crossing; "about 5,600 times the remaining budget" (23 Nov), "about 4,900 times more tests", "8.4 nats"; spy's version 38.7 against 31 nats = e^7.7 = x2,200; P = 0.007% (170k design) to 0.03% (213k design). **COST**, from the row model that is validated at low thresholds only. **Scope:** N < 10^200, one class on each of 88-89 smallest primes, present engine, about 7,000 CU, independence of rows (P-2). Authors' own exits: "either a way to find numbers aligned with the primes above 463 without scoring them one by one, or about 4,900 times more tests"; spy: change scope/size, buy compute, or a new mechanism. [lead][rr1][cover][spy]

**RO-2. Reaching 20% (426,140) by any mechanism on the two 100-idea lists.** *Research + Lean.* E near 80 (e^87 today, extrapolated); even a perfect search to sieve depth 10^8 needs e^44 tests, e^13 times the budget; "out of reach ... by more than 20 nats even for an oracle". **COST** (the ledger calls the conclusion "a judgement"). **Scope:** 200 digits, budget e^30.75, the mechanisms on the lists. [rr1][cover][l-search]

**RO-3. A perfect search as a route beyond about 16%.** *Research.* Ordering all N < 10^200 by rows left at depth 10^8 would reach 343,000 (16.1%) on the budget. **COST** (tilt sampler, rows treated as independent beyond 20,000-50,000). **Scope:** budget e^30.75; fair-sample assumption (P-9); deeper residues (10^12) "would give more ... but nobody can sieve them" (ASSERTED). [rr1]

**RO-4. Aiming the fleet at the 213,070 design (or 180k / 190k / 200k designs).** *Lead, on research's design menu.* Raises P(>=213,070) from 7.0e-5 to 2.9e-4 and lowers the expected final record from 175,934 to 169,988; "raises the chance of that threshold by a factor of two to four and no more ... and pays 3,000 to 6,000 in expected record". **COST + DECISION.** **Scope:** objective = expected final record (P-21); 8.0 days at 52M members/s; the model assumes the sieve is half the work (SIEVE = 0.5); readers could not rerun it. Offered to the user three times, never answered. A mixed option was priced: each 10% of the fleet on that design adds 0.0016 points of chance. [lead][cover][cons-box]

**RO-5. Hidden slack in the luck model (hits running further than predicted; "frailty").** *Research.* 356 hits against 366.5 expected at Q = 40,000-75,000; 1,223 hits survived 41.0 rows beyond Q against 40.8; hazard flat at 0.0349. **MEASURED** at low thresholds, 200 digits. **Scope:** no design hit exists at Q = 170,000; the Q = 75,000 run alone read 56.2 against 40.8 (1.38 +/- 0.22); July campaign 3 ran 0.4 nats above theory; the fixed-gap game found 5 hits where 12.3 were expected (2%). Lean: "any dependence is a lever". [cover][lead][l-phd][res-traj]

---

## B. Better covers on the campaign's moduli ("Door 1")

**RO-6. Better covers as the route to 10%.** *Research.* At Q = 213,070 (19,050 rows): best cover 1,609; free-energy floor 1,554 (both starts agree to 0.5 up to beta 1.07) to 1,596 (beta 1.65); recursion 1,584; needed 1,470 rows for a 1% chance, 1,375 for 10%, 1,295 for even odds. "Better covers are not a way to 10%." **MEASURED** (two starts, 300,000 sweeps) + heuristic recursion; no certified floor exists at this Q. **Scope:** class vectors on the 89 smallest odd primes, one class each, unweighted rows, 0.0243 nats a row, "the fleet as it is", "the days that remain". Named loophole: "unless the equilibrium at that temperature is dominated by covers that neither start reaches"; "Not a proof: blind to covers no start reaches." [rr2][rr3][res-traj]

**RO-7. Covers with fewer than about 1,214 rows at Q = 170,000 (best known 1,248; 1,245 on the 491 set).** *Research; uarch for the certified part.* Two 10^6-sweep runs agree within 0.4 up to beta = 1.31 (floor 1,214; 34 rows = 0.83 nat = "a factor 2.3 at the very most"); the cold end (1,247-1,248, e^4.0 covers at 1,248, 186 found) comes from the best-cover start only. **MEASURED**; the only theorem is the exhaustive floor **777** rows (fix the 10 smallest moduli every way, fullest-class bound on the rest; one implementation), which "still allows about 11 nats"; an LP floor of 1,170 holds only with the best cover's 22 small classes fixed (LP value "unverified"). **Scope:** moduli 3..463 only (never run on the 491 set); cold-end statements are "about the family of the best cover and about every family the warm temperatures feed into it". The words "under every cover" in the summaries should read "measured" (consultant). [rr2][uarch][l-search][cons-narr]

**RO-8. Better covers on the fleet's weighted (landing-aware) measure.** *Research.* 491 set: both starts agree on a floor of 1,264 (beta 1.19) and 1,277 (beta 1.31) weighted rows; best cover 1,308.67; "nothing below 1,308.67 was seen from either side". **MEASURED.** **Scope:** the interval 1,277 to 1,308.67 is "not seen", not excluded; research values one or two weighted rows at +100 to +250 expected record. [res-traj][rr2]

**RO-9. A cover family better than family B.** *Research + contractor.* Thirteen families taken to the bottom (300,000 sweeps inside a frame, three seeds give the same cover): B 1,308.67, then 1,309.94, 1,310.48, 1,313.20 ... 1,318.19; of 25 random-start runs six ended in B, nineteen at 1,310.14 or worse; closest family worth 176,055 against 176,341. **MEASURED.** **Scope:** a frame = classes on the six smallest moduli; all candidates share 3:2 5:3 7:5; candidates came from the best 1,200 of 92,160 frames by a 10,000-sweep score that research calls "a coarse guide and no more" (20,000-sweep values sit 6-8 rows above bottoms; a frame third in the final table was not in the thirty best scores); frames ranked 1,201-2,000 were dropped unfinished ("the family question is settled well enough"); a million-sweep unrestricted run ended at 1,309.36 in a family nobody identified; B itself was "a lucky find", reached by one random start in four, and in two of three long runs "was not visited at the cold end at all". Authors: "What is not excluded is a family that none of these routes reaches." [cover][res-traj][others]

**RO-10. A rare "ordered" cover far below the plateau (brainstorm idea 2: k <= 1,500 at 213,070).** *Research + Lean.* The tempering entropy S(k) reaches zero within a few rows of the best cover (0.62 of the random mean at Q = 122,000, 0.71 at 213,070); exact agreement where enumeration is possible (13 moduli, Q = 10,007: min 186; 9 moduli, 429 rows: min 67 by 18 of 1,021,870,080 vectors). **MEASURED**; authors: "a heuristic certificate ... not a proof"; Lean: "I cannot prove k > 1,500 at full size (every bound I have is vacuous)". **Scope:** equilibrium of the sampler down to beta about 4; at 88 moduli "the cold end of the sampler is not fully mixed"; the random-start entropy vanishes about ten rows too early. [cover][lean][ideas]

**RO-11. PRECEDENT (a negative verdict that fell): "greedy's 867 rows at Q = 122,000 are at or near the optimum".** *July WP9.* Backed by 41 exact CP-SAT windows, 21 of 22 LP-certified, BP decimation at 874, exact endgame blocks. **OVERTURNED** in November by tempering: 850-851 rows (0.4 nats), found by two sessions independently. [phd][cons-narr]

**RO-12. Local search, annealing, coordinate ascent, random restarts, iterated local search, greedy + descent as cover optimisers.** *July WP8/WP9; uarch; student.* Random-start ascents 954-981 against 867; ILS cannot improve 1,010 and stalls at 1,103 from random (400 digits); greedy + descent 1,309 against 1,248 at the campaign point (+4.9%), 258 against 229 at Q = 48,000. **MEASURED.** **Scope:** those optimisers; tempering is the benchmark. [phd][uarch][archip]

**RO-13. Belief propagation / survey-style decimation.** *July.* 874 / 887 / 922; naive Bethe gives 35. **MEASURED**, one instance, replica-symmetric only; 1RSB / survey propagation "not run". [phd]

**RO-14. LP relaxation or LP duals as an optimality certificate.** *July.* Fractional coverage is 100.00% (sum 1/(r-1) = 1.86 > 1): "the entire exponent E ... is an integrality/rounding gap". **MEASURED** (HiGHS). **Scope:** plain set-cover LP; Sherali-Adams / Lasserre lifts "not runnable" (10^19.2 monomials at level 5). [phd]

**RO-15. Sieve-theoretic floors for the cover (large sieve, linear sieve, under GRH).** *WP10; consultant.* Large sieve gives |U| <= 318,514 against 11,474 primes (vacuous, wrong direction); linear sieve negative; only level D = Q (beyond Elliott-Halberstam) certifies 142-282 residuals against 827-867. **MEASURED/computed** at record parameters. [phd][l-fleet]

**RO-16. A closed formula for the cover optimum; the first-moment (annealed) count.** *Research.* Mean-field gives 0.79-0.84 of the truth (682 against 851); first moment predicts 790 rows at 170,000 (found 1,248) and put the end of complete covers at 32,300 (found about 16,000); "no sign of approaching it". **MEASURED.** [cover][rr2]

**RO-17. Heat-bath tempering as a stronger optimiser.** *uarch.* 1,025 against 1,027 at equal CPU at 400 digits; does not move a seeded 1,183-row cover in 6,000 sweeps. **MEASURED** over minutes at 131 and 159 moduli. **Scope:** the opposite holds at 629 moduli (student: 2,829 against 3,059); "heat-bath move inside replica exchange" was suggested as worth "10-20 rows at every size" and not tried at the 200-digit point; the student's `heatbath_pt` is untuned. [uarch][others][archip]

**RO-18. Other cover optimisers: survey propagation, population annealing, cluster / pair / triple moves, crossover, renormalised covers mod 30030, discrepancy rounding, CP-SAT / ILP, quantum annealing (brainstorm 47-49, 76, 77, 92; Lean ideas 42, 43).** *Lean + research.* "nothing to gain unless 2 is true"; exact polish of the last 15 moduli "feasible and worth a few rows" (0.05 nats), never done. **ASSERTED**, conditional on RO-10. **Scope:** CP-SAT/ILP "never got tried seriously" at scale; uarch's MILP test was dropped because `pip install highspy` was blocked (**BLOCKED**, not merit). [cover][ideas][uarch]

**RO-19. AlphaEvolve-evolved cover optimisers.** *July.* 0.9 digits under warm start; "did not beat the existing one". **MEASURED** (threshold game, evolved move sets only). [phd][l-phd]

**RO-20. Raising the certified floor (j = 12), D(36), a further D(89) walk.** *uarch, by agreement with research.* Two more fixed moduli cost x42 then x163 in nodes; nodes x4 per 2,000 off Y. **COST**; stopped by choice. **Scope:** this "fullest-class" cut, which "ignores that the classes of large moduli overlap" and loses 4-5 orders of magnitude between 30 and 89 moduli; never run for other moduli sets or Q. [uarch][rr2]

**RO-21. Local rearrangement of the 15,907 complete cover.** *uarch.* Large-neighbourhood search freeing up to 32 of 89 moduli finds nothing: "locally rigid". **MEASURED.** **Scope:** only steps with |U| <= 255; authors: "seems to need the tight small moduli to move (3 alone strikes 241 primes ... that nothing else strikes)". [uarch]

**RO-22. Structured class choices: crystals (class alpha/beta on every modulus) and mixed crystals (one constant c on every modulus above z).** *Research + Lean.* Best crystal 2,156 rows at 213,070; mixed 2,118 / 2,021 / 1,986 / 1,943 for z = 13 / 31 / 61 / 101 against 1,623-1,634 free. **MEASURED.** **Scope:** |alpha| <= 40, beta <= 12; one constant |c| <= 150, z <= 101, coordinate descent from three starts. [cover][lean]

**RO-23. "All classes 1" on every modulus up to x/ln x.** *Consultant.* Leaves 1.09-1.18 times the random count. **MEASURED** (x = 10^3 to 10^5). The author later called it "the wrong structured family". [cons-narr]

**RO-24. The Erdős-Rankin common-integer block as a cover at computable sizes.** *Consultant, Lean, research.* (a) x = 10^4, complete-cover game: block + greedy small moduli + greedy top reaches 0.39-0.48·x·ln²x against 0.71 for plain greedy; block alone leaves 0.93 / 0.86 / 0.72 / 0.57 of random at x = 10^4 / 10^5 / 10^6 / 3.75·10^6 (consultant) or 0.98 at 10^4 (Lean), half only near 10^25. (b) Campaign point, 25 Nov 13:33-13:45Z: block-type covers on the 89 moduli leave 1,342-1,449 rows at Q = 170,000 against 1,248, "no better than random blocks of the same shape"; Q = 213,070 was still running. **MEASURED.** **Scope:** (a) one size, one block (z, y], N1 = best of 200 consecutive integers, greedy completion, no tempering. (b) four block shapes ((17|23|41, 113] and (41, 199]); N1 = best of about 3,000 random integers in [Q, 50Q); remaining moduli tempered 40,000 sweeps from scratch; plain rows; not seeded into the best cover; not on the weighted measure. Not tested: a block-type start for tempering at the 89-moduli end of complete covers (consultant suggested it, research "will not spend cores on it"); blocks at several scales or different integers per block ("likely" better per the consultant); the block at 491 / 629 moduli (asserted "no use at your size"); "the block turned from a cover into an order" (on research's untested list). Observation on record: common-integer blocks have about 5x the spread of random blocks (sd 147 against 27). [cons-narr][res-traj][rr3][others]

**RO-25. Primorial-shift progressions N = q0 + k·P#.** *July.* 1,468 residuals against about 770. **MEASURED**, one size (161-digit modulus). [ideas]

**RO-26. Greedy with moduli in decreasing order.** 0.10 falling to 0.03 of x·ln²x. **MEASURED.** [cons-narr]

**RO-27. One cover good at several thresholds (Pareto family).** 1,028-1,033 against 1,007 rows (0.5 nats). **MEASURED.** [cover]

**RO-28. Soft-threshold / taper / overshoot-aware cover design (brainstorm 8; Lean ideas 49, 99).** First ruled "no gain" ("rows above Q are uncovered at the random rate whatever the taper"), then **WITHDRAWN**: rows above Q differ by family (about 30 rows in 170-190k) and are worth about +1,000 expected record. What remains ruled: a weighted cap adds nothing within a family; weighted tempering finds nothing better than B (see RO-9). [cover]

**RO-29. NOT A RULING, an opening on record: the independent-cell maximum as a ceiling for what the top moduli can strike.** Refuted by one tempered cover (167 moduli): its 56 largest moduli strike 1.38 times the fullest of independent cells; real covers strike 31-56% more than the recursion says at the last moduli. [archip][rr3]

---

## C. Changing the modulus set or the shape of the design

**RO-30. More moduli under the cap (a 90th and beyond; adding 443, 449, 457).** *Research, Lean, uarch.* Two more moduli buy 14 rows = 0.25 nats for 5.3 digits ("+0.1 nat each"); 443/449/457 give 831 rows at Q = 122,000 but about 60 members a vector; with a 90th modulus a vector holds 3.6·10^4 members and the per-vector fixed sieve cost dominates (120-800 ns a member against 24). **MEASURED** at Q = 122,000 (86/88/90 moduli) + **COST** for the rest; no 90-modulus design was ever measured at 170,000. **Scope:** a vector must hold at least 2^24 members (89th prime <= 590); the present sieve's per-vector fixed cost (about 30 ms "with an ideal of ~3-5 ms"). Research's later line "more moduli with shorter progressions ... already collected by the fleet's selection on survivor counts" is **ARGUED**, no measurement. Two prices for one more modulus coexist: "+7 rows, x1.18" and "~14 rows (+25%)". [cover][ideas][res-traj]

**RO-31. A different modulus set.** *Research + contractor.* Screening the 89th prime from 463 to 900: 491 best (1,245 rows; 557: 1,246; 463: 1,248); best weighted rows per last prime 463..587: 491 at 1,308.7, 557 at 1,309.7; "the campaign's allocation is optimal up to the 0.2 nats we measured". **MEASURED** for one swap of the last prime. **Scope:** the first 88 odd primes held fixed; no search over non-initial sets at 200 digits, although the 2,692-digit megagap used "a selected set up to 12,277" (7.3% better than greedy on the same moduli) and the 150-digit record used 68 moduli up to 613; the student's proposal of moduli selection got no answer; the spy's item (swap 461 or 457 for 499 / 503 / 509) is untested; the only swap ever tried beat its prediction (+6% predicted, +7 to +8.5% measured). [cover][others][spy]

**RO-32. Moduli chosen by fullness; one larger prime with a freak class (brainstorm 3, 19; Lean 44, 59).** Over every prime in (683, 10^6) the fullest class of the 1,634 uncovered rows holds 9 rows (at 743); "Not 40". **MEASURED**, one cover. [lean][cover]

**RO-33. Several allowed classes per modulus / set-valued conditioning.** *July FRONTIER; Lean.* Gains 1-2.8 nats nominally, about 0.2 once the admissible set must be an arithmetic progression; a prime "costs ln r of the 460.5 nats whether one class is allowed or many". **MEASURED** inside an exact product model at 100-150 digits (threshold game) + **LEAN** counting bound (`card_residues_in_le`). **Scope:** no 200-digit figure; "the classic cover is the unique design ... free to enumerate" is flagged "conjectural" by the ledger; Lean states the claim is FALSE "for information" (benefit is concave: "a little from every prime beats everything from the first 88"). [ideas][l-search][cover][lean]

**RO-34. Zero classes (r | N).** A zero class covers at most one row. **LEAN.** [lean]

**RO-35. Prime-power, composite or non-coprime moduli.** They kill nothing a prime factor does not kill. **LEAN** (kills only, no cost statement). [lean][phd]

**RO-36. Oversized covers with a small CRT representative (WP3; ISD, Stern, BJMM, Wagner k-tree, BKZ/CVP, Coppersmith, partial-fraction subset sum; brainstorm 36-42; Lean 47, 48; IDEAS100 C1).** Modular subset sum at density 1.026 (lattices need < 0.94; Wagner 2^938); GSS radius 5.2x short; net 0.2-0.4 nats at 200 digits. **COST** + heuristic first-moment "barrier" (after a retracted "open window"); toy LLL only at 61 positions. **Scope / loophole (authors):** "CRT list-recovery beyond the Johnson radius for structured, solution-abundant instances" and "density-1 subset-sum with 2^82 planted solutions" are named open problems; the BKZ-20 against MITM toy test was never run; the prize if it could be done: E = 34.5 with 200 moduli (25.75 with no size limit) against 39.2. [phd][ideas][cover]

**RO-37. Joint representative with an oversize modulus (joint.py).** It works (24.3 digits of modulus cancelled; a 211-digit-modulus cover with E = 18.09, "better ... than the record's own") but costs 10 to 10^4 times more per candidate. **MEASURED**, July CPU code. [l-search]

**RO-38. One member per vector at the full modulus budget (Lean idea 46).** "with one member a vector there is no progression to sieve". **ARGUED**; assumes selection information can only come from sieving a progression. [cover]

**RO-39. A wheel on k: keep only the best classes of k modulo non-cover primes (Lean 29, 55, 56); "wheel and list merges" (ladder rung 6).** Best 5% of classes mod 443 gives +9% success (+0.1 nat) for one prime, "then negative" because setup is paid per class; rung 6 costed at 0.1-0.4 nats. **COST**; "not started". [cover][rr4]

**RO-40. Tree / beam / depth-first search over the residues of medium primes; a tree over k mod 463, 467, ...; Gibbs or tempering over k (Lean 30, 31).** "worth about +10% each; they amount to adding one more prime"; "after 3.6 primes k is determined"; "random search with extra cost". **ARGUED.** [lead][cover]

**RO-41. Pinning the residues of further primes by enumeration (covers beyond the CRT line).** In the miniature a prime beyond the line buys 0.44-3.15 nats (10 successes) for an overhead of 6.5 to 10^73 residue vectors; for complete covers it was done at 92 and 93 primes (20.5% and 0.03% of covers land below 10^200) and failed at 94 (one in 1.25 million). **MEASURED.** **Scope:** enumeration as the pinning method. [rr1][rr2]

**RO-42. One long progression instead of many short covers (fixed-gap game, 124 moduli).** 0.94 expected hits in its whole range; 1.5x worse per core-second. **MEASURED.** [uarch]

---

## D. Finding good N without scoring every member (problem P′)

**RO-43. NOT RULED OUT: a sublinear search.** Consultant's map: "No sublinear algorithm is known and none is ruled out"; research: "Nothing here proves that no algorithm exists"; "a lower bound against every algorithm on that family [rows = primes] is out of reach of any known proof technique"; "The instance is special (all lists are images of one set of rows), and that is the only place left to look." Until 25 Nov 12:54Z only three mechanisms had been scored on the miniature (RO-41, RO-50, RO-56). [rr1][cons-narr][res-traj]

**RO-44. Lattice decoding / CRT with errors or lists (Goldreich-Ron-Sudan, Boneh, Guruswami-Sahai-Sudan, Coppersmith, Bleichenbacher-Nguyen).** Needs agreement at least 3.88x typical for K = 2^32; for the 580 primes 467-5,000 with one-class lists in a population of e^83 the best agreement that exists is about 22 against a radius of 78; in list form only singleton lists (= the cover) are usable. **LEAN arithmetic under hypotheses "quoted from the literature"** + one computed instance + a toy (61 positions). Research, 25 Nov: "ruled out by cost arithmetic at 200 digits and ... not run on the miniature as algorithms". **Scope:** the named Johnson-radius decoders; the task "find every t" for the product of all rows; needs "a solution is expected". Being run as an algorithm on the miniature by Lean since 13:40Z (no result yet). [lean][rr1][res-traj]

**RO-45. Meet in the middle, generalised birthday (Wagner), list merges.** Pays only when H <= 2(F - C); with F = 460, C about 425 and memory e^21 "extends the reach by one prime" (0.2 nats); "at most about 5 nats ... even with a perfect solver". **LEAN** for two lists (cost linear in list length, average yield); the k-list extension is prose; rest **COST**. Being run on the miniature (Lean). [lean][rr1]

**RO-46. Locality-sensitive hashing / bucketing on N = u + v.** At best K^0.94 (two derivations: 0.88 and 0.99). **ARGUED**; rests on the class lists being "random-looking"; "no lower-bound proof". Being run on the miniature (Lean). [rr1]

**RO-47. Lists of classes on primes above Q (intervals, progressions, the row set itself).** A nat of constraint buys at most 0.207 rows = 0.005 nats, six times less than a covering prime. **LEAN.** **Scope:** a product of lists, one prime at a time, s >= Q = 213,070, at most 1,609 rows; for primes between 463 and Q (classes of up to 9 rows) only the general inequality exists, never instantiated. Authors' loophole: the prize "is collected only by members that are good in total without being constrained prime by prime". [lean][rr1]

**RO-48. The interval structure of the lists for primes above Q with lattice simultaneous approximation.** "a hundred to a thousand times less per nat than the last prime of the cover". **ARGUED** with numbers. [rr1]

**RO-49. Black-box (oracle) search.** m questions reach the fraction m·g/K. **LEAN** in the query model. Authors: "The real instance is not a black box: every class ... is computable, nothing is hidden." [lean]

**RO-50. A fast general algorithm for covers or lists treated as arbitrary data.** Contains SAT (arbitrary rows; every modulus larger than the number of rows); NP-complete with two classes per modulus (Manders-Adleman). **LEAN / literature**, worst case. Authors: for rows = primes "nothing is proved here, and nothing of the kind is known". [lean][rr1]

**RO-51. Local moves, hill climbing, annealing, splitting, importance sampling, evolution, iterative decoding over N beyond the CRT line (brainstorm 46, 50, 55, 99).** Two N below X in the same class mod M and mod sieve primes T need M·∏T < X: at most three sieve primes kept (27 of 1,634 rows); miniature: rows left for N and N + 2·3···23 correlate at -0.029 over 118 million pairs; "a random-energy model". **LEAN** for exact residue-preserving moves that keep the same M; the random-energy picture is **MEASURED in the miniature only** (one move, depth 200). [lean][rr1]

**RO-52. A smarter choice of members inside the present progressions.** "A perfect, free method ... would gain at most 5.3 nats"; best of 2^32 = 7.6 nats over random. **LEAN identity for an exactly Gaussian count**; the extreme-value step is heuristic; inputs "crude". **Scope:** one progression of K members at one sieve depth; the same model gives 17.6 nats for e^100 members "i.e. a cover that has given up 78 ... nats of modulus"; the tail is measured only to 3 sd on 131,072 members of one vector. [lean][cover]

**RO-53. Any score better than "rows left" (learned scores, ML, proxies, per-vector quality, near-miss mining; brainstorm 51, 54, 56-60, 75; Lean 24, 25, 39, 94; IDEAS100 C5).** LightGBM with 133 residue features loses by 0.00012 nats; vectors with equal rows differ by 0.0002 nats. **MEASURED** near 10^15 and 10^18 at sieve depths 97 and 997; **LEAN** "count is sufficient" inside the independence model. **Scope:** features are functions of the same residues; not tested at 200 digits. First out-of-grammar score on the miniature (consultant, 13:44Z; size of N + rows at depth 23): -0.57 to +0.88 nats, all below one nat. [cons-box][cover][cons-traj]

**RO-54. Reaching the ideal N by enumerating covers best-first.** Ideal N are 10.6 sd (depth 1,000) to 17.5 sd (depth 20,000) below the members of the best cover; they have about 1,950 rows at depth 463 against 1,609; in the miniature 1 of the 62 best numbers lies in the best covers. **MEASURED.** [rr1]

**RO-55. The tilted / ideal distribution as a way to search.** The explicit tilt family reaches E = 29.0 (primes to 10^7) against 39.5, but "It is not a way to search": "one nat of work per nat of information"; a 2-list merge recovers about 20 nats = three moduli = 0.5 nats. **ASSERTED** ("I know no method"; "No algorithm is known"). This is the single assertion the verdict rests on (P-8). [cover][lean]

**RO-56. Sharing row values or work between candidates: windows, shift-invariant covers, combs, convolution of P + Q (brainstorm 26, 27, 71; Lean 98).** Two candidates sharing a row value agree only on moduli of product below g; one vector optimised for N and N + 30030 has 1,772 / 1,826 rows (E 42.9 / 44.2 against 39.5). **LEAN + MEASURED** (700 sweeps, one shift family). **Scope:** identical integers N - q = N′ - q′; "says nothing about sharing partial computations between different integers"; Lean: "'loses e^10' is a little strong; 'loses e^7 or more' is safe". [lean][cover]

**RO-57. Neighbours of a known success, row inheritance, clusters ("archipelagos", "islands").** A neighbour at distance 30,030 inherits about 6,000 of 19,050 rows but keeps about 1,600 at risk, "the same as a fresh member"; P = 4·10^-15 over 7,000 shifts. The effect is real: 4 pairs of successes closer than Q in the miniature against 0.09 expected; near 10^18, N + 30 is 18 times likelier to be big, and "Knowing six neighbours' outcomes adds about as much as sieving 65 times deeper". **COUNTED + LEAN** (`shared_row_value`). **Scope:** "cannot be sieved in bulk" is asserted; "inheritance turned into a search" is on research's untested list; the consultant expects about 0.02 nats (not yet scored). [rr1][cons-box][res-traj]

**RO-58. The "stretch" method: decide consecutive N by look-ups in a shared prime map.** About 6,000 operations per N against 20,000, but success e^-46.6 without a cover against 0.17·e^-30.0: "a million times worse per operation". **COST.** **Scope:** compares no cover with the full cover; the only intermediate is one sentence ("A cover on the primes up to 13 ... gains a nat or two of the sixteen"); the low-end interval sieve ("an estimated 7 cycles each") was never built. Research calls this "the only place where prime rows are cheaper than arbitrary ones". [rr1][cover]

**RO-59. A cheap estimate of a member's number of prime rows.** "capped at ln(cost per member / cost of the estimator) = ln(11/2) = 1.7 nats, because every member must at least be touched". **ARGUED** (the premise is the sublinear question itself). [cover]

**RO-60. Rejecting members part-way through the sieve; two-stage selection; pruning after the small-prime stage.** Research (24 Nov): "does not fit a sieve that strides over arithmetic progressions" (**ARGUED**, no measurement); Lean idea 22: "NO SAVING BY ITSELF" (**ARGUED**); pruning after the cheap stage "+3%", not built; on record: "90% of the final best 3% are in the best 15% after primes <= 1e6" (measured). The spy's model of a deeper two-stage score (x1.1 to x1.97 depending on an unmeasured cost) is unverified. [res-traj][cover][fleet][spy]

**RO-61. A rule that skips candidates when generating record holders (A025018).** "What it cannot do is skip"; five simple rules each broken. **ARGUED** + small experiments. [lean]

**RO-62. The Lean session's own tries: lattices of moves, additive and multiplicative splittings of t, tree search with bounds, polynomial parametrisations, row sharing by convolution.** "could not". **ASSERTED** without detail in any map. [rr1]

---

## E. A third way to make rows composite

**RO-63. Planted-divisor certificate schemes other than covering (July "Closure Theorem", Door 3).** 13,661 enumerated + 41 evolved schema instances, zero passes, best 53x too expensive (2.2 nats an offset against 0.041). **PAPER at draft rigour, conditional on H1 and H2**, plus a sweep. **Scope:** a grammar of seven families chosen by the authors (Congruence, PolyImage deg <= 4, ExpFamily, MultiPoly deg <= 2 and v <= 3, NormForm disc <= 10^4, Cyclotomic n <= 200, Compose depth <= 2); the code is narrower (PolyImage only a·m^k - c; NormForm and binary-quadratic verdicts assigned by rule with no computation; the evolver could only vary parameters); the bar is covering's average price, and on the marginal price one family was a near tie (1.02 against 1.0 nats a kill at 10^100); hybrids "only mentioned, not priced". Authors: "A mechanism outside L ... is not excluded, and nobody knows of one." WP7's three conditions for a real mechanism: far more than √Q offsets, o(ln r) nats each, invisible in bulk statistics ("activated only by special N"). [phd][l-phd]

**RO-64. Polynomial value-set identities (N = f(u), rows f(c)).** At most √Q + 1 rows (350 at Q = 122,000) for half of ln X. **LEAN.** **Scope:** one univariate f with f(c) >= c². [lean][phd]

**RO-65. Exponent families N = j·a^n + c (Sierpiński-Riesel).** 1,048 offsets cost 1,151 nats against 460; at most 419 affordable. **COST** (exact purchase plan) for a in {2, 3, 5, 7}, primes s < 10^5. Residue kept by the authors: "shared sieve state along n ... noted for the engine backlog". [phd]

**RO-66. Norm forms, cyclotomic / Aurifeuillian splittings, several quadratic forms, divisibility sequences, perfect powers, Lucas terms (brainstorm 11-16, 18, 20).** One row per identity or O(√Q) rows. **LEAN** for powers and doubling sequences; **literature cited, not proved** for quadratic forms (Siegel / Bennett) and norm forms; rule-in-code for NormForm. [lean][cover][phd]

**RO-67. Multivariate product identities.** v < d: at most 13 offsets per candidate against about 18,000; v >= d ("window-dense"): isolation and orbit accounting, 10^145 trials. **PAPER, first-moment, "[P-shaped]"**; equidistribution of form values assumed; fails as worded for total degree >= 38. On record: products of two binary quadratic forms represent about 9,300 of 17,983 prime offsets below 200,000. [phd]

**RO-68. Compositions of two identity families.** N = m² - c1 = m′² - c2 forces m <= |c1 - c2|. **PAPER**, for that pair. [phd]

**RO-69. A mechanism made of large divisors (brainstorm 100).** Divisors >= Q serve one row each; 38 pairwise coprime divisors >= 213,070 determine N < 10^200. **LEAN**, for independently prescribed divisors. Verdict in the source: "NOT BROKEN, NOT FULLY PROVED"; loophole named: the divisors must be "dependent on each other, as a polynomial identity does"; "Non-polynomial parametrisations I can neither exclude nor imagine." [lean][cover]

**RO-70. An integer counterpart of the function-field parity mechanism (Liouville function of N - q; genus theory / class-group 2-rank; Jacobi symbols).** "no known formula short of factoring"; parity problem. **ARGUED.** "the transfer needs new mathematics, and the programme does not assume it will be found"; the Lean source "contains no statement transferring this to the integers and no statement that it cannot be". In the toy it is a proved third mechanism worth 4.5x. [rr1][lean]

**RO-71. Extracted (per-instance) divisor certificates.** "factoring-equivalent". **ASSERTED**; no reduction written. [phd]

**RO-72. Planting composites by congruences on k; "k-side covers"; mini-covers on k.** Forcing s | N - q costs ln s >= 6.1 nats to save 0.06; "selects a sub-progression the sieve already identifies". **COST / one sentence.** [ideas][phd]

**RO-73. Using prime gaps: parking rows in a gap, catalogued gaps, N = p + g, prime-gap transfer (brainstorm 21, 22; Lean 95, 96).** 34 nats to save 4.7; a gap of 18,000 frees about 150 rows (3.6 nats) but then E = 54 against 39. **COST**; assumes a gap-anchored N cannot also carry an optimised cover. [cover][lean]

**RO-74. Parity mod 4, 8; "function-field mirror" moduli.** **LEAN** (nothing) / "TRUE AND USELESS". [cover]

**RO-75. RH / GRH as a lever; the remark.pdf Lean archive as a source of technique.** Shortfall 10^95.9-10^97.1 at 200 digits; archive: no covering, decoding or integer-parity content found. **Computed / ASSERTED from a name-level scan** (0.76% compiled; core read at statement level). Loophole (consultant): "A technique hiding under unfamiliar names cannot be excluded"; prior "low but nonzero"; "Stepanov = Coppersmith" was judged "on the note's description and a sample". [phd][l-fleet][cons-traj]

---

## F. Exploiting the luck model

**RO-76. Pair correlations, collision-rich uncovered sets, singular-series design, variance-widening "anti-covers" (brainstorm 5, 64; IDEAS100 B8/C8; SoK 7.1).** Pair term -0.032 nats, varying 0.0002 nats over twelve near-optimal covers; pairs congruent mod a non-cover prime below 5,000 are 0.80 of naive for covers and random vectors alike; at most +0.2 nats on offer. **MEASURED.** **Scope:** pairs only; near-optimal covers on the same 88 moduli; SoK still lists the deliberate-design version as "open ... modest constant"; a second file reports 0.8523. [cover][ideas]

**RO-77. Stopping rules (abandon a member early); choosing which row to test first.** Never abandoning is optimal; order is irrelevant with equal p and c. **LEAN**, inside the independence model with equal test cost. [lean]

**RO-78. Maier-matrix positioning, Chebyshev bias (10^-70), Linnik emptiness, Siegel zero, prime-poor parametrisations N0 + M·t², admissible-tuple obstructions, Selberg weights (brainstorm 61-68; IDEAS100 B4-B7).** **ASSERTED / research's own counts** "Agreed as you have them". [cover][ideas]

**RO-79. Harvesting near-misses as a shortcut (July); breadth-first shallow campaigns.** Beating the incumbent without a full hit was "only e^0.29 ... likelier" then. **COST** at July parameters. (Since 23 Nov both records are near-misses of a higher design.) [phd]

---

## G. Cheaper tests (H2 and around it)

**RO-80. NOT RULED OUT: a compositeness detector cheaper than one modular exponentiation (H2).** "Open in both directions"; "no lower bound is known in any realistic model"; opinion on 25 Nov: "very likely true and can't be proved". Value if false: at most ln(1/f) nats. [phd][others]

**RO-81. One exponentiation for all rows of a member.** The identity is a theorem (`fermat_from_product`); the product-modulus + remainder-tree scheme costs b·M(S·b) >= S·b·M(b). **PAPER for that scheme**; "a product modulus costs 8x more" (ASSERTED). "Any other sharing remains open, and I know of no candidate." [lean][others]

**RO-82. Jacobi symbol, gcd, residues mod small primes as cheap filters after the sieve.** No signal. **PAPER** ([P] in the H2 note). [others]

**RO-83. Product-tree trial division / batch gcd to 2^40 (brainstorm 32; Lean 14, 23).** More limb products per row than the Fermat test; removes 20% of rows left. **COST.** The batch remainder-tree versions (IDEAS100 A7, C3) are "never tried". [cover][ideas]

**RO-84. Shared or incremental exponentiation across members k; early exit for composites; "lazy deeper sieving and batched Fermat tests".** **ASSERTED** (one-liners; uarch's note has no numbers). Brainstorm 29 (Fermat along a progression) and 30 (a group test for a prime in a set) were explicitly *not* ruled: "No method known". [ideas][others][cover]

**RO-85. Kernel arithmetic alternatives: 64-bit limbs, FP64 / FP32, Karatsuba, tensor cores, RNS, FPGA / ASIC, fewer-multiplication variants, extra accumulators.** Kernel "at its multiplier floor" (five variants within 1.1%). **MEASURED** for most; estimates for tensor cores and ASIC. "Not tried": exponent prefix (+0.6%), shifts as adds (+1%), trimming 223 non-multiply instructions (+3%). The production kernel already has a dedicated square, lazy reduction and 23 limbs of 29 bits. [fleet][ideas]

**RO-86. Running with unreliable arithmetic for speed.** Safe (theorem under a fault model); "I see 10%, not 2". [lean][cover]

---

## H. Engine, sieve and selection engineering

**RO-87. A deeper sieve.** B = 10^8 is the optimum: 2^28 -3%, 10^9 -31% (hits per test +28%); joint (B, f) re-optimisation gives at most +1.2%. **MEASURED** on the RTX staged kernel. **Scope:** the per-(row, prime) marking cost of this design; "a different design for primes above 2^25 ... Not built"; a model row says 3x the rate if a large-prime mark cost 0.0033 ns instead of 0.030. [fleet][cover]

**RO-88. A deep "head" (extra large-prime stage on the first 64 rows).** -8.4% tests, +0.7% batch time. **MEASURED** at f = 0.985; the estimated optimum (3·10^8, +1.2%) not run. [fleet]

**RO-89. Keep-fraction changes.** RTX stays at 0.985 (model optimum 0.9875-0.99 = +1.1%, "f is supply-bound"); L4 at 0.985 gave x0.9865 (predicted x1.13-1.15). **MEASURED.** [fleet]

**RO-90. Near-miss truncation (rank members by rows below the record).** x1.065 near-misses, x0.937 design hits: "A wash at best". **MEASURED on CPU counts + DECISION** (lead, 23 Nov, for 7 GPUs and 9.5 days). **Scope:** not revisited for the 5-GPU fleet; every record at Q = 170,000 so far is a near-miss and no design hit has occurred; a weighting of rows above the record "needs a second count: not built". [fleet][lead]

**RO-91. Covers with fewer rows below the record (family A).** Family B has about 20-30 fewer uncovered primes in 170-190k: +1,000 expected record; A/B test at Q = 60,000: mean g - Q 3,766 against 3,071 (4.7 s.e.). **MEASURED + model.** Reverses below about 0.35-0.5 expected design hits left. [cover]

**RO-92. A persistent (work-queue) Fermat kernel.** Alone -3.4%; beside the sieve +5% to +19% slower. **MEASURED** on RTX; untested on L4 / T4. [fleet]

**RO-93. Sieve and scheduling micro-items under the 1-2% bar** (survivor-list tail kernel, tail rule, control stream, rows2, race-free marking, pipeline on L4, more Fermat threads, equal priorities). **MEASURED**; "at the noise floor". The ruling covers the sieve third of a batch only. [fleet]

**RO-94. Running the 491 covers on L4 / T4.** At most +1.6% fleet-wide. **COST** (fleet's estimate). [lead]

**RO-95. ECC off (+1.3%); k beyond 2^32 on the GPU.** **DECISION** (lead's risk call; "not now"); untested. [lead]

---

## I. Compute

**RO-96. Volunteer or distributed compute.** **USER DECISION** ("No volunteer bs."). Priced: 1,000 cards = +5.8 nats (8% to 9.3%). [lead][cover]

**RO-97. Rented or spot GPUs, other providers, extra quotas.** **DECISION by the lead** (its widening of the user's sentence; "must not be raised again"); research: "the user's money". Priced: about $20 a day per RTX-equivalent; 10x the fleet = +2.3 nats = +0.5 points. [lead][ideas]

**RO-98. More small cards; filling a refused G4 slot with a less efficient card; A100.** "budget fixed"; per unit an L4 gives 0.64 (or 0.75) and a T4 0.50 (or 0.58) of a G4. **ARGUED + measured yields.** A T4 stopgap was also refused by the permission classifier (**BLOCKED**). [lead][others]

**RO-99. CPU cores on the main game.** At Q = 150,000 a hit "can almost never beat" the record; 230 cores = one RTX. **ARGUED / measured rate.** (The coder's local share and the G4 hosts' CPU drivers still run Q = 150,000 vectors; the CPU engine has no near-miss reporting.) [lead][others][fleet]

**RO-100. Quantum (Grover); ASIC / FPGA.** Crossover E* = 55 / 41 / 27; priced, not executed. **COST.** [phd]

**RO-101. NOT DECIDED: stopping the L4s and the T4 for unit efficiency (+6% to +11% expected hits).** Held by the lead until after the 25 Nov evening handover. [lead][res-traj]

---

## J. Scope, size and target choices

**RO-102. Moving the fleet to 225-240 digits for g >= 200,000.** 7.3% of that size's ceiling against 8.0%; "trades one record for another at no gain". **COST.** Kernels exist for 200 digits only. [res-traj][rr4]

**RO-103. Smaller N / closeness against the own-size ceiling (brainstorm 25; Lean 71-75).** "CLOSED BY THE USER" on 22 Nov (a session's gloss of "no baby steps"). **DECISION, now reopened:** research's model gives about 16-17% at 100 digits and 11% at 150 with the remaining units (UNVERIFIED; kernels for 332 and 498 bits do not exist); the lead is asking the user. [cover][res-traj]

**RO-104. Luck-free records (complete covers, BLS N - 1 certificates) under 10^200.** Complete covers end at 15,907 (89 primes) to 16,981 (93); "each extra covering prime buys about 43"; the N - 1 form "spends digits". **LEAN** for the values; **MEASURED** count for the end; exhaustive D(89) < 35,000. **Scope:** the "end near 16,000" is an end of the covers the counts see (P-14). [rr2][uarch]

**RO-105. g > 10^6 below 200 digits (E = 196.4); T(100,000) below 100 digits (9·10^5 GPU-years).** **COST**, single-class covers. [l-search][phd]

**RO-106. The fixed gap 200,000 below about 290-300 digits on CPUs; a cheapest size short of the luck-free size.** 78 CPU-hours a hit at 300 digits, 12,000 (gmpy2) at 260; "50 digits less cost a factor of 11 to 30". **COST + measured** at 300-400 digits. [rr4][uarch]

---

## K. Theory rulings (all about very large N)

**RO-107. WITHDRAWN limits of the cover depth.** D/(r·ln²r) -> 1.349, then [1.1, 1.349], then 1.1275 (withdrawn 25 Nov 10:20Z), then D <= 1.349·r·ln²r/ln ln r (withdrawn 11:45Z), and the consultant's "ratio tends to 0" (withdrawn after 20 minutes). Now: "no limit ... is known"; order open between c·r·ln²r·ln₃r/(ln₂r)² (paper) and r^(4+ε). [rr3][cons-narr]

**RO-108. FALSE: "small / frozen moduli can do no better than random classes".** "true of the model and false of the primes" (block on one common integer: 32.3% against 44.0% of rows at Q = 6·10^7). Consequence stated by the consultant: the count of typical covers and existence "are different things once structured families exist". [lean][cons-narr]

**RO-109. Pigeonhole / first-moment counting beyond the constant 1.349; a deletion or rainbow-matching route to the constant 2; a nibble at the top moduli.** Deletion keeps 9-11% (constant about 1.5); paper proof gives 1.3523; nibble "out of reach with these inputs". **ARGUED / MEASURED / PAPER.** (The block then gave every constant by another device.) [cons-narr][archip]

**RO-110. Refinements of the counting recursion** (finite-class, binomial closure, along-cover dispersion, exact pair sum). Each is worse against the counts. **MEASURED.** The exact treatment of frozen levels "has not been built". [res-traj][rr3]

**RO-111. Independent-balls / Poisson models of survivors in classes.** Pairs 0.38-0.87 of independent. **MEASURED** to 10^6. [archip]

**RO-112. BLOCKED, not refuted:** a written proof beyond 1.349 in the Lean session ("stopped three times ... by a safety filter"), a conditional theorem on Radomskii's lemma (declined), DRAT checking (classifier denial), a Lean toolchain in the July session (refused), the last factor ln₃ in Lean ("I would not spend the time"), primality certificates for the fixed-gap numbers (no PARI). [others][uarch]

---

## L. The spy's brainstorm (25 Nov, 49 ideas)

**RO-113. Rejected at the rank step (reasons visible):** survivor-score triage as new (already live since 23 Nov); two-dimensional vector on k mod 491 and 499 (+3.7% at best, leans on a truncated reading of RO-47); uniform deeper sieve (see RO-87; its test predates selection); per-row hazard curve as a decision tool ("no decision flips"); a cover-only route to 179,000-184,000 (see RO-8); row-count gates as a track ("No candidate construction exists to gate"); Bayesian design at 21-60 digits ("too vague"); "joint residue classes on non-consecutive primes" (ARGUED: "any N has exactly one residue per prime"); ceiling calibration and gate measurement as stand-alone tasks. [spy]

**RO-114. Rejected at critique with no visible reason (28 of 49; titles known for few):** lazy sieving of late rows (replacement costs about 1.4·10^5 modular operations); exact joint re-optimisation of 6-10 covering primes by CP-SAT / ILP; all-in cost accounting; closed-form keep threshold; idea 46 was never critiqued. **ASSERTED** (critics told to "Default to reject"). [spy]

**RO-115. The spy's own verdict:** "No idea in this set escapes the 200-digit local minimum"; all kept ideas together x1.3-2.4 (0.3-0.9 nats). **COST**, from the lead's relays only; the spy read no other transcript and no repository file. [spy]

---

## M. Older rulings in other games (July; recorded so that they are not mistaken for 200-digit results)

**RO-116.** Many shallow variant specs instead of one deep spec (0 hits in 2,132 specs). MEASURED, threshold game. **RO-117.** Raw GPU throughput without a re-tuned cover (112,249 lost to the CPU's 119,419). MEASURED, one campaign. **RO-118.** fscan / tscan at 20-27 digits: more than 13 fixed primes, tree search by success probability, sharing the sieve between neighbours "did not help"; a 14th cover prime "did not justify" the scanner. ARGUED with measured costs. **RO-119.** Partial covers in the height game (save < 10%). COST. **RO-120.** July "Game 1 beyond g about 2.5M" (certification wall): OVERTURNED on 21 Nov by writing N - g = 1 + 2^n·R ("one line", found twice). [ideas][uarch][phd]

---

## N. Index of rulings whose strength is ASSERTED or ARGUED only (no measurement, no theorem)

RO-3 (deeper residues cannot be sieved), RO-18, RO-30 (research's "already collected"), RO-38, RO-40, RO-46, RO-48, RO-55, RO-59, RO-60, RO-62, RO-70, RO-71, RO-72, RO-75 (archive), RO-78, RO-84, RO-109 (nibble), RO-114.
Rulings by cost arithmetic that were never run as algorithms until 25 Nov: RO-44, RO-45, RO-46 (now assigned to Lean on the miniature).
Rulings by decision or blocking, not merit: RO-4, RO-90, RO-95, RO-96, RO-97, RO-103, RO-112, and the MILP test in RO-18.
