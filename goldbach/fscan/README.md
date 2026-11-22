# fscan: score first, test in bulk

A second scanner for the low end of the threshold game (smallest N with
g(N) > 10,000). It searches the same space as `tscan/vscan.py`, the
progressions N = N0 + k·M with M = 2·3·…·43 and one progression per residue
vector on the 13 cover primes, but spends the work differently. On the same
progression and the same range it gives about 4.5 times as many expected
successes per core-second as `tscan`, and about 6 times on the residual
classes it is run on. It needs AVX2. With AVX-512 BW and IFMA (Ice Lake or
later, Zen 4 or later) it uses them and is about twice as fast as without.

| file | what it is |
|---|---|
| `fscan.c` | the scanner: enumerates the residue vectors and scans each one |
| `fermat52.h` | base-2 Fermat test, 24 numbers at a time, 52-bit limbs (AVX-512 IFMA) |
| `fermat26.h` | the same test, 12 numbers at a time, 26-bit limbs (AVX2), used when the CPU has no IFMA |
| `test_fermat.c`, `test_fermat.py` | check of `fermat52.h` against Python on 150,000 numbers of 41 to 100 bits |
| `check_small.py` | end-to-end check against brute force on a small threshold |
| `check.py` | recomputes g(N) from N alone with gmpy2 |
| `enumv.c` | counts the residue vectors by residual size |
| `tune.py` | expected successes per core-second for a grid of thresholds |
| `run_classes.sh` | resumable production driver, one pass per residual class |

## Why a different allocation pays

`tscan` sieves every member of a progression to 131,072 (about 400 cycles a
member) and then Fermat-tests the 1.3% with the fewest rows left, with a
scalar test of about 2,500 cycles. That balance is right when a test is that
expensive. With 52-bit multiply-add instructions 24 tests run side by side
at 119 cycles each (about 20 times cheaper), and the best balance moves to
almost no sieving and many more tests:

1. **Score.** For a small prime s the number of residual rows q with
   s | N − q depends only on k mod s. So it is a periodic byte table, and the
   score of 64 consecutive members is one unaligned 64-byte add per prime.
   With the 62 primes from 47 to 383 this costs 1.35 cycles a member. The
   score counts a row twice when two primes divide it, which is why it is
   only a filter (its correlation with the exact count is 0.87).
2. **Exact rows.** For the members whose score reaches the threshold (0.8%),
   the rows that no prime ≤ 383 kills are computed exactly from one 256-bit
   mask per prime: about 90 cycles. Members with more than Ta rows left are
   dropped.
3. **Fermat.** The rows of the remaining members (0.3%) are tested one row
   per member per round, 24 members at a time, and a member is dropped at
   its first probable prime (5.2 tests on average, since a row that survives
   the primes ≤ 383 is prime with probability 0.19).

A member costs 4 to 6 cycles in total instead of about 420. The price is the
share: the tested members hold only 5 to 7% of a progression's expected
successes, against 74% for `tscan`. That is made up for with more
progressions: there are 154,098 vectors with 193 residual primes, 467,071
with 194, 1,346,301 with 195 and 3,714,537 with 196 (`enumv.c`; it
reproduces the 18,208 vectors up to 191 of `variants.py` exactly), and the
residue vectors are enumerated inside the scanner, so nothing is written to
disk per progression.

## Measured (4 cores, Sapphire Rapids 2.3 GHz, Q = 10,007)

Same progression (191 residual primes), same members (k from 2^26 to 2^27,
N from 0.9 to 1.8·10^24):

| | cycles per member | share of the expected successes | expected successes per core-second |
|---|---|---|---|
| `tscan`, B = 131,072, T = 50 | 418 | 74% | 1.5·10^-5 |
| `fscan`, L = 383, θ = 100, Ta = 113 | 5.2 | 4.1% | 7·10^-5 |

Both figures in the last column are corrected to one model (see the next
section). The ratio is 4.5.

