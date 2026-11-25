# Working backwards: where a batching factor of about 250 would have to come from (25 November)

Reaching 200,000 with the present budget means disposing of e^36.5 candidates with about e^31 units of work: a factor of about 250
over one-at-a-time scanning. A candidate is disposed of in one of two ways. It is cut by the sieve, which needs no exponentiation.
Or it is rejected by finding one prime row N − q, which needs a primality test: no sieve can show that a number is prime.

So any batching mechanism must share work between candidates in one of two places: the sieve (small factors) or the primality
tests. Taking each mechanism in turn, what would two candidates have to share, and is it shared?

**Marks.** **[P]** proved. **[M]** measured. **[O]** opinion.

| mechanism | what it would need two candidates to share | shared here? | number |
|---|---|---|---|
| **Sieving along progressions** | the (row, prime) progression k ≡ (q − N0)·M⁻¹ (mod s) | yes: every member of a window shares it | in use: 3 ns a member, 2.7 nats of selection |
| **Product and remainder trees** | a modulus, so that one exponentiation modulo ∏ n serves all | no: each test is modulo its own n = N0 + kM − q | ≥ 1× the separate tests: 0.98–10.7× at k = 2–64 **[M, uarch]** |
| **Fast multipoint evaluation** | one polynomial evaluated in one ring | the polynomial is shared, G(k) = ∏(N0 + kM − q), but the ring is not: primality of a factor needs arithmetic modulo that factor | ≤ 1× **[P]**; its only use, G(k) mod small primes, is the sieve |
| **Baby-step giant-step** | a group, with varying exponents | the exponents are structured, the groups are not (see below) | ≤ 1× **[P]** |
| **Index calculus / relation reuse** | a relation (a found prime) valid for many targets | a prime P = N − q rejects every even P + q′ (17,984 numbers), all within Q of N; members of a cover are M ≈ 10^193 apart, so none of them is a cover member | the best population where they are: row-sharing families, −10.9 nats **[M]** (`shared_rows.py`) |
| **Lattice reduction** | a low-degree structure vanishing on the candidates | the only polynomial vanishing on the rows has degree 1,502 | radius fixed at ln(X/M) = 16.6 nats for soft CRT decoding **[P]** (`../two_stage/d_answer.md`) |
| **Birthday / meet in the middle** | a split of the constraint into two halves that recombine additively | yes: a knapsack in Z/P | halves the exponent, and representation techniques give about 0.23–0.29 of it; the deficit is 900–1,500 nats **[P]** |
| **Symmetries of the defining polynomial** (Joux's pinpointing, Frobenius) | an automorphism mapping candidates to candidates and rows to rows | U is a set of primes with no affine symmetry; the only structure is the CRT on the cover's moduli, which the cover already uses; the pair structure does not depend on the classes **[P, Lean]** | none |

## Baby-step giant-step, exactly

- For a fixed row q and members k, the Fermat residue is 2^(n_k − 1) = A·B^k (mod n_k), with A = 2^(N0 − q − 1) and B = 2^M.
- If A mod n_k and B mod n_k were known, each test would cost about log₂ k ≈ 24 squarings instead of about 664: 27 times cheaper.
- But A and B are powers with exponents of about 640 bits. Reducing them modulo n_k is a full exponentiation each, and modulo ∏ n_k
  it is the tree above. **[P]**
- The same holds for a fixed member and varying rows: 2^(N_k − 1 − q) needs 2^(N_k − 1) modulo each n_{k,q}.
- So the exponent's structure (geometric in k, a shift in q) is real but unusable without a common modulus. A common modulus costs
  at least the sum of the separate tests, by the tree measurement.

## The common obstacle

Every mechanism that batches exponentiations needs a ring shared by the candidates. Ours are 1,502 distinct moduli per member, in
progressions whose common difference M is coprime to all of them. **[P]**

The mechanisms that do share something (sieving, birthday, lattices) act on the sieve side: residues modulo small primes. There the
deficit is 900 nats or more, and the radius 16.6.

So the factor of 250 would need one of two things:
- a primality detector shared by distinct moduli (H2's batch form; uarch's measurements, and `../H2_one_page.md`, find none);
- or a sieve-side structure that is not random, and the measurements in §8 of `README.md` show U carries none.

**[O]** If a fourth currency exists, it is a new primality-detection idea or a new kind of family, not a new way of organizing these
eight mechanisms.
