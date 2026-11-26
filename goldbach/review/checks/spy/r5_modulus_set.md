# r5_modulus_set — working notes (reviewer, 25 Nov 2026)

Recommendation: "Optimise the modulus set itself under the 200-digit budget (more swaps of the 463-to-491 kind)";
anneal family B's frame on 5 more sets (461 or 457 swapped for 499, 503 or 509; one two-for-one swap).

## Primary sources read
- research `origin/ccr-d4a17dd0-7uu03r:goldbach/fscan/cover/README.md` (630 lines): l.84-89 (other sets at Q=122,000),
  l.170-199 ("One more modulus"), l.200-213 ("Which 89th prime"), l.215-240 ("The first 88 odd primes", top32),
  l.336-360 (supply, weighted screen to 900, "3.6 weighted rows"), l.374-384 (family_search with 463 replaced by every
  prime up to 590, ~40 runs), l.395-470 (frames; 300,000 sweeps in family B's frame = 1,308.67 / 1,245 in 17 min a core).
- research `goldbach/fscan/cover/family_search/family_eval.py` header: "r <= 590 keeps a vector at least 2^24 members long below 10^200".
- research `goldbach/fscan/cover/brainstorm/README.md` l.141-142 ("One or two more moduli (89 or 90) ... +0.1 each"),
  `ideas_lean.txt` items 44, 45, 46, `verdicts_on_lean_ideas.txt` (22 Nov 23:36Z): "44, 59. UNDER 0.05", "45, 60. YES, +0.1 PER MODULUS
  while the per-vector setup is small", "46. NO", "29, 56 ... with two primes a progression has 21,600 members and the setup costs more than the sieve".
- research `goldbach/sublinear/README.md` l.1311-1356 (floor 1,214; bottom "1,247 or 1,248"; "factor 2.3 at the very most";
  at 213,070: 1,609 best, 1,470 needed for a 1% chance; "Better covers are not a way to 10%").
- fleet `origin/ccr-8ffe9d7a-4ni11u:goldbach/phd/campaign3_gpu/README.md` l.380-405 (vector mode: one 2^24 window a vector),
  l.614-633 (top placement; loader asserts [10^199, 10^200)), l.785-793 (491 gate: x1.061 design hits/s),
  `search_gpu5.py` l.557-580 (VectorSource: a vector whose window does not fit is SKIPPED),
  `runlogs/2026-11-24/day_one_report.txt` (x1.085 at cap 1,248-1,249; x1.051 against gold-g4 alone; x1.067 at cap 1,250),
  `TALLY.md` (c170r 491 family on RTX; c170g m88f on L4/T4).

## log10 sums recomputed
- first 89 odd primes 3..463: 192.3690 (spy 192.369: OK). M = 2*prod: 192.6700 -> 21,378,977 members below 10^200.
- first 88 + 491: 192.3945 (spy 192.394: OK). M: 192.6955 -> 20,159,809 members.
- first 88 (3..461): 189.7034; M 190.0044 -> 9,898,466,666 members.
- first 90 (..467): 195.0383; M 195.3393 -> 45,779 members (a 2^24 window needs 366 vectors).
- Deployed limit: one 2^24 window with every N in [10^199, 10^200) needs >= 2^24/0.9 = 18,641,352 members, i.e. odd-part
  log10 <= 192.4285. Research's looser limit (>= 2^24 members, some N with 199 digits): <= 192.4743.
- The spy's sets (491 set with 461 or 457 swapped out):
  461->499 192.4289 (18,624,593 members), 461->503 192.4324 (18,476,485), 461->509 192.4375 (18,258,688),
  457->499 192.4327 (18,462,992), 457->503 192.4361 (18,316,169), 457->509 192.4413 (18,100,261).
  ALL six are below 18,641,352: the deployed loader would skip every vector (they fit only the looser 2^24 rule).

## Experiment 1 (mine, scratchpad `spycheck/r5/screen2.py`, `screen3.py`): extension screen
Family-B covers of `starts/q170000_m89r491.txt` (best cover recomputed: 1,245 rows, 1,308.67 weighted, as stated).
- Replication of the README's "which 89th prime" (drop 491, add r with its best class, 400 covers):
  491:1245 557:1246 479/503/523/613:1247 463:1248 499:1248 509:1248 — identical to the README.
- Rows struck ONLY by each top modulus in the best cover: 439:9 443:12 449:9 457:10 461:9 491:10. A swap gains only if the
  newcomer's best class on the residual beats 9-10.
- Spy's swaps (491 kept), no re-optimisation: 461->499 1,246; 461->503 1,246; 461->509 1,247; 457->499 1,248; 457->503 1,247;
  457->509 1,248. All worse than 1,245. Weighted: 1,310.3 / 1,309.1 / 1,311.0 / 1,310.7 / 1,310.2 / 1,311.4 against 1,308.67.
- Two slots at once (any two of 449, 457, 461, 491 out; any two primes 449..599 in, exact best pair of classes, 60 covers,
  1,103 sets): nothing below 1,245; the only ties are sets with 557 (too short). Best deployable alternative
  (457, 461, 479, 491) [449->479]: 1,246 / 1,309.66.

## Experiment 2 (mine): capped-walk descent (research's covergen, descend.sh logic) from the extended covers
- control, 491 set started from its 1,246-1,248 covers only: re-finds 1,245 (2 covers).
- 461->499: stays at 1,246. 461->503: stays at 1,246. (stopped there to free the cores for experiment 3)

## Experiment 3 (mine): the spy's own test — 300,000 sweeps of research's ptcover_wfast inside family B's frame
(3:2 5:3 7:5 11:6 13:5 17:4), random classes on the other 83 moduli, weights_8.9days.txt, seed 11; `my_frame.py` =
research's frame_search.py with the three top moduli given explicitly.
Round 1 (ended 13:05Z):
| set (moduli above 449) | swap | weighted rows | rows < 170,000 | expected final record, 8.2 d / 52M / 160,357 | same, 5.5 d / 35M |
|---|---|---|---|---|---|
| 457, 461, 491 (control) | none | 1,308.67 | 1,245 | 176,341 | 172,579 |
| 457, 479, 491 | 461->479 | 1,307.86 | 1,250 | 176,351 | 172,147 |
| 457, 491, 503 | 461->503 (spy) | 1,308.12 | 1,251 | 176,375 | 172,402 |
| 457, 491, 499 | 461->499 (spy) | 1,309.98 | 1,251 | 176,175 | 172,247 |
The control reproduces the README's figures exactly (1,308.67 / 1,245 / 176,341): the setup measures what research measures.
Expected final record by research's own `brainstorm/rank_covers.py` (copied unchanged).
Extension covers (no anneal): 461->479 with its weight-best class: 1,308.14 weighted, 1,246 rows, 176,402 (+61) at 8.2 d / 52M,
172,570 (-9) at 5.5 d / 35M. 449->479: 176,362 (+21). 461->499: 176,200 (-141). 461->503: 176,304 (-37).
Round 2 (the other four spy sets): see the end of this file.

## Reading
- By rows below 170,000 (the design-hit rate) nothing beats the 491 set: every swap is 1 to 6 rows worse.
- By the weighted measure of 24 Nov two swapped sets come out 0.5 to 0.8 weighted rows lower, by taking 5 to 6 more rows
  below 170,000 for fewer above; in expected final record that is +10 to +61 at the horizon of 24 Nov and -9 to -430 at
  today's shorter horizon. The whole neighbourhood is flat to within about 60 in g (0.013 nats at 4,500 in g a nat).
- The gain of the one swap that was made: 3 rows at the best cover (0.073 nats), 2 rows at the supply level, +190 in
  expected final record (176,020 against 175,830, README table l.273-276).
- Needed for 10%: 213,070 - 160,357 = 52,713 in g; E 39.06 against 29.86 (9.2 nats).

## Verdict
partly_done: the one-slot version is done and deployed (491) and exhaustively screened by research (463..700 plain, to
900 weighted, ~40 tempering runs with 463 replaced by every prime to 590). The multi-slot version (461 or 457 out) had
never been tried by the team; this review ran it (screen, capped walk, the spy's own frame anneal) and it is flat.
All six of the spy's sets are also too short for the deployed loader (18.10 to 18.62 million members against the
18,641,352 that a 2^24 window of 200-digit N needs).
Residual gain: 0 to 0.015 nats.

## Round 2 of experiment 3
Started 13:05Z for 461->509, 457->499, 457->503, 457->509 and stopped by me at 13:07Z: the machine is shared with other
reviewers and the runs were getting 40% of a core each (28 minutes to go). These four sets are covered by the extension
screen only (1,247 / 1,248 / 1,247 / 1,248 rows; 1,311.0 / 1,310.7 / 1,310.2 / 1,311.4 weighted), each worse on that screen
than the two sets annealed in round 1 (1,246 / 1,246).

## Not verified
- Why the L4s and the T4 run the first-88 set in campaign mode and not 89-prime vectors: no statement found. TALLY mean
  E^ is 30.11 there against 30.01 on the RTX cards (0.10 nats on about 13% of the fleet's rate).
- "Two-for-one swap": the spy's wording is ambiguous. Two out and one in is an 88-prime set (about 7 rows worse: 1,255
  against 1,248); one out and two in is a 90-prime set (at most 45,779 members a vector).

## Files of this check (scratchpad, nothing in the repository was touched)
spycheck/r5/screen1.py (log10 sums, members), screen2.py (one-slot screen), screen3.py (two-slot screen), wcheck.py,
mkstart.py, mkstart_w.py, descend2.sh, runall.log, my_frame.py, anneal.log, wd_anneal/*.best, rank_covers.py (research's, unchanged).
