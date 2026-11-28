# g(N) = 203,659 for a 266-digit N (T(200,000) fixed-gap game)

N = 50820577705701328766772729052116367335044181538390547148992068522880761678012566354998937204455173290684540291792503012152251175949093521760038937584181871822792668131933672670738488676833706777157239724402886068458316020050521525330539144435555464147872960424338782

- N is even and has 266 digits (N ≈ 5.08·10^265).
- N − p is composite for every prime p < 203,659 (18,277 primes), and N − 203,659 is proven prime, so g(N) = 203,659 > 200,000.
- Takes another 14 digits off the 280-digit T(200,000) record. Stays on the Pareto frontier because its g = 203,659 exceeds the smaller 255d and 250d records.
- Closeness (`../../closeness.py`): 5.1567% of the largest g expected at 266 digits, 89.4× a typical 266-digit even number.

## How it was found

- Cover `c0089_r1311` for Q = 200,000: the first 113 odd primes (3 through 619), M = 2·∏r of 259 digits, leaving 1,311 residual primes below 200,000 (1,341 below 203,659).
- Canonical CRT reconstruction: N = N0 + k·M with k = 18,834,171 (stored in `record.json` and `package_stdlib.json`).
- Found on 2026-11-27 by the multi-limb GPU DeepSieve + fused 28-bit Montgomery Fermat scanner (`gpu_g200k_v2.py`) on a GCP Spot A100 GPU (europe-west4-a).

## Proof files

| file | what it holds |
|---|---|
| `N.txt`, `N_minus_g.txt` | decimal `N` and `N − g` |
| `record.json` | `N`, `g`, `k`, `N0`, `M`, `Q = 200000`, the 113 cover classes, and the 1,311 residual primes |
| `evidence.json`, `verify_record.log` | per-offset compositeness witness for every prime p < g (`verify_record.py`): p = 2 by parity, 16,935 by a cover modulus dividing N − p, 607 by trial division, 734 by a failed strong base-2 test |
| `check.log` | `fscan/check.py` recomputing g(N) from N alone (gmpy2) |
| `complement_cert.gp`, `check_cert.log` | PARI/GP 2.15.4 `primecert(N − g)` (38-step ECPP certificate, final small prime `4,746,127,866,386,930,761`) and `primecertisvalid` = 1 |
| `ecpp_check.log` | `goldbach/ecpp_check.py` (patched exact radical-free Goldwasser–Kilian + composite-modulus Jacobian guard, gmpy2 only) re-verifying `complement_cert.gp` against `N_minus_g.txt`: `INDEPENDENT ECPP CHECK PASSED` |
| `package_stdlib.json`, `verify_stdlib.log` | `slop/goldbach/records/verify_record.py` (patched stdlib verifier) rebuilding N from the 113 congruences and `t = k`, proving all 1,341 uncovered complements composite, re-verifying the 38-step ECPP chain, and checking `g > 200,000` and `digits ≤ 266`: `PASS` |
| `crosscheck.gp`, `crosscheck.log` | standalone PARI/GP cross-check: `ispseudoprime(N − p)` false for all 18,277 primes `p < g`, `isprime(g) = 1`, `isprime(N − g) = 1` (proof), and `primecertisvalid(complement_cert.gp) = 1` with top-level binding `cert[1][1] == N − g` |
| `MANIFEST.sha256` | SHA-256 hashes of every file in this folder (excluding `MANIFEST.sha256` itself) |

## Re-verifying (from the `goldbach/` directory)

```sh
R=records/g200k_266digit_g203659
(cd "$R" && sha256sum -c MANIFEST.sha256)
python3 ecpp_check.py "$R/complement_cert.gp" "$R/N_minus_g.txt"
python3 ../slop/goldbach/records/verify_record.py "$R/package_stdlib.json"
gp -q --default colors=no "$R/crosscheck.gp" < /dev/null
```
