# Goldbach Desert Records

## The 100% line, computed instead of fitted (2026-11-22)

Closeness divides g by the largest g a number of that size is expected to
have. That line used to be 1.4·ln²N·ln ln N, with the 1.4 fitted to one
number, the largest g of the exhaustive search. It is now computed from the
Hardy–Littlewood prime tuple heuristic with no fitted constant
(`ceiling_model.py`; its docstring states the model). Nothing about the size
of g(N) is proved, so the line is still a prediction. These are the checks
it passes.

- **Random numbers.** `gsample.c` computed g for 600 million random even N
  in [10^18, 1.1·10^18) (`samples/random_1e18.txt`). The model's chance of
  g(N) ≥ y agrees with the measured share within 0.5% from y = 11 (86% of
  the numbers) to y = 1,801 (one in 43,000), within 2% to y = 2,203 (one in
  240,000), and within the counting error beyond that: 75 numbers have
  g ≥ 3,001 where the model expects 69. The same test on 300 million random
  14-digit numbers (`samples/random_1e13.txt`) agrees within 1.3% down to
  one in 43,000 (y = 1,201) and within the counting error beyond.
- **Real numbers far in the tail.** For one progression of the 25-digit
  search (residues fixed on 13 primes, 189 complements left) two unrelated
  computations give the chance that a member has g > 10,000: the scanner's
  sieve statistics over 16.7 million consecutive members, and the model's
  average over the residues. Both give e^−25.40, within the 0.6% counting
  error of the first.
- **Successes of the scanner.** `tscan` predicts its successes with the same
  model, with the sieve done by brute force. Over its test instances and
  the four record searches it predicted 138 and found 145.
- **Record holders.** `record_holders.txt` has the 69 record holders below
  4·10^18: each is the first N whose g reaches its value. For the last one,
  g = 9,781 at 3.3·10^18, the model's median for the largest g below that N
  is 9,570 (5% to 95%: 9,190 to 10,240). For each record holder the model
  also gives the expected number of earlier numbers with a g at least as
  large; with an exact model these behave like a standard exponential
  variable (median 0.69). Over the 35 record holders above 10^9 the median
  is 0.29: the real ones come somewhat early, by about two standard errors.
  If that is a real effect the line is about 1.5% too low. No correction is
  applied.
- **The sampler** that evaluates the model agrees with full enumeration of
  the residue vectors on small cases to four digits.

| digits of N | largest g expected below N (median) | 5% to 95% | ÷ ln²N·ln ln N | earlier fitted line |
|---|---|---|---|---|
| 19 (3.3·10^18) | 9,570 | 9,190 to 10,240 | 1.40 | 9,560 |
| 20 | 11,560 | 11,120 to 12,350 | 1.42 | 11,370 |
| 22 | 14,560 | 14,070 to 15,450 | 1.45 | 14,100 |
| 25 | 19,740 | 19,120 to 20,830 | 1.47 | 18,800 |
| 28 | 25,770 | 25,090 to 26,970 | 1.49 | 24,240 |
| 32 | 35,240 | 34,430 to 36,690 | 1.51 | 32,680 |
| 40 | 59,000 | 57,930 to 60,880 | 1.54 | 53,720 |
| 50 | 98,250 | 96,860 to 100,720 | 1.56 | 88,070 |
| 63 | 165,920 | 164,030 to 169,300 | 1.58 | 146,630 |
| 80 | 283,410 | 280,870 to 287,920 | 1.60 | 247,790 |
| 100 | 465,350 | 462,100 to 471,120 | 1.61 | 403,730 |
| 150 | 1.14 million | 1.13 million to 1.15 million | 1.63 | 976,120 |
| 200 | 2.13 million | 2.12 million to 2.14 million | 1.64 | 1.82 million |

The ratio to ln²N·ln ln N is 1.40 at 19 digits, where the old constant was
fitted, and it grows with size. The earlier line was therefore too low
everywhere above 19 digits, by 5% at 25 digits and 10% at 40, and every
closeness figure drops (`closeness.py` now interpolates this table):

| record | g | closeness, fitted line | closeness, model line |
|---|---|---|---|
| 25 digits | 10,357 | 56.4% | 53.8% |
| 27 digits | 10,111 | 47.3% | 44.7% |
| 30 digits | 10,459 | 39.0% | 36.5% |
| 46 digits | 20,551 | 28.2% | 25.5% |
| 63 digits | 30,139 | 20.7% | 18.3% |
| 150 digits | 104,527 | 10.7% | 9.2% |

The closeness figures in the sections below were written with the fitted
line; the table in the Closeness section near the end has the model values
for every record.

Two more numbers from the model. The smallest N with g > 10,000 is expected
near 7·10^18, just above the exhaustive range; our 25-digit N is about a
million times larger. And about 9·10^9 even numbers below that 25-digit N
should have a g of at least its 10,357 (for the 27-digit record: 9·10^12).

What is published (literature check by a third session, 2026-11-22; it
could not open the 2014 paper itself, so the second item is second-hand).
Granville, van de Lune and te Riele (1989, p. 432) conjecture only the
order, g(N) ≪ ln²N·ln ln N, with no constant. Two candidate constants for
the limit of max g ÷ (ln²N·ln ln N) are attributed to Granville in later
papers (Juhász et al. 2023, citing Oliveira e Silva, Herzog and Pardi 2014):
1/C₂ = 1.515 and 2e^−γ/C₂ = 1.701, C₂ being the twin prime constant, with
the data called inconclusive. We found no published calculation of the
expected record at a given size. The model here has 1/C₂ as its limit, but
from above and extremely slowly: its ratio is 1.40 at 19 digits, passes
1.515 near 35 digits, and is still rising at 200 (1.64). So a ratio above
1.515 at reachable sizes says nothing against that limit, and the two
candidates cannot be told apart by any feasible search.

Past the table (above 200 digits) `closeness.py` uses a formula that
reproduces the table within 1.5%, and within 0.3% from 50 digits up: the
ceiling is the prime number with index
(L ÷ 1.3203)·(L − ln 2 − 0.71·ln L − 2.74), where L = ln N and
1.3203 is twice the twin prime constant.

## The threshold game at 30,000 (2026-11-22): g(N) > 30,000 at 63 digits

**g(N) = 30,139** for
N = 563696031021545043161771326159246716394341421918582840246518722
(63 digits, `records/threshold_63digit_g30139/`). It is the smallest N known
to us with g above 30,000. The next N we know with a g that large is the
150-digit one (g = 104,527).

- **Closeness.** g is 20.7% of the conjectural ceiling for a 63-digit
  number (`closeness.py`) and 77 times the g of a typical number of that
  size. A perfect N for this g would have about 31 digits.
- **Search.** N mod r is fixed for 32 primes r ≤ 149 (`cover.py 30011 22`;
  131 and 139 are left free), which leaves 348 primes below 30,011
  uncovered. `tscan/scan.py` scanned the members k < 7.03·10^9 of that one
  progression in 19 minutes on 4 cores: 6.3 million k per second, testing
  the 0.86% of the k with at most 126 complements left, which hold 16–17%
  of the expected successes. The success is at k = 6,878,744,425. The model
  put the expected number of successes up to k = 7.03·10^9 at 0.22, so this
  one came early.
