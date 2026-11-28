# Skeptic's check of the "algorithmic" audit

Verdict: the conclusion (no algorithmic loophole; barrier holds) is warranted, and is firmer than the auditor states.
Every table sampled reproduces. Three supporting statements are wrong or unsupported, none changes the verdict.
Scripts and raw output: `audit/run/algorithmic_skeptic/` (a_verify.py, b_tree.py + b_tree.txt, c_checks.py + c_checks.txt, d_recheck.py + d_recheck.txt).
Cover used: first line of `goldbach/fscan/cover/starts/q213070_m89.txt` on origin/ccr-d4a17dd0-7uu03r (byte-identical to the auditor's copy; the file holds 10 covers at 1,609 rows and 1,259 at 1,610).

## Numbers recomputed (independent code)
- 19,050 odd primes < 213,070; 1,609 rows; theta(89 cover primes) = 442.946; 16.88 nats free = 2.14e7 members per cover. Match.
- p_z = 0.0240, 0.0268, 0.0295, 0.0330, 0.0383 at 463, 1,000, 2,000, 5,000, 20,000. Match. (1-p_463)^-1609 = e^39.06.
- Members: 1,438.6 +- 11.3 (depth 1,000, n=4,000), 1,169.4 +- 16.8 (5,000), 1,007.8 +- 17.5 (20,000). Match.
- Per-prime table (467, 509, 997, 2003, 4999): mu, W, variance, pin rate, list_gain bound, tilt rates all match to the digit (467: 3.45, 9, 2.77, 0.90, 5.78, 7.65/2.51/1.43).
- Cover-side exchange: unpin 28 primes >= 300 (166.6 nats) loses 224 rows (1.34/nat); top-2/3/5 lists 1.62/1.54/1.46 rows per nat. Match exactly.
- Pins beyond the line: 21.8, 40.6, 63.2, 92.2 rows for 20, 40, 64, 100 nats; list_gain bound 116, 228, 351, 533. Match.
- Soft selection (own heat-bath, other seed, random sweep order): rows gained at C = 20/40/64/100: 73/106/136/171 at depth 1,000, 108/153/195/245 at 5,000. Match.
- Block-diagonal: 1,608.2 vs 1,602.2 at KL 30 (break-even 36); 1,602.2 vs 1,580.1 at KL 25 (break-even 45); 1,625.3 vs 1,550.0 at KL 14 (break-even 68). Match.
- Koetter-Vardy rough number: sqrt(460.5 * sum_{463<s<=5000} s ln s / 3) = 43,368 (auditor: 44,000); theta(463,5000] = 4,468, theta(<=5000) = 4,912.
- Join exponent: the auditor's 0.82 / 0.82 / 0.82 / 0.87 are exactly ln s/(ln s + ln(1/density)), i.e. the trivial rectangle |A| = 1 (pin u mod s, v in L - u). No rectangle beats the trivial one.
- Requirement table: 283 rows -> 265 nats (1,000), 229 -> 89 (5,000), 197 -> 55 (20,000) by interpolation in the auditor's tilt files; 10^8: binomial KL gives 17 nats, about 20 with the 0.83 variance factor.
- list_gain_le (origin/ccr-36ca7b46-8twf14:goldbach/lean/GoldbachGaps/Cap/ListGain.lean line 64) is stated for a Finset L, as the auditor says.

## Where the auditor is off
1. Tilt versus real top-fraction selection. Direct sample of 120,000 members at depth 1,000: the best e^-1, e^-3, e^-6 fractions gain 11.5, 23.4, 35.3 rows; the tilt at the same cost gives about 15.6, 27.5, 39.8. The "soft selection" columns are upper bounds, 10 to 25% high below 6 nats (a few % at 20+). Direction: barrier firmer.
2. "Exchange is negative on the real cover" (about -1 row per nat). That price (1.5 rows per nat of list entropy) is for per-prime top-k product lists. Entropy taken jointly is 3 to 5 times cheaper (the e^22 covers within 1,609 to 1,620 rows: about 0.5 rows per nat), and block lists with soft selection are cheaper still. Priced with a joint tilt on blocks straddling the line (b_tree.txt, upper bounds, rows versus today's best cover at the same depth):
   - two lists of e^21, join of 21 nats (primes to 487, K kept): -1 row, +0.03 nats.
   - two lists of e^21, isolated outputs (join 39 nats, primes to 503): -20 rows, +0.48 nats.
   - 4-tree with lists of e^21, isolated outputs (join 56 to 60 nats, primes to 523): -13 rows, +0.32 nats.
   - hypothetical lossless join of 60 / 120 nats: -28 / -50 rows, +0.68 / +1.22 nats.
   So in rows the exchange is zero to slightly positive, not negative. The team's "about 0.2 nats per extra prime" is high (0.03 to 0.1 here).
3. What actually kills every one of these: a join constraint beyond the line makes prod(coordinates) > X/K, so outputs are isolated N, not progressions. The fleet's 11 ns sieve exists only on progressions of about 2e7 members (fscan README line 246: setup per vector 60,000 cycles against 4.6 to 6.7 cycles per member). An isolated N costs 26 to 30 Fermat tests (1/p_z) against about half a test for an amortised member, and has no deep-sieve selection behind it: 4 to 7 nats per candidate (estimate from the task's cost figures and README line 734, "20,000 operations per member"; not measured). The auditor flagged this in one clause ("expect loses amortisation, not measured") and priced nothing with it.
4. Same hidden cost in the auditor's requirement table and in (P'). "At constant cost per candidate" assumes a candidate costs what a member costs. Candidates selected beyond the line are isolated, so the luck needed is 7.7 + (4 to 7), not 7.7: at depth 5,000 about 230 nats of selection, not 89; at 20,000 about 160, not 55. For the team's prize table: 3.5 nats at depth 1,000 is negative net of this cost, 8.8 at 5,000 becomes 2 to 5, 12.6 at 20,000 becomes 6 to 9. README caveat (ii) states the assumption (deep sieve and 3% rule behind every tested N) but does not price its failure for isolated N.
5. "Weights are Fourier-flat" (asserted, not run). False above a few thousand. max |w^(h)|^2 / R: 5.9 (s=467), 5.9 (997), 12.4 (2,003), 43.7 (4,999), 64.4 (10,007), 182 (30,011), 1,500 (250,007), against about ln s for a flat set. Peaks sit at h/s within 1/Q of c/d with d = 6, 15, 30, 42, 66, 210, 390; they carry 1.9%, 3.1%, 5.2%, 8.9% of the energy at s = 4,999, 10,007, 30,011, 250,007. Cause: 1,608 of the 1,609 rows are 1 mod 6, they use 4 classes mod 30 and 16 mod 210. Not a loophole: the tilt tables are computed from the exact weights, list_gain bounds any list shape, and the refined interval condition (N mod s below Q and in an allowed class mod 210) costs ln(s/Q) + 2.6 nats for 0.10 rows, 0.04 rows per nat, 30 times worse than a cover prime. It does correct the README's "R fills under 1% of the interval": within allowed classes mod 210 it fills 9.9%.
6. "Best pairs" cap of 3 to 3.5 nats is not a cap. It fixes depth 5,000 and C = 30. The auditor's own table gives 5.7 nats for 30 nats at depth 20,000 and says 18 nats suffice at 10^8. And the outputs of a best-pairs algorithm are isolated N (item 3). As a loophole it is worth zero: no algorithm is offered.
7. Block-diagonal design 1 (A <= 421 plus 10 primes to 479) is a 91-prime cover with 100 members per progression; with the fleet's setup figure that is several nats worse, not 0.15.

## Not examined by the auditor (within the lens)
- The cost of an isolated candidate, and the shortest progression the GPU sieve can amortise (needs the fleet's setup cost per cover; decides the true position of the line: 460.5 - ln K_min).
- README point 5 (the sieve cannot skip members; kept fraction fixed): staged sieving, sub-progressions on one or two beyond-line primes, incremental setup between neighbouring covers.
- The reachable population: selection among members of near-best covers is capped at 39 - 30.75 = 8 nats in all; the requirement table (263/89/55/18 nats "among members of the best cover") describes a population that does not exist.
- Whether the 7.7-nat shortfall is net of the 1.5% rule (if it is, the 10^8 line is about 25 nats, not 18).
- Fourier/spectrum check (done here, item 5).
