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

## Appendix: the two-stage sieve as a GPU design (for the GPU session, if the lead wants it built)

**Withdrawn (25 Nov 18:42Z), before it was built: a net loss.**  Step 4's filter is one random lookup into the 2 MB candidate bitmap per
large-prime mark, 7.1e9 a 2^24 window; random 4-byte accesses into an L2-resident buffer run at 136 G/s on the RTX PRO 6000 (the GPU
session's bench_pipes, DEEPSIEVE.md): 52 ms a window (18 ms even at 400 G/s), against at most ~17 ms saved (85% of pass B's flush, 8.2
ms, and of the tile kernel's bin reads, ~12 ms).  The estimate below priced the lookup at zero.  The filter cannot sit where the marks are
made (a generate CTA's marks fall anywhere in the window: the bitmap does not fit its shared memory) and saves nothing where they are read
(the reads are the cost).  The selection numbers of section 1 stand; only this way of using them fails.

What it removes: the binning of the large-prime marks (and their apply) for the members that cannot make the cut.  What it does NOT
remove: pass A's 7.1e9 start-position visits a 2^24 window - a visit is what computes where a (prime, row) pair hits, and only then is
it known whether the hit lands on a candidate; skipping visits would mean candidate-major work (N_k mod s and a row lookup for every
candidate and prime: ~9.5e12 operations a window), 1,300x more.

1. Tile kernel with the primes below 10^6 only (today's small-prime marks): the bit matrix of the window (1,502 rows x 2^24 bits =
   3.1 GB, written to DRAM) and the counts a6 of every member.
2. Select the candidates: the emptiest 10-20% of each 32,768-block by a6 (s200_select's counting sort); a candidate bitmap of the window
   (2^24 bits = 2 MB, L2-resident) and a candidate index.
3. Pass A for the primes in (10^6, 10^8), unchanged (13.8 ms a 2^24 window).
4. Pass B with a filter: a mark is binned only if its member's bit is set in the candidate bitmap (one L2 read a mark); 10-20% of the
   marks reach the bins (pass B 8.4 ms -> ~1-2 ms, the bin apply ~12 ms -> ~1-2.5 ms).
5. Apply the bins to the candidates' words of the matrix (re-read from DRAM, ~4 ms a window at 1.5 TB/s), recount a8 for the candidates.
6. The final keep (0.5% of the window) by a8 among the candidates; their survivor rows as today.

Estimated: 2.0-2.3 ns a member against 3.06 (with today's pass A), 1.5-1.6 ns if pass A reaches ~0.5 ps a visit; at the re-optimised
keep of 0.5%: 0.10-0.15 nats, 0.23-0.27 nats.  Selection measured on this CPU (section 1): 96% (top 10%) to 99% (top 20%) of the
captured hit mass of exact counts for every member, at the same 14.0 tests a kept member.  The filter check in pass B and the matrix
round trip are the two costs not in today's pipeline; both are estimates.

## Predictions for the approved items in the G4 pipeline (`pipeline.py`; the two-stage rows are void, see the appendix; carry-over revised to 2-6%, see the end)

The GPU session's a2 pipeline (depth 2): while both run, Fermat at 0.735 and the sieve at 0.43 of their solo speed; a batch of 2^26 members at keep 1.5%
needs 1.318 s of Fermat alone and 0.434 s of sieve.  The Fermat time scales with the keep except the tail (0.175 s a pool at t_min = 4 ms, 0.09 s at
t_min = 0; carry-over removes it); the two-stage sieve takes 2.0-2.3 / 3.06 of the sieve time; hits a batch from the measured capture curves.
Expected hits a second against today (t_min 4 ms / t_min 0):

| | keep 1.5% | 0.75% | 0.5% | 0.3% |
|---|---|---|---|---|
| rounds as now, one-stage | 1.000 / 1.000 | 1.049 / 1.085 | 0.964 / 1.016 | 0.818 / 0.881 |
| rounds as now, two-stage top 10% | 1.019 / 1.019 | 1.128 / 1.182 | 1.123 / 1.217 | 1.013 / 1.111 |
| carry-over, one-stage | 1.124 / 1.060 | 1.212 / 1.169 | 1.144 / 1.110 | 1.000 / 0.979 |
| carry-over, two-stage top 20% | 1.167 / 1.098 | 1.369 / 1.297 | 1.337 / 1.291 | 1.211 / 1.180 |
| carry-over, two-stage top 10% | 1.154 / 1.084 | 1.392 / 1.317 | 1.417 / 1.365 | 1.311 / 1.275 |

The three together: x1.37-1.42 (0.31-0.35 nats).  The two-stage sieve alone at keep 1.5% is worth only 2-3% (the sieve is hidden behind the Fermat rounds); it pays
once the keep is lowered and the batch turns sieve-bound.

## Carry-over as built (`carry_sim.py`; `../../fermat661/cuda/search_gpu5_carry.patch`, `fround_carry.patch`)

A half-pool of production (503,808 kept members a batch, target 2^18, dmax 8, p = 0.0714, 423 rows; fround's round rule simulated member by member, steady state
over 14 pools):

| stop (active members) | rounds a pool | tests computed | waste | launches < target / 2 | smallest launch | carried: members / rows | slice lines deferred (batches) |
|---|---|---|---|---|---|---|---|
| none (production) | 45.2 | 7.278M | 3.04% | 18.2 | 9 | 0 | 0 |
| 32,768 (target / 8) | 26.0 | 7.172M | 1.61% | 0 | 139,515 | 25,431 / 9.7M | 1-4 (mean 3.2) |
| 65,536 | 24.6 | 7.109M | 0.68% | 0 | 137,639 | 58,397 / 22.7M | 1-6 (3.9) |
| 131,072 (simulated; the default target / 2 + 1 = 131,073 keeps D = 1 in every round) | 22.0 | 7.058M | 0.00% | 0 | 132,265 | 122,756 / 48.6M | 1-8 (4.7) |
| 262,144 (target) | 15.0 | 7.051M | 0.00% | 0 | 265,948 | 246,936 / 98.9M | 1-9 (5.0) |

(The production row is the GPU session's own model: 44 rounds, 7.28M tests, 17 rounds under half the target.)  A slice's line waits for its deepest member: the
deepest of ~250,000 needs ~170 tests, ~22 a pool; a design hit needs all its rows (~19 pools).  A deferral bounded to one batch would need a per-member D for the
carried members (a change of fr_plan) and gives back most of the waste; not built.

The driver (`--carry-over 1`, campaign mode with fused rounds): each part of run_pool_split carries its undecided members (k, the rows they have left as rows of
their own slice, the slice, the tests so far) into the same part of the next pool; the tester of a batch covers every open slice (CarryTester: the new slices
checked and made by MultiTester itself, the older ones' tables cached).  A slice's line, with its SUCCESS / NEARMISS / discrepancy lines in run_batch's order, is
printed when every member is decided; its counted tests and expected hits go into that batch's stats line (a restart, which redoes the unprinted slices, never
counts them twice); found records are written when verified, each N once.  CPU proof (`../../sieve200/cuda/test_carry_campaign_fake.py`, whole campaigns on fake
windows with the real driver code and fround's kernels compiled by g++): every slice line and its found lines identical to production's code, found.jsonl the same
records, counted tests equal, with two parts, one part and a lower stop, the pipeline with slices of two windows and a mid-batch flush, and a kill after a batch's
found records followed by a restart; over 48 batches waste 2.75% -> 0.06% and rounds 3,266 -> 2,069.

What it can gain on a G4: the waste (3.0% of the Fermat tests, ~2% of a batch) for certain; the 18 small rounds a half-pool only where the sieve does not already
fill them.  The GPU session's control-stream run (gap 0.10 s a half-pool shorter, batch unchanged) says the gaps between rounds are hidden already; the expected
batch time is therefore 2-6% shorter, not the 6-12% of the pipeline model above.

At keep 0.75% (item 2: 251,904 kept members a half-pool a batch, `CARRY_NEW=251904 python3 carry_sim.py 65537 131073`) the rounds as now are worse
and carry-over is worth more: without it 34.9 rounds a pool, waste 5.72%, 17.9 launches under target / 2; with the default stop 15.0 rounds, waste
0.00%, no small launch (smallest 132,984), slice lines deferred 1-9 batches (mean 5.0).  The two items are complements: carry-over removes 3.0% of
the tests at 1.5% and 5.7% at 0.75%.
