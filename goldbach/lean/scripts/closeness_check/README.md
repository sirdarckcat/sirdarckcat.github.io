# The closeness game: check before the certificates

`check_frontier.py` rechecks the research session's numbers from `N` alone (even, number of digits, the least prime
`p` with `N - p` a probable prime, no base-2 Fermat pseudoprime among the rows no small modulus strikes) and its Pratt
trees node by node (`goldbach/sublinear/frontier_pratt.json` on branch `ccr-d4a17dd0-7uu03r` at `94b5ea8`, read as
data), and writes for each number the two files that `../gen_record.py --lucas` reads: `record.json` (N, g, the
classes of N modulo the odd primes up to 43) and `lucas.json` (a primitive root and the prime factors of `n - 1` for
every prime `n` of the tree from 1024 on). `check_frontier.txt` is its output; `records/` holds what it wrote.

    python -I check_frontier.py frontier_pratt.json records
    python ../gen_record.py --lucas records/frontier_27digit_g11467 Record27_g11467 ../../GoldbachGaps/Record27_g11467.lean

Nothing here is trusted by Lean: the kernel re-evaluates the negative side (`GoldbachGaps/Desert.lean`) and checks
the proof that Mathlib's `primality` tactic builds from the witnesses. The statements are in
`GoldbachGaps/Closeness.lean`.
