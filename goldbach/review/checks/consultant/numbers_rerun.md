# numbers_rerun: re-run of data/limit_check on origin/ccr-cdb2641a-5zg8un

Run dir: consultcheck/run/numbers_rerun/ (scripts copied by git show; rec/ = recorded outputs, new/ = my outputs, extra.py = my extra checks).
Environment: python3 -I via runner.py (adds script dir to sys.path); system numpy; scipy 1.18.1 pip-installed into ./deps (not present on the machine).

## Reproduction: 13/13 recorded outputs byte-identical (timing fields stripped)
greedy_real small/inc/dec, bulkgain, allones, topcheck 20000 0.70, topode3 (out_top_capacity), calib, extrap,
model_greedy, coherent_surv (all four x incl. 1e6 and 3.75e6), coherent_D 10000, coherent 10000 0.72.
Not run: topode.py standalone (no recorded output of its own; used as a library by topode3/extrap).

## Quotation check: LIMIT_CHECK.md and COHERENT_BLOCK.md quote all outputs correctly
3.1 table, 3.2 table, 3.3 table and 0.915, 3.4 both tables, calib 0.82..0.88, 3.5 (0.72/0.86/0.87), CB 3.1 table, CB 3.2 (0.39-0.48, 0.31), CB 4 (0.398 vs 0.383, 0.459 vs 0.420).

## Caveats found (none is a transcription error)
1. CB 3.1 ratios 0.93/0.86/0.72/0.57 are best-of-50 N1, and the best N1 is odd in all four cases. Mean over the 50 N1: 1.00/0.95/0.85/0.72 of ln z/ln y;
   even N1 mean: 1.04/1.00/0.93/0.81. At x=1e4 a typical N1 gives no gain at all. Comparator ln z/ln y is 1-2.5% below the exact product (0.5740, 0.5070, 0.4132, 0.3735),
   so vs exact the best-of-50 ratios are 0.904/0.854/0.708/0.567.
2. Greedy completion is not monotone in Q: x=2000 leftover 1 at 0.645, 0 at 0.650-0.655, 2 at 0.660, 0 at 0.665 and 0.675. Recorded 0.656; last success on a 0.005 grid 0.675. x=1e4, 2e4 clean (0.710, 0.715).
3. coherent_D starts bisection at 0.30 x ln^2 x; "0.000" = fails at 0.30, not "no complete cover". y=x/2 results (0, 0.308, 0, 0, 0, 0.300) show the non-monotonicity too.
4. 3.3 "0.718 of the random-bulk figure" is vs kappa*pi/ln y1 (10245), not the exact product. Model max uses 4 Poisson samples per modulus.
5. "accurate to about 10%" (3.3, one-step model at real U) vs "12 to 18% weaker" (3.4, full ODE) are different comparisons.
6. model_greedy thresholds are noisy (3 random reps, seed fixed): 0.859, 0.843, 0.890, 0.890, 0.874.
7. README table omits coherent*.py; says table 2e7 although coherent scripts build 6e7/7e7.
