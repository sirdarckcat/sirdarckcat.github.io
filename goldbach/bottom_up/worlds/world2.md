# World 2: linear coupling (list recovery of polynomial CRT codes)

This page answers the research session's request of 26 Nov, 00:15 UTC, for Worlds 2 and 4. Marks: **[P]** proved, **[M]** measured,
**[O]** opinion. Here "the room" means the window of members, measured in nats.

## The dictionary

| our problem (Z) | F_q[t] | coding |
|---|---|---|
| the window N0 + kM, k < K; room ln K = 16.6 | deg N < n; room n ln q | dimension n |
| the later primes s > 463, residue field Z/s | monic irreducibles π of degree d, residue field F_{q^d}, norm Q = q^d | positions; with degree-1 places, Reed–Solomon of length m ≤ q |
| the weights w_s(a): rows killed at N ≡ a (Poisson, mean \|U\|/s, \|U\| = 1,502) | soft weights g_π | soft information |
| the heaviest fraction ρ of the classes | hard lists L_π, \|L_π\| = ρQ | list recovery |
| rate: 16.6 / 1,496 = 0.011 for the places 467–1,999; about 10⁻⁷ for the places to 10⁸ | n / Σ deg π | R |
| target: the top e^−κ (κ ≤ room), e^(room − κ) outputs | the same | an exponential output, not a short list |

**What the members we want look like.** They agree with the lists at a rate ρ(1 + δ), with
δ ≈ √(2(1 − ρ)κ / (ρ m_eff)). For example, δ = 0.39 at ρ = 1/2, κ = 16.6, with the 213 places below 2,000.

## W2.1: Johnson-type decoding is never cheaper than scanning [P, given the decoding radius, in the CRT model with a Gaussian tail]

**The decoders.** These are Guruswami–Sudan, Koetter–Vardy, and Guruswami–Sahai–Sudan (GSS) for CRT codes.

**The decoders' guarantee.** They return every N with G(N) = Σ_π g_π(N mod π) ≥ √(ln K · Σ_π ‖g_π‖² / ln Q_π). In F_q[t], replace
ln by the degree.

**Only the occupied classes need weight [P].** This correction is the research session's (26 Nov, 03:43 UTC).
- At a place Q the window occupies min(Q, K) classes. Weight on any other class helps no member.
- Above K, each occupied class holds one member, and its label is that member's own index (k mod Q = k).
- The first two versions of this page weighted every class. For consecutive primes that overstated the decoder's input 7,000 to
  25,000 times (table below).

**The theorem.** Suppose such an N exists at depth κ of G. Take residues at distinct places as independent and uniform over the
occupied classes (the CRT idealization) and the tail as Gaussian. Then

    M′ := Σ_π (ln Q_π)/min(Q_π, K)  ≥  ln K − 2κ·a,      a = the largest (ln Q_π)/min(Q_π, K) among the places used.

For K ≥ 467, a = ln 467/467 = 0.0132, unless some place above K exceeds e^(0.0132 K).

**Proof.** On the occupied classes O_π, write g_π = ḡ_π + d_π, where ḡ_π is the mean over O_π and Σ d_π = 0 there.

- **The mean part.** U = Σ ḡ_π is the same for every member, so it carries no information. By Cauchy–Schwarz,
  U ≤ √(M′ · A) with A = Σ |O_π| ḡ_π²/ln Q_π. The cheapest choice is ḡ_π ∝ ln Q_π/|O_π|.
- **The deviation part.** D(N) = Σ d_π(N mod π) has mean 0 and variance at most a·B, where B = Σ ‖d_π‖²/ln Q_π.
- **The member.** At z standard deviations, G(N) ≤ √(M′·A) + z√a·√B ≤ √(M′ + z²a) · √(A + B).
  This is Cauchy–Schwarz on the two parts together.
- **The guarantee.** Its right-hand side is √(ln K)·√(A + B).
- Set z = √(2κ). ∎

The split into mean and deviation is the research session's (26 Nov, 01:12 UTC). The first version of this page bounded the two
parts separately, which gave the looser (√(ln K) − √(2κa))².

