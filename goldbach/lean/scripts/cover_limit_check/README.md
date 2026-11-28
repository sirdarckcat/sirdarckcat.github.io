# A referee's check of the limit of the counting law

The research session's write-up (`goldbach/sublinear/README.md` on branch `ccr-d4a17dd0-7uu03r`, section
"Where the constant ends up", read at commit `d4de717`) ends in

    D(n) / (r ln² r)  →  e^γ / (2 C₂ Λ(1)) = 1.1275,

a heuristic limit reached in four steps. It asked (25 November 2026, 07:50 UTC) for an independent
check of the four steps, and for numbers on the first two. This directory is that check. Nothing here
is a proof; the exact identities it starts from are the ones proved in
`GoldbachGaps/CoverPairs.lean` and `GoldbachGaps/CoverPairSums.lean`.

A second read, of what the research session put in the place of this limit (the entropy of every prefix
of the moduli, and a bound with `1/ln ln r`), is in `../cover_prefix_check/`.

## The verdict

* **Steps 1, 2 and 3 hold**, as statements about leading order. Each was rederived here and tested
  against exact sums up to 10^11. They are approached slowly: the first corrections are of relative
  size `const / ln`, with large constants, and they have closed forms (below). With them the exact
  sums are reproduced to four or five digits.
* **Step 4 holds for the recursion as it is defined.** The recursion over the actual primes, given the
  same dispersion as the continuum equation, tends to the continuum constant: 0.27% below it at
  `x = 10^8`, the gap shrinking like `1/ln² x`. "The largest price that can be carried to the end" is
  attained at a price `ln(x − 1)/v` after the last modulus and is flat there, so identifying it with
  the solution that blows up at the last modulus is right.
* **What the four steps establish is the limit of the recursion**, not of `D(n)/(r ln² r)`. The
  recursion takes the dispersion of the alive rows from random class vectors, while the sum over
  classes that it models is taken along covers; the research session's own measurement
  (`cover_tilt.txt`) finds the dispersion along covers different, and in the limit the tilt of each
  modulus, `e^{v p}`, is a function of `α` of order one, so nothing in the derivation makes that
  difference vanish. The recursion agrees with the measured losses within about 5% at every size
  tried; whether that error goes to zero is not known. So `1.1275` is the constant of the recursion's
  limit, with an unquantified model error of that order on top.

## Notation

`s` a prime modulus; `u_t = 2/(t − 3)` for the primes `5 ≤ t < s`, `1/(t − 2)` for the primes `t > s`;
`u(d)` their product over the primes of a squarefree `d` prime to `6s`; `f(j) = Σ_{d | j} u(d)`;
`a = 6s/(s − 1)`, `c = ∏ (1 + u_t/t)^{-1}`; `W(j) = a c f(j)` the pair weight;
`R(m) = a m − Σ_{j ≤ m} W(j)`, `M(x) = Σ_{d ≤ x} u(d)`; `g₂ = ½ ∏_p (1 − 1/p)² (1 + u_p)` with
`u_p = 2/(p − 3)` for all `p ≥ 5`; `m(ρ)` the solution of `m = ρ²` on `[0, 1]`,
`ρ m′ = 2m − m(ρ − 1)` beyond. Constants: `γ` Euler's, `C₂` the twin-prime constant.

## Step 1: `R(m) = (a c / 2) M(m) (1 + o(1))`

True. The exact form (`pairWeight_defect`) is `R(m) = a c Σ_d u(d) (m/d − ⌊m/d⌋)`. In Dirichlet series,
`Σ f(j) j^{-w} = ζ(w) · Σ u(d) d^{-w}`, and `ζ(w)/ζ(0) = exp(w ln 2π + …)`, which gives, in every range
of `m` and `s`,

    R(m) = (a c / 2) · M(2π m) − a/2      on the mean over integers m,

up to a term of second order (at most `0.12` in the units of the table) and an oscillation of a few
units at single values of `m`. The `−a/2` is the difference between integers and reals (`{m/d}` averages
`½ − 1/(2d)` over integers); in the dispersion it cancels the term `a·L2(0)` exactly.

