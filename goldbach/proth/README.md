# Proth/BLS-certified Goldbach deserts — the height game without ECPP

For even N, g(N) is the least prime p with N − p prime. Every earlier record
in this repo proves the partition N = g + (N − g) with an ECPP certificate
for the complement, and the SoK names that as the wall of the height game
("Game 1"): *"the binding constraint is certifying N−q … arranging N−q to
have Pocklington-friendly form while satisfying the cover congruences would
blow the wall off entirely … nobody knows how to intersect the two
constraint systems."*

They intersect by one line of algebra. (SoK §7.2 had already sketched the
Proth version as an untried angle; this directory carries it out, with
two refinements: a cube-root N−1 test, and complete covers.)

## The construction

Fix a cover {(r, a_r)} of **all** primes below a threshold Q by residue
classes modulo distinct odd primes r, and let g be the least prime ≥ Q in no
class (so every prime below g is in a class, and g is not). Look for N with

    P = N − g = m·2ⁿ + 1.

The cover congruence N ≡ a_r (mod r) reads m·2ⁿ ≡ a_r − g − 1 (mod r), and
2ⁿ is a unit mod r, so it is the congruence

    m ≡ (a_r − g − 1)·2⁻ⁿ  (mod r)

on m. CRT turns the whole cover into m ≡ m₀ (mod M_c), M_c = ∏r; candidates
are m = m₀ + t·M_c, t = 0, 1, 2, …. Choose n with 2³ⁿ > P. Then:

1. **Every prime q < g is excluded by an explicit divisor**: q ≡ a_r ≡ N
   (mod r) for some r, so r | N − q, and N − q is far larger than r. There
   are *no residual primes*, hence no lottery over e^E candidates, no
   strong-pseudoprime witnesses, nothing probabilistic.
2. **P is proved prime by one modular exponentiation.** If
   b^((P−1)/2) ≡ −1 (mod P), every prime factor p of P has ord_p(b)
   divisible by the full power of two F = 2^v in P − 1, so p ≡ 1 (mod F).
   If F² > P that is Proth/Pocklington. If only F³ > P, a composite P would
   be (xF+1)(yF+1) with xy < F and x+y < F; writing (P−1)/F = c₂F + c₁
   forces c₁ = x+y, c₂ = xy, so c₁² − 4c₂ = (x−y)² would be a perfect
   square — one integer square root rules it out
   (Brillhart–Lehmer–Selfridge 1975, Thm 5).
3. The witness base b is fixed in advance: take b among the cover moduli,
   so that P mod b is the same for all candidates, with ((a_b − g)/b) = −1
   (P ≡ 1 mod 4, so this is the Jacobi symbol (b/P)). Then the search's probable-prime test *is* the
   primality proof.

Hence **g(N) = g exactly, and the complete proof is a sieve check of the
cover plus one `powmod` and one `isqrt`.**

The search is a search for one prime in an arithmetic progression: sieve
t by every prime not in the cover up to B, then test survivors; about
ln P / (e^γ ln B) tests are expected.

## Records

