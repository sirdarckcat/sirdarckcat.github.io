# r7_r8_supply_pairs: working notes (spy ranks 7 and 8)

Checked 25 Nov 2026 against the branches as fetched (research tip 65819e1, fleet tip c518c38).
Work files (scripts, walks, outputs): `r7r8work/` beside this file.

## Rank 7: "surrogate-guided cover generation to keep supply at the best row count"

Facts in the premise: all three hold.
- "ran out within an hour": fleet README l.800, "The 491 pool at <= 1,248 rows ran out within the hour: each partition's walk found only covers already in its ledger."
- "step to 1-2 more rows": cap 1,248 -> 1,249 (23 Nov 20:25-21:08Z) -> 1,250 (24 Nov 02:43-03:25Z), CAPMAX 1,252 (fleet README l.800-822, runlogs/2026-11-24/day_one_report.txt l.21-26, gold-g4d/e/f summary.txt l.6-7).
- "2.4% a row": p1 = boost/ln N = 11.043/460.5 = 0.02398 (recomputed); cover README l.144. Fleet measured 9.84e-7 -> 9.68e-7 design hits/s (-1.6%) from cap 1,248-1,249 to cap 1,250 (rates_0400.txt, 30-min window).

Hidden premise: a better generator could keep the supply at the best level. False: the level sets are finite, counted, and the walk exhausts them.
- Counts (491 set, family B): 2 covers at 1,245, 93 at 1,246, 1,828 at 1,247 (starts file); ~24,000 at <= 1,248, ~290,000 at <= 1,249, ~3.7M at <= 1,250, ~50M at <= 1,251 (cover README l.334-338, capture-recapture). Fleet actually made 387,175 at cap 1,249 before the walks dried up (day_one_report l.23).
- Bottom of the landscape by a method that needs no search (partition function, sublinear README l.1399-1403): e^4.0 covers at the best row count, x50 at +1, then x22 falling to x11 per row.
- Consumption: 5.48 vectors/s per G4 (rates_0400.txt) = 473k/day/card; 2 G4s now = 0.95M/day; 1,946,360 consumed in c170r by 25 Nov 10:25Z (TALLY.md).
- Generator is already exhaustive and best-first: vecgen491.sh walks at the cap, make_specs.py sorts by residual length (l.111, l.121), ledger per partition; cap steps when a walk yields < 100 new.

My own run (covergen.c from the research branch, 4 cores, family-B starts):
- cap 1,248, two independent 100 s walks: 17,184 and 19,970 new covers, 13,135 in common -> Lincoln-Petersen 26,100 new + 3,924 starts = ~30,000 covers at <= 1,248. At 11-16 vectors/s that is 30-45 minutes of the G4s.
- cap 1,250 walk, 110 s: 102,389 new covers (3,033 / 19,056 / 80,300 at 1,248 / 1,249 / 1,250). Of its 3,033 covers at <= 1,248, 426 (14%) were not in my two cap-1,248 walks, which hold 92% of their own pool: so walking above the cap exposes ~7% more best-level covers (~2,000, three minutes of supply). No hidden reservoir.
- Fleet evidence of the same: after 16 h at cap 1,250 the row guards read last-2,000 = 1,249.994 / 1,249.986 / 1,249.987, i.e. ~1% leftovers.

Other pools at the same level: other 89th primes (557 best 1,246; 479, 503, 523 best 1,247; cover README l.199-203) would add ~0.48M covers at <= 1,250, +13% of that level = half a day of two G4s one row better = 0.2% averaged over the remaining ~5.7 days. Family A and the twelve other frames are worse on the landing measure or 9+ rows worse below Q.

Verdict 7: invalid premise (facts right, lever void). Residual 0 to 0.002 nats.

## Rank 8: "rank spare vectors by the second-order Hardy-Littlewood pair term; spread +/-1-2%"

