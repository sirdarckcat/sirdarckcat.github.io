# The 200-digit side scan on idle CPU cores: the 523 family (uarch session's ledger)

The research session asked this session (25 Nov 2026, evening UTC) to scan, on its four otherwise idle cores, covers that the
GPU fleet does not use, at the record target. Research keeps the overall ledger of these side scans on its branches
(`goldbach/sublinear/cpu_scan/LEDGER.md` on `ccr-d4a17dd0-7uu03r`, `goldbach/bottom_up/cpu_scan/LEDGER.md` on
`ccr-c6e00296-3g7fp9`). This file is this session's part. It ended at the wind-down of 26 Nov, 08:37 UTC.

**What was scanned.** The covers are the 8,572 of `covers_first88_523.txt.xz`. Each fixes a class for each of the first 88
odd primes and for 523. The file is a copy of research's dump at `ccr-d4a17dd0-7uu03r` @ `eabec2d`
(`goldbach/sublinear/cpu_scan/`, same SHA-256). The covers are taken in their order of rows (the primes below the target that
no class removes). Each spec, from `../cover_specs.py <dump> 160367 3000 200 4 <prefix>`, holds every member N = N0 + kM below
10^200: 18,907,136 members a cover.

**The target** is 160,367, the prime after the record g = 160,357. A find would be an N below 10^200 with no prime p < 160,367
for which N - p is prime, so it would beat the record. Every such find would first have gone to research and the lead for
recomputation.

**The settings** (`../../sieve200/search_c.py`, one process per worker, four workers, each taking every fourth cover):

    SEARCH_C_FERMAT=fm13 SEARCH_C_CHUNK=128 python3 search_c.py <spec>_w<i>.json --procs 1 --sort-tests --skip-frac 0.985 \
        --p-est 0.0626 --sieve-b 10000000 --kmax 1 --out <prefix>_found_w<i>.jsonl

That means:
- a sieve to 10^7 over windows of 2^22 members;
- in each block of 32,768 members, the 1.5% with the fewest surviving rows tested;
- rows tested in increasing order with the 13-limb IFMA Fermat kernel `fm13`, stopping at a member's first probable prime.

## Result

| block | covers | when (UTC) | members | Fermat tests | core-hours | found |
|---|---|---|---|---|---|---|
| 1 | c0000-c0599 (c0316-c0599 rerun after a container recycle killed the first run at 22:05 on 25 Nov) | 25 Nov 20:01 - 26 Nov 01:52 | 1.134e10 | 2.727e9 | 15.1 | 0 |
| 2 | c0600-c1199 | 26 Nov 01:54 - 05:45 | 1.134e10 | 2.726e9 | 15.2 | 0 |
| 3 | c1200-c1615 (stopped at the wind-down; c1616-c1799 not scanned) | 26 Nov 05:47 - 08:37 | 7.865e9 | 1.890e9 | 11.2 | 0 |
| **all** | **1,616 covers, c0000-c1615, contiguous** | | **3.055e10** | **7.343e9** | **41.5** | **0** |

- The covers had 1,189 to 1,197 rows below 160,367.
- A cover took about 95 seconds on one core.
- No find file has a line.
- The expected number of finds is 0.0015, computed as research's tally does: the sum over covers of K·e^-E^·hit% from each
  summary line. A Gaussian correction for the spread of the survivor counts puts this formula about 1.5 times too high.
- So none was expected. One find at this target costs about 23,000 core-hours, against the 41.5 spent here.

Also in `logs/`: `famB_rescan_w*.log`, 20 covers of the fleet's own family B (c0000-c0019, 4.27e8 members, no find). They were
scanned before it was noticed that the fleet had already used that family, so they are rescans, not new coverage.

## Files

- `covers_first88_523.txt.xz`: the cover dump (input).
- `logs/`: every worker's summary lines, one per cover (`c523*`: block 1; `b2c*`: block 2; `b3c*`: block 3).
- `tally.py`: recomputes the table from the logs.

**To resume** at cover 1,616, regenerate the specs with the command above, but with 3,000 replaced by the number of covers
wanted. Drop every spec whose index is below 1,616, then run the four workers as above.
