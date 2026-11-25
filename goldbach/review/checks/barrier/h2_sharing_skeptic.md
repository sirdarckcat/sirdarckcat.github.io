# h2_sharing_skeptic: check of the h2_sharing audit

Verdict: the conclusion (no loophole in the sieve+test layer) stands. Three of its numbers do not.
Scripts: run/h2_sharing_skeptic/mymodel.py (exact binomial alive counts, no Monte Carlo), k_sweep.py, auditor_model.py (the auditor's model, rerun unchanged).

## Errors found in the audit
1. "Free sieve x7.7 = 2.04 nats" and "free test x11.7 = 2.46 nats" use the wrong reference. model.py sets `ref` inside each scenario, so each "free" row is divided by the free scenario's own value at (1e8, 1.5%), not by the real deployed point.
   - Against the real deployed point (1.913e-19): free test = 5.884e-18 -> x30.8 = 3.43 nats (my model: x30.9). Free sieve at (1e12, 0.2%) = 2.379e-18 -> x12.4 = 2.52 nats.
   - Neither is a cap. Both optima sit on a grid corner. Free sieve: keep 0.05% gives x24 = 3.19 nats and it grows without limit as keep -> 0. Free test: the 1.85 ns floor is the grid's lowest B (1e6); with shallower sieves a test 1,000x cheaper gives 3.64 nats, 10^4x 5.9, 6x10^4x 7.7.
   - Correct statement: a test K times cheaper, re-optimised, is worth 0.39 nats (K=2), 0.76 (4), 1.22 (10), 2.37 (100). 7.7 nats needs K ~ 60,000 with no sieve: ~0.6 ps a row = ~10 word multiplies for a 24-limb number.
   - Budget form: deployed = 57 ns per full-weight member (12.3 ns a member, 21.6% of hit mass kept). 10% needs 0.026 ns, less than half of ONE modular squaring step (0.056 ns).
2. "Deep head: not built, not run, +3.5%". HEADROOM.md sections 0 and 3d: built, GPU-gated, production A/B at f = 0.985 on ~1,010 batches a card: +0.7% WORSE, taken off 12:24Z 23 Nov. Re-priced optimum B2 = 3e8: ~+1.2% of a batch. So 0.012 nat at best, not 0.02-0.04.
3. "The brief's 0.03 ns a mark disagrees with the team". It is the team's own figure: the large-prime stage measured 23 Nov 01:30Z (ledger E_sievedepth; campaign3_gpu README line 243: 0.030 ns a mark, 11.5 ns a member at 2^25). Stale (9 ps by 05:30Z) and only for marks above the window. The "53 ns" contradiction comes from applying it to all 1,768 marks; on the ~457 large-prime marks it gives 13.7 ns.
4. FFT product-modulus penalty "4-8x": not derived. Team figures: 8x (HEADROOM) and 30x with NTT (ideas_research #28); my count ~20x. Sign is unanimous.

## Numbers that reproduce
- Operating point: optimum B = 1e8, keep 1-1.25%, x1.010 (mine: x1.010 at keep 1%). Table rows within 3%: 1e6 x0.75, 1e7 x0.92, 3e7 x0.99, 3e8 x0.94, 1e9 x0.75, 1e10 x0.28.
- My model reproduces the team's old-engine f sweep to 0.5% (0.936/0.967/1/1.032/1.061/1.077/1.058 vs team .937/.968/1/1.031/1.059/1.074/1.053).
- p_B = 0.0713, 14.02 tests a kept member; 14^log2(3) = 65.5; filter break-even x < r(1-p): (0.5, 0.5) -> x0.966, so the closure theorem's "halves the cost" sentence is wrong (verbatim at lines 123-124). The team's h2_open_problem.md has the right formula, 1/(c + 1 - r).
- 876 multiplies a step, 43 ns a test (now 40.6), 3-9 ps a mark, lattice crossover 4.5e9: all in HEADROOM.md. Troisi 30-70%: arXiv 2012.03771 abstract.

## Not examined by the audit
- The team's own on-lens file: fscan/cover/brainstorm/ideas_research.txt section D (ideas 26-35) and verdicts_on_research_ideas.txt. It already has: #28 product modulus (identity Lean-proved, "no variant wins at 665 bits"), #26 shared row values (Lean dichotomy, loses e^7 or more), #27 shifted covers (3-5 nats lost), #31 estimator of prime rows (capped 1.7 nats), #33 deep sieve (pairs = pi(B) x rows per vector whatever the layout), #34 stop-at-first-PRP optimal (Lean), #35 faulty arithmetic (loses no hits; "10%, not 2").
- #29 Fermat along a progression and #30 group test: team verdict "no method known". Open, unpriced.
- 88-moduli long-vector mode. Pair visits are a property of 2e7-member vectors, not of sieving. With 88 moduli (7.8e9 members) and windows of 2^28-2^30, large primes cost marks only: my model x1.15 at B = 1e9, x1.29 at 1e10; the team's count says "worth 1.5" at 1e11. Against that the 89th modulus is worth x1.23 (1,609 vs 1,623 rows). Net -0.1 to +0.2 nats, sign unknown; needs a new bin layout.
