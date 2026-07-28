# Toy CRT-code lattice decoding vs. the Johnson radius

Empirical study of where practical LLL succeeds relative to the proven
Johnson-type list-decoding radius for Chinese Remainder codes
(GSS FOCS 2000 / Howgrave-Graham formulation). Implementation:
[`decoder.py`](decoder.py); raw data: [`results.json`](results.json).

## Setup (exact values)

| parameter | value |
|---|---|
| positions | odd primes 3 <= p < 300, n = 61 |
| ln M = sum ln p | 276.332 |
| B (message bound) | 10^12, ln B = 27.631 |
| Johnson radius A_J = sqrt(ln B ln M) | **87.380** |
| lattice degrees tried per instance | ell in {12, 20, 30}, z = max(1, round(ell * A/ln M)) |
| trials per rho | 20 (predeclared), seed tag `v1` |
| LLL backend | python-flint 0.9.0 (FLINT `fmpz_mat.lll`, delta = 0.99, eta = 0.51) |
| root extraction | FLINT `fmpz_poly.factor` on **all** ell+1 reduced rows |

Instances plant m* uniform in [B/2, B), reveal m* mod p on a uniformly random
subset grown greedily to mass >= rho * A_J (mean overshoot ~ +0.03 A_J), and set
uniformly random *wrong* residues elsewhere. Sanity checks passed before the
sweep: brute-force verification of instance generation / agreement mass /
CRT lift on a rho = 1.0 instance, and 5/5 planted recovery at rho = 1.4.

## Main table (predeclared sweep, 20 trials/rho, 3 ells each)

| rho (target A/A_J) | recovery % | any-solution % | mean best-agreement/A_J | mean realized planted A/A_J | recovered by ell 12/20/30 |
|---:|---:|---:|---:|---:|:---:|
| 0.70 | 0 | 0 | 0.000 | 0.724 | 0/0/0 |
| 0.80 | 0 | 0 | 0.000 | 0.817 | 0/0/0 |
| 0.90 | 0 | 0 | 0.000 | 0.935 | 0/0/0 |
| 1.00 | 60 | 0 | 0.625 | 1.033 | 0/4/12 |
| 1.10 | 100 | 0 | 1.126 | 1.126 | 20/20/20 |
| 1.25 | 100 | 0 | 1.278 | 1.278 | 20/20/20 |

Conventions: *recovery* = planted m* among the integer roots for **any** ell;
*any-solution* = some root m != m*, |m| <= B, with agreement mass >= 0.9 rho A_J;
*best-agreement* = 0 when no roots were found (below threshold the reduced basis
yields **zero** integer roots, so the mean at rho = 1.00 is 0.60 x mean planted
mass of the recovered trials). Full sweep: 28.5 s wall on 4 cores.

## Empirical 50% threshold

**rho\* = 0.983** (linear interpolation between rho = 0.90 at 0% and
rho = 1.00 at 60%, in units of the *target* ratio). This nominally sub-Johnson
value is entirely an artifact of the greedy overshoot: realized planted mass at
rho = 1.00 averages 1.033 A_J. Measured against **realized** agreement mass the
transition is razor sharp and strictly above the Johnson radius: across all 120
predeclared instances, every ell = 30 decode with planted mass <= 1.0271 A_J
failed and every one with >= 1.0278 A_J succeeded, i.e. **A\*/A_J ~ 1.028
(ell = 30)**.

## Threshold vs. finite-dimension theory

Determinant-bound prediction (Howgrave-Graham sufficient condition with the
shortest vector at the determinant scale, no LLL slop):
A_min(ell) = min_z [z(z+1) ln M + ell(ell+1) ln B] / [2(ell+1) z].

| ell | theory A_min/A_J (opt. z) | empirical cutoff interval (realized A/A_J) |
|---:|---:|:---|
| 12 | 1.0825 (z=4) | (1.0565, 1.1081) |
| 20 | 1.0541 (z=6) | (1.0445, 1.0507) |
| 30 | 1.0354 (z=10) | (1.0271, 1.0278) |
| 45 | 1.0238 (z=14) | (1.0141, 1.0293) — supplementary, below |

Practical LLL lands ~1% *below* the sufficient-condition bound at each ell
(the usual "Coppersmith methods slightly beat their proof" effect: delta = 0.99
LLL behaves far better than its worst-case factor and the HG condition is
sufficient, not necessary) but tracks the finite-ell determinant bound
essentially exactly, converging to A_J from above like ~1 + c/ell.

**Supplementary ell = 45** (post-hoc, beyond the predeclared grid; 10
trials/rho, seed tag `supp45`): 0/10 at rho = 0.90, **0/10 at rho = 0.95**
(including an instance with realized mass 1.0041 A_J), 7/10 at rho = 1.00
(cutoff between 1.0141 and 1.0293) — confirms the trend is finite-dimension
slop shrinking toward A_J, not penetration below it.

## Solution abundance below the radius

These sub-Johnson instances are solution-abundant: the first-moment heuristic
E[#m < B with mass >= 0.9 rho A_J] ~ exp(ln B (1 - 0.81 rho^2)) gives ~1.7e7
(rho = 0.70), ~6e5 (0.80), ~1.3e4 (0.90), ~1.9e2 (1.00) valid targets for the
any-solution criterion. LLL found **none of them**: across all 390 decodes of
the study (predeclared + supplementary), every integer root ever extracted was
the planted m* itself (in the predeclared sweep, 131 of the 136 successful
decodes had m* in the shortest reduced row, occasionally as deep as row rank
16), and below the finite-ell threshold the reduced rows contain no
integer-rooted polynomial at all.

## Conclusion

No: practical lattice reduction does not beat the Johnson radius on
solution-abundant CRT instances — at toy scale it does not even reach it,
succeeding only above a sharp finite-dimension threshold at realized agreement
~1.028 A_J for ell = 30 (~1.02 A_J at ell = 45), about 1% below the provable
finite-ell bound and converging to A_J from above as ell grows. Below the
threshold the failure mode is total: LLL's short vectors are integer-rootless
polynomials, returning not the planted message, nor any of the 10^2-10^7
existing high-agreement alternatives. The Johnson radius thus behaves as a hard
practical barrier for this lattice family, with the only slack being the
well-known ~1% grace of LLL over its worst-case guarantee.

## Reproduce

```
python3 decoder.py --selftest        # LLL + convention invariants (incl. pure-Python fallback vs FLINT)
python3 decoder.py --sanity          # brute-force instance check + rho=1.4 recovery (must be 5/5)
python3 decoder.py --sweep --trials 20 --jobs 4 --out results.json
```

Deterministic per-instance seeds (`toycrt:v1:{rho}:{trial}`). Mean LLL time:
9 ms (ell=12), 86 ms (ell=20), 0.77 s (ell=30), ~6 s (ell=45, d=46,
~6000-bit entries).
