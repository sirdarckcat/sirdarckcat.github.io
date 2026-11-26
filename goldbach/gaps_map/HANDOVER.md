# Handover: what these notes answer, how far to trust each, and what is unfinished

Written on 26 November 2026 for a curious reader without a mathematics degree. The notes are in this folder (`goldbach/gaps_map/`) on the branch `ccr-cdb2641a-5zg8un`. The helper session, one of the AI assistants on this project, wrote them for the other sessions (research, proofs in Lean, and the search on graphics cards). No human mathematician has refereed any of them.

## The question

A prime is a whole number above 1 that only 1 and itself divide (2, 3, 5, 7, 11, …). Goldbach's conjecture says every even number above 2 is a sum of two primes. For an even number N, the smallest prime p for which N − p is also prime is its *smallest Goldbach summand*; it is usually below a hundred. The project asks how large it can be for a special N below 10^200, a 200-digit number. The best found has a smallest summand of 160,357 (24 November).

The method chooses N so that, for many primes q, N − q is divisible by a small prime and so cannot be prime. A *cover* gives each small prime r one remainder class that N must have; a *row* is a prime q still to be knocked out. The best cover leaves about 1,500 of the 18,000 primes below 200,000 as rows, and the rest is luck and testing. Effort is counted in *nats*: one nat multiplies the work by about 2.7. *Lean* is a program that checks a proof line by line.

## The notes

**`GAPS_MAP.md` and `viz/goldbach_map.html`.** A picture of how the 196 results of the project depend on each other; interactive, also published at https://claude.ai/artifact/61W1713byd63vzpSgCL69p. Built from the other sessions' documents and tested in a browser; only as reliable as they are.

**`COHERENT_BLOCK.md` (the stronger lower bound).** Proves on paper that for infinitely many even N the smallest summand is at least a constant times ln N · (ln₂N)² · ln₄N / (ln₃N)², where ln is the natural logarithm and ln₂, ln₃, ln₄ apply it two, three and four times. The idea, giving all primes in a long range the remainder of one common number, came from the Lean session's careful reading and borrows a device of Erdős and Rankin; I replaced a heavy step by an average. I am the only reader of this write-up; the Lean session has machine-checked a weaker version missing the very slowly growing factor ln₄N.

**`PAIR_COVER.md`.** Asks whether knocking out two rows with one prime improves the proven constant, from 1.349 to about 1.352. It does, by 0.2%, and is superseded by the note above. Argued on paper, logic checked by me only, numbers computed once.

**`LIMIT_CHECK.md`.** Examines the research session's claim that the best cover depth divided by x · (ln x)² tends to 1.1275. Neither it nor my first answer (that the ratio tends to zero) is shown; I withdrew mine after the Lean session found the structure used above. Heuristic, tested on real primes, checked by nobody else.

**`LITERATURE_SEARCH.md`.** Asks whether our bounds were already known. Before 2026 I found nothing; two 2026 preprints come close (see below). An assistant's search plus my reading of the first pages of the key papers; several classical sources were not read.

**`MECHANISMS.md`.** Scores seven ideas for making N − q composite without a small factor, on small test problems with computable answers. None is worth a nat, except one that stops being worth it once the cost of testing a prime counts. Computed on three small cases, rebuilt from scratch and matched to the research session's numbers.

**`ROWS_AND_GAPS.md`.** Reaching 200,000 needs about 5.4 more nats, a factor of 220 in work. Could it come from the arithmetic of the rows, the record-gap methods or covering theorems? Seven candidates each give under a tenth of a nat or lose. Computed once, on a cover I rebuilt; the literature part is partly listed rather than read.

**`LATTICE_CHECK.md`.** Tests whether lattice reduction, a tool from cryptography, can pick out the special numbers of a search window. The best variant I found reaches 0.36 of what it would need. Computed with a formula and a simulated window; no independent check.

**`BOTTOM_UP.md`.** Starts from scratch: where do the 460 nats of a 200-digit number go, and does anything beat the present method? Nothing lowers the effort. It holds a success model that matches the 69 published records (within its error for the large ones, optimistic for the small), a tally of the fleet's finds (11 found, 12.8 expected), a scan on ordinary processors (273 covers at the record level, nothing found; at a lower level 42 found against 46.7 predicted), and a check that the present design is best for any plausible tail behaviour. Computed, scripts and logs included.

**`TOY_WORLDS_LITERATURE.md`.** What the literature proves about the toy problems the research session set up (error-correcting codes and their integer analogues, noisy interpolation, knapsack-style problems, polynomials over finite fields). Statements read in about twenty papers, not their proofs; a few (Bleichenbacher–Nguyen, Goldreich–Ron–Sudan, Guruswami–Sahai–Sudan) only through abstracts or citations, as the note says.

## What is unfinished

**The Radomskii question.** Radomskii (arXiv 2610.14127, version 3 of 1 November 2026) is a single-author preprint, a paper posted online before formal review. His Theorem 1.1 says that for any set B of numbers there is a stretch of consecutive integers none of which is a prime plus an element of B. Taking B to be the primes up to y gives, for large X, an even number with smallest summand above y, hence a smallest summand of at least a constant times ln N · (ln₂N)² infinitely often. He does not state this as a Goldbach result; that step is my inference, and I checked its logic. Everything rests on his Lemma 3.1, in a section of about 24 pages, whose statement I confirmed but whose proof I have not read and nobody has refereed.

If the lemma holds, our two bounds (any constant times ln N · ln₂N, and the larger order above) are probably not new as statements, because his would imply them; what stays ours is the machine-checked proofs, which use only elementary tools. My unchecked observation is that his lemma plus our structured block should add a further factor, which would be new. If the lemma fails, our bounds are new as far as I could search. An expert should read his Section 3; if it holds, state the combination as a hypothesis in Lean and present our result as an independent formal proof citing his theorem.

**The fleet's near-miss rate.** It would pin down the chance of ever reaching 200,000. I cancelled the final analysis when asked to stop. At 07:11 UTC the fleet had logged 5 events against 6.3 expected, and they ran 1.55 ± 0.45 times as far past the threshold as the model predicts, too few to conclude anything. The data are in `goldbach/phd/campaign3_gpu/runlogs/2026-11-25/calib_hourly.jsonl` (branch `ccr-8ffe9d7a-4ni11u`); `data/bottomup/nearmiss_rescale.py` computes the numbers in minutes.

**Scans not done.** About 2,700 more covers at the record level were planned for ordinary processors; their combined chance of any find was 0.27%.

**No second reader.** Apart from the Lean-checked parts, every note is single-author work that no one has refereed, and each quotes results from other sessions that I did not recompute.
