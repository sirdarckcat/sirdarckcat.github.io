# Handover: the fast arithmetic and sieving code

This note is for a reader who wants to know what this part of the repository does, how much faster it made the searches, and
how far it got. It covers the work of the session that wrote the CPU and GPU kernels, from 21 to 26 November 2026.

## The problem in one paragraph

For an even number N, let g(N) be the smallest prime p such that N − p is also prime. The searches look for N with an unusually
large g(N). The method chooses N so that, for most primes p below a target, N − p is divisible by some small prime and so cannot
be prime. It does this by fixing the remainder of N on division by each of the first hundred or so odd primes; such a choice is
called a cover. About 1,200 primes p below the target are left that no remainder deals with; we call them rows. For N to
succeed, every N − p for a row must be composite by luck. The candidates N form an arithmetic progression, N = N0 + k·M, and we
call them members.

Two operations take all the time:
- **The sieve.** It strikes out every N − p that has a small prime factor, and so counts how many rows are still open for each
  member. Only the members with the fewest open rows are worth testing.
- **The Fermat test.** It checks whether one of the open N − p is prime. If 2^(n−1) leaves remainder 1 on division by n, then
  n is almost certainly prime; any other remainder proves n composite.

A member dies at its first prime N − p. The rare member whose open N − p are all composite is a find. At 200 digits the chance
per member is a few in 10^13, so finds come from testing tens of billions of members, and twice the speed means twice the
finds.

## What the code does, and what it gained (all measured)

**On the CPU.**
- `sieve200/` is the sieve in C. It processes a block of 32,768 members in 0.07–0.2 s, where the earlier numpy code took 1.7 s.
  `search_c.py` is a drop-in replacement for `search.py`: same command line, same output.
- `fermat661/fm13.c` is the Fermat test for the 661–665-bit numbers of the 200-digit search. It uses the AVX-512 IFMA
  instructions, which multiply 52-bit pieces of eight numbers at once. It takes 10–11 µs a test, against 124 µs for gmpy2 (the
  standard big-number library), so it is about 11 times faster.
- `fermatw/` is the same idea for numbers of any size, 8 to 12 times faster than gmpy2 at 1,000–1,340 bits. With it, the
  400-digit scan ran at 10,789 members a second instead of 1,874.

**On the GPU (an RTX PRO 6000).**
- `fermat661/cuda/` holds the Fermat kernel. It cuts a number into 24 pieces of 28 bits, so that every partial product fits one
  64-bit multiply-add with no carry handling, and squares with half the multiplications of a general product. It ran 22.9 million
  tests a second, against 13.1 million for the kernel it replaced and 8.9 million for the first one. With 29-bit pieces it reached
  24.6 million. `fround.py` moved the bookkeeping between test rounds onto the GPU: about 8% off each batch.
- `sieve200/cuda/` holds the GPU sieve:
  - the small primes are struck in the processors' fast on-chip memory;
  - the primes up to 10^8 are sorted into bins in the card's main memory, then applied;
  - the selection of the emptiest members runs on the card too.

  The measured gains:
  - sieving to 10^8 instead of 10^6: 32% more finds a second;
  - a single-pass version of the binning kernel: 2.7–4.3% off each batch;
  - running the sieve beside the Fermat kernel instead of after it: 1.14 times faster in production;
  - splitting the test pool in two: +2.7%;
  - testing the emptiest 0.75% instead of 1.5%: +5.6%.

The GPU session found the 200-digit records g = 157,837, 158,209 and 160,357 with these kernels in production.

**How it was checked.** Every kernel was compared with an independent reference before it was used:
- `fm13` and `fmw` against gmpy2: the final remainder and the verdict, on random numbers of every size, on primes, on base-2
  pseudoprimes, and on every N − q of the records. `fm13` is exact up to 672 bits. Above that it can only wrongly say "composite",
  never wrongly "prime".
- The sieve against plain trial division and against the numpy sieve. `search_c.py` against `search.py`, end to end, with
  identical log lines and identical finds.
- The GPU code was written without a GPU. Each CUDA kernel also compiles as ordinary C++ and is checked on the CPU against brute
  force; `goldbach/run_cpu_tests.sh` runs these tests. On the card, the GPU session then checked each kernel:
  - 0 mismatches against gmpy2 on 40,000 numbers of the production range for every variant;
  - summary lines identical to the previous version;
  - known near-misses found again.

## Records found: g(N) of at least 200,000 with N as small as possible

