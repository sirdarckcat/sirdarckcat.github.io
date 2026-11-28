# CPU side scan at 200 digits: ledger

Idle session cores scanning for a member with g above the record held (160,357), with the lead's go-ahead of
25 November 19:52 UTC and its conditions: only covers the fleet does not use, a ledger of what was scanned, the
target at the record, and any find sent in full to the lead (and to the GPU session) for recomputation before it
is reported. Expected yield is small: about 7·10^-7 record-beating members per cover, 0.3 to 0.5% of the fleet per
four cores.

Pipeline: the uarch session's (`goldbach/sieve200/search_c.py` with the `fm13` Fermat kernel, its branch
`ccr-b8c25887-i6tn9f` at 8f5e2dd), specs by `goldbach/g200k/cover_specs.py <covers> 160367 <n> 200 4 <prefix>`:
target Q = 160,367 (the next prime after the record), every member of a cover below 10^200 (k from 0), sieve to
10^7, the emptiest 1.5% of each block of 32,768 tested in increasing q until the first probable prime. A find is a
member with N − q composite for every prime q below 160,367.

Sets of moduli the fleet has used, not to be scanned (GPU session, 19:58 UTC): the first 89 odd primes (3 to 463;
515,652 vectors on 23 November, ledgers under `goldbach/phd/campaign3_gpu/runlogs/2026-11-23/` on
`ccr-8ffe9d7a-4ni11u`); the first 88 with 491 (current production); the first 88 alone (`m88f`).

| set of moduli | covers | file | scanned by | status |
|---|---|---|---|---|
| first 88 odd primes + 557 | 8,543 (2 at 1,246 rows below 170,000, 83 at 1,247, 1,064 at 1,248, 7,211 at 1,249, 183 at 1,250) | `covers_first88_557.txt.xz` | research session, the first 3,000 in order of rows below 160,367 (four workers, every fourth each) | started 19:59 UTC 25 Nov; stopped at 04:15 UTC 26 Nov when the session's worker was restarted: 959 covers done (indices 0 to 959 of the order except 958), 17.0 billion members, 4.09 billion Fermat tests, no find; logs in `logs_557/` |
| first 88 odd primes + 523 | 8,572 (4 at 1,247, 154 at 1,248, 1,211 at 1,249, 6,922 at 1,250, 281 at 1,251) | `covers_first88_523.txt.xz` | uarch session, the first 600 in order of rows (four workers, 18.9 million members a cover) | started 20:01 UTC 25 Nov; its container was recycled at 22:05 UTC after 316 covers (no find); the other 284 resumed at 00:08 UTC 26 Nov as two harness tasks of 142 covers (c0316 to c0457, c0458 to c0599); all 600 done at 01:52 UTC, no find (2.73 billion tests); the next 600 (c0600 to c1199) done at 05:46 UTC, no find; stopped at the wind-down at 08:37 UTC after c0000 to c1615, contiguous (1,616 covers, 3.06·10^10 members, 7.34 billion Fermat tests, 41.5 core-hours, no find; c1616 onward not scanned); its ledger, worker logs and a copy of the covers file are in `goldbach/g200k/cpu_scan_523/` on `ccr-b8c25887-i6tn9f` (commit eb77d0b) |
| first 88 odd primes + 613 | 8,537 | `covers_first88_613.txt.xz` | Opus session, the first 3,000 in order of rows (four workers, 16.1 million members a cover) | started 20:05 UTC 25 Nov; 2,174 covers done at 06:27 UTC 26 Nov, no find (its last report before the wind-down) |
| first 88 odd primes + 503 | 8,582 | `covers_first88_503.txt.xz` | contractor session, the first 2,400 in order of rows (three workers, 19.7 million members a cover) | started 20:06 UTC 25 Nov; 648 of 2,400 covers done at 01:27 UTC 26 Nov (three workers, 93 s a cover), no find (its last report) |
| first 88 odd primes + 479 | 8,582 | `covers_first88_479.txt.xz` | consultant session, the first 3,000 in order of rows: three workers at the record target (every fourth cover, indices 0, 1, 2 mod 4), the fourth on a calibration target of 80,000 for about four hours before it joins them | started 20:06 UTC 25 Nov; stopped by the two-hour limit on its tasks with 273 covers done at the record target (no find), 114 at 80,000 and 1 at 120,000 (the calibration: 42 finds at 80,000, ln(found/expected) = -0.11 ± 0.15); its own ledger is `goldbach/gaps_map/data/bottomup/scan479/LEDGER.txt` on `ccr-cdb2641a-5zg8un`; the covers done are indices 0 to 362 of the order that are 0, 1 or 2 modulo 4 (checked by the Opus session against regenerated specs); the Opus session planned to take the other 2,727 from about 10:30 UTC 26 Nov, after its 613 scan, which the wind-down overtook |
| first 88 odd primes + 467 | 8,572 | `covers_first88_467.txt.xz` | Lean session, the first 3,000 in order of rows | started 20:20 UTC 25 Nov; stopped when its machine restarted at about 04:13 UTC 26 Nov: 796 covers (c0000 to c0795, contiguous), 16.8 billion members, 4.05 billion Fermat tests, no find; its ledger and logs are in `goldbach/lean/scripts/scan200/` on `ccr-36ca7b46-8twf14` (commit 031aee3) |

Both files: the first-88 family-B covers of `../../fscan/cover/starts/q170000_m88f.txt` extended by the two fullest
classes of the 89th prime, then a capped walk from them (`../../fscan/cover/covergen 170000 <starts> <cap> 8000 <seed>`,
cap 1,249 and seed 557; cap 1,250 and the 89th prime as seed for the others). The best covers of these sets have
1,246 rows below 170,000 with 557, 1,247 with 479, 503, 523 and 613, 1,248 with 467; the fleet's set has 1,245.

Rescans, recorded so that they are not counted as new work: lines 113 to 116 of
`../../fscan/cover/starts/q170000_m89.txt` (first 89 primes) were scanned whole here from 19:56 to 19:58 UTC before
the GPU session's answer arrived (4 covers, 85.5 million members, 20.5 million tests, no find); the uarch session
scanned 20 covers of lines 1 to 112 of the same file from 19:49 to 20:01 UTC (427 million members, no find). The fleet had tested the emptiest 1.5% of one window of
2^24 members of each such cover on the 23rd.

Check of the build used here (20:06 UTC): the best cover of the 557 set scanned whole at a target of 70,001 (557
rows, 60 s): 3 finds where about 1.8 were expected (24 members with no summand below the target, 7.4% of them in the
tested 1.5%), each recomputed from N alone with gmpy2 (every N − q for the odd primes q in turn): g = 70,249 to
81,727, equal to the pipeline's.

## Finds

None. On 26 November at 08:37 UTC the lead relayed the user's decision to stop all work in every session; the
counts above are the last each session reported. In all, about 6,000 covers of sets of moduli the fleet never
used were scanned at the record target (959 + 1,616 + 2,174 + 648 + 273 + 796 = 6,466), each in the emptiest 1.5%
of every block of its members, some 2.7·10^10 Fermat tests by the counts reported, and no member with a
least Goldbach summand above the record 160,357 was found, as the expected yield said (about 7·10^-7 such
members a cover, about 0.004 in all).
