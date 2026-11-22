# tscan: the small-N threshold scanner

The threshold game asks for the smallest N with g(N) > Q. For Q = 10,000 the
answer lies just above the exhaustive range (g ≤ 9,781 for N ≤ 4·10^18), and
how small an N we can exhibit is limited only by how many candidates we can
scan. This directory is the scan step of `search.py`, rewritten in C for
numbers of 20 to 80 digits.

| file | what it is |
|---|---|
| `tscan.c` | the scanner: one progression N = N0 + k·M, one range of k |
| `scan.py` | resumable driver for a list of progressions, one after the other |
| `variants.py` | every near-optimal residue vector on a cover's primes |
| `vscan.py` | driver that scans many such progressions in lockstep, smallest N first |
| `selftest.py` | tests against gmpy2 and a brute-force reference (`selftest_q3001.json`) |

A record never rests on this code. Each success is re-checked by
`search.verify_success`, then proved by `package_record.py` (a witness per
prime below g, ECPP certificate for N − g) and by a direct PARI check.

## Method

A cover (`cover.py`) fixes N mod r for a few small primes r. A prime q < Q is
*covered* when r | N − q for one of them; the others are the residual primes
U. A member k of the progression succeeds when N − q is composite for every
q in U.

1. **Bit sieve.** For a block of 2^18 consecutive k, a bit table (one row per
   q in U) is cleared wherever N − q has a prime factor s ≤ B = 131,072. Primes
   s < 384 are applied 512 bits at a time from a periodic pattern (AVX-512);
   larger ones one bit at a time, with a fixed number of marks per prime so
   the loop has no unpredictable branch.
2. **Count.** a(k) = number of rows still set in column k.
3. **Select.** A survivor is prime with some probability p (about 0.35 here),
   so k succeeds with probability about (1 − p)^a(k). Most k have far too many
   survivors to matter. Only the k with a(k) ≤ T are tested. The scanner prints
   the histogram of a(k), from which the driver computes which share of the
   expected successes the tested k hold, and picks the T that maximises
   share ÷ time.
4. **Test.** Base-2 Fermat tests on the survivors of a selected k, stopping at
   the first probable prime (which kills that k). A k whose survivors all fail
   is reported: each failure proves a complement composite. The test is a
   Montgomery ladder on 2 to 4 limbs of 64 bits that keeps the residue as a
   plain power of 2, so nothing is converted to or from Montgomery form.

## Measured (4 cores, Xeon 2.1 GHz, Q = 10,007, 188 residual primes, 27-digit N)

| | k per second |
|---|---|
| `search.py` (numpy sieve, gmpy2, tests every k; 30-digit job) | 0.3 million |
| `tscan`, testing every k | 1.0 million |
| `tscan`, T = 49: tests 1.26% of the k, which hold 61–66% of the successes | 16–19 million |

In successes per second that is about 35 times `search.py`.

## Many progressions instead of one

`cover.py` picks the residues greedily. For the 13 primes r ≤ 43 and
Q = 10,007 the greedy vector leaves 188 residual primes. An exhaustive
search (`variants.py`) finds 6 vectors with 186, 28 with 187, 157 with 188,
818 with 189, 3,523 with 190 and 13,676 with 191. They all share M, and a
vector's success rate depends on little but its residual count. Scanning V
of them to the same height reaches a V times smaller N for the same number
of candidates. `vscan.py` does this: it always advances the progression
that is lowest. Several machines can share one list: each takes every n-th
progression (last argument `i/n`) and keeps its own state file.

Why 13 primes and not 14: fixing the residue mod 47 as well gives 47 times
as many progressions, each 47 times shorter, and lets the search keep only
the best classes mod 47 instead of sieving all of them. There are 7 vectors
on the 14 primes with 178 residual primes, 85 with 179, 462 with 180, 2,498
with 181, 10,936 with 182 and 42,906 with 183. For the same number of
candidates that is an estimated 1.3 times more successes, which did not
justify a scanner that handles tens of thousands of short progressions.

## Use

```
python3 selftest.py                                   # about 10 s
python3 ../cover.py 10007 23 spec.json                # then add a "name" field
python3 scan.py plan.json 3600                        # plan.json: see scan.py
python3 variants.py spec.json 3 variants.json
python3 vscan.py variants.json state.json 3600 188    # only vectors with <= 188 residual primes
python3 vscan.py variants.json mine.json 3600 190 24 0/3   # one of three machines sharing the list
```

`scan.py` compiles `tscan.c` on first use (`gcc -O3 -march=native -fopenmp`).
Without AVX-512 the scanner still works, with a slower sieve and count.
