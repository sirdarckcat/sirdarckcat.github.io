# g(N) = 125,269 for a 199-digit N (below 10^199)

N = 9806519255397062824472765467682451908097625481983877655666179056517874786554091701751807381313324813623198086928774990835290463710654433767962651104495228698940988749379805213193593709075933115577482

- N is even, has 199 digits, and N < 10^199.
- N − p is composite for every prime p < 125,269 (11,757 primes), and N − 125,269 is prime.
- So the least prime p with N − p prime is g(N) = 125,269. The previous largest g known below 10^199
  (and below 10^200) was 119,419 (`../budget_1e200_199digit_g119419/`).
- Closeness (`../../closeness.py`): 5.94% of the largest g expected at 199 digits, 77.5× a typical
  199-digit number.

## How it was found

- `phd/campaign3`'s cover: Q = 122,000, 88 congruence classes, M = 2·∏r (191 digits), and the
  residue-swap variant `r200b_q122k_v367`, whose 874 residual primes q < 122,000 are left uncovered.
  The variant is number 368 of `gen_variants.py base_spec.json out.json 1000 150000000 199`; its N0
  is in `../../phd/campaign3/variants1000_index.json`.
- N = N0 + k·M with k = 533,337,309.
- Found on 2026-11-22 at about 20:31 UTC by `phd/campaign3_gpu/search_gpu3.py` on a Colab G4
  runtime (NVIDIA RTX PRO 6000 Blackwell), about 10 minutes into its run:
  - selection: skip-frac 0.97 (each block's emptiest 3%, 14.2% of the hit mass);
  - order: the top half of k first;
  - work before the hit: 5,308 slices, 5.39·10^9 members.
  - The model expected 0.5 hits for that work.
- `found.jsonl` is the search's own output line. `search.verify_success` had re-checked it on the CPU
  before writing it.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-22, this session's container).

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 88 classes and the 874 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 11,757 primes p < g: p = 2 by parity, 10,838 by a class modulus r dividing N − p, 458 by trial division, 460 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 88 classes and t = k. It proves N − p composite for every p < g (the 918 uncovered ones, 874 below 122,000 and 44 above, by failed strong tests). It re-verifies the 30-step ECPP certificate and checks the claims g > 119,419 and digits ≤ 199: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 11,757 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 199 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
