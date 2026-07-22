# PhD Research Log — Extremal Least Goldbach Summands

Programme: *Extremal Least Goldbach Summands* (4-year proposal, record snapshot 2026-07-22).
Student log, year 3 — project kickoff with delegated subagent execution.

## Record board (project incumbents at kickoff, 2026-07-22)

| Game | Incumbent | Value | Status |
|---|---|---|---|
| Height H (Game 1) | 2,692-digit N (813-congruence cover, k=14) | g = 1,134,871 | audit in progress |
| Threshold T(100,000) (Game 2) | N₁₉₇ ≈ 6.939·10^196 (197 digits) | g = 107,719 | audit in progress |
| Budget R(10^199) (Game 3) | same N₁₉₇ | g = 107,719 | audit in progress |

Grand-slam target: N < N₁₉₇ **and** g(N) ≥ 1,134,877 — aspirational (O5);
RESULTS.md notes covering methods leave ≥20,000 residuals under a ≤192-digit
modulus (success density e^−400), so O5 requires mechanisms beyond static covers (WP7).

## Programme status

| WP | Scope | Status |
|---|---|---|
| WP1 (E1) | Independent audit of both incumbents + adversarial mutation tests | **delegated** — running |
| WP2/WP6 (E2/E8) | Cover frontier Q=107,720; density calibration on this box | **delegated** — running |
| WP8 (E10) | Incremental record campaign: g > 107,719 with N < 10^199; N < N₁₉₇ if lucky | pending covers |
| Certification | PARI/GP 2.15.4 installed for ECPP; ecpp_check.py as independent verifier | ready |

## Log

### 2026-07-22 — kickoff
- Surveyed inherited machinery (PR #15/#16): cover.py, anneal.py, gen_variants.py,
  search.py, verify_record.py, mega_verify.py, ecpp_check.py, package_record.py; both
  record artifact directories present.
- Environment: 4 cores, Python 3.11.15, gmpy2 2.3.1, numpy 2.4.6, sympy 1.14.0,
  PARI/GP 2.15.4 (installed today; prior campaign certificates were produced with gp).
- Delegated WP1 audit and WP2/WP6 frontier+calibration to two parallel subagents.
- Campaign design decision: one E10 campaign with Q = 107,720 (covers every prime
  ≤ 107,719) so that ANY hit strictly beats R(10^199) = 107,719; hits are ranked by N so
  a sub-N₁₉₇ hit would also take T(100,000). Variants searched breadth-first in k to
  bias toward small N.
