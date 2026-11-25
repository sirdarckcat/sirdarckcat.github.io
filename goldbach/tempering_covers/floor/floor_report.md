### Summary

c = slope in units of 1/ln²x. Ends are where a line reaches ln g0 = 0, as multiples of the tempered reach.

| x | tempered reach | θ(x) | c, 0 to 60% | c, 60–75% | c, 75–85% | c, 85–93% | least-squares intercept − θ(x) | least-squares c | end: least squares | end: line through 60–85% | end: last interval | end: θ(x)·ln²x (c = 1) | 93% point below the 60–85% line (seed difference) | 93% from the tempered cover / random starts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1,999 | 98,731 | 1939.1 | 0.989 | 0.991 | 1.155 | 1.132 | +98.0 | 1.077 | 1.107 | 1.117 | 1.095 | 1.135 | 17.61 (0.06) | 333.21 / 319.02, 319.08 |

### x = 1,999: tempered reach 98,731 (vector found at Q = 98,495)

| target Q | share of reach | ln g0, seed 1 | ln g0, seed 2 | mean |
|---|---|---|---|---|
| 59,239 | 0.60 | 925.98 | 924.65 | 925.32 |
| 74,048 | 0.75 | 671.85 | 670.49 | 671.17 |
| 83,921 | 0.85 | 474.13 | 473.54 | 473.84 |
| 91,820 | 0.93 | 319.02 | 319.08 | 319.05 |

Slope of the last interval: -19.60 per 1,000. Straight-line end: 108,102 (1.095 × the tempered reach).
Tail of the 91,820 run (seed 1): ln g0 = 319.0 at 91,837, 318.5 at 91,867, 318.5 at 91,909, 318.5 at 91,921, 317.5 at 91,939, 317.3 at 91,951, 315.7 at 91,957, 312.7 at 92,077, 310.2 at 92,107, 310.0 at 92,119.

The line ln g0 = θ(x) − c·Q/ln²x: θ(1999) = 1939.15 (odd primes), ln²x = 57.77.
- slope between consecutive targets, in units of 1/ln²x: 0.991 (59,239–74,048), 1.155 (74,048–83,921), 1.132 (83,921–91,820)
- least-squares line through the 8 points: intercept 2037.12 against θ(x) = 1939.15 (+97.98); c = 1.077; end 109,310 = 1.107 × the tempered reach. With c = 1 through θ(x) the end would be θ(x)·ln²x = 112,017 (1.135 × reach).
- residuals of the mean from that line: -7.82 at 59,239, +14.02 at 74,048, +0.68 at 83,921, -6.89 at 91,820; seed-to-seed differences: 1.33, 1.36, 0.59, 0.06
- average slope from Q = 0 (ln g0 = θ(x)) to the 60% target: 0.989 in units of 1/ln²x; the straight line through the 60, 75 and 85% points ends at 110,315 = 1.117 × the tempered reach
- the 93% point against the line through the first three: -17.61 (seed difference there 0.06): below by more than the seed difference
- the 93% target started from the best tempered cover (cover_floor's two-sided test): ln g0 = 333.21, against 319.02 and 319.08 from random starts
- the 85% target started from the best tempered cover: ln g0 = 474.82, against 474.13 and 473.54 from random starts
- independent check from the tail of the 83,921 run: ln g0(84,631) = 462.31 (22 samples) against 459.92 between the 85% and 93% points and 467.52 on the line through the first three

Loss θ − ln g0 against the research session's figures (pair sum / closed formula), and the drift of each run between its 2nd and 4th quarters (nats, + = ln g0 still rising; largest change of <k> at the middle and the cold temperatures, rows):

| target Q | run | ln g0 | loss | predicted (pair sum) | measured / predicted | predicted (closed) | measured / predicted | drift (nats) | middle | cold |
|---|---|---|---|---|---|---|---|---|---|---|
| 59,239 | seed 1 | 925.98 | 1013.2 | 1024.8 | 0.989 | 1032.7 | 0.981 | +1.37 | 1.53 | 0.57 |
| 59,239 | seed 2 | 924.65 | 1014.5 | 1024.8 | 0.990 | 1032.7 | 0.982 | -0.70 | 0.78 | 1.14 |
| 74,048 | seed 1 | 671.85 | 1267.3 | 1263.8 | 1.003 | 1277.3 | 0.992 | +2.61 | 1.32 | 1.43 |
| 74,048 | seed 2 | 670.49 | 1268.7 | 1263.8 | 1.004 | 1277.3 | 0.993 | +3.62 | 1.27 | 1.33 |
| 83,921 | seed 1 | 474.13 | 1465.0 | 1425.3 | 1.028 | 1443.1 | 1.015 | +9.59 | 2.60 | 3.59 |
| 83,921 | seed 2 | 473.54 | 1465.6 | 1425.3 | 1.028 | 1443.1 | 1.016 | +5.71 | 0.71 | 3.40 |
| 83,921 | cover start | 474.82 | 1464.3 | 1425.3 | 1.027 | 1443.1 | 1.015 | +6.79 | 3.94 | 3.60 |
| 91,820 | seed 1 | 319.02 | 1620.1 | 1553.3 | 1.043 | 1573.2 | 1.030 | +15.53 | 2.84 | 4.08 |
| 91,820 | seed 2 | 319.08 | 1620.1 | 1553.3 | 1.043 | 1573.2 | 1.030 | +18.21 | 2.54 | 4.23 |
| 91,820 | cover start | 333.21 | 1605.9 | 1553.3 | 1.034 | 1573.2 | 1.021 | +10.36 | 2.53 | 2.78 |

