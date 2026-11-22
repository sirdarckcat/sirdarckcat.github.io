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
- Since 21:08Z the GPUs run Q = 140,000 (research cover, 1,011 rows; gold-g4, gold-g4b, L4) and Q = 150,000 (1,093-1,094 rows;
  gold-g4c), both checked here, k in [2^30, 2^32), top first (`run_v3_campQ.sh`). `TALLY.md` has expected against found.
- `gpu_fermat_ref.py`: a limb-exact CPU model of the kernel (for the Lean proof). 200 candidates, k = 0..3, 247, 248,
  2^32 − 1 and random: 0 mismatches against pow(2, n − 1, n).
- Order: E falls as N grows (p ∝ 1/ln N): E^ is ≈ 20.8 just below 10^199 and ≈ 21.05 at k ≈ 10^7, so the
  GPUs scan k ∈ [2.73·10^8, kcap] from the top down (`--desc --klo 272629760 --kmax 543859952`).

Successes are re-checked on the CPU with `search.verify_success` before they are written to
`found.jsonl`, and a hit is then certified as usual (evidence for every prime offset, PARI ECPP
for N − g, an independent checker).
