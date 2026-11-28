# PREMISE LEDGER: what the 200-digit plan and its negative verdict rest on

Synthesis of the 21 maps (no new ideas). Written 2026-11-25 about 14:45Z.
Status words: **proved (Lean)**, **proved (paper)**, **measured** (with size), **heuristic**, **assumed** (unexamined), **decision** (a choice by a session or the user), **false** (refuted in the sources).
"RO-n" refers to RULED_OUT.md. Numbers are as the sources give them; "[derived]" marks arithmetic done by a mapper or here from two stated numbers.
Premises are numbered P-1 to P-44 and grouped by theme, so the numbers are not in reading order. P-28 is not used (cost scaling across sizes is inside P-39).

Index: frame P-1, P-37, P-20, P-38, P-27, P-21 | luck P-2, P-3, P-4, P-39, P-43 | covers P-5, P-6, P-7, P-10, P-11, P-12, P-44, P-13, P-14, P-15, P-42, P-26 | search P-8, P-30, P-31, P-9, P-32, P-17, P-29 | mechanisms and tests P-18, P-19, P-16, P-24, P-25 | forecast P-22, P-23, P-35 | process P-34, P-33, P-36, P-40, P-41.

---

## A. The frame

**P-1. The game is "largest g(N) with N < 10^200", scored as g / 2,130,704.**
- Status: user statement ("maximize g(N) within N<1e200 (maximize closeness % within that class)"), known through the lead's compaction summaries.
- Load-bearing for: every ranking of options (expected final record), the refusal of GPUs to the fixed-gap game, RO-102, RO-103.
- Weakest point: the denominator. The team's "11% at 150 digits, 17% at 100" uses each size's own ceiling, a different score; the spy says the definition "was not verified against the raw user messages"; the user also wrote "200 digits domain". The lead is asking the user.

**P-37. The target is 10% (g >= 213,070).**
- Status: user-originated (`/goal reach 10%` on the research session; "TO GET TO 10% AT LEAST AND THEN HILL CLIMB TO 20, 30, 40 AND 50%"; "to reach 10%-50%"). The lead holds it "per the research session's reports, not verified by me".
- Load-bearing for: the "x2,200 / x5,600 short" verdict (RO-1); the stop hook that keeps research working.
- Weakest point: it is a first milestone in the user's words, and the fleet is not aimed at it (P-21).

**P-20. Compute is fixed: the remaining Colab units (7,027.8 CU at 07:33Z 25 Nov), nothing else.**
- Status: user statement ("Let's see how far we can get with the current colab resources"; "No volunteer bs.") as extended by the lead ("do not cost or mention them again"; "the units, not a date, end the campaign").
- Load-bearing for: every "N times the remaining budget" figure; RO-96, RO-97, RO-98.
- Weakest point: the user named volunteers only; "units, not a date" is the lead's assertion (research: "If there is a date I do not know of, or the units expire, ignore this"); the unit burn is 28.30 CU/h where 25.13 was predicted (+3.17 unexplained), which is about 11% of the expected hits [derived: 7.95e-3 hits/h ÷ 28.30 against ÷ 25.13].

**P-38. Colab's limits are binding and outside the project.**
- Status: measured (24 h runtimes; G4 capped at 2 since 24 Nov 19:59Z, L4 at 2 since 22:39Z; HTTP 412 on every retry for 18+ hours; a T4 granted at once).
- Load-bearing for: the 5-card fleet (0.19 against 0.29 design hits a day), the no-proactive-stops rule, the risk at the 19:15-19:33Z handover (two G4s = 80-87% of expected hits).
- Weakest point: "not checked against Colab documentation" (spy); cause unknown (cap, capacity or throttle).

**P-27. The size is fixed at 200 digits; a smaller N is a scope change that needs the user.**
- Status: assumed from "200 digits domain, no baby steps"; research's gloss "Small N is allowed only as an experiment for a 200-digit method"; brainstorm ideas 71-75 "CLOSED BY THE USER".
- Load-bearing for: RO-103 and the absence of any engine or cover work at other sizes before 25 Nov 13:00Z.
- Weakest point: the user's own sentence allows 21-digit CPU work "to obtain empirical data"; the gloss is a session's.

