# A constant above 1.349 by striking two rows with one prime: the argument, its constant, and the gaps

> **Superseded in order, 25 Nov 12:50 UTC.** `COHERENT_BLOCK.md` proves, at paper level, a depth of order r·ln² r·ln₃ r/(ln₂ r)², above every constant times r·ln r. The argument below is, as far as I checked it, correct for what it states (a constant of about 1.352 on r·ln r), which is now a statement about a smaller order.

Written 2026-11-25 for the research session (its request of 09:10 UTC; the consultant session of the map, branch
`ccr-cdb2641a-5zg8un`). Status of everything below: **paper-level, not Lean** (the inputs are Lavrik-type almost-all Hardy–Littlewood and
Selberg's sieve, neither in Mathlib, and the first has ineffective constants). I did not run any of it as a proof; the numbers in
section 7 and the Euler-product identity in section 4 I computed.

## 0. Answer in five lines

* **(A)** The reduction (rainbow matching of rows, deletion bound, expectations) is correct as stated. One condition is the
  finishing inequality `R − m ≤ π(y) − π(z₁)`.
* **(B)** The inputs exist, with one range problem that decides which theorem has to be cited: every difference that a label
  prime r ∈ (αy, y] divides is at least r ≈ Q/ln Q, so the pair counts needed are for **shifts of size ≍ X**, not ≤ X^(1−ε).
  Mikawa's range (X^(1/3+ε) ≤ H ≤ X^(1−ε)) does not contain them; the long-range almost-all statement (Lavrik; Wolke 2x ≤ y) does.
  The survival weights carry exactly, and the Hardy–Littlewood singular series cancels against them identically (section 4).
* **(C)** Outcome: a proof of an explicit **c₁ ≈ 1.3523 (> e^γ/(2C₂) = 1.34897)**, complete modulo two items named in section 9:
  the exact form of the long-range theorem, and a routine averaging lemma for the weights. If the label term has to use Selberg's
  constant 8 per pair as well, c₁ ≈ 1.3512. The gain is 0.2%: it is limited by the Selberg constant 48 for the triple count,
  not by the deletion method (if every second moment had its predicted value the same argument gives 1.479).
* Pigeonhole alone cannot beat 1/κ in any order (section 8).
* Not formalisable in Lean in any reasonable time; as a map box its status would be "paper".

## 1. Setting and statement

y large; z₁ = y/ln y; α ∈ (0,1) fixed; P₁ = odd primes ≤ z₁ (stage 1); M = primes in (z₁, αy]; L = primes in (αy, y];
Q = ⌊c·y·ln y⌋ with c fixed; rows ℛ = odd primes < Q. A *class vector* gives each odd prime r ≤ y a class a_r ∈ {1,…,r−1}; r
*strikes* q if q ≡ a_r (mod r). If every row is struck then (Chinese remainder theorem) some even N < 2∏_{3≤r≤y} r = e^((1+o(1))y)
has r | N − q for some r ≤ y for every odd prime q < Q, so g(N) ≥ Q and `max_{N ≤ X} g(N) ≥ (c + o(1)) ln X ln ln X` (y = (1 + o(1)) ln X).
The Lean library has this for every c < 1/κ, κ = 2C₂e^(−γ) = 0.741308, 1/κ = 1.348967.

**Theorem (to be proved).** Let c₁ be the root of ρ(1 − δ(ρ)) = 1 with c₁ = ρ/κ, where
δ(ρ) = max_α u / (16·[(c_v/2)·u + c_l·ρ(1 − α)/8]), u = α ln²(1/α), and c_v = 48·(26/25) = 49.92, c_l = 1 (or 64).
Then for every c < c₁ and all large y there is a class vector striking every odd prime below c·y·ln y.
Numerically c₁ = 1.35233 (c_l = 1) or 1.35123 (c_l = 64); the maximising α is 0.203.

## 2. The reduction

Stage 1: independent uniform a_s ∈ {1,…,s−1} for s ∈ P₁. S = rows not struck by P₁, R = |S|.

**Lemma 1 (completion).** Assume Q < (αy)². Let G be the graph on S with q ~ q′ iff some r ∈ L divides q′ − q, the *label* of the
edge. Every edge has exactly one label (two labels would give (αy)² < rr′ ≤ q′ − q < Q). If G has a rainbow matching F (disjoint
edges, distinct labels) of size m and R − m ≤ |M| + |L|, then classes on M ∪ L strike all of S.

*Proof.* For (q, q′) ∈ F with label r put a_r ≡ q ≡ q′ (mod r); it is nonzero because r | q forces q = r and then r | q′ forces q′ = q.
The other R − 2m rows go injectively to the other |M| + |L| − m primes (row q adjacent to every prime except q itself); by Hall's
condition this is possible when |M| + |L| − m ≥ R − 2m (a set of at least two rows is adjacent to every prime). ∎

**Lemma 2 (deletion).** For a simple graph with labelled edges let X = Σ_v C(deg v, 2) + Σ_ℓ C(e_ℓ, 2), e_ℓ the number of edges
with label ℓ. For every t ∈ [0, 1] there is a rainbow matching of size ≥ t|E| − t²X.

*Proof.* Keep each edge independently with probability t. The expected number of kept edges is t|E|; two distinct edges conflict
if they share a vertex (at most one, the graph is simple) or a label, and X is at least the number of conflicting pairs, so the
expected number of conflicting kept pairs is ≤ t²X. Delete one edge of every conflicting kept pair. ∎

**Lemma 3 (averaging over stage 1).** Fix a constant t ∈ [0, 1], the same for every outcome ω of stage 1. By Lemma 2 applied to G(ω),
m(ω) ≥ t|E(ω)| − t²X(ω) pointwise, so R − m ≤ R − t|E| + t²X pointwise, and some outcome has R − m at most the expectation
E[R] − t·E|E| + t²·E[X]. Hence it suffices that `E[R] − (t·E|E| − t²·E[X]) ≤ |M| + |L| = (1 + o(1)) y / ln y`. With the best
t = E|E| / (2E[X]) the saving is `E|E|² / (4E[X])` (here t ≈ ln²y / y, far below 1). No concentration is needed.

## 3. Stage-1 moments

*First moment of R.* A row q > z₁ is unstruck with probability ∏_{s∈P₁}(1 − 1/(s−1)) = κ(z₁) = ∏_{3≤s≤z₁}(s−2)/(s−1) ∼ 2C₂e^(−γ)/ln z₁
(Mertens, proved in the Lean library); the π(z₁) = O(y/ln²y) rows ≤ z₁ change this by a factor ≤ 2 and are negligible. So
`E[R] = (1 + o(1))·π(Q)·κ/ln y = (1 + o(1))·ρ·y/ln y` with ρ = cκ.

*Survival of a set T of rows > z₁:* `Pr[T ⊂ S] = ∏_{s∈P₁}(1 − ν_s(T)/(s−1))`, ν_s(T) the number of residues of T mod s (all nonzero).
At s = 3 a pair survives only if the two rows are congruent mod 3 (then probability 1/2); a triple only if all three are.

*Local identity (the cancellation).* For k = 2, 3 and a prime s ≥ 5 let ρ_s(ν) = (1 − ν/(s−1))/(1 − 1/(s−1))^k be the survival factor
relative to independent rows and σ_s(ν) = (1 − ν/s)/(1 − 1/s)^k the Hardy–Littlewood local factor of the prime k-tuple, ν = number of
residues of the tuple mod s. Averaged over the equally likely offset patterns, ρ_sσ_s has mean exactly 1.
For k = 2 (probabilities 1/s, (s−1)/s of ν = 1, 2): the numerator is (s−2)/s² + (s−3)(s−2)/s² = (s−2)²/s² and the denominator
((s−2)/(s−1))²((s−1)/s)² is the same. For k = 3 (probabilities 1/s², 3(s−1)/s², (s−1)(s−2)/s² of ν = 1, 2, 3) both are (s−2)³/s.
(The pair case is the Lean statement `sum_rho_mul_sigma` of `CoverPairs.lean`.)

## 4. The edge count: a lower bound

For a pair {q, q + d} with d = 6rj (r ∈ L), the pair survives with probability w(d) = ½·Π·∏_{p | j, 5 ≤ p}(p−2)/(p−3)
where Π = ∏_{5≤s≤z₁}(s−3)/(s−1): primes of P₁ dividing d are exactly the primes dividing 6j (j ≤ J ≈ c ln y/(6α) ≪ z₁ < r).
The Hardy–Littlewood density of such a pair is 𝔖(d) = 4C₂·((r−1)/(r−2))·∏_{p | j, p ≥ 5}(p−1)/(p−2) (3 | d gives the factor 2).
Hence `w(d)·𝔖(d) = 2C₂·Π·(1 + O(1/r))·h(j)` with h(j) = ∏_{p | j, p ≥ 5}(p−1)/(p−3) = Σ_{e | j} b(e),
b multiplicative, b(p) = 2/(p−3); so `Σ_{j ≤ J} h(j) = J·M₀ + O((ln J)²)`, M₀ = ∏_{p≥5}(1 + 2/(p(p−3))).

**Euler-product identity.** With P₀ = ∏_{p≥5}(1 − 1/(p−2)²), C₂ = ¾∏_{p≥5}(1 − 1/(p−1)²):
(1 − 1/(p−1)²)(1 − 1/(p−2)²)(1 + 2/(p(p−3))) = [p(p−2)/(p−1)²]·[(p−1)(p−3)/(p−2)²]·[(p−1)(p−2)/(p(p−3))] = 1
for every prime p ≥ 5, so **C₂·M₀·P₀·4/3 = 1** (numerically 0.99999999 with the primes below 10^7). Since
Π/κ(z₁)² → 4P₀, this gives, for the sum over all differences d = 6rj < Q,
`E|E| = (1 + o(1))·(E[R]²/2)·λ`, λ = Σ_{r∈L} 1/(r−1) ∼ ln(1/α)/ln y — exactly the independent-rows prediction.

*The input.* **(L)** (long-range almost-all Hardy–Littlewood.) For every A > 0 and X ≥ 2, for all but O_A(X(ln X)^(−A)) even h ≤ X/2:
Σ_{n≤X}Λ(n)Λ(n+h) = 𝔖(h)X + O(X(ln X)^(−A)). This is the Lavrik / Vinogradov-type statement (circle method, Siegel–Walfisz major arcs; the
constants are ineffective). **I could not retrieve Lavrik's text.** What I found: Mikawa 1991 (Tsukuba J. Math. 15) and Perelli–Pintz 1992
as quoted in Evans (arXiv 2102.12297): X^(1/3+ε) ≤ H ≤ X^(1−ε), all but O(H(ln X)^(−A)) shifts |h| ≤ H, which is the wrong range; and an
abstract of Baier quoting Lavrik for almost all d ≤ y/2; and Wolke: almost all k ≤ x when 2x ≤ y ≤ x^(8/5−ε), shifts k ≤ x up to half the prime
range y. The argument needs shifts up to Q/3 with prime range X = Q − h (so h ≤ X/2 ⟺ h ≤ Q/3); X varies with h, handled by a grid of
O(1/η) prime ranges and Selberg's bound for the leftover n-interval (relative error η, then η → 0).
Restricting to differences d ≤ Q/3 keeps the fraction f = 5/9 of all pairs.

Evaluating Σ_{r∈L}Σ_{j: 6rj ≤ Q/3} w(6rj)·N(6rj), N(h) the prime pairs below Q: `E|E_f| ≥ (1 − o(1))·f·(E[R]²/2)·λ`, f = 5/9.
(The terms of the exceptional shifts are dropped, which only lowers a lower bound; their number is smaller than the set of differences
by a factor (ln Q)^(A−1).)

## 5. The conflict count: upper bounds

*Vertex term.* X_v = Σ_v C(deg v, 2) counts triples (v; u₁, u₂) with labels r₁, r₂ ∈ L on v u₁, v u₂ and differences ≤ Q/3.
Selberg's upper bound (Halberstam–Richert Thm 5.7): the number of n < Q with n, n+h₁, n+h₂ all prime is ≤ (48 + o(1))·𝔖₃(h₁, h₂)·Q/ln³Q
uniformly in the shifts. With the survival weights (local identity for k = 3: mean 1 per prime), the sum over (r₁, r₂, j₁, j₂) gives
`E[X_v] ≤ (48 + o(1))·g·E[R]³λ²/2`, where g = ∫ deg² dt over the restricted region = 26/81 against 1 for the full graph (degrees as
functions of position t = v/Q: deg(t) = min(t, 1/3) + min(1−t, 1/3) times E[R]λ).

*Label term.* X_l = Σ_r C(e_r, 2). The four rows of two edges of one label are two independent prime pairs, so the count of prime pairs
is a product of two pair counts; the survival weights couple them only through the offset t = q″ − q: for primes s > (ln y)^2 dividing one of the
four numbers t, t − d, t + d′, t + d′ − d the factor is 1 + O(1/s) and each of these integers has at most ln Q/(2 ln ln y) such prime factors, so
the product is 1 + O(1/(ln y ln ln y)) pointwise. Then `E[X_l] ≤ c_l·f²·(E[R]⁴/8)·Σ_{r∈L} 1/(r−1)²`, with c_l = 1 if (L) is available with a
congruence condition modulo e ≤ (ln X)^B (classical for such moduli), and c_l = 64 (Selberg's 8 per pair) otherwise. Σ_{r∈L} 1/(r−1)² ∼ (1 − α)/(α y ln y).

*Lemma W (weights).* In both terms the weights are functions of n = r₂j₂ ∓ r₁j₁ (and of t) of the form Σ_{e | n}ψ(e), ψ multiplicative, ψ(p) = O(1/p).
Averaging over prime labels: for e ≤ y^(1/4) use Bombieri–Vinogradov (on average over e) for the progression r₂j₂ ≡ r₁j₁ (mod e); for e > y^(1/4)
the divisor bound 2^(ω(n)) = y^(o(1)) kills the tail. This gives the same values as averaging over residue classes, i.e. the local identity
applies. This is routine but I have only the outline above (item 2 of section 9).

## 6. Putting it together

R = ρy/ln y, E|E_f| = (f/2)R²λ, E[X] ≤ 48·g·R³λ²/2 + c_l·f²·(R⁴/8)·Σ1/(r−1)², λ = L/ln y with L = ln(1/α). The saving is
`E|E|²/(4E[X]) = R·u / (384·γ_v·u + 2·c_l·ρ(1−α))` with γ_v = g/f² = 26/25 and u = α ln²(1/α).
So `R − m ≤ (1 − δ)R` with δ = u/(399.36·u + 2c_lρ(1−α)); the finishing inequality `ρ(1 − δ(ρ)) ≤ 1` gives c₁ = ρ/κ.

## 7. The constants

| inputs used | δ at α = 0.203 | c₁ |
|---|---|---|
| every second moment at its predicted value (not provable with present inputs) | 0.0878 | 1.4789 |
| Selberg 48 for triples, Lavrik for the label term, all differences | 0.00258 | 1.35246 |
| the same, differences ≤ Q/3 (the range that (L) covers) | 0.00248 | **1.35233** |
| Selberg 48 and 64, all differences | 0.00172 | 1.35129 |
| Selberg 48 and 64, differences ≤ Q/3 | 0.00167 | 1.35123 |

(1/κ = 1.348967. Research's heuristic 0.0855 uses Σ_{r∈L} 1/r² ≈ 1/(αy ln y); the correct value is (1 − α)/(αy ln y), which gives 0.0878.)
A sharper upper bound for the triple count than 2³·3! = 48 improves δ linearly; each factor 2 doubles it.

## 8. What limits the method, and pigeonhole in other orders

* The deletion bound uses only first and second moments. The graph has average degree ≈ yL/ln²y → ∞ and each label has ≈ y/(2 ln²y) edges, so
  a rainbow matching of size close to R/2 almost certainly exists; the proof of anything near that needs near-regularity (a Rödl nibble). Pointwise
  degree bounds need the number of primes in the union of progressions through a fixed row; Brun–Titchmarsh loses ln y/ln ln y there, and the
  asymptotic needs Hardy–Littlewood for triples on average, which is unknown.
* **Pigeonhole alone.** The only guarantees of averaging are: a modulus r can be given a class that strikes at least |S|/(r−1) of the current
  unstruck rows, and at least one while any is left. Using the first on a set A of moduli leaves ≤ π(Q)∏_{r∈A}(1 − 1/(r−1)) rows, which is smallest
  when A consists of the smallest primes; the moduli not in A can only be used one row each, so they must outnumber the rows left. Optimising gives
  c < e^γ/(2C₂) whatever the order or adaptivity (reversing the order makes the averaging steps nearly void, 1 − 1/y each).
* The "missing" constant in practice is large: covers found by search reach 0.72 to 0.88 · x ln² x, which is a factor ln x times the theorem. The
  present argument gains 0.2% in the constant.

## 9. Gaps, named exactly

1. **The theorem (L).** The statement used: all but O(X(ln X)^(−A)) even h ≤ X/2 satisfy the Hardy–Littlewood asymptotic for Σ_{n≤X}Λ(n)Λ(n+h) with
   relative error (ln X)^(−A), for the prime range X = Q − h on a grid. Please check against Lavrik's paper (Dokl. Akad. Nauk SSSR 132 (1960)) or a
   modern treatment, including whether shifts up to X/2 (or up to X) are in range, and whether a congruence condition n ≡ a (mod e), e ≤ (ln X)^B,
   is allowed (it gives c_l = 1 rather than 64). If it only holds for h ≤ X/4 the constant changes in the third digit, not in its sign.
2. **Lemma W.** The averaging of the survival weights over prime labels (section 5). Provable by the truncated divisor expansion above; not written out.
3. **Uniformity of Selberg's bound** in shifts of size ≍ Q (Halberstam–Richert Thm 5.7 is uniform for shifts ≤ x): fine as I read it.
4. The rows ≤ z₁ (which are also moduli) and the grid in X contribute o(1) relative errors; not written out.
5. Everything is for "all large y"; the constants are ineffective (Siegel zeros).

## 10. Where this sits on the map

Box 'Why 1.349 is not the truth: pairs, deletion and the nibble' (research session's sketch and the archipelago measurements) is the heuristic
side. This note would be its rigorous side with status "paper" (draft rigour): 1.3523 for the pair-covering route against the heuristic 1.479 (which agrees with the archipelago session's measured deletion fractions, 1.48 to 1.51). It
does not touch the record at 200 digits.
