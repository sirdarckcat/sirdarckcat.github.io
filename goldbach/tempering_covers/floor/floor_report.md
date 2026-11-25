### Summary

c = slope in units of 1/ln²x. Ends are where a line reaches ln g0 = 0, as multiples of the tempered reach.

| x | tempered reach | θ(x) | c, 0 to 60% | c, 60–75% | c, 75–85% | c, 85–93% | least-squares intercept − θ(x) | least-squares c | end: least squares | end: line through 60–85% | end: last interval | end: θ(x)·ln²x (c = 1) | 93% point below the 60–85% line (seed difference) | 93% from the tempered cover / random starts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 797 | 30,931 | 758.4 | 1.017 | 0.972 | 1.065 | 1.213 | +17.9 | 1.052 | 1.065 | 1.082 | 1.041 | 1.094 | 12.96 (1.48) | 99.86 / 92.56, 94.04 |
| 1,499 | 70,111 | 1461.4 | 0.984 | 0.982 | 1.207 | 1.177 | +99.7 | 1.100 | 1.083 | 1.096 | 1.068 | 1.115 | 18.81 (3.42) | 233.50 / 211.02, 214.44 |

### x = 797: tempered reach 30,931 (vector found at Q = 30,916)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 18,559 | 0.60 | 335.45 | 335.36 | 335.40 |
| 23,198 | 0.75 | 234.62 | 234.06 | 234.34 |
| 26,291 | 0.85 | 160.74 | 160.36 | 160.55 |
| 28,766 | 0.93 | 92.56 | 94.04 | 93.30 |

Slope of the last interval: -27.17 per 1,000. Straight-line end: 32,200 (1.041 × the tempered reach).
Tail of the 28,766 run (seed 1): ln g0 = 92.6 at 28,771, 92.3 at 28,789, 91.5 at 28,807, 90.0 at 28,837, 85.2 at 28,879, 85.1 at 28,909, 85.0 at 28,921, 84.9 at 29,017, 82.7 at 29,101.

The line ln g0 = θ(x) − c·Q/ln²x: θ(797) = 758.40 (odd primes), ln²x = 44.63.
- slope between consecutive targets, in units of 1/ln²x: 0.972 (18,559–23,198), 1.065 (23,198–26,291), 1.213 (26,291–28,766)
- least-squares line through the 8 points: intercept 776.32 against θ(x) = 758.40 (+17.92); c = 1.052; end 32,940 = 1.065 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 33,850 (1.094 × reach).
- residuals of the mean from that line: -3.52 at 18,559, +4.74 at 23,198, +3.85 at 26,291, -5.07 at 28,766; seed-to-seed differences: 0.09, 0.56, 0.38, 1.48
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 1.017 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 33,478 = 1.082 × the tempered reach
- the 93% point against the line through the first three: -12.96 (seed difference there 1.48): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 99.86, against 92.56 and 94.04 from random starts
- the 85% target started from the best tempered cover: ln g0 = 159.14, against 160.74 and 160.36 from random starts
- independent check from the tail of the 26,291 run: ln g0(26,839) = 152.24 (650 samples) against 145.66 between the 85% and 93% points and 149.71 on the line through the first three

Loss θ − ln g0 against the research session's figures (pair sum / closed formula), and the drift of each run between its 2nd and 4th quarters (nats, + = ln g0 still rising; largest change of <k> at the middle and the cold temperatures, rows):

| target Q | run | ln g0 | loss | predicted (pair sum) | measured / predicted | predicted (closed) | measured / predicted | drift (nats) | middle | cold |
|---|---|---|---|---|---|---|---|---|---|---|
| 18,559 | seed 1 | 335.45 | 423.0 | 434.0 | 0.975 | 433.3 | 0.976 | +1.50 | 0.69 | 0.66 |
| 18,559 | seed 2 | 335.36 | 423.0 | 434.0 | 0.975 | 433.3 | 0.976 | +0.75 | 0.50 | 0.31 |
| 23,198 | seed 1 | 234.62 | 523.8 | 535.5 | 0.978 | 537.8 | 0.974 | +0.37 | 0.46 | 0.38 |
| 23,198 | seed 2 | 234.06 | 524.3 | 535.5 | 0.979 | 537.8 | 0.975 | +0.72 | 0.66 | 0.68 |
| 26,291 | seed 1 | 160.74 | 597.7 | 601.6 | 0.993 | 606.2 | 0.986 | +2.17 | 0.67 | 1.37 |
| 26,291 | seed 2 | 160.36 | 598.0 | 601.6 | 0.994 | 606.2 | 0.987 | +1.86 | 0.72 | 0.73 |
| 26,291 | cover start | 159.14 | 599.3 | 601.6 | 0.996 | 606.2 | 0.989 | +2.06 | 0.49 | 0.83 |
| 28,766 | seed 1 | 92.56 | 665.8 | 656.3 | 1.015 | 662.9 | 1.004 | +6.52 | 0.89 | 1.86 |
| 28,766 | seed 2 | 94.04 | 664.4 | 656.3 | 1.012 | 662.9 | 1.002 | +2.98 | 0.59 | 0.87 |
| 28,766 | cover start | 99.86 | 658.5 | 656.3 | 1.003 | 662.9 | 0.993 | +3.70 | 0.63 | 1.49 |