| g(N) | digits of N | cover | PRP tests | proof of the partition | directory |
|---|---|---|---|---|---|
| **5,000,251** | 33,938 | 5,342 classes (moduli ≤ 167,107, lazy greedy), complete below g | 68 CPU + 3,072 GPU (Colab A100); the hit is the 3,080th survivor (expected ~2,118) | one `powmod` (5^((P−1)/2) ≡ −1) + one `isqrt`; F = 2^37584 > P^(1/3) | `../records/height_33938digit_g5000251` |
| **2,000,269** | 15,595 | 2,670 classes (moduli ≤ 79,139, lazy greedy), complete below g | 648 (expected ~970) | one `powmod` (11^((P−1)/2) ≡ −1) + one `isqrt`; F = 2^17274 > P^(1/3) | `../records/height_15595digit_g2000269` |
| **1,200,109** | 11,263 | 2,005 classes (moduli ≤ 17,431, paper's greedy), complete below g | 2,647 (expected ~700; a 2% unlucky draw) | one `powmod` (7^((P−1)/2) ≡ −1) + one `isqrt`; F = 2^12477 > P^(1/3) | `../records/height_11263digit_g1200109` |

Previous height records, for scale: g = 1,134,871 (2,692 digits) and
g = 1,157,341 (2,480 digits), each resting on a ~250-step ECPP certificate
(for the latter: ~1.7 h to produce, ~2 h to re-verify independently, ~2 h
of APR-CL) and on ~1,900–3,100 strong-pseudoprime witnesses for the
residual primes.

Verify any record (Python standard library only; gmpy2 is used for the
single modular exponentiation if present):

    python3 verify.py ../records/<dir>/record.json             # 6 s with gmpy2
    NO_GMPY2=1 python3 verify.py ../records/<dir>/record.json  # 102 s, plain Python ints
    python3 ../bls/xverify.py ../records/<dir>/record.json     # second stack, ~90 s
    cd ../records/<dir> && gp -q crosscheck.gp                 # independent PARI/GP path, ~2 min

(timings for the 11,263-digit record on one core; the 15,595-digit record takes 12 s, 270 s and ~8.5 min).

`crosscheck.gp` does not use the cover classes: it lets PARI build and
validate its own N−1 (Pocklington–Lehmer) certificate for P, and brute-force
scans every prime q < g checking that N − q shares a factor with the
primorial of the largest cover modulus.

## Independent replication, and the verification stack

A second session, working separately, arrived at the same construction the
same morning (same n, same complete cover; memo `../phd/wp11_bls_game1.md`)
and certified g = 1,200,109 for a *different* 11,263-digit N
(`../records/bls_game1_11263digit_g1200109`). The two branches reviewed
each other (`../phd/crossreview_*.md`) and were merged
(`../phd/merge_2026-11-21.md`). What that leaves:

- **Three independently written legs, and every record passes all of
  them**: `verify.py` here; `../bls/verify_bls_record.py` and
  `../bls/xverify.py` (the other session's; `interop.py` exports a record
  into their format, in which N is rebuilt from the congruences by CRT);
  and PARI's own N−1 proof with a brute-force scan (`crosscheck.gp` in
  each record directory).
- `tamper_test.py`: 11/11 tampered records are rejected by `verify.py`,
  each for the expected reason.
- The two long waits at 1.2·10⁶ were one stretch of one progression: the
  other search ran over exactly the odd-t half of the candidates searched
  here, 1,341 integers were tested twice, and jointly it is one ~5% event
  (`overlap_check.py`). The candidates neither session had tested were
  then probed exhaustively with `probe.py`: 6 primes among 3,245
  candidates against 4.62 expected, z = +0.64
  (`probe_1200k_result.json`; `../phd/wp12_prime_covering_grh_ledger.md`
  §6). The cost model holds on fresh numbers.

Hashes quoted in prose anywhere in the repo are sha256 of the decimal
string of N; the `SHA256SUMS` / `MANIFEST.sha256` files hash the files.

## Why full covers win here (and lose everywhere else)

REGISTRY.md row A2 marks complete covers "dominated": for Q = 10⁵ a full
cover costs 1,020 digits where a partial cover plus search reaches 150. That
is the right verdict for the *bounded* games, where digits are the score.
In the height game digits are free and the costs are (i) search and (ii)
certification. With (ii) gone:

| design at g ≈ 1.2·10⁶ | digits | expected PRP tests | cost here | certificate |
|---|---|---|---|---|
| megagap-style partial cover + ECPP (record of July) | 2,692 | e^{6.56} ≈ 700 candidates expected, each a run of PRP tests | search + ~6 h of ECPP, re-verification and APR-CL | 253-step ECPP + 1,867 SPRP witnesses |
| same partial cover, BLS-form complement | ~4,050 | 2·e^{4.4}·250 ≈ 40,000 | ~5 core-hours | 1 modexp + ~2,700 SPRP witnesses |
| **full cover, BLS-form complement** | 11,263 | ~700 | ~1 core-hour | **1 modexp, 0 witnesses** |

Leaving 200–500 primes uncovered and trusting luck for them would save
< 10% of the compute; not worth the witnesses.

## Cost model and the ladder

Measured on this 4-core container (GMP via gmpy2; `powmod` of a b-bit
number): 5.8 s at 37k bits, 11 s at 50k, 30 s at 75k, 57 s at 100k, 151 s at
150k (exponent ≈ 2.3–2.6). Full-cover sizes are exact (deterministic
greedy); test counts are expectations at sieve depth 10⁹.

