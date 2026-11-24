# The largest least Goldbach summands, rank by rank

For an even N let g(N) be the least prime p with N − p prime. Scanning N upwards, keep the ten
largest values of g seen so far. An N *arrives at rank j* when g(N) is larger than exactly j − 1
of the kept values: rank 1 is a new record, rank 2 a new runner-up, and so on.

    gcc -O3 -march=native -fopenmp -o lgs_scan lgs_scan.c -lm
    ./lgs_scan 1000000000000 cand_1e12.txt hist_1e12.txt       (63 min on 3 cores; 10^11: 4 min on 4)
    python3 -I rank_records.py cand_1e12.txt 10 > ranks_1e12.txt
    python3 -I patterns.py ranks_1e12.txt > patterns_1e12.txt
    python3 -I spacing.py cand_1e12.txt hist_1e12.txt 1e12 > spacing_1e12.txt

`lgs_scan.c` computes g(N) for every even N in [6, X] with a segmented sieve and prints the N
above a threshold that stays below the tenth largest value (`rank_records.py` checks the margin).
`hist_1e12.txt` is the distribution of g over all 5·10^11 even numbers up to 10^12
(`hist_1e11.txt`: the same up to 10^11).

## What the arrivals have in common (up to 10^12; 287 arrivals above 10^5 at ranks 1 to 10)

The patterns are the same at every rank.

| pattern | measured | status |
|---|---|---|
| 3 divides N + g(N) | 287 of 287 | theorem: `IsSummand.three_dvd_add` (true for every N not divisible by 3) |
| N is divisible by 3 | 0 of 287 (chance: 96) | theorem below 2^25: `RankSieve.notAmongTen_of_dvd_6` (no multiple of 3 above 1362 enters the ten largest); measured beyond |
| N is divisible by 5, by 7, by 11, by 13 | 1, 2, 9 and 8 of 287 (chance: 57, 41, 26 and 22) | measured |
| N is a quadratic non-residue mod 3, 5, 7 | 202 : 85, 193 : 93, 176 : 109 | measured; the direction is a theorem in the range: `card_rows_mod_three_le`, `card_rows_mod_five_le` |
| arrivals come in clusters closer than g | 15 pairs (independent positions: about 2.4) | mechanism is a theorem: `IsNeedle.add_of_forall` |
| pairs (N, g), (N + h, g + h) sharing the prime N − g | 4 pairs | theorem: `IsLeastSummand.add_of_forall`; instances `shift_pairs` |
| g(N) is at least the distance to the previous prime | always | theorem: `IsLeastSummand.sub_le` |
| record value over ln²N · ln ln N | 0.9 rising to 1.4 – 1.5 | measured; the conjectured limit is 1/C₂ = 1.51 |

## How the ranks are spaced (`spacing.py`, `spacing_1e12.txt`)

Count the even N ≤ X whose least summand is at least the m-th odd prime: each further prime
removes a nearly fixed fraction, `T(m + 1) / T(m) = exp(-r / (ln X - 1))`. Up to 10^12 the rate
`r` falls from 1.99 at the start (the mean of the Goldbach singular series is 2) to about 1.5 to
1.6 from the 100th prime on (the same values as up to 10^11); its limit should be 2 C₂ = 1.32,
the value for N without small odd prime factors, which are the N that last. A geometric tail
makes the largest values sit like the top of an exponential sample: the j-th and (j + 1)-th
largest are about `(ln X - 1) / (r j)` primes apart. Measured at the powers of ten from 10^5 to
10^12, the average of `j · (π(g_j) - π(g_{j+1})) / (ln X - 1)` over j = 1..9 is 0.681, against
`1 / r = 0.667` for `r = 1.5`. So the second, third, … largest values carry no pattern of their own: they are the
next draws from the same tail as the record. Like the tail itself this is the Hardy–Littlewood
heuristic, not a theorem.

The 42 record holders up to 10^12 (rank 1; the last three are 105963812462, 244885595672 and
599533546358 with g = 3061, 3163 and 3457) agree with OEIS A025018 / A025019 (terms 2 to 43 of
the b-files, which come from T. Oliveira e Silva's computations and continue to 3.3·10^18); their values are
kernel-checked in `GoldbachGaps/RankData.lean` (`recordTable_spec`). That no smaller number does
better is a theorem for the 26 record holders below 2^25 (`RankSieve.isRecordHolder_iff`, see
`scripts/rank_sieve`), and this scan for the 16 beyond.

Below 2^25 = 33,554,432 the scan is replaced by proofs (`scripts/rank_sieve/README.md`): every
even N there is a sum of two primes with the smaller at most 997; a multiple of 3 never needs a
prime above 379, of 5 above 619, of 7 above 661; and after 1362 no multiple of 3 is ever among
the ten largest.

Why the non-residue classes: the prime r kills the rows q ≡ N (mod r), and below any level in
this range the non-residue classes contain more primes than the residue classes (Chebyshev's
bias). Why 3 never divides N: then no row at all is divisible by 3, against half of them
otherwise. Neither statement about the record holders themselves can be proved with present
methods: an upper bound for g(N) on any infinite set of N would already be a form of Goldbach's
conjecture.
