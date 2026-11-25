# g200k: an even N with g(N) >= 200,000 and as few digits as possible

g(N) = the least prime p with N - p prime.  A cover gives each modulus r (the first odd primes) a nonzero class a_r; N = a_r
(mod r) for all of them and N = 0 (mod 2) makes N - q composite for every prime q < Q = 200,000 in a covered class.  The rows
left (q in no class) must be composite by luck: members N = N0 + k M (M = 2 prod r) are sieved by the primes above the largest
modulus, the emptiest (fewest surviving rows) are Fermat-tested until a prime N - q kills them, and a member whose survivors
are all composite is a hit (checked: every N - q, q < Q prime, BPSW-composite; g = the first prime q >= Q with N - q prime).

| file | what |
|---|---|
| `make_spec.py cover Q name out.json` | spec (N0, M, rows, cover) for `../sieve200/search_c.py` from a cover (a BEST/COVER line or a JSON list) |
| `slices.py spec name n blocks ceiling out.json` | the spec cut into k slices (one summary line each) |
| `run_scan.sh slices.json` | the scan: search_c.py with fmw (`../fermatw`), B = 10^7, selection by survivors (`SKIP`, `PROCS`, `OUT` env) |
| `make_record.py found.jsonl spec.json outdir` | a hit's record: N.txt, record.json, ../verify_record.py evidence, ../fscan/check.py from N alone, MANIFEST |
| `cover_ils.c` | iterated local search for covers (best-class moves against the uncovered rows, random kicks); does not beat the tempering covers (below) |
| `cover400_k1010.txt`, `cover350_k1113.txt` | tempering covers (`../ptcover/ptcover_fast`, 200,000 and 100,000 sweeps): 159 moduli to 941 / 1,010 rows; 142 moduli to 823 / 1,113 rows |

## Results

| digits | g(N) | N | cover | B, tested | members sieved | tests | hits | CPU-hours |
|---|---|---|---|---|---|---|---|---|
| 400 | 200,293 | `../records/g200k_400digit_g200293/N.txt` (k = 70,023,538) | 159 moduli to 941, 1,010 rows | 10^7, emptiest 2.5% | 72.35M (two hits) | 57.96M | 2 | 1.8 (3 cores, 36 min) |
| 400 | 206,593 | `../records/g200k_400digit_g206593/N.txt` (k = 70,144,479) | same | same | same scan | | | |

Each record has `verify_record.py`'s evidence (a reason N - q is composite for every prime q < g: the cover congruence, a trial
divisor, or a strong base-2 witness; g prime; N - g BPSW) and `fscan/check.py` run on N alone (g recomputed by testing every N - q).
The 400-digit scan had no hit in its first 69.2M members, where the survivor counts predict 1 found hit per 10.7M; the checks made
during the drought (sieve against brute force with rows above 2^16, fmw against gmpy2 on the scanned range, the same cover at
Q = 30,000 / 100,000 / 130,000 with 329 / 6 / 10 hits found against 355 / 6.0 / 9.0 predicted, the first-prime positions of 52,480
tested members against the geometric law up to position 333, and the rows that kill members) all agreed with the model.
