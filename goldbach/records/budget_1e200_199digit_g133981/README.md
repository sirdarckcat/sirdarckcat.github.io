# g(N) = 133,981 for a 199-digit N (below 10^199)

N = 9947429524999730315009926113700406118030140654287882038795827785248798203256901592090230783397036111602662774040944866933428352345248439148243673698521122303962860788030113522996748663335382195498052

- N is even, has 199 digits, and N < 10^199.
- N − p is composite for every prime p < 133,981 (12,493 primes), and N − 133,981 is prime.
- So the least prime p with N − p prime is g(N) = 133,981. It is the largest g known below 10^200.
  The same campaign found 125,269 eight minutes earlier (`../budget_1e200_199digit_g125269/`); before
  that the largest was 119,419 (`../budget_1e200_199digit_g119419/`).
- Closeness (`../../closeness.py`): 6.36% of the largest g expected at 199 digits, 82.9× a typical
  199-digit number.

## How it was found

- `phd/campaign3`'s cover: Q = 122,000, 88 congruence classes, M = 2·∏r (191 digits), and the
  residue-swap variant `r200b_q122k_w175` of the second family, whose 870 residual primes q < 122,000
  are left uncovered. The family is `gen_variants.variants(base, 6000, kmax=150000000, ceiling=199,
  pair_pool=120)` minus the first family's N0s, |U| ≤ 872 kept; its N0 is in
  `../../phd/campaign3/variants_w_index.json`.
- N = N0 + k·M with k = 541,000,854.
- Found on 2026-11-22 at about 20:38 UTC by `phd/campaign3_gpu/search_gpu3.py` on the second Colab G4
  runtime (NVIDIA RTX PRO 6000 Blackwell), about 9 minutes into its run:
  - selection: skip-frac 0.97 (each block's emptiest 3%, 14.2% of the hit mass);
  - order: the top half of k first;
  - work before the hit: 4,135 slices, 3.90·10^9 members.
  - The model expected 0.4 hits for that work.
- `found.jsonl` is the search's own output line. `search.verify_success` had re-checked it on the CPU
  before writing it.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-22, this session's container).

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 88 classes and the 870 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 12,493 primes p < g: p = 2 by parity, 11,482 by a class modulus r dividing N − p, 492 by trial division, 518 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 88 classes and t = k. It proves N − p composite for every p < g (the 1,010 uncovered ones, 870 below 122,000 and 140 above, by failed strong tests). It re-verifies the 31-step ECPP certificate and checks the claims g > 119,419 and digits ≤ 199: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 12,493 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 199 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
