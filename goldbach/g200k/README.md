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
| `costcalc.py cover ...` | expected cost of a hit for a cover: digits of the first found hit, raw members per hit, the best cut, CPU-hours (model: survivors binomial, p_B = e^gamma ln B / ln N, test times of fmw by limb count) |
| `../ptcover/ptcover_hb.c` | ptcover_fast with heat-bath moves for the moduli above 61 in the cold replicas (new class drawn from all r - 1 with weight e^(-beta dk), one pass over the uncovered rows) |

Digits of a hit = log10 M + log10 k, and with the cut the first found hit comes near k = 1 / (E[(1-p)^a] h), about 10^(m + 1.2)
(h = the hit mass kept), so a cover must be chosen for the digits of its hit, not of M: 134 moduli (M 318.1 digits) give hits near
327 digits, which also needs fmw L = 22 (1,086 bits) instead of L = 21 (up to 1,080 bits, 325 digits), a much slower kernel here.

## Results

| digits | g(N) | N | cover | B, tested | members sieved | tests | hits | CPU-hours |
|---|---|---|---|---|---|---|---|---|
| 400 | 200,293 | `../records/g200k_400digit_g200293/N.txt` (k = 70,023,538) | 159 moduli to 941, 1,010 rows | 10^7, emptiest 2.5% | 72.35M (two hits) | 57.96M | 2 | 1.8 (3 cores, 36 min) |
| 400 | 206,593 | `../records/g200k_400digit_g206593/N.txt` (k = 70,144,479) | same | same | same scan | | | |
| 347 | 216,289 | `../records/g200k_347digit_g216289/N.txt` (k = 302,750,559) | 141 moduli to 821, 1,115 rows (`cover348_141_k1115.txt`) | 10^7, emptiest 0.5%, K = 2^21 | 318.8M | 44.3M | 1 | 1.04 (4 cores, 16 min) |
| (350) | none | | 142 moduli to 823, 1,113 rows (`cover350_k1113.txt`) | 10^7, emptiest 2%, K = 2^19 | 487.6M (its whole 350-digit range) | 273.7M | 0 | 7.5 |
| 319 | 207,307 | `../records/g200k_319digit_g207307/N.txt` (k = 1,430,868,604) | 131 moduli to 743, 1,183 rows (`cover319_131_k1183.txt`) | 10^7, emptiest 0.8%, K = 2^21 | 1.443G | 295.5M | 1 | 6.4 (4 cores, 96 min) |

The 350-digit phase: the 142-moduli cover's range below 10^350 ends at k = 4.82e8 (M has 341.3 digits) and held no hit
(1.75 expected from its survivor counts, P(0) = 17%); the 141-moduli cover (M 338.4 digits, every member below 10^350 up to
k = 4e11) with the larger window and the tighter cut found one after 3.03e8 members (8.1e8 expected per found hit).

Each record has `verify_record.py`'s evidence (a reason N - q is composite for every prime q < g: the cover congruence, a trial
divisor, or a strong base-2 witness; g prime; N - g BPSW) and `fscan/check.py` run on N alone (g recomputed by testing every N - q).
The 400-digit scan had no hit in its first 69.2M members, where the survivor counts predict 1 found hit per 10.7M; the checks made
during the drought (sieve against brute force with rows above 2^16, fmw against gmpy2 on the scanned range, the same cover at
Q = 30,000 / 100,000 / 130,000 with 329 / 6 / 10 hits found against 355 / 6.0 / 9.0 predicted, the first-prime positions of 52,480
tested members against the geometric law up to position 333, and the rows that kill members) all agreed with the model.

## The closeness frontier, 10% line (frontier.py)

Rungs of the frontier asked for by the lead (most digits at which an N with closeness >= 10% at its own size is held), each
also a point of the hit-rate calibration: `frontier.py` (one rung: many PT_DUMP covers of one set of moduli, the window
10^(d-1) < N <= c 10^(d-1), target Q = 0.10 ceiling(c 10^(d-1))), `frontier_combine.py` (a rung split over runs with
`--cover-offset`), `frontier_recheck.py` (every hit from N alone), `frontier_row.py` (the table row and hits file).
Results: `frontier/RESULTS.md`.

Speed (101 digits, 407 rows, one 2^22-member window, all four cores busy): the old pipeline (fm13's 13 limbs on 333-bit
numbers, 2^20 windows, numpy selection, s200_extract) cost about 500 CPU-s an expected hit; now about 207 (2.4x):

- fmw with the limbs the numbers need (7 at 333 bits, 8 at 353-404): 2.30 us a test against fm13's 6.90; two groups
  of 8 lanes up to 8 limbs (1.22x at 7, 1.11x at 8; `fermatw/README.md`).
- sieve windows of 2^22 members: 0.52 us a member against 0.87 at 2^20 (the per-prime work of the primes above the
  window is per window; 2^23 rows no longer fit the 2 MB L2).  c chosen so that a cover is a whole number of windows
  (120 digits: c = 1.1991218, 15 windows) saves the last, mostly empty window (6% at 120 digits).
- s200_select and s200_csr (C) for the selection and the survivor lists: s200_extract's 430 strided reads a member cost
  4.6 us a selected member.
- skip 0.97 (the emptiest 3% of each block) instead of 0.98: cost per expected hit 207 against 245 CPU-s (flat from 0.96 to
  0.975).  B = 10^7 stays: 10^8 raises the kept hit mass by 20% at a cost of 3x in the sieve.

Where the time goes at 120 digits (578 rows, 396 bits): about 40% the sieve (2.5 s a window: marks of the primes 400..16384
29%, 16384..2^20 33%, 2^20..2^22 18%, beyond 9%, patterns and counts 10%) and 58% the Fermat tests (9.5 a tested member, the
first probable prime ends a member).  Both are within about 1.3x of what this approach can do on this core: the L1 mark loop
takes 2.1 cycles a mark (an L1 byte tile 1.4, but 8x the per-tile work), and the 8-limb step runs at 74% of the two
512-bit ports that every IFMA, add and shift shares (2 IFMA a cycle measured, 4.1 GHz).

Cost per expected hit (CPU-s, skip 0.97, one full window of the rung's best cover, four busy cores; the range is the window's
own p^ against p scaled from 101 digits): 105 digits 513-563, 110 1,930-2,370, 115 7,440-7,990, 120 18,100-21,600 (before
the two-group fmw; about 5% less with it), so about x3.8 per 5 digits; 125 is about 15-20 CPU-h an expected hit.
