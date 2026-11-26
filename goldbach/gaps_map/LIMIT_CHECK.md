# Does D(x)/(x ln²x) tend to 1.1275, or to 0? A check of the bulk/top argument (corrected: neither is shown)

Status: the consultant's note of 25 Nov 2026, written at the research session's request (its message of 10:04 UTC, which doubts its own limit 1.1275).
Heuristic, with tests on real primes. Nothing here is a proof and nobody else has checked it.
Scripts and outputs: `data/limit_check/` (all of it runs in under a few minutes on one core).

> **CORRECTION, 25 Nov, about 11:30 UTC (server clock): the asymptotic verdict of this note (the ratio tends to 0) is withdrawn.** The Lean session's second referee read
> (`goldbach/lean/scripts/cover_prefix_check/README.md`, section (d), commit 9eb7e2a on `ccr-36ca7b46-8twf14`) showed that the small moduli
> are not held to what random classes do: giving every modulus of a block (z, x/4] the class of one common integer near Q leaves O(ln ln x/ln x)
> of the rows against ln z/ln x. I checked it (real-prime counts and a line-by-line proof of a rigorous D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)²) in
> [`COHERENT_BLOCK.md`](COHERENT_BLOCK.md). Section 0 below is the corrected verdict. Every measurement in section 3 stands and the capacity form of
> the top phase stands for covers whose small moduli act like random classes; what is withdrawn is the premise of step (1) in section 2, the
> cooperation paragraph of 4 (A), and the limit "→ 0". Where the text below says otherwise it is marked.

Notation. Rows are the odd primes q ≤ Q. Moduli are the odd primes s ≤ x. One class c_s per modulus strikes the rows q ≡ c_s (mod s). D(x) is the largest Q for which some class vector strikes every row.
κ = 2C₂e^(−γ) = 0.741308, so 1/κ = e^γ/(2C₂) = 1.348967. Mertens: ∏_{3≤s≤y}(1 − 1/(s−1)) = (κ + o(1))/ln y.
Bulk = moduli ≤ y₁ = x/ω, top = moduli in (y₁, x]. R(b) = rows the bulk configuration b leaves alive; R₀ = κ·π(Q)/ln y₁ is its mean over random b.

## 0. Verdict (corrected; the first version of this section is withdrawn)

1. **Withdrawn: "D(x)/(x ln²x) tends to 0, like 1.349/(ln ln x − 1)".** The argument bounds D(x) only for covers whose moduli below the top primes leave what random classes leave. The small moduli can be set otherwise. Giving every modulus in a block (z, x/4] the class of one common integer N₁ near Q leaves O(ln ln x/ln x) of the rows where random classes leave ln z/ln x (Erdős–Rankin; found by the Lean session's referee read). That gives a rigorous D(n) ≥ c·r·ln² r·ln₃ r/(ln₂ r)² (`COHERENT_BLOCK.md`, checked line by line), and the capacity count for the top primes applied to such a prefix forbids nothing below about x·ln³x·ln₃x/(3(ln₂x)³) (the Lean session's table; not a claim that covers exist there). So the ratio is not shown to tend to 0 and has no known finite limit. The order of D(n) is open between c·r·ln² r·ln₃ r/(ln₂ r)² and r^(4+ε).
2. **What the capacity argument still says.** For covers whose small moduli act like random classes (the typical covers, which the law ln g0 = θ − c·Q/ln²x and the recursion describe), a complete cover needs the largest classes of the top primes to add up to the rows left. The largest class at s = x/u holds ln x/(ln ln x − 1 − ln u + o(1)) rows and the sum is x/(ln ln x − 1), so D ≤ (1 + o(1))·x ln²x/(κ(ln ln x − 1)) for them, with κ = 0.7413, the constant 1/κ = 1.349 and the "− 1" as the research session has them (§2). That is a bound for those covers, not for D(x).
3. **Two things in the argument were wrong; one I tested wrongly.** (a) Step (1) of §2 assumed a Gaussian lower tail of the alive count, so that the entropy of the small moduli (x/ln x nats) allows only a saving of about 2/√(ln x). The block has entropy about ln x nats and an unbounded effect. My structured-prefix test ("all classes 1", which left 1.09 to 1.18 times the random count) used the wrong family (it made the small moduli coherent too, which leaves only the rows with N₁ − q prime); the right one, classes N₁ mod t with N₁ ≥ Q on the moduli above z only, leaves 0.93, 0.86, 0.72 and 0.57 of the random count at x = 10⁴, 10⁵, 10⁶, 3.75·10⁶ (`COHERENT_BLOCK.md` 3.1). (b) "All R rows struck with probability p^R" is an annealed count, and the capacity form is the right object; that part stands.
4. **Measurements stand, and at accessible sizes nothing changes.** Greedy covers on real primes: 0.55 at x = 151, 0.66 at 2·10³, 0.72 from 2·10⁴ to 10⁵. Greedy classes on the moduli up to x/ln x leave 0.72 to 0.74 of what random classes leave. At x = 2·10⁴ the top classes chosen by greedy add up to 0.915 of the Poisson-max model. A cover built from the block, greedy small moduli and greedy top reaches 0.39 to 0.48·x ln²x at x = 10⁴ against 0.71 for plain greedy, so the block does not pay below x far beyond 10⁶. The fitted model of §3.4 (a plateau to 10⁶, then a slow fall) describes greedy and typical covers, not D(x).
5. **What is not proved**: Poisson class sizes of the alive set mod top primes out to class size ≈ ln x/ln ln x (Hardy–Littlewood for k-tuples in progressions); and, for the structured prefixes, whether better ones than the block exist (blocks at several scales). The lower tail of the alive count is not Gaussian (3a), and I have no replacement for it.

