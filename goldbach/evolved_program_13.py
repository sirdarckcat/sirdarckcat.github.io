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

    if len(targets) == 0: return congr_dict

    import math
    LN10 = math.log(10)

    def get_D(n_res, lm, lb):
        boost = math.exp(lb)
        m_digs = lm / LN10
        ub = n_res * boost
        return (m_digs + math.sqrt(m_digs**2 + 4 * ub / (LN10**2))) / 2

    curr_cover = congr_dict.copy()
    curr_cnt = cnt_array.copy()
    curr_logm = logm
    curr_logboost = logboost
    curr_n_res = np.count_nonzero(curr_cnt == 0)

    best_cover = curr_cover.copy()
    best_D = get_D(curr_n_res, curr_logm, curr_logboost)
    curr_D = best_D

    # SNO: Run 1000 hyper-accelerated micro-generations of stellar evolution (MCMC inside macro step)
    MICRO_STEPS = 1000
    for step in range(MICRO_STEPS):
        # Local temperature decays dynamically over micro-steps but is scaled by global macro t_temp
        inner_temp = max(t_temp * (1.0 - step / MICRO_STEPS), 1e-4)

        action = random.random()
        if not curr_cover:
            action_type = 'add'
        elif action < 0.4:
            action_type = 'optimize'
        elif action < 0.8:
            action_type = 'add'
        else:
            action_type = 'drop'

        if action_type == 'optimize': # 40% Beta Decay
            r = random.choice(list(curr_cover.keys()))
            a_old = curr_cover[r]

            mask_old = ((targets % r) == a_old).astype(np.int16)
            curr_cnt -= mask_old

            weights = (curr_cnt == 0).astype(float)
            counts = np.bincount(targets % r, weights=weights, minlength=r)
            a_new = int(np.argmax(counts))

            # Quantum tunneling: occasionally make a random jump regardless of structural gradient
            if random.random() < inner_temp:
                a_new = random.randint(0, r - 1)

            curr_cover[r] = a_new
            mask_new = ((targets % r) == a_new).astype(np.int16)
            curr_cnt += mask_new
            curr_n_res = np.count_nonzero(curr_cnt == 0)

            new_D = get_D(curr_n_res, curr_logm, curr_logboost)
            delta = new_D - curr_D

            if delta <= 0 or random.random() < math.exp(-delta / inner_temp):
                curr_D = new_D
            else:
                curr_cnt -= mask_new
                curr_cnt += mask_old
                curr_cover[r] = a_old
                curr_n_res = np.count_nonzero(curr_cnt == 0)

        elif action_type == 'add': # 40% Neutron Capture
            pool = [m for m in cand_mods if m not in curr_cover]
            if pool:
                # Fast greedy batch-sample to discover heavy stable elements
                cands = random.sample(pool, min(10, len(pool)))

                best_cand, best_a, max_z = None, -1, -1
                weights = (curr_cnt == 0).astype(float)

                for r in cands:
                    counts = np.bincount(targets % r, weights=weights, minlength=r)
                    a = int(np.argmax(counts))
                    if counts[a] > max_z:
                        max_z = counts[a]
                        best_cand, best_a = r, a

                if best_cand is not None:
                    r, a = best_cand, best_a
                    mask_new = ((targets % r) == a).astype(np.int16)
                    curr_cnt += mask_new
                    curr_logm += math.log(r)
                    curr_logboost += math.log(r / (r - 1))
                    curr_n_res = np.count_nonzero(curr_cnt == 0)
                    curr_cover[r] = a

                    new_D = get_D(curr_n_res, curr_logm, curr_logboost)
                    delta = new_D - curr_D

                    if delta <= 0 or random.random() < math.exp(-delta / inner_temp):
                        curr_D = new_D
                    else:
                        curr_cnt -= mask_new
                        curr_logm -= math.log(r)
                        curr_logboost -= math.log(r / (r - 1))
                        del curr_cover[r]
                        curr_n_res = np.count_nonzero(curr_cnt == 0)

        elif action_type == 'drop': # 20% Alpha Decay
            r = random.choice(list(curr_cover.keys()))
            a_old = curr_cover[r]

            mask_old = ((targets % r) == a_old).astype(np.int16)
            curr_cnt -= mask_old
            curr_logm -= math.log(r)
            curr_logboost -= math.log(r / (r - 1))
            del curr_cover[r]
            curr_n_res = np.count_nonzero(curr_cnt == 0)

            new_D = get_D(curr_n_res, curr_logm, curr_logboost)
            delta = new_D - curr_D

            if delta <= 0 or random.random() < math.exp(-delta / inner_temp):
                curr_D = new_D
            else:
                curr_cnt += mask_old
                curr_logm += math.log(r)
                curr_logboost += math.log(r / (r - 1))
                curr_cover[r] = a_old
                curr_n_res = np.count_nonzero(curr_cnt == 0)

        if curr_D < best_D:
            best_D = curr_D
            best_cover = curr_cover.copy()

    # Apply the most stable isotope configuration found during nucleosynthesis simulation
    congr_dict.clear()
    congr_dict.update(best_cover)
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
