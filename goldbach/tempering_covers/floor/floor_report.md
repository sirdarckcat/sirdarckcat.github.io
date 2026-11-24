### Summary

c = slope in units of 1/ln²x. Ends are where a line reaches ln g0 = 0, as multiples of the tempered reach.

| x | tempered reach | θ(x) | c, 0 to 60% | c, 60–75% | c, 75–85% | c, 85–93% | least-squares intercept − θ(x) | least-squares c | end: least squares | end: line through 60–85% | end: last interval | end: θ(x)·ln²x (c = 1) | 93% point below the 60–85% line (seed difference) | 93% from the tempered cover / random starts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 127 | 2,311 | 111.2 | 1.115 | 1.154 | 1.190 | 1.224 | +4.0 | 1.181 | 0.991 | 0.995 | 0.987 | 1.129 | 0.53 (0.07) | 6.77 / 6.95, 6.88 |
| 149 | 2,953 | 131.0 | 1.120 | 0.948 | 1.095 | 1.636 | +2.5 | 1.133 | 0.998 | 1.040 | 0.964 | 1.110 | 6.39 (0.25) | 6.74 / 6.74, 6.49 |
| 251 | 6,451 | 231.4 | 1.045 | 1.033 | 1.077 | 1.268 | +7.1 | 1.094 | 1.032 | 1.047 | 1.012 | 1.095 | 3.92 (0.15) | 22.28 / 21.94, 22.09 |
| 349 | 10,159 | 322.6 | 1.027 | 1.071 | 0.982 | 1.515 | +19.2 | 1.126 | 1.024 | 1.053 | 0.991 | 1.089 | 10.68 (0.29) | 27.30 / 27.43, 27.14 |
| 397 | 12,163 | 370.0 | 1.018 | 1.151 | 1.020 | 1.269 | +22.3 | 1.128 | 1.024 | 1.032 | 1.011 | 1.089 | 3.48 (0.80) | 36.27 / 34.37, 35.17 |
| 599 | 21,067 | 562.3 | 1.022 | 0.985 | 1.138 | 1.362 | +32.2 | 1.113 | 1.037 | 1.062 | 1.009 | 1.092 | 15.05 (0.64) | 61.40 / 55.28, 55.92 |

### x = 127: tempered reach 2,311 (vector found at Q = 2,300)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 1,387 | 0.60 | 45.25 | 45.35 | 45.30 |
| 1,733 | 0.75 | 28.30 | 28.26 | 28.28 |
| 1,964 | 0.85 | 16.39 | 16.74 | 16.56 |
| 2,149 | 0.93 | 6.95 | 6.88 | 6.92 |

Slope of the last interval: -52.16 per 1,000. Straight-line end: 2,282 (0.987 × the tempered reach).
Tail of the 2,149 run (seed 1): ln g0 = 7.0 at 2,161, 6.5 at 2,179, 6.2 at 2,221, 6.1 at 2,239, 6.1 at 2,251, 0.6 at 2,281.

The line ln g0 = θ(x) − c·Q/ln²x: θ(127) = 111.22 (odd primes), ln²x = 23.47.
- slope between consecutive targets, in units of 1/ln²x: 1.154 (1,387–1,733), 1.190 (1,733–1,964), 1.224 (1,964–2,149)
- least-squares line through the 8 points: intercept 115.24 against θ(x) = 111.22 (+4.02); c = 1.181; end 2,291 = 0.991 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 2,610 (1.129 × reach).
- residuals of the mean from that line: -0.16 at 1,387, +0.23 at 1,733, +0.14 at 1,964, -0.21 at 2,149; seed-to-seed differences: 0.10, 0.04, 0.35, 0.07
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.115 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 2,299 = 0.995 × the tempered reach
- the 93% point against the line through the first three: -0.53 (seed difference there 0.07): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 6.77, against 6.95 and 6.88 from random starts
- independent check from the tail of the 1,964 run: ln g0(2,137) = 9.74 (4308 samples) against 7.54 between the 85% and 93% points and 8.04 on the line through the first three

### x = 149: tempered reach 2,953 (vector found at Q = 2,921)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 1,772 | 0.60 | 51.66 | 51.73 | 51.69 |
| 2,215 | 0.75 | 34.93 | 34.93 | 34.93 |
| 2,510 | 0.85 | 22.04 | 22.03 | 22.04 |
| 2,746 | 0.93 | 6.74 | 6.49 | 6.62 |

