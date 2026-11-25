# T5: an even N with g(N) ≥ 1,000,000 in as few digits as possible (2,196 digits found; 2,000 next)

This task comes from the research session (25 November). g(N) is the least prime p with N − p prime. Every odd prime
q < Q = 1,000,003 is a row; the moduli are odd primes r, and each gets a nonzero class a_r. When N ≡ a_r (mod r) for every
modulus, every row q ≡ a_r (mod r) has r | N − q, so N − q is composite. The rows in no class are left to luck. If every such
N − q is composite too, then g(N) ≥ Q. The record held before this work is g = 1,157,341 at 2,480 digits.

## Pipeline

1. **Cover** (`cover.py`, `heatbath.c`, `heatbath_pt.c`).
   - Greedy in increasing order of the moduli, then 1-flip descent, then iterated local search (`cover.py`).
   - Then heat-bath annealing (`heatbath.c`). Every visit to a modulus samples its new class from all r − 1 classes with
     weight e^(−β·dk), using the gains of all classes from one pass over the uncovered rows. A sweep takes about 17 ms at
     Q = 10⁶.
   - `heatbath_pt.c` is the same move inside replica exchange.
   - ptcover's random-class proposals almost never reach the few good classes of a large modulus, so tempering with them
     (`ptcover_big`, MAXM 1024) does not move at this size.
2. **Members** (`members.py`). N0 comes from the Chinese remainder theorem (N0 ≡ a_r mod r for every r, and N0 even),
   with D = 2M and M the product of the moduli. The members are N0 + k·D.
3. **Sieve** (`sieve.c`). For each row left and each prime s in (X, B], the members with s | N_k − q are
   k ≡ (q − N0)·D⁻¹ (mod s). Pass 1 counts the surviving rows of every member; pass 2 lists them for the chosen members.
   It was checked against a direct count.
4. **Selection and tests** (`run_scan.py`, `test_members.py`). The members with the fewest survivors are taken, about
   3.3 sd below the mean. The spread of the survivor count is binomial: sd² = mean·(1 − ln X/ln B). Each member is tested
   with base-2 Fermat on N − q, in increasing order of survivors, until the first hit.
5. **Check** (`verify.py`). From N alone, every N − q for q < Q is shown composite, by a factor up to 10⁶ or a failed
   Fermat test. Then g = the least prime p ≥ Q with N − p a BPSW probable prime.

## Covers at Q = 1,000,003 (rows left)

| moduli (odd primes up to) | greedy | + descent | + local search | heat-bath, 3k sweeps | heat-bath, 20k more | research's estimate (revised) |
|---|---|---|---|---|---|---|
| 491 (3,527) | | 3,810 | | 3,611 | | 3,130 |
| 629 (4,657) | 3,112 | 3,091 | 3,028 | 2,864 | 2,829 | 2,440–2,460 |
| 683 (5,113) | | 2,852 | | 2,595 | 2,563 | 2,150–2,200 |

Four more anneals at 629 moduli (`heatbath2`, `anneal4657.sh`) all end between 2,825 and 2,839:
- the 5,113 recipe from greedy plus descent ends at 2,850 and 2,861 after 3k sweeps, then 2,838 and 2,839 after 20k more;
- 20k sweeps from the 5,113 cover restricted to the moduli up to 4,657 (2,860 rows at the start) end at 2,825 and 2,827.

`hb4657_rs1.txt` (2,825) is the cover of the 2,000-digit run.

## Is the 629-moduli cover near its floor?

**A two-sided test with `heatbath_pt2`.** The ladder had 81 values of β from 0 to 4 (step 0.05), 600 rounds with 300 of
burn-in, and two starts: `hb_b1` (2,829) and random classes.
- The mean k agrees at β = 0 (6,875.8 and 6,875.6, against 6,876.8 exact) and at β = 0.15.
- Above that, the random start stays higher: by 66 rows at β = 0.3, 131 at 0.6, 172 at 0.9, 214 at 1.5, 238 at 2.1, 256 at 2.7,
  250 at 3.0 and 232 at 3.6. The sd within a chain is 50 at the hot end and falls to 10.
