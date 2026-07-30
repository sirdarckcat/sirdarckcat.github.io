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

    if action == 'add':
        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if cand_pool:
            # Scale up sample size for a more comprehensive selection
            sample_size = min(64, len(cand_pool))
            sampled_cands = random.sample(cand_pool, sample_size)

            n_res = int(np.sum(cnt_array == 0))
            zeros_mask = (cnt_array == 0)
            targets_zeros = targets[zeros_mask] if n_res > 0 else np.array([])
            LN10 = math.log(10)

            scores = []
            cands_data = []
            for r in sampled_cands:
                if n_res > 0:
                    counts = np.bincount(targets_zeros % r, minlength=r)
                    a = int(np.argmax(counts))
                    c = counts[a]
                else:
                    a = random.randint(0, r - 1)
                    c = 0

                new_n_res = n_res - c
                new_boost = math.exp(logboost + math.log(r / (r - 1)))
                new_m_digits = (logm + math.log(r)) / LN10
                new_ub = new_n_res * new_boost

                new_D = (new_m_digits + math.sqrt(new_m_digits**2 + 4 * new_ub / (LN10**2))) / 2
                # Maximize score (minimize D)
                scores.append(-new_D)
                cands_data.append((r, a))

            scores = np.array(scores)
            ptp = np.ptp(scores)
            if ptp > 0:
                norm_scores = (scores - np.min(scores)) / ptp
            else:
                norm_scores = np.zeros_like(scores, dtype=float)

            temp = max(t_temp, 1e-4)
            scaled_scores = norm_scores / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(sampled_cands), p=probs)
            best_cand, best_a = cands_data[idx]
            congr_dict[best_cand] = int(best_a)

    elif action == 'optimize':
        mods_in = list(congr_dict.keys())
        if mods_in:
            r = random.choice(mods_in)
            a_old = congr_dict[r]

            # Subtract the contribution of the active modulus to obtain background coverage
            is_covered_by_r = (targets % r) == a_old
            cnt_bg = cnt_array - is_covered_by_r

            # Primary: cover completely uncovered targets. Secondary: cover targets covered only once.
            weights_opt = np.where(cnt_bg == 0, 1.0, np.where(cnt_bg == 1, 0.05, 1e-4))

            counts = np.bincount(targets % r, weights=weights_opt, minlength=r)

            ptp = np.ptp(counts)
            if ptp > 0:
                norm_counts = (counts - np.min(counts)) / ptp
            else:
                norm_counts = np.zeros_like(counts, dtype=float)

            temp = max(t_temp, 1e-4)
            scaled_counts = norm_counts / temp
            scaled_counts = scaled_counts - np.max(scaled_counts)
            probs = np.exp(scaled_counts)
            probs /= np.sum(probs)

            a_new = np.random.choice(r, p=probs)
            congr_dict[r] = int(a_new)

    elif action == 'drop':
        mods_in = list(congr_dict.keys())
        if mods_in:
            n_res = int(np.sum(cnt_array == 0))
            LN10 = math.log(10)
            ones_mask = (cnt_array == 1)
            targets_ones = targets[ones_mask] if np.any(ones_mask) else np.array([])

            sample_size = min(64, len(mods_in))
            sampled_mods = random.sample(mods_in, sample_size)

            scores = []
            for r in sampled_mods:
                a = congr_dict[r]
                if len(targets_ones) > 0:
                    c_lost = int(np.sum((targets_ones % r) == a))
                else:
                    c_lost = 0

                new_n_res = n_res + c_lost
                new_boost = math.exp(logboost - math.log(r / (r - 1)))
                new_m_digits = (logm - math.log(r)) / LN10
                new_ub = new_n_res * new_boost

                new_D = (new_m_digits + math.sqrt(new_m_digits**2 + 4 * new_ub / (LN10**2))) / 2
                # Maximize score (minimize D)
                scores.append(-new_D)

            scores = np.array(scores)
            ptp = np.ptp(scores)
            if ptp > 0:
                norm_scores = (scores - np.min(scores)) / ptp
            else:
                norm_scores = np.zeros_like(scores, dtype=float)

            temp = max(t_temp, 1e-4)
            scaled_scores = norm_scores / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(sampled_mods), p=probs)
            r_drop = sampled_mods[idx]
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
