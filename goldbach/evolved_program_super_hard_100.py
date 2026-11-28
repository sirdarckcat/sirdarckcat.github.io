# Copyright 2026 Google LLC
from typing import Any, Mapping
import math
import random
import numpy as np

# EVOLVE-BLOCK-START
def optimize_cover_step(congr_dict, cand_mods, targets, cnt_array, logm, logboost, t_temp):
    """Optimize congruence cover using an intensive internal simulated annealing / local search.

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

    # Precompute / cache logs, weights and targets % r
    if not hasattr(optimize_cover_step, "log_cache"):
        optimize_cover_step.log_cache = {}
    log_cache = optimize_cover_step.log_cache
    if not hasattr(optimize_cover_step, "weight_cache"):
        optimize_cover_step.weight_cache = {}
    weight_cache = optimize_cover_step.weight_cache

    for r in cand_mods:
        if r not in log_cache:
            log_cache[r] = (math.log(r), math.log(r / (r - 1)))
        if r not in weight_cache:
            weight_cache[r] = 1.0 / (r ** 0.8)

    if not hasattr(optimize_cover_step, "mod_cache"):
        optimize_cover_step.mod_cache = {}
    mod_cache = optimize_cover_step.mod_cache

    def get_score(n_res, lm, lb):
        m_dig = lm / 2.302585092994046
        ub = n_res * math.exp(lb)
        return (m_dig + math.sqrt(m_dig * m_dig + 0.7544467881615819 * ub)) / 2

    # Initialize current state variables
    cnt_array = cnt_array.copy()
    n_res = int(np.count_nonzero(cnt_array == 0))
    current_score = get_score(n_res, logm, logboost)

    # Run an intensive internal search of 150 steps
    num_inner_steps = 150
    temp = max(t_temp, 1e-4)

    for step in range(num_inner_steps):
        proposals = []
        # Always include the option to stay
        proposals.append((current_score, 'stay', None, n_res))

        # 1. ADD MOVES
        cand_pool = [m for m in cand_mods if m not in congr_dict]
        sampled_adds = []
        if cand_pool:
            # Weighted random sampling without replacement using Gumbel-Max
            pool_keys = [(random.random() ** (1.0 / weight_cache[m]), m) for m in cand_pool]
            pool_keys.sort(reverse=True)
            sampled_adds = [m for _, m in pool_keys[:min(40, len(pool_keys))]]

            uncovered_mask = (cnt_array == 0)
            n_uncovered = n_res

            for r in sampled_adds:
                cache_key = (id(targets), r)
                t_mod = mod_cache.get(cache_key)
                if t_mod is None:
                    t_mod = targets % r
                    mod_cache[cache_key] = t_mod

                if n_uncovered > 0:
                    sub_arr = t_mod[uncovered_mask]
                    counts = np.bincount(sub_arr, minlength=r)
                    best_a = int(np.argmax(counts))
                    max_covered = counts[best_a]
                else:
                    best_a = 0
                    max_covered = 0

                n_res_new = n_res - max_covered
                lm_new = logm + log_cache[r][0]
                lb_new = logboost + log_cache[r][1]
                score_new = get_score(n_res_new, lm_new, lb_new)
                proposals.append((score_new, 'add', (r, best_a), n_res_new))

        # 2. DROP MOVES
        if congr_dict:
            # Evaluate dropping each active modulus
            for r, a in congr_dict.items():
                cache_key = (id(targets), r)
                t_mod = mod_cache.get(cache_key)
                if t_mod is None:
                    t_mod = targets % r
                    mod_cache[cache_key] = t_mod

                num_newly_uncovered = int(np.count_nonzero((t_mod == a) & (cnt_array == 1)))
                n_res_new = n_res + num_newly_uncovered
                lm_new = logm - log_cache[r][0]
                lb_new = logboost - log_cache[r][1]
                score_new = get_score(n_res_new, lm_new, lb_new)
                proposals.append((score_new, 'drop', (r, a), n_res_new))

        # 3. SWAP MOVES (OPTIMIZE CONGRUENCE)
        if congr_dict:
            # Evaluate optimizing congruence for some active moduli
            sampled_swaps = list(congr_dict.keys())
            if len(sampled_swaps) > 40:
                sampled_swaps = random.sample(sampled_swaps, 40)

            for r in sampled_swaps:
                a_old = congr_dict[r]
                cache_key = (id(targets), r)
                t_mod = mod_cache.get(cache_key)
                if t_mod is None:
                    t_mod = targets % r
                    mod_cache[cache_key] = t_mod

                is_covered = (t_mod == a_old)
                cnt_bg = cnt_array - is_covered
                uncovered_mask_bg = (cnt_bg == 0)
                n_uncovered_bg = int(np.count_nonzero(uncovered_mask_bg))

                if n_uncovered_bg > 0:
                    sub_arr = t_mod[uncovered_mask_bg]
                    counts = np.bincount(sub_arr, minlength=r)
                    best_a = int(np.argmax(counts))
                    max_covered = counts[best_a]
                else:
                    best_a = 0
                    max_covered = 0

                if best_a != a_old:
                    n_res_new = n_uncovered_bg - max_covered
                    score_new = get_score(n_res_new, logm, logboost)
                    proposals.append((score_new, 'swap', (r, best_a), n_res_new))

        # 4. REPLACE MOVES (DROP ONE, ADD ONE)
        if congr_dict and len(sampled_adds) > 0:
            active_list = list(congr_dict.keys())
            # Biased drop: prefer replacing larger moduli
            drop_keys = [(random.random() ** (1.0 / r), r) for r in active_list]
            drop_keys.sort(reverse=True)
            sampled_drops = [r for _, r in drop_keys[:min(10, len(drop_keys))]]

            for r_old in sampled_drops:
                a_old = congr_dict[r_old]
                cache_key_old = (id(targets), r_old)
                t_mod_old = mod_cache.get(cache_key_old)
                if t_mod_old is None:
                    t_mod_old = targets % r_old
                    mod_cache[cache_key_old] = t_mod_old

                sampled_news = [m for m in sampled_adds[:5] if m != r_old]

                is_covered_old = (t_mod_old == a_old)
                cnt_bg = cnt_array - is_covered_old
                uncovered_mask_bg = (cnt_bg == 0)
                n_uncovered_bg = int(np.count_nonzero(uncovered_mask_bg))

                for r_new in sampled_news:
                    cache_key_new = (id(targets), r_new)
                    t_mod_new = mod_cache.get(cache_key_new)
                    if t_mod_new is None:
                        t_mod_new = targets % r_new
                        mod_cache[cache_key_new] = t_mod_new

                    if n_uncovered_bg > 0:
                        sub_arr = t_mod_new[uncovered_mask_bg]
                        counts = np.bincount(sub_arr, minlength=r_new)
                        best_a = int(np.argmax(counts))
                        max_covered = counts[best_a]
                    else:
                        best_a = 0
                        max_covered = 0

                    n_res_new = n_uncovered_bg - max_covered
                    lm_new = logm - log_cache[r_old][0] + log_cache[r_new][0]
                    lb_new = logboost - log_cache[r_old][1] + log_cache[r_new][1]
                    score_new = get_score(n_res_new, lm_new, lb_new)
                    proposals.append((score_new, 'replace', (r_old, a_old, r_new, best_a), n_res_new))

        # Choose a proposal using Boltzmann distribution
        scores = np.array([p[0] for p in proposals])

        # Softmax selection (minimizing score)
        logits = -scores / temp
        logits = logits - np.max(logits)  # Numerically stable
        probs = np.exp(logits)
        probs = probs / np.sum(probs)

        cum_probs = np.cumsum(probs)
        chosen_idx = np.searchsorted(cum_probs, random.random())
        chosen_idx = min(chosen_idx, len(proposals) - 1)

        chosen_score, move_type, move_args, n_res_new = proposals[chosen_idx]

        # Apply the chosen move
        if move_type == 'add':
            r, a = move_args
            congr_dict[r] = a
            cache_key = (id(targets), r)
            t_mod = mod_cache[cache_key]
            cnt_array += (t_mod == a)
            logm += log_cache[r][0]
            logboost += log_cache[r][1]
            n_res = n_res_new
            current_score = chosen_score
        elif move_type == 'drop':
            r, a = move_args
            del congr_dict[r]
            cache_key = (id(targets), r)
            t_mod = mod_cache[cache_key]
            cnt_array -= (t_mod == a)
            logm -= log_cache[r][0]
            logboost -= log_cache[r][1]
            n_res = n_res_new
            current_score = chosen_score
        elif move_type == 'swap':
            r, a = move_args
            a_old = congr_dict[r]
            cache_key = (id(targets), r)
            t_mod = mod_cache[cache_key]
            cnt_array -= (t_mod == a_old)
            cnt_array += (t_mod == a)
            congr_dict[r] = a
            n_res = n_res_new
            current_score = chosen_score
        elif move_type == 'replace':
            r_old, a_old, r_new, a_new = move_args
            # Remove old
            del congr_dict[r_old]
            cache_key_old = (id(targets), r_old)
            t_mod_old = mod_cache[cache_key_old]
            cnt_array -= (t_mod_old == a_old)
            # Add new
            congr_dict[r_new] = a_new
            cache_key_new = (id(targets), r_new)
            t_mod_new = mod_cache[cache_key_new]
            cnt_array += (t_mod_new == a_new)

            logm += log_cache[r_new][0] - log_cache[r_old][0]
            logboost += log_cache[r_new][1] - log_cache[r_old][1]
            n_res = n_res_new
            current_score = chosen_score

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
