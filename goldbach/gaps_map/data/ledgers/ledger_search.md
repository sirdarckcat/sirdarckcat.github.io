# Result ledger: search and sublinear-search research on Goldbach gaps

Compiled 2026-11-23 by reading text files only (nothing from the repo was run or modified). g(N) = least prime p with N - p prime. Base path B = `research/goldbach/` of the worktree; all `where:` paths are relative to B unless they start with `slop/`.

Scope and sources. All assigned files were read (sublinear/README.md and every .txt in sublinear/; FRONTIER.md, RESULTS.md, PROPOSAL_NEXT_CAMPAIGNS.md, ceiling_model.py docstring, record_holders.txt, fscan/README.md, fscan/cover/README.md, fscan/FERMAT26_STEP.md, proth/README.md, tscan/README.md, bls/README.md). To fix the chronology and the context of the sublinear question I also read, and mark "(outside assigned list)" in `where:`: fscan/cover/brainstorm/ (README, verdicts_on_lean_ideas.txt, verdicts_on_research_ideas.txt, head of ideas_lean.txt, oracle/price/portfolio/reach_target/sieve_depth/overshoot txt), slop/goldbach/records/README.md, parts of phd/RESEARCH_LOG.md, phd/wp7_probes.md, phd/wp10_grh_remark.md, phd/wp12_prime_covering_grh_ledger.md section 2, phd/toy_crt/results.md, phd/wp9/h2_open_problem.md and parts of phd/wp9/wp9_closure_theorem.md, and the docstrings of the main scripts. Statements "I re-derived" mean I recomputed them in a scratch script from the committed text files (complete-cover figures, miniature counts, parity formula on four rows).

Conventions. Lean statuses are quoted from the READMEs and verdict files: there is no lean/ directory in this worktree (the Lean work is on branch `ccr-36ca7b46-8twf14`), so no Lean claim could be checked here. One "nat" = a factor e in the number of members that must be tested (4,500 in g, 0.21 points of closeness at 200 digits, per the brainstorm README). The "fleet" is the GPU fleet of 22-23 November 2026.

Entry count: 79 (records 10, covers 13, engines 9, models 13, sublinear and function-field toy 28, verdicts and corrections 6).

---

# A. Records and chronology

