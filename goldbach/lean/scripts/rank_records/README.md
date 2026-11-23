# The largest least Goldbach summands, rank by rank

For an even N let g(N) be the least prime p with N − p prime. Scanning N upwards, keep the ten
largest values of g seen so far. An N *arrives at rank j* when g(N) is larger than exactly j − 1
of the kept values: rank 1 is a new record, rank 2 a new runner-up, and so on.

    gcc -O3 -march=native -fopenmp -o lgs_scan lgs_scan.c -lm
    ./lgs_scan 100000000000 cand_1e11.txt hist_1e11.txt        (4 min 13 s on 4 cores)
    python3 -I rank_records.py cand_1e11.txt 10 > ranks_1e11.txt
    python3 -I patterns.py ranks_1e11.txt > patterns_1e11.txt

`lgs_scan.c` computes g(N) for every even N in [6, X] with a segmented sieve and prints the N
above a threshold that stays below the tenth largest value (`rank_records.py` checks the margin).
`hist_1e11.txt` is the distribution of g over all 5·10^10 even numbers.

## What the arrivals have in common (up to 10^11; 249 arrivals above 10^5 at ranks 1 to 10)

The patterns are the same at every rank.

| pattern | measured | status |
|---|---|---|
| 3 divides N + g(N) | 249 of 249 | theorem: `IsSummand.three_dvd_add` (true for every N not divisible by 3) |
| N is divisible by 3 | 0 of 249 (chance: 83) | measured; a multiple of 3 has no row divisible by 3 |
| N is divisible by 5, by 7 | 1 and 2 of 249 (chance: 50 and 36) | measured |
| N is a quadratic non-residue mod 3, 5, 7 | 174 : 75, 165 : 83, 155 : 92 | measured; the direction is a theorem in the range: `card_rows_mod_three_le`, `card_rows_mod_five_le` |
| arrivals come in clusters closer than g | 15 pairs (independent positions: about 2.4) | mechanism is a theorem: `IsNeedle.add_of_forall` |
| pairs (N, g), (N + h, g + h) sharing the prime N − g | 4 pairs | theorem: `IsLeastSummand.add_of_forall`; instances `shift_pairs` |
| g(N) is at least the distance to the previous prime | always | theorem: `IsLeastSummand.sub_le` |
| record value over ln²N · ln ln N | 0.9 rising to 1.5 | measured; the conjectured limit is 1/C₂ = 1.51 |

The 39 record holders up to 10^11 (rank 1) agree with OEIS A025018 / A025019; their values are
kernel-checked in `GoldbachGaps/RankData.lean` (`recordTable_spec`). That no smaller number does
better is this scan, not a Lean theorem.

Why the non-residue classes: the prime r kills the rows q ≡ N (mod r), and below any level in
this range the non-residue classes contain more primes than the residue classes (Chebyshev's
bias). Why 3 never divides N: then no row at all is divisible by 3, against half of them
otherwise. Neither statement about the record holders themselves can be proved with present
methods: an upper bound for g(N) on any infinite set of N would already be a form of Goldbach's
conjecture.
