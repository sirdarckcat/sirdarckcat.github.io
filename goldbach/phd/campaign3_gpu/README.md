# campaign3 on a GPU

`campaign3` (`../campaign3/`) searches the budget game below 10^199 with the Q = 122,000 cover:
any hit gives g(N) ≥ 122,011 > 119,419. At this size nearly all the time goes to base-2
Fermat tests of ~661-bit complements N − q. This directory runs the same search with those
tests on a GPU.

| file | what it is |
|---|---|
| `gpu_fermat.py` | CuPy kernel: 2^(n−1) mod n for a batch of n = (N0 − q_i) + k·M, n built on the GPU from 21 32-bit limbs; Montgomery squaring (CIOS), the base 2 as doublings |
| `test_gpu_fermat.py` | the kernel against gmpy2 on campaign3 candidates, then its speed |
| `search_gpu3.py` | the production version (22 Nov 20:22Z): `search_gpu2.py`'s sieve, with A = (q − N0 mod s)·M^−1 mod s computed in the thread; search.py's selection (`--skip-frac`); the survivors of a whole batch of slices tested as one pool (all variants share M, so one tester holds every variant's N0 − q), at most `--dmax` complements of a member a launch. Campaign mode (`--campaign DIR`) drives itself; `--desc --klo` scans the top of k first |
| `check_v3.py` | `search_gpu3.py`'s sieve against `search.run_block`'s, its slice lines against `search_gpu2.py`'s at skip-frac 0 and 0.95 (also with small pools), and the Q = 3001 end-to-end check at skip-frac 0 and 0.5 |
| `prof_gpu2.py` | where `search_gpu2.py`'s time goes on a block, and what each skip fraction would give |
| `search_gpu2.py` | the previous version: the sieve on the GPU as well (one thread per residual and sieve prime, the same arithmetic as `search.run_block`), then the tests as in `search_gpu.py`, block by block |
| `search_gpu.py` | `search.py` with the tests on the GPU: the same sieve (worker processes, `search.init_spec`), then GPU launches that test the next D complements of every open member in `search.run_block`'s order, stopping a member at its first PRP; prints `search.py`'s per-slice line |
| `check_block.py` | `search_gpu.py` against `search.run_block` on whole blocks |
| `check_sieve.py` | `search_gpu2.py`'s GPU sieve against the CPU sieve (identical alive matrices), then its tests and prps against `search.run_block` |
| `check_small_gpu.py` | end to end where successes are frequent (Q = 3001): brute force with gmpy2, `search.run_block` and `search_gpu2.py` must find the same successes with the same tests and prps |
| `search.log` | the GPU run's slice log (seeded with the committed campaign3 lines of its variants) |
| `run_c3gpu.py` | driver: the variants in `my_specs.json`, k-major slices of 2^20 k, resumes from its own `search.log` |
| `variant_split.json` | which variants each runner scans (disjoint): the GPU, the six CPU machines, session 2ce9e63a's 4 cores, and the unassigned rest |
| `../campaign3/specs_variants_ext.json` | 20 more residue-swap variants, v39..v58 (22 Nov): `gen_variants.py base_spec.json out.json 60 150000000 199`, whose first 40 specs are field for field those of `specs_variants.json`; for each new one N0 ≡ a (mod r) for every cover pair, M = 2·∏r, and the residual list is exactly the primes 3 ≤ q < 122,000 that no pair covers (869 of them) |

Checks, on a Colab NVIDIA L4 (22 Nov):
- The kernel matches gmpy2 on 80,000 candidates of two variants (1,884 PRPs, 0 mismatches),
  k across the whole range including the smallest and largest. It runs 2.3·10^6 tests/s,
  against 111 µs a test for gmpy2 on one core of the same runtime (~260 cores).
- `search_gpu.py` equals `search.run_block` on 4 whole blocks: alive 50,897,453, tests 2,412,669,
  prps 131,072 on both (`BLOCKS MATCH`).
- `search_gpu2.py`'s GPU sieve gives the same alive matrix as the CPU sieve at k0 = 4,030,464
  and k0 = 299,991,040 (12,725,961 and 12,726,187 survivors), and the same tests and prps on the
  4 blocks above.
- End to end on the Q = 3001 self-test cover, k < 131,072: brute force finds 13 members whose 54
  residual complements are all composite (all pass `verify_success`); `search.run_block` and
  `search_gpu2.py` find the same 13, with 234,961 tests and 131,059 PRPs on both. The model's
  k·exp(−E^) says 28.3 there; that approximation is poor at p^ = 0.56 and much closer at
  campaign3's p^ = 0.054.
- With `search_gpu2.py`: ~66,800 k/s (16 s a slice of 2^20 k). The GPU is at about half its test
  rate; batching several blocks per launch should gain more.
- First production version (`search_gpu.py`): ~49,000 k/s with full hit mass (`--skip-frac 0`), E^ ≈ 21.0 as on the CPU.
  `campaign3` on 4 CPU cores ran 16,000 k/s keeping 29.6% of the hit mass (skip-frac 0.92),
  ~4,700 k/s in effect, so one L4 is ~10 such machines. The CPU sieve (11 workers) is now the
  limit; the GPU is at ~40% of its test rate.

Version 3 (22 Nov):
- `prof_gpu2.py` on the L4: a block of 32,768 k cost 1.8 ms of sieve, 37 ms of matrix preparation and
  478 ms of tests, and 41% of the tests computed came after a member's first PRP (each launch held
  one block's members, so it tested up to 262,144/members complements of each). At skip-frac 0.97
  that waste was 93%.
- `search_gpu3.py` pools the members of a batch of 32 slices: waste 5-9%.
- `check_v3.py` passes on the RTX PRO 6000 and on the L4: identical alive matrices, identical slice lines
  (tests, prp, p^, alive/k, E^, hit%, found) to `search_gpu2.py` at skip-frac 0 and 0.95, and at Q = 3001
  the same 13 successes as brute force, with the CPU's tests and PRPs at skip-frac 0 and 0.5.
- The kernel on the RTX PRO 6000 Blackwell (Colab G4): 80,000 candidates against gmpy2, 0 mismatches;
  8.9·10^6 tests/s (L4: 2.3·10^6).
- Speed on the G4, steady state, 16 slices a batch:

  | skip-frac | k/s | hit mass kept | k/s × hit mass |
  |---|---|---|---|
  | 0.90 | 3.4M | 31.9% | 1.07M |
  | 0.95 | 6.0M | 20.2% | 1.21M |
  | 0.97 | 9.3M | 14.2% | 1.32M |
  | 0.98 | 11.2M | 10.6% | 1.19M |

  For comparison, `search_gpu2.py` on the L4 at full mass did 63-67k.
- Production runs skip-frac 0.97 on both GPUs. The variants come from `gen_variants.py base_spec.json out.json 1000 150000000 199`;
  `../campaign3/variants1000_index.json` lists each variant's name, N0, |U| and E, and the full output
  has sha256 22e9b38769d96d92d1a331d81cc5c02331991e5025fcbcae3d5621b328fc5bbd. Its first 60 specs are
  those of `specs_variants.json` and `specs_variants_ext.json`.
- A second family, `r200b_q122k_w0..w4950` (`../campaign3/variants_w_index.json`): `gen_variants.variants(base, 6000,
  kmax=150000000, ceiling=199, pair_pool=120)`, minus every N0 of the first family, |U| ≤ 872 kept (sha256 of the
  full list 352fe5962138c19b125274661b507a2d8a24f7b4787f0c6be353c185ac7d5cb1).
- Three GPUs since 20:30Z: gold-gpu (L4), gold-g4 and gold-g4b (RTX PRO 6000 each), ~21M k/s together at hit% 14.2.
- A hit is certified by `certify_c3.sh found.jsonl specs.json`. It runs `package_record.py`
  (witnesses, PARI primecert), `ecpp_check.py`, slop's stdlib `verify_record.py` with the claims
  g > 119,419 and ≤ 199 digits, and direct gmpy2 and PARI checks. Rehearsed on the g = 119,419 record:
  every check passes except, by construction, the claim g > 119,419.
- Since 20:43-20:45Z all three GPUs scan the Lean session's 850-row cover for Q = 122,000. Its spec is
  `../campaign3/base_spec_k850.json`, = goldbach/phd/cap200/spec_q122000_k850.json at 3922f8e on ccr-36ca7b46-8twf14,
  with the same 88 moduli and M. Checked here: cover.crt reproduces N0 and M, and the residual list is exactly the 850
  uncovered primes. There are 3,000 residue-swap variants of it (`mint850.py`, |U| 850-862, each checked the same way;
  index `../campaign3/variants850_index.json`, full list sha256 4c22a9d6b6e09be4faece7b734c504e0d8a45569a6bc8e1c601623e2beed95e5).
  They run for N < 10^200 with k in [2^31, 2^32), top first (`run_v3_camp850.sh`), because the kernel takes k as u32.
  E^ measured there is ≈ 20.3-20.4, against ≈ 20.8-21.0 for the 867-row family.
- Kernel 3, `gpu_fermat3.py` (22 Nov 21:25Z, production on all GPUs, `--kernel 3`):
  - a dedicated squaring (the products x_i·x_j for i < j once, doubled, plus the diagonal: 231 products instead of 441);
  - lazy Montgomery reduction (no compare-and-subtract in the exponent loop: x < 4n before a squaring and < 2n after it, valid
    because 16n < R = 2^672 for n < 2^665, i.e. N < 10^200);
  - one REDC with a zero upper half at the end, then the comparison with 1.
  - `test_fermat3.py`: 0 mismatches against gmpy2 on 80,000 candidates (k = 0..3 and up to 2^32 − 1 included, Q = 122,000 and
    150,000 covers), and flags identical to `gpu_fermat.py`'s on 8.4M random candidates. `check_v3.py` with `SEARCH_GPU3_KERNEL=3`
    passes everything.
  - Speed: RTX PRO 6000 13.16M tests/s against 8.89M (1.48×); L4 3.97M against 2.23M (1.78×). A batch of 32 slices takes 2.8 s
    on the RTX PRO 6000, against 3.6 s before.
  - The Lean proof (goldbach/lean/GoldbachGaps/Gpu, ccr-36ca7b46-8twf14) covers the default kernel 2; kernel 3 rests on the tests above.
- CPU shares on the G4 hosts (22 Nov 22:40Z): the uarch session's `sieve200/search_c.py` (C sieve and AVX-512 IFMA Fermat tests)
  under `../campaign3/run_campaign3_hi.py`, on Q = 150,000 vectors at k ≥ 2^32 (which the GPU kernels cannot reach).
  - `cpu_share.sh` sets it up after `test_dropin.py` (ALL IDENTICAL) and `test_fm13.py` (ALL OK) pass on each host.
  - `cpu_share4.sh` runs 4 drivers × 11 processes on quarters of the vectors, because the engine makes a process pool per slice.
  - Per host: 1.8M members/s at hit% 30.9, i.e. 0.56M full-weight. The GPU batches still take 1.1 s.
- `search_gpu5.py` (22 Nov 22:17-22:33Z, production on all five GPUs): the uarch session's all-GPU sieve (branch ccr-b8c25887-i6tn9f at
  6e01704, goldbach/sieve200/cuda: `GpuFeeder`). It has one CTA per row with the window's bit map in shared memory, Barrett
  reduction, a bit-sliced counter, selection by histogram (exactly np.argsort(counts, kind="stable")[:keep]), and the kept rows
  read straight from the bit matrix. Windows are 2^19 members, L = 2^15.
  - Its own test (`test_gpu_sieve.py`): identical to the CPU feeder on 3 windows on each of the RTX PRO 6000, the A100 and the L4.
    `check_v5.sh`: slice lines identical to search_gpu3.py's on the 12 production slices (f = 0.97 and f = 0), and on 4 more on
    the A100 and the L4 with kernel 3.
  - Sieve + count + select + rows per member: RTX PRO 6000 2.7 ns (372M members/s), A100 16.6 ns, L4 24.4 ns. The old GPU
    sieve was ~32 ns (RTX PRO 6000) to ~140 ns (L4).
  - Production batch of 32 slices (33.5M members) at f = 0.97:

    | GPU | before | search_gpu5.py | full-weight members/s |
    |---|---|---|---|
    | RTX PRO 6000, kernel 28 | 1.1 s (CPU feeder) | 1.1 s, host CPUs free | ~4.8-5.0M |
    | A100, kernel 3 | 6.5 s | 3.5 s | 1.56M |
    | L4, kernel 3 | 9.6 s | 6.1 s | 0.86M |

  - f = 0.99 on an RTX PRO 6000: 0.5 s a batch but less than half the hit mass. That gives 1.56e-5 against 1.50e-5 expected hits
    a second, i.e. +4%, for 2.2x the k-range, so production stays at f = 0.97 while vectors are the constraint.