## R_baseline | Baseline records before this repo
- kind: record
- says: Exhaustive search (Oliveira e Silva, Herzog and Pardi, Math. Comp. 83, 2014) shows g(N) <= 9,781 for every even N <= 4*10^18; the 69 record holders in record_holders.txt end with N = 3,325,581,707,333,960,528, g = 9,781 (Herkommer's tables reach g = 8,443 at 2n ~ 1.2*10^17); the source paper "Cute Goldbach Gaps" (July 2026) had a 199-digit N with g = 105,667 serving both bounded games and a 237-digit N with g = 109,621 for the height game, and web searches (2026-07-27 and 2026-11-21) found no other constructive literature.
- status: computed/verified (every g in record_holders.txt recomputed with gmpy2; paper incumbents re-verified with gmpy2/BPSW); the literature items are external and were not re-checked
- uses: ext:Oliveira-e-Silva-Herzog-Pardi-2014, ext:Herkommer-tables, ext:Cute-Goldbach-Gaps-paper
- where: record_holders.txt; RESULTS.md "Prior-art check (2026-07-27)" and "low end of the threshold game (2026-11-21, night)"
- matters: fixes the exhaustive ceiling (about 9,781 at 19 digits) and the incumbents the constructive records beat.

## R_megagap | g = 1,134,871 at 2,692 digits
- kind: record
- says: On 2026-07-21 the first session certified a 2,692-digit N (N0 + 14*M over a 813-congruence cover) with g = 1,134,871, which is 1.0196 times the largest certified prime gap (1,113,106) while the local prime gap at N is only 8,970 (ratio 126.5). Of 88,239 primes q < g, 1 is excluded by parity, 85,476 by a cover divisor, 895 by trial division and 1,867 by strong base-2 witnesses; N - g has a 253-step ECPP certificate; the search exponent was E = 6.56 and the hit came at k = 14.
- status: computed/verified (PARI primecertisvalid = 1; independent checker ecpp_check.py; verify_megagap.py; MANIFEST.sha256)
- uses: C_basic, E_verify, M_density
- where: RESULTS.md "Prime-gap domination record (2026-07-21)"; records/megagap_2692digit_g1134871/
- matters: shows E falls as N grows (the larger the construction the easier the search) and that Goldbach deserts can exceed prime-gap records.

## R_budget | Budget-game records 107,719 and 112,249
- kind: record
- says: 2026-07-21: a 197-digit N with g = 107,719 (N0 + 951,928*M, 89-modulus cover, M of 191 digits, 750 residual primes, E = 18.2, about 1.4*10^8 elements over 165 progressions at about 1,850 per second on 4 cores) beat the paper's 105,667 for R(10^199) and gave T(100,000) at 6.94*10^196, about 84 times smaller than the paper's 5.83*10^198. 2026-07-23: a 200-digit N = 1.0336*10^199 with g = 112,249 (k = 56,770, 90-modulus cover, M of 194.3 digits, measured E 18.4 over about 4.6*10^7 scanned elements) appeared as a by-product just above the 10^199 cap, and was later passed by the slop session's 119,419 and by the fleet.
- status: computed/verified (witness counts 1 parity + 9,471 cover + 378 trial + 400 strong base-2 for 107,719 and 1 + 9,830 + 409 + 402 for 112,249; PARI ECPP certificates validated by primecertisvalid)
- uses: C_basic, E_search, M_density, R_slop
- where: RESULTS.md "New record (2026-07-21)" and "New record (2026-07-23)"; records/dual_197digit_g107719/, records/budget_1e200_200digit_g112249/
- matters: first records of the pipeline and the calibration of E (measured 18.2 against predicted 18.2).

## R_slop | CPU-session ratchet records (slop branch)
- kind: record
- says: A parallel CPU session (2026-07-21/22) certified g = 1,157,341 at 2,480 digits (760 classes, 86,689 target primes, 245-step ECPP) and a 199-digit N with g = 110,917, then ratcheted T(100,000) through 193 digits (g = 102,337), 186 digits (g = 109,357, merged by 2026-07-25) and 179 digits (g = 101,149, by 2026-07-28), and R(10^200) to g = 119,419 at 199 digits (round 1). The 119,419 was the sub-10^200 incumbent in RESULTS.md's in-repo note, SoK and PROPOSAL_NEXT_CAMPAIGNS.md until the November fleet records.
- status: computed/verified (per slop/goldbach/records/README.md: stdlib verifier PASS, ECPP plus APR-CL, PARI full scans with 0 violations; re-verified in goldbach per RESEARCH_LOG 2026-07-25 and 2026-07-28)
- uses: C_basic, E_verify
- where: slop/goldbach/records/README.md (outside assigned list); RESULTS.md "Prior-art check" in-repo note; PROPOSAL_NEXT_CAMPAIGNS.md table; phd/RESEARCH_LOG.md 2026-07-25, 2026-07-28 (outside assigned list)
- matters: its "selective testing" lesson (rank each window by rows left, test only the best fraction) was adopted into the pipeline, and its 119,419 is the baseline of the 200-digit campaign.

## R_thresh | T(100,000) records at 195 and 150 digits
- kind: record
- says: 2026-07-25: a 195-digit N of about 7.12*10^194 with g = 100,297 (N0 + 70,186*M, 88-modulus cover, M of 190.0 digits, pure threshold cover Q = 100,003 with 704 residual primes, E = 17.28 against 18.2 for the dual cover, hit after 1,590 progressions, ascending-survivor test order measured 1.8 times better). 2026-07-26: a 150-digit N of about 8.27*10^149 with g = 104,527 (N0 + 62,147,038,260*M over 68 moduli, M of 140 digits, E = 24.91) found by the CUDA engine on a Colab fleet at k = 6.21*10^10, 63.8% into the round; the round [0, 7.5*10^10) finished 2026-07-27 with about 2.1*10^12 Fermat tests and exactly one hit (Poisson mean 0.63).
- status: computed/verified (evidence.json: 1 parity + 8,903 cover + 312 trial + 398 base-2 at 195 digits, 1 + 9,097 + 433 + 446 at 150 digits; ECPP certificates validated by primecertisvalid; check_cert.log)
- uses: C_basic, E_search, E_gpu150, M_density
- where: RESULTS.md "New record (2026-07-26)" and "New record (2026-07-25)"; records/threshold_195digit_g100297/, records/threshold_150digit_g104527/
- matters: first fleet result; per RESEARCH_LOG the gain was throughput (ln 430 = 6.1 nats, the gap in E between 24.9 and about 19), not cover quality.

## R_height_ecpp_free | g = 1,200,109 and 2,000,269 without ECPP
- kind: record
- says: On 2026-11-21 g = 1,200,109 at 11,263 digits (P = N - g = m*2^12475 + 1, complete 2,005-class cover with moduli <= 17,431 so no residual primes, 2,647 tests against about 700 expected) was certified by two sessions for two different N: first at 08:03 UTC by the ccr-2ce9e63a session (proth/desert.py), then at 08:44 UTC by the ccr-8ffe9d7a session (bls_search.py, 3,472 tests against 762 expected, over the odd-index half of the same progression, jointly a roughly 5% event; 6 primes among 3,245 untested candidates against 4.62 expected, z = +0.64). The same session as the first then certified g = 2,000,269 at 15,595 digits (2,670-class cover, moduli <= 79,139, 148,950 primes below g) after 648 tests (about 970 expected), 37 minutes on 4 cores.
- status: computed/verified (proth/verify.py, bls/verify_bls_record.py, bls/xverify.py, PARI crosscheck.gp N-1 certificate plus brute-force gcd scan; tamper_test.py 11/11 rejected)
- uses: C_bls, E_verify, E_search
- where: RESULTS.md "New height records (2026-11-21)"; proth/README.md "Records"; phd/RESEARCH_LOG.md 2026-11-21 cross-reviews (outside assigned list); records/height_11263digit_g1200109/, bls_game1_11263digit_g1200109/, height_15595digit_g2000269/
- matters: removes the ECPP wall of the height game by making certification one modular exponentiation.

## R_height_gpu | g = 5,000,251 and 10,000,141 by GPU
- kind: record
- says: Evening of 2026-11-21: g = 5,000,251 at 33,938 digits (5,342-class cover, moduli <= 167,107; 68 CPU tests then 3,072 GPU screens at 0.82-0.92 s on a Colab A100; hit was the 3,080th survivor against about 2,118 expected; 44 minutes of GPU). Night of 2026-11-21: g = 10,000,141 at 61,329 digits (9,095-class cover, moduli <= 306,239, all 664,584 primes below g, g being the first prime above 10^7 the cover misses; 3,072 GPU screens at 2.35 s, about 2 h of A100; hit was the 2,718th survivor of the 10^11-sieved list against about 3,130 expected; CPU re-proof 306 s, verify.py 292 s, PARI brute-force scan 2.8 h; the other session re-ran every check and all passed).
- status: computed/verified (GPU results are never trusted: each hit was re-proved on the CPU by desert.bls_prove, then verify.py, bls/xverify.py, PARI crosscheck)
- uses: C_bls, E_prothgpu, E_verify
- where: RESULTS.md "New height record (2026-11-21, night)" and "(evening)"; proth/README.md; phd/RESEARCH_LOG.md "Campaign G" (outside assigned list)
- matters: doubled the previous height record twice in one evening, leaving only the 16,045,849 rung (longer than the largest known prime gap, costed in C_bls).

## R_lowend | Low-end threshold records, 30 to 63 digits
- kind: record
- says: Threshold game "smallest N with g > Q" just above the exhaustive range, by cover plus tscan scan: g = 10,459 at 30 digits (2026-11-21 night, k = 101,138,639), g = 10,111 at 27 digits (k = 23,025,113,687), g = 20,551 at 46 digits (k = 3,202,304,117, 6.5 min on 4 cores), g = 10,357 at 25 digits (N = 5471513744131872011405456, k = 418,223,156 after 4.9*10^11 members in 6.5 h; the model had expected 2.7 successes, chance of none 7%) and g = 30,139 at 63 digits (k = 6,878,744,425, 19 min), the last four all on 2026-11-22 (intra-day order inferred from section order); closeness on the model line is 53.8% (25 digits), 44.7% (27), 36.5% (30), 25.5% (46) and 18.3% (63). Non-frontier points: 20 digits g = 5,407, 22 digits g = 6,073, 40 digits g = 11,173.
- status: computed/verified (a witness for every prime q < g: cover prime, prime < 10^5, failed strong base-2 test or parity; ECPP for N - g; direct_check.gp repeats the check in PARI)
- uses: E_tscan, M_ceiling, C_basic, E_verify
- where: RESULTS.md sections 2026-11-21 night to 2026-11-22; records/threshold_{25,27,30,46,63}digit_*/
- matters: calibrates the search model at 25-63 digits and sets the figures the fscan work tries to beat.

## R_fscan23 | Five 23-digit numbers with g above 10,000
- kind: record
- says: fscan class 197, run on six machines by another session, found N = 83668534093338795647672 (g = 10,159), 78209882584085138254532 (10,399), 54284735534856910692542 (11,701), 35505990484772441527442 (10,771) and 30625623272505310405982 (10,729). Five against 0.78 expected for the class is a 0.13% event (about 2% over all classes run); the smallest, 3.06*10^22, replaces the 25-digit N with g = 10,357 as the smallest known N with g > 10,000 (date not stated, after 2026-11-22).
- status: computed/verified (rows left at 383 and at 131,072 recomputed from N alone; check.py recomputes g(N) from N with gmpy2); not packaged with certificates in records/
- uses: E_fscan, R_lowend
- where: fscan/README.md "Production runs"
- matters: shows the scanner's gain and carries an unexplained excess over expectation.

## R_fleet200 | 200-digit fleet records to 157,837
- kind: record
- says: Below 10^200 the best known value passed from 119,419 (slop, 199 digits) to 133,981 (6.3% of the 2,130,704 ceiling), then to 146,191 (6.9%) on the evening of 2026-11-22, and stood at 157,837 (7.41%) at 2026-11-23 02:40Z, with about 10 days of compute left at 29 million effective full-weight members per second; the fleet now reports near-misses (the first probable-prime row of a tested member is g(N)). The requester's figure of about 158,209 appears in none of the assigned files.
- status: conjectural (as quoted: the records live on the fleet's branch, not in this tree, and records/ holds no certificate above 112,249); the finder is not named in the files and is inferred to be the GPU fleet
- uses: M_portfolio, M_price, E_sievedepth
- where: fscan/cover/brainstorm/README.md header and "The remaining budget" (outside assigned list); brainstorm/portfolio_budget.txt
- matters: this is the frontier against which the 10% target (213,070) and all sublinear arithmetic are measured.

---

# B. Cover constructions

## C_basic | Congruence cover plus residual lottery
- kind: construction
- says: Fix N mod r for odd primes r so that q = N (mod r) forces r | N - q, and take members N = N0 + t*M with M = 2*prod r; the uncovered ("residual") primes U must have N - q composite by luck, at density e^-E with E = |U|*boost/ln N and boost = 2*prod r/(r-1), each modulus costing ln r of the ln B = D*ln 10 size budget. The 88-to-90-modulus covers for 200 digits are built by greedy weighted set cover (cover.py), annealing of ln M + E (anneal.py) and residue-swap variants (gen_variants.py).
- status: computed/verified; the density model is empirical (predicted against measured E: toy 26-digit 12.53/12.51, toy 62-digit 13.52/13.57, 197-digit record 18.2/18.2, 2,692-digit record 6.6/6.56)
- uses: M_density
- where: cover.py, anneal.py, gen_variants.py docstrings; RESULTS.md "The 1M-desert-below-200-digits question"; fscan/cover/README.md intro
- matters: every search, sieve and sublinear question is a way of finding members of such a progression.

## C_ptcover | Parallel-tempering cover optimiser
- kind: algorithm
- says: ptcover.c keeps one nonzero class per modulus per replica, moves by single-modulus Metropolis steps over 56 replicas (about 10^7 moves per second on 4 cores) and also measures the entropy S(k) of covers with about k uncovered rows. Check: on 13 moduli (3 to 43) at Q = 10,007 exhaustive enumeration gives minimum 186 reached by exactly 6 covers and ptcover finds 186 with entropy 2.15 against ln 6 = 1.79; at Q = 122,000 the entropy is 27 nats at mean k = 866 and 45 at 871 and vanishes within a few rows of the best cover (0.62 of the random mean 1,377 +- 20), so "the plateau is the optimum".
- status: computed/verified (13-modulus exhaustive check); the optimality claim is conjectural (heuristic certificate resting on equilibrium down to beta about 4, not a proof)
- uses: C_basic, C_nofomula
- where: fscan/cover/README.md "Method", "Check on a case with a known answer", "Three conclusions"
- matters: the same sampler, with every prime up to z as a modulus, produces the density of states behind the ideal-search prize (S_tilt).

## C_table88 | Best covers on 88 moduli by target
- kind: empirical
- says: On the 88 moduli of campaign 3 the best uncovered-row counts k found (E = p1*k at 200 digits) are 851 at Q = 122,000 (E 20.34), 921 at 130,000 (22.02), 1,011 at 140,000 (24.17; the other sampler found 1,007), 1,092 at 150,000 (26.10), 1,181 at 160,000 (28.23), 1,262 at 170,000 (30.17), 1,323 at 177,500 (31.63) and 1,623 at 213,070, the 10% target (E 38.80; four runs of 150,000 sweeps all ended at 1,623), against 867 for campaign 3's greedy-plus-anneal cover at 122,000. Raising the target costs 8.7 rows, 0.21 nats, per 1,000 in g, steady from 122,000 to 160,000.
- status: computed/verified (check_specs.py rechecks every spec from N0 and M alone)
- uses: C_ptcover, C_basic
- where: fscan/cover/README.md "Result for the 200-digit game"
- matters: these row counts drive every price (M_price), portfolio (M_portfolio) and the comparison in the ideal-search table (S_prize).

## C_supply | Bulk supply of near-best covers
- kind: algorithm
- says: covergen.c walks the connected set of covers with at most a cap of uncovered rows and prints each once: at Q = 150,000 cap 1,092 gives 2,282 covers but cap 1,093 gives more than 120,000 (20,000 in 5 s); at 140,000 cap 1,007 gives 65 and 1,008 about 4,800; at 170,000 caps 1,262, 1,263, 1,264 give 36, about 9,800 and more than 50,000. One more row multiplies the supply by 30 to 100 and costs 2.4% of success probability per member, so 1,700 vectors a day stay within one or two rows of the best for months; descend.sh reached 1,181 at Q = 160,000 in a minute.
- status: computed/verified
- uses: C_ptcover, C_table88
- where: fscan/cover/README.md "Vectors in bulk (covergen.c, gen_vectors.sh)"
- matters: makes vectors free, the premise for adding moduli (C_m89) and for fscan's many short progressions (E_fscan).

## C_m89 | One or two more moduli (89, 90)
- kind: empirical
- says: On the first 89 odd primes (3 to 463; M of 192.7 digits, 2.14*10^7 members per vector) the optimiser reaches 1,248 rows at Q = 170,000 and 1,609 at 213,070, against 1,262 and 1,623 on the campaign's 88 moduli, i.e. E = 30.30 against 30.53 and 39.06 against 39.27, 1.27 and 1.23 times the success rate. Two more moduli buy 14 rows (about 0.25 nats) for 5.3 digits of modulus, about +0.1 nats per modulus at 89 or 90.
- status: computed/verified
- uses: C_table88, C_supply
- where: fscan/cover/README.md "One more modulus"; brainstorm/README.md "Engineering still open" (outside assigned list)
- matters: 1,609 is also the minimum the ideal-tilt sampler finds at depth 463, anchoring the whole prize table (S_prize).

## C_nofomula | No closed formula, no floor proof
- kind: negative-result
- says: A mean-field formula (meanfield.py) predicts 682 rows at Q = 122,000 against 851 found (ratio 0.79 to 0.84 in every case), because prime by prime the greedy class is 1 to 2 rows below the largest class of a Poisson sample (6 against 7 at r = 439, 26 against 28 at r = 97, 1,436 against 1,455 at r = 5; plain greedy ends at 912). Every proof route for a floor on k is vacuous for 88 moduli (capacity about 3,500 rows for 2,957 alive after exact enumeration to 13; Hunter-Worsley inclusion-exclusion over-counts; bounded-difference and Bernstein bounds are dominated by small primes), and the Lean session's exhaustive count of all 1,021,870,080 vectors on moduli 3..29 for the 429 rows below 3,000 (minimum 67, 18 vectors) is matched by the sampler but is only evidence at full size.
- status: computed/verified (measurements); no theorem
- uses: C_ptcover
- where: fscan/cover/README.md "What does not give the optimum"; brainstorm/verdicts_on_research_ideas.txt item 2 (outside assigned list)
- matters: the sampler, not a formula, is the only tool for k_opt, so every statement of cover optimality is empirical.

## C_c15907 | Complete cover to 15,907, no luck needed
- kind: construction
- says: Tempering on the 89 smallest odd primes (3 to 463) gives classes such that every one of the 1,852 odd primes q <= 15,901 lies in the class of some modulus, so for every even N = N0 + t*M (N0 of 193 digits, 21,378,978 members below 10^200) each N - q is divisible by a prime <= 463 and g(N) >= 15,907 with no primality test; that is 0.7% of the ceiling against 7.4% for the best found by search. At Q = 15,950 and 16,000 the best covers found on these primes leave one row, so where complete covers stop is unknown.
- status: computed/verified (complete_cover.py checks divisibility for N0 and N0 + M; I re-derived M of 193 digits, 21,378,978 members and no uncovered prime below 15,907); Lean-checked per README (Cover15907.lean and Records.lean, commit c9591a7: exists_lt_ten_pow_200_complete_cover_15907, exists_progression_complete_cover_15907), not visible in this tree
- uses: C_ptcover, C_leanbound
- where: sublinear/README.md "At 200 digits, without luck"; complete_cover.py; complete_cover_15907.txt, .out
- matters: what can be constructed by divisibility alone is far behind what search finds, the same construction-versus-existence gap as for prime gaps.

## C_cmore | Complete covers on 91 and 92 primes
- kind: construction
- says: Adding 467 and 479 (91 primes, M of 199 digits, 95 members below 10^200) gives a complete cover to 16,381 (1,898 rows, N0 of 198 digits). On 92 primes (to 487, M of 201 digits, about 5.1 times 10^200) tempering found 17,131 complete covers at 16,500 and 16,600, of which 3,505 (20.5% against 19.5% expected) have their number below 10^200, and the best certifies 16,747 (1,934 rows, one 200-digit N).
- status: computed/verified (complete_cover.py; I re-derived the member counts 95 and 1, the digit counts and zero uncovered rows)
- uses: C_c15907, S_b_crt
- where: sublinear/README.md "At 200 digits, without luck"; complete_cover_16381_91primes.txt/.out, complete_cover_16747_92primes.txt/.out
- matters: one prime beyond the Chinese-remainder line can be bought by enumeration, exactly as the line's sharpness predicts.

## C_leanbound | Provable covering lower bound 1.349
- kind: theorem
- says: The maximum of g(N) over even N <= X is at least (e^gamma/(2*C2) - o(1))*ln X*ln ln X with e^gamma/(2*C2) = 1.349 (C2 the twin-prime constant), by giving the primes up to alpha*y random nonzero classes (an odd prime q < Q stays uncovered with probability about 2*C2*e^-gamma/ln(alpha*y)) and each remaining row a prime of (alpha*y, y] of its own. The Lean versions are eventually_exists_even_le_no_summand (constant 0.73, from prod (r-2)/(r-1) <= (1575/1152)/ln(w+1)), eventually_exists_even_le_of_mul_lt_one (every constant below 1.349) and the explicit constant 1.2; the unrefereed counting bound (1/2 + o(1))*ln X*ln ln X is W. Shi arXiv:2605.21529 Thm 6.22, and at y = 463 the theorem's count gives 3,830 while greedy covers every prime below 6,000 and tempering reaches 15,907.
- status: Lean-checked per README (CoverBound.lean commit 4a747b6 and a4c5d0f; Mertens.lean mertens_third from Mathlib alone; Counting.lean constant 1/48; branch ccr-36ca7b46-8twf14, standard axioms only), not visible here; proved-in-text as Theorem 1 of phd/wp12 section 2 (outside assigned list)
- uses: C_basic, ext:Mertens-third-theorem, ext:Shi-arXiv-2605.21529, ext:twin-prime-constant
- where: sublinear/README.md "A provable lower bound"; phd/wp12_prime_covering_grh_ledger.md section 2; RESULTS.md "Prior-art check" addendum
- matters: the only provable lower bound on the maximal order known to the team, a logarithm below the conjectured ln^2 N ln ln N (Granville, van de Lune, te Riele 1989).

## C_wp12ceil | Ceiling for covering certificates x^(4+eps)
- kind: theorem
- says: Residue classes modulo primes <= x can cover the primes below Q only if Q <= x^(4+eps), or x^(2+eps) under Elliott-Halberstam, by the linear sieve with Bombieri-Vinogradov to level Q^(1/2-eps); with x about ln N this confines covers to (1.349 - o(1))*ln N*ln ln N <= g <= (ln N)^(4+eps) while the data say about ln N*(ln ln N)^2, and greedy covers track Q = 0.72*x*ln^2 x over four decades.
- status: proved-in-text (wp12 Theorem 2), with the cross-review caveat that it is asymptotic and vacuous at record parameters (moduli to 79,139, Q <= 2*10^6; the finite-size sieve floor is negative at level Q^(1/2))
- uses: C_leanbound, ext:Bombieri-Vinogradov
- where: phd/wp12_prime_covering_grh_ledger.md section 2 (outside assigned list); cited in RESULTS.md and proth/README.md "Covers"
- matters: the rigorous shadow of the construction-versus-existence gap, though no help at record size.

## C_joint | Joint representative and coverage constructions
- kind: construction
- says: joint.py minimises Phi = E - ln K(x, M; B) and uses a multiple-choice modular meet-in-the-middle (Wagner-style, 2^d lists) to place CRT representatives below 10^197 for oversize moduli: constructions/m211_x196.json (211-digit modulus, 196-digit representative, 738 residual primes, E 18.09, a better cover than the record's own 752), m219_x197.json (784 residuals, E 19.33) and m221_x197.json (221-digit modulus, 24.3 digits cancelled, 83 solutions, about 25 min and 8 GB on 4 cores, 782 residuals, E 19.32). There is no structural small-x bias (deciles of x/M uniform): the gain equals the entropy of the residue search.
- status: computed/verified (each file re-verified end to end: x = a_r mod r for all 96-99 congruences, x < 10^197, residual set recomputed)
- uses: C_basic, S_b_mitm
- where: RESULTS.md "Joint representative/coverage optimization (2026-07-22)"; constructions/m211_x196.json, m219_x197.json, m221_x197.json
- matters: the measured instance of going past the Chinese-remainder line by enumeration; it costs 10 to 10^4 times more per candidate than a sieved scan, so it did not improve the bounded records.

## C_1Mwall | The 1M-desert wall and blueprint
- kind: negative-result
- says: For g > 10^6 below 200 digits the failure exponent E(D) at Q = 10^6 is 196.7 at 199 digits (91 moduli, 8,157 residuals, cost 10^85.4), 124.3 at 300, 89.3 at 400, 28.4 at 1,000 and 6.9 at 2,400 digits; the best annealed 199-digit system (constructions/wall_1M_199d.json) has 8,146 residuals and E = 196.4, annealing recovering only 0.3%. The existence heuristic (E_random about 445) says about 10^6.5 such N exist below 10^200 yet the cheapest known exhibition costs 10^85 tests, while the practical blueprint (constructions/blueprint_1M_1250d.json: 420 moduli, M of 1,247 digits, 4,205 residuals, E = 20.74, about 10^9 elements, 235 core-days at 50 candidates per second) needs about 1,250 digits.
- status: computed/verified (both constructions verified); the existence count is a heuristic
- uses: C_basic, M_density
- where: RESULTS.md "The 1M-desert-below-200-digits question (2026-07-22)"; constructions/wall_1M_199d.json, blueprint_1M_1250d.json
- matters: puts a number on the construction-versus-existence gap (10^6.5 numbers exist, 10^85 tests to find one).

## C_bls | Proth/BLS construction and cost ladder
- kind: construction
- says: Take a cover of all primes below Q, let g be the least prime above Q in no class and look for N with P = N - g = m*2^n + 1; the cover congruences become congruences on m, CRT gives m = m0 (mod M_c), and with 2^(3n) > P one modular exponentiation b^((P-1)/2) = -1 (mod P) plus one integer square root (Brillhart-Lehmer-Selfridge 1975, F^3 > P) proves P prime, so every q < g has an explicit divisor and there is no lottery, no witness and no ECPP. The 4-core GMP ladder (cover digits / digits of N / expected tests) is 7,503 / 11,263 / 703 for 1.2M, 10,392 / 15,595 / 973 for 2M, 14,617 / 21,936 / 1,369 for 3M, 22,620 / 33,938 / 2,118 for 5M, 40,881 / 61,329 / 3,827 for 10M and 61,162 / 91,753 / 5,725 for 16,045,848, the largest known prime gap of any kind (about 13 days, costed but not run); lazy covers are about 10% shorter than the paper's increasing-order covers.
- status: proved-in-text (the BLS argument, witness base chosen among cover moduli with Jacobi symbol -1) and computed/verified in four records; the rows not marked done are costed projections; Lean formalisation not done (proth/README: toolchain install refused)
- uses: C_basic, ext:Brillhart-Lehmer-Selfridge-1975
- where: proth/README.md "The construction", "Cost model and the ladder", "Lean"; phd/wp11_bls_game1.md (outside assigned list)
- matters: moves the height game from ECPP-limited (about 2.5*10^6 per the SoK) to PRP-limited and puts the 16M rung within about two weeks of 4 cores.

---

# C. Search engine and kernels

## E_search | search.py: sieved progression search
- kind: algorithm
- says: For a cover spec (N0, M, residual primes U, Q) it scans k upward, sieves the residual rows by primes s <= B (B = 10^6 the measured optimum), Fermat base-2 tests the survivors (a failure proves compositeness, a pass kills k), re-verifies successes with BPSW over all primes below Q and computes g by scanning q >= Q. About 1,850 progression elements per second on 4 cores (0.3 million k per second on the 30-digit job); the ascending-survivor test order (--sort-tests) measured a 1.8 times conditional discovery gain.
- status: computed/verified
- uses: C_basic, M_density, M_selection
- where: search.py docstring; RESULTS.md records of 2026-07-21 and 2026-07-25; tscan/README.md measured table
- matters: the baseline engine against which every faster kernel is quoted.

## E_gpu150 | CUDA scanner and Colab fleet protocol
- kind: algorithm
- says: engine150.py sieves a k-tile into a bit matrix alive[|U|][tile] and then runs "wave" kernels in which every alive k locates its next surviving residual and runs a Montgomery CIOS base-2 Fermat chain (a k that drains all survivors without a pass is a success, same semantics as search.py); it is validated bit for bit against Python, runs about 2.5M tests/s on a T4 and 8.5M tests/s on an A100 (about 430 times the 4-core CPU pipeline), and fleet.py shards k-ranges over Colab sessions with git-committed safe_k checkpoints (HARVEST FIRST), which survived about 10 session culls with zero coverage loss. Later kernels (28-bit limbs, dedicated squaring) reach 22.9M tests/s on an RTX PRO 6000, an all-GPU sieve at 2.7 ns a member (B = 10^6, windows of 2^19, 3% kept), 4.8M full-weight members/s per card and 18.7M for the fleet.
- status: computed/verified (the later-kernel figures are quoted from the research session's verdict file, not measured here)
- uses: E_search, E_sievedepth
- where: gpu/engine150.py and gpu/fleet.py docstrings; RESULTS.md "New record (2026-07-26)"; brainstorm/verdicts_on_lean_ideas.txt header (outside assigned list)
- matters: throughput moved the 200-digit frontier: ln 430 = 6.1 nats matches the gap in E between rungs.

## E_tscan | tscan: C scanner with selection by rows left
- kind: algorithm
- says: tscan.c bit-sieves a block of 2^18 consecutive k to B = 131,072, counts the rows a(k) still alive and Fermat-tests only the k with a(k) <= T (a k succeeds with probability about (1 - p)^a(k), p about 0.35), stopping at the first probable prime; it does 16-19M k/s at 27 digits (testing 1.26% of k, which hold 61-66% of the successes), 10.8M k/s at 46 digits (1.09%, 27-28%) and 6.3M k/s at 63 digits (0.86%, 16-17%), about 35 times search.py per second. vscan.py scans many near-optimal residue vectors in lockstep (for the 13 primes <= 43 at Q = 10,007 there are 6 vectors with 186 residual primes, 28 with 187, 157 with 188, 818 with 189, 3,523 with 190, 13,676 with 191), always advancing the lowest progression so that the first success is the smallest N (in simulation 100% of runs against 18% class by class and 1% densest first).
- status: computed/verified (selftest.py against gmpy2 and brute force; over its test instances and the four record searches it predicted 138 successes and found 145)
- uses: E_search, M_selection, M_density
- where: tscan/README.md; RESULTS.md "Successes of the scanner"
- matters: established the select-by-rows-left rule (the "3% rule") that production still uses.

## E_fscan | fscan: score first, test in bulk
- kind: algorithm
- says: It adds 64 consecutive members' scores per unaligned byte-table add (62 primes from 47 to 383, 1.35 cycles per member, correlation 0.87 with the exact count), computes exact rows only for the 0.8% above threshold (about 90 cycles), then Fermat-tests the remaining 0.3% 24 at a time with a 52-bit IFMA kernel at 119 cycles per test (about 20 times cheaper than tscan's 2,500-cycle scalar test); a member costs 4 to 6 cycles instead of 418, giving 4.5 times tscan's expected successes per core-second (7*10^-5 against 1.5*10^-5) although only 5-7% of a progression's expected successes are tested, which is paid for with 154,098 / 467,071 / 1,346,301 / 3,714,537 vectors at 193 / 194 / 195 / 196 residual primes. One expected success below 10^23 needs about 30-35 core-hours against 100-130 for tscan; classes 193-195 found none against 0.35 expected (probability 0.70); an AVX2-only build uses fermat26.h at about 450 cycles per test and is 1.85 times slower.
- status: computed/verified (test_fermat.py: 152,907 numbers, 43,097 probable primes, no mismatch with pow(2, n-1, n); check_small.py agrees with brute force on 168 vectors; the vector enumeration reproduces variants.py's 18,208 vectors)
- uses: E_tscan, E_fermat26, C_supply
- where: fscan/README.md
- matters: the repo's clearest "score first" selection, and it shows the gain is a constant factor, not a better exponent.

## E_fscan_neg | fscan: what did not work
- kind: negative-result
- says: (1) A search over more than 13 fixed primes, or a tree or beam search scored by the exact success probability, trades share against enrichment at the same rate because ln(success probability) is close to a sum of many small independent terms (selecting the best fraction f multiplies the mass by about exp(|z_f|*sigma) and costs a factor 1/f; the primes 47 to 383 contribute sigma of about 1.2 in total, 47 alone 0.28), so cost is decided by the price of looking (400 cycles for the full sieve, 1.35 for the byte score). (2) Sharing the sieve between nearby N by an exhaustive interval search (about 7 cycles per N, not built) loses to tscan by a factor 2-3 at 25 digits because its candidates are typical numbers 100-200 times less likely to succeed; the cost per digit stays above 3.8 (measured 8.0*10^-6, 2.4*10^-6, 4.3*10^-7, 1.3*10^-7 expected successes per core-second below 10^23, 10^22, 10^21, 3*10^20, i.e. about 30, 220, 2,700, 18,000 core-hours per expected success), and per-vector setup of 60,000 cycles is 17% of a run below 10^21 and 60% below 3*10^20.
- status: computed/verified (measurements); an earlier version of the file said 4.3 per digit at 23 digits and 5.5 at 21, which was too optimistic (see X_corrections)
- uses: E_fscan, M_selection, S_b_score
- where: fscan/README.md "What did not work, and why"
- matters: an early measured form of the claim that selection cannot beat enumeration plus a cheap score, which S_b_score extends to 200 digits.

## E_fermat26 | 3-limb Montgomery step, stated for a proof
- kind: proposition
- says: The 3-limb (30-bit limbs, R = 2^90) squaring-and-reduce step FM3_STEP of fermat26.h, used for odd n with 2^40 < n < 2^86, is exact (Y = 2^b*(A^2 + mu*n)/R, so Y = 2^b*A^2*R^-1 mod n), range-preserving (A < 4n maps to Y < 4n), overflow-free (every intermediate below 2^62; the largest value seen over millions of random and adversarial steps was 2^61.89) and uses only multiplier operands below 2^32; after t steps the lane holds 2^(1-n) mod n and the verdict is y == 1.
- status: proved-in-text (claims C1 to C4 with an exact bounds table); computed/verified (model3.py exact-integer mirror; test_fermat.py and stress_fermat.py, about 1.5 million numbers of 41 to 100 bits including Carmichael cases; check_record.sh); not Lean-checked
- uses: E_fscan
- where: fscan/FERMAT26_STEP.md
- matters: a false "prime" verdict silently kills a success, so kernel correctness is a soundness property of the search.

## E_prothgpu | GPU screening and deep sieve
- kind: algorithm
- says: gpu_screen.py computes 2^((P-1)/2) mod P for batches P_t = 1 + 2^n*(m0 + t*Mc) with 15-bit limbs in float64, batched cuFFT convolutions, Montgomery reduction (R = 2^(15L) > 16P) and an exact carry-lookahead kernel for long 0x7FFF runs; it takes 0.82-0.92 s per test at 5*10^6 (about 100 times one GMP core), 2.76 s (v2) and 2.35 s (v3) at 10^7 (about 130 times) and 6.10 s (v3) at 16M, with v3 bit-for-bit equal to v2 over 40-64 squarings. The sieve is deepened during the run (deepsieve.c via mpn_mod_1, 8-9 times faster per core), removing about 18% of expected tests at 10^11 and 25% at 10^12, and a CPU fleet of 8-vCPU runtimes at about 29 tests per hour each runs beside the GPU.
- status: computed/verified (each engine version validated against gmpy2; the known primes of the 1.2*10^6 progression pass and 16 neighbours fail); a wrong GPU answer can cost time but never a wrong record because every pass is re-proved on the CPU
- uses: C_bls, E_verify
- where: proth/README.md "GPU screening (Colab A100)"
- matters: made g = 5*10^6 and 10^7 feasible within an evening and the 16M rung plausible.

## E_verify | Three-leg verification stack
- kind: construction
- says: Every height record passes three independently written legs (proth/verify.py, stdlib only, 6 s with gmpy2 and 102 s with plain ints; bls/verify_bls_record.py and bls/xverify.py, which rebuild N from the congruences by product-tree CRT; and PARI's own N-1 certificate plus a brute-force gcd scan in crosscheck.gp), older records carry a PARI ECPP certificate re-checked by ecpp_check.py plus a compositeness witness per prime (parity, cover divisor, trial divisor < 10^5, failed strong base-2 test), and tamper_test.py rejects 11/11 mutated records. A fail-open flaw was found on 2026-11-22: gp carries on after an error, so older crosscheck scripts could print "valid" and "PASSED" after a failure; no committed log has an error line besides a stack-size warning, and package.py is now fail-stop.
- status: computed/verified
- uses: C_bls, R_height_ecpp_free
- where: proth/README.md "Independent replication, and the verification stack"; bls/README.md; ecpp_check.py docstring; RESULTS.md
- matters: no record rests on the scanner that found it.

## E_sievedepth | Deeper sieve bound in production
- kind: empirical
- says: sieve_depth.py models full-weight members per second per card against the cost of a mark by a prime above the window: production at B = 2^20 with 3% kept is 4.64M, the model gives 8.4M at B = 2^24, 11.2M at 2^28 and 14.1M at 2^32 if a large-prime mark costs 0.0033 ns, 6.0, 6.7 and 7.5 at 0.03 ns and nothing at 0.1 ns. It has been in production since 23 Nov 01:30Z on the three RTX PRO 6000 at B = 10^8 (bucketed large-prime stage, measured mark cost 0.030 ns; the L4 at 0.10 ns stays at 10^6), giving 1.38 times the expected successes per batch for 1.05 times the time, 1.32 times per second, about +28% for the fleet.
- status: computed/verified (the model reproduces the fleet's measured 15.6% of the successes held by the emptiest 3%)
- uses: M_selection, E_gpu150, C_m89
- where: fscan/cover/brainstorm/README.md "Engineering still open" and sieve_depth.txt (outside assigned list)
- matters: the only remaining engineering lever above 0.3 nats, and it is a constant factor.

---

# D. Selection, tilt and frontier models

## M_density | Success-density model E = |U|*boost/ln N
- kind: empirical
- says: A member of a progression succeeds when all |U| residual complements are composite; each is odd and coprime to the cover so prime with probability p = boost/ln N, boost = 2*prod r/(r-1), giving density e^-E with E = |U|*p, and after sieving to depth z a member with k rows left succeeds with probability (1 - p_z)^k, p_z = 2*prod(3<=s<=z) s/(s-1) / ln N. Predicted against measured E: toy 26 digits 12.53/12.51, toy 62 digits 13.52/13.57, 197-digit record 18.2/18.2, 2,692-digit record 6.6/6.56; tscan predicted 138 successes and found 145; at Q = 7,001 fscan found 50 against 48.7 expected (mean overshoot g - Q 316 against 307).
- status: computed/verified as an empirical model; conjectural as a statement of independence of rows (fscan measures a pair correction c2 = -2.39*10^-4 per pair at Q = 10,007, L = 383)
- uses: C_basic
- where: cover.py docstring; RESULTS.md first section and "1M-desert" section; fscan/README.md "What 'expected' means, and its correction"
- matters: every price in this ledger, and the ideal-search counts, come from this model.

## M_ceiling | Hardy-Littlewood ceiling for g(N)
- kind: empirical
- says: ceiling_model.py computes the largest g expected below N from the Hardy-Littlewood prime-tuple heuristic with no fitted constant (P(g >= y) = average over residues of (1 - eps_z)^(surviving odd primes below y), eps_z = (1/ln N)*prod(1 - 1/q)^-1); the median ceiling is 9,570 at 19 digits, 19,740 at 25, 98,250 at 50, 465,350 at 100, 1.14 million at 150 and 2.13 million (2,130,704) at 200, and its ratio to ln^2 N ln ln N rises from 1.40 to 1.64 (the candidate limits 1/C2 = 1.515 and 2*e^-gamma/C2 = 1.701 attributed to Granville cannot be told apart). Checks: 600 million random even N in [10^18, 1.1*10^18) agree within 0.5% from y = 11 to 1,801 and within 2% to 2,203 (75 numbers with g >= 3,001 against 69 expected); the 35 record holders above 10^9 arrive early (median expected-earlier count 0.29 against 0.69), so the line may be 1.5% too low (not corrected).
- status: conjectural (a prediction, nothing about the size of g is proved); validated empirically as listed
- uses: M_density
- where: ceiling_model.py docstring; RESULTS.md "The 100% line, computed instead of fitted"; closeness.py
- matters: defines the yardsticks "10% = 213,070" and "7.41%" used throughout the campaign.

## M_selection | Selection identity and hit mass
- kind: proposition
- says: If the count of rows left R over members is Normal(mu, sd^2) and a member with R rows succeeds with probability (1 - p)^R, the members with R <= mu - z*sd hold the fraction Phi(lambda - z) of all successes, lambda = -sd*ln(1 - p), exact for the normal. Measured on 131,072 members of a Q = 130,000 vector: at sieve depth 2^17 the rows left are 483.0 +- 14.7 (p = 0.0456) and the emptiest 0.1%, 1%, 8% hold 0.8%, 5.0%, 23.7% of the hit mass against 0.9, 5.3, 24.3 for the binomial model; at 2^28, 293.3 +- 14.0 and 2.2%, 10.5%, 37.1% against 2.4, 11.1, 38.2; the fleet's 3% rule holds 15.6%, worth 2.0 nats.
- status: computed/verified (selection_check.py tables); the identity is exact for the normal (proved-in-text in the verdict file) and approximate for the real distribution, which is less spread than binomial (model 5-10% optimistic in the tail); the Lean theorems Cap.expected_hits and test_order are cited in the verdict files
- uses: M_density
- where: fscan/cover/README.md "Which members to test"; brainstorm/verdicts_on_lean_ideas.txt last paragraph (outside assigned list); sublinear/README.md Result 3 caveat (ii)
- matters: selection is the only gain over plain enumeration, and the ideal-search tables are costed on top of it.

## M_frailty | Low-threshold checks find no hidden slack
- kind: empirical
- says: frailty200.py runs the 200-digit search at Q = 40,000, 60,000, 75,000 where successes are common and finds 251, 85, 20 against 255.9, 91.9, 18.7 expected (356 against 366.5), with 40.0, 39.6, 56.2 rows surviving beyond Q (model 40.8, mean observed 40.8) and a hazard of 0.0349 for the next tested row to be a probable prime whatever the number of composite rows already seen (4*10^7 tests at 75,000). With the fleet's selection (Q = 60,000, 60.8 million members) it found 1,188 against 1,175.7 expected and an overshoot of 41.0 against 40.8 (ratio 1.004 +- 0.029); the early excess (four successes that ran 2.2 times further than expected) was judged chance, and the fleet's 8 found against about 8.6 (README) or 9.0 (verdict file) expected is within chance (z = 1.7 for the overshoot of nine successes).
- status: computed/verified
- uses: M_density, M_selection
- where: fscan/cover/brainstorm/README.md "Checks of the model made for this exchange"; overshoot_selected.txt (outside assigned list)
- matters: no unmodelled effect to exploit, so the model's price list can be trusted.

## M_setvalued | Set-valued conditioning buys only 1 to 2.8 nats
- kind: negative-result
- says: Constraining N mod r to a set of k residues (cost ln(r/k) instead of ln r) in the exact CRT survival model lowers E from 43.84 to 41.83 at 100 digits, 34.25 to 32.67 at 120, 31.62 to 29.23 at 130, 29.36 to 26.53 at 140 and 25.55 to 24.47 at 150 (gains 2.0, 1.6, 2.4, 2.8, 1.1 nats), and the optimiser never uses a modulus above 1,123. The Gaussian extreme-value prediction sqrt(2*H*sum P_r) (about 3,400 extra covered primes at 100 digits) is an unattainable upper bound: the measured gain scales like H^0.35, not H^0.5, because sum P_r is about 25,000 against 9,591 targets (overlap) and large classes hold 0 or 1 target (Poisson discreteness).
- status: computed/verified (entropy_frontier.py, frontier_table.py; the k = 1 case reproduces the validated E to 0.3% and the 150-digit prediction 25.55 against 24.91 measured)
- uses: M_density, C_basic
- where: FRONTIER.md "Result 1" and "Result 2"
- matters: weaker conditioning cannot break the wall, the same lesson as the oracle floor (M_oracle).

## M_realizable | Enumerability constraint: the classic cover is optimal
- kind: proposition
- says: Free enumeration by progression scanning needs M1 = prod of conditioned moduli <= B, so the candidate pool is exp(rho + Lambda) with rho = ln B - ln M1 and Lambda = sum ln k_r; realizable E is 43.66 at 100 digits (10^19.0 candidates, M of 78 digits, pure k-room) and 27.50 at 140 digits (10^11.9 candidates, k-room e^20 plus multiplicity e^12.4), and multiplicity is nearly free (12.4 nats of candidates for 0.15 nats of E) but redundant (k-room costs about 0.05 nats of E per nat of candidates), net gain about 0.2 nats. FRONTIER.md concludes that the classic cover is "the unique design whose admissible set is an arithmetic progression, i.e. free to enumerate".
- status: computed/verified (realizable_frontier.py); the "unique design" statement is an interpretation (conjectural)
- uses: M_setvalued, S_b_crt
- where: FRONTIER.md "Result 3"
- matters: the first statement of the enumerability principle that the sublinear programme tries to circumvent.

## M_wall100 | Sub-100-digit wall and the reachable band
- kind: verdict
- says: g > 100,000 below 10^100 costs 9.1*10^18 candidates, about 193,000 GPU-years at an optimistic 1.5M candidates per second or 19 years on 10,000 GPUs ("roughly seven orders of magnitude beyond plausible compute"); for a two-session Colab fleet at a measured 7.9*10^5 candidates per second end to end the reachable band is 150 digits at 10^11.1 candidates (about 2 days, matching the banked record campaign), 140 digits at 10^11.9 (about 13 days), 135 at 10^12.5 (about 47 days) and 130 at 10^13.0 (about 5 months), so 137-140 digits is the deepest rung of a week-to-fortnight campaign. PROPOSAL_NEXT_CAMPAIGNS.md (citing WP3) puts the rungs after about 142 at about 135 (10 fleet-weeks), 127-130 (about 10^2 GPU-years), a practical wall at 120-125 digits and sub-100 at about 5*10^4 GPU-years.
- status: conjectural (extrapolations from the validated density model); the GPU-year figures disagree between files (see Doubts)
- uses: M_realizable, M_density, M_wp3
- where: FRONTIER.md "Verdict"; PROPOSAL_NEXT_CAMPAIGNS.md "Where the ladder ends"
- matters: fixes the digit-count scale of the T(100,000) game.

## M_wp3 | WP3 decoding barrier and retraction of "open window"
- kind: retraction
- says: Version 1 of the WP3 memo claimed a polynomial-time CRT-decoding escape for oversized covers ("open window") but compared the decoding radius at one agreement size with an existence bound maximised at a different one; at the same cover mass A the window is closed at every pool size (verify_barrier.py, Legendre transform): pool R = 1,000, A_max 339 against A_J 469 (ratio 0.723); R = 60,000, 570 against 3,711 (0.154); R = 60,000 with L = 16, 1,305 against 14,845 (0.088); R = 10^6, L = 16, 1,697 against 60,651 (0.028), and the computed radius at R = 60,000, L = 16 reproduces WP3's 14,845 nats exactly. Corrected costs: the conventional sub-100 optimum is 44 moduli, M = 10^79, 1,060 residuals, E = 44.1 (1.4*10^19 candidates), while oversized covers (420 moduli, 165 residuals, E = 10.2, about 2.7*10^4 candidates) would be easy but their small representatives have design-space density e^-2630, a modular subset-sum at density 1.026 (lattice attacks need below 0.94; a Wagner k-tree needs 2^938).
- status: retracted (the v1 claim); the corrected barrier is computed/verified (verify_barrier.py)
- uses: S_b_mitm, S_b_lattice, ext:Guruswami-Sudan-2000
- where: FRONTIER.md "Independent verification of the WP3 decoding barrier (2026-07-28)"; phd/RESEARCH_LOG.md "2026-07-28 RETRACTION" (outside assigned list); phd/wp3_small_representative_memo.md
- matters: the first formulation of the "decode a CRT code beyond the Johnson radius" barrier that the sublinear programme inherits.

## M_wp7 | Algebraic-mechanism probes all terminate
- kind: negative-result
- says: Five bounded probes (2026-07-28, predeclared gates, benchmark about 4,400 offsets per nat at r = 3 falling to about 0.4 at r about 1,200) all terminated: prime-power moduli kill nothing new (p^2 costs ln p more); identities N = m^k - c kill at most O(Q^(1/2)) offsets (113 below 10^5 at k = 2, 26 times worse than covering, about 316 at any price, about 8% landing in the residual set); Sierpinski-Riesel exponent families reduce to covering (at best a constant-factor sieve-sharing trick); norm forms and splitting conditions reduce to congruences mod disc K; and the residual-bias loophole is bounded (|E_measured - E| <= 0.1 over three covers and about 1.2*10^9 candidates). A genuine mechanism must certify far more than Q^(1/2) offsets, cost o(ln r) nats per offset and stay invisible in bulk density statistics.
- status: computed/verified (probes executed); the Q^(1/2) ceiling is a mini-proposition proved-in-text
- uses: C_basic, M_density
- where: phd/wp7_probes.md (outside assigned list; cited by sublinear/README.md "every algebraic certificate tried so far" and PROPOSAL_NEXT_CAMPAIGNS.md Campaign D)
- matters: the three requirements it states are the bar that the function-field parity mechanism does not clear over the integers (S_intgap).

## M_closure | Divisor-paradigm closure theorem (conditional draft)
- kind: negative-result
- says: WP9 states that no certificate scheme whose compositeness witnesses are planted divisor identities can beat covering, because certifying an offset costs at least the covering marginal ln d (congruence classes), has at most O(Q^(1/k)) offsets at any price (polynomial value sets, at most 349 offsets), or must factor; Lemma 2(i) shows a divisor of N - q1 and N - q2 divides q1 - q2 and so lies below Q. A sweep of 13,661 hand-enumerated schema instances plus 41 LLM-evolved programs found zero passes (best budget-aware fitness 0.0919: 209 affordable offsets at 2.197 nats each against more than 1,048 needed at under 0.44), and the first evolutionary run exposed a 50 times accounting error in the author's own evaluator.
- status: proved-in-text at draft rigor on the grammar L, conditional on H1 (Hardy-Littlewood independence of shifted primes given divisor data, unproved) and H2 (no compositeness test cheaper than one modular exponentiation on rough inputs, open); mechanisms outside L are not excluded
- uses: M_wp7, M_density
- where: phd/wp9/wp9_closure_theorem.md sections 2-3, 14 (draft v0.1, 2026-07-29) and phd/wp9/h2_open_problem.md (outside assigned list)
- matters: the prior, theory-side version of the claim that nothing but covering and trial makes N - q composite; its H2 is the integer counterpart of rung 5 in S_ladder.

## M_price | Price list: what raising the target costs
- kind: empirical
- says: At 200 digits (success per full-weight member 0.89*(1 - p)^k; one RTX PRO 6000 does 4.8M full-weight members/s, the fleet 18.7M/s) one expected success costs 0.8 card-days (0.21 fleet-days) at design Q = 150,000 (1,093 rows, E 26.13), 7.7 at 160,000 (1,185, 28.33), 49 at 170,000 (1,262, 30.17), 436 at 180,000, 3,406 at 190,000, 26,627 at 200,000 and 400,099 card-days (1,100 card-years, 102,699 fleet-days) at 213,070 (1,634 rows, E 39.06). A success lands about 4,100 above the design Q, every +10,000 in g costs a factor 8 to 9 and 20% needs E near 80; for a fixed fraction of the ceiling E grows like the number of digits (50% needs about 0.4*ln N nats: 19.7 at 23 digits, 36.5 at 40, 99.8 at 100, 209.2 at 200, versus 38.9 for 10% at 200 digits).
- status: computed/verified (model-based prices from price_list.py and closeness_cost.py)
- uses: M_density, C_table88
- where: fscan/cover/brainstorm/README.md "What the search costs" and price_list.txt (outside assigned list); fscan/cover/README.md "What a given closeness costs at each size of N"
- matters: the baseline against which the sublinear prize (S_prize) is quoted.

## M_portfolio | Expected record from the remaining budget
- kind: empirical
- says: From a record in hand of 157,837 with 10 fleet-days at 29.0M effective full-weight members per second, the expected final record with near-misses counted is 168,933 (7.93%) for a cover designed at Q = 150,000, 171,248 at 160,000, 172,260 at 167,500, 172,280 at 170,000, 172,489 (8.10%) at 172,500 and 169,973 at 180,000, flat from 167,500 to 175,000, against only 165,473 at 175,000 when only successes count. For the 10% event (9 fleet-days) the best design is the cover built for 213,070 itself (1,623 rows, chance 0.0177%, 50,749 fleet-days for one expected crossing, about 5,600 times the remaining budget), which yields only 164,488 expected; a week of the fleet is worth about 167,000 (7.9%), a month 174,000 (8.2%), a year 186,000 (8.7%).
- status: computed/verified (portfolio_budget.py, reach_target.py); the week/month/year figures are model extrapolations from the Lean session's portfolio.py
- uses: M_price, C_table88, R_fleet200
- where: fscan/cover/brainstorm/README.md "The remaining budget", portfolio_budget.txt, reach_target.txt (outside assigned list)
- matters: sets the budget of e^30.75 members (my arithmetic: about 9 fleet-days at 29M/s) used in every sublinear table.

## M_oracle | Oracle floor and the "two budgets"
- kind: empirical
- says: Requiring a representative below 10^200, the best residue vector for Q = 213,070 leaves E = 38.8, 37.3, 35.9, 34.5 with 100, 120, 150, 200 moduli against 39.2 for the 88 in use (oracle_213070.txt gives 38.27, 36.78, 35.43, 34.01 plus 0.5 because a success needs e^E representatives; with no size limit 37.58, 34.86, 31.21, 25.75), and the Lean session's explicit product-measure family (cover on the first m moduli, other primes r <= z drawn with weight exp(theta*rows killed)) reaches E = 39.08 with primes to 547, 36.99 to 1,229, 33.85 to 10,007, 31.36 to 213,070, 29.93 to 10^6 and 29.00 to 10^7 (cover on 52 moduli, theta 0.40, 198 nats in the tilt), refuting the claim "E >= 33 for every modulus set". Two budgets: a prime used constructively costs ln r of the 460.5 nats whether one class or many (the campaign's allocation is optimal to about 0.2 nats), while information beyond that can only be collected by enumerating members and counting rows, one nat of work per nat of information (or ln of the list size free by a merge of lists).
- status: computed/verified (exact sums by oracle_tilt.py; floor by the sampler); the family is an upper bound on the floor (product measure, cover not re-optimised)
- uses: C_table88, S_b_crt, M_density
- where: fscan/cover/brainstorm/README.md "Result" and oracle_213070.txt; verdicts_on_research_ideas.txt "TWO BUDGETS" (outside assigned list)
- matters: sizes the prize beyond the modulus budget at about 10 nats, which S_question asks to locate without enumeration.

---

# E. Sublinear programme and the function-field toy

## S_question | The sublinear search question and its origin
- kind: open-problem
- says: Given the rows R, the progression N0 + t*M (0 <= t < K) and sieve primes s <= z, find t for which the number of rows q with N0 + t*M - q free of prime factors <= z is far below its mean, in time sublinear in K; more generally find any way of making many N - q composite that is neither a covering congruence (ln r of the 460.5 nats of 10^200 per prime) nor trial. It arose from the 22 November brainstorm, which called it "the one open door" (worth about 10 nats, i.e. 10% within a fleet-week and not 20%); the programme began 23 November 2026 with the user's pointer to alpo.ge/remark.pdf, from which only the method was taken (find a function-field toy, look for the native integer counterpart, formalise as you go) and whose claimed RH proof nothing relies on.
- status: conjectural (open problem)
- uses: V_brainstorm, M_oracle, V_wp10
- where: sublinear/README.md "The question" and "What the note remark.pdf contributed"; fscan/cover/brainstorm/README.md "Result" (outside assigned list)
- matters: this is the whole programme.

## F_parity | Parity theorem for N - Q over F_q[x]
- kind: theorem
- says: Let q be odd, N in F_q[x] of degree n with leading coefficient lambda and N' = 0, Q monic irreducible of degree d < n with p not dividing d, and N vanishing at every root of Q'; then N - Q is squarefree and its number r of irreducible factors satisfies (-1)^(n-r) = chi(-1)^A * chi(lambda)^(n-d-1) * chi(-d)^n * chi(d)^d * (-1)^(d-1) with A = n(n-1)/2 + n(d-1) + (d-1) + d(d-1)/2, so r has the same parity for all such Q of one degree and when it is even every N - Q is reducible without any factor being exhibited. The proof uses f' = -Q', the discriminant through resultants and Stickelberger-Swan; the Lean session derived it independently as one identity over any field, discr(N - Q) = (-1)^(n(n-1)/2 + nd + (d-1) + d(d-1)/2) * lambda^(n-d-1) * d^(n-d) * discr(Q).
- status: Lean-checked per README (ParityDesert.lean: the identity, squarefreeness, the parity formula, the deserts; branch ccr-36ca7b46-8twf14, standard axioms only), not visible here; I confirmed the formula on four rows of parity_desert.txt (F_3, d = 2, deg N = 9 and 12, both kinds of lambda)
- uses: F_stick, ext:Stickelberger-Swan-theorem
- where: sublinear/README.md "Result 1"
- matters: the proof of concept that a compositeness mechanism that is neither a small factor nor luck exists in a toy setting.

## F_stick | First formal proof of Stickelberger-Swan
- kind: theorem
- says: For a finite field of odd characteristic and every squarefree g, chi(discr g) = (-1)^(deg g + number of irreducible factors); it was not in Mathlib and, as far as either session knows, this is the first formal proof of Stickelberger-Swan. It removes the only external input of the parity theorem.
- status: Lean-checked per README (Stickelberger.lean, commit c0e3fb4), not visible here; the theorem itself is classical (Swan 1962, via Pellet's formula)
- uses: ext:Swan-1962, ext:Pellet-formula
- where: sublinear/README.md "Formal status (23 November)"
- matters: makes the toy theorem and its corollary free of unproved hypotheses (axioms: standard only).

## F_ext | Extensions: any degree and smooth derivative
- kind: theorem
- says: (a) For any degree including p | d, with e = deg Q' and l its leading coefficient, discr(N - Q) = +-lambda^(n-2-e) * l^(n-d) * discr(Q), and for q a square and lambda a non-square the number of irreducible factors is even exactly when (-1)^(d+1+e) * chi(l)^(n-d) = 1 (always true for p not dividing d, where e = d - 1 and l = d); checked on all 240 irreducible cubics over F_9 for deg N = 243 and 246 with 0 disagreements (parity_rule.txt). (b) The hypothesis is about Q' only (every irreducible factor of Q' divides N), so N = lambda*V_J^p makes N - Q reducible for every row of degree below deg N with p not dividing d whose derivative is J-smooth; exact counts over F_9 with J = 3 (deg N = 2,403) are every quartic, 8,928 of 11,808 quintics (75.6%) and 282,672 of 683,280 rows of degree 7 (41.4%), after which the proportion is estimated, not counted, to fall like Dickman's function of (d-1)/J.
- status: Lean-checked per README (commits 4d62189 and d3d39ea), not visible here; computed/verified for the F_9 counts and parity_rule.py; the Dickman statement is conjectural (an estimate)
- uses: F_parity, F_check
- where: sublinear/README.md "Two extensions found by the Lean session"; parity_rule.py, parity_rule.txt
- matters: widens the mechanism from one degree to a positive proportion of rows at every degree, but only for rows with smooth derivative.

## F_corollary | Desert corollary N = lambda * V_J^p
- kind: theorem
- says: For q an odd square, J >= 1, V_J the product of all monic irreducibles of degree <= J and lambda a non-square, N = lambda*V_J^p has N - Q reducible for every monic irreducible Q of degree <= J + 1 with p not dividing J + 1 (those of degree <= J divide N, degree J + 1 follows from the parity formula), with deg N = p*deg V_J, a little above p*q^J (2,403 against 2,187 for F_9, J = 3). Forcing the same by congruences needs degree of order q^(J+1)/J, a cover of degree p*q^J followed by luck succeeds with probability about exp(-0.7*q/(p*(J+1))), and over a prime field the same N handles a single top degree at no saving.
- status: Lean-checked per README (the deserts in ParityDesert.lean), not visible here; the cover comparison is a counting estimate (the constant 0.7 is not derived in the README)
- uses: F_parity, F_cvd
- where: sublinear/README.md "Corollary (deserts)"
- matters: the Goldbach-shaped statement (N fixed and inseparable, the row varying); the authors have not found it stated elsewhere.

## F_check | Parity mechanism checked by factorisation
- kind: empirical
- says: parity_desert.py (python-flint) finds that r has one parity per row degree, equal to the formula, in every case tried: F_3, F_5, F_7, F_9, F_25, F_49, rows of degree 2, 3, 4, both kinds of lambda, n = 0 and p (mod 2p); rows with p | d have mixed parity that follows the sign rule row by row. Larger cases are samples (12 rows of the 1,620 quartics over F_9 at deg N = 2,403, 12 of the 5,200 cubics over F_25 at deg N = 3,125, 200 of the 1,176 quadratics over F_49), while the README's "all 300 irreducible quadratics over F_25" is backed by an output line showing 150 tested (deg N = 125); all 150 quartics over F_5 (deg N = 725) were tested.
- status: computed/verified
- uses: F_parity, F_ext
- where: parity_desert.txt, parity_desert_big.txt, parity_rule.txt; sublinear/README.md "Checked"
- matters: independent computational evidence beside the formal theorem.

## F_cvd | Desert versus cover, settled by counting
- kind: proposition
- says: A zero class at a prime pi makes pi's factor in the parity symbol +1 for every row, while a nonzero class makes it a coin flip for the rows with pi | Q' and kills the rows in that class by divisibility; a coin flip buys nothing in search (the expected number of irreducible N - Q is unchanged, it only says where they are). At equal degree over F_9 (deg N = 2,403) the desert kills every quartic, 75.6% of quintics and 41.4% at degree 7, while an ordinary cover (nonzero classes on the 285 primes of degree <= 3 plus 400 quartic moduli) leaves 13.8% of the rows of every degree before optimisation and mops up the 223 quartics left, so it equals the desert at degree J + 1 and beats it above; the desert wins only on the deterministic objective at degree exactly J + 1 and only when q/p is large ((1 + 0.56*(q-1)/J)/p is 1.5 for F_25, J = 2 and 2.1 for F_49).
- status: computed/verified for the counts; the constant 0.56 and the ratios are model estimates
- uses: F_corollary, F_ext
- where: sublinear/README.md "Desert or cover? (the design question, settled by counting.)"
- matters: closes the idea of replacing covers by parity deserts, even in the toy: use an ordinary cover, a generic N and the parity filter on what is left.

## F_toy | Toy search: parity filter worth 4-5x
- kind: empirical
- says: toy_search.py runs the whole search over F_3[x]: a greedy cover on the 14 irreducibles of degree <= 3 (deg M = 33), 1,318 rows of degree <= 8 (42 left after the cover), members of degree 93 and a sieve to degree 6; 30,000 members gave 1,426 successes against 1,431 predicted by (1 - p)^k. Half the rows have odd parity (0.4984; 0.5000 among sieve survivors), no irreducible N - Q has even parity, and among odd survivors the irreducible fraction is 0.2505 against 0.1252 for all survivors (exactly twice); at the best 3% of members, successes per 1,000 tests are 14.6 when ranked by rows left with every row tested (the production scheme) and 65.2 when ranked by odd rows left with only odd rows tested, a factor 4.5 (5.1 at 1%, 3.8 at 10%, 2.0 with no selection), i.e. 1.4 to 1.6 nats.
- status: computed/verified
- uses: F_parity, M_selection, M_density
- where: sublinear/README.md "Result 2"; toy_search.py; toy_search_m3_g8.txt
- matters: measures what the only transferable mechanism is worth: a constant factor, every member still being looked at.

## F_prior | The mechanism is known: a non-analogy
- kind: verdict
- says: The parity mechanism predates this work: Swan (1962) has families with an even number of factors throughout (x^(8k) + x^m + 1 over F_2), Conrad, Conrad and Gross (2008) give the Mobius function of f(g) for f in T^p including irreducible polynomials with no irreducible value, and Sawin and Shusterman (Ann. Math. 196, 2022) use it to break the parity barrier for twin primes over F_q[T]; K. Conrad's survey "Irreducible values of polynomials: a non-analogy" calls it the standard example of something true over F_q[T] with no integer counterpart, and the Goldbach-shaped corollary (N fixed and inseparable, the row varying) was not found stated.
- status: conjectural (literature claims quoted from the README, not checked here)
- uses: ext:Swan-1962, ext:Conrad-Conrad-Gross-2008, ext:Sawin-Shusterman-2022, ext:K-Conrad-non-analogy
- where: sublinear/README.md "What this is and is not" and References
- matters: warns that the toy result is a known non-analogy, so transfer needs new mathematics.

## S_intgap | Why the integers are harder
- kind: negative-result
- says: The integer counterpart would compute or force the parity of the number of prime factors of N - q, but lambda(n) has no formula short of factoring (no "differentiating whole numbers"), information depending only on n modulo small numbers (Jacobi symbols, genus characters, norm-form conditions) is uncorrelated with lambda(n) by the prime number theorem in progressions (the parity problem of sieve theory), and every algebraic certificate tried (differences of powers, two quadratic-form representations, cyclotomic values) exhibits a factorisation N - q = A*B costing a congruence mod A per row unless rows share it, which they do only through small primes or for at most sqrt(Q) rows. Genus theory does give an integer shadow (the number of prime factors of n is the 2-rank of the class group of Q(sqrt(-n)) plus one; for n = 3 mod 4 squarefree, n is prime iff h(-n) is odd) but reading it means finding ambiguous forms, as hard as factoring (Shanks, Schnorr-Lenstra), whereas in F_q[x] it is one resultant.
- status: conjectural (informal argument; nothing proves that no transfer exists)
- uses: F_prior, M_wp7, M_closure, ext:parity-problem-of-sieve-theory
- where: sublinear/README.md "Why the integers are harder (the gap to close)"
- matters: pinpoints why the toy mechanism does not transfer and what new mathematics would be needed.

## S_decoding | The search as soft-decision CRT decoding
- kind: negative-result
- says: Dictionary: members t < K are messages, (t mod s) for the sieve primes is a codeword of a Chinese-remainder code (a Reed-Solomon code over F_q[x]) and the wanted t maximises a weighted agreement; algebraic list decoding (Guruswami-Sudan, Koetter-Vardy; over the integers Goldreich-Ron-Sudan, Boneh, Guruswami-Sahai-Sudan, Coppersmith) needs about four times the typical agreement while the best member among K exceeds the typical one by a few percent, lists and birthday merges give only ln(list size) nats, maximum-likelihood decoding of Reed-Solomon codes is NP-hard (Guruswami-Vardy) and at least as hard as discrete logarithms in a range (Cheng-Wan), and noisy Chinese remaindering falls to lattices only for short lists (Bleichenbacher-Nguyen). The instance is special (all lists are images of one set of rows), "the only place left to look".
- status: conjectural (no proof that no algorithm exists; literature results are external)
- uses: S_b_crt, S_b_lattice, S_b_mitm, ext:Guruswami-Sudan-2000, ext:Guruswami-Vardy-2005, ext:Cheng-Wan, ext:Bleichenbacher-Nguyen-2000
- where: sublinear/README.md "The search problem itself: where it sits"
- matters: places the open problem in coding theory, where it is hard in general.

## S_toycrt | Practical lattice decoding stops at the Johnson radius
- kind: empirical
- says: A toy Howgrave-Graham/Guruswami-Sudan decoder (61 odd primes below 300, B = 10^12, Johnson radius A_J = 87.380, FLINT LLL, 390 decodes) recovers the planted message only above a sharp threshold at realised agreement about 1.028*A_J for lattice degree 30 (about 1.02 at degree 45), about 1% below the provable finite-degree bound and falling toward A_J like 1 + c/ell; below it the reduced rows contain no integer-rooted polynomial, and no non-planted solution was ever found although about 10^7 to 10^2 high-agreement alternatives exist (1.7*10^7 at rho = 0.7, 190 at rho = 1.0).
- status: computed/verified (decoder.py, results.json; 20 predeclared trials per rho)
- uses: S_decoding, M_wp3
- where: phd/toy_crt/results.md (outside assigned list; background for sublinear/README.md "Why nothing known collects the prize" item 2)
- matters: an empirical sign that solution abundance buys nothing for lattice methods below the radius.

## S_prize | What a perfect search would be worth
- kind: empirical
- says: At the 10% target 213,070, an ideal search to depth z (test even N < 10^200 in increasing order of the rows k_z left with no prime factor <= z) needs N tested for one success: e^39.3 for z <= 463 (today; 1,620 rows, expected successes 0.0002 in the remaining budget e^30.75), e^35.8 for z <= 1,000 (1,319 rows against 1,439 +- 11 for a typical member of the best cover; 0.007), e^33.4 for 2,000 (1,116 against 1,309 +- 14; 0.08), e^30.5 for 5,000 (910 against 1,170 +- 17; 1.3), e^26.7 for 20,000 (685 against 1,007 +- 18; 50), e^24.5 for 50,000 (574 against 922 +- 19; 400) and about e^11.8 for depth 10^8 with rows beyond 50,000 treated as independent (160 against 542). The prize is 3.5, 5.9, 8.8, 12.6 and 14.8 nats for depths 1,000 to 50,000: an ideal search to 5,000 would bring the 10% record within the remaining budget, to 20,000 fifty times over.
- status: computed/verified (tempering plus multi-histogram reweighting, 108 temperatures; ideal_tilt_213070.txt); conjectural where the sampler is out of equilibrium (z = 463 is 20 nats low at the very bottom and is checked against the covers instead) and for the fair-sample assumption
- uses: S_tilt, C_m89, M_density, M_portfolio
- where: sublinear/README.md Result 3; ideal_tilt_213070.txt
- matters: the quantitative size of the prize any sublinear algorithm could collect.

## S_tilt | The ideal-tilt method and its check
- kind: algorithm
- says: ideal_tilt.c samples residue vectors (a class for every odd prime <= z, nonzero for s <= 29) by parallel tempering with energy k = rows left, and ideal_tilt.py turns the histograms by multi-histogram reweighting into g(k), the number of states, normalised by the product of the s; the number of even N < 10^200 with k rows left is g(k)*(10^200/2)/prod s, assuming the N below 10^200 are a fair sample of the residue vectors (the assumption the whole campaign rests on). At z = 463 (the 89 primes of the best covers) it gives one success per e^39.31 members and e^-8.49 expected in the budget e^30.75, against e^39.2 and 0.02% from the covers directly, and reaches the known minimum of 1,609 rows; for z >= 1,000 forward and backward free-energy estimates agree within 0.1 nats and a second seed on a shorter ladder gives e^33.31 and e^30.46 for depths 2,000 and 5,000 (first run e^33.37 and e^30.50).
- status: computed/verified
- uses: C_ptcover, M_density
- where: sublinear/README.md Result 3 "Method" and "Check"; ideal_tilt.c and ideal_tilt.py docstrings; ideal_tilt_213070.txt
- matters: the machinery that turns "number of ideal N" into a cost in nats.

## S_notcovers | Ideal N are not best-cover members
- kind: empirical
- says: 1,319 rows at depth 1,000 is 10.6 standard deviations below the mean of random members of a best cover (20,000 members of a 1,609-row cover, member_depth.py: 1,439 +- 11) and 685 at depth 20,000 is 17.5 below (1,007 +- 18), while the e^39 members of all covers within a few rows of 1,609 reach only about 9. The ideal N give up a few rows on the small primes and are mildly aligned with all primes above: at the relevant temperature a class change is accepted with probability below 0.01 for moduli under 128, about 0.1 for 128 to 512, 0.4 for 512 to 2,048, 0.7 for 2,048 to 8,192 and 0.9 above, so no prime beyond 512 is pinned to its best class but each is in a better-than-average one (I confirmed the buckets against the z = 20,000 block of ideal_tilt_213070.txt).
- status: computed/verified
- uses: S_tilt, S_prize
- where: sublinear/README.md Result 3, after the table; member_depth.py
- matters: the best numbers are lucky members of mediocre covers, so enumerating covers best-first cannot find them.

## S_count | Number of solutions: one N in 10^25
- kind: empirical
- says: Summing (1 - p_z)^k over all N gives the expected number of even N < 10^200 with no prime row below the target and must not depend on z; for 213,070 six runs give e^403.30, 403.28, 403.27, 403.26, 403.24, 403.24 (z = 463 to 50,000), about 10^175 numbers, and the count is e^395.7 at 245,000, e^383.1 at 300,000, e^371.5 at 350,000 and e^338.0 at 500,000 (about 0.23 nats less per 1,000 in the target, reaching zero near 2.1 million). So at the 10% level one N in 10^25 is a solution and one in e^39 among members of the best covers: the difficulty is entirely one of location.
- status: computed/verified (consistency across depth is the check); conjectural as an absolute count (rests on the fair-sample and independence assumptions)
- uses: S_tilt, M_ceiling
- where: sublinear/README.md Result 3 "How many solutions there are"
- matters: existence is not in doubt at 10%; only exhibiting such an N is.

## S_targets | Ideal search at higher targets
- kind: empirical
- says: The ln of N tested per success (ideal_tilt_targets.txt), for an ideal search to depth 20,000 and to depth 10^8 with rows beyond 20,000 independent, is 26.7 and 11.7 at 213,070, 32.5 and 16.1 at 245,000, 42.7 and 24.1 at 300,000, 52.3 and 31.9 at 350,000 and 81.4 and 56.8 at 500,000 (265,000 at z = 50,000: 33.7 and 19.0). With the remaining budget e^30.75 the target reached is 172,000 (8.1%) today, 214,000 (10.0%) with an ideal search to 5,000, 235,000 (11.0%) to 20,000, 249,000 (11.7%) to 50,000 and 343,000 (16.1%) to 10^8; even a perfect depth-10^8 search needs about e^44 tests for 20% (426,140), e^13 times the budget, against about e^87 for today's method.
- status: computed/verified for the tabulated numbers; the README's claims that the cost grows like the 1.4th to 1.8th power of the target and that expected successes rise from e^18 at depth 10^8 to e^27 at 10^12 have no output file behind them (see Doubts)
- uses: S_prize, S_tilt, M_portfolio
- where: sublinear/README.md Result 3 "How far an ideal search would go"; ideal_tilt_targets.txt
- matters: even a perfect solver would not reach 20% with the remaining compute.

## S_toyexact | Exact miniature: cover-first against ideal order
- kind: empirical
- says: With X = 10^9 and Q = 1,000 (167 rows), enumerating all 157,947,020 even N with no prime factor from 3 to 29 finds exactly 256 with g(N) >= 1,000 (one in e^13.33); ordering by rows left at the Chinese-remainder line (depth 23, "cover first") needs 2,982, 63,350, 253,380, 1,205,425, 12,004,497 and 151 million N for 1, 3, 10, 30, 100 and all 256 successes, against 13, 401, 10,811, 73,849, 1,720,522 and 154 million when ordered by rows left at depth 200 (ratios 229, 158, 23, 16, 7, 1; 5.4 nats for the first success). The 62 numbers with at most 8 rows left at depth 200 have 24 to 34 rows left at depth 23 (the best covers have 22; one of the 62 lies among the 888 members of covers with at most 24 rows), the 256 successes have 25 to 41 (average N 36.8), and the Lean session's independent re-enumeration gave the same joint histogram byte for byte.
- status: computed/verified (exact enumeration, no model; I re-derived the totals 157,947,020 and 256, the 62, the 888 and the 24-34 and 25-41 ranges from toy_exact_1e9_1000.txt; the Lean cross-check is quoted, not seen)
- uses: S_tilt, S_prize
- where: sublinear/README.md "The same thing in miniature, exactly"; toy_exact.c, toy_compare.py, toy_compare_1e9_1000.txt, toy_exact_1e9_1000.txt
- matters: a testbed where any proposed method for (P') can be checked against the truth in seconds.

## S_toypredict | The tilt prediction matches the miniature
- kind: empirical
- says: The count of N by rows left at depth 200 predicted from residue vectors alone (tempering, reweighting and the fair-sample assumption at e^-168 numbers per residue vector) against the exact count is 0.9 against 1 at 6 rows, 7.9 against 12 at 7, 53.8 against 49 at 8, 311 against 339 at 9, 1,541 against 1,564 at 10, 24,522 against 24,859 at 12, 226,760 against 229,438 at 14, 1,306,248 against 1,310,838 at 16 and 11,450,782 against 11,436,352 at 20, within 3% where the count is large and within sampling noise at the bottom. The 256 successes follow count*(1 - p)^k with p = 0.485 (found 12, 18, 15, 29, 28, 36, 34, 30, 18 at k = 12 to 20 against 8.7, 14.4, 21.2, 27.6, 32.1, 33.3, 31.1, 26.0, 19.7), and the prime density among 200-rough numbers below 10^9 is 0.489.
- status: computed/verified (I re-derived the exact counts and the success counts by level from the histogram file and the expected values from p = 0.485)
- uses: S_tilt, S_toyexact, M_density
- where: sublinear/README.md "The miniature also checks the method of this section"; toy_compare_1e9_1000.txt; toy_tilt_1000_200.txt
- matters: validates the method behind the prize table on a case where the truth is known.

## S_needles | Miniature: best numbers are independent needles
- kind: empirical
- says: The 62 numbers with at most 8 rows left, the 1,965 with at most 10 and the 256 successes are spread evenly over [0, 10^9) (successes lean to large N, where primes are rarer), sit in several good classes modulo each small prime (class 2 mod 5 for 73%, class 3 for 19%; the most popular class holds 30% mod 7 and less beyond), show 1.3 standard deviations more incidences with the primes 31 to 199 than a random number (successes 0.35), and two of the 62 agree modulo 0.49 of those primes on average against 0.45 by chance; over 118 million pairs N, N + 2*3*5*...*23 the rows left at depth 200 correlate at -0.029. What each prime beyond the line buys in the miniature (gain in nats over cover first for 10, 30, 100 successes) is 0.44, 0.21, 0.10 at z = 29, 1.71, 0.62, 0.78 at 61, 2.40, 1.50, 1.16 at 97 and 3.15, 2.79, 1.94 at 200, against an overhead (residue vectors per number below X) of 6.5 at 29, 1.3*10^7 at 43, 1.2*10^14 at 61, 2.3*10^27 at 97 and 7.8*10^72 at 200.
- status: computed/verified (toy_rem_check.c for the correlation)
- uses: S_toyexact, S_b_crt
- where: sublinear/README.md "Looking at the best numbers of the miniature directly" and "What each prime beyond the line is worth, and costs"
- matters: no structure ties one good number to another, and a prime just beyond the line buys a fraction of a nat for its own size in work.

## S_b_crt | Barrier: free coordinates stop at X
- kind: proposition
- says: By the Chinese remainder theorem the residues modulo any primes with product at most X = 10^200 can be prescribed and N is then determined, and the residue modulo any further prime is a sum of one term per free coordinate, so changing one coordinate changes every further residue; two different N < X agree modulo primes of total size below ln X only (Lean: move_budget, "same class modulo M and modulo every s in T, both below X, implies M*prod T < X"; move_keeps_at_most_three: with X <= M*463^4 at most three sieve primes can be kept, at most 27 rows of 1,634). Beyond the line the landscape is a random-energy model: in the miniature rows left at depth 200 of N and N + 2*3*...*23 correlate at -0.029, and the 460.5 nats of 10^200 just suffice to choose residues modulo the primes up to 463 (product of 2 and the odd primes to 463 is 10^192.67, which I re-derived), so enumerating covers best-first is an ideal search to depth 463.
- status: Lean-checked per README and verdict file (move_budget; move_keeps_at_most_three in Cap/Brainstorm.lean), not visible here; the miniature measurement is computed/verified
- uses: C_ptcover, S_needles
- where: sublinear/README.md "Why nothing known collects the prize" point 1; brainstorm/verdicts_on_research_ideas.txt item 46 (outside assigned list)
- matters: explains why there are no local moves, hence no annealing or hill-climbing beyond the line.

## S_b_lattice | Barrier: lattices and CRT with errors or lists
- kind: negative-result
- says: Chinese remaindering with errors or lists (Goldreich-Ron-Sudan, Boneh, Guruswami-Sahai-Sudan, Bleichenbacher-Nguyen) finds N when lists are short and agreement high: the weighted agreement must exceed about sqrt(ln X * sum w^2 / ln s), while the constraint available per prime beyond the line is about one nat (if the primes to about 400 are pinned, some 80 nats remain for the 79 primes from 467 to 997), i.e. lists holding a third of all classes. For the 580 primes from 467 to 5,000 with one-class lists in a population of e^83 the best agreement that exists is about 22 against a decoding radius of 78, and with lists of a third the radius exceeds the number of primes; the Lean session proves the radius is at least 3.88 times the typical agreement for K = 2^32 (Cap/Radius.lean, list_deficit, johnson_leaves_the_cover).
- status: computed/verified (counts and radii); Lean-checked per README for the radius and list_deficit statements, not visible here
- uses: S_decoding, S_toycrt, M_wp3
- where: sublinear/README.md point 2 and Ladder rung 4
- matters: shows the instance sits on the wrong side of every decoding radius.

## S_b_mitm | Barrier: meet in the middle and birthday trees
- kind: negative-result
- says: With population e^F, constraint cost C = sum ln(s/l_s) and list entropy H = sum ln l_s there are e^(F-C) solutions and a meet in the middle produces them at constant cost each only when H <= 2(F - C), with lists of e^(H/2) in memory; for the whole problem (F = 460, C about 425) and a memory of e^21 entries this extends the reach by one prime (covers on 90 or more primes, worth about 0.2 nats per extra prime), and Wagner's tree needs more slack, not less. The measured instance is joint.py (C_joint), which cancelled 24.3 digits at the price of the search entropy.
- status: Lean-checked per README for the condition (mitm_condition_log: ln P <= 2F - C, Cap/Population.lean), not visible here; the arithmetic is computed
- uses: C_joint, S_decoding
- where: sublinear/README.md point 3 and Ladder rung 4
- matters: shows the only way past the line is ln(list size) nats, one prime at a time.

## S_b_hash | Barrier: locality-sensitive hashing for near neighbours
- kind: negative-result
- says: Writing N = u + v, the agreement of a pair is an inner product of a one-hot vector with a set indicator block by block; the sets are translates of random-looking class lists, so a locality-sensitive scheme collides on a good pair at most about twice as often as on a random one for a bucket of the same size. The exponents computed are 0.88 (this session) and 0.99 (the Lean session, for its variant), i.e. at best K^0.94 work for a population K, where the populations here are e^80 and more against e^33 operations available.
- status: computed/verified (two independent derivations); no lower-bound proof
- uses: S_decoding
- where: sublinear/README.md point 4
- matters: rules out sublinear near-neighbour search at this scale.

## S_b_score | Barrier: linear-time scoring is at its optimum
- kind: proposition
- says: What remains is to score every member, which is what the fleet's sieve does at 23 ns a member; the gain of selection depends only on the kept fraction, which is fixed by sieve cost against test cost, and the sieve cannot skip members because marks are generated along progressions, so the present design is at its optimum under that cost. The Lean session's bounds are that m questions to a black box reach the fraction m*g/K of the target set (Cap/BlackBox.lean) and that a perfect solver on the present progressions is worth at most 4.3 to 5.3 nats over the 3% rule for a population of e^22 (hitMass_selected_le in Chernoff form, Cap/Population.lean: m tests on a population e^F expect at most m*y^k + e^F*u^(-k)*prod(1 - s_j + s_j*y*u) successes however the members were found); it also tried lattices of moves, additive and multiplicative splittings of t, tree search with bounds, polynomial parametrisations and row sharing by convolution without success.
- status: Lean-checked per README for the bounds, not visible here; the optimality statement is conjectural
- uses: M_selection, E_fscan_neg
- where: sublinear/README.md point 5, the paragraph after it, and Ladder rung 4
- matters: states that nothing cheaper than scoring each member is known, with a formal bound on what a perfect solver could add.

## S_b_lists | Barrier: list gain, NP-completeness and interval structure
- kind: theorem
- says: For one prime s let w(a) be the number of rows killed when N is in class a, mu its average and W its maximum; any list L of classes gains at most (W - mu)/ln(W/mu) * ln(s/|L|) rows over the average (Lean: Cap/ListGain.lean, list_gain_le), which for every prime above Q (W = 1, at most 1,609 rows) is 0.207 rows, 0.005 nats of success, per nat of constraint (list_gain_above_Q), six times less than an extra covering prime, so nothing that enumerates a product of lists collects the part of the prize above Q. For arbitrary lists "does any N below a bound meet every list" is NP-complete already with two classes per modulus (Manders-Adleman 1978; Garey-Johnson AN1), and for these lists the problem is finding intervals (N - Q, N] poor in rough numbers at fixed offsets, the same as record prime gaps; the one structure that exists, that for s > Q the list is the set R of rows so "N mod s in the list" implies "N mod s small", is findable by lattice reduction but R fills under 1% of [0, Q), so forcing N mod s below Q costs ln(s/Q) nats and raises the kill chance only from k/s to k/Q = 0.8%, 100 to 1,000 times less per nat than the last covering prime.
- status: Lean-checked per README (list_gain_le, list_gain_above_Q), not visible here; NP-completeness is external (Manders-Adleman); the rest computed
- uses: S_b_mitm, S_b_lattice, ext:Manders-Adleman-1978
- where: sublinear/README.md end of "Why nothing known collects the prize"
- matters: a general theorem that no list-based method can be both exact and fast, and a quantification of why the prize above Q is out of reach for them.

## S_Pprime | Open problem (P'): few rows, little work
- kind: open-problem
- says: Find even N < 10^200 for which at most 1,320 of the primes q < 213,070 have N - q free of prime factors up to 1,000, at a cost of fewer than e^30 operations in all for e^30 such N; about e^36 such N exist, the best covers give 1,439 +- 11 and nothing below about 1,340 within any budget considered. A solution is worth 3.5 nats (a factor 30) at the 10% target, and the same question at depth 5,000 (910 rows) is worth 8.8.
- status: conjectural (open problem)
- uses: S_prize, S_b_crt, S_notcovers
- where: sublinear/README.md "Open problem (P')"
- matters: the sharpest testable form of the sublinear question, and the exact miniature (S_toyexact) lets proposed methods be tried.

## S_ladder | Programme ladder and the state of each rung
- kind: open-problem
- says: Rung 1 (toy theorem and corollary with formal proof) done; rung 2 (toy search with the parity filter) done, 4 to 5 times; rung 3 (a toy instance small enough to enumerate every member: does anything besides parity and the symmetries of F_q[x] predict the best members?) to do; rung 4 (formal barrier statements for the integer search, Cap/BlackBox, Radius, Population) done; rung 5 (integer information that is not a residue, i.e. anything cheaper than a Fermat test that correlates with primality of a rough number in a special family of N) open, no candidate yet; rung 6 (wheel and list merges inside the production sieve) costed at 0.1 to 0.4 nats, not started; rung 7 (number of N by rows left at depth z and the cost of an ideal search) done for z up to 50,000 at the 10% target; rung 8 (problem (P'), any method reaching beyond the Chinese-remainder line for less than scoring every member) open, lattices, meet in the middle, birthday trees and hashing ruled out with numbers.
- status: conjectural (plan and bookkeeping); rung 5 is the integer counterpart of open problem H2 of phd/wp9
- uses: F_parity, F_toy, S_b_score, S_prize, S_Pprime, M_closure
- where: sublinear/README.md "Ladder"
- matters: the programme's own account of what is proved, measured and open.

---

# F. Verdicts and corrections

## V_brainstorm | 200-idea brainstorm: nothing worth a nat
- kind: verdict
- says: On 22 November 2026 the two sessions each wrote 100 ideas for a large step at 200 digits (yardstick 2,130,704; the record that evening went from 133,981 to 146,191) and tested each other's: no idea is worth one nat as a change of method, and what is left is engineering worth 0.6 to 1.3 nats (the agreed statement says 1 to 1.5, and the Lean session counted 2 to 2.5 in total) and compute. Every prime that helps constructively costs ln r of the 460.5 nats, under which budget the cover in use is optimal to about 0.2 nats; 20% (E near 80) is "out of reach of every mechanism on both lists, by more than 20 nats even for an oracle"; the compute levers are 1,000 volunteer cards (+5.8 nats, 8% to 9.3%) and 10 times the fleet (+2.3 nats, +0.5 points); and the one open door is the sublinear decoding problem, worth about 10 nats and nothing more.
- status: computed/verified (measurements) and Lean-checked theorems per the verdict files (Cap/Brainstorm.lean, commit efbd1b6); the conclusion that 20% is out of reach is a judgement
- uses: M_oracle, M_price, M_portfolio, S_question, V_third
- where: fscan/cover/brainstorm/README.md; verdicts_on_lean_ideas.txt; verdicts_on_research_ideas.txt (all outside assigned list)
- matters: the origin of the sublinear programme and of the conclusion that what is left is compute.

## V_third | A third way to force compositeness is bounded
- kind: negative-result
- says: A third way of making N - q composite besides a small prime by congruence and luck was the last idea of the brainstorm, and the Lean session's theorems bound it: a certificate is one divisor per row, a divisor of two rows is below Q, prescribing coprime divisors above 213,070 for 38 rows leaves at most one N below 10^200, and identities serve at most sqrt(Q) rows. Related theorems named in the verdict files are large_divisors_unique, card_prescribed_le (at most X/prod + 1 numbers), pow_window, doubling_window, zero_class_row (a zero class covers exactly the row q = r), affine_combination and Cap.card_le_sqrt_succ.
- status: Lean-checked per the brainstorm README and verdict file, not visible here
- uses: M_wp7, M_closure
- where: fscan/cover/brainstorm/README.md "Result" last paragraph; verdicts_on_research_ideas.txt items 4, 43-44, 61-69 (outside assigned list)
- matters: closes the algebraic-certificate route at the Q = 213,070 scale with theorems, complementing the empirical probes (M_wp7).

## V_wp10 | An RH/GRH proof would not move the frontier
- kind: verdict
- says: WP10 (2026-11-21) assumed the claim in the four-page note dated 2026-11-20 at alpo.ge/remark.pdf (a proof of RH and GRH found with Claude and formalised in Lean; the 14-part archive was not downloaded and nothing is checkable as written) and found that RH and GRH give square-root-quality estimates while every bottleneck lives at x^o(1) scale: the RH prime-in-interval window falls 10^72.4 short at 150 digits, 10^97.1 (RH) and 10^95.9 (GRH) at 200 digits and 10^1343 at 2,692 digits; GRH would only make Miller's test a proof (Bach: all prime bases below 2 ln^2 n; 1.4 s at 150 digits, 5.8 core-days at 2,480, 44 core-days at 4,000, no certificate) and change constants in the paper (Linnik exponent 12/5 for smooth moduli by erratum, factor 1.2 not 2.5). The only transferable idea is methodological (proof-carrying records).
- status: computed/verified (wp10/grh_reach.py prints every number); the verdict is conditional on the claim
- uses: S_question
- where: phd/wp10_grh_remark.md (outside assigned list); RESULTS.md (reference); sublinear/README.md "What the note remark.pdf contributed"
- matters: the programme's use of the note is purely methodological, and the same "no lever moves" reasoning shows nothing in it depends on the RH claim.

## V_sublinear | Programme verdict so far
- kind: verdict
- says: In the toy setting a third compositeness mechanism (the parity of a discriminant, proved formally and known as a non-analogy) exists and is worth only a constant factor of 4 to 5 (1.4 to 1.6 nats) in a toy search, while over the integers a perfect search would be worth 3.5, 5.9, 8.8, 12.6 and 14.8 nats at depths 1,000 to 50,000 and beyond the Chinese-remainder line lattices, list decoding, meet in the middle, birthday trees and hashing are ruled out with numbers (best agreement 22 against radius 78; at best K^0.94) and linear-time scoring is at its optimum. Nothing proves that no sublinear algorithm exists: the claim is only that the prize is real and of known size, covers collect all of it below the line, and above it every known method costs more than scoring members one by one; open are (P'), the fully enumerable toy (rung 3), non-residue information (rung 5) and constants worth 0.1 to 0.4 nats.
- status: conjectural (negative evidence, not a proof)
- uses: F_parity, F_toy, S_prize, S_b_crt, S_b_lattice, S_b_mitm, S_b_hash, S_b_score, S_b_lists, S_Pprime, S_ladder
- where: sublinear/README.md throughout, especially "Why nothing known collects the prize" (last paragraph) and "Ladder"
- matters: the answer to the thread's question as of 23 November 2026: no sublinear search is known and none is ruled out.

## V_campaign | July 2026 campaign proposal and its fate
- kind: verdict
- says: PROPOSAL_NEXT_CAMPAIGNS.md (2026-07-29) planned Campaign A (T(100,000) below 145 digits: modulus about 299 nats, expected residual k about 740-770, E[t] about 1-7*10^10, fallback 145 digits at about 4*10^9, with lessons from campaign 2's 2,132 of 2,400 variant-specs and 0 hits), Campaign B (R(10^200) above 135,000 from 119,419: modulus about 434 nats, covers to Q = 135,000-140,000, k about 950, E[t] about 3-5*10^9, about 60 expected hits in range), Campaign C (g > 2,000,000, estimated at 6-12 h of ECPP) and Campaign D (algebraic mechanisms, CRT list recovery beyond the Johnson radius, density-1 subset-sum, Pocklington-friendly N - q), in the order B, A, C. Outcome: C was achieved without any ECPP (R_height_ecpp_free), B's 135,000 target was passed by the later fleet records (146,191, 157,837), and D's items became the negative results M_wp3, M_wp7 and M_closure.
- status: conjectural (a plan; outcomes are read off other entries)
- uses: R_fleet200, R_height_ecpp_free, M_wp3, M_wp7, M_closure, M_wall100
- where: PROPOSAL_NEXT_CAMPAIGNS.md
- matters: shows how the agenda evolved and which questions stayed open into the sublinear programme.

## X_corrections | Corrections and retractions recorded in the files
- kind: retraction
- says: (a) The 100% line was 1.4*ln^2 N*ln ln N with 1.4 fitted to one number and is now computed (ratio 1.40 at 19 digits rising to 1.64 at 200), so every closeness figure fell (25 digits 56.4% to 53.8%, 150 digits 10.7% to 9.2%); (b) WP3 v1 "open window" was retracted (M_wp3); (c) fscan's earlier "4.3 per digit at 23 digits, 5.5 at 21" was too optimistic (5 to 7 for the first digit, 12 for the next); (d) tscan's expectation was recomputed with the p of each member (changes the sum by about 20%); (e) PARI crosscheck scripts before 2026-11-22 were fail-open; (f) the wp10 erratum (Linnik exponent 12/5, not 5) and the supersession of the paper's Theorem 14 by Shi and wp12 Theorem 1; (g) wp12 Theorem 2 is vacuous at record parameters; (h) the Lean session refuted "E >= 33 for every modulus set" (idea 38) and found idea 7 false as a statement about information though true for constructions, and the research session raised its floor table by 0.5 nats (S(k) = oversize + E); (i) WP9's first evolutionary run exposed a 50 times accounting error in the author's evaluator, and the "new record / first without ECPP" label for 1.2M was relabelled "independent second certificate".
- status: retracted (each item as stated in its file)
- uses: M_ceiling, M_wp3, E_fscan_neg, E_verify, C_wp12ceil, M_oracle, M_closure, R_height_ecpp_free
- where: RESULTS.md first section; fscan/README.md; proth/README.md; phd/wp10_grh_remark.md erratum; phd/wp12 Theorem 2 caveat; verdicts files; phd/wp9/wp9_closure_theorem.md section 12; phd/RESEARCH_LOG.md cross-review (several outside assigned list)
- matters: tells the reader which numbers in the older files are superseded.

---

## Dependency notes

The twelve dependency chains that matter most, in plain words.

1. **The basic pipeline and its price.** A congruence cover (C_basic) fixes N modulo about 88 small primes, the residual rows are composite only by luck, and the density model M_density (E = |U|*boost/ln N, validated at four scales) prices every search; sieve-and-test engines (E_search, then E_tscan, E_fscan and E_gpu150) are just faster ways of walking the same progression, and every record from R_budget to R_fleet200 is one draw from it. Because all later prices (M_price, M_portfolio, S_prize) come from the same model, an error in M_density would propagate everywhere, which is why M_frailty tests it at low thresholds.
2. **Row counts to prices to the budget.** The tempering sampler (C_ptcover) gives the number of uncovered rows k for each target (C_table88, C_m89, C_supply); k feeds the price list (M_price), the expected-record portfolio (M_portfolio, which shows about 172,000 is what the remaining 10 days buy from 157,837) and the budget e^30.75 used by every sublinear table.
3. **The prize chain.** The same sampler with every prime up to z as a modulus (S_tilt) counts how many N have few rows left; this gives the ideal-search costs S_prize, the solution count S_count and the higher targets S_targets, is anchored at depth 463 by the 1,609-row cover of C_m89 and by the direct cover calculation, is validated in an exactly enumerable miniature (S_toyexact, S_toypredict), and rests on the fair-sample assumption of M_density.
4. **Selection is the only gain over enumeration.** The selection identity (M_selection) explains why testing only the emptiest 3% of members pays; tscan and fscan (E_tscan, E_fscan) implement it with ever cheaper scores, E_fscan_neg and S_b_score say smarter selection is a constant factor, and E_sievedepth (+28% in production) is the only engineering lever left above 0.3 nats.
5. **The two budgets lead to the open question.** The oracle floor and the Lean family (M_oracle) show about 10 nats of information exist beyond the modulus budget, the brainstorm (V_brainstorm) shows nothing constructive can collect it, so the only door left is locating good members without enumerating them (S_question, then S_Pprime).
6. **The Chinese-remainder line.** S_b_crt (move_budget: two N below X agree modulo primes of total size below ln X) means there are no local moves beyond the primes whose product is at most 10^200; the complete covers (C_c15907, C_cmore), the meet-in-the-middle count (S_b_mitm), the joint construction (C_joint) and the enumerability statement of FRONTIER.md (M_realizable) are the same fact seen as a construction, a count, an experiment and a design principle.
7. **The decoding barrier.** Posing the search as soft-decision CRT decoding (S_decoding) leads to S_b_lattice (agreement 22 against radius 78), to the toy decoder S_toycrt (LLL stops at 1.028 times the Johnson radius and finds no alternative solutions) and back to the older WP3 barrier and its retraction (M_wp3); together they underlie the verdict V_sublinear that lattice and list-decoding methods are out.
8. **List gain.** The theorem list_gain_le (S_b_lists: 0.207 rows per nat above Q, six times worse than a covering prime, NP-complete for arbitrary lists) means nothing that enumerates a product of lists can collect the part of the prize above Q; with S_b_hash (K^0.94 at best) and S_b_score it completes the case that scoring each member is optimal for known methods.
9. **The function-field toy.** Classical Stickelberger-Swan (F_stick, Lean) gives the parity theorem (F_parity), widened by F_ext and stated as the desert corollary (F_corollary), supported by factorisation checks (F_check); F_cvd shows an ordinary cover beats the desert at equal degree, F_toy shows the parity filter is worth only a constant 4 to 5 times, F_prior says the mechanism is a known non-analogy and S_intgap says why no integer analogue is known, so the toy yields no sublinear algorithm.
10. **Algebraic certificates.** Five empirical probes (M_wp7) and the closure draft (M_closure, zero passes in 13,661 plus 41 evolved schemas, conditional on H1 and H2) say nothing but covering and trial makes N - q composite within a grammar; the Lean theorems of V_third close it at the 213,070 scale, and what remains is rung 5 of S_ladder (non-residue information), which is the same as open problem H2.
11. **Covering theory and the existence gap.** Mertens' theorem (Lean-proved) gives the constructive 1.349 ln X ln ln X bound (C_leanbound), whose finite instance is the Lean-checked complete cover to 15,907 (C_c15907); the ceiling for covering certificates (C_wp12ceil) and the 1M-desert numbers (C_1Mwall: 10^6.5 such numbers exist, 10^85 tests to exhibit one) quantify the construction-versus-existence gap that motivates the sublinear question.
12. **The height records.** The Proth/BLS construction (C_bls) with GPU screening and a deepening sieve (E_prothgpu) produced g = 1.2M to 10M (R_height_ecpp_free, R_height_gpu), and the three-leg verification stack (E_verify) is why none of them rests on the search that found it; the only rung left is 16,045,848, costed at about 5,725 tests.

---

## Record chronology

Every record found in the files, in order. "Digits" is the digit count of N. Intra-day order on 2026-11-22 is inferred from the order of sections in RESULTS.md (newest first); times are given where a file gives them.

| # | date | g | digits | game | found by / what | where |
|---|---|---|---|---|---|---|
| 1 | published 2014 | 9,781 | 19 | exhaustive range (N <= 4*10^18; N = 3,325,581,707,333,960,528) | Oliveira e Silva, Herzog and Pardi (not ours); 69 record holders from g = 2 at N = 4 | record_holders.txt |
| 2 | July 2026 | 105,667 | 199 | T(100,000) and R(10^199) incumbent | source paper "Cute Goldbach Gaps" | RESULTS.md |
| 3 | July 2026 | 109,621 | 237 | height-game incumbent | same paper | RESULTS.md |
| 4 | 2026-07-21 | 1,134,871 | 2,692 | height (Game 1) | this repo's first session; 813-congruence cover, E = 6.56, hit at k = 14, 253-step ECPP | records/megagap_2692digit_g1134871 |
| 5 | 2026-07-21 | 107,719 | 197 | T(100,000) and R(10^199) | same session; 89-modulus cover, about 1.4*10^8 elements, k = 951,928 | records/dual_197digit_g107719 |
| 6 | 2026-07-21/22 | 1,157,341 | 2,480 | height (Game 1) | slop CPU session; 760 classes, 245-step ECPP | slop/goldbach/records/g1 |
| 7 | 2026-07-21/22 | 110,917 | 199 | T and R(10^199) | slop CPU session; 88 classes, t = 299,581,384 | slop/goldbach/records/g23 |
| 8 | 2026-07-23 | 112,249 | 200 (N = 1.0336*10^199) | R(10^200) | this repo; by-product of the R(10^199) campaign, k = 56,770, measured E = 18.4 | records/budget_1e200_200digit_g112249 |
| 9 | by 2026-07-25 (date not stated for the 193-digit one) | 102,337 / 109,357 | 193 / 186 | T(100,000) | slop CPU session ratchet rounds 1-2 | slop/goldbach/records/README.md; RESEARCH_LOG 2026-07-25 |
| 10 | by 2026-07-25 | 119,419 | 199 | R(10^200) | slop CPU session, round 1 | slop/goldbach/records/r200 |
| 11 | 2026-07-25 | 100,297 | 195 | T(100,000) | this repo; k = 70,186, 1,590 progressions, E = 17.28 | records/threshold_195digit_g100297 |
| 12 | by 2026-07-28 | 101,149 | 179 | T(100,000) | slop CPU session, round 3 | slop/goldbach/records/t100k |
| 13 | 2026-07-26 (round finished 2026-07-27) | 104,527 | 150 | T(100,000) | GPU session; CUDA engine on a Colab fleet, k = 6.21*10^10, ~2.1*10^12 Fermat tests in the round | records/threshold_150digit_g104527 |
| 14 | 2026-11-21 08:03 UTC | 1,200,109 | 11,263 | height | ccr-2ce9e63a session (proth/desert.py), 2,647 tests, first certificate without ECPP | records/height_11263digit_g1200109 |
| 15 | 2026-11-21 08:44 UTC | 1,200,109 (different N) | 11,263 | height | ccr-8ffe9d7a session (bls_search.py), 3,472 tests, independent code | records/bls_game1_11263digit_g1200109 |
| 16 | 2026-11-21 (same day) | 2,000,269 | 15,595 | height | ccr-2ce9e63a session; 2,670-class lazy cover, 648 tests, 37 min on 4 cores | records/height_15595digit_g2000269 |
| 17 | 2026-11-21 evening | 5,000,251 | 33,938 | height | ccr-8ffe9d7a session (Campaign G), Colab A100, 44 min GPU | records/height_33938digit_g5000251 |
| 18 | 2026-11-21 night | 10,000,141 | 61,329 | height | ccr-8ffe9d7a session, Colab A100, about 2 h GPU | records/height_61329digit_g10000141 |
| 19 | 2026-11-21 night | 10,459 | 30 | T(10,000) | this repo; cover on 16 primes <= 59, 53 min on 4 cores, k = 101,138,639 | records/threshold_30digit_g10459 |
| 20 | 2026-11-22 | 10,111 | 27 | T(10,000) | tscan, 24 min, k = 23,025,113,687 | records/threshold_27digit_g10111 |
| 21 | 2026-11-22 | 20,551 | 46 | T(20,000) | tscan, 6.5 min on 4 cores, k = 3,202,304,117 | records/threshold_46digit_g20551 |
| 22 | 2026-11-22 (later) | 10,357 | 25 | T(10,000) | tscan/vscan, 4.9*10^11 members in 6.5 h, k = 418,223,156 | records/threshold_25digit_g10357 |
| 23 | 2026-11-22 | 30,139 | 63 | T(30,000) | tscan, 19 min, k = 6,878,744,425 | records/threshold_63digit_g30139 |
| 24 | 2026-11-21/22 (non-frontier points) | 5,407 / 6,073 / 11,173 | 20 / 22 / 40 | low-end scans | same cover-and-scan method | RESULTS.md table |
| 25 | 2026-11-22 evening | 133,981 (standing at the start of that evening) then 146,191 | 200 (N < 10^200) | R(10^200) | the fleet (finder not named in the files); 6.3% then 6.9% of the 2,130,704 ceiling | fscan/cover/brainstorm/README.md |
| 26 | 2026-11-23 02:40Z | 157,837 | <= 200 (N < 10^200) | R(10^200) | the fleet (finder not named); 7.41% of the ceiling | fscan/cover/brainstorm/README.md |
| 27 | date not stated (after 2026-11-22) | 10,159 / 10,399 / 11,701 / 10,771 / 10,729 | 23 | T(10,000) | fscan class 197 on six machines, another session; smallest N = 30625623272505310405982 | fscan/README.md |
| 28 | not found in any file | about 158,209 | N < 10^200 | R(10^200) | quoted by the requester; unverified here | none |

---

## Doubts

Unclear status, contradictions between files, and claims that look unsupported. Items 1 to 8 matter most for the sublinear question.

1. **The figure 158,209 is not in the assigned files.** The latest recorded value is 157,837 (7.41%, 2026-11-23 02:40Z, brainstorm README, outside the assigned list); the numbers 133,981, 146,191 and 157,837 have no directory in records/ (which tops out at 112,249 below 10^200) and the fleet's branch (phd/campaign3_gpu) is cited but absent. The string 158209 occurs only as a prime inside row lists of constructions/wall_1M_199d.json and fscan/cover/deliver/specs_q160000_128.json, so I cannot tell whether 158,209 is a newer record.
2. **Lean claims cannot be checked from this tree.** There is no lean/ directory here (the lean files are on branch ccr-36ca7b46-8twf14); the READMEs quote file names and commits (c0e3fb4, 4d62189, d3d39ea, 4a747b6, a4c5d0f, c9591a7, efbd1b6) and say "standard axioms only". "First formal proof of Stickelberger-Swan" is the sessions' belief ("as far as either session knows"), and the miniature cross-check "byte for byte" refers to goldbach/lean/scripts/mini_check/, also absent (I re-derived the exact miniature numbers myself). proth/README.md says Lean for the height records was not done.
3. **"About e^10 times better" against the table.** The introduction of sublinear/README.md says the best N for primes up to 10^7 is about e^10 times better than a typical member, but the last row of the Result-3 table goes from e^39.3 to about e^11.8 at depth 10^8, i.e. 27.5 nats; the text does not reconcile them. The e^10 matches the Lean explicit product-measure family (E = 29.0 against 39.2, an upper bound on the floor), while e^11.8 is an idealised count assuming independence of rows beyond 50,000.
4. **Claims with no output file behind them.** "Expected successes of an ideal search go from e^18 at depth 10^8 to e^27 at depth 10^12" (only B = 10^8 is in the committed outputs); "the cost grows like the 1.4th to 1.8th power of the target" (from the nats columns I get exponents of about 1.2 to 1.4 for the z = 20,000 column and 1.6 to 2.3 for the depth-10^8 column, and "cost" is ambiguous between nats and tests); "20% costs about e^87 with today's method" against "E near 80" in the brainstorm README and verdict file.
5. **The fair-sample assumption is tested only where it is easy.** The count of N by rows left assumes the N below 10^200 are a fair sample of residue vectors; the miniature tests this at e^-168 numbers per residue vector, but at z = 20,000 there are e^-19,345 numbers per vector (e^16.9 at z = 463), and for z >= 1,000 there is no direct count at full size, only forward/backward and second-seed agreement. At z = 463 the sampler is itself out of equilibrium at the very bottom (20 nats low), which is why that line is checked against the covers.
6. **The budget e^30.75 is never defined in the sublinear files.** By my arithmetic it is about 9 fleet-days at 29M effective full-weight members per second (the brainstorm README says "9 days ... 29 million"); the sublinear README equates "N tested" with a "full-weight member" and calls the budget "the Colab units that remain", which depends on accounts the verdict file calls "the user's money". The "23 ns a member" for the fleet's sieve (README point 5) is hard to reconcile with 2.7 ns a member per card (verdict file) and 29M per second effective (about 34 ns).
7. **Different k at Q = 213,070 are used side by side**: 1,609 (89 primes), 1,620 (the z = 463 tilt), 1,623 (best on 88 moduli), 1,634 and 1,639 (earlier runs). The price list uses 1,634 (E = 39.06) though 1,623 (E = 38.80) is the best known on the same moduli, so quoted costs differ by about 0.3 nats between files.
8. **The miniature's "best covers".** The README says the best covers have 22 rows left at depth 23 and also that one of the 62 best numbers lies "in the 888 members of the best covers"; the 888 is the number of N with at most 24 rows (14 + 124 + 750 by my count), and only 14 N have 22 rows.
9. **README versus output for the F_25 check.** The README says "all 300 irreducible quadratics over F_25" were checked; parity_desert.txt shows 150 of 300 tested at deg N = 125 and 12 at deg N = 3,125, and the larger cases are 12-row samples. The formal theorem makes this low risk, but the sentence overstates the output.
10. **Two GPU-year figures for sub-100 digits, one retracted.** FRONTIER.md says 193,000 GPU-years (9.1*10^18 candidates at an optimistic 1.5M candidates per second); the RESEARCH_LOG of 2026-07-28 first gives about 5*10^4 GPU-years, then corrects it to about 9*10^5 GPU-years ("a units slip: divided by test rate instead of candidate rate"); PROPOSAL_NEXT_CAMPAIGNS.md (2026-07-29) still quotes about 5*10^4. FRONTIER.md's "roughly seven orders of magnitude beyond plausible compute" fits none of them obviously.
11. **Stale "smallest/largest known" claims.** RESULTS.md headlines 112,249 as "the largest least-Goldbach summand known below 10^200" and 195 digits as "the smallest known" for T(100,000) although the slop branch had 119,419 and 193/186/179-digit bounds in parallel (RESULTS.md's own in-repo note concedes this), and its low-end frontier table lists the 25-digit g = 10,357 as the smallest N with g > 10,000 while fscan/README.md reports five 23-digit numbers (smallest 30625623272505310405982, g = 10,729) that have no records/ directory.
12. **The fscan excess is unexplained.** Class 197 found 5 numbers against 0.78 expected (a 0.13% event, about 2% over all classes run, 5 against 1.6) although the README says the expectation may be about 10% high (raw/deep 1.23 +- 0.08 on tested members, 1.09 over all) and checks out at Q = 7,001 (50 found against 48.7); the brainstorm checks (356 against 366.5) find no excess either.
13. **The ceiling is a prediction.** "10%" and "7.41%" inherit its uncertainty: the 35 record holders above 10^9 arrive early (median 0.29 against 0.69), so the line may be 1.5% too low (not corrected), and the two candidate limiting constants 1.515 and 1.701 cannot be separated by any feasible search; the 2014 paper that gives them was read second-hand.
14. **FRONTIER.md Result 1 is not monotone in digits.** The set-valued gains are 2.0, 1.6, 2.4, 2.8 and 1.1 nats at 100 to 150 digits with no explanation, while the text asserts the frontier is "converged, not pool-limited" because no modulus above 1,123 is chosen.
15. **Constants in the toy comparison are not derived in the README**: the 0.56 in (1 + 0.56(q-1)/J)/p, the 0.7 in exp(-0.7*q/(p*(J+1))), and "a factor of about 4 (1.4 nats)" in the first estimate before rung 2 measured 4 to 5. Also "the theorem and the corollary carry no hypothesis" cannot mean no hypotheses (N' = 0, p not dividing d, and so on), only no unproved assumptions.
16. **WP12 Theorem 2 is vacuous at record parameters** (acknowledged after the cross-review), and the closure theorem (M_closure) is conditional on H1 (unproved) and H2 (open) and on a finite grammar; "no mechanism outside the grammar is known" is not a proof of none.
17. **Dates of several slop records are not stated** (193-digit T(100,000) and the exact day of the 119,419); the intra-day order of the five 2026-11-22 low-end records is inferred from section order; the date of the fscan 23-digit finds is not given.
18. **"The prize" assumes a free oracle.** The ideal-search costs count only tests; any real method pays to find the N, and the README's statement that a perfect search to depth 5,000 would bring 10% within the budget is therefore a bound, not a plan; the Lean bound of at most 4.3 to 5.3 nats for a perfect solver on the present progressions (population e^22) is a different, smaller quantity, and how it relates to the 8.8 to 14.8 nats of the prize table is not spelled out.
19. **Lean-adjacent item named in the assignment does not exist.** "B/lean-adjacent items" is not a directory; what exists is brainstorm/ideas_lean.txt and brainstorm/verdicts_on_lean_ideas.txt (see the inventory below).

---

## Directory inventory

- **B/records** (15 directories; I listed the names and printed only the key names and a few short scalar fields of each record.json, no certificates, witnesses or full integers): one directory per certified record, each with record.json (N or its CRT reconstruction data, g, cover) and either evidence.json plus a PARI ECPP certificate (complement_cert.gp, check_cert.log) for the older records or crosscheck.gp/log, verify.log, N.txt and SHA256SUMS/MANIFEST.sha256 for the BLS height records: threshold_{25,27,30,46,63}digit_* (the low-end T games), threshold_195digit_g100297 and threshold_150digit_g104527, dual_197digit_g107719, budget_1e200_200digit_g112249, megagap_2692digit_g1134871, height_{11263,15595,33938,61329}digit_* and bls_game1_11263digit_g1200109 (independent second certificate for g = 1,200,109). The largest g below 10^200 held is 112,249; the slop (119,419), fleet (133,981 to 157,837) and fscan 23-digit records are not here.
- **B/lean-adjacent items** (no such directory; there is no lean/ in this worktree): the Lean-related material present is fscan/cover/brainstorm/ideas_lean.txt (the Lean session's 100 unvetted ideas of 22 November, "babble on purpose"), fscan/cover/brainstorm/verdicts_on_lean_ideas.txt (the research session's one-line verdicts on them, with the engine facts and price list) and verdicts_on_research_ideas.txt (the Lean session's verdicts on the research session's 100 ideas, with theorem names from Cap/Brainstorm.lean), plus the Lean file and commit names quoted in sublinear/README.md.
- **B/constructions** (5 files, not read): blueprint_1M_1250d.json (the 420-modulus, 1,247-digit blueprint for g > 10^6 at E = 20.74), wall_1M_199d.json (the best 199-digit system for g > 10^6: 91 moduli, 8,146 residual primes, E = 196.4), and m211_x196.json, m219_x197.json, m221_x197.json (oversize-modulus covers whose CRT representative lies below 10^197, from joint.py).
