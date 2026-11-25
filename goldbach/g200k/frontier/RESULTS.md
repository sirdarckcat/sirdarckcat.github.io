# Closeness frontier, 10% line (frontier.py)

A rung d: every even N with 10^(d-1) < N <= c 10^(d-1) whose N - q are composite for all primes q < Q = ceil(0.10 ceiling(c 10^(d-1)))
(goldbach/closeness.py) has g(N) >= Q, so closeness >= 10% at its own size.  Covers: ptcover PT_DUMP sets of the first n odd
primes (fewest rows at Q first); per cover the members N0 + k M of the window, sieve200 to 10^7 in 2^22-member windows, the
emptiest 1 - skip of each 32,768-block, fmw / fm13 until the first probable prime.  Hits are verified from N alone (frontier.py's
verify, then frontier_recheck.py: sympy BPSW for every N - p with p < g, BPSW + 50-round Miller-Rabin for N - g).
Expected = sum over the tested members of (1 - p^)^a (a = its alive rows after the sieve, p^ = prp / tests of the run, range for
p^ -+ 1 s.e.).  Nominal E = rows x -ln(1 - p0), p0 = e^gamma ln(p_n) / ln N; E_tested = mean tested a x -ln(1 - p^).

| digits | c | Q | moduli | covers | rows | nominal E | E_tested | members | tested | p^ | skip | expected | found | found/expected | CPU-h | best closeness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | 1.1 | 46,578 | 49 | 37 | 407 | 17.5 | 15.50 | 1.94G | 38,825,506 | 0.12463 | 0.98 | 7.99 (7.97-8.02) | 7 | 0.88 | 1.35 | 0.1115 (g = 51,907) |

The 101-digit rung ran on the code before dce3cf2 (fm13 at 333 bits, 2^20 windows); the same rung costs ~0.55 CPU-h now.

Hits: hits101.txt (digits, g, closeness, N).
