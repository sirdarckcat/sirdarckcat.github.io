# Delta ledger: what the ARCHIPELAGO session pushed after the map snapshot (884f014 .. d960f7f)

Compiled 2026-11-25 by reading text files only; nothing from the repo was run or modified. Branch `ccr-c6e00296-3g7fp9`, 42 commits, 24 Nov 14:27 to 25 Nov 08:48. `git diff --stat 884f014 HEAD`: 192 files, all added, in three directories and nowhere else: `goldbach/balls_in_boxes/` (tasks T1 and T3), `goldbach/tempering_covers/` (T2; T4 under `floor/`), `goldbach/g_million/` (T5; no README). `goldbach/archipelagos/` is untouched. All `where:` paths are under `goldbach/` on that branch. T1 to T5 are the research session's task labels; the briefs for T4 and T5 are not in the repo, so I infer T4 ("cover counts") and T5 ("g >= 10^6") from commit messages and file headers. Statements by the research session cite its `goldbach/sublinear/README.md` (branch ccr-d4a17dd0-7uu03r, head 48c73de).

Method. Read: balls_in_boxes/README.md, T3.md, tempering_covers/README.md, floor/floor_report.md, floor/x997_report.md, t2_table.md, all script docstrings and logs, all 42 commit messages, the Lean worktree (head a1c77dc). I re-derived numbers with my own scratch code (python3 -I, numpy, in `scratchpad/gbmap2/work_archip/`):
- all ten best tempered vectors and the five `complete_cover_*` files (first odd prime in no class): all match;
- ln g0 for all 100 raw `cover_floor` outputs, with my own Bennett-acceptance-ratio chain: every reported value matches to 0.01; the x = 1,999 values are new (not written up);
- T5: rows left 1,309 and 3,028 re-counted, greedy 1,317 and 3,112 reproduced;
- T3: all-greedy C* = 6.556 (x = 10^4) and 8.393 (10^5) reproduced by independent greedy code; T3c numbers reproduced;
- T1: independent-balls counts at x = 10^5 (to 0.02%) and short re-simulations (3 draws at 10^5, 5 at 10^4, w = x/2, C = 1.35);
- the T2 bracket table from `t2_runs.jsonl`;
- the integers in Cover40459/41047/41659.lean against the archipelago vectors.

Not checked: Lean proofs (only file docstrings and commit messages); whether the `cover_floor` samples are in equilibrium (I only redo the arithmetic from the stored histograms); the 20-draw T1 runs themselves; the x = 10^6 T1 data (JSON lost, log lines only); the tempering runs (not re-run); the research session's recursion (read, not re-derived).
Unverified at the time of writing: all-greedy C* = 9.973 at x = 10^6 (my run had not finished); the hand-computed c values quoted for x = 797 to 1,999 in ar_t4_law.

Entry count: 21 (T1: 6, T3: 3, T2: 4, T4: 3, T5: 2, cross-cutting: 3).

---

