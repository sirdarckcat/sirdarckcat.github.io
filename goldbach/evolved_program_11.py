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
    import math

    if len(targets) == 0:
        return congr_dict

    def compute_D(lm, lb, nr):
        m_digits = lm / math.log(10)
        boost = math.exp(lb)
        ub = nr * boost
        LN10 = math.log(10)
        D = (m_digits + math.sqrt(max(0.0, m_digits ** 2 + 4 * ub / (LN10 * LN10)))) / 2.0
        return D

    n_res_curr = np.sum(cnt_array == 0)
    D_curr = compute_D(logm, logboost, n_res_curr)

    cand_pool = [m for m in cand_mods if m not in congr_dict]
    cand_pool.sort()
    mods_in = list(congr_dict.keys())

    moves = [('noop', None, None, D_curr)]

    # 1. ADD moves: evaluation of 100 smallest and 100 random larger candidates
    if cand_pool:
        if len(cand_pool) <= 200:
            sampled_adds = cand_pool
        else:
            sampled_adds = cand_pool[:100] + random.sample(cand_pool[100:], 100)

        uncovered_mask = (cnt_array == 0)
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

    # 2. OPTIMIZE moves for current mods
    for r in mods_in:
        a_old = congr_dict[r]
        is_covered_by_r = (targets % r) == a_old
        cnt_bg = cnt_array - is_covered_by_r
        bg_uncovered_mask = (cnt_bg == 0)
        uncovered_targets_bg = targets[bg_uncovered_mask]

        if len(uncovered_targets_bg) > 0:
            rem = uncovered_targets_bg % r
            counts = np.bincount(rem, minlength=r)
            a_new = int(np.argmax(counts))
            k = counts[a_new]
        else:
            a_new = 0
            k = 0
        if a_new != a_old:
            n_res_new = len(uncovered_targets_bg) - k
            D_new = compute_D(logm, logboost, n_res_new)
            moves.append(('optimize', r, a_new, D_new))

    # 3. SWAP moves: swap an existing mod with a candidate mod
    if mods_in and cand_pool:
        n_src = min(len(mods_in), 10)
        src_mods = random.sample(mods_in, n_src)
        n_dst = min(len(cand_pool), 15)
        dst_mods = cand_pool[:n_dst//2] + random.sample(cand_pool[n_dst//2:], n_dst - n_dst//2)
        dst_mods = list(set(dst_mods))

        for r_in in src_mods:
            a_in = congr_dict[r_in]
            is_covered_by_r = (targets % r_in) == a_in
            cnt_bg = cnt_array - is_covered_by_r
            bg_uncovered_mask = (cnt_bg == 0)
            uncovered_targets_bg = targets[bg_uncovered_mask]

            logm_bg = logm - math.log(r_in)
            logboost_bg = logboost - math.log(r_in / (r_in - 1))

            for r_out in dst_mods:
                if r_out == r_in:
                    continue
                if len(uncovered_targets_bg) > 0:
                    rem = uncovered_targets_bg % r_out
                    counts = np.bincount(rem, minlength=r_out)
                    a_out = int(np.argmax(counts))
                    k = counts[a_out]
                else:
                    a_out = 0
                    k = 0
                n_res_new = len(uncovered_targets_bg) - k
                logm_new = logm_bg + math.log(r_out)
                logboost_new = logboost_bg + math.log(r_out / (r_out - 1))
                D_new = compute_D(logm_new, logboost_new, n_res_new)
                moves.append(('swap', (r_in, r_out), a_out, D_new))

    # 4. DROP moves for current mods
    for r in mods_in:
        a = congr_dict[r]
        is_covered_by_r = (targets % r) == a
        cnt_bg = cnt_array - is_covered_by_r
        n_res_new = np.sum(cnt_bg == 0)
        logm_new = logm - math.log(r)
        logboost_new = logboost - math.log(r / (r - 1))
        D_new = compute_D(logm_new, logboost_new, n_res_new)
        moves.append(('drop', r, None, D_new))

    deltas = np.array([move[3] - D_curr for move in moves])
    temp = max(t_temp * 0.5, 1e-4)
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
    elif chosen_action == 'swap':
        r_in, r_out = r
        if r_in in congr_dict:
            del congr_dict[r_in]
        congr_dict[r_out] = a

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
