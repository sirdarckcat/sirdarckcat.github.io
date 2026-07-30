# Cute Goldbach Gaps — the thesis

`thesis.pdf` (60 pages) collects the whole Goldbach-desert research
programme into one document. Each chapter is written to stand alone as a
paper (the July 2026 manuscript `slop/goldbach/goldbach.pdf` is the
outdated ancestor of Chapter 2):

1. Introduction — the least Goldbach summand, the three record games,
   the certified record board.
2. Foundations — factorial/Wilson warm-ups, primorial deserts,
   unconditional unboundedness, prime-offset covers, the FGKMT-transfer
   lower bound, and the first-generation records (g = 109,621 @ 237
   digits; g = 105,667 @ 199 digits).
3. The cost model — E = |U|·boost/ln N, validated to ±0.1 nats over
   1.2·10⁹ candidates; frontiers, regimes, the million-desert wall,
   Poisson discipline, truth calibration.
4. Engineering + the record ladder — both pipelines, the engine
   optimizations, certification standard, and every certified
   construction down to T(100,000) ≤ 8.27·10¹⁴⁹ (g = 104,527) and
   R(10¹⁹⁹) ≥ 119,419.
5. Prime gaps vs deserts — g = 1,157,341 @ 2,480 digits and the
   2,692-digit desert with a certified 126.5× desert-to-gap ratio;
   the certification wall and the two-sided (Proth-first) idea.
6. Limits of compression — joint-representative and set-valued-conditioning
   ceilings, the density-1.026 subset-sum barrier, the Johnson-radius
   experiment, the sub-100-digit verdict (~9·10⁵ GPU-years), THE WALL
   per game.
7. The Divisor-Paradigm Closure Theorem — schemes/certificates, the
   grammar L, three lemmas, the falsification engine (13,661 + 41
   adversarial instances, zero passes), Door 1 (rounding gap), the
   three doors.
8. Conclusions — established results, the ranked open problems, the
   methodological legacy.

Appendix A maps every claim to its machine-checkable artifact in
`goldbach/` and `slop/goldbach/` and gives the verification runbook.

Build: `pdflatex thesis.tex` (×2 for cross-references); TeX Live with
amsmath/booktabs/hyperref suffices.
