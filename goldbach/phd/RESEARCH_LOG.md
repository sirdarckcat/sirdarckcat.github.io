# PhD Research Log — Extremal Least Goldbach Summands

Programme: *Extremal Least Goldbach Summands* (4-year proposal, record snapshot 2026-07-22).
Student log, year 3 — project kickoff with delegated subagent execution.

## Record board (updated 2026-11-21)

| Game | Incumbent | Value | Status |
|---|---|---|---|
| Height H (Game 1) | **91,752-digit** N (records/height_91752digit_g16046137) | g = **16,046,137** | **new 2026-11-22**; PFGW-screened (Colab CPU), CPU-proved (BLS), complete cover. Passes verify.py, PARI (N−1 certificate, isprime and the full scan) and both bls/ verifiers here. Cross-verified by the second session (verify.py, bls/xverify.py, the PARI scan and certificate: all pass). Previous: g = 10,000,141 @ 61,329d (records/height_61329digit_g10000141), GPU-screened (Colab A100), CPU-proved (BLS), complete cover; passes verify.py, PARI and both bls/ verifiers here; cross-verified by the second session (verify.py, PARI, bls/xverify.py: all pass). Earlier the same evening: g = 5,000,251 @ 33,938d (records/height_33938digit_g5000251), GPU-screened, CPU-proved; passes verify.py, PARI and both bls/ verifiers. Earlier the same day: g = 2,000,269 @ 15,595d (records/height_15595digit_g2000269), N−1 (BLS) proof, no ECPP, complete cover; passes both independently written verifiers and PARI. Same day: g = 1,200,109 certified twice, for two different 11,263-digit N, by two independent sessions (records/height_11263digit_g1200109 and records/bls_game1_11263digit_g1200109). Previous: g = 1,157,341 @ 2,480d (slop/goldbach/records/g1) |
| Threshold T(100,000) (Game 2) | **150-digit** N (GPU fleet, records/threshold_150digit_g104527) | g = 104,527 | **re-verified PASS here** (witnesses + independent ECPP, 2026-07-28) |
| Budget R(10^199)/R(10^200) (Game 3) | **199-digit** N (records/budget_1e200_199digit_g133981) | g = **133,981** | **new 2026-11-22**; campaign3 on Colab GPUs (search_gpu3.py), certified by certify_c3.sh: witnesses, PARI primecert, ecpp_check.py, slop's stdlib verify_record.py, direct gmpy2 and PARI. Same night: g = 132,103 and 125,269 (both 199 digits, also frontier points). Previous: g = 119,419 (r200 round 1) |

### 2026-11-22 (night) — Game 3 on Colab GPUs (`ccr-8ffe9d7a` session): g = 125,269, 132,103, 133,981 below 10^199

- **Engine.** `search_gpu2.py` (GPU sieve plus GPU Fermat tests) ran 63-67k members/s on an L4. `prof_gpu2.py` showed why:
  41% of the tests computed fell after a member's first PRP (93% at skip-frac 0.97), because a launch held one block's members.
  `search_gpu3.py` pools a batch of 32 slices into one tester (all variants share M), which cuts the waste to 5-9%.
  `check_v3.py` shows identical alive matrices and slice lines to `search_gpu2.py`, and Q = 3001 end to end against brute force.
  Production uses skip-frac 0.97 (each block's emptiest 3%, ~14% of the hit mass) and the top of k first: E falls as N grows,
  ≈ 0.25 nats between k ≈ 10^7 and the 199-digit ceiling.
- **Hardware.** Colab G4 runtimes (NVIDIA RTX PRO 6000 Blackwell; the kernel does 8.9·10^6 tests/s against 2.3·10^6 on an
  L4): three of them, plus the L4 and later an A100. One G4 does 9.3M members/s at f = 0.97, i.e. 1.32M members/s of full
  hit mass, ~21x `search_gpu2.py` on the L4.
- **Hits.** In the first 25 minutes with the 867-row campaign-3 families (Q = 122,000, N < 10^199): 125,269 (v367),
  133,981 (w175), 132,103 (v851). All are certified and all are frontier points; 133,981 is the largest g known below 10^200
  (closeness 6.36%).
- **Lean 850-row cover** (Q = 122,000, N < 10^200; 3,000 residue-swap variants): four more hits, 122,827-126,397, none
  above the record. The overshoot model, from the cover's own classes beyond Q (an uncovered prime there is killed with
  probability 1 − 0.122, then N − q is prime with probability ≈ 0.024), gives a mean g − Q ≈ 3,300-3,450 and
  P(g > 133,981) ≈ 0.034 per hit. So the two large hits were lucky draws, and larger Q is the lever.
- **Tally** (`campaign3_gpu/TALLY.md`): over all covers, 7.26 expected against 7 found. The model is on target in aggregate.
- **Since 21:08Z**: Q = 140,000 (research cover, 1,011 rows; E^ 24.04-24.18 measured) and Q = 150,000 (1,093-1,094 rows;
  E^ 25.97-26.14). Both covers were checked here.
- **Kernel 3** (`gpu_fermat3.py`, 21:25Z): dedicated squaring plus lazy Montgomery reduction (16n < 2^672). It matches gmpy2
  and the proven kernel, and is 1.48x faster on the RTX PRO 6000 and 1.78x on the L4. Expected rate ≈ 8 hits a day at
  Q = 140,000 on three GPUs.

### 2026-11-21 (evening) — Campaign G (`ccr-8ffe9d7a` session): GPU rungs on Colab; g = 5,000,251 and 10,000,141

Authorized by the user ("colab the fuck out of this problem"). One A100
runtime (the account allows one GPU at a time), its 12 vCPUs, and a second
8-vCPU CPU runtime. The split with the other session: it runs g > 3·10⁶ on
its own CPU; this session owns 5·10⁶, 10⁷ and 16,045,849.

- **Engine.** `proth/gpu_screen.py` is a CuPy batched Montgomery engine
  (15-bit limbs in float64, cuFFT).
  - v1 failed validation on structured operands: Mont(1) = R mod P has
    long 0x7FFF limb runs. An exact carry-lookahead kernel fixed it.
  - v2 merges an inverse FFT (1.11×). v3 drops the copies (1.12×, bit-for-bit
    equal to v2).
  - Every version is validated against gmpy2 and the known primes before
    use. GPU passes are re-proved on the CPU.
- **g = 5,000,251 at 33,938 digits.** 68 CPU and 3,072 GPU tests (0.85 s
  each). The hit is the 3,080th survivor, against ~2,118 expected
  (p ≈ 0.23 of waiting that long). It passes the CPU BLS proof, `verify.py`
  and the PARI cross-check, which is now a `parforprime`: identical logs,
  2.8× faster on 3 threads. The second stack passes too: `bls/xverify.py` and
  `verify_bls_record.py` (via `interop.py to-bls`), in pure-Python ints,
  46 min each. Their logs are in the record directory.
- **g = 10,000,141 at 61,329 digits.** 3,072 GPU tests (512 with v2 at
  2.76 s, the rest with v3 at 2.35 s), ~2 h of A100 time in all. The hit
  t = 6063 is the 2,718th survivor of the 10¹¹-sieved list (expected
  ~3,130; p ≈ 0.42 of waiting that long).
  - The total includes 113 tests on candidates that the live deep sieve
    removed later.
  - The hit was re-proved on the CPU (BLS, 306 s) and passes `verify.py`:
    9,095 cover classes and all 664,584 primes below g.
  - It also passes the PARI cross-check (2.8 h) and both `bls/`
    verifiers (61 min each through `proth/divmod_pow_run.py`). The second
    session re-ran `verify.py`, PARI and `bls/xverify.py`: all pass.
  - g is the first prime above 10⁷ that the cover (built for the odd
    primes below 10⁷) misses; the five primes in between are covered.
- **Deeper sieve.** `deepsieve.c` takes the survivors from 10⁹ to 10¹¹
  (10⁷ rung) and toward 10¹² (16M rung) while the GPU runs. That is ~18%
  and ~25% fewer expected tests. It repurposes the 16M CPU helper's
  cores: PRP tests on CPU would have covered ~8% of that rung in the same
  time.
- **Incident.** My batch-boundary restart script for the 10⁷ rung read
  the line count of a log that did not exist yet, fell through, and killed
  the first 10⁷ batch at 76%. That lost ~17 min of GPU time. The intended
  end state (a reloading search) was reached anyway. Lesson: guard every
  wait on a file's existence.
- **Second incident (an H100 attempt).** An H100 has ~2.2× the A100's
  memory bandwidth, and the engine is bandwidth-bound. The account allows
  one GPU, so trying meant releasing the A100. My freeze script waited
  for the 10⁷ deep sieve to finish but not for the batch boundary, and
  stopped a batch at 98.5%. It also used `pkill -f` inside `sh -c`, which
  matched its own shell, so the later kills never ran; a PID-based kill
  finished the job. All state was harvested and no H100 was available, so
  a fresh A100 took over after 10 min idle (engine re-validated on it,
  queue resumed from the logs). Cost: ~33 min of GPU time in all.
