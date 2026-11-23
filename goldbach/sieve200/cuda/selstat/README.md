# selstat: what the selection statistic is worth (CPU, real sieve counts)

Scripts behind NEARTRUNC.md and the model in HEADROOM.md (uarch, 23 Nov 2026).  They run sieve200's C sieve on a production vector spec (a Q = 170,000 spec with 1,248 rows: `SPEC=...`, default `phd/campaign3_gpu/v89/knowncase_spec.json` of origin/ccr-8ffe9d7a-4ni11u) at B = 1e8 on windows of 2^19 members (~25 s a window).

* `selexp.py B logK k0_offset`: expected near-misses >= G (sum (1-p)^c_G over the kept) and design hits (sum (1-p)^c_total), selecting by c_G against by c_total, with the production keep rule (blocks of 2^15, 492 kept).
* `selcurve.py B logK`: the same gain against the near-miss threshold G.
* `fsweep2.py`: the time model (batch = fixed + slope (1 - f)) validated against the GPU session's measured keep-fraction sweep, and today's predicted optimum.
