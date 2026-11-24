# The cover depth D(n): how far the first n odd primes can strike the primes with no luck

Give each of the first `n` odd primes `r` one residue class `a_r`. The vector *strikes* an odd
prime `q` when `q ≡ a_r (mod r)` for some `r`; then every `N ≡ a_r (mod r)` has `r | N − q`.
`D(n)` is the largest, over all vectors, of the least odd prime that is not struck. The object and
the values for `n ≤ 12` are the research session's (`goldbach/sublinear`, branch
`ccr-d4a17dd0-7uu03r`); this directory recomputes them independently and adds `n = 13, 14, 15` (all three since
confirmed by the research session's own program, with another best vector at `n = 15`).

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
| 9 | 29 | 181 | 1.85 | 961 | 986,410 | 40,403 | exact, kernel (72 pieces) | 3:2 5:2 7:5 11:7 13:5 17:9 19:3 23:13 29:18 |
| 10 | 31 | 223 | 2.09 | 1369 | 9,864,101 | 259,040 | exact by two programs; ≥ in the kernel | 3:2 5:2 7:5 11:9 13:8 17:7 19:3 23:20 29:23 31:13 |
| 11 | 37 | 271 | 2.03 | 1681 | 108,505,112 | 2,272,366 | exact by two programs; ≥ in the kernel | 3:2 5:3 7:6 11:9 13:1 17:7 19:18 23:15 29:9 31:19 37:16 |
| 12 | 41 | 331 | 2.17 | 1849 | 1,302,061,345 | 18,513,174 | exact by two programs; ≥ in the kernel | 3:2 5:3 7:3 11:6 13:8 17:7 19:10 23:1 29:10 31:19 37:0 41:38 |
| 13 | 43 | 419 | 2.59 | 2209 |  | 155,637,417 | exact by two programs; ≥ in the kernel | 3:1 5:3 7:1 11:4 13:11 17:13 19:17 23:18 29:21 31:14 37:5 41:19 43:11 |
| 14 | 47 | 499 | 2.76 | 2809 |  | 1,523,561,730 | exact by two programs; ≥ in the kernel | 3:2 5:2 7:5 11:2 13:4 17:3 19:14 23:7 29:2 31:8 37:3 41:29 43:30 47:40 |
| 15 | 53 | 613 | 2.91 | 3481 |  | 18,318,280,161 | exact by two programs; ≥ in the kernel | 3:2 5:2 7:6 11:10 13:8 17:11 19:8 23:18 29:19 31:3 37:14 41:31 43:34 47:23 53:8 |
| 16 | 59 | 709 | 2.95 | 3721 |  |  | exact by the uarch session's program (rechecked by the research session); ≥ in the kernel | 3:2 5:2 7:6 11:10 13:8 17:11 19:8 23:15 29:19 31:3 37:2 41:31 43:34 47:3 53:6 59:34 |
| 17 | 61 | 739 | 2.95 | 4489 |  |  | exact by the uarch session's program (rechecked by the research session); ≥ in the kernel | 3:2 5:3 7:6 11:1 13:5 17:7 19:18 23:19 29:19 31:23 37:24 41:36 43:36 47:33 53:17 59:41 61:12 |
| 18 | 67 | 859 | 3.05 | 5041 |  |  | exact by the uarch session's program (rechecked by the research session); ≥ in the kernel | 3:2 5:2 7:6 11:10 13:8 17:11 19:8 23:15 29:8 31:23 37:5 41:40 43:21 47:3 53:48 59:31 61:11 67:19 |

Timings: `n = 12` plain 13 s; `n = 13` pruned 30 s; `n = 14` pruned 5 min; `n = 15` pruned 66 min (one core).
The values for `n = 16, 17, 18` are from a faster search of the uarch session (`desert_fast3.c`, branch
`ccr-b8c25887-i6tn9f`), not from `depth.c`.

## What is proved (`GoldbachGaps/CoverDepth.lean`, `GoldbachGaps/CoverDepthRun.lean`)

* The search is proved correct (`search_iff`) and run by the kernel: **`D(0), …, D(9)` =
  3, 5, 7, 19, 31, 43, 67, 103, 163, 181 are theorems** (`isDepth_0` … `isDepth_9`). The upper
  bound is the exhaustive part. The kernel keeps every intermediate term (about 45 kB per node),
  so eight moduli are cut into eight checks and nine into 72 (five minutes); ten would need 720
  (about an hour) and was not done; beyond
  `n = 9` only the lower bound is proved, from one vector each (`coversBelow_10` … `coversBelow_18`).
* `IsDepth.lt_cons`: a new modulus always increases the depth (it can strike the first unstruck
  prime); `IsDepth.prime`: the depth is an odd prime; `IsDepth.unique`.
* `least_summand_le_depth`: **the least Goldbach summand of an even `N` is at most the depth of
  the odd primes up to `√N`**: the residues of `N` itself strike every odd prime below its least
  summand.
* `exists_isSummand_le_depth`, `exists_isSummand_of_lt_841`: **Goldbach by covering.** If that
  depth is at most `N − 3`, `N` is a sum of two primes, one of them at most the depth. With
  `D(0..9)`: every even number from 6 to 960 is a sum of two primes, one at most 181
  (`exists_isSummand_of_lt_961`), and no `N − q` is tested for primality. In the table, compare `D(n)` with the next prime squared:
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

## The greedy rule, and a certified vector on 167 moduli (`greedy.py`, `greedy.txt`)

The research session measured how far the plainest rule reaches: take the odd primes up to `x` in
increasing order and give each the nonzero class that contains the most odd primes below `y` not
yet covered. `greedy.py` recomputes its table with independent code:

| x | moduli | first odd prime not covered | research session | / (x ln x) | / (x ln² x) |
|---|---|---|---|---|---|
| 23 | 8 | 127 | 126 | 1.76 | 0.56 |
| 53 | 15 | 379 | 372 | 1.80 | 0.45 |
| 100 | 24 | 1,039 | 1,021 | 2.26 | 0.49 |
| 200 | 45 | 3,343 | 3,315 | 3.15 | 0.60 |
| 463 | 89 | 9,769 | 10,428 | 3.44 | 0.56 |
| 1,000 | 167 | 29,581 | 30,184 | 4.28 | 0.62 |
| 3,000 | 429 | 131,203 | 132,567 | 5.46 | 0.68 |
| 10,000 | 1,228 | 600,697 | 601,525 | 6.52 | 0.71 |

The two codes agree within a few percent; the differences come from how ties are broken and
from the fact that "nothing is left" is not monotone in `y`, so a bisection finds one threshold
among several. Both show the same thing: the reach grows like `0.6` to `0.7` times `x ln² x`,
faster than the `1.349 · x ln x` that is proved (`GoldbachGaps/CoverBound.lean`).

Scanning `y` and breaking ties at random does better than the bisection: on the 167 odd primes
up to 997 one vector covers every odd prime below **32,971** (`greedy_997_vector.txt`). That
vector is certified by the kernel, by divisibility alone (`GoldbachGaps/Cover32971.lean`, a
416-digit `N`), and `coversBelow_32971` in `GoldbachGaps/CoverDepthGreedy.lean` states it as a
lower bound for the cover depth of 167 moduli. For comparison `1.349 · x ln x` is 9,290 at
`x = 997` and `0.7 · x ln² x` is 33,300. No run out of 40 left nothing uncovered for any `y` from
33,000 to 37,000.

The same on the 429 odd primes up to 2,999: one vector covers every odd prime below **135,511**
(`greedy_2999_vector.txt`), certified in `GoldbachGaps/Cover135511.lean` (a 1,274-digit `N`,
17 kernel block checks, under four minutes) and stated as `coversBelow_135511`. There
`1.349 · x ln x` is 32,390, so the certified reach is 4.2 times the proved bound; it is
`0.705 · x ln² x`. No run out of 16 left nothing uncovered from `y` = 134,000 to 146,000 except
the two that gave 134,839 to 135,511.

| moduli | largest prime | certified: every odd prime below | `1.349 · x ln x` | ratio |
|---|---|---|---|---|
| 24 | 97 | 1,471 (research session's tempered vector, `coversBelow_1471`) | 599 | 2.5 |
| 45 | 199 | 4,909 (the same, `coversBelow_4909`) | 1,421 | 3.5 |
| 61 | 293 | 8,311 (the same, `coversBelow_8311`; the three vectors are in `tempered_97_199_293_vectors.txt`) | 2,245 | 3.7 |
| 89 to 93 | 463 to 491 | 15,907 to 16,981 (research session's covers) | 3,830 to 4,100 | 4.1 |
| 167 | 997 | 32,971 (greedy) | 9,290 | 3.5 |
| 167 | 997 | 40,111 (research session's tempered vector, `tempered_997_vector.txt`, `coversBelow_40111`) | 9,290 | 4.3 |
| 429 | 2,999 | 135,511 | 32,390 | 4.2 |
| 1,228 | 9,973 | 614,101 (greedy, plain rule at `y` = 614,000; `greedy_9973_vector.txt`, `coversBelow_614101`; a 4,298-digit `N`, 75 kernel block checks, 17 minutes) | 123,900 | 5.0 |

    python3 -I greedy.py 23 53 100 200 463 1000 3000 10000 > greedy.txt

## What it means for the 200-digit search

Nothing changes in the cost model. The depth is the part of a least summand that divisibility
alone can force; the records at 200 digits (160,357) are about nine times the certified covers
(16,981), and the difference is luck on what the cover leaves. `D(n)` measures how good a cover
can be at all, not how to find one below `10^200`.
