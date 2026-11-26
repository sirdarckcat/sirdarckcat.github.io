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
| first 88 odd primes + 613 | the first 3,000 in order of rows below 160,367 (four workers, every fourth each; 16,121,856 members a cover) | 20:05 UTC 25 Nov | stopped at 08:37 UTC 26 Nov at the lead's wind-down request (the user's decision to stop all work and submit PR #34): 2,589 covers done (indices 0–2,587 and 2,589), 4.174·10^10 members, 1.003·10^10 Fermat tests, 50.1 core-hours, no find. Not scanned: index 2,588 and 2,590–2,999. The four logs are in `logs/` |
| first 88 odd primes + 479 | the 2,727 of the first 3,000 in order of rows that the consultant session did not scan. It scanned 273 (indices 0–362 that are 0, 1 or 2 mod 4), and they match this session's specs by name, index and row count. This session takes indices 3 mod 4 below 364, and 364–2999 (rows 1,187–1,200, 20,643,840 members a cover) | was chained to start when the 613 scan ended | never started: the chain was stopped at the wind-down |
| first 88 odd primes + 613, second batch | covers 3,000–5,999 of the same order (the first 6,000 specs made again agree with the first 3,000 in N0, M and rows; rows 1,189–1,199 below 160,367, 16,121,856 members a cover) | was chained to start after the 479 scan | never started: the chain was stopped at the wind-down |

## Finds

None.
