# What is left to do

All work stopped on 26 November 2026 at the owner's request, with the record for an even N below 10^200 at
g(N) = 160,357. This list collects what the nine sessions left unfinished, sorted by kind, with where each item stands,
where to pick it up, and roughly what it would cost. `COVER_LETTER.md` explains the background; the words used here
(cover, row, window, sieve, near-miss, closeness) are explained in its glossary.

Each session also wrote a handover note with its own list:
`phd/campaign3_gpu/HANDOVER.md` (GPU search), `sublinear/HANDOVER.md` (research), `lean/HANDOVER.md` (Lean proofs),
`sieve200/HANDOVER.md` (performance), `bottom_up/HANDOVER.md` (second analysis), `gaps_map/HANDOVER.md` (consultant) and
`review/OUTSIDE_REVIEW_2026-11-25.md` (outside review). All paths here are relative to `goldbach/`.

## 1. Searches that can simply be continued

These need computing time and nothing else. The tools are written, tested and documented.

### 1.1 The 200-digit search (the main goal)

- **Where it stands.** Stopped on 26 November at 08:39:40 UTC, after 67.5 trillion candidates on a design for
  g ≥ 170,000. It found the near-miss records 158,209 and 160,357 and no success at 170,000, where the model expected
  0.69. One third of the covers (partition 2) had been waiting since 24 November for a third RTX PRO 6000 card, which
  Colab never granted. 6,395 Colab compute units were left, and nothing is running.
- **How to restart.** `phd/campaign3_gpu/HANDOVER.md` and `phd/campaign3_gpu/README.md`. The programs regenerate the
  covers and skip the candidates that `runlogs/` lists as done. The cards' snapshot archives lived only in the GPU
  session's temporary storage and will not survive it, so the restart has to start from the repository.
- **What to expect.** On 25 November, with about 6,700 units left, the model gave a restart on the same design an 85%
  chance of beating 170,000, 46% of reaching 175,000, 17% of 180,000, 1.4% of 190,000 and about 1 in 750 of reaching
  200,000. The expected final record was about 175,000. An even chance of reaching 170,000 needs about four days on two
  RTX PRO 6000 cards (about 2,100 units).
- **Built but never deployed** (`sieve200/HANDOVER.md`): selecting candidates by their rows below the record only
  (1.065 times the record-beating events, but 0.937 times the successes at 170,000; declined at the time); faster
  end-of-window kernels (about 0.6%); a second sieve stage up to 3·10^8 (about 1.2%, never tried).

### 1.2 Side scans of the 200-digit covers on ordinary processors

- **Where it stands.** Spare processor cores in six sessions scanned about 6,900 covers that the GPUs never used, at the
  record target. Nothing was found, and about 0.004 finds were expected. The combined ledger lists 6,466 covers; the
  second analysis session's final count for its set (2,589 covers, not the 2,174 listed) arrived after the ledger was
  closed.
- **What is unscanned.** 411 of the first 3,000 covers of the 613 family and its covers 3,000 to 5,999; the 2,727 free
  covers of the 479 family; the 523 family after cover 1,616 (of 8,572); the 467 family after cover 795 (of 3,000); and
  the 557 family after its first 959 covers.
- **Where the ledgers are.** `sublinear/cpu_scan/LEDGER.md` (the combined ledger), `bottom_up/cpu_scan/`,
  `g200k/cpu_scan_523/LEDGER.md` and `lean/scripts/scan200/`.
- **Is it worth it?** Barely. About 2,700 more covers would give a 0.27% chance of any find. It is a use for idle
  cores, not a route to 200,000.

### 1.3 Fixed gap 200,000 with fewer than 319 digits

- **Where it stands.** The record is a 319-digit N with g(N) = 207,307 (`records/g200k_319digit_g207307/`). An attempt
  at 300 digits scanned 24 covers with no find, against about 0.06 expected. The helper session scanned a further 136
  and 55 covers at 300 digits, also with no find.
- **How to pick it up.** `g200k/README.md` and `g200k/scan300/`; covers for 290 to 400 digits are in
  `sublinear/dual_covers/` and `g200k/`.
- **Cost.** One find at 300 digits should take some 65 to 100 CPU-hours on these covers.

### 1.4 The million gap with fewer than 1,797 digits

- **Where it stands.** The record is a 1,797-digit N with g(N) = 1,021,897 (`g_million/record_1797digit/`). A
  1,700-digit step was prepared (a cover on 547 primes, the sieve, and 300,000 selected candidates), and 1,184 of the
  candidates were tested (`g_million/tested_d1700.jsonl`) before it was paused.
- **Cost.** About 35 CPU-hours per find at 1,700 digits. Each further 100 digits costs about three times more.

### 1.5 The closeness frontier

- **Where it stands.** We hold numbers at 10% of the ceiling up to 110 digits, 25% up to 48 digits and 50% up to 27
  digits. Half of the 120-digit rung of the 10% line was scanned (200 covers, 1.12 finds expected, none found); the other
  half was lost when a container restarted. The 125-digit rung was not started.
- **How to pick it up.** `g200k/frontier/RESULTS.md` and `g200k/frontier.py`.

## 2. Mathematical questions

None of these has a known route to an answer. They are listed with what an answer would be worth.

### 2.1 The prize: good numbers without scanning

