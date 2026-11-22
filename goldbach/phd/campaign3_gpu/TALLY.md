# campaign3 on the GPUs: expected against found

Updated 2026-11-22 23:56 UTC. Regenerated from the runtimes' own logs:
- `tally_rt.py` runs on each runtime and reads its search.log, gpu3_stats.log and found.jsonl;
- this page is written from those results.

Columns:
- **members**: members scanned (sieved).
- **hit mass**: members × hit% summed, i.e. the members' worth of full hit mass that was tested.
- **expected**: the model's expected successes, measured on the members actually tested:
  - *logged*: from `gpu3_stats.log`, Σ (1 − p^)^count over the tested members, p^ the batch's measured PRP rate;
  - *model*: for slices from before that accounting (20:22-20:50 UTC), members × hit% × exp(−1.0275·E^ + 0.33) from each slice's own line. On the slices where both exist, this formula is within ~16% of the logged figure.
- **found**: successes, each re-checked by `search.verify_success`; certified records are in `goldbach/records/`.

## Q = 150,000, 1,093-1,094 rows (research cover), N < 10^200

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| A100 (gold-a100) | 66,048 | 69.26e9 | 11.414e9 | 26.19 | 0.033 (0.033 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4) | 81,856 | 85.83e9 | 14.162e9 | 26.20 | 0.041 (0.041 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4b) | 80,960 | 84.89e9 | 14.005e9 | 26.19 | 0.041 (0.041 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4c) | 238,016 | 249.58e9 | 40.564e9 | 26.16 | 0.121 (0.121 + 0.000) | 0 | - |
| L4 (gold-gpu) | 12,928 | 13.56e9 | 2.237e9 | 26.20 | 0.006 (0.006 + 0.000) | 0 | - |
| **all** | | 503.12e9 | 82.382e9 | | **0.242** | **0** | - |

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

**All covers: expected 8.74, found 8.**

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

- Q = 122,000: 7 hits survived 425 rows against 285.1 expected, P(sum ≥ that) = 0.108.
- Q = 140,000: 1 hits survived 63 rows against 40.8 expected, P(sum ≥ that) = 0.217.
