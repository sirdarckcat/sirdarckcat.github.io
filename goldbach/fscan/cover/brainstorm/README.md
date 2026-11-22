# Brainstorm of 22 November 2026: 200 ideas for a large step at 200 digits

The game: an even N below 10^200 with g(N), the least prime p with N − p
prime, as large as possible. The yardstick is 2,130,704, the model's ceiling
at 200 digits; the record that evening went from 133,981 (6.3%) to 146,191
(6.9%). The question put to two sessions was how to reach 10% (213,070) and
then 20% to 50%, with the instruction to look outside the method in use.

Protocol: this session wrote 100 ideas and the Lean session tried to refute
each, by a kernel-checked theorem where the claim was exact and by
measurement otherwise; the Lean session wrote 100 ideas and this session
costed each. Units below: one nat is a factor e in the number of members that
must be tested, 4,500 in g, 0.21 points of closeness.

## Result

**No idea on either list is worth one nat as a change of method.** What is
left is engineering worth 0.6 to 1.3 nats and compute. The reason has a short
form, found from both sides:

- Every prime that helps constructively (its class is chosen and combined by
  the Chinese remainder theorem) costs ln r of the 460.5 nats in 10^200,
  whether one class is allowed or several. Under that budget the cover in use
  is optimal to about 0.2 nats (sampled optimum, and exact agreement on an
  instance small enough to enumerate).
- More information exists: the best residue vector that still has a
  representative below 10^200 leaves E = 38.8 / 37.3 / 35.9 / 34.5 with
  100 / 120 / 150 / 200 moduli against 39.2 for the 88 in use
  (`oracle_213070.txt`, plus 0.5 because a success needs e^E representatives),
  and an explicit family of the Lean session reaches 29.0 with all primes to
  10^7. But beyond the modulus budget the residues of a number are determined
  by the number, so this information can only be collected by enumerating
  members and counting the rows the sieve leaves: one nat of work per nat.
- The one open problem this leaves: find t below K whose count of rows left is
  far below the mean in time sublinear in K. Equivalently, maximum-likelihood
  decoding of a Chinese-remainder code far beyond its list-decoding radius. No
  algorithm is known. It would be worth about 10 nats: 10% in a week of the
  present fleet, and not 20%.

A third way of making N − q composite, besides a small prime by congruence and
luck, was the last idea on the list. The Lean session's theorems bound it: a
certificate is one divisor per row, a divisor of two rows is below Q, and
prescribing coprime divisors above 213,070 for 38 rows leaves at most one N
below 10^200; identities serve at most √Q rows.

## What the search costs (`price_list.py`)

Rows left by the best cover found on the 88 moduli (new runs at 170,000 to
200,000 in `price/`), one RTX PRO 6000 at 4.8 million full-weight members a
second, the fleet at 18.7 million:

| design Q | rows left | E | card-days per expected success | fleet-days |
|---|---|---|---|---|
| 150,000 | 1,093 | 26.1 | 0.8 | 0.2 |
| 160,000 | 1,185 | 28.3 | 7.7 | 2.0 |
| 170,000 | 1,262 | 30.2 | 49 | 13 |
| 180,000 | 1,352 | 32.3 | 436 | 112 |
| 190,000 | 1,437 | 34.3 | 3,400 | 874 |
| 200,000 | 1,522 | 36.4 | 26,600 | 6,800 |
| 213,070 (10%) | 1,634 | 39.1 | 400,000 (1,100 card-years) | 103,000 |

A success at design Q lands about 4,100 higher on average. Every 10,000 in g
costs a factor 8 to 9. By the Lean session's `portfolio.py` (its branch) at
the present rate, the expected record is 167,000 (7.9%) after a week, 174,000
(8.2%) after a month and 186,000 (8.7%) after a year, with the design chosen
for 4 to 6 expected successes. 20% needs E near 80.

The prime-gap record searches use the same scheme (a primorial as cover,
sieve, rank by survivors, test). After more than ten years the best merit
found at any size is 42.5, and 39.6 at 175 digits, which is 9.8% of ln² p.

