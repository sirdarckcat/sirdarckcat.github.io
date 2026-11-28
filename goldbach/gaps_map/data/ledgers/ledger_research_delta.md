# Delta ledger: research session, snapshot 02564fb to head 48c73de

Compiled 2026-11-25 (sublinear/README.md head state of 25 Nov 08:46 UTC). Ids are rd_*. All `where:` paths are relative to `goldbach/` on branch ccr-d4a17dd0-7uu03r unless they name another branch.

**Scope.** 104 commits, 23 Nov 16:37 to 25 Nov 08:46 UTC, 115 files: `sublinear/README.md` (+1,362 / -27 lines: the cover-depth programme, the floor, the counting law, the dual game), `fscan/cover/README.md` (+355: families, rows above the design level, design menu), `fscan/cover/brainstorm/README.md`, new scripts and outputs in `sublinear/` (cover_floor, cover_price, cover_price_hl, cover_dispersion, cover_tilt, cover_limit, cover_dual, cover_dual_cpu, greedy_cover, desert*.c, complete_cover_*.txt), starting files in `fscan/cover/starts/`, `family_search/` tools, raw runs in `sublinear/cover_floor_runs/` (gz, not read; headers and the committed .txt summaries only).

**Method.** Read every hunk of the three README diffs, all 104 commit messages and the new .txt outputs. To match claims I read (not ran) Lean-side docstrings on `ccr-36ca7b46-8twf14` at a1c77dc (CoverDepth, CoverDepthRun, CoverDepthMore, CoverCount, CoverCountAsymptotic, CoverCountRun, CoverPairs, CoverPairSums, Cap/Hardness, Cap/Thinning, Records, Record200_g160357, scripts/cover_depth, cover_count, cover_floor_runs, cover_limit_check, lgs_heuristic) and two uarch-branch result files (`desert_fast5_results.txt`, `cover_ub_results.txt`, branch ccr-b8c25887-i6tn9f). I wrote my own scratch code (python3 -I and C, in `gbmap2/work_research/`, no repo code run) and **re-derived**: (1) all 13 published complete covers: moduli are all odd primes up to x, every class nonzero, first unstruck odd prime equals the claimed bound, overlaps 49 and 7 of 167 as stated; (2) D(1..13) by my own exhaustive search and the optimal-vector counts for n = 2..12; (3) the limit constants, with my own solver of the delay and price equations: Lambda(1) = 1.19639276, 0.88690, 1.127528, plus the two known-answer checks; (4) theta(x) column, first-moment losses, rows left by random classes (1,853 and 2,278), D ratios, Goldbach-room numbers, pi(160,357) = 14,711; (5) the six family lines of the "rows above" table, every starting-file header count and histogram; (6) the floor table against the raw `cover_floor_q170000.txt`; (7) a Monte Carlo of the dispersion; (8) mechanism-check ratio ranges and dual-game table arithmetic; (9) the premises of the LP floor (2,321 alive rows, capacity 1,218) from the starting file.

**Could not check.** Lean statuses (taken from READMEs, commit messages and module docstrings). The tempering data behind the law, floors and families (raw gz not read). The planning-model outputs (weighted rows, expected final records, probabilities, the family rule, the design menu). The exhaustive certified floors and D(89) < 35,000 (uarch program, not rerun). D(n) for n >= 14 and counts for n >= 13 (my search stopped at 13 and 12). The record's own N, its row 1,193, the 52-base test. The dual-game ceiling digits (68.5, 142). Opus-branch reports written after the README's last edit (seen only in passing). Anything not in the list above under "re-derived" is marked "unverified" in its status.

---

# A. The cover-depth programme: exact D(n), certified reach, bounds

## rd_dn_table | D(n): exact values to n = 35 and the number of optimal vectors
- kind: record
- says: D(n) is the least odd prime that no class vector on the first n odd primes strikes together with all smaller odd primes (a "strike" is q in the class of some modulus, so N - q is divisible by it). n = 1..35: 5, 7, 19, 31, 43, 67, 103, 163, 181, 223, 271, 331, 419, 499, 613, 709, 739, 859, 907, 1,051, 1,213, 1,279, 1,381, 1,471, 1,567, 1,669, 1,801, 1,933, 2,137, 2,311, 2,521, 2,647, 2,749, 2,953, 3,079. Optimal vectors for n = 2..28: 2,1,2,2,6,6,1,2,1,17,9,2,1,3,2,2,4,2,1,2,2,1,1,2,12,10,1. D/(r ln^2 r) is 0.72 at n = 8, 0.78 at 20, 0.81 at 35 (D/(r ln r) 4.06). Not in the OEIS (searched 24 Nov). No D(n) box exists on the map.
- status: computed (exhaustive, uarch session; two programs agree to n = 28); I reproduced D(1..13) and counts for n = 2..12 with my own search; n >= 14 unverified by me. Lean-checked per README and module docstrings: exact to n = 9, one-vector lower bounds to n = 35.
- uses: rd_dn_search, l_cover, c_cover_cap, ext:uarch-session-desert_fast5
- where: sublinear/README.md, "The same question exactly, for few primes"; desert.c, desert_fast.c (branch ccr-d4a17dd0-7uu03r)
- matters: First exact measure of how far a given set of moduli can force summands away with no luck; the base of the whole depth programme.