Already measured and rejected in the brainstorm of 22 Nov:
- Lean branch `goldbach/phd/cap200/brainstorm/pairspread.py`, README l.76-83: pair term -0.032 nats at Q = 213,070 (-0.016 at 140,000); among twelve near-optimal covers from four independent runs it varies by 0.0002 nats; congruent-pair count 0.80 of naive for every cover and for random vectors alike (sd 0.001); doubling it would be worth +0.2 nats and is 36,982 sd away (`pairspread_Q213070.txt`).
- Research verdicts: `verdicts_on_research_ideas.txt` l.81 ("64. REFUTED ... sd 0.0002 over independent covers"), `verdicts_on_lean_ideas.txt` l.40 ("34, 86. NO: vectors with equal rows differ by 0.0002 nats").
- Student branch `goldbach/archipelagos/README.md` l.22-24: P(all rows composite) within ~1% once the sieve passes the threshold; LightGBM with 133 features incl. pairs_same_class and pair_w loses to the plain count.

My recomputation on the fleet's own family (`r7r8work/pairspread2.py`; 6,093 covers: 93 at 1,246 and 1,500 each at 1,247-1,250, from the family-B starts and a cap-1,250 walk):

| rows | pair term, nats (mean, sd, min..max) | alive-row sd per member after sieve to 1e8 (binomial) | selected-hit proxy at f = 0.985, sd / range |
|---|---|---|---|
| 1,247 | -0.02089, 0.00007, -0.02108..-0.02069 | 16.4393 +- 0.0008 (16.687) | 0.00017 / 0.00093 |
| 1,248 | -0.02092, 0.00008 | 16.4457 +- 0.0009 (16.694) | 0.00019 / 0.00110 |
| 1,249 | -0.02096, 0.00008 | 16.4521 +- 0.0010 (16.700) | 0.00019 / 0.00126 |
| 1,250 | -0.02100, 0.00008, -0.02129..-0.02077 | 16.4584 +- 0.0010 (16.707) | 0.00020 / 0.00123 |

So the spread at equal row count is 0.008% (sd) unconditionally and 0.02% through the selection, against the spy's 1-2%: 50 to 250 times too large. The rows are 1.5% less dispersed than binomial (the Lean remark), identically for every cover. Taking the best 5% by this score gains 0.04%; discarding half the supply costs ln 2/ln 12 = 0.28 rows = 0.7%.

Verdict 8: measured and rejected.

## What does vary at equal row count (not the spy's mechanism)

Rows above the design level. Same samples, research's `family_search/weights_8.9days.txt`:
- weighted rows at fixed k: sd 0.52 / 0.66 / 0.72 / 0.77 / 0.83 at k = 1,246..1,250; corr 0.91 with the uncovered primes in 170-180k.
- uncovered primes at k = 1,250 (n = 4,000): 170-180k 96.3 sd 1.40; 170-190k 200.6 sd 2.6; 170k-213,070 426.1 sd 3.0 (413..437).

Current rule: plain rows below Q, family-B starts; cover README l.345-349 says a weighted cap "does not improve the supply within a family" (at 3.6M covers, order-of-magnitude counts).

Equal-supply test here (capture-recapture on two 100 s walks each, `wcompare2.py`):

| weights | weighted cap | pool | mean k | mean weighted rows | plain ordering, same supply | gain |
|---|---|---|---|---|---|---|
| 8.9 days (research file) | 1,311.5 | ~17,400 | 1,249.01 | 1,311.17 | k 1,247.88, 1,312.04 | 0.88 |
| 8.2 days (table interpolated; best cover 1,287.30 vs research 1,287.19) | 1,290.0 | ~4,790 (walk stalled) | 1,248.18 | 1,289.69 | k 1,247.58, 1,290.35 | 0.66 |
| 8.2 days | 1,290.8 | ~35,000 | 1,248.43 | 1,290.43 | ~1,290.84 (extrapolated) | ~0.4 |

The weighted pool trades ~1.1 more rows below Q for ~3.5 fewer uncovered primes in 170-180k. Not checked at the 3.7M level the fleet draws from, and the weights are for record 158,209.
Worth, by research's conversion (10 weighted rows ~ a quarter of the record-deciding rate ~ +1,000 expected record): 0.4-0.9 weighted rows ~ 1-2% ~ +40 to +90 expected record ~ 0.01-0.02 nats.

## Combined residual
0 to 0.02 nats. Zero from either recommendation as written; the upper end is the weighted (landing-aware) ordering of the supply, which neither names.
