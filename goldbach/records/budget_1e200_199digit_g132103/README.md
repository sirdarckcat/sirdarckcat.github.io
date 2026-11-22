# g(N) = 132,103 for a 199-digit N (below 10^199)

N = 9894553756108096928234320109107625115977538913651148352553596429516470518067267161989558557857817289922028979503155325438171478377328950812158643210287778862549807965028644573244541378308032537054652

- N is even, has 199 digits, and N < 10^199.
- N − p is composite for every prime p < 132,103 (12,333 primes), and N − 132,103 is prime, so g(N) = 132,103.
- It is the third hit of the campaign that found 125,269 and 133,981 (`../budget_1e200_199digit_g125269/`,
  `../budget_1e200_199digit_g133981/`). Its N lies between theirs, and so does its g, so all three are on the frontier.
- Closeness (`../../closeness.py`): 6.27% of the largest g expected at 199 digits, 81.8× a typical
  199-digit number.

## How it was found

- `phd/campaign3`'s cover (Q = 122,000, 88 classes, M = 2·∏r of 191 digits).
- Residue-swap variant `r200b_q122k_v851`, with 871 residual primes below 122,000. It is number 852 of
  `gen_variants.py base_spec.json out.json 1000 150000000 199`; its N0 is in
  `../../phd/campaign3/variants1000_index.json`.
- N = N0 + k·M with k = 538,125,153.
- Found on 2026-11-22 at about 20:45 UTC by `phd/campaign3_gpu/search_gpu3.py` on the second Colab G4 runtime
  (RTX PRO 6000 Blackwell), skip-frac 0.97, the top half of k first, with `--no-stop` after the 133,981 hit.
- `found.jsonl` is the search's output line. `search.verify_success` had re-checked it on the CPU before writing it.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-22, this session's container).

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 88 classes and the 871 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 12,333 primes p < g: p = 2 by parity, 11,345 by a class modulus r dividing N − p, 497 by trial division, 490 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 88 classes and t = k. It proves N − p composite for every p < g (the 987 uncovered ones by failed strong tests). It re-verifies the 23-step ECPP certificate and checks the claims g > 119,419 and digits ≤ 199: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 12,333 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 199 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
