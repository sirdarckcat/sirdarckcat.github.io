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

    # Dynamic action probabilities based on the number of elements
    n_mods = len(congr_dict)
    factor = np.clip(t_temp, 0.0, 1.0)

    if n_mods < 3:
        p_add = 1.0
        p_opt = 0.0
        p_drop = 0.0
        p_swap = 0.0
    elif n_mods < 6:
        p_add = 0.60 - 0.20 * factor
        p_opt = 0.15 + 0.10 * factor
        p_drop = 0.05
        p_swap = 0.20 + 0.10 * factor
    else:
        p_add = 0.10
        p_opt = 0.40 - 0.10 * factor
        p_drop = 0.15 + 0.10 * factor
        p_swap = 0.35 + 0.10 * factor

    kind = random.random()
    if not congr_dict:
        action = 'add'
    else:
        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if not cand_pool:
            total_p = p_opt + p_drop
            p_opt_norm = p_opt / total_p
            action = 'optimize' if kind < p_opt_norm else 'drop'
        else:
            total_p = p_add + p_opt + p_drop + p_swap
            p_add_norm = p_add / total_p
            p_opt_norm = p_opt / total_p
            p_drop_norm = p_drop / total_p
            if kind < p_add_norm:
                action = 'add'
            elif kind < p_add_norm + p_opt_norm:
                action = 'optimize'
            elif kind < p_add_norm + p_opt_norm + p_drop_norm:
                action = 'drop'
            else:
                action = 'swap'

    LN10 = 2.302585092994046

    if action == 'add':
        cand_pool = [m for m in cand_mods if m not in congr_dict]
        if cand_pool:
            uncovered_targets = targets[cnt_array == 0]
            n_res = len(uncovered_targets)

            D_news = []
            cands_data = []

            for r in cand_pool:
                rem = uncovered_targets % r
                counts = np.bincount(rem, minlength=r)
                a = int(np.argmax(counts))
                k = counts[a]

                n_res_new = n_res - k
                logm_new = logm + math.log(r)
                logboost_new = logboost + math.log(r / (r - 1))

                m_digits_new = logm_new / LN10
                ub_new = n_res_new * math.exp(logboost_new)
                val = m_digits_new**2 + 4 * ub_new / (LN10 * LN10)
                D_new = (m_digits_new + math.sqrt(max(val, 0.0))) / 2

                D_news.append(D_new)
                cands_data.append((r, a))

            D_news = np.array(D_news)
            temp = max(t_temp * 0.1, 1e-5)
            scaled_scores = -D_news / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(cand_pool), p=probs)
            best_cand, best_a = cands_data[idx]
            congr_dict[best_cand] = int(best_a)

    elif action == 'optimize':
        mods_in = list(congr_dict.keys())
        if mods_in:
            all_choices = []
            all_D_news = []

            for r in mods_in:
                a_old = congr_dict[r]
                is_covered_by_r = (targets % r) == a_old
                cnt_bg = cnt_array - is_covered_by_r

                uncovered_bg = targets[cnt_bg == 0]
                n_res_bg = len(uncovered_bg)

                counts = np.bincount(uncovered_bg % r, minlength=r)

                n_res_news = n_res_bg - counts
                m_digits_new = logm / LN10
                ub_news = n_res_news * math.exp(logboost)
                val = m_digits_new**2 + 4 * ub_news / (LN10 * LN10)
                D_news = (m_digits_new + np.sqrt(np.clip(val, 0.0, None))) / 2

                # Get the top 5 best a's (or fewer if r < 5)
                top_k = min(5, r)
                best_indices = np.argpartition(-counts, top_k - 1)[:top_k]

                for a in best_indices:
                    all_choices.append((r, a))
                    all_D_news.append(D_news[a])

            all_D_news = np.array(all_D_news)
            temp = max(t_temp * 0.1, 1e-5)
            scaled_scores = -all_D_news / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(all_choices), p=probs)
            r_opt, a_opt = all_choices[idx]
            congr_dict[r_opt] = int(a_opt)

    elif action == 'drop':
        mods_in = list(congr_dict.keys())
        if mods_in:
            D_news = []

            for r in mods_in:
                a = congr_dict[r]
                is_covered_by_r = (targets % r) == a
                cnt_bg = cnt_array - is_covered_by_r
                n_res_new = np.sum(cnt_bg == 0)

                logm_new = logm - math.log(r)
                logboost_new = logboost - math.log(r / (r - 1))

                m_digits_new = logm_new / LN10
                ub_new = n_res_new * math.exp(logboost_new)
                val = m_digits_new**2 + 4 * ub_new / (LN10 * LN10)
                D_new = (m_digits_new + math.sqrt(max(val, 0.0))) / 2
                D_news.append(D_new)

            D_news = np.array(D_news)
            temp = max(t_temp * 0.1, 1e-5)
            scaled_scores = -D_news / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx = np.random.choice(len(mods_in), p=probs)
            r_drop = mods_in[idx]
            del congr_dict[r_drop]

    elif action == 'swap':
        mods_in = list(congr_dict.keys())
        if mods_in:
            D_drops = []
            for r in mods_in:
                a = congr_dict[r]
                is_covered_by_r = (targets % r) == a
                cnt_bg = cnt_array - is_covered_by_r
                n_res_new = np.sum(cnt_bg == 0)

                logm_new = logm - math.log(r)
                logboost_new = logboost - math.log(r / (r - 1))

                m_digits_new = logm_new / LN10
                ub_new = n_res_new * math.exp(logboost_new)
                val = m_digits_new**2 + 4 * ub_new / (LN10 * LN10)
                D_new = (m_digits_new + math.sqrt(max(val, 0.0))) / 2
                D_drops.append(D_new)

            D_drops = np.array(D_drops)
            temp = max(t_temp * 0.1, 1e-5)
            scaled_scores = -D_drops / temp
            scaled_scores = scaled_scores - np.max(scaled_scores)
            probs = np.exp(scaled_scores)
            probs /= np.sum(probs)

            idx_drop = np.random.choice(len(mods_in), p=probs)
            r_old = mods_in[idx_drop]

            a_old = congr_dict[r_old]
            del congr_dict[r_old]

            is_covered_by_r_old = (targets % r_old) == a_old
            cnt_bg = cnt_array - is_covered_by_r_old
            logm_bg = logm - math.log(r_old)
            logboost_bg = logboost - math.log(r_old / (r_old - 1))

            cand_pool = [m for m in cand_mods if m not in congr_dict and m != r_old]
            if cand_pool:
                uncovered_targets = targets[cnt_bg == 0]
                n_res = len(uncovered_targets)

                D_news = []
                cands_data = []

                for r in cand_pool:
                    rem = uncovered_targets % r
                    counts = np.bincount(rem, minlength=r)
                    a = int(np.argmax(counts))
                    k = counts[a]

                    n_res_new = n_res - k
                    logm_new = logm_bg + math.log(r)
                    logboost_new = logboost_bg + math.log(r / (r - 1))

                    m_digits_new = logm_new / LN10
                    ub_new = n_res_new * math.exp(logboost_new)
                    val = m_digits_new**2 + 4 * ub_new / (LN10 * LN10)
                    D_new = (m_digits_new + math.sqrt(max(val, 0.0))) / 2

                    D_news.append(D_new)
                    cands_data.append((r, a))

                D_news = np.array(D_news)
                scaled_scores = -D_news / temp
                scaled_scores = scaled_scores - np.max(scaled_scores)
                probs = np.exp(scaled_scores)
                probs /= np.sum(probs)

                idx = np.random.choice(len(cand_pool), p=probs)
                best_cand, best_a = cands_data[idx]
                congr_dict[best_cand] = int(best_a)
            else:
                congr_dict[r_old] = a_old

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