## 1. Where the numbers come from

The proved bound (Lean) strikes one row per top prime: R ≤ π(x) gives Q ≈ x ln x/κ. The conjectured and measured depths are a factor ≈ ln x larger because a top prime can strike many rows: its chosen class holds, for a good choice, several alive rows. The question is how many, and the answer is a large-deviation one: the alive rows are about half a row per class for s near x (R/s ≈ 0.4 to 0.7), the average cover must strike a number of rows of order ln x per top prime, and the best class among s − 1 has only about ln x/ln ln x.

## 2. The capacity form of the argument

**Step 1 (bulk). [Premise withdrawn: the lower tail of R(b) is not Gaussian, see section 0.3a.]** There are at most e^(θ(y₁)) bulk configurations. If R(b) has Gaussian lower tail with variance R₀, then min_b R(b) ≥ (1 − δ)R₀ with δ = √(2θ(y₁)/R₀). With y₁ = x/ω and R₀ ≈ x/Λ (Λ = ln ln x − 1 below) this is δ ≈ √(2Λ/ω): small once ω ≫ ln ln x, and then the top range (y₁, x] still holds a fraction 1 − 1/ω of all primes up to x.

**Step 2 (top).** A top modulus strikes only the alive rows of its one chosen class. If M_s is the size of the largest class of the alive set mod s, a complete cover needs

  Σ_{s in top} M_s ≥ R(b).

This is deterministic. Under the class-size model (rows in class c mod s ~ Poisson(m_s), m_s = R/(s − 1), independent over classes), M_s is the k with (s − 1)·e^(−m)·m^k/k! = 1.
Write s = x/u, r = R/x. For u ≪ ln x/ln ln x,

  M_s = ln x / Λ_u,  Λ_u = ln ln x − ln Λ_u − 1 − ln(r·u).

At the threshold r = 1/Λ the two ln Λ terms cancel (this is the self-consistency that removes any ln ln ln x), leaving Λ_u = ln ln x − 1 − ln u + o(1). The number of top primes at scale u is (x/ln x)·du/u², so

  Σ_top M_s = (x/ln x) ∫₁^ω (du/u²)·ln x/(ln ln x − 1 − ln u) = x/(ln ln x − 1) · (1 + O(1/ln ln x)).

