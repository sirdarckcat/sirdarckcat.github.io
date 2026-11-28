# Copyright 2026 Google LLC
from typing import Any, Mapping
import math
import random
import numpy as np

# EVOLVE-BLOCK-START
def optimize_cover_step(congr_dict, cand_mods, targets, cnt_array, logm, logboost, t_temp):
    """Optimize a single step of congruence cover using simulated annealing style logic.

    Args:
        congr_dict: Dictionary of r -> a
        cand_mods: List of prime candidates
        targets: np.array of target primes
        cnt_array: np.array of coverage counts
        logm: current log of modulus M
        logboost: current log of boost factor
        t_temp: current temperature

    Returns:
        Updated congr_dict
    """
    import numpy as np
    import random

    if len(targets) == 0:
        # Safety fallback
        kind = random.random()
        r_in = random.choice(list(congr_dict)) if congr_dict else None
        if kind < 0.5 and r_in is not None:
            a_old = congr_dict[r_in]
            a_new = random.randint(0, r_in - 1)
            if a_new != a_old:
                congr_dict[r_in] = a_new
        elif kind < 0.7 and r_in is not None:
            del congr_dict[r_in]
        else:
            r_out = random.choice(cand_mods)
            if r_out not in congr_dict:
                a_new = random.randint(0, r_out - 1)
                congr_dict[r_out] = a_new
        return congr_dict

    # Crazy Idea: Unify Add/Drop/Optimize into a single thermodynamic step!
    # Generate proposed mutations, evaluate their exact true delta on coverage,
    # scale by log(r) cost, and sample directly using the Gumbel-Max trick.
    mods_in = list(congr_dict.keys())
    cand_pool = [m for m in cand_mods if m not in congr_dict]

    mutations = []
    if cand_pool:
        for r in random.sample(cand_pool, min(20, len(cand_pool))):
            mutations.append(('add', r))
    if mods_in:
        for r in random.sample(mods_in, min(10, len(mods_in))):
            mutations.append(('optimize', r))
        for r in random.sample(mods_in, min(5, len(mods_in))):
            mutations.append(('drop', r))

    if not mutations:
        return congr_dict

    scores = []
    final_mutations = []

    uncovered = (cnt_array == 0)
    covered_once = (cnt_array == 1)

    for action, r in mutations:
        cost = np.log(r) if r > 1 else 1.0

        if action == 'add':
            counts = np.bincount(targets[uncovered] % r, minlength=r)
            a = int(np.argmax(counts))
            score = counts[a] / cost
            scores.append(score)
            final_mutations.append(('add', r, a))

        elif action == 'optimize':
            a_old = congr_dict[r]
            lost = np.sum(covered_once & ((targets % r) == a_old))
            bg_uncovered = uncovered | (covered_once & ((targets % r) == a_old))
            counts = np.bincount(targets[bg_uncovered] % r, minlength=r)
            a = int(np.argmax(counts))
            score = (counts[a] - lost) / cost
            scores.append(score)
            final_mutations.append(('optimize', r, a))

        elif action == 'drop':
            a = congr_dict[r]
            lost = np.sum(covered_once & ((targets % r) == a))
            score = -lost / cost
            scores.append(score)
            final_mutations.append(('drop', r, None))

    # Normalize scores roughly to [0, 1] scale to match temperature magnitude
    scores = np.array(scores)
    max_score = np.max(np.abs(scores))
    if max_score > 0:
        scores = scores / max_score

    temp = max(t_temp, 1e-4)
    noisy_scores = scores + temp * np.random.gumbel(size=len(scores))
    best_idx = int(np.argmax(noisy_scores))

    best_action, best_r, best_a = final_mutations[best_idx]
    if best_action in ('add', 'optimize'):
        congr_dict[best_r] = best_a
    elif best_action == 'drop':
        del congr_dict[best_r]

    return congr_dict
# EVOLVE-BLOCK-END

def evaluate(eval_inputs: Mapping[str, Any]) -> dict[str, float]:
    """Run evaluation on the optimized step."""
    # Let's say we maximize -n_digits_est (smaller estimated N-size)
    # Using sympy/math to compute est digits
    import sympy
    import numpy as np
    Q = 100003
    targets = np.array(list(sympy.primerange(3, Q)), dtype=np.int64)
    # Let's run the optimize_cover_step starting from empty cover for some iterations
    congr_dict = {}
    cand_mods = [int(r) for r in sympy.primerange(3, 8000)]
    cnt_array = np.zeros(len(targets), dtype=np.int16)
    logm = math.log(2)
    logboost = math.log(2.0)

    for it in range(10):
        t_temp = 0.8 * (0.02 / 0.8) ** (it / 10)
        # Update cnt_array based on congr_dict
        cnt_array = np.zeros(len(targets), dtype=np.int16)
        logm = math.log(2)
        logboost = math.log(2.0)
        for r, a in congr_dict.items():
            cnt_array += (targets % r) == a
            logm += math.log(r)
            logboost += math.log(r / (r - 1))

        congr_dict = optimize_cover_step(congr_dict, cand_mods, targets, cnt_array, logm, logboost, t_temp)

    # Recalculate final metrics
    cnt_array = np.zeros(len(targets), dtype=np.int16)
    logm = math.log(2)
    logboost = math.log(2.0)
    for r, a in congr_dict.items():
        cnt_array += (targets % r) == a
        logm += math.log(r)
        logboost += math.log(r / (r - 1))

    n_res = int((cnt_array == 0).sum())
    boost = math.exp(logboost)
    m_digits = logm / math.log(10)

    ub = n_res * boost
    LN10 = math.log(10)
    D = (m_digits + math.sqrt(m_digits ** 2 + 4 * ub / (LN10 * LN10))) / 2
    return {"neg_est_digits": -float(D)}