- **Proof.** Built the same way as for the 25-digit record below.
  `evidence.json` has a compositeness witness for N − q for each of the
  3,260 primes q < g: a cover prime (2,911), a prime below 10^5 (224), a
  failed strong base-2 test (124), or parity (q = 2). N − g is proved prime
  by a PARI ECPP certificate (`complement_cert.gp`, `primecertisvalid` = 1).
  `direct_check.gp` repeats the whole check in PARI without the evidence
  file.

The low end of the frontier after today's three records (a point is on it
when no smaller known N has a g at least as large):

| digits of N | g | closeness | record |
|---|---|---|---|
| 19 | 9,781 | ~100% | exhaustive search ≤ 4·10^18 (not ours) |
| 25 | 10,357 | 56.4% | `threshold_25digit_g10357` (today) |
| 30 | 10,459 | 39.0% | `threshold_30digit_g10459` |
| 40 | 11,173 | 20.9% | table in the 30-digit section |
| 46 | 20,551 | 28.2% | `threshold_46digit_g20551` (today) |
| 63 | 30,139 | 20.7% | `threshold_63digit_g30139` (today) |
| 150 | 104,527 | 10.7% | `threshold_150digit_g104527` |

## The low end of the threshold game (2026-11-22, later): g(N) > 10,000 at 25 digits

**g(N) = 10,357** for N = 5471513744131872011405456 (25 digits,
`records/threshold_25digit_g10357/`). It is 55 times smaller than the
27-digit N two sections down and has a larger g, so it replaces that N as
the smallest N known to us whose g exceeds everything in the exhaustive
range (9,781).

- **Closeness.** g is 56.4% of the conjectural ceiling for a 25-digit
  number (`closeness.py`) and 92 times the g of a typical number of that
  size. The 27-digit record has 47.3%.
- **What changed.** One progression became 1,009. `tscan/variants.py`
  lists every residue vector on the 13 primes r ≤ 43 that leaves at most
  189 primes below 10,007 uncovered: 6 vectors with 186, 28 with 187, 157
  with 188 and 818 with 189. They all share the modulus M.
  `tscan/vscan.py` scans them in lockstep, always advancing the progression
  that is lowest, so N grows as slowly as possible for the work done.
- **Search.** 4.9·10^11 members in 6.5 hours on 4 cores. The 191
  progressions with at most 188 residual primes were scanned for k below
  7.4·10^8 or more (N up to 9.7·10^24), the 818 with 189 for k below
  4.2·10^8. The scanner tested about 1% of the members (the ones with the
  fewest complements left after the sieve: at most 49 of 189 in the
  progression that succeeded), and by the survivor histogram those hold
  about two thirds of the expected successes. The success is at
  k = 418,223,156 of a progression with 189 residual primes.
- **It came late.** By the model the expected number of successes up to
  there was 2.7; the chance of none by then is 7%. Because of the empty
  stretch the scanner and the model were checked again before the success
  turned up, on cut-down instances where successes are common (only the
  first 110 or 130 residual primes as rows): 103 successes found against
  95 expected, and 16 against 17.5 with `vscan.py` end to end. Every one
  of them was confirmed with gmpy2.
- **Nothing smaller in the scan.** All 1,009 progressions have been
  scanned up to this N, and this is the only success among the members
  tested. The members that were not tested hold the other third of the
  expected successes, so a smaller N may still sit among them or in other
  progressions.
- **Proof.** Nothing in it depends on the scanner. `evidence.json` has a
  compositeness witness for N − q for each of the 1,270 primes q < g: a
  cover prime (1,073), a prime below 10^5 (146), a failed strong base-2
  test (50), or parity (q = 2). N − g is proved prime by a PARI ECPP
  certificate (`complement_cert.gp`, `primecertisvalid` = 1).
  `direct_check.gp` repeats the whole check in PARI without the evidence
  file.

The 27-digit N leaves the frontier, because a smaller N with a larger g is
now known. The 30-digit N stays: no smaller N with a g as large as its
10,459 is known.

## The threshold game at 20,000 (2026-11-22): g(N) > 20,000 at 46 digits

**g(N) = 20,551** for N = 7687588743764734829791950727864816819276291322
(46 digits, `records/threshold_46digit_g20551/`). It is the smallest N known
to us with g above 20,000. Until now the smallest N we had with a g that
large was the 150-digit one (g = 104,527).

- **Closeness.** g is 28.2% of the conjectural ceiling for a 46-digit
  number (`closeness.py`) and 79 times the g of a typical number of that
  size. A perfect N for this g would have about 26 digits.
- **Search.** N mod r is fixed for 24 primes r ≤ 101 (`cover.py 20011 22`;
  97 is left free), which leaves 268 primes below 20,011 uncovered.
  `tscan/scan.py` scanned the members k < 4.15·10^9 of that one progression
  in 6.5 minutes on 4 cores: 10.8 million k per second, testing the 1.09%
  of the k with at most 88 complements left, which hold 27–28% of the
  expected successes. The success is at k = 3,202,304,117. The model put
  the expected number of successes up to k = 4.15·10^9 at 0.26, so this
  one came early.
- **Proof.** Built the same way as for the 27-digit record below.
  `evidence.json` has a compositeness witness for N − q for each of the
  2,319 primes q < g: a cover prime (2,038), a prime below 10^5 (186), a
  failed strong base-2 test (94), or parity (q = 2). N − g is proved prime
  by a PARI ECPP certificate (`complement_cert.gp`, `primecertisvalid` = 1).
  `direct_check.gp` repeats the whole check in PARI without the evidence
  file.

It is a frontier point: every smaller N we know has a smaller g (the
40-digit N in the table further down has 11,173).

## The low end of the threshold game (2026-11-22): g(N) > 10,000 at 27 digits

**g(N) = 10,111** for N = 301232067011489734233412892 (27 digits,
`records/threshold_27digit_g10111/`). It is 646 times smaller than the
30-digit N of the next section and replaces it as the smallest N known to
us whose g exceeds everything in the exhaustive range (9,781).
Later the same day the 25-digit N at the top of this file took that place,
and this N left the frontier.

- **Closeness.** g is 47.3% of the conjectural ceiling for a 27-digit
  number (`closeness.py`); the 30-digit record has 39.0%.
- **What changed.** The scan step was rewritten in C (`tscan/`, see its
  README). Two things make it fast:
  - A bit sieve over the table (residual prime q, member k) removes every
    N − q with a prime factor below 131,072.
  - Only the k with the fewest surviving complements are tested. Here that
    was 1.26% of the k (at most 49 of 188 complements left), and by the
    survivor histogram they hold 61–66% of the expected successes.
  - Speed on 4 cores: 16–19 million k per second. `search.py`, which
    tests every k, did 0.3 million per second on the 30-digit job.
- **Search.** N mod r is fixed for the 13 primes r ≤ 43
  (`cover.py 10007 23`), which leaves 188 primes below 10,007 uncovered.
  The members k < 2.38·10^10 of that one progression were scanned in 24
  minutes. The success is at k = 23,025,113,687; the model put the
  expected number of successes up to there at 0.7.
