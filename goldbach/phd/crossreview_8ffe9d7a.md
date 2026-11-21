# Cross-review: branch `ccr-2ce9e63a-hn0fuw` against `ccr-8ffe9d7a-4ni11u`

> **Status after the merge (2026-11-21).** Written before the two branches
> were merged; "this branch" is `ccr-2ce9e63a-hn0fuw`, its memo is now
> WP12 and its records are in `goldbach/records/`. The other session
> checked this review and found three inaccuracies, corrected in place
> and marked ⟲: (1) their mutation-test harness was never committed, only
> its results; (2) this review read their head `98efe92`, and three items
> it lists as open had already been fixed in their `6c66bcd`; (3) Chang's
> exponent 12/5 is a literature citation not re-checked by either
> session. Their own review is `crossreview_2ce9e63a.md`; what was agreed
> is in `merge_2026-11-21.md`.

2026-11-21. Requested by the user: review the results of this branch
(`ccr-2ce9e63a-hn0fuw`, commits `e1e8d0f`…`63746e6`) against the branch
`ccr-8ffe9d7a-4ni11u` (head `98efe92`: `54f5e5c` WP10, `4adaa4d` WP11
pipeline, `647efbf`, `98efe92` record). The two branches share no commits
beyond master; they were given the same starting point and worked
separately. Everything below was re-run here; scripts are named.

## 1. Headline

Both sessions arrived at the same three conclusions:

1. A proof of GRH would not move any record ("no lever moves" there,
   "constants, not walls" here).
2. The certification wall of the height game falls to one line of CRT:
   write N − g = 1 + 2ⁿ·R, let the cover congruences act on R, and prove
   N − g prime by the Brillhart–Lehmer–Selfridge N−1 test with F = 2ⁿ >
   (N − g)^(1/3). Both chose complete covers.
3. Both built a pipeline and certified **g(N) = 1,200,109** at 11,263
   digits — for *two different integers N*.

Independent convergence on the construction, on n = 12,475, and on the
value of g (forced: same deterministic cover) is the strongest evidence
either branch has that the method is right. Nothing in either branch
contradicts the other. The differences are complementary and are listed
in §4; four statements are stale or incomplete once the branches are read
together (§5).

## 2. Cross-verification (every record, every verifier)

Each branch has its own stdlib verifier, written without sight of the
other. `interop.py` converts record formats in both directions.

| record | `proth/verify.py` (this branch) | `bls/verify_bls_record.py` (theirs) | PARI/GP: own N−1 certificate, `isprime`, brute-force scan of all primes < g |
|---|---|---|---|
| this branch, g = 1,200,109, 11,263 d (sha256 of decimal `cf388b5b…`) | PASS | **PASS**, 89 s (n := 12,477, i = 696; their CRT rebuild equals the stored N) | PASS |
| this branch, g = 2,000,269, 15,595 d (`28604428…`) | PASS | **PASS**, 233 s (n := 17,274, i = 326) | PASS |
| theirs, g = 1,200,109, 11,263 d (`7bdbe05a…`) | **PASS**, 5.5 s | PASS, 89 s (re-run here) | **PASS** (⟲ at `98efe92` their branch had GMP BPSW only; their `6c66bcd` added this same PARI leg) |
| their Q = 10⁵ test vector, g = 100,069, 1,536 d | **PASS** | PASS (theirs) | — |

Bold = a check that did not exist before this review. Hashes are of the
decimal string of N (no newline); the `SHA256SUMS`/`MANIFEST` files hash
the files. So all three
records are now confirmed by two independently written proof checkers
and by PARI's independent N−1 proof.

⟲ Their memo reports a 6-case mutation test of their verifier (6/6
rejected; the harness itself was not committed). This branch had none. `tamper_test.py` now applies their six
cases plus five more to `verify.py`: **11/11 rejected for the expected
reason, on both records** (base replaced by a residue; next N in the
progression; a congruence dropped; class changed mod 3 and mod 17; a digit
of N altered; g replaced by the next prime; composite modulus; repeated
modulus; parity class removed; wrong digit count). Two bare assertions in
`verify.py` got explicit messages in the process.

## 3. The two "unlucky" searches were one unlucky stretch

Both branches report an improbable wait at Q = 1.2·10⁶: 2,647 tests here
against 703 expected (p = 0.024), and 3,472 there against 762 (p = 0.011).
Two independent events of that size would have joint probability
2.5·10⁻⁴ and would be serious evidence against the density model that
every ladder estimate rests on. They are not independent:

- Same cover, same g, same n ⇒ **the same arithmetic progression**. In
  this branch's indexing the candidates are P_t = 1 + 2ⁿ(m₀ + t·M_c);
  their extra condition "2ⁿ divides P − 1 exactly" keeps precisely the
  odd t (m₀ is even). Their hit, offset i = 6,781, is t = 13,563 = 2i + 1.
  Re-sieving the odd t ≤ 13,563 to their depth 2·10⁸ gives **3,472
  survivors — exactly their logged test count.**
- **1,341 integers were tested by both sessions.** A further 118 of
  theirs lie below this branch's stopping point but were removed by its
  deeper sieve (they have a factor in (2·10⁸, 10⁹]); 2,013 lie beyond it.
  Together the sessions tested 4,778 distinct numbers.
- The prime at t = 5,568 has 2^12477 | P − 1, so the exact-division rule
  skipped it; that is why their N is 2.44× larger. (The rule costs
  nothing in tests per prime — it only discards half of each stretch of
  N — but here it discarded the one that mattered.)

