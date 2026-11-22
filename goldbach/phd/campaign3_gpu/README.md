# campaign3 on a GPU

`campaign3` (`../campaign3/`) searches the budget game below 10^199 with the Q = 122,000 cover:
any hit gives g(N) ≥ 122,011 > 119,419. At this size nearly all the time goes to base-2
Fermat tests of ~661-bit complements N − q. This directory runs the same search with those
tests on a GPU.

| file | what it is |
|---|---|
| `gpu_fermat.py` | CuPy kernel: 2^(n−1) mod n for a batch of n = (N0 − q_i) + k·M, n built on the GPU from 21 32-bit limbs; Montgomery squaring (CIOS), the base 2 as doublings |
| `test_gpu_fermat.py` | the kernel against gmpy2 on campaign3 candidates, then its speed |
| `search_gpu.py` | `search.py` with the tests on the GPU: the same sieve (worker processes, `search.init_spec`), then GPU launches that test the next D complements of every open member in `search.run_block`'s order, stopping a member at its first PRP; prints `search.py`'s per-slice line |
| `check_block.py` | `search_gpu.py` against `search.run_block` on whole blocks |
| `run_c3gpu.py` | driver: the variants in `my_specs.json`, k-major slices of 2^20 k, resumes from its own `search.log` |
| `variant_split.json` | which of the 40 variants the GPU and the CPU machines scan (disjoint) |

Checks, on a Colab NVIDIA L4 (22 Nov):
- The kernel matches gmpy2 on 80,000 candidates of two variants (1,884 PRPs, 0 mismatches),
  k across the whole range including the smallest and largest. It runs 2.3·10^6 tests/s,
  against 111 µs a test for gmpy2 on one core of the same runtime (~260 cores).
- `search_gpu.py` equals `search.run_block` on 4 whole blocks: alive 50,897,453, tests 2,412,669,
  prps 131,072 on both (`BLOCKS MATCH`).
- Production rate: ~49,000 k/s with full hit mass (`--skip-frac 0`), E^ ≈ 21.0 as on the CPU.
  `campaign3` on 4 CPU cores ran 16,000 k/s keeping 29.6% of the hit mass (skip-frac 0.92),
  ~4,700 k/s in effect, so one L4 is ~10 such machines. The CPU sieve (11 workers) is now the
  limit; the GPU is at ~40% of its test rate.

Successes are re-checked on the CPU with `search.verify_success` before they are written to
`found.jsonl`, and a hit is then certified as usual (evidence for every prime offset, PARI ECPP
for N − g, an independent checker).
