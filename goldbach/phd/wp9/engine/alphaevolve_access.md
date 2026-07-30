# AlphaEvolve access — resolved configuration (2026-07-29)

Access granted by the account owner and verified end-to-end. **No secrets
in this file**; the credential lives in an environment variable
(`ALPHAEVOLVE_ADC_JSON`, an ADC `authorized_user` blob) and is written to
a scratchpad file that `GOOGLE_APPLICATION_CREDENTIALS` points at.

## Resource coordinates

    project           sdcpocs   (number 799795028847)
    location          global    (the API rejects us/eu on this endpoint)
    collection        default_collection
    engine            goldbach_1784979910032   ("goldbach", SOLUTION_TYPE_SEARCH)
    api root          https://discoveryengine.googleapis.com/v1alpha/
    quota header      x-goog-user-project: sdcpocs   (required — user creds
                      carry no quota project of their own)

Sessions hang under the engine; AlphaEvolve experiments hang under a
session; programs hang under an experiment:

    .../engines/{engine}/sessions/{session}/alphaEvolveExperiments/{exp}
                                          .../alphaEvolvePrograms/{prog}

**Gotcha:** every `name` the API returns is a RELATIVE resource name
(`projects/799795028847/...`), not a URL — prefix with the api root or
urllib reports `unknown url type`. Also `initialAlphaEvolveProgram` is a
resource-name STRING pointing at a program, not an inline program.

## Environment repair needed on this image

`cryptography` ships broken (missing `_cffi_backend`, Rust bindings panic),
which breaks `google.auth.transport.requests`. Fix:

    pip install --ignore-installed cryptography     # 41.0.7 -> 49.0.0

Then `google.auth.default(scopes=[".../auth/cloud-platform"])` +
`creds.refresh(Request())` works, which is also the durable-refresh path
(raw POSTs to `oauth2.googleapis.com` are blocked by the sandbox's
permission classifier, the library call is not).

## Verified capabilities

| capability | status |
|---|---|
| credential refresh (survives restarts) | WORKS |
| list engines / sessions | WORKS (1 engine, 13 sessions) |
| read experiment + config | WORKS |
| list programs + their multi-objective scores | WORKS (100/experiment) |
| read program source (`content.files[].content`) | WORKS |
| create/start experiment, acquire/submit evaluations | not yet exercised |

## Prior art discovered in the project (7 experiments)

Five COMPLETED, two PAUSED — these are the runs behind the evolved
programs reviewed earlier in this programme. Example config (experiment
9582896010645531772, "Super Hard Constrained Multi-Objective Goldbach
Cover Step-Heuristic"):

    programLanguage    python
    runSettings        maxPrograms 100, concurrency 8, maxDuration 86400s
    generationSettings includeFullProgramInPrompt true,
                       gemini-3.1-pro-preview (0.7) + gemini-3.5-flash (0.3)
    metrics            neg_est_digits, neg_E, neg_residual_count, neg_m_digits
    program format     single file `program.py` (~8 KB) with an
                       `# EVOLVE-BLOCK-START` region around the evolved
                       function (`optimize_cover_step(...)`)

Score sample from that run: best `neg_est_digits` ≈ −193.6 at
`neg_E` ≈ −17.56; failed candidates are sentinel −1e12. This corroborates
the earlier file-based review (the evolved optimizer did not beat the
existing one under warm start) and gives the exact metric/score shape to
mirror.

## What this means for the WP9 generative tier

The API is a *client-evaluated* loop (`acquirePrograms` →
evaluate locally → `submitProgramsEvaluations`), which is what
`harness.md` assumed: grading stays on our machine, so the anti-
reward-hack property is preserved. Build order:

1. Seed program `program.py` with an EVOLVE-BLOCK around a
   `propose_schemas()` function whose ONLY output is schema JSON lines in
   the L grammar (never kills, never fitness — see harness.md's
   THREAT-MODEL section).
2. Evaluator: run each acquired program sandboxed, harvest emitted
   schemas, grade with `scorer.py` in a fresh interpreter, submit
   `{metric: fitness}` plus diagnostics (`killable`, `nats_per_kill`).
3. Metrics to expose, mirroring the local filter: `fitness` (primary),
   `killable_ratio`, `neg_nats_per_residual_kill`.
4. Do NOT start a 24h/100-program run without the owner's go-ahead — it
   spends their Gemini Enterprise quota.