### x = 1,499: tempered reach 70,111 (vector found at Q = 70,059)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 42,067 | 0.60 | 687.42 | 687.80 | 687.61 |
| 52,583 | 0.75 | 494.54 | 494.54 | 494.54 |
| 59,594 | 0.85 | 336.25 | 336.21 | 336.23 |
| 65,203 | 0.93 | 211.02 | 214.44 | 212.73 |

Slope of the last interval: -22.02 per 1,000. Straight-line end: 74,865 (1.068 × the tempered reach).
Tail of the 65,203 run (seed 1): ln g0 = 210.8 at 65,239, 209.5 at 65,257, 208.9 at 65,269, 208.9 at 65,287, 206.3 at 65,293, 206.3 at 65,323, 201.8 at 65,371.

The line ln g0 = θ(x) − c·Q/ln²x: θ(1499) = 1461.45 (odd primes), ln²x = 53.47.
- slope between consecutive targets, in units of 1/ln²x: 0.982 (42,067–52,583), 1.207 (52,583–59,594), 1.177 (59,594–65,203)
- least-squares line through the 8 points: intercept 1561.11 against θ(x) = 1461.45 (+99.66); c = 1.100; end 75,904 = 1.083 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 78,149 (1.115 × reach).
- residuals of the mean from that line: -8.31 at 42,067, +14.90 at 52,583, +0.78 at 59,594, -7.36 at 65,203; seed-to-seed differences: 0.38, 0.00, 0.04, 3.42
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 0.984 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 76,829 = 1.096 × the tempered reach
- the 93% point against the line through the first three: -18.81 (seed difference there 3.42): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 233.50, against 211.02 and 214.44 from random starts
- the 85% target started from the best tempered cover: ln g0 = 337.96, against 336.25 and 336.21 from random starts
- independent check from the tail of the 59,594 run: ln g0(60,013) = 327.39 (250 samples) against 327.00 between the 85% and 93% points and 334.89 on the line through the first three

Loss θ − ln g0 against the research session's figures (pair sum / closed formula), and the drift of each run between its 2nd and 4th quarters (nats, + = ln g0 still rising; largest change of <k> at the middle and the cold temperatures, rows):

| target Q | run | ln g0 | loss | predicted (pair sum) | measured / predicted | predicted (closed) | measured / predicted | drift (nats) | middle | cold |
|---|---|---|---|---|---|---|---|---|---|---|
| 42,067 | seed 1 | 687.42 | 774.0 | 791.9 | 0.977 | 796.1 | 0.972 | +0.12 | 1.00 | 0.51 |
| 42,067 | seed 2 | 687.80 | 773.6 | 791.9 | 0.977 | 796.1 | 0.972 | +1.99 | 0.90 | 1.24 |
| 52,583 | seed 1 | 494.54 | 966.9 | 978.2 | 0.988 | 987.7 | 0.979 | +4.49 | 1.50 | 1.36 |
| 52,583 | seed 2 | 494.54 | 966.9 | 978.2 | 0.988 | 987.7 | 0.979 | +2.27 | 1.15 | 0.91 |
| 59,594 | seed 1 | 336.25 | 1125.2 | 1104.9 | 1.018 | 1118.7 | 1.006 | +5.39 | 1.20 | 1.94 |
| 59,594 | seed 2 | 336.21 | 1125.2 | 1104.9 | 1.018 | 1118.7 | 1.006 | +3.89 | 1.59 | 1.82 |
| 59,594 | cover start | 337.96 | 1123.5 | 1104.9 | 1.017 | 1118.7 | 1.004 | +3.19 | 0.94 | 1.62 |
| 65,203 | seed 1 | 211.02 | 1250.4 | 1200.9 | 1.041 | 1216.5 | 1.028 | +11.45 | 2.46 | 2.25 |
| 65,203 | seed 2 | 214.44 | 1247.0 | 1200.9 | 1.038 | 1216.5 | 1.025 | +8.80 | 1.98 | 2.25 |
| 65,203 | cover start | 233.50 | 1227.9 | 1200.9 | 1.023 | 1216.5 | 1.009 | +2.91 | 0.94 | 1.58 |

