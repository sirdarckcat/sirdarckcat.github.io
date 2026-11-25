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
| first 88 odd primes + 557 | 8,543 (2 at 1,246 rows below 170,000, 83 at 1,247, 1,064 at 1,248, 7,211 at 1,249, 183 at 1,250) | `covers_first88_557.txt.xz` | research session, the first 3,000 in order of rows below 160,367 (four workers, every fourth each) | started 19:59 UTC 25 Nov |
| first 88 odd primes + 523 | 8,572 (4 at 1,247, 154 at 1,248, 1,211 at 1,249, 6,922 at 1,250, 281 at 1,251) | `covers_first88_523.txt.xz` | offered to the uarch session | |
| first 88 odd primes + 613 | 8,537 | `covers_first88_613.txt.xz` | offered to the Opus session | |
| first 88 odd primes + 503 | 8,582 | `covers_first88_503.txt.xz` | offered to the contractor session | |
| first 88 odd primes + 479 | 8,582 | `covers_first88_479.txt.xz` | offered to the consultant session | |
| first 88 odd primes + 467 | 8,572 | `covers_first88_467.txt.xz` | offered to the Lean session | |

Both files: the first-88 family-B covers of `../../fscan/cover/starts/q170000_m88f.txt` extended by the two fullest
classes of the 89th prime, then a capped walk from them (`../../fscan/cover/covergen 170000 <starts> <cap> 8000 <seed>`,
cap 1,249 and seed 557; cap 1,250 and the 89th prime as seed for the others). The best covers of these sets have
1,246 rows below 170,000 with 557, 1,247 with 479, 503, 523 and 613, 1,248 with 467; the fleet's set has 1,245.

Rescans, recorded so that they are not counted as new work: lines 113 to 116 of
`../../fscan/cover/starts/q170000_m89.txt` (first 89 primes) were scanned whole here from 19:56 to 19:58 UTC before
the GPU session's answer arrived (4 covers, 85.5 million members, 20.5 million tests, no find); the uarch session
started on lines 1 to 112 of the same file at 19:49 UTC. The fleet had tested the emptiest 1.5% of one window of
2^24 members of each such cover on the 23rd.

Check of the build used here (20:06 UTC): the best cover of the 557 set scanned whole at a target of 70,001 (557
rows, 60 s): 3 finds where about 1.8 were expected (24 members with no summand below the target, 7.4% of them in the
tested 1.5%), each recomputed from N alone with gmpy2 (every N − q for the odd primes q in turn): g = 70,249 to
81,727, equal to the pipeline's.

## Finds

None.
