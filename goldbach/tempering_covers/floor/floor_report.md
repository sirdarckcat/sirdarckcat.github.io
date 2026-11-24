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
- the 93% point against the line through the first three: -3.92 (seed difference there 0.15): below by more than the seed difference
- independent check from the tail of the 5,483 run: ln g0(5,779) = 35.70 (1130 samples) against 31.15 between the 85% and 93% points and 33.50 on the line through the first three

