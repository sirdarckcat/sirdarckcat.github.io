# Idle cores scanning at 200 digits: this session's family

Asked by the research session on 25 November 2026 (20:04 UTC), under the lead's ruling of 19:52 UTC: session cores
that are idle scan members of covers the fleet does not use, at 200 digits, for a member whose least Goldbach summand
exceeds the record held (160,357). The ledger of all sessions is the research session's
(`goldbach/sublinear/cpu_scan/LEDGER.md` on `ccr-d4a17dd0-7uu03r`); this file records what runs here.

**Family**: the first 88 odd primes with 467 (`covers_first88_467.txt.xz` on `ccr-d4a17dd0-7uu03r` at `eb66883`,
8,572 covers). **Taken**: the first 3,000 in order of rows; rows below 160,367 from 1,189 to 1,199; 21,168,128 members
of each below 10^200; four workers with 750 covers each (every fourth).

**Pipeline**: the uarch session's, `ccr-b8c25887-i6tn9f` at `8f5e2dd` (`goldbach/sieve200/search_c.py`, the `fm13`
Fermat kernel, `goldbach/g200k/cover_specs.py`), with the research session's command line:

    python cover_specs.py covers467.txt 160367 3000 200 4 f467
    SEARCH_C_FERMAT=fm13 SEARCH_C_CHUNK=128 nice -n 10 python search_c.py f467_w$w.json --procs 1 --sort-tests \
        --skip-frac 0.985 --p-est 0.0626 --sieve-b 10000000 --kmax 1 --out f467_found_w$w.jsonl

Target 160,367 (the next prime after the record): a find is a member N with N − q composite for every prime q below
160,367. Every member of a cover is sieved to 10^7; the emptiest 1.5% of each block of 32,768 are tested, rows in
increasing order, until the first probable prime.

**Checked here before starting** (the code that runs was read first): the kernel's own tests on this CPU (0 wrong
residues, 0 wrong verdicts); `sanity.py`: the C sieve against trial division on 6 members of the first cover, and the C
member loop against gmpy2 on its 96 emptiest members of one window (2,163 tests, no difference; 15.2 microseconds a test).

| when (UTC) | covers done | members | tests | finds |
|---|---|---|---|---|
| 25 Nov 20:20:40 | started | | | |
| 25 Nov 20:22:52 | 4 (c0000 to c0003) | 84.7 million | 20,368,738 | 0 |

125 s a cover a core on this machine (4 cores): about 115 covers an hour. Chance that a cover holds a record-beating
member: about 7·10^−7 (the research session's figure), so the 3,000 covers together have about one chance in 500.
A find goes to the research session in full, which recomputes it from N alone before anyone else is told.
