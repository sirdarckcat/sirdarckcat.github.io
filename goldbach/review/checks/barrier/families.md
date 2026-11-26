# Audit, lens "enumerable families and constructions" (KEY=families)

Scripts and outputs: `audit/run/families/` (`common_integer.py/.out`, `cover_checks.py/.out`, `entropy_bottom.py/.out`).
Cover used: first line of `origin/ccr-d4a17dd0-7uu03r:goldbach/fscan/cover/starts/q213070_m89.txt` (verified: 1,609 rows).

## Verdict
No loophole found in this lens. The barrier holds for every family examined; the one bounded lever is
engineering worth at most about half a nat. (P') stays open: nothing here proves it impossible.

## Why the lens closes (three facts)
1. Pigeonhole. Any set of N < X whose members share a class modulo each prime of a set S has at most X/prod(S) + 1
   members (team: `card_prescribed_le`, `move_budget`). The 1,609-row cover fixes 443.6 of 460.5 nats, so every
   usable family is, per cover, a subset of one progression N0 + kM with k < e^16.88 = 2.14e7. S-unit, Lucas,
   elliptic-divisibility, sparse and lattice families cannot contain more.
2. Price of sparsity (measured). Giving cover primes back to make room for a thin family costs 0.027 to 0.033 nats
   of luck per nat freed (1 prime: +0.21 nats; 8: +1.32; 24: +4.06; 45: +7.72). A family that keeps a fraction
   e^-sigma of the integers therefore loses about 0.03*sigma nats and must earn it back elsewhere.
3. Compositeness with no small factor comes only from algebraic identities (at most sqrt(Q) rows, team's thin-set
   bound) or from luck.

## Measurements
Reference: 19,050 rows; random nonzero classes 2,278.8 +- 23.9 (min 2,198 of 300); team cover 1,609;
boost 11.0448, p = 0.02398, E = 39.06 nats.

### Common integer (Erdos-Rankin), N = t mod every odd prime <= 463
| t range (even t) | min rows | at t | mean |
|---|---|---|---|
| [100,000, 213,070] | 2,129 | 211,664 = 2^4 * 13,229 | 3,527 |
| (Q, 2Q] | 1,975 | 352,448 | 3,186 |
| (2Q, 4Q] | 2,006 | 429,404 | 3,247 |
| [-2Q, 0) | 1,994 | -121,522 | 3,203 |

From t = 211,664: 20 largest primes re-choose greedily -> 1,954 (best over the 30 best t: 1,954, mean 1,990);
20 smallest -> 2,125; all 89 by coordinate descent -> 1,764. Control from random classes: top-20 -> 2,153;
all-89 -> 1,736 mean, 1,708 best. Block variant (primes <= z fullest class, rest common integer, t in [-2Q, 4Q]):
1,975 (z=7), 2,004 (13), 2,027 (23), 2,038 (43), 1,979 (73), 1,962 (101), 1,923 (151), 1,871 (199).
Best hybrid is 345 rows (8.4 nats) worse than 1,609 in the task's form, 262 rows (6.4 nats) in the best block form.
Reason: the common integer sits at the Buchstab minimum (u = 2, omega = 0.5 against 0.5615), a factor 0.87 to 0.93
of random; tempering reaches 0.706.

### Extra cover primes beyond 463 (greedy, on the 1,609 rows)
467..499 kill 9 each, 503: 8, 509: 10, 521: 7, 523: 8. Cumulative: 6 primes 1.29 nats, 9 primes 1.89, 12 primes
2.48, 16 primes 3.23, 24 primes 4.64. That is 0.218 falling to 0.193 nats per prime, 0.0355 falling to 0.0306 per
nat of modulus. Confirms the team's "about 0.2 nats per extra prime".

### Exponential families, order collapse
N = j*a^n + c with j, c fixed, n = n0 mod L: best L fixes classes worth 108 nats (a=2, L=660, 49.5 nats on cover
primes), 100 (a=3), 89 (a=5), 85 (a=7), 72 (a=10), always against ln(a^L) = 327 to 457 nats, and leaves one
member. With j or c free the family is an ordinary congruence class.

### Number of near-optimal covers
File: 10 distinct covers with 1,609 rows, 1,259 with 1,610 (all verified). Exact count within Hamming distance 2 of
one best cover: 5 / 122 / 847 / 3,934 / 15,324 / 49,510 / 139,629 vectors with exactly 1,609..1,615 rows.
The table in `ideal_tilt_213070.txt` has ln g = -20.88, -13.61, ..., 8.82 for the same k: low by at least 23 nats
at 1,609, 21 at 1,610, 3.4 at 1,615 (cumulative). The README already says so ("20 nats low at the very bottom").
Effect on the headline: under 0.2 nats.

## Family by family
| family | kill | number |
|---|---|---|
| S-unit N = c + j*prod a_i^n_i | pigeonhole; e^20.5 (4 bases), e^39.3 (10), e^69 (25), e^128 (all 90 primes <= 463) members (`smooth_count.py`) | sparsity >= 332 nats -> about 10 nats lost |
| Lucas / elliptic divisibility | pigeonhole + supply | <= 664 terms (Lucas), ~30 (EDS) against e^39 needed |
| common integer | measured | 1,954 best hybrid vs 1,609: -8.4 nats |
| dual view, stretch of consecutive N | team's count stands | no cover: e^-46.6 at 170,000 vs e^-30 |
| N above a large prime gap | gap needs all odd offsets | merit 77 needed for 320 rows; record ~42 |
| sparse N = 2^n + d | 51 nats of freedom against 443.6 | saving <= 0.4 nats even if free |
| 2-parameter lattice | same progression re-parametrised | setup share <= 20% of sieve: <= 0.1 nat |
| sumset members A + B via merge | bounded | about +0.5 nat gross, 0 +- 0.5 net |

## Corrections to the brief / team documents
- "Meet in the middle extends the line by m nats only": true for two lists. With 2^t lists it is t*m, paid for by
  2^t*m nats of class entropy. Gross gain peaks near +1.0 nat (t = 1 or 2, m = 20) and is negative at t = 4.
- README point 3 says memory e^21 "extends the reach by one prime"; the brainstorm verdict says three moduli for two
  lists and six for four. The second is the right count.
- Single-member covers lose the amortised sieve: about 2 microseconds a member (23 test-equivalents) against 23 to
  29 ns, 4.4 nats. The team's "net 0.2 to 0.4" for oversized covers does not show this charge.
- Closure theorem section 13b prices ExpFamily "one offset per order condition" and stops at "419 offsets". An order
  condition fixes N mod s and kills the whole class; the family dies by pigeonhole (<= 664 members with j, c fixed).
  Verdict unchanged, argument and number are not the right ones.
- Shortfall: E = 39.06 for the 1,609 cover against e^30.75 is 8.3 nats (README table: 8.5). The brief's 7.7 is 0.6
  to 0.8 optimistic unless the budget figure is newer.

## Price list entry from this lens
Fifteen extra cover primes (to 557) bring E to about 30.75: N < 10^241 instead of 10^200 buys the whole shortfall
(6.6 nats from the lower prime density, 2.6 from 125 fewer rows, -1.0 from the larger boost). 213,070 would then be
6.9% of the 241-digit ceiling.
