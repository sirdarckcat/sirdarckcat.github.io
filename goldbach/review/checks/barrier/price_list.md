# price_list: the price of every exit, from the team's own models (audit notes, 25 Nov 2026)

Scripts and raw outputs: /tmp/claude-0/-home-user-sirdarckcat-github-io/df2f42b3-a989-5e01-80a4-d6d0ee0e6589/scratchpad/audit/run/price_list/work/
(fastfloor.py, model.py, tables.py, tables2.py, tables3.py; out_base.txt, out_tables2.txt, out_tables3.txt, five sensitivity runs out_*.txt)

## Model (all pieces are the team's)
- rows left by the best cover at (digits d, target Q): the price recursion cover_price.floor (research branch,
  goldbach/sublinear/cover_price.py, cover_dual.py), re-implemented as an O(n) backward recursion; reproduces
  cover_dual.txt to every printed digit. Corrected to the best covers actually found with
  found/floor = 0.897 + 0.223 D/Q + 0.0242 ln(moduli) (22 points from 13 to 159 moduli: closeness_cost.txt,
  design_menu.txt, README "The other direction"; rms 0.5%, max 0.9%). At 200 digits the covers found are used
  directly up to 213,070 (1,092 / 1,181 / 1,248 / 1,336 / 1,420 / 1,503 / 1,609 rows), floor x 1.016 above.
