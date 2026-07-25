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

    best_congr = dict(congr_dict)
    best_D = float('inf')

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

        # 2. Coordinate descent to optimize residues of all active primes deterministically (until convergence)
        for _ in range(2):
            changed = False
            for r in list(congr_dict.keys()):
                a_old = congr_dict[r]
                cnt_array -= (targets % r) == a_old
                uncovered = targets[cnt_array == 0]
                if len(uncovered) > 0:
                    a_new = int(np.argmax(np.bincount(uncovered % r, minlength=r)))
                else:
                    a_new = 0
                if a_new != a_old:
                    changed = True
                congr_dict[r] = a_new
                cnt_array += (targets % r) == a_new
            if not changed:
                break

        n_res = np.sum(cnt_array == 0)
        D_curr = compute_D(logm, logboost, n_res)

        if D_curr < best_D:
            best_D = D_curr
            best_congr = dict(congr_dict)

        # 3. Generate candidate moves: ADD, DROP, SWAP, noop
        moves = [('noop', None, None, D_curr)]

        k_drops = {}
        for r, a in congr_dict.items():
            k_drops[r] = np.sum((cnt_array == 1) & ((targets % r) == a))
            n_res_new = n_res + k_drops[r]
            logm_new = logm - math.log(r)
            logboost_new = logboost - math.log(r / (r - 1))
            D_new = compute_D(logm_new, logboost_new, n_res_new)
            moves.append(('drop', r, None, D_new))

        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if cand_pool:
            cand_pool.sort()
            if len(cand_pool) <= 80:
                sampled_adds = cand_pool
            else:
                sampled_adds = cand_pool[:40] + random.sample(cand_pool[40:], 40)

            add_moves = []
            uncovered = targets[cnt_array == 0]
            for r in sampled_adds:
                if len(uncovered) > 0:
                    counts = np.bincount(uncovered % r, minlength=r)
                    a = int(np.argmax(counts))
                    k = counts[a]
                else:
                    a = 0
                    k = 0
                n_res_new = len(uncovered) - k
                logm_new = logm + math.log(r)
                logboost_new = logboost + math.log(r / (r - 1))
                D_new = compute_D(logm_new, logboost_new, n_res_new)
                add_moves.append((r, a, D_new))
                moves.append(('add', r, a, D_new))

            # Swap moves: swap one of the worst active primes with one of the best candidates
            if len(congr_dict) > 0 and len(add_moves) > 0:
                active_sorted = sorted(list(congr_dict.keys()), key=lambda r: k_drops.get(r, 0))
                worst_active = active_sorted[:6]
                add_moves.sort(key=lambda x: x[2])
                best_candidates = [item[0] for item in add_moves[:8]]

                for r_old in worst_active:
                    a_old = congr_dict[r_old]
                    mask_uniq = (cnt_array == 1) & ((targets % r_old) == a_old)
                    U_temp = targets[(cnt_array == 0) | mask_uniq]
                    for r_new in best_candidates:
                        if r_new == r_old:
                            continue
                        if len(U_temp) > 0:
                            counts = np.bincount(U_temp % r_new, minlength=r_new)
                            a_new = int(np.argmax(counts))
                            k_cover = counts[a_new]
                        else:
                            a_new = 0
                            k_cover = 0
                        n_res_new = len(U_temp) - k_cover
                        logm_new = logm - math.log(r_old) + math.log(r_new)
                        logboost_new = logboost - math.log(r_old / (r_old - 1)) + math.log(r_new / (r_new - 1))
                        D_new = compute_D(logm_new, logboost_new, n_res_new)
                        moves.append(('swap', r_old, (r_new, a_new), D_new))

        # 4. Boltzmann selection
        deltas = np.array([move[3] - D_curr for move in moves])
        curr_temp = max(t_temp * (0.75 ** inner), 1e-5)
        logits = -deltas / curr_temp
        logits -= np.max(logits)
        probs = np.exp(logits)
        probs /= np.sum(probs)

        idx = np.random.choice(len(moves), p=probs)
        chosen_action, r, a, D_new = moves[idx]

        if chosen_action == 'add':
            congr_dict[r] = a
        elif chosen_action == 'drop':
            del congr_dict[r]
        elif chosen_action == 'swap':
            del congr_dict[r]
            r_new, a_new = a
            congr_dict[r_new] = a_new

    return best_congr
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
