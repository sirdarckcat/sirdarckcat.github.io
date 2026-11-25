# proof_referee_b -- working notes

## Part A. My own sketch (written after reading ONLY the title, section 0 item 1 and section 1 of COHERENT_BLOCK.md)

Setting: moduli = odd primes t <= x. Rows = odd primes q < Q. Target Q = c x ln^2 x ln_3 x / (ln_2 x)^2.
Parameters: w = x/4, z = exp(ln x * ln_3 x / (alpha ln_2 x)), alpha > 1 fixed. N1 in (Q, 2Q].

Stage 1 (block (z, w], class N1 mod t). Row q survives iff n = N1 - q in [1, 2Q) has no prime factor in (z, w].
  S := { n <= 2Q : no prime factor in (z, w] }. Since 2Q < w^2 for large x, n in S is z-smooth, or n = a p with p > w prime, a < 2Q/w.
  2Q/w = 8c ln^2 x * (...) < z, so a is automatically z-smooth: no constraint on a at all.
  |S| <= Psi(2Q, z) + sum_{a < 2Q/w} pi(2Q/a).
     second term <= (1+o(1)) (2Q/ln w) * ln(2Q/w)   [Chebyshev/PNT + harmonic sum]  ~ 2Q * 2 ln_2 x / ln x.
     first term: u = ln(2Q)/ln z ~ alpha ln_2 x/ln_3 x, u ln u ~ alpha ln_2 x, so Psi <= 2Q (ln x)^(-alpha+o(1)) (Rankin's trick suffices), negligible for alpha > 1.
  I need: #{q < Q prime : N1 - q in S} << pi(Q) * ln_2 x/ln x for SOME N1. Two routes:
   (a) fixed N1 (say N1 = 2^k), upper-bound sieve for the pair (p, N1 - a p) for each a < 2Q/w: 
       << (Q/a)/ln^2(Q/a) * prod_{l | a N1, l > 2}(1 + 1/l); sum over a gives << Q ln_2 x/ln^2 x. Needs Brun/Selberg uniform in a
       (Halberstam-Richert Thm 3.11/3.12) and N1/phi(N1) bounded. Unconditional but heavier.
   (b) average over N1 in (Q, 2Q]:  sum_{N1} #{q : N1 - q in S} = sum_q #{n in (Q-q, 2Q-q] cap S} <= pi(Q) |S|.
       So some N1 has survivors <= pi(Q) |S|/Q <= (4+o(1)) pi(Q) ln_2 x / ln x. Needs only Chebyshev + Rankin-trick smooth bound. No sieve.
  (b) is strictly weaker input than (a). I would use (b).

Stage 2 (odd t <= z, greedy). Rows q > z are nonzero mod every t <= z, hence lie in t - 1 classes; fullest class has >= 1/(t-1) of the live rows > z.
  After all t <= z: live <= pi(z) + |R1| prod_{3 <= t <= z} (1 - 1/(t-1)) = pi(z) + |R1| (2 C_2 e^-gamma + o(1))/ln z, 2 C_2 e^-gamma = 0.7413.
Stage 3 (t in (w, x]): one row each; there are (3/4 + o(1)) x/ln x such t.

Condition: (Q/ln x)(4 ln_2 x/ln x)(0.7413 alpha ln_2 x/(ln x ln_3 x)) (1+o(1)) + pi(z) <= (3/4) x/ln x
  => Q = c x ln^2 x ln_3 x/(ln_2 x)^2 with any c < 0.75/(4*0.7413*alpha) ~ 0.253/alpha, i.e. any c < 1/4 (crude; the factor 4 is lossy by 2:
     windows (Q-q, 2Q-q] have length Q, so the true average is about 2 ln_2 x/ln x and c < 1/2).
Order obtained by my sketch: x ln^2 x ln_3 x/(ln_2 x)^2. Same as the stated Theorem.
Corollary by CRT: N in (P, 2P], P = 2 prod_{t<=x} t, ln N ~ x; N - q > x is divisible by some t <= x hence composite for all odd primes q < Q; q = 2 trivial.

## Part B. Comparison with the file's proof (section 2), read afterwards

Same construction, same order, same route (b) (average over N1). Differences:
- File takes alpha = 3 (ln z = ln x ln_3 x/(3 ln_2 x)) because its home-made Rankin bound (F4) carries an extra factor ln z; with de Bruijn any alpha > 1. Constant only.
- File's step (ii) invokes Brun-Titchmarsh (F2) to bound #{q prime in an interval of length <= Q, q < Q} by 2Q/ln Q. Not needed: that count is <= pi(Q) <= C0 Q/ln Q by (F1). So the Theorem needs only Chebyshev, Mertens and Rankin's trick. Section 4's "it needs the smooth-number estimate and Brun-Titchmarsh" overstates the formalisation cost.
- Line-by-line check of Step 1 (i),(ii), averaging, Step 2 recursion |S| -> |S|(1-1/(t-1)) + 1 (slack <= pi(z)), Step 3, Step 4 arithmetic (3 C1 C2 c x/ln x + z <= 0.7 x/ln x - 1 with c = 1/(8 C1 C2)): all correct.
- Small defects:
  * "c fixed at the end" but C1 is used before; C1 does not depend on c only because ln M <= 2 ln_2 x for every fixed c and large x. Should be said.
  * (F4) "Hence Psi(X,z) <= C X ln z exp(-u ln u + u)": the derivation gives exp(-u ln u + (1+o(1))u). Harmless (u = o(u ln u)).
  * CRT paragraph: "N < 2 prod t ... N - q is divisible by a modulus t < N - q": false if the CRT representative happens to be <= Q + x. Take N in [2 prod t, 4 prod t). Trivial.
No step of mine needed a stronger input than the file's; the file's needs one more input (F2) than necessary.

## Part C. Numerics (my scripts: run/proof_referee_b/mine.py, mine2.py, mine3.py; written before opening coherent_surv.py)

Rows = odd primes < Q, block = primes in (z, x/4], class N1 mod t. "left" = fraction of rows with no prime factor of N1 - q in the block.
Columns: exact random expectation prod(1-1/(t-1)); the file's baseline ln z/ln w; random-class simulation; coherent over N1 = Q..Q+49.

x=10^4, Q=610,000, z=80:  prod=0.5740, ln z/ln w=0.5601, sim=0.5746 | coherent min=0.5192 (N1=610031, prime), mean=0.5597, max=0.6076
x=10^5, Q=9,000,000, z=160: prod=0.5070, ln z/ln w=0.5012, sim=0.5057 | coherent min=0.4327 (N1=9000011), mean=0.4776, max=0.5453
x=10^6, Q=4*10^7, z=160:  prod=0.4132, ln z/ln w=0.4083 | min=0.2926 (N1=40000021), mean=0.3457, max=0.4169
x=3.75*10^6, Q=6*10^7, z=160: prod=0.3735, ln z/ln w=0.3691 | min=0.2119 (N1=60000001), mean=0.2657, max=0.3369
Lean count N1=2^26, block (406, 937500]: 0.3230 against prod 0.4396, ratio 0.735. Reproduces "32.3% against 44.0%, 0.735".

=> the file's table (0.519/0.560, 0.433/0.501, 0.293/0.408, 0.212/0.369) reproduces to 3 digits; z = 80/160/160/160 is the ratio-minimising z in my runs too.

Things the table does not say:
1. Its "random" column is ln z/ln w, not the exact product. Exact: 0.574, 0.507, 0.413, 0.3735. Ratios against exact: 0.904, 0.854, 0.708, 0.567 (file: 0.93, 0.86, 0.72, 0.57). The file is conservative here.
2. The coherent figure is the MINIMUM over 50 N1 and over z. The spread over N1 is structural, not noise (random-class sd is ~0.002):
   x=10^4, z=80: 0.519 .. 0.608. Mean over N1=Q..Q+49: 0.5597 (ratio 0.975 to exact, 1.000 to ln z/ln w).
   Mean over 250 N1 spread over the whole (Q, 2Q] (what the proof averages): 0.5828, ratio 1.015 -> at x=10^4 the AVERAGE N1 is slightly worse than random.
   x=10^5, z=160: near Q mean 0.4776 (0.942); whole (Q,2Q] mean 0.5037 (0.994).
   x=10^6: near-Q mean ratio 0.837; x=3.75*10^6: 0.711. The downward trend holds for the mean as well, starting one decade later.
3. Which N1 are good: odd N1 with no small prime factor (610031 prime; 610013=47*12979; 610039=41*14879). Even N1 mean 0.5805, odd mean 0.5389 at x=10^4.
   Worst: N1 divisible by 2*3*... (610038 = 2*3^3*11*13*79 -> 0.6076; 610020 -> 0.6046).
   Reason: n = N1 - q is coprime to every prime dividing N1, so the cofactor a in n = a p is confined to a coprime to N1; to first order the Hardy-Littlewood factor
   (l-1)/(l-2) for l | N1 exactly compensates (1 + 1/(l-2) either way), and what is left is the cut-off a < M = 2Q/w: relative effect O(1/ln M) = O(1/ln_2 x), never negligible.
   Consequence: N1 = 2^26 (Lean session) is a poor choice of common integer: at Q=6*10^7, z=406 it leaves 0.3230; N1=60000041 leaves 0.2683 (17% fewer rows).
   Survivor split at x=10^4,z=80,N1=610031: a*p part 0.395, z-smooth part 0.124 (z-smooth part is NOT negligible at this size; u = ln Q/ln z = 3.0).

## Part D. Can it be pushed?

Accounting of the Theorem: survivors after block ~ pi(Q) * 2 ln_2 x/ln x (the a*p numbers, sum_{a<M} 1/a = ln M), small primes Mertens 0.74/ln z, top primes 1 row each.
(1) Blocks at several scales / several integers: no gain in order. The smooth-number saving happens once, for a block reaching up to Q^(1-o(1)).
    A lower block (z', z] with another integer N2 leaves the Mertens fraction ln z'/ln z of rows (numbers free of prime factors in (z', z] with z << sqrt Q have density
    ~ ln z'/ln z), the same as greedy/random. Splitting the primes of (z, w] between two integers destroys the saving (each half behaves like a sieve of density sqrt).
    Using N1 also on the primes below M = 2Q/w forces a = 1 (survivors = exact Goldbach pairs q + p = N1): gains 1/ln M and costs the Mertens factor of those primes, 0.74/ln M. Same order (constant 1.35 worse).
    Unconditional, but nothing to gain beyond constants.
(2) Top primes striking >= 2 survivors (Maier-Pomerance/Pintz analogue). Heuristically abundant: |R|^2/(2t) ~ x/ln^2 x colliding pairs per top prime. Gain: at most the constant c doubles.
    Needed input: lower bound, for the fixed N1, for #{(q,q') in R^2 : t | q - q'} on average over t in (w, x], i.e. counts of prime quadruples
    q, q + h t, (N1 - q)/a, (N1 - q - h t)/a'. For fixed N1 two of these forms have proportional linear parts (q and N1 - q): binary/Goldbach type, not available.
    After averaging over N1, m = N1 - q becomes a free variable and the count is sum_{d = h t} T1(d) T2(d), a product of two "twin primes on average" counts; that is
    unconditional (Lavrik; the input Maier-Pomerance used), but one then needs a variance in N1 to get one N1 that is good for Step 1 and for the matching, and the adaptive greedy
    small-prime stage must be replaced by fixed classes so that R is explicit. Constant-factor gain only; the Theorem's c is unspecified anyway.
(3) k survivors per top prime, k -> infinity (FGKT analogue): system {t, q + c_j t, (N1 - q - c_j t)/a_j}. With N1 fixed: infinite complexity (pairs sum to N1) -> Green-Tao-Ziegler does not apply.
    With N1 as a variable: finite complexity, GTZ applies in principle (unconditional), giving D(n)/(r ln^2 r ln_3 r/(ln_2 r)^2) -> infinity. Obstacles: (i) second moment over N1;
    (ii) cofactors a_j range up to M ~ ln^2 x with logarithmic weight 1/a, so truncating a <= A0 keeps only ln A0/ln M -> 0 of the survivors; GTZ has no uniformity in coefficients of that size
    (variant with N1 also on primes < M makes a = 1 and removes this, at a constant cost). Research-paper level; I have not verified it goes through.
(4) FGKMT analogue (gain ln_2 x, target x ln^2 x ln_3 x/ln_2 x): needs Maynard-type weights that detect survivors. Survivors are pairs (q prime, (N1-q)/a prime). For fixed N1 evaluating
    sum w(n) 1_P(n + h_i t) 1_P((N1 - n - h_i t)/a) is a twin-prime-type sum: not unconditional. Averaged over N1 the sum can be evaluated (n and m = N1 - n independent, Bombieri-Vinogradov
    suffices) but then sum_i P(both i-th forms prime) = O(1) for any sieve weight I can construct (product of two Maynard weights gives k (ln k/k)^2). So I see no unconditional
    route to an unbounded gain by Maynard's sieve; conditional on Hardy-Littlewood k-tuples with uniformity, yes.
    Decoupling (choose top classes rich in primes, ignore N1) does not help: boost needed is ln x/ln_2 x primes among ~ ln x sifted integers of an AP.
(5) Heuristic ceiling of the family: k-fold collisions exist while x (theta/ln x)^k/k! >= 1, i.e. k <~ ln x/ln_2 x, so ~ x ln^3 x ln_3 x/(ln_2 x)^3, agreeing with the file's "block_capacity" remark. Not provable with current tools.
