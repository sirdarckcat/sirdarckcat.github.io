# Hit-rate calibration: found against expected (g200k/calib.py)

Research's covers (cover_d100_Q75000_49primes_k709, cover_d150_Q123000_69primes_k1003 at e756e20), rows cut below each target;
sieve200 to 10^7, the emptiest 2% of each 32,768-block, fm13 until the first probable prime; every found member verified
(N - q composite for every prime q below the target).  Expected = sum of n(a) (1 - p^)^a over the tested members' survivor
counts a, p^ = prp / tests of the same run.  Nominal E = rows x -ln(1 - p0) (p0 = 0.04256 at 100 digits, 0.03045 at 150);
E_tested = mean tested count x -ln(1 - p^).

| digits | target | rows | nominal E | E_tested | members | tested | p^ | expected (p^ -+ se) | found | found/expected | CPU-h | digits <= |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 150 | 40,000 | 355 | 11.0 | 9.61 | 25.2M | 503,808 | 0.08466 | 35.16 (34.67-35.66) | 39 | 1.11 | 0.02 | 148 |
| 100 | 25,000 | 271 | 11.8 | 10.05 | 50.3M | 1,007,616 | 0.12670 | 46.48 (45.99-46.97) | 44 | 0.95 | 0.03 | 99 |
| 150 | 50,000 | 422 | 13.0 | 11.52 | 167.8M | 3,358,720 | 0.08404 | 34.94 (34.71-35.17) | 24 | 0.69 | 0.15 | 149 |
| 100 | 30,000 | 312 | 13.6 | 11.63 | 134.2M | 2,686,976 | 0.12537 | 25.76 (25.57-25.96) | 29 | 1.13 | 0.08 | 100 |
| 100 | 35,000 | 361 | 15.7 | 13.60 | 587.2M | 11,755,520 | 0.12477 | 15.92 (15.86-15.99) | 19 | 1.19 | 0.36 | 101 |
| 150 | 60,000 | 512 | 15.8 | 14.12 | 1073.7M | 21,495,808 | 0.08356 | 16.77 (16.72-16.82) | 18 | 1.07 | 1.07 | 150 |
| 100 | 40,000 | 404 | 17.6 | 15.31 | 1610.6M | 32,243,712 | 0.12411 | 8.02 (7.99-8.04) | 6 | 0.75 | 1.16 | 101 |

Total: 179 found against 183.1 expected (0.98).

Check of the driver: Q = 12,000 on the 100-digit cover (143 rows, E_tested 5.4): 487 found, 510.6 expected (t_12k.json).

The rungs above E 15.7 continue as closeness-frontier rungs (frontier.py: many covers, d-digit windows), which test the same model:
../frontier/RESULTS.md.  With the 101-digit rung (E_tested 15.50: 7 found, 7.99 expected) the total is 186 found against
191.1 expected (0.97).
