# WP10 — After the GRH announcement: what it changes, what it does not, and two things it made us look at

Status: 2026-11-21. Trigger: `https://alpo.ge/remark.pdf` (4 pages, dated
2026-11-20), read on request "for inspiration". Companion code and records:
`goldbach/proth/`. Everything conjectural is marked [C], proved here [P],
measured [V], and cited-but-not-rechecked [L].

## 0. What the PDF is (and is not)

It is **not** a Goldbach paper. It is a short announcement by the owner of
`alpo.ge` that he and Claude have found a proof of the Riemann Hypothesis,
"easily" extended to GRH, and that the argument is formalized in Lean "without
assumptions" (14 archive parts are linked; the note deliberately presents
*only* Lean, because posting a 250,000-page generated write-up would be
"slop"). The mathematical content of the note is a 20-item timeline of
ingredients (a Stepanov-type argument with multiplicity manufactured by a
chain of ~√X theta lifts between definite unitary groups, Weil positivity
via determinants, an Iwasawa tower, a Bost slope inequality, a relative
trace formula, a weakening of Vandiver, …). There are no statements we can
check from the PDF itself, and I did **not** download or check the Lean
archive. So throughout this memo "GRH" means "GRH, if that proof stands";
nothing below depends on it unless it says so.

Two things in the note are usable here:

1. **GRH as a hypothesis we may soon be allowed to drop.** §3 goes through
   every place the programme could use it. Summary: *it moves constants, not
   walls.* The honest surprise is how little it buys — and working out why
   led to the two results below, neither of which needs it.
2. **"Present the proof object, not the slop."** The records in this repo
   are trusted because of process (dual stacks, audits). The construction in
   §1 makes the *entire* proof of a record so small — a sieve check plus one
   modular exponentiation — that a kernel-checked Lean proof of
   `g(N) = g` is realistic (§4).

## 1. Result A — the certification wall of the height game is removable [P, V]

SoK §6 ("Game 1"): *"the binding constraint is certifying N−q … A
construction breakthrough — arranging N−q to have Pocklington-friendly form
while satisfying the cover congruences — would blow the wall off entirely …
nobody knows how to intersect the two constraint systems, and we flag it as
the single most valuable open trick in this problem family."* SoK §7.2
sketches the Proth variant as an untouched angle.

The two constraint systems intersect trivially. Write the complement as

    P = N − g = m·2ⁿ + 1.

