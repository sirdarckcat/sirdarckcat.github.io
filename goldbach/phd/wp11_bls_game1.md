# WP11 — Game 1 without ECPP: certified Goldbach deserts by construction

> **After the merge (2026-11-21).** A second session found this
> construction independently the same morning (`../proth/`, WP12), set
> the current incumbent g = 2,000,269, and the two branches were merged.
> What that changes for a reader of this memo:
> - **Pipeline.** New work uses `proth/desert.py` (lazy cover ~9% shorter,
>   sieve to 10⁹). This memo's own code — `bls_search.py`, `full_cover.py`,
>   `density_probe.py`, `ladder.py` — was retired at the merge and is in
>   the history at commit `6c66bcd`. The cover, search, density-probe and
>   ladder numbers in §2–§4 were produced by that code (the search by
>   `bls_search.py` at `4adaa4d`). The verification numbers come from
>   `bls/verify_bls_record.py` (kept), from an uncommitted tamper harness
>   whose six cases are in `proth/tamper_test.py`, and from an inline GMP
>   BPSW check. The §4 ladder is ~30% pessimistic next to
>   `proth/README.md`.
> - **Verification.** `bls/verify_bls_record.py` and `bls/xverify.py` stay
>   as the independent second stack; all three records pass both stacks
>   and PARI.
> - **§3, "a ~1%-tail draw".** This search and the other session's were
>   one progression (joint p = 0.046); see WP12 §6 for that and for the
>   out-of-sample probe (6 primes against 4.62 expected).
> - Reviews: `crossreview_2ce9e63a.md` (by this memo's author) and
>   `crossreview_8ffe9d7a.md`; decisions: `merge_2026-11-21.md`.

Status: 2026-11-21. Prompted by the user's challenge after WP10: if
frontier-level research is now possible, find a non-brute-force way to
move faster. Code: `goldbach/bls/` (cover, search, independent verifier,
cost ladder).

## 0. Result in one paragraph

Game 1 (largest g, N unbounded) was walled by certification. Every record
proved its prime complement P = N − g with ECPP, which caps g near 2.5M
(SoK §6). The repo flagged the escape as *"arranging N−q to have
Pocklington-friendly form while satisfying the cover congruences …
nobody knows how to intersect the two constraint systems"* (SoK §6,
§7.2; PROPOSAL_NEXT_CAMPAIGNS). **They intersect by plain CRT.**

- The cover modulus is odd, so N mod 2^(n+1) is free. Setting
  N ≡ g + 1 + 2^n (mod 2^(n+1)) makes F = 2^n exactly divide P − 1.
- With F³ > P, the Brillhart–Lehmer–Selfridge theorem proves P prime from
  one modexp.
- The price is that P has ≈1.5× the cover's digits.
- Combined with the paper's full covers, which leave no residuals,
  g(N) = g is certified by congruences plus one modexp. There is no ECPP,
  no PRP assumption and no GRH.

The Game-1 ceiling is then set by modexp cost instead of ECPP: about 5M in
13 h and 10^7 in about 4 days on this 4-core box, against the ~2.5M ECPP
forecast.

## 1. The certificate (proved here, used as stated)

Let P − 1 = F·R with F = 2^n, R odd, and F³ > P ≥ F².

- **Pocklington.** Suppose a^((P−1)/2) ≡ −1 (mod P). Then a^(P−1) ≡ 1 and
  gcd(a^((P−1)/2) − 1, P) = gcd(−2, P) = 1, so every prime p | P has
  2^n | ord_p(a) | p − 1, that is, p ≡ 1 (mod F).
- **BLS (N^(1/3)).** If P were composite, all its prime factors would
  exceed F > P^(1/3), so it would be exactly (uF+1)(vF+1) with u, v ≥ 1.
  From uvF² < P < F³ we get uv < F. We also get u + v ≤ uv + 1 ≤ F, and
  u + v = F would force P = (F+1)(F²−F+1) = F³+1 > P. So the base-F
  digits of P are c₂ = uv, c₁ = u+v and c₀ = 1, and c₁² − 4c₂ = (u−v)² is
  a square. **Hence: if c₁² − 4c₂ is not a square, P is prime.** ∎

This is a certificate in the ordinary sense: (n, a). A verifier redoes one
modexp, which is the same cost as checking a Proth prime.

## 2. Pipeline and its validation

