# Door 1, D1.0 diagnostics + D1.1 gate status (turn 1)

Instance: `instance_q122k.json` (Q=122,000, 88 moduli, prime universe
sha256-pinned, baseline |U| = 867 = the c1/greedy plateau; 1 prime =
0.0240 nats of E).

## D1.0 landscape diagnostics (d10_diagnostics.py)

- **Stability at the greedy point**: per-modulus best-alternative gaps
  min=0, median=3, max=507; **19 of 88 moduli are tight (gap ≤ 1)** —
  near-degenerate class choices concentrated in the endgame moduli;
  small moduli are locked (gap up to 507). LNS windows target the
  tight set first.
- **Random-start coordinate ascent (8 runs)**: |U| ∈ [954, 981] — all
  ~90–110 primes WORSE than greedy's 867. Greedy's sequential
  adaptivity is worth ~2.2–2.6 nats over naive local search; the
  plateau is not an artifact of ascent being weak from any start —
  it is specifically the greedy basin that is good.
- **Backbone**: pairwise class-agreement between independent ascent
  solutions is 2.4% (chance level), agreement with c1 5%. **The
  landscape is fully degenerate: many mutually-distant solutions of
  similar quality, no shared backbone.** Consequences: crossover/merge
  methods have nothing to graft; clustering-based reasoning
  (survey-propagation decimation) may still apply but population
  methods will not concentrate; exact windows and tempering carry the
  attack.

## D1.1 exact-LNS gate (d11_lns.py) — status after turn 1: OPEN

22 CP-SAT windows solved (sizes 10–12, caps 25–45 s, warm-started,
incumbent-floored): **no window improved on 867; every window matched
it exactly** once the incumbent floor was added. However all solves
finished [feas], not [OPT] — CP-SAT could not close the optimality
proof within the caps, so "no improvement exists at window scale
10–12" is not yet certified. Next turn: (a) per-window LP bounds
(instant): ⌊LP⌋ = incumbent certifies window-optimality without
CP-SAT closing; (b) provable small windows (6–8); (c) longer caps on
the tight-set window only. Gate verdict criteria unchanged: any −1
prime = first improvement over the plateau; 3 turns of certified
no-gain = plateau evidence feeding the P3 certificate track.
