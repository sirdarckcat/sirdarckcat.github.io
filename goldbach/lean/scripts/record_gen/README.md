# A generator for A025018, and what forcing it term by term shows

A025018: the even numbers N ≥ 4 whose least Goldbach summand g(N) (the least prime q with
N − q prime) exceeds that of every smaller even number: 4, 6, 12, 30, 98, 220, 308, 556, 992, …
A025019: those summands: 2, 3, 5, 7, 19, 23, 31, 47, 73, …

## The generator

    strikers: the primes q = 2, 3, 5, 7, 11, … in order; q strikes the numbers q + p, p prime
    front:    the smallest even number ≥ 4 that no striker has struck yet (it starts at 4)

    for each striker q:
        if q hits the front (front − q is prime):
            the front is a term, q is its value
            the front moves to the next even number that no striker up to q has struck
        else: nothing; the front waits

`GoldbachGaps/RecordGen.lean` is this program in Lean (`records X`: the terms below X), on
bitmasks, with the proof that it is correct for every X:

| | |
|---|---|
| `mem_records` | `(N, g) ∈ records X ↔ N < X ∧ IsRecord N g` (the output is exactly the sequence below X) |
| `records_sorted` | the terms come out in increasing order, numbers and values |
| `isRecord_iff_front` | a term is a front that its striker hits |
| `IsFront.unique` | the front depends on the striker alone: the state of the generator is one prime |
| `testBit_primeMask` | the prime sieve inside it is exact: digit j is 1 iff j is a prime below X |
| `RecordGenRun.records_two_pow_20` | the kernel runs the generator to 2^20: the first 21 terms, by the generator alone |

Run it: `lake env lean scripts/record_gen/Run.lean` (21 terms below 2^20 in under a second, 24
below 2^22 in about a second, 27 below 2^25 in 22 s, 30 below 2^27 in 3 min 12 s; all equal to
the first terms of the OEIS b-files). Nothing is searched number by number: the
cost is one shift and one OR of an X-digit number per striker, plus the prime sieve.

## The N generator: walk the even numbers and say when a record falls

The generator above loops over the strikers and asks where the front is. The same sequence with
`N` as the loop variable:

    G = 0                                        the largest least summand so far
    for N = 4, 6, 8, 10, …:
        if no prime q ≤ G has N − q prime:       N beats every number before it
            announce N;  G = the least prime q with N − q prime

`GoldbachGaps/RecordWalk.lean` is this program (`walk X`: the numbers announced below `X`) with
its proof:

| | |
|---|---|
| `mem_walk` | `N ∈ walk X ↔ N < X ∧ ∃ g, IsRecord N g`: for every X it announces exactly the terms of A025018 below X |
| `walk_sorted` | in increasing order |
| `walk_eq_map_records` | `walk X` is the list of numbers of `records X`: the walker and the sieve are one generator |
| `walk_two_pow_20` | below 2^20 it announces 21 numbers: 4, 6, 12, 30, 98, …, 503222 |
| `not_isSummand_iff_neighbours` | the question looks only at the primes within G below N: N is announced iff none of them is at a prime distance from N |
| `beats_iff_wheels` | or at N alone: N beats G iff its residues modulo the primes r ≤ √N cover the strikers (every prime q ≤ G has such an r with N ≡ q mod r) |

Run it in Lean: `lake env lean scripts/record_gen/Walk.lean` (the 15 terms below 100,000).

`ngen.c` is the same walker made fast. It prints each term the moment it reaches it:

    gcc -O3 -march=native -fopenmp -o ngen ngen.c -lm
    ./ngen 100000000000          the terms up to 10^11, one "N g(N)" per line
    ./ngen                       no limit: it keeps walking until it is stopped
    ./ngen 0 <from> <G>          take the walk up again from a "# state" line it printed

What it carries along: `G`; the odd primes up to `G` (the strikers, a few hundred numbers); the
primes among the last 2^17 numbers below `N`, as bits; and the primes up to √N, used only to mark
the primes of the next stretch. Its question to `N`, "is one of N − 3, N − 5, N − 7, N − 11, …
prime?", is put to 64 consecutive even numbers at once, one AND per striker, and most blocks are
settled after a hundred strikers. On 3 cores of this machine:

| up to | time | terms announced |
|---|---|---|
| 10^9 | 0.7 s | 34 |
| 10^10 | 6 s | 36 |
| 10^11 | 65 s | 40 |
| 5·10^12 | 83 min | 46 |

all equal to the OEIS b-file. That is about 4 ns of one core per even number at 10^9, and it
grows slowly (more primes to mark, more strikers): every further factor of 10 costs a little more
than 10 times as much.

What it cannot do is skip. A number is passed over only because a prime q ≤ G with N − q prime
was found for it, so the walker meets a Goldbach partition of every even number on its way, and
its position is bounded by how many numbers one can afford to visit (4·10^18 is the furthest
anyone has gone). Where the next term is *likely* to be, without visiting anything, is a
different question with a usable answer: `scripts/lgs_heuristic/forecast.py`.

## How far does it go?