**The hypothesis.** The tail is Gaussian when the deviation is spread over many places and over the classes at each. It fails for
weightings concentrated on a few classes, pins being the extreme case. A decoder could then certify a thin set of members deep in its
own weighting. Research's verifier flagged that case as open for its second page (26 Nov, 03:52 UTC). W2.1b treats it without the
tail.

**What the theorem says.**
- **[P] The deviation enters only at second order.** It is the only informative part, and it contributes 2κa ≤ 0.026·ln K.
- **[P] The decoder needs places above K.**
  - The primes from 467 to K give M′ ≤ ln(K/467); the exact sums are 0.07 below it.
  - That leaves the decoder about 5.8 nats short at every window size measured (ln K from 8 to 18.4). In general it falls short for
    every window below e^233.
- **[P, in the model] It names every member.**
  - Every certified member therefore needs weight at a place above K. There its class is the member itself.
  - Weights that carry no information on which members are deep must therefore name every member: at least one weighted class
    per member (research).
  - So the decoder is the enumeration of the window with its threshold moved slightly. It is never cheaper than the scan.
- **[P, in the model] Its cheapest place set.**
  - Each weighted class buys a mass of ln Q/min(Q, K)². That falls as Q grows to K and then rises as ln Q/K².
  - So the cheapest set is the primes from 467 to some y0 in full, plus places above K as large as the model allows.
  - Keeping a = 0.0132 caps those places at ln Q ≤ 0.0132 K. At ln K = 16.6 the cheapest set is then the primes to y0 = 1.2·10⁵,
    plus 811 places that each name the whole window: 851 weighted classes per member.
  - Without that cap, one place of ln Q ≥ K ln K names the window once: one class per member, the floor.
- **The real tables.** The classes that strike a row have density about 1,500/p.
  - Their mass converges to about 1.8 (Ein(3.2)), against ln K = 16.6.
  - Above K they add only about 1,500·ln(ln y/ln K)/K.

**Exact prime sums [M] (`johnson_cost.py`, `johnson_cost.out`).** Weighted classes per member of the window:

