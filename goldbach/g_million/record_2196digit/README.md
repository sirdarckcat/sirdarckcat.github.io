# A 2,196-digit N with g(N) ≥ 1,000,003 (g(N) = 1,001,491 if N − 1,001,491 is prime)

g(N) is the least prime p with N − p prime. N is in `N.txt`. It is even, has 2,196 digits, and begins 39385920356954952507… .
N = N0 + k·D, where:
- k = 8,179,130;
- D = 2·∏(odd primes up to 5,113), which has 2,189 digits;
- N0 is the even number from the Chinese remainder theorem with N0 ≡ a_r (mod r) for the 683 moduli of the cover (`cover.txt`, `setup.json`).

The record held before this work is g = 1,157,341 at 2,480 digits.

## What is shown

- **Every N − q, for every odd prime q < 1,000,003, is composite.** N − 2 is even, so g(N) ≥ 1,000,003. This needs no proof of
  primality.
  - `verify.py` checks it from N alone: 76,977 rows have a factor up to 10⁶ and the other 1,520 fail a base-2 Fermat test
    (`verify.log`, `verify.json`).
  - `certificate.py` checks it again and gives one reason per row (`certificate.txt`):
    - 75,934 rows are covered by a modulus r of the cover, with N ≡ q (mod r);
    - 1,593 rows have a least prime factor of N − q in (5,113, 10⁹], found from N alone;
    - the remaining 970 rows fail base-2 Fermat, 2^(N−q−1) ≢ 1 (mod N − q).

    The 970 rows with no factor up to 10⁹ are exactly the sieve's survivor list for this member.
- **g(N) = 1,001,491, if N − 1,001,491 is prime.**
  - N − 1,001,491 is a BPSW probable prime, and also passes 25 more Miller–Rabin rounds. Its primality is not proved; that would
    need an ECPP certificate.
  - For each of the 115 primes p with 1,000,003 ≤ p < 1,001,491, N − p is proved composite by a Miller–Rabin or BPSW witness.
  - So g(N) ≥ 1,001,491 holds unconditionally.
  - `certificate_to_g.txt` gives one reason per row for every odd prime q < 1,001,491, in the same form as `certificate.txt`.

## Kernel certificate (the Lean session)

The Lean session built and checked this certificate (branch `ccr-36ca7b46-8twf14`, commit `9d4555f`). The full build passes, and
it uses only the axioms propext, Classical.choice and Quot.sound.

It proves two theorems, in `goldbach/lean/GoldbachGaps/FixedGap.lean`:
- `exists_2196_digit_no_summand_below_1001491`: there is an even N with 10^2195 ≤ N < 10^2196 such that N − q is not prime for
  any prime q < 1,001,491.
- `exists_lt_ten_pow_2196_no_summand_below_1000000`: the same with the bound 1,000,000.

The certificate is `GoldbachGaps/Gap1M_2196digit_g1001491.lean`, with `_Base` and 31 parts, `_0` to `_30` (3.4 MB of Lean).
- **How it works:** it is in witness form. Each q below the bound gets one witness, which the kernel checks by one division,
  or by the base-2 Fermat test.
- **What the kernel checked:** 78,613 primes below the bound, q = 2 included:
  - 76,036 struck by a modulus or by 2;
  - 1,600 by the factors in `certificate_to_g.txt`, each verified by division before use;
  - 977 by the Fermat test.
- **Cost:** 16 minutes of kernel time, two parts at a time.
- **Not certified:** that N − 1,001,491 is prime.

The Lean session also checked the record independently from `N.txt` and `cover.txt` alone and agrees row for row. So does the
research session.

## How it was found

1. **Cover** (`cover.txt`, 683 moduli, the odd primes up to 5,113): 2,563 of the 78,497 rows are in no class. It came from greedy
   plus 1-flip descent (2,852 rows), then heat-bath annealing (3,000 sweeps, β from 2 to 6: 2,595 rows), then 20,000 more sweeps
   (β from 1.8 to 10: 2,563 rows).
2. **Sieve**: 2·10⁷ members N0 + k·D against the primes in (5,113, 10⁹]. Pass 1 took 619 s on 4 threads.
   - Survivors per member: mean 1,058.2, sd 24.8 (binomial), minimum 927.
   - Pass 2 (305 s) listed the survivors of the 10,000 emptiest members, those with S ≤ 977 (3.27 sd below the mean).
3. **Tests**: members in increasing order of S, base-2 Fermat on N − q for the survivors, stopping at the first probable prime
   (`tested.jsonl`).
   - The hit was the 3,615th member, with S = 970. By then 3.18 hits were expected, so a first hit this late had probability 4%.
   - The tests also check the model. The deaths give 138.5 tests per prime found, against 137.0 from e^γ·ln B/ln N.
4. **Cost**:
   - tests: 501,670 Fermat tests at 65.6 ms each, 9.1 CPU-hours (2.3 hours on 4 cores);
   - sieve: about 1.0 CPU-hour;
   - cover: about 0.2 CPU-hours;
   - in all, about 10.4 CPU-hours on one 4-core machine.

## Files

`N.txt`, `hit.json` (k and N), `cover.txt`, `setup.json` (moduli, classes, N0, D), `verify.log` and `verify.json`,
`certificate.txt` with `certificate.txt.json` and `certificate.log`, `tested.jsonl` (every member tested).
