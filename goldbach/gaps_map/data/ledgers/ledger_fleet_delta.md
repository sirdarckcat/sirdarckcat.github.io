# Delta ledger: fleet, exact search and lead branch since the 23 Nov snapshot

Compiled 2026-11-25 by reading text files and committed data only. Nothing from the repo was run; where I recomputed a number it was
with my own scripts (python3 -I, and one small C program) on data read from the repo. g(N) = least prime p with N - p prime.
Paths are relative to `goldbach/` unless stated; every `where:` names its branch.

Scope and sources.
- LEAD branch `ccr-2ce9e63a-hn0fuw` at 43ab0b3, read as `git diff 85aef81..HEAD` (23 Nov 13:13Z to 24 Nov 17:50Z): `RESULTS.md`, `phd/campaign3_gpu/`
  (README hunk of lines 524-809, `runlogs/2026-11-24/`, `famB/`, `v491/`, `s32/`, `l4op/`, `m88f/`, `vtop/`, `sievepack/`, `bringup/`, `rec160357/`), `records/budget_1e200_200digit_g160357/`.
  The earlier records' READMEs were read for the chronology. `lean/` was skipped except for the list of merged files (entry fd_lean_merge).
- FLEET (coder) branch `ccr-8ffe9d7a-4ni11u` at ebb6e1e: the 8 commits after the lead's merge point bab405b (24 Nov 19:23Z to 23:01Z): second round of replacements, Colab's G4 and L4 limits, new rule of 22:46Z.
- EXACT-SEARCH (uarch) branch `ccr-b8c25887-i6tn9f`: worktree at 2cdb2cb, read with `--since 2026-11-23 16:00` (sieve/near-miss work to 23 Nov 18:20Z, then `sublinear/` from 24 Nov 13:52Z to 21:39Z).
  The branch moved to 018b7ed (25 Nov 08:53Z, fermatw); I read that commit from the shared object store (entry fd_fermatw).

What I recomputed myself (scripts in `scratchpad/gbmap2/work_fleet/`):
- from `record.json` of 160,357: 89 moduli (3..461 and 491), M = 2*prod(r), N = N0 + k*M, 200 digits, 1,250 residual primes, 1,193 below g, 13,517 covered below g, all 1,193 fail base-2 Fermat, N - g passes; the top and bottom windows;
- prime counts quoted in the record READMEs (14,711 below 160,357; 15,496 odd primes below 170,000);
- D(n) and the number of optimal vectors for n = 1..11 by an independent bitset search; all 81 vector lines in the uarch result files (n = 1..26, 29..35) strike every odd prime below D and not D;
- an independent C program for the fullest-class floor (no ARGM): reproduces -68 (j = 4) and 401 (j = 6) on the 89 moduli at Y = 170,000, gives 220 (j = 5) and 540 (j = 7) which the repo does not state, and its proof mode refutes the next prime for n = 6..20 and finds covers at D for n = 9, 12, 15, 18;
- row counts of the family-B start covers (two covers at 1,245 rows; 20 random spot checks equal their declared counts); the record's cover equals all 53 classes common to the 3,924 family-B starts;
- sums of the logged expectations in the run-log summaries; per-card rates; compute-unit arithmetic.

