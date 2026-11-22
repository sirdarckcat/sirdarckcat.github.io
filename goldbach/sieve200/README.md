# sieve200: the sieve of `search.run_block` in C

`search.py`'s first stage builds, for a block of members `k0 .. k0+L-1` of the progression `N = N0 + k M`, the
boolean matrix `alive[r][j]`: row `r` (residual prime `q = U[r]`) is alive for member `j` unless a sieve prime `s`
(3 <= s < B, `s` not dividing `M`, not a cover prime) divides `N0 + (k0+j) M - q`.  numpy does that in about 1.7 s per
block of 32,768 members for campaign 3 (867 rows, B = 10^6).  `sieve200.c` does the same in 0.07-0.2 s, with the
counts (rows alive per member, 16 bit, not saturating) and the survivor lists of chosen members.

| file | what |
|---|---|
| `sieve200.c` | the library: `s200_new` (context for one `N0`, `M`, rows, `B`, block size `K = 2^logK`), `s200_block` (bit rows + counts of a window of K members), `s200_extract` / `s200_extract_bitmaps` (alive rows of chosen members) |
| `sieve200.py` | ctypes wrapper, compiles the C file with gcc on first use (`SIEVE200_MARCH=haswell` for AVX2, `generic` for plain C; default `native`) |
| `search_c.py` | **drop-in for `search.py`**: same command line, same log line, same results; replaces `init_spec` and `run_block` only |
| `test_sieve200.py` | alive matrix and counts against the definition (brute force) and against `search.py`'s numpy sieve |
| `test_dropin.py` | `run_block` of both on the same blocks (six returned numbers equal), and the two command lines (log line and found file equal) |
| `bench_sieve200.py` | microseconds per member against `B` and `K` |
| `curves.py` | sieve cost against `B` and `K`, measured probability that a survivor is prime, hit mass of the emptiest 8% |
| `Feeder` (`sieve200.py`), `s200_select`, `s200_csr` | **the feeder for a GPU Fermat tester**: sieve a window, exact `u16` counts, the emptiest fraction of every block, their survivor rows as CSR, the block statistics (below) |
| `test_feeder.py`, `bench_feeder.py` | the feeder against numpy (argsort, alive matrix, hit mass, GPU session's reference numbers), and its speed |

## Use

    python3 goldbach/sieve200/search_c.py slice.json --procs 4 --sort-tests --skip-frac 0.92 --p-est 0.055 \
            --sieve-b 1000000 --out found.jsonl

(for `run_campaign3.py`: replace `os.path.join(GOLDBACH, "search.py")` by `os.path.join(GOLDBACH, "sieve200", "search_c.py")`).
If gcc is missing it says so on stderr and runs `search.py`'s own sieve.  `SEARCH_C_CHUNK` (default 4) is the number of
consecutive blocks a worker sieves as one window of `K = 2^logK` members; a bigger window amortises the per-prime
set-up (it matters for `--sieve-b` above 10^6), but the pool needs at least `procs` windows per `search_spec` call.

## Method

For every row and every sieve prime `s` the first member offset divisible by `s` is `(q M^-1 + c_s - k0) mod s`
(`c_s = -N0 M^-1 mod s`, one 64-bit multiply and a reduction with a double-precision reciprocal), and the row's bits at
that offset, offset + s, ... are cleared.  Primes below 384 clear 512 bits at a time from a periodic bit pattern
(campaign 3's cover takes nearly all of them, so there are almost none).  Every other prime is a fixed-trip loop of
masked single-bit clears, so there is no unpredictable branch; marks beyond the window are masked out.  The counts
come from a carry-save vertical counter over the rows.

## Tests

    python3 test_sieve200.py [--full] [--march haswell|generic]   # about 10 s, --full: 867 rows, B up to 10^6
    python3 test_dropin.py [--full]                               # about 70 s, --full: a whole campaign-3 block

All pass for the AVX-512, AVX2 (`-march=haswell`) and plain C builds.


## The feeder (`Feeder`)

    fd = Feeder(N0, M, U, B=1_000_000, L=1 << 15, logK=19, f=0.97, p_est=0.055, exclude=cover_primes)
    for fb in fd.window(k0):            # K = 2^logK members k0 .. k0 + K - 1, cut into K / L blocks of L members
        fb.k          # u64[nsel]   k of the selected members: the ceil(L (1 - f)) emptiest, ascending count, ties ascending k
        fb.cnt        # u16[nsel]   their survivor counts
        fb.offs       # i64[nsel+1] CSR offsets into fb.rows
        fb.rows       # u16[tot]    their alive rows (indices into U), ascending within a member
        fb.alive_total, fb.hm_all, fb.hm_kept   # sum of counts over all L members; sum of (1-p_est)^count over all / over selected

`np.argsort(counts, kind="stable")[:keep]` is the selection of `search.run_block`; the hit masses are summed over the histogram, so they
agree with numpy's to 1e-12 relative, not bit for bit.  One `Feeder` per thread (it owns a K x rows bit matrix: 64 MB for 2^19 members
and 1011 rows); the C calls release the GIL, so threads run in parallel; `Feeder(sv=other.sv)` shares the read-only sieve context.
`L` is the selection block and may be any power of two dividing `K` (`2^15` reproduces `run_block`'s blocks exactly; `2^19` selects among
more members for the same `f`).  Survivor rows of a member are tested in this order and the tests stop at the first probable prime.

Reference numbers of the GPU session (850-row cover, k0 = 4,293,885,952, L = 32,768, B = 1e6, f = 0.97) are reproduced:
alive total 12,459,413, counts sha256 704be04a..., 984 kept, first members j = 24236, 12679, 14788, 27793, 11914, hit mass 2.899909e-06 / 2.059896e-05.
