# r9_small_size_calibration: working notes (25 Nov 2026)

Recommendation checked: RANK 9 "Calibrate the ceiling and the cover-plus-luck model on exhaustive small-size
data (to 4e18 and 21 digits)", incl. "run the constructive pipeline at ~19 digits and compare its best g with
the exhaustive maximum (9,781 below 4e18, as recalled)".

Verdict: ALREADY DONE, several times over and by independent routes. Residual gain for the 200-digit search: 0 nats.

Sources (read-only, `git show origin/<branch>:<path>`):
- lead `ccr-2ce9e63a-hn0fuw` @ cd82336: goldbach/RESULTS.md, closeness.py, ceiling_model.py, ceiling_table.json,
  record_holders.txt, samples/random_1e13.txt, samples/random_1e18.txt, FRONTIER.md, SOK_GOLDBACH_GAPS.md
- fleet `ccr-8ffe9d7a-4ni11u` @ c518c38: goldbach/closeness.py (identical), records/, phd/campaign3_gpu/TALLY.md
- research `ccr-d4a17dd0-7uu03r` @ 65819e1: goldbach/sublinear/README.md, toy_exact_1e9_1000.txt,
  toy_compare_1e9_1000.txt, goldbach/fscan/README.md, fscan/runs/calib/Q7001_R137_s0.log, fscan/cover/README.md
- Lean `ccr-36ca7b46-8twf14`: goldbach/lean/scripts/{lgs_heuristic,rank_records,rank_sieve,mini_check}/
- student `ccr-c6e00296-3g7fp9`: goldbach/archipelagos/README.md, theory_e18.txt, tail_e18.json

## Premises
- "9,781 below 4e18": TRUE. record_holders.txt last line `3325581707333960528 9781` (69 holders, OEIS A025018/9,
  every g recomputed with gmpy2); closeness.py l.59 REFERENCE.
- "exhaustive data to 21 digits": FALSE. Exhaustive truth ends at 4e18 (19 digits). "21 digits" is the user's
  permission for CPU experiments ("CPUs can go to 21 digits if necessary to obtain empirical data"), not a data set.
  Above 4e18 there are only windows/samples and constructive finds.
- "the ceiling is uncalibrated / fitted": FALSE since 22 Nov. ceiling_model.py has no fitted constant.

## What calibration exists
A. Ceiling (largest g expected below N)
 1. ceiling_model.py (HL tuple heuristic, sequential importance sampling over residues, no fitted constant).
    RESULTS.md l.285-340:
    - 600M random even N in [1e18, 1.1e18): P(g >= y) within 0.5% from y = 11 to y = 1,801 (1 in 43,000), within 2%
      to 2,203, 75 vs 69 expected at g >= 3,001. 300M random 14-digit N: within 1.3% down to 1 in 43,000.
    - far tail: one 25-digit progression, P(g > 10,000) = e^-25.40 by sieve statistics over 16.7M members and by
      the model, within the 0.6% counting error.
    - 69 record holders: last one 9,781 at 3.3e18, model median 9,570 (5%..95%: 9,190..10,240). Expected count of
      earlier N with g at least as large: median 0.29 over the 35 holders above 1e9 (Exp(1): 0.69), "about two
      standard errors"; "If that is a real effect the line is about 1.5% too low. No correction is applied."
    - sampler vs full enumeration on small cases: four digits.
 2. Lean session, independent closed formula (lgs_heuristic/README.md): u(N,m) = (1-h)^m exp(-c A_m m h^2), one
    constant c = 0.92 fitted on the exact scan of all 5e11 even N <= 1e12; out-of-sample at 1e11 within 5%;
    record value at 1e8 / 1e12 / 1e18: model 1097 / 3229 / 8861, actual 1093 / 3457 / 9341; 57 jumps between
    record holders to 1e18: mean 1.00 +- 0.13; forecast band for the next holder: 53 of 59 inside 5-95% (53.1 exp.).
    At 1e200: ln #{N: g >= Q} = 403.2 / 395.7 / 383.0 / 371.5 / 337.9 vs research sampler 403.3 / 395.7 / 383.1 /
    371.5 / 338.0; one expected N at 2,133,689 vs campaign ceiling 2,130,704 (0.14%); moves 0.4% for c in 0.5..1.3.
    Rule-B generator started at 98: 9,533 at 4e18 (real 9,781), 68 terms (real 69).
 3. Lean: all even N < 2^25 as kernel-checked theorems (rank_sieve), all even N <= 1e12 by scan (rank_records).