Nothing about the generator is tied to 2^25. That number is where the *certified table* of
`scripts/rank_sieve` stops, and it was chosen for build time. There are four different limits:

| what | how far | why |
|---|---|---|
| the proof that the program is right | every X | `mem_records` is a statement about all X |
| the front (the next candidate) | exists for every striker, forever | `exists_isFront`, no hypothesis |
| new terms, forever | exactly if Goldbach's conjecture is true | `goldbach_iff_generator_never_stops`, `goldbach_iff_records_unbounded` (`GoldbachGaps/RecordInfinite.lean`) |
| running the proved generator | 2^25 in 20 s, 2^27 in 3 min; 2^30 (about 10^9) was stopped unfinished after 2 hours | every sieving prime costs a pass over an X-digit number, so the time grows at least like X^1.6 |
| statements checked by the kernel | 2^25 in 90 s; about 2 hours for 10^9; about 1.6 days for 10^10 | measured on single segments: 2.5 s per million numbers near 3·10^7, 8.5 s near 10^9, 21 s near 10^10, with 1 to 6 GB of memory |
| the walker in C (`ngen.c`: the proved rule, the program itself not proved) | 10^11 in 65 s on 3 cores: 40 terms; 5·10^12 in 83 min: 46 terms | it visits every even number; memory is the primes up to √N |
| fast scan of all least summands, not proved (`scripts/rank_records/lgs_scan.c`) | 10^12 in 63 min: 43 terms | |
| anyone's computation | 4·10^18: 69 terms (Oliveira e Silva, Herzog and Pardi, Math. Comp. 2014; OEIS b-file) | |

So "to infinity" has a precise meaning. The program is correct to infinity and never runs out of
fronts. Whether it keeps *producing terms* is Goldbach's conjecture, no more and no less: if some
even number is not a sum of two primes, the front arrives at the smallest such number and no
striker ever hits it (`isFront_of_counterexample`); if there is none, the terms go on forever.
A term beyond 4·10^18 cannot be proved to exist today, and patterns such as "no term after 30 is
divisible by 3" cannot be proved for all N for the same reason: any bound on the least summand
of every N is at least Goldbach's conjecture.

## Forcing it: first 2 terms, then 3, then 4, …

`ladder.py` tries the simplest rule that produces the first terms and lets the next term break
it. Each break is one idea of the generator (`python3 -I ladder.py 12`):

| rule | right for | broken by | what the break teaches |
|---|---|---|---|
| 1. next even number; value = next prime | 2 terms | 8 = 3 + 5 | a term must dodge the earlier value: N − 3 composite gives 12 |
| 2. N − (last value) composite | 3 terms | 14 = 3 + 11 | it must dodge every earlier value, not only the last: 30 |
| 3. N − v composite for every earlier value v; value = next prime | 4 terms | 98 − 11, 98 − 13, 98 − 17 are composite | the value is not the next prime: 11, 13, 17 miss 98 and its value is 19 |
| 4. as 3, value = first prime that hits | 5 terms | 124 = 11 + 113 | the primes that missed must keep striking: 11 hits 124, the true term is 220 |
| 5. N − q composite for every prime q up to the last value; value = first prime that hits | all | — | this is the sieve above; proved in Lean |

The breaks are theorems too (`GoldbachGaps/RecordGenRun.lean`): `not_isRecord_8`,
`not_isRecord_14`, `isRecord_98` (the value of 98 is 19 and not 11) and `not_isRecord_124`.

So the sequence hides two things that the first four terms do not show. Until 30 the terms are
2·3, 4·3, 2·3·5: each new term just adds the next prime as a factor (N − q is a multiple of q).
At 98 that stops: 98 − 3 = 5·19, 98 − 5 = 3·31, 98 − 7 = 7·13, 98 − 11 = 3·29, 98 − 13 = 5·17,
98 − 17 = 3⁴: one small prime now kills several summands at once (3 kills 5, 11, 17; 5 kills 3
and 13), which is the covering mechanism of the large searches. And from 98 on strikers miss, so
A025019 skips primes; the number of misses before a hit grows like ln N.

One rule with no primality in it does survive five terms: "take the residue classes of the first
n odd primes that strike the longest run of primes, and announce the least even number carrying
them" gives 6, 12, 30, 98 for n = 0, 1, 2, 3 and then says 1118 where the sixth term is 220
(`scripts/lgs_heuristic/hgen.py`, rule A; `GoldbachGaps/CoverDepth.lean`, `isRecord_and_isDepth`).
The first five terms are the best possible coverings; from the sixth on a term is only the best
covering that happens to occur in time.

What forcing does not give: a way to jump to the next front without the sieve. The next front
is the smallest N with N − q composite for all primes q up to the last value, and no rule that
avoids looking at every N in between has survived (for instance "skip the multiples of 3" is
right for every term after 30 among the 69 terms of the OEIS b-file, up to 3.3·10^18, and is a
theorem below 2^25, `RankSieve.notAmongTen_of_dvd_6`, but it is not proved in general, so a
generator using it would not be a proved generator).