* So `R/((a c/2) M) − 1 = ln(2π) · M′/M − 1/(c M)`, where `M′ = dM/d ln m`: the first term is about
  `3.68/(ln m + 3.6)` below `s` and `1.84/(ln(m/s) + 3.6)` far above. The ratio is 1.17 at
  `m = 10^6` and 1.12 at `10^10` for `s` infinite, 1.06 at `10^10` for `s = 1009`.
* `R(m)` at one `m` depends on the small prime factors of `m` (when `d` divides `m` its term vanishes).
  Powers of ten sit 2 to 6 units low. The tables use the mean of `R` over 65,536 consecutive `m`.
* Checked (`steps_1_2.txt`): the mean of `R` minus `(a c/2) M(2π m) − a/2` is between `−0.02` and
  `+0.05` at every `m` from `10^6` to `10^10` for the five finite `s`, on values of 40 to 140, and
  `+0.10` to `+0.14` for `s` infinite. That remainder is the predicted second-order term,
  `0.317 · (a c/2) · d²M/d(ln m)²` (`0.317 = −ζ″(0) − ½ ln² 2π`), which is `0.12` where `M` is
  quadratic in `ln m` and vanishes where it is linear.

## Step 2: `M(s^ρ) = g₂ ln² s · m(ρ) (1 + o(1))`

True, and the equation is the right one. It follows from the exact identity

    M(x) ln x − ∫₁ˣ M(t) dt/t = Σ over prime powers p^k of (−1)^{k−1} u_p^k ln p · M(x / p^k),

whose weight `W(t) = Σ_{p^k ≤ t} (−1)^{k−1} u_p^k ln p` is `2 ln t − (2γ + ln 12) + o(1)` below `s`
(because `u_p/(1 + u_p) = 2/(p − 1)` exactly) and grows like `ln t` above `s`. The `2 ln t` and `ln t`
give `ρ m′ = 2m − m(ρ − 1)`. The constant gives the first correction:

    M(s^ρ) = g₂ ln² s · [ m(ρ) + (2γ + ln 12) · m′(ρ) / ln s + … ],

a shift of `ln x` by `2γ + ln 12 = 3.639` (`x → 38.07 x`). Below `s` the expansion is exact up to a
power of `x`:

    M(x) = g₂ [ ln² x + 7.27868 ln x + 5.5170 ],        g₂ = 0.0874661499,

and the exact sums agree with it to `2·10^-4` from `x = 10^6` on and to `10^-5` from `10^8` to
`10^11`.

* The leading term alone is far off at any size that can be summed: the ratio
  `M(s^ρ)/(g₂ ln² s m(ρ))` is 2.16, 1.47, 1.26 at `ρ = 1, 2, 3` for `s = 1009`.
* With the first-order term the ratio is within 0.7% of 1 for `ρ ≥ 2` at `s = 1009`, and
  `(ratio − 1) · ln s` tends to the predicted `(2γ + ln 12) m′(ρ)/m(ρ)`: 3.22 against 3.15 at `ρ = 2`,
  1.80 against 1.79 at `ρ = 3`.
* The slope `2 e^γ` at large `ρ` is confirmed twice over: by the delay equation
  (`scripts/cover_count/Lam_check.py`, `m(ρ)/(ρ − 1) = 3.562144835980` at `ρ = 20` and `40`) and by the
  exact asymptotics for fixed `s`, `M(x) = H_s(0) · (ln(x/s) + 2γ + ln 12)` with `H_s(0) ~ 2 g₂ e^γ ln s`.

## Step 3: the constants, and the profile `v(α) = 1 − (e^-γ/2) α m((1 − α)/α)`

True. `c g₂ = 1/(24 C₂)`: numerically `24 C₂ c g₂ = 1.0000000000`, and it is
`∏_{p ≥ 5} (p − 1)²/(p (p − 2)) = 3/(4 C₂)` (`tendsto_prod_sq_div` in `CoverPairSums.lean`) divided by
18. With `φ(s) = 2 C₂ e^-γ / ln s` the deficit of the dispersion is
`(φ(s)/li(Q)) · 2 Σ R(m) ΔL2(m) → (e^-γ/2) α m(ρ₀)`, `ρ₀ = (1 − α)/α`; rederived here.

