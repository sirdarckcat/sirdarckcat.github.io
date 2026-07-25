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

    # Dynamic action probabilities based on temperature
    factor = np.clip(t_temp, 0.0, 1.0)
    # Slightly favor optimization and drop at low temperatures
    p_opt = 0.85 - 0.40 * factor
    p_add = 0.10 + 0.30 * factor
    p_drop = 0.05 + 0.10 * factor
    total_p = p_opt + p_add + p_drop
    p_opt /= total_p
    p_add /= total_p
    p_drop /= total_p

    kind = random.random()
    cand_pool = [m for m in cand_mods if m not in congr_dict]
    mods_in = list(congr_dict.keys())

    if not congr_dict:
        action = 'add'
    elif not cand_pool:
        p_opt_cond = p_opt / (p_opt + p_drop)
        action = 'optimize' if kind < p_opt_cond else 'drop'
    else:
        if kind < p_add:
            action = 'add'
        elif kind < p_add + p_opt:
            action = 'optimize'
        else:
            action = 'drop'

    # Objective function parameters for exact evaluation
    LN10 = 2.302585092994046
    alpha = 0.6  # Weight for secondary redundancy objective
    decay = 1.2  # Decay rate for redundancy penalty

    current_n_uncov = int(np.sum(cnt_array == 0))
    current_sum_pen = float(np.sum(np.exp(-decay * cnt_array)))
    pen_reduction_factor = 1.0 - np.exp(-decay)

    energies = []
    cands_data = []

    if action == 'add' and cand_pool:
        sample_size = min(200, len(cand_pool))
        sampled_cands = random.sample(cand_pool, sample_size)

        mask0 = (cnt_array == 0).astype(float)
        w_pen = np.exp(-decay * cnt_array)

        for r in sampled_cands:
            rem = targets % r
            c0_all = np.bincount(rem, weights=mask0, minlength=r)
            cw_all = np.bincount(rem, weights=w_pen, minlength=r)

            n_uncov_new = current_n_uncov - c0_all
            sum_pen_new = current_sum_pen - cw_all * pen_reduction_factor

            lm_new = logm + np.log(r)
            lb_new = logboost + np.log(r / (r - 1))

            md = lm_new / LN10
            ub = n_uncov_new * np.exp(lb_new)
            # True resulting D metric for all sub-residues
            D = (md + np.sqrt(md**2 + 4 * ub / (LN10**2))) / 2.0
            E_new = D + alpha * sum_pen_new

            top_k = min(2, r)
            if top_k < r:
                best_as = np.argpartition(E_new, top_k - 1)[:top_k]
            else:
                best_as = np.arange(r)

            for a in best_as:
                energies.append(E_new[a])
                cands_data.append((r, a))

        if energies:
            energies = np.array(energies)
            temp = max(t_temp, 1e-4) * 0.5
            scaled_E = -energies / temp
            scaled_E = scaled_E - np.max(scaled_E)
            probs = np.exp(scaled_E)
            probs /= np.sum(probs)

            idx = np.random.choice(len(energies), p=probs)
            best_cand, best_a = cands_data[idx]
            congr_dict[best_cand] = int(best_a)

    elif action == 'optimize' and mods_in:
        sample_size = min(40, len(mods_in))
        sampled_mods = random.sample(mods_in, sample_size)

        for r in sampled_mods:
            a_old = congr_dict[r]
            is_covered_by_r = (targets % r) == a_old
            cnt_bg = cnt_array - is_covered_by_r

            mask0_bg = (cnt_bg == 0).astype(float)
            w_pen_bg = np.exp(-decay * cnt_bg)

            rem = targets % r
            c0_all = np.bincount(rem, weights=mask0_bg, minlength=r)
            cw_all = np.bincount(rem, weights=w_pen_bg, minlength=r)

            n_uncov_bg = np.sum(mask0_bg)
            sum_pen_bg = np.sum(w_pen_bg)

            n_uncov_new = n_uncov_bg - c0_all
            sum_pen_new = sum_pen_bg - cw_all * pen_reduction_factor

            md = logm / LN10
            ub = n_uncov_new * np.exp(logboost)
            D = (md + np.sqrt(md**2 + 4 * ub / (LN10**2))) / 2.0
            E_new = D + alpha * sum_pen_new

            top_k = min(3, r)
            if top_k < r:
                best_as = np.argpartition(E_new, top_k - 1)[:top_k]
            else:
                best_as = np.arange(r)

            for a in best_as:
                energies.append(E_new[a])
                cands_data.append((r, a))

        if energies:
            energies = np.array(energies)
            temp = max(t_temp, 1e-4) * 0.5
            scaled_E = -energies / temp
            scaled_E = scaled_E - np.max(scaled_E)
            probs = np.exp(scaled_E)
            probs /= np.sum(probs)

            idx = np.random.choice(len(energies), p=probs)
            best_r, best_a = cands_data[idx]
            congr_dict[best_r] = int(best_a)

    elif action == 'drop' and mods_in:
        for r in mods_in:
            a_old = congr_dict[r]
            is_covered_by_r = (targets % r) == a_old

            c0_diff = np.sum((cnt_array == 1) & is_covered_by_r)
            n_uncov_new = current_n_uncov + c0_diff

            w_diff = np.sum(np.exp(-decay * cnt_array[is_covered_by_r])) * (np.exp(decay) - 1.0)
            sum_pen_new = current_sum_pen + w_diff

            lm_new = logm - np.log(r)
            lb_new = logboost - np.log(r / (r - 1))

            md = lm_new / LN10
            ub = n_uncov_new * np.exp(lb_new)
            D = (md + np.sqrt(md**2 + 4 * ub / (LN10**2))) / 2.0
            E_new = D + alpha * sum_pen_new

            energies.append(E_new)
            cands_data.append(r)

        if energies:
            energies = np.array(energies)
            temp = max(t_temp, 1e-4) * 0.5
            scaled_E = -energies / temp
            scaled_E = scaled_E - np.max(scaled_E)
            probs = np.exp(scaled_E)
            probs /= np.sum(probs)

            idx = np.random.choice(len(energies), p=probs)
            r_drop = cands_data[idx]
            del congr_dict[r_drop]

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