At the 10% target (213,070), the numbers that could supply the missing factor have about 1,116 rows left after sieving
by the primes up to 2,000, where members of the best cover have 1,309 give or take 14. A method that produced such
numbers below 10^200 for less than the cost of about 550 primality tests each would break even with the GPU search; an
ideal one would be worth a factor of 20 to 60,000. Nobody on the team found a way, and the second analysis session's
NP-completeness argument says a method would have to use something special about the primes. Background:
`sublinear/HANDOVER.md` (open question 1), `sublinear/README.md` (sections "Result 3" and "Why nothing known collects the
prize") and `bottom_up/query_bound.md`.

### 2.2 Several sorted lists on the one-condition problem

The research session's prediction, never measured because the runs were refused by a usage limit: two sorted lists
reach nine more small primes within one window-scan of work and gain five or six rows; four lists reach twelve primes but
need about seven rows of slack, so they lose. A four-list run at twelve primes that beats the window's best member by
more than seven rows would prove the prediction wrong and make the route worth pursuing (`sublinear/HANDOVER.md`, open
question 2).

### 2.3 A fast test of the parity of the number of prime factors

Whether this can be computed faster than factoring is open. It would matter here only if it cost under 2% of one
primality test per row, and even then it would be worth a factor of about four to ten, not 250.

### 2.4 Even and odd members

Rows of members with even index looked 0.35% likelier to be prime than rows of members with odd index (2.6 standard
deviations), with the opposite sign in a later sample. About ten million tests of each kind from the GPU logs would
settle it to 0.1%. No mechanism is known, and the research session expects noise.

### 2.5 How far covers can reach

How far the first n odd primes alone can deal with every prime is known exactly for n up to 35 (Lean up to 9, computed
twice up to 15, once beyond). Every formula proposed for how this grows was withdrawn, and no limit is known. A long
cover-search run on 1,228 small primes (2,000,000 sweeps) was stopped before it produced output.

### 2.6 What a fast method would contradict

The question of which standard hardness assumptions a fast generator of good candidates would contradict was asked and
not answered beyond the NP-completeness result for arbitrary tables.

## 3. Proofs and checks owed

- **132,103.** The only 200-digit-range record without a Lean proof and without a check by a second session. Its folder
  has the other proofs (`records/budget_1e200_199digit_g132103/`).
- **N − g prime for the fixed-gap and million-gap numbers.** For the numbers at 319, 347 and 400 digits and at 1,797,
  1,997 and 2,196 digits, Lean proves that no prime below g works, which is all those games ask. That N − g itself is
  prime rests on strong probable-prime tests. ECPP proofs at these sizes are possible but slow.
- **The stronger growth bound in Lean.** Lean has the bound ln X·(ln ln X)²/(150,000·(ln ln ln X)²)
  (`eventually_exists_even_le_log`). The consultant's written version adds one more very slowly growing factor,
  ln ln ln ln X, and has had only one reader (`gaps_map/COHERENT_BLOCK.md`).
- **Other gaps in the Lean library** (`lean/HANDOVER.md`, "Started but not finished"). Exact cover depths are proved
  only up to 9 primes; from 10 to 35 Lean has lower bounds. The old 2,480-digit height record (g = 1,157,341) is not
  checked, because the kernel's primality check is far too slow at that size. Of the toy worlds, Worlds 1, 3 and 5 are
  formalised, and the World 5 lower bound rests on a published result whose statement was not checked. Several laws
  were measured but not proved: the size of the number of covers, the steps of its derivation that rest on the
  Hardy–Littlewood conjecture, and the regularities found in World 3.
- **Results nobody else has read.** The second analysis session's newest toy-world results (W4.4, W4.5 and W2.1b in
  `bottom_up/worlds/`) and its NP-completeness proof; the consultant's stronger bound; and the replacement round of the
  research session, whose verifiers, synthesis and critic were all refused by a usage limit, so its eight reports are
  computed once and unrefereed. The coding-theory report of that round was stopped by a safety filter and not retried.
- **Calibration left inconclusive.** Near-misses at 140,000 in the last day: 5 found against 7.15 expected, running
  1.55 ± 0.45 times as far past the threshold as the model predicts (data: `phd/campaign3_gpu/runlogs/2026-11-25/calib_hourly.jsonl`;
  analysis script: `gaps_map/data/bottomup/nearmiss_rescale.py`). The fixed-gap searches made 5 finds where the model
  expected 12.3 in the same time (a 2% event); the outside reviewer considers this settled by the other calibrations,
  which all agree with the model.

## 4. Literature and novelty

- **Radomskii's preprint** (arXiv 2610.14127, version 3). If its Lemma 3.1 holds, it implies our two growth statements,
  and what stays ours is the elementary proofs and their machine check. The lemma sits in a section of about 24 pages
  that none of us read in full. An expert should read Section 3 before any claim of novelty is made. If the lemma
  holds, the consultant suggests stating it as a hypothesis in Lean and presenting our result as an independent formal
  proof (`gaps_map/HANDOVER.md`).
- **Searches not done.** MathSciNet and zbMATH were not searched, and several classical sources were cited second-hand
  (`gaps_map/LITERATURE_SEARCH.md`). Some toy-world references were read only through abstracts or citations
  (`gaps_map/TOY_WORLDS_LITERATURE.md`).

## 5. Decisions for the owner

- Whether to restart the 200-digit search, and on which design (section 1.1).
- Whether to submit the cover-depth sequence (how far the first n odd primes reach, exact to n = 35) to the OEIS.

## 6. Housekeeping

- Older sections of `RESULTS.md` quote closeness against the earlier fitted ceiling; the first sections and the
  closeness table use the computed one.