The same expansions give the first correction, which the research session had measured and not
derived:

    variance/mean = v(α) − c(α)/ln Q + …,     c(α) = (e^-γ/2) · [ (2γ + ln 4π − 1) · m′(ρ₀) + α · m(ρ₀) ].

The constant `2γ + ln 4π − 1 = 2.6855` collects the shift of step 2 (`2γ + ln 12`), the shift of
step 1 (`ln 2π`), the `6` of `d = 6 s j` (`−ln 6`) and the mean of `ln y` over the range (`−1`); the term
`α m` is from `li(Q)` and from the Hardy–Littlewood integral. Against the measured `c(α)`
(`cover_limit.txt`, extrapolated in `1/ln Q` from its two sizes): 2.35 against 2.38 at `α = 0.4`,
2.00 against 2.06 at 0.45, 1.65 against 1.59 at 0.5, 1.34 against 1.33 at 0.55, 1.08 against 1.08 at
0.6, 0.87 against 0.89 at 0.65. Below `α = 0.3` the formula is 10 to 20% under the measurement; the
moduli there are below 100 at the sizes measured and an expansion in `1/ln s` cannot be expected to
hold.

## Step 4: from the recursion to `dp/d ln α = (e^{v p} − 1)/v`

`price_check.py` runs the recursion `p_s = p_{s⁺} − κ_s(p_{s⁺})/(s − 1)` over the actual odd primes up
to `x`, with `v_s = v(ln s/ln Q)`, the limit profile, so that the only thing tested is the passage from
the primes to the continuum. `Λ_disc = p₃ ln Q/(2 C₂ e^-γ)` against `Λ(λ)` (`price_check.txt`):

| `x` | 10^3 | 10^4 | 10^5 | 10^6 | 10^7 | 10^8 |
|---|---|---|---|---|---|---|
| `Λ_disc/Λ` at `λ = 1` | 0.9574 | 0.9827 | 0.9912 | 0.9947 | 0.9964 | 0.9973 |
| at `λ = 0.9` | 0.9607 | 0.9844 | 0.9922 | 0.9953 | 0.9967 | 0.9976 |
| at `λ = 0.8` | 0.9639 | 0.9860 | 0.9930 | 0.9958 | 0.9971 | 0.9978 |

* The gap times `ln² x` is `−2.4, −1.8, −1.4, −1.2, −1.1, −1.1`: the approach is like `1/ln² x`.
* The price before the first modulus, as a function of the price `P` after the last one, has its
  maximum at `P = ln(x − 1)/v_x` (0.999 of it at every size) and is flat: moving `P` by 10% changes it
  by `10^-3` at `x = 10^3` and by `10^-5` at `10^6`; at `1.2 P₀` it has collapsed for `x ≥ 10^6`. So
  the largest price is well defined and is the blow-up solution of the continuum equation.
* `Λ(λ)` recomputed for `λ = 0.6, 0.7, 0.8, 0.9, 0.95, 1`: 2.44038, 1.93436, 1.60177, 1.36834,
  1.27625, 1.19639, the research session's table to all its digits.

## Files

* `pair_limit.c`: exact `M`, `Σ u(d)/d`, `Σ f`, `R` and the windowed mean of `R` at checkpoints, by a
  segmented sieve; the constant `c` from the primes up to 10^9 and an integral tail.
  `pair_limit_s*.txt`: its output for `s = 101, 1009` (to 10^10), `10007, 100003, 1000003` (to 10^11)
  and `s` infinite (`pair_limit_sinf.txt`, to 10^11).
* `analyse.py`, `steps_1_2.txt`: the tables behind steps 1 to 3.
* `price_check.py`, `price_check.txt`: step 4.

    gcc -O3 -march=native -fopenmp -o pair_limit pair_limit.c -lm
    ./pair_limit 1009 10000000000 > pair_limit_s1009.txt         (s = 0 stands for s infinite)
    python3 -I analyse.py pair_limit_s101.txt pair_limit_s1009.txt pair_limit_s10007.txt pair_limit_s100003.txt pair_limit_s1000003.txt pair_limit_sinf.txt > steps_1_2.txt
    python3 -I price_check.py > price_check.txt