A cover congruence N ≡ a_r (mod r) is then m ≡ (a_r − g − 1)·2⁻ⁿ (mod r):
a congruence on m, because 2ⁿ is a unit modulo every odd r. CRT gives
m ≡ m₀ (mod M_c), M_c = ∏r, and the search runs over m = m₀ + t·M_c. With
2ⁿ > P^{1/3} the primality of P follows from **one** modular exponentiation
(Brillhart–Lehmer–Selfridge N−1 test; with 2ⁿ > P^{1/2} it is literally
Proth's theorem). No cover freedom is spent: all residues stay greedy-optimal.

Consequences (records and timings in `goldbach/proth/README.md`; the first
certified record is g = 1,200,109 at 11,263 digits):

- **ECPP disappears from the pipeline.** The 2,480-digit record needed a
  245-step ECPP certificate (~1.7 h to build, ~2 h to re-verify, +2 h
  APR-CL). The new certificate is one `powmod` (5.7 s with GMP, 102 s
  with plain Python integers).
- **Full covers become the optimal design.** With certification free the
  only cost is PRP tests, and a cover with *no residual primes at all*
  needs just one prime in a progression (~ln P/(e^γ ln B) tests) instead of
  a lottery of e^E candidates. REGISTRY.md row A2 ("complete cover —
  dominated") flips: costed with the measured modexp timings, at
  g ≈ 1.2·10⁶ the full cover is ~4× cheaper than a megagap-style partial
  cover with a BLS-form complement, and leaving 200–500 residuals to luck
  would save < 10%.
- **The proof of a record is now tiny and has no probabilistic residue.**
  Every prime q < g has an explicit divisor r | N − q from the cover; the
  partition is one N−1 test. The stdlib verifier is ~100 lines.
- **The ladder is PRP-bound, not ECPP-bound** — see the table in
  `goldbach/proth/README.md`: g > 10⁷ is a few thousand PRP tests at
  ~61,000 digits; the "absolute gap" milestone g > 16,045,848 (longer than
  the largest known prime gap of any kind) is ~6,000 tests at ~91,000
  digits. Both were classed as "ECPP far beyond practice".

What it costs: digits. N is ≈ 1.5× the full-cover modulus, which itself is
~2.5–2.8× a megagap-style partial modulus. This is the height game, where
digits are free; the bounded games T(100,000) and R(10²⁰⁰) are untouched.

## 2. Result B — the prime-covering function: a new constant, and a ceiling [P]

Let **C(x)** be the largest Q such that residues a_r (odd primes r ≤ x) can
be chosen with every odd prime q < Q in some class q ≡ a_r (mod r). Any even
N in all those classes with N > Q + x has no Goldbach summand below C(x)
(Proposition 10 of the paper), and such N exist in (x#, 2·x#], so ln N ≤ θ(x)+ln 2.
C(x) is the Jacobsthal problem with the targets restricted to primes.

**Theorem 1 (lower bound).** C(x) ≥ (e^γ/(2C₂) − o(1))·x·ln x, where
C₂ = ∏_{p>2}(1 − 1/(p−1)²) is the twin-prime constant; e^γ/(2C₂) = 1.3490.

*Proof.* Process the odd primes r in increasing order, each taking a class
containing the most surviving targets. If t targets survive, at most one of
them is r itself and the other t−1 lie in the r−1 non-zero classes, so the
best class holds ≥ (t−1)/(r−1) of them: t ← t(1 − 1/(r−1)) + 1/(r−1). After
all odd r ≤ w,

    t_w ≤ π(Q)·∏_{3≤r≤w} (r−2)/(r−1) + O(ln ln w)
        = (2C₂e^{−γ} + o(1))·π(Q)/ln w,

since (r−2)/(r−1) = (1 − 1/(r−1)²)(1 − 1/r) and Mertens. Every prime in
(w, x] then removes at least one survivor. With w = x/ln x this covers
everything as soon as (2C₂e^{−γ}+o(1))·π(Q)/ln x ≤ (1+o(1))·x/ln x, i.e.
π(Q) ≤ (e^γ/(2C₂) − o(1))·x. ∎

So there are explicit even N with **no prime below
(1.349 − o(1))·ln N·ln ln N** as a Goldbach summand. Three comparisons:

- *The paper's Theorem 14* (`slop/goldbach/paper.tex`) transfers the
  Ford–Green–Konyagin–Maynard–Tao prime-gap bound and gets
  ln N·ln₂N·ln₄N/ln₃N — **weaker** than Theorem 1 by a factor ln₃N/ln₄N → ∞,
  from far heavier machinery. Its open question 3 ("Sparser than gaps: does
  the restriction to prime offsets let g exceed the maximal-prime-gap
  rate?") has the answer yes at the level of *provable* bounds (the
  counting bound in the next item already shows it; Theorem 1 shows it
  constructively). Whether g exceeds the *true* maximal gap is untouched.
  The reason is structural: in the Erdős–Rankin scheme the middle primes are
  spent killing smooth composites, so only primes ≤ z = x^{o(1)} thin the
  survivors (factor 1/ln z); with prime targets there are no composites to
  kill and *every* prime up to x/ln x thins (factor 1/ln x).
- *W. Shi, arXiv:2605.21529v6, Thm 6.22(iii)* [L] proves
  max_{n≤X} p(n) ≥ (½ + o(1))·ln X·ln ln X by counting pairs (p, n)
  (with p(n) = ∞ when n has no partition), and remarks that ½ "is the
  limit of pure counting … an improvement would need a covering
  construction in the spirit of [FGKMT], here covering only the primes."
  Theorem 1 is that covering construction — elementary rather than
  FGKMT-style — and raises the constant from 0.5 to 1.349 under the same
  convention, with an explicit N instead of an existence count.
- *Pigeonhole is a worst case; greedy does much better* [V]
  (`goldbach/proth/pigeonhole_table.py`): the guaranteed threshold Q_pig(x)
  against what the deterministic greedy cover reaches.

  | x | θ(x) (≈ ln N) | Q_pig(x) | Q_pig/(x ln x) | Q_greedy(x) | Q_greedy/(x ln²x) |
  |---|---|---|---|---|---|
  | 2,393 | 2,348 | 22,111 | 1.19 | 10⁵ | 0.690 |
  | 15,083 | 14,922 | 177,988 | 1.23 | 10⁶ | 0.716 |
  | 26,713 | 26,531 | 337,074 | 1.24 | 2·10⁶ | 0.721 |
  | 102,983 | 102,694 | 1,497,439 | 1.26 | 10⁷ | 0.729 |
  | 755,137 | 753,995 | 13,054,972 | 1.28 | 10⁸ | 0.723 |

  Greedy tracks **0.72·x·ln²x** across four decades: one full logarithm
  above the theorem. Proving any f(x) → ∞ with C(x) ≥ f(x)·x·ln x is the
  natural next theorem (it needs the large primes to capture several
  survivors each — exactly the FGKMT hypergraph-covering step, here for
  prime tuples in progressions of large prime difference).

**Theorem 2 (ceiling for covering certificates).** For every ε > 0 and
x ≥ x₀(ε), C(x) ≤ x^{4+ε}. Under the Elliott–Halberstam conjecture,
C(x) ≤ x^{2+ε}.

*Proof.* Sift A = {primes q < Q} by the classes a_r, r ≤ z. The density is
1/(r−1) per sifting prime (dimension 1; if a_r = 0 only q = r is removed),
and Bombieri–Vinogradov controls the remainders, uniformly in the residue
class, up to level D = Q^{1/2−ε}. The linear sieve lower bound is positive
for ln D/ln z > 2, i.e. z ≤ Q^{1/4−ε}: at least c_ε·π(Q)/ln Q primes below
Q avoid every class. So no system with moduli ≤ Q^{1/4−ε} covers the primes
below Q. EH raises the level to Q^{1−ε} and the range to z ≤ Q^{1/2−ε}. ∎

Reading: *divisors of size ≤ x can certify a desert of length at most
x^{4+ε}* — the first unconditional impossibility statement in this problem
family (SoK §7.3 asked for one). With the CRT construction x ≈ ln N, so
covering certificates are confined to
(1.349 − o(1))·ln N·ln ln N ≤ g ≤ (ln N)^{4+ε}, and the data say the truth
for covers is ≈ ln N·(ln ln N)² — *below* the conjectured maximal order
(ln N)²·ln ln N of g itself [C, Granville–van de Lune–te Riele]. Certified
deserts are a thin, structured subfamily of the extremal ones; that is the
rigorous shadow of the construction-versus-existence gap measured in
RESULTS.md and FRONTIER.md. Note GRH does not improve Theorem 2:
Bombieri–Vinogradov already is GRH on average.

**Genuine Goldbach numbers.** Theorem 1 controls small summands; to make N a
sum of two primes take s an uncovered prime and t the least prime
≡ N − s (mod x#). Then g(N) ≥ C(x) and ln N ≤ L·θ(x)(1+o(1)), where L is a
Linnik exponent for the modulus x#:

| input | L | g(N) ≥ (c − o(1))·ln N·ln ln N, c = |
|---|---|---|
| Linnik, general modulus (Xylouris) [L] | 5 | 0.270 |
| exceptional set E(X) < X^{0.72} (Pintz) [L], no explicit partition | 1/0.28 | 0.378 |
| smooth modulus (Chang 2014, Cor. 11) [L] — x# is x-smooth | 12/5 | 0.562 |
| **GRH** (Lamzouri–Li–Soundararajan: P(a,q) ≤ (φ(q) ln q)²) [L] | 2 | 0.674 |
| Goldbach's conjecture for N itself | 1 | 1.349 |

## 3. The GRH ledger — where it enters, item by item

| # | place | without GRH | with GRH | verdict |
|---|---|---|---|---|
| 1 | realisation of a cover as a Goldbach number (paper Thm 12) | ln N ≤ 2.4·ln M (smooth-modulus Linnik) | ln N ≤ 2·ln M + 2 ln ln M, explicit for all M > 3 | constant 0.56 → 0.67 |
| 2 | *existence* of an N−1-certifiable complement in the cover progression (§1) | needs a Linnik exponent < 3 for D = 2ⁿM_c; Chang's 12/5 applies (D is smooth) ⇒ N < M_c^{12+o(1)} | P ≤ (φ(D) ln D)² < 2^{3n} once 2ⁿ ≥ 16·M_c²·ln²M_c ⇒ N < M_c^{6+o(1)} | exponent 12 → 6; in practice 1.5 [V] |
| 3 | primality proof of N − g by Miller's test (deterministic on GRH; witnesses below 2 ln²P, Bach) | — | π(2 ln²P) ≈ 6.7·10⁷ strong tests at 11,263 digits ≈ 12 core-years here | **not competitive**: BLS is 1 test (5.7 s); ECPP would be of the order of a core-month (extrapolated) |
| 4 | ceiling Theorem 2 | level ½ (Bombieri–Vinogradov) | level ½ | no change (needs EH) |
| 5 | density model E = \|U\|·boost/ln N (WP9's H1) | heuristic | still heuristic: GRH gives π(X; M, a) only for M < X^{1/2−ε}; the records live at M ≈ X^{0.95}, and joint primality of the residual complements is a k-tuple statement | no change |
| 6 | Goldbach itself / "g(N) exists" | open | still open; exceptional set X^{1/2+ε} (Hardy–Littlewood) | realisation constant ½, same as #1 |
| 7 | the bounded games T(100,000), R(10²⁰⁰) | search exponent e^E | identical | no change |
| 8 | compositeness witnesses (strong base-2 failures) | unconditional already | — | no change |

*GRH moves constants, not walls.* The one wall that did move (§1) moved for
a structural reason — changing the shape of the number — and row 3 shows
the contrast starkly: even granted GRH, the "free" deterministic primality
test it provides is seven orders of magnitude more expensive than simply
constructing the complement so that it carries its own proof.

A Hardy–Littlewood-type statement is what the programme's forecasts rest
on, and that is on the far side of the parity barrier from GRH. If the
announced method really does produce "multiplicity over the integers",
the place to look for consequences here is not Dirichlet L-functions but
whether any of it speaks to correlations Λ(n)Λ(n+h) — outside what this
memo can assess.

## 4. The Lean angle (taken from the note's own stance)

SoK §7.8 lists "formal verification of the verifier" as untouched. With the
old records that meant formalizing ECPP (elliptic-curve group law,
Goldwasser–Kilian) and ~2,800 strong-pseudoprime witnesses. With §1's
records the complete statement

    IsLeast {p | p.Prime ∧ (N − p).Prime} g

needs only: (a) one lemma — the BLS/Pocklington N−1 criterion, a page of
`orderOf` reasoning in Mathlib; (b) a decidable check that each prime
q < g lies in a cover class and N lies in every class; (c) one modular
exponentiation and one integer-square-root comparison. That is a
few-hundred-line development and it would make these the first
machine-proof-carrying records in the genre. Status: see
`goldbach/proth/README.md` (§ Lean) for what was done in this session.

## 5. Ranked next steps

1. **Run the ladder** (PRP-bound, embarrassingly parallel, resumable):
   g > 3·10⁶ (≈2.7 h on this 4-core box), 5·10⁶ (≈11 h), 10⁷ (≈3–4 days),
   16,045,848 (≈2 weeks) — all with GMP; a gwnum-class PRP engine or the
   repo's GPU fleet cuts each by 10× or more.
2. **Shrink full covers.** The paper's greedy sits at 0.72·x·ln²x and its
   tail is wasteful (at Q = 1.2M the last 300 targets cost 138 one-kill
   moduli). A weighted lazy greedy over a 3× prime pool already recovers
   ~10% (6,787 vs 7,503 digits; `proth/desert.py`). What is left is
   Door 1 in a sparse regime, where the objects are pairs, triples and
   quadruples of targets sharing a class and the question is a rainbow
   hypergraph matching — far more tractable than the dense 88-modulus
   instance of WP9. Each 10% of digits is ~30–35% of compute.
3. **Theorem with f(x) → ∞** in C(x) ≥ f(x)·x·ln x (FGKMT step for prime
   targets) — a real paper-level result; and patch `paper.tex`
   (Theorem 14, the sandwich display, open question 3) with Theorem 1.
4. **KP/CHG variants**: Konyagin–Pomerance (F ≥ P^{3/10}) or
   Coppersmith–Howgrave-Graham (F ≥ P^{1/4+ε}) shrink N by 5–11%
   (16–32% compute) at the price of a more elaborate certificate.

## Appendix — proposed patch for `slop/goldbach/paper.tex` (not applied)

The paper's Theorem 14 and open question 3 are superseded by Theorem 1
above. The paper is left untouched (its PDF was built elsewhere); this is
the text I would substitute for Theorem 14 and its lead-in, plus three
bibliography items. The sandwich display in §6 then reads
`\log\N\,\log_2\N \ll \max \g \lesssim (\log\N)^2\log_2\N`, and open
question 3 becomes: *is $\max_{\N'\le\N}\g(\N')/(\log\N\log_2\N)$ unbounded?*

```latex
\begin{theorem}[Covering the primes directly]\label{thm:primecover}
Let $C_2=\prod_{p>2}\bigl(1-\tfrac1{(p-1)^2}\bigr)$ and
$\kappa=e^{\gamma}/(2C_2)=1.3490\ldots$. For every $\varepsilon>0$ and all
sufficiently large $x$ there are residues $a_r$, one for each odd prime
$r\le x$, such that every odd prime $q<(\kappa-\varepsilon)\,x\log x$ has
$q\equiv a_r\pmod r$ for some $r$. Consequently:
\begin{enumerate}
\item there are even $\N$ with $\log\N\le\theta(x)+\log2$ such that no prime
below $(\kappa-\varepsilon)\log\N\,\log_2\N$ is a Goldbach summand of $\N$;
\item there are infinitely many even $\N$ with an explicit Goldbach
representation and
$\g(\N)\ge(\kappa/L-\varepsilon)\log\N\,\log_2\N$, where $L$ is an
admissible Linnik exponent for the smooth moduli $\prod_{r\le x}r$:
$L=12/5$ unconditionally~\cite{Chang}, $L=2$ under GRH~\cite{LLS}.
\end{enumerate}
\end{theorem}
\begin{proof}
Treat the odd primes $r\le x$ in increasing order, each time choosing for
$a_r$ a class containing the most surviving targets. If $t$ targets survive,
at most one of them equals $r$ and the remaining $t-1$ lie in the $r-1$
non-zero classes, so some class contains at least $(t-1)/(r-1)$ of them and
the number of survivors drops to at most $t\,\frac{r-2}{r-1}+\frac1{r-1}$.
Since $\frac{r-2}{r-1}=\bigl(1-\frac1{(r-1)^2}\bigr)\bigl(1-\frac1r\bigr)$,
Mertens' theorem gives, after all odd $r\le w$,
\[
t_w\ \le\ \pi(Q)\prod_{3\le r\le w}\frac{r-2}{r-1}+O(\log_2 w)
\ =\ \bigl(2C_2e^{-\gamma}+o(1)\bigr)\frac{\pi(Q)}{\log w}.
\]
Each prime in $(w,x]$ removes at least one further survivor. With
$w=x/\log x$ there are $(1+o(1))x/\log x$ of them and $\log w\sim\log x$, so
all targets are covered once $\pi(Q)\le(\kappa-\varepsilon)x$, i.e.\ for
$Q=(\kappa-\varepsilon)x\log x$. Part~(1) is
Proposition~\ref{prop:cover} with $\N\in(M,2M]$, $M=2\prod_{3\le r\le x}r$;
part~(2) is Theorem~\ref{thm:coverdirichlet} with $s$, $t$ the least primes
in their classes modulo $M$.
\end{proof}

\begin{remark}
(i) The transfer from large prime gaps~\cite{FGKMT} yields only
$\log\N\,\log_2\N\,\log_4\N/\log_3\N$: in the Erd\H{o}s--Rankin scheme the
primes in the middle range are spent on smooth composites, so only primes
up to $x^{o(1)}$ thin the survivors, whereas with prime targets every prime
up to $x/\log x$ does. (ii) Counting pairs $(p,\N)$ gives
$\max_{\N\le X}\g(\N)\ge(\tfrac12+o(1))\log X\log_2X$ with the convention
$\g=\infty$ when no representation exists~\cite{Shi}; under that convention
part~(1) improves $\tfrac12$ to $\kappa$. (iii) In the other direction the
linear sieve with the Bombieri--Vinogradov theorem shows that residues
modulo the primes $r\le x$ can never cover all primes below $x^{4+\varepsilon}$
($x^{2+\varepsilon}$ on the Elliott--Halberstam conjecture). The greedy
coverings of Table~\ref{tab:results} reach $Q\approx0.72\,x(\log x)^2$.
\end{remark}

\bibitem{Chang} M.-C.~Chang, \emph{Short character sums for composite
moduli}, J. Anal. Math. \textbf{123} (2014), 1--33.
\bibitem{LLS} Y.~Lamzouri, X.~Li, K.~Soundararajan, \emph{Conditional bounds
for the least quadratic non-residue and related problems}, Math. Comp.
\textbf{84} (2015), 2391--2412.
\bibitem{Shi} W.~Shi, \emph{Matrix $B$: exact prime counting, algebraic row
correspondences, and semiprime distributions}, arXiv:2605.21529v6 (2026),
Theorem~6.22.
```