For a search with a fixed size limit the gain is smaller than that, because
the small share forces `fscan` onto more and therefore slightly worse
vectors (each residual class is worth about 13% less per member than the one
before). For one expected success below 10^23 `tscan` needs the classes up
to 193 or 194, about 100 to 130 core-hours here; `fscan` needs the classes
up to 196 or 197, about 30 to 35 core-hours. That is a factor of 3 to 4 in
compute, or close to one digit of N at the measured cost of 3.8 per digit.

The thresholds sit on a flat optimum. On the class with 194 residual primes
below 10^23, every setting between (L, θ, Ta) = (293, 91, 118), (383, 99,
113), (383, 101, 113) and (509, 109, 109) gives 1.0 to 1.15·10^-5 expected
successes per core-second, with shares from 4.5% to 10% (`tune.py`). The
threshold θ moves by one per residual class, Ta does not move.

## Production runs (Q = 10,007, N below 10^23, 4 cores)

One pass per residual class, θ = 99 at class 194 plus one per class,
Ta = 113, L = 383. `expected` is with the pair correction of the next
section but one. The per-unit counts are in `runs/`.

| class | vectors | members | Fermat tests | found | expected | share of the class | wall time |
|---|---|---|---|---|---|---|---|
| 193 | 154,098 | 1.178·10^12 | 2.32·10^10 | 0 | 0.045 | 8.4% | 26 min (first build, threads partly idle) |
| 194 | 467,071 | 3.570·10^12 | 5.29·10^10 | 0 | 0.100 | 7.2% | 43 min |

Class 194 ran at 1.37·10^9 members per second on the 4 cores, 6.7 cycles a
member, with 1.5% of the members Fermat-tested.

## Without AVX-512

On a CPU with AVX2 only (the Colab machines are EPYC 7B12, Zen 2) the byte
score runs 32 members to a vector instead of 64 and the Fermat test is
`fermat26.h`: four 26-bit limbs, the 32×32→64 multiply, 12 numbers at a
time. Built with `-march=haswell` on the Sapphire Rapids machine it costs
about 450 cycles a test (119 with IFMA, about 2,500 for the scalar test of
`tscan`), and the whole scanner is 1.85 times slower than the AVX-512 build
with the same thresholds. Both builds give the same counts to the last
digit on a whole class (class 192 below 2·10^21: 47,484 vectors,
7,244,499,944 members, 89,439,031 selected, 38,733,221 kept, 174,078,592
tests).

## What "expected" means, and its correction

`fscan` adds (1 − ε)^a over the members it tests, a = rows left by the
primes ≤ L and ε = 1/(ln N · ∏_{r ≤ L}(1 − 1/r)) the chance that such a row
is prime. This treats the rows as independent, and they are not quite: a
prime s > L divides two rows only when it divides the difference of their
primes, and the residual primes of a cover vector all lie in one class mod 3
and in few classes mod 5, 7, …, so their differences are multiples of 6 and
rarely have a prime factor above 383. The rows therefore die more
"one at a time" than independent ones would, the number left after a deeper
sieve is less spread out (measured variance 30.4 against 31.4 for
independent thinning, exactly what the pair count predicts), and a member
with no prime row is rarer. To second order the factor is
exp(c2 · (ε/(1−ε))² · a(a−1)/2) with c2 = −2.39·10^-4 per pair of rows for
Q = 10,007 and L = 383 (sum over the primes s from 383 to 131,072 of
[s divides the difference]/(s−1) − [it does not]/(s−1)², averaged over the
pairs of residual primes; the same value within 3% on 31 vectors). `fscan`
prints both: `expected` with the factor (about 0.92 at a = 110) and
`expected_raw` without. The direct comparison with the estimate `tscan`
uses, (1 − p)^(rows left at 131,072) on the same 13,878 tested members,
gives raw/deep = 1.23 ± 0.08; over all members of a range it gives 1.09.
So `expected` may still be some 10% high. In the table above `tscan`'s
figure is its own estimate, (1 − p)^(rows left at 131,072) summed over the
tested members, recomputed with the p of each member instead of one p for
the whole range (N doubles over that range, which changes the sum by about
20%).

## Checks

