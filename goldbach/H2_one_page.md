# H2: compositeness detection cheaper than one modular exponentiation, for the cover search

Each statement is marked. **[P]** proved, here or by a standard argument. **[L]** known in the literature; "checked" means checked
today at the abstract level. **[M]** our measurement. **[O]** my opinion. Written 25 November 2026 for the research session and the
lead. It sits beside `goldbach/phd/wp9/h2_open_problem.md` and Lemma 3 of `wp9_closure_theorem.md` on the lead's branch.

## 1. Statement and cost model

- **What the search sees.**
  - A member N of a cover has S survivors n_i = N − q_i. Each has b bits: 660 at 200 digits, 6,600–7,300 at our sizes.
  - Each survivor is coprime to every prime ≤ B (B = 10⁹ in our runs) and is prime with probability p' ≈ e^γ·ln B / ln n.
    That is 1–4% in our runs and the uarch session's. **[L: Mertens and the prime number theorem as a heuristic. M: 1/138.5
    measured against 1/137.0 predicted at 2,196 digits.]**
  - The member is a hit exactly when all S are composite. It is rejected at its first prime, which now costs about 1/p' base-2
    Fermat tests.
- **Cost unit.**
  - One modular exponentiation (modexp) costs E(b) = Θ(b·M(b)) bit operations, where M(b) is the cost of a b-bit
    multiplication: about b squarings mod n. **[P: square-and-multiply.]**
  - A Fermat test takes as long as about 495 products a·b mod n at 662 bits, and 4,740 at 6,641 bits. **[M]**
  - "Cheaper" means o(b·M(b)), or in practice a fraction f < 1 of a Fermat test.
- **H2, in the negative form on which the closure theorem rests:**
  - Take n uniformly random among the B-rough integers of b bits.
  - No randomized algorithm, with one-sided error (it may answer "don't know", but never "composite" for a prime), says
    "composite" with probability ≥ c > 0 on composite n in time o(b·M(b)).
