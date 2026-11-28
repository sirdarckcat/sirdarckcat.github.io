# g(N) = 201,667 for a 250-digit N (T(200,000) fixed-gap game)

N = 6790364865826687937949763213137580601259218374843933226955250954763327939629051949969863412555517888602039161158253596200129782395054377602487632736998326315647089865606703349538699221282572467523839331841948431675296509737578827220878835884711700828

- N is even and has 250 digits (N ≈ 6.79·10^249).
- N − p is composite for every prime p < 201,667 (18,113 primes), and N − 201,667 is proven prime, so g(N) = 201,667 > 200,000.
- Current T(200,000) record: smallest known even N with g(N) ≥ 200,000 (69 digits below the 319-digit CPU record g = 207,307, and dominating `g200k_255digit_g201307`). On the Pareto frontier.
- Closeness (`../../closeness.py`): 5.8358% of the largest g expected at 250 digits, 95.2× a typical 250-digit even number.

## How it was found

- Cover `c0382_r1354` for Q = 200,000: the first 107 odd primes (3 through 593), M = 2·∏r of 242 digits, leaving 1,354 residual primes below 200,000 (1,370 below 201,667).
- Canonical CRT reconstruction: N = N0 + k·M with k = 128,743,795 (stored in `record.json` and `package_stdlib.json`).
- Found on 2026-11-27 by the multi-limb GPU DeepSieve + fused 28-bit Montgomery Fermat scanner (`gpu_g200k_v2.py`) on a GCP Spot A100 GPU (us-central1-c).

## Proof files

| file | what it holds |
|---|---|
| `N.txt`, `N_minus_g.txt` | decimal `N` and `N − g` |
| `record.json` | `N`, `g`, `k`, `N0`, `M`, `Q = 200000`, the 107 cover classes, and the 1,354 residual primes |
| `evidence.json`, `verify_record.log` | per-offset compositeness witness for every prime p < g (`verify_record.py`): p = 2 by parity, 16,742 by a cover modulus dividing N − p, 635 by trial division, 735 by a failed strong base-2 test |
| `check.log` | `fscan/check.py` recomputing g(N) from N alone (gmpy2) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)` (37-step ECPP certificate, final small prime `40,554,065,681,690,347`) and `primecertisvalid` = 1 |
| `ecpp_check.log` | `goldbach/ecpp_check.py` (patched exact radical-free Goldwasser–Kilian + composite-modulus Jacobian guard, gmpy2 only) re-verifying `complement_cert.gp` against `N_minus_g.txt`: `INDEPENDENT ECPP CHECK PASSED` |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (patched stdlib verifier) rebuilding N from the 107 congruences and `t = k`, proving all 1,370 uncovered complements composite, re-verifying the 37-step ECPP chain, and checking `g > 200,000` and `digits ≤ 250`: `PASS` |
| `crosscheck.gp`, `crosscheck.log` | standalone PARI/GP cross-check: `ispseudoprime(N − p)` false for all 18,113 primes `p < g`, `isprime(g) = 1`, `isprime(N − g) = 1` (proof), and `primecertisvalid(complement_cert.gp) = 1` with top-level binding `cert[1][1] == N − g` |
| `MANIFEST.sha256` | SHA-256 hashes of every file in this folder (excluding `MANIFEST.sha256` itself) |

## Re-verifying (from the `goldbach/` directory)

```sh
R=records/g200k_250digit_g201667
(cd "$R" && sha256sum -c MANIFEST.sha256)
python3 ecpp_check.py "$R/complement_cert.gp" "$R/N_minus_g.txt"
python3 ../slop/goldbach/records/verify_record.py "$R/package_stdlib.json"
gp -q --default colors=no "$R/crosscheck.gp" < /dev/null
```