| target g > | cover digits | digits of N | tests | 4-core wall-clock (GMP) |
|---|---|---|---|---|
| 1,200,000 (done; paper's greedy cover) | 7,503 | 11,263 | 703 expected (2,647 used) | 17 min expected (64 min used) |
| 2,000,000 (done; lazy cover) | 10,392 | 15,595 | 973 expected (648 used) | 51 min expected (37 min used) |
| 3,000,000 | 14,617 | 21,936 | 1,369 | ~2.7 h |
| 5,000,000 (done; GPU) | 22,620 | 33,938 | 2,118 expected (3,080 used) | ~11 h expected; done in 44 min of A100 time |
| 10,000,000 | 40,881 | 61,331 | 3,827 | ~3.4 days |
| 16,045,848 (g would be 16,046,137) | 61,162 | 91,753 | 5,725 | ~13 days |

Rows not marked done are costed, not run: cover sizes are exact (the
covers were built), test counts are expectations, and timings extrapolate
the measured `powmod` curve. SoK §6 put the ECPP-bound
ceiling of this game at g ≈ 2.5·10⁶ and classed g > 10⁷ as "ECPP far
beyond practice". The 16,045,848 line is the largest known prime gap of
any kind (its endpoints are 385,713-digit *probable* primes): a certified
Goldbach desert longer than that is ~5,700 PRP tests at 91,753 digits —
about two weeks here, hours on a gwnum-class PRP engine or the repo's GPU
fleet. The search is embarrassingly parallel and resumable
(`tests.jsonl` is the checkpoint).

## GPU screening (Colab A100)

`gpu_screen.py` computes 2^((P−1)/2) mod P for a batch of candidates
P_t = 1 + 2ⁿ(m0 + t·Mc) at once, one row per candidate. It uses 15-bit
limbs in float64, batched cuFFT convolutions, Montgomery reduction with
R = 2^(15L) > 16P, and an exact carry-lookahead kernel for long 0x7FFF
runs. P ≡ 1 (mod 8), so a prime gives 1. The GPU is only a screen: a pass
is re-proved on the CPU by `desert.bls_prove` with the spec's
non-residue base (`gpu_hit.py`), and the record is then packaged by
`package.py` as usual. A wrong GPU answer can cost search time, never a
wrong record.

Every engine version was checked against gmpy2 before use:
- exact residues at 120, 3k and 20k bits;
- the 2·10⁶ spec gives F/T/F at t = 1305..1307;
- the eight known primes of the 1.2·10⁶ progression pass and their 16
  neighbours fail (`gpu_validate*.py`);
- v3 (the default from the 16M rung on) is also bit-for-bit equal to v2
  after each of 40–64 squarings at the 5·10⁶, 10⁷ and 16M sizes.

Throughput on one A100, per test:

| rung | s/test | vs one GMP core |
|---|---|---|
| 5·10⁶ | 0.82–0.92 | ~100× |
| 10⁷ | 2.7 | |
| 16M | ~6.3 expected with v3 (v1 measured 7.8; v2 ~7) | |

The sieve is deepened while the search runs, which removes ~18% of the
expected tests at 10¹¹ and ~25% at 10¹²:
- `deepsieve.c` (GMP `mpn_mod_1`, same root formula as `desert.py`,
  identical kill lists, 8–9× faster per core) runs on the GPU host's
  spare CPUs and on a second Colab CPU runtime.
- `deep_sieve.py` re-checks every kill in gmpy2 and rewrites the
  survivors file atomically.
- `gpu_search.py` re-reads that file, and any `*.kills.json` lists,
  between batches.

For the 16,045,849 rung a CPU fleet runs beside the GPU:
- `cpu_search.py` runs on Colab CPU runtimes, each 8 vCPUs at ~29 tests/h
  (the account allows 7 runtimes in all). Machine j takes the survivors
  with t ≡ j (mod 8), top-down, while the GPU climbs from t = 0.
- Each machine re-reads the relayed survivors and kill lists, and proves
  any pass itself with `desert.bls_prove`.
- The A100 host's CPUs join once their sieve range is done. PRP tests then
  save more GPU time than sieving [3·10¹¹, 10¹²) would (~180 against
  ~100 tests).

Known constant factors not taken: a Montgomery reduction specialised to
P = m·2ⁿ+1 (P⁻¹ ≡ 1 mod 2ⁿ, so the quotient word is free; prototyped and
checked against GMP, but only 17% faster at 52k bits), and the
Konyagin–Pomerance (F ≥ P^{3/10}) or Coppersmith–Howgrave-Graham
(F ≥ P^{1/4+ε}) forms of the N−1 test, which shorten N by 5–11%.

## Covers

`desert.py` builds the cover two ways:

- `--increasing`: the paper's algorithm (odd primes in increasing order,
  each taking its fullest class). Reproduces the paper's table exactly
  (Q = 10⁶: 1,762 congruences, r_max = 15,083, 6,480 digits).