- **The two forms the search can use.**
  - (a) *A per-number detector.* It costs f modexps and has recall r on composites, with Fermat run on what it passes. The test
    cost per member is then multiplied by about f + 1 − r. **[P: the arithmetic of the pipeline.]**
  - (b) *A per-member detector.* It decides "some survivor is prime" in o(1/p') modexps without finding which one. Nothing of
    this kind is known. **[O]**

## 2. What a positive answer is worth here

- **Measured costs per hit** **[M]**:
  - 2,196 digits: 9.1 CPU-hours of tests (501,670 Fermat tests at 65.6 ms), 1.0 of sieve (619 s + 305 s on 4 threads), 0.2 of
    cover.
  - 1,997 digits (running): 0.9 CPU-hours of sieve; about 8 of tests expected.
  - 200 digits, the lead's engine: Fermat tests take at least 95% of wall time.
- **Gain with the sieve and cover held fixed**, G(f) = ln(C / (C − (1 − f)·C_test)), in nats:

  | f (test cost as a fraction of a Fermat test) | 1/2 | 1/10 | 1/100 | → 0 |
  |---|---|---|---|---|
  | 2,196 digits [M] | 0.58 | 1.59 | 2.08 | 2.15 |
  | 200 digits, sieve share ≤ 5% (a lower bound) | 0.64 | 1.93 | 2.82 | ≥ 3.00 |

- **Re-tuning cannot give more than ln(1/f) in all.** Re-tuning means sieving less, cutting shallower, or testing more members.
  For any strategy, C_sieve + f·C_test ≥ f·(C_sieve + C_test), so the new optimum costs at least f times the old one. **[P]**
- **In digits.**
  - Between 2,000 and 1,500 digits the cost rises by about ln(180/8) ≈ 3.1 nats (the research session's 180 CPU-hours at 1,500
    digits, against about 8 at 2,000). That is about 160 digits of record per nat. So f = 1/10 would be worth about 250 digits
    here. **[M plus research's estimate]**
  - At 200 digits, one nat is about 2 digits on the lead's frontier, where "each 10× ≈ +2.3 nats ≈ 4 digits". **[lead's M]**

## 3. What is known against it

- **Every known test needs a full-size exponentiation.** Each compositeness test with constant soundness on rough inputs raises
  something to a power of size about n, in a ring over Z/nZ. **[L: Grantham's figure checked (arXiv 1908.02394); the rest standard
  (Crandall–Pomerance), not rechecked.]**
  - Fermat, Solovay–Strassen and Miller–Rabin: one modexp each.
  - Lucas and Frobenius: 2 to 3 modexp-equivalents; Grantham's QFT is at most 3 Fermat tests.
  - BPSW: Miller–Rabin plus Lucas.
  - AKS: works in a polynomial ring and costs far more.
  - Elliptic-curve tests and ECPP: point multiplications.
- **Local tests see nothing after the sieve.**
  - Take a test whose answer depends only on n mod m, where every prime factor of m is ≤ B. Primes and B-rough composites in
    [X, 2X] are both asymptotically equidistributed over (Z/mZ)*, so the test has no advantage.
  - This holds for m up to a power of log X (Siegel–Walfisz, and the fundamental lemma for rough numbers), and on average for
    m up to X^(1/2−ε) (Bombieri–Vinogradov). **[L: standard; not rechecked]**
  - So trial division, wheels, product and remainder trees, and Bernstein's batch gcd see only the factors below their bound,
    which the sieve has already used.
  - Going on to a bound B' finds a factor with probability about 1 − ln B/ln B', at the cost of a residue for every prime in
    (B, B']. **[P: Mertens]**
- **Cheap global functions carry no signal on their own.**
  - For a non-square composite n, the Jacobi symbol (a/n) is a nontrivial character mod n. It is +1 and −1 equally often on
    (Z/nZ)*, exactly as for a prime n. **[P]**
  - gcd(a, n) > 1 for a random a with probability Σ_{p|n} 1/p < (log₂ n)/B. **[P]**
  - Each costs 1/40 of a Fermat test at 200 digits and about 1/1,300 at 2,000 digits here (measured on a loaded machine). **[M]**
  - They become a test only when combined with an exponentiation, as in Euler's criterion.
- **Bit-pattern detectors in restricted classes are ruled out.**
  - Majority reduces to primality under AC0 reductions, so primality is not in AC0[p] (Allender, Saks and Shparlinski, JCSS
    2001). **[L, checked]**
  - μ is asymptotically orthogonal to every AC0 function of the binary digits (Green, CPC 2012) and to Walsh functions
    (Bourgain, J. Anal. Math. 2013). The sum of the binary digits of primes is equidistributed (Mauduit and Rivat, 2010).
    **[L, checked]**
  - These exclude detectors computable by bounded-depth circuits on the bits, not detectors of general polynomial cost.
- **There are no lower bounds in general models.**
  - A proof of H2 needs an average-case lower bound of order b·M(b) ≈ b² for a problem in P. No superlinear time lower bound is
    known for any explicit problem on general RAMs. **[L: the standard barrier; not rechecked]**
  - The only bound on exponentiation itself covers the multiplication route: an addition chain for e has length at least log₂ e
    (Brent and Zimmermann, *Modern Computer Arithmetic*). **[L, checked]** It says nothing about algorithms that read the bits of
    n, and neither do generic-ring bounds. **[O]**
- **Partial advantage.** I found no result bounding the advantage of a sub-modexp test with recall r < 1 on rough inputs, in
  either direction. **[L: searched, nothing found; the search was not exhaustive]**

## 4. Near misses: engineering, not H2

- **Sharing work among the survivors of one member.**
  - The S Fermat tests have nearly the same exponent: 2^(n_i − 1) = 2^(N − q_max − 1) · 2^(q_max − q_i).
  - So one exponentiation modulo P = ∏ n_i, followed by a remainder tree, gives all S results. But it costs b·M(S·b) ≥
    S·b·M(b), no less than S separate tests. **[P for this scheme]**
  - A common divisor of n_i and n_j divides q_i − q_j, so any coupling between the survivors goes through primes below Q, which
    the cover and the sieve have already used (Lemma 2(i) of wp9). **[P]**
  - Whether some other kind of sharing helps is open. I know of no candidate. **[O]**
- **SIMD and vector batching.** It lowers the constant, not the b·M(b) scaling. The uarch session measures 2.2× gmpy2 at 6,644
  bits and expects 4–6× from its loop version, which is ln 6 ≈ 1.8 nats at most. **[uarch's M]**
- **Deeper sieving.**
  - Going from B to B' multiplies the Fermat tests per member by ln B/ln B' and the sieve cost by about π(B')/π(B).
  - The chance that a member is a hit does not depend on B to first order: p'·S ≈ e^γ·rows·ln X/ln N. **[P at heuristic level;
    M: the survivors' mean and sd are within 0.5% of the prediction in both runs]**
  - At 2,196 digits, B = 10¹⁰ would save about 10% of 9.1 CPU-hours of tests for about 8 more CPU-hours of sieve. The trade is
    tuned already. **[M plus arithmetic]**
- **Ordering the survivors.** Every survivor is prime with the same p' to first order, so no order of testing kills a member
  sooner. **[O: consistent with the 138.5 measured against 137.0]**

**Verdict [O].** For detectors with constant recall, negative H2 is very likely true, and it cannot be proved with today's
lower-bound techniques. What remains is constants (vector kernels, at most about 1.8 nats) and the cover, which sets the
exponent.