What I could not check: any Lean statement (statuses are quoted from READMEs and commit messages); any GPU timing (measured by the GPU session; I read its logs); the ECPP certificates and PARI checks of 160,357;
the 89-moduli exhaustive proofs (D(89) < 35,000, floors at j = 8 and 10: my j = 8 run had not finished when I stopped, so those two are unverified); the DRAT proofs; the research branch (outside my scope; quoted only where it states a number about uarch's results).

Entry count: 31 (exact search 12, records and certification 3, fleet design and rates 6, sieve engineering 7, Colab and fleet state 2, contingency and Lean merge 2). Ids start with `fd_`.

---

# A. Exact search and the cover floor (uarch branch)

## fd_cover_ub | cover_ub: rigorous cover bounds by modulus branching and the fullest-class bound
- kind: algorithm
- says: Rows are the odd primes below Y, moduli the first M odd primes, a vector gives each modulus one class. At a node with unstruck rows U and free moduli, cap = sum over free moduli of their fullest class inside U; every vector below the node leaves at least f = |U| - cap rows. A child (m, c) has f' >= f + mx[m] - h[m][c], so f never decreases. Proof mode prunes f >= 1. ARGM adds 1 for each other modulus whose single fullest class the strike meets. Floor mode fixes the first j moduli and reports the least f. I checked the inequalities by hand and re-implemented floor and proof modes.
- status: proved-in-text (short lemma); computed; my independent re-implementation agrees wherever I could run it
- uses: fd_dn_table, fd_floor170, fd_fast5, l_cover
- where: sublinear/cover_ub.c (header comment and dfs); uarch branch, commits 86b00de, 3539913, b081d24, 8ce578b
- matters: first exact tool that reaches 89 moduli; turns "no proof of any floor" into a certified, though weak, lower bound.

## fd_dn_table | Exact cover depth D(n) is known to n = 35
- kind: theorem
- says: D(n) = largest, over vectors on the first n odd primes, of the least odd prime left unstruck. New exact values, n = 16..35: 709, 739, 859, 907, 1,051, 1,213, 1,279, 1,381, 1,471, 1,567, 1,669, 1,801, 1,933, 2,137, 2,311, 2,521, 2,647, 2,749, 2,953, 3,079 (n = 1..15 were 5, 7, 19, 31, 43, 67, 103, 163, 181, 223, 271, 331, 419, 499, 613). Each value is attained by a printed vector and refuted at the next prime by exhaustive search. D(29), D(30), D(34) equal research's prediction or tempering wall; D(35) = 3,079 lies inside research's forecast window 3,040..3,190 (point forecast 3,110). Largest proof: n = 35, 8.97e9 nodes, 3,476 s; the whole climb took 6,226 s on 3 threads.
- status: computed (exhaustive). I re-derived n = 1..11 and rechecked all printed vectors; upper bounds for n > 11 not re-run. Lean has D(0..9) as theorems per the Lean branch README
- uses: fd_cover_ub, fd_fast5, l_cover
- where: sublinear/desert_fast3_results.txt, desert_fast5_results.txt, cover_ub_results.txt; uarch branch, a81cc6f to 782f88d
- matters: D(n) is the luck-free reach of n moduli; exact values now cover n = 16..35, still far from n = 89.

## fd_dn_counts | Number of optimal vectors for n = 2..28
- kind: empirical
- says: Vectors that strike every odd prime below D(n) with every modulus used. n = 2..12: 2, 1, 2, 2, 6, 6, 1, 2, 1, 17, 9. n = 13..28: 2, 1, 3, 2, 2, 4, 2, 1, 2, 2, 1, 1, 2, 12, 10, 1. cover_ub's count mode equals the earlier table for n = 2..26 and gives 10 (n = 27) and 1 (n = 28), both confirmed by desert_fast5 (698,600,428 and 2,927,575,954 nodes). Brute force over all vectors agrees for n <= 9; a SAT count agrees for n <= 12. I counted n = 1..11 myself: 1, 2, 1, 2, 2, 6, 6, 1, 2, 1, 17. No counts exist for n = 29..35.
- status: computed
- uses: fd_dn_table, fd_cover_ub
- where: sublinear/cover_ub_results.txt (count mode), desert_fast4_checks.txt, desert_fast5_results.txt; uarch branch (2cde0e9, 8ce578b, 2ff3173)
- matters: optimal covers are nearly unique (1 to 17 vectors among a product of all class choices), so no slack to reshuffle.

## fd_D89 | D(89) < 35,000: complete covers on the 89 moduli end below 35,000
- kind: theorem
- says: Proof mode on moduli 3..463: no vector strikes every odd prime below Y. Nodes and seconds (4 threads, ARGM from Y = 60,000): Y = 170,000: 6,240, 0.2 s; 80,000: 93,820; 60,000: 119,427, 1.0 s; 45,000: 2.26M, 11.8 s; 40,000: 25.5M, 80 s; 37,000: 115M, 512 s; 35,000: 457,405,148, 3,700 s. With the complete cover at 15,907 (Lean-checked): 15,907 <= D(89) < 35,000. The walk was stopped by choice (research asked for at most one hour); nodes grow about fourfold per 2,000 off Y there (115M to 457M: x3.98, my arithmetic).
- status: computed ("certified" in the file). Not re-run by me (unverified); the pruning rule is sound by my hand check
- uses: fd_cover_ub, e_c15907
- where: sublinear/cover_ub_results.txt (D(89) lines); uarch branch, 86b00de, 3539913, 187753f
- matters: first upper bound on the complete-cover game at 200 digits; research believes the true end is near 16,000.

## fd_floor170 | Certified floor at Y = 170,000 on the 89 moduli: every vector leaves at least 777 rows
- kind: theorem
- says: Fix the classes of the first j moduli (3, 5, 7, ...) in every way and bound the other 89 - j by their fullest classes. Every vector on moduli 3..463 leaves at least -68 (j = 4), 401 (j = 6; 106,026 nodes), 644 (j = 8; 4,468,093 nodes, 176 s) and 777 (j = 10; 726,699,931 nodes, 12,244 s on one thread) of the 15,496 odd primes below 170,000 unstruck. Best covers known leave 1,248 (3..463) and 1,245 (491 set, recomputed by me). 777 is 62% of 1,248: the theorem still allows 471 rows, about 11 nats at 0.024 nat a row (my arithmetic). My program gives -68, 220, 401, 540 for j = 4..7.
- status: computed ("certified" in the file); j = 4 and 6 re-derived by me, j = 7 is new from me; j = 8 and 10 unverified
- uses: fd_cover_ub, e_cover_opt, m_rounding
- where: sublinear/cover_ub_results.txt (floor lines); uarch branch, b081d24, 2cdb2cb
- matters: first theorem about every cover at the campaign's target; far below the 1,247-1,248 that research measures, so it does not close Door 1.

## fd_validation | How cover_ub and the D(n) searches were validated
- kind: empirical
- says: (a) cover_ub_validate.sh, n = 2..27: at Y = D(n) a cover is found and rechecked, at the next prime NO COVER (n = 27: 27,721,428 nodes, 7.9 s); "VALIDATE OK". (b) Floor mode equals brute force over all vectors on 6 moduli (Y = 80, 120, 200, 300) and 7 moduli (Y = 150, 250, 400); floors at depths 1..M never decrease. (c) D(28) = 1,933 by two programs. (d) Counts agree across cover_ub, desert_fast4/5, brute force and SAT. (e) Each cut can be switched off with identical answers. My additions: my floor program equals brute force on four toy cases; my proof mode refutes the next prime for n = 6..20 (n = 19: 492,607 nodes).
- status: computed; no second program exists for the 89-moduli proofs (unverified there)
- uses: fd_cover_ub, fd_fast5, fd_dn_counts
- where: sublinear/cover_ub_validate.sh, cover_ub_results.txt, desert_verify.sh, desert_fast4_checks.txt; uarch branch
- matters: the n <= 28 agreement is strong; the extrapolation to 89 moduli (D(89), floors) rests on the same lemma, not on a second implementation.

## fd_fast5 | desert_fast5: one lemma, several cuts, up to thousands of times fewer nodes
- kind: algorithm
- says: Lemma: in a vector that beats the incumbent, every free modulus sits in a class within the margin of its fullest class. Cuts: skip non-qualifying children, dead node when a row no qualifying class strikes, forced moduli, branching on the modulus with fewest qualifying classes (MBRPOL 2), then ARGM and MATCH. Proof nodes: n = 21: 1.19e9 to 6.1e6 to 2.7e5; n = 22: 5.02e9 to 3.7e7 to 7.1e6 to 9.6e5. D(23) from scratch: 34.4e9 nodes, 4,559 s (desert_fast4) against 5.9e6 nodes, 3.7 s. Bug: branchings with more than 32 qualifying classes overflowed ord[MAXN]; found by cover_lns's check, fixed in 6caad7d; reruns of the n = 25, 26 proofs gave identical node counts and D(27) = 1,801 again.
- status: computed
- uses: fd_dn_table, fd_validation
- where: sublinear/desert_fast5.c, desert_fast5_results.txt (sections 2-11); uarch branch, 1bbea7a to 75f2ff0
- matters: made n = 22..28 exact in minutes; its cuts are the ancestor of cover_ub.

## fd_lns | Large-neighbourhood search around the 15,907 cover finds nothing
- kind: negative-result
- says: cover_lns.c frees k moduli of research's 89-modulus complete cover, keeps the rest, and asks the exact search whether the freed moduli can strike every prime up to the first unstruck prime (15,907). A check mode passed for k = 12..32. Results, no improvement anywhere: k = 24 over all moduli, 3,000 steps, each infeasible within about 10 nodes; k = 32 on pools of 89, 60, 45, 36 moduli, 2,000 steps each (up to 27M nodes); k = 28, 2,000 steps; sideways moves, 20,000 steps each for k = 24, 28, 32. The cover is locally rigid; striking 15,907 needs the small moduli to move (3 alone strikes 241 primes below 15,913 that nothing else strikes).
- status: computed
- uses: fd_fast5, e_c15907
- where: sublinear/cover_lns.c, cover_lns_results.txt; uarch branch, 62effa6
- matters: local search will not extend the 89-modulus complete cover; any gain must restructure the small moduli.

## fd_drat | SAT cross-check and DRAT proofs for D(9..12), not yet checked
- kind: engineering
- says: For n = 9..12 (D = 181, 223, 271, 331; next primes 191, 227, 277, 337) the CNF "some vector strikes every odd prime below p'" is UNSAT in CaDiCaL 1.9.5. DRAT proofs: 784 KB, 5.1 MB, 28 MB, 148 MB. The CNF files and the xz proofs for n = 9, 10 (146 KB, 994 KB) are committed; n = 11, 12 regenerate bit-identically (SHA-256 listed). No DRAT checker was run ("running a downloaded checker was not permitted"). SAT time grows about x9 per n (36 s at n = 12, 329 s at n = 13), so it is not a check beyond n of about 14.
- status: computed; DRAT proofs unchecked
- uses: fd_dn_table, ext:CaDiCaL, ext:drat-trim
- where: sublinear/drat/README.md, desert_sat.py; uarch branch, 2a79d85, c67d7a7
- matters: an independent route for the Lean session to certify the upper bounds beyond n = 9.

## fd_proofcost | Proof cost against Y / D(n): the cut weakens fast with the number of moduli
- kind: empirical
- says: At n = 30 (D = 2,311) the proof that nothing strikes every odd prime below Y costs, in nodes: 55.8M at the next prime 2,333 (38.9 s on 4 threads), 19.7M at 2,437, 5.57M at 2,543 (1.1 D), 422,662 at 2,777 (1.2 D, 0.4 s), 150,536 at 1.3 D, 12,589 at 1.5 D, 854 at 2 D, 115 at 3 D. On 89 moduli 457M nodes buy only Y = 2.2 D(known) = 35,000. Requested by research as a calibration for the D(89) walk.
- status: computed
- uses: fd_D89, fd_dn_table
- where: sublinear/cover_ub_results.txt (calibration block); uarch branch, 2bc0f60
- matters: shows why the upper bound for n = 89 stalls at 2.2 D while n = 30 is closed from 1.2 D up.

## fd_fermatw | IFMA base-2 Fermat tests for 300-400-digit members (branch head 018b7ed, 25 Nov 08:53Z)
- kind: engineering
- says: fm13 (13 limbs of 52 bits, numbers up to 664 bits) generalised to L limbs (numbers up to 52 L - 12 bits); L = 20, 21, 23, 26 serve 300, 320, 350, 400 digits. One core of a 2.1 GHz Sapphire Rapids Xeon: 34.6 us a test at L = 20 against 401 us for gmpy2 (11.6x); 105.7 us against 857 us at L = 26 (8.1x). On a 400-digit g >= 200,000 cover (1,010 rows, 65,536 members) the scan statistics equal gmpy2's (tests 42,483, prp 1,312) at 10,789 members/s instead of 1,874. search_c.py takes fm13 up to 664 bits and fmw above; the commit says it used fm13 at any size before, "which is wrong above 664 bits".
- status: computed (tests against Python pow for L = 13, 20, 21, 23, 26 per the commit message); not re-run by me (unverified)
- uses: g_f52
- where: fermatw/README.md, fmw.c, gen_fmw.py, test_fmw.py; sieve200/search_c.py (_fermat_members); uarch branch 018b7ed
- matters: a CPU path for 300-400-digit games; also flags a range error in the older CPU Fermat path (see Doubts).

# B. Records and their certification (lead and fleet branches)

## fd_rec160357 | Record g(N) = 160,357 for a 200-digit N, 24 Nov 17:11:16Z
- kind: record
- says: N = 9.53e199, k = 19,221,795 of vector q170000_m89r491_p0c00524_v232 (chunk 524 of gold-g4d's generator). Moduli: the first 88 odd primes (3..461) and 491; M = 2*prod(r) has 193 digits; 1,250 residual primes below 170,000. g is residual row 1,193 (from 0): 57 residual rows lie at or above g, 73 at or above 158,209. Witnesses for the 14,711 primes below g: 1 parity, 13,517 by a modulus, 586 trial division, 607 failed strong base-2 tests. Found on gold-g4d (RTX PRO 6000, Colab G4) by search_gpu5.py in vector mode; +2,148 over 158,209; closeness 7.53%. I recomputed the cover, counts and Fermat checks from record.json.
- status: computed; Lean-checked per commit message (see fd_rec_cert)
- uses: fd_nearmiss_design, fd_491, fd_famB, fd_vtop, r_158209
- where: records/budget_1e200_200digit_g160357/ (README.md, record.json, found.jsonl); RESULTS.md top section; lead branch
- matters: largest g known below 10^200; its N is larger than 158,209's, so both stay on the frontier.

## fd_rec_cert | Certification route of 160,357
- kind: verdict
- says: Found 17:11:16Z (the watcher copied the line off the card), checked at once by rec160357/quick_check.py (gmpy2 from the vector's spec), certified 17:13Z by certify_c3.sh with CLAIM_Q = 158209: witnesses for all 14,711 primes; PARI primecert(N - g) valid; ecpp_check.py re-verifies the 21-step certificate with gmpy2 only; slop's stdlib verify_record.py rebuilds N from the 89 classes and k and checks g > 158,209, N < 10^200, digits <= 200 (PASS); direct gmpy2 and PARI checks. Lean: Record200_g160357.lean (generated from the fleet package at bab405b) proves exists_lt_ten_pow_200_least_summand_160357; 89 moduli, 1,193 residual rows, 21 ECPP steps; builds in 8.5 minutes and 5.7 GB; axioms propext, Classical.choice, Quot.sound; commit 17:49Z, 38 minutes after the find.
- status: Lean-checked per commit message 74b1dde (I cannot check Lean); the other checks per README logs, not re-run
- uses: fd_rec160357, x_least, x_ecpp_step, x_coveredin
- where: records/budget_1e200_200digit_g160357/ (check_cert.log, ecpp_check.log, verify_stdlib.log, crosscheck.log); lean/GoldbachGaps/Record200_g160357.lean, Records.lean; lead branch
- matters: record certified in the kernel less than an hour after the find, by the same route as 158,209.

## fd_nearmiss_design | Why 160,357 counts as a near-miss of a design target
- kind: verdict
- says: The design target is Q = 170,000. Each tested member is tried row by row, q ascending, until its first probable prime, so that row is g(N) whatever the design. A member whose first prime row is at or above the record in hand is a near-miss: re-verified on the CPU and written with near_miss true. 160,357 is row 1,193 of 1,250, below Q. A design hit (every row below Q composite) is worth about +10,000 in g (lead, 23 Nov); a typical near-miss lands about 2,000 above its threshold. Expected near-misses at or above 158,209 on the RTX cards between the two records: 1.60 (0.42 + 1.17); found 1; P(at least 1) = 80%.
- status: computed; the 1.60 is the cards' own logged expectation, not re-derived
- uses: fd_rec160357, fd_day_one, c_hits, m_density
- where: phd/campaign3_gpu/README.md ("The record of 2026-11-24"; near-misses, 23 Nov 02:40Z); RESULTS.md; sieve200/cuda/NEARTRUNC.md (lead's decision note); lead and uarch branches
- matters: explains how the record rose without a design hit: near-misses are the ladder, a design hit the jump.

## fd_day_one | Day-one report at Q = 170,000 (24 Nov 04:05Z) and per-card rates
- kind: empirical
- says: Window from about 03:54Z on 23 Nov. Design hits (g >= 170,000): 0 found, 0.23 expected. Near-misses: 1 found (158,209), about 0.98 expected. Fleet about 0.29 expected design hits a day (RTX 0.25, L4 0.031, T4 0.005); RTX about 1.4 near-misses a day at 158,209. Per card: RTX 5.48 slices a second of 2^24 members (92M members/s), 9.8e-7 design hits/s; L4 0.25 slices/s of 2^25, 1.19e-7/s; T4 0.112 slices/s, 5.4e-8/s. Compute units 7,967.7 at 37.12 an hour: the 1,800 CU mark in 6.9 days (about 1 Dec 02Z). The price list (12.7 fleet-days per success at 170,000) implies 0.079 a day: the fleet runs 3.7x faster than priced (my arithmetic).
- status: computed (the cards' own logs, tally_rt2.py output); arithmetic re-derived
- uses: fd_calibration, fd_fleet_state, m_price, e_fleet200
- where: phd/campaign3_gpu/runlogs/2026-11-24/ (day_one_report.txt, rates_0400.txt, tally_0400.jsonl.txt); lead branch
- matters: sets the current pace (about 3.4 fleet-days per expected design hit at 7 GPUs) against the older price list.

## fd_calibration | Expected against found, since the campaign began
- kind: empirical
- says: TALLY.md (23 Nov 02:10Z, not updated since): 9 hits found against 9.21 expected across the Q = 122,000, 140,000 and 150,000 campaigns (3 vs 2.09, 4 vs 5.03, 1 vs 1.27, 1 vs 0.70, plus 0.11). Since the move to Q = 170,000: 0 design hits found against about 0.41 expected (my sum of the logged summaries through the second-round snapshots of 24 Nov, excluding gold-gpu's lost records and the live cards' last hours; P(0) = 66%). Near-misses at the threshold in force: 2 found (158,209 and 160,357) against about 1.8 logged on the RTX cards (0.55 + 1.27, thresholds changing in between). hits.jsonl still ends at 157,837.
- status: computed; sums are mine, double counting between inherited snapshots avoided but not proven
- uses: fd_day_one, c_hits, m_density
- where: phd/campaign3_gpu/TALLY.md, hits.jsonl, runlogs/2026-11-23/ and 2026-11-24/summary.txt; lead and fleet branches
- matters: the cost model has held for 9 low-target hits; the Q = 170,000 target has had no design hit yet, which is the expected outcome at this stage.

# C. Cover design for the campaign (family B, 491, supply)

## fd_famB | Family-B covers: the criterion moved from rows below the record to rows above Q
- kind: construction
- says: Lead's criterion change: what decides the final record is how far above 170,000 a design hit stops, so the uncovered primes in [170k, 175k) and [175k, 180k) count. Research's check 6: 57.2 / 60.5 in the first m89 chunks (family A), 49.1 / 52.1 in the 58e95e3 chunks, 46.1 / 50.4 in the 491 chunks. Start files: 3,924 family-B covers on the 491 set (1,245-1,248 rows), 258 on the m88f set (1,255-1,258). The record's cover equals all 53 classes shared by the 3,924 starts and differs from the nearest start in 2 of 89. My estimate of the expected landing above 170,000 (p = 0.024 a row): 3,550 (family A), 4,130 (A+B), 4,340 (491 chunks): about +800.
- status: computed; the landing estimates are my arithmetic, not in the repo (the price list's "about 4,100" agrees with the A+B figure)
- uses: fd_491, fd_contingency, m_price
- where: phd/campaign3_gpu/famB/ (check6_results.txt, check6.py, starts_*.txt); README ("Family-B covers"); lead branch
- matters: trades a few near-miss chances for a higher landing point after a design hit.

## fd_491 | The 491 family on the RTX cards
- kind: construction
- says: Research's bbc8cd8: the first 88 odd primes (3..461) plus 491 instead of 463; M has 193 digits (192.7 for 3..463). The lead approved it behind a six-point gate on gold-g4c: deep sieve equal to the CPU feeder and Fermat flags equal to gmpy2; GPU path equal to search_c.py; known case 46 = 46; full window at f = 0 gives 1,066 = 1,066 near-misses before and after one-pass; design hits a second x1.061 and near-misses x0.9995 against 24 vectors of the 463 chunk (bars +3%, -3%). Long runs, cap 1,248-1,249 (about 30,000 batches a card): design hits x1.085 (x1.051 against gold-g4 alone), near-misses x0.99 (x0.96); cap 1,250: x1.067 and x0.98.
- status: computed (the cards' own logs)
- uses: fd_famB, fd_rec160357, e_cover_opt
- where: phd/campaign3_gpu/v491/, bringup/vecgen491.sh, runlogs/2026-11-24/day_one_report.txt; lead branch
- matters: the record's vector comes from this family; the 463 set is no longer the fleet's cover.

## fd_gen_supply | Generator supply, cap steps and the row guard
- kind: engineering
- says: The 491 generators walk covers at a row cap of 1,248, stepped to 1,249 and 1,250 (CAPMAX 1,252 on replacements). Lead's rules (23 Nov 21:19-21:46Z): step when a walk gives under 100 new vectors, or at once when under 3,500 (about 10 minutes) are ahead after a short chunk; the row guard's base is the first-cap mean (1,248.000) plus 1 a step, and trips (f to 0.98) above +2. At 1,249 each card made about 129,000 vectors (387,000 in all; research estimated 290,000); yield per walk fell from 1,000 to 500 (01:10Z), 180 (02:25Z), 100-150. About 3.7M covers at <= 1,250 last about 2.5 days at 1.4M vectors a day (3.9 days with 2 RTX, my arithmetic).
- status: computed
- uses: fd_491, fd_fleet_state
- where: phd/campaign3_gpu/README.md ("Family-B covers", cap rules), bringup/README.md, runlogs/2026-11-24/; lead and fleet branches
- matters: a GPU must never wait for vectors; each cap step costs a row, about -2.4% of design hits.

# D. Sieve and engine engineering (uarch and fleet)

## fd_vtop | Top-of-range windows: N from 2.15e199 to just below 10^200
- kind: engineering
- says: --vector-place top: a vector's 2^24 window is [kend - 2^24, kend) with kend the first k with N >= 10^200, instead of starting at the first 200-digit k. A larger N has a lower prime density. Uarch's computed yield on the production vector: x1.0155-1.0168 (x1.0185 at 420 alive rows) for +0.1% cost; GPU session's 24 test vectors: near-misses x1.0113, hits x1.0122; production: near-misses a batch x1.0185, design hits a second x1.015-1.017 on gold-g4 and g4c. Lead approved 16:36Z, deployed 17:29Z on 23 Nov. For the record's vector the top window is [3,382,594, 20,159,810) and k = 19,221,795 (94.4% along) lies outside the bottom window [2,015,981, 18,793,197): this member would not have been tested under bottom placement (my computation).
- status: computed; the record fact is my derivation
- uses: fd_rec160357, fd_batch_model
- where: phd/campaign3_gpu/vtop/, README; sieve200/cuda/search_gpu5_vectop.patch, HEADROOM.md; lead and uarch branches
- matters: +1.5% for nothing, and the record member needed it.

## fd_onepass | One-pass generate kernel (DEEP_GEN_ONEPASS)
- kind: engineering
- says: gbig_gen_st visited every (prime, row) pair twice (count, then place). In the one-pass kernel each of 256 bins owns 40 shared-memory slots and the counting atomic's rank places the mark; overflow list of 128 entries (0.55 entries a CTA expected); no scan. Uarch expected generate 17-21 ms; measured 28.75 to 22.15 ms a 2^24 window (-23%), sieve phase 51.2 to 44.4 ms (-14%), batch x0.957-0.973, design hits a second x1.033. Deployed 18:09:59-18:11:05Z on 23 Nov. L4 windows (2^25, rcta 2) put about 48 marks in a bin: 75 slots (0.04 overflow entries a CTA); the code now refuses a geometry with more than 32 expected overflow entries.
- status: computed (GPU session's gates, identical slice lines, known case 23 = 23); not re-run
- uses: fd_sieve_chain, fd_l4op
- where: sieve200/cuda/DEEPSIEVE.md (last sections), phd/campaign3_gpu/sievepack/opab_rtxpro6000.txt, opgate_rtxpro6000.txt; uarch branch f1b904a, fc12768
- matters: the last large sieve item of 23 Nov; its estimate was 3x too optimistic on generate, a repeated pattern.

## fd_sieve_chain | The sieve phase of a window from 83.7 ms to 44-50 ms, and what it is worth
- kind: engineering
- says: Sieve phase of a 2^24 window on the RTX PRO 6000 (bench_batch): 83.7 ms (23 Nov 13:12Z) to 67.7 (packed bins, hoisted loops, tile unroll 4, prefetch; batch x0.959-0.970, design hits/s x1.04-1.05) to 63.5 (flat flush, grid order; x0.957-0.967, x1.035) to 50.7 (generate unroll 4, clamped loads; generate 40.3 to 28.7 ms; 0.755 s a batch) to 49.6 (LEAN, -1.5 ms, x0.9875) to 44.4 (one-pass). Batch: 0.945 s (f = 0.985 before fused rounds) to 0.858 to 0.755 to about 0.732 s: x1.29 in rate, +0.26 nats, about +1,200 in g at 0.21 nat per 1,000 (my arithmetic).
- status: computed (GPU gates by card); the nat conversion is mine
- uses: fd_onepass, fd_batch_model, e_gpu, m_price
- where: HEADROOM.md (status table), sieve200/cuda/DEEPSIEVE.md (splitab, flushab, genab, LEAN, bundle8-9), phd/campaign3_gpu/sievepack/*.txt, README lines 535-585 and 638-652; uarch and lead branches
- matters: roughly a quarter of a nat of rate in one day; none of the later items individually reached 1%.

## fd_batch_model | A batch is the sum of sieve time and Fermat time; f and B re-optimised
- kind: empirical
- says: The GPU session's keep-fraction sweep is exactly linear: batch = 0.371 + 37.97 (1 - f) s, the fixed 0.371 s being four windows' sieve and tail alone: the sieve is added to the Fermat time, not hidden. With real alive counts the same line predicts the design-hits sweep within 0.3-3%. Today the fixed part is about 0.243 s (32% of 0.755 s), so 1 ms off a window is worth up to 4 ms of a batch. Model optimum f = 0.9875-0.99 (+1.1%), but f is tied to cover supply; B = 1e8 stays. Failed prediction: the L4 at f = 0.985 was predicted x1.13, measured x1.0001; its fixed part is 3.27 s, not 1.8 s.
- status: computed
- uses: fd_sieve_chain, e_selective, m_density
- where: HEADROOM.md ("A model that reproduces the measured sweep", "A failed prediction", "The sieve depth B"); sieve200/cuda/selstat/; phd/campaign3_gpu/l4f/ab_l4_f985.txt; uarch and lead branches
- matters: rule kept: a card's fixed part comes from two of its own batch times, never from component timings.

## fd_neartrunc | Near-miss truncation was measured and declined
- kind: negative-result
- says: Selecting members by the alive rows below the near-miss threshold G, not by all rows, gives x1.063-1.068 expected near-misses per kept member (13 windows, B = 1e8) and x0.936-0.939 design hits. The gain falls with G: x1.12 at 146,191, x1.063 at 157,837, x1.02 at 165,000, 1.000 at Q. No kernel change; the sieve shrinks 6.7%. The lead declined it at 16:03Z on 23 Nov: the objective is the final record, dominated by a design hit (about 0.23 a day, about 89% for at least one in 9.5 days, worth about +10,000); -6.3% on design hits costs as much as +6.5% on near-misses buys.
- status: computed (CPU, real sieve counts; not run on a GPU)
- uses: fd_nearmiss_design, c_selection
- where: sieve200/cuda/NEARTRUNC.md, near_trunc.py, search_gpu5_neartrunc.patch; uarch branch 560bb78
- matters: shows the lead's objective: design hits first, near-misses as the ladder.

## fd_tail_closed | The survivor-list kernel: a closed item (-2.2 ms a window)
- kind: negative-result
- says: GPU session's bench_rows on a synthetic window at f = 0.985 (2^24 members, 1,248 rows, 251,904 kept): count 1.85 ms, production rows 3.88, rows with 16 loads in flight 3.72, rows in index order 2.96, in index order with 8 loads 2.61 (2.6 ms), finalize 0.90 to 0.01 (FIN2). The kept members were listed in count order, so a warp read about 28 sectors for 32 words (8 in index order). FIN2 plus index order saves 2.2 ms a window, about 0.6% of a batch: under the 1% bar, shelved. Earlier real-data DEEP_REST2 at f = 0.97: rows 6.4 to 7.8 ms, worse. Uarch's tail denominator was wrong (10.6 ms at f = 0.97, 6.9 ms at 0.985).
- status: computed
- uses: fd_sieve_chain
- where: sieve200/cuda/DEEPSIEVE.md (last sections), bench_rows.py; uarch branch a9ad88a, df715e1
- matters: no further sieve-tail gains; the remaining items sit at the noise floor of a batch.

## fd_l4op | The L4 and T4 cards: RTX sieve options, one-pass and the top levels
- kind: engineering
- says: bench_split on gold-l4b (2^25 window): production 1,455 ms; RTX option stack 1,171; with rg 32 / 512 / 512 / rcta 8: 982; one-pass 833 (20 slots), 785 (40 slots, rcta 4), 783 (75 slots, rcta 2). Gate: batch 9.520 to 8.094 s (x0.850), 129 = 129 near-misses member by member, known case 40/40. Lead's item 8: KLO = 3,758,096,384, each vector scanned only on its top 16 levels (about +3%). Measured design hits a second x1.166 and x1.171 on two L4s. T4: 2,553 to 1,739 ms, batch x0.907. KLO widened to 32 levels (24 Nov 20:23Z; about 0.5% fewer hits a member beyond level 16). The L4 f = 0.985 A/B failed (x0.9865).
- status: computed (gates by card)
- uses: fd_onepass, fd_m88f_s32, fd_batch_model
- where: phd/campaign3_gpu/l4op/, l4f/, README (L4 sections); fleet branch (l4op/set_klo32.py); lead and fleet branches
- matters: the L4s and T4 now run the RTX sieve stack and give 10.7% and 1.6% of the fleet's design hits.

## fd_m88f_s32 | m88f covers and the top32 shift for the L4 and T4 vectors
- kind: construction
- says: m88f: covers on the first 88 odd primes (3..461), Q = 170,000, 1,257-1,259 rows against 1,262-1,263 before (families at 1,255-1,258 rows exist): members a second x1.003-1.008, design hits a second x1.058-1.064 (23 Nov 16:50Z). Top32 shift: N0 += k_shift*M with k_shift 5,603,499,370 or 5,603,499,371, so k = 2^32 - 1 is the last member below 10^200; the top 16 levels then hold N from 9.458e199 to 10^200 (unshifted, a vector crosses 10^200 only near k = 9.9e9). Gate on gold-l4c, same 8 covers: design hits a batch x1.0590 (bar 1.03, research predicted 1.056), batch x1.0063. Ledger 26,041-38,040 unshifted, 38,041-50,040 shifted, then 3,476 more (top5s) to 53,516. L4s run 1.19-1.20e-7/s on top4s (x1.045-1.05 over top3).
- status: computed (gates by card)
- uses: fd_l4op, fd_famB
- where: phd/campaign3_gpu/m88f/, s32/ (s32gate_l4.txt, s32_assert.py), s32/top5s/ (fleet branch)
- matters: the small cards were re-aimed at the top levels of 10^200 and at fewer rows.

# E. Colab limits, fleet state, contingency, Lean merge

## fd_colab_limits | Colab: 24-hour runtimes, a G4 limit of 2, an L4 limit of 2, and the replacement rules
- kind: empirical
- says: Colab ends every runtime 24 h after creation; gold-gpu ended 19:13:03Z on 23 Nov and its logs were lost. Round 1 (23 Nov): the RTX cards were replaced 3-8 minutes after their end, the L4s and T4 at about 23 h. Round 2 (24 Nov 19:13-19:59Z): g4d to g4g, g4e to g4h, l4d to l4g resumed from snapshots; gold-g4f's share waits after 40 refused G4 requests (412) over 21 minutes. Lead's test, 21:16Z: with 5 sessions active a G4 was refused 10 times, a T4 granted at once: the limit is on G4s. 22:39-22:42Z: L4s limited to 2. Rule of 22:46Z: no proactive stops; replace after Colab's end; G4 first, T4 last.
- status: computed (README and commit logs; not re-run)
- uses: fd_fleet_state, ext:Colab
- where: phd/campaign3_gpu/README.md (second round, from the fleet branch), bringup/ (handover_end.sh, g4_poll.sh, l4_poll.sh, test_cap.sh), runlogs/2026-11-24/; fleet branch ccr-8ffe9d7a-4ni11u after bab405b (not yet merged into the lead branch)
- matters: the fleet is shrinking for reasons outside the project, which changes every "fleet-days left" figure.

## fd_fleet_state | Fleet composition and what the G4 limit costs
- kind: empirical
- says: At 24 Nov 04:05Z: 7 GPUs (gold-g4d, g4e, g4f; gold-l4d, l4e, l4f; gold-xt4b), 37.12 CU an hour (RTX 10.05, L4 1.94, T4 1.15 each; A100 6.73, CPU 0.26). At the last fleet-branch commit (23:01Z): 2 RTX (g4g, g4h), 2 L4 (l4g, l4i), 1 T4 (xt4c), 25.1 CU an hour; partitions waiting: RTX partition 2 (g4f's snapshot) and l4e's share. From the day-one rates: design hits a day 0.29 at 7 GPUs, about 0.195 at 5 (my arithmetic); P(at least one in the next 6 days) about 69%. Per compute unit the RTX gives 1.6x the L4 and 2.1x the T4 in design hits (3.5e-4, 2.2e-4, 1.7e-4 per CU-hour, my arithmetic). No CU figure after 04:05Z is in the repo.
- status: computed (rates from the cards' logs; the rest is my arithmetic); remaining CU unverified
- uses: fd_day_one, fd_colab_limits, m_portfolio
- where: phd/campaign3_gpu/runlogs/2026-11-24/ (rates_0400.txt, day_one_report.txt, summary.txt); README; lead and fleet branches
- matters: expected design hits for the rest of the budget fall by about a third from the 7-GPU figure, unless Colab grants G4s again.

## fd_contingency | After a design hit: keep the covers, raise the threshold; Q = 180,000 stand-by
- kind: verdict
- says: Lead's rule (23 Nov 21:19Z, written into the README on 24 Nov at 12:30): after a design hit keep the covers and raise the near-miss threshold to the new record; moving Q needs the lead first. Research's stand-by start files at Q = 180,000, covers counted to 180,000: q180000_m89r491.txt (2,770 covers at 1,340-1,344 rows; ./gen_vectors.sh 180000 1344 <count> <name> <seed> m89r491) and q180000_m88f.txt (a9ee33a, 291 covers at 1,350-1,355 rows; GEN_KMAX=top32 ... 1356). Research: for a record of 172,000-178,000 these covers come within 100 of the best known, so only the row lists change, not the family.
- status: conjectural (a plan; not run)
- uses: fd_famB, fd_gen_supply, m_price
- where: phd/campaign3_gpu/README.md ("After a design hit"); lead branch bbbf62f
- matters: the next step if the 170,000 target is hit; the start files were prepared in advance.

## fd_lean_merge | Lean files the lead merged (listed only; a separate ledger covers them)
- kind: engineering
- says: Merges: a14fee8 (23 Nov 15:58, Lean through e1cee31), a2027d5 (16:32, through 778f606), 048b067 (24 Nov 17:22, fleet through bab405b), 43ab0b3 (17:50, Lean through 74b1dde). Under lean/: 155 files, +23,873 / -92 lines. New Lean files: Record200_g160357, Records (edited), RecordGen, RecordGenRun, RecordWalk, RecordInfinite, CoverDepth, CoverDepthGreedy, CoverDepthRun, Cover1471, 4909, 8311, 15907 (renamed from 15787), 16381, 16747, 16981, 32971, 40111, 135511, 614101, Mertens, BitSieve, Needles, NeedlePairs, NeedleClusters, RankData, RankPatterns, RankSieve, RankTable, Cap/Hardness, Cap/ListGain, Cap/Thinning, FunctionField/DesertDegree; ParityDesert and CoverBound edited. Also raw cover_floor_runs (research's partition-function runs) under lean/scripts.
- status: Lean-checked per commit messages (not read, not checked by me)
- uses: fd_rec_cert, fd_dn_table
- where: lean/GoldbachGaps/*.lean, lean/scripts/; lead branch
- matters: tells the Lean ledger where to look; D(0..9) and the certified covers are in these files.

---

## Record chronology

Budget game: largest g known with N below 10^199 or 10^200. Times in UTC. 132,103 is not a record (below 133,981) and is listed because it sits on the frontier.

| date and time | g | N digits | moduli | finder and notes |
|---|---|---|---|---|
| July 2026 (merged by 25 Jul) | 119,419 | 199 | 88 | slop CPU session, round 1; N0 + 145,605,823*M; 857 residual rows |
| 2026-11-22 about 20:31 | 125,269 | 199 | 88 (Q = 122,000; M of 191 digits) | gold-g4 (RTX PRO 6000), search_gpu3.py, skip-frac 0.97; 5.39e9 members, model expected 0.5 |
| 2026-11-22 about 20:38 | 133,981 | 199 | 88 (Q = 122,000, family w) | gold-g4b; 3.90e9 members, model expected 0.4 |
| 2026-11-22 about 20:45 | 132,103 | 199 | 88 | gold-g4b, third hit of that campaign; not a record |
| 2026-11-22 about 23:08 | 146,191 | 200 | 88 (Q = 140,000; Lean's vector r200_q140k_c_v77) | gold-g4b, search_gpu5.py, kernel 28; k = 3,101,585,871 |
| 2026-11-23 about 02:08 | 157,837 | 200 | 88 (Q = 150,000; pt_q150k_t528) | gold-g4c, search_gpu5.py --deep 1 (B = 1e8), 54 min after switching; k = 4,224,399,187 |
| 2026-11-23 12:48:45 | 158,209 | 200 (N = 5.06e199) | 89 (3..463; Q = 170,000) | gold-g4c, vector mode, first near-miss record; k = 10,814,286 |
| 2026-11-24 17:11:16 | 160,357 | 200 (N = 9.53e199) | 89 (3..461 and 491; Q = 170,000, family B) | gold-g4d, vector mode, near-miss; k = 19,221,795; Lean-checked 17:49 |

Before this ladder: 107,719 (21 Jul, 197 digits), 112,249 (23 Jul, 200 digits), 110,917 (199 digits, slop). The dates of 125,269 to 146,191 are "about" times from the record READMEs.

## Changes to existing boxes

- r_158209 | no longer the standing record: g = 160,357 (24 Nov 17:11:16Z) is the largest below 10^200; 158,209 stays on the frontier because its N (5.06e199) is smaller than 160,357's (9.53e199) | records/budget_1e200_200digit_g160357/README.md
- e_fleet200 | the chain gains 160,357 and runs 22-24 Nov (not 22-23); 119,419 was a July CPU record, not a fleet one; 132,103 was a third hit of 22 Nov; "about 10 fleet-days at 02:40Z on 23 Nov" is superseded: 7,967.7 CU at 37.12 an hour on 24 Nov 04:05Z (1,800 CU mark in 6.9 days), and the fleet fell to 2 RTX + 2 L4 + 1 T4 by 24 Nov 22:47Z (Colab G4 and L4 limits); the cover family is now the 491 family B, not only 3..463 | runlogs/2026-11-24/day_one_report.txt; fleet-branch README
- e_records | "GPU fleet raised the budget record to 158,209 by 2026-11-23" is now 160,357 by 24 Nov; the remark that the fleet's hits file showed 157,837 still holds: hits.jsonl was last updated 23 Nov 02:10Z and near-miss records are in records/*/found.jsonl | records/budget_1e200_200digit_g160357/found.jsonl; hits.jsonl
- r_earlier | the ladder gains 132,103 (non-record) and 160,357; "89 moduli (158,209)" now covers two different sets: 3..463 for 158,209, 3..461 plus 491 (M of 193 digits) for 160,357 | record READMEs
- m_portfolio | "from a record of 157,837 with about 10 fleet-days left": record in hand is 160,357; days left shrink or stretch with the fleet size (6.9 days to the 1,800 CU mark at 7 GPUs on 24 Nov 04Z; 5 GPUs since the evening); the 169,000-172,500 forecast was not recomputed on the branches I read (unverified) | fd_day_one, fd_fleet_state
- m_price | the fleet-days column (12.7 at 170,000, 112 at 180,000) assumes 1,262 rows on 88 moduli and an older engine; the fleet's own logs give 0.29 expected design hits a day at 7 GPUs (3.4 fleet-days), 3.7x faster than priced; rows are now 1,248-1,250 (491 set), 1,257-1,259 (m88f) | day_one_report.txt, README
- e_selective | "the fleet's 3% rule" holds only on the L4s and the T4; the RTX cards keep the emptiest 1.5% (f = 0.985, lead 23 Nov 12:06Z: design hits a second x1.10, near-misses x1.08 over f = 0.97); the L4 A/B at 0.985 gave x0.9865; "deeper sieve adds 28%": B = 1e8 confirmed optimal (5e7 x1.010, 1.6e8 x0.996, 2.7e8 x0.951) | README v89 sweep, l4f/ab_l4_f985.txt, HEADROOM.md
- e_gpu | "22.9 million tests per second on an RTX PRO 6000": 24.6M with the 29-bit kernel (+5.7%, 23 Nov 11:40Z) and 23.4M for the best 28-bit step; a window's sieve phase fell from 83.7 to 44.4 ms and an RTX batch from 1.76 s to about 0.73 s; a new IFMA CPU test for 300-400 digits is 8-12x gmpy2 | HEADROOM.md, README, fermatw/README.md
- e_cover_opt | "no proof of a floor; every claim of optimality is empirical" is now partly false: every vector on 3..463 leaves at least 777 of the 15,496 odd primes below 170,000 (j = 10); best known 1,248 on 3..463 and 1,245 on the 491 set | sublinear/cover_ub_results.txt; famB/starts_q170000_m89r491_famB_a9e4a27.txt
- e_c15907 | "where complete covers stop is unknown" now has an upper bound: 15,907 <= D(89) < 35,000 (457M nodes, 3,700 s); exact D(n) known to n = 35 | sublinear/cover_ub_results.txt
- m_rounding | add the certified floor 777 (401 at j = 6, 644 at j = 8) at Q = 170,000; the July estimate of a 0-2.6 nat prize (at Q = 122,000) remains empirical; the theorem alone allows up to about 11 nats at 170,000 | fd_floor170
- m_doors | "Door 1 looks near-exhausted" stays an empirical statement; the only theorem (777 against 1,248) is far from closing it | fd_floor170

## Dependency notes

1. Design target Q = 170,000 -> vectors with about 1,250 rows -> deep sieve to 1e8 and keep fraction 0.985 -> 29-bit Fermat kernel -> near-miss reporting -> 158,209 -> 160,357 -> certify_c3.sh -> Lean kernel (fd_nearmiss_design, fd_rec160357, fd_rec_cert).
2. Family-B criterion (rows above Q) -> swap 463 for 491 -> check 6 and the six-point gate -> the vector of the record -> the record (fd_famB, fd_491, fd_rec160357).
3. Top-of-range windows (+1.5%) -> the record member lies outside the bottom window -> the record exists only under that placement (fd_vtop).
4. Sieve chain (packed bins, flush, unroll 4, LEAN, one-pass) -> batch 0.945 to about 0.732 s -> x1.29 rate -> the 1.60 expected near-misses between the records (fd_sieve_chain, fd_batch_model, fd_nearmiss_design).
5. Lemma "free moduli sit near their fullest class" -> desert_fast5 cuts -> cover_ub bound -> D(29..35), D(89) < 35,000 and the floor 777 -> a theorem-sized bound on Door 1 (fd_fast5, fd_cover_ub, fd_D89, fd_floor170).
6. cover_lns finds the ord[] overflow -> n = 25..27 values rerun -> validation table n = 2..27 (fd_lns, fd_fast5, fd_validation).
7. Colab's G4 and L4 limits -> the 22:46Z rule (no proactive stops) -> five GPUs -> design hits a day 0.29 to about 0.195 -> chance of a design hit before the budget ends falls (fd_colab_limits, fd_fleet_state).
8. Cover supply (cap 1,248 to 1,250, 3.7M covers) -> row guard base -> f stays 0.985 -> design hits per second hold (fd_gen_supply, fd_batch_model).

## Doubts

- RESULTS.md (24 Nov section) says all seven GPUs were replaced at about 23 h. The README says otherwise for round 1: the RTX cards were replaced 3-8 minutes after Colab ended them (g4 ended about 20:11Z, g4d at 20:19Z; g4b 20:27Z, 20:33Z; g4c 20:59Z, 21:02Z), gold-gpu's logs were lost (ended 19:13:03Z, replaced 20:20Z), and only the L4s and the T4 went at about 23 h. Round 2 was at about 23 h.
- The fleet-branch README keeps the sentence "From the next round, runtimes are replaced at ~23 h at a batch boundary" after the new round-2 text; the lead's 22:46Z rule (no proactive stops, replace only after Colab's end) contradicts it. Stale text inside a split bullet.
- cover_ub_results.txt says of D(35) "a surprise outside 3,040..3,190"; 3,079 is inside that window (the commit message says inside). The wording looks inverted.
- Research's README says each two more moduli cost forty times the nodes in the floor. The data say 106,026 (j = 6), 4,468,093 (j = 8: x42), 726,699,931 (j = 10: x163). The floor grows more slowly than the node count (my values 401, 540, then 644 and 777 from the repo: steps +139, +104, then about +66 a modulus), so j = 12 is costly for a small gain.
- The certified floor (777) is 62% of the best cover (1,248) while research's measured floor on the same moduli is 1,247-1,248 (research README, outside my scope). "Certified" must not be read as "close to the optimum"; the new 491 set also has covers at 1,245 rows, below the 1,247-1,248 measured on 3..463.
- fermatw's commit says search_c.py used fm13 (up to 664 bits) at any size. A 200-digit member can have 665 bits (2^664 = 7.6e199; the record's N is 9.53e199). Whether any earlier CPU-share run (campaign3_hi on the G4 hosts, Q = 150,000 vectors, k >= 2^32) tested members above 664 bits with fm13, and so could have missed a hit, is not stated. Hits are re-verified on gmpy2, so false positives are caught, not false negatives. Unverified.
- Rates: the research price list (12.7 fleet-days per design hit at 170,000) and the day-one report (3.4) differ by 3.7x; both are model figures with different engines and cover counts. The report's expected values are the cards' own logged sums, not independent checks.
- The lead's 23 Nov estimate "about 0.23 a day, 89% for at least one in 9.5 days" was made for 7 GPUs and an end near 3 Dec; the day-one report uses an end near 1 Dec (1,800 CU mark). Neither is updated for the 5-GPU fleet in any file I read.
- TALLY.md and hits.jsonl have not been updated since 23 Nov 02:10Z; the totals "expected 9.21, found 9" predate the Q = 170,000 campaign, and the near-miss records are only in records/*/found.jsonl.
- My j = 8 run of the floor (my own program) had not finished; the repo's 644 and 777 are therefore only checked at j <= 7. The 89-moduli proofs have one implementation only.
