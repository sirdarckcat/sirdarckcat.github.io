# A structured prefix beats random classes: the Erdős–Rankin block, and a rigorous D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)²

Status: the consultant's note of 25 Nov 2026, 12:50 UTC. Paper-level proof (standard analytic inputs, none proved here), written out line by line at the Lean session's request; nobody else has read the write-up.
The idea is the Lean session's: its second referee read (`goldbach/lean/scripts/cover_prefix_check/README.md`, section (d), branch `ccr-36ca7b46-8twf14`, commit 9eb7e2a; the device is Erdős–Rankin's). The proof below replaces its pair sieve by an average over the common integer, which needs less. The counts on real primes in section 3 are mine; the Lean session's exact counts are cited as its.
Scripts and outputs: `data/limit_check/` (`coherent*.py`, `out_coherent*.txt`).

Notation: ln₂ = ln ln, ln₃ = ln ln ln, ln₄ = ln ln ln ln. Rows are the odd primes q < Q. Moduli are the odd primes t ≤ x; one class c_t per modulus strikes the rows q ≡ c_t (mod t) (q = t is struck by the class 0). D(n) is the largest Q for which some classes on the first n odd primes strike every row below Q; r is the n-th odd prime, so r ~ x.

## 0. What this says

1. **Theorem.** There is c > 0 such that, for all large x, classes on the odd primes up to x strike every odd prime below Q = ⌊c·x·ln²x·ln₃x/(ln₂x)²⌋. So D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)² for large n.
2. This beats every constant times r·ln r, in particular the theorem of the Lean library (`GoldbachGaps/CoverBound.lean`, constants A < 1.349) and my draft `PAIR_COVER.md` (1.352), which are statements about a smaller order.
3. Through the Chinese remainder theorem it gives infinitely many even N with no Goldbach summand below c·ln N·(ln₂N)²·ln₄N/(ln₃N)²: take x ≈ ln N, so ln x = ln₂N, ln₂x = ln₃N, ln₃x = ln₄N (Rankin's bound for prime gaps, ln N·ln₂N·ln₄N/(ln₃N)², with one more logarithm, because only primes have to be struck).
4. The device also breaks the premise of every argument for a limit of D(n)/(r ln² r): "the small moduli can do no better than random classes". The research session's limit 1.1275, its replacement of order r·ln² r/ln ln r, and my check of that replacement (`LIMIT_CHECK.md`, asymptotic verdict) all used it. **My verdict that the ratio tends to 0 is withdrawn.** What survives is in section 4.
5. At the sizes that can be computed nothing changes (section 3.2).

## 1. The idea

Give every modulus t of a block B = (z, w] (w = x/4) the class N₁ mod t, one integer N₁ ∈ (Q, 2Q] for all of them. Then t strikes q exactly when t divides N₁ − q, and the block strikes q exactly when N₁ − q has a prime factor in (z, w]. A row survives only if n = N₁ − q has no prime factor in (z, w]. Since n < 2Q < w² there is at most one prime factor above w, so n is z-smooth, or n = a·p with p > w prime and a < 2Q/w having all its prime factors ≤ z. Both are rare: the smooth numbers have density ρ(u), and the numbers a·p with p prime above x/4 are about (ln(2Q/w)/ln Q) of the integers below 2Q, that is O(ln₂x/ln x). Random classes leave ln z/ln w of the rows. Classes of different moduli above √N₁ never strike the same row here, where random classes overlap.

The rest of the cover is ordinary: each odd prime up to z takes its fullest class among the rows still alive (a factor 1 − 1/(t − 1) each, at least), and each prime in (w, x] strikes one row.

## 2. Proof

Take w = x/4, ln z = ln x·ln₃x/(3·ln₂x), Q = c·x·ln²x·ln₃x/(ln₂x)² with c fixed at the end, M = 2Q/w (so ln M ≤ 2·ln₂x), and let P be the odd primes below Q. Inputs, all classical:

* (F1) Chebyshev: π(X) ≤ C₀X/ln X; and the prime number theorem: π(x) − π(x/4) ≥ 0.7·x/ln x for large x.
* (F2) Brun–Titchmarsh: an interval of length h ≥ 2 contains at most 2h/ln h primes.
* (F3) Mertens: ∏_{3≤t≤z}(1 − 1/(t − 1)) ≤ C₂/ln z.
* (F4) Smooth numbers, by Rankin's trick (derived here, no deep theorem needed). For any σ > 1/2, Ψ(X, z) ≤ X^σ·∏_{t≤z}(1 − t^(−σ))^(−1). Take σ = 1 − η/ln z with e^η = u, u = ln X/ln z. By convexity e^(ηs) ≤ 1 + (e^η − 1)s on [0, 1], so Σ_{t≤z} t^(−σ) ≤ Σ_{t≤z}(1/t)(1 + (e^η − 1)·ln t/ln z) = ln ln z + O(1) + (e^η − 1)(1 + o(1)) (Mertens), and the terms t^(−2σ) add O(1). Hence Ψ(X, z) ≤ C·X·ln z·exp(−u ln u + u). Here u = (1 + o(1))·3 ln₂x/ln₃x = o(ln₂x), so u ln u = 3 ln₂x·(1 − o(1)) and Ψ(2Q, z) ≤ Q/(ln x)^(2−o(1)) (the factor ln z ≤ ln x costs one power).

**Step 1: the block, averaged over N₁.** For N₁ ∈ (Q, 2Q] let L(N₁) be the rows q ∈ P with no prime factor of N₁ − q in (z, w]. For q ∈ L(N₁), n = N₁ − q lies in [1, 2Q) and (by section 1) is either (i) z-smooth, or (ii) n = a·p, p > w prime, a < M. Count pairs (N₁, q):

* (i) at most Ψ(2Q, z)·π(Q), choosing n first and then q.
* (ii) at most Σ_{a<M} Σ_{w<p≤2Q/a} #{q prime: Q − ap < q ≤ 2Q − ap, q < Q}. Each inner interval has length at most Q, so by (F2) holds at most 2Q/ln Q primes; and by (F1) there are at most C₀·2Q/(a·ln(2Q/a)) ≤ 2C₀Q/(a·ln w) primes p. So (ii) ≤ (4C₀Q²/(ln Q·ln w))·Σ_{a<M} 1/a = O(Q²·ln₂x/ln²x).

Dividing by the Q choices of N₁, some N₁ has

  |L(N₁)| ≤ C₁·Q·ln₂x/ln²x,

because the average of (i) is at most Ψ(2Q,z)π(Q)/Q ≤ Q/(ln x)^(3−o(1)) by (F4), which is smaller than the right side. Fix this N₁ and give every t ∈ B the class N₁ mod t.

**Step 2: the small primes.** Take the odd primes t ≤ z in increasing order. Let S be the set of rows still alive. All rows of S except possibly q = t lie in the t − 1 nonzero classes mod t, so the fullest class holds at least (|S| − 1)/(t − 1) of them; give t that class. Then |S| becomes at most |S|·(1 − 1/(t − 1)) + 1. After all of them, by (F3),

  |S| ≤ C₂·|L(N₁)|/ln z + π(z) ≤ 3·C₁C₂·Q·(ln₂x)²/(ln³x·ln₃x) + z.

**Step 3: the top primes.** The odd primes in (w, x] number at least 0.7·x/ln x − 1 by (F1). Take them in any order; each one takes the class of one row still alive (if the row is q = t itself, the class 0). Every row is struck once |S| ≤ 0.7·x/ln x − 1.

**Step 4: the numbers.** With Q = c·x·ln²x·ln₃x/(ln₂x)² the bound of Step 2 is 3·C₁C₂·c·x/ln x + z, and z = x^(o(1)). So c = 1/(8·C₁C₂) is enough for large x. ∎

The classes on the odd primes up to x are then realised by an integer N (Chinese remainder theorem, N < 2∏t, ln N = (1 + o(1))x), and N − q is divisible by a modulus t < N − q for every prime q < Q, which is item 3 of section 0.

Checks I made on the steps: n = N₁ − q ≥ 1 because N₁ > Q > q; n < 2Q < w² for large x, so at most one prime factor above w and (ii) is exhaustive; the sum in (ii) counts each (N₁, q) at most once since the factorisation n = a·p with p > w prime is unique; in (F4) the condition z ≥ (ln X)^(1+ε) holds since ln z ≫ ln₂x; the slack of Step 2 accumulates to at most π(z).

## 3. Numbers

### 3.1 Rows left by the block against random classes

Real primes, rows = the odd primes below Q, block (z, x/4], N₁ the best of 50 integers from Q up, z the best of 10, 20, ..., 2,560 (`coherent_surv.py`):

| x | Q | block (z, x/4] | left, common integer | left, random classes ln z/ln w | ratio |
|---|---|---|---|---|---|
| 10⁴ | 610,000 | z = 80 | 0.519 | 0.560 | 0.93 |
| 10⁵ | 9,000,000 | z = 160 | 0.433 | 0.501 | 0.86 |
| 10⁶ | 40,000,000 | z = 160 | 0.293 | 0.408 | 0.72 |
| 3.75·10⁶ | 60,000,000 | z = 160 | 0.212 | 0.369 | 0.57 |

(Q is capped at 6·10⁷ by the prime table, so for the last two Q/x is smaller than ln²x and the ratio is favourable by some tens of percent. The Lean session's exact count at Q = 6·10⁷ with N₁ = 2²⁶: block (406, 937,500] leaves 32.3% against 44.0%, ratio 0.735, and its leading-order formula ρ(u) + ln(ln N₁/ln w) gives 31.9%.) Its asymptotic table, w = x/4, Q = x ln² x, best z: ratio 0.98, 0.91, 0.81, 0.66, 0.55, 0.46, 0.37, 0.22, 0.07 at ln x = 9.2, 13.8, 20.7, 34.5, 50, 69, 100, 230, 1000; half as many rows only near x = 10²⁵. I have not recomputed that table, only its direction.

### 3.2 A cover built from the block, at x = 10⁴

Block (z, y], greedy classes on the odd primes up to z, greedy classes on the primes in (y, x], N₁ the best of 200 from Q up, Q found by bisection (`coherent_D.py 10000`): D/(x ln²x) = 0.39 to 0.48 for y = x/4 (z from 10 to 500), 0.31 at best for y = x/2, and no complete cover for y = 3x/4 at any z tried; plain greedy reaches 0.71 at x = 10⁴. The structured prefix loses at this size: it spends the moduli up to x/4 on a rigid choice and gives up the gain of 27% that greedy classes on the moduli up to x/ln x make (`LIMIT_CHECK.md`, 3.2), and the research session's constrained recursion reaches 1.0 at 9,973. It starts to pay only where the survivor ratio of 3.1 has fallen far enough, which is x far beyond 10⁶.

## 4. What this changes

* **The proved order.** For large n, D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)². Together with the proved upper window D(n) ≪ r^(4+ε) (r^(2+ε) under Elliott–Halberstam), the order of D(n) is open between these. Not formalisable in Lean soon: it needs the smooth-number estimate and Brun–Titchmarsh (the averaging and the greedy lemma of Step 2 alone could be); the inputs (F1) to (F4) are classical, and (F4) is elementary.
* **`LIMIT_CHECK.md`.** The capacity form for the top primes and every measurement stand. What goes: the premise that the small moduli leave what random classes leave, up to a Gaussian saving of 2/√(ln x) from the entropy of their settings. The block is a family of settings with entropy about ln x nats (one integer N₁) whose effect on the rows left is unbounded (ratio to random: 0.07 at ln x = 1000), so the lower tail of the alive count is not Gaussian. My test of a structured prefix ("all classes 1") used the wrong family: q ≡ 1 (mod t) says that q − 1 has a prime factor in the block, the rows q − 1 are shifted primes with no complementary prime, and the effect in the ratio does not appear (it left 1.09 to 1.18 times the rows of a random prefix). The block uses N₁ ≥ Q and the complement N₁ − q.
* **The limits.** "D(n) ≤ (e^γ/(2C₂) + o(1))·r ln² r/ln ln r" is not derived, by the research session's entropy argument or by my capacity check, and "D(n)/(r ln² r) → 0" is not shown. The count for the top moduli (classes of ln x/ln₂x rows each) applied to the block prefix forbids nothing below about x·ln³x·ln₃x/(3(ln₂x)³) (the Lean session's `block_capacity.txt`; it is the write-up's own count applied to a prefix it had excluded, and not a claim that covers exist there, which would need a second moment). Nothing contradicts the earlier numbers: the rigorous lower bound here is below r ln² r/ln₂ r.
* **The law ln g0 = θ − c·Q/ln² x, the constrained recursion, the plateau.** They describe the covers the entropy count sees, which is what can be computed. The block's covers are rare and isolated at these sizes; the count can end where typical covers end and D(n) can still be larger, once the structured ones exist. At x ≤ 10⁶ the block is not competitive (3.2).
* **`PAIR_COVER.md`.** Its argument is correct as far as I checked it, for the order r ln r; the order is superseded here.
* **The 200-digit game.** Nothing moves: 89 to 1,228 moduli, x ≤ 10⁴.

## 5. What I did not check

* The constants (C₁, C₂, c) are not computed; the argument gives existence of c.
* (F4) is derived above by Rankin's trick in a few lines that I have checked once; the sharper saddle-point estimates of de Bruijn and Hildebrand–Tenenbaum are not needed (they would only improve the power of ln x, not the result).
* The heuristic extension (large top classes, x ln³x·ln₃x/(ln₂x)³), and the Lean session's capacity table.
* Whether still better prefixes exist (blocks at several scales, different integers in different blocks): likely, and the true order of D(n) is open.

## 6. Reproduction

`data/limit_check/`: `coherent_surv.py` (3.1; needs numpy and a prime table to 7·10⁷, built inside), `coherent_D.py 10000` and `coherent.py 10000 0.72` (3.2).