- `search_gpu4.py` (22 Nov 21:57Z, production on the three RTX PRO 6000s): the sieve, counts and selection run on the host's
  CPUs with the uarch session's `sieve200.Feeder` (branch ccr-b8c25887-i6tn9f at 554e85c, goldbach/sieve200; C with AVX-512,
  46 threads on the G4's 48 Zen 5 vCPUs), and the GPU only tests. The CPU prepares batch b+1 while the GPU tests batch b.
  - `check_v4.sh`: slice lines identical to search_gpu3.py's (kernel 28) on the 12 production slices of `check_k28.sh`, at
    f = 0.97 and f = 0.
  - Feeder alone on a G4 host (1,011-row cover, B = 1e6): 0.59 µs a member on one thread at f = 0.97; 27M members/s on
    24 threads; 35-42M on 48.
  - Production: a batch of 32 slices takes 1.1 s, with the CPU side 1.03-1.13 s and the GPU side 1.09-1.14 s, i.e. ~30M members/s
    per G4. That is against 2.2 s with search_gpu3.py and kernel 28, and 3.6 s at 21:00Z. The survivor rows travel to the GPU as
    u16, per window, and are widened and offset there.
- Q = 150,000 supply: 4,462 residue-swap variants of the research vectors pt_q150k_v0..v3 (`gen_variants.variants(base, 1500, pair_pool=80)` per base, |U| ≤ 1,097 kept; |U| 1,094-1,097 against the best 1,093). Each was checked independently
  (congruences, M, residual list, ceiling 200), and N0 is distinct from the research 128. Index:
  `../campaign3/variants_q150k_minted_index.json`; full list sha256 b864f9f8915b0fe196282d5bb617b96c3a4ad34a885762eee6e866fb99d436ac.
- More Q = 150,000 supply (23 Nov 00:06Z): 10,134 residue-swap variants pt_q150k_t0..t10133 of the 1,092-row research vectors
  pt_q150k_b_v0..v7 (same call, |U| ≤ 1,096 kept; |U| 1,092-1,096, mean 1,094.0). `check_specs.py` (rows covered exactly when
  gcd(N0 − q, M) > 1, from the integers) passes on all of them, and every N0 is distinct from the 4,974 earlier Q = 140,000 and
  150,000 vectors. Index: `../campaign3/variants_q150k_minted_t_index.json`; full list sha256
  ebdb6d0f04bcbf38fb394d15e9f027b8234f1989796f729fbe25f837dca90d8a.
  - gold-g4c: t0..t1999 since 00:09Z, after its share of the research 128 ran out at 00:08Z.
  - gold-a100: t2000..t2699 when it finishes the research 128 in [2^30, 2^31) (`chain_next.sh`).
  - gold-l4b, a second L4 (23 Nov 00:45Z): t2700..t3099 (`run_l4b.sh` checks the kernels against gmpy2 and kernel 3 against kernel
    28 on 12 production slices on that GPU first).
  - gold-l4c, a third L4 (00:48Z, same checks): t3100..t3499.
  - t3500..t10133 are in reserve.
- The research generator (`gen_vectors.sh` on ccr-d4a17dd0-7uu03r at 5bc33a1, with every vector above added to its ledger first)
  gives 1,092-row vectors, 2-4 rows better than the minted ones (≈ +5-10% hit rate). Batch g8ffe1 (23 Nov 01:00Z): 400 at
  1,092 rows, checked again here with `check_specs.py` and against the 15,108 earlier vectors. Index:
  `../campaign3/variants_q150k_g8ffe1_index.json`; sha256 54d87d6c751da532f7d3c35efebde1f5dbd9ac7f86ef697f1cbc0bc55d14e755.
  - k ≥ 2^32 (CPU shares): v0..v63 the lead's container (`../campaign3/q150k_cpu/specs_lead.json`), v64..v127 the helper
    session (`specs_helper.json`), v128..v191 this session's container.
  - k in [2^30, 2^32): v0..v399 for the L4 that was to replace the A100. The A100 was stopped at 01:40Z, after its share of the
    research 128 and the uarch measurements (`uarch_measure/measure_a100_sections1-6.txt`). Colab then refused an L4 and a G4
    ("precondition failed") and had no A100 ("Service Unavailable"). It granted a T4 (gold-xt4, 1.15 units an hour), which took
    v0..v399 at 02:03Z in deep mode, after test28_prod (s1rw 2.5M tests/s), check_v5w and check_deep. With two slices a batch,
    deep mode ran out of the T4's 15 GB after three batches. With one slice a batch (BATCH=1) it holds steady at 12.7 GB:
    10.5 s per 2^25 members, 2.45e-5 expected hits.
    That is ≈0.76M full-weight members/s per unit-hour, as the L4 (0.79M) and RTX PRO 6000 (0.74M) with deep.
- Cost per GPU type, from the Colab usage rate as runtimes were added (22 Nov): RTX PRO 6000 10.05 compute units an hour, A100
  6.73, L4 1.94, CPU runtime 0.26. Full-weight members/s per unit an hour: L4 0.57M, RTX PRO 6000 0.54M, A100 0.27M. A fourth
  RTX PRO 6000 is refused ("precondition failed"); a second and a third L4 were granted, a fourth refused (seven GPUs in all).
- Kernel 28 (22 Nov 21:44Z, production on the three RTX PRO 6000s, `--kernel 28`): the uarch session's `gpu_fermat28.py`
  (branch ccr-b8c25887-i6tn9f at 554e85c, goldbach/fermat661/cuda; files used in `fermat28_used.sha256`). It has 24 limbs of 28 bits,
  so each product is one IMAD.WIDE with no carry chain; a dedicated, fully unrolled squaring; lazy reduction; and the start value
  2^(672−c) instead of 672 doublings. The variant used is "s1 asm".
  - `test28_prod.py` on production-range candidates (k in [2^30, 2^32), n ≥ 2^662): 0 mismatches against gmpy2 on 40,000 for every
    variant, flags identical to fermat2's on 2M.
  - Speed (best variant):

    | GPU | fermat2 | fermat3 | fermat28 |
    |---|---|---|---|
    | RTX PRO 6000 | 8.86M tests/s | 13.08M | 22.86M |
    | A100 | 4.03M | 6.94M | 6.95M |
    | L4 | 2.18M | 4.07M | 4.02M |

    So the A100 and the L4 stay on kernel 3.
  - `check_k28.sh`: search_gpu3.py with kernels 3 and 28 on 12 production slices below 2^30 gives identical slice lines at f = 0.97
    and at f = 0.
  - Production batch of 32 slices on an RTX PRO 6000: 2.2 s.
  - search_gpu3.py asserts 2^642 ≤ n < 2^668 for kernel 28 (it flags 2 outside), and counts only flag == 1 as a PRP.
