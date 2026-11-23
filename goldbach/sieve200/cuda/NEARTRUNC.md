# Near-miss truncation: select by the alive rows BELOW the near-miss threshold (uarch, 23 Nov 2026, 16:30Z; opt-in `--near-truncate 1`; CPU-verified, not run on a GPU)

> **Decision (lead, 23 Nov 16:03Z): not deployed; selection stays on all rows.**  The campaign's objective is the final record when the units end (~3 Dec), which is dominated by whether a DESIGN hit (g >= 170,000) lands (~0.23 a day, ~89% for at least one in 9.5 days, worth ~+10,000 in g); a typical near-miss lands only ~2,000 above G and each one raises G and shrinks
> the gain.  The -6.3% on design hits costs about as much as the +6.5% on near-misses buys, and the CPU path is one more thing to trust.  For the design-hit objective the ranking by all rows IS the right statistic.  The measurements below stand and stay as a note (they are exactly the trade-off table the decision needed); the patch stays opt-in and unused.

## The observation

The campaign's gate metric is the expected number of tested members whose first probable-prime row is at or above the near-miss threshold G (`--near-miss`, 157,837; `--log-near-exp 1`, design hits included).  For a member with c_G alive rows **below G** that probability is
(1 - p)^c_G, p = 0.0713 (a row alive after the sieve to 1e8 is a probable prime with that probability).  The rows at or above G cannot change the event.  But `s200g_count` counts every row, the selection keeps the members with the fewest alive rows over ALL of them, and every kept member carries the
whole row list.  On the production vector 84 of the 1,248 rows (6.7%) lie at or above G: their alive count (mean 28, sd 4.3, independent of the rest) is noise in a ranking whose purpose is to find the members with the fewest alive rows below G.

## Measured (CPU, real sieve, no model of the sieve)

`sieve200`'s C sieve on the production vector's spec (`phd/campaign3_gpu/v89/knowncase_spec.json`, `q170000_m89_t1_v0`, 1,248 rows, G = 157,837 = row 1,164), B = 1e8 (5.76M primes), windows of 2^19 members from the vector's first 200-digit k, blocks of 2^15, f = 0.985 (492 kept a block, the
production rule: `np.argsort(counts, kind="stable")[:nkeep]`), p = 0.0713.  The expected near-misses of the kept set, sum over the kept of (1 - p)^c_G, selecting by c_total (production) against by c_G:

| windows | near-misses >= G | design hits (all rows composite: sum (1 - p)^c_total) |
|---|---|---|
| 13 windows at B = 1e8 | **x1.0626 - x1.0682** (mean 1.0654, sd 0.0015) | **x0.936 - x0.939** (4 windows) |
| 1 window at B = 1e7 / 1e6 | x1.063 / x1.058 | |

