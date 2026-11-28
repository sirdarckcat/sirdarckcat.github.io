# How many members must be read to output one in the top e^−κ of its window (25 November)

This is the model the alignment work arrived at, stated as precisely as I can, with what is proved in it. It turns "scanning is the
only currency for random boxes" into theorems in two models. Their hypotheses say what a fourth currency has to break.

**Marks.** **[P]** proved here, under the hypotheses stated. **[M]** computed at the fleet's parameters. **[O]** opinion.

## The model

- **The window:** members k ∈ [0, K), with N = N0 + kM. Here K = X/M = e^16.6.
- **Later primes:** s_1, …, s_n, all of them above the cover's moduli, with P = ∏ s_i ≫ K.
- **Weights:** for each i, a weight w_i(a) on the residues a mod s_i. These are the rows killed when N ≡ a, or their contribution to
  the survivors. The w_i are independent across i given the cover. This is measured: §8 of `README.md` and the Lean session's pair
  variance.
- **Score:** score(k) = Σ_i w_i(k mod s_i). The window's top e^−κ is score ≥ t_κ.
- **The goal:** output one member with score ≥ t_κ.

Reading weights is never the obstacle: all of them take Σ s_i reads, about 2.6·10⁵ for the primes up to 2,000. The obstacle is
finding k < K whose residues are good. So the bounds below count **members**, either evaluated or produced, not weight reads. A
bound on all computation is out of reach for any explicit problem, so each bound is stated for a class of algorithms.

## Theorem A: random residues **[P]**

**Statement.** Suppose each member's residue vector (k mod s_i)_i is independent and uniform across members (the CRT, idealized).
Then any algorithm that outputs a member with score ≥ t_κ evaluates, at least partly, an expected e^κ·(1 − o(1)) distinct members.
It therefore reads at least as many residues.

**Proof.** Each member is in the top independently, with probability e^−κ. Information about one member says nothing about another.
So after touching T members, the probability of having touched a top member is at most T·e^−κ. Summing over T gives
E[T] ≥ Σ_T (1 − T e^−κ)⁺ ≥ e^κ/2. A finer count gives e^κ(1 − o(1)). ∎

## Theorem B: enumerative CRT algorithms **[P]**

**The class.** The algorithm knows every weight and may enumerate any sub-progression S(I, a) = {k < K : k ≡ a_i (mod s_i) for
all i ∈ I}, for any set I and any residues a, adaptively. It pays one unit per member listed and one unit per residue vector tried.
Within S(I, a), the residues at the primes outside I are independent and uniform: Theorem A's idealization, restricted to those
primes.

**Statement.** Write P_I = ∏_{i∈I} s_i, and let π(I, a) be the chance that a member of S(I, a) is in the top. Then

    E[cost] ≥ min over (I, a) of  max(1, P_I/K) / π(I, a).

**Proof.**
- A member listed from S(I, a) is in the top with probability π(I, a), independently of everything listed before.
- If P_I > K, then S(I, a) is empty except for a share K/P_I of the residue vectors a. So reaching one member of it costs
  P_I/K tries on average.
- So every unit of cost buys a success with probability at most max over (I, a) of π(I, a)/max(1, P_I/K). Wald's identity gives the
  bound. ∎

**At the fleet's parameters [M].**
- Take the 200,000 cover, the survivors at 10⁸, and z = the threshold in sd. A pin at i moves the score by ΔS_i survivors. In the
  Gaussian approximation, π grows by a factor e^(z·ΔS_i/σ).
- Only pins with P_I ≤ K are not penalized. That allows two primes. The best two, 523 and 503, have the heaviest classes relative
  to their means.
- They save **0.49 nats at κ = 4.2** (the fleet's 1.5% cut), 0.89 at κ = 10, 1.67 at κ = 30 and **3.08 at κ = 95** (the depth of
  the ideal members).
- This is in the unit-cost model. A sub-progression of K/(503·523) = 81 members costs the GPU sieve about 10⁵ times more per member
  than a full window (research session: 440,000 ns a member at 2⁷, against 3 at 2²⁴). So with the real sieve, plain scanning is the
  optimum of this class.
- Even counted at unit cost, pinning never gains more than about 3 nats, against a prize of 3 to 11.

## Statement C: additive algorithms (open)

- The CRT makes the problem a knapsack in Z/P: k = Σ e_i·t_i (mod P), with t_i ∈ A_i (the good residues) and target [0, K). An
  algorithm may add partial solutions.
- Meet in the middle and representation techniques belong to this class. In the exchange rates of §7 they charge
  (ln s + KL)/2 per soft-constrained prime, or about 0.23–0.29 of the deficit, so they reach 0.39–0.85 rows per nat. That is below a
  pin (0.94) and below the cover's last modulus (1.47) at our parameters. **[P under the stated costs]**
- A lower bound for this class would be a lower bound for random knapsacks over a product of small cyclic groups. None is known.
  Generic-group bounds do not apply, because the decomposition into Z/s_i is explicit.
- So within the additive class, the statement is: no known algorithm beats pinning plus scanning at these parameters. It is not a
  theorem.

## What a fourth currency has to break

The hypotheses of A, B and C name the exits.
- **Independence of the weights given the cover** (A, B). Structured boxes would break it, and §8 measures them absent: the cover
  has no first-order handle on U mod a later prime.
- **Members produced only as sub-progressions** (B), **or as sums of them** (C). A fourth currency must produce integers below K
  whose residues at many later primes are jointly controlled, by an operation that is neither an intersection of progressions nor an
  addition.
  - The known non-additive constructions are polynomial values, which keep a share 1/d of the range and whose structure is not
    aligned with the boxes (§5), and products, whose residues are uniform. Both lose.
  - **[O]** A construction with multiplicative structure, aligned with boxes that come from additive data (which rows are left),
    would be new mathematics. I do not see where it would come from.
- **The window constraint, k < K.** It changes only through the cover, which is pinning (rate 1, already optimized).
