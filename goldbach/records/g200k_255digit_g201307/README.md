# g(N) = 201,307 for a 255-digit N (T(200,000) fixed-gap game)

N = 406105245331819281594676662283951055782875062025849376930570201517983495831018672824912894573909355881548800275193871127344927918424187318442362346289368726731332884742018146718860437433955248600016185056738788597014179897411969116841572276015087884805998

- N is even and has 255 digits (N ≈ 4.06·10^254).
- N − p is composite for every prime p < 201,307 (18,084 primes), and N − 201,307 is proven prime, so g(N) = 201,307 > 200,000.
- Takes another 11 digits off the 266-digit T(200,000) record; subsequently superseded on the Pareto frontier by `g200k_250digit_g201667` (smaller N and larger g = 201,667).
- Closeness (`../../closeness.py`): 5.5909% of the largest g expected at 255 digits, 92.9× a typical 255-digit even number.

## How it was found

- Cover `c0463_r1340` for Q = 200,000: the first 109 odd primes (3 through 601), M = 2·∏r of 248 digits, leaving 1,340 residual primes below 200,000 (1,350 below 201,307).
- Canonical CRT reconstruction: N = N0 + k·M with k = 21,388,016 (stored in `record.json` and `package_stdlib.json`).
- Found on 2026-11-27 by the multi-limb GPU DeepSieve + fused 28-bit Montgomery Fermat scanner (`gpu_g200k_v2.py`) on a GCP Spot A100 GPU (us-east1-b).

## Proof files

| file | what it holds |
|---|---|
| `N.txt`, `N_minus_g.txt` | decimal `N` and `N − g` |
| `record.json` | `N`, `g`, `k`, `N0`, `M`, `Q = 200000`, the 109 cover classes, and the 1,340 residual primes |
| `evidence.json`, `verify_record.log` | per-offset compositeness witness for every prime p < g (`verify_record.py`): p = 2 by parity, 16,733 by a cover modulus dividing N − p, 623 by trial division, 727 by a failed strong base-2 test |
| `check.log` | `fscan/check.py` recomputing g(N) from N alone (gmpy2) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)` (35-step ECPP certificate, final small prime `2,490,778,224,859`) and `primecertisvalid` = 1 |
| `ecpp_check.log` | `goldbach/ecpp_check.py` (patched exact radical-free Goldwasser–Kilian + composite-modulus Jacobian guard, gmpy2 only) re-verifying `complement_cert.gp` against `N_minus_g.txt`: `INDEPENDENT ECPP CHECK PASSED` |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (patched stdlib verifier) rebuilding N from the 109 congruences and `t = k`, proving all 1,350 uncovered complements composite, re-verifying the 35-step ECPP chain, and checking `g > 200,000` and `digits ≤ 255`: `PASS` |
| `crosscheck.gp`, `crosscheck.log` | standalone PARI/GP cross-check: `ispseudoprime(N − p)` false for all 18,084 primes `p < g`, `isprime(g) = 1`, `isprime(N − g) = 1` (proof), and `primecertisvalid(complement_cert.gp) = 1` with top-level binding `cert[1][1] == N − g` |
| `MANIFEST.sha256` | SHA-256 hashes of every file in this folder (excluding `MANIFEST.sha256` itself) |

## Re-verifying (from the `goldbach/` directory)

```sh
R=records/g200k_255digit_g201307
(cd "$R" && sha256sum -c MANIFEST.sha256)
python3 ecpp_check.py "$R/complement_cert.gp" "$R/N_minus_g.txt"
python3 ../slop/goldbach/records/verify_record.py "$R/package_stdlib.json"
gp -q --default colors=no "$R/crosscheck.gp" < /dev/null
```
