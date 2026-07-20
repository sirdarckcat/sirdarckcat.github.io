"""Simulated-annealing refinement of congruence covers.

Objective (natural log units):  F = log(M) + E  (+ hard cap E <= e_cap),
since for a fixed success probability the expected decimal size of the
found N is digits(M) + E/ln10 + const.  E is the expected number of
prime residual complements per progression element:
    E = |U| * boost / ln(N),  boost = 2 * prod r/(r-1).

Moves: change a residue, drop a modulus, add a modulus, or swap.
State is kept incrementally: cnt[i] = how many congruences cover target i.
"""

import json
import math
import random
import sys

import numpy as np
from sympy import primerange

import cover as C

LN10 = math.log(10)


class State:
    def __init__(self, Q, chosen, rmax=8000, e_cap=17.5, ln_n=None):
        self.Q = Q
        self.targets = np.array(list(primerange(3, Q)), dtype=np.int64)
        self.cand = [int(r) for r in primerange(3, rmax)]
        self.mods = {}          # r -> targets % r  (lazy)
        self.chosen = dict(chosen)
        self.e_cap = e_cap
        self.cnt = np.zeros(len(self.targets), dtype=np.int16)
        self.logm = math.log(2)
        self.logboost = math.log(2.0)
        for r, a in self.chosen.items():
            self.cnt += self.tmod(r) == a
            self.logm += math.log(r)
            self.logboost += math.log(r / (r - 1))
        self.ln_n = ln_n

    def tmod(self, r):
        if r not in self.mods:
            self.mods[r] = self.targets % r
        return self.mods[r]

    def energy(self, logm=None, n_res=None, logboost=None):
        logm = self.logm if logm is None else logm
        n_res = int((self.cnt == 0).sum()) if n_res is None else n_res
        logboost = self.logboost if logboost is None else logboost
        boost = math.exp(logboost)
        if self.ln_n:
            E = n_res * boost / self.ln_n
            D = logm / LN10 + E / LN10
        else:
            D, E = C.self_consistent_D(logm / LN10, n_res, boost)
        pen = 0.0 if E <= self.e_cap else 200.0 * (E - self.e_cap) ** 2
        return logm + E + pen, D, E

    def n_res(self):
        return int((self.cnt == 0).sum())

    # ---- move helpers ----
    def delta_change_residue(self, r, a_new):
        a_old = self.chosen[r]
        m = self.tmod(r)
        oldmask = m == a_old
        newmask = m == a_new
        # residuals after: covered only by r -> exposed; newly covered by r
        n_res_new = self.n_res() + int(((self.cnt == 1) & oldmask).sum()) \
            - int(((self.cnt == 0) & newmask).sum())
        return self.energy(n_res=n_res_new)

    def apply_change(self, r, a_new):
        m = self.tmod(r)
        self.cnt -= (m == self.chosen[r]).astype(np.int16)
        self.cnt += (m == a_new).astype(np.int16)
        self.chosen[r] = a_new

    def delta_drop(self, r):
        m = self.tmod(r)
        n_res_new = self.n_res() + int(((self.cnt == 1) & (m == self.chosen[r])).sum())
        return self.energy(logm=self.logm - math.log(r), n_res=n_res_new,
                           logboost=self.logboost - math.log(r / (r - 1)))

    def apply_drop(self, r):
        m = self.tmod(r)
        self.cnt -= (m == self.chosen[r]).astype(np.int16)
        self.logm -= math.log(r)
        self.logboost -= math.log(r / (r - 1))
        del self.chosen[r]

    def best_residues(self, r, topj=4):
        alive = self.targets[self.cnt == 0]
        if len(alive) == 0:
            return [(0, 0)]
        cnts = np.bincount(alive % r, minlength=r)
        order = np.argsort(cnts)[::-1][:topj]
        return [(int(a), int(cnts[a])) for a in order if cnts[a] > 0]

    def delta_add(self, r, a):
        m = self.tmod(r)
        n_res_new = self.n_res() - int(((self.cnt == 0) & (m == a)).sum())
        return self.energy(logm=self.logm + math.log(r), n_res=n_res_new,
                           logboost=self.logboost + math.log(r / (r - 1)))

    def apply_add(self, r, a):
        self.cnt += (self.tmod(r) == a).astype(np.int16)
        self.logm += math.log(r)
        self.logboost += math.log(r / (r - 1))
        self.chosen[r] = a


