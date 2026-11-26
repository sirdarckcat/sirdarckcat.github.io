# A failed CPU re-check is never dropped (the lead's rule of 25 Nov 10:20Z, after uarch's note)

Before this change, `search_gpu5.py` re-checked every GPU claim on the CPU (gmpy2) and, when the re-check failed, dropped the
member: `verify_success` returned None silently, and `verify_near_miss` logged only `NEARMISS-REJECTED`. A false composite on a
member's true first-PRP row would then have lost its true g.

Now both production engines handle a failed re-check the same way: `search_gpu5.py` (RTX, sha256 4f27d916ea93) and
`fround/search_gpu5_fr.py` (L4/T4, 30c34d151dd4).

- `true_g(N)` recomputes g(N) from N alone: the least prime p with N - p a probable prime (gmpy2, 25 rounds).
- The event is logged loudly as `C3GPU-KERNEL-DISCREPANCY <spec> k=<k>`, with the claim and the true g:
  - on stdout (the driver log, which the fleet watcher reports);
  - in the search log, as a line ending in "(re-check Error)", which the watcher's peek reports as well;
  - in `kernel_discrepancy.jsonl` next to `found.jsonl`.
- If the true g is at or above `--near-miss` (Q without it), the member is written to `found.jsonl` like any found line,
  with `kernel_discrepancy: true` and `claimed_q`.

Tested members, slice lines and the GPU path are unchanged: the new code runs only after a re-check fails.

`test_recheck.py` takes the four functions from the engine file itself and runs them on the CPU, on the 160,357 record's vector
(`test_recheck_out.txt`, both engines PASSED):

1. A wrong claim on the record's member (q = 160,343): the true g, 160,357, is found and recorded.
2. A claimed design hit on that member: the same.
3. A wrong claim (165,001) on its neighbour k + 1, whose true g is 619: logged, not recorded.

Each recompute takes at most 0.46 s.

Failed re-checks before the change: no `NEARMISS-REJECTED` line in any c170* search log (13 final snapshots, 5 running cards).
A failed `verify_success` left no trace, so the logs cannot count those.

Deployment, "at the next restarts":

- The patched engine was placed in each running card's `/content/c3g` at 10:33-10:36Z on 25 Nov. The old one is kept as
  `search_gpu5_pre_recheck.py`. The running processes are unchanged (threads only, already loaded).
- The ~23 h snapshots carry the patched engine to the replacements. Their gates (`kc_prod.sh`, `opl4gate2.sh`) run it on the
  GPU before production.
- The two waiting shares' local final snapshots got the same file (originals kept).