**P-21. The quantity to optimise is the expected final record (design Q = 170,000), and the final record is "dominated by a design hit".**
- Status: decision by the lead on research's tables; never confirmed by the user.
- Load-bearing for: Q = 170,000, family B, the refusal of near-miss truncation (RO-90) and of the 213,070 design (RO-4).
- Weakest point: every record at Q = 170,000 so far (158,209; 160,357) is a near-miss, with 0 design hits against 0.53 expected; the decision was taken for 7 GPUs and 9.5 days and not redone for 5 GPUs.

---

## B. The luck side

**P-2. H1: the uncovered rows of a member are prime independently, each with p = boost/ln N (0.0239-0.0243 nats a row at 200 digits); P(hit) = 0.89·(1-p)^rows.**
- Status: heuristic (Hardy-Littlewood k-tuple statement, "not implied by GRH"). Measured: 356 hits against 366.5 at Q = 40,000-75,000 (200 digits); 1,184 / 1,186 successes at Q = 60,000; fleet tally 9 found against 10.31 expected over all covers; exhaustive windows at 10^12-10^18 within about 1% once the sieve is deep; ladder at 100 / 150 digits 0.95, 0.95, 1.11, 1.13 found/expected at tested exponents 5.4-11.6. Lean: an inequality only for moduli >= Q inside the residue model ("Below Q ... the inequality is not a theorem").
- Load-bearing for: every price, forecast and "times short" figure; the ceiling; the closure theorem; the prize table.
- Weakest point: never tested at the design exponent. At Q = 170,000 there is no design hit (0 against 0.53). In the fixed-gap game at exponents 13-21 the first hits were late: 5 found against 12.3 expected ("a 2% event if the model is right"; "an unexplained factor of about 2.5 (anything from 1 to 5 is compatible)"). Other counter-signals: the Q = 75,000 run (56.2 rows survived against 40.8), July campaign 3 (+0.4 nats), shallow sieves overstate by 2-9%, rows of one N "slightly less dispersed than independent". Over a thousand rows "a 1% error in p·w is e^0.3". A calibration ladder to exponent about 19 is running (uarch).

**P-3. The cards' logged expectations are a calibrated yardstick.**
- Status: measured at Q <= 150,000 (9 against 9.21-10.31); at Q = 170,000 only near-misses (2 against 2.2).
- Load-bearing for: the forecast (P-22), unit efficiency, tallies.
- Weakest point: the expectations are "the cards' own logged sums, not independent checks"; before 25 Nov a failed CPU re-check of a claimed design hit was dropped with no log line, so silent drops "cannot be counted".

**P-4. The ceiling for N < 10^200 is 2,130,704.**
- Status: heuristic (median of a Hardy-Littlewood model, 128 particles; 5-95%: 2,123,360-2,143,754); an independent one-constant formula gives 2,133,689; "good to about 0.4%"; "may be 1.5% too low" (record holders arrive early); at 19 digits the model gives 9,570-10,187 against the true 9,781.
- Load-bearing for: all percentages; the 213,070 target; own-size ceilings at 100 / 150 digits (465,348; 1,136,627; recheck with 200 particles running).
- Weakest point: "Nothing about the size of g(N) is proved"; never compared with constructive results at small N.

**P-39. The same hit model prices other sizes** (p = 0.0426 at 100 digits, 0.0305 at 150, 0.0170 at 300, 0.0133 at 400; Fermat cost "roughly the cube of the number of digits", tests per member proportional to digits).
- Status: heuristic + measured constants (138.5 tests per prime against 137.0; survivor mean and sd as predicted).
- Load-bearing for: the dual-game tables; "11% at 150 digits, 17% at 100" (research: E = 30.84 at 709 rows / 100 digits, 31.01 at 1,003 rows / 150 digits, both UNVERIFIED); RO-102, RO-106.
- Weakest point: the first table was "too hopeful by a factor of two to four in members"; analytic calculators were 1.5x optimistic at 1,183 rows; no engine exists at those sizes; error bar "within about one nat".