| window ln K | depth κ | consecutive primes 467..y | per member | cheapest with a = 0.0132: primes 467..y0, places above K | per member | without the cap | previous version (every class) |
|---|---|---|---|---|---|---|---|
| 16.88 (research's window) | 16.88 | y = 1.45·10⁸ = 6.8 K | 7.5·10⁶ | y0 = 1.39·10⁵, 821 | 861 | 1 | — |
| 16.6 | 16.6 | y = 1.10·10⁸ = 6.8 K | 5.7·10⁶ | y0 = 1.21·10⁵, 811 | 851 | 1 | 3.9·10¹⁰ |
| 16.6 | 8.3 | y = 1.13·10⁸ | 5.9·10⁶ | y0 = 1.20·10⁵, 828 | 868 | 1 | 5.9·10¹⁰ |
| 16.6 | 4.2 | y = 1.15·10⁸ | 6.0·10⁶ | y0 = 1.20·10⁵, 836 | 876 | 1 | 7.3·10¹⁰ |
| 12.4 | 12.4 | y = 1.67·10⁶ | 1.2·10⁵ | y0 = 13,327, 667 | 708 | 1 | 8.9·10⁸ |
| 8 | 8 | y = 20,959 | 2,120 | y0 = 1,259, 519 | 552 | 1 | 1.8·10⁷ |
| 4 (about the window left by two pins) | 4 | y = 643, every place above K = 55 | 27 | — (no place has a ≤ 0.0132) | — | 1 | 5.7·10⁵ |
| ln 2 | ln 2 | y = 467: two classes at one prime (research) | 1 | — | — | 1 | 2.5·10⁴ |

- **Research's figures** are for consecutive primes at ln K = 16.88: y ≈ 1.5·10⁸, 1.7·10¹⁴ classes and 8·10⁶ per member. This
  script gives 1.45·10⁸, 1.6·10¹⁴ and 7.5·10⁶.
- **[O] The decoder's work exceeds its input.** Interpolating over moduli of 10⁸ nats or more is not counted here: the 811 places of
  2.1·10⁵ nats each, or the one place of K ln K.

**In F_q[t].** The window is deg N < n, with q^n members.
- The places of one degree e ≤ n carry a mass of at most 1.
- Above degree n, each occupied class is one member, since a polynomial of degree < n is its own residue. A place of degree e
  carries e/q^n (research).
- So the layers up to n and about one more suffice: of order q^(2n)/n weighted classes, quadratic in the window. The previous
  version's members^1.95, times a factor from the starting degree, assumed every class weighted.
- Larger places lower the cost as in Z, down to one class per member.

**Your Guruswami–Sudan statement [P].**

- **Full agreement.** With degree-1 places, list recovery needs agreement τ > √(nρq/m) ≥ √(nρ), so full agreement needs n < 1/ρ. The
  same holds for any places, since Σ_{deg π = d} d ≤ q^d. Confirmed.
- **The agreement our members have.** At τ = ρ(1 + δ), GS needs n < ρ(1 + δ)², so it returns no member of degree ≥ 1. At q = 467 and
  ρ = 1/2, the region GS guarantees and the region where members exist (n ln q ≥ m·KL(τ‖ρ)) are disjoint.
- **The weighted Johnson radius on the primes 467..y,** for y ≤ K, is √(ρ ln K / 2) = 2.88√ρ. That is at least 2.9 times the random
  agreement at every ρ, and above 1 (unreachable) for ρ > 0.12.
  - Places above K lower it, to √(ρ K ln K/y) for y ≫ K. But each listed class there is one member.
  - It reaches the random agreement ρ only at y ≈ K ln K/ρ, which is about K² weighted classes.

## W2.1b: which sets a Johnson-type decoder can certify, without the Gaussian tail [P, given the radius]

**The statement.**
- A set C of members of the window is certified by some choice of weights if and only if, for every probability distribution μ on
  C,

      Σ_π ln Q_π · Σ_a μ(N mod π = a)²  ≥  ln K.

- For given weights with support W, every set C that they certify satisfies

      Σ_{(π,a) ∈ W} ln Q_π · c_{π,a}²  ≥  |C|² · ln K,      where c_{π,a} is the number of members of C in class a at π.

**The proof.**
- A member N is returned when ⟨g, x_N⟩ ≥ √(ln K)·‖g‖. Here x_N is the indicator of N's classes, and ‖g‖² = Σ g²/ln Q.
- Average over μ, then apply Cauchy–Schwarz: ⟨g, Σ_N μ_N x_N⟩ ≤ ‖g‖·(Σ_W ln Q·(Σ_N μ_N x_N)²)^½. Both inequalities follow, as
  necessary conditions.
- For sufficiency, the normalised weights and μ range over compact convex sets and the form is bilinear, so the minimax theorem
  applies. The optimal weights, g = ln Q·Σ_N μ_N x_N, are nonnegative, as the decoders require. ∎

**What it gives.**
- **Pairs.** Expand the second form: Σ_{N∈C} Λ_W(N) + Σ_{N≠N′} λ_W(N, N′) ≥ |C|² ln K.
  - Λ_W(N) sums ln Q over the places where N's class is weighted.
  - λ_W(N, N′) sums ln Q over the weighted places where N and N′ share a class.
  - Two members share a class at π exactly when Q_π divides k − k′. So λ_W < ln K always.
  - For pairs that look like random members of the window, the mean λ̄ is at most Σ_{467≤Q≤K} ln Q/Q = ln(K/467) − 0.07 = 10.38
    at K = e^16.6. The class tilt of the deepest members adds about 0.25.
- **[P] Capacity.** |C| ≤ (Λ − λ̄)/(ln K − λ̄), where Λ is the sum of ln Q over the places used. For deep members that is at most
  (Λ − 10.6)/6.0. With places only up to y < K the pair term is about ln(y/467), and the bound is tighter.
- **[P] Naming.** On average the certified members must be named at weighted places of total norm at least (ln K − λ̄)·|C|, at
  least 6.0·|C| nats. At a place above K a weighted class names a single member.
- **[M] Thin sets are cheap once named** (`johnson_named.py`, `johnson_named.out`: exact prime sums, with weights on the members'
  own classes at the primes from 467):

  | given members | places needed | Λ | pair term | weighted classes a member | the scan, per member of the top \|C\| |
  |---|---|---|---|---|---|
  | 10 | to 641 (26) | 164 | 0.30 | 26 | 1.6·10^6 |
  | 100 | to 2,027 (217) | 1,527 | 1.43 | 217 | 1.6·10^5 |
  | 1,000 | to 13,841 (1,546) | 13,271 | 3.33 | 1,546 | 1.6·10^4 |
  | 10,000 | to 112,663 (10,587) | 111,799 | 5.42 | 10,587 | 1,620 |

  - So for thin, strongly tilted sets the radius is not the obstacle.
  - The obstacle is naming them without their scores. Weights computed from the tables alone make G a separable score of its own,
    and the decoder lists the top of G above the Johnson threshold.
  - Whether some such G has a top that is thin, deep in S and cheaper to reach than by scanning is World 4's selection problem
    (W4.4, W4.5), not a decoding question.

**[M] Concentrated weightings on the integers reduce to a try** (`johnson_capacity.py`, `johnson_capacity.out`).
- Put weight ln Q on the j heaviest classes at each of the first n primes from 467. A member is returned when the places where it
  lies in a weighted class have total norm at least √(ln K·j·Λ_n).
- In the CRT model, the expected number returned from a window of e^16.6 is:
  - j = 1: at most 0.149, at n = 3. That is the member, if there is one, in the heaviest class at 467, 479 and 487: a try of
    Theorem B. It is 3.0·10^−4 at n = 4, 1.5·10^−3 at n = 5, and smaller beyond.
  - j = 2: at most 7.7·10^−8 (n = 6). j = 3: 1.6·10^−12. j = 5 and 10: below 10^−20.
- Members deep in the score lie in the heaviest classes more often. Give every place the tilt of a member 5 standard deviations deep
  toward the heaviest class at 467, a factor of about 4.5 (an exponential-tilt estimate). Even then the window's five or so members
  at that depth are returned with probability under 4·10^−6 a window.

## The Johnson barrier on generic lists: the research session's claim of 26 Nov, 00:41 UTC, checked

**The exact forms.**
- **Reed–Solomon, confirmed verbatim.** Theorem 3 of Sudan's survey (AAECC 2001, after Guruswami–Sudan) returns every p with k
  coefficients such that Σ_{i : p(x_i) = y_i} w_i > √(k(ε + Σ_i w_i²)), over distinct pairs (x_i, y_i). A list is several pairs
  sharing one x_i. With unit weights this gives agreement > √(k m ℓ).
- **The integers.** The survey quotes three bounds, for K ≤ p_1 ⋯ p_k with the primes sorted:
  - Goldreich–Ron–Sudan: n − √(2nk log p_n/log p_1);
  - Boneh: n − √(nk log p_n/log p_1);
  - Guruswami–Sahai–Sudan: n − √(n(k + ε)), with weights favouring the small moduli.
- **The weighted form used here,** Σ_agree w_i ln p_i ≥ √(ln K · Σ_i w_i² ln p_i), is the same interpolation in the ideal-code frame.
  Its unit-weight case is Boneh's bound. The Guruswami–Sahai–Sudan paper itself could not be read from here.

**(i) The algebra, per agreement set: correct.** Fix the agreement set A, with every l_i = l ≥ 2.
- The guarantee and a first moment K·∏_A (l/p_i) ≥ 1 give a² ≥ ln K · l · a ≥ (a − |A| ln l) · l · a.
- So the mean of ln p_i over A is at most l ln l/(l − 1). For l = 1 they force A = everything, with total inside the room.

**(ii) The premise undercounts [P].**
- A member exists if some agreement set works. The first moment is K · P(Σ_i B_i ln p_i ≥ a), with B_i independent Bernoulli(ρ_i).
- It carries the entropy of the choice of A, about C(m, |A|). So it can be ≫ 1 while every single A has K∏_A ρ_i ≪ 1.
- **A counterexample to (i) as a statement about the decoder.** Take m equal places of norm p, with lists of l = ρp.
  - The guarantee starts at t* = √(ln K · m l/ln p) agreements. That is below the typical ρm once m ≥ ln K · p/(ρ ln p).
  - Example: p = 467, l = 233, ln K = 16.6 needs m ≥ 2,521. At m = 3,000, t* = 1,375 < 1,500.
  - Then about half of all members are guaranteed. Yet the mean of ln p over their agreement sets is 6.15, above l ln l/(l − 1) = 5.47.

**(iii) The correct statement [P, given the radius].**
- Typical members are guaranteed iff (Σ ρ_i ln p_i)² ≥ ln K · Σ ρ_i min(p_i, K) ln p_i, counting occupied classes only.
- By Cauchy–Schwarz this needs the mass Λ_ρ = Σ ρ_i ln p_i/min(p_i, K) ≥ ln K.
- Members at depth κ need M′ ≥ ln K − 2κa (W2.1).

**(iv) Reed–Solomon (places t − a, m ≤ q): the claim holds [P asymptotically; M at q = 467].**
- The guarantee needs τ > √(kρq/m) ≥ √(kρ). Existence needs k ln q ≥ m·KL(τ‖ρ).
- These are incompatible once q · min_u u·KL(√(kρ/u)‖ρ) > k ln q.
- At q = 467 that is 41 > 6.2 (k = 1, ρ = 1/2) and 307 > 18.4 (k = 3, ρ = 1/8). Equivalently, Λ = m/q ≤ 1 < k.
- So on generic lists the decoder returns nothing beyond pins for every k ≥ 2.

**(v) The integers [P, M].**
- Λ grows like ln(y/467) up to K and like (θ(y) − θ(K))/K beyond, so the guarantee does meet existing members. With consecutive
  primes that happens at y ≈ 6.8 K.
- But the places above K name the members one by one: at least one weighted class per member (W2.1). So it is not vacuous, just
  never cheaper than the scan.
- **The research session's moral stands:** list recovery certifies few consistent codewords; we are in the regime of e^(room − κ) of
  them.

## W2.2: folding and multiplicities buy nothing for separable scores [P]

**What a separable score gives.** A score that is a sum over places gives product lists for folded symbols (L_a1 × … × L_as). It
gives cylinder lists for multiplicities: the value in L_a, every derivative allowed.

**Folding.** Take the Guruswami–Rudra / Parvaresh–Vardy interpolation with s-folding, r variables and multiplicity μ.

- The constraints are N_f (s − r + 1)(ρq)^r C(μ + r, r + 1); the monomials of weighted degree D are D^(r+1) / ((r+1)! (k − 1)^r).
- Decoding needs the agreeing windows to exceed D/μ. That is, a per-place agreement

      β > ( ρ(k − 1) · s/(s − r + 1) )^(1/(r+1)).

- This grows with r when ρ(k − 1) < 1, and is impossible when ρ(k − 1) ≥ 1. So the best is r = 1, which is plain Guruswami–Sudan.
- The linear-algebraic version (Guruswami–Wang) needs the window agreement above (ρq)^r/(r + 1), which is worse.

**Average-case lists.** These conditions depend only on the list sizes. So random product lists fare exactly as worst-case product
lists, and the subfield counterexamples do not enter.

**Multiplicity codes.** With cylinder lists, membership ignores the derivatives. List recovery of the multiplicity code is then
exactly RS list recovery at the same points.

**So** every beyond-Johnson decoder needs lists that correlate coordinates. Separable scores never produce them, in F_q[t] or
anywhere else.

**In the many-solutions regime.**
- **[P]** The conditions above fail for dense product lists whatever the size of the output.
- **[O]** The decoders' certificates cannot hold e^(room − κ) generic members anyway. Those certificates are at most L roots, or (in
  Guruswami–Wang) an affine subspace of dimension at most s − 1. For random lists the deep members span the room, so any subspace
  that contains them is the whole room, and enumerating it is scanning.
