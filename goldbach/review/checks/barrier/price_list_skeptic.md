# price_list_skeptic: check of the price-list audit (25 Nov 2026)

Scripts: /tmp/claude-0/-home-user-sirdarckcat-github-io/df2f42b3-a989-5e01-80a4-d6d0ee0e6589/scratchpad/audit/run/price_list_skeptic/ (chk1.py, chk2.py)

## Verdict
The auditor's arithmetic holds and its conclusion is warranted: no pricing loophole. Three corrections:
1. 10% at 200 digits is e^7.8 to e^8.1 (x2,400 to x3,400), not a point x2,340. x2,340 is the low edge.
2. None of the three "loopholes" is a gain at 200 digits on the user's terms. Budget slack is bookkeeping already in
   the team's 175,000-176,000 forecast. The scope exit is worth 0 nats at 200 digits. Cheaper compute is 0.25-1.0 nats
   per dollar and the user ruled out leaving Colab (23 Nov 09:40: "see how far we can get with the current colab resources").
3. The auditor's explanation of e^30.75 is a back-calculation. Its real origin: 9 days x 29M members/s on 23 Nov
   (ln = 30.747; brainstorm/README.md "What 10% takes"). Stale since the engine went to 52M/s.

## Recomputed (independent, chk1.py / chk2.py)
- p = 2 prod_{3..463} s/(s-1) / ln 10^200 = 0.0239834; -ln(1-p) = 0.0242757; 89 moduli, 2*prod = 10^192.67, 10^7.33 members a cover.
- E: 1,248 rows 30.41; 1,250 rows 30.46; 1,609 rows 39.18; 1,623 rows 39.52 (all with +0.117). Matches auditor.
- ceiling(10^200) = 2,130,704; 10% = 213,070; ln^2 = 212,076. Matches.
- Budget: 0.29 hits/day at 37.12 units/h = 3.255e-4 hits a unit (37.12 = 3 RTX x 10.05 + 3 L4 x 1.94 + T4 1.15, exact).
  7,000 units = 2.28 design hits = e^31.22 (fleet's logged rate e^-30.40 per full-weight member: 0.1318 / 2111.6e9) to
  e^31.28 (auditor's E = 30.46). With the 1,800-unit mark held back: 5,200 units = e^30.93 to e^30.98.
  8 days x 52M/s (design_menu.txt) = e^31.21. 9 days x 29M/s = e^30.75.
- Units left: day-one report says 7,967.7 CU at 04:05Z on 24 Nov at 37.12/h, 5 cards (603/day) since 22:42Z -> about 6,950 now. OK.
- Slope: (39.18 - 30.41) / 43.07 = 0.204 nats per 1,000 in g; 4.35 nats a percentage point. README: "a factor e moves 0.2-0.3 points". OK.
- Recursion: auditor's fastfloor.py rerun; team's cp.floor(463, 200000) = 1449.33 / 1474.46; cover_dual.txt says 1449 / 1474, E 35.36. OK.
- Table D sample (closeness.py from the lead branch, identical to auditor's copy): 150 digits 9.21% / 0.877; 63 digits 18.33% / 1.444;
  200 digits 7.53% / 0.756; 347 digits 3.08% / 0.339. All match.
- Table B4 against closeness_cost.txt: 50% at 60 digits 57.1 (auditor 58.7), at 100 digits 99.8 (101.0), at 200 digits 209.2 on 88 moduli (212.0 on 89). OK.
- D2 spot check: 160 digits, e^32.1 x 0.438 x 60 ns / 332 RTX-s a unit = 6,850 units (auditor 6,940). 150 digits 10%: 184 (186). OK.
- Table C: cover_dual.txt E at 220 / 240 digits 31.1 / 27.6 uncorrected; +3% rows and (230/200)^3 test cost -> about 230 digits. OK.
- Ideal-search column: README table has 343,000 (16.1%) at depth 10^8 on e^30.75; 500,000 costs 56.8; linear extension to 532,676 is 62. OK.

## The 0.3-nat spread in the 10% price
- design_menu.txt (team): P(g >= 213,070) = 2.9e-4 in 8 days at 52M/s with the 213,070 design -> x3,450 on e^31.21.
- Auditor: x2,340 on e^31.28 (x2,500 on e^31.21).
- Cause: design_menu.py slows the 1,610-row design by 1/(0.5 + 0.5 rows/1250) = 0.874 and keeps the hit share fixed.
  But the selection sharpens with rows: with survivors Binomial(k, ln 463 / ln 10^8), the emptiest 1.5% hold 17.4% of the
  hit mass at 1,250 rows (fleet measured 16.8%) and 22.0% at 1,609. Net cost per full-weight member x0.90, not x1.14.
  So the auditor is right and the team's own menu understates the 213,070 line by about 0.24 nats (x1.27).
- Against that: supply. 10% needs about 3e10 covers; the README's own z = 463 line gives e^39.31 (1,620 effective rows),
  +0.13 nats on 39.18. And the fleet's fitted rate exp(-1.0275 E^ + 0.33) has a 1.5% steeper slope than (1-p)^k: +0.14 nats over 359 rows.
- Range: 7.8 to 8.1 nats. "One expected success" is a 63% chance; 90% needs another +0.83 nats.

## Hit model validation (auditor did not cite it)
TALLY.md: all 200-digit covers, expected 10.31 design hits, found 9; near-misses 2.21 expected, 2 found. All at E <= 26.2.
Prices above E = 31 extrapolate 9+ nats past the validated range: a 1% error in nats per row is 0.4 nats at 10%, 2 nats at 50%.
The reviewer's own note (OUTSIDE_REVIEW section 7): fixed-gap runs at 300-2,196 digits have 4 design hits against about 12 expected.
If real (1.1 nats), table C is about 5 digits optimistic. Not examined by the auditor.

## Loopholes
1. Budget slack: reproduced, 0.18-0.53 nats against e^30.75. Zero against the team's current forecast. Bookkeeping.
2. Scope exit: prices reproduce; the reviewer's 100-digit demo (g = 47,881, 10.3%, 407 rows found against 413 modelled,
   18 CPU-minutes) confirms one point. Worth 0 nats at 200 digits; the user's words are "on 200 digits" and "within N<1e200".
   Kernels exist only at 200 digits. Cost model has one calibration point.
3. Cheaper compute: web check 25 Nov: RTX 5090 median on-demand $0.72-0.78/h (rising 14% in 90 days), cheapest interruptible $0.25-0.50/h,
   against about $1.00/h for the Colab RTX PRO 6000 (10.05 units at $0.0999; the Colab price is confirmed only by 2022 sources).
   So 0.25-0.33 nats at the median, up to 0.7-1.4 at the cheapest spot, if a 5090 matches the kernel-28 rate (unmeasured).
   Auditor's 0.5-1.1 is high at the low end. Excluded by the user on 23 Nov.

## Not examined by the auditor
- The user's recorded constraints, which pre-empt exits 1-3.
- Per-unit productivity by card: RTX 3.45e-4 hits a unit, L4 2.2e-4, T4 1.8e-4 (day-one figures). RTX-only spending of the
  remaining units is +9% (0.09 nats, about +450 in g) at the cost of calendar time. The auditor quotes the fleet README's
  older "L4 0.57M, RTX 0.54M per unit-hour", which predates the deep sieve on the RTX.
- The exchange rate applied to the team's open engineering list and to partial mathematics (1 nat = x2.72 = +4,900 in g = +0.23 points;
  depth-1,000 ordering 3.5 nats = x33).
- Probability rather than expectation; calendar (5 of 7 cards, Colab's per-account limit); the 1,800-unit reserve.
- Optimal modulus count by size (fixed at ">= 2^24 members" everywhere).
