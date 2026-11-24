# The rank experiment as theorems, below 2^25

`scripts/rank_records` found patterns in a scan. Here the scan is replaced, below
2^25 = 33,554,432, by proofs that Lean's kernel checks: `GoldbachGaps/RankSieve.lean`
(generated) on top of `GoldbachGaps/BitSieve.lean` (the method).

    gcc -O2 -o classmax classmax.c && ./classmax 33554432 6 10 14 30 42 70 210 22 26 > scan_2e25.txt
    gcc -O2 -o topten topten.c && ./topten 33554432 6 1368 >> scan_2e25.txt
    python3 -I ../gen_ranksieve.py scan_2e25.txt ../../GoldbachGaps/RankSieve.lean
    (put the "classmax" and "witness" lines it prints into ../rank_records/certified.txt, then)
    python3 -I ../gen_least.py ../rank_records/certified.txt ../../GoldbachGaps/RankData.lean

`scan_2e25.txt` only tells the generator which statements to ask for. A wrong line makes the
build fail; it cannot make a false theorem pass.

## What is proved (for every even N with 6 ≤ N < 2^25)

| statement | Lean name |
|---|---|
| N is a sum of two primes, the smaller at most 997 | `RankSieve.exists_summand_le` |
| N has a larger least summand than every smaller even number iff N is one of 6, 12, 30, 98, 220, 308, 556, 992, 2642, 5372, 7426, 43532, 54244, 63274, 113672, 128168, 194428, 194470, 413572, 503222, 1077422, 3526958, 3807404, 10759922, 24106882, 27789878 | `RankSieve.isRecordHolder_iff` |
| if 3 divides N the least summand is at most 379 (attained at 29012496) | `exists_summand_le_of_dvd_6` |
| if 5 divides N: at most 619 (31083410); 7: 661 (21184688); 11: 683 (22360822); 13: 709 (14131052) | `…_dvd_10`, `…_dvd_14`, `…_dvd_22`, `…_dvd_26` |
| if 15 divides N: at most 239 (23188020); 21: 269 (16541868); 35: 439 (22512140); 105: 157 (29764560) | `…_dvd_30`, `…_dvd_42`, `…_dvd_70`, `…_dvd_210` |
| if 3 divides N and N > 1362, ten smaller even numbers have a least summand at least as large: N never enters the ten largest | `RankSieve.notAmongTen_of_dvd_6` |

The last line is the pattern of the experiment ("no arrival is divisible by 3"), as a theorem on
this range. 1362 is the last multiple of 3 that does enter the ten largest (rank 8, by the scan).
The bounds fall with the prime: 379, 619, 661, 683, 709 for 3, 5, 7, 11, 13, against 997 for all
even numbers; that is the Goldbach singular series (a prime factor p of N multiplies the number
of representations by (p − 1)/(p − 2)), seen as a theorem on a range instead of a heuristic.

## How

The kernel cannot test thirty million numbers one by one, but it can do arithmetic on numbers
with a million binary digits. `BitSieve.lean` keeps the primes of an interval as the digits of
one natural number:

* the multiples of d are the digits of a number built by doubling (`multMask`), and a pass of
  the sieve is `P xor (P and mask)`;
* a digit that survives the passes for all primes below D, in an interval ending below D², is a
  prime (`prime_of_testBit_segSieve`; nothing is claimed for the digits that were cleared);
* "N − q is prime for some q ≤ G" is the union of the prime mask shifted by each q
  (`unionShift`), and "every N of [A, B) divisible by m" is one more mask (`specMask`); the test
  is a single equality of big numbers (`specCheck`), and `holds_of_segCheck` turns it into the
  statement about Goldbach summands.

33 sieves of about a million numbers each (760 passes; 2.5 s and one gigabyte of intermediate
numbers per sieve in the kernel) and a trial-division check below 4096. `RankSieve.lean` builds
in about 90 s and needs about 7 GB of memory; it sets `Elab.async false` so that the sieves run
one at a time.

What is not proved here: anything beyond 2^25 (the method would go on at the same cost per
number, roughly 3 s per million), and the statistical patterns (quadratic non-residues,
clusters), which are not statements about every N.
