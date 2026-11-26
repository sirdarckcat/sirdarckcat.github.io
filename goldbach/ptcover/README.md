# ptcover_fast: the cover optimizer of `fscan/cover/ptcover.c`, 1.4-2.1x faster, identical output

`ptcover.c` (the research session's parallel tempering over residue covers, branch ccr-d4a17dd0-7uu03r, `goldbach/fscan/cover/`) spends its
time in the evaluation of a move: the rows the move loses (rows of the old class that this modulus alone covers) and gains (rows of the new class
that nothing covers), two walks over the class lists, 444 ns a move on average.  `ptcover_fast.c` has the same command line and
makes the same moves with the same random numbers, so for a given seed it prints the same tables and BEST and writes the same `PT_DUMP`
file (`./test_identical.sh <dir with the moduli and beta files>` checks five runs and a dump of 6,090 covers, byte for byte, against `ptcover_ref.c`,
a verbatim copy of the original).

| build (one thread, 56 replicas, Q = 140,000, 88 moduli) | ns a move | speed-up |
|---|---|---|
| `ptcover_ref.c` | 419-453 | 1 |
| `ptcover_fast.c`, AVX2 only (`-march=haswell`) | 296 | 1.4 |
| `ptcover_fast.c`, AVX-512 | 209-224 | 2.0-2.1 |

On 4 threads 8.6 -> 15.1 million moves a second (the hot replicas, which accept 90% of their moves and are dominated by the update of the
counts, are not faster).  Cold replicas (beta >= 2): 380 -> 130 ns a move.

What is different (all in the evaluation, nothing in the Markov chain):

* The class lists of the large moduli are scanned sixteen rows at a time with a gather.
* In the cold replicas (beta >= `BCUT` = 0.6) the classes of the moduli up to 61 are bit sets over the rows (214 words), and the replica keeps two more bit sets:
  the rows with no cover and the rows with exactly one.  The rows lost are `popcount(class_old & one)`, the rows gained `popcount(class_new & none)`: 214 words
  instead of up to 4,300 rows (the moduli 3 to 61 are 73% of all the walking).  The hot replicas run without the bit sets (accepted
  moves would pay for keeping them more than they save); a state that arrives in a cold slot from a hot one by a replica exchange rebuilds its bit sets
  before its first move.
* exp(-beta d) from a table for d < 130.

    gcc -O3 -march=native -fopenmp -o ptcover_fast ptcover_fast.c -lm      # any x86-64; AVX-512 is used if present

Left on the table: the two random-number reductions (`% nmod`, `% (r - 2)`) are 64-bit divisions, about 15 ns a move; a multiply-shift reduction
would change the random stream, so the output would no longer be comparable byte for byte.