**P-43. Records arrive as near-misses of a higher design; a design hit is worth about +10,000 in g (lands 3,500-4,100 above Q), a near-miss about +2,000.**
- Status: measured (2 near-misses against 2.2 expected); values are the lead's and research's estimates.
- Load-bearing for: P-21, the row weights, family B.
- Weakest point: the +10,000 figure has no stated derivation; landing estimates are ledger arithmetic.

---

## C. The cover side

**P-5. The CRT line: a number below 10^200 (460.5 nats) can have prescribed residues only modulo primes of product at most 10^200, i.e. the 88-89 smallest odd primes (M about 10^192.7; about 2·10^7 members a vector).**
- Status: proved (Lean `card_residues_in_le`, `move_budget`) as a counting bound for constraints that are a product over coprime moduli of per-modulus residue sets.
- Load-bearing for: "covers are solved", "the rest is luck", RO-30, RO-33, RO-51.
- Weakest point: it is a statement about residue-set products. The Lean file itself names what is outside: sets "good in total without being constrained prime by prime". It does not bound cost or probability.

**P-6. The right design is one residue class on each prime modulus; the classic cover is "the unique design whose admissible set is an arithmetic progression (free to enumerate)".**
- Status: prime moduli suffice: proved (Lean). One class: measured in a product model at 100-150 digits only. "Unique enumerable design": flagged "conjectural" by the ledger.
- Load-bearing for: RO-33, RO-38, every floor (all are over one-class vectors).
- Weakest point: no 200-digit figure; "enumerable" is defined as "is an arithmetic progression"; Lean says the underlying claim is false "for information".

**P-7. The modulus set (first 88 odd primes plus 463 or 491) is optimal to about 0.2 nats.**
- Status: measured for one swap of the last prime (463..900) and for 86 / 88 / 90 initial primes at Q = 122,000.
- Load-bearing for: all floors ("on these moduli"), RO-30, RO-31.
- Weakest point: assumed-unexamined beyond that. No non-initial set was optimised at 200 digits; the one swap tried beat its prediction; older records used selected sets; the size-unconstrained oracle has E = 25.75 with 200 moduli against 39.2 (13 nats attributed wholly to the cap).

**P-10. The covers in use are within a row or two of the best possible on their moduli** (1,248 rows at Q = 170,000 against a floor of 1,214; 1,609 against 1,554-1,596 at 213,070; theory 1,221 / 1,584).
- Status: measured (two-start tempering free energy; "measurements, not proofs"); certified floor only 777; LP floor 1,170 conditional on 22 fixed classes.
- Load-bearing for: "The cover lever is closed from all three sides"; RO-6 to RO-9.
- Weakest point: the equilibrium loophole ("covers that neither start reaches"); floors computed on 3..463, not the fleet's 491 set; the proof-level gap is 471 rows (about 11 nats); the July verdict of the same kind fell (RO-11); "converged at 1,218" at 125 moduli was beaten by 1,216 two hours later.

**P-11. Tempering reaches the bottom of the landscape when seeds agree.**
- Status: measured; exact at 30 and 34 moduli; fails to equilibrate at 629 moduli above beta 0.3; at 1,228 moduli no run has converged.
- Load-bearing for: P-10, P-12, the counting law.
- Weakest point: family trapping. Cold replicas keep the start's classes on the first twelve moduli; B "was not visited at the cold end" in two of three runs; short screens sit 6-8 rows above bottoms.

**P-12. Family B (frame 3:2 5:3 7:5 11:6 13:5 17:4) is the best family.**
- Status: measured for 13 of 92,160 frames.
- Load-bearing for: the fleet's covers; +1,000 expected record over family A.
- Weakest point: found by luck; candidates chosen by a score the authors call "a coarse guide"; an unidentified family at 1,309.36; "a family that none of these routes reaches" not excluded. Research values the stake at only +100 to +250.

