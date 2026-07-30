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
    # At high temp, we explore (more add/drop). At low temp, we exploit (more optimize).
    factor = np.clip(t_temp, 0.0, 1.0)
    p_opt = 0.85 - 0.45 * factor
    p_add = 0.10 + 0.25 * factor
    p_drop = 0.05 + 0.20 * factor
    total_p = p_opt + p_add + p_drop
    p_opt /= total_p
    p_add /= total_p
    p_drop /= total_p

    kind = random.random()
    if not congr_dict:
        action = 'add'
    else:
        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if not cand_pool:
            p_opt_cond = p_opt / (p_opt + p_drop)
            action = 'optimize' if kind < p_opt_cond else 'drop'
        else:
            if kind < p_add:
                action = 'add'
            elif kind < p_add + p_opt:
                action = 'optimize'
            else:
                action = 'drop'

    import math

    def eval_D(n_uncovered, cur_logm, cur_logboost):
        ub = max(0, n_uncovered) * math.exp(cur_logboost)
        LN10 = 2.302585092994046
        m_dig = cur_logm / LN10
        return (m_dig + math.sqrt(m_dig**2 + 4 * ub / (LN10**2))) / 2

    current_n_res = int((cnt_array == 0).sum())
    current_D = eval_D(current_n_res, logm, logboost)
    temp = max(t_temp, 1e-4)

    if action == 'add':
        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if cand_pool:
            # Quantum-inspired multi-verse evaluation: directly compute the exact
            # topological deformation of the D-loss landscape for a massive sample!
            sample_size = min(128, len(cand_pool))
            sampled_cands = random.sample(cand_pool, sample_size)

            uncovered_mask = (cnt_array == 0)

            delta_Ds = []
            cands_data = []
            for r in sampled_cands:
                rem = targets % r
                # We only care about how many currently uncovered targets we can cover
                counts = np.bincount(rem[uncovered_mask], minlength=r)
                a = int(np.argmax(counts))
                max_cov = counts[a]

                new_n_res = current_n_res - max_cov
                new_logm = logm + math.log(r)
                new_logboost = logboost + math.log(r / (r - 1))
                new_D = eval_D(new_n_res, new_logm, new_logboost)

                delta_Ds.append(new_D - current_D)
                cands_data.append((r, a))

            # Gibbs-Boltzmann selection over the exact objective gradients
            scaled_scores = -np.array(delta_Ds) / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(sampled_cands), p=probs)
            best_cand, best_a = cands_data[idx]
            congr_dict[best_cand] = int(best_a)

    elif action == 'optimize':
        mods_in = list(congr_dict.keys())
        if mods_in:
            # Optimize a highly connected modulus by evaluating the exact D-loss
            # across all its parallel residue dimensions
            r = random.choice(mods_in)
            a_old = congr_dict[r]

            is_covered_by_r = (targets % r) == a_old
            cnt_bg = cnt_array - is_covered_by_r
            bg_uncovered_mask = (cnt_bg == 0)
            total_bg_uncovered = bg_uncovered_mask.sum()

            counts = np.bincount(targets[bg_uncovered_mask] % r, minlength=r)

            delta_Ds = []
            for a_new in range(r):
                new_n_res = total_bg_uncovered - counts[a_new]
                # logm and logboost remain identical during optimization
                new_D = eval_D(new_n_res, logm, logboost)
                delta_Ds.append(new_D - current_D)

            scaled_scores = -np.array(delta_Ds) / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            a_new = np.random.choice(r, p=probs)
            congr_dict[r] = int(a_new)

    elif action == 'drop':
        mods_in = list(congr_dict.keys())
        if mods_in:
            # Extinction event probability guided by inverse thermodynamic loss contribution
            delta_Ds = []
            for r in mods_in:
                a = congr_dict[r]
                # Targets covered ONLY by this modulus will become uncovered
                mask = ((targets % r) == a) & (cnt_array == 1)
                lost_cov = mask.sum()

                new_n_res = current_n_res + lost_cov
                new_logm = logm - math.log(r)
                new_logboost = logboost - math.log(r / (r - 1))
                new_D = eval_D(new_n_res, new_logm, new_logboost)
                delta_Ds.append(new_D - current_D)

            scaled_scores = -np.array(delta_Ds) / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(mods_in), p=probs)
            r_drop = mods_in[idx]
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
