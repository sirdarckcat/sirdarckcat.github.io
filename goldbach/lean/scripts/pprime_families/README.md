# The four families for (P′), run on the miniature

The research session asked (25 November) for the four known families of methods that could reach beyond the
Chinese-remainder line to be *run as algorithms* on the miniature, so that "ruled out" rests on a measurement:

1. Chinese remaindering with errors or with lists, by lattice reduction;
2. meet in the middle on the linear form of the residues;
3. the generalised birthday tree (Wagner);
4. hashing / bucketing by the residues modulo the primes beyond the line.

**Result: none of them gains.** Everything below is counted on the exact enumeration of the miniature, no model.

| family | version run (the one closest to the reference, see below) | work, units | successes collected | gain in nats over cover first at 1 / 3 / 10 / 30 successes | the cover-first prefix scored with the same work: successes; gains |
|---|---|---|---|---|---|
| 1. lattices | one-class lists on the 37 primes 29..199, lattice of dimension 39 | 39.6 million (one reduction, 4.35 s) | 0: the decoder returns nothing | none | 178; +5.44 / +5.07 / +3.00 / +2.65 |
| 2. meet in the middle, lists beyond the line only | the 3 best classes of 29 | 17.5 million | 15 | +0.97 / +1.87 / −0.58 / – | 124; +5.44 / +5.13 / +3.04 / +2.60 |
| | a third of the classes of 29..47 (6 primes; first size at which the join is needed) | 181,463 | 1 | −0.63 / – / – / – | 7; +2.06 / +3.21 / – / – |
| 2. meet in the middle as N = N1 + k·M (best covers joined with lists beyond the line) | covers with at most 28 rows left at depth 23, half of the classes of 29 | 180,822 | 4 | +2.22 / +2.05 / – / – | 7; +2.06 / +3.21 / – / – |
| 3. four-list tree | half of the classes of 29..59 (8 primes) | 610,886 | 1 | −1.68 / – / – / – | 18; +4.42 / +3.25 / +2.68 / – |
| 4. bucketing, tables of listed class tuples | covers with at most 33 rows left, 16 tables of 3 primes among the first 10, a third of the classes | 7.47 million | 55 | +1.35 / +3.00 / +2.42 / +1.26 | 74; +5.44 / +5.23 / +2.79 / +1.48 |
| 4. bucketing, one table modulo 29·31·37·41 mixed with the cover | 10,000 members kept | 10,546 | 2 | +2.48 / – / – / – | 2; +2.65 / – / – / – |
| | 1,000,000 members kept | 1,058,066 | 27 | +4.22 / +4.27 / +2.89 / – | 29; +5.60 / +5.64 / +3.17 / – |

"–" means that the candidates do not contain that many successes. Over all 179 configurations of families 2 to 4
(`table.md`) **none contains more successes, or more of the best members, than the cover-first prefix scored with
the same work**; the shortfall is 0.19 to 6 nats, or everything. Family 1 cannot be instantiated at this size at all.
The positive entries in the gain column come from the scoring at depth 200 that every candidate receives, not from
the family: a random sample scored at depth 200 also "gains" (`refs.txt`).

## What is measured

