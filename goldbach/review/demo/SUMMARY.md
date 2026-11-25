# Demonstration points: even N with g(N) >= 10% of the size's ceiling (closeness.py), 4-core shared CPU container

Not project records: demonstration points for a review.  g(N) = least prime p with N - p prime.  Every N below was re-checked from N alone by `scripts/verify_g.py` (see `results/<digits>/check.txt`); N - g is a probable prime (12 strong bases + gmpy2 strong BPSW), every N - q for prime q < g fails a base-2 Fermat test (proof of compositeness).

| digits | Q (10% of ceiling(10^digits)) | g(N) | ceiling(N) | closeness | g/(ln N)^2 | ideal digits | moduli (largest) | rows | model before scan: p, R*p, raw members/hit | members sieved to first hit | Fermat tests | wall s | CPU s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 46,535 | 47,881 | 464,470 | 10.31% | 0.9046 | 36.5 | 49 (229) | 407 | 0.04256, 17.32, 4.88e+07 | 432,013,312 | 120,737,029 | 713 | 1,106 |

N (100 digits, g = 47,881, k = 431,044,114):

    8223574663857043817842483455238569126110624927813137471170822278151226773853347935411335888798540538

## 110-digit scan parts (cover seeds s11 on 1 process; s12, s13 on 3 processes)

| log | members sieved | Fermat tests | CPU s | model E[found hits] (sum of (1-p_B)^survivors over tested members, p_B = 0.0973) | model E[raw hits] |
|---|---|---|---|---|---|
| scan110_s11.log | 547,356,672 | 168,776,196 | 1,600 | 0.2691 | 1.267 |
| scan110_s12_part1.log | 41,943,040 | 12,914,586 | 123 | 0.02063 | 0.0971 |
| scan110_s12b.log | 1,077,903,360 | 332,624,740 | 3,164 | 0.53 | 2.495 |
| total | 1,667,203,072 | 514,315,522 | 4,887 | 0.8197 | 3.859 |

## What ran

* Tools (git archive of origin/ccr-b8c25887-i6tn9f, unmodified): `ptcover/ptcover_fast` (covers), `g200k/make_spec.py`, `sieve200/search_c.py` + `search.py` (`search_spec`: C sieve, selection by survivors, Fermat loop in C with the `fermat661/fm13` AVX-512 IFMA kernel, which serves every size up to 672 bits; `fmw` is only for larger numbers), `g200k/costcalc.py`; `closeness.py` from origin/ccr-2ce9e63a-hn0fuw.  `scripts/scan.py` is my driver: it calls `search.search_spec` slice by slice, stops at the first hit, sums the log lines and the hit-mass numbers `run_block` returns.
* Settings for all scans: B = 10^6, blocks of 32,768, windows of 16 blocks, `--sort-tests --skip-frac 0.97` (the emptiest 3% of each block tested).
* Moduli = the first m odd primes; m = the largest for which the members below 10^digits hold several expected raw hits.

## Model against measurement, 100 digits (one hit: one sample of an exponential waiting time)

