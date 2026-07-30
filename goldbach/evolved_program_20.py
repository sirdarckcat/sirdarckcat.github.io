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

    def compute_D(lm, lb, nr):
        m_digits = lm / math.log(10)
        boost = math.exp(lb)
        ub = nr * boost
        LN10 = math.log(10)
        return (m_digits + math.sqrt(max(0.0, m_digits ** 2 + 4 * ub / (LN10 * LN10)))) / 2.0

    # Multi-step inner simulated annealing loop to find much deeper local minima
    for inner in range(12):
        # 1. Recalculate cnt_array, logm, logboost based on current congr_dict
        cnt_array = np.zeros(len(targets), dtype=np.int16)
        logm = math.log(2)
        logboost = math.log(2.0)
        for r, a in congr_dict.items():
            cnt_array += (targets % r) == a
            logm += math.log(r)
            logboost += math.log(r / (r - 1))

        # 2. Coordinate descent to optimize residues of all active primes stochastically
        active_primes = list(congr_dict.keys())
        random.shuffle(active_primes)
        for r in active_primes:
            a_old = congr_dict[r]
            cnt_array -= (targets % r) == a_old
            uncovered = targets[cnt_array == 0]
            if len(uncovered) > 0:
                counts = np.bincount(uncovered % r, minlength=r)
                max_c = np.max(counts)
                best_aas = np.where(counts == max_c)[0]
                a_new = int(random.choice(best_aas))
            else:
                a_new = 0
            congr_dict[r] = a_new
            cnt_array += (targets % r) == a_new

        n_res = np.sum(cnt_array == 0)
        D_curr = compute_D(logm, logboost, n_res)

        # 3. Generate candidate moves: ADD, DROP, noop
        moves = [('noop', None, None, D_curr)]

        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if cand_pool:
            cand_pool.sort()
            if len(cand_pool) <= 60:
                sampled_adds = cand_pool
            else:
                sampled_adds = cand_pool[:20] + random.sample(cand_pool[20:], 40)

            uncovered = targets[cnt_array == 0]
            for r in sampled_adds:
                if len(uncovered) > 0:
                    counts = np.bincount(uncovered % r, minlength=r)
                    max_c = np.max(counts)
                    best_aas = np.where(counts == max_c)[0]
                    a = int(random.choice(best_aas))
                    k = max_c
                else:
                    a = 0
                    k = 0
                n_res_new = len(uncovered) - k
                logm_new = logm + math.log(r)
                logboost_new = logboost + math.log(r / (r - 1))
                D_new = compute_D(logm_new, logboost_new, n_res_new)
                moves.append(('add', r, a, D_new))

        for r, a in congr_dict.items():
            k_drop = np.sum((cnt_array == 1) & ((targets % r) == a))
            n_res_new = n_res + k_drop
            logm_new = logm - math.log(r)
            logboost_new = logboost - math.log(r / (r - 1))
            D_new = compute_D(logm_new, logboost_new, n_res_new)
            moves.append(('drop', r, None, D_new))

        if congr_dict and cand_pool:
            active_list = list(congr_dict.keys())
            sampled_drops = random.sample(active_list, min(len(active_list), 4))
            if len(sampled_adds) > 5:
                sampled_swaps = sampled_adds[:5] + random.sample(sampled_adds[5:], min(len(sampled_adds)-5, 5))
            else:
                sampled_swaps = sampled_adds

            for r_drop in sampled_drops:
                a_drop = congr_dict[r_drop]
                mask_uncovered = (cnt_array == 0) | ((cnt_array == 1) & ((targets % r_drop) == a_drop))
                uncovered_swap = targets[mask_uncovered]
                logm_drop = logm - math.log(r_drop)
                logboost_drop = logboost - math.log(r_drop / (r_drop - 1))
                for r_add in sampled_swaps:
                    if len(uncovered_swap) > 0:
                        counts = np.bincount(uncovered_swap % r_add, minlength=r_add)
                        max_c = np.max(counts)
                        a_add = int(random.choice(np.where(counts == max_c)[0]))
                        k_add = max_c
                    else:
                        a_add = 0
                        k_add = 0
                    n_res_new = len(uncovered_swap) - k_add
                    logm_new = logm_drop + math.log(r_add)
                    logboost_new = logboost_drop + math.log(r_add / (r_add - 1))
                    D_new = compute_D(logm_new, logboost_new, n_res_new)
                    moves.append(('swap', r_drop, r_add, a_add, D_new))

        # 4. Boltzmann selection
        deltas = np.array([move[3] - D_curr for move in moves])
        curr_temp = max(t_temp * (0.8 ** inner), 1e-4)
        logits = -deltas / curr_temp
        logits -= np.max(logits)
        probs = np.exp(logits)
        probs /= np.sum(probs)

        idx = np.random.choice(len(moves), p=probs)
        move_chosen = moves[idx]
        chosen_action = move_chosen[0]

        if chosen_action == 'add':
            congr_dict[move_chosen[1]] = move_chosen[2]
        elif chosen_action == 'drop':
            del congr_dict[move_chosen[1]]
        elif chosen_action == 'swap':
            del congr_dict[move_chosen[1]]
            congr_dict[move_chosen[2]] = move_chosen[3]

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
