# Brainstorm of 2026-11-22: measurements behind the verdicts

The research session sent 100 ideas for raising the largest known `g(N)`, `N < 10^200`, from
6.3% of the ceiling (133,981 of 2,130,704) to 10% and beyond, and asked for each to be attacked.
The statements with a proof are in `goldbach/lean/GoldbachGaps/Cap/Brainstorm.lean`. The ones
that need a number are measured here. Target of all runs: `Q = 213,070` (10%), 19,050 rows, the
88 moduli of campaign 3, `p = 0.02390`, so `E = 0.02419 · (rows left)`.

Every script is run as `python3 -I script.py ...`; the header of each file gives the arguments.

## The cover at the 10% target

`tempering.py` (parent directory), 1,500 sweeps: **1,634 rows left, `E` = 39.53**
(`pool_Q213070_m88_seed11.json`, `tempering_Q213070_m88_seed11.json`). Random classes leave
2,288 ± 25. The research session has 1,639 on the first 88 odd primes with its own sampler.

## Idea 2: can the sampler miss a rare ordered minimum?

`exact_small.py 3000 9` enumerates all 1,021,870,080 nonzero class vectors on the moduli
3, …, 29 for the 429 rows below 3,000. Exact minimum: 67 rows, attained by 18 vectors.
`tempering.py` on the same instance (6,000 sweeps) finds 67, and its log-number of vectors
at each of the 46 temperatures agrees with the exact one to 0.08 nats (`compare_small.txt`).
On an instance small enough to enumerate there is no state the sampler does not see.

## Idea 1: mixed crystals

`crystal_mixed.py`: one constant `c` on every modulus above `z`, free classes below
(`crystal_mixed.txt`, `|c| ≤ 150`, coordinate descent from three starts on the free part).

| z | free moduli | best rows left | median over c |
|---|---|---|---|
| 13 | 5 | 2,118 | 2,259 |
| 31 | 10 | 2,021 | 2,193 |
| 61 | 17 | 1,986 | 2,088 |
| 101 | 25 | 1,943 | 2,033 |

Against 1,634 with all classes free. The constant buys nothing; the free classes do the work.

## Ideas 7 and 38: two budgets, and an explicit family below the claimed floor

`oracle_tilt.py`: a cover on the first `m` moduli, and for every other prime `r ≤ z` the
residue of `N` drawn with weight `exp(θ · rows that r kills for that class)`. For this
family the information used (the log of the share of the progression it keeps) and the
exponent `E` are exact sums. It holds a success by the first moment as soon as
`ln M_m + info + E ≤ ln 10^200` (`oracle_tilt_Q213070_z1e6.txt`, `…_z1e7.txt`).

| primes used up to | E of the best family found | cover on | θ | information in the tilt |
|---|---|---|---|---|
| 461 (the cover itself) | 39.53 | 88 moduli | | |
| 547 | 39.08 | 68 | 1.30 | 101 nats |
| 1,229 | 36.99 | 68 | 0.74 | 105 |
| 10,007 | 33.85 | 60 | 0.56 | 155 |
| 213,070 | 31.36 | 52 | 0.46 | 189 |
| 10^6 | 29.93 | 52 | 0.44 | 203 |
| 10^7 | 29.00 | 52 | 0.40 | 198 |

These are upper bounds for the information optimum (the family is a product measure on top
of a cover that was not re-optimised for fewer moduli; the research session's sampler on 200
moduli gives 34.0 where this gives 37.0). So the statement "every modulus set has `E ≥ 33`"
is false, and the optimum keeps falling as primes are added, to 0 at `√N` where the residues
decide everything.

It is not a way to search. A prime that takes part constructively (its classes listed and
combined by the CRT) costs `ln r` of the 460.5 nats whether one class is allowed or many;
under that budget full classes on the smallest primes are the best use, as the campaign does.
The tilted family uses far more primes than fit; its members can only be found by enumerating
the progression and counting rows, which is the sieve with selection, at one nat of work per
nat of information. A 2-list merge on CRT representatives recovers at most the log of the list
size (about 20 nats, three more moduli, 0.5 nats of `E` before the entropy it costs).

## Idea 19: one larger prime for many rows

Over every prime in (683, 10^6) the fullest class of the 1,634 uncovered rows holds 9 rows
(at 743). Not 40.

## Ideas 5 and 64: pair correlations as a design variable

`pairspread.py`: the pair term of the Hardy–Littlewood model is −0.032 nats at this target
(−0.016 at `Q = 140,000`). Among twelve near-optimal covers from four independent runs at
140,000 it varies by 0.0002 nats. The number of pairs of uncovered rows congruent modulo a
non-cover prime below 5,000 is 0.80 of the naive `k²/2s` for every cover and for random class
vectors alike (sd 0.001): twice the expected number is not on offer, and would be worth
+0.2 nats.

## Ideas 26, 27, 53: sharing row values between candidates

`shifts.py`, `neighbours_of_hit.py`, `tempering_shift.py`:

- The optimum for `N` used for `N + 30030`: 2,187 rows (+34%), 608 of them row values of `N`.
  Other shifts in `shifts_single_optimum.txt`: +31% to +63%.
- One class vector optimised for `N` and `N + 30030` together (`tempering_shift.py`, 700
  sweeps): 1,772 and 1,826 rows, `E` = 42.9 and 44.2 against 39.5, 542 shared values.
  Three to five nats lost on each candidate to share a sixth of the tests.
- Given that `N` is a success, the chance that one of the 7,000 shifts `N + 30j` is one too:
  4 · 10^-15 (best shift 2 · 10^-16, 1,497 new rows).

The exact dichotomy is `shared_row_value` in the Lean file: two candidates that share a row
value agree only on moduli whose product is below `g`.

## Idea 9: which design threshold

`portfolio.py`, with the measured `E(Q)`, 3 · 10^6 members a second, overshoot mean
`ln Q / (0.12 p)`, standing record 133,981:

| budget | best design Q | expected record | expected successes there |
|---|---|---|---|
| one week | 151,000 | 159,100 (7.5%) | 4.3 |
| one month | 157,000 | 166,300 (7.8%) | 5.4 |
| one year | 169,000 | 178,400 (8.4%) | 5.6 |
| 100 years | 191,000 | 200,900 (9.4%) | 6.1 |

The optimum is flat downwards (a week: within 500 for `Q` from 144,000 to 152,000) and falls
off quickly upwards (160,000 gives 149,100: half the time there is no success at all).
An expected record of 213,070 needs about 1,000 years of this fleet.