- `python3 test_fermat.py`: 152,907 numbers, 43,097 probable primes, no
  mismatch with `pow(2, n-1, n)`.
- `python3 check_small.py` (Q = 3,001, the 1,803 vectors with at most 51
  residual primes, 13.2 million members below 10^20): brute force with gmpy2
  on 168 of the vectors finds 190 successes; `fscan` with the thresholds off
  reports exactly those on each of the 168 vectors (2,214 on all vectors);
  with thresholds that test 14% of the members it reports 908, all true on
  the checked vectors, where its own expectation was 884 (904 in the AVX2
  build, which sums it over shorter chunks). Both builds report the same
  members.
- The vector enumeration gives the same N0 and residual list as
  `variants.py` for all 18,208 vectors up to 191 residual primes.
- A reported member has every row left by the primes ≤ L proved composite by
  a failed Fermat test; `check.py` then recomputes g(N) from N alone.

## Use

```
gcc -O3 -march=native -fopenmp -o fscan fscan.c -lm
gcc -O3 -march=native -o test_fermat test_fermat.c && python3 test_fermat.py 1 ./test_fermat 12
python3 check_small.py                                             # needs gmpy2; a few minutes
./fscan 10007 383 193 193 4e18 1e23 98 113 done=runs/R193.done    # one residual class, resumable
./run_range.sh 4e18 1e23 193 194 195                               # the same, class after class
./fscan 10007 383 196 196 4e18 1e23 101 113 slice=2/6 done=R196_2.done   # machine 2 of 6 on class 196
grep -h '^S ' runs/*.log | python3 check.py -                      # g(N) for everything reported
```

Arguments: Q, L, the range of residual sizes, the range of N, the score
threshold θ for residual size `rref` (default: the first size), and Ta.
`slice=i/n` takes one n-th of the vectors (by a hash of N0, so the shares are
equal: 618,244 to 619,545 vectors for the six slices of class 196), for
several machines sharing a class. `done=FILE` records each finished work
unit that holds vectors (a unit is a choice of residues mod 3, 5, 7, 11, 13,
17, 19), with its counts, and skips it on a restart; the file is tied to the
arguments, the slice included. The units are very unequal, because the small
vectors share the best classes of the small primes, so the threads share the
subtrees eleven primes deep of a batch of units (measured: 3.95 of 4 cores
busy). The classes up to
192 are what the `vscan.py` runs cover, so the production runs here start
at 193.

## What did not work, and why

- **A search over more than 13 fixed primes, or a tree/beam search with the
  exact success probability as the score.** Every such scheme is a rule for
  which members to look at and how closely, and they all trade share against
  enrichment at the same rate, because the logarithm of a member's success
  probability is close to a sum of many small independent terms, one per
  prime. Selecting the best fraction f of the members by the terms seen so
  far multiplies the mass per member by about exp(|z_f|·σ), where σ is the
  spread those terms contribute, and costs a factor 1/f in members to choose
  from. The primes from 47 to 383 contribute σ of about 1.2 in total, 47
  alone 0.28. What decides the cost is then the price of looking: 400 cycles
  for the full sieve, 1.35 for the byte score. A deeper tree only replaces
  part of the 1.35.
- **Sharing the sieve between numbers.** Two numbers N and N' share a row
  (N − q = N' − q') only when N' − N = q − q' is small, that is in an
  exhaustive search of an interval. Such a search could count the rows left
  for every N of the interval at an estimated 7 cycles each (one sieved
  position per N, the count by bit-sliced adds; not built), but its
  candidates are typical numbers, 100 to 200 times less likely to succeed
  than the members of the best vectors, and a shifted copy of a good vector
  is a typical vector. By that estimate it loses to `tscan` by a factor 2 to
  3 at 25 digits and scales worse (4.5 per digit against 3.8).
- **A cost per digit below 3.8.** With the vector counts above, the cost of
  one more digit should rise slowly as N falls (the classes needed are closer
  to the bulk, where the count grows by less per class): an estimated 3.8 at
  25 digits, 4.3 at 23, 5.5 at 21. The gain of this scanner is a constant
  factor, not a better exponent.
