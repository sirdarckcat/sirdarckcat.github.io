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
  - t2700..t10133 are in reserve.
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
- Since 21:08Z the GPUs run Q = 140,000 (research cover, 1,011 rows; gold-g4, gold-g4b, L4) and Q = 150,000 (1,093-1,094 rows;
  gold-g4c), both checked here, k in [2^30, 2^32), top first (`run_v3_campQ.sh`). `TALLY.md` has expected against found.
- `gpu_fermat_ref.py`: a limb-exact CPU model of the kernel (for the Lean proof). 200 candidates, k = 0..3, 247, 248,
  2^32 − 1 and random: 0 mismatches against pow(2, n − 1, n).
- Order: E falls as N grows (p ∝ 1/ln N): E^ is ≈ 20.8 just below 10^199 and ≈ 21.05 at k ≈ 10^7, so the
  GPUs scan k ∈ [2.73·10^8, kcap] from the top down (`--desc --klo 272629760 --kmax 543859952`).

Successes are re-checked on the CPU with `search.verify_success` before they are written to
`found.jsonl`, and a hit is then certified as usual (evidence for every prime offset, PARI ECPP
for N − g, an independent checker).