- **Proof.** Nothing in it depends on the scanner. `evidence.json` has a
  compositeness witness for N − q for each of the 1,241 primes q < g: a
  cover prime (1,049), a prime below 10^5 (137), a failed strong base-2
  test (54), or parity (q = 2). N − g is proved prime by a PARI ECPP
  certificate (`complement_cert.gp`, `primecertisvalid` = 1).
  `direct_check.gp` repeats the whole check in PARI without the evidence
  file.

The 30-digit N keeps its place on the frontier: its g = 10,459 is larger,
and no smaller N with a g that large is known.

## The low end of the threshold game (2026-11-21, night): g(N) > 10,000 at 30 digits

**g(N) = 10,459** for N = 194465365536282197945444045558 (30 digits,
`records/threshold_30digit_g10459/`).

- **Why this target.** Exhaustive search has g(N) ≤ 9,781 for every even
  N ≤ 4·10^18 (Oliveira e Silva, Herzog & Pardi), so T(10,000), the
  smallest N with g(N) > 10,000, lies above 4·10^18 and is not known. The
  conjectural ceiling first reaches 10,000 near 10^19, so the true value
  is expected not far above that. This N was the smallest known to us
  whose g exceeds everything in the exhaustive range, until the 27-digit
  N of the section above.
- **Closeness.** g is 39.0% of the conjectural ceiling for a 30-digit
  number (`closeness.py`). Our next best is the 150-digit record at 10.7%.
- **Search.** N mod r is fixed for the 16 primes r ≤ 59 (greedy residues),
  which leaves 177 primes below 10,007 uncovered. A scan of the 3.67·10^8
  members N0 + k·M between 10^29 and 8.0·10^29 (53 minutes on 4 cores,
  gmpy2) gave one member with g > 10,000, at k = 101,138,639.
- **Proof.** `evidence.json` has a compositeness witness for N − q for each
  of the 1,279 primes q < g: a cover prime (1,098), a prime below 10^5
  (134), a failed strong base-2 test (46), or parity (q = 2). N − g is
  proved prime by a PARI ECPP certificate (`complement_cert.gp`,
  `primecertisvalid` = 1). `direct_check.gp` repeats the whole check in
  PARI without the evidence file.

The same cover-and-scan method at other sizes, each proved in PARI the same
way. Scan effort differs from row to row, so read the closeness column as
"what a few CPU-minutes to one CPU-hour buys", not as a limit.

| digits | N | g | closeness | members scanned | on the frontier |
|---|---|---|---|---|---|
| 20 | 70009540006994447438 | 5,407 | 48.4% | 4.8·10^8 (the whole progression) | no: 9,781 is known at 19 digits |
| 22 | 8314310102096915044292 | 6,073 | 43.4% | 2.9·10^7 | no: same reason |
| 30 | 194465365536282197945444045558 | 10,459 | 39.0% | 3.7·10^8 | yes |
| 40 | 8495171008612585955282488984129056734312 | 11,173 | 20.9% | 6.3·10^6 | yes |
| 46 | 7687588743764734829791950727864816819276291322 | 20,551 | 28.2% | 4.1·10^9 (`tscan`, own section above) | yes |
| 63 | 563696031021545043161771326159246716394341421918582840246518722 | 30,139 | 20.7% | 7.0·10^9 (`tscan`, own section above) | yes |

Just above the exhaustive range a cover plus a scan reaches about half the
ceiling, and a smaller number with a larger g is already known. A point
counts only when it is on the frontier: no smaller known N has a g at least
as large. Such a point is at once a T record (smallest N for its g) and an
R record (largest g below its N).

## New height record (2026-11-22): g(N) = 16,046,137

**g(N) = 16,046,137** for a 91,752-digit N
(`records/height_91752digit_g16046137/`):
- **Cover.** All 1,033,885 primes below g lie in a class of a complete
  13,094-class cover (prime moduli ≤ 459,089, built for the primes below
  Q = 16,045,849). g is the first prime the cover misses.
- **Proof.** N − g = m·2^101604 + 1 (m odd) is proved prime by
  7^((P−1)/2) ≡ −1 (mod P) with 2^101604 > P^(1/3), plus the BLS
  non-square condition. P has 304,793 bits.
- **Search.** 13,124 distinct candidates were tested, against ~4,488
  expected per prime: a late draw, with a probability of ~5%.
  - Main range t < 32768, sieved to 3·10¹¹ (14,579 survivors): 12,470
    tested. 7,168 of these were GPU screens on a Colab A100 (6.1 s each).
    The rest ran on up to six Colab CPU runtimes: GMP Euler tests at
    ~1,000 s each, then from 07:50Z on 22 Nov OpenPFGW Fermat PRP tests at
    ~60 s each, four per runtime (`proth/pfgw_search.py`).
  - Fallback range t ∈ [32768, 131072): the spec allows t < 2^20. It was
    sieved to 3·10¹¹ on this session's container while the search ran
    (44,130 survivors), and each CPU runtime moved there when its main
    slice ran out.
  - The hit is the fallback range's 643rd test: t = 127,534, found by PFGW
    on the A100 host's CPUs (45.5 s). 2,109 survivors below 32768 were
    still untested.
- **Verification.** No screen result is trusted. The hit was re-proved
  with `desert.bls_prove` on the runtime, and again on this container's
  CPU (759 s). It passes `verify.py` (700 s).
  - The independent `bls/` stack passes: `xverify.py` (2.4 h) and
    `verify_bls_record.py` (2.5 h) on Python ints, through
    `proth/divmod_pow_run.py` (`xverify_divmod.log`,
    `verify_bls_record_divmod.log`). Each ran alone on a Colab CPU
    runtime, with CPython 3.13.18 as here.
  - The PARI cross-check is running here. PARI's own N−1 certificate for
    P is valid; `isprime` and the gcd scan of all 1,033,885 complements
    follow.
- **Cross-verification.** The second session rebuilt N from `spec.json`
  and t alone and got the same sha256. On its own machine:
  - `verify.py` passed (632 s), and `bls/xverify.py` passed (8,313 s).
  - The PARI gcd scan passed in nine ranges whose counts add up to
    1,033,885 = π(g − 1), and PARI's N−1 certificate is valid.
  - Its own PARI `isprime` call was not completed (it needs about 3 hours on
    one core and was stopped at a 2-hour task limit); the first session's
    PARI run printed isprime(P) = 1. Log: `crossverify_2ce9e63a.log`.

## New height record (2026-11-21, night): g(N) = 10,000,141, GPU-screened

**g(N) = 10,000,141** for a 61,329-digit N
(`records/height_61329digit_g10000141/`):
- **Cover.** All 664,584 primes below g lie in a class of a complete
  9,095-class cover (prime moduli ≤ 306,239). g itself is the first prime
  above 10⁷ that the cover misses.
- **Proof.** N − g = m·2^67914 + 1 (m odd) is proved prime by
  11^((P−1)/2) ≡ −1 (mod P) with 2^67914 > P^(1/3) (P has 203,731 bits).
