# g(N) = 157,837 for a 200-digit N (below 10^200)

N = 77674393411106372037785741609148759532201866595844925004069305259376785028458059444586695037279120087424944926035330358836277635018594469510412190238072490182642415096768996238992699953873325601950178

- N is even, has 200 digits, and N < 10^200.
- N − p is composite for every prime p < 157,837 (14,508 primes), and N − 157,837 is prime, so g(N) = 157,837.
- It is the largest g known below 10^200. The previous largest was 146,191 (`../budget_1e200_200digit_g146191/`),
  whose N is smaller, so that one stays on the frontier.
- Closeness (`../../closeness.py`): 7.42% of the largest g expected at 200 digits, 97.2× a typical 200-digit number.

## How it was found

- Q = 150,000 cover on campaign 3's 88 moduli (M = 2·∏r, 191 digits).
  - The vector is `pt_q150k_t528`, a residue-swap variant of the research session's 1,092-row cover `pt_q150k_b_v0`:
    `gen_variants.variants(base, 1500, pair_pool=80)`, minted in this session at 00:06 UTC on 2026-11-23
    (`../../phd/campaign3/variants_q150k_minted_t_index.json`).
  - It leaves 1,094 residual primes below 150,000. It was checked here with `check_specs.py`, which counts a row covered
    exactly when gcd(N0 − q, M) > 1.
  - The member survived 91 more uncovered rows, those in [150,000, 157,837).
- N = N0 + k·M with k = 4,224,399,187.
- Found on 2026-11-23 at about 02:08 UTC by `phd/campaign3_gpu/search_gpu5.py --deep 1` on the Colab G4 runtime gold-g4c
  (RTX PRO 6000 Blackwell):
  - the uarch session's deep sieve: primes up to 10^8, those above 10^6 through its bucketed large-prime stage, windows of
    2^25 members;
  - Fermat kernel 28 with the redundant-limb step `fermat28_step_s1r.cuh` and PTX mad.wide;
  - skip-frac 0.97: each block's emptiest 3%, which hold ≈22.6% of the hit mass at this bound;
  - k in [2^30, 2^32), top first.
  The deep sieve had been in production on this GPU for 54 minutes. It raises the expected hits per GPU-second by ×1.37
  on these cards: tests ×0.75, kept hit mass ×1.43 (`../../phd/campaign3_gpu/README.md`, "Deep sieve").
- It was the first hit of the Q = 150,000 run, after ≈0.75 expected on all the GPUs together
  (`../../phd/campaign3_gpu/TALLY.md`).
- `found.jsonl` is the search's own output line. `search.verify_success` had re-checked it on the CPU before writing it.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-23, this session's container).

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 88 classes and the 1,094 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 14,508 primes p < g: p = 2 by parity, 13,322 by a class modulus r dividing N − p, 588 by trial division, 597 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 88 classes and t = k. It proves N − p composite for every p < g (the 1,185 uncovered ones by failed strong tests). It re-verifies the 24-step ECPP certificate and checks the claims g > 146,191, N < 10^200 and digits ≤ 200: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 14,508 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 200 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
