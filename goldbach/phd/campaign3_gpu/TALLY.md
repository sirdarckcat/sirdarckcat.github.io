# campaign3 on the GPUs: expected against found

Updated 2026-11-22 21:17 UTC. Regenerated from the runtimes' own logs:
- `tally_rt.py` runs on each runtime and reads its search.log, gpu3_stats.log and found.jsonl;
- this page is written from those results.

Columns:
- **members**: members scanned (sieved).
- **hit mass**: members × hit% summed, i.e. the members' worth of full hit mass that was tested.
- **expected**: the model's expected successes, measured on the members actually tested:
  - *logged*: from `gpu3_stats.log`, Σ (1 − p^)^count over the tested members, p^ the batch's measured PRP rate;
  - *model*: for slices from before that accounting (20:22-20:50 UTC), members × hit% × exp(−1.0275·E^ + 0.33) from each slice's own line. On the slices where both exist, this formula is within ~16% of the logged figure.
- **found**: successes, each re-checked by `search.verify_success`; certified records are in `goldbach/records/`.

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
| RTX PRO 6000 (gold-g4) | 4,288 | 4.50e9 | 0.703e9 | 24.18 | 0.015 (0.015 + 0.000) | 0 | - |
| RTX PRO 6000 (gold-g4b) | 4,320 | 4.53e9 | 0.709e9 | 24.18 | 0.015 (0.015 + 0.000) | 0 | - |
| L4 (gold-gpu) | 1,088 | 1.14e9 | 0.178e9 | 24.18 | 0.004 (0.004 + 0.000) | 0 | - |
| **all** | | 10.17e9 | 1.591e9 | | **0.034** | **0** | - |

## Q = 150,000, 1,093-1,094 rows (research cover), N < 10^200

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| RTX PRO 6000 (gold-g4c) | 3,872 | 4.06e9 | 0.669e9 | 26.14 | 0.002 (0.002 + 0.000) | 0 | - |
| **all** | | 4.06e9 | 0.669e9 | | **0.002** | **0** | - |

## Q = 122,000, 867-869 rows, search_gpu2.py at full mass, N < 10^199

| GPU | slices | members | hit mass | mean E^ | expected (logged + model) | found | g |
|---|---|---|---|---|---|---|---|
| L4 (gold-gpu) | 180 | 0.19e9 | 0.189e9 | 21.02 | 0.110 (0.000 + 0.110) | 0 | - |
| **all** | | 0.19e9 | 0.189e9 | | **0.110** | **0** | - |

**All covers: expected 7.26, found 7.**
