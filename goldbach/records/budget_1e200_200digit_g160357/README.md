# g(N) = 160,357 for a 200-digit N (below 10^200)

N = 95347106818046249718570776328527805394387907539756369117325081343361548773031798520383947495686099037769506167416423881905531645343709972339865033333397602306957446186830655985687114607924513408740178

- N is even, has 200 digits, and N < 10^200.
- N − p is composite for every prime p < 160,357 (14,711 primes), and N − 160,357 is prime, so g(N) = 160,357.
- It is the largest g known below 10^200, 2,148 above the 158,209 of 23 Nov 12:48 UTC (`../budget_1e200_200digit_g158209/`).
  - Its N, 9.53·10^199, is larger than that one's (5.06·10^199), so 158,209 stays on the frontier too.
- Closeness (`../../closeness.py`): 7.53% of the largest g expected at 200 digits, 98.7× a typical 200-digit number
  (158,209: 7.45%, 97.5×).

## How it was found

- The cover is a Q = 170,000 cover from the research session's 491 family: the first 88 odd primes and 491 in place of
  463, 89 moduli, M = 2·∏r with 193 digits (bbc8cd8).
  - It came from research's family-B start covers (a9e4a27; fewer uncovered primes just above 170,000).
  - It was walked on the card by `phd/campaign3_gpu/bringup/vecgen491.sh`: covergen at cap 1,250, the card's share by
    md5 mod 3 (partition 0).
  - It was checked by `check_specs.py`: a row counts as covered exactly when gcd(N0 − q, M) > 1.
  - The vector is `q170000_m89r491_p0c00524_v232`, from chunk 524 of gold-g4d's producer, with 1,250 residual primes
    below 170,000.
  - 160,357 is its row 1,193 (counting from 0). So the member's first 1,193 residual rows were all composite, and 73 of
    its rows lie in [158,209, 170,000).
- N = N0 + k·M with k = 19,221,795. That k is inside the vector's top 200-digit window [3,382,594, 20,159,810)
  (`--vector-place top`, the lead's decision of 23 Nov 16:36 UTC).
- It was found on 2026-11-24 at 17:11 UTC by `phd/campaign3_gpu/search_gpu5.py` in vector mode on the Colab G4 runtime
  gold-g4d (RTX PRO 6000 Blackwell). gold-g4d had replaced gold-g4 at Colab's 24 h limit the evening before. The engine
  of that hour:
  - the uarch session's deep sieve: primes up to 10^8, windows of 2^24, row groups of 32, rcta 8 with 512 generate
    threads, and its one-pass generate kernel;
  - keep fraction f = 0.985;
  - Fermat kernel 28 with uarch's 29-bit step and the fused Fermat rounds;
  - near-miss reporting: a member whose first probable-prime row is at or above the record 158,209 is verified on the CPU
    and written to `found.jsonl`.
- The RTX cards had logged 1.60 expected near-misses at or above 158,209 between the two records (0.42 on gold-g4 /
  g4b / g4c until their replacement, 1.17 on gold-g4d / g4e / g4f since). This is the first one found, about on schedule.
- The fleet watcher copied the line off the card at 17:11:16 UTC.
- `found.jsonl` is the search's own output line. `verify_near_miss` had re-checked it on the CPU before writing it: N − p
  composite for every prime p < g, and N − g a probable prime.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-24, this session's container) with `CLAIM_Q=158209`.

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 89 classes and the 1,250 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 14,711 primes p < g: p = 2 by parity, 13,517 by a class modulus r dividing N − p, 586 by trial division, 607 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 89 classes and t = k. It proves N − p composite for every p < g (the 1,193 uncovered ones by failed strong tests). It re-verifies the 21-step ECPP certificate and checks the claims g > 158,209, N < 10^200 and digits ≤ 200: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 14,711 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 200 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