Hence R ≤ (1 + o(1))·x/(ln ln x − 1). With R = (1 − δ)κπ(Q)/ln y₁ and Q = π(Q)·ln Q:

  **D(x) ≤ (1 + o(1)) · x ln²x / (κ (ln ln x − 1))**, the o(1) containing a *positive* relative term 2 ln ln x/ln x from ln Q = ln x + 2 ln ln x + ..., which is not small at any size reachable (42% at x = 10⁵).

**Relation to the first-moment form.** With every row independently struck by some top prime with probability p = 1 − ∏_top(1 − 1/(s − 1)) = ln ω/ln x, the number of covers of a typical alive set is at most e^(θ_top)·p^R, whose rate R·ln(1/p) = R(ln ln x − ln ln ω) has the same leading term. It differs at O(1) (the "− 1" becomes − ln ln ω, tunable through ω) because it counts covers that use classes of size m_s/μ (μ = Σ_top 1/s = ln ω/ln x); for those to exist one needs r·u ≲ 1, which fails for most of the covering weight at large ln ln x. The capacity form uses only classes that exist.

**Lower bound (greedy).** Take top moduli in increasing order and at each one the class holding most of the still-uncovered rows. In the Poisson model the capacity C(x) of this dynamic (largest R it completes, §3.4) satisfies C(ln ln x − 1)/x = 0.56 (x = 2·10⁴), 0.70 (10⁶), 0.82 (10⁹), 0.93 (10¹⁵), 1.00 (10³⁰), 1.04 (10⁶⁰), 1.03 (10¹²⁰). So greedy reaches the capacity bound within a few percent for large x, and in the model D(x) ~ x ln²x/(κ(ln ln x − 1)) from both sides. The approach is slow; the o(1) is large at every size below 10⁹.

## 3. Tests on real primes

### 3.1 Greedy cover depth

Greedy: moduli in increasing order, at each the class holding most uncovered rows; Q found by bisection to 1%; rows are all odd primes ≤ Q (`greedy_real.py`).

| x | D_greedy | D/(x ln²x) | ln ln x |
|---|---|---|---|
| 151 | 2,082 | 0.548 | 1.61 |
| 500 | 11,995 | 0.621 | 1.83 |
| 1,000 | 30,179 | 0.632 | 1.93 |
| 2,000 | 75,756 | 0.656 | 2.03 |
| 5,000 | 248,742 | 0.686 | 2.14 |
| 10⁴ | 603,063 | 0.711 | 2.22 |
| 2·10⁴ | 1,407,096 | 0.717 | 2.29 |
| 5·10⁴ | 4,236,727 | 0.724 | 2.38 |
| 10⁵ | 9,593,899 | 0.724 | 2.44 |

The same greedy taking the moduli in decreasing order does badly (0.10 at x = 151, 0.03 at x = 5·10⁴), as it should: the large moduli face the whole row set and strike one or two rows each.
The ratio rises and flattens at 0.72, which is the value the research session reports for greedy. The exact depth is larger than greedy's: 3,079 at x = 151 (ratio 0.81), tempering 0.78 to 0.88 up to 302 moduli.

### 3.2 The bulk gain

After greedy classes on the moduli ≤ y₁ = x/ln x (Q = 0.7·x·ln²x), the number of alive rows against a random bulk (exact product over the same moduli):

| x | rows | alive after greedy bulk | alive after random bulk | ratio |
|---|---|---|---|---|
| 300 | 878 | 119 | 161 | 0.737 |
| 10³ | 3,575 | 378 | 526 | 0.718 |
| 3·10³ | 12,547 | 1,146 | 1,559 | 0.735 |
| 10⁴ | 48,633 | 3,709 | 5,140 | 0.722 |
| 3·10⁴ | 164,835 | 11,063 | 15,274 | 0.724 |
| 10⁵ | 619,818 | 37,067 | 50,624 | 0.732 |

