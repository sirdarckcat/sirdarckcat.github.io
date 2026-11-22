# fermat661: base-2 Fermat tests of 661-bit numbers with AVX-512 IFMA

`search.py` spends 97% of a campaign-3 block in `gmpy2.powmod(2, n - 1, n)` on numbers of 661 bits (124 us each on a
2.1 GHz Xeon).  `fm13.c` does the same test 8 numbers at a time with the IFMA instructions (13 limbs of 52 bits), 10-11 us
a number on the same core: about 11 times faster, same verdicts.

| file | what |
|---|---|
| `fm13.c`, `fm13_step.h` | the kernel. `fm13_test` tests any count of numbers, `fm13_members` runs `search.run_block`'s loop (the survivors of many members, stop at a member's first probable prime) with the 8 lanes holding 8 different members |
| `gen_fm13.py` | generates `fm13_step.h` (the step is straight-line code: `python3 gen_fm13.py 1`) |
| `fm13.py` | ctypes wrapper (`available()`: avx512ifma present; compiled with gcc on first use) |
| `test_fm13.py` | final residue 2^(1-n) mod n and verdict against Python `pow`, on random numbers of 100 to 664 bits, mixed lengths in one batch, primes, base-2 pseudoprimes, edge values; the member scheduler against a plain loop |
| `bench_fm13.py` | microseconds per test against gmpy2 |

`../sieve200/search_c.py` uses it automatically on a CPU with IFMA (`SEARCH_C_FERMAT=gmpy2` turns it off).

## Method

The residue is kept as a power of two, so there is no conversion to or from Montgomery form (the construction of
`../fscan/fm_common.h`): with R = 2^676 and t = bits(max n of the batch) - 6 steps, the start value is 2^(676-c) and the exponent
bits are those of (c 2^t - n - 675), with c = ceil((n + 675) / 2^t); after the t steps y = 2^(1-n) mod n, and n passes iff y = 1.
A step is a Montgomery squaring times 2^b (b the lane's exponent bit): the off-diagonal products a_i a_j (i < j) once and
doubled plus the diagonal (182 IFMA instructions), 13 reduction rounds m = lo52(t_i n'), t += m n (351), the doubling for b
as a masked add, and a carry chain to bring the limbs below 2^52.  Column sums stay below 2^58, the value below 4n.  533 IFMA
instructions per step and 8 lanes; the Sapphire Rapids core issues 1.6 of them a cycle.
