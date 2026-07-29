# Open problem H2 — sub-modexp compositeness detection on rough inputs

Self-contained statement, extracted from the WP9 Divisor-Paradigm
Closure Theorem (wp9_closure_theorem.md, Lemma 3), where it is the
single identified escape from the cost floor of Goldbach-desert search.
Suitable for posting (MathOverflow / a note); constants quantified from
a live computation.

## The problem

Let X → ∞, and let n be uniformly random among integers in [X, 2X]
with no prime factor below B₀ = (log X)^{O(1)} ("rough" inputs — what a
wheel/sieve leaves behind). Let M(b) denote the bit-complexity of
b-bit multiplication.

**Does there exist a randomized algorithm that decides compositeness of
n with soundness ≥ 2/3 (one-sided error allowed: it may say "don't
know", but must say "composite" correctly with probability ≥ 2/3 when n
is composite) in time o(M(log X)·log X) — i.e., asymptotically cheaper
than one modular exponentiation?**

Variants of interest, in decreasing strength:
1. Constant recall r > 0 at cost c·(modexp) with c·(1/r) < 1 — any
   such detector strictly improves the Fermat-first pipeline.
2. Amortized/batch version: given n₁, …, n_k (distinct, pairwise
   near-coprime by construction), certify compositeness of a constant
   fraction of the composites among them in o(k) modexps total.
   (Product-tree trial division reaches divisors ≤ B efficiently; the
   question is strictly about the beyond-B composite mass.)
3. Non-uniform/preprocessing version: polynomial advice depending on X
   (but not n) allowed.

## Known art (why the floor sits at one modexp)

- Trial division / batch gcd (Bernstein product trees) certify exactly
  the small-divisor mass; on B-rough inputs their recall is 0 by
  construction.
- Jacobi/Kronecker symbols, quadratic characters: equidistributed on
  rough composites; soundness o(1).
- Fermat, Euler, Miller–Rabin, Frobenius tests: all cost Θ(M·log X)
  (one modexp or a small multiple); nothing cheaper is known with
  constant soundness, and we found no literature giving a
  sub-modexp bound in either direction. The AKS line lowers proof
  complexity, not detection cost.
- Lower bounds: none known in any realistic model (this is the
  interesting half — even a conditional lower bound in a restricted
  arithmetic-circuit / straight-line model would be new and would
  finish our Lemma 3).

## Quantified downstream consumer (why we care, with live numbers)

The Goldbach-desert record engine (this repository) spends ≥95% of its
wall time executing exactly this primitive: base-2 Fermat tests of
~660-bit rough integers at ~10⁶–10⁷ tests/s/GPU, ~17 tests per
candidate, ~e^{20.8}–e^{37.7} candidates per record campaign
(measured: 1.2×10⁹ candidates banked; next targets 1.7×10⁹ and
2.4×10¹⁶). A detector at cost c and recall r improves throughput by
factor 1/(c + (1−r)) (run detector first, Fermat only on survivors):
e.g. c = 0.25, r = 0.5 gives 1.33×; c = 0.1, r = 0.9 gives 5×. Because
record difficulty is log(compute) (measured frontier: each 10× ≈ +2.3
nats ≈ 4 digits of record), any such detector converts directly into
records — and into savings for every prime-hunting project (GIMPS,
PrimeGrid) built on the same primitive.

## Status

Open in both directions, to our knowledge. The desert-search closure
theorem (wp9) is stated conditional on the negative answer (H2); a
positive answer breaks the cost floor of an entire family of
computational number theory searches, which is the more interesting
outcome.