- E = -rows ln(1-p) + 0.117 (p = 2 prod r/(r-1) / ln N; 0.117 = -ln 0.89, price_list.py's measured ratio).
- cost of a member: cover_dual_cpu.cost (sieve all, test the emptiest; binomial survivors) with GPU constants
  calibrated to one RTX PRO 6000 at 200 digits: 9.8e-7 design hits/s on 1,250 rows (day-one report) = 60 ns per
  full-weight member; sieve 4.0 ns per raw member in proportion to rows (2.7 and 6.4 tried), Fermat test ~ digits^3
  (2.5 tried). Units: 0.29 design hits a day at 37.12 units an hour (fleet mix) = 3.25e-4 hits a unit.
- ceiling: goldbach/closeness.py (lead branch).
- checks: E(200, 213,070) = 39.18 (README 39.2-39.3); E(150, 100,003) = 24.8 (FRONTIER.md 24.9-25.5);
  E(100, 100,003) = 42.3 (FRONTIER.md 43.7-43.8); 63-digit record: cover used 22.3, scan log implies 22.4, model 21.4;
  CPU-hours per hit at 300/350/400 digits 83 / 2.6 / 0.23 (team 78 / 2.7 / 0.24); 200-digit forecast 174,200 with one
  expected success, ~176,200 expected record (team 175,000-176,000); with the README's e^30.75: 171,600 (team 172,000);
  150 digits 11.1%, 100 digits 17.3% (team "11%" and "17%"); 200,000 with the remaining units at 230 digits (team ~225),
  one fleet-day 244 (team ~240).

## Findings
1. Budget accounting. 7,000 units at the fleet's logged rate are e^31.28 full-weight members, not e^30.75; e^30.75 is
   ~4,100 units. The README's two forecasts (172,000 and 175,000-176,000) differ for this reason only. The shortfall
   for 10% is e^7.8 (x2,340) with 7,000 units and 1,609 rows; e^8.4-8.5 with e^30.75; x5,600 in brainstorm (1,623 rows).
2. 200 digits, today's method: 0.204 nats per 1,000 in g, 4.4 nats per percentage point of closeness.
   x10 -> 185,400 (+0.5 pp), x100 -> 196,900, x1,000 -> 208,700, x10,000 -> 220,100.
   10% x10^3.4; 12.5% x10^8.1; 15% x10^12.9; 20% x10^22.3; 25% x10^31.8; 50% x10^78.3.
3. Size: at fixed budget closeness x digits is nearly constant (17.9 at 60 digits, 16.4 at 200, 15.6 at 300);
   at 10% closeness one more digit of N costs x1.25. Reachable now: 10% up to 165 digits, 25% up to 71, 50% up to 36;
   achieved: 63, 46, 25. g > ln^2 N reachable up to 160 digits (x10: 171, x100: 183); achieved up to 63.
4. The stretch 63-150 digits of the frontier is empty and cheap: 96 CPU-hours buy 58,000 at 100 digits (12.5%, g > ln^2 N).
5. Money: 7,000 units ~ $700 at $9.99 per 100 units (assumed list price, 2022 launch figure); x10 $7,000; x100 $70,000;
   10% at 200 digits 16.6 million units ~ $1.7 million (to $3.3 million on the README's budget convention), 188 RTX-years.
6. Even a perfect search to depth 10^8 (README Result 3) ends near 16% with this budget; 25% needs ~e^31 times more
   even then (extrapolated e^62 against e^31.3), 50% about e^120-140 times.
# calibration: sieve 4.0 ns/raw member, effective test 31.0 ns at 200 digits, test ~ d^3; a unit = 332 RTX-s (fleet mix); corr shift +0.000
# seconds per full-weight member at 200d/170k: 60.2 ns; 7,000 units = e^31.28 full-weight members; README budget e^30.75 = 4101 units
# check: units per design hit at 170,000: 2928 (fleet: 3072)
# checks: E(100 digits, 100,003) = 42.33 (FRONTIER.md: 43.84 classic, 43.66 realizable); E(150, 100,003) = 24.81 (FRONTIER.md: 25.55 predicted, 24.91 the cover used); E(200, 213,070) = 39.18 (README 39.2-39.3)

## A1. 200 digits: target vs cost (today's method)
target | share | rows | E=ln(members/success) | units per success | x of 7,000 units | ln x | x of README budget e^30.75
160,357 (record) | 7.5% | 1184 | 28.9 | 10^2.80 | 10^-1.04 | -2.4 | 10^-0.82
170,000 | 8.0% | 1248 | 30.4 | 10^3.47 | 10^-0.38 | -0.9 | 10^-0.15
180,000 | 8.4% | 1336 | 32.5 | 10^4.38 | 10^0.53 | 1.2 | 10^0.78
190,000 | 8.9% | 1420 | 34.6 | 10^5.25 | 10^1.41 | 3.2 | 10^1.67
200,000 | 9.4% | 1503 | 36.6 | 10^6.11 | 10^2.27 | 5.2 | 10^2.54
213,070 (10%) | 10.0% | 1609 | 39.2 | 10^7.22 | 10^3.37 | 7.8 | 10^3.66
245,000 (11.5%) | 11.5% | 1881 | 45.8 | 10^10.05 | 10^6.21 | 14.3 | 10^6.53
266,338 (12.5%) | 12.5% | 2062 | 50.2 | 10^11.94 | 10^8.10 | 18.6 | 10^8.44
300,000 (14.1%) | 14.1% | 2346 | 57.1 | 10^14.91 | 10^11.07 | 25.5 | 10^11.43
319,606 (15%) | 15.0% | 2516 | 61.2 | 10^16.69 | 10^12.85 | 29.6 | 10^13.23
350,000 (16.4%) | 16.4% | 2776 | 67.5 | 10^19.41 | 10^15.57 | 35.8 | 10^15.96
426,141 (20%) | 20.0% | 3417 | 83.1 | 10^26.15 | 10^22.30 | 51.4 | 10^22.73
500,000 (23.5%) | 23.5% | 4042 | 98.2 | 10^32.72 | 10^28.87 | 66.5 | 10^29.31
532,676 (25%) | 25.0% | 4318 | 104.9 | 10^35.62 | 10^31.77 | 73.2 | 10^32.22
1,065,352 (50%) | 50.0% | 8729 | 212.0 | 10^82.15 | 10^78.31 | 180.3 | 10^78.73

## A2. 200 digits: record level bought by a multiple of the remaining 7,000 units
multiplier | units | Q with one expected success | share | expected record ~ Q1+2,000 | share | same with README budget e^30.75 x mult (members only)
x1 | 7,000 | 174,247 | 8.18% | 176,247 | 8.27% | 171,614 (8.05%)
x3 | 21,000 | 179,396 | 8.42% | 181,396 | 8.51% | 176,793 (8.30%)
x10 | 70,000 | 185,350 | 8.70% | 187,350 | 8.79% | 182,468 (8.56%)
x100 | 700,000 | 196,895 | 9.24% | 198,895 | 9.33% | 193,805 (9.10%)
x1000 | 7,000,000 | 208,679 | 9.79% | 210,679 | 9.89% | 205,355 (9.64%)
x10000 | 70,000,000 | 220,058 | 10.33% | 222,058 | 10.42% | 216,902 (10.18%)
x100000 | 700,000,000 | 231,242 | 10.85% | 233,242 | 10.95% | 227,990 (10.70%)
x1e+06 | 7,000,000,000 | 242,678 | 11.39% | 244,678 | 11.48% | 239,238 (11.23%)

## B. closeness reachable with 7,000 units, by size
digits | moduli | ceiling | Q with one expected success | closeness | rows | p | E | cost per full-weight member vs 200d | ln^2 N | Q/ln^2 N | same Q, README e^30.75 budget (closeness)
60 | 31 | 148,547 | 44,264 | 29.8% | 521 | 0.0641 | 34.6 | 0.036 | 19,087 | 2.32 | 43,628 (29.4%)
80 | 41 | 283,408 | 62,640 | 22.1% | 647 | 0.0512 | 34.1 | 0.060 | 33,932 | 1.85 | 61,674 (21.8%)
100 | 49 | 465,348 | 80,630 | 17.3% | 769 | 0.0426 | 33.6 | 0.103 | 53,019 | 1.52 | 79,428 (17.1%)
120 | 57 | 695,303 | 98,808 | 14.2% | 883 | 0.0366 | 33.0 | 0.171 | 76,347 | 1.29 | 97,242 (14.0%)
140 | 65 | 976,392 | 117,332 | 12.0% | 990 | 0.0322 | 32.6 | 0.276 | 103,917 | 1.13 | 115,632 (11.8%)
150 | 69 | 1,136,627 | 126,488 | 11.1% | 1042 | 0.0304 | 32.3 | 0.350 | 119,293 | 1.06 | 124,578 (11.0%)
160 | 73 | 1,308,704 | 135,758 | 10.4% | 1092 | 0.0289 | 32.1 | 0.438 | 135,729 | 1.00 | 133,724 (10.2%)
170 | 77 | 1,494,005 | 145,208 | 9.7% | 1142 | 0.0274 | 31.9 | 0.542 | 153,225 | 0.95 | 142,838 (9.6%)
180 | 81 | 1,692,679 | 154,352 | 9.1% | 1190 | 0.0262 | 31.7 | 0.668 | 171,781 | 0.90 | 152,018 (9.0%)
200 | 89 | 2,130,704 | 174,247 | 8.2% | 1285 | 0.0240 | 31.3 | 0.985 | 212,076 | 0.82 | 171,642 (8.1%)
250 | 107 | 3,460,750 | 219,534 | 6.3% | 1511 | 0.0199 | 30.4 | 2.401 | 331,369 | 0.66 | 216,108 (6.2%)
300 | 125 | 5,136,234 | 266,118 | 5.2% | 1722 | 0.0170 | 29.7 | 5.082 | 477,171 | 0.56 | 262,050 (5.1%)

## B2. largest size at which a closeness is reachable with 7,000 units (and x10, x100)
x1: 10%: 165 digits; 12.5%: 135 digits; 15%: 114 digits; 25%: 71 digits; 50%: 36 digits
x10: 10%: 175 digits; 12.5%: 143 digits; 15%: 121 digits; 25%: 75 digits; 50%: 39 digits
x100: 10%: 185 digits; 12.5%: 151 digits; 15%: 128 digits; 25%: 79 digits; 50%: 41 digits

## B3. largest size with g > ln^2 N reachable (one expected success)
x1: 160 digits (ln^2 N = 135,729, 10.4% of that size's ceiling)
x10: 171 digits (ln^2 N = 155,033, 10.2% of that size's ceiling)
x100: 183 digits (ln^2 N = 177,555, 10.1% of that size's ceiling)

## C. fixed gap: digits needed on the GPU fleet (kernels assumed to exist at every size)
gap | budget | units | digits | lag = digits / ideal digits | closeness at that size
200,000 | one fleet-day, 7 cards | 891 | 244 | 3.56 (ideal 68.5) | 6.1%
200,000 | one fleet-day, 5 cards | 603 | 247 | 3.61 (ideal 68.5) | 5.9%
200,000 | 7,000 units | 7,000 | 230 | 3.36 (ideal 68.5) | 6.9%
200,000 | x10 | 70,000 | 217 | 3.17 (ideal 68.5) | 7.9%
200,000 | x100 | 700,000 | 204 | 2.98 (ideal 68.5) | 9.0%
200,000 | x1,000 | 7,000,000 | 194 | 2.83 (ideal 68.5) | 10.0%
213,070 | one fleet-day, 7 cards | 891 | 258 | 3.66 (ideal 70.4) | 5.8%
213,070 | one fleet-day, 5 cards | 603 | 261 | 3.71 (ideal 70.4) | 5.6%
213,070 | 7,000 units | 7,000 | 244 | 3.46 (ideal 70.4) | 6.5%
213,070 | x10 | 70,000 | 230 | 3.27 (ideal 70.4) | 7.4%
213,070 | x100 | 700,000 | 217 | 3.08 (ideal 70.4) | 8.4%
213,070 | x1,000 | 7,000,000 | 206 | 2.92 (ideal 70.4) | 9.4%
## check of the CPU model against cover_dual_cpu.txt (found covers): CPU-hours per hit, vector kernel
400 digits: model rows 1006 (found 1010); model CPU-hours 0.229 (team, with the found cover: 0.241)
350 digits: model rows 1109 (found 1113); model CPU-hours 2.58 (team, with the found cover: 2.74)
300 digits: model rows 1222 (found 1218); model CPU-hours 83.2 (team, with the found cover: 77.6)

## C (CPU). fixed gap on processors: digits needed
gap | budget | CPU-hours | digits, vector kernel | digits, gmpy2 | lag (vector) | closeness there
200,000 | one core-day | 24 | 317 | 342 | 4.63 | 3.5%
200,000 | 4 cores, one day | 96 | 300 | 320 | 4.38 | 3.9%
200,000 | 4 cores, a week | 672 | 279 | 297 | 4.07 | 4.6%
200,000 | 64 cores, a month | 46,080 | 245 | 257 | 3.58 | 6.0%
213,070 | one core-day | 24 | 337 | 364 | 4.78 | 3.2%
213,070 | 4 cores, one day | 96 | 319 | 342 | 4.53 | 3.6%
213,070 | 4 cores, a week | 672 | 297 | 315 | 4.22 | 4.2%
213,070 | 64 cores, a month | 46,080 | 260 | 272 | 3.69 | 5.7%

## D. every record: g / ln^2 N, closeness, lag
record | digits | g | ln^2 N | g / ln^2 N | closeness | ideal digits | lag = digits/ideal | on the frontier
exhaustive search <= 4e18 (not ours) | 19 | 9,781 | 1,819 | 5.378 | 102.24% | 19 | 1.02 | yes
threshold_23digit_g10729 | 23 | 10,729 | 2,681 | 4.002 | 69.94% | 19 | 1.19 | yes
threshold_23digit_g10771 | 23 | 10,771 | 2,696 | 3.995 | 69.74% | 19 | 1.18 | yes
threshold_23digit_g11701 | 23 | 11,701 | 2,740 | 4.270 | 74.31% | 20 | 1.14 | yes
threshold_23digit_g10399 | 23 | 10,399 | 2,779 | 3.742 | 64.96% | 19 | 1.20 | no
threshold_23digit_g10159 | 23 | 10,159 | 2,786 | 3.647 | 63.26% | 19 | 1.21 | no
threshold_25digit_g10357 | 25 | 10,357 | 3,245 | 3.192 | 53.81% | 19 | 1.31 | no
threshold_27digit_g10111 | 27 | 10,111 | 3,717 | 2.720 | 44.75% | 19 | 1.43 | no
threshold_30digit_g10459 | 30 | 10,459 | 4,548 | 2.300 | 36.52% | 19 | 1.56 | no
threshold_46digit_g20551 | 46 | 20,551 | 11,163 | 1.841 | 25.45% | 25 | 1.81 | yes
threshold_63digit_g30139 | 63 | 30,139 | 20,877 | 1.444 | 18.33% | 30 | 2.10 | yes
threshold_150digit_g104527 | 150 | 104,527 | 119,161 | 0.877 | 9.21% | 51 | 2.92 | yes
threshold_179digit_g101149 | 179 | 101,149 | 168,509 | 0.600 | 6.10% | 51 | 3.53 | no
threshold_186digit_g109357 | 186 | 109,357 | 181,672 | 0.602 | 6.08% | 52 | 3.55 | yes
threshold_193digit_g102337 | 193 | 102,337 | 196,137 | 0.522 | 5.23% | 51 | 3.79 | no
threshold_195digit_g100297 | 195 | 100,297 | 201,300 | 0.498 | 4.98% | 50 | 3.86 | no
dual_197digit_g107719 | 197 | 107,719 | 205,430 | 0.524 | 5.23% | 52 | 3.78 | no
budget_1e200_199digit_g119419 | 199 | 119,419 | 208,678 | 0.572 | 5.70% | 54 | 3.65 | yes
dual_199digit_g110917 | 199 | 110,917 | 209,466 | 0.530 | 5.28% | 53 | 3.77 | no
budget_1e200_199digit_g125269 | 199 | 125,269 | 209,943 | 0.597 | 5.94% | 56 | 3.58 | yes
budget_1e200_199digit_g132103 | 199 | 132,103 | 209,951 | 0.629 | 6.27% | 57 | 3.49 | yes
budget_1e200_199digit_g133981 | 199 | 133,981 | 209,956 | 0.638 | 6.36% | 57 | 3.47 | yes
budget_1e200_200digit_g112249 | 200 | 112,249 | 209,991 | 0.535 | 5.33% | 53 | 3.77 | no
budget_1e200_200digit_g158209 | 200 | 158,209 | 211,449 | 0.748 | 7.45% | 62 | 3.24 | yes
budget_1e200_200digit_g146191 | 200 | 146,191 | 211,559 | 0.691 | 6.88% | 60 | 3.36 | no
budget_1e200_200digit_g157837 | 200 | 157,837 | 211,843 | 0.745 | 7.42% | 62 | 3.25 | no
budget_1e200_200digit_g160357 | 200 | 160,357 | 212,032 | 0.756 | 7.53% | 62 | 3.22 | yes
g200k_347digit_g216289 | 347 | 216,289 | 637,966 | 0.339 | 3.08% | 71 | 4.89 | yes
g200k_400digit_g200293 | 400 | 200,293 | 845,049 | 0.237 | 2.11% | 69 | 5.84 | no
g200k_400digit_g206593 | 400 | 206,593 | 845,052 | 0.244 | 2.17% | 69 | 5.76 | no
height_2480digit_g1157341 | 2480 | 1,157,341 | 32,585,971 | 0.036 | 0.25% | 151 | 16.40 | yes
megagap_2692digit_g1134871 | 2692 | 1,134,871 | 38,394,524 | 0.030 | 0.20% | 150 | 17.96 | no
height_11263digit_g1200109 | 11263 | 1,200,109 | 672,486,600 | 0.002 | 0.01% | 154 | 73.24 | yes
bls_game1_11263digit_g1200109 | 11263 | 1,200,109 | 672,532,772 | 0.002 | 0.01% | 154 | 73.24 | no
height_15595digit_g2000269 | 15595 | 2,000,269 | 1,289,395,414 | 0.002 | 0.01% | 194 | 80.26 | yes
height_33938digit_g5000251 | 33938 | 5,000,251 | 6,106,381,298 | 0.001 | 0.00% | 296 | 114.54 | yes
height_61329digit_g10000141 | 61329 | 10,000,141 | 19,941,661,882 | 0.001 | 0.00% | 409 | 150.11 | yes
height_91752digit_g16046137 | 91752 | 16,046,137 | 44,633,296,576 | 0.000 | 0.00% | 509 | 180.21 | yes

## D2. what 'g > ln^2 N' and '10% of the ceiling' cost at each size (GPU fleet, kernels assumed at every size)
digits | ln^2 N | share of ceiling | rows | E | units for one expected success | x of 7,000 | 10% of ceiling | rows | E | units | x of 7,000
100 | 53,019 | 11.4% | 482 | 21.1 | 0.0269 | 3.85e-06 | 46,535 | 413 | 18.1 | 0.00143 | 2.04e-07
120 | 76,347 | 11.0% | 662 | 24.8 | 1.93 | 0.000276 | 69,530 | 594 | 22.3 | 0.159 | 2.27e-05
140 | 103,917 | 10.6% | 865 | 28.5 | 119 | 0.017 | 97,639 | 807 | 26.6 | 18.3 | 0.00262
150 | 119,293 | 10.5% | 975 | 30.3 | 893 | 0.128 | 113,663 | 923 | 28.7 | 186 | 0.0266
160 | 135,729 | 10.4% | 1092 | 32.1 | 6.94e+03 | 0.991 | 130,870 | 1049 | 30.8 | 1.97e+03 | 0.281
170 | 153,225 | 10.3% | 1215 | 33.9 | 5.19e+04 | 7.42 | 149,401 | 1180 | 33.0 | 2e+04 | 2.85
180 | 171,781 | 10.1% | 1340 | 35.6 | 3.47e+05 | 49.5 | 169,268 | 1317 | 35.0 | 1.92e+05 | 27.4
190 | 191,399 | 10.0% | 1473 | 37.5 | 2.5e+06 | 357 | 190,487 | 1466 | 37.3 | 2.07e+06 | 296
200 | 212,076 | 10.0% | 1601 | 39.0 | 1.35e+07 | 1.93e+03 | 213,070 | 1609 | 39.2 | 1.66e+07 | 2.37e+03

## B4. at a fixed share of the ceiling, E against digits (the statement 'E grows in proportion to the digits')
digits | E at 10% | E at 25% | E at 50% | E at ln^2 N
60 | 10.2 | 28.8 | 58.7 | 13.7
80 | 13.9 | 38.8 | 79.5 | 17.3
100 | 18.1 | 49.6 | 101.0 | 21.1
150 | 28.7 | 76.9 | 155.4 | 30.3
200 | 39.2 | 104.9 | 212.0 | 39.0
250 | 50.7 | 133.0 | 267.1 | 48.4
300 | 62.0 | 161.7 | 324.3 | 57.2
63-digit check: moduli 32 log10 M 52.91353580307637
  p = 0.0616; E with the cover used (348 rows) = 22.14; implied by '0.22 expected in 7.03e9 members': 24.19
  model (first 32 primes to 137, floor 336, corrected 336 rows, p 0.0615): E = 21.43

## B5. what processors buy by size (one success expected; sieve to 1e7, tests at gmpy2 speed)
digits | 96 CPU-hours: Q | closeness | Q/ln^2 N | 10,000 CPU-hours: Q | closeness | best achieved at or below this size (closeness)
46 | 23,834 | 29.4% | 2.12 | 28,002 | 34.5% | 20,551 at 46 digits (25.5%)
63 | 34,592 | 20.8% | 1.64 | 40,760 | 24.6% | 30,139 at 63 digits (18.3%)
80 | 45,588 | 16.1% | 1.34 | 53,658 | 18.9% | 30,139 at 63 digits
100 | 58,154 | 12.5% | 1.10 | 68,684 | 14.8% | 30,139 at 63 digits
120 | 71,144 | 10.2% | 0.93 | 83,904 | 12.1% | 30,139 at 63
150 | 90,500 | 8.0% | 0.76 | 107,172 | 9.4% | 104,527 at 150 digits (9.2%)
200 | 123,668 | 5.8% | 0.58 | 146,514 | 6.9% | 160,357 at 200 digits (7.5%)

## B6. lag (digits / ideal digits) along the 7,000-unit frontier
60 digits: Q = 44,264, ideal digits 35, lag 1.70
100 digits: Q = 80,630, ideal digits 46, lag 2.18
150 digits: Q = 126,488, ideal digits 56, lag 2.68
200 digits: Q = 174,247, ideal digits 64, lag 3.11
250 digits: Q = 219,534, ideal digits 71, lag 3.50
300 digits: Q = 266,118, ideal digits 78, lag 3.86
