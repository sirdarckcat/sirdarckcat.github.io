"""Fixed-modulus anneal for the R(10^200) budget game.

The ceiling game wants max Q such that a cover with M <= 10^(200 - rho)
has feasible E at ln N = 200 ln10, where rho ~ 11 digits supplies the
k-range (ln K ~ 25.5 nats).  The plain annealer objective F = ln M + E
is wrong here: k-room beyond the scan budget is worthless, so the
optimum sits AT the modulus cap.  This driver anneals E alone subject to
logm <= cap, using cover.build_cover for a start and anneal.State for
incremental deltas.

Usage: r200_anneal.py Q m_cap_digits iters seed out.json
"""

import json
import math
import random
import sys

import cover as C
from anneal import State

LN10 = math.log(10)
LNN = 200 * LN10


def trim_to_cap(st, cap):
    """Drop worst-value moduli (E increase per nat of size) until under cap."""
    while st.logm > cap:
        best = None
        for r in list(st.chosen):
            _, _, E2 = st.delta_drop(r)
            val = (E2 - st.energy()[2]) / math.log(r)
            if best is None or val < best[0]:
                best = (val, r)
        st.apply_drop(best[1])


def anneal_capped(st, cap, iters, seed, t0=0.25, t1=0.01):
    rng = random.Random(seed)
    E_cur = st.energy()[2]
    best = (E_cur, dict(st.chosen))
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        kind = rng.random()
        move = None
        if kind < 0.55 and st.chosen:
            r = rng.choice(list(st.chosen))
            cands = [a for a, _ in st.best_residues(r, topj=4)
                     if a != st.chosen[r]]
            if cands:
                move = ("chg", r, rng.choice(cands))
        elif kind < 0.75 and st.chosen:
            move = ("drop", rng.choice(list(st.chosen)), None)
        else:
            r = rng.choice(st.cand)
            if r not in st.chosen and st.logm + math.log(r) <= cap:
                br = st.best_residues(r, topj=2)
                if br and br[0][1] > 0:
                    move = ("add", r, br[0][0])
        if move is None:
            continue
        op, r, a = move
        if op == "chg":
            _, _, E_new = st.delta_change_residue(r, a)
        elif op == "drop":
            _, _, E_new = st.delta_drop(r)
        else:
            _, _, E_new = st.delta_add(r, a)
        if E_new < E_cur or rng.random() < math.exp((E_cur - E_new)
                                                    / max(T, 1e-9)):
            if op == "chg":
                st.apply_change(r, a)
            elif op == "drop":
                st.apply_drop(r)
            else:
                st.apply_add(r, a)
            E_cur = E_new
            if E_cur < best[0] and st.logm <= cap:
                best = (E_cur, dict(st.chosen))
        if it % 10000 == 0:
            print(f"  it={it:6d} T={T:.3f} E={E_cur:6.3f} "
                  f"congr={len(st.chosen)} M={st.logm / LN10:.1f}d "
                  f"|U|={st.n_res()}", flush=True)
    return best


def main():
    Q = int(sys.argv[1])
    cap = float(sys.argv[2]) * LN10
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 40000
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    out = sys.argv[5] if len(sys.argv) > 5 else None

    res = C.build_cover(Q, e_target=16.5, rmax=8000, verbose=False)
    st = State(Q, dict(res["cover"]), rmax=8000, e_cap=99.0, ln_n=LNN)
    trim_to_cap(st, cap)
    print(f"Q={Q} start: congr={len(st.chosen)} M={st.logm / LN10:.1f}d "
          f"|U|={st.n_res()} E={st.energy()[2]:.3f}", flush=True)
    bestE, chosen = anneal_capped(st, cap, iters, seed)
    st = State(Q, chosen, rmax=8000, e_cap=99.0, ln_n=LNN)
    E = st.energy()[2]
    lnK = LNN - st.logm
    print(f"FINAL Q={Q}: congr={len(st.chosen)} M={st.logm / LN10:.2f}d "
          f"|U|={st.n_res()} boost={math.exp(st.logboost):.2f} E={E:.3f} "
          f"lnK={lnK:.1f} E[hits]={math.exp(min(lnK, lnK) - E):.2f}")
    if out:
        cov = sorted((int(r), int(a)) for r, a in st.chosen.items())
        N0, M = C.crt(cov)
        residual = [int(q) for q in st.targets[st.cnt == 0]]
        json.dump({"Q": Q, "cover": cov, "residual": residual,
                   "boost": math.exp(st.logboost),
                   "m_digits": st.logm / LN10, "E": E,
                   "N0": str(N0), "M": str(M),
                   "name": f"r200_q{Q}"}, open(out, "w"))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
