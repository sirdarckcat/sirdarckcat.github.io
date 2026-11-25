# A 1,797-digit N with g(N) ≥ 1,000,003 (g(N) = 1,021,897 if N − 1,021,897 is prime)

g(N) is the least prime p with N − p prime. N is in `N.txt`. It is even, has 1,797 digits, and begins 227711320328389340397461707149… .
N = N0 + k·D, where:
- k = 30,561,546;
- D = 2·∏(odd primes up to 4,201), which has 1,789 digits;
- N0 comes from the Chinese remainder theorem on the 574 moduli of the cover (`cover.txt`, `setup.json`).

This replaces the 1,997-digit N of `../record_1997digit/` as the smallest N found with g(N) ≥ 10⁶. The research session asked that
this descent stop here (at 1,800 digits), unless the user or the lead asks for more.

## What is shown

- **Every N − q, for every odd prime q < 1,000,003, is composite.** N − 2 is even, so g(N) ≥ 1,000,003.
  - `verify.py` checks it from N alone: 76,739 rows have a factor up to 10⁶, and 1,758 fail a base-2 Fermat test.
  - `certificate.py` gives one reason per row: 75,394 rows by a modulus, 1,943 by the least prime factor of N − q in
    (4,201, 10⁹], and 1,160 by Fermat. The 1,160 Fermat rows are exactly the sieve's survivors for this member.
- **g(N) = 1,021,897, if N − 1,021,897 is prime.**
  - N − 1,021,897 is a BPSW probable prime, and passes 25 more Miller–Rabin rounds. Its primality is not proved.
  - For each of the 1,619 primes p with 1,000,003 ≤ p < 1,021,897, N − p is proved composite.
  - `certificate_to_g.txt` covers all 80,116 odd primes below g: 76,827 by a modulus, 2,049 by a factor, 1,240 by Fermat.
- **In the Lean kernel.** The Lean session certified g(N) ≥ 1,021,897 at the lead's go-ahead: commit `90c3778` on branch
  `ccr-36ca7b46-8twf14`.
  - The module is `GoldbachGaps/Gap1M_1797digit_g1021897` (32 parts).
  - The theorems are in `GoldbachGaps/FixedGap.lean`:
    - `exists_1797_digit_no_summand_below_1021897`: an even N with 10^1796 ≤ N < 10^1797 and N − q composite for every prime
      q < 1,021,897;
    - `exists_lt_ten_pow_1797_no_summand_below_1000000`.
  - Both use only the standard axioms.
  - Its own check from N.txt and cover.txt alone agrees with every one of the 80,116 lines of `certificate_to_g.txt`.
  - As for the other records, the theorem is the negative side only (at least 1,021,897). It gives no proof that N − 1,021,897 is
    prime.

## How it was found

1. **Cover** (`cover.txt`, 574 moduli, the odd primes up to 4,201): 3,103 of the 78,497 rows are in no class.
   - It started from the 1,997-digit record's cover with the moduli above 4,201 removed (3,140 rows).
   - Then 20,000 heat-bath sweeps (`heatbath2`, `anneal_next.sh`) brought it to 3,103, the better of two seeds.
2. **Sieve**: 6·10⁷ members against the primes in (4,201, 10⁹].
   - Pass 1 took 739 s on 4 threads. Survivors per member: mean 1,251.5 and sd 27.2, against 1,252 and 27.3 predicted, with a
     minimum of 1,103.
   - Pass 2 (1,203 s) listed the survivors of the 100,000 emptiest members, those with S ≤ 1,172 (2.92 sd below the mean).
3. **Tests**: the uarch session's AVX-512 IFMA kernel through `../test_members_fmw.py`, for every member, at nice 19 for most of
   the run.
   - The hit was the 21,920th member, with S = 1,160. About 0.75 hits were expected by then, so a first hit this late had
     probability 47%.
   - The deaths give 111.1 tests per prime, against 112.1 predicted.
4. **Cost**:
   - tests: 2,435,204 Fermat tests, 11.6 CPU-hours (17.2 ms a test; the cores were shared for part of the run);
   - sieve: about 2.2 CPU-hours;
   - cover: about 0.1 CPU-hours;
   - in all, about 14 CPU-hours, which is what `cost_model.py` predicted.
