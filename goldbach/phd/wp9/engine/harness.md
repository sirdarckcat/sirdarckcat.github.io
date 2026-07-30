# WP9 generative-tier harness (AlphaEvolve integration contract)

Purpose: let an external evolutionary search loop (AlphaEvolve or any
proposer) hunt for certificate schemas that falsify the Divisor-Paradigm
Closure Theorem, with a scorer that cannot be gamed into a false win.

## Scorer entry point

    python3 goldbach/phd/wp9/engine/scorer.py '<schema-json>'

stdin also accepted. One schema in, one JSON row out:

    {"family": ..., "params": ..., "killable": int,
     "residual_kills": int, "design_cost": nats,
     "nats_per_residual_kill": float|null,
     "verdict": "PASS"|"REJECT"|"BASELINE",
     "fitness": 0.0..1.0, "reason": str}

Grammar (families + param shapes) is documented in scorer.py's
docstring and wp9_closure_theorem.md §4. Out-of-grammar or erroring
proposals score fitness 0.0 — the search space is the grammar, and
extending the grammar is a HUMAN action (add an evaluator, re-run the
exhaustive tier for the new family first).

## What the evolve loop should optimize

fitness = min(1, killable/CEIL) × min(1, BENCH/nats_per_residual_kill),
CEIL = 3√Q ≈ 1048 distinct certified prime offsets below Q = 122,000,
BENCH = 1.01 nats per residual kill (the measured covering endgame).
fitness 1.0 ⟺ both filter conditions cleared ⟺ formal PASS.

Landscape hints for the proposer: the current frontier of REJECTed
families is ExpFamily at 3.1–4.2 nats/residual-kill (order conditions);
PolyImage tops out at ~113 killable offsets (ceiling-limited); products
of quadratic forms die at an enumeration wall measured at
height^0.50–0.74 work per offset. A winning schema must beat ALL of:
the value-set ceiling, the order-condition cost, and the
balanced-representation wall — wp9 §3 Lemma 1 explains why we believe
none exists; the evolve loop's job is to prove us wrong.

## Anti-reward-hack protocol (non-negotiable)

1. The scorer re-derives every number from primitives: deterministic
   sieve primality for the Q-range, the git-committed c1 residual set,
   symbolic factorization via sympy. Nothing the proposer asserts is
   trusted; proposals are data (JSON), never code.
2. Fitness is capped at 1.0 and monotone in verified counts only.
   There is no fitness reward for reasons/text, run time, or novelty.
3. Every row with fitness ≥ 0.25 is retained for human review; every
   PASS triggers a full hand audit before it is treated as real:
   (a) re-derive the certificate identity symbolically and verify the
   divisor witness on 100 random instances at 200-digit scale;
   (b) recompute design cost from first principles (family density in
   [1, B), not the scorer's formula); (c) check P5-consistency (the
   mechanism must be invisible in the 1.2×10⁹ banked candidates unless
   it activates only on constructed N); (d) only then does the theorem
   get amended and the user notified.
4. Known leak modes, already closed: congruence-containing schemas are
   BASELINE (fitness 0 — the paradigm cannot "escape" itself);
   composition claims of super-additivity require ≥5 joint events
   beyond 3σ of the additive prediction (wp9 §8 audit note); duplicate
   or trivially reparameterized schemas score identically by
   construction (no novelty bonus to farm).
5. Scaling caveat: ev_expfamily samples 25 offsets × 40 moduli for
   speed. Before ANY ExpFamily-family row is accepted as a near-record
   (fitness ≥ 0.25), rerun with the full offset range and s ≤ 10^5
   (flag `--deep`, to be added when the generative tier goes live).

## AlphaEvolve integration facts (from the Cloud API reference, 2026-07-29)

AlphaEvolve is served by the **Discovery Engine API v1alpha**, not a
standalone service. Relevant surface:

    POST /v1alpha/{parent}/alphaEvolveExperiments        create
    POST /v1alpha/{name}:start                          start
    POST /v1alpha/{parent}:acquirePrograms              pull candidates
    POST /v1alpha/{parent}:submitProgramsEvaluations    push scores
    GET  /v1alpha/{parent}/alphaEvolvePrograms          list

parent = projects/{p}/locations/{l}/collections/{c}/engines/{e}/sessions/{s}

Prerequisites (all on the account owner's side): active **Gemini
Enterprise** license (Standard/Plus/Frontline), **Discovery Engine API**
enabled, IAM role **Discovery Engine User**, and Application Default
Credentials — the docs specify
`gcloud auth application-default login --project=<PROJECT_ID>`.
There is a CLI (`ae experiment list`, `ae results best <exp> --top 5`).
Platform limits that constrain our candidate format: ≤50 files per
program, ≲4–5k LOC total, <200k tokens of context, concurrency 1–30,
30-minute client-side execution timeout.

**Auth note for future sessions.** A clickable "login link" that returns
a pasteable code is NOT obtainable: Google deprecated the out-of-band
redirect, and the gcloud public client's registered redirects are
`http://localhost:PORT/` loopbacks that a remote browser cannot reach
into this container (attempting `https://sdk.cloud.google.com/authcode.html`
yields `Error 400: redirect_uri_mismatch`). The credential must be minted
on a machine with a browser and injected as an environment variable —
either the whole ADC JSON (`type: authorized_user`, carrying the refresh
token) or a service-account key.

## THREAT-MODEL CHANGE: AlphaEvolve candidates are CODE, not JSON

The protocol above hands us *programs* to run, whereas §"Anti-reward-hack"
above assumed proposals are inert JSON. Executing evolved code that also
reports its own fitness would void every guarantee in this file (a
candidate could monkeypatch sympy, mutate the residual set, or simply
print a winning number). Required architecture, therefore:

1. A candidate program's ONLY contract is to write schema JSON to stdout
   (one schema per line, in the L grammar). It never computes kills,
   never imports the scorer, never reads the residual set.
2. We run candidates in a locked-down subprocess (no network, temp cwd,
   CPU/memory/wall limits, output size cap), harvest the emitted schemas,
   and grade them with `scorer.py` in a FRESH interpreter.
3. The fitness submitted back via `submitProgramsEvaluations` is the
   scorer's number for the best schema the program emitted — so the
   evolutionary pressure is on *inventing certificate schemas*, which is
   the actual research question, and never on manipulating measurement.
4. A program that emits nothing parseable scores 0. Grammar extensions
   remain a human action (see the grammar-extension rule above).

## Suggested evolve-loop shape

Population over the grammar's parameter space (ints, small tuples,
2-deep composition trees). Mutations: parameter nudges, family swaps,
composition grafts. This is a needle-in-haystack landscape by design —
the interesting output is (i) any fitness > 0.25 (near-miss for the
paper's table), (ii) the empirical fitness ceiling per family, which
becomes the exhaustion certificate's quantitative form.