- **The linearisation route (Arora–Ge style)** turns a list of size ℓ into a degree-ℓ equation in the coefficients. It needs about k^ℓ
  places, so it works for constant ℓ only, and that is again the few-solutions regime.

## (b) What folding uses, and prime powers

**Folding uses three things.**
1. A ring automorphism, f(X) ↦ f(γX). It preserves the room and permutes places whose residue fields are isomorphic.
2. The identity f(γX) ≡ f(X)^q (mod X^(q−1) − γ). This bounds the number of solutions of Q(X, f, f∘σ, …) = 0.
3. Lists that correlate the folded coordinates.

**On Z [P].**
- Aut(Z) = {1}. The residue fields Z/p have pairwise different sizes, so no symmetry can permute places. The maps that keep the
  window an interval, x ↦ ±x + c, fix every place.
- So (1) and (2) are absent. (3) is absent in both worlds for separable scores (W2.2), so their absence costs nothing here.

**The nearest substitute for (1) [P/O].**
- Gal(K/Q), for a Galois number field K, permutes the primes above p, which have isomorphic residue fields.
- But a rational N is Galois-fixed, so its conjugate residues coincide and carry no information.
- Members in O_K would be a different problem.

**Multiplicities on Z [P].**
- N mod p² ≅ (N mod p, δ_p N mod p), where δ_p N = (N − N^p)/p is Buium's p-derivation. It is a bijection, since
  δ_p(N + pt) ≡ δ_p N + t.