- **Search.** 3,072 GPU screens on Colab A100s, 2.35 s per test with
  engine v3 (2.76 s with v2), ~2 h of GPU time in all.
  - The survivors were deep-sieved from 10⁹ to 10¹¹ while the search ran.
  - The hit is the 2,718th survivor of the 10¹¹ list (expected ~3,130).
  - The total includes 113 tests on candidates the deeper sieve removed
    later, and the rest of the hit's batch.
  - Another ~1.4 h of GPU work was lost when a runtime vanished; those
    candidates were re-run.
- **Verification.** No GPU result is trusted. The hit was re-proved on the
  CPU with `desert.bls_prove` (306 s), and it passes `verify.py` (292 s)
  and the PARI cross-check: PARI's own N−1 certificate, `isprime`, and a
  brute-force gcd scan of all 664,584 complements (2.8 h, `crosscheck.log`,
  no error lines). The independent `bls/` stack passes as well:
  `xverify.py` and `verify_bls_record.py`, 61 min each on Python ints
  (`xverify_divmod.log`, `verify_bls_record_divmod.log`).
  - Both ran unchanged except for their one big modular exponentiation.
    `proth/divmod_pow_run.py` supplies it as a square-and-multiply that
    reduces with `divmod`, ~4× faster than the built-in 3-argument `pow`
    at this size on CPython ≥ 3.12, and checkpointed.
  - The first, fully unmodified runs were lost at ~3.4 h, when this
    session's container was replaced.
- **Cross-verification.** The second session re-ran all three checks on
  its own machine, with verifier code from a commit older than the record:
  `proth/verify.py` (246 s), the PARI cross-check, and `bls/xverify.py`
  on Python ints with the same kind of `divmod` exponentiation (51 min).
  All passed (`crossverify_2ce9e63a.log`).

This doubles the evening's 5·10⁶ record, which is described next. The cost
model had put this rung at ~3.4 days on 4 cores. The 16,045,849 rung now
has the GPU, with a CPU fleet beside it (`proth/README.md`, "GPU
screening").

## New height record (2026-11-21, evening): g(N) = 5,000,251, GPU-screened

**g(N) = 5,000,251** for a 33,938-digit N
(`records/height_33938digit_g5000251/`):
- **Cover.** All 348,526 primes below g lie in a class of a complete
  5,342-class cover (moduli ≤ 167,107).
- **Proof.** N − g = m·2^37583 + 1 (here 2^37584 | P − 1) is proved prime
  by 5^((P−1)/2) ≡ −1 (mod P) with 2^37584 > P^(1/3).
- **Search.** It ran on a Colab A100: 68 CPU tests, then 3,072 GPU screens
  of 2^((P−1)/2) mod P (`proth/gpu_screen.py`, 0.82–0.92 s per
  112,738-bit test, ~100× one GMP core). The hit was the 3,080th sieve
  survivor (expected ~2,118).
- **Verification.** No GPU result is trusted. The hit was re-proved on the
  CPU (81 s), and it passes `verify.py` and the PARI cross-check: PARI's
  own N−1 certificate, `isprime`, and a brute-force gcd scan of all
  348,526 complements. The independent `bls/` stack passes as well
  (`xverify.py` and `verify_bls_record.py`, pure-Python ints, 46 min each).

This is 2.5× the record set earlier the same day, which is described next.
The 4-core cost model had put this rung at ~11 h; it took 44 min of GPU
time.

## New height records (2026-11-21): g(N) = 2,000,269 and 1,200,109, proved without ECPP

**g(N) = 2,000,269** for a 15,595-digit N
(`records/height_15595digit_g2000269/`): all 148,950 primes below g
are excluded by an explicit divisor from a complete 2,670-class cover, and
N − g = m·2^17273 + 1 is proved prime by 11^((P−1)/2) ≡ −1 (mod P) with
2^17274 > P^(1/3). Found after 648 tests (expected ~970), 37 minutes on 4
cores; verified by the stdlib verifier and by the PARI cross-check. This is
Campaign C's target ("g > 2,000,000", budgeted at 6–12 h of ECPP plus
re-verification) with no ECPP at all. The first record of the series,
found earlier the same day, is described next; the method is the same.

### g(N) = 1,200,109

**N** has 11,263 digits (`records/height_11263digit_g1200109/`,
full decimal in `N.txt`); its least Goldbach summand is
**g(N) = 1,200,109**, above both earlier height records (1,157,341 at
2,480 digits in `slop/goldbach/records/g1`, and 1,134,871 at 2,692 digits
below). What changed is not the number but the proof:

| | megagap record (July) | this record |
|---|---|---|
| primes q < g excluded by an explicit divisor | 85,476 + 895 of 88,239 | **all 92,942** |
| excluded by a strong-pseudoprime witness | 1,867 | **0** |
| primality of N − g | 253-step ECPP certificate | **one modular exponentiation** |
| re-verifying the partition proof | replay a 253-step ECPP chain | replay one `powmod` (5.7 s) |
| full re-verification incl. PARI cross-check | — | 134 s on one core |

The complement is *constructed* as P = N − g = m·2^12475 + 1: every cover
congruence N ≡ a_r (mod r) is a congruence on m, so the cover and the
"Pocklington-friendly form" that the SoK called the most valuable open
trick intersect by CRT. Then 7^((P−1)/2) ≡ −1 (mod P) with
2^12477 > P^(1/3) proves P prime (Brillhart–Lehmer–Selfridge N−1 test).
With certification free, a *complete* cover (no residual primes, hence no
lottery) is the cheapest design; the search is for one prime in a
progression (2,647 tests here against an expectation of ~700 — an
unlucky 2% draw; the density model was re-checked and holds).

Verified by `proth/verify.py` (stdlib only) and independently by PARI/GP
(`crosscheck.gp`: PARI's own N−1 certificate, `isprime`, and a brute-force
scan of all 92,942 primes that does not use the cover). Method, cost
model and the ladder to g > 16,045,848 (longer than the largest known
prime gap of any kind): `proth/README.md`; the same construction as
derived by the second session: `phd/wp11_bls_game1.md`. What a proof of
GRH would and would not change here: `phd/wp10_grh_remark.md`. Theory
that came out of the review — a new constant for covering the primes and
a sieve ceiling for covering certificates — is in
`phd/wp12_prime_covering_grh_ledger.md`.

### g(N) = 1,200,109 a second time — an independent certificate

A second session, working separately, found the same construction the
same morning and certified g = 1,200,109 for a **different** 11,263-digit
N (`records/bls_game1_11263digit_g1200109/`). Its code shares nothing with
`proth/`: its own cover builder, CRT, sieve and search (`goldbach/bls/` at
commit `6c66bcd`; that search code was retired at the merge in favour of
`proth/desert.py`) and its own stdlib verifier
(`bls/verify_bls_record.py`, which rebuilds N from the congruences by
product-tree CRT). Its complement has P − 1 = 2^12475·R with R odd; the
first record's has 2^12477 | P − 1.

The two certificates come from one progression: same cover, same g, same
n, and the second search ran over exactly the odd-index half of the first
one's candidates (`proth/overlap_check.py`; 1,341 integers were tested by
both). Each search alone looked like a 1–2% unlucky wait (3,472 tests
against 762 expected there, 2,647 against ~700 here); jointly it is one
~5% event. The 3,245 candidates neither session had tested were then
probed exhaustively: 6 primes against 4.62 expected (z = +0.64), so the
density model holds on fresh numbers
(`phd/wp12_prime_covering_grh_ledger.md` §6).