Slope of the last interval: -65.34 per 1,000. Straight-line end: 2,847 (0.964 × the tempered reach).
Tail of the 2,746 run (seed 1): ln g0 = 6.7 at 2,749, 6.6 at 2,767, 5.8 at 2,791, 5.7 at 2,797, 4.1 at 2,857.

The line ln g0 = θ(x) − c·Q/ln²x: θ(149) = 130.95 (odd primes), ln²x = 25.04.
- slope between consecutive targets, in units of 1/ln²x: 0.948 (1,772–2,215), 1.095 (2,215–2,510), 1.636 (2,510–2,746)
- least-squares line through the 8 points: intercept 133.42 against θ(x) = 130.95 (+2.46); c = 1.133; end 2,947 = 0.998 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 3,279 (1.110 × reach).
- residuals of the mean from that line: -1.51 at 1,772, +1.78 at 2,215, +2.24 at 2,510, -2.50 at 2,746; seed-to-seed differences: 0.07, 0.00, 0.01, 0.25
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.120 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 3,071 = 1.040 × the tempered reach
- the 93% point against the line through the first three: -6.39 (seed difference there 0.25): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 6.74, against 6.74 and 6.49 from random starts
- independent check from the tail of the 2,510 run: ln g0(2,689) = 12.86 (368 samples) against 10.34 between the 85% and 93% points and 15.28 on the line through the first three

### x = 251: tempered reach 6,451 (vector found at Q = 6,440)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 3,871 | 0.60 | 98.89 | 98.92 | 98.91 |
| 4,838 | 0.75 | 66.31 | 66.09 | 66.20 |
| 5,483 | 0.85 | 43.58 | 43.31 | 43.45 |
| 5,999 | 0.93 | 21.94 | 22.09 | 22.02 |

Slope of the last interval: -41.53 per 1,000. Straight-line end: 6,529 (1.012 × the tempered reach).
Tail of the 5,999 run (seed 1): ln g0 = 21.9 at 6,007, 21.4 at 6,043, 21.2 at 6,073, 19.7 at 6,121, 19.5 at 6,199, 16.1 at 6,217, 16.0 at 6,271.

The line ln g0 = θ(x) − c·Q/ln²x: θ(251) = 231.43 (odd primes), ln²x = 30.53.
- slope between consecutive targets, in units of 1/ln²x: 1.033 (3,871–4,838), 1.077 (4,838–5,483), 1.268 (5,483–5,999)
- least-squares line through the 8 points: intercept 238.54 against θ(x) = 231.43 (+7.12); c = 1.094; end 6,656 = 1.032 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 7,066 (1.095 × reach).
- residuals of the mean from that line: -0.91 at 3,871, +1.04 at 4,838, +1.40 at 5,483, -1.54 at 5,999; seed-to-seed differences: 0.03, 0.22, 0.27, 0.15
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.045 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 6,754 = 1.047 × the tempered reach
- the 93% point against the line through the first three: -3.92 (seed difference there 0.15): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 22.28, against 21.94 and 22.09 from random starts
- independent check from the tail of the 5,483 run: ln g0(5,779) = 35.70 (1130 samples) against 31.15 between the 85% and 93% points and 33.50 on the line through the first three

### x = 349: tempered reach 10,159 (vector found at Q = 10,116)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 6,095 | 0.60 | 140.12 | 139.80 | 139.96 |
| 7,619 | 0.75 | 92.17 | 92.49 | 92.33 |
| 8,635 | 0.85 | 63.05 | 63.39 | 63.22 |
| 9,448 | 0.93 | 27.43 | 27.14 | 27.29 |

Slope of the last interval: -44.20 per 1,000. Straight-line end: 10,065 (0.991 × the tempered reach).
Tail of the 9,448 run (seed 1): ln g0 = 27.4 at 9,463, 27.0 at 9,511, 26.7 at 9,547, 26.6 at 9,601, 24.2 at 9,619, 23.4 at 9,631, 22.1 at 9,643, 21.9 at 9,661, 18.6 at 9,679, 16.0 at 9,733.

