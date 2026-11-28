# g(N) = 210,631 for a 280-digit N (T(200,000) fixed-gap game)

N = 3040503868090367486446557743270979461856916654237398211944686010860055500751349555516781504196723012444711828785256982528391281804589976354772407331457012987865269015449889189836471157120163264573934853511405498032512479390169718241151621091622828324310577120488382143366312956188

- N is even and has 280 digits (N ≈ 3.04·10^279).
- N − p is composite for every prime p < 210,631 (18,862 primes), and N − 210,631 is proven prime, so g(N) = 210,631 > 200,000.
- First GPU step below the 319-digit CPU record (g = 207,307), taking 39 digits off T(200,000) and taking 319d off the frontier. Stays on the Pareto frontier because its g = 210,631 exceeds the smaller 266d, 255d, and 250d records.
- Closeness (`../../closeness.py`): 4.7801% of the largest g expected at 280 digits, 87.1× a typical 280-digit even number.

## How it was found

- Cover `c0060_r1283` for Q = 200,000: the first 118 odd primes (3 through 653), M = 2·∏r of 273 digits, leaving 1,283 residual primes below 200,000 (1,392 below 210,631).
- Canonical CRT reconstruction: N = N0 + k·M with k = 10,255,023 (stored in `record.json` and `package_stdlib.json`).
- Found on 2026-11-27 by the multi-limb GPU DeepSieve + fused 28-bit Montgomery Fermat scanner (`gpu_g200k_v2.py`) on a GCP Spot A100 GPU (us-central1-a).

## Proof files

| file | what it holds |
|---|---|
| `N.txt`, `N_minus_g.txt` | decimal `N` and `N − g` |
| `record.json` | `N`, `g`, `k`, `N0`, `M`, `Q = 200000`, the 118 cover classes, and the 1,283 residual primes |
| `evidence.json`, `verify_record.log` | per-offset compositeness witness for every prime p < g (`verify_record.py`): p = 2 by parity, 17,469 by a cover modulus dividing N − p, 645 by trial division, 747 by a failed strong base-2 test |
| `check.log` | `fscan/check.py` recomputing g(N) from N alone (gmpy2) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)` (38-step ECPP certificate, final small prime `51,624,727,238,317`) and `primecertisvalid` = 1 |
| `ecpp_check.log` | `goldbach/ecpp_check.py` (patched exact radical-free Goldwasser–Kilian + composite-modulus Jacobian guard, gmpy2 only) re-verifying `complement_cert.gp` against `N_minus_g.txt`: `INDEPENDENT ECPP CHECK PASSED` |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (patched stdlib verifier) rebuilding N from the 118 congruences and `t = k`, proving all 1,392 uncovered complements composite, re-verifying the 38-step ECPP chain, and checking `g > 200,000` and `digits ≤ 280`: `PASS` |
| `crosscheck.gp`, `crosscheck.log` | standalone PARI/GP cross-check: `ispseudoprime(N − p)` false for all 18,862 primes `p < g`, `isprime(g) = 1`, `isprime(N − g) = 1` (proof), and `primecertisvalid(complement_cert.gp) = 1` with top-level binding `cert[1][1] == N − g` |
| `MANIFEST.sha256` | SHA-256 hashes of every file in this folder (excluding `MANIFEST.sha256` itself) |

## Re-verifying (from the `goldbach/` directory)

```sh
R=records/g200k_280digit_g210631
(cd "$R" && sha256sum -c MANIFEST.sha256)
python3 ecpp_check.py "$R/complement_cert.gp" "$R/N_minus_g.txt"
python3 ../slop/goldbach/records/verify_record.py "$R/package_stdlib.json"
gp -q --default colors=no "$R/crosscheck.gp" < /dev/null
```
