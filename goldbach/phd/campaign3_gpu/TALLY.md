# campaign3 on the GPUs: expected against found

Updated 2026-11-25 10:25 UTC. Regenerated from the cards' own logs (`gpu3_stats.log`, `search.log`, `found.jsonl` of each
campaign directory):
- the replaced cards: their final snapshots (`runlogs/snap.py`);
- the five running cards: `runlogs/t3.py` on each card;
- the inputs and the script that writes the tables: `runlogs/2026-11-25/tally_1025/`.

Columns:
- **members**: members scanned (sieved).
- **hit mass**: members × hit% summed, i.e. the members' worth of full hit mass that was tested.
- **expected**: the model's expected successes, measured on the members actually tested:
  - *logged*: from `gpu3_stats.log`, Σ (1 − p^)^count over the tested members, p^ the batch's measured PRP rate;
  - *model*: for slices from before that accounting (20:22-20:50 UTC), members × hit% × exp(−1.0275·E^ + 0.33) from each slice's own line. On the slices where both exist, this formula is within ~16% of the logged figure.
- **found**: successes, each re-checked by `search.verify_success`; certified records are in `goldbach/records/`.
- **near-misses** (Q = 170,000): a member whose first probable-prime row lies at or above the record of the time (but
  below Q). Each one is re-checked on the CPU by `verify_near_miss` before it is written. In vector mode the RTX cards
  log the expected number per batch: Σ (1 − p^)^c over the tested members, c = the member's alive rows below the
  threshold.

## Q = 170,000, 1,245-1,263 rows (88/89 moduli, 491 family, family-B covers), N < 10^200, since 23 Nov 03:55Z

Design hits (no probable prime below 170,000). A replaced card's row is from its final snapshot; a share that moved to a
new card carries its campaign directory, so its row covers both cards.

| GPU (cards) | slices | members | hit mass | mean E^ | expected design hits (logged) | found | |
|---|---|---|---|---|---|---|---|
| **c170**: 88-moduli covers, campaign mode, 23 Nov 03:55Z to 10:57Z (RTX) / 16:51Z (L4, T4) | | | | | | | |
| RTX PRO 6000 (gold-g4) | 29,940 | 1004.62e9 | 253.309e9 | 30.21 | 0.0130 | 0 | |
| RTX PRO 6000 (gold-g4b) | 25,998 | 872.35e9 | 219.963e9 | 30.21 | 0.0113 | 0 | |
| RTX PRO 6000 (gold-g4c) | 29,438 | 987.78e9 | 249.064e9 | 30.21 | 0.0128 | 0 | |
| L4 (gold-l4b) | 9,134 | 306.49e9 | 77.279e9 | 30.21 | 0.0040 | 0 | |
| L4 (gold-l4c) | 9,458 | 317.36e9 | 80.022e9 | 30.21 | 0.0041 | 0 | |
| T4 (gold-xt4) | 4,678 | 156.97e9 | 39.580e9 | 30.21 | 0.0020 | 0 | |
| **c170v**: 89-moduli vectors, RTX vector mode, 23 Nov 10:26Z to 20:52Z | | | | | | | |
| RTX PRO 6000 (gold-g4) | 152,400 | 2556.85e9 | 442.861e9 | 30.05 | 0.0268 | 0 | |
| RTX PRO 6000 (gold-g4b) | 162,136 | 2720.19e9 | 477.902e9 | 30.05 | 0.0289 | 0 | |
| RTX PRO 6000 (gold-g4c) | 164,980 | 2767.91e9 | 477.567e9 | 30.04 | 0.0289 | 0 | near-miss 158,209 |
| **c170f**: m88f family-B covers, campaign mode, 23 Nov 16:51Z to 24 Nov 00:44Z | | | | | | | |
| L4 (gold-l4b) | 5,638 | 189.18e9 | 47.660e9 | 30.16 | 0.0026 | 0 | |
| L4 (gold-l4c) | 6,210 | 208.37e9 | 49.093e9 | 30.16 | 0.0027 | 0 | |
| T4 (gold-xt4) | 3,145 | 105.53e9 | 26.588e9 | 30.16 | 0.0014 | 0 | |
| **c170r**: 491-family vectors, RTX vector mode, top windows, since 23 Nov 20:18Z | | | | | | | |
| RTX PRO 6000 (partition 0: gold-g4d → gold-g4g) | 749,356 | 12572.11e9 | 2111.636e9 | 30.01 | 0.1318 | 0 | running; near-miss 160,357 on gold-g4d |
| RTX PRO 6000 (partition 1: gold-g4e → gold-g4h) | 744,212 | 12485.81e9 | 2097.136e9 | 30.01 | 0.1309 | 0 | running |
| RTX PRO 6000 (partition 2: gold-g4f) | 452,792 | 7596.59e9 | 1275.857e9 | 30.01 | 0.0799 | 0 | waits for a G4 since 24 Nov 19:59Z |
| **c170g**: top32-shifted m88f family-B (top3 first on gold-l4d), L4/T4 top levels, since 23 Nov 20:20Z | | | | | | | |
| L4 (gold-l4d → gold-l4g) | 34,028 | 1141.79e9 | 287.706e9 | 30.11 | 0.0163 | 0 | running |
| L4 (gold-l4e) | 20,612 | 691.62e9 | 174.275e9 | 30.11 | 0.0099 | 0 | waits for an L4 since 24 Nov 22:39Z |
| L4 (gold-l4f → gold-l4i) | 30,956 | 1038.71e9 | 261.734e9 | 30.11 | 0.0148 | 0 | running |
| T4 (gold-xt4b → gold-xt4c) | 13,626 | 457.21e9 | 115.208e9 | 30.11 | 0.0065 | 0 | running |
| **all logged** | | 48.18e12 | 8.764e12 | | **0.528** | **0** | |