B. Cover-plus-luck model (H1: a row with no factor <= z is prime with probability c_z, independently)
 1. Archipelagos (student): exact g for 2e7 consecutive even N near 1e12, 1e15, 1e18. P(every row composite)
    totals 0.993..1.005 of the prediction for z >= 997 (theory_e18.txt: 0.993, 0.995, 0.994 at z = 997, 9973,
    65521; shallow z = 13, 97: 0.927, 0.978). Tail: g >= 3,137 expected 1.21, seen 1 (tail_e18.json). 366 lags
    within ~1%. LightGBM with 133 residue features loses to (1-c)^rows.
 2. Miniature (research README l.536-581; toy_compare_1e9_1000.txt), X = 1e9, Q = 1,000 (167 rows; 55% of the
    true maximum 1,789 below 1e9): all 157,947,020 even N with no prime factor 3..29; exactly 256 with g >= 1,000.
    N examined for 1 / 3 / 10 / 30 / 100 / 256 successes: cover first (depth 23 = CRT line) 2,982 / 63,350 /
    253,380 / 1,205,425 / 12,004,497 / 151M; ideal to depth 200: 13 / 401 / 10,811 / 73,849 / 1,720,522 / 154M;
    ratio 229 (5.44 nats) / 158 / 23.4 / 16.3 / 7.0 / 1.0. Successes have 25..41 rows at depth 23, best covers 22,
    average N 36.8; 1 of the 62 best lies in the 888 members of the best covers. Prediction of counts by rows
    left at depth 200 from residue vectors alone: within 3% (1 / 12 / 49 / 339 / 1,564 exact vs 0.9 / 7.9 / 53.8 /
    311 / 1,541). Success law p = 0.485 vs prime density of 200-rough numbers 0.489. Re-enumerated by the Lean
    session with a different program: joint histogram byte-identical (mini_check.txt, sha256 5775e6ee...).
 3. Lean cover_rank (lgs_heuristic README section 3): on the exact record sequence, 17 terms 54,244..113,632,822,
    ordering by rows left at depth z reaches the next record after 1 candidate in 4 / 10 / 16 / 48 / 408 / 36,880
    for z = 3 / 7 / 13 / 31 / 101 / 1009. "a term is a good cover and lucky on what the cover leaves".
 4. Constructive pipeline just above the exhaustive range:
    - fscan calibration (runs/calib/Q7001_R137_s0.log STATS line): Q = 7,001, Xmin = 4e18, Xmax = 3e21, class 137,
      5,143,522 vectors, 1.18e12 members, found = 50, expected = 48.7362 (raw 51.47), 2,081 s on 4 threads.
      Smallest success 1.62e20 (21 digits). Mean overshoot g - Q 316 vs 307 predicted (README l.116-119).
    - tscan over test instances and four record searches: 138 predicted, 145 found (RESULTS.md l.310).
    - fscan class 197 below 1e23, Q = 10,007: 5 found vs 0.78 expected for the class, 5 vs 1.6 for all classes
      run ("about 2%"), README l.114. Unexplained, same direction as the early record holders.
    - cost of one expected g > 10,000: ~30 core-hours below 1e23, 220 below 1e22, 2,700 below 1e21, 18,000 below
      3e20 (fscan README l.238-243): factor 5-7 for the first digit, 12 for the next.
 5. At 200 digits directly (fleet TALLY.md l.133-134): "All covers: design hits expected 10.31, found 9";
    near-misses at Q = 170,000: expected 2.21, found 2.

## Closeness achieved by size (closeness.py run on the fleet tree, model line)
| digits | g | ceiling | closeness | how |
| 19 | 9,781 | 9,567 | 102% | exhaustive search, not ours |
| 20 | 5,407 | 11,341 | 47.7% | one cover, whole progression (4.8e8 members), CPU minutes |
| 21-22 | >= 7,001 (50 numbers) | 12,000-14,400 | ~50-60% | fscan calibration, 35 min x 4 cores |
| 22 | 6,073 | 14,436 | 42.1% | one cover, 2.9e7 members |
| 23 | 11,701 | 15,747 | 74.3% | fscan, 6 Colab CPU machines (others 63.3-69.9%) |
| 25 | 10,357 | 19,248 | 53.8% | tscan |
| 27 | 10,111 | 22,595 | 44.7% | |
| 30 | 10,459 | 28,637 | 36.5% | 53 min on 4 cores |
| 40 | 11,173 | 58,755 | 19.0% | |
| 46 | 20,551 | 80,741 | 25.5% | tscan |
| 63 | 30,139 | 164,441 | 18.3% | tscan, 19 min on 4 cores |
| 150 | 104,527 | 1,135,248 | 9.2% | GPU |
| 186 | 109,357 | 1,799,400 | 6.1% | |
| 200 | 160,357 | 2,130,223 | 7.53% | GPU fleet (record) |
| 347 | 216,289 | ~7.03M | 3.1% | "other direction" |
| 2,196 | 1,001,491 | ~3.6e8 | 0.28% | |
Predicted for a fixed budget (fscan/cover/README.md l.545-575, closeness_cost.txt): 50% costs ~0.4 ln N nats
(e^19.7 at 23 digits, e^26.2 at 30, e^36.5 at 40, e^46.4 at 50, e^99.8 at 100, e^209.2 at 200); a fleet that
affords ~28 nats reaches ~85% at 21-23 digits, ~45% at 40, 7-7.5% at 200: "the share is set by the size of N,
not by the method".

