# Skeptic review of the "families" audit (KEY=families_skeptic)

Scripts and outputs: audit/run/families_skeptic/ (verify1.py, verify2.py, verify3.py; own code, direct lookups, no FFT).
Primary sources read: origin/ccr-d4a17dd0-7uu03r goldbach/sublinear/README.md (lines 376-500, 612-740),
ideal_tilt_213070.txt, fscan/cover/starts/q213070_m89.txt, fscan/cover/brainstorm/verdicts_on_*_ideas.txt,
crystals.txt, sieve_depth.txt; origin/ccr-2ce9e63a-hn0fuw goldbach/phd/wp9/wp9_closure_theorem.md section 13b.

## Verdict
The auditor's conclusion (no loophole in the families lens) is warranted. Its one positive lever
(oversized covers by list merging, "0 +- 0.5 net") does not survive: the gain per extra prime is overstated by
60%, the "sumset" rescue does not amortise the sieve, and the team had already rejected the idea for exactly
that reason. Nothing in this lens is worth more than a few tenths of a nat.

## Numbers reproduced
- 19,050 rows; 89 odd primes; sum ln = 442.946 (443.639 with the 2, 10^192.670); slack 16.878 nats = 2.138e7 members.
- Cover file identical to the auditor's copy; first cover 1,609; 98 sampled lines all correct; 10 at 1,609, 1,259 at 1,610.
- Boost 11.0448, p 0.02398, E 39.06; E - 30.75 = 8.31 (README sampler: 8.49). The brief's 7.7 does not follow from its own numbers.
- Random nonzero classes 2,276 +- 24; product formula 2,278.0.
- Common integer, direct scan: 2,129 at t = 211,664 (mean 3,527.0); 1,975 at 352,448; 1,994 at -121,522. Odd t: 2,416.
- Hybrid top-20 re-choice 1,954; block z = 199: 2,246 survivors, 1,871 at t = -260,260.
- Give back 1 / 4 / 8 / 24 primes: 1,621 / 1,651 / 1,694 / 1,889 rows, +0.21 / +0.67 / +1.32 / +4.06 nats.
- Scope: 15 extra primes at 10^241: 1,483 rows, p 0.02049, E 30.70.
- Exponential family a = 2, L = 660: 22 primes, 108.3 nats (49.5 on cover primes) against 457.5.
- Team table: S = 79.31 at <k> = 1,646.3, 41.61 at 1,626.3, 12.64 at 1,615.6.

## Numbers that do not hold
1. Extra cover primes. The auditor multiplies rows killed by -ln(1-p) and does not charge the larger boost
   (every surviving row is now known coprime to the new prime, so p rises by s/(s-1)). Correct change in E:
   | primes added | rows | auditor | boost charged |
   |---|---|---|---|
   | 1 | 1,600 | +0.22 | +0.13 |
   | 6 | 1,556 | +1.29 | +0.81 |
   | 9 | 1,530 | +1.89 | +1.23 |
   | 12 | 1,506 | +2.48 | +1.62 |
   | 24 | 1,416 | +4.64 | +3.12 |
   0.134 to 0.137 nats a prime, 0.022 a nat of modulus (not 0.218 and 0.035). Same thing as (W - mu) rows instead of
   W: 9 - 3.45 = 5.55 rows. Coordinate descent on all 90 to 113 primes after the greedy step changes nothing.
   A jointly optimised extra prime could reach about 0.18 (cover primes 373..463 hold 11.3 unique rows on average;
   463 holds 12, hence the 0.21 in the give-back table, where the auditor did charge the boost).
   The team's own figure is 0.17 a modulus ("two lists give 3 moduli (+0.5 gross)").
2. Entropy charge. Read against 1,609, but today's design already runs at S ~ 14 nats, about 1,616 rows.
   Relative cost of 40 to 51 nats of entropy: 10 to 14 rows, 0.25 to 0.35 nats (auditor: 0.4 against 40 only; a
   budget of e^30.75 members at e^-20 members a vector needs 51 nats in all).
   Corrected gross for two lists: +0.81 - 0.3 = +0.5 (auditor's table: +0.9). Four lists: +1.23 - 0.73 = +0.5.
   Eight lists: negative. This matches the Lean session's "cap about 0.5" and the team's "net 0.2 to 0.4".
3. "The team does not visibly charge the lost sieve": false. verdicts_on_lean_ideas.txt 47/48: "NO: your own
   count, 0.2 to 0.4 net at lists of 5e8, and each solution is a single member that has lost the amortised sieve";
   46: "with one member a vector there is no progression to sieve"; 29/56: "+0.1 for one prime, then negative".
4. Sumset rescue. With modulus e^20 over the line only e^-20 of the pairs (A_i, B_j) are members (sum mod M' below
   10^200). Marks generated on the sumset land on pairs; a bucket join by residue costs r operations per useful mark;
   the direct way costs pi(z) residues per member (5.76e6 at depth 10^8 against about 2,200 operations today).
   No amortisation. The 4.4-nat penalty the auditor quotes for single members is asserted, not derived; with
   trial division to about 2e4 at today's per-member cost I get a loss of 1 to 2 nats from the shallower sieve.
   Either figure exceeds the +0.5 gross.
5. Scope price. 10^241 buys the number 213,070, which is 6.9% of that ceiling, not 10%. More digits make the
   percentage harder, not easier. Fermat cost at 241 digits (x1.45 to x1.75 on the test share, 0.3 to 0.5 nats) is not
   charged: 10^247 to 10^250 is the honest figure.
6. Two-parameter lattice "under 0.1 nat": 440 of 2,200 operations is 0.22 nats by the auditor's own count; in time
   the setup is about 5% (roots at 8e11 a second, 12 ms against 235 ms a cover). Immaterial.
7. smooth_count.py prints two estimates for y = 463: e^128.2 (saddle point) and e^94.5 (lattice formula); only the
   first is reported. Kill unaffected (sparsity 332 or 366 nats).
8. Notes say "first line of the file"; cover_checks.py uses the lexicographically first 1,609 cover. On the first
   line my single-site histogram is {0: 3, 1: 23, 2: 103, 3: 282} against {0: 2, 1: 34, 2: 91, 3: 287}. Same size.

## What the auditor did not examine in its lens
- Unions across class vectors. The pigeonhole fact bounds one class vector only. S-unit and similar families are
  spread over many vectors; what kills them is equidistribution plus the sparsity price, which was assumed, not measured.
- Common algebraic number (N = a root of f modulo each cover prime). Dead on paper: the rows left follow the Buchstab
  function at u = deg(f) * ln Q / ln 463, whose minimum 1/2 is at u = 2, the rational case already measured
  (0.87 to 0.93 of random against 0.706 for the optimised cover). Team's crystals alpha/beta: 2,156 at best.
- Whether 1,609 is the floor on 89 primes. Every family tested is worse than tempering; none tests the other
  direction. A cover 5% better would be worth 1.9 nats. Evidence is the team's sampler and its exact miniature.
- The slack-against-depth trade (90 primes inside the line with progressions of 4.6e4): team says +0.1.
- Scope in the direction the user's metric rewards (fewer digits).