- So at this size neither start reaches equilibrium above β ≈ 0.3 in 600 sweeps.
- The cause is the small and middle moduli. Their classes are frozen at any β where the large moduli still move, so each start
  keeps the arrangement it began with.

**The small moduli of a greedy cover are close to the best.**
- For the moduli 3 to 13, `hb_b1`'s classes leave 20,141 rows uncovered. Over all 5,760 combinations of nonzero classes, the
  minimum is 20,135, the mean 20,238 and the sd 28. Greedy is 3.4 sd below the mean: it picks up the bias in how primes fall into
  residue classes.
- The cover's lead over random classes keeps growing as moduli are added. Rows uncovered by the moduli up to y, for `hb_b1`
  against the expectation with random classes:

| y | 31 | 100 | 200 | 500 | 1,000 | 2,000 | 4,657 |
|---|---|---|---|---|---|---|---|
| `hb_b1` | 15,717 | 12,036 | 10,050 | 8,118 | 6,679 | 5,119 | 2,829 |
| random classes | 15,944 | 12,493 | 10,776 | 9,290 | 8,393 | 7,636 | 6,877 |

**The floor of the cover's basin, by thermodynamic integration** (`ti_floor.py`).
- In the cover-start ladder, −d⟨k⟩/dβ matches var(k) at every β, for example 185 against 192 at β = 3. So within its basin
  the ladder is in local equilibrium.
- The entropy of the covers is S(β) = ln Z(0) − ∫⟨k⟩dβ + β⟨k⟩, with ln Z(0) = Σ ln(r − 1) = 4,578.1 nats. This ladder gives
  S = 317 nats at ⟨k⟩ = 2,860 (β = 4).
- Below that point, every cover has dS/dk ≥ 4. So this basin's floor is at least 2,780, and about 2,785 if β(k) is extrapolated
  linearly. `hb4657_rs1` (2,825) is about 1.5% above it.
- A floor near 2,450 would need a separate, more ordered family of covers that these local moves do not reach.

Calibration at the research session's campaign point (89 moduli, Q = 170,000), in plain rows:
- greedy plus descent leaves 1,309, with no local search, against the best cover known there, 1,248 (+4.9%);
- the campaign's weighted measure (1,308.67 for the fleet's family) is a different quantity.

At 89 moduli and Q = 48,000:
- greedy plus descent leaves 258;
- the heat-bath reaches 229 and 233 with two seeds, the same as the research session's tempering (229) against its
  predicted floor of 217.

## Cost

A Fermat test takes 49 ms at 2,000 digits and 26 ms at 1,500 here, with the machine loaded. A hit needs about e^(p·rows)
members, with p = 2·∏ r/(r − 1)/ln N. The cut on the emptiest members gains about 2×.

## Runs

- **About 2,196 digits** (683 moduli, cover `hb5113_b1.txt`, 2,563 rows):
  - D has 2,189 digits.
  - Sieve: 2·10⁷ members against the primes in (5,113, 10⁹]. Survivors: mean 1,058.2, sd 24.8 (binomial), minimum 927.
  - The 10,000 members with S ≤ 977 (3.27 sd below the mean) were tested, lowest S first.
  - **Hit at the 3,615th member** (k = 8,179,130, S = 970): **N has 2,196 digits, and g(N) = 1,001,491 if N − 1,001,491 is prime**
    (it is a BPSW probable prime). Every N − q for an odd prime q < 1,001,491 is proved composite, so g(N) ≥ 1,001,491 holds
    regardless.
  - Cost: 501,670 Fermat tests, 9.1 CPU-hours; about 10.4 CPU-hours with the sieve and the cover.
  - Everything is in `record_2196digit/`: N, the cover, the check from N alone, and a certificate with one reason per row.
- **About 1,997 digits** (629 moduli, odd primes up to 4,657; cover `hb4657_rs1.txt`, 2,825 rows; tag `d1996`):
  - D has 1,990 digits.
  - The plan: sieve 4·10⁷ members against the primes in (4,657, 10⁹], then test the 15,000 emptiest members
    (`run/chain_d1996.sh`), stopping at the first hit.
  - The model predicts survivors with mean about 1,153 and sd 26, a cut at about 3.4 sd, about 2.2 hits expected within the 15,000,
    and about 8 CPU-hours of tests.