Jointly: 6.42 primes were expected in the union of the two ranges and 2
were found, P(≤ 2 | 6.42) = **0.046**. One mildly unlucky stretch, seen
twice. With the exhaustive probes (theirs: 54 vs 48.7 and 8 vs 9.3;
this branch: 46 vs 48.6), their shakedown (122 tests vs 123) and this
branch's 2M run (648 vs 973), the pooled count is 112 primes observed
against 114.7 expected. The model stands. (`overlap_check.py` reproduces every
number in this section from the two record files.)

## 4. What each branch has that the other lacks

| | this branch (`proth/`, WP10) | theirs (`bls/`, WP10 + WP11) |
|---|---|---|
| records | 1,200,109 **and 2,000,269** | 1,200,109 |
| cover | paper's greedy **and a lazy weighted greedy, 8–10% shorter** (≈ 30% less search) | paper's greedy |
| sieve | to 10⁹, vectorised, 4 processes, 65 s | to 2·10⁸, one Python loop, 68 s (≈ 8% more tests) |
| 2-adic condition | 2ⁿ ∣ P − 1; proof uses the full power 2^v | 2ⁿ ∥ P − 1 exactly |
| search order | first hit seen (`imap_unordered`) | smallest offset (`imap`), deterministic |
| verifier | checks N lies in every class | **rebuilds N by product-tree CRT from the congruences** and compares |
| second proof of the complement | PARI N−1 certificate + `isprime` + brute-force scan | GMP BPSW at `98efe92`; ⟲ the same PARI leg since `6c66bcd` |
| verifier mutation test | adopted in this review (11 cases, committed) | ⟲ **reported** (6 cases; harness not committed) |
| density check | one probe (46 vs 48.6) | **two probes with z-scores** |
| GRH assessment | constants ledger (Linnik exponents 5 → 12/5 → 2, guaranteed N−1-certifiable realisation 12 → 6, Miller cost) | **quantified at record scale** (`grh_reach.py`: RH window 10^72.4 short at 150 digits, GRH 10^65.6 short; Door-1 sieve floors −0.46·π(Q); positivity hierarchy 10^19 monomials) |
| theory | **C(x) ≥ (1.349 − o(1))·x·ln x; C(x) ≤ x^{4+ε}; prior art arXiv:2605.21529; LaTeX patch for the paper** | — |
| ladder | exact lazy covers to 16,045,848 | fixed-order covers, **plus the 10⁸ row** (491,191 digits, ~27,600 tests, ~24 core-years with GMP) |
| per-record README | no | yes |

The two verifiers are worth keeping *both*: two independently written
checkers plus PARI is the repo's own dual-stack standard (SoK §4), now
obtained without having planned it.

## 5. Statements that are stale or incomplete once the branches meet

1. **Theirs — record board.** RESULTS ("the largest proven value"), the
   SoK Game-1 heading and summary row, and the research-log board all
   say 1,200,109. Superseded by g = 2,000,269 on this branch.
   ⟲ Already corrected by them in `6c66bcd` ("independent second
   certificate", incumbent named).
2. **Theirs — WP10, row "Paper theorems: constants only".** It says
   `thm:lower` gains only the Linnik factor. `thm:lower` (Theorem 14,
   the FGKMT transfer) is in fact *superseded* in rate — by the counting
   bound of arXiv:2605.21529 and by the elementary covering bound in this
   branch's WP10 §2. And for the paper's moduli (primorial-type, hence
   smooth) the unconditional Linnik exponent is 12/5 (Chang; ⟲ a
   literature citation, marked [L] in WP12 and not re-checked by either
   session), not 5, so GRH's gain there is a factor 1.2, not 2.5.
3. **This branch — Theorem 2 needed a caveat.** The ceiling
   C(x) ≤ x^{4+ε} is asymptotic and says nothing at record parameters
   (x = 613–79,139 against Q ≤ 2·10⁶). Their §B is the finite-size
   version of the same sieve computation and finds it vacuous there
   (floor −0.46·π(Q) at level Q^{1/2}; positive only at level Q, beyond
   Elliott–Halberstam). Caveat added to WP10 §2.
4. **Both — "an unlucky 1–2% draw".** True of each search alone;
   together it is one ~5% event (§3).

Also: both branches number a memo "WP10" (different files, overlapping
subject), and their WP11 and this branch's `proth/README.md` describe the
same construction under two names ("BLS" / "Proth-BLS").

## 6. If the branches are merged

A trial merge conflicts in `SOK_GOLDBACH_GAPS.md` and
`phd/RESEARCH_LOG.md`; `RESULTS.md` merges textually but would then carry
two "new record" sections. Nothing conflicts in code or records. A
coherent union would be:

- one pipeline (`proth/desert.py`: it is the superset — lazy cover, deep
  sieve), **both verifiers**, their `density_probe.py`, `ladder.py` and
  `grh_reach.py`, and all three records;
- their WP10 as the GRH assessment (it is the quantitative one), their
  WP11 as the construction memo, and this branch's memo renumbered WP12
  for what is only here (covering bounds, Linnik exponents, lazy covers,
  the 2M record, this review);
- the shared docs updated once, to 2,000,269.

Not done here: the request was a review, and merging would put their
commits on this branch. ⟲ Subsequently agreed with the other session and
carried out: see `merge_2026-11-21.md`. One difference from the list
above: their `density_probe.py` and `ladder.py` were retired with the
rest of their search code, in favour of `proth/probe.py` and
`proth/ladder.py`; `grh_reach.py` and both of their verifiers are kept.
