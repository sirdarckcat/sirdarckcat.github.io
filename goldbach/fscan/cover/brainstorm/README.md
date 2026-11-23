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

The same question with the fleet's selection rule (`overshoot_selected.py`,
asked again when nine fleet successes had survived 579 rows beyond their
thresholds against 367 expected): `goldbach/search.py` at Q = 60,000 with a
sieve to 10^6 and only the emptiest 3% of the members tested. 60.8 million
members gave 1,188 successes against 1,175.7 expected, and the 1,223 successes
in all survived 41.0 rows beyond Q on average against 40.8 (ratio 1.004 ±
0.029), with the tail as the geometric law says (6.1% survive 120 rows, model
5.5%; 0.74% survive 200, model 0.79%). The count of successes also bounds any
member-to-member variation of p: it could lengthen the overshoot at
Q = 150,000 by 5% at most. The fleet's excess is within chance (z = 1.7).

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
   Outcome: in production since 23 Nov 01:30Z on the three RTX PRO 6000s at
   B = 10^8 (the engine session's bucketed large-prime stage; measured mark
   cost 0.030 ns, 0.10 ns on the L4, which stays at 10^6): 1.38 times the
   expected successes per batch for 1.05 times the time, 1.32 times per
   second, about +28% for the fleet (`phd/campaign3_gpu/README.md` on the
   fleet's branch). The model's row for 0.03 ns a mark says 1.3 at 2^28
   against the re-tuned 2^20.
3. One or two more moduli (89 or 90), now that vectors are free
   (`../covergen.c`): +0.1 each.

## The remaining budget (`portfolio_budget.py`)

State on 23 November 02:40Z: record in hand 157,837 (7.41%), about 10 days
of compute left at 29 million effective full-weight members a second (deep
sieve included), and the fleet's search now reports near-misses: its kernel
stops each tested member at its first probable prime with the rows ascending,
that row is g(N), and it is reported whenever it beats the record in hand
(suggested here, implemented by the fleet the same night). With that, a
member counts whatever the design threshold, and the best cover is the one
with the fewest uncovered rows at the level where the record is expected to
end. Expected final record by design threshold, each with its own best cover:

| design Q | rows below Q | successes only | near-misses counted | chance of no improvement |
|---|---|---|---|---|
| 150,000 | 1,092 | 168,900 | 168,900 (7.93%) | 0.02% |
| 160,000 | 1,181 | 171,200 | 171,200 (8.04%) | 0.00% |
| 165,000 | 1,221 | 171,500 | 171,700 (8.06%) | 0.09% |
| 167,500 | 1,243 | 171,100 | 172,300 (8.08%) | 0.01% |
| 170,000 | 1,262 | 169,700 | 172,300 (8.09%) | 0.03% |
| 172,500 | 1,284 | 167,800 | 172,500 (8.10%) | 0.4% |
| 175,000 | 1,302 | 165,500 | 172,300 (8.09%) | 0.2% |
| 180,000 | 1,352 | 161,300 | 170,000 (7.98%) | 2.9% |

The optimum is flat from 167,500 to 175,000 (differences there are within the
scatter between individual covers) and about 1,000 above a design at 160,000.
Staying another 20 hours at 150,000 first costs about 200. With 8 days
instead of 10 the best design is 167,500 to 172,500 at 171,200 to 171,300;
at 40 million members a second it is 172,500 at 174,200. Supply at 170,000:
about 1,400 covers with at most 1,263 rows and more than 50,000 at 1,264.

### What 10% takes (`reach_target.py`)

The user's standing goal since 23 November is g ≥ 213,070, 10% of the
ceiling. For that event only the number of uncovered rows below 213,070
matters, so the cover should be designed for exactly that threshold. Four
runs of 150,000 sweeps all ended at 1,623 rows (the previous best, from the
other sampler, was 1,634; my first run had 1,639), and the capped walk finds
nothing lower; `starts/q213070.txt` holds 106 covers at 1,623 and 900 at
1,624. With 9 days of the fleet at 29 million effective members a second:

| cover designed for | uncovered rows below 213,070 | chance of g ≥ 213,070 | fleet-days for one expected | expected final record |
|---|---|---|---|---|
| 170,000 | 1,718 | 0.0018% | 505,000 | 171,800 |
| 200,000 | 1,657 | 0.0078% | 116,000 | 166,200 |
| 213,070 | 1,623 | 0.0177% | 50,700 | 164,500 |

On the first 89 odd primes the cover for 213,070 has 1,609 rows
(`starts/q213070_m89.txt`), another factor 1.23 if the engine takes vectors
of 2·10^7 members: 41,000 fleet-days for one expected crossing.

So the best design is ten times better for the 10% event than the design
that maximises the expected record, and it still needs about 5,600 times
the remaining budget (140 years of the present fleet, about 600 card-years)
for one expected crossing. Nothing on the method side that survived the
brainstorm changes that by more than a factor 2; the rest is compute or a
new method (`../../../sublinear/`).

A soft threshold was tried as well (`ptcover_w.c`, `soft_weights.py`,
`eval_cover.py`): with near-misses a row at q matters in proportion to the
chance that the final record ends above q, so the optimiser was given those
weights instead of a sharp Q. A run of 60,000 sweeps gave a cover worth
172,500, the same as the best sharp design (172,500 at Q = 172,500; 172,300 at
170,000; `eval_cover.txt`). The sharp designs near the expected record are
already within 100 to 200 of what the weighted objective can give, so the
vectors stay as they are.

## Files

- `ideas_research.txt`, `verdicts_on_research_ideas.txt`: this session's 100
  ideas as sent, and the Lean session's verdicts as received (its proofs are in
  `goldbach/lean/GoldbachGaps/Cap/Brainstorm.lean`, its measurements in
  `goldbach/phd/cap200/brainstorm/`, branch `ccr-36ca7b46-8twf14`).
- `ideas_lean.txt`, `verdicts_on_lean_ideas.txt`: the Lean session's 100 ideas
  as received, and this session's verdicts as sent.
- `oracle_floor.py`, `oracle_213070.txt`; `crystals.py`, `crystals.txt`;
  `frailty200.py`, `frailty_*.json`, `frailty_*.txt`, `cover*.txt`;
  `overshoot_selected.py`, `overshoot_selected.txt`,
  `overshoot_selected_found.jsonl.gz` (the successes of the selected run);
  `portfolio_budget.py`, `portfolio_budget.txt`; `soft_weights.py`,
  `eval_cover.py`, `eval_cover.txt`, `soft_run_w170.txt` (with
  `../ptcover_w.c`);
  `sieve_depth.py`, `sieve_depth.txt`; `price_list.py`, `price_list.txt`,
  `price/run_*.txt` (cover runs with `ptcover_fast.c` of the uarch session,
  branch `ccr-b8c25887-i6tn9f`).