The bulk is not negligible: it removes 27% of the rows a random bulk would leave, and the fraction does not shrink over a factor 300 in x. The entropy cap √(2θ(y₁)/R₀) is 0.64 at x = 10⁴ and falls like 2/√(ln x), reaching the measured 0.27 only near x = 10²² to 10²³ (assuming the Gaussian tail). So step (1) as stated, min_b R(b) = (1 − o(1))R₀, becomes true at sizes far beyond any computation. The effect is one-sided (it helps covers) and vanishes slowly.

### 3.3 The top phase on real primes

x = 2·10⁴, Q = 0.70·x ln²x (1,373,107; 105,181 rows), greedy completes. After the bulk (moduli ≤ 2,019) 7,361 rows are alive, 0.718 of the random-bulk figure. In the top range the chosen class holds k rows, and the Poisson-max model (the expected largest of s − 1 Poisson(U/(s − 1)) variables at the current uncovered count U) predicts:

| s | U uncovered | k real | k model | real/model |
|---|---|---|---|---|
| 2,027 | 7,361 | 11 | 11.5 | 0.96 |
| 3,119 | 6,130 | 7 | 8.75 | 0.80 |
| 5,437 | 4,412 | 5 | 5.75 | 0.87 |
| 7,853 | 3,140 | 4 | 4.25 | 0.94 |
| 10,321 | 2,140 | 3 | 3.5 | 0.86 |
| 14,293 | 981 | 2 | 2.5 | 0.80 |
| 18,223 | 156 | 1 | 1.5 | 0.67 |

Summed over all the top moduli (s from 2,027 to 19,997): real 7,361 (the number of alive rows, since the cover is complete), model 8,041, ratio 0.915. The Poisson class model for the top is accurate to about 10% for real primes, in the range k = 1 to 11. (Output: `out_topcheck_x20000.txt`.)

### 3.4 Capacity of the top in the Poisson model, calibration, extrapolation

`topode3.py` runs the dynamic greedy in the Poisson model deterministically (expected largest class, moduli in bins of 3% of s) and bisects on the starting number of alive rows. C(x) is the largest start it can complete.

| x | C/x | C(ln ln x − 1)/x |
|---|---|---|
| 2·10³ | 0.433 | 0.445 |
| 2·10⁴ | 0.436 | 0.564 |
| 10⁵ | 0.435 | 0.628 |
| 10⁶ | 0.429 | 0.697 |
| 10⁹ | 0.404 | 0.821 |
| 10¹⁵ | 0.364 | 0.925 |
| 10³⁰ | 0.310 | 1.002 |
| 10⁶⁰ | 0.263 | 1.035 |
| 10¹²⁰ | 0.222 | 1.025 |

Calibration against the real greedy at its own critical Q (alive rows after the bulk, `calib.py`): real/model = 0.82 (x = 2,000), 0.83 (5,000), 0.87 (10⁴), 0.87 (2·10⁴), 0.88 (5·10⁴), 0.88 (10⁵). The real top is 12 to 18% weaker than the model, and the gap narrows slowly. I have no explanation beyond the roughness of class sizes 1 to 11.

Extrapolation (`extrap.py`): convert the capacity into Q by R = (bulk factor)·κ·π(Q)/ln y₁, with bulk factor 0.73 and top factor 0.88 as measured, and 1.0 and 1.0 for the bare model.

| x | calibrated D/(x ln²x) | bare model | 1.349/(ln ln x − 1) | 1.349/ln ln x |
|---|---|---|---|---|
| 2·10³ | 0.69 | 0.56 | 1.31 | 0.67 |
| 2·10⁴ | 0.72 | 0.59 | 1.04 | 0.59 |
| 10⁵ | 0.73 | 0.59 | 0.94 | 0.55 |
| 10⁶ | 0.72 | 0.59 | 0.83 | 0.51 |
| 10⁹ | 0.69 | 0.57 | 0.66 | 0.45 |
| 10¹² | 0.65 | 0.54 | 0.58 | 0.41 |
| 10¹⁵ | 0.62 | 0.51 | 0.53 | 0.38 |
| 10²⁰ | 0.58 | 0.48 | 0.48 | 0.35 |
| 10³⁰ | 0.52 | 0.43 | 0.42 | 0.32 |
| 10⁶⁰ | 0.44 | 0.36 | 0.34 | 0.27 |
| 10¹²⁰ | 0.37 | 0.30 | 0.29 | 0.24 |