Every record passes every verifier: `proth/verify.py`,
`bls/verify_bls_record.py` (through `proth/interop.py` for the two
`height_*` records), `bls/xverify.py`, and PARI's own N−1 certificate with
a brute-force scan (`crosscheck.gp` in each record directory). The reviews
the two sessions wrote of each other are `phd/crossreview_8ffe9d7a.md` and
`phd/crossreview_2ce9e63a.md`; what was agreed at the merge is in
`phd/merge_2026-11-21.md`.

## Prior-art check (2026-07-27)

A web literature search for published constructions of even integers
with large least Goldbach summands found none beyond the incumbents
this repo already cites and supersedes. For context: in *observed*
(exhaustive-verification) data the minimal summand stays tiny — the
largest known naturally occurring value is g = 9 781 near the
4·10^18 verification frontier (Oliveira e Silva, Herzog & Pardi,
Math. Comp. 2014; Herkommer's tables reach g = 8 443 at
2n ≈ 1.2·10^17), and a 2025 arXiv study of minimal primes in
generalised Goldbach partitions (arXiv:2510.21870) is observational
up to 10^9 only. The only constructive incumbents we are aware of
remain the source paper's 199-digit N with g = 105 667 and 237-digit
N with g = 109 621 (both re-verified in this repo before we started).
The records below are therefore "smallest/largest known to us"; if a
competing constructive literature exists it did not surface in the
search.

Addendum (2026-11-21): a second search found no competing constructions
either, but did find a theorem: W. Shi, arXiv:2605.21529v6, Thm 6.22
proves max_{n≤X} p(n) ≥ (½+o(1))·ln X·ln ln X by counting, which already
supersedes the paper's FGKMT-transfer bound; `phd/wp12_prime_covering_grh_ledger.md`
improves the constant to 1.349 by an explicit covering.

In-repo note: a parallel effort in `slop/goldbach/records/` (merged
from another working branch) holds a certified T(100k) bound of 179
digits (g = 101 149) and R(10^200) g = 119 419. The 150-digit record
below supersedes the 179-digit T bound; the slop R value g = 119 419
at 199 digits supersedes this directory's g = 112 249.

## New record (2026-07-26): T(100 000) at 150 digits — the GPU rung,
## 45 digits below our own 195-digit record

**N** (150 digits, `records/threshold_150digit_g104527/record.json`,
N = N0 + 62 147 038 260·M over a 68-modulus cover with M of 140 digits):

```
82666896361422214889140173486824909338317018059813
51031435344058125034274739390508125558021767403422
36249163597526688699521722930930329320505713336368
```

**g(N) = 104 527 > 100 000** with N ≈ 8.27·10^149 — the smallest known
even integer whose least Goldbach summand exceeds 100 000, taking 45
digits off the 195-digit record below (10^45× smaller). Evidence
(`evidence.json`, fully machine-checkable): all 9 977 prime offsets
q < 104 527 have N − q composite — parity (1), congruence divisor from
the cover (9 097), trial divisor < 10^5 (433), strong base-2
Miller–Rabin witness (446, unconditional). 104 527 is prime and
N − 104 527 is ECPP-certified prime (`complement_cert.gp`,
validated by `primecertisvalid`, see `check_cert.log`).

This rung was unreachable by the CPU pipeline (failure exponent
E = 24.91 at 150 digits vs 17.5 at 195 — e^7.4 ≈ 1 600× more search
per hit) and is the first result from the CUDA engine
(`gpu/engine150.py`: bit-matrix sieve + Montgomery CIOS base-2 Fermat
waves, validated bit-for-bit against Python; ~2.5M tests/s on a T4,
~8.5M tests/s on an A100 — ~430× the 4-core CPU pipeline). The k-range
[0, 7.5·10^10) was sharded across a rotating two-session Colab fleet
driven by `gpu/fleet.py` (safe_k checkpointing in git survived ~10
session culls and several container rollbacks with zero coverage
loss). The hit landed at k = 6.21·10^10, 63.8% into the round —
cumulative expectation ~0.63·0.64 ≈ 0.40 at the exact density
e^-24.91, within the central mass of the Poisson draw. The engine
found it after ~1.9·10^9 Fermat tests on this shard alone.

ROUND COMPLETE (2026-07-27): the full k-round [0, 7.5·10^10) has now
been scanned end to end (~2.1·10^12 Fermat tests across the fleet) —
exactly one hit, the record above. One draw against a Poisson mean of
0.63 is an unremarkable outcome; the density model stays unfalsified.
The next rung is 140 digits (E ≈ 28, ~22× this round's search).

## New record (2026-07-25): T(100 000) at 195 digits — 100× below the
## previous smallest desert past 100 000

**N** (195 digits, `records/threshold_195digit_g100297/record.json`,
N = N0 + 70 186·M over an 88-modulus cover with M of 190.0 digits):

```
71214124265787855971290038426160102511378229003272506217668297957
68214756376976852660013284997485991512845267319174394030269434418
51527812156074627008575588613267417336439269800778493535893423578
```

**g(N) = 100 297 > 100 000** with N ≈ 7.12·10^194 — the smallest known
even integer whose least Goldbach summand exceeds 100 000, beating the
197-digit record below by two orders of magnitude (and the paper's
199-digit incumbent by four). Evidence (`evidence.json`, fully
machine-checkable): all 9 614 prime offsets q < 100 297 have N − q
composite — parity (1), congruence divisor from the cover (8 903),
trial divisor < 10^5 (312), strong base-2 Miller–Rabin witness (398,
unconditional). 100 297 is prime and N − 100 297 is ECPP-certified
prime (`complement_cert.gp`, validated by `primecertisvalid`, see
`check_cert.log`).

Why this was reachable (see IDEAS.md for the measured ledger): the old
197-digit record came from a *dual-game* cover built at Q = 105 668; a
pure threshold cover at Q = 100 003 needs |U| = 704 instead of 752,
dropping the failure exponent from 18.2 to 17.28 (~3× cheaper), and
the new ascending-survivor test order (`search.py --sort-tests`,
measured 1.8× conditional discovery gain) plus the B = 10^6 sieve
optimum stack on top. The hit arrived after 1 590 progressions
(~1.75·10^8 sieved elements) across two 600-spec catalogs — cumulative
expectation ~1.9 at the exact density e^-17.5, so the draw landed
right at the mean. Measured Ê = 17.4 throughout, matching prediction
to 0.1.

## New record (2026-07-23): g(N) = 112 249 below 10^200

**N** (200 digits, `records/budget_1e200_200digit_g112249/record.json`,
N = N0 + 56 770·M over a 90-modulus cover with M of 194.3 digits):

```
10336361862320265637534248784107115912943733452949552173021625784255
26491232455104184949353771968786907192598875701371548940638695734951
1701812962805353232599898800895271779892845641377568833632
```

**g(N) = 112 249** — the largest least-Goldbach-summand known below
10^200, beating the best previous sub-10^200 value g = 107 719 (the
197-digit record below) and the paper's 237-digit height-game incumbent
g = 109 621 at 37 fewer digits. It misses the budget game R(10^199) by
3.4%: N = 1.0336·10^199. The find is a by-product of the R(10^199)
frontier campaign (see the 1M section below): search blocks are sieved
in full 16 384-element chunks, so ~16% of scanned candidates sit just
above the 10^199 ceiling, and the first success of the campaign landed
there (k = 56 770 vs the in-budget cap k ≤ 54 924) — at the measured
density Ê = 18.4 that is a fair draw from ~4.6·10^7 scanned elements.

Evidence (`evidence.json`, fully machine-checkable): all 10 642 prime
offsets q < 112 249 have N − q composite — parity (1), congruence
divisor from the cover (9 830), trial divisor < 10^5 (409), strong
base-2 Miller–Rabin witness (402, unconditional). 112 249 is prime and
N − 112 249 is ECPP-certified prime (`complement_cert.gp`,
validated by `primecertisvalid`, see `check_cert.log`).

## The 1M-desert-below-200-digits question (2026-07-22): measured — the
## frontier is ~1,250 digits, and 199 digits is short by a factor e^170

Target: even N < 10^200 with g(N) > 10^6, i.e. all 78,498 primes
q ≤ 10^6 have N − q composite. `exp1m.py` measures what that costs.

**Mechanism audit.** Compositeness of N − q across many q at once can
only be forced by congruence covers — r | N − q exactly when q ≡ N
(mod r), one residue class per prime r. Everything else is dead on
arrival: composite or prime-power moduli cover subsets of what their
prime factors already cover; algebraic factorizations of N − q need q of
a special polynomial shape no prime > 2 has; perfect powers in the
window [N − 10^6, N] don't exist (consecutive squares at 10^200 are
~10^100 apart); and hiding the desert inside a genuine prime gap of
10^6 needs gap merit 2,180 versus ~42 ever observed and ~460
conjecturally possible anywhere. What the cover leaves uncovered must
be composite by luck, at density e^−E with E = |U|·boost/ln N — a model
this repo has now validated at four scales (toy 26-digit: predicted
E 12.53, measured 12.51; toy 62-digit: 13.52/13.57; the 197-digit
record: 18.2/18.2; the 2,692-digit mega: 6.6/6.56).