**P-44. Cover quality = rows left below Q.**
- Status: false as first used (23 Nov): rows above Q matter (families A and B differ by about 30 rows in 170-190k). Replaced by weighted rows.
- Load-bearing for: the optimiser's objective until 23 Nov; the unweighted floors still use it.
- Weakest point: "residual risk is other blind spots of the same kind" (ledger). The weights depend on the horizon (1,308.67 under 8.9-day weights, 1,287-1,291 under 8.2-day weights).

**P-13. The counting law ln g0 = θ(x) - c·Q/ln²x (c about 1) and the price recursion describe covers; the recursion's floor is 2% low at the campaign point.**
- Status: measured at 14 sizes / heuristic (rests on Hardy-Littlewood pair counts); Lean proves only identities and much weaker lower bounds.
- Load-bearing for: theory floors 1,221 / 1,584; the dual-game tables; "where the count of covers runs out".
- Weakest point: a hand-chosen cut at moduli 3-17 ("reproduces the one end that is known"); with exact inputs the end is 5% too far at 89 moduli; not invariant under the order of the moduli (loss 3,349 / 3,452 / 1,606); floor 4-14% low nearer the end and 15-20% low at 629 moduli; negative prefix entropy.

**P-14. Where the count of (typical) covers runs out is where covers stop existing.**
- Status: false in general (consultant, 25 Nov 11:30Z): the entropy count "describes the typical covers, not D(n)" and "cannot see structured covers"; "true of the model and false of the primes" (Lean).
- Load-bearing for: "complete covers end near 16,000 on 89 moduli"; the floors 1,214 / 1,554 as existence statements; RO-104.
- Weakest point: rigorous knowledge is only 15,907 <= D(89) < 35,000 and a floor of 777 rows. Tempered covers already strike 1.38x what independent cells allow at the top moduli.

**P-15. "Nothing changes at 200 digits" (structured covers, the block, every theory result of 24-25 Nov).**
- Status: asserted by research and consultant, repeated by the lead; then measured on 25 Nov 13:33-13:45Z for four block shapes at Q = 170,000 (1,342-1,449 rows against 1,248); 213,070 pending.
- Load-bearing for: keeping P-10 after P-14 fell.
- Weakest point: before 13:33Z it rested on one construction at x = 10^4 with greedy completion. The new test compares fresh 40,000-sweep covers around a block with the best cover; other structured families (several scales, different integers, a block as a tempering start or as an ordering) are untested, and the consultant calls better prefixes "likely".

**P-42. Small-moduli classes of greedy covers are near-optimal; optimal covers are "nearly unique".**
- Status: measured (5,760 combinations on moduli 3-13 at 629 moduli; counts of optimal vectors for n <= 28).
- Load-bearing for: "no slack to reshuffle"; frames as the coordinate of a family.
- Weakest point: small-n, complete-cover statements; at 167 moduli e^98.6 complete covers sit in one family at 96% of the reach, and the furthest-reaching family is not the most populous.

**P-26. Vectors are free (covers are plentiful), so the search is limited by compute, not by the range of a progression.**
- Status: measured (e^27 covers within 10 rows; about 50 million family-B covers at <= 1,251 rows).
- Load-bearing for: 89 moduli with only one 2^24 window per vector; f = 0.985.
- Weakest point: contradicted in the same documents by "f is supply-bound"; each row-cap step costs 2.4%; the best level "ran out within an hour".

---

## D. The search side

**P-8. Information beyond the modulus budget can only be collected by enumerating members and counting rows: "one nat of work per nat of information"; linear scoring is at its optimum; "the sieve cannot skip members".**
- Status: assumed / asserted ("I know no method"; "No algorithm is known"); the ledger calls the optimality statement "conjectural".
- Load-bearing for: the whole negative verdict. If false, 3.5 nats (depth 1,000) to 14.8 nats (depth 50,000) become collectable; depth 5,000 alone "would bring the 10% record within the Colab units that remain".
- Weakest point: no proof and, until 25 Nov, no experiment: the four method families were "ruled out by cost arithmetic at 200 digits and ... not run on the miniature"; nobody worked on it from 24 Nov to 25 Nov 12:54Z. Research: "The instance is special ..., and that is the only place left to look."