- default (`lazy`): weighted set-cover greedy over all odd primes up to
  3× that r_max, always taking the (r, class) with the best kills/ln r.
  Each modulus is used while its best class is intact, which removes most
  of the one-kill tail: **~10% fewer digits ≈ 30% less search**
  (Q = 1.2·10⁶: 6,787 vs 7,503 digits; Q = 2·10⁶: 10,392 vs 11,522).

Greedy covers reach Q ≈ 0.72·x·ln²x with moduli up to x; what is provable
and what is the ceiling are in `../phd/wp12_prime_covering_grh_ledger.md` §2
(`pigeonhole_table.py` reproduces its table).

## What this does not do

- It does not touch the bounded games T(100,000) and R(10²⁰⁰): there the
  score is the size of N, and this construction spends digits freely.
- N is ~1.5× the modulus of a *full* cover, so the numbers are long
  (11k–100k digits). The integers are stored in full in `record.json`.

## Lean

The announcement that prompted this work presents its result *only* as
Lean. These records are small enough to do the same: the full statement is

    theorem goldbach_desert :
        IsLeast {p : ℕ | p.Prime ∧ (N - p).Prime} g

and its proof needs (a) one lemma, the N−1 criterion above (`orderOf`
reasoning in `ZMod p`, then the two-factor argument); (b) a decidable check
that N lies in every class and every q < g is either in a class or has a
divisor below √g; (c) one modular exponentiation and one square-root
comparison on literals, which Lean's kernel evaluates with GMP.

**Not done in this session.** Installing a Lean toolchain was refused twice
by the session's permission policy (the `elan` installer script, then the
official release archive), and I did not work around it. No unchecked Lean
is committed here on purpose — an uncompiled formal proof is exactly the
kind of artifact the announcement warns against. With a toolchain allowed
this is a few-hundred-line development plus a data file generated from
`record.json`.

## Files

- `desert.py` — cover builders, CRT, sieve, parallel search (`build`, `search`)
- `verify.py` — standalone verifier (stdlib only)
- `package.py` — runs the verifier and the PARI cross-check, writes checksums
- `pigeonhole_table.py` — rigorous worst-case coverage vs greedy (WP12 §2)
- `tamper_test.py` — mutation test for `verify.py`
- `interop.py`, `overlap_check.py` — cross-check against the independent
  pipeline (`../bls/`); the reviews are `../phd/crossreview_*.md`
- `probe.py` — exhaustive prime count over sieve survivors vs the model;
  `probe_1200k_result.json` is its result on the 1.2·10⁶ progression
- `ladder.py` — the cost ladder above, from lazy covers and measured timings
- `gpu_screen.py`, `gpu_search.py`, `gpu_hit.py` — GPU screen (CuPy),
  batch driver, and hit → CPU proof → packaged record
- `gpu_validate.py`, `gpu_validate_v2.py`, `gpu_validate_v3.py`,
  `gpu_bench*.py` — engine validation against gmpy2 and timings
- `deepsieve.c`, `deep_sieve.py` — deeper sieve (C, GMP), streamed into a
  live search; `colab_queue*.sh`, `colab_sieve_chain.sh`,
  `colab_status.py` — the Colab orchestration as run
- `../records/height_*` — one directory per record: `record.json`,
  `N.txt`, `crosscheck.gp`, logs, `SHA256SUMS`