- Kernel 28 step files (22 Nov 23:34-23:52Z, production on all five GPUs): the uarch session's a641ecc (same directory; files used in
  `fermat28_used_a641ecc.sha256`), chosen with `--k28-step` / `--k28-asm` (env `K28_STEP`, `K28_ASM`, `FERMAT28_DIR`).
  - The RTX PRO 6000s run `fermat28_step_s1r.cuh` with PTX mad.wide.
  - The A100 and the L4 run `fermat28_step_s1rw.cuh` in plain C. The "w" files drop the dead IADD3s that sm_80/89 executed.
  - `test28_prod.py ... w` (production range, campaign paused): 0 mismatches against gmpy2 on 40,000 for every variant, and flags
    identical to fermat2's on 2M. Tests/s at 128 threads, best single launch:

    | GPU | fermat3 | s1 asm | s1 plain | s1 plain+w | s2 plain+w | s1r plain+w | s1r asm |
    |---|---|---|---|---|---|---|---|
    | RTX PRO 6000 | 13.08M | 22.85M | 22.23M | 22.27M | 22.58M | 22.74M | **23.39M** |
    | A100 | 6.94M | 6.60M | 6.95M | 7.55M | 7.51M | **7.63M** | 6.95M |
    | L4 | 3.92M | 3.74M | 4.00M | 4.57M | 4.54M | **4.62M** | 3.89M |

  - The L4 runs at its 72 W cap in production, at 1,440-1,600 MHz of 2,040. `ab_sustained.py` (interleaved rounds of 6 × 2^20
    tests after a 15 s warm-up) measures it there: fermat3 3.92M tests/s (54.6k tests/J), s1rw 4.59M (63.8k), s1w 4.53M,
    s1 plain 3.98M, s1r asm 3.87M.
  - `check_v5w.sh`: on each of the five GPUs, the production configuration and the new step file give identical slice lines on the
    12 production slices (f = 0.97 and f = 0).
  - Production, steady state, batches of 64 slices:

    | GPU | before | after |
    |---|---|---|
    | RTX PRO 6000 (×3) | 31.1-31.8M members/s | 31.9-32.7M (+2.5-3.1%) |
    | A100 | 9.77M | 11.09M (+13.5%) |
    | L4 | 11.4 s a batch | 10.0 s (+14%) |

  - Restarts: compare steady states, not the first batches. After a restart, the first pass over the variants carries the
    per-variant setup. On the L4 (1,462 variants, 23 batches a round) that is ~2 s a batch: 13.4 s against 11.4 s on kernel 3.
- Sieve bound B (23 Nov 00:20-00:45Z; production stays at B = 10^6). A deeper bound makes the f = 0.97 selection sharper and
  leaves fewer tests per kept member.
  - `deep_sieve_bound.py` (uarch `Sieve200`, CPU) gives each member's alive count at several B. The model: an alive row is prime
    with p_B, and Σ_k c_B p_B is independent of B. That gives p_B = 0.0536, 0.0625, 0.0715, 0.0804 at 10^6 … 10^9; Mertens gives
    0.0801 at 10^9. Each member's weight is (1 − p_Bmax)^c_Bmax.
  - At f = 0.97, on 4M members of each of two vectors (`sieve_bound/cpu_*.txt`):

    | selection bound | hit mass kept | tests per kept member | hit mass per test |
    |---|---|---|---|
    | 10^6 (production) | 15.9-16.0% | 18.66 | ×1 |
    | 2·10^6 | 17.0% | 17.77 | ×1.12 |
    | 4·10^6 | 18.0% | 16.96 | ×1.24 |
    | 10^7 | 19.3% | 15.99 | ×1.41 |
    | 10^8 | 22.65% | 13.99 | ×1.89-1.90 |
    | 10^9 | 25.95% | 12.44 | ×2.45 |

    That is ≈ (ln B / ln 10^6)^2.2: tests fall as 1 / ln B and kept mass rises as (ln B)^1.2.
  - On the GPU (`bench_sieveb.sh`, the same 64 production-range slices at each B on an RTX PRO 6000,
    `sieve_bound/gpu_rtxpro6000_64slices.txt`), the logged expected hits rise ×1.041, ×1.085, ×1.206 and ×1.254 at
    2·10^6, 4·10^6, 10^7 and 2·10^7. Tests fall ×0.857 at 10^7, which is the model's figure.
  - The batch time rises 2.70 → 3.50, 4.60, 7.60 and 14.7 s, so expected hits/s fall to ×0.80, ×0.64, ×0.43 and ×0.23.
  - The cause is that `GpuFeeder` does one step per (prime, row, window) even when s > K and the pair hits at most once:
    ≈0.08 ns a pair, linear in π(B).
  - Break-even on a G4 batch of 64 slices (2.03 s, ~1.6 s of it Fermat): the primes above 10^6 must cost under ~0.65 s for
    B = 10^7 and under ~1.25 s for B = 10^8. At 10^8 and K = 2^19 that is 7.9·10^11 pair-steps a batch, so a
    large-prime path near 0.5 ps a pair (one Shoup modmul, a shift by k_start mod s, a compare) would give ~+40%. With
    K = 2^21, near +65%.
  - The CPU shares (search_c.py, f = 0.92) stay at B = 10^6 too. At f = 0.92 the model gives kept mass ×1.15 / ×1.23 / ×1.30
    and tests ×0.86 / ×0.80 / ×0.75 at 10^7 / 3·10^7 / 10^8. The engine on 4 slices with 4 processes
    (`sieve_bound/cpu_engine_search_c_4slices.txt`) takes 26.3 s at 10^6, 34.6 s at 10^7 (window 2^20), 46.4 s at 3·10^7 and
    110.6 s at 10^8, so even 10^7 is a net ×0.87.
- Deep sieve, B = 10^8 (23 Nov 01:30Z on, production on the three RTX PRO 6000s). This is the uarch session's bucketed
  large-prime stage: each (row, prime) pair is visited once per 2^25-member window, and marks are binned by (row, 2^19-bit tile).
  It runs through `search_gpu5.py --deep 1` (`search_gpu5_deep.patch`, `deep_feeder.py`, `gbatch.py`, `gbig.py` on
  ccr-b8c25887-i6tn9f at eecb551, plus two one-line fixes in `uarch_measure/fixes_8ffe.patch`).
  - `uarch_measure/measure_*.txt` (`measure_all.sh` on an RTX PRO 6000 and an L4): the large-prime stage costs 0.030 ns a
    mark on the RTX PRO 6000 and 0.10 ns on the L4. A whole 2^25 window at B = 10^8 takes 11.5 / 52.6 ns a member, and
    `--check` shows it identical to the CPU feeder.
  - `check_deep.sh` on an RTX PRO 6000 (2 variants × 2^25 members below 2^30), `uarch_measure/deepcheck_rtxpro6000.txt`:
    - the new sieve tree gives slice lines identical to the production sieve;
    - `--deep` at B = 10^6 gives tests and PRPs identical to the normal path;
    - at B = 10^8, expected hits ×1.434 and tests ×0.750.
  - Steady batches of 2^26 members (`uarch_measure/deeptime_rtxpro6000.txt`): production 2.00 s and 3.23e-5 expected hits.
    `--deep` at 10^6 takes 1.90 s. At 10^8 it takes 2.10 s for 4.46e-5 expected hits: ×1.32 hits/s.
  - `switch_deep.sh` restarts a running campaign in deep mode exactly at a 2^25 boundary: it waits until every variant has
    the row k0 = m·2^25 in search.log, then sets KMAX = k0. Nothing is skipped, and nothing is rescanned beyond the batches
    in flight. `run_v5_campQ.sh` passes `DEEP_ARGS`
    (`--deep 1 --klog 25 --slice 33554432 --sieve-b 100000000 --p-est 0.0715`, BATCH=2).