**P-30. The Lean barrier theorems bound what search can do.**
- Status: proved (Lean), each inside a model: oracle access (BlackBox: "The real instance is not a black box"); arbitrary rows with moduli larger than the number of rows (Hardness); Johnson-radius decoders with their conditions taken as hypotheses (Radius); products of per-prime lists for s >= Q (ListGain); two-list merges (Population); exact Gaussian counts in one progression (Tilt); uniform residues and moduli >= Q (Thinning).
- Load-bearing for: RO-44 to RO-52.
- Weakest point: the consultant's sentence: "they are exact only inside their models". The spy used a truncated paraphrase of one of them to reject ideas.

**P-31. Beyond the CRT line the landscape is a random-energy model: no local moves.**
- Status: proved (Lean) for moves that keep the same M and exact residues; measured in the miniature only (correlation -0.029, one move, depth 200).
- Load-bearing for: RO-51 and everything that needs local structure.
- Weakest point: needles are not independent (4 close pairs against 0.09 expected; 15 cluster pairs against 2.4 among record arrivals); successes "lean to large N"; class 2 mod 5 holds 73% of the miniature's best numbers.

**P-9. The N below 10^200 are a fair sample of residue vectors.**
- Status: assumed; checked in the miniature within 3% (at e^-168 numbers per vector; the real case is e^-19,345 at depth 20,000).
- Load-bearing for: the prize table, the 10^175 solutions, "16% for a perfect search".
- Weakest point: "for z >= 1,000 there is no direct count at full size".

**P-32. The best N are not members of the best covers ("luckily aligned members of mediocre covers").**
- Status: measured (20,000 members of a 1,609-row cover; exact in the miniature: 1 of the 62 best lies in the best covers).
- Load-bearing for: the conclusion that cover-first is not the ideal order (229x in the miniature for the first success, 1x for all 256).
- Weakest point: it is used only as a description; the campaign's design still goes best-cover-first.

**P-17. The count of rows left is a sufficient statistic, selection on it is near its limit, and survivor counts are binomial.**
- Status: measured (LightGBM near 10^15-10^18; sd 16.4 against 16.7 binomial at 200 digits; tail resolved to 0.1% on one vector); proved (Lean) inside the independence model.
- Load-bearing for: RO-52, RO-53, the keep fraction, "selection gains 2-4x, not more".
- Weakest point: only residue features were tried; nothing measured beyond 3 sd; the selection cap is per progression and per sieve depth.

**P-29. The miniature (X = 10^9, Q = 1,000) is a valid scoreboard for mechanisms meant for 10^200.**
- Status: assumed by the lead's scoring rule of 25 Nov.
- Load-bearing for: the tasks now running (Lean: four families; consultant: five or more out-of-grammar mechanisms).
- Weakest point: 256 successes ("Noise ... is large at k = 1 and 3"); CRT line at 23, depth 200; two more miniatures were built only at 13:40Z.

---

## E. Mechanisms and tests

**P-18. A row is made composite only by a small prime factor (cover or sieve) or by chance; no third mechanism exists over the integers.**
- Status: proved (paper, draft rigour) on a seven-family grammar under H1 and H2; the parity non-analogy is argued.
- Load-bearing for: "Door 3 is closed"; RO-63 to RO-71.
- Weakest point: "Mechanisms outside the grammar are not excluded"; the code tested less than the grammar; the whole chain was written in about 80 minutes on one day in July; in F_q[x] a third mechanism is a Lean theorem.

**P-19. Dependence between rows runs only through primes below Q, and that information is fully harvested by cover and sieve.**
- Status: first half proved (Lean); "fully harvested" is argued in one sentence.
- Load-bearing for: RO-72, RO-76.
- Weakest point: the theorem is about one integer dividing two rows; linked divisors are named as outside.