**The E(D) frontier at Q = 10^6** (lazy-greedy digit-capped covers,
`exp1m.py frontier`; E at ln N = D·ln 10):

| digits D | moduli | |U| | E | search cost e^E |
|---|---|---|---|---|
| 199 | 91 | 8 157 | 196.7 | 10^85.4 |
| 300 | 127 | 7 311 | 124.3 | 10^54.0 |
| 400 | 161 | 6 728 | 89.3 | 10^38.8 |
| 600 | 226 | 5 865 | 54.9 | 10^23.8 |
| 800 | 288 | 5 241 | 38.2 | 10^16.6 |
| 1000 | 347 | 4 741 | 28.4 | 10^12.3 |
| 1300 | 435 | 4 100 | 19.6 | 10^8.5 |
| 1600 | 519 | 3 588 | 14.2 | 10^6.2 |
| 2400 | 736 | 2 492 | 6.9 | 10^3.0 |

D_min for a record-scale search (1.4·10^8 candidates, E ≤ 16.6):
**~1,470 digits**; heavy single-box (10^9, E ≤ 21): **~1,250**;
distributed (7·10^10, E ≤ 25): **~1,120**; a cosmological budget
(10^12/s for the age of the universe, E ≤ 68): **~520 digits**. The
2,400-digit row reproduces the mega record's regime (E 6.9 vs its 6.56)
— the model and the ladder are consistent end to end.

**The 199-digit wall** (`constructions/wall_1M_199d.json`, verified):
the best 199-digit system found — 91 moduli, residue-annealed — leaves
|U| = 8,146 residual primes, E = 196.4, success density 10^−85.3.
Annealing recovers only ~0.3% of E: the wall is structural, not an
optimization shortfall. (Structural in the sieve sense, not the
counting sense: the 91 best classes hold 148,290 slots for 78,497
targets, a 1.89× supply, so a union bound alone forbids nothing — but
prime residue classes overlap like independent sieves, coverage stops
at ~90%, and 60,000 anneal moves reclaim 11 residuals of 8,157.) Joint x/M
optimization does not help either: +25 digits of k-list entropy moves
E from 196 to ~194. Meanwhile the existence heuristic (E_random ≈ 445
for unstructured even N) predicts ~10^6.5 such N below 10^200 *exist* —
the conjectured (log N)²·log log N maximal order sits at 1.3·10^6
exactly at 200 digits — but the cheapest known path to *exhibit* one
costs 10^85 primality tests. This is a construction-versus-existence
gap of fifty-nine orders of magnitude beyond cosmological.

**The blueprint** (`constructions/blueprint_1M_1250d.json`, verified):
the cheapest practical 1M desert this machinery can specify — 420
moduli, M = 1,247 digits, |U| = 4,205, E = 20.74, i.e. ~10^9
progression elements ≈ **235 core-days** at 50 candidates/s. A
distributed campaign at mega-record throughput would find an
N ≈ 1,255 digits with g(N) > 10^6; that is the realistic version of
this target.

**The achievable 200-digit frontier** is the budget game R(10^199)
itself: at Q = 107,720 the annealer lands M = 194.3 digits, |U| = 764,
E = 18.0 (~18.3 at the 199-digit budget) — each residue-swap variant
progression holds ~47,000 sub-budget candidates, so a scan block of
several hundred variants is a ~25–35% lottery at beating g = 107,719.
The campaign run for this work scanned 1,300 distinct progressions
(500 + 800 fresh via the new `pair_pool` knob in `gen_variants.py`) —
8.5·10^7 elements at 1,850/s and measured Ê = 18.4 (predicted 18.3).
Expected hits: 0.70 in-budget + 0.14 in the 16% sieve-block overshoot
above 10^199. Observed: exactly one, in the overshoot — the
g = 112 249 record above. Poisson-fair on both counts; the strict
R(10^199) coin flip (48% per ~14 h of 4-core scan at this frontier)
landed tails this time. The incumbent 107 719 consumed ~21 h at the
same frontier; extending the catalog (deeper pair_pool, triple swaps,
or re-annealed bases) and re-running is purely a matter of core-hours.

## Joint representative/coverage optimization (2026-07-22): a 221-digit
## modulus with a sub-10^197 representative

Question: can we deliberately build a CRT system whose modulus M has far
more than 197 digits but whose least positive representative x has fewer
than 197 digits — while keeping record-class coverage of prime offsets?
Answer: **yes, by tens of digits, and the gain is exactly the entropy of
the residue search; hundreds or thousands of digits are out of reach.**

