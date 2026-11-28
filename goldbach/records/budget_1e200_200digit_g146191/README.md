# g(N) = 146,191 for a 200-digit N (below 10^200)

N = 57029127813410048199078859757119177693798484018006261321188027402909552678291951327166757524531855646414922244577615335610931976048573823145033500892678855456399836830384244990181982269493502895078088

- N is even, has 200 digits, and N < 10^200.
- N − p is composite for every prime p < 146,191 (13,523 primes), and N − 146,191 is prime, so g(N) = 146,191.
- It is the largest g known below 10^200. The previous largest was 133,981 (`../budget_1e200_199digit_g133981/`),
  whose N is smaller (199 digits), so that one stays on the frontier.
- Closeness (`../../closeness.py`): 6.88% of the largest g expected at 200 digits, 90.1× a typical 200-digit number.

## How it was found

- Q = 140,000 cover on campaign 3's 88 moduli (M = 2·∏r, 191 digits): the Lean session's vector `r200_q140k_c_v77`
  (goldbach/phd/cap200/specs_q140000_top128.json at 6518249 on ccr-36ca7b46-8twf14). It leaves 1008 residual primes below
  140,000, and was checked here independently (congruences, M, residual list).
- N = N0 + k·M with k = 3,101,585,871.
- Found on 2026-11-22 at about 23:08 UTC by `phd/campaign3_gpu/search_gpu5.py` on the Colab G4 runtime gold-g4b
  (RTX PRO 6000 Blackwell):
  - the uarch session's GPU sieve and Fermat kernel 28;
  - skip-frac 0.97 (each block's emptiest 3%, 15.6% of the hit mass);
  - k in [2^30, 2^32), top first.
- It was the first hit of the Q = 140,000 run. The model expected 0.58 hits on this GPU's logged batches, and ~1.3 on all
  the Q = 140,000 GPUs together.
- `found.jsonl` is the search's own output line. `search.verify_success` had re-checked it on the CPU before writing it.

## Proof files

Made by `phd/campaign3_gpu/certify_c3.sh` (2026-11-22, this session's container).

| file | what it holds |
|---|---|
| `record.json` | N, g, k, N0, M, Q, the 88 classes and the 1008 residual primes (`package_record.py`) |
| `evidence.json` | a compositeness witness for N − p for each of the 13,523 primes p < g: p = 2 by parity, 12,451 by a class modulus r dividing N − p, 528 by trial division, 543 by a failed strong base-2 test (definite for a composite) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)`, an ECPP certificate, and `primecertisvalid` = 1 |
| `N_minus_g.txt`, `ecpp_check.log` | `ecpp_check.py` re-verifies the certificate without PARI (gmpy2 only): INDEPENDENT ECPP CHECK PASSED |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (Python standard library only) rebuilds N from the 88 classes and t = k. It proves N − p composite for every p < g (1,071 uncovered ones by failed strong tests). It re-verifies the 25-step ECPP certificate and checks the claims g > 133,981, N < 10^200 and digits ≤ 200: PASS |
| `direct_check.log` | gmpy2 from N and g alone: N − p composite for all 13,523 primes p < g, N − g a probable prime |
| `crosscheck.gp`, `crosscheck.log` | PARI from N and g alone: `ispseudoprime(N − p)` false for every prime p < g, `isprime(g)` = 1, `isprime(N − g)` = 1 (a proof), N even, 200 digits |
| `found.jsonl` | the search's output line |
| `MANIFEST.sha256` | hashes of the files above |