| piece | what it does | validation |
|---|---|---|
| `bls/full_cover.py` | increasing-order greedy full cover of the odd primes < Q, as in the paper | **reproduces the paper's Table tab:results exactly**: Q=10^5 → 356 congruences, r_max 2,393, 1,020 digits. Q=10^6 → 1,762 / 15,083 / 6,480. Q=10^7 → 9,853 / 102,983 / 44,599 (vs. 44,600: rounding) |
| `bls/bls_search.py` | picks g = least uncovered prime ≥ Q; CRT with N ≡ g+1+2^n (mod 2^(n+1)); sieves P₀ + i·L by primes to S; runs parallel Euler tests with a non-residue base; applies the BLS square check | shakedown at Q=10^5: 122 tests against 123 predicted (ln P / (e^γ ln S)) |
| `bls/verify_bls_record.py` | stdlib-only; product-tree CRT (a different algorithm from the search's loop); marks every class progression a_r + kr below g; Python-int modexp; shares no code with the search | **tamper test, 6/6 rejected for the right reason**: non-residue base replaced by a residue; neighbouring offset (composite P); one congruence dropped; class changed mod 3 or mod 17 (uncovered primes); stale N. One bug was caught at record scale: Python 3.13's 4,300-digit cap on int-to-string conversion crashed the check, so the verifier lifts the cap |
| `bls/density_probe.py` | exhaustive prime count over the first K sieve survivors, compared with the model | z = +0.76 and −0.43 (§3) |

## 3. Records

- **Shakedown at Q = 10^5 (validation, not a record).** N has 1,536
  digits and g(N) = 100,069, at offset i = 291 after 122 tests (123
  predicted). The verifier passes in 0.2 s. As extra legs, BPSW agrees on
  P, and all N − q for the first 2,000 odd q were checked composite by
  brute force. Committed as the verifier's test vector:
  `bls/testvec_q1e5.json`.
- **New Game-1 record: g(N) = 1,200,109**, beating 1,157,341. N has
  11,263 digits. It needs 2,004 cover congruences (r ≤ 17,431) and
  n = 12,475, and the hit came at offset i = 6,781 with BLS base 7. See
  `records/bls_game1_11263digit_g1200109/`. Verification:
  - the independent verifier passes in 87 s of pure-Python arithmetic;
  - GMP BPSW agrees on P;
  - the congruences recheck under GMP.

  Certifying the previous record's complement took ~2 h of ECPP, plus
  ~2 h of re-verification and ~2 h of APR-CL.
- **The discovery took 3,472 tests against 762 predicted**, on 4 cores in
  76 min. That is a ~1%-tail draw for an exponential wait. Because every
  rung of §4 rests on the density model, the model was measured directly
  (`bls/density_probe.py`, exhaustive tests, no early stop):

  | Q | P digits | tests | primes | model | z |
  |---|---|---|---|---|---|
  | 10^5 | 1,536 | 6,000 | 54 | 48.7 | +0.76 |
  | 3·10^5 | 3,670 | 2,400 | 8 | 9.3 | −0.43 |

  The model holds, and the sieve was audited separately: survivors are
  rough, kills are real, and P is coprime to M. Ladder costs are
  expectations; per the SoK's variance rule, budget individual rungs at
  ~3×.

## 4. The ladder (measured costs, `bls/ladder.py`)

One test costs one modexp a^((P−1)/2) mod P. The single-core GMP time fits
7.64·10⁻⁹·d^2.21 s over four points from 11.5k to 67k digits. Expected
tests are ln P / (e^γ ln S), with S = 2·10^8 below Q = 5M and S = 10^10
above.

| Q (≈ g) | congruences | M digits | P digits | s/test | tests | core-days | this 4-core box |
|---|---|---|---|---|---|---|---|
| 1.2·10^6 | 2,005 | 7,504 | 11,265 | 7 | 762 | 0.06 | 0.3 h |
| 2·10^6 | 2,931 | 11,523 | 17,293 | 17 | 1,170 | 0.23 | 1.4 h |
| 5·10^6 | 5,800 | 24,753 | 37,138 | 91 | 2,085 | 2.2 | 13 h |
| 10^7 | 9,853 | 44,600 | 66,909 | 335 | 3,757 | 14.6 | 3.6 d |
| **16,045,849** | 14,204 | 66,816 | 100,233 | 816 | 5,628 | 53 | 13 d |
| 10^8 | 60,627 | 327,455 | 491,191 | 27,149 | 27,578 | 8,666 | — |

- **The bold rung** is the largest known prime gap with PRP endpoints
  (RESULTS.md). A certified Goldbach desert past it would be longer than
  every known prime gap, proven endpoints or not.
- **GMP is the slow way to do this arithmetic.** GWNUM-class FFT code
  (LLR, PFGW) runs about 5–10× faster from ~10^5 digits up, and the
  search is ticket-parallel exactly like the existing fleet. That brings
  10^7 to under a day and 1.6·10^7 to days on the GPU fleet. 10^8 becomes
  a modest distributed campaign, about 3 core-years with GWNUM.
- **Compared with SoK §6's Game-1 forecast**, the ECPP ceiling of ≈2.5M is
  passed on this box in under a day. The "fastECPP-class, months on a
  cluster" band near 5·10^7 is reached instead by a ticket-parallel
  search that needs no certificate chain.
- **Second-order lever, not taken here.** A near-full cover with a tiny
  residual set (E ≈ 1–2) trades ~half the endgame moduli for residual
  Fermat tests. At Q = 10^6 the two costs come out comparable, so the full
  cover is kept for simplicity.

## 5. What this does not change

The threshold and budget games, T(10^5) and R(10^200), are search-bound:
E ≈ 25 at 150 digits, and their ECPP certificates take minutes. Nothing
here touches them. Their non-brute-force doors are still the ones WP8/WP9
identified:

- the rounding gap (0–2.6 nats);
- CRT list-recovery beyond the Johnson radius (WP3);
- an out-of-grammar compositeness mechanism.

The lesson is narrower: Game 1's wall was an artifact of proving
whatever prime the search produced. Choosing the prime's *form* first
removed it, and no new mathematics was needed.
