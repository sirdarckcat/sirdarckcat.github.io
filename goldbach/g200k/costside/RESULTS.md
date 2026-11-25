# The cost side at 200 digits, from first principles (research's bottom-up round, 25 Nov)

Research's 1,502-row cover (`../screens/q200000_m89.txt`, 89 moduli, Q = 200,000, N < 10^200), one window of 2^22 members
(4,194,304) in the middle of its k range, sieve200 on this CPU.  G4 costs are research's (GPU session, 25 Nov): Fermat 40.6 ns a
test, sieve 3.06 ns a member (2^24 windows: tile 20.9 ms, generate 22.2 ms of which pass A 13.8 ms for 7.1e9 visits, the rest
8.2 ms), 14.0 tests a kept member.  Hit mass of a member: (1 - p8)^a8, p8 = 0.0716.

## 1. The member score: its floor, and a cheaper organisation

Floor of today's design (exact alive counts to 1e8 for every member, 2^24 windows): ~1,220 marks a member from the primes below
1e6 in shared memory (12 ATOMS.AND a clock an SM: 0.23 ns), ~430 from the primes in (1e6, 1e8) through DRAM bins (8 B a mark
written and read, 4.8 B packed, at ~1.5 TB/s: 1.4-2.3 ns), 423 pass-A visits (0.15-0.2 ns at the integer pipes' rate; measured
1.94 ps a visit = 0.82 ns).  So ~1.8-2.7 ns against today's 2.65: the bins' DRAM traffic is this design's floor.

What breaks it: the count has to be exact only near the cut (`counts.py`, `curves.py`):

| score (selection per 32,768-block) | captured hit mass, keep 0.5% | 1.5% | tests a kept member |
|---|---|---|---|
| exact to 1e8 (today) | 0.1046 | 0.1987 | 14.0 |
| exact to 1e7 | 0.0814 | 0.1624 | 16.0 |
| exact to 1e6 | 0.0607 | 0.1267 | 18.6 |
| exact to 1e6 minus the rows hit by (1e6, 1e8) without dedup | 0.0729 | 0.1486 | 18.6 |
| two-stage: top 10% by the 1e6 count, then exact to 1e8 | 0.1028 | 0.1906 | 14.0 |
| two-stage: top 20% by the 1e6 count, then exact to 1e8 | 0.1041 | 0.1966 | 14.0 |

(corr(a6, a8) = 0.78, corr(a7, a8) = 0.90.)  The large-prime marks are needed for the top 10-20% only: binned for those, the bins
shrink 5-10x.  Cost per unit of captured hit mass (`cost.py`, keep re-optimised each time):

| | sieve ns a member | best keep | ns a unit | nats against today's best |
|---|---|---|---|---|
| today, keep 1.5% | 3.06 | (1.5%) | 58.2 | -0.06 |
| today, keep re-optimised | 3.06 | 0.75% | 54.8 | 0 |
| two-stage, top 10-20% (bins of non-candidates dropped; the matrix round trip adds ~4 ms a window) | 2.0-2.3 | 0.5% | 47.2-49.6 | 0.10-0.15 |
| the same with pass A at ~0.5 ps a visit (it runs latency-bound at 1.94) | 1.5-1.6 | 0.5% | 41.8-43.6 | 0.23-0.27 |

The keep of 1.5% is worth re-checking with the fleet's full costs: on these curves 0.75% is 6% cheaper a unit (if nothing else
scales with the keep).

## 2. Sharing between sibling covers

Consecutive covers of the q200000 dump: row sets with a median Jaccard of 0.983, one modulus with another class (median and min).
Start positions of a sibling differ by one shift a prime, but applying it still touches every (prime, row) pair (a subtract and a
compare, against ~5 operations of Shoup's recomputation) and costs 7.1e9 stored positions a window: 28 GB each way, ~37 ms at
1.5 TB/s against pass A's 13.8 ms.  Skipping pairs needs per-prime row lists sorted by q M^-1 mod s (a window is then a cyclic
range query: ~0.10 R hits a member instead of 0.28 R visits for the primes above 2^24, pass A ~2.7x smaller): 34 GB of lists,
patched for each sibling (~25 rows in and out of each of 5.7M lists, ~3e9 updates).  Negative.

## 3. Short windows (`shortwin.py`)

Per prime the cheaper of R start positions and the lattice enumeration of the residues N0 + jM mod s below Q (W Q / s + log2 s
steps); operations a member for the primes above W:

| W | 2^15 | 2^17 | 2^19 | 2^21 | 2^24 |
|---|---|---|---|---|---|
| B = 1e8 | 55,387 (per-row alone 263,929) | 33,494 | 15,665 | 4,015 | 419 |
| B = 1e7 | 24,719 | 7,475 | 1,780 | 365 | 0 |

The enumeration helps 4.8x at 2^15 but the residues below Q it lists are mostly not rows (R / Q = 0.75%), and its total Q ln(ln B /
ln s*) a member does not shrink with W.  At ~2 ps an operation: 31-110 ns a member at 1e8 for 2^19..2^15, 10-35x today's whole
sieve, against 0.23-0.46 nats for two more moduli: negative by about 2 nats.

## 4. The Fermat rounds' tail (`tail.py`)

run_pool simulated exactly (D = max(1, min(8, rem, 2^20 / active)) rows a member a launch, first PRPs geometric with p = 0.0715,
2,015,232 members of 423 rows): 52 launches, waste 3.1% (measured 3.1%).  With a launch costing max(T / 24.6M, 4 ms) + 2.2 ms of
gap, 1.265 s of kernels and 1.379 s of wall (the 23 Nov profile: 1.277 / 1.375): 20.4M counted tests/s, -17% against the
benchmark.  Carrying the unfinished members into the next pool (every launch 2^20 single-row tests): 27 launches, 23.4M (-5%, the
gaps): +15% Fermat throughput, 0.07-0.1 nats at the re-optimised keep.  On this model the tail and the waste are most of the 19%
between benchmark and production; the sieve's contention (x1.08 beside it) the rest.  t_min is fitted (4 ms): timing launches of
8, 1K, 10K and 100K tests would pin it.

## 5. Which survivor is the prime one (`survivors_labelled.py 300`, `predict.py`)

137,209 survivors (the 300 first kept members of the window, every row tested), 9,783 PRPs (7.13%).  Chi-square of the PRP rate
against: position among the member's rows (p = 0.30; the first 14 against the rest p = 0.08), q mod m for m <= 30 (all p > 0.14),
(N - q) mod m (p > 0.2; mod 64 p = 0.036 among ~25 tests), the member's alive count (p = 0.96), the gap to the previous alive row
(p = 0.35, 0.86), the previous row's verdict (p = 0.89); the PRPs a member have 0.935 times the binomial variance (no member is
richer in primes than another).  Nothing predicts; a factor two in tests a kept member needs p' doubled, i.e. a sieve to ~10^16.

## Total

About 0.3-0.45 nats on the cost side: keep 0.06, two-stage score 0.10-0.15, pass A at its integer floor 0.12, carried rounds
0.07-0.1.  Whole nats would need the tests to get cheaper or fewer, and neither the kernel (at the IMAD floor) nor any predictor
(above) offers that.