- **CPU fleet for 16M.** Colab allows 7 active runtimes (one GPU). The six
  CPU slots hold gold-cpu (sieving), four 8-vCPU runtimes running
  `cpu_search.py` top-down on t mod 8 = 0..3 (~29 tests/h each), and one
  orphan CPU runtime that a timed-out TPU request left behind. The CLI
  cannot address the orphan. The A100 host's CPUs and gold-cpu join as
  slices 4 and 5 when their sieve ranges finish, which together adds ~30%
  to the GPU's ~570 tests/h. A third pgrep self-match (`os.popen` →
  `sh -c`) would have blocked the joins; it was caught in the first status
  cycle and fixed with the `[.]` pattern trick.
- **Third incident (the replacement A100 vanished).** Between 21:33Z and
  21:47Z the A100 runtime dropped out of Colab's assignment list, with no
  error or notice. The CLI then pruned it as stale. Its loss was costly
  because the A100 watcher had hung since ~20:36Z on a `colab exec` to
  gold-cpu that never returned; the CLI's own `--timeout` did not fire.
  So the 10⁷ log had last been harvested at 2,048 tests. About three
  batches (~1,500 tests) and a partial fourth were lost, ~1.4 h of GPU
  time with the restart.
  - Correctness is unaffected: the search re-runs those survivors in the
    same order.
  - A new A100 passed the v3 known-answer check and resumed at 21:56Z.
  - Fixes: every Colab call now has a hard `timeout`; each watcher loop
    writes a heartbeat that the alarm checks; the 16M fleet's master list
    and kill lists are kept locally, not on the GPU host.
  - A seventh runtime was then refused with six active, so the six slots
    are the GPU and five CPU runtimes. The orphan is gone.
- **16M sieve to 3·10¹¹.** gold-cpu's [10¹¹, 3·10¹¹) pass (7.7·10⁹ primes,
  2.5 h on 8 threads) found 767 kills, all re-verified locally (p prime,
  p | P_t). 636 are new against the 10¹¹ list, which goes 15,215 → 14,579.
  gold-cpu then joins the fleet as slice 5.