| digits of N | g(N) | cost | directory |
|---|---|---|---|
| 400 | 200,293 and 206,593 | 1.8 CPU-hours (one scan, two finds) | `records/g200k_400digit_g200293/`, `.../g206593/` |
| 347 | 216,289 | 1.0 CPU-hour (after 7.5 CPU-hours on a 350-digit cover that held none) | `records/g200k_347digit_g216289/` |
| 319 | 207,307 | 6.4 CPU-hours | `records/g200k_319digit_g207307/` |

Each directory holds:
- N;
- a reason why N − p is composite for every prime p below g: the cover's congruence, a small factor, or a base-2 witness;
- a check that g is prime and that N − g passes the BPSW primality test;
- a second computation of g from N alone.

Lean proofs of the two 400-digit records and the 347-digit one are on PR #34. The 319-digit record was not yet in that PR's
table.

Also on this branch: a 200-digit side scan on idle cores at the record target, with no find, as expected (1,616 covers, 41.5
core-hours, 0.0015 finds expected; `g200k/cpu_scan_523/LEDGER.md`).

## Ideas that were tried and failed

**Carry-over.** Members still being tested at the end of a batch were to move into the next batch's test rounds, so that the GPU
would not idle while the last few finished.
- Predicted: +2.1 to +5.3% finds a second.
- Measured in production: −1.1%. Its own bookkeeping cost about 4% of a batch, which the prediction had counted as zero.
- Reverted.

**Two-stage sieve.** The large primes were to be sieved only for the 10–20% of members that look best after the small primes.
- Withdrawn before it was built. Deciding whether each large-prime mark lands on a kept member takes one random read of a 2 MB
  table, about 7 billion reads a window.
- That is about 52 ms a window, against at most 17 ms saved.

**Clusters.** Pooling the on-chip memory of several of the GPU's processors would let the large-prime marks skip the trip
through main memory.
- The largest pool that launches holds 1,584 KB.
- Writes into another processor's memory run at 16–41 billion a second, against 2,100–2,850 billion locally (70–130 times
  slower).
- No gain.

**Smaller losses, also measured:**
- a Fermat kernel that never exits: 5–19% slower beside the sieve;
- a second, deeper sieve stage at production settings: 0.7% slower;
- 31-bit and 30-bit pieces: 33% and 24% slower;
- Karatsuba multiplication: a loss;
- using the floating-point units beside the integer multiplier: no gain, because both share the same hardware lanes;
- a new keep fraction for the L4 cards: predicted 1.15 times, measured 1.000 times.

All the numbers are in `goldbach/HEADROOM.md` and `g200k/costside/RESULTS.md`.

## Where it stands, and what is unfinished

At 200 digits the GPU engine is close to its limits. The Fermat test runs at the speed of the card's integer multiplier, and the
sieve is within about 1.5 times of its memory-traffic limit. The review of 25 November found at most 1.35 to 1.6 times left
in total. Of that, the part that worked (the 0.75% keep) is in production; the carry-over failed and the two-stage sieve was
withdrawn. By the research session's accounting, reaching g = 200,000 below 10^200 would need roughly 220 times today's
computing, or mathematics that nobody on the team found.

Unfinished:
- **The 200-digit side scan** stopped at cover 1,616 of 8,572. How to resume is in its ledger.
- **The fixed-gap game below 319 digits.** A 300-digit attempt tested 24 covers with no find, against about 0.06 expected, and
  then stopped. One find there should cost some 65 to 100 CPU-hours (`g200k/README.md`, `g200k/scan300/`).
- **The 10% closeness frontier.** The rungs at 101, 105 and 110 digits are done. Half of the 120-digit rung is done (200 covers,
  1.12 finds expected, none found); the other half was lost when the container restarted. The 125-digit rung was not started
  (`g200k/frontier/RESULTS.md`).
- **GPU options built and checked on the CPU but not deployed:**
  - selecting members by the rows below the record only: 1.065 times the record-beating events, 0.937 times the 170,000 finds;
    declined by the lead;
  - faster end-of-window kernels: about 0.6%, shelved;
  - a second sieve stage only up to 3·10^8: about +1.2%, never tried.

Where to start reading:
- the CPU kernels: `sieve200/README.md`, `fermat661/README.md`, `fermatw/README.md`;
- the GPU kernels: `fermat661/cuda/FERMAT28.md`, `FERMAT29.md`, `FROUND.md`, `sieve200/cuda/DEEPSIEVE.md`;
- the GPU audit: `goldbach/HEADROOM.md`;
- the searches: `g200k/README.md`.