The line ln g0 = θ(x) − c·Q/ln²x: θ(349) = 322.63 (odd primes), ln²x = 34.28.
- slope between consecutive targets, in units of 1/ln²x: 1.071 (6,095–7,619), 0.982 (7,619–8,635), 1.515 (8,635–9,448)
- least-squares line through the 8 points: intercept 341.83 against θ(x) = 322.63 (+19.20); c = 1.126; end 10,406 = 1.024 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 11,060 (1.089 × reach).
- residuals of the mean from that line: -1.65 at 6,095, +0.78 at 7,619, +5.05 at 8,635, -4.18 at 9,448; seed-to-seed differences: 0.32, 0.32, 0.34, 0.29
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.027 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 10,701 = 1.053 × the tempered reach
- the 93% point against the line through the first three: -10.68 (seed difference there 0.29): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 27.30, against 27.43 and 27.14 from random starts
- independent check from the tail of the 8,635 run: ln g0(8,821) = 52.03 (32 samples) against 55.00 between the 85% and 93% points and 56.96 on the line through the first three

### x = 397: tempered reach 12,163 (vector found at Q = 12,131)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 7,298 | 0.60 | 162.58 | 162.52 | 162.55 |
| 9,122 | 0.75 | 103.81 | 104.07 | 103.94 |
| 10,339 | 0.85 | 69.37 | 69.15 | 69.26 |
| 11,312 | 0.93 | 34.37 | 35.17 | 34.77 |

Slope of the last interval: -35.45 per 1,000. Straight-line end: 12,293 (1.011 × the tempered reach).
Tail of the 11,312 run (seed 1): ln g0 = 34.4 at 11,317, 34.3 at 11,353, 33.6 at 11,383, 33.5 at 11,437, 33.5 at 11,443, 32.2 at 11,491, 30.6 at 11,551, 30.6 at 11,689, 24.7 at 11,701.

The line ln g0 = θ(x) − c·Q/ln²x: θ(397) = 370.04 (odd primes), ln²x = 35.81.
- slope between consecutive targets, in units of 1/ln²x: 1.151 (7,298–9,122), 1.020 (9,122–10,339), 1.269 (10,339–11,312)
- least-squares line through the 8 points: intercept 392.32 against θ(x) = 370.04 (+22.28); c = 1.128; end 12,460 = 1.024 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 13,250 (1.089 × reach).
- residuals of the mean from that line: +0.02 at 7,298, -1.15 at 9,122, +2.49 at 10,339, -1.36 at 11,312; seed-to-seed differences: 0.06, 0.26, 0.22, 0.80
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.018 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 12,554 = 1.032 × the tempered reach
- the 93% point against the line through the first three: -3.48 (seed difference there 0.80): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 36.27, against 34.37 and 35.17 from random starts
- the 85% target started from the best tempered cover: ln g0 = 69.42, against 69.37 and 69.15 from random starts
- independent check from the tail of the 10,339 run: ln g0(10,513) = 58.81 (68 samples) against 63.09 between the 85% and 93% points and 62.85 on the line through the first three

### x = 599: tempered reach 21,067 (vector found at Q = 21,036)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 12,640 | 0.60 | 246.46 | 246.47 | 246.47 |
| 15,800 | 0.75 | 170.43 | 170.23 | 170.33 |
| 17,907 | 0.85 | 111.83 | 111.57 | 111.70 |
| 19,592 | 0.93 | 55.28 | 55.92 | 55.60 |

Slope of the last interval: -33.29 per 1,000. Straight-line end: 21,262 (1.009 × the tempered reach).
Tail of the 19,592 run (seed 1): ln g0 = 55.3 at 19,597, 54.7 at 19,603, 54.0 at 19,609, 52.7 at 19,681, 52.7 at 19,687, 49.9 at 19,699, 44.6 at 19,753.

The line ln g0 = θ(x) − c·Q/ln²x: θ(599) = 562.29 (odd primes), ln²x = 40.90.
- slope between consecutive targets, in units of 1/ln²x: 0.985 (12,640–15,800), 1.138 (15,800–17,907), 1.362 (17,907–19,592)
- least-squares line through the 8 points: intercept 594.49 against θ(x) = 562.29 (+32.21); c = 1.113; end 21,852 = 1.037 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 22,997 (1.092 × reach).
- residuals of the mean from that line: -4.16 at 12,640, +5.68 at 15,800, +4.37 at 17,907, -5.89 at 19,592; seed-to-seed differences: 0.01, 0.20, 0.26, 0.64
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.022 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 22,366 = 1.062 × the tempered reach
- the 93% point against the line through the first three: -15.05 (seed difference there 0.64): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 61.40, against 55.28 and 55.92 from random starts
- the 85% target started from the best tempered cover: ln g0 = 111.45, against 111.83 and 111.57 from random starts
- independent check from the tail of the 17,907 run: ln g0(18,211) = 102.88 (401 samples) against 101.58 between the 85% and 93% points and 105.82 on the line through the first three