- Near-misses (`search_gpu5.py --near-miss G`, env `NEAR_MISS`; 23 Nov 02:40Z, verified; live from the move to Q = 160,000).
  - Why: each tested member is tested row by row with q ascending until its first probable prime. Every earlier row is
    composite (by the cover's class, by the sieve, or by a failed Fermat test), so that first-PRP row is g(N) whatever the
    design Q. A member that dies at a row above the record in hand is a new record.
  - What changed: `run_pool` now records each member's first-PRP row. It also checks explicitly that every member's
    survivor rows are strictly ascending, and the tester checks that each residual list is ascending. After a batch, a
    member with first-PRP q ≥ G is verified on the CPU (`verify_near_miss`: every prime p < q gives a composite N − p,
    N − q is a probable prime) and written to found.jsonl with `near_miss: true`. It counts toward found= and the tally's
    found only as a near-miss. Which members are tested, and how, is unchanged.
  - `check_nearmiss.sh` on an RTX PRO 6000 (`nearmiss_check/`). The known case is 146,191's member
    (r200_q140k_c_v77, k = 3,101,585,871) with its vector's residual list taken to Q = 150,000 (1,120 rows).
    - The normal path with all members tested reports it as a near-miss at g = 146,191, and so does the deep path at
      f = 0.97.
    - Slice lines are identical with reporting on and off, on that slice and on two deep production slices.
    - The final driver, with near-misses and the uarch session's in-place row offset that frees ~4.5 GB a deep window, gives
      lines identical to the earlier driver.
  - Rows above 1,100 need `--deep-max-rows` (1,200 for Q = 160,000).
  - Cost: the first version checked the order over the whole survivor array of a pool (~7·10^8 rows) and cost 0.5 s a
    batch (2.60 against 2.10 s). The check now runs on the rows actually tested, as they are tested: each row above the
    member's previous one, about 3·10^7 a batch, sharing the kernel-28 range check's sync.
- Staged large-prime kernel and the overlap (23 Nov 03:00Z, uarch tree b344e85; `uarch_measure/overlap_trial_rtxpro6000.txt`,
  `driver_tree_staged_ab_rtxpro6000.txt`). Steady batches of 2 × 2^25 members on an RTX PRO 6000, tests and PRPs identical
  in every case:
  - production driver f43e7f9 with the old tree: 2.10 s;
  - this driver with the new tree: 2.00 s;
  - plus `DEEP_STAGED=1` (marks sorted by bin in shared memory, written as whole lines): 1.70 s, ×1.24.
  - `--overlap 1` (the next window's sieve on a second stream) gave no gain: 2.50 → 2.50 s on the slow-check driver.
    `--fermat-cta-sm 3/4` made it worse (2.60-2.85 s), and so did 128-thread tile CTAs.
  - In production on the three RTX PRO 6000s since 03:07Z (`deploy_staged.py`): 1.7-1.8 s a batch, from 2.1 s.
- Q = 170,000 (23 Nov 03:55-04:04Z on all seven GPUs; the lead's decision, from the research session's table with near-misses
  counted: expected final record 172,300 against 171,200 at 160,000, flat optimum 167,500-175,000).
  - Vectors: 9,000 from the research generator (`gen_vectors.sh 170000 1263 9000`, starting covers of 07ff825; 71 at 1,262
    rows, 8,929 at 1,263), checked here with `check_specs.py`. Index: `../campaign3/variants_q170k_index.json`. Split by GPU
    speed, about 2.4 days of work; more at cap 1,264 to follow. The 12,827 Q = 160,000 vectors stay staged, unused.
  - Each GPU switched with `switch170.py`: `--deep-max-rows 1300`, the staged kernel, B = 10^8, NEAR_MISS = 157,837. The
    script waits for the old campaign process to exit before it starts the new one.
  - The lead's four conditions:
    - (1) the vectors above, checked;
    - (2) 1,300 matrix rows;
    - (3) memory at 1,262-1,263 rows: L4 16-20 GB of 23 GB, T4 13.2 of 15.4 GB (`revert150.py` returns a card to
      Q = 150,000 if it runs short);
    - (4) a Q = 170,000 check slice with identical lines with near-misses on and off (`nearmiss_check/c170check_rtxpro6000.txt`).
  - Batches: RTX PRO 6000 1.8 s, L4 9.9-10.1 s, T4 10.0-10.2 s a slice: +3-7% over Q = 150,000 from the extra rows. Alive
    rows 424 a member, E^ 30.2.
  - Sieve bound with the staged kernel (`uarch_measure/bsweep_staged_rtxpro6000.txt`): 10^8 1.70 s, 2.623e-5 expected hits
    a second; 2^28 1.90 s, 2.543e-5; 10^9 2.80 s, 1.817e-5. So B stays at 10^8.
- Pool split and round profile (23 Nov 04:15Z, the uarch session's `search_gpu5_roundprof.patch` and `search_gpu5_poolsplit.patch`).
  - `--profile-pool 1` on an RTX PRO 6000 at Q = 170,000 (`uarch_measure/profile_pool_rtxpro6000.txt`): 44-45 Fermat
    rounds a pool take 1.27 s on the GPU, and the GPU idles 0.08-0.10 s between rounds, ≈5% of a 1.8 s batch.
  - `--pool-threads 2` tests a pool as two halves (split at a member boundary) in two threads on two streams.
    `uarch_measure/poolsplit_check_rtxpro6000.txt`: slice lines identical to the production driver, steady batches 1.80 →
    1.70 s, and the 146,191 near-miss is still reported.
  - In production on the three RTX PRO 6000s since 04:16Z (`restart_ps.py`). Not on the L4s or the T4, whose ~10 s batches
    leave proportionally less idle time.
- Rows a CTA of the staged large-prime kernel (the uarch session's section H, `uarch_measure/secth_rcta_rtxpro6000.txt`).
  - At B = 10^8, on a 2^25 window of a Q = 170,000 vector, the sieve column measured rcta 2 193.2 ms, rcta 4 201.9 ms, rcta 8
    (512 generate threads) 186.6 ms, and rcta 2 again 193.2 ms. Kept members and survivor rows were the same in all four
    runs.
  - rcta 8 saves 6.6 ms a window, about 0.75% of a batch, which is under the 20 ms bar for a production change. DEEP_RCTA
    stays at 2.
- Sieve under the Fermat kernel (23 Nov 08:03-08:11Z, gold-g4b).
  - Hardware: the uarch session's `bench_overlap.py` (`uarch_measure/overlap_probe_rtxpro6000.txt`).
    - Its sieve windows ran on a highest-priority stream beside one Fermat launch of 2^26 tests.
    - The Fermat kernel ran ×1.10 slower and the sieve ×2.89 slower, which projects a production batch of 1.46 s against
      1.76 s (×1.20). The default carve-out did as well as carve-out 100.
    - The 80-register Fermat kernel was worse. Without the stream priority the sieve got no SM time.
  - Driver (`uarch_measure/overlap_driver_rtxpro6000.txt`).
    - The 03:10Z `--overlap` trial could not have overlapped anything. With `--pool 2097152`, a batch's two windows
      (≈1.008M members each) fill the pool only once, at the final flush, so every sieve ran before any Fermat round.
    - With `--pool 1000000` (one flush a window) the steady batches were:

      | sieve thread | one vector | a new vector every window |
      |---|---|---|
      | off | 1.90 s | 1.90 s |
      | on | 1.84 s | 1.88 s |

    - Production does 1.75-1.76 s, and the smaller pool alone costs +0.14 s.
    - The hardware probe implies about 0.16 s from hiding the second window's sieve, so something on the host side keeps
      the thread from sieving under the Fermat rounds.
    - Slice lines were identical in every run. Production is unchanged.
- Cross-batch sieve pipeline (23 Nov 08:40Z on the RTX PRO 6000s; the uarch session's `search_gpu5_xbatch2.patch` and
  `overlap.Pipeline`, its tree a752ea3).
  - One sieve thread for the whole campaign plans the next batch itself. It sieves that batch's two windows on the
    highest-priority stream under the current batch's one flush (`--pipeline 1 --pipeline-depth 2`, production's pool of
    2^21). `--trace-pipeline 1` prints, per batch, how long the consumer waited for the sieve and how long the sieve thread
    was busy and idle.
  - The patched driver keeps the old behaviour by default. It is now `search_gpu5.py` here and on the RTX cards, with the old
    file kept as `search_gpu5_prev.py` on each card. The L4s and the T4 still run the old file.
  - Measured in campaign mode (`uarch_measure/pipeline_v1_rtxpro6000.txt`, `pipeline_v2_rtxpro6000.txt`; batch ends
    stamped every 20 ms):

    | configuration | batch |
    |---|---|
    | production | 1.744-1.752 s |
    | v1, a flush per window, two pool threads | 1.647 s (batches 3-5 ≈ 1.69 s) |
    | v2, sync-free sieve windows | 1.73-1.76 s |
    | v2, per-group overflow check (`GBATCH_DEFER_CHECK=0`) | 1.55-1.60 s |

    - The sync-free sieve runs at full speed (0.44 s a batch) and the Fermat rounds wait for it.
    - The per-group check's host round trips let the sieve trickle beside the Fermat rounds (≈1 s busy a batch), and the
      consumer never waits.
  - Slice lines were identical to production in every run. The 72 near-misses at a threshold of 63,097 were identical
    with and without the pipeline. Peak memory is +1.6 GB.
  - Production since 08:40-08:42Z (`deploy_pl.py`):
    - tree `/content/ua_v2` (a752ea3 over the previous tree), with `GBATCH_DEFER_CHECK=0`;
    - deep arguments plus `--pipeline 1 --pipeline-depth 2 --trace-pipeline 1`;
    - gold-g4b's first 71 batches took 1.594 s each, against 1.76 s before.
  - Burst shaping (09:03-09:21Z, the uarch session's `plt3.sh`, `plt4.sh` and this session's `plt5.sh`; tree 4f8edff).
    Results are in `uarch_measure/plt3_burst_rtxpro6000.txt`, `plt4_rtxpro6000.txt` and `plt5_cpu_rtxpro6000.txt`.
    - A 0.5 ms bubble after each checked row group (`GBATCH_GROUP_DELAY_US=500`) with 512-thread tile CTAs
      (`--deep-tile-threads 512`, honoured from 4f8edff on) gives 1.526 and 1.529 s against 1.574 and 1.580 s, -3%. Slice
      lines are identical.
    - Pausing the host's CPU share (48 niced `search_c.py` processes) changes nothing.
    - What costs the batch is GPU sharing: beside the sieve, the Fermat kernels of a half-pool take 0.70-0.76 s on the GPU
      instead of 0.65-0.69 s.
    - In production on the three RTX PRO 6000s since 09:20-09:21Z (`deploy_a2.py`):
      - tree `/content/ua_v3`;
      - driver = the pipeline driver plus the uarch session's inert `search_gpu5_prio.patch` (it is `search_gpu5.py` here);
      - `GBATCH_GROUP_DELAY_US=500` and `--deep-tile-threads 512`.
  - Not on the L4s or the T4.
    - On gold-l4b the pipeline ran 10.000 s a batch against 10.054 s before (08:44-08:48Z), so the card went back to its
      previous configuration.
    - The fleet-mode probe on that L4 (`uarch_measure/overlap_probe_l4.txt`): beside the sieve the Fermat kernel runs
      ×2.1 slower, for ×1.10 work a second at best. Chunked launches and the plain stream do worse.
- 89-moduli vectors (23 Nov, the lead's gated decision; research's covers on the first 89 odd primes, e24f6e2 on
  ccr-d4a17dd0-7uu03r). Files are in `v89/`.
  - The vectors.
    - At Q = 170,000 they have 1,248-1,250 rows against 1,262-1,263 on the 88 moduli.
    - M has 192.7 digits, so a vector has only k < 21,378,978. It is k >= 2,137,898 for a 200-digit N.
    - Only 85.6 of their rows lie at or above the record 157,837, against 67.0 on the 88 moduli. So 32 fewer rows below the
      record have to be composite for a near-miss that beats it.
  - Vector mode: `search_gpu5.py --vector-dir DIR`.
    - Specs come from chunk files `DIR/vec_*.json`, which are read in order as they appear.
    - Each vector is one slice, the window [k_lo, k_lo + 2^24) from its first 200-digit k. That k is not a multiple of the
      window, which the sieve and the kernel handle. The vector's window must lie below its kmax.
    - `cq_limbs` computes N0 - q vectorized, so a new vector every window costs little host time.
    - `--log-near-exp 1` logs, per batch, the expected number of tested members whose first PRP row is at or above
      `--near-miss` (design hits included). This is the lead's gate metric.
    - The 88-moduli path is unchanged: slice lines are identical to the previous driver.
    - `test_vector_mode_fake.py` covers the stub tests: `cq_limbs` against `to_limbs`; campaign() in vector mode with and
      without the pipeline (every vector once, k_lo exact, a chunk written mid-run, restart, exhaustion).
  - The producer (`vecgen.sh`, one per RTX host).
    - It runs covergen walks from `starts/q170000_m89.txt` at cap 1,250, raised by one when a walk gives nothing new, and
      keeps the card's share of the covers (`part.py`: md5 mod 3, so no vector reaches two cards).
    - Each chunk goes through `make_specs.py` (kmax auto, the card's own ledger) and `check_specs.py`, then is published
      by an atomic rename.
    - It makes 1,000 vectors every 45 s, and a card uses about 2.6 a second.
    - Supply: cap 1,249 is exhausted at about 5,700 covers, while cap 1,250 had 131k after 10 min and was not exhausted.
      Research plans on about 1,251 rows on average over nine days.
  - Window cost (`wcost_rtxpro6000.txt`): 2^24 windows cost 6.3-6.4 ns a member against 5.5-5.6 ns at 2^25, +15%. 89
    moduli cost the same as 88.
  - Validation (`validation_gpu_rtxpro6000.txt`, `knowncase_cpu_brute.txt`).
    - The deep sieve, staged and plain, is identical to sieve200's CPU feeder at k_lo and at k_lo + 2^21 + 12345.
    - The kernel-28 flags are identical to gmpy2 on 8,192 random (row, k) with k in [k_lo, k_lo + 2^24).
    - The known case: on one vector's 524,288 members from k_lo, the GPU path (skip-frac 0, near-miss 46,171) and a CPU
      brute force (gcd residual, BPSW scan of every member) find the same 23 members, with the same least prime q.
- 29-bit Fermat kernel (23 Nov, uarch 710585f on ccr-b8c25887-i6tn9f; files in `k29/`), deployed under the lead's standing
  rule for engine changes.
  - The kernel has 23 limbs of 29 bits and a 31-bit top Montgomery digit (R = 2^669).
    - A step costs 805 + 23 multiplications, against 876 + 24 for the 24 × 28-bit kernel.
    - It covers n < 2^665, against 2^668. N < 10^200 = 2^664.4.
    - It flags n ≥ 2^665, and the driver then raises.
  - Step files: `fermat29_step_s1.cuh` (asm 1) on the RTX PRO 6000s, `fermat29_step_s1w.cuh` (asm 0) on the L4s and the T4.
  - The driver takes uarch's `search_gpu5_k29.patch`: its kernel-28 n-range assertion follows the step file
    (`gpu_fermat28.step_nmax`).
  - First light (`t29.sh`, `first_light_*.txt`).
    - 0 mismatches against gmpy2 on 2,000 candidates, on an 88-moduli spec and on an 89-moduli vector window.
    - Tests a second rose ×1.057 on both cards: 23.29M to 24.62M on the RTX, 4.47M to 4.73M on the L4.
  - Each card ran its own check before its deploy.
    - The RTX cards ran `k29v.sh` and then `deploy_k29r.py` (`identity_rtxpro6000.txt`).
      - 24 vector windows had slice lines identical to production's, with no range errors.
      - The vector known case found the same 23 (k, q) as the CPU brute force.
    - The L4s and the T4 ran `k29l2.sh` (`identity_l4_t4.txt`).
      - 8 production windows just below 2^30 had identical slice lines.
      - 146,191's member, under its Q = 150,000 residual (`nm150_v77.json`), was reported with g = 146,191 by both the normal
        and the deep sieve.
      - The script deploys only if the 29-bit batch is also at least 1% faster.
      - The campaign has to be stopped for about 3 minutes: a card that size holds one sieve matrix only. The first version
        (`k29l.sh`) only paused it, and its runs ran out of memory: the paused process held 22.2 of the L4's 23.0 GB.
  - Batch times:

    | card | production | 29-bit | change |
    |---|---|---|---|
    | gold-g4c (RTX PRO 6000) | 1.582 / 1.575 s | 1.510 s | −4.3% |
    | gold-g4 (RTX PRO 6000) | 1.577 / 1.570 s | 1.516 s | −3.7% |
    | gold-g4b (RTX PRO 6000) | 1.564 / 1.567 s | 1.501 s | −4.1% |
    | gold-l4b (L4) | 10.103 / 10.057 s | 9.705 s | −3.7% |
    | gold-gpu (L4) | 9.861 / 9.788 s | 9.469 s | −3.6% |
    | gold-l4c (L4) | 9.871 / 9.901 s | 9.587 s | −3.0% |
    | gold-xt4 (T4) | 9.633 / 9.611 s | 9.276 s | −3.6% |

    All seven GPUs run it since 11:54Z. In production the RTX cards run 1.517 s a batch (1.575 s before), and gold-l4b
    9.69 s (about 10.06 s before).
- Keep fraction in vector mode (`v89/vsweep.sh`, `v89/vsweep_rtxpro6000.txt`; gold-g4, 29-bit kernel, the same 24 windows
  at each f).
  - Expected near-misses ≥ 157,837 a second, against f = 0.97:

    | f | 0.96 | 0.965 | 0.97 | 0.975 | 0.98 | 0.985 | 0.99 |
    |---|---|---|---|---|---|---|---|
    | batch | 1.890 s | 1.692 s | 1.508 s | 1.324 s | 1.134 s | 0.939 s | 0.751 s |
    | near-misses a second | ×0.942 | ×0.975 | ×1 | ×1.026 | ×1.054 | ×1.080 | ×1.046 |
    | design hits a second | ×0.934 | ×0.971 | ×1 | ×1.032 | ×1.067 | ×1.102 | ×1.079 |

  - A repeat of f = 0.97 came within 0.5%.
  - At f = 0.985 a card uses its vectors ×1.6 faster: 4.26 a second instead of 2.64.
  - The lead moved the three RTX cards to f = 0.985 at 12:06Z (`v89/deploy_f985.py`). The basis was this sweep and
    research's supply figure: 12M distinct 89-moduli covers for nine days at about 1,251 rows. The L4s and the T4 stay at
    0.97.
  - The producers keep up. `vecgen.sh` holds 12,000 vectors ahead and walks only below that, so its chunk interval tracks
    consumption. Filling the buffer it made 1,000 vectors every 46 s, about 21.7 a second a card.
  - The lead's guard (`v89/rowguard.sh`, `rowguard.py`) runs on each RTX card every 5 minutes.
    - It compares the average row count of the last 2,000 consumed vectors with the average of every vector consumed before
      the switch: 1249.84 / 1249.88 / 1249.81 on gold-g4 / gold-g4b / gold-g4c.
    - If the gap passes +2 rows, the card drops itself to f = 0.98 and writes `/content/rowguard_tripped.txt`.
    - The producers stop at CAPMAX 1,253, so a trip needs the cap at 1,252-1,253 on most vectors.
  - DEEP_RCTA=8 with `--deep-gen-threads 512` gave identical slice lines and 1.498 s a batch against 1.508 / 1.515 s (−0.9%).
    uarch's wcost3 has it at −5.3 ms a 2^24 window of sieve alone (`uarch_measure/wcost3_rtxpro6000.txt`). Both are under
    the agreed 8 ms bar, so it is not deployed.
- Deep head (uarch 0e45ea8; files in `head/`). It sieves the first 64 rows of each window by the primes in (1e8, 1e9],
  after the count and the selection. So the kept members are unchanged, and only composite rows leave their lists.
  - The gate ran on gold-g4c (`headv.sh`, `headv_rtxpro6000.txt`) under the lead's approval and this session's conditions.
    - `headcheck.py`: OK. The head removes 11.11% of the head rows (modelled 11.11%), and sampled removed rows have a
      factor in range.
    - The head costs 11.5 ms a 2^24 window (136.1 to 147.6 ms) and 1.72 GB of device memory.
    - On the 24 test windows, production and the head driver with no head gave identical slice lines.
    - With and without the head, the per-member dumps were identical for all 12,091,392 members (k, first-PRP row,
      success), and tests fell 8.42%. The logged expected near-misses and design hits were ×0.9998.
    - The dump runs are slow (`savez_compressed`), so they give no timing.
  - Deployed on gold-g4c at 12:06:49Z together with f = 0.985, for a production A/B against gold-g4 and gold-g4b (no head,
    also at f = 0.985).
    - The A/B (`head/ab_production_f0985.txt`) ran 960 s, about 1,010 batches a card. With the head a batch took 0.9514 s,
      against 0.9449 s on both other cards: +0.7%. Tests fell 8.4%, and the expected near-misses a batch were the same.
    - At f = 0.985 the sieve is busy about 92% of a batch: 0.87 s of 0.945 s. So the head's extra sieve work, about 13.6 ms a
      window beside the Fermat kernel, costs more than the 8.4% of tests save.
    - The head came off gold-g4c at 12:24:38Z (`head/revert_head.py`).
- uarch's bench_pipes, parts 1-3 (`uarch_measure/bench_pipes_rtxpro6000.txt`).
  - A random-address ATOMS.AND costs what a random STS.32 or LDS.32 does: about 2.6 cycles a warp-op an SM, against 5.3-6.7
    for a plain read-modify-write.
  - So a race-free marking scheme would not speed the tile kernel. That kernel runs at about 0.8 marks a clock an SM, far
    below the unit's rate.
- Fused Fermat rounds and rcta 8 (23 Nov; files in `fround/`), deployed under the standing rule on the three RTX cards at
  12:30:45-12:31:09Z.
  - Fused rounds: uarch 4639f17, `--fused-rounds 1`.
    - `run_pool`'s ~100 small cupy kernels and ~6 host syncs a round become ~10 launches and one host read.
    - The Fermat kernel and the test lists are unchanged.
    - The driver is k29 plus `search_gpu5_fround.patch` (13e19e57aa0f, now `search_gpu5.py`).
    - `FERMAT28_DIR=/content/f29fr` is `/content/f29` with `fround.py` and `fround_kernels.cuh`.
  - rcta 8: `DEEP_RCTA=8` with `--deep-gen-threads 512`, so a generate CTA takes 8 rows at once with 512 threads.
  - They pay at f = 0.985 because the sieve is busy about 92% of a batch, so both sides of the pipeline are on the critical
    path.
  - Measured at f = 0.985 on the 24 test windows, alternating with production; every run had identical slice lines.

    | change | batch | production | factor |
    |---|---|---|---|
    | fused rounds alone (`frab_rtxpro6000.txt`) | 0.869 s | 0.940 s | ×0.924 |
    | rcta 8 alone (`uarch_measure/r8f_rtxpro6000.txt`) | 0.930 s | 0.946 s | ×0.983 |
    | both, gold-g4 (`comb_rtxpro6000.txt`) | 0.846 s | 0.949 s | ×0.892 |
    | both, gold-g4b | 0.855 s | 0.948 s | ×0.902 |
    | both, gold-g4c | 0.847 s | 0.947 s | ×0.894 |

  - Each card's vector known case with the new settings gave the same 23 (k, q) as the CPU brute force.
  - With `--profile-pool`, the gap a pool beside the sieve fell from 0.33-0.35 s (about half of `run_pool`) to 0.24-0.30 s.
  - In production the RTX cards run 0.858 s a batch (0.945 s before), about +10% expected near-misses a second.
  - The L4s and the T4 took fused rounds alone at 12:34-12:41Z (`fround/frl.sh`, `frl_l4_t4.txt`).
    - Each card was checked in the k29l2.sh pattern: 8 identical windows, and 146,191's member found by both sieves.
    - Batch: gold-l4b ×0.983, gold-gpu ×0.986, gold-l4c ×0.987, gold-xt4 ×0.983.
  - The keep fraction, re-swept on the new engine (`v89/vsweep2_rtxpro6000.txt`), is flat between 0.985 and 0.9875 (×1.018,
    within the ×1.012 of a repeat at 0.985). f = 0.985 stays.
- `--target 524288`, the most tests in one Fermat launch, half the default.
  - In tune2.sh it gave ×0.986, within the noise.
  - In a production A/B on gold-g4, 12:51:30-13:10:00Z, it ran 0.8473 s a batch against 0.8585 s on gold-g4b and gold-g4c
    (`fround/ab_target_production.txt`): ×0.987. Expected near-misses a second rose ×1.011.
  - Rolled out to gold-g4b and gold-g4c at 13:11Z, after each card's own check (`fround/dtgt2.sh`): 24 identical windows
    and the known case with it.
- The record of 12:48:45 UTC, g(N) = 158,209 (`../records/budget_1e200_200digit_g158209/`), came from gold-g4c in this
  configuration.
  - It was a near-miss of the 89-moduli vector `q170000_m89_p2c00019_v545` at k = 10,814,286.
  - Since then every card reports near-misses from 158,209 up (`NEAR_MISS=158209`, `v89/set_nm.py`). The L4s and the
    T4 restarted for it at 12:57Z, the RTX cards with the `--target` roll-out.
- uarch's opt-in sieve variants (3209f0d; files in `sievepack/`), deployed on the three RTX cards at 13:17:39-13:17:51Z.
  - The tree is `/content/ua_v5`: `ua_v3` with 3209f0d's whole `sieve200/cuda`, whose default build is SASS-identical.
  - The variants:
    - `DEEP_BIN_PACK=1`: 5 marks of 19 bits in 3 words, 40% fewer bin bytes;
    - `DEEP_GEN_HOIST=1`: the generate kernel's visit loops with the row, q and table pointer hoisted;
    - `DEEP_TILE_UNROLL=4`: 4 small primes set up at once in the tile kernel;
    - `DEEP_TILE_PREFETCH=256`.
  - splitab (`sievepack/splitab_rtxpro6000.txt`), ms a 2^24 window of sieve: 83.7 for production; 78.1 with PACK; 81.2 with
    HOIST; 76.9 with UNROLL=4; 70.3 with all three; 69.3 adding the prefetch.
  - Each card's own check (`packab.sh`, `packab_rtxpro6000.txt`) ran production, the new tree without options, and the two
    combinations, alternating on the 24 windows.
    - Slice lines were identical in all seven runs on every card.
    - The known case with all four options gave the same 23 (k, q) as the CPU brute force.
    - Batch: gold-g4 ×0.970 (it took the variant without prefetch), gold-g4b ×0.969, gold-g4c ×0.959.
  - The batch gains less than the sieve does: with the sieve 17% faster, the Fermat side (pool wall ~0.65 s) becomes the
    floor.
  - In production, 13:18:30-13:34Z: 0.814-0.817 s a batch (`sievepack/production_1318_1334.txt`). Design hits a second
    rose ×1.04-1.05.
- uarch's flat flush and grid order (8558276; `DEEP_GEN_FLUSH2=1 DEEP_GEN_ORDER=1`), deployed on the three RTX cards at
  13:48:32-13:51:31Z on top of the four options above.
  - The tree is `/content/ua_v6`: `ua_v3` with 8558276's whole `sieve200/cuda`.
  - Per the instruction accounting, the generate kernel was issue-bound on its warp-a-bin flush, which was half its
    instructions. FLUSH2 makes the flush one flat loop, a thread a word.
  - ORDER runs the 4 row slices of a prime chunk together, so they read the prime table from L2.
  - splitab6 (`sievepack/splitab6_rtxpro6000.txt`): all six options 63.5 ms a window, against 67.7 for production's four.
    Generate fell from 45.9 to 40.3 ms.
  - Each card's own check (`flushab.sh`, `flushab_rtxpro6000.txt`) ran production, ua_v6 with production's options,
    +FLUSH2, and +FLUSH2+ORDER, alternating on the 24 windows.
    - Slice lines were identical in all seven runs on every card.
    - The known case with all six options gave the 23 (k, q).
    - Batch: gold-g4c ×0.967, gold-g4 ×0.957, gold-g4b ×0.963, all with both options.
  - In this regime the sieve thread is busy about 100% of a batch, and beside the Fermat kernels it runs about 3× slower
    than alone.
  - In production, 13:52:30-14:08Z: 0.7815 s a batch on all three cards (`sievepack/production_1352_1408.txt`). Design hits a
    second rose ×1.035.
- uarch's generate unroll with clamped table loads (0d42e4d; `DEEP_GEN_UNROLL=4`), deployed on the three RTX cards at
  14:14:28-14:14:39Z on top of the six options above.
  - The tree is `/content/ua_v7`.
  - After the flat flush the generate kernel was waiting on its 16-byte prime-table loads. The unrolled loops keep 4 loads in
    flight a warp, at 23-24 instructions a visit like unroll 1.
  - genab (`sievepack/genab_rtxpro6000.txt`), generate ms a window: 40.30 at unroll 1, 32.43 at 2, 28.74 at 4, 30.10 at 8.
    Smaller CTAs and rcta 16 are slower. Tile unroll 8 / 16 add nothing over 4.
  - Each card's own check (`unrab.sh`, `unrab_rtxpro6000.txt`) ran production, ua_v7 with production's options, unroll 4,
    and unroll 2, alternating on the 24 windows.
    - Slice lines were identical in all seven runs.
    - The known case with unroll 4 gave the 23 (k, q).
    - Batch with unroll 4: gold-g4 ×0.969, gold-g4b ×0.962, gold-g4c ×0.966.
  - In production, 14:15:30-14:31Z: 0.755 s a batch on all three cards (`sievepack/production_1415_1431.txt`).
- The last small items (15:00-15:35Z) are at the noise floor of a batch.
  - `sievepack/bundle8_rtxpro6000.txt`, ms a window: the tile kernel's clamped loads made no change. Prefetch 384 / 512, the
    split points and tile 18 were all slower. The pipelined tile kernel at AT=64 saved 1.5 ms.
  - `sievepack/bundle9_rtxpro6000.txt`: LEAN (GEN_SCAN2 + RESV_LATE + MINRED) saved 1.2 ms a window, 2.8 with the pipelined
    tile.
  - The LEAN gate (`sievepack/leanab_gold-g4c.txt`, `leanab2_g4_g4b.txt`):
    - gold-g4c took LEAN at ×0.9875 (15:02:52Z);
    - gold-g4 took LEAN + the pipelined tile at ×0.9895 (15:06:25Z);
    - gold-g4b failed the 1% gate at ×0.9928 and is unchanged.
    - On every card, slice lines were identical and the known case ran with the deployed set (`kc_prod.sh`).
    - The three cards now differ in options whose differences are within the noise.
  - The fused rounds' control stream (uarch 27db8d0, `fround/ctlab_rtxpro6000.txt`) cut the gap a half-pool beside the
    sieve from 0.295 to 0.198 s. But the batch did not move (×0.998), so it is not deployed.
- The keep fraction, re-swept with the 13:17Z engine (`v89/vsweep3_rtxpro6000.txt`, near-misses from 158,209): ×0.903 /
  ×0.926 / ×0.942 / ×0.975 / ×1.006 at f = 0.975 / 0.9775 / 0.98 / 0.9825 / 0.9875 against 0.985, and a repeat at 0.985
  gave ×0.985. f = 0.985 stays.
- research's m88f covers on the L4s and the T4 (23 Nov; files in `m88f/`). These are covers on the first 88 odd primes
  (b3d6688), Q = 170,000, with 1,257-1,259 residual rows against 1,262-1,263 for the 88-moduli covers before. The lead
  decided at 15:58Z, subject to four checks.
  - 2,040 vectors (`ledger_q170000_m88f.txt`), 510 per card. Every N is in [10^199, 10^200) on the campaign's k range
    [2^30, 2^32).
  - The checks:
    1. The prime tables come from each spec's own cover and M.
    2. The GPU normal path equals search_c.py on a 2^20 slice at f = 0.97 and 0.9 (`checks_l4_cpu.txt`).
    3. The known case, deep path at f = 0, k ∈ [2^32 − 2^19, 2^32), near-misses from 45,061: the GPU's 40 (k, q) equal
       `cpu_brute_k0.py`'s (`knowncase_cpu_brute_m88f.txt`).
    4. The first 20 vectors gave members a second ×1.0114 on gold-l4b.
  - The cards switched at batch ends, 16:50:45-16:51:24Z (`deploy_m88f.py`, campaign dir `/content/c170f`; `/content/c170`
    is kept for a revert).
  - Measured over the first ~15 minutes (`deploy_l4_t4.txt`): members a second ×1.003-1.008, expected design hits a second
    ×1.058-1.064, alive rows a member 423.8 → 422.5.
- Top-of-range windows in vector mode (23 Nov; the lead decided at 16:36Z, subject to four checks; files in `vtop/`).
  - `--vector-place top` (`search_gpu5_vtop.patch`, 22 changed lines): a vector's 2^24 window is [kend − 2^24, kend),
    with kend = min(kmax, ⌈(10^200 − N0)/M⌉). That is N from 2.15·10^199 to just below 10^200, instead of 10^199 to
    8.85·10^199 from k_lo.
  - A larger N has a slightly lower prime density, so a member's rows are less likely to hold a prime. Expected
    near-misses from 158,209 rise ×1.0113 a vector and expected hits ×1.0122 (the 24 test vectors), at the same batch
    time (×1.003, inside the noise).
  - The loader asserts that every window lies in [10^199, 10^200). It skips a vector whose name is in the done set
    under either placement, since the two windows of one vector overlap by ~85%.
  - The checks, on gold-g4b (`vtop_rtxpro6000.txt`):
    1. The loader, run from the code itself on all 228 chunk files (112,931 vectors). At the default placement it
       matches production on every chunk. At the top, it takes each of the 12,579 vectors not yet done exactly once,
       and a simulated restart takes nothing again.
    2. The GPU normal path equals search_c.py on the top 2^19 of a production vector, at f = 0.97 and 0.9.
    3. The bottom known case gives the same 23 (k, q), and the slice lines at the default placement are identical to
       production's.
    4. A top-window name is name@4601761 or name@4601762; a bottom one is name@2137898.
    - Extra: the known case at the top (k ∈ [20,854,690, 21,378,978), f = 0, near-misses from 46,171) gives the same 25
      (k, q) on the GPU and in `cpu_brute_k0.py` (`knowncase_top_cpu_brute.txt`).
  - Deployed on gold-g4, gold-g4b and gold-g4c at 17:29:09-17:29:18Z (`deploy_vtop.py`, `deploy_rtxpro6000.txt`).
    `search_gpu5.py` here is the deployed driver. The L4s and the T4 still run the earlier one, which is the same in
    campaign mode.
  - At 17:42Z the three generators got research's 426 starting covers (58e95e3: 186 at 1,248 rows, 240 at 1,249). Their
    walks from the 210 starting covers were making only 1,251-row vectors, at +1.2 over the row guard's base.
- uarch's one-pass generate kernel (f1b904a, `DEEP_GEN_ONEPASS=1`; tree `/content/ua_v10` = `ua_v3` + f1b904a's
  `sieve200/cuda`), deployed on the three RTX cards at 18:09:59-18:11:05Z under the standing rule.
  - The large-prime generate kernel used to visit every (prime, row) pair twice: once to count each bin's marks, once to
    place them. Now the counting atomic's rank places the mark in the bin's 40 shared-memory slots, with an overflow list
    and a fallback to the old path. The marks and bits are the same. With the flag unset, the kernel source is
    byte-identical.
  - bench_split on gold-g4b (`sievepack/opab_rtxpro6000.txt`), ms a 2^24 window: generate 28.75 → 22.15, the whole sieve
    51.2 → 44.4. Unroll 8, 30 slots and 25 slots were slower.
  - The driver gate on each card (`sievepack/opgate.sh`, `opgate_rtxpro6000.txt`): base / ONEPASS / ONEPASS + launch
    bounds 512,3, alternating on the 24 test vectors.
    - Batch ×0.9728 on gold-g4, ×0.9566 on gold-g4b, ×0.9725 on gold-g4c.
    - Slice lines were identical everywhere, and the known case gave 23/23 with the chosen settings.
  - Production (`vtop/production_rtxpro6000.txt`), on gold-g4 and gold-g4c:
    - top placement against bottom: expected near-misses a batch ×1.0185, design hits a second ×1.015-1.017;
    - one-pass on top of that: batch ×0.972, design hits a second ×1.033.
- A trade-off in the newer covers. Research's new starting files lower the total rows but put more rows below the
  near-miss threshold (158,209).
  - On the RTX, chunks from 58e95e3 average 1,250.5-1,250.9 rows (from 1,251.0), but 1,171.8-1,176.8 of them lie below
    158,209 (from ~1,169.3). Expected near-misses a batch fell ~10% from 18:20Z, when they reached the queue, while design
    hits a batch rose ~0.8%.
  - On the L4s and the T4, top2 has 1,257.65 rows (from 1,258.65), but 2.8 more below 158,209: about +2.4% design hits and
    -6.5% near-misses.
  - Both are kept for now, and the choice is with the lead.
- The lead's L4 keep-fraction A/B (`l4f/ab_l4_f985.txt`): gold-l4c at f = 0.985 against gold-gpu and gold-l4b at 0.97,
  17:30-18:30Z. Expected design hits a second came out ×0.9865 against the controls, below the +5% bar, so it went back
  to 0.97 at 18:34Z.
  - The L4 runs sieve then Fermat in series, under its power cap. Its fixed part is 3.27 s of a 9.33 s batch, so halving
    the tests only removes the Fermat half.
- At 18:34-18:35Z the four L4/T4 cards switched to 6,000 m88f vectors from research's 3bcdbf6 starting file at cap 1,258
  (1,800 a card on the L4s, 600 on the T4; `m88f/deploy_l4_t4.txt`).
- The RTX sieve options and the one-pass kernel on the L4s (`l4op/`), under the standing rule. Until now the L4s and the
  T4 ran the old tree uaB with only `DEEP_STAGED` and the driver's defaults (rg 16, 256-thread CTAs, rcta 2).
  - bench_split on gold-l4b (`opl4b_l4.txt`), ms a 2^25 window:
    - production 1,455.1; with the RTX option stack 1,171.5; with the stack at the RTX's rg 32 / 512 / 512 / rcta 8,
      982.4;
    - with one-pass: 832.5 (20 slots, rcta 8), 785.4 (40 slots, rcta 4), and 783.1 at 75 slots, rcta 2, rg 32,
      512 / 512.
    - uarch sized the slots: about 3/4 of the stage's marks over rcta × 64 tiles bins a CTA.
  - The gate (`gate_deploy_l4.txt`):
    - Batch 9.520 → 8.094 s (×0.850), with slice lines identical.
    - On a production window at f = 0.97, the near-misses from 45,061 were 129 = 129 member by member.
    - The known case gave 40/40 with the new options and parameters. The 2^19 window runs with one-pass off, because
      on one tile uarch's host-side check (fc12768) refuses it.
    - A 2^25 window at f = 0 needs 28 GB of survivor rows, more than an L4 has.
  - Deployed at 18:55:40-18:56:28Z on gold-l4b, gold-gpu and gold-l4c, together with the lead's item 8: `KLO =
    3,758,096,384`.
    - So each vector is scanned only on the top 16 levels of 2^25, and the card then moves on to fresh vectors.
    - Hits a slice at the top level run ~9% above the bottom level, so this is about +3% against the full
      [2^30, 2^32).
    - Each campaign's `search.log` (one name@k0 line a slice) is the record of the levels done;
      `l4op/levels_done.py` tallies it.
  - On the T4, bench_split gives 2,553 → 1,739 ms with the same row; the stack alone is slower there (2,715).
    - Its gate (`gate_deploy_t4.txt`): batch ×0.907 with slice lines identical; the same 129 per-member near-misses as
      the L4 on that window; the known case 40/40.
    - Deployed at 19:11:41Z with the top 16 levels.
  - Measured on the L4s (`l4rate.py`, 18:57-19:08Z against 18:35-18:54Z): batch ×0.854 / ×0.852, expected design hits
    a second ×1.166 / ×1.171 on gold-gpu / gold-l4c. gold-l4b's earlier window includes the test stops.
- Colab ends every runtime 24 h after creation. gold-gpu was created at 2026-11-22T19:12:40Z and ended at 19:13:03Z on
  the 23rd, taking its logs with it.
  - Before every later end, each card's state was snapshotted (`runlogs/snap.py`), and its compact records went to
    `runlogs/2026-11-23/`: done sets, generator ledgers, found files, expected sums.
  - The user approved replacements (~20:10Z). The kit is in `bringup/`. Colab refuses a fourth concurrent G4, so each
    RTX replacement waits for its predecessor's slot.
  - gold-g4 → gold-g4d (20:19Z), gold-g4b → gold-g4e (20:33Z) and gold-g4c → gold-g4f (21:02Z): each on research's
    491-family vectors (below), with a fresh campaign directory `/content/c170r` and generator partitions 0, 1 and 2.
    - Each new GPU first passed the production known case at the top window (25 = 25, `kc_top_check.py`).
  - gold-gpu → gold-l4d (20:20Z), on gold-gpu's untouched top3 share in `/content/c170g`.
    - It first passed the per-member check and the m88f known case 40/40 on the new GPU.
  - Following the lead (19:27Z), found lines are copied off every card every 2 minutes (`runlogs/found_sync.sh`).
    That job hit the 2 h limit on background jobs at 22:30Z. Since 22:35Z the fleet watcher does it on each poll,
    ~3 min apart (`bringup/fjob_watch20.sh`; `peek_v3.py` also returns every found line, and the list ends with a
    marker).
    - A replacement starts with its predecessor's lines marked as already copied, so lines restored from a snapshot
      are not reported again as new.
  - Proactive replacements at ~23 h, each onto its share of the shifted family-B vectors in a fresh c170g:
    gold-l4b → gold-l4e (23:38-23:45Z), gold-l4c → gold-l4f (23:41-23:47Z) and gold-xt4 → gold-xt4b (a T4,
    00:44-00:48Z on the 24th, 1,572 vectors). Each new GPU passed the per-member check (129 = 129 near-misses at
    production f on the L4s; identical on the T4) and the m88f known case (40 = 40) before deploying.
    - Since 00:48Z all four L4/T4 cards run their top32-shifted family-B shares.
    - gold-l4f's first bring-up stopped after 34 s because gold-l4c's snapshot had no `opl4gate2.sh` (the L4 gate had
      run on gold-l4b only). The script was uploaded from the repo and the bring-up re-run. Now the handover scripts
      upload it themselves.
    - Lesson: an edit to `handover_pro.sh` while a handover was running it broke that job with a syntax error (bash
      reads a script as it runs). Only the local follow-up died; the card's bring-up finished on its own. Scripts in use
      are not edited in place.
    From the next round, runtimes are replaced at ~23 h at a batch boundary (`bringup/handover_pro.sh`).
- research's 491-family vectors on the RTX cards (bbc8cd8: the first 88 odd primes and 491 instead of 463), approved by
  the lead behind a six-point gate (`v491/`, gold-g4c):
  1. The deep sieve matches the CPU feeder at the top windows, and the Fermat flags match gmpy2.
  2. The GPU normal path equals search_c.py at f = 0.97 and 0.9.
  3. The known case gives the same 46 (k, q) on the GPU and in `cpu_brute_k0.py`.
  4. The full 2^24 window at f = 0 gives 1,066 = 1,066 near-misses member by member, before and after one-pass.
  5. Against what production consumed (24 vectors of the newest 463 chunk), design hits a second ×1.061 and near-misses
     ×0.9995. The lead's bars were +3% and −3%.
  6. On gold-g4d the generator makes 1,000 vectors at 1,248 rows every ~40 s.
- Family-B covers (research a9e4a27; the lead changed the criterion at 20:00Z). What decides the final record is how far
  above 170,000 a design hit stops. So the uncovered primes in 170,000-180,000 count, not the rows below 158,209.
  - Check 6 (`famB/check6_results.txt`), uncovered primes in [170k, 175k) / [175k, 180k): 57.2 / 60.5 in the first
    m89 chunks (family A), 49.1 / 52.1 in the 58e95e3 chunks (A + B), and 46.1 / 50.4 in the 491 chunks.
  - The 491 family-B-only file (3,924 covers, a subset of 4,000) has run since 20:26Z. The m88f file is B ∩ present
    (258 covers).
  - The 491 pool at ≤ 1,248 rows ran out within the hour: each partition's walk found only covers already in its ledger.
    The generators raised their cap to 1,249 (gold-g4d 20:25Z, gold-g4e 20:40Z, gold-g4f 21:08Z).
    - The row guard's base is 1,248.000 and it trips only above +2. With CAPMAX = 1,250 the trailing average cannot get
      there, so the cap rise cannot trip it.
    - Research estimates ~290,000 covers at ≤ 1,249 and ~3.7 million at ≤ 1,250. At ~1.5 M vectors a day, cap 1,250
      lasts ~2.5 days. Then either CAPMAX or the guard must change, which is the lead's call.
    - The lead decided at 21:19Z and 21:35Z, and both rules are now in place:
      - The guard's base is the mean measured at the first cap (1,248.000), plus one row for each of the generator's cap
        steps (its `cap raised to N` lines). The +2 trip is relative to that, so a planned cap step can never lower f.
        It went live on gold-g4d, g4e and g4f at 21:38-21:46Z: base 1,249.000 at cap 1,249, trailing +0.000.
      - At the first `no chunk at cap 1250`, the cap goes on to 1,251, then 1,252. The live generators keep CAPMAX 1,250,
        since their pool outlasts these runtimes. Every replacement starts its generator at the old card's last cap with
        CAPMAX 1,252.
      - Watcher 19 reports cap steps (for the regular reports), a stall at CAPMAX, fewer than 2,000 vectors ahead, and a
        dead generator (`peek_rg.py`'s supply fields).
    - The tail before a cap step: at 1,248 on gold-g4d, a walk's new covers fell from 1,000 to 1 over 28 walks in
      ~3 min. The 12,000-vector buffer (~35 min) covered that easily.
      - The 1,250 pool is ~130× larger, so its tail could keep an RTX waiting for 1-2 h. The lead decided (21:46Z) to
        step the cap when a walk gives fewer than 100 new vectors, and at once when fewer than 3,500 (~10 min) are
        ahead after a walk that did not fill its chunk: "a GPU must never idle waiting for vectors".
      - The leftovers at the old cap still come out of later walks, best first (`vecgen491.sh`, YMIN / BUFMIN).
      - A mock run of the generator checked both rules (`bringup/README.md`).
      - The live generators were restarted on these rules at an idle moment between walks (`restart_gen.py`), so no
        ledger line or chunk was cut. Their cap carried over (1,249), with CAPMAX 1,252.
- research's top32 shift for the L4/T4 vectors (4de3423; the lead approved it at 20:34Z behind a three-point gate; `s32/`).
  - Each vector gets N0 += k_shift·M, with k_shift = 5,603,499,370 or 5,603,499,371, so that k = 2^32 − 1 is its last
    member below 10^200.
  - The top 16 levels then hold N from 9.458e199 up to just below 10^200. Unshifted, a vector would cross 10^200 only at
    k ≈ 9.9e9, and its N at 2^32 is about 4.3e199.
  - The batch is the shifted twin of the unshifted family-B batch: the same 12,000 covers, in the same order.
  - The gate:
    1. `s32_assert.py`, independent of research's `check_specs.py`, matched all 12,000 shifted specs to their unshifted
       covers: the same M and residual rows, the residues mod the 88 cover primes, N(2^32 − 1) < 10^200 and
       N(KLO) ≥ 10^199. `check_specs.py` also passed (12,000 OK, all N0 distinct).
    2. The known case (top4s_v0, the top 2^19 at f = 0, T = 48,397) gave 40 (k, q) on the GPU (gold-l4c) and the same 40
       in `cpu_brute_k0.py` (`kc/compare_result.txt`).
    3. On gold-l4c, the same 8 covers, top two levels, shifted against unshifted: expected design hits a batch ×1.0590.
       The bar was ×1.03 and research predicted ×1.056. Batch time was ×1.006 (`s32gate_l4.txt`).
  - Ledger: lines 26,041-38,040 hold the unshifted batch's keys and lines 38,041-50,040 the shifted ones
    (`m88f/ledger_index.txt`). The names mark the shifted vectors (`q170000_m88f_top4s_v*`) and each spec carries its
    `k_shift`.
  - gold-l4d has run its share (3,476 vectors) since 21:26Z, switched at a batch end by `switch_top4s.py`. The done set
    carries over, and the top3 vectors it had done stay done.
  - gold-l4b and gold-l4c get 3,476 each and gold-xt4 1,572, at tonight's ~23 h replacements. Each share is about 62 h
    of top-16 levels.
- Resuming the new campaign dirs (fixed 21:30Z, before any snapshot needed it). `snap.py` had kept only the old dirs.
  - The next round of replacements would have lost the RTX cards' c170r done sets and 491 ledgers, and gold-l4d's c170g.
  - The fixes:
    - `snap.py` keeps c170r, c170g, cover491 with its ledgers, the row guard's row counts (rowidx491) and vec491/made.txt.
    - `resume491.sh`, run by the RTX bring-up, starts a replacement with nothing ahead (made.txt = vectors consumed) and
      numbers its chunks after the old card's last one. Without it, the new chunk names would repeat names already in
      the done set and be skipped. The row guard skips names whose chunks are gone.
    - `bringup_l4.sh` resumes c170g as well as c170f.
    - `handover_pro.sh` gained KIND `l4`, which resumes an L4/T4 campaign dir.
- uarch's bench_split (`uarch_measure/bench_split_rtxpro6000.txt`) splits a window's sieve kernel by kernel.
  - At production's rg 32 / rcta 8: generate 49.6 ms (pass A 15.6, pass B 34.1), tile kernel 33.0 ms (small primes 14.6,
    bin apply 19.9).
  - Bin apply halves at rg 4, where the bins fit in L2, but the generate passes grow with the number of groups.
- uarch's E5 (`uarch_measure/e5_ffma_rtxpro6000.txt`): a dummy FFMA inside the real Fermat step adds about 1.2 ticks, close
  to an IADD3 (1.1-1.6), not the ~0 of a free pipe. So the FP32 pipe does not run free beside the multiplier.
- Fermat step on the RTX PRO 6000 (`uarch_measure/run_experiments_FGC_rtxpro6000.txt`).
  - clock64 counts SM cycles (2.43 GHz), but a dependent IMAD costs 6 cycles on sm_120.
  - The cost per IMAD.WIDE is flat at 4.57 ticks from two warps a scheduler up, so the step is at its multiplier floor.
  - s2r_asm (−3.5%) and s4r_asm (−7.9%) only add cost, so production stays on s1r_asm.
- Skip fraction, re-measured with supply no longer a constraint (`bench_skipfrac.sh`, same 64 slices,
  `sieve_bound/gpu_rtxpro6000_skipfrac.txt`): expected hits ×1.40 / ×1 / ×0.74 / ×0.45 / ×0.29 at f = 0.95 / 0.97 / 0.98 /
  0.99 / 0.995, with tests in proportion to the kept fraction. On production batch times (2.03 s at 0.97, of which ~0.38 s is
  not Fermat), f = 0.98 is +1.4% and f = 0.99 is −3%. Production stays at f = 0.97.
- Since 21:08Z the GPUs run Q = 140,000 (research cover, 1,011 rows; gold-g4, gold-g4b, L4) and Q = 150,000 (1,093-1,094 rows;
  gold-g4c), both checked here, k in [2^30, 2^32), top first (`run_v3_campQ.sh`). `TALLY.md` has expected against found.
- `gpu_fermat_ref.py`: a limb-exact CPU model of the kernel (for the Lean proof). 200 candidates, k = 0..3, 247, 248,
  2^32 − 1 and random: 0 mismatches against pow(2, n − 1, n).
- Order: E falls as N grows (p ∝ 1/ln N): E^ is ≈ 20.8 just below 10^199 and ≈ 21.05 at k ≈ 10^7, so the
  GPUs scan k ∈ [2.73·10^8, kcap] from the top down (`--desc --klo 272629760 --kmax 543859952`).

Successes are re-checked on the CPU with `search.verify_success` before they are written to
`found.jsonl`, and a hit is then certified as usual (evidence for every prime offset, PARI ECPP
for N − g, an independent checker).