## Checks of the model made for this exchange

`frailty200.py` runs the 200-digit search at a low threshold, where successes
are frequent, to see whether successes are more frequent or run further than
the model says (four successes at Q = 122,000 had run 2.2 times further than
expected):

| Q | rows | members | found | expected | rows survived beyond Q (model 40.8) |
|---|---|---|---|---|---|
| 40,000 | 180 | 20,000 | 251 | 255.9 | 40.0 |
| 60,000 | 346 | 400,000 | 85 | 91.9 | 39.6 |
| 75,000 | 469 | 1,600,000 | 20 | 18.7 | 56.2 |

Together 356 found against 366.5, and 40.8 rows survived on average. The
chance that the next tested row is a probable prime is 0.0349 whatever the
number of composite rows already seen (4·10^7 tests at 75,000). The fleet's
own tally stood at 8 found against about 8.6 expected. So the early excess was
chance, and there is no slack hidden in the model.

`crystals.py`: covers in which every modulus takes the class α/β for one
rational α/β (the residue vectors of numbers with a short description) leave
2,156 rows at best at Q = 213,070 against 2,283 for random classes and 1,634
to 1,639 for the optimum.

## Engineering still open

`sieve_depth.py` gives what a deeper sieve bound is worth as a function of the
cost of a mark by a prime above the window; the model behind it reproduces the
fleet's measured share of the successes in the emptiest 3% (15.6%).

| cost of a large-prime mark | B = 2^20 | 2^24 | 2^28 | 2^32 | 2^36 |
|---|---|---|---|---|---|
| 0.0033 ns | 5.8 | 8.4 | 11.2 | 14.1 | 16.2 |
| 0.01 ns | 5.8 | 7.5 | 9.2 | 11.0 | 12.3 |
| 0.03 ns | 5.8 | 6.0 | 6.7 | 7.5 | 8.1 |
| 0.1 ns | 5.8 | 4.2 | 4.2 | 4.3 | 4.4 |

(Million full-weight members a second for one card, keep fraction re-optimised;
production is at 4.64 by the same model, with B = 10^6 and 3% kept.)

1. Keep fewer members than 3% at the present bound: the model says 0.6% and
   +23%; the fleet measured +4% at 1% (the mass kept was as predicted, the
   batch was slower than the tests alone would make it). So between +0.04 and
   +0.2.
2. A deeper bound: +0.3 to +0.9 if a large-prime mark costs under 0.03 ns,
   nothing above 0.05 ns. The engine session estimates 0.005 to 0.01 ns on the
   large cards with a bucketed layout (not yet measured); with its costs the
   model gives 7.4 to 8.0 at 2^24, 8.2 to 9.1 at 2^26 and 8.7 to 9.8 at 2^28
   against 4.64 today: 1.6 to 2 times, +0.5 to +0.7 nats, and 2^26 has 93% of
   what 2^28 gives. It needs the pipeline to work per batch of 2^25 members
   instead of per window of 2^19.
3. One or two more moduli (89 or 90), now that vectors are free
   (`../covergen.c`): +0.1 each.

## Files

- `ideas_research.txt`, `verdicts_on_research_ideas.txt`: this session's 100
  ideas as sent, and the Lean session's verdicts as received (its proofs are in
  `goldbach/lean/GoldbachGaps/Cap/Brainstorm.lean`, its measurements in
  `goldbach/phd/cap200/brainstorm/`, branch `ccr-36ca7b46-8twf14`).
- `ideas_lean.txt`, `verdicts_on_lean_ideas.txt`: the Lean session's 100 ideas
  as received, and this session's verdicts as sent.
- `oracle_floor.py`, `oracle_213070.txt`; `crystals.py`, `crystals.txt`;
  `frailty200.py`, `frailty_*.json`, `frailty_*.txt`, `cover*.txt`;
  `sieve_depth.py`, `sieve_depth.txt`; `price_list.py`, `price_list.txt`,
  `price/run_*.txt` (cover runs with `ptcover_fast.c` of the uarch session,
  branch `ccr-b8c25887-i6tn9f`).
