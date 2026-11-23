# The cover depth D(n): how far the first n odd primes can strike the primes with no luck

Give each of the first `n` odd primes `r` one residue class `a_r`. The vector *strikes* an odd
prime `q` when `q ≡ a_r (mod r)` for some `r`; then every `N ≡ a_r (mod r)` has `r | N − q`.
`D(n)` is the largest, over all vectors, of the least odd prime that is not struck. The object and
the values for `n ≤ 12` are the research session's (`goldbach/sublinear`, branch
`ccr-d4a17dd0-7uu03r`); this directory recomputes them independently and adds `n = 13, 14`.

    gcc -O3 -march=native -o depth depth.c
    ./depth 12        plain depth-first search: strike the least unstruck prime with each modulus left
    ./depth 14 1      the same with a capacity rule: to beat the best vector so far, the primes still
                      unstruck below it must fit into the fullest classes of the moduli left

| n | r_n | D(n) | D / (r ln r) | next prime squared | nodes, plain | nodes, pruned | status | one best vector (modulus:class) |
|---|---|---|---|---|---|---|---|---|
| 0 | – | 3 | – | 9 | 1 | | exact, kernel | (no modulus) |
| 1 | 3 | 5 | 1.52 | 25 | 2 |  | exact, kernel | 3:0 |
| 2 | 5 | 7 | 0.87 | 49 | 5 |  | exact, kernel | 3:0 5:0 |
| 3 | 7 | 19 | 1.39 | 121 | 16 |  | exact, kernel | 3:2 5:3 7:0 |
| 4 | 11 | 31 | 1.18 | 169 | 65 |  | exact, kernel | 3:2 5:3 7:0 11:8 |
| 5 | 13 | 43 | 1.29 | 289 | 326 |  | exact, kernel | 3:2 5:2 7:3 11:2 13:6 |
| 6 | 17 | 67 | 1.39 | 361 | 1,957 |  | exact, kernel | 3:2 5:3 7:5 11:7 13:5 17:3 |
| 7 | 19 | 103 | 1.84 | 529 | 13,700 |  | exact, kernel | 3:2 5:2 7:3 11:2 13:6 17:9 19:4 |
| 8 | 23 | 163 | 2.26 | 841 | 109,601 | 6,183 | exact, kernel | 3:2 5:2 7:5 11:7 13:5 17:9 19:3 23:13 |
| 9 | 29 | 181 | 1.85 | 961 | 986,410 | 40,403 | exact by two programs; ≥ in the kernel | 3:2 5:2 7:5 11:7 13:5 17:9 19:3 23:13 29:18 |
| 10 | 31 | 223 | 2.09 | 1369 | 9,864,101 | 259,040 | exact by two programs; ≥ in the kernel | 3:2 5:2 7:5 11:9 13:8 17:7 19:3 23:20 29:23 31:13 |
| 11 | 37 | 271 | 2.03 | 1681 | 108,505,112 | 2,272,366 | exact by two programs; ≥ in the kernel | 3:2 5:3 7:6 11:9 13:1 17:7 19:18 23:15 29:9 31:19 37:16 |
| 12 | 41 | 331 | 2.17 | 1849 | 1,302,061,345 | 18,513,174 | exact by two programs; ≥ in the kernel | 3:2 5:3 7:3 11:6 13:8 17:7 19:10 23:1 29:10 31:19 37:0 41:38 |
| 13 | 43 | 419 | 2.59 | 2209 |  | 155,637,417 | exact by `depth.c` alone; ≥ in the kernel | 3:1 5:3 7:1 11:4 13:11 17:13 19:17 23:18 29:21 31:14 37:5 41:19 43:11 |
| 14 | 47 | 499 | 2.76 | 2809 |  | 1,523,561,730 | exact by `depth.c` alone; ≥ in the kernel | 3:2 5:2 7:5 11:2 13:4 17:3 19:14 23:7 29:2 31:8 37:3 41:29 43:30 47:40 |

Timings: `n = 12` plain 13 s; `n = 13` pruned 30 s; `n = 14` pruned 5 min (one core).

## What is proved (`GoldbachGaps/CoverDepth.lean`, `GoldbachGaps/CoverDepthRun.lean`)

* The search is proved correct (`search_iff`) and run by the kernel: **`D(0), …, D(8)` =
  3, 5, 7, 19, 31, 43, 67, 103, 163 are theorems** (`isDepth_0` … `isDepth_8`). The upper bound is
  the exhaustive part. The kernel keeps every intermediate term (about 45 kB per node), so eight
  moduli are cut into eight checks and nine would need 72 of them (about five minutes); beyond
  `n = 8` only the lower bound is proved, from one vector each (`coversBelow_9` … `coversBelow_14`).
* `IsDepth.lt_cons`: a new modulus always increases the depth (it can strike the first unstruck
  prime); `IsDepth.prime`: the depth is an odd prime; `IsDepth.unique`.
* `least_summand_le_depth`: **the least Goldbach summand of an even `N` is at most the depth of
  the odd primes up to `√N`**: the residues of `N` itself strike every odd prime below its least
  summand.
* `exists_isSummand_le_depth`, `exists_isSummand_of_lt_841`: **Goldbach by covering.** If that
  depth is at most `N − 3`, `N` is a sum of two primes, one of them at most the depth. With
  `D(0..8)`: every even number from 6 to 840 is a sum of two primes, one at most 163, and no
  `N − q` is tested for primality. In the table, compare `D(n)` with the next prime squared:
  "`D(n) < (next prime)² − 2` for all `n`" would be Goldbach's conjecture, with much room.
* `exists_isLeastSummand_ge_depth`: conversely (Dirichlet), arbitrarily large even numbers have
  least summand at least the depth.
* `isRecord_and_isDepth`: **the terms 6, 12, 30, 98 of A025018 attain the depth of their own
  small primes** (3, 5, 7, 19): they are the best vectors on no modulus, on 3, on 3, 5 and on
  3, 5, 7 (98 ≡ 2, 3, 0). From 220 on a term stays below it (`g(220) = 23` against `D(5) = 43`):
  an even `N` below the next prime square carries one vector, and from four moduli on there are
  far more vectors (2·3·5·7·11 = 2310) than such `N` (below 169), so the best vector does not occur
  in time. This is the point where "forcing" the sequence stops working
  (`scripts/record_gen/README.md`).
* `coversBelow_15907` … `coversBelow_16981`: the complete covers certified for the 200-digit
  search are lower bounds: the depth of the 89, 91, 92, 93 odd primes up to 463, 479, 487, 491 is
  at least 15907, 16381, 16747, 16981.

## What it means for the 200-digit search

Nothing changes in the cost model. The depth is the part of a least summand that divisibility
alone can force; the records at 200 digits (158,209) are about nine times the certified covers
(16,981), and the difference is luck on what the cover leaves. `D(n)` measures how good a cover
can be at all, not how to find one below `10^200`.