def anneal(state, iters=60000, t0=0.8, t1=0.02, seed=0, verbose=True):
    rng = random.Random(seed)
    f_cur, D, E = state.energy()
    best = (f_cur, dict(state.chosen))
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        kind = rng.random()
        r_in = rng.choice(list(state.chosen)) if state.chosen else None
        try_moves = []
        if kind < 0.5 and r_in is not None:
            for a, _ in state.best_residues(r_in, topj=3):
                if a != state.chosen[r_in]:
                    try_moves.append(("chg", r_in, a))
        elif kind < 0.7 and r_in is not None:
            try_moves.append(("drop", r_in, None))
        else:
            r_out = rng.choice(state.cand)
            if r_out not in state.chosen:
                br = state.best_residues(r_out, topj=2)
                if br and br[0][1] > 0:
                    try_moves.append(("add", r_out, br[0][0]))
        for op, r, a in try_moves:
            if op == "chg":
                f_new, _, _ = state.delta_change_residue(r, a)
            elif op == "drop":
                f_new, _, _ = state.delta_drop(r)
            else:
                f_new, _, _ = state.delta_add(r, a)
            if f_new < f_cur or rng.random() < math.exp((f_cur - f_new) / max(T, 1e-9)):
                if op == "chg":
                    state.apply_change(r, a)
                elif op == "drop":
                    state.apply_drop(r)
                else:
                    state.apply_add(r, a)
                f_cur = f_new
                if f_cur < best[0]:
                    best = (f_cur, dict(state.chosen))
                break
        if verbose and it % 10000 == 0:
            _, D, E = state.energy()
            print(f"  it={it:6d} T={T:.3f} F={f_cur:8.2f} congr={len(state.chosen):4d} "
                  f"M={state.logm/LN10:6.1f}d |U|={state.n_res():4d} E={E:5.2f} D~{D:6.1f}",
                  flush=True)
    # restore best
    state2 = State(state.Q, best[1], e_cap=state.e_cap, ln_n=state.ln_n)
    return state2


def main():
    Q = int(sys.argv[1])
    e_cap = float(sys.argv[2])
    out = sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    iters = int(sys.argv[5]) if len(sys.argv) > 5 else 60000
    res = C.build_cover(Q, e_target=e_cap, verbose=False)
    st = State(Q, res["cover"], e_cap=e_cap)
    print(f"greedy: congr={len(st.chosen)} M={st.logm/LN10:.1f}d |U|={st.n_res()} "
          f"E={st.energy()[2]:.2f} D~{st.energy()[1]:.1f}")
    st = anneal(st, iters=iters, seed=seed)
    f, D, E = st.energy()
    print(f"anneal: congr={len(st.chosen)} M={st.logm/LN10:.1f}d |U|={st.n_res()} "
          f"E={E:.2f} D~{D:.1f}")
    covr = sorted((int(r), int(a)) for r, a in st.chosen.items())
    N0, M = C.crt(covr)
    residual = [int(q) for q in st.targets[st.cnt == 0]]
    spec = {"Q": Q, "cover": covr, "residual": residual,
            "boost": math.exp(st.logboost), "m_digits": st.logm / LN10,
            "E": E, "n_digits_est": D, "N0": str(N0), "M": str(M),
            "name": f"anneal_q{Q}_e{e_cap}_s{seed}"}
    json.dump(spec, open(out, "w"))
    print("wrote", out)


if __name__ == "__main__":
    main()
