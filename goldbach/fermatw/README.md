# fermatw: base-2 Fermat tests of 300-400 digit numbers with AVX-512 IFMA

`../fermat661/fm13.c` (13 limbs of 52 bits, numbers up to 664 bits) for any limb count L: numbers up to 52 L - 12 bits.
L = 20 / 21 / 23 / 26 serve 300 / 320 / 350 / 400 digits.  Same method (residue kept as a power of two, Montgomery squaring
times 2^b per exponent bit, 8 lanes of different numbers), same member scheduler (`fmw_members`: the Fermat loop of
`search.run_block`, 8 members in flight).

| file | what |
|---|---|
| `gen_fmw.py L [G] [variant]` | writes `fmw_step_L<L>.h`, the straight-line step: column sums of the square (off-diagonal once, doubled, plus the diagonal), L reduction rounds, the masked doubling, the carry chain. `win`: the reduction keeps a window of L + 1 columns in variables (phase 1 stores the 2L columns to the stack); `win2`: the same, with the square's columns in blocks of 4, two accumulators a column (lo and hi terms) and the terms of the 8 chains emitted round-robin, so the chains are half as long and independent IFMAs sit next to each other; `flat`: fm13's shape. `fmw.py` uses `win2` for L >= 21 and `win` below (`FMW_VARIANT` overrides) |
| `fmw.c` | the batch, test and member functions (`-DFMW_L=L -DFMW_HDR='"fmw_step_L<L>.h"'`) |
| `fmw.py` | ctypes wrapper: `limbs_for(bits)`, `lib(L)` (generates and compiles on first use), `test(ns)`, `Members(N0, M, U, kmax)` |
| `test_fmw.py [L ...]` | residues y = 2^(1-n) mod n and verdicts against Python `pow`: random odd numbers at the top size and mixed sizes in one batch, primes, base-2 pseudoprimes (4^p - 1)/3, semiprimes; the member scheduler against a plain loop |
| `bench_fmw.py L [variant] [G]` | microseconds per test against gmpy2 |
| `bench_ab.py L A B [reps]` | two variants alternately in one process (the machine is noisy): min and median |

`../sieve200/search_c.py` uses it automatically when the members of a progression have more than 664 bits (fm13 below);
`SEARCH_C_FERMAT=gmpy2` turns both off.  On the g >= 200,000 cover at 400 digits (1,010 rows, B = 10^7, skip 0.98, 65,536
members, one core) the scan statistics are identical to gmpy2's (tests = 42,483, prp = 1,312) at 10,789 members/s instead of 1,874.

## Speed (one core of the 2.1 GHz Sapphire Rapids Xeon, three other cores busy)

| L | bits | fmw us/test | gmpy2 us/test | ratio | cycles a step (8 lanes, at 2.1 GHz) |
|---|---|---|---|---|---|
| 20 | 1028 | 34.6 | 401 | 11.6 | 568 (1,240 IFMA: 2.2 a cycle) |
| 26 | 1340 | 105.7 (`flat` 99.2) | 857 | 8.1 | 1,331 (2,080 IFMA: 1.6 a cycle) |

At L = 26 the window of 27 columns plus the multiplier and constants fills the 32 vector registers; G = 2 groups are slower
(117 us).  The peak on this core is 2 IFMA a cycle at about 3.1 GHz (tput microbenchmark), so the floor is about 26 / 40 / 58 us
at L = 20 / 23 / 26: L = 20 runs at about 80% of it, L = 23 and 26 at 50-60%.  `win2` against `win` (`bench_ab.py`, alternating
runs in one process, 16-30 each, three other cores busy; min / median us): L = 20 30.7 / 35.3 vs 30.1 / 33.3; L = 21 37.7 / 44.9
vs 38.7 / 45.8; L = 23 45.8 / 62.2 vs 50.7 / 64.3; L = 26 75.9 / 95.6 vs 91.2 / 102.1.