## rd_dn_search | How D(n) was computed and cross-checked (and the n = 25-27 overflow)
- kind: algorithm
- says: Depth-first search: branch on the least unstruck prime, try each unused modulus. Cuts: children ordered most-struck-primes-first (D(15) from 1.6e10 to 1.1e7 nodes), a capacity cut (unstruck primes must fit in the sum of the free moduli's fullest classes), a lemma keeping only classes near the fullest (another 100-200x), a pair cut. D(35): 9.0e9 nodes, an hour. Checks: two child orders, brute force n <= 9, CaDiCaL SAT (n = 8,10,12,13; counts n <= 12), each cut switchable off, D(24) found by tempering first. An array overflow in the uarch build used for n = 25-27 withdrew those counts on 24 Nov 17:03; they were rerun and agree (2, 12, 10).
- status: computed; overflow and rerun confirmed in the uarch results file; my own search (capacity cut only) agrees to n = 13.
- uses: rd_dn_table
- where: sublinear/README.md, same section; uarch branch `desert_fast5_results.txt`, `cover_ub_results.txt`
- matters: Shows exact values rest on one session's programs plus independent count modes, not on Lean beyond n = 9.

## rd_dn_lean | What Lean proved about D(n): bound on g(N), Goldbach by covering
- kind: theorem
- says: `CoverDepth.lean` proves the search correct and runs it in the kernel: D(0..9) = 3, 5, 7, 19, 31, 43, 67, 103, 163, 181 are theorems. Proved consequences: g(N) <= D(n) for n = odd primes up to sqrt N; if D(n) <= N-3 then N is a sum of two primes, one at most D(n), so "D(n) < (next prime)^2 - 2 for every n" implies Goldbach (room: 163 vs 841 at n = 8, 499 vs 2,809 at 14, 3,079 vs 24,647 at 35); D is strictly increasing; the records 6, 12, 30, 98 attain D(0..3); every even N from 6 to 960 is a sum of two primes, one at most 181.
- status: Lean-checked per README and Lean module docstrings (I read them, they match; Lean not run). Room numbers re-derived by me.
- uses: rd_dn_table, l_isleast, l_cover
- where: sublinear/README.md, "The same question exactly..."; Lean branch GoldbachGaps/CoverDepth.lean, CoverDepthRun.lean, CoverDepthMore.lean
- matters: Ties the cover depth to Goldbach itself: D(n) = O(r ln^2 r) would give Goldbach for large N.

## rd_ub89 | Certified bounds on covers at the campaign's size: 15,907 <= D(89) < 35,000, floor 777
- kind: theorem
- says: The uarch session's `cover_ub.c` (capacity cut, written separately from the D searches) proves no class vector on the 89 moduli 3..463 strikes every odd prime below Y for Y = 170,000 (6,240 nodes), 80,000, 60,000, 50,000, 45,000, 40,000, 37,000, 35,000 (4.6e8 nodes, an hour). So 15,907 <= D(89) < 35,000 (first bound was < 37,000). Certified floors at Q = 170,000: every vector leaves at least 401 (j = 6, 3 s), 644 (j = 8, 4.5e6 nodes), 777 (j = 10, 7.3e8 nodes, 3.5 h) of the 15,496 odd primes: 62% of the best cover. The cut loses 4-5 orders of magnitude between 30 and 89 moduli at fixed Y/D.
- status: computed (exhaustive; program validated against D(n) for n = 2..27 and brute force on 6-7 moduli), not Lean-checked, unverified by me; the lower end is Lean-checked.
- uses: rd_dn_table, rd_floor_170000, m_thm2
- where: sublinear/README.md, "At the campaign's own size there is now a certified bound from above"; uarch branch `cover_ub_results.txt`
- matters: First rigorous upper bound on covers at 200 digits (2.2 times the truth) and the only rigorous floor on rows, far below the measured 1,214.

## rd_greedy | Plain greedy reaches 0.71-0.73 x ln^2 x, not x ln x
- kind: empirical
- says: Take odd primes r <= x in increasing order, each taking the nonzero class holding most unstruck primes below y. G(x), the first y where nothing is left: 126 (x = 23), 1,021 (100), 10,428 (463), 30,184 (1,000), 132,567 (3,000), 601,525 (10^4), 9,650,028 (10^5), 34,610,715 (3x10^5). G/(x ln^2 x): 0.56 at 23, 0.60 at 463, then 0.71 to 0.73 from 10^4. The theorem's count is 4-7 times lower. A mean-field model gives 0.90 (463), 0.86 (10^5), 0.84 (3x10^5). Lean's own code agrees within a few percent (9,769 vs 10,428 at 463, 6%) and certified 32,971 (167 moduli), 135,511 (429), 614,101 (1,228 moduli, 4,298-digit N).
- status: computed; Lean-checked per README at three points; I checked the printed x = 463 vector (first unstruck odd prime 10,429).
- uses: m_thm1, rd_reach_table
- where: sublinear/README.md, "Why 1.349 is not the truth"; greedy_cover.py/.txt, greedy_meanfield.py
- matters: Shows the real reach is about x ln^2 x, one logarithm above the proved x ln x; empirical base of the conjecture.

## rd_reach_table | Best complete reach known for each set of moduli
- kind: record
- says: Every odd prime struck below: 163 (x = 23, 8 moduli, exact), 613 (53, 15, exact), 1,471 (97, 24, exact), 4,909 (199, 45), 8,311 (293, 61), 15,907 (463, 89), 41,659 (997, 167). Over x ln^2 x: 0.72, 0.73, 0.73, 0.88, 0.88, 0.91, 0.88. On 167 moduli: 40,111 -> 40,459 -> 41,047 -> 41,659 (Opus session, last two in other families; 41,768 missed by 1-2 rows). Also 70,111 on 238 moduli (0.875 x ln^2 x) and 98,731 on 302 (0.855). Lean-certified: all but 70,111 and 98,731.
- status: computed; I rechecked all 13 published covers independently (all pass); Lean-checked per README/docstrings for the rest.
- uses: rd_dn_table, e_c15907, m_thm1
- where: sublinear/README.md, "Why 1.349 is not the truth" (table "best reach known"); complete_cover_*.txt, complete_covers_97_199_293.txt
- matters: Tempered reach stays at 0.85-0.91 of x ln^2 x from 45 to 302 moduli: where the luck-free depth sits.

## rd_cover_93_final | The 94th prime does not pay; 16,981 stands
- kind: negative-result
- says: A 94th modulus (499; one complete cover in 1.25 million would fall below 10^200) was tried: complete covers exist up to at least 17,250 but only a few hundred thousand could be enumerated at 17,000. So 16,981 (93 primes to 491) stays the best pure-divisibility certificate under 10^200 (each extra prime had bought about 235). All four certificates, 15,907, 16,381, 16,747, 16,981, are checked by the Lean kernel (Records.lean, commit 9acf05d). A 92-prime run: 3,505 of 17,131 covers fall below 10^200 (20.5% vs 19.5% expected).
- status: computed; the four covers re-verified by me (first unstruck prime = bound, nonzero classes); Lean-checked per README.
- uses: r_cover_more, e_c15907
- where: sublinear/README.md, "At 200 digits, without luck"
- matters: Closes the "one more prime" route for pure covers at 200 digits.

# B. The counting law, its derivation, its limit

## rd_law_ln_g0 | The number of complete covers: ln g0 = theta(x) - c Q/ln^2 x, c = 1.00 +- 0.03
- kind: empirical
- says: g0(x,Q) = number of class vectors modulo the odd primes up to x that strike every odd prime below Q (g0(x,0) = e^theta(x)). Tempering at 14 sizes, 9 to 1,228 moduli, gives c = 1.013 (x = 463), 1.009 (997, Q 15,000-38,000), 0.99-1.03 (2,999), 1.006 and 1.012 (9,973); 1.09-1.45 at small sizes. Sampler vs exact count at nine moduli: within 0.03 (42 values within 0.09). Hence D(n) = theta ln^2 x / c: 1,082 vs exact 1,051 at n = 20; ends 16,300, 45,400, 191,000, 827,000 at 89, 167, 429, 1,228 moduli. The first-moment count is wrong by 1.349 ln Q/ln x in the loss (it put the end at 32,300 for 89 moduli).
- status: computed (measurement); the law itself conjectural. I re-derived the theta column and the first-moment losses (with the theta convention); the sampler data are unverified.
- uses: rd_dn_table, rd_recursion, c_pigeon
- where: sublinear/README.md, "How many complete covers there are: a law, and where they end"; cover_floor_law.txt
- matters: Turns "how good can a cover be" into one straight line, the base of every prediction below.

## rd_end_89 | Complete covers on the 89 moduli end near 16,000
- kind: empirical
- says: Runs from random vectors stop sampling in proportion above about 85% of the way, so a million sweeps were run from the 15,907 cover: ln g0 = 62.9 (Q 14,000), 42.2 (14,500), 29.2 (15,000), 20.5 (15,300), 16.6 (15,600), 3.5 (15,907) against the c = 1 line 71.3, 58.0, 44.8, 36.8, 28.8, 20.7. About thirty complete covers at 15,907; slope 1.17/ln^2 x over the last eighth; best covers at 15,950 and 16,000 leave one row. The recursion says 15,973 or 16,069. On 167 moduli the end is at or below about 43,600 (extrapolated), so 41,659 is at least 96% of it. At 30-108 moduli the curve bends below the line before the end (slope 1.22-1.64 over 85-93%).
- status: computed (measurement).
- uses: rd_law_ln_g0, rd_reach_table, e_c15907
- where: sublinear/README.md, "The last eighth of the range"
- matters: Answers "where do pure covers stop" at 200 digits: about 16,000, found 15,907.

## rd_families_complete | Complete covers sit in few families fixed by the smallest moduli
- kind: empirical
- says: At 167 moduli, Q = 40,111: e^98.6 complete covers in the family of the known cover, e^94.6 in the best vector of the other family; runs from random vectors count only the family they are in (10-20 nats fewer); the covers to 41,047 and 41,659 lie in a third family. At 45 moduli (frame = one nonzero class on each of the six smallest moduli, 92,160 frames; 24 random frames per target) a typical family holds e^-10 of an equal share at 41% of the way (Q = 2,000), e^-21 at 61%, and at 81% 15 of 24 hold none. ln g0 correlates with the rows the frame leaves alive: -0.91, -0.96, -0.85, slope -1.4, -1.9, -2.9 nats per row.
- status: computed (measurement); the 167-moduli cover frames and overlaps re-checked by me.
- uses: rd_law_ln_g0, rd_families_campaign
- where: sublinear/README.md, "How many complete covers...", paragraphs "Families"; cover_floor_runs/families/frames_x199.txt, cover_floor_families.py
- matters: Explains why runs from random starts miss the end, and sets up the family search at the campaign's target.

## rd_recursion | The derivation: a price per alive row, with the dispersion from Hardy-Littlewood pairs
- kind: construction
- says: Count complete covers modulus by modulus, smallest first: with price p per alive row, p before s = p after s - kappa(p)/(s-1), kappa = (e^(vp)-1)/v, v = variance/mean of the alive rows per class. Poisson (v = 1) is the first moment. Measured v (Montgomery-Hooley) gives the straight line with constant (1.124/b), b = 1.12 giving 1. Derived: v = 1 - 6 phi(s)(s/(s-1))(pi(Q)/Q) ln(Q/(6s)), phi(s) = prod(1 - 1/(t-1)); better, the whole pair sum W(j) = a c prod(1+u_t), u_t = 2/(t-3) below s, 1/(t-2) above. K = 1.5164516079595 (to 28 digits, exact rational arithmetic, Lean session). Lean proves the exact first step: the pair weight has mean exactly 6s/(s-1), product form, partial sums <= the mean.
- status: conjectural (heuristic, nothing fitted; second-order term rests on Hardy-Littlewood); the exact pieces Lean-checked per README/docstrings.
- uses: m_h1, rd_law_ln_g0
- where: sublinear/README.md, "Why a straight line with slope 1/ln^2 x", "The dispersion derived, and the law with nothing fitted", "The whole pair sum"; cover_dispersion.py, cover_price.py, cover_price_hl.py; Lean CoverPairs.lean, CoverPairSums.lean
- matters: Predicts the loss within 5% and the end of covers within 4% with no fitted constant; the engine of several later entries.

## rd_recursion_checks | How the recursion fares against measurement
- kind: empirical
- says: Loss within 5% at the first nine points (463 to 9,973 moduli; first moment off by 1.5-1.9). Opus session's 24 points (30-108 moduli): measured/recursion 0.96-1.05 (closed formula), 0.93-1.02 (pair sum); within 4% from 53 moduli. Ends within 4% of the best cover known from 20 to 89 moduli; the pair sum is 0.5-5.5% below the new exact D(29..35), the closed formula 1-6% above. Mechanism on 1,500 complete covers (89 moduli, Q = 12,000): the chosen class strikes e^(vp) times an average class within 16% to s = 263 (factor 1.1 to 8), more beyond (+31% at 293, +56% at 443); at 167 moduli 0.79-1.18 while the factor runs 1 to 185. A thinning correction made the loss 8-22% too small.
- status: computed; I re-derived the first-moment column, the mechanism ratio ranges from cover_tilt.txt, and ran my own Monte Carlo of v (x = 463, Q = 10,000): 0.49, 0.58, 0.68, 0.69, 0.75, 0.78, 0.81, 0.85 at s = 43..463; the closed formula overshoots by about 0.04 above s = 260. Other columns unverified.
- uses: rd_recursion
- where: sublinear/README.md, tables after "The dispersion derived..."; "The mechanism checked on covers themselves"; cover_price.txt, cover_tilt.txt
- matters: The recursion is good to about 5% wherever it can be tested, and its mechanism is what covers do.

## rd_prediction_test | The prediction test: what was written down first and what came out
- kind: empirical
- says: (1) 429 moduli, Q = 100,000: loss 1,545 on record 24 Nov 18:02; long runs on the Lean machine gave 1,541.3 and 1,542.0 (a short run 1,589). (2) D(35): "near 3,110, window 3,040-3,190" committed 19:55; exact 3,079 at 21:53. (3) 167 moduli at 39,000 and 40,111: loss within 1.5%. (4) 1,228 moduli, Q = 300,000: 3,330-3,414 on record at 18:02, 3,394 (pair sum) written 19:07; measured 3,582 (12k sweeps), 3,465.9 and 3,464.6 (150k), 3,437.7 (500k), 3,466.9 from the 614,101 cover: from above, 1.3% off, not reached; a three-point power law gives 3,388-3,393. (5) Losses at 797, 1,499, 1,999 moduli written 25 Nov 07:31, unmeasured in the README.
- status: computed; (4) open, (5) pending in the README at head (the Opus branch later reports measured/pair-sum 0.975-1.04 at 797 and 1,499, unverified by me).
- uses: rd_recursion_checks, rd_dn_table
- where: sublinear/README.md, "A prediction, and its test"; cover_price_hl.txt (last block)
- matters: A one-sided test: every finite run overestimates the loss, so only a measured value below the prediction could refute it.

## rd_limit | The limit constant 1.1275 and how it is derived
- kind: construction
- says: In the limit the recursion gives ln g0 = theta(x) - 0.8869 Q/ln^2 x, so D(n)/(r ln^2 r) tends to e^gamma/(2 C2 Lambda(1)) = 1.1275 (1.349 for independent rows). Steps: m(rho) = rho^2 for rho <= 1, rho m' = 2m - m(rho-1), m ~ 2e^gamma (rho-1); v(alpha) = 1 - (e^-gamma/2) alpha m((1-alpha)/alpha); price ODE dp/d ln alpha = (e^(vp)-1)/v, p infinite at alpha = ln x/ln Q; Lambda(1) = 1.19639276351. D/(x ln^2 x): 1.09 (10^4), 1.14 (10^5), 1.16 (10^6), maximum 1.20 at 10^12-10^15, 1.17 (10^50), 1.14 (10^200). Constant at the end: 0.92 (1,228 moduli), 0.88 (10^5), 0.83 (maximum). History: 1.349 on 24 Nov 17:53, open 18:02, 1.1275 at 19:08.
- status: conjectural (heuristic). Lean recomputed the constant (floating point) and its referee check of 25 Nov 08:40 says steps 1-4 hold for the recursion but establish only the recursion's limit, not that of D(n)/(r ln^2 r). I re-derived Lambda(1) = 1.1963927635 and 1.12752818 independently.
- uses: rd_recursion, rd_law_ln_g0
- where: sublinear/README.md, "Where the constant ends up"; cover_limit.py/.txt; Lean branch scripts/cover_count/Lam_check.py, scripts/cover_limit_check/README.md
- matters: States the asymptotic constant of the luck-free reach; at the sizes measured the approach is 10 orders of magnitude away.

## rd_conjecture | Conjecture: the forced reach is about ln N (ln ln N)^2, with constant 1.1275
- kind: open-problem
- says: For Q between x and a fixed fraction of theta(x) ln^2 x, g0 = exp(theta(x) - 2 C2 e^-gamma Lambda(ln x/ln Q) Q/ln^2 Q (1+o(1))). Hence D(n) = kappa_n r_n ln^2 r_n, kappa_n 0.77-0.91 for 20-89 moduli, 1.16 at 78,497, maximum near 1.20, limit 1.1275; the least summand divisibility by primes up to ln N can force is (1.1275 + o(1)) ln N (ln ln N)^2. Companion: for every A infinitely many even N have no summand below A ln N ln ln N. Proven window: r ln r << D(n) << r^(4+eps) (linear sieve with Bombieri-Vinogradov; r^(2+eps) under Elliott-Halberstam); r^2 is the Goldbach barrier. An upper bound on g0 of the law's shape would prove Goldbach for large N.
- status: conjectural.
- uses: rd_limit, rd_dn_lean, m_thm1, m_thm2, m_lower
- where: sublinear/README.md, "Conjecture (counting law)" and "For the frame, what is known from above"
- matters: The open next step beyond the proved 1.349 constant, and a route to Goldbach for large N.

## rd_nibble_sketch | Why 1.349 is not the truth: a sketch and the measurements behind it
- kind: open-problem
- says: Sketch, not proved or formalised: random small classes, then the large primes each strike two or more survivors (pairs in a common class, only pairs congruent mod 3 count); a deletion argument gives (1+delta) 1.349; "every constant" needs a near-perfect hypergraph matching (Rodl nibble). Opus measurements (x = 3,000..10^5): survivors within 1%, pairs within 4% (0.4-0.9 of independent balls), second moment <= 1.26 mean^2; deletion keeps 9-14% so about 1.5, not 2. Fullest-class rule: all struck to C = 1.39, 1.93, 2.47, 3.14. Greedy's excess is 0.454-0.458 ln x per prime, 55-71% from primes above x^0.8; the rule "random classes up to x^theta" predicted 0.92, 0.71, 0.44 at 10^6, measured 0.95, 0.74, 0.45.
- status: conjectural; measurements by the Opus session (branch ccr-c6e00296-3g7fp9), unverified by me.
- uses: rd_greedy, m_thm1
- where: sublinear/README.md, "Why 1.349 is not the truth, and what a proof of more would need"
- matters: Says what a proof of every constant would need and how much of the greedy reach comes from the largest moduli.

# C. The floor under every cover, and the families

## rd_floor_method | A floor under every cover from the partition function
- kind: algorithm
- says: Z(beta) = sum over all class vectors of e^(-beta k) >= e^(-beta k_min), so k_min >= -ln Z(beta)/beta for every beta. ln Z(beta) comes from parallel tempering at all temperatures with Bennett's ratio between neighbours; equilibrium is tested from random covers and from the best cover known. Checks: 7 moduli, all 4.8 million vectors, agree to 0.01; complete covers sampled up to the proven D(20) = 1,051 and D(21) = 1,213, and the scan gave 1,279, 1,381, 1,471 for n = 22-24; ln g0 at n = 20 falls to 0 +- 0.5 at 1,051. Limit: with very few complete covers runs do not sample them in proportion (n = 24: Z thirty times too small).
- status: computed; the floor is a measurement (valid only where the run is in equilibrium; a run from the best cover cannot report better covers it does not find), not a proof.
- uses: rd_law_ln_g0, rd_dn_table
- where: sublinear/README.md, "A floor under every cover"; cover_floor.c, cover_floor.py
- matters: The measurement behind "the covers in use are the best there are".

## rd_floor_170000 | At Q = 170,000 on the 89 moduli: floor 1,214, bottom 1,247-1,248
- kind: empirical
- says: 15,496 rows; random nonzero classes leave 1,853; best cover known 1,248. Two runs of 10^6 sweeps (random start, best-cover start) agree within a row in the mean to beta = 1.07 and within 0.4 in the floor to 1.31: floor 951, 1,112, 1,154, 1,182, 1,201, 1,214 at beta = 0.59 ... 1.31, then 1,224, 1,232, 1,241, 1,244, 1,246, 1,247 (cover start) to beta = 5. Bottom: e^4.0 covers with 1,248 rows (e^5.6 in a run ten times shorter; 186 found), fifty times as many at 1,249; so the best cover has 1,247 or 1,248 rows. No cover has fewer than about 1,214 unless covers neither start reaches dominate: a factor 2.3 in rate at most.
- status: computed; I checked every floor and mean entry of the README table against the committed raw table `cover_floor_q170000.txt` (all match).
- uses: rd_floor_method, rd_ub89, m_rounding, e_cover_opt
- where: sublinear/README.md, "A floor under every cover"; cover_floor_q170000.txt; fscan/cover/README.md, "Three conclusions" 1
- matters: Measures what is left of "Door 1": at most 0.8 nat at the campaign's design level.

## rd_floor_213070 | At the 10% target no cover is within 80 rows of a 1% chance
- kind: verdict
- says: Q = 213,070 (19,050 rows; best cover known 1,609): 300,000 sweeps from both starts agree within 0.5 to beta = 1.07 (floor 1,554) and within 1 to 1.65 (floor 1,596); the cover-start run ends at 1,608 with e^2.8 covers at 1,609. Planning model (0.0243 nats per row): a 1% chance of the 10% record needs about 1,470 rows, 10% needs 1,375, an even chance 1,295; the floor 1,554 is 84 rows above the first. On the fleet's weighted measure (89 moduli 3..461 and 491): floors 1,264.1 and 1,264.4 at beta = 1.19, 1,276.6 and 1,277.2 at 1.31; family B's best cover 1,308.67; a random-start run 1,309.36 in another family. Better covers are not a way to 10%.
- status: computed; the 1,470/1,375/1,295 figures come from the planning model, unverified by me.
- uses: rd_floor_method, rd_floor_170000, s_prize, m_portfolio
- where: sublinear/README.md, "A floor under every cover" (after the 170,000 table); cover_floor_q213070.txt, cover_floor_w491.txt
- matters: Closes the cover-improvement door for the 10% target.

## rd_floor_formula | The same calculation above the end: how few rows a cover can leave
- kind: construction
- says: With a finite end price the recursion gives ln Z(beta) = theta - c (Q/ln^2 x) E(b beta ln x/ln Q); above the end D the entropy reaches zero at a finite temperature. Fewest rows / rows left by random classes: 0.22 (D/Q = 0.5), 0.48 (0.2), 0.63 (0.096), 0.73 (0.05), 0.88 (0.01); 1 - sqrt(K D/Q) for large Q. On the 89 moduli: 1,221 at 170,000 and 1,584 at 213,070 (entropy zero at 1,218 and 1,566), within 2% of the best covers (1,248; 1,609). The same function gives Result 3's table: predicted fewest rows of any N < 10^200 at depth 463, 1,000, 5,000, 50,000: 1,505, 1,262, 888, 550 against the ideal-search cutoffs 1,620, 1,319, 910, 574.
- status: conjectural (heuristic calculation); I confirmed the 1,218/1,221/1,566/1,584 outputs in cover_price.txt; the rest unverified.
- uses: rd_recursion, s_prize, rd_floor_170000
- where: sublinear/README.md, "The same calculation above the end"; cover_price.py floor, cover_price.txt
- matters: The prize of an ideal search (3.5-14.8 nats) and the floor under covers are one function of 460 ln^2 z/Q.

## rd_lp_floor | A certified floor for fixed small classes: 1,170 rows
- kind: theorem
- says: With the classes of the 22 smallest moduli fixed as in the best cover at Q = 170,000, 2,321 rows are alive; the fullest classes of the other 67 moduli add up to 1,218, a linear programme over them allows 1,151, the cover strikes 1,073 (leaving 1,248). So for that choice of small classes completions leave at least 1,170 rows (the bound is within 13% of the cover); what cannot be done is the enumeration of the e^77 (README; I get e^74.0) choices of those 22 classes. Earlier routes (fixed classes to 13 then fullest classes: capacity 3,500 for 2,957 rows; Hunter-Worsley; bounded differences) stay vacuous.
- status: computed; the LP value 1,151 is unverified (no LP solver here) and the floor is conditional on the 22 classes. I re-derived from the starting file 2,321 alive rows, the capacity 1,218 and 1,073 struck (1,248 left); the README's e^77 does not reproduce (ln of the product of the first 22 odd primes is 74.0).
- uses: rd_ub89, e_cover_opt
- where: fscan/cover/README.md, "What does not give the optimum: a formula, or a proof"
- matters: Shows how close a rigorous bound gets per choice of small classes; the 1,170 is not a floor for all covers.

## rd_families_campaign | Families at the campaign's target: family B stands
- kind: empirical
- says: A family = a frame, the classes of the smallest moduli. Every fleet cover has 3:2 5:3 7:5 11:6 13:5 17:4 19:10 23:4 29:21 31:13 37:20 41:1 (family B). B's frame ranks 121 of 92,160 by weighted rows left alive (3,822.9); the runner-up 11:4 13:6 17:4 ranks 13th. Contractor scan: bottoms of thirteen families in weighted rows: B 1,308.67 (1,245 rows below 170,000), 11:8 13:5 17:4 1,309.94, 11:8 13:4 17:4 1,310.48, then 1,313.20 to 1,318.19; of 25 random-start runs six end in B. Unrestricted runs hold 5-10 frames, shares depend on the seed (B reached by 1 of 3). Not excluded: a family no route reaches. After a design hit at 180,000 the two best families are even.
- status: computed; I confirmed the frame of all 3,924 covers in the 491 file and all 291 in the first-88 file (196 of 224 in the first-89 file); scan data unverified.
- uses: rd_families_complete, rd_rows_above, rd_491
- where: fscan/cover/README.md, "Families at the campaign's target"; family_search/ tools; sublinear/cover_floor_families.py
- matters: Backs the choice of family B with measurements rather than luck.

# D. The campaign: rows above the design level, 491, the record

## rd_rows_above | Rows above the design level decide the final record: two families
- kind: empirical
- says: The optimiser counts rows below Q only; a member also stops at the first uncovered prime above Q with N - q prime. Near-optimal covers split into two families. First 89: A (396 covers) 1,248.6 rows below 170,000, 1,168.2 below 158,209, 57.2 / 60.6 / 110.9 uncovered in 170-175k / 175-180k / 180-190k; B (224) 1,249.0, 1,174.0, 46.6, 49.1, 105.2. Same split on the 491 set (76 / 3,924) and the first 88 (653 / 291). B is 9-11 weighted rows better, about +1,000 expected final record. Direct test at Q = 60,000: 1,184 vs 1,186 successes, mean g - Q 3,766 vs 3,071 (4.7 standard errors). Rule: B while expected design hits left exceed about 0.5.
- status: computed; I recomputed all rows-below/above columns for the six lines and every header count (exact match); weighted rows, expected record and the hits-left rule come from the planning model, unverified.
- uses: m_density, rd_families_campaign, rd_491
- where: fscan/cover/README.md, "Rows above the design level: two families"; brainstorm/ab_rows_above.txt, rank_covers.py, soft_weights.py
- matters: Corrects the cost model's blind spot: the final record depends on rows above the design level.

## rd_491 | A better 89th prime (491), the first-88 set, and 32-bit ranges
- kind: construction
- says: The 89th modulus need not be 463: extending each first-88 cover by the best class of r gives 1,245 rows at 170,000 for 491, 1,246 for 557, 1,247 for 479, 503, 523, 613, 1,248 for 463. First 88 + 491: 1,800 covers at <= 1,247 rows, 26,000 at <= 1,248, 82,000 at <= 1,249 in 40 s; E = 29.86 against 29.93; 5-7% more successes per member at supply level; best 89th prime on the weighted measure up to 900 (1,287.2 vs 1,289.8). First 88 primes (3..461): optimum 1,255 (= 1,248 + 7), E = 30.03 against 30.17 for the campaign set (1,262): +14% at the best cover. 32-bit k ranges ending at 10^200 (top32): +5.6% successes per member.
- status: computed; I recounted the starting files (491: 2/93/1,828/2,001 covers at 1,245..1,248; first 88: 2/99/2/188 at 1,255..1,258) and the 175k/180k/190k/200k/213k files (1,291; 1,334 and 1,340-1,344; 1,420; 1,502; 1,609), all match; E values unverified.
- uses: e_cover_opt, rd_rows_above
- where: fscan/cover/README.md, "One more modulus", "Which 89th prime", "The first 88 odd primes"; make_specs.py (top32)
- matters: The cover on which the 24 Nov record was found.

## rd_record_160357 | The record 160,357 (24 Nov 17:11 UTC)
- kind: record
- says: A family-B cover of the 491 set with 1,250 rows below 170,000; the member's first 1,193 rows composite and 160,357 is row 1,193. Rechecked "from the N alone" by the research session: N - p composite for all 14,711 primes below 160,357; N - 160,357 a strong probable prime to 52 bases. 7.53% of the ceiling 2,130,704. Lean: `Record200_g160357.lean` (ECPP, kernel; commit 74b1dde, 17:49), generated from branch ccr-8ffe9d7a-4ni11u at bab405b. Supersedes 158,209 (23 Nov 12:48, first-89 set at 170,000).
- status: Lean-checked per README and commit message; the research recheck is text only (I confirmed 14,711 and 7.526%; N, row 1,193 and the 52 bases unverified).
- uses: rd_491, r_158209, e_fleet200
- where: fscan/cover/README.md, "One more modulus"; sublinear/README.md, top summary; Lean branch GoldbachGaps/Record200_g160357.lean
- matters: The standing budget record, found on family B as the family analysis predicted.

## rd_design_menu | What each design level buys, and the expected final record
- kind: empirical
- says: Best cover known per design level on the first 89 primes (8.0 days, 52M effective members per second, record 158,209): P(final >= 170k / 175k / 180k / 190k / 213,070) and expected record: 170k family B 0.89 / 0.52 / 0.19 / 0.017 / 7e-5, 175,900; family A 174,900; design 175k 175,600; 180k 174,900; 190k 173,000; 200k 170,400; 213,070 170,000. A far-threshold design raises its chance 2-4 times for 3,000-6,000 of expected record. With the corrected 8.9 days (from 24 Nov 04:05 UTC): 176,800, 176,500, 175,900, 174,200, 171,500, 171,100. Headline: expected final record 175,000-176,000 (8.2%), chance of 10% below 0.01%. Earlier plan (29M/s, 8.5 days): 172,700.
- status: computed (planning model), unverified by me; starting files at 190,000 (1,420 rows) and 200,000 (1,502 rows) checked.
- uses: rd_rows_above, m_portfolio, m_price
- where: fscan/cover/README.md, "What each design level buys"; brainstorm/design_menu.txt, portfolio_budget.py
- matters: Updates what the remaining fleet budget is expected to buy.

# E. The fixed-gap game and barriers

## rd_dual_game | The other direction: a fixed gap and the fewest digits
- kind: construction
- says: A number of size e^L carries the odd primes up to about L as moduli; the best cover leaves rho(D/Q) of the rows random classes leave, so one member in e^E succeeds with E = 2 C2 (pi(Q)/L) rho(kappa L ln^2 L/Q), zero once D(L) >= Q. Gap 200,000: members per success 10^15.4 at 200 digits (1,474 rows), 10^12.0 at 240, 10^8.6 at 300, 10^0.5 at 1,000; forced by divisibility from about 1,300 digits; ceiling 68.5 digits. Gap 1,000,000: 10^37.4 at 400 digits to 10^0.2 at 4,000; forced from about 4,700; ceiling 142; held 2,480. Gap 200,000 at about 225-230 digits costs what 170,000 costs at 200.
- status: conjectural (model prediction, untested: row counts from uarch and Opus started 25 Nov; the gap game was proposed by the user on 25 Nov); I checked the arithmetic E = p x rows = 35.36 = 10^15.36.
- uses: rd_floor_formula, rd_dn_table, m_ceiling, e_height
- where: sublinear/README.md, "The other direction: a fixed gap and the fewest digits"; cover_dual.py, cover_dual.txt
- matters: Opens a second game whose records need smaller numbers; the closeness to the ceiling is no better than the present campaign.

## rd_dual_cpu | The fixed-gap game costed on a processor
- kind: empirical
- says: One core, base-2 Fermat test with gmpy2: 0.11 ms at 200 digits, 0.30 at 300, 0.66 at 400, 30 at 1,500, 51 at 2,000. After a sieve to 10^9 (assumed 3 ns per mark) only members with few survivors are tested (cut 2.5-4 sigma below the mean). CPU-hours per hit, gap 200,000: 260 digits 49,000 tested plainly vs 3,200 (emptiest only), 300: 650 vs 55, 350: 18 vs 2.0, 400: 1.3 vs 0.18, 500: 0.04 vs 0.009. Gap 1,000,000: 1,200 digits 71,000 vs 12,000, 1,500: 420 vs 100, 2,000: 3.4 vs 1.3, 2,480: 0.38 vs 0.19, 3,000: 0.09 vs 0.05. Four cores for a day reach about 300 digits for 200,000 and 1,500 digits for 1,000,000.
- status: computed; README tables match `cover_dual_cpu.txt` (I compared); the 3 ns per mark and the 4,000-digit test time are assumptions, the sieve cost unmeasured.
- uses: rd_dual_game, e_selective
- where: sublinear/README.md, same section (last paragraphs); cover_dual_cpu.py, cover_dual_cpu.txt
- matters: Says which fixed-gap records a CPU can reach without a GPU.

## rd_prime_map_sharing | Neighbouring N share the prime map, but it excludes a cover
- kind: negative-result
- says: If the primes of a stretch of length L near 10^200 are known, every even N of it is decided by look-ups: N fails iff N - pi is a prime below the target for some stretch prime pi. About 68 marks per N at 170,000; some 6,000 operations per N against about 20,000 for a cover member. But a number without a cover succeeds at 170,000 with probability about e^-46.6 against 0.17 e^-30.0 for a sieved cover member: 4 times cheaper per number, about a million times worse per operation. A cover on the primes up to 13 gains a nat or two of sixteen. The two structures exclude each other (cover members lie 10^193 apart, sharing needs 2x10^5).
- status: computed (estimate; correction commit 4171931).
- uses: s_score, s_crt, e_cover_opt
- where: sublinear/README.md, "Why nothing known collects the prize" (paragraph "A second structure exists")
- matters: The one place prime rows are cheaper than arbitrary rows, priced and found unusable.

## rd_hardness_sat | For arbitrary rows the cover question contains SAT
- kind: theorem
- says: From a CNF formula with n variables and m clauses, Lean builds n prime moduli and m(n+1) rows of polynomial size such that the formula is satisfiable iff some residue vector covers every row iff some N is congruent to every row modulo one of the moduli (`sat_iff_coversList`, `sat_iff_exists_number`, `sat_iff_search`; commit 84040ae). With the black-box bound, nothing that treats rows or lists as arbitrary data, or only asks members how good they are, can beat enumeration. It says nothing about rows = primes below Q: a lower bound against every algorithm on that family is out of reach of any known proof technique.
- status: Lean-checked per README and Lean docstring (read, not run).
- uses: c_blackbox, c_deficit, s_verdict
- where: sublinear/README.md, "Why nothing known collects the prize" (paragraph with Manders-Adleman); Lean branch GoldbachGaps/Cap/Hardness.lean
- matters: Makes the "no sublinear method known" verdict precise: hard for arbitrary rows, open for the primes.

## rd_thinning_regularity | The 1/ln^2 z regularity of the ideal search is explained
- kind: empirical
- says: Cost times ln z and rows left times ln^2 z of the ideal search were nearly constant (241-265; 61,000-67,200). Lean's thinning law explains it: if the primes in (z, z'] kill rows independently, the deep table is the shallow one at another temperature, 1 - e^-beta = theta (1 - e^-beta'). Rows fall like (ln z)^-a, a = (e^beta - 1 - p)/(beta - p); measured beta 1.32, 1.23, 1.22, 1.25, 1.29 at depths 1,000-50,000 gives a = 2.1, 2.0, 2.0, 2.0, 2.1. The whole table follows from one shallow table within 0.4 nats from depth 5,000, 1.4 from 463. For primes above Q independence is a proved inequality (`thinCount_le_of_lt`), slack about 0.3 nats.
- status: Lean-checked per README and Lean docstring for the inequality (`Cap/Thinning.lean`); the measured betas computed; unverified by me.
- uses: c_thinning, s_prize, m_h1
- where: sublinear/README.md, Result 3 (paragraph "A regularity, and its explanation")
- matters: Turns an empirical "not a law" into a derived regularity and makes the last line of Result 3's table a safe direction.

## rd_lean_closed_formula | Lean's independent route to Result 3's counts and the ceiling
- kind: empirical
- says: A closed formula in the singular series of N, with one constant (c = 0.92, the rows of one N are less dispersed than independent ones) fitted on the Lean session's scan of every even N <= 10^12, gives ln(number of N < 10^200 with g >= Q) = 403.2, 395.7, 383.0, 371.5, 337.9 at Q = 213,070, 245,000, 300,000, 350,000, 500,000, within 0.1 nats of the sampler (403.3, 395.7, 383.1, 371.5, 338.0) with no shared code. One expected N at 2,133,689 (c = 0: 2,154,007), against the ceiling 2,130,704; the ceiling moves 0.4% for c from 0.5 to 1.3.
- status: computed; numbers match the Lean `scripts/lgs_heuristic/README.md` (read); not re-derived.
- uses: m_ceiling, s_prize, m_h1
- where: sublinear/README.md, Result 3 (paragraph after the counts); Lean branch scripts/lgs_heuristic/
- matters: A second route to the prize counts and the ceiling, agreeing to 0.14%.

# F. Verdict and corrections

## rd_verdict_25nov | The sublinear verdict as of 25 November morning
- kind: verdict
- says: The summary says "No method was found, and the reason is now understood and quantified": (a) the covers in use are the best there are; better covers are not a way to 10%; (b) the numbers wanted exist (about 10^175 even N below 10^200 have g >= 213,070) but 10^200 only pins residues up to 463, and beyond that every method examined costs more than scoring candidates; (c) a perfect search at the fleet's sieve depth stops near 16% of the ceiling; (d) nothing proves sublinear search impossible for prime rows. The ladder has nine rungs: rung 3 done over the integers (not in F_q[x]), rung 4 adds ListGain and Thinning, rung 9 (provable lower bound, 16,981) done.
- status: Lean-checked per README for rungs 1, 4, 9; the rest computed or conjectural as stated in the entries.
- uses: s_verdict, s_ladder, rd_floor_213070, rd_hardness_sat, rd_prime_map_sharing
- where: sublinear/README.md, "Where it stands (25 November, morning)" and "Ladder"
- matters: The programme's current answer: no sublinear method known, none ruled out, and the cover door shut.

## rd_retractions | Walk-backs and corrections since the snapshot
- kind: retraction
- says: (1) Brainstorm README: the soft-threshold conclusion ("sharp designs within 100-200 of the weighted objective, vectors stay") was wrong; the same weights showed near-optimal covers differ by 9-11 weighted rows (+1,000 expected record). (2) D(n) counts at n = 25-27 withdrawn 24 Nov after an overflow, restored after rerun. (3) The law's limit: 1.349 (24 Nov 17:53), "open between 1.1 and 1.349" (18:02), 1.1275 (19:08). (4) Marks per N at 170,000 83 to 68; cover-member operations 23,000 to 20,000. (5) Gap 1,000,000 forced from 4,500 to 4,700 digits. (6) Horizon 8.5 / 8.2 days corrected to 8.9; rate 29M to 52M per second. (7) The entropy-zero plateau argument is about 10 rows early at 170,000.
- status: retracted or corrected per the text and commit messages (checked against git history).
- uses: m_errata, v_brainstorm
- where: fscan/cover/brainstorm/README.md; sublinear/README.md; commits e2b791d, 4171931, cc53905, 785445a, be0d04b, d966273
- matters: Tracks which earlier claims on the map are now stale.

---

## Changes to existing boxes

- r_158209 | standing record is now 160,357 (24 Nov 17:11 UTC, 7.53% of 2,130,704, family-B cover of the 491 set); 158,209 (23 Nov 12:48) is second | fscan/cover/README.md "One more modulus"; sublinear/README.md top; Lean Record200_g160357.lean
- r_earlier | the ladder continues 158,209 then 160,357 | same
- r_cover15907 | "the record 158,209 reaches about ten times further" is now 160,357 (7.5% against 0.7% of the ceiling) | sublinear/README.md "At 200 digits, without luck"
- e_fleet200 | record chain ends 160,357 not 158,209; "10 fleet-days at 29M/s on 23 Nov 02:40" superseded by 8.9 days from 24 Nov 04:05 UTC and 52M effective members per second (model units); covers now include the 491 set and the first-88 set (smaller cards) | fscan/cover/README.md
- m_portfolio | expected final record 169,000-172,500 is outdated: 172,700 at design 170,000 with 158,209 and 8.5 days at 29M/s, then 175,000-176,000 (8.2%) at the measured rate; chance of 10% below 0.01%; family B worth +1,000; designs 170,000-175,000 equivalent, far-threshold designs cost 3,000-6,000 | fscan/cover/README.md "What each design level buys"
- m_price | "a success lands about 4,100 above the design target" depends on the cover's uncovered primes above Q: at Q = 60,000 mean g - Q was 3,766 against 3,071 for 41 against 55 uncovered primes in the next 4,000; row weights 1.00 (<= 164k), 0.83 (170k), 0.39 (175k), 0.12 (180k), 0.03 (185k) | fscan/cover/README.md "Rows above the design level"
- m_density | E counts rows below the design Q only; the final record also depends on uncovered primes above Q (a success survives each with probability 1 - p; confirmed 1,184 vs 1,186 successes, shift x1.23) | same
- e_cover_opt | "no closed formula and no proof of a floor": now a derived predictor (1,221 rows at 170,000, 1,584 at 213,070, within 2% of the best found, heuristic), measured floors 1,214 and 1,554, a certified floor 777 and D(89) < 35,000 (exhaustive), an LP floor 1,170 for fixed small classes; the 89-prime optimum 1,248 confirmed three ways (186 covers), 1,245 with 491 as the 89th prime. Also "Greedy gives 867" is greedy plus annealing (campaign 3); plain greedy ends at 912 in the same README | sublinear/README.md floor sections; fscan/cover/README.md
- m_rounding | Door 1 now measured: at 170,000 the best cover (1,248) is 34 rows (0.83 nat, factor <= 2.3) above the measured floor 1,214; at 213,070, 1,609 against floors 1,554-1,596 (<= 1.3 nats). The "annealed first-moment threshold 758" is explained: the first-moment count is off by 1.349 ln Q/ln x in the loss (it predicts about 790 rows at 170,000, found 1,248). The entropy-zero estimate of random-start runs is about 10 rows too early | sublinear/README.md "A floor under every cover"; fscan/cover/README.md Three conclusions 1
- m_doors | "Door 1 looks near-exhausted" is now measured closed: better covers are not a way to 10% | sublinear/README.md
- m_staircase | "about 4 nats of rounding mathematics plus a 10x fleet" is outdated: the whole rounding gap is at most 0.8 nat at 170,000 and 1.3 at 213,070 | same
- e_c15907 | "where complete covers stop is unknown": measured near 16,000 (about thirty covers at 15,907); recursion 15,973 or 16,069; 15,907 <= D(89) < 35,000 certified | sublinear/README.md "The last eighth of the range"
- r_cover_more | add: a 94th prime (499) does not pay; 16,981 stands; all four certificates kernel-checked (Records.lean, 9acf05d) | sublinear/README.md
- m_thm1 | the open "any f(x) -> infinity times x ln x" now has a sketch (Rodl nibble), measured ingredients (deletion gives about 1.5, not 2), certified covers to 614,101 and a conjectured D(n) ~ 1.1275 r ln^2 r | sublinear/README.md
- m_thm2 | "vacuous at record parameters": a computed non-asymptotic bound D(89) < 35,000 and exact D(n) to 35 now exist; window r ln r << D << r^(4+eps) restated; Lean: D(n) < (next prime)^2 - 2 for all n implies Goldbach | sublinear/README.md
- m_lower | add the conjectured forced reach (1.1275 + o(1)) ln N (ln ln N)^2, between the proved order and ln^2 N ln ln N | sublinear/README.md "Conjecture (counting law)"
- m_ceiling | Lean's independent closed formula (one fitted constant) gives one expected N at 2,133,689 (+0.14%; c = 0: 2,154,007), the ceiling known to about 0.4% | sublinear/README.md Result 3; Lean scripts/lgs_heuristic/README.md
- m_h1 | for primes above Q independence is a proved safe direction (`thinCount_le_of_lt`); the rows of one N are slightly less dispersed than independent ones (c = 0.92); direct test at Q = 60,000 agrees with (1 - p)^rows | sublinear/README.md Result 3; Lean Cap/Thinning.lean
- s_prize | the prize is the same function as the floor under covers (one function of 460 ln^2 z/Q); the 1/ln^2 z regularity is explained (a = 2.0-2.1, beta 1.22-1.32); the whole table follows from one shallow table within 0.4-1.4 nats | sublinear/README.md Result 3 and "The same calculation above the end"
- s_score | row sharing by convolution is now priced: 68 marks per N, 4 times cheaper per number, a million times worse per operation, and exclusive with covers | sublinear/README.md "Why nothing known collects the prize"
- s_ladder | nine rungs, not eight; rung 3 done over the integers (not in F_q[x]); rung 4 adds Cap/ListGain and Cap/Thinning; rung 9 (provable lower bound, 16,981) done | sublinear/README.md "Ladder"
- s_verdict | still none known, none ruled out; adds SAT-hardness for arbitrary rows, no lower bound for prime rows with known techniques, the prime-map barrier, and "better covers are not a way to 10%" | sublinear/README.md top and "Why nothing known collects the prize"
- v_brainstorm | the soft-threshold result of the brainstorm README is retracted; the family finding is worth about +1,000 expected record (about 0.2 nat), consistent with "nothing worth a nat" | fscan/cover/brainstorm/README.md
- m_errata | add: soft-threshold conclusion; D(n) counts n = 25-27 (overflow); 1.349 limit; marks per N 83 to 68; 4,500 to 4,700 digits; 8.5 / 8.2 days to 8.9 and 29M to 52M per second; plateau entropy 10 rows early | see rd_retractions

## Dependency notes

1. Exact D(n) and the record covers (rd_dn_table, rd_reach_table) give the measured law (rd_law_ln_g0); the law is derived by the price recursion with the Hardy-Littlewood pair-sum dispersion (rd_recursion), whose limit is 1.1275 (rd_limit), which becomes the conjecture (rd_conjecture); an upper bound of that shape on g0 would give Goldbach for large N through Lean's D(n) < (next prime)^2 - 2 implication (rd_dn_lean).
2. The same recursion with a finite end price (rd_floor_formula) predicts the fewest rows at 170,000 and 213,070; the partition-function floor (rd_floor_method, rd_floor_170000, rd_floor_213070) measures them; together they say better covers are not a way to 10%, which shuts "Door 1" and the "rounding mathematics" rung of the staircase.
3. The measured floors (1,214) are measurements limited by the search at the cold end; the only rigorous floors are the exhaustive 777 (rd_ub89) and the conditional LP 1,170 (rd_lp_floor); the gap between rigorous and measured is the overlap of the large moduli's classes, which the capacity cut cannot see.
4. The cost model counts rows below Q only; rows above Q (rd_rows_above) split near-optimal covers into families A and B; the scan (rd_families_campaign) shows B has the best bottom; B on the 491 set (rd_491) produced 160,357 (rd_record_160357); the design menu (rd_design_menu) turns this into the 175,000-176,000 expectation.
5. The prize of an ideal search (s_prize, 3.5-14.8 nats) and the floor under covers are one function of 460 ln^2 z/Q (rd_floor_formula); the thinning law (rd_thinning_regularity) explains its depth dependence and makes independence above Q a safe direction; Lean's closed formula (rd_lean_closed_formula) reproduces its counts.
6. SAT-hardness (rd_hardness_sat) and the black-box bound close arbitrary rows; the prime-map sharing barrier (rd_prime_map_sharing) closes the one structure specific to prime rows; so the verdict (rd_verdict_25nov) stays "none known, none ruled out".
7. The recursion also prices the fixed-gap game (rd_dual_game); CPU costing (rd_dual_cpu) turns it into hours per hit; it is untested until the uarch and Opus row counts come back.
8. The 94th prime fails (rd_cover_93_final); the certified upper bound D(89) < 35,000 (rd_ub89) and the measured end near 16,000 (rd_end_89) frame how far pure divisibility can go at 200 digits.

## Doubts

1. Pre-registration timing. The pair-sum figure 3,394 for the 1,228-moduli loss is stated as "computed and written here at 19:07 UTC" and the first long run (3,465.9) as "read here after the figure was written", but the Lean branch pushed that run's raw output at 18:56 (commit 99815c7). The clearly earlier figure is the range 3,330-3,414 (commit be0d04b, 18:02). The prediction table of 797/1,499/1,999 first carried a future time stamp (07:40) in a 07:30:59 commit, corrected to 07:31 (commit 785445a).
2. The 1,228-moduli test is one-sided: every finite run overestimates the loss, so a value from above agrees with the prediction without testing it from below; the "3,388-3,393" power law has three parameters for three points; the README itself says it is not a test. The strongest honest statement is "from above, 1.3% off at 500,000 sweeps".
3. The limit 1.1275 is the limit of the recursion, not shown to be that of D(n)/(r ln^2 r): the Lean referee check (25 Nov 08:40, after the README's last edit on this point) says so and puts the model error at the unquantified order of the 5% seen. The README at head states "In the limit it gives c = 0.887, that is D(n) ~ 1.1275 r ln^2 r" without that caveat, and the maximum (1.20) is reached at 10^12-10^15 moduli, ten orders beyond any data.
4. "Floor" names three different things: the measured partition-function floor (1,214 at 170,000), the certified exhaustive floor (777), and the LP floor for fixed small classes (1,170, valid only for the 22 small classes of the best cover, not for all covers). The summary uses "a floor of 1,214 rows under every cover" with the qualifier "where the two starts agree"; the cold end (1,241-1,247) is not a bound, as the README says.
5. "The count at the end of the 167 moduli (within 1.5%)" is a statement about the loss theta - ln g0; ln g0 itself differs by 2-12 nats (pair sum 110.2 against measured 98.6 at Q = 40,111). The recursion's end for 167 moduli (44,900-45,600) is 3-5% above the extrapolated end 43,600.
6. The first-89 starting file "family B" holds 28 of 224 covers in another frame (11:4 13:6 17:4 19:6 ...), the runner-up family, while later sections define a family by frame and say every fleet cover has frame B (true for the 491 and first-88 files, 3,924 of 3,924 and 291 of 291). The two meanings of "family" (split by rows above Q; fixed by the smallest classes) are not identical.
7. The planning horizon and rate change between tables (8.5, 8.2, 8.0, 8.9 days; 29M and 52M per second); the design menu file is computed for 8.0 days and the 8.9-day column appears only in prose, so 172,700, 175,900 and 176,800 are not directly comparable.
8. The Lean reproduction of the greedy table is "within a few percent": 9,769 against 10,428 at x = 463 is 6.3%; the headline 0.71-0.73 at large x is within about 1%. "D/(r ln r) at least 5.6 at n = 89 and 93" is 5.58 at n = 93.
9. "Greedy 867" on a box and "plain greedy ends at 912" in the same cover README (unchanged text): 867 is campaign 3's greedy-plus-annealing cover at Q = 122,000.
10. D(n) exactness for n >= 14 and the certified floors rest on one session's exhaustive programs (with independent count modes and a validation to n = 27); Lean checks only lower bounds beyond n = 9; I reproduced n <= 13 only.
11. Dual-game tables are predictions; the first test found on another branch (Opus, d960f7f, after the README head) left 3,028 rows with a greedy/descent/local-search cover for 629 moduli at Q = 1,000,003 against 2,301-2,315 in `cover_dual.txt` for 2,000 digits; not tempered, unverified by me, but it shows the tables are untested far from 200 digits. At the boundary the two estimators in `cover_dual.txt` disagree (1,300 digits, Q = 200,000: end of covers 197,753 below Q, yet "fewest rows" is nan with floor -32).
12. In the LP-floor remark the README says the 22 small classes have "e^77 choices"; the product of the first 22 odd primes (3..83) is e^74.0 (e^72.6 for nonzero classes), a small numerical slip that does not change the point.
13. The 160,357 recheck (row 1,193, 52 bases) is described in the READMEs but no N or script is in the research files; only the Lean file and the other branch hold the data.
