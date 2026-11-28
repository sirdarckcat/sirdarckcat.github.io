# Copyright 2026 Google LLC
from typing import Any, Mapping
import math
import random
import numpy as np

# EVOLVE-BLOCK-START
def optimize_cover_step(congr_dict, cand_mods, targets, cnt_array, logm, logboost, t_temp):
    """Optimize a single step of congruence cover using simulated annealing style logic."""
    import numpy as np
    import random
    import math

    if len(targets) == 0:
        return congr_dict

    LN10 = 2.302585092994046
    CONST_UB = 0.754446820542302

    def compute_D(lm, lb, nr):
        m_digits = lm / LN10
        ub = nr * math.exp(lb)
        return (m_digits + math.sqrt(max(0.0, m_digits * m_digits + CONST_UB * ub))) / 2.0

    congr_dict = dict(congr_dict)
    cnt_array = cnt_array.copy()

    # Cache targets % r for active primes to speed up drop evaluation and coordinate descent
    mod_cache = {r: targets % r for r in congr_dict}

    # Perform highly-parallelized, ultra-fast Simulated Annealing iterations
    for inner in range(40):
        n_res = np.sum(cnt_array == 0)
        D_curr = compute_D(logm, logboost, n_res)

        moves = [('noop', None, None, D_curr)]

        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if cand_pool:
            cand_pool.sort()
            if len(cand_pool) <= 50:
                sampled_adds = cand_pool
            else:
                sampled_adds = cand_pool[:25] + random.sample(cand_pool[25:], 25)

            uncovered = targets[cnt_array == 0]
            if len(uncovered) > 0:
                for r in sampled_adds:
                    counts = np.bincount(uncovered % r, minlength=r)
                    a = int(np.argmax(counts))
                    k = counts[a]
                    n_res_new = len(uncovered) - k
                    logm_new = logm + math.log(r)
                    logboost_new = logboost + math.log(r / (r - 1))
                    D_new = compute_D(logm_new, logboost_new, n_res_new)
                    moves.append(('add', r, a, D_new))
            else:
                for r in sampled_adds:
                    logm_new = logm + math.log(r)
                    logboost_new = logboost + math.log(r / (r - 1))
                    moves.append(('add', r, 0, compute_D(logm_new, logboost_new, 0)))

        for r, a in congr_dict.items():
            targets_mod_r = mod_cache[r]
            k_drop = np.sum((cnt_array == 1) & (targets_mod_r == a))
            n_res_new = n_res + k_drop
            logm_new = logm - math.log(r)
            logboost_new = logboost - math.log(r / (r - 1))
            D_new = compute_D(logm_new, logboost_new, n_res_new)
            moves.append(('drop', r, a, D_new))

        # Boltzmann selection
        deltas = np.array([move[3] - D_curr for move in moves])
        curr_temp = max(t_temp * (0.85 ** inner), 1e-4)
        logits = -deltas / curr_temp
        logits -= np.max(logits)
        probs = np.exp(logits)
        probs /= np.sum(probs)

        idx = np.random.choice(len(moves), p=probs)
        chosen_action, r, a, D_new = moves[idx]

        if chosen_action == 'add':
            congr_dict[r] = a
            targets_mod_r = targets % r
            mod_cache[r] = targets_mod_r
            cnt_array += targets_mod_r == a
            logm += math.log(r)
            logboost += math.log(r / (r - 1))
        elif chosen_action == 'drop':
            del congr_dict[r]
            targets_mod_r = mod_cache.pop(r)
            cnt_array -= targets_mod_r == a
            logm -= math.log(r)
            logboost -= math.log(r / (r - 1))

    # Perform final deterministic coordinate descent on the residues of all active primes
    for r in list(congr_dict.keys()):
        a_old = congr_dict[r]
        targets_mod_r = mod_cache[r]
        cnt_array -= targets_mod_r == a_old
        uncovered = targets[cnt_array == 0]
        if len(uncovered) > 0:
            a_new = int(np.argmax(np.bincount(uncovered % r, minlength=r)))
        else:
            a_new = 0
        congr_dict[r] = a_new
        cnt_array += targets_mod_r == a_new

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
