# A 1,997-digit N with g(N) ≥ 1,000,003 (g(N) = 1,008,589 if N − 1,008,589 is prime)

g(N) is the least prime p with N − p prime. N is in `N.txt`. It is even, has 1,997 digits, and begins 692288497273852599498545622672… .
N = N0 + k·D, where:
- k = 26,758,760;
- D = 2·∏(odd primes up to 4,657), which has 1,990 digits;
- N0 is the even number from the Chinese remainder theorem with N0 ≡ a_r (mod r) for the 629 moduli of the cover (`cover.txt`, `setup.json`).

This replaces the 2,196-digit N of `../record_2196digit/` as the smallest N found with g(N) ≥ 10⁶.

## What is shown

- **Every N − q, for every odd prime q < 1,000,003, is composite.** N − 2 is even, so g(N) ≥ 1,000,003. This needs no proof of
  primality.
  - `verify.py` checks it from N alone: 76,839 rows have a factor up to 10⁶ and the other 1,658 fail a base-2 Fermat test
    (`verify.log`, `verify.json`).
  - `certificate.py` gives one reason per row (`certificate.txt`):
    - 75,672 rows are covered by a modulus r of the cover, with N ≡ q (mod r);
    - 1,767 rows have a least prime factor of N − q in (4,657, 10⁹], found from N alone;
    - the remaining 1,058 rows fail base-2 Fermat.

    The 1,058 rows with no factor up to 10⁹ are exactly the sieve's survivor list for this member.
- **g(N) = 1,008,589, if N − 1,008,589 is prime.**
  - N − 1,008,589 is a BPSW probable prime, and also passes 25 more Miller–Rabin rounds. Its primality is not proved.
  - For each of the 646 primes p with 1,000,003 ≤ p < 1,008,589, N − p is proved composite.
  - So g(N) ≥ 1,008,589 holds unconditionally.
  - `certificate_to_g.txt` gives one reason per row for all 79,143 odd primes q < 1,008,589: 76,241 by a modulus, 1,808 by a factor,
    1,094 by Fermat.

## How it was found

1. **Cover** (`cover.txt`, 629 moduli, the odd primes up to 4,657): 2,825 of the 78,497 rows are in no class.
   - It started from the 2,196-digit record's cover with the moduli above 4,657 removed (2,860 rows).
   - Then 20,000 heat-bath sweeps with β from 1.8 to 10 (`heatbath2`, `anneal4657.sh`) brought it to 2,825.
   - It is the best of four anneals, which ended between 2,825 and 2,839.
   - Thermodynamic integration puts the floor of this family of covers at about 2,785 (`../README.md`).
2. **Sieve**: 4·10⁷ members against the primes in (4,657, 10⁹]. Pass 1 took 428 s on 4 threads.
   - Survivors per member: mean 1,153.6 and sd 26.0, against 1,153 and 26 predicted, with a minimum of 1,019.
   - Pass 2 (427 s) listed the survivors of the 15,000 emptiest members, those with S ≤ 1,066 (3.37 sd below the mean).
3. **Tests**: members in increasing order of S, base-2 Fermat on N − q for the survivors, stopping at the first probable prime
   (`tested.jsonl`).
   - The first 2,238 members used gmpy2.
   - The next 2,368 used the uarch session's AVX-512 IFMA kernel: `goldbach/fermatw`, branch `ccr-b8c25887-i6tn9f`, commit `63f0b8d`,
     through `../test_members_fmw.py`. On 48 members already tested with gmpy2 it put the first probable prime at the same position
     for all 48, over 5,213 tests. The hit was tested again with gmpy2.
   - The hit was the 4,606th member, with S = 1,058. About 0.99 hits were expected by then, so a first hit this late had
     probability 37%.
   - The deaths give 122.8 tests per prime found, against 124.6 from e^γ·ln B/ln N.
4. **Cost**:
   - tests: 565,572 Fermat tests, 5.5 CPU-hours (4.2 with gmpy2 at 54 ms a test, then 1.3 with the kernel at 16.2 ms);
   - sieve: about 0.95 CPU-hours;
   - cover: about 0.1 CPU-hours of annealing, starting from the earlier record's cover;
   - in all, about 6.6 CPU-hours on one 4-core machine. With the kernel from the start, the tests would have taken about
     2.5 CPU-hours.

## Files

`N.txt`, `hit.json` (k and N), `cover.txt`, `setup.json` (moduli, classes, N0, D), `verify.log` and `verify.json`,
`certificate.txt` and `certificate_to_g.txt` (each with a `.json` summary and a `.log`), and `tested.jsonl` (every member tested;
the kernel's members are marked `"kernel": "fmw"`).