| quantity | model | measured |
|---|---|---|
| rows alive per member after the sieve to 10^6 | R ln(229)/ln(10^6) = 160.1 | 162.1 |
| P(survivor is a base-2 PRP) | e^gamma ln B / ln N = 0.1069 at 10^100 (0.1090 at 10^98) | 0.1075 over the scan (0.1105 in the first slice, k < 2.1e6) |
| hit mass kept by the 3% cut | 22.3% (costcalc's normal approximation) | 21.3% (sum of (1-p)^survivors over the blocks) |
| raw members per hit | (1-p)^-407 = 4.9e7 at 10^100 (p = 2 prod r/(r-1) / ln N = 0.04256); costcalc: 10^7.61 = 4.1e7 (it uses Mertens' estimate for the product, 17% low here) | - |
| members sieved per found hit at the 3% cut | 2.3e8 (4.9e7 / 0.213) | 4.32e8 to the first hit |
| expected found hits when the first hit came (k = 431,044,114), p(N) integrated along the progression | 1.72 | 1 (P(waiting at least this long) = 18%) |
| CPU per member | 0.46 us sieve + 0.28 tests x 7.25 us = 2.5 us (measured separately, one process) | 2.56 us (1,106 s / 4.32e8) |
| CPU-seconds per found hit | 590 (2.3e8 x 2.56 us); costcalc at this cut 454, at its best cut (1.2%) 408 | 1,106 to the first hit |

The first hit took 1.9 times the model's mean number of members (1.7 times when the smaller N at the start of the progression is
taken into account: members with small k are up to 8 digits shorter, their rows are prime more often, hits are rarer there; the
scan started at k = 0).  With one hit this neither confirms nor contradicts the model beyond a factor of a few.  The quantities that
do not depend on luck (survivors, PRP rate, hit mass kept, cost per member) agree with it within 1-5%.
Wall-clock: 713 s with 3 worker processes on a machine shared with other jobs (load average 4-10 on 4 cores); the slices of 64 blocks
gave the 3 workers only 4 tasks at a time, so they were 2/3 busy (1,106 CPU-s / 713 s = 1.55 cores).  Fixed for the 110-digit runs.

## 120 and 130 digits: not attempted (cost by the model, cover and rates measured here)

| digits | Q | cover (ptcover_fast) | rows | p, R*p | raw members per hit | members below 10^digits | CPU-hours per found hit |
|---|---|---|---|---|---|---|---|
| 120 | 69,531 | 57 moduli to 271 (40,000 sweeps; 3,000 sweeps gave 594) | 590 | 0.03661, 21.60 | 3.6e9 | 3.1e9 (0.87 raw hits: several covers needed, or 56 moduli: 600 rows, 4.8e9 raw members per hit, range 8.5e11) | about 14-16 at the 3% cut (1.7e10 members x 3.0-3.5 us); costcalc at its best cut: 9.5 |
| 130 | 82,935 | 61 moduli to 293 (3,000 sweeps) | 699 | 0.03428, 23.96 | 3.9e10 | 4.9e9 (0.13 raw hits; 60 moduli: 708 rows, 4.9e10, range 1.4e12) | about 170 at the 3% cut; costcalc at its best cut: 101 |

A 1,048,576-member slice of each was sieved and tested to measure survivors and speed (242.6 / 291.5 rows alive per member, 0.33 / 0.35
tests per member, 3.0 / 3.4 us CPU per member).  With at most 4 CPU-hours in the hour (less on the shared machine) a 120-digit hit had
a chance of a few percent, so the time after the 100-digit hit went to an intermediate size, 110 digits, instead.

## Problems with the tools

* `ptcover_fast` with its OpenMP threads on the loaded machine: 4,000 sweeps of 49 moduli took 63 s wall on 4 threads; with OMP_NUM_THREADS=1, 3,000 sweeps took 5 s.  Longer tempering gained little at these sizes (594 -> 590 rows from 3,000 to 40,000 sweeps at 120 digits; four seeds at 110 digits: 494, 494, 494, 495).
* `g200k/costcalc.py` has Q = 200,000 and the fmw test times for 300-400 digits built in; used through `scripts/costcalc_wrap.py` (Q, test time and sieve cost passed in).  Its raw-members figure uses Mertens' estimate for prod r/(r-1), which is 17-25% optimistic at these small moduli.
* `search.py` / `search_c.py`: the summary line prints only the ratio hit% = hm_kept / hm_all, not the expected number of hits; `--p-est` must be the PRP rate after the sieve (e^gamma ln B / ln N), not p; a slice whose number of 16-block windows is not a multiple of the process count leaves workers idle; `search.py` and `make_spec.py` need sympy and gmpy2 (pip installed both).
* The model's p depends on ln N, and the members at the start of a progression are much smaller than 10^digits: hits are rarer there than (1-p)^-R at the size limit says.  The 110-digit scans start at k = 6e8 (N > 10^109.59) for that reason.
* fm13 / sieve200 built and ran on this CPU (avx512ifma present); no fallback was needed.

