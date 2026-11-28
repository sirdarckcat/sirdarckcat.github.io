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
    C_UB = 0.7544470357876127

    def compute_D(lm, lb, nr):
        m_digits = lm / LN10
        ub = nr * math.exp(lb)
        return (m_digits + math.sqrt(max(0.0, m_digits * m_digits + C_UB * ub))) / 2.0

    uncovered_mask = (cnt_array == 0)
    n_res_curr = np.sum(uncovered_mask)
    D_curr = compute_D(logm, logboost, n_res_curr)

    cand_pool = [m for m in cand_mods if m not in congr_dict]
    mods_in = list(congr_dict.keys())

    moves = [('noop', None, None, D_curr)]

    # 1. ADD moves
    if cand_pool:
        sampled_adds = cand_pool if len(cand_pool) <= 35 else cand_pool[:15] + random.sample(cand_pool[15:], 20)
        uncovered_targets = targets[uncovered_mask]
        for r in sampled_adds:
            if len(uncovered_targets) > 0:
                rem = uncovered_targets % r
                counts = np.bincount(rem, minlength=r)
                a = int(np.argmax(counts))
                k = counts[a]
            else:
                a = 0
                k = 0
            n_res_new = len(uncovered_targets) - k
            logm_new = logm + math.log(r)
            logboost_new = logboost + math.log(r / (r - 1))
            D_new = compute_D(logm_new, logboost_new, n_res_new)
            moves.append(('add', r, a, D_new))

    # 2 & 3. OPTIMIZE and DROP moves for current mods
    for r in mods_in:
        a_old = congr_dict[r]
        is_covered_by_r = (targets % r) == a_old
        cnt_bg = cnt_array - is_covered_by_r
        bg_uncovered_mask = (cnt_bg == 0)

        # DROP
        n_res_drop = np.sum(bg_uncovered_mask)
        logm_drop = logm - math.log(r)
        logboost_drop = logboost - math.log(r / (r - 1))
        moves.append(('drop', r, None, compute_D(logm_drop, logboost_drop, n_res_drop)))

        # OPTIMIZE
        uncovered_targets_bg = targets[bg_uncovered_mask]
        if len(uncovered_targets_bg) > 0:
            rem = uncovered_targets_bg % r
            counts = np.bincount(rem, minlength=r)
            a_new = int(np.argmax(counts))
            k = counts[a_new]
        else:
            a_new = 0
            k = 0
        n_res_opt = len(uncovered_targets_bg) - k
        moves.append(('optimize', r, a_new, compute_D(logm, logboost, n_res_opt)))

    deltas = np.array([move[3] - D_curr for move in moves])
    temp = max(t_temp, 1e-4)
    logits = -deltas / temp
    logits = logits - np.max(logits)
    probs = np.exp(logits)
    probs /= np.sum(probs)

    idx = np.random.choice(len(moves), p=probs)
    chosen_action, r, a, D_new = moves[idx]

    if chosen_action == 'add':
        congr_dict[r] = a
    elif chosen_action == 'optimize':
        congr_dict[r] = a
    elif chosen_action == 'drop':
        del congr_dict[r]

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