Read this as shape, not value. The calibrated column reproduces the measured plateau by construction (two fitted factors). What is predicted is the shape: a maximum near 10⁵ to 10⁶, then a slow fall. The closed form 1.349/(ln ln x − 1) is a poor predictor at the sizes that can be tested (it overshoots the calibrated column by a factor 1.9 at 2·10³, 1.4 at 2·10⁴ and 1.15 at 10⁶) because the o(1) terms in it are large; 1.349/ln ln x is too low at large x. If the bulk gain tends to 0 as the entropy cap does, the calibrated column rises by at most 1/0.73 = 1.37 at the largest x.

### 3.5 What a pure Poisson model gets wrong

A model with Poisson classes at *all* moduli (`model_greedy.py`) gives larger depths than real primes (0.72 at x = 151, 0.86 at 10³, 0.87 at 2·10⁴, against 0.55, 0.63, 0.72): it lets the small and medium bulk moduli gain from class-count fluctuations, and primes in progressions mod s ≪ Q are less dispersed than Poisson. The top moduli, s ≥ Q/ln²x, are in the range where the dispersion is Poisson-like, and §3.3 shows the Poisson model fits there. This is why the check above treats bulk and top separately.

## 4. Answers to the four questions

**(A) Is (1) to (3) sound as a heuristic?** Step (2), the capacity form of the top, yes. Step (1), no: section 0.3. The bullets are as first written, the third one withdrawn. In detail:
- Concentration in (1): the union bound over e^(θ(y₁)) bulk configurations needs the lower tail of R(b) at e^(−x/ln x), which is a statement about moments of order x/ln x. For the real bulk δ = 0.27 now, not o(1); the asymptotic statement is δ ≲ 2/√(ln x).
- "General position" in (2): it means the alive set has Poisson class sizes mod s ∈ (x/ω, x] out to size ln x/ln ln x. Tested directly on real primes for k up to 11 (x = 2·10⁴): real/model = 0.915 in total. For larger k it is a Hardy–Littlewood statement for k-tuples of primes in a progression (k up to about ln x/ln ln x); the singular-series average over k-subsets equals 1 exactly in the independent-residue model, with a correction exp(−k²/(2K ln K)) for progression length K = Q/s ≈ ln²x, which stays small for k ≲ ln x/ln ln x.
- Can bulk and top cooperate? **Yes, and by more than I said (withdrawn paragraph replaced).** The block of `COHERENT_BLOCK.md` is a setting of the small moduli with entropy about ln x nats that leaves an unbounded factor fewer rows than random classes (0.07 of the random count at ln x = 1000, by the Lean session's table). My count (a fraction about 1/(ε ln x) of the top primes could be helped) assumed a Gaussian tail and applies only to settings near random classes.

**(B) Constant and correction.** Leading constant 1/κ = 1.348967 (= e^γ/(2C₂)). For covers with random-like small moduli, the correction from the capacity form is ln ln x − 1 + O(1/ln ln x), as the research session has it. The first-moment form gives ln ln x − ln ln ω instead, so the "− 1" is only trustworthy in the capacity form. The relative size of the correction terms at any reachable x is large (§2, §3.4); do not use 1.349/(ln ln x − 1) as a predictor below x ≈ 10¹⁵.

**(C) Does greedy on the top match?** (For random-like small moduli.) To leading order yes: in the Poisson model the dynamic greedy reaches 1.00 to 1.04 of the capacity bound x/(ln ln x − 1) for x ≥ 10³⁰ (the few percent either way are inside the O(1/ln ln x) terms dropped in §2), and 0.45 to 0.82 of it for x between 2·10³ and 10⁹. On real primes greedy reaches 82 to 88% of the model's top capacity at x = 2·10³ to 10⁵.

**(D) Literature.** I did not find a treatment of this prime-row covering function. The nearest analogue is the Jacobsthal function, where the rows are all integers of an interval and the lower bound is the hypergraph covering result of [Ford, Green, Konyagin, Maynard and Tao, *Long gaps between primes*, JAMS 31 (2018)](https://www.doi.org/10.1090/JAMS/876) (a Pippenger–Spencer-type covering lemma proved by the Rödl nibble; [arXiv 1412.5029](https://arxiv.org/pdf/1412.5029)), with the large-gap theorem of [Ford, Green, Konyagin and Tao, Annals 183 (2016)](https://annals.math.princeton.edu/2016/183-3/p04); Maynard obtained the same large-gap result by a different, sieve-theoretic method. The upper bound there is Iwaniec's h(k) ≪ (k ln k)², and Costello and Watts ([Math. Comp. 84 (2015)](https://www.ams.org/journals/mcom/2015-84-293/S0025-5718-2014-02896-2), [arXiv 1208.5342](https://arxiv.org/abs/1208.5342)) bound h(k) computationally for 50 ≤ k ≤ 10,000, with exact values only for k ≤ 49 (Hagedorn). Why a nibble does not by itself reach beyond the capacity here: it takes classes of typical size, and at the top moduli a typical class holds less than one alive row (0.4 to 0.7 at s ≈ x); the mean number of strikes per alive row from the top is only ln ln x/ln x. So the leftover of any procedure that uses typical classes is close to the Mertens leftover κπ(Q)/ln x (the measured greedy bulk gain is 27% below it), and the top has to clear that leftover with large classes, which the capacity limits. For integers the class-0 structure of the small primes changes the bulk (no entropy is spent and the rows are the rough numbers), but if the same counting holds at the top it predicts Y(x) ≍ x ln x/ln ln x, above the FGKMT lower bound x ln x · ln₃x/(ln₂x)² and far below Iwaniec's upper bound. I have not tested that; the Jacobsthal numbers j(p_k#) for k ≤ 49 are the cheap place to try (the capacity C(x) of §3.4 with a class-0 bulk).

## 5. What this does to the map and to the campaign

- The conjecture box (1.1275): withdrawn on 25 Nov by the research session; its replacement (order r ln² r/ln ln r) is not derived either, because of the block (section 0). The map has a box for the block and one for this check, which says what survives.
- Where the recursion may go wrong (I did not rederive it): κ(p) = (e^(vp) − 1)/v is the second-order, compound-Poisson, truncation, and the price needed at the top moduli is a tail quantity (class size ≈ ln x/ln ln x against mean 0.7). Replacing κ(p) by the exact Poisson-max functional at the moduli above y₁ and re-running its limit would show whether the recursion reproduces the plateau-then-fall of §3.4. If it does, 1.1275 is the recursion's value at no particular x.
- For the 200-digit game nothing changes: 89 to 1,228 moduli (x ≤ 10⁴) sit on the plateau and the measured depths are what to use.

## 6. What I did not check

- The Poisson class model for k above 11, and the lower tail of R(b) at e^(−x/ln x): both are Hardy–Littlewood-type and open.
- Whether the exact depth (not greedy) follows the same shape; at x = 151 the exact value is 48% above greedy, tempering is 30% above greedy at x = 2,000.
- The 12 to 18% gap between the real top and the model (§3.4).
- The research session's recursion (read only through the map ledger).
- Any structured prefix other than the block (blocks at several scales, different integers per block); I found the block only through the Lean session's referee read.
- Greedy runs are single deterministic runs (ties go to the smallest residue), bisection to 1%.

## 7. Reproduction

`data/limit_check/`: `greedy_real.py inc|dec x…` (§3.1), `bulkgain.py` (§3.2), `topcheck.py 20000 0.70` (§3.3), `topode3.py x…` and `calib.py` (§3.4), `extrap.py` (§3.4 last table), `model_greedy.py` (§3.5). They need numpy and scipy, and a prime table to 2·10⁷ (built inside), so Q = 0.7·x·ln²x must stay below it (x up to about 1.2·10⁵). The `out_*.txt` files are the outputs quoted here.