**The miniature** (as in the research session's `toy_exact.c`, and `../mini_check/` here): X = 10^9, target 1,000
(167 rows, the odd primes below 1,000), Chinese-remainder line at 23, deeper sieve to 200. The 157,947,020 *members*
are the even N in [1202, 10^9) with no prime factor from 3 to 29; exactly 256 are *successes* (N − q composite for
every row q). `truth.c` writes, for every member, the rows left at depth 23, the rows left at depth 200 and the
success flag; `refs.py` recomputes the two published orders from that file and finds the published numbers exactly:

| successes wanted | N examined, cover first (rows left at depth 23) | N examined, ideal (rows left at depth 200) | prize, nats |
|---|---|---|---|
| 1 | 2,982 | 13 | 5.44 |
| 3 | 63,350 | 401 | 5.06 |
| 10 | 253,380 | 10,811 | 3.15 |
| 30 | 1,205,425 | 73,849 | 2.79 |

**How a family is judged.** A family puts forward candidates N. Those that are members are scored at depth 200 and
examined in increasing order of rows left (random inside a level, as in `toy_compare.py`); "N examined for t
successes" is read off that order and the gain is ln(cover first / family), with the cover-first numbers of the table
above. `table.md` also gives the gain when the candidates are examined in cover-first order *without* being scored.

**Unit of work**: one member scored at depth 200, that is 45 reductions modulo 3..199, 45 ORs of three-word masks and a
popcount; `unit.c` measures 110 ns (91 ns when the residues up to 23 come with the cover). Conversion:

- every modular reduction or multiplication, every comparison of a sort or binary search, every table probe and every
  candidate written counts as one operation, and 90 operations are one unit;
- every member among the candidates costs one unit (its scoring);
- memory is reported as a number of stored entries (16 bytes each) and not converted;
- lattice reduction is converted by CPU time (seconds / 110 ns).

`results.jsonl` also records the CPU time of every generation; converting by time instead of by operations changes
no conclusion (the generation is usually a small part of the work, and where it is not, it is the larger part by a
factor of tens to thousands).

**The reference: the same work spent on the cover.** Take the first W members in cover-first order, score them at
depth 200 and examine them in that order (`refs.py`, `refcurve.py`). This is what any amount of work W buys with no
new idea:

| work W | successes among the W | N examined for 1 / 3 / 10 / 30 | gain over cover first at 1 / 3 / 10 / 30 |
|---|---|---|---|
| 10,000 | 2 | 203 / – / – / – | +2.69 / – / – / – |
| 100,000 | 4 | 290 / 4,859 / – / – | +2.33 / +2.57 / – / – |
| 1,000,000 (0.63% of the members) | 28 | 11 / 216 / 10,299 / – | +5.60 / +5.68 / +3.20 / – |
| 10,000,000 | 92 | 13 / 354 / 11,263 / 152,010 | +5.44 / +5.19 / +3.11 / +2.07 |
| 157,947,020 (all) | 256 | 13 / 401 / 10,811 / 73,849 | +5.44 / +5.06 / +3.15 / +2.79 |

A random sample of W members scored the same way: 1.2 successes at W = 10^6 (−2.73 at one success), 16 at 10^7
(+1.68 / +2.51 / +0.03 / –). So a family *selects* if it does better than a random sample of the same size, and it
*gains* only if it does better than the cover-first prefix of the same work. In the miniature the first 0.63% of the
cover-first order, once scored, already reaches 1, 3 and 10 successes as soon as the ideal order does (11 / 216 /
10,299 numbers examined against 13 / 401 / 10,811), so that prefix collects the whole prize at 1 to 10 successes; a
method for (P′) has to beat it at equal work, not merely beat the unscored cover-first order.

**The robust count.** One or three successes are one or three particular numbers, so "N examined for 1 success" is
decided by whether one particular N is among the candidates. Every row therefore also carries the number of members
with at most 9, 10 and 12 rows left at depth 200 (401, 1,965 and 33,598 in all) that the candidates contain, next to
the same count for the cover-first prefix of equal work and for a random sample of equal size.

## 1. Lattices (`lattice_decode.py`, `agree.c`)

Instance: the 37 primes s = 29..199 (their product P has ln P = 169.34), for each a list of its best classes (ranked
by rows struck), unknown N′ = N/2 < 5·10^8 (ln B = 20.03). The decoder is Howgrave-Graham's form of Coppersmith's
method as used for Chinese-remainder codes: a monic polynomial G of degree l (the list size) with G(N′) ≡ 0 modulo
every prime at which N′ is in the list, the lattice of x^j P^(a−i) G^i and x^j G^a evaluated at xB, reduced by LLL
(python-flint). Each run comes with a certified threshold: every N′ < B whose *agreement amplitude* (the sum of ln s
over the primes where it agrees) exceeds (ln √d + ln |v|)/a is an integer root of the reduced polynomial.

The decoder works (`lattice_planted.txt`): an N′ planted with amplitude just above the certified threshold is
recovered in 5 trials out of 5 at every size tried. On the miniature's own lists it returns nothing
(`lattice_real.txt`), because nothing that high exists (`agree.txt`, every even N below 10^9 enumerated):

| lists | asymptotic radius √(l · ln B · ln P), nats | certified threshold reached (dimension, CPU) | largest agreement that exists | decoder output |
|---|---|---|---|---|
| best class of each prime | 58.2 | 60.9 (39, 4.35 s = 39.6 million units) | 36.9 nats; at most 8 of the 37 primes (6 numbers) | none |
| best 2 classes | 82.4 | 88.3 (31, 1.24 s) | 45.5 nats; at most 10 primes (5 numbers) | none |
| best 3 classes | 100.9 | 107.3 (34, 1.17 s) | 55.1 nats; at most 12 primes (2 numbers) | none |
| best third of the classes | above ln P for every l > ln P / ln B = 8.45 | not instantiable: the lists hold 9 to 66 classes | 133.7 nats; at most 29 primes | – |

The weighted (soft-decision) form of Guruswami, Sahai and Sudan needs a weighted agreement of
√(ln B · Σ w²/ln s): with weight 1 on the listed classes that is 12.8 primes for one-class lists (8 exist), 18.1 for
lists of 2 (10 exist), 22.2 for lists of 3 (12 exist) and 75.3 for lists of a third (more than the 37 primes there
are); with weight equal to the rows struck by the class it is 268 incidences, where an N sitting in the best class of
every prime at once would have 142 and the best N that exists has 106; with centred weights 107 against 67 and about
32. So the method cannot be instantiated on the miniature: the agreement it needs is 1.6 to 2 times the largest that
exists for short lists, and for the lists that matter (a third of the classes) it exceeds total agreement.

## 2. Meet in the middle (`families.c`, modes `mitm` and `prefix`)

For a set T of primes beyond the line and a list of classes for each, the even N < X in every list are the sums
x + y mod P (P = 2∏T) of two Chinese-remainder half-sums that fall in [0, X): one half sorted, the other looked up
by binary search. When P ≤ X no join is needed, the product of the lists is a union of progressions. The output was
checked against a direct filter of the member file.

**Lists beyond the line only** (20 configurations: the best 1, 2, 3 classes, a third, a half, of the first 1 to 10
primes beyond the line). The candidates are members with good classes modulo a few primes beyond 23 and an arbitrary
cover. They contain 1.2 to 3.7 times as many of the best members as a random sample of the same size, and 0 to 16%
of what the cover-first prefix of equal work contains (−1.8 nats or worse). The reason, measured: the members in the
best class of 29 (one in 28) have 23.05 rows left at depth 200 on average against 23.34 for all members, the best
28th of the members by cover have 19.19; a selection of one in 28 buys 0.3 rows beyond the line and 4.2 on it.

**Where the join stops being free.** With lists of a third of the classes:

| primes | residue vectors in the product | members found | work, units | units per member found | memory, entries |
|---|---|---|---|---|---|
| 29..47 (6) | 2.9·10^6 | 175,071 | 181,463 | 1.04 | 3,438 |
| 29..59 (8) | 9.5·10^8 | 18,097 | 29,643 | 1.64 | 61,755 |
| 29..67 (10) | 4.2·10^11 | 1,883 | 294,436 | 156 | 1,295,640 |

and with lists of a half: 523,243 members for 608,643 units on 8 primes (1.16 per member), 126,847 members for
2,833,704 units on 10 primes (22 per member, 10.4 million entries in memory). Scoring a member costs 1 unit, so from
ten primes on the generation alone costs tens to hundreds of times the scoring of what it finds: this is the
condition "list entropy at most twice the log of the number of solutions" with the numbers of the miniature.

**N = N1 + k·M with sorted lists** (128 configurations). N1 runs over the residues modulo M = 2·3·5···23 of the best
covers (at most c rows left at depth 23, c = 28..35), sorted or tabulated by N1 mod ∏T; for each k < X/M and each
tuple of listed classes the matching N1 are read off. This is the form that keeps the cover exact and adds lists
beyond the line. Every configuration contains fewer of the best members than the cover-first prefix of equal work:
83% at best (covers ≤ 28 rows, half of the classes of 29), typically a half, down to 0.4% for one-class lists. The
milder the lists, the closer to the reference, and the reference is the case of no list at all.

At one success, 21 of the 128 configurations examine fewer N than the reference, and all 21 are one event: the best
success of the miniature, N = 60,119,912 (7 rows left at depth 200, 29 at depth 23), happens to lie in the fourth
best of the 28 classes of 29, so every configuration whose list on 29 is the best third or the best half contains it,
and a smaller set that contains it reaches it sooner (the same N is in the worst class of 31). At 3 successes two
configurations do better, at 10 and 30 none.

## 3. The four-list tree (`families.c`, mode `ktree`)

Four lists of Chinese-remainder partial sums; pairs (1, 2) whose sum falls in a window of width A, pairs (3, 4) whose
sum falls in the complementary window, joined on the final interval; one window finds the share A/P of the solutions
and successive windows find them all. Run over all windows it returns exactly the set of the meet in the middle
(identical outputs on 29..59 with lists of a third; identical member counts in the five configurations both ran), with
less memory and about the same work:

| lists, primes | work, units (meet in the middle) | memory, entries (meet in the middle) | members found |
|---|---|---|---|
| a third, 29..59 (8) | 29,966 (29,643) | 1,122 (61,755) | 18,097 |
| a third, 29..67 (10) | 194,408 (294,436) | 10,943 (1,295,640) | 1,883 |
| a half, 29..67 (10) | 2,395,819 (2,833,704) | 36,075 (10,443,780) | 126,847 |
| a half, 29..73 (12) | 127,234,907 (not run: 3 GB per list) | 80,934 | 30,725 |
| a third, 29..73 (12) | 9,181,150 | 23,334 | 184 |

So the tree extends the reach in memory, not in work: on 12 primes with lists of a half it spends 127 million units,
four fifths of the cost of scoring every member of the miniature, to find 30,725 members holding no success and 2 of
the 1,965 best members. A single window is no cheaper per member found (a third on 10 primes: 1,411 units for 7
members; a half on 12 primes: 13,137 units for 2 members). The candidates are those of family 2, so is the verdict.

## 4. Bucketing (`families.c`, mode `bucket`; `bucket_soft.py`)

**Tables of listed class tuples** (19 configurations). Each table takes a random subset of t primes among the first
ones beyond the line; the bucket of an N is its residue vector on the subset, and the buckets whose key is a tuple of
listed classes are read out (progressions, or the join above when the modulus exceeds X); the union over the tables
is put forward. On all members: 0.2 to 18% of what the cover-first prefix of equal work contains. On the best covers
(each table a run of the sorted-list variant): 52% at best.

**One table mixed with the cover**, the strongest form found. A table indexed by N mod 29·31·37·41 (1.36 million
buckets, small enough for a second-level cache) holds the incidences of the bucket's four classes with the rows;
members of the best covers are looked up (one reduction, one probe) and kept when
rows left at depth 23 − λ·(bucket value − average) is small, so that a member of a worse cover is kept only from a
better bucket. With λ = 0.1, over 8 tie-breaks (`bucket_soft_reps.txt`), best members (at most 10 rows left at depth
200) captured against the cover-first prefix of equal work:

| members kept | work | table | cover-first prefix | ratio, nats | successes, table / prefix |
|---|---|---|---|---|---|
| 10,000 | 10,546 | 83.6 ± 0.5 | 74.4 ± 1.9 | +0.12 | 2.0 / 2.0 |
| 30,000 | 32,269 | 157.9 ± 1.1 | 151.1 ± 2.6 | +0.04 | 2.0 / 2.4 |
| 100,000 | 107,872 | 297.9 ± 0.3 | 300.0 ± 2.8 | −0.01 | 4.0 / 4.2 |
| 300,000 | 323,107 | 532.8 ± 1.9 | 525.1 ± 4.5 | +0.01 | 12.0 / 13.1 |

That is the effect of ordering the members of one cover level by four more primes instead of at random: a tenth of a
nat where the work ends inside a level, nothing otherwise, and no more successes. Larger λ and a second table
(43·47·53·59) lose (`bucket_soft.txt`).

## What the classes beyond the line could give if they were free

- `classes.txt`: the best members are barely enriched in good classes. Of the 37 primes 29..199, an average member
  has 0.45 in its best class and 12.1 in its best third; the 401 members with at most 9 rows left have 0.73 and 14.5;
  the 256 successes 0.48 and 12.9.
- `ceilings.txt`: all members ordered by their incidences with 29..199 alone, without any scoring: −3.46 / −1.68 /
  −2.58 / −2.12 nats against cover first. Cover first with ties broken by those incidences: +1.02 / +0.89 / +0.16 /
  0.00. The best mix found in hindsight (rows left at depth 23 minus 0.1 or 0.2 times the incidences): +1.4 to +1.8
  at one success, at most +1.5 at three, +0.1 to +0.4 at ten, nothing at thirty.
- `hybrid_ceiling2.txt`: the same mixed score used to choose which W members to score at depth 200 would capture 1.6
  times as many of the best members as the cover-first prefix at W = 10^4, 1.3 times at 10^5, 1.2 at 10^6, 1.1 at
  10^7, and about as many successes (2 / 7 / 24 / 106 against 2 / 4 / 28 / 91). But the score is the incidence count
  of every member with all 37 primes, which costs as much as scoring it at depth 200.

So even free, selection on the classes beyond the line is worth a fraction of a nat at equal work; the families can
only deliver the part of it that sits in product lists on a few primes, and that part is negative.

In `table.md` the last four columns give the gain when a family's members are examined in cover-first order without
any scoring, which is the comparison with cover first in the strict sense. With lists beyond the line only it is
negative in all 45 configurations, except for two of the bucketing ones at one success (+0.01 and +0.39). For the
best covers joined with lists (134 configurations) it is positive in 10 at one success (7 of them are one number, at
+0.90; the others +0.75, +0.85 and +1.63), in 3 at three successes (+0.40 to +0.88), in 2 at ten (+0.09 and +0.55)
and in none at thirty. That is the tie-breaking effect of `ceilings.txt` and no more, bought with 0.7 to 23 million
units of look-ups that would buy +5.6 / +5.6 / +3.2 if spent on scoring the cover-first prefix.

## Files

| file | what |
|---|---|
| `truth.c` | the miniature member by member → `data/N.u32`, `k1.u8`, `k2.u8`, `succ.u8` (1.1 GB, not kept here) |
| `pp.py`, `refcurve.py` | scoring of a candidate set against the truth; the references at equal work |
| `refs.py` → `refs.txt` | the published orders recomputed; cover-first prefix and random sample by work |
| `classes.py`, `ceilings.py`, `hybrid_ceiling.py`, `hybrid_ceiling2.py` → `.txt` | where the best members sit; what a free score would give |
| `unit.c` → `unit.txt` | the unit of work, timed |
| `families.c` | meet in the middle, N = N1 + k·M, four-list tree, bucketing, with operation counts |
| `make_prefix.py`, `run_all.py` → `results.jsonl`; `summarise.py` → `table.md` | all 179 configurations and their scores |
| `bucket_soft.py`, `bucket_soft_reps.py` → `.txt` | the table mixed with the cover |
| `agree.c` → `agree.txt` | the agreement that exists, by enumeration of every even N below 10^9 |
| `lattice_decode.py` → `lattice_planted.txt`, `lattice_real.txt` | the lattice decoder, planted checks and the miniature's instance |

To reproduce (numpy; python-flint for the lattice script; about half an hour on four cores, 3 GB of memory):

```
gcc -O3 -march=native -o truth truth.c && mkdir data && ./truth 1000000000 1000 23 200 data
python refs.py; python classes.py; python ceilings.py; python hybrid_ceiling.py; python hybrid_ceiling2.py
gcc -O3 -march=native -o unit unit.c && ./unit data/N.u32 20000000
gcc -O3 -march=native -o families families.c
python make_prefix.py 26 27 28 29 30 31 32 33 34 35
python run_all.py mitm; python run_all.py ktree; python run_all.py prefix; python run_all.py bucket; python summarise.py
python bucket_soft.py; python bucket_soft_reps.py
gcc -O3 -march=native -o agree agree.c -lm && ./agree
python lattice_decode.py planted; python lattice_decode.py real
```