**P-16. H2: no compositeness test cheaper than one modular exponentiation; the tests of one member cannot share work.**
- Status: open ("no lower bound ... in any realistic model"); sharing disproved for one scheme only.
- Load-bearing for: the cost floor; the closure theorem.
- Weakest point: untouched from July to 25 Nov 13:37Z. The H2 note's 200-digit gains (0.64 / 1.93 / 2.82 / 3.00 nats for f = 1/2, 1/10, 1/100, 0) assume a sieve share "of at most 5%", while the fleet measures the fixed sieve part at 28-32% of an RTX batch.

**P-24. The engine is at its optimum:** sieve to 10^8, keep 1.5% (RTX) or 3% (L4 / T4), about 14 Fermat tests per kept member, kernel at its multiplier floor; a vector is one 2^24 window; k is 32-bit; kernels exist for 661-665-bit numbers only.
- Status: measured on the cards (gates of 1-2%).
- Load-bearing for: "engineering ideas add x1.3-2.4 at best"; no work at other sizes.
- Weakest point: optimum of this design (per-prime marking cost 0.030 ns; per-vector fixed cost about 30 ms "with an ideal of ~3-5 ms"); L4 / T4 less tuned; several named items "not built".

**P-25. The kernels give no wrong verdict.**
- Status: measured (0 mismatches on 100,000 + 5,000 + 15,496 numbers); Lean covers an older kernel.
- Weakest point: the inline-PTX path is covered only by on-device gates; pre-patch silent drops are unauditable.

---

## F. Forecast and conversion

**P-22. The forecast: expected final record 175,100-176,500 (8.2-8.3%); P(>= 170,000) 0.88-0.92; P(>= 213,070) 0.00007.**
- Status: one planning model (research), inputs revised about five times; readers "could not rerun" it.
- Load-bearing for: P-21, RO-4, the unit-efficiency advice.
- Weakest point: the 2.20 expected design hits use 25.13 CU/h; at the actual 28.30 CU/h the same rates give about 1.97 [derived]; if the G4s are not replaced tonight the rate falls by 80-87%.

**P-23. Conversions: +1,000 in Q = 8.7-10 rows = 0.21-0.24 nats; 1 nat = about 4,500 in g = 0.21 points; x10 compute = +10,600 in g.**
- Status: measured slope on fixed moduli (Q = 122,000-213,070) and extrapolated.
- Weakest point: a property of one-class covers on about 88 moduli; the spy quotes 4,300 to 11,000 per nat.

**P-35. The prime-gap record community has hit "the same wall" (merit 39.6 at 175 digits = 9.8% of ln²p).**
- Status: cited by research, figure once corrected, unverified by the lead.
- Load-bearing for: outside support for the verdict only.

---

## G. Process premises

**P-34. Other sessions' numbers and proofs are right; relays are faithful.**
- Status: assumed. The lead checks records from N and g only and never rebuilds Lean; research treats the lead's paraphrases as the user's words; the spy saw only the lead's relays.
- Weakest point: errors were found only when another session was asked to referee (two limit claims, the consultant's 29 map errors, uarch's "wrong above 664 bits", stale tallies); clocks differ by 10 minutes to 2 hours.

**P-33. The record g = 160,357 is correct.**
- Status: proved (Lean kernel: 20 block checks + 21 elliptic-curve steps), re-checked from N by three sessions. Not in doubt.

**P-36. Rental and other paid compute are excluded.**
- Status: decision by the lead, not the user (see P-20).

**P-40. The asymptotic theorems are new.**
- Status: "probably not new as statements" if Radomskii's unrefereed 1 Nov 2026 lemma holds; the kernel-checked elementary proof is the team's.
- Load-bearing for: nothing at 200 digits.

**P-41. GRH and the remark.pdf archive cannot help the search.**
- Status: argued; archive triaged by names and statements only.
- Weakest point: the user gave the archive as "a map on how to make progress"; nobody has read its proof architecture.
