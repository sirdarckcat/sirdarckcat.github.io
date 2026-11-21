# g > 3,000,000 rung: parked, no prime yet

Target g = 3,000,061, lazy full cover, n = 24,291, base 11, N would have
21,936 digits. Sieve to 1e9 left 8,246 of 16,384 values of t.

Stopped 2026-11-21 20:57 UTC after 2,120 tests (t up to 4,196, about 27 s
each on one core), none prime. About 1,369 tests were expected per prime, so
the chance of getting this far with no hit is about 21%. It was parked because
the 5,000,251 record had already passed it and the session it ran in limits
background jobs to two hours.

Resume (skips everything in tests.jsonl):

    python3 desert.py search runs/q3000000/spec.json runs/q3000000 --procs 4 --sieve 1e9 --T 16384