## ar_t1_study | T1: the ball-and-box mechanism behind "why 1.349 is not the truth"
- kind: empirical
- says: Question, from the research session's sketch for beating the constant 1.349: give the odd primes up to w random nonzero classes; how do the survivors (odd primes below y = C·x·ln x in none of them) sit in the classes of the primes in (w, x]? Method: x = 3,000 to 100,000 (10^6 reduced, 4 draws), w = x/2 or x^0.9, C = 1 to 8, 20 draws, C kernels checked against Python. Report A: pair counts, moments, conflicts, deletion. Report B: large primes take the fullest class. Headline: survivors are not independent balls; the two moment bounds hold; deletion would give about 1.5, not 2; random-small plus greedy-large reaches C* = 1.39 to 4.47 (w = x^0.9), still rising.
- status: computed (finite sizes; my short re-simulations gave E/balls 0.532 at 10^5 and 0.491 at 10^4, the README's values)
- uses: m_thm1, l_cb_sharp, ext:research-sublinear-README, ext:FGKMT-long-gaps
- where: balls_in_boxes/README.md (Findings 1-6, tables); commits 621315a, 4fe691a
- matters: First measurement of every quantity in the proposed route past 1.349; shows which assumptions of the sketch hold at x up to 10^6 and which fail.

## ar_t1_thinned | Survivors are capped, thinned targets, not independent balls
- kind: negative-result
- says: Pairs of survivors in one class of a large prime are 0.38-0.87 of the independent-balls count; classes with 3 or more survivors are 2-81% of Poisson, 4 or more 0-62%; the shortfall is largest at small C. At x = 10^5, w = x/2, C = 1.35, classes with 3 or more survivors: 8,638 measured, 37,556 if each class's targets were thinned independently (a class holds only about C targets), 72,597 for balls; 4 or more: 1, 550, 2,191. The rest is mod 3: survivors all lie in the one class mod 3 left unstruck, yet a class's targets cycle through all three. I re-derived the balls counts to 0.02% and got 8,548 (3 draws) measured.
- status: computed
- uses: ar_t1_study, m_thm1
- where: balls_in_boxes/README.md Finding 1; capacity_check.py, capacity_check.txt
- matters: "fullest classes hold about ln x / ln ln x survivors" overstates what large primes can collect at C near 1.35; independence fails on the cover side by known factors.

## ar_t1_pair3 | The outline's pair formula is zero at r = 3; the exact form holds
- kind: empirical
- says: The outline's expected number of surviving pairs in one class, N·∏(1 - 2/(r - 1)) over 3 <= r <= w, is 0 because the r = 3 factor is 0: survivors all share one class mod 3. Corrected: ½·N₃·∏(1 - 2/(r - 1)) over 5 <= r <= w, N₃ the pairs in a common class of r′ that are also congruent mod 3 (N₃/N = 0.35-0.48, not ½). It ignores the gain from congruences mod 5, 7, ..., so it is a lower bound; measured pair counts are 0.99-1.15 times it. The exact expectation (48 sampled pairs per large prime) matches the draws within 4.3% (0.957-1.022). The research README already carries the r = 3 correction.
- status: proved-in-text (lower bound is one line) and computed
- uses: ar_t1_study
- where: balls_in_boxes/README.md Finding 2; Report A table columns E/exact, E/(r = 3 exact)
- matters: Corrects the formula the proof outline would have used; the corrected count is close to the truth, so the outline's pair step is sound.

## ar_t1_moments | The two upper bounds the outline needs hold with small constants
- kind: empirical
- says: Second moment: mean(E²)/mean(E)² per large prime is 1.26 at x = 3,000, C = 1 and falls to 1.0002 at large C and x (56 settings, 1.0002-1.2583). Conflicts: mean X/(mean E₁·mean E₂)·|S| is 3.87-4.10 in every setting (README text says 3.87-4.04; the table maximum is 4.096) and 4.00-4.03 at 10^6; 4 is the value for independent degrees. Survivor counts match N·∏(1 - 1/(r - 1)) within 0.84%. These are finite-size measurements; the research outline reduces both bounds to upper-bound sieves (Brun, Selberg), which is not done.
- status: computed
- uses: ar_t1_study, ar_t1_deletion
- where: balls_in_boxes/README.md Findings 3-4; Report A table, columns E² ratio and conflicts
- matters: Supports, without proving, the claim that the deletion argument loses only constants at the sizes tried.

## ar_t1_deletion | Deletion keeps 9-11% of large primes at C = 1.35: constant about 1.5, not 2
- kind: empirical
- says: Mark each colliding pair of a large prime with probability θ/mean E; a prime is good if it has exactly one marked pair that meets no marked pair of another prime. The best good fraction is 0.09-0.11 at C = 1.35 (θ about 0.2-0.35), 0.12-0.14 at C = 2, up to 0.28 at C = 8, with no trend in x (3,000 to 10^6). With φ of 0.10-0.12 of large primes striking two survivors, the outline's constant would be 1.349·(1 + φ), about 1.48-1.51, not 2. The outline itself is not written out or formalised (research README).
- status: computed (the constant is an inference from the measured fraction); conjectural as a proof
- uses: ar_t1_moments, m_thm1
- where: balls_in_boxes/README.md Finding 5; Report A (v) table
- matters: The sketched route would improve 1.349 by about 10-12%, not by a factor.

## ar_t1_cstar | Random small classes plus greedy large primes: reach C* grows with x
- kind: empirical
- says: C* (largest C with nothing left in at least half the draws), random classes up to w, large primes taking the fullest class in increasing order. With w = x^0.9: 1.39, 1.93, 2.47, 3.14, 4.47 at x = 3·10³, 10⁴, 3·10⁴, 10⁵, 10⁶. With w = x/2: 1.12, 1.40, 1.56, 1.78, 2.17. C*/ln x is still rising (0.17 to 0.32 for x^0.9). Increasing order beats decreasing by about 3-9%. All-greedy reaches 5.5-8.4 at 3·10³-10⁵, so choosing the small classes well is worth ×2.7-4. At C* large primes strike mostly 2-4 survivors. T3's θ = 0.9 run measured 4.477 at 10^6, agreeing with 4.471.
- status: computed
- uses: m_thm1, ar_t3_excess
- where: balls_in_boxes/README.md Finding 6, Report B tables, section "x = 10^6 (reduced run)"; t1_x*.log
- matters: Even a crude random-plus-greedy design passes the theorem's 1.349 (by ×1.03 at 3,000 to ×3.3 at 10^6); 1.349 is a lower bound far from what covers do.

## ar_t3_excess | T3b: where the all-greedy reach comes from
- kind: empirical
- says: Question: why does all-greedy (increasing primes, fullest nonzero class) reach about 0.72·x·ln²x? For each prime the excess m - λ (class taken minus the average class of what is left) totals about x: 0.454, 0.458, 0.458 × ln x per prime at x = 10⁴, 10⁵, 10⁶. Primes up to 113 make 85% of the strikes but 3.5% of the excess (x = 10⁵); primes above x^0.8 make 5-6% of strikes and 55, 63, 71% of the excess. All-greedy C* = 6.556, 8.393, 9.973 = 0.712, 0.729, 0.722 × x·ln²x (first two reproduced by me). Middle range: excess is 0.58-0.89 of independent cells; top: 0.92-0.97 of the maximum, the cap of about C targets per class does not bind.
- status: computed (10^6 value unverified by me)
- uses: ar_t1_cstar, ext:Montgomery-Hooley
- where: balls_in_boxes/T3.md "Reading" 1-3, T3b tables; commit 323c674
- matters: Puts the x·ln²x scale in the largest moduli, not the small ones; the 1.349 theorem uses first-order averages only.

## ar_t3_reach | T3a: reach kept = one minus the excess share of the random range (predicted at 10^6 in advance)
- kind: empirical
- says: With random nonzero classes up to w = x^θ and the fullest class above, C*(θ)/C*(0) = 0.99, 0.98, 0.88, 0.58, 0.29 (x = 10⁴) and 1.00, 0.99, 0.92, 0.67, 0.38 (10⁵) for θ = 0.2, 0.4, 0.6, 0.8, 0.9. This is within 0.05 of 1 - s(θ), s the share of the all-greedy excess made by primes up to x^θ, in all 13 measured cases (measured higher in 12). The rule's 10^6 predictions (0.92, 0.71, 0.44) are in the text committed at 15:01 (323c674), before the 15:43-15:58 runs; measured 0.949, 0.741, 0.449 with 2 draws each. s(θ) falls with x at every θ.
- status: computed (prediction date checked in git history)
- uses: ar_t3_excess
- where: balls_in_boxes/T3.md Reading 4, tables T3a and "T3a against T3b"; commits 323c674, 4fe80c4, 8c2a7a8
- matters: A proof may leave the classes up to x^0.6 to chance for a cost of 5-12% of the reach; the hard part is the primes between x^0.6 and x.

## ar_t3_tempered | T3c: a planned assignment beats the independent-cell maximum at the top
- kind: empirical
- says: On the 167 moduli up to 997, targets below 40,111 (4,211): the tempered cover leaves 0, greedy (ties to the smallest class) 33; below 32,971 (3,532): 0 against 9. The tempered vector takes the fullest class at 133 of 167 moduli (80%) and gives up 44 strikes (1.0%) against always taking the fullest on its own path; its 56 largest moduli (617-997) strike 2.41 targets each, 1.38× the fullest of independent cells, greedy's 2.02 (0.96×). I re-derived 4,211, 133/167, 44, 2.41, 33 and 9. The 32,971 quoted for greedy used random tie-breaking; greedy_cover.txt has 30,184 at x = 1,000.
- status: computed (re-derived)
- uses: ar_t3_excess, e_cover_opt
- where: balls_in_boxes/T3.md Reading 5, T3c tables; t3.py c
- matters: The independent-cell maximum is not a ceiling: the best covers plan the endgame, so greedy falls short of tempering. Greedy's reach moves 9% with tie-breaking at x = 997.

## ar_t2_reach | T2: best known complete covers on 30-302 moduli
- kind: record
- says: Parallel tempering (ptcover_fast2: 56 replicas, 80,000-160,000 sweeps, 4 seeds, bisection on Q to 0.5%) on the odd primes up to x finds class vectors with every odd prime below Q in a class: Q = 2,311; 2,953; 6,451; 10,159; 12,163; 21,067; 30,931; 41,659; 70,111; 98,731 for x = 127, 149, 251, 349, 397, 599, 797, 997, 1,499, 1,999 (30-302 moduli). That is 0.775, 0.792, 0.842, 0.849, 0.856, 0.860, 0.870, 0.876, 0.875, 0.855 × x·ln²x. I re-derived all ten and the five complete_cover files by direct trial. The 238- and 302-moduli vectors are the best known at those sizes. 300 runs, about 45 core-hours (sum of logged times).
- status: computed (vectors checked by reach.py, by direct division, and by me)
- uses: e_cover_opt, e_c15907, ar_t2_wall
- where: tempering_covers/README.md table; t2_vectors.txt; complete_cover_*primes.txt; t2_runs.jsonl
- matters: Extends the luck-free depth series from 15,907 (89 moduli) to 98,731 (302); the scale is 0.78-0.88 × x·ln²x, budget-limited above 349 moduli.

## ar_t2_wall | Wall or run length?
- kind: empirical
- says: At the smallest Q every seed missed, 4× longer runs (320,000 sweeps) stay at k = 1 for x = 127, 149, 251 (a wall) but reach k = 0 at x = 349 (2 of 4 seeds, Q = 10,116) and 397 (4 of 4, Q = 12,131). The wall at 127 is the exact optimum: D(30) = 2,311, and D(34) = 2,953, in the uarch session's exhaustive search (cover_ub_results.txt on its branch). From 397 on the successful seeds used 50-97% of the budget (x = 1,999: 96%), so entries from 349 are budget-limited lower bounds; x of 599 and above were not probed with longer runs. Instrumented reruns reproduced 27 of 27 logged runs exactly.
- status: computed
- uses: ar_t2_reach
- where: tempering_covers/README.md Finding 2; t2_probe.log; t2_firsthit.log
- matters: Separates "tempering hit the optimum" (up to 251 moduli) from "tempering ran out of time" (349 and up).

## ar_t2_997 | x = 997: from 40,111 to 41,659, Lean-checked
- kind: construction
- says: All 24 tempering runs at x = 997 start from the 40,111 cover. At Q = 41,000 three of four seeds reach k = 0, at 41,512 one, at 41,640 one (vector complete to 41,659); 41,768 and beyond miss. Separately, cover_floor2 sampling at Q = 40,111 produced a vector complete to 40,459. My Python check: the integers N in Cover40459, Cover41047 and Cover41659 (416, 416, 415 digits) reproduce the vectors' classes on all 167 moduli, and N - q has a listed divisor for every odd prime q below Q. 41,047 and 41,659 share only 7 and 5 of 167 classes with the 40,111 cover.
- status: Lean-checked per Lean commits 3ccf2f0, 9470f08, 673c39d (I cannot check Lean); computed (my direct check)
- uses: ar_t2_reach, ar_lean_status, r_cover15907
- where: tempering_covers/README.md Finding 4; floor/x997_report.md; complete_cover_41047_167primes.txt, complete_cover_41659_167primes.txt, floor/runs/best_cover_x997.txt
- matters: Best luck-free depth on 167 moduli: a 415-digit even N with no Goldbach summand below 41,659, by divisibility alone.

## ar_x997_families | x = 997: complete covers split into families; random starts undercount
- kind: empirical
- says: ln g0 (log of the number of complete covers) at Q = 39,000 and 40,111: 130.5, 129.8 and 98.57, 98.60 from runs started at the 40,111 cover; 119.1, 121.3 and 79.9, 74.3 from random starts; 95.0, 94.2 from the best vector of the random runs' family. So two families hold e^98.6 and e^94.6 complete covers at 40,111 (4 nats apart) and random starts had mostly not arrived; cold replicas keep the start's classes on the first twelve moduli. 400,000 sweeps, 70 temperatures, 2 seeds. I re-derived every value from the raw histograms; equilibrium itself I cannot check.
- status: computed
- uses: ar_t4_law, ext:research-sublinear-README
- where: tempering_covers/floor/x997_report.md; run_997.py; commits 9e9dd76, 7a306ab
- matters: Near the end of complete covers the count depends on the start's family, so random-start counts are lower bounds there.

## ar_t4_law | T4: how many complete covers (counts at 60, 75, 85, 93% of the reach)
- kind: empirical
- says: ln g0(Q), the log of the number of class vectors covering every odd prime below Q, from the research session's cover_floor (70 temperatures, 400,000 sweeps, 2 seeds) at four targets per x for x = 127-1,499 and the first two at 1,999. The law ln g0 = θ(x) - c·Q/ln²x gives c about 1.02 over the first 60% for x of 251 and up (1.045, 1.027, 1.018, 1.022, 1.017, 0.984 for 53-238 moduli). At 797, 1,499, 1,999 loss·ln²x/Q is 0.98-1.03 at every target (random starts; hand arithmetic, unverified by script). New, not written up: at x = 1,999 ln g0 = 925.98, 924.65 (Q = 59,239) and 671.85, 670.49 (Q = 74,048), θ = 1,939.15.
- status: computed (my re-derivation of every ln g0)
- uses: ar_x997_families, ext:research-sublinear-README
- where: tempering_covers/floor/floor_report.md; floor_points.json; floor/runs/out_x*; commits 63dab52 to edeb914, d960f7f
- matters: Supports the research session's counting law (loss about Q/ln²x) at 53-302 moduli; the Lean files prove identities and lower bounds only.

## ar_t4_predict | Measured loss against the research session's recursion, stated in advance
- kind: empirical
- says: The research session put predicted losses θ - ln g0 on record (commit 6d3ebdf, 25 Nov 07:30) before the runs at 797, 1,499, 1,999. Measured over the pair-sum prediction at 60, 75, 85, 93% of the reach: 0.975, 0.979, 0.994, 1.013 (x = 797); 0.977, 0.988, 1.018, 1.040 (1,499); closed formula 0.974-1.004 and 0.972-1.028. At 1,999 only the 60 and 75% targets were run; I get 0.989 and 1.003 (pair sum), 0.982 and 0.993 (closed). The measured loss is 1.74-1.92 times the first-moment (independent-rows) loss, by my computation. Start-from-cover runs at the 93% targets give 1.003 and 1.023.
- status: computed (out of sample; the 1,999 ratios are my arithmetic)
- uses: ar_t4_law, c_pigeon, c_nofree
- where: tempering_covers/floor/floor_report.md ("Loss against the research session's figures"); research branch sublinear/cover_price_hl.txt
- matters: The recursion predicts counts to within about 4% at 138-302 moduli, where independent rows miss by ×1.7-1.9.

## ar_t4_bend | The bend near the end: established to 349 moduli, weaker above
- kind: empirical
- says: README: ln g0 falls with slope 1.2-1.6 (units 1/ln²x) between the 85 and 93% targets, and a line through the last interval ends at 0.96-1.01 × the tempered reach (x = 127-599). floor_report gives 1.213 and 1.177 for x = 797 and 1,499, with line ends 1.041 and 1.068 × reach. But start-from-cover runs count more than random starts at the 93% target by 0.0 (x up to 349), +1.5 (397), +5.8 (599), +6.6 (797), +20.8 nats (1,499). With the start-run counts I get last-interval slopes 1.22, 1.215, 1.069, 0.996 and line ends 1.02, 1.03, 1.065, 1.109 × reach for x = 397, 599, 797, 1,499: at 1,499 there is no bend.
- status: computed (my arithmetic on floor_report and raw outputs); bend established for x up to 349 where all starts agree within 0.3 nats; unverified beyond
- uses: ar_t4_law, ar_x997_families
- where: tempering_covers/floor/floor_report.md; README Finding 3; floor_points.json
- matters: Decides whether tempering sits at the true end of complete covers: yes up to 108 moduli; at 238 moduli the count line points 7-11% beyond the 70,111 found.

## ar_t5_cover | T5: a cover on 629 moduli for g >= 10^6 (about 1,990 digits)
- kind: construction
- says: Question (research session; the user's fixed-gap game, fewest digits for g(N) >= 1,000,000). Step 1: classes modulo the 629 odd primes up to 4,657 (product about 10^1,989) leaving few of the 78,497 odd primes below 1,000,003 unstruck. cover.py: greedy (increasing moduli, fullest nonzero class), 1-flip descent, iterated local search (perturb 2-7 moduli, descend, keep if not worse). Rows left: 3,112, then 3,091, then 3,028 (4,445 rounds, seed 1); I re-counted 3,028 and reproduced 3,112. Calibration at 89 moduli, Q = 170,000: greedy 1,317, descent 1,309 (no local search) against 1,248 for the best tempered cover (+4.9%).
- status: computed (re-counted by me)
- uses: e_threshold, e_megagap, m_density, ar_t2_reach
- where: g_million/cover.py, cover_X4657.txt, cover_X463_Q170000.txt; commit d960f7f
- matters: Start of the 10^6 threshold game. 3,028 rows left is about 31% above the research table's recursion value (2,315), so not yet a test of the recursion.

## ar_t5_status | T5 is a first step: no N, no tempering run, no certificate
- kind: open-problem
- says: g_million has no README or results table. Present: cover.py, ptcover_big.c (ptcover_fast2.c with MAXM 1024, a one-line diff), betas_k3000.txt (24 temperatures, 0.4-6.0), start_X4657.txt (the descent cover, 3,091 rows; 136 classes differ from the 3,028 cover), two cover files. Absent: a tempering run at 629 moduli, any sieve or Fermat search, a certificate, the 491-moduli (about 1,500 digits) cover that cover.py's header mentions, Fermat timings (bench_* is gitignored). The research table puts 629 moduli at 2,315 rows and 10^3.3 members per success; with 3,028 rows E is about 9.9, about 10^4.3 (my arithmetic: rows × e^γ·ln 4,657 / ln N).
- status: conjectural (plan and my cost arithmetic); computed (file facts)
- uses: ar_t5_cover, e_megagap, e_threshold, m_density
- where: g_million/ (all files); commit d960f7f; research README "The other direction: a fixed gap and the fewest digits"
- matters: The 10^6 game has a cover but no record claim; the best known for g >= 10^6 stays at 2,480 digits (research README).

## ar_lean_status | Which archipelago covers are in the Lean kernel, and what Lean says about T4
- kind: verdict
- says: At Lean head a1c77dc: Cover40459, Cover41047, Cover41659 (the archipelago vectors; Lean commits 3ccf2f0, 9470f08, 673c39d) exist and are listed in CoverCountRun.lean as lower bounds ln g0(x, Q) >= θ(x) - θ(997). No Lean file exists for the 70,111 (238 moduli) or 98,731 (302) vectors. The archipelago README names only 40,459 and 41,047. CoverCount*.lean proves the inclusion-exclusion identity and lower bounds and says the law measured in T4 is not proved; CoverPairs proves the exact mean of the pair weight; CoverDepthMore has D(30) >= 2,311 and D(34) >= 2,953 as kernel lower bounds (upper bounds are uarch's search); Cap/Hardness: finding covers for arbitrary rows contains SAT.
- status: Lean-checked per file docstrings and commit messages (I cannot check Lean)
- uses: ar_t2_997, ar_t4_law, ar_t2_wall
- where: Lean worktree goldbach/lean/GoldbachGaps/Cover40459.lean, Cover41047.lean, Cover41659.lean, CoverCountRun.lean, CoverCount.lean, CoverPairs.lean, CoverDepthMore.lean, Cap/Hardness.lean
- matters: Only the 167-moduli covers are kernel-certified; the 238- and 302-moduli records rest on direct rechecks; the counting law of T4 has no Lean backing.

## ar_h1h2 | What the new work says about H1 and H2: nothing directly
- kind: verdict
- says: No new file mentions H1, H2, the ceiling model or any t_* box; goldbach/archipelagos/ is untouched. Everything measured is on the divisibility side (which rows a class vector strikes); nothing tests whether leftover rows are prime or whether a compositeness test cheaper than one exponentiation exists. So H1 and H2 are untouched and no t_* box changes. What is shown: independence fails on the cover side by measured factors, survivors in large-prime classes at 0.38-0.87 of independent balls (T1) and the loss behind complete covers 1.74-1.92 times the independent-rows first moment (T4). T5's cost E would rest on H1 at about 2,000 digits.
- status: conjectural (my reading; the session's text does not discuss H1 or H2)
- uses: m_h1, m_h2, t_calib, t_joint, ar_t1_thinned, ar_t4_predict
- where: absence across balls_in_boxes/, tempering_covers/, g_million/; balls_in_boxes/README.md Finding 1; floor_report.md
- matters: Luck-side evidence for H1 stays with the exhaustive windows (t_calib, t_joint); the cover-side non-independence found here is a different, measured effect.

## ar_ceiling_door1_sublinear | Ceiling model, Door 1, sublinear programme
- kind: verdict
- says: Ceiling (m_ceiling): untouched; the research table gives 142 digits as the ceiling size for a gap of 10^6, against T5's 1,500-2,000. Door 1 (m_rounding): T2-T4 quantify the integrality gap with size: a random class vector covers below Q with probability about e^(-Q/ln²x); tempering reaches 0.78-0.88 × x·ln²x, greedy 0.72, and the theorem's 1.349·x·ln x is only 0.1-0.2 × x·ln²x for x of 10³ to 10⁶. Sublinear programme: covers look near their optimum (walls to 251 moduli, counts ending near the tempered reach to 108), so any gain must come from outside the cover, as s_verdict says; (P′) is not addressed.
- status: conjectural (my synthesis of ar_t2_wall, ar_t4_bend, ar_t3_tempered)
- uses: m_ceiling, m_rounding, s_verdict, s_question, ar_t4_law, ar_t2_reach
- where: tempering_covers/README.md; floor/floor_report.md; balls_in_boxes/T3.md
- matters: Gives Door 1 its first size-dependent numbers; supports "covers in use are about the best", with the budget caveat at 238 and 302 moduli.

---

## Changes to existing boxes

None is contradicted. Extensions (the text would be incomplete, not wrong):
- t_data, t_calib, t_joint, t_archip, t_props, t_tail, t_ml, t_budget | no change and no extension: the new work is on covers, not on the exhaustive g(N) windows, and goldbach/archipelagos/ is untouched | git diff --stat 884f014..d960f7f
- m_thm1 | extend: measured cover reaches are far above 1.349·x·ln x and grow like ln x (random-small plus greedy-large 1.39-4.47, all-greedy 5.5-10, tempered 3.8-6.5, in units of x·ln x, x = 127 to 10^6); the theorem is a lower bound, not the truth | ar_t1_cstar, ar_t3_excess, ar_t2_reach
- e_cover_opt | extend: tempering results at 30-302 moduli (0.775-0.876 × x·ln²x); a greedy-plus-descent code leaves 1,309 rows at the campaign point against 1,248 tempered | ar_t2_reach, ar_t5_cover
- e_c15907 | extend: complete covers continue to 41,659 (167 moduli, Lean-checked), 70,111 (238) and 98,731 (302) | ar_t2_reach, ar_lean_status
- m_rounding | extend: complete covers number about e^(θ - Q/ln²x) and split into families (4 nats at x = 997) | ar_t4_law, ar_x997_families
- e_threshold, e_records | extend: the threshold game at Q = 10^6 has started (a cover only; nothing found or certified) | ar_t5_cover, ar_t5_status
- m_h1, m_h2, m_ceiling | no change | ar_h1h2

## Dependency notes

1. T1 tests the research session's sketch for beating 1.349: survivors are thinned, the two moment bounds hold, deletion gives about 1.5. T3 asks why greedy does so much better than the sketch. The answer is the largest primes, and T3c shows a planned assignment does better still. That is the case for tempering, which is T2.
2. T2 finds complete covers up to 0.78-0.88 × x·ln²x; T4 counts how many complete covers exist at 60-93% of that reach. Up to 349 moduli the count ends where tempering stops; at 797 and above the counts depend on the start, so the end is only bracketed.
3. x = 997 chain: the 40,111 cover (research) feeds the T4 family test, which samples a 40,459 vector (Lean-checked); tempering from the 40,111 start then reaches 41,047 and 41,659 (both Lean-checked). The research tables and Lean's CoverCountRun lower bounds use them.
4. The research session wrote predicted losses for 797, 1,499, 1,999 before the runs; T4 measured them (about 4% agreement). The Lean files prove only pieces of that law (pair-weight mean, lower bounds).
5. T5 follows from the user's fixed-gap proposal: the research table says a 629-modulus cover should leave 2,315 rows; cover.py leaves 3,028. The next steps are a tempering run (ptcover_big, start file, betas ready), then sieve and Fermat tests at about 2,000 digits; neither is in the repo.
6. Cross-check chain for greedy: the research session's greedy_cover.py, the Lean session's greedy.py and the archipelago's C kernel agree on G(x)/(x·ln x) to 0.2-0.4% at 10^4 and 10^5, and my own numpy code reproduces the archipelago's 6.556 and 8.393; tie-breaking alone moves the x = 997 value by 9%.

## Doubts

1. Bend versus start-run undercount (ar_t4_bend). README Finding 3 says "the bend is real" and a last-interval line ends at 0.96-1.01 × reach; that range covers x up to 599 only. The final floor_report (797, 1,499) gives 1.041 and 1.068, and the start-run counts, which are higher by up to 20.8 nats at 1,499, remove the bend there. README Finding 3 also says the 127-599 summary is in floor_report.md; that file was regenerated for 797 and 1,499 only, so the 127-599 summary exists only in git history (commit b343bec).
2. T1's 10^6 paragraph compares different columns. It sets E/balls at 10^6 against the "classes with 2 or more survivors / Poisson" column for x up to 10^5 (0.832 and 0.872 at C = 4, 10^5 are that column; 0.665 and 0.726 at C = 2 likewise). Like for like, E/balls rises: C = 2: 0.619 to 0.662 (w = x/2), 0.671 to 0.727 (x^0.9); C = 4: 0.763 to 0.790, 0.795 to 0.831. So "flat at 2" and "a drop at 4 that I cannot explain" (commit 37c417c) look like a column mix-up, not a physical effect. My reading of the JSON and table; not re-run.
3. The T2 series 0.775 ... 0.855 is not one budget or one start type. x = 997 comes from runs all started at the 40,111 cover; the values at 349 and 397 come from 4× longer runs; 599 and up were not probed with longer runs; the research README says "at one budget". The plateau is budget-limited: the research recursion puts the end at about 1.00 × x·ln²x for 1,499 and 1,999, so the covers found are 85-88% of that. "Luck-free depth known to a few percent at every size" holds for losses (counts), not for D at 238 and 302 moduli.
4. T5 is unfinished and a little inconsistent. start_X4657.txt is the descent cover (3,091 rows), not the best (3,028). The 89-moduli calibration ran 0 local-search rounds, so it calibrates greedy-plus-descent only; 1,309 there is unweighted and is not the research session's 1,308.67 (a weighted measure). The 3,028 against 2,315 gap is mostly a search deficit, not evidence about the recursion. No README.
5. Unreported work: the last commit says "T4: first 1,999 counts" but nothing reports them (I computed them from the raw files); only the 60 and 75% targets at 1,999 exist.
6. T1 README small slips: conflicts "3.87 to 4.04" against a table range 3.869-4.096; exact-expectation agreement "within 4%" against 4.3%; E/(r = 3 exact) "1.00 to 1.15" against 0.989-1.153; "increasing is best by 3% to 7%" against -1% (x = 3,000, w = x/2) to +9% (10^4, x^0.9). The 10^6 run had 4 draws, no exact expectation and a lost JSON; the "random" order for w = x^0.9 is missing.
7. Lean status in the archipelago README is incomplete: it names 40,459 and 41,047 certified; the Lean branch also has 41,659 (commit 673c39d). The 70,111 and 98,731 covers rest on reach.py plus my direct check.
8. T3a rule: 1 - s(θ) matches within 0.05 in 13 cases, but s(θ) comes from one all-greedy run per x and the 10^6 test used 2 draws per θ. It is an empirical regularity, with no theory behind it; "greedy reach 0.72 × x·ln²x" depends on tie-breaking (30,184 against 32,971 at x = 997).
9. Unverified by me: the all-greedy C* = 9.973 at x = 10^6 (run unfinished when this was written); the hand arithmetic for c at 797, 1,499, 1,999 in ar_t4_law; whether tempering from random starts at 599 to 1,999 moduli would have found the same families as the 40,111-start runs at 997.
