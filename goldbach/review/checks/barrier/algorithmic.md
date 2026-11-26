# Audit, lens = algorithms for (P')

Verdict: the barrier holds in this lens. No loophole found; three candidate mechanisms were priced on the real
1,609-row cover (first cover of `goldbach/fscan/cover/starts/q213070_m89.txt`, research branch) and all are zero or negative.
Scripts and raw output: `audit/run/algorithmic/` (part1.py, part2.py, tiltmc.py, diag.py, lsh.py, tilt_*.txt, diag.txt).

## Reproduced from the team's documents
- 19,050 odd primes below 213,070; the cover leaves 1,609; theta(cover) = 442.95 nats of 460.52 (16.9 left after the factor 2).
- p_z = 0.0240, 0.0268, 0.0295, 0.0330, 0.0383 at z = 463, 1,000, 2,000, 5,000, 20,000.
- Members of the cover: 1,438.2 +- 11.0 rows at depth 1,000, 1,170.0 +- 17.5 at 5,000, 1,008.6 +- 17 at 20,000 (README: 1,439 +- 11, 1,170 +- 17, 1,007 +- 18).
- Dense-list join exponent on real lists (best 20-30% of classes): rho = 0.82-0.90 (README: 0.88).
- Coppersmith/GSS/Koetter-Vardy: with lists of a fraction delta of the classes the Johnson condition needs
  agreement > sqrt(ln X * sum delta*s*ln s) = 44,000 nats at z = 5,000, delta = 1/3, against 4,900 nats in total. Dead by a factor 9 even at full agreement.

## Per-prime numbers (real rows)
s: mu, W, variance, pin rows/nat (W-mu)/ln s, list_gain bound (W-mu)/ln(W/mu), tilt rows/nat at KL 0.1 / 1 / 3
- 467: 3.45, 9, 2.77, 0.90, 5.79, 7.65 / 2.51 / 1.43
- 997: 1.61, 5, 1.33, 0.49, 2.99, 5.32 / 1.74 / 0.97
- 2003: 0.80, 5, 0.69, 0.55, 2.30, 3.95 / 1.38 / 0.86
- 4999: 0.32, 3, 0.29, 0.31, 1.20, 2.66 / 0.97 / 0.61
Counts are sub-Poisson (variance/mu about 0.83).

## Rows purchasable with C nats of beyond-line constraint (members of the best cover)
| C | pins on best classes (first order) | uniform lists, Lagrangian (first order) | list_gain bound | soft selection, exact rows left, z=1,000 | z=5,000 | z=20,000 |
|---|---|---|---|---|---|---|
| 20 | 22 | 41 | 116 | 73 | 107 | 119 |
| 40 | 41 | 71 | 228 | 105 | 153 | 168 |
| 64 | 63 | 104 | 352 | 135 | 195 | 213 |
| 100 | 92 | 148 | 533 | 170 | 245 | 266 |
Luck bought by soft selection (rows * -ln(1-p_z)): z=5,000: 3.6, 5.1, 6.5, 8.2 nats; z=20,000: 4.6, 6.6, 8.3, 10.4; z=1,000: 2.0, 2.9, 3.7, 4.6.
Soft selection = keep the best e^-C fraction by total score (Gibbs tilt; C = KL by thermodynamic integration of a heat-bath Monte Carlo).

To buy 7.7 nats from members of the best cover: 263 nats at depth 1,000, 89 at 5,000, 55 at 20,000, about 18 at 10^8 (binomial estimate).
(P') itself (1,320 rows at depth 1,000) is 50 nats of soft selection among members of the best cover.

## Slack in the chain
1. rows-per-nat bound. `list_gain_le` is a statement about uniform lists (Finset). For C >= 20 it is loose by 1.1x to 2.2x
   (real requirement harsher). For C < 10 soft selection exceeds it (19 rows/nat at C = 1.5, 47 at C = 0.25, depth 5,000;
   7.65 rows/nat on the single prime 467 at KL 0.1 against the bound 5.79). That region is what the fleet's 3% rule
   already collects by enumeration; net of enumeration cost the gain is positive only for C below about 0.3 nats. No loophole.
2. "memory e^m extends the line by m nats" is generous. Pins beyond the line have to be paid for in list entropy on the cover:
   cover side loses 1.34 rows/nat when a prime >= 300 is unpinned and 1.46-1.62 rows per nat of top-k list entropy;
   beyond-line pins buy 0.9-1.1 rows/nat. At the 2:1 exchange of a two-list or four-list merge that is about -1 row per nat.
   Memory is not the binding constraint (Wagner 4-tree gives C = 2m, Schroeppel-Shamir the same with all solutions); the
   460.5-nat budget is.
3. Different primes never cost less than the sum: exact pins are CRT-additive, kills are a union (sub-additive), and the
   weights are Fourier-flat (prime rows are equidistributed mod s; only the Poisson noise remains).

## Mechanisms tested here
- Block-diagonal (separable) split: N = N_A + j1*b1 + j2*b2 with b1 = prod(A)*prod(B2), b2 = prod(A)*prod(B1). Residues on B1
  depend on j1 only, on B2 on j2 only, so soft selection costs J + J for J^2 members and the join exponent disappears.
  Budget: theta(A) + theta(B) + ln J <= 459.8. Measured (joint tilt = upper bound):
  A <= 421, 10 block primes to 479, selection <= 30 nats: 1,608 rows against 1,602 today at the same depth (6 worse; break-even needs 37 nats).
  A <= 397, 21 block primes to 523, selection <= 25 nats: 22 rows worse. A <= 349, 40 primes to 601, <= 14 nats: 75 rows worse.
- Dense-list join by bucketing: free filter (1 - rho)*m = 0.12-0.18 m, i.e. 3-4 nats, about 6 rows, 0.2 nats, before the list
  entropy is paid; hash operations against 11 ns sieve operations make it negative in practice.
- Pins on 467 and 479 inside X (91-prime covers): 5.5 and 5.6 rows, 0.14 nats each (README says about 0.2), 95 members per cover.

## What would have to exist
A near-linear-time "best pairs" algorithm for sum_s w_s(u_s + v_s) over two lists of e^23 to e^30 (bichromatic maximum
inner product, cosine about 0.01, dimension about 10^6, random-like data). Even a perfect one is worth about 3 to 3.5 nats
at depth 5,000 on product lists (selection C about 30 nats = 4.5 nats of luck, less 1.1 for the list entropy), under half of 7.7.
