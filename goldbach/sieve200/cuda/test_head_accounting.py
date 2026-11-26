#!/usr/bin/env python3
"""The expected-hit accounting of search_gpu5_head.patch on a simulation (numpy only).

A kept member has A rows alive on the B = 1e8 sieve, each prime with probability p0 (P(prime | alive on the B sieve)) independently.  The deep head sieves the first `hrows` rows by the primes in (B, B2]:
a head row is removed with probability c = 1 - ln B / ln B2 (it has a factor there: composite); the head rows that stay have the higher probability p0 / (1 - c).  Without the head the driver estimates
p^ = PRP / tests over all tests and sums (1 - p^)^count.  With it: p^ = the PRP fraction of the tests PAST each member's head rows, and the exponent is the PRE-head count (Window.cnt_acc).  Checked, on a large
simulated pool: (1) the first-PRP row, the success flag and the PRP flag of every member are the same with and without the head (the same random draws), (2) the counted tests fall by the predicted 8-9%,
(3) the logged expected hits and expected near-miss values (rows below the threshold row) of the two accountings agree within ~1% (same PRP numerator, a denominator that estimates the same tests), where the NAIVE accounting (p^ over all tests,
post-head counts) is off by a factor of ~10.

    python3 test_head_accounting.py
"""
import numpy as np

rng = np.random.default_rng(7)
P0, B, B2, HROWS, N, THR = 0.0715, 1e8, 1e9, 64, 400000, 1200          # members, threshold row for the near-miss accounting
c = 1.0 - np.log(B) / np.log(B2)
ph = P0 / (1.0 - c)
# rows 0..1247, each alive on the B sieve with probability 0.31 (the kept members have ~383 alive rows of 1,248)
R = 1248
alive = rng.random((N, R)) < 0.307
head = np.arange(R) < HROWS
removed = alive & head[None, :] & (rng.random((N, R)) < c)                  # a head row with a factor in (B, B2]: composite, leaves the list
prime = alive & ~removed & (rng.random((N, R)) < np.where(head[None, :], ph, P0))
# the first-PRP row of a member (ascending rows), -1: none (a success)
first_prime = np.where(prime.any(axis=1), prime.argmax(axis=1), -1)


def simulate(lists_alive):
    """what the driver sees for the rows in lists_alive (bool [N, R]): tests = index of the first PRP among the listed rows + 1 (all of them for a success), prp flag, cnt"""
    cnt = lists_alive.sum(axis=1)
    cum = np.cumsum(lists_alive, axis=1)                                   # 1-based index of a listed row among the listed rows
    pr = prime & lists_alive
    has = pr.any(axis=1)
    frow = np.where(has, pr.argmax(axis=1), -1)
    tests = np.where(has, cum[np.arange(N), np.maximum(frow, 0)], cnt)
    return cnt, tests.astype(np.int64), has, frow


cnt0, tests0, prp0, frow0 = simulate(alive)
cnt1, tests1, prp1, frow1 = simulate(alive & ~removed)
assert np.array_equal(frow0, frow1) and np.array_equal(prp0, prp1), "the head changed a first-PRP row"
print(f"(1) first-PRP rows and PRP / success flags identical for {N} members; successes (all rows composite): {int((frow1 < 0).sum())}")
print(f"(2) counted tests: {tests0.sum()} without the head, {tests1.sum()} with it: {100 * (1 - tests1.sum() / tests0.sum()):.2f}% fewer (model: ~8.6% for 64 rows, B2 = 1e9)")

# the production accounting (no head): p^ over all tests, exponent = count
pp0, tt0 = int(prp0.sum()), int(tests0.sum())
p_prod = pp0 / tt0
hits_prod = float(((1.0 - p_prod) ** cnt0.astype(np.float64)).sum())
cb0 = (alive & (np.arange(R)[None, :] < THR)).sum(axis=1)                  # alive rows below the threshold row: exponent of the near-miss expectation
near_prod = float(((1.0 - p_prod) ** cb0.astype(np.float64)).sum())
# the head accounting (the patch's formulas): head_n = head rows left in the list, tests_o past them, c_emp = removed / (removed + head rows left), p_mod = all PRPs / (tests on head rows / (1 - c_emp) + tests_o),
# exponents cnt_acc / cb + (cnt_acc - cnt)
cnt_acc = cnt0
head_n = (alive & ~removed & head[None, :]).sum(axis=1).astype(np.int64)
tests_o = np.maximum(tests1 - head_n, 0)
prp_o = prp1 & (tests1 > head_n)
rem_tot = int((cnt_acc - cnt1).sum())
c_emp = rem_tot / max(rem_tot + int(head_n.sum()), 1)
tto = int(tests_o.sum())
p_mod = int(prp1.sum()) / ((int(tests1.sum()) - tto) / (1.0 - c_emp) + tto)
hits_head = float(((1.0 - p_mod) ** cnt_acc.astype(np.float64)).sum())
cb1 = (alive & ~removed & (np.arange(R)[None, :] < THR)).sum(axis=1) + (cnt_acc - cnt1)
near_head = float(((1.0 - p_mod) ** cb1.astype(np.float64)).sum())
# the naive accounting: p^ over all tests, post-head counts
p_naive = int(prp1.sum()) / int(tests1.sum())
hits_naive = float(((1.0 - p_naive) ** cnt1.astype(np.float64)).sum())
print(f"    p^ production {p_prod:.5f}; p^ of the head run over all tests {p_naive:.5f}, the head accounting's {p_mod:.5f} (c measured {c_emp:.4f}, model {c:.4f}; P(prime | alive on the B sieve) = {P0})")
print(f"(3) expected hits: production {hits_prod:.5e}, head accounting {hits_head:.5e} ({100 * (hits_head / hits_prod - 1):+.2f}%), naive {hits_naive:.5e} ({hits_naive / hits_prod:.3f}x)")
print(f"    expected near-miss values: production {near_prod:.5e}, head accounting {near_head:.5e} ({100 * (near_head / near_prod - 1):+.2f}%)")
ok = abs(hits_head / hits_prod - 1) < 0.02 and abs(near_head / near_prod - 1) < 0.02 and 0.07 < 1 - tests1.sum() / tests0.sum() < 0.10 and hits_naive / hits_prod < 0.5
print("OK" if ok else "FAILED")
raise SystemExit(0 if ok else 1)
