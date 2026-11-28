# Copyright 2026 Google LLC
from typing import Any, Mapping
import math
import random
import numpy as np

# EVOLVE-BLOCK-START
def optimize_cover_step(congr_dict, cand_mods, targets, cnt_array, logm, logboost, t_temp):
    """Optimize congruence cover using a powerful local search with Simulated Annealing style logic."""
    import numpy as np
    import random
    import math

    if len(targets) == 0:
        return congr_dict

    # Copy to avoid side effects during search
    cnt_array = cnt_array.copy()
    n_res = int((cnt_array == 0).sum())

    LN10 = math.log(10)

    def calc_D_val(n_res_val, logm_val, logboost_val):
        boost = math.exp(logboost_val)
        m_digits = logm_val / LN10
        ub = n_res_val * boost
        inside_sqrt = m_digits ** 2 + 4 * ub / (LN10 * LN10)
        D = (m_digits + math.sqrt(max(0.0, inside_sqrt))) / 2

        E_actual = ub / (D * LN10) if D > 0 else 0.0
        penalty = 1000.0 * (E_actual - 17.5) ** 2 if E_actual > 17.5 else 0.0
        return D + penalty

    def optimize_subset(keys, congr, cnt):
        for r in keys:
            a_old = congr[r]
            rem = targets % r
            cnt[rem == a_old] -= 1
            counts = np.bincount(rem[cnt == 0], minlength=r)
            a_new = int(np.argmax(counts))
            cnt[rem == a_new] += 1
            congr[r] = a_new

    # Initial residue optimization
    init_keys = list(congr_dict.keys())
    random.shuffle(init_keys)
    optimize_subset(init_keys, congr_dict, cnt_array)
    n_res = int((cnt_array == 0).sum())
    current_D = calc_D_val(n_res, logm, logboost)

    temp = max(t_temp, 1e-6)
    N_STEPS = 100000

    for step in range(N_STEPS):
        # Periodically optimize all to stay on the local optimum manifold
        if step > 0 and step % 10000 == 0:
            keys = list(congr_dict.keys())
            random.shuffle(keys)
            optimize_subset(keys, congr_dict, cnt_array)
            n_res = int((cnt_array == 0).sum())
            current_D = calc_D_val(n_res, logm, logboost)

        action = random.choices(['add', 'drop', 'swap', 'optimize'], weights=[0.25, 0.25, 0.40, 0.10], k=1)[0]

        if action == 'add':
            r = random.choice(cand_mods)
            if r not in congr_dict:
                counts = np.bincount(targets[cnt_array == 0] % r, minlength=r)
                a = int(np.argmax(counts))
                new_n_res = n_res - counts[a]
                new_D = calc_D_val(new_n_res, logm + math.log(r), logboost + math.log(r / (r - 1)))

                if new_D < current_D or random.random() < math.exp(-(new_D - current_D) / temp):
                    congr_dict[r] = a
                    cnt_array[targets % r == a] += 1
                    n_res, current_D = new_n_res, new_D
                    logm += math.log(r)
                    logboost += math.log(r / (r - 1))

        elif action == 'drop':
            active = list(congr_dict.keys())
            if active:
                r = random.choice(active)
                a = congr_dict[r]
                lost_cov = np.sum((targets[cnt_array == 1] % r) == a)
                new_n_res = n_res + lost_cov
                new_D = calc_D_val(new_n_res, logm - math.log(r), logboost - math.log(r / (r - 1)))

                if new_D < current_D or random.random() < math.exp(-(new_D - current_D) / temp):
                    cnt_array[targets % r == a] -= 1
                    del congr_dict[r]
                    n_res, current_D = new_n_res, new_D
                    logm -= math.log(r)
                    logboost -= math.log(r / (r - 1))

        elif action == 'swap':
            active = list(congr_dict.keys())
            if active:
                r_drop = random.choice(active)
                r_add = random.choice(cand_mods)

                if r_add not in congr_dict:
                    a_drop = congr_dict[r_drop]

                    rem_drop = targets % r_drop
                    cnt_array[rem_drop == a_drop] -= 1
                    n_res_after_drop = int((cnt_array == 0).sum())
                    logm_after = logm - math.log(r_drop)
                    logboost_after = logboost - math.log(r_drop / (r_drop - 1))

                    counts = np.bincount(targets[cnt_array == 0] % r_add, minlength=r_add)
                    a_add = int(np.argmax(counts))

                    new_n_res = n_res_after_drop - counts[a_add]
                    new_D = calc_D_val(new_n_res, logm_after + math.log(r_add), logboost_after + math.log(r_add / (r_add - 1)))

                    if new_D < current_D or random.random() < math.exp(-(new_D - current_D) / temp):
                        del congr_dict[r_drop]
                        congr_dict[r_add] = a_add
                        cnt_array[targets % r_add == a_add] += 1
                        n_res, current_D = new_n_res, new_D
                        logm = logm_after + math.log(r_add)
                        logboost = logboost_after + math.log(r_add / (r_add - 1))
                    else:
                        cnt_array[rem_drop == a_drop] += 1

        elif action == 'optimize':
            active = list(congr_dict.keys())
            if active:
                sampled = [random.choice(active)]
                optimize_subset(sampled, congr_dict, cnt_array)
                n_res = int((cnt_array == 0).sum())
                current_D = calc_D_val(n_res, logm, logboost)

    # Final cleanup to ensure absolute optimality of residues
    final_keys = list(congr_dict.keys())
    random.shuffle(final_keys)
    optimize_subset(final_keys, congr_dict, cnt_array)
    return congr_dict
# EVOLVE-BLOCK-END

def evaluate(eval_inputs: Mapping[str, Any]) -> dict[str, float]:
    """Run evaluation on the optimized step."""
    import sympy
    import numpy as np
    Q = 100003
    targets = np.array(list(sympy.primerange(3, Q)), dtype=np.int64)

    # Warm-start from the 195-digit record cover instead of starting empty
    congr_dict = {int(r): int(a) for r, a in eval_inputs["warm_start_cover"]}

    cand_mods = [int(r) for r in sympy.primerange(3, 8000)]
    cnt_array = np.zeros(len(targets), dtype=np.int16)

    # Pre-populate counts
    for r, a in congr_dict.items():
        cnt_array += (targets % r) == a

    for it in range(10):
        t_temp = 0.8 * (0.02 / 0.8) ** (it / 10)
        # Recalculate cnt_array based on congr_dict
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

    # Constrain E <= 17.5 via Lagrangian penalty to prevent reward hacking
    E_limit = 17.5
    E_actual = ub / (D * LN10) if D > 0 else 0.0
    lagrangian_penalty = 0.0
    if E_actual > E_limit:
        lagrangian_penalty = 100.0 * (E_actual - E_limit) ** 2

    score_headline = -float(D + lagrangian_penalty)

    # Expose E, |U|, digits(M) as negated secondary metrics for joint optimization visibility
    return {
        "neg_est_digits": score_headline,
        "neg_E": -float(E_actual),
        "neg_residual_count": -float(n_res),
        "neg_m_digits": -float(m_digits)
    }
