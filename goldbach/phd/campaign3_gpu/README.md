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
- Order: E falls as N grows (p ∝ 1/ln N): E^ is ≈ 20.8 just below 10^199 and ≈ 21.05 at k ≈ 10^7, so the
  GPUs scan k ∈ [2.73·10^8, kcap] from the top down (`--desc --klo 272629760 --kmax 543859952`).

Successes are re-checked on the CPU with `search.verify_success` before they are written to
`found.jsonl`, and a hit is then certified as usual (evidence for every prime offset, PARI ECPP
for N − g, an independent checker).