- But δ_p is not a derivation (δ(ab) = a^p δb + b^p δa + p δa δb), and it differs for each p. So the chain rule that the multiplicity
  decoders use does not exist.
- And a score of N mod s gives cylinder lists in it anyway.

**Prime-power accounting [P].**
- A modulus s^e ≤ K contributes e ln s/s^e to Λ and costs s^e of input. Λ falls by e/s^(e−1) per place (1/233 at s = 467, e = 2), and by
  e/s^(2(e−1)) per unit of input.
- The hard-list GS condition worsens by √(2/s) per place.
- The extra digits of N are redundancy that a score of N mod s cannot constrain. So prime powers never help decoding here.

## (a) Which known algorithms are output-priced in our regime

- **Interpolation through places of total norm at most the room.** This is pinning (Theorem B): n places of degree 1 in F_q[t], two
  primes ≥ 467 in Z. It is the only one.
- **Johnson-type decoders.** The guarantee needs places above the window's size, and there the input names the members one by one.
  That is at least one weighted class per member, and about 850 under the Gaussian model's own condition (W2.1). Without that
  condition, certified sets must be named at about 6|C| nats of places, and weightings concentrated on heavy classes return at most a
  try (W2.1b).
- **Folded RS, multiplicity and subspace-design codes.** They need sparse lists (ℓ ≤ |Σ|^O(ε)) that correlate coordinates. Our lists
  are dense and product (W2.2).
