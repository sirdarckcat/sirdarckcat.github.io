"""Door 1, D1.1 basin probe: start from a random-ascent solution
(~960) and apply exact LNS windows. Does it descend to greedy quality
(867), beat it, or stall? Evidence on whether the greedy basin is
special. Does NOT touch d11_best.json.
"""
import sys

import numpy as np

import d11_lns as d


def ascent_from_random(seed):
    rng = np.random.default_rng(seed)
    assign = {r: int(rng.integers(1, r)) for r in d.moduli}
    cc = np.zeros(len(d.P), dtype=np.int16)
    for r in d.moduli:
        cc += (d.RES[r] == assign[r])
    improved = True
    while improved:
        improved = False
        order = list(d.moduli)
        rng.shuffle(order)
        for r in order:
            m = d.RES[r] == assign[r]
            cc -= m
            hist = np.bincount(d.RES[r][cc == 0], minlength=r)
            a = int(hist.argmax())
            if hist[a] > hist[assign[r]]:
                assign[r] = a
                improved = True
            cc += (d.RES[r] == assign[r])
    return assign, cc


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    nwin = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    cap = float(sys.argv[3]) if len(sys.argv) > 3 else 22.0
    rng = np.random.default_rng(seed + 1)
    assign, cc = ascent_from_random(seed)
    u = int((cc == 0).sum())
    traj = [u]
    print(f"basin probe: random-ascent start |U|={u}", flush=True)
    tight = d.stability_order(assign, cc)
    for w in range(nwin):
        if w % 2 == 0:
            W = tight[(w // 2) * 8 % 60:(w // 2) * 8 % 60 + 8]
        else:
            W = [int(r) for r in rng.choice(d.moduli, size=8, replace=False)]
        na, _, _ = d.solve_window(assign, W, cap)
        u2, cc2 = d.ucount(na)
        if u2 < u:
            assign, u, cc = na, u2, cc2
            tight = d.stability_order(assign, cc)
        traj.append(u)
    print(f"trajectory: {traj}", flush=True)
    print(f"final |U|={u} (greedy basin: 867; start was {traj[0]}; "
          f"recovered {traj[0]-u} of the {traj[0]-867} gap)", flush=True)


if __name__ == '__main__':
    main()
