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
- **About 2,000 digits** (629 moduli, odd primes up to 4,657): next, with a better cover than `hb_b1.txt` (2,829 rows).