## Ceiling function (closeness.py l.74-103, ceiling_table.json)
median of the largest g below N; table 18.5..200 digits, log-log interpolation; beyond: the prime with index
(L / 1.3203) (L - ln 2 - A ln L - B), A = 0.7128, B = 2.736 (fit to the table, within 1.5%, 0.3% from 50 digits);
below 3.3e18: first point scaled by L^2 ln L.
| digits | median | 5%..95% | / (ln^2 N lnln N) |
| 18.52 (3.3e18) | 9,567 | 9,189..10,237 | 1.40 |
| 20 | 11,560 | 11,117..12,348 | 1.42 |
| 22 | 14,564 | 14,067..15,449 | 1.45 |
| 25 | 19,736 | 19,123..20,826 | 1.47 |
| 28 | 25,771 | | 1.49 |
| 32 | 35,241 | | 1.51 |
| 40 | 58,996 | 57,934..60,881 | 1.54 |
| 50 | 98,250 | | 1.56 |
| 63 | 165,924 | | 1.58 |
| 80 | 283,408 | | 1.60 |
| 100 | 465,348 | | 1.61 |
| 150 | 1,136,627 | | 1.63 |
| 200 | 2,130,704 | 2,123,360..2,143,754 | 1.64 |
Extrapolated below the table vs truth: 1e9: 1,824 (true max 1,789); 1e12: 3,551 (3,457); 1e15: 5,922 (5,569);
1e18: 8,966 (9,341). ideal_digits(213,070) = 70.4; ideal_digits(160,357) = 62.1.

## Is anything not done?
1. A literal run aimed at N <= 4e18. Not done, and it cannot beat 9,781 there by definition. What it would show
   is already shown at 1e9 (miniature) and at <= 1.1e8 (cover_rank). My own 5-second extension to the real
   holders (r9work/mine/holder_split.py, not a team file):
   N = 3325581707333960528 (g = 9,781; 1,204 rows; CRT line 47, primorial 6.1e17, so 6.5 members per full cover):
   rows left at depth 47: 210. Best cover found by coordinate descent: 179. Random even N: median 272,
   1% point 211, 0.1% point 206. So the true 19-digit champion is a top-1% cover, 31 rows short of the best one,
   and lucky after that (rows left at depth 101 / 1009 / 1e4 / 1e5 / 1e6: 173 / 102 / 74 / 51 / 37).
   Same picture for 2.8e18 (213 vs 173, top 6%), 9.1e17 (204 vs 168, top 2%), 1.2e17 (184 vs 155, top 0.4%),
   1.0e15 (153 vs 126, top 2%). With p = 0.169 per row at depth 47 (0.185 nats per row) the best cover costs
   e^33.1 per member and has 6.5 members; the holder's own cover costs e^38.9; all even N below 4e18: e^42.1.
   At 19 digits the method has no room left to be a method: it is the exhaustive scan in a different order.
2. The two ~2 sigma excesses in the same direction (holders early: 0.29 vs 0.69; class 197: 5 vs 1.6) were noted
   and left. If real: ceiling ~1.5% higher, 7.53% -> 7.42%, target 213,070 -> ~216,300 (+0.5 nat). At 200 digits
   the tally (9 vs 10.31) excludes any factor-3 excess of hits.
3. Not a gap but a reading the spy missed: this calibration is the origin of the team's verdict, not an exit
   from it. It shows the model is right to ~1%, so the e^8.5 shortfall for 10% is real, and it shows where the
   nats are: the miniature's factor 229 (5.4 nats) between cover-first and ideal-to-depth-200 is the small-size
   image of the 39.3 -> 30.5 nats (8.8 nats) of "ideal to 5,000" at 200 digits (research README l.505-513),
   which would reach 10%. Nobody can collect it (research README "Why nothing known collects the prize").

## Residual gain
0 nats for the search (diagnostic only; all of it done). Cheapest decisive test: read the STATS line of
goldbach/fscan/runs/calib/Q7001_R137_s0.log (found=50 expected=48.7362, Xmin=4e18 Xmax=3e21) and the last line of
toy_compare_1e9_1000.txt; or run r9work/mine/holder_split.py (5 s).
