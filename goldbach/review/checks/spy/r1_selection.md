# r1_selection: "Deepen the selection score, not the test" - working notes (25 Nov 2026)

Verdict: already_done (the deep score is production since 23 Nov 01:30Z); going deeper was measured and rejected; the two-stage form was assessed twice and not built.

## What production actually runs (primary sources)

- Deployed args, runlogs/2026-11-24/<card>/deep_env*, next_campaign_env (fleet branch ccr-8ffe9d7a-4ni11u):
  - G4 (gold-g4d/e -> g4g/h): `--deep 1 --klog 24 --slice 16777216 --sieve-b 100000000 --p-est 0.0715 ... --pipeline 1 --pipeline-depth 4`, `SKIPF=0.985`.
  - L4 / T4: `--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000`, `SKIPF=0.97` (T4 BATCH=1).
- Selection rule, search_gpu5.py lines 9-13: per block of 2^15 members the emptiest ceil(L(1-f)) by survivor count (492 of 32,768 at f = 0.985), ties by ascending k. The count is taken AFTER the whole sieve to B (gbatch.py line 3: "Everything after the sieve (count, select, finalize, rows) is GpuFeeder's").
- So the score = alive rows after sieving every row by all primes <= 10^8, on every card.

## The spy's model, reconstructed exactly

G(keep) = Phi(Phi^-1(keep) + a*sd) / (c + (1-c) keep).
- base a*sd = 0.955, c = 0.0053: G(1.5%)/G(3%) = 1.0996 (the "+10%").
- deep a*sd = 1.35 (= 0.955 * sqrt 2): optimum gain x1.972 (c = 0.0053, keep 0.73%), x1.501 (c = 0.01, keep 1.26%), x1.099 (0.02), x0.792 (0.04). These are the spy's four numbers. (spycheck/spy.py)

## Why the premise fails

a*sd read from the cards' own logs (kept hit mass = Phi(z + a*sd)):
- B = 10^6 normal path, f = 0.97: hit% 18.0-18.1 (v491/v491gate_rtxpro6000.txt:9, vtop/vtop_rtxpro6000.txt:70) -> a*sd = 0.97.
- production deep path, L4, f = 0.97: hit% 25.2 (l4op/gate_deploy_l4.txt; TALLY c170g 287.7e9/1141.8e9) -> 1.213.
- production deep path, G4, f = 0.985: 2111.6e9/12572.1e9 = 16.8% (TALLY c170r) -> 1.208.
- fit to the measured f sweep's hits/batch (v89/vsweep_rtxpro6000.txt, 9 points): 1.28.
The spy's "base" 0.955 is the 10^6 score. Its "deep" 1.35 is ~B = 10^9 (CPU counts: sd 16.06 / 15.39 / 14.95 and p 0.0536 / 0.0715 / 0.0804 at 1e6 / 1e8 / 1e9 give 0.885 / 1.14 / 1.25 on the Q = 150k vector; x1.06 on the 1,248-row vectors).
Production is at 1.21-1.28. The x1.97 is the 10^6 -> 10^8 step: sieve_bound/cpu_t2700_k3221225472_2e22.txt has hit mass per test x1.903 (f = 0.97), x1.968 (f = 0.98), x2.082 (f = 0.99) at 10^8.

Unchecked premise 1 (did the sieve-depth test run without selection): no. deep_sieve_bound.py applies the production rule at f = 0.95...0.995 with the selection bound varied; GPU repeat bench_sieveb.sh at f = 0.97.
Unchecked premise 2 (did the "extra sieve stage" re-select): no. The deep head (primes (1e8, 1e9] on the first 64 rows) runs after count / select; kept members identical for 12,091,392 members (head/headv_rtxpro6000.txt), tests -8.42%, batch +0.7% (0.9514 vs 0.9449 s, head/ab_production_f0985.txt), taken off 12:24Z.

## Measured: B

| step | source | result |
|---|---|---|
| 10^6 -> 10^8 (plain deep kernel) | uarch_measure/deeptime | 2.00 s, 3.23e-5 -> 2.10 s, 4.46e-5: x1.32 hits/s |
| 10^8 -> 2^28 -> 10^9 (staged) | uarch_measure/bsweep_staged_rtxpro6000.txt | 2.623e-5 -> 2.543e-5 (-3%) -> 1.817e-5 (-31%) hits/s |
| joint (B, f) on the 23 Nov 17:40Z engine | HEADROOM.md:46 (selstat/bsweep.py + bmodel.py) | best B = 1e8, f = 0.99 x1.012; 1.6e8 x0.996; 2.7e8 x0.951 |

Cost structure: a deeper score is paid per (prime, row) visit per vector, not per member. (1e8, 1e9] is 45,086,079 primes x 1,248 rows = 5.63e10 visits a 2^24 window, 8x today's 7.1e9; at the head kernel's 4.7e-9 ms a visit that is 264 ms a window against a 51 ms window. My break-even for a 10^9 score: +56 ms a window (spycheck/opt.py). A free 10^9 score would be x1.32-1.36.

## Measured: f

- G4: v89/vsweep (x1.102 design hits/s at 0.985 vs 0.97), vsweep2 (0.9875 x1.023, 0.99 x0.991, repeat x1.012), vsweep3 (0.9875 x1.010, repeat x0.985). Last sweep 23 Nov 13:46Z; the sieve window has gone 67.7 -> 44.4 ms since.
- L4: l4f/ab_l4_f985.txt x0.9865 at 0.985 (S = 3.27 s, F = 6.06 s). Then l4op cut the batch 9.520 -> 8.094 s (all sieve), so S ~ 1.84 s. No re-test after 18:55Z.

## Two-stage, already judged

- research, verdicts_on_lean_ideas.txt:30 (Lean idea 22, the same idea): "NO SAVING BY ITSELF: a deep pass over the kept members still has to visit every hit of every pair".
- uarch, HEADROOM.md:70: pruning after the small-prime stage saves only the apply part, ~+3% (":150 pruned apply +1.5%"). Not built.

## Residual (fleet nats)

| item | status | gain |
|---|---|---|
| G4 f 0.985 -> ~0.99 on today's engine | not re-swept since 13:46Z 23 Nov | model x1.01-1.05 on 87% of the fleet, before supply (a cap step of +1 row costs 2.4%): 0 to 0.04 |
| L4/T4 f 0.97 -> 0.985 after l4op | never tested | model x1.086 on 12.9%: 0.011 |
| head at B2 = 3e8 | estimated, not built | ~0.01 |
| pruned apply (two-stage as layout) | estimated, not built | 0.013-0.026 |
| deeper B | measured, negative | 0 |
| overlap | deployed on G4 (x1.14), nothing on L4/T4 | 0 |

Total 0 to ~0.08 nats, against the claimed 0.68. For scale: 0.21 nats per +1,000 in g; 213,070 is ln 5,600 = 8.6 nats away (research brainstorm README).

Scripts: fit.py, opt.py, spy.py, resid.py in this directory.