- **Bleichenbacher–Nguyen noisy polynomial interpolation and noisy Chinese remaindering [O].** These have full agreement and a single
  planted solution, which a lattice finds as an unusually short vector. Our problem has e^(room − κ) partial-agreement solutions and
  nothing planted.

So the obstruction in this world is the integers' obstruction. It is not the missing automorphism; it is dense product lists at
near-random agreement with an exponential output.

| ingredient | used by | on Z? | substitute and its cost |
|---|---|---|---|
| CRT and interpolation through places of norm ≤ room | pins | yes | — |
| interpolation with multiplicities, then root finding | GS, KV | yes: Coppersmith/Howgrave-Graham lattices (Boneh; GSS) | same radius, at lattice-reduction cost |
| degree as the size of a residue | the radius | yes (ln) | — |
| a place-permuting automorphism that preserves the room | folding | no: Aut Z = 1, residue fields of different sizes | Galois conjugates in O_K; rational N are fixed, so nothing is gained |
| f(γX) ≡ f(X)^q mod E | folding's list bound | no | none |
| derivatives with a chain rule | multiplicity codes | partly: δ_p on Z/p², not a derivation, one per prime | irrelevant here (cylinder lists) |
| lists that correlate coordinates | every beyond-Johnson decoder | no, and not in F_q[t] for separable scores | — |