`joint.py` extends the annealer's objective log M + E to the expected-hit
objective **Phi = E − log K(x, M; B)**, where K = max(0, ⌊(B−1−x)/M⌋+1)
counts progression elements below the size budget B. It tracks the exact
representative incrementally through the CRT basis C_{r,a} =
a·(M/r)·((M/r)^{-1} mod r): a residue move shifts x by (a′−a)·C_{r,1}
mod M, so coverage counts and x anneal together. The heavy tool is a
multiple-choice modular meet-in-the-middle (`klist_solve`): split a block
of moduli into 2^d lists, enumerate the top-c residue classes of each,
and Wagner-merge with shrinking centered windows until the representative
lands in a target interval. 2^d lists of size L buy about
(d+1)·log10(L) digits of cancellation below M.

Measured on the 197-digit record's cover (88 odd moduli, M = 191
digits, |U| = 752, B = 10^197):

- **No structural small-x bias.** Over 2 000 random top-4 residue
  reassignments the deciles of x/M are (0.10, 0.25, 0.50, 0.75, 0.90) —
  uniform; the minimum matches the 1/samples order a uniform draw
  predicts. Only search entropy buys small representatives.
- **Phi reduces to the old objective while M ≪ B.** Across all x in
  [0, M), K changes by at most one (Δlog K = 7.3·10^−7): the record
  pipeline was already optimal in its regime, and E computed at the
  budget scale (18.20) reproduces the measured search density Ê = 18.2.
- **2-list MITM, moduli held fixed**: 46 solutions with x/M < 10^−8
  from 4^8 combos per side (entropy predicts ~43); the best costs
  **+8 residuals** (752 → 760) for **8.3 digits of cancellation**.

Constructions past the budget (`constructions/`, each re-verified
end-to-end: x ≡ a_r (mod r) for all 96–99 congruences, x < 10^197,
residual set recomputed from scratch):

| file | moduli | digits(M) | digits(x) | \|U\| | E at 10^197 |
|---|---|---|---|---|---|
| `m211_x196.json` | 2 + 95 | 211 | **196** | 738 | 18.09 |
| `m219_x197.json` | 2 + 98 | 219 | **< 197** | 784 | 19.33 |
| `m221_x197.json` | 2 + 98 | 221 | **< 197** | 782 | 19.32 |

The 211-digit system (4 lists × 8 moduli × top-5, 14.9 digits
cancelled) is a strictly *better* cover than the record's own (|U| 738
vs 752, E 18.09 vs 18.20) — the seven added moduli cover more residuals
than the block reassignment exposes. The 219-digit system (8 lists ×
8 moduli × top-5, 21.3 digits cancelled, 52 solutions where the
window/entropy calculus predicted ~50) shows the 4-level Wagner tree
delivering its full (d+1)·log10 L budget. The deepest run, 8 lists ×
8 moduli × top-6 over 64 block moduli, cancelled **24.3 digits**
(83 solutions, ~25 min / ~8 GB on 4 cores) for the 221-digit system —
within half a digit of its 24.9-digit entropy ceiling, and with no
coverage penalty over the top-5 run because the larger solution pool
compensates for the looser residue lists.

**Why this does not improve the bounded record games.** A sieved
progression scan generates ~1 850 candidates/s; k-list construction
generates 0.1–100 constructions/s of K = 1 candidates each, i.e.
candidates are 10^1–10^4× more expensive, while E is no lower. In Phi
terms: the record progression scores Phi = 18.20 − log 1 371 832 = 4.07,
an M > B construction scores Phi = E ≥ 18. Joint optimization is the
right tool exactly when the modulus *must* exceed the budget, and it
caps out at the search entropy: reaching 197 digits from the 2 692-digit
Game-1 cover would need ~10^2495 enumerated states (with lists of 10^6
that is 2^415 lists), so compressing that cover is impossible — matching
the uniform-representative estimate 10^(197−2692).

## Prime-gap domination record (2026-07-21): g(N) = 1 134 871

**The certified Goldbach desert exceeds the largest known prime gap with
proven endpoints** (1 113 106, between 18 662-digit primes), while the
ordinary prime gap around this N is just 8 970 — the desert is **126.5×
longer** than the local prime-free interval, so it comes entirely from
covering *prime* offsets, not from an ordinary prime gap.

N has 2 692 digits (6.9× smaller than the certified-gap endpoints); see
`records/megagap_2692digit_g1134871/record.json` (reconstructable as
N = N0 + 14·M from the stored 813-congruence cover).

| quantity | value |
|---|---|
| g(N) — least Goldbach summand | **1 134 871** (= 1.0196 × certified-gap record) |
| digits of N | 2 692 |
| prime offsets q < g proven non-summands | 88 239 |
| — by parity / congruence divisor / trial divisor | 1 / 85 476 / 895 |
| — by strong base-2 witness (unconditional) | 1 867 |
| prev/next prime around N | N−7 329 / N+1 641 (gap 8 970) |
| g(N) ÷ local prime gap | **126.5** |

The complement N − 1 134 871 is certified prime by the PARI/GP ECPP
certificate in `complement_cert.gp` (`primecertisvalid` = 1), and the
253-step certificate is additionally re-verified by the PARI-independent
projective-coordinate checker `ecpp_check.py`, which also asserts the
binding between the certificate's top-level candidate and N − g. The
local-gap endpoints N−7 329 and N+1 641 carry their own validated ECPP
certificates (`localgap_{prev,next}_cert.gp`), and every interior number
of that interval is deterministically composite, so the 8 970 local gap
is fully certified as well. Every negative witness is deterministic.
`verify_megagap.py` re-checks the entire record from the committed
artifacts in one run and writes `MANIFEST.sha256`. Search: E = 6.56
cover found the hit at k = 14. The larger the construction, the *easier*
the search — E = |U|·boost/ln N falls as N grows — so this game
optimizes at a ~2 700-digit N, unlike the digit-frugal bounded games
below.

**Remaining open targets from the challenge**: the absolute-known-gap
milestone g ≥ 16 045 849 (beating the largest PRP-endpoint gap) needs
π(16M) ≈ 1.03M covered offsets → M ≈ 20 000 digits and ~0.2 s/modexp,
i.e. a distributed campaign roughly 100–1000× this 4-core box.
(Superseded 2026-11-21: with a full cover and an N−1-form complement the
same milestone is ~5,700 PRP tests at 91,753 digits and needs no ECPP —
about two weeks on this box with GMP, hours on the GPU fleet or a few
dozen cores of gwnum-class FFT code; see
`proth/README.md`.) The
"1M-desert below 200 digits" bonus is beyond covering methods entirely:
a ≤192-digit modulus leaves ≥20 000 residual primes below 1.1M, giving
success density e^−400; note (log N)²·log log N ≈ 1.3×10⁶ at 200 digits,
so such an N sits at the extremal constant of the conjectured
Granville–van de Lune–te Riele maximal order.


Machinery and results for the two bounded record games defined in *Cute
Goldbach Gaps* (July 2026): for an even N, let g(N) be the least prime p
such that N − p is also prime (the least Goldbach summand).

- **Threshold game** T(100 000): find the *smallest* even N with
  g(N) > 100 000.
- **Budget game** R(10^199): find the *largest* g(N) attainable with
  N < 10^199 (fewer than 200 digits).

The paper's incumbents (both verified here with gmpy2/BPSW before we
started): a 199-digit N with g = 105 667 serving both games, and a
237-digit N with g = 109 621 for the unbounded height game.