- gold-gpu (L4) also ran c170 and c170f from 03:55Z until its runtime ended at 19:13Z on 23 Nov, before snapshots existed.
  Its records were lost; at the other L4s' rates it adds ~0.006.
- So expected ~0.53, found 0. P(none) = e^−0.53 = 0.59.

Near-misses, where logged (the RTX cards in vector mode; one card's campaign-mode stretch, 0.005, is in the first line):

| threshold | in force | expected | found |
|---|---|---|---|
| ≥ 157,837 | 23 Nov, from vector mode (10:26Z) to 12:57Z | 0.128 | 1: g = 158,209 (gold-g4c, 12:48Z) |
| ≥ 158,209 | 23 Nov 12:57Z to 24 Nov 17:14-17:20Z | 1.601 | 1: g = 160,357 (gold-g4d, 17:11Z) |
| ≥ 160,357 | since 24 Nov 17:14-17:20Z | 0.476 | 0 |
| **all** | | **2.205** | **2** |

The L4s and the T4 also report the near-misses they find (none so far) but do not log their expectation.

The 140,000 calibration (the lead, 25 Nov 18:52Z), on the two G4s since 19:55Z:
- Each card runs at `--near-miss 140000 --record 160357`. A verified event with g ≤ 160,357 is a sub-record event:
  - it is written to `near_events.jsonl` with `"sub_record": true`, and `found.jsonl` keeps the records and design hits;
  - records (g > 160,357) and their certification path are unchanged.
- The per-hour log is `runlogs/2026-11-25/calib_hourly.jsonl`, made by `runlogs/calib_peek.py` (v2) through
  `runlogs/collect.sh`.
  - It holds one object per card, hour and threshold: the expected events at the threshold, the found events and
    restart gaps.
- First event: g = 159,631 on gold-g4j at 23:07:10Z.
  - Vector `q170000_m89r491_p0c01147_v866@3382593`, k = 6,806,439, row 1,189 of its 1,250 residual rows.
  - N = 3.38·10^199, 200 digits.
  - It was checked on the CPU again from N and g alone (`runlogs/check_event.py`,
    `runlogs/2026-11-25/near_events_gold-g4j*`).
  - It is not a record. Its N is below 158,209's (5.06·10^199) with a larger g, so it is on the (N, g) frontier.
- To 23:10Z, at 140,000: 1.57 expected, 1 found (in the 4 full hours: 1.17 expected, 0 found).

The smaller fleet since 24 Nov 19:59Z, when partition 2 lost its G4 (14.4 h to 10:24Z on 25 Nov):
- 6 cards until gold-l4e's share lost its L4 at 22:39Z, 5 since 22:42Z. The T4 was down 11 min at 21:16Z.
- Expected design hits 0.116 and near-misses ≥ 160,357 0.373; none found. By card:
  - gold-g4g 0.0498 / 0.1865, gold-g4h 0.0497 / 0.1864;
  - gold-l4g 0.0061, gold-l4i (with gold-l4f to 22:42Z) 0.0062, gold-l4e (to 22:39Z) 0.0011;
  - gold-xt4c (with gold-xt4b to 21:16Z) 0.0028.
- That is 0.19 design hits a day, against ~0.29 with seven cards (the 24 Nov day-one report), and 0.62 near-misses a day
  at the 160,357 threshold.
- The running cards' own shares since they took over: gold-g4g 0.0522 / 0.1955, gold-g4h 0.0511 / 0.1916, gold-l4g
  0.0064, gold-l4i 0.0050, gold-xt4c 0.0026.

## Q = 150,000, 1,092-1,097 rows (research covers, minted variants, generator batches; deep sieve B = 10^8 since 01:14-01:26Z on 23 Nov), N < 10^200

Final: the GPUs moved to Q = 170,000 at 03:55-04:04Z on 23 Nov. Rows from the cards' final snapshots, except gold-a100
(stopped at 01:40Z) and gold-gpu. gold-gpu's row is its ~01:55Z figure, since its later records were lost with its
runtime. The CPU shares at k ≥ 2^32 (`search_c.py`) are not in this table.

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| A100 (gold-a100) | 131,072 | 137.44e9 | 22.652e9 | 26.20 | 0.065 (0.065 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4) | 238,424 | 558.68e9 | 111.818e9 | 26.20 | 0.331 (0.331 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4b) | 229,974 | 537.27e9 | 107.460e9 | 26.19 | 0.320 (0.320 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4c) | 390,926 | 720.35e9 | 137.853e9 | 26.16 | 0.419 (0.419 + 0.000) | 1 | 157,837 |
| L4 (gold-gpu), to ~01:55Z | 48,066 | 58.79e9 | 10.235e9 | 26.20 | 0.030 (0.030 + 0.000) | 0 | - |
| L4 (gold-l4b) | 16,580 | 77.85e9 | 16.674e9 | 26.17 | 0.051 (0.051 + 0.000) | 0 | - |
| L4 (gold-l4c) | 14,602 | 73.89e9 | 15.882e9 | 26.15 | 0.049 (0.049 + 0.000) | 0 | - |
| T4 (gold-xt4) | 708 | 23.76e9 | 5.369e9 | 26.12 | 0.017 (0.017 + 0.000) | 0 | - |
| **all** | | 2188.03e9 | 427.943e9 | | **1.282** | **1** | 157,837 |

## Q = 122,000, 867-872 rows (v, w families), N < 10^199

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| RTX PRO 6000 (gold-g4) | 10,720 | 11.07e9 | 1.573e9 | 20.92 | 1.016 (0.000 + 1.016) | 1 | 125,269 |
| RTX PRO 6000 (gold-g4b) | 8,192 | 8.15e9 | 1.158e9 | 20.90 | 0.767 (0.000 + 0.767) | 2 | 133,981, 132,103 |
| L4 (gold-gpu) | 3,136 | 3.21e9 | 0.456e9 | 20.88 | 0.306 (0.000 + 0.306) | 0 | - |
| **all** | | 22.43e9 | 3.187e9 | | **2.089** | **3** | 133,981, 132,103, 125,269 |

## Q = 122,000, 850-862 rows (Lean cover), N < 10^200

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| RTX PRO 6000 (gold-g4) | 12,992 | 13.62e9 | 1.913e9 | 20.41 | 1.998 (1.383 + 0.615) | 1 | 122,827 |
| RTX PRO 6000 (gold-g4b) | 12,672 | 13.29e9 | 1.865e9 | 20.39 | 1.969 (1.362 + 0.607) | 2 | 126,397, 125,221 |
| RTX PRO 6000 (gold-g4c) | 3,744 | 3.93e9 | 0.551e9 | 20.40 | 0.567 (0.567 + 0.000) | 0 | - |
| L4 (gold-gpu) | 3,200 | 3.36e9 | 0.471e9 | 20.40 | 0.495 (0.359 + 0.136) | 1 | 123,259 |
| **all** | | 34.19e9 | 4.800e9 | | **5.028** | **4** | 126,397, 125,221, 123,259, 122,827 |

## Q = 140,000, 1,011 rows (research cover), N < 10^200

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| RTX PRO 6000 (gold-g4) | 156,160 | 163.75e9 | 25.599e9 | 24.15 | 0.589 (0.589 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4b) | 154,944 | 162.47e9 | 25.400e9 | 24.15 | 0.582 (0.582 + 0.000) | 1 | 146,191 |
| L4 (gold-gpu) | 28,960 | 30.37e9 | 4.751e9 | 24.19 | 0.104 (0.104 + 0.000) | 0 | - |
| **all** | | 356.58e9 | 55.750e9 | | **1.274** | **1** | 146,191 |

## Q = 122,000, 867-869 rows, search_gpu2.py at full mass, N < 10^199

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| L4 (gold-gpu) | 180 | 0.19e9 | 0.189e9 | 21.02 | 0.110 (0.000 + 0.110) | 0 | - |
| **all** | | 0.19e9 | 0.189e9 | | **0.110** | **0** | - |

**All covers: design hits expected 10.31, found 9** (Q = 170,000: 0.53 expected, none found yet). **Near-misses at
Q = 170,000, where logged: expected 2.21, found 2** (158,209 and 160,357, both records).

## How far past Q the hits went (`overshoot.py`)

The rows a hit survived beyond its threshold are the primes q in [Q, g) that its cover leaves uncovered. Each such N − q is
a composite the cover did not force. The model makes each prime with probability p = boost / ln N, so the count is geometric
with mean (1 − p)/p ≈ 41 and tail P(≥ u) = (1 − p)^u, and the sum over hits is negative binomial.

| hit | Q | g | rows survived | expected | P(≥ that) |
|---|---|---|---|---|---|
| `r200b_q122k_v367@532676608` | 122,000 | 125,269 | 44 | 40.6 | 0.343 |
| `r200b_q122k_w175@540016640` | 122,000 | 133,981 | 140 | 40.6 | 0.033 |
| `r200b_q122k_v851@537919488` | 122,000 | 132,103 | 116 | 40.6 | 0.060 |
| `r200_q122k_k850_v1760@4292870144` | 122,000 | 126,397 | 57 | 40.8 | 0.252 |
| `r200_q122k_k850_v2028@4291821568` | 122,000 | 123,259 | 16 | 40.8 | 0.679 |
| `r200_q122k_k850_v440@4282384384` | 122,000 | 122,827 | 9 | 40.8 | 0.804 |
| `r200_q122k_k850_v1039@4281335808` | 122,000 | 125,221 | 43 | 40.8 | 0.353 |
| `r200_q140k_c_v77@3100639232` | 140,000 | 146,191 | 63 | 40.8 | 0.217 |
| `pt_q150k_t528@4194304000` | 150,000 | 157,837 | 91 | 40.8 | 0.111 |

- Q = 122,000: 7 hits survived 425 rows against 285.1 expected, P(sum ≥ that) = 0.108.
- Q = 140,000: 1 hits survived 63 rows against 40.8 expected, P(sum ≥ that) = 0.217.
- Q = 150,000: 1 hits survived 91 rows against 40.8 expected, P(sum ≥ that) = 0.111.
