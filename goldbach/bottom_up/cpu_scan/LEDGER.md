# CPU side scan at 200 digits: this session's ledger

This session's part of the idle-core scan in research's ledger (`goldbach/sublinear/cpu_scan/LEDGER.md` on its branch
`ccr-d4a17dd0-7uu03r`). The conditions are the lead's (25 Nov, 19:52 UTC):
- only covers the fleet does not use;
- a ledger of what was scanned;
- the target at the record;
- any find sent in full to the lead and to the GPU session for recomputation before it is reported.

**The pipeline.** It is the uarch session's: `goldbach/sieve200/search_c.py` with the `fm13` Fermat kernel, specs by
`goldbach/g200k/cover_specs.py <covers> 160367 3000 200 4 <prefix>`. The settings:
- target 160,367, the prime after the record of 160,357;
- every member of a cover below 10^200;
- sieve to 10^7;
- the emptiest 1.5% of each block of 32,768 tested in increasing q until the first probable prime.

`tally.py` sums a scan's logs.

| set of moduli | covers | started | status |
|---|---|---|---|
| first 88 odd primes + 613 | the first 3,000 in order of rows below 160,367 (four workers, every fourth each; 16,121,856 members a cover) | 20:05 UTC 25 Nov | 2,175 covers done at 06:30 UTC 26 Nov: 3.51·10^10 members, 8.43·10^9 Fermat tests, 41.4 core-hours, no find; 2,463 at 07:58 UTC, no find. It ends about 10:45 UTC |
| first 88 odd primes + 479 | the 2,727 of the first 3,000 in order of rows that the consultant session did not scan. It scanned 273 (indices 0–362 that are 0, 1 or 2 mod 4), and they match this session's specs by name, index and row count. This session takes indices 3 mod 4 below 364, and 364–2999 (rows 1,187–1,200, 20,643,840 members a cover) | chained to start when the 613 scan ends (about 10:45 UTC 26 Nov) | queued; about 17 hours |
| first 88 odd primes + 613, second batch | covers 3,000–5,999 of the same order (the first 6,000 specs made again agree with the first 3,000 in N0, M and rows; rows 1,189–1,199 below 160,367, 16,121,856 members a cover) | chained to start when the 479 workers have all ended (about 04:00 UTC 27 Nov) | queued; about 15 hours. The target is to be raised first if the record has moved |

## Finds

None.