## New record (2026-07-21): one integer beats both bounded games

**N** (197 digits, `records/dual_197digit_g107719/record.json`):

```
69391050047962771785886014481525499530404869626881147528776141740954715
09405658481222615550358933673643532753354708616005981520465642550488792
3382772685792448907579623625079335835156550325768132008
```

**g(N) = 107 719**, with the Goldbach partition N = 107 719 + (N − 107 719).

- Budget game: N < 10^199 and g(N) = 107 719 > 105 667 — **new best
  known R(10^199) lower bound**.
- Threshold game: N ≈ 6.94·10^196 < N_199 ≈ 5.83·10^198 with
  g(N) > 100 000 — **new best known T(100 000) upper bound**
  (~84× smaller than the incumbent).

### Proof structure (fully machine-checkable)

Every prime q < 107 719 (10 250 odd primes plus q = 2) has N − q
composite, witnessed in `evidence.json`:

| witness type | count |
|---|---|
| parity (q = 2) | 1 |
| congruence divisor r \| N − q from the 89-congruence cover | 9 471 |
| trial divisor < 10^5 | 378 |
| strong base-2 Miller–Rabin compositeness witness | 400 |

A strong-base-2 failure is an unconditional compositeness proof, so the
negative side is deterministic. The positive side: 107 719 is prime
(64-bit check) and N − 107 719 is proven prime by the PARI/GP ECPP
(Atkin–Morain) certificate in `complement_cert.gp`, validated with
`primecertisvalid` (see `check_cert.log`).

### Construction

N = N0 + k·M with k = 951 928, where M = 2·∏r over an 89-modulus
congruence cover (M has 191 digits) chosen so that every covered prime
q < 105 668 satisfies q ≡ N (mod r) for some cover modulus r | M, giving
N − q ≡ 0 (mod r). The cover was produced by a greedy set-cover pass
plus simulated annealing (`cover.py`, `anneal.py`) minimizing
digits(M)·ln 10 + E, where E = |U|·boost/ln N is the expected number of
prime complements among the |U| = 750 uncovered ("residual") primes —
the negative log of the per-k success density. The search
(`search.py`) scanned 165 independent CRT progressions (residue-swap
variants, `gen_variants.py`) with a small-prime sieve to 6·10^6 followed
by Fermat base-2 filtering, at ~1 850 progression elements/second on 4
cores; ≈1.4·10^8 elements were scanned before the hit, matching the
predicted density e^−18.2. The measured density model (calibrated at
Ê = 16.65 vs predicted 16.43 on a Q = 100 003 cover) was accurate to
~0.2 in E throughout.

### Comparison table

| record | paper incumbent | this work |
|---|---|---|
| T(100 000) upper bound | 5.83·10^198 (199 digits) | **6.94·10^196 (197 digits)** |
| R(10^199) lower bound | 105 667 | **107 719** |

## Closeness: every record scored against the size of its N (2026-11-21, line recomputed 2026-11-22)

The height game has no ceiling, so its records measure compute, not how
remarkable the number is. `closeness.py` scores each record by
g(N) ÷ ceiling(N), where ceiling(N) is the largest g a number of that size
is expected to have: the median of the largest g below N in the
Hardy–Littlewood model of `ceiling_model.py` (a prediction, checked as
described in the first section of this file; tabulated up to 200 digits
and continued by a formula beyond). The literal bound g ≤ N/2 is attained
only at N = 4 and 6 and is useless elsewhere.

| record | g | digits of N | ceiling at that size | closeness | × a random number of that size | digits a perfect N would have |
|---|---|---|---|---|---|---|
| exhaustive search ≤ 4·10^18 (not ours) | 9,781 | 19 | ~9,600 | 102% (inside the model's 5% to 95% range) | 131 | 19 |
| `threshold_25digit_g10357` | 10,357 | 25 | ~19,200 | 53.8% | 92 | 19 |
| `threshold_27digit_g10111` | 10,111 | 27 | ~22,600 | 44.7% | 81 | 19 |
| `threshold_30digit_g10459` | 10,459 | 30 | ~28,600 | 36.5% | 73 | 19 |
| `threshold_46digit_g20551` | 20,551 | 46 | ~80,700 | 25.5% | 79 | 25 |
| `threshold_63digit_g30139` | 30,139 | 63 | ~164,400 | 18.3% | 77 | 30 |
| `threshold_150digit_g104527` | 104,527 | 150 | ~1.1M | 9.2% | 91 | 51 |
| `budget_1e200_200digit_g112249` | 112,249 | 200 | ~2.1M | 5.3% | 69 | 53 |
| `megagap_2692digit_g1134871` | 1,134,871 | 2,692 | ~5.5·10^8 | 0.20% | 35 | 150 |
| `height_15595digit_g2000269` | 2,000,269 | 15,595 | ~2.2·10^10 | 0.0090% | 8.7 | 194 |
| `height_33938digit_g5000251` | 5,000,251 | 33,938 | ~1.1·10^11 | 0.0044% | 9.3 | 296 |
| `height_61329digit_g10000141` | 10,000,141 | 61,329 | ~3.9·10^11 | 0.0026% | 9.8 | 409 |
| `height_91752digit_g16046137` | 16,046,137 | 91,752 | ~9.0·10^11 | 0.0018% | 10.2 | 509 |

Two readings. (1) A random even number with as many digits as the 5M
record already has g near 540,000 (Hardy–Littlewood mean; measured on
random numbers at 300 and 1,000 digits, see the script's docstring), so
that record is about 9 times ordinary for its size. (2) Closeness falls
roughly like 1/ln N for every covering construction, because covers give
g proportional to ln N while the ceiling grows like ln²N. A single
closeness leaderboard is therefore won at the smallest sizes, where
exhaustive search already holds ~100%. The non-arbitrary races are the
fixed-target ones: for a given g, the smallest N (the T game; the last
column is the target), and for a given size, the largest g (the R game).

## Reproduction

```
python3 verify_record.py records/dual_197digit_g107719/record.json /tmp/ev.json
gp -q  # read complement_cert.gp; primecertisvalid(...) == 1
```

`search.py` reconstructs N as N0 + k·M from `record.json` (fields N0, M,
k) and re-derives all witnesses; nothing depends on the discovery path.

## Files

- `cover.py` — greedy weighted congruence-cover builder + CRT
- `anneal.py` — simulated-annealing cover refinement
- `gen_variants.py` — independent progression variants from a base cover
- `search.py` — multiprocess sieved progression search (Fermat filter,
  exhaustive BPSW verification of successes)
- `verify_record.py` — per-offset compositeness evidence generator
- `package_record.py` — record dir: evidence + PARI ECPP certificate
- `records/` — the record integers and their proofs
- `tscan/` — the C scanner for the small-N threshold game, with its drivers
- `closeness.py` — every record scored against the largest g expected at
  its size
- `ceiling_model.py` — that largest expected g, from the Hardy–Littlewood
  heuristic with no fitted constant; `ceiling_table.json` is its output
- `gsample.c` — g(N) for random N of a given size; `samples/` has two runs
- `record_holders.txt` — the 69 record holders of g below 4·10^18
