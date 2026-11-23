# g(N) = 158,209 for a 200-digit N (below 10^200)

N = 50583740589138609697834580677536505029993742021564403324742841593805675019483643333405234558658003443364952736004219490803519504354430208924939648722453717301132634879292790425977206547799605815328328

- N is even, has 200 digits, and N < 10^200.
- N − p is composite for every prime p < 158,209 (14,535 primes), and N − 158,209 is prime, so g(N) = 158,209.
- It is the largest g known below 10^200, 372 above the 157,837 of 02:08 UTC (`../budget_1e200_200digit_g157837/`).
  - Its N, 5.06·10^199, is smaller than that one's (7.77·10^199) and than 146,191's (5.70·10^199).
  - So it dominates both on the frontier.
- Closeness (`../../closeness.py`): 7.45% of the largest g expected at 200 digits, 97.5× a typical 200-digit number.

## How it was found

- The cover is a Q = 170,000 cover on the first 89 odd primes, M = 2·∏r with 192.7 digits: the research session's
  89-moduli family (e24f6e2 on ccr-d4a17dd0-7uu03r).
  - The covers were walked on the card by `phd/campaign3_gpu/v89/vecgen.sh`: covergen at cap 1,250, and the card's share
    by md5 mod 3.
  - Each was checked by `check_specs.py` (a row counts as covered exactly when gcd(N0 − q, M) > 1).
  - The vector is `q170000_m89_p2c00019_v545`, from chunk 19 of gold-g4c's producer, with 1,250 residual primes below
    170,000.
  - 158,209 is its row 1,168 (counting from 0). So the member's first 1,168 residual rows were all composite, and 86 of
    its rows lie in [157,837, 170,000).
- N = N0 + k·M with k = 10,814,286. That k is inside the vector's first 200-digit window [k_lo, k_lo + 2^24), where
  k_lo = 2,137,898.
- It was found on 2026-11-23 at 12:48:45 UTC by `phd/campaign3_gpu/search_gpu5.py` in vector mode on the Colab G4 runtime
  gold-g4c (RTX PRO 6000 Blackwell). The engine of that hour:
  - the uarch session's deep sieve: primes up to 10^8, windows of 2^24, row groups of 32, rcta 8 with 512 generate
    threads;
  - keep fraction f = 0.985, the emptiest 1.5% of each window (the lead's decision of 12:01 UTC);
  - Fermat kernel 28 with uarch's 29-bit step `fermat29_step_s1.cuh` (23 limbs of 29 bits, R = 2^669) and the fused
    Fermat rounds (`--fused-rounds 1`);
  - near-miss reporting: a member whose first probable-prime row is at or above the record 157,837 is verified on the CPU
    and written to `found.jsonl`.
- The vector campaign had logged 0.106 expected near-misses at or above 157,837 by then: 0.031 / 0.043 / 0.032 on gold-g4
  / gold-g4b / gold-g4c, over its first 2.4 hours. So this one came early.
- `found.jsonl` is the search's own output line. `verify_near_miss` had re-checked it on the CPU before writing it: N − p
  composite for every prime p < g, and N − g a probable prime.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-23, this session's container) with `CLAIM_Q=157837`.

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 89 classes and the 1,250 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 14,535 primes p < g: p = 2 by parity, 13,366 by a class modulus r dividing N − p, 578 by trial division, 590 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 89 classes and t = k. It proves N − p composite for every p < g (the 1,168 uncovered ones by failed strong tests). It re-verifies the 26-step ECPP certificate and checks the claims g > 157,837, N < 10^200 and digits ≤ 200: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 14,535 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 200 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