The counts are almost pure binomial noise (sd of c_total 16.4 against 16.7 expected from 1,248 rows at 34% alive: the vector's structure adds little), which is why the six percent are there: the kept members are 1.4 rows emptier below G (351.9 against 353.3 alive) when the ranking ignores the rows above G.
Against the threshold (one window, B = 1e7, the same rule):

| G | rows above G | gain in near-misses >= G |
|---|---|---|
| 30,000 | 78.0% | x1.79 |
| 63,097 | 57.0% | x1.64 |
| 100,000 | 36.5% | x1.38 |
| 130,000 | 21.2% | x1.21 |
| 146,191 | 12.3% | x1.12 |
| 150,000 | 9.9% | x1.09 |
| **157,837** | **6.7%** | **x1.063** |
| 165,000 | 2.6% | x1.02 |
| 170,000 (= Q) | 0 | x1.000 |

What this is and is not: it is the effect of the selection rule on the expectation the campaign gates on, computed from the real alive counts of real windows.  The events themselves (~1e-5 a second a card) are far too rare to observe, so "x1.065" is a statement about (1 - p)^c_G, the standard model for a near-miss, and the A/B on `expected near>=G` will show it by construction.

## What it costs: nothing on the GPU, and it makes the sieve smaller

No kernel changes.  Cut the row list at G when the specs are loaded (`near_trunc.truncate_spec`, the whole list kept as `residual_full`): the sieve, count, selection, row lists, Fermat rounds and the CSR then see 1,164 rows, so **the pipeline selects by c_G automatically**, the bit matrix, the visits of both
sieve stages and the count / rows kernels shrink by 6.7% (~-3.5 ms of a 61 ms window alone; a guess of ~-1% of a batch), and the Fermat tests are unchanged (a member is tested until its first probable prime, ~14 tests, far below row 1,164).  Done in the driver by `search_gpu5_neartrunc.patch` (applies to `search_gpu5.py` at origin/ccr-8ffe9d7a-4ni11u @eca6d5a):
`--near-truncate 1` (env `NEAR_TRUNCATE`, needs `--near-miss`), default off.

The one new duty: a member with no probable prime among the rows below G is a "success" of the cut list (the GPU cannot tell a design success from a near-miss).  The CPU settles it (`near_trunc.settle_successes`): `search.verify_success` on the FULL spec (`full_spec`: it must see every row, or it would call a near-miss a design success), and if that fails the first
probable prime among the rows at or above G (`first_prp_row`, gmpy2 BPSW + 25 Miller-Rabin rounds on the rows >= G; the rows below G were found composite by Fermat tests, a certain verdict, and covered offsets are composite by their congruence) is the near-miss's g(N), appended to `s["near"]` for the driver's existing `verify_near_miss`
(every prime below q composite, N - q prime).  These events happen at the rate of the near-misses (~1e-5 a second): the CPU cost is nil.

## The trade-off, which is the lead's decision

* The campaign's yield is near-misses (a near-miss >= G beats the record): **+6.5% with the cut list**.
* A design hit (every row composite, g > Q) is a subset of the near-misses (about 15% of them) and needs the rows above G composite too, which the cut ranking no longer favours: **-6.3%**.
* A selection that weighs the rows above G by some w in (0, 1) would sit between the two (it needs a second count: not built).
* The gate metric the README names (`expected near>=G`, design hits included) improves; if design hits are valued far above near-misses the lead should say so.  Raising G (a new record) shrinks the rows above it, and the gain follows the table.

## CPU checks (`test_near_trunc_cpu.py`, 35 s)

1. `truncate_spec` keeps the whole list, is idempotent; `full_spec` restores it.
2. sieve200's CPU Feeder on the rows below G keeps exactly the members that numpy selects by c_G over the full list (same blocks, same keep rule), with the same alive rows below G (B = 200,003, 8 blocks of 4,096).
3. Verdicts: 3,280 kept members of that window, Fermat base-2 tests of the rows below G = 6,000 (the cut pipeline): 2,354 have a probable prime below G, 926 have none; for all 926 `settle_successes` finds a first probable prime q >= G equal to the full list's first probable-prime row (ground truth from the full alive list), 0 disagreements;
   the design branch with a stub `verify_success` (the full spec goes to it, a verified success is a design record, a failed one with a first PRP row becomes a near-miss).

## To run on a GPU

1. `NEAR_MISS=157837 NEAR_TRUNCATE=1` with the production flags, `--log-near-exp 1`: per batch the log prints `expected near>=157837 ...`: compare with the same batches without `NEAR_TRUNCATE` (x1.06 expected), and the batch time (expected a little under 1% shorter).
2. The known case (`v89/`, vector window, `--skip-frac 0`, `NEAR_MISS=46171`) with `NEAR_TRUNCATE=1`: the 23 (k, q) pairs must be identical to the CPU brute force: with G = 46,171 only 399 of 1,248 rows reach the GPU and every one of the 23 pairs is found through the new CPU path.  This is the end-to-end test of the glue; the slice lines (`alive/k`, `E^`, `hit%`) change by construction.
3. A record near-miss (g >= G) found with truncation on must show `SUCCESS-NEARMISS` in `found.jsonl` exactly as before.