- **Fourth incident (this session's container was replaced).** At ~02:11Z
  on 11-22 the local container was reclaimed while no harness-tracked task
  was running: the failure mode logged on 2026-07-22. Files survived;
  processes did not.
  - Lost: the two unmodified `bls/` verifier legs for 10⁷, ~3.4 h into
    a ~4.5 h run, and the local Colab watchers.
  - Unaffected: Colab. All six runtimes kept searching the 16M rung.
  - Recovery: the legs were re-run through `proth/divmod_pow_run.py`
    (divmod reduction, ~4× faster, checkpointed) as harness-tracked
    tasks, which also keep the container alive. Both passed in 61 min.
    When nothing is running, a scheduled check-in now resumes the session.
  - Both legs do the same exponentiation, so they shared one checkpoint
    file. Neither resumed from it, so each computed it in full. The
    checkpoint key now includes the verifier's name, and a finished run
    deletes its checkpoint.
- **Time limit, relay and a fallback range (05:45Z).** The alarm and the
  local slice 6/8 reached the harness's 2 h limit for background tasks.
  They were not restarted: the alarm now runs under the Monitor tool
  (30-min re-arms), and the local cores went to the fallback below.
  - After 5,517 tests with no hit, the chance that the remaining 9,062
    survivors below 32768 hold no prime is e^(−9062/4488) ≈ 13%. The spec
    allows t < 2^20, so the local cores sieve t ∈ [32768, 131072) by the
    same chain.
  - That sieve reproduced the main 10⁹ pool exactly below 32768. The
    local `deepsieve` build matched the Colab kills on [10⁹, 2·10⁹)
    exactly (607 of 607). [10⁹, 10¹¹) took 56,187 → 45,994 survivors
    (−18.1%; the main pool lost 18.0%).
  - A relay now puts every tested t on every machine as a `*.kills.json`
    list, so the GPU (bottom-up) and the fleet (top-down) stop at each
    other's work. gold-cpu3's first reload dropped exactly the 516
    GPU-tested t of its slice.
- **PFGW (~07:50Z, approved by the user).** OpenPFGW 4.1.8 (gwnum)
  replaced GMP on all six CPU runtimes, as a screen only; a pass is
  re-proved by `desert.bls_prove`.
  - On gold-cpu5, with its GMP search paused, the 10⁷ record's P was
    3-PRP in 23 s, and eight known composites came out composite with
    reproducible residues.
  - A 16M test took ~60 s with four in parallel, against ~1,000 s for one
    GMP test with eight in parallel: ~240 tests/h per runtime instead of
    ~29.
  - The fleet goes from ~170 to ~1,450 tests/h, beside the GPU's ~590.
  - gold-gpu runs five at nice 19 so the GPU's host process keeps
    priority.
- **g = 16,046,137 at 91,752 digits (hit 10:52Z on 11-22).** It was found
  on gold-gpu's fallback slice 4/6, at t = 127,534: PFGW 3-PRP in 45.5 s,
  then `desert.bls_prove` on the runtime. All searches stopped at 10:53Z.
  - Tests run: 13,124 distinct t. 12,470 of the 14,579 survivors below
    32768 were tested (7,168 GPU, the rest CPU), and 643 of the 44,130 in
    the fallback range.
  - 191 t were tested by both the GPU and the fleet, where they met; all
    were composite both times.
  - At ~4,488 expected tests per prime, a first prime this late has a
    probability of ~5%. The hit came from the fallback range while 2,109
    survivors below 32768 were still untested. Those had about a 37%
    chance of holding a prime; that range is now left unsearched.
  - Proved again here with `desert.bls_prove` (759 s). F = 2^101604, since
    m = m0 + t·Mc is divisible by 16; P has 304,793 bits.
  - The second session rebuilt N from `spec.json` and t alone and got the
    same sha256. Its `verify.py` passed in 632 s.
  - Both `bls/` legs pass, run alone on two Colab CPU runtimes:
    `xverify` in 2.4 h and `verify_bls_record` in 2.5 h.
  - PARI here passes in full (5.4 h): N−1 certificate valid,
    `isprime(P) = 1` (~3 h on one core), and the complete scan. A second
    scan, in six ranges on two Colab runtimes, passes too.
  - Colab reclaimed the four runtimes that sat idle after the search,
    the A100 among them.
  - The second session's `xverify` and PARI scan (nine ranges) pass too.
- **Not available.** A second GPU (TooManyAssignments) and a TPU host
  (pool "Service Unavailable" twice). The compute-unit balance (~9,300)
  is not a constraint.

### 2026-11-21 — the two branches merged (`ccr-2ce9e63a-hn0fuw` ← `ccr-8ffe9d7a-4ni11u`)
- Two sessions started from the same commit, both prompted by the same
  PDF, and worked separately. Both concluded that a proof of GRH moves no record, both
  found the same N−1 construction for Game 1, and both certified
  g = 1,200,109 (two different N). Each then reviewed the other, and the
  merge was agreed by message between the sessions at the user's request.
  Decisions, path map and errata: `merge_2026-11-21.md`.
- **Layout.** One build-and-search pipeline (`proth/desert.py`). One
  verification stack with three independently written legs
  (`proth/verify.py`, `bls/verify_bls_record.py` + `bls/xverify.py`, and
  PARI's own N−1 proof via `crosscheck.gp` in each record directory). All
  three records in `records/`. Memos: WP10 and WP11 are the
  `ccr-8ffe9d7a` session's, WP12 the `ccr-2ce9e63a` session's.
- **Errata folded in.** The two long searches at 1.2·10⁶ were one
  progression (joint p = 0.046, not ≈1%); the paper's Theorem 14 is
  superseded in rate, and GRH's Linnik gain on the paper's smooth moduli
  is ×1.2, not ×2.5; one mutation-test harness had never been committed.
- **Out-of-sample probe of the 1.2·10⁶ progression** (WP12 §6): the 3,245
  sieve survivors with t ≤ 16,383 that neither search had tested, done
  exhaustively. 6 primes against 4.62 expected (z = +0.64); over the
  whole range 8 against 11.0. The density model holds on fresh numbers;
  the long waits were chance.
- **Verified by both sessions after the merge**: every record passes
  every leg in both containers. The other session's check of the merged
  branch found four small misstatements of its work, all fixed
  (`merge_2026-11-21.md`, errata 9–12).
- The entries below are kept as each session wrote them, labelled by
  branch.

### 2026-11-21 — cross-review of `ccr-8ffe9d7a-4ni11u` (by the `ccr-2ce9e63a` session)
- A second session did the same exercise separately and converged on the
  same construction (BLS-form complement, complete cover, n = 12,475) and
  the same g = 1,200,109, for a different N. Full review:
  `phd/crossreview_8ffe9d7a.md`.
- **Cross-verification, all PASS**: their stdlib verifier on both records
  here (via `proth/interop.py`), this branch's verifier and PARI's N−1
  proof on theirs. Three records, two independently written checkers,
  plus PARI.
- **The two unlucky waits were one event.** Their search ran over exactly
  the odd-t half of this branch's progression (re-sieving reproduces their
  3,472 tests); 1,341 integers were tested by both. Jointly: 2 primes
  where 6.42 were expected, p = 0.046 — not two independent 1–2% tails.
  Pooled over all probes and searches: 112 primes vs 114.7 expected.
- **Adopted from them**: verifier mutation test (11/11 rejected).
  **Corrected here**: Theorem 2 of WP12 is vacuous at record scale (their
  finite-size sieve computation shows it); caveat added.
- **For them**: the board is at 2,000,269; the paper's Theorem 14 is
  superseded, not merely re-constanted; lazy covers and a 10⁹ sieve are
  ~35% less search; PARI gives a second proof where they have BPSW.
- Trial merge: conflicts only in the SoK and this log. (Merged later the
  same day; see the entry above.)

### 2026-11-21 — cross-review of `ccr-2ce9e63a-hn0fuw` (by the `ccr-8ffe9d7a` session)
- The other session found the WP11 construction independently and first
  (08:03 against 08:44 UTC). It then certified g = 2,000,269 with a lazy
  cover ~10% shorter, and proved two covering theorems:
  - C(x) ≥ 1.349·x·ln x, which beats the paper's Theorem 14 and Shi's ½;
  - C(x) ≤ x^(4+ε).
- **Verification.** All three records pass both branches' verifiers and
  PARI, re-run here. Their theorems were re-derived; their Shi citation
  was verified verbatim against the v6 PDF.
- **Corrections here.** "New record" and "first without ECPP" are
  relabelled "independent second certificate"; WP11's ladder is ~30%
  pessimistic next to the lazy cover.
- **Open item (corrected at the merge, at this session's request).** The
  two Q = 1.2·10^6 searches were not independent (one progression); joint
  P(≤ 2) = 0.046; out-of-sample probe in WP12. A merge plan is in
  `crossreview_2ce9e63a.md` (carried out; see the entry above).

### 2026-11-21 — WP12 (`ccr-2ce9e63a` session; numbered WP10 on its branch): review "with the GRH announcement for inspiration"
- User directive: look over the Goldbach-gaps work for improvements, reading
  `alpo.ge/remark.pdf` for inspiration. The PDF is not about Goldbach: it
  announces a proof of RH/GRH found with Claude and formalized in Lean
  (not checked here). Full memo: `phd/wp12_prime_covering_grh_ledger.md`.
- **GRH ledger** (WP12 §3): it moves constants, not walls. Realisation
  constant 0.56 → 0.67; guaranteed N−1-certifiable realisation exponent
  12 → 6 (practice: 1.5); Miller's deterministic test would cost ~12
  core-years per 11k-digit complement, against one modexp for a
  constructed one; the bounded games and the density model are untouched.
- **Certification wall of Game 1 removed** (`goldbach/proth/`): complement
  built as m·2ⁿ+1, cover congruences moved onto m by CRT, primality by the
  BLS N−1 test. With certification free, complete covers beat partial
  cover + luck by 4–8× here (REGISTRY A2 "dominated" flips for this game).
  Record g = 1,200,109 at 11,263 digits; 2,647 PRP tests against ~700
  expected (a 2% tail; sieve and density model re-validated at full and
  at reduced scale before accepting that it was luck). Then
  g = 2,000,269 at 15,595 digits on the shorter lazy cover: 648 tests
  against ~970 expected, 37 min on 4 cores — Campaign C's target.
- **Covers**: weighted lazy greedy over a 3× prime pool is ~10% shorter
  than the paper's fixed-order greedy (the one-kill tail mostly goes);
  a price-reweighted variant was tried and was worse. Remaining gap to a
  proper packing of the sparse tail is the new Door-1-style problem.
- **Theory** (WP12 §2): prime-covering function C(x) ≥ (e^γ/2C₂ − o(1))·x·ln x
  = 1.349·x·ln x by pigeonhole — stronger than the paper's FGKMT-transfer
  Theorem 14 and than the counting constant ½ of arXiv:2605.21529 — and
  C(x) ≤ x^{4+ε} by the linear sieve + Bombieri–Vinogradov, the first
  impossibility statement in the family. Greedy data: 0.72·x·ln²x.
- **Not done**: a Lean proof of the record. Toolchain installation was
  refused by the session's permission policy; nothing unchecked was
  committed. Paper patch drafted (WP12 appendix) but `paper.tex` untouched.

### 2026-11-21 — WP11 (`ccr-8ffe9d7a` session): Game 1's certification wall removed; g = 1,200,109 (independent second certificate; see the cross-reviews above)
- **Prompt.** The user pushed back after WP10: if frontier research is
  possible, find a non-brute-force way to move faster. Answer: for the T
  and R games the brute force is the cheap part (≈0.03 nats of luck per
  residual against ≥ ln Q ≈ 11.5 nats to plant a divisor). Game 1's wall,
  though, was an artifact of proving whatever prime the search produced.
- **The trick (SoK §6/§7.2, flagged as open).** The cover modulus is odd,
  so N ≡ g+1+2^n (mod 2^(n+1)) is free by CRT. Then 2^n exactly divides
  P − 1 for P = N − g, and with 2^(3n) > P the BLS theorem proves P prime
  from one modexp. The price is ×1.5 digits. With full covers (no
  residuals), the certificate is the congruences plus one modexp. The
  proof is re-derived in `wp11_bls_game1.md` §1.
- **Validation.**
  - `bls/full_cover.py` reproduces the paper's Table rows for Q = 10^5,
    10^6 and 10^7 exactly.
  - The independent stdlib verifier rejects 6/6 tampered records. It had
    one bug at record scale (Python's 4,300-digit int-to-string cap),
    now fixed.
  - The density model was measured at z = +0.76 and −0.43; the sieve was
    audited.
- **Record.** 11,263 digits, g = 1,200,109, found after 3,472 tests on 4
  cores in 76 min. That was a ~1%-tail draw against 762 expected. It was
  verified three ways: the stdlib proof checker (87 s), GMP BPSW, and a
  GMP recheck of the congruences.
- **Ladder on this box (GMP).** 5M ≈ 13 h, 10^7 ≈ 3.6 d, 16,045,849 ≈ 13 d
  (longer than every known prime gap). GWNUM or the GPU fleet should be
  5–10× faster. The T(10^5) and R(10^200) frontiers are unchanged.

### 2026-11-21 — WP10 (`ccr-8ffe9d7a` session): a claimed RH/GRH proof (alpo.ge/remark.pdf) assessed: no lever moves
- User asked whether the announcement inspires frontier progress. The
  analysis assumes the claim is true. The Lean archive was not checked,
  and the verdict does not depend on it. Memo:
  `wp10_grh_remark.md`. Numbers: `wp10/grh_reach.py` (6 s).
- RH/GRH are √x-quality statements and every bottleneck here is
  x^{o(1)}-scale. The RH prime-window is 10^72.4 too coarse for the
  150-digit desert. GRH on the scanned progression is 10^65.6 short and
  bites only at N ≈ 280 digits. The sieve level GRH gives is the one
  Bombieri–Vinogradov already gives, and there the Door-1 floors are
  vacuous (−0.46·π(Q)). H1 and H2 are untouched. Miller-under-GRH
  certification costs 5.8 core-days at 2,480 digits against ECPP's ~2 h,
  with no certificate.
- Paper constants only: the Linnik step L ≤ 5 becomes 2 + o(1). SoK §7.3's
  GRH sub-angle is closed. The one transferable idea is methodological:
  proof-carrying records (SoK §7.8). The board is unchanged; Doors 1 and 2
  remain the only levers.

### 2026-07-29 — WP9 (Door 3) underway: closure theorem + falsification engine
- User directive: work Door 3 first (AlphaEvolve access offered for the
  generative tier). Delivered so far, all in `phd/wp9/`:
  **theorem draft v0.1** (scheme/certificate formalism, three lemmas with
  proof-status marks, schema language L, falsification protocol);
  **tier-0 calibration** — engine reproduces every WP7 hand number exactly
  (m²−c: c=398/113 kills; the 5.8-vs-10.5 nats/residual discrepancy
  reconciled as B=10^100 vs 10^200 context), and surfaced two refinements:
  covering endgame ≈ 1.0 nats/offset at Q=122k (2.5 was context-bound), and
  budget binds at 122k vs boost–kills equilibrium at 200k;
  **exhaustive tier: 13,661 schema instances, 0 passes** (16 first-run
  passes audited away as a baseline-family filter leak — semantics
  hardened); near-miss board topped by ExpFamily at 3.1–4.2 nats/residual
  kill (3× covering endgame, as WP7-P3 predicted);
  **Lemma 2 rigorous draft** (deterministic shared-divisor proposition +
  explicit H1 + the 1.2e9-candidate empirical bound);
  **enumeration wall measured**: quartic-product certificates cost
  height^0.50–0.74 work per certified offset (theory ½) → ~10^100
  ops/offset at B=10^200 — Lemma 1(c)'s first data.
- Later same day: §9–§10 land the mathematics — k_max cluster formula
  closes EVERY shared-variable identity family with v < d (all certify
  ≤13 offsets vs ~18,000 needed; α̂=0.761 measured vs 0.750 predicted);
  within-grammar Lemma 1 now [P] modulo value equidistribution. H2 note
  posting-ready; AlphaEvolve scorer harness ready (blocked on access).
  Remaining math: torus-action ⇒ norm-structure classification (v ≥ d).
- §11 (same day, continued): the classification item DISSOLVED — local
  isolation (all ellipsoid extents < 1 at 10^200) + orbit conservation
  (symmetry preserves value or factor; mixed words miss the window by
  10^190) close the dense frontier outright. Lemma 1 [P at draft rigor]
  on L and beyond; Door 3's mathematical core is COMPLETE at draft
  level. Next: Door 1 gate D1.0/D1.1 (does anything beat 867?).
- Door 1 turn 1 (same day): D1.0 diagnostics — 19/88 moduli tight
  (gap ≤ 1) at the greedy point; random-start ascents land 90–110 primes
  WORSE (greedy's adaptivity ≈ 2.4 nats); backbone overlap 2.4% = chance
  (fully degenerate landscape — no crossover structure). D1.1 gate after
  22 exact-LNS windows (CP-SAT, incumbent-floored): 867 never beaten,
  always matched; optimality proofs did not close within caps — gate
  OPEN, next: per-window LP certificates + provable small windows.
- Door 1 turn 2: LP certification added — **17 of 18 new windows
  CERTIFIED optimal at the incumbent** (floor(LP) = incumbent coverage;
  sizes 7 and 12, incl. tight-set at 120s caps). 40 windows total, 867
  never beaten. The one uncertified window contains small moduli (LP
  gap 16 — the global LP vacuousness in miniature). Turn 3: size 14-16
  at 300s + random-restart basin probe, then gate verdict.
- Door 1 turn 3 — **GATE VERDICT: 867 survives, certified.** 41 exact
  windows (7–15, up to 300s), 21/22 LP-certified window-optimal; basin
  probe: a random-ascent solution at 968 is ALSO window-optimal (0/101
  gap recovered in 20 windows) — the landscape is a field of distant
  locally-exact basins; greedy's adaptive construction sits ~100 primes
  deeper than typical. Local exactness is exhausted; remaining Door-1
  upside = global moves (basin-hopping tempering, SP-decimation) and
  banded constructions (D1.2/D1.3). Full verdict:
  wp9/door1/d11_gate_verdict.md. D1.1 chain stopped.
- Door 1 D1.2 (BP/SP): BP validated (toy exact-optimum found by
  decimation; soft-regime E[U] to 0.7%). Real instance: decimation 874
  / 887 / 922 across β; LNS polish of 874 stalls at 874 — a THIRD
  isolated locally-exact basin (867/874/968). Naive Bethe slides to the
  fractional fantasy at low T (35 at β=4): RS invalid as threshold
  estimator, 1RSB/SP needed. Running verdict: 867 is at/near the
  quenched optimum; annealed 758 likely a clustering gap. Door-1 prize
  revised to 0–2.6 nats. Verdict: d11_gate_verdict.md addendum.
- **AlphaEvolve access LIVE** (owner-granted, verified 2026-07-29): project
  sdcpocs, engine goldbach_1784979910032, Discovery Engine v1alpha. Read
  path fully working — 7 prior experiments found (5 COMPLETED, 2 PAUSED),
  including the "Super Hard Constrained Multi-Objective Goldbach Cover
  Step-Heuristic" run whose 100 programs and scores corroborate the earlier
  file-based review (best neg_est_digits −193.6 at E 17.56). Coordinates,
  API gotchas (relative resource names; broken `cryptography` needing
  --ignore-installed), and the WP9 build order are in
  wp9/engine/alphaevolve_access.md. Confirms the loop is CLIENT-evaluated
  (acquirePrograms → local grading → submitProgramsEvaluations), so the
  harness's anti-reward-hack property holds. Not yet started: a real
  experiment (spends the owner's quota — awaiting go-ahead).
- **Generative tier ran** (owner approved): experiment
  15926813306184238842, ~36 candidates, ~617k output tokens. It found a
  hole in MY EVALUATOR before it found anything about the theorem —
  per-offset costs were billed only against the 867 residuals, so
  ExpFamily could advertise 10,416 offsets costing 22,900 nats against a
  460-nat budget (apparent fitness 0.46). Hardened; re-scored 0.046. The
  correction sharpened the economics: the bar for a bulk mechanism is
  covering's AVERAGE 0.041 nats/offset, not its 1.01-nat marginal
  endgame. Then the closures went from empirical to costed: ExpFamily
  needs 1151 nats to reach 1048 offsets (2.5x budget; ceiling 419),
  PolyImage/Cyclotomic cap at sqrt(Q)=349 offsets at ANY price, Compose
  is empty at scale ((m-m')(m+m')=c1-c2 forces m <= |c1-c2| while record
  scale needs m ~ 1e100). Memo secs 12, 13, 13b, 13c.
- **DOOR 3 COMPLETE** (draft rigor). Generative tier converged at 41
  candidates / 4 families / zero passes (best 0.0919). Verdict in memo
  sec 14: closure theorem holds across the grammar with every family
  closed by a proof of its own kind; conjectural remainder is H1, H2, the
  o(1) terms, and out-of-grammar mechanisms. Methodological headline: the
  adversary broke the REFEREE first (50x accounting error), the audit
  protocol caught it pre-claim, and fixing it strengthened the theorem —
  adversarial search is best reported as referee-hardening, not as failed
  refutation. Programme consequence: the covering monopoly is now a
  result, so records are governed by Door 1 (rounding gap, 0-2.6 nats,
  resistant to LP-certified windows / BP / 44-modulus exact blocks) and
  Door 2 (throughput).

### 2026-07-29 — WP8: strategy reflection (3 crazy / 3 small / 3 professor / path to 200k)
- Full memo: `phd/wp8_beyond_covering.md` (scripts in `phd/wp8/`). Four new
  hard results produced for it: (1) **rung ladder** E(Q) at 199d computed to
  Q=200,000 — E=37.69, e^E=2.4e16 ≈ 950 fleet-years, geometric rung spacing
  makes climbing cost ~4% more than jumping; (2) **packing probe** — c1 is a
  local optimum (ascent+kicks gain 0 at 122k, −0.8 nats at 200k); (3)
  **boost-vs-kills equilibrium** — cover size is set by dE=0, not by the lnB
  budget (adding r=461 nets +0.00 nats), explaining the flat frontier; (4)
  **SoK §7.4 LP certificate executed and VACUOUS** — fractional coverage is
  100.00% at both Q (kill-mass 1.86·π), so the entire game exponent is an
  integrality/rounding gap: naive 15.6% → greedy 7.56% → fractional 0;
  1% absolute ≈ 2.7 nats ≈ 15× compute. Headline recommendations: quantum
  crossover computed and negative (E*≈41–55 ≥ all reachable targets);
  GPU port of skip-frac (O1, ~2–3×); Erdős–Rankin/FGKMT rounding-gap
  programme (P2) as the central open problem; Operation Staircase ladder
  140k→150k→165k→175k→200k with priced closers for the final e^5.5 wall
  (volunteer swarm / ASIC / mathematics).

### 2026-07-29 — CAMPAIGN 3 STOPPED at user request (duplicative with another worker)
- Stopped at **380/17,200 slices (3.98e8 raw candidates, hit-mass λ=0.077,
  survival 0.926)** — a clean in-model early stop; per-slice p̂/Ê/hit% steady
  throughout (p̂≈0.054, Ê≈21.08, hit%≈27.6, ~16.3k k/s). Checkpoint is
  committed; `run_campaign3.py --chunk-seconds 560` resumes losslessly.
  If any session resumes or runs a parallel budget-game campaign, coordinate
  variant/k-space assignment first — independent workers should scan
  DISJOINT variants (they compose losslessly; duplicated k-ranges are pure
  waste). Wakeup chain deleted. Next: strategy reflection memo (wp8).

### 2026-07-28 — CAMPAIGN 3 LAUNCH: budget game, target g > 119,419 under 10^199
- Target switched by user directive: largest g(N) below 200 digits. Cover: the
  ratchet session's unstarted round-2 leftover c1 (Q=122,000, 88 classes,
  M=191d, |U|=867, boost 11.01), independently re-verified here (CRT ✓,
  uncovered ≡ residual ✓); a fresh greedy re-derivation at 199d matched its E
  to 3 decimals — the frontier is flat at this Q, no better cover exists in
  this family. **Any hit gives g(N) ≥ 122,011 > 119,419 with N < 10^199.**
- 40 residue-swap variants (shared M ⇒ shared sieve-inverse cache), kmax
  4.5e8 each under the 199d ceiling ⇒ 1.8e10 raw candidates in the pool.
- **Engine: the 179d winner's selective-testing lesson, adopted exactly.**
  New `--skip-frac f` in search.py tests only the emptiest (1−f) of each
  block in survivor-count order; the sacrificed hit mass is computed exactly
  from the survivor histogram (w = (1−p̂)^a) and logged per-slice as hit%.
  p̂ stays unbiased, so Ê model validation continues to work under skipping.
- Calibration at 199d (131k-k slices): baseline 1,772 k/s (p̂=0.063,
  alive/k=337, Ê=21.24±0.06 — 0.4 nats above theory's 20.83; watching).
  Selected **f=0.92, sieve-B=1e6: 14,957 raw k/s with 29.6% hit mass kept ⇒
  ~3× net discovery rate**. Two mechanisms: test cost per candidate is
  ≈1/p̂ Fermat tests regardless of survivor count (every k dies at its first
  PRP pass), so skipping full k's is nearly pure profit; and once tests stop
  dominating, the per-block sieve-residue cost (∝ π(B)·|U|) makes the small
  sieve win. Measured hit% matched the Gaussian survivor-histogram model
  to ±0.4pp at every f tried.
- Plan: e^21.25 ≈ 1.7e9 equivalent candidates ⇒ expected first hit ≈ 3.5–4.5
  wall-days at ~85% duty. Pool capacity 1.8e10 × 0.296 ⇒ E[hits] ≈ 3.1,
  P(≥1) ≈ 96%; if exhausted hitless, mint more residue-swap variants (free)
  and continue. On hit: stop_on_success, then the standard certification
  pipeline (verify_record.py witnesses + PARI ECPP + independent checker).
- Driver: phd/campaign3/run_campaign3.py — chunked (≤560s/chunk), slices of
  1.048e6 k checkpointed in git-tracked search.log (rollback-safe),
  idempotent resume, lazy round materialization, exit 3 on hit.

### 2026-07-28 — CAMPAIGN 2 STOPPED at user request (session close)
- Stopped at **2,132/2,400 batch-1 slices (5.6e8 elements), 0 hits** — survival
  probability ≈ 0.22 under the validated model; a second consecutive unlucky-but-
  in-model draw. Per-slice statistics matched the blueprint model throughout.
- Master meanwhile certified T(100,000) = 179 digits (g=101,149; ratchet round 3)
  and closed that session with a round-4 164-digit-modulus cover built but unstarted.
- IMPORTANT: campaign 2 is NOT obsoleted by the 179d record — every attainable hit
  is ≤ 175 digits (N ≤ N0 + 1.5e6·M ≈ 1.2e174), which would still beat 179 by 4+
  digits. It is stopped, not falsified. To resume: re-run
  `python3 goldbach/phd/campaign2/run_campaign2.py --chunk-seconds 590` in chunked
  turns — the committed search.log checkpoint makes resumption lossless (268 slices
  remain in batch 1; specs_reserve.json holds 712 more variants).

### 2026-07-28 — post-mortem: evaluation of the winning 179d record (t100k round 3)
- Verified PASS here (standalone verifier). Construction: Q=99,991 cover, 80 classes,
  M=169.4 digits, |U|=728, boost 10.79 — statistically the SAME frontier point as our
  168d blueprint (167.9d, 754 res). The covers are equivalent; the outcome difference
  was search strategy and engineering, not mathematics.
- **Depth vs breadth**: they scanned ONE progression to t=758,850,385 (~7.6e8
  elements; hit after surviving λ≈2.5, P≈8% — unlucky too, but a single deep
  progression has unbounded runway, so bad luck costs digits (N grows only
  logarithmically with t) instead of terminating the campaign. Our 400×1.5e6
  breadth-first design capped every hit at ≤175 digits (better record if hit) but
  hard-exhausted at 6.3e8 elements when the dice ran cold. Ratcheting
  (199→193→186→179, banking a certified record each round) dominates our
  grand-slam-per-campaign design under fixed compute.
- **Selective testing**: their tsearch2 ranks each window's t by surviving-complement
  count and Fermat-tests only the most promising fraction — sacrificing a slice of
  hit density for a multiple of throughput. We adopted the ordering but kept
  exhaustive testing (result-preserving); their result argues the aggressive skip
  is net-positive for time-to-record.
- Left for a future session: round-4 covers (cover_t100k_d ~172d target,
  cover_r200_c1 q>122k) with search positions in their logs; our campaign 2
  checkpoint (≤175d attainable, 268+4272 slices remaining) — the two approaches
  could be merged (their engine, our smaller-N spec set).

### 2026-07-28 — evaluation of the 150-digit GPU record (post-close addendum)
- **Verified PASS here**: verify_record.py re-derives all 9,977 witnesses; ECPP chain
  (17 steps) passes the PARI-independent checker with correct binding. Dual-validated.
- Construction: 68-modulus cover, M=140 digits, k=62,147,038,260 of a full
  [0, 7.5e10) scan at E=24.91 — hit at 63.8% depth, cumulative expectation ≈0.40,
  a central Poisson draw. No luck debt this time; they simply bought enough tickets.
- **The enabler was raw throughput, not mathematics**: CUDA engine (bit-matrix sieve +
  Montgomery CIOS Fermat waves, validated bit-for-bit vs Python) at 2.5–8.5M tests/s
  ≈ 430× our 4-core pipeline. ln(430) ≈ 6.1 — exactly the E-gap (24.9 vs ~19) between
  their reachable rung and ours. The record frontier is log(compute); covers and
  strategy were already saturated at our scale.
- Other adoptable practices: full-range scan then bank the MINIMAL hit (optimal for
  the smallest-N game, vs stop-on-first-hit); git-committed safe_k checkpoints
  surviving ~10 Colab culls (our slice-checkpoint pattern, independently converged);
  bit-for-bit GPU-vs-CPU validation as certification hygiene.
- Standing record board after reconciliation: T(100k)=150d/g=104,527 (GPU session),
  R: g=119,419 @199d (slop session), Height: g=1,157,341 @2,480d.

### 2026-07-28 — RETRACTION + corrected sub-100 analysis (see wp3_small_representative_memo.md v2)
- Literature search done: GSS FOCS'00 Thm 3 obtained and verified; the recalled
  radius sqrt(L·lnB·P) is CORRECT (numerically within 0.4% of the exact finite-ℓ
  optimum). The error was mine elsewhere: v1 compared the decoding radius at
  agreement size s against an existence bound maximised over a DIFFERENT s.
  Coupling them closes the window at every pool size. **"Open window" retracted.**
- Corrected costs: conventional sub-100 optimum is 44 moduli, M=10^79, |U|=1060,
  **E = 44.1 → 1.4e19 candidates ≈ 5e4 GPU-years** (not 3e8 — earlier extrapolation
  was too pessimistic). Sub-100 is expensive, not impossible: ~10^4 A100s for a
  few years, and 120–125 digits is ~10^2 GPU-years (fundable now).
- Oversized covers would make it trivial (420 moduli, |U|=165, **E = 10.2**, ~2.7e4
  candidates) but their small representatives have design-space density e^-2630.
  Finding one = modular subset-sum with choices at **density 1.026** — the hardest
  known regime (lattice attacks need <0.94; Wagner k-tree needs 2^938 here).
- Net: the record now rests on two well-posed open problems (CRT list-recovery
  beyond the Johnson radius; density-1 subset-sum with 2^82 planted solutions),
  and WP7 algebraic mechanisms become the highest-value untested route — they are
  the only family that escapes the ln r-nats-per-offset entropy accounting.

### 2026-07-28 — (superseded by the entry above) FORWARD MEMO: the road to sub-100 digits
Brute-force frontier (validated model, Q≈10^5, dE/dD ≈ −0.10..−0.19/digit):
| D | E | candidates e^E | A100-years @8.5M tests/s |
|---|---|---|---|
| 140 | ~28 | 1.6e12 | 0.01 |
| 130 | ~32 | 1.1e14 | 0.6 |
| 120 | ~38 | 2.7e16 | ~160 |
| 110 | ~44 | 1.8e19 | ~1e5 |
| 100 | ~52 | 4.7e22 | ~3e8 |
Verdict: the covering+scan paradigm ends near D≈125 even for org-scale fleets.
Sub-100 is NOT a compute problem — it needs e^~30 of algorithmic efficiency.

Existence is not the obstacle: conjecturally max g(N) ≈ (ln N)²·ln ln N ≈ 287,000
already at 10^100 (crosses 100,000 near 10^60), so sub-100 deserts exist in
abundance heuristically. The obstacle is purely constructive.

**The breakthrough required: decouple digits(N) from digits(M)** (proposal RQ2/WP3).
Entropy accounting says it is possible in principle: a cover drawing ~150 moduli
from the 668 primes < 5,000 carries ~809 bits of design freedom (subset ~509 +
residue choices ~300), while shrinking a 10^300-mass cover's least representative
into [0,10^100) needs only ~664 bits — a surplus of ~145 bits, i.e. ~2^145 valid
systems are expected to exist with N < 10^100 and residual load E ≈ 19–26
(a trivially searchable e^19–e^26 tail). Sub-100 T(100,000) is therefore an
ALGORITHMIC SEARCH problem: find one member of an exponentially large but
exponentially sparse family — formally, an inhomogeneous modular subset-sum /
CVP-with-choices instance at density ≈ 809/997 ≈ 0.81, uncomfortably close to but
not obviously outside the lattice-reducible regime (low-density subset-sum breaks
< 0.94 for point targets; here the target is a 2^332-wide window, which helps).

Forward programme (in priority order):
1. WP3 theory memo: exact reduction of small-representative-with-choices to
   modular subset-sum; identify which relaxations (fixed subset, ±1 residue swaps
   as shift vectors δ_r) make it a clean lattice problem.
2. E4 falsifiable toy (per proposal gate): Q=1,000, pool primes<300, target a
   representative ≥30 digits below M via BKZ/fplll on the swap-shift lattice.
   Predeclared success metric; negative scaling result is publishable (RQ7).
3. If signal: ladder 10^40 → 10^60 → 10^100 targets; the found system's E≈20
   means the *search* phase runs on CPU — only certification is unchanged.
4. In parallel (cheap wins, log-compute track): merge the GPU engine with
   full-range-minimal-hit ratcheting to grind 150 → ~135 digits; D=130 costs
   only ~0.6 A100-years — reachable by a patient Colab fleet.
5. Fallback (RQ7): if lattice attacks fail at density 0.81, prove a restricted
   no-go (e.g., equivalence to average-case-hard lattice problems) — the
   "conventional model cannot reach sub-100 without solving X" barrier theorem.

### 2026-07-28 — costed menu for follow-up work (validated: model reproduces the
150d record at "6 days on 2 Colab GPUs" — the actual campaign duration)
| rung | E | candidates | A100-yr | spot-$ | 2-GPU-Colab wall |
|---|---|---|---|---|---|
| 140d | 28.1 | 1.6e12 | 0.10 | ~$1k | ~2 months |
| 135d | 29.7 | 7.7e12 | 0.49 | ~$5k | ~10 months |
| 130d | 31.2 | 3.6e13 | 2.3 | ~$24k | — |
| 125d | 32.9 | 1.9e14 | 12 | ~$125k | — |
| 120d | 34.7 | 1.2e15 | 73 | ~$770k | — |
| 100d | 44.1 | 1.4e19 | 8.9e5 | ~$9.4B | — |
(Expected values; ×1.6 for 80% confidence. Throughput engineering shifts all rows.)
Toy CRT decoder: ~zero compute, 2–4 sessions; measures practical-vs-Johnson gap.
WP7 probes: ~zero compute, ~5 bounded probes × 1–2 sessions; only unbounded-upside route.

### 2026-07-28 — master reconciliation: FRONTIER.md + SoK §7 (PRs #27/#28)
- Merged parallel sessions' work. FRONTIER.md independently measures the sub-100
  wall: realizable E = 43.66 vs our 44.1 (agreement to 0.4 nats — two independent
  implementations of the costing now concur), and its set-valued-conditioning study
  (gain saturates at H^0.35, worth 1–2.8 nats) plus enumerability theorem ("classic
  cover = unique freely-enumerable design") confirm our density-1.026 subset-sum
  barrier from the constructive side.
- CORRECTION to our memo: sub-100 cost is ~9×10^5 GPU-years, not 5×10^4 — a units
  slip (divided by test rate instead of candidate rate). Costed-menu table row was
  already correct ($9.4B at D=100); memo prose fixed. FRONTIER's fleet band also
  supersedes our Colab wall-clock estimates (140d ≈ 13 days, not ~2 months).
- SoK §7 lists 10 open angles; #2 (prime-first construction), #9 (NP-hardness of
  the existence problem) and #10 (Grover: sub-100 at ~e^22 quantum queries) are
  genuinely complementary to our WP3/WP7 program and noted in the memo.

### 2026-07-28 — toy CRT decoder + WP7 probes both executed (post-merge follow-ups)
- **Toy CRT decoder (delegated; goldbach/phd/toy_crt/)**: Howgrave-Graham/GSS lattice
  decoder implemented (FLINT LLL, cross-validated pure-Python fallback), 61-position
  pool, B=10^12, A_J=87.38, 390 decodes. Verdict: practical LLL does NOT penetrate
  below the Johnson radius — the empirical threshold is A ≈ 1.028·A_J at ℓ=30,
  approaching A_J from above like 1+c/ℓ (ℓ=45 post-hoc: cutoff ≈1.02, one failure at
  1.0041·A_J). Below threshold the failure is TOTAL: reduced bases yield zero integer
  roots, and across all 390 decodes no non-planted solution was ever found despite
  ~10^7 valid alternatives existing at ρ=0.7 — solution abundance buys nothing.
  Empirics track finite-dimension determinant bounds to ~1%: the radius is tight in
  practice for this family, closing the last "maybe practical reduction beats the
  proof" hope from the WP3 memo.
- **WP7 probes (wp7_probes.md)**: all five terminated at predeclared gates — P1
  prime-powers strictly dominated (zero new kills); P2 value-set identities 26×
  dominated on average, 2–3× at the margin, with a provable Q^(1/2) offset ceiling;
  P3 exponent families reduce to covering (search-throughput note kept); P4 norm
  forms are covering in Galois clothing; P5 hidden bias empirically ≤0.1 nats from
  1.2e9 banked candidates. Output: 3 simultaneous conditions any real mechanism must
  meet (≫√Q offsets, o(ln r) entropy each, invisible to bulk density stats).
- **Programme position, final**: sub-100 T(100,000) has exactly one live route
  (Regime-I brute force, ~5×10^4 GPU-years) and three precisely-stated mathematical
  problems that would change that. RQ7 chapter complete; 140d rung (~$1k) remains
  the cheap constructive next step.

## Programme close-out summary (2026-07-22 → 2026-07-28)
- **O1 achieved**: both kickoff incumbents independently audited PASS (dual-
  implementation ECPP validation, adversarial mutation tests); two later external
  records re-verified with the standalone verifier.
- **O2 achieved**: density model E = |U|·boost/ln N validated to ~0.1 across
  3 covers and ~1.2e9 scanned progression elements — the model is exact; both
  campaign misses were 0.22-0.30-probability draws, not model error.
- **O3/WP2 progress**: cover frontier mapped at two Q values; AlphaEvolve move-set
  audited, reward-hacking failure diagnosed (unconstrained −D fitness), E-capped
  variant built and benchmarked (blueprint within ~1 digit of frontier at E≈20);
  PR #20 blueprint audited (valid cover, inflated claims, unusable shipped kmax)
  and re-parameterized into a viable campaign.
- **O4**: no new certified record from this session's own campaigns (two honest
  negative results, fully logged); parallel sessions ratcheted all three games.
- **O6 achieved**: restart-safe chunked-compute methodology (slice checkpoints in
  git, idempotent resume, ~85% duty cycle through ~15 container restarts/rollbacks),
  sieve-inverse cache + survivor-ordered testing adopted and verified
  result-preserving; all artifacts, logs, and decisions committed to this branch.

### 2026-07-28 — compute turns (campaign 2, final stretch before stop)

Superseded (this project's kickoff incumbents, all audited PASS 2026-07-22):
height 1,134,871 @ 2,692d; dual N₁₉₇ (197d, g=107,719).

Grand-slam target: N < N₁₉₇ **and** g(N) ≥ 1,134,877 — aspirational (O5);
RESULTS.md notes covering methods leave ≥20,000 residuals under a ≤192-digit
modulus (success density e^−400), so O5 requires mechanisms beyond static covers (WP7).

## Programme status

| WP | Scope | Status |
|---|---|---|
| WP1 (E1) | Independent audit of both incumbents + adversarial mutation tests | **done — PASS** |
| WP2/WP6 (E2/E8) | Cover frontier Q=107,720; density calibration on this box | **done** — see below |
| WP8 (E10) | Incremental record campaign: g > 107,719 with N < 10^199 AND N < N₁₉₇ | **launched** |
| Certification | PARI/GP 2.15.4 installed for ECPP; ecpp_check.py as independent verifier | ready |

## Log

### 2026-07-22 — kickoff
- Surveyed inherited machinery (PR #15/#16): cover.py, anneal.py, gen_variants.py,
  search.py, verify_record.py, mega_verify.py, ecpp_check.py, package_record.py; both
  record artifact directories present.
- Environment: 4 cores, Python 3.11.15, gmpy2 2.3.1, numpy 2.4.6, sympy 1.14.0,
  PARI/GP 2.15.4 (installed today; prior campaign certificates were produced with gp).
- Delegated WP1 audit and WP2/WP6 frontier+calibration to two parallel subagents.
- Campaign design decision: one E10 campaign with Q = 107,720 (covers every prime
  ≤ 107,719) so that ANY hit strictly beats R(10^199) = 107,719; hits are ranked by N so
  a sub-N₁₉₇ hit would also take T(100,000).

### 2026-07-22 — WP1 interim
- Part A (dual 197-digit record): PASS — byte-identical N reconstruction, all bounds,
  evidence regeneration matches committed witness counts, ECPP binding verified.
- Part C (adversarial audit): PASS — all three deliberate corruptions detected.
- Part B (megagap 88,239-witness replay + 3 ECPP chains) still running.

### 2026-07-22 — WP1 final verdict: PASS (O1 achieved)
Delegated audit report (full text in agent log; scripts in scratchpad wp1/):
- **Dual 197-digit record** — N reconstructed byte-identical from (N0, M, k=951,928);
  parity/size/bound checks pass; verify_record.py re-derives all 10,250 witnesses from
  scratch and they are IDENTICAL to committed evidence.json (parity 1, congruence 9,471,
  trial 378, strong-MR 400; offsets = π(107,718) confirmed independently); g prime,
  N−g BPSW-prime; ECPP chain (26 steps) validated by the PARI-independent
  ecpp_check.py incl. binding cert[0][0] = N−g.
- **Megagap 2,692-digit record** — MANIFEST.sha256 matches all 7 artifacts;
  verify_megagap.py end-to-end on a copy: all 813 cover congruences hold, all 88,239
  prime offsets < g re-proven non-summands (85,476 congruence + 895 trial + 1,867
  strong base-2 + parity), regenerated manifest byte-identical; local gap 8,970
  fully certified; all three ECPP chains (253/267/246 steps) validated by
  ecpp_check.py with correct bindings.
- **Adversarial audit** — digit flip in N, deleted offset witness, and swapped
  certificate candidate were each loudly DETECTED (plus a colluding-expected-value
  variant also detected via chain arithmetic).
- **PARI second opinion (lead)** — after installing PARI/GP 2.15.4,
  `primecertisvalid` = 1 for all four certificates: dual complement, megagap
  complement, and both local-gap endpoints. Every ECPP certificate in the corpus is
  now validated by two independent implementations.
- One environmental note: the audit agent's Part B originally ran without PARI
  present; its ecpp_check.py validation is a superset of the missing step, and the
  lead's PARI cross-check above closes the second-implementation gap.

### 2026-07-22 — WP2/WP6 results (delegated agent)
Cover frontier at Q = 107,720 (cover.py):

| e_target | congr | digits(M) | U | E | est digits(N) | k-cap N<N₁₉₇ |
|---|---|---|---|---|---|---|
| 17.0 | 92 | 202.6 | 746 | 17.00 | 210.0 | — (M too big) |
| 17.5 | 91 | 198.4 | 750 | 17.50 | 206.0 | 0 |
| 18.0 | 89 | 194.3 | 764 | 18.00 | 202.1 | 3.8e2 |
| 18.5 | 88 | 190.6 | 770 | 18.50 | 198.6 | **1.69e6** |

- Annealing (2 seeds, ~13 min each) gave zero improvement over greedy at e_cap 18.5 —
  the greedy cover is a robust local optimum of log M + E.
- **Chosen base spec `phd_q107720_e185`**: 88 congruences (moduli 3–643), M = 190.61
  digits, |U| = 770, boost 10.99, E = 18.50. With kmax = 1.5e6 < 1.69e6 (the N₁₉₇
  k-cap), *every* hit beats both bounded games simultaneously.
- 200 variants (gen_variants.py), E ∈ [18.500, 18.546], |U| ∈ [770, 772];
  total budget 3e8 progression elements.
- Calibration (E8): 2118 k/s on 4 procs (3.8× scaling), ~17 Fermat tests/k,
  measured Ê = 18.79 vs model 18.85 → model confirmed to ~0.1 in E. Two artifacts
  documented: kmax must be a block multiple for meaningful Ê printouts, and
  sub-block kmax collapses to one worker.
- Forecast at E_eff = 18.71: e^E ≈ 1.33e8 elements → ~17.5 h expected to first hit;
  P(hit ≤ 12h) ≈ 0.50, P(≤ 24h) ≈ 0.75, P(full 39h budget) ≈ 0.90.
  Expected hit near k ≈ 6.7e5 → N ≈ 2.8e196 < N₁₉₇ (dual-game record).

### 2026-07-22 — E10 campaign launched
- `search.py phd/campaign/specs_variants.json --procs 4 --out phd/campaign/found.jsonl`
  running in background; successes append to found.jsonl and are re-verified
  exhaustively (BPSW over all primes < Q) by verify_success before being reported.
- Monitoring via hourly check-ins; on first hit: stop, certify (evidence + PARI ECPP +
  independent ecpp_check.py + manifest), package record, push.

### 2026-07-22 — check-in #1 (10:22 UTC): infrastructure hardening after two container restarts
- Finding (operational, WP1-adjacent): the remote container is reclaimed during idle
  periods between session turns, killing detached (`nohup`/`setsid`) processes. Two
  restarts (~09:47, ~10:21 UTC) each wiped in-flight scanning with zero completed-spec
  checkpoints — coarse per-variant checkpointing (12 min/unit) loses too much.
- Fix, campaign driver v2: the 200×1.5e6-k budget is now cut into 1,200 interleaved
  slices of 262,144 k (~2 min each), checkpointed per slice in search.log and resumed
  idempotently; the search runs as a harness-tracked background task instead of a
  detached process, with a log monitor armed for hit/crash signatures.
- Bonus: interleaving slices round-robin across variants makes the global scan
  breadth-first in k, so the first hit found also tends to minimise k — and hence
  N ≈ k·M — which is exactly the threshold-game (smallest N) preference.
- Progress at check-in: 0 hits, 0 completed slices survive the restarts; effective
  campaign clock restarted 10:24 UTC. Forecast unchanged (~17.5 h expected to hit,
  subject to duty-cycle losses from restarts).

### 2026-07-22 — check-in #2 (11:25–12:30 UTC): driver v3, chunked foreground compute
- Harness-tracked background tasks ALSO die on idle reclaim (measured duty cycle ~12%
  in the 10:24–11:24 window: 3 slices/54 min). Driver v3 therefore runs the search as
  timeboxed foreground chunks inside scheduled session turns: ~9.7 min per chunk,
  whole slices only, exit code 3 signals a hit for immediate certification.
- This check-in turn ran 6 chunks: 26/1200 slices complete (rounds 0 of variants
  v0–v25), 0 hits, throughput steady at ~1950 k/s, Ê ≈ 18.8 nominal.
- Cadence going forward: wakeup turns of ~6–8 chunks (~1 h compute) chained ~1 min
  apart; expected first hit around slice ~510 (Poisson, e^18.7 elements).

### 2026-07-22 — compute turns #3–#4 (12:25–14:55 UTC)
- 88/1200 slices complete (2.3e7 progression elements), 0 hits; throughput steady
  ~1870 k/s per slice incl. init overhead; chunks reliably complete 4 slices each.
  Survival to this depth has Poisson probability e^(-88/510) ≈ 0.84 — unremarkable.

### 2026-07-23 — 28-hour suspension and restart (21:30 UTC)
- The session was suspended mid-compute-turn on 2026-07-22 ~17:20 UTC (user
  interruption followed by session idle) and resumed 2026-07-23 21:28 UTC. No compute
  advanced during the gap; checkpoint state (142/1200 slices, 0 hits) survived intact
  and the chain resumed losslessly — validation of the slice-checkpoint design.
- Wakeup chain re-armed; compute turns continue at ~32 slices/turn.
- Turn #7 (21:30–22:55 UTC): 178/1200 slices (4.7e7 elements), 0 hits; slices running
  slightly faster post-restart (~530 s/chunk). Survival probability ≈ 0.70 — on-model.

### 2026-07-24 — compute turns #8–#9 (23:00–01:30 UTC)
- 242/1200 slices (6.3e7 elements, 20.2% of budget), 0 hits; survival ≈ 0.62.
  Round 0 of all 200 variants nearly complete (k < 262,144 across the ensemble);
  first hit still expected near slice ~510. Two worker restarts absorbed losslessly.

### 2026-07-24 — compute turns #10–#12 (01:32–05:25 UTC)
- 338/1200 slices (8.9e7 elements, 28.2% of budget), 0 hits; survival ≈ 0.52.
  Steady state: 32 slices/turn, ~555 s/chunk, no restarts lost work.

### 2026-07-24 — compute turns #13–#15 (05:26–09:15 UTC)
- 434/1200 slices (1.14e8 elements, 36.2% of budget), 0 hits; survival ≈ 0.43.
  Passed the model median (~slice 354 for 50%); Ê per-slice remains 18.7–18.9,
  so the deficit is ordinary Poisson variance, not model error. Worker restarts
  continue to be absorbed at zero slice loss.

### 2026-07-26 — constrained_100 benchmarked (warm-start = 168d blueprint, 6-iter schedule)
- cap E≤17.5 (as shipped): D=193.2 (85 congr, M=185.6d, |U|=723) — its own frontier
  point does NOT beat the 186-digit incumbent; the E↔D trade is steeper than the
  harness authors assumed.
- cap E≤20.0 (edited): D=179.6 — WORSE than both the blueprint (176.5) and our
  greedy-proposal anneal (175.6) at equal wall-time. The random single-move
  Metropolis walk degrades the warm start at high temperature and cannot recover;
  deterministic best-residue proposals with Boltzmann selection dominate it here.
- Conclusion: harness design is exemplary (constraint in fitness AND internal
  objective, warm start, multi-metric); the evolved *search engine* is not
  competitive with our current optimizer under warm-start conditions. No adoption
  beyond the harness pattern.

### 2026-07-26 — AlphaEvolve deep-dive part 2 (uploaded programs review)
- `evolved_program_constrained_100`: well-posed harness — warm-start cover,
  Lagrangian E≤17.5 penalty in BOTH fitness and the block's internal objective,
  secondary metrics (E, |U|, m_digits); Metropolis engine with 100k single-moves.
  Targets a cheaper/weaker frontier point (E 17.5 → expected hit ~184–185d) than
  campaign 2 (E≈19.9 → ~176.5d); noted its deeper engine for the post-hit ratchet.
- `evolved_program_super_hard_100`: reward-hacked unconstrained fitness (the
  D≈50.7 collapse lineage), but transferable engineering: Gumbel weighted move
  sampling (add small moduli ∝ r^-0.8, drop large), REPLACE move with shared
  background counts, constant-folded 4/ln²10. Anti-lesson: mod_cache keyed by
  id(targets) is a stale-cache bug pattern; our caches key by value.
- Campaign 2: 269/2,400 slices (7.1e7 elements), 0 hits; survivor-ordered testing
  active since slice ~29.

### 2026-07-25 — AlphaEvolve cover-optimizer analysis (WP2 cross-pollination)
- Reviewed evolved_program.py and evolved_program_1.py (branch
  goldbach-alphaevolve-analysis-*): SA over ADD/DROP/SWAP moves with Boltzmann
  acceptance, minimizing self-consistent D. The shipped evaluate() harness confirms
  the fitness was unconstrained −D from an empty cover — with no E cap the block
  collapses to infeasible covers (D=50.7 at E=111 observed here). With an E≤20
  penalty added, it improves the 168d blueprint by 0.9 digits (D 176.5→175.6 at
  E=20.0): the blueprint is near-locally-optimal at this E budget.
- Adopted: move-set + penalized objective as campaign2/evolved_cover_step.py
  experiment; improved cover saved (evolved_best_cover.json) for a post-hit ratchet.
  Evolved hyperparameters noted for that round: temp schedule 0.8→0.02 geometric,
  candidate moduli to 8,000.
- Campaign 2 progress: 124/2,400 slices (3.3e7 elements), 0 hits — early days
  (expected hit ≈ slice 1,700).

### 2026-07-25 — CAMPAIGN 1 RETIRED, CAMPAIGN 2 LAUNCHED (~18:30 UTC)
- Master merge brought records from parallel sessions (PRs #18/#21): height
  g=1,157,341 @ 2,480d; **T(100,000) = 186 digits (g=109,357)**; **R = 119,419 @ 199d**
  plus a stdlib-only standalone verifier. Both bounded-game incumbents re-verified
  here (verifier PASS on t100k_r2 and r200_r1; SHA warning is the self-referential
  SHA256SUMS line only).
- Campaign 1 (g>107,719, N<N₁₉₇) thereby became strictly obsolete at 1,213/2,400
  slices, 0 hits (a P≈0.30 outcome). Retired. Scientific value kept: 3.18e8 elements
  of density-model validation (Ê−E within 0.1 throughout) and the restart-safe
  chunked-compute methodology.
- PR #20 (Jules) audit: 168-digit blueprint (Q=100,003, 79 congr, M=167.9d, 754
  residuals) is mathematically VALID (CRT + cover completeness verified here), but
  its claims were inflated: honest self-consistent E=19.84 (not 20.85), expected-hit
  N ≈ 176.5 digits (not 168), and its 1,111 shipped variants had ceiling_digits=170
  ⇒ only ~120 candidates/variant (~1.3e5 total vs ~4e8 needed) — unusable as shipped.
- **Campaign 2** (user-approved adoption of PR #20 code): variants re-parameterized
  to kmax=1.5e6, ceiling 185 (strictly below the 186d incumbent). Any hit ⇒ new
  T(100,000) record. search.py sieve-inverse cache adopted + driver batches 4 slices
  per process: measured **~2,900 k/s** (+47% vs campaign 1), Ê ≈ 20.2 at k≈0 (drifts
  down with log N; effective E ≈ 19.9). Batch 1 = 400 specs (2,400 slices, capacity
  6.3e8 elements, λ≈1.5); 712 variants in reserve. Expected ~1,700 slices ≈ 2.5 days
  of chunked compute to first hit.

### 2026-07-25 — original budget EXHAUSTED, extension launched (~16:45 UTC)
- Turns #31–#39 completed the original 1,200-slice budget: **3.15e8 progression
  elements scanned across 200 variants (all k < 1.5e6), zero successes.**
- Negative-result assessment: at Ê ≈ 18.7 the expected hit count for the full budget
  was λ ≈ 2.2, so P(no hit) ≈ 0.11 — an unlucky but statistically ordinary draw.
  Per-slice p̂ (0.0588–0.0592) and alive/k (318–319) matched the calibrated model
  throughout; no evidence of implementation error or model bias. This is exactly the
  E8-validated regime: the density model is confirmed, the dice were cold.
- Contingency executed: 200 additional residue-swap variants generated from the same
  base cover (deduplicated against the first 200 by cover; E ∈ [18.546, 18.661]),
  committed as specs_variants2.json; driver now reads both spec files (2,400-slice
  extended budget). Every hit still beats both bounded games (kmax unchanged).
- Forecast for the extension: λ ≈ 2.0 → P(hit) ≈ 0.86; expected ~12 further compute
  turns to first hit.

### 2026-07-25 — compute turns #28–#30 (01:14–04:45 UTC)
- 909/1200 slices (2.38e8 elements, 76% of budget), 0 hits; survival ≈ 0.17 — an
  unlucky but unexceptional draw (a 1-in-6 outcome). Per-slice p̂ and alive/k remain
  exactly on-model, ruling out an implementation regression. Contingency (200 extra
  residue-swap variants preserving the dual-game property) locked in for rc=2.

### 2026-07-25 — compute turns #25–#27 (20:58–01:10 UTC)
- 815/1200 slices (2.14e8 elements, 68% of budget), 0 hits; survival ≈ 0.21.
  Deeper than any depth the July campaign reached (1.4e8). Contingency planning
  for possible budget exhaustion: extend the same 200 variants to kmax ≈ 2.4e8/M-cap
  under ceiling 199 digits (keeps the R(10^199) game live; drops the automatic
  sub-N₁₉₇ guarantee), OR regenerate more residue-swap variants at kmax 1.5e6 to
  retain the dual-game property. Decision due at rc=2.

### 2026-07-24 — compute turns #22–#24 (17:07–20:55 UTC)
- 719/1200 slices (1.88e8 elements, 60% of budget), 0 hits; survival ≈ 0.24.
  All variants now past k = 786,432 (round 3); remaining budget is rounds 4–5.

### 2026-07-24 — compute turns #19–#21 (13:10–16:55 UTC)
- 626/1200 slices (1.64e8 elements, 52% of budget), 0 hits; survival ≈ 0.29.
  Steady 32 slices/turn; a worker restart mid-turn-21 cost only the in-flight slice.

### 2026-07-24 — compute turns #16–#18 (09:19–13:10 UTC)
- 529/1200 slices (1.39e8 elements, 44% of budget), 0 hits; survival ≈ 0.35.
  Now past the naive expected-hit depth (1.33e8 elements). By the memoryless
  property the expected additional wait is still ~510 slices of compute; the
  full-budget hit probability from here is 1−e^−1.32 ≈ 0.73. Decision standing:
  run the full 1,200-slice budget before any redesign (per §11.4 stopping rules).
