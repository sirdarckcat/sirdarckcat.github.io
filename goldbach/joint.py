"""Joint residue/representative optimizer for congruence covers.

anneal.py minimizes F = log M + E and accepts whatever CRT representative
x the chosen residues happen to produce.  That is fine while M is far
below the size budget B: the progression below B holds

    K(x, M; B) = max(0, (B - 1 - x)//M + 1)

candidates, and for M << B the representative shifts K by at most one.
Near or above the budget the representative *is* the game, so here we
track x exactly and minimize the expected-hit objective

    Phi = E - log K(x, M; B)

(E = |U| * boost / ln B is the per-candidate failure exponent; K e^-E is
the expected number of hits under the bound).  Tools:

  * Basis / JointState -- CRT basis C_{r,a} = a*(M/r)*((M/r)^{-1} mod r)
    (mod M); a residue move a -> a' shifts x by (a'-a)*C_{r,1} mod M, so
    coverage counts and the exact representative anneal together.  A
    200-300 digit modular add is negligible next to a Fermat test.
  * anneal_phi -- single-residue annealing on Phi.  Useful when M is
    within a couple of orders of B; useless when M >> B, because a
    single-residue move re-randomizes x uniformly mod M.
  * klist_solve -- multiple-choice modular meet-in-the-middle, Wagner
    style: split a block of moduli into 2^d lists, enumerate the top-c
    residue classes of each side, and merge with shrinking centered
    windows so the final representative lands in a target interval
    [0, T).  2^d lists of size L buy about (d+1)*log10(L) digits of
    cancellation below M; that entropy law is also the ceiling for what
    any such search can do.

CLI experiments (see RESULTS.md):
    baseline  -- x/M distribution over residue reassignments; K sensitivity
    mitm      -- smallest x/M at near-fixed coverage, moduli held fixed
    push      -- extend M past the budget, then force x back under it
"""

import argparse
import json
import math
import random
from bisect import bisect_left

import numpy as np
from sympy import isprime, primerange

LN10 = math.log(10)


# --------------------------------------------------------------------------
# CRT basis and joint state
# --------------------------------------------------------------------------

class Basis:
    """Fixed odd modulus set + the forced N == 0 (mod 2) congruence."""

    def __init__(self, odd_moduli):
        self.rs = sorted(int(r) for r in odd_moduli)
        M = 2
        for r in self.rs:
            M *= r
        self.M = M
        self.C1 = {}
        for r in self.rs:
            Mr = M // r
            self.C1[r] = (Mr * pow(Mr % r, -1, r)) % M  # even: 2 | M/r

    def x_of(self, chosen):
        x = 0
        for r, a in chosen.items():
            x += a * self.C1[r]
        return x % self.M


class JointState:
    """Residue assignment with incremental coverage counts and exact x."""

    def __init__(self, Q, chosen, budget_digits):
        self.Q = Q
        self.targets = np.array(list(primerange(3, Q)), dtype=np.int64)
        self.chosen = {int(r): int(a) for r, a in chosen.items()} \
            if isinstance(chosen, dict) else {int(r): int(a) for r, a in chosen}
        self.basis = Basis(self.chosen.keys())
        self.M = self.basis.M
        self.B = 10 ** budget_digits
        self.lnB = budget_digits * LN10
        self.mods = {}
        self.cnt = np.zeros(len(self.targets), dtype=np.int16)
        self.boost = 2.0
        for r, a in self.chosen.items():
            self.cnt += self.tmod(r) == a
            self.boost *= r / (r - 1)
        self.x = self.basis.x_of(self.chosen)

    def tmod(self, r):
        if r not in self.mods:
            self.mods[r] = self.targets % r
        return self.mods[r]

    def n_res(self):
        return int((self.cnt == 0).sum())

    def E(self, n_res=None):
        n = self.n_res() if n_res is None else n_res
        return n * self.boost / self.lnB

    def K(self, x=None):
        x = self.x if x is None else x
        return max(0, (self.B - 1 - x) // self.M + 1) if x < self.B else 0

    def phi(self, x=None, n_res=None):
        """E - log K, with a smooth overshoot penalty for x >= B (K = 0)."""
        x = self.x if x is None else x
        E = self.E(n_res)
        if x < self.B:
            K = (self.B - 1 - x) // self.M + 1
            return E - math.log(K)
        return E + math.log(x / self.B) + 1.0  # smooth ramp above the budget

    def set_residue(self, r, a_new):
        a_old = self.chosen[r]
        if a_new == a_old:
            return
        m = self.tmod(r)
        self.cnt -= (m == a_old).astype(np.int16)
        self.cnt += (m == a_new).astype(np.int16)
        self.x = (self.x + (a_new - a_old) * self.basis.C1[r]) % self.M
        self.chosen[r] = a_new

    def peek_residue(self, r, a_new):
        """(x', n_res') after a residue move, without applying it."""
        a_old = self.chosen[r]
        m = self.tmod(r)
        x_new = (self.x + (a_new - a_old) * self.basis.C1[r]) % self.M
        n_new = self.n_res() \
            + int(((self.cnt == 1) & (m == a_old)).sum()) \
            - int(((self.cnt == 0) & (m == a_new)).sum())
        return x_new, n_new

    def top_residues(self, r, c, alive_mask=None):
        """Top-c residue classes of r by coverage of the alive set."""
        alive = self.targets[self.cnt == 0] if alive_mask is None \
            else self.targets[alive_mask]
        cnts = np.bincount(alive % r, minlength=r) if len(alive) \
            else np.zeros(r, dtype=np.int64)
        order = np.argsort(-cnts, kind="stable")[:c]
        return [int(a) for a in order]


# --------------------------------------------------------------------------
# Phi annealer (single-residue moves)
# --------------------------------------------------------------------------

def anneal_phi(state, iters=20000, t0=0.5, t1=0.01, topj=4, seed=0,
               verbose=True):
    rng = random.Random(seed)
    f_cur = state.phi()
    best = (f_cur, dict(state.chosen), state.x)
    rs = list(state.chosen)
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / max(iters - 1, 1))
        r = rng.choice(rs)
        cands = state.top_residues(r, topj)
        a_new = rng.choice(cands)
        if a_new == state.chosen[r]:
            continue
        x_new, n_new = state.peek_residue(r, a_new)
        f_new = state.phi(x=x_new, n_res=n_new)
        if f_new < f_cur or rng.random() < math.exp((f_cur - f_new) / max(T, 1e-12)):
            state.set_residue(r, a_new)
            f_cur = f_new
            if f_cur < best[0]:
                best = (f_cur, dict(state.chosen), state.x)
        if verbose and it % 5000 == 0:
            print(f"  it={it:6d} Phi={f_cur:8.3f} |U|={state.n_res():5d} "
                  f"x/M={state.x/state.M:.3e} K={state.K()}", flush=True)
    for r, a in best[1].items():
        state.set_residue(r, a)
    return best[0]


# --------------------------------------------------------------------------
# k-list meet-in-the-middle (Wagner merge) on a block of moduli
# --------------------------------------------------------------------------

def _enum_group(basis, group, allowed):
    """All residue combos of `group`: values mod M, mixed-radix codes."""
    M = basis.M
    vals, codes = [0], [0]
    for r in group:
        C = basis.C1[r]
        avs = [(a * C) % M for a in allowed[r]]
        w = len(avs)
        nv, nc = [], []
        for v, code in zip(vals, codes):
            b = code * w
            for i, av in enumerate(avs):
                s = v + av
                nv.append(s if s < M else s - M)
                nc.append(b + i)
        vals, codes = nv, nc
    return vals, codes


def _decode_group(code, group, allowed):
    out = {}
    for r in reversed(group):
        w = len(allowed[r])
        out[r] = allowed[r][code % w]
        code //= w
    return out


def _center(v, M):
    return v - M if v > M // 2 else v


def _merge(av, ac, bv, bc, lo, hi, M, cap, rng, label=""):
    """Pairs with centered (va+vb mod M) in [lo, hi).  Parallel lists."""
    order = sorted(range(len(bv)), key=bv.__getitem__)
    bs = [bv[i] for i in order]
    bcs = [bc[i] for i in order]
    half = M // 2
    ov, oc = [], []
    for va, ca in zip(av, ac):
        for delta in (-M, 0, M):
            l, h = lo - va + delta, hi - va + delta
            if h < bs[0] or l > bs[-1]:
                continue
            i = bisect_left(bs, l)
            j = bisect_left(bs, h)
            for k in range(i, j):
                s = va + bs[k]
                if s > half:
                    s -= M
                elif s <= -half:
                    s += M
                if lo <= s < hi:
                    ov.append(s)
                    oc.append((ca, bcs[k]))
    if len(ov) > cap:
        keep = rng.sample(range(len(ov)), cap)
        ov = [ov[i] for i in keep]
        oc = [oc[i] for i in keep]
    if label:
        print(f"    merge {label}: {len(av)}x{len(bv)} -> {len(ov)} "
              f"in window {float(hi - lo):.3e}", flush=True)
    return ov, oc


def _flatten_code(code):
    if isinstance(code, tuple):
        return _flatten_code(code[0]) + _flatten_code(code[1])
    return [code]


def klist_solve(state, block, allowed, nlists, T, slack=3, cap=None,
                final_cap=1000, seed=0, verbose=True):
    """Find block assignments landing x in [0, T).

    Returns list of (x, assignment dict for block moduli), unsorted.
    """
    rng = random.Random(seed)
    basis, M = state.basis, state.M
    x_fixed = state.x
    for r in block:
        x_fixed = (x_fixed - state.chosen[r] * basis.C1[r]) % M

    groups = [block[i::nlists] for i in range(nlists)]
    lists = []
    for gi, g in enumerate(groups):
        vals, codes = _enum_group(basis, g, allowed)
        if gi == 0:
            vals = [(v + x_fixed) % M for v in vals]
        vals = [_center(v, M) for v in vals]
        lists.append((vals, codes))
        if verbose:
            print(f"    list {gi}: {len(vals)} combos over moduli {g}",
                  flush=True)
    L0 = min(len(v) for v, _ in lists)
    cap = cap or 6 * L0

    width = M
    while len(lists) > 2:
        width = max(slack * width // L0, 8)
        nxt = []
        for i in range(0, len(lists), 2):
            (av, ac), (bv, bc) = lists[i], lists[i + 1]
            nxt.append(_merge(av, ac, bv, bc, -width // 2, width // 2, M,
                              cap, rng, label=f"lvl w={float(width):.2e}"
                              if verbose else ""))
        lists = nxt
    (av, ac), (bv, bc) = lists
    ov, oc = _merge(av, ac, bv, bc, 0, T, M, final_cap, rng,
                    label="final" if verbose else "")

    sols = []
    for x_val, code in zip(ov, oc):
        leaf = _flatten_code(code)
        asg = {}
        for g, cd in zip(groups, leaf):
            asg.update(_decode_group(cd, g, allowed))
        sols.append((x_val, asg))
    return sols


def eval_assignment(state, block, asg):
    """(x, n_res) if block moduli take residues `asg` (exact, non-mutating)."""
    cnt = state.cnt.copy()
    x = state.x
    for r in block:
        a_old, a_new = state.chosen[r], asg[r]
        if a_new == a_old:
            continue
        m = state.tmod(r)
        cnt -= (m == a_old).astype(np.int16)
        cnt += (m == a_new).astype(np.int16)
        x = (x + (a_new - a_old) * state.basis.C1[r]) % state.M
    return x, int((cnt == 0).sum())


def block_allowed(state, block, c, keep_current=True):
    """Top-c residues per block modulus, ranked on the block-exposed set."""
    cnt_nb = state.cnt.copy()
    for r in block:
        cnt_nb -= (state.tmod(r) == state.chosen[r]).astype(np.int16)
    exposed = cnt_nb == 0
    allowed = {}
    for r in block:
        top = state.top_residues(r, c, alive_mask=exposed)
        if keep_current and state.chosen[r] not in top:
            top = [state.chosen[r]] + top[:c - 1]
        allowed[r] = top
    return allowed, int(exposed.sum())


# --------------------------------------------------------------------------
# cover extension past the budget
# --------------------------------------------------------------------------

def extend_cover(state, target_mdigits, rmax=20000):
    """Greedily add primes (best residual coverage per digit) until
    digits(M) >= target_mdigits.  Rebuilds the state (new basis)."""
    chosen = dict(state.chosen)
    have = set(chosen)
    residual = state.targets[state.cnt == 0]
    logm = math.log(2) + sum(math.log(r) for r in chosen)
    cands = [r for r in primerange(463, rmax) if r not in have]
    while logm / LN10 < target_mdigits and cands:
        best = None
        for r in cands:
            cnts = np.bincount(residual % r, minlength=r)
            a = int(cnts.argmax())
            score = cnts[a] / math.log10(r)
            if best is None or score > best[0]:
                best = (score, r, a)
        _, r, a = best
        chosen[r] = a
        cands.remove(r)
        logm += math.log(r)
        residual = residual[residual % r != a]
    return JointState(state.Q, chosen,
                      budget_digits=round(math.log10(state.B)))


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------

def verify_system(spec, budget_digits=None):
    """Check the CRT system spec end to end.  Returns dict of stats."""
    x, M, Q = int(spec["N0"]), int(spec["M"]), spec["Q"]
    cover = [(int(r), int(a)) for r, a in spec["cover"]]
    assert x % 2 == 0 and 0 <= x < M
    Mchk = 2
    for r, a in cover:
        assert isprime(r) and 0 <= a < r
        assert x % r == a, (r, a, x % r)
        Mchk *= r
    assert Mchk == M
    targets = list(primerange(3, Q))
    residual = []
    for q in targets:
        if not any(q % r == a for r, a in cover):
            residual.append(q)
    assert residual == [int(q) for q in spec["residual"]]
    out = {"m_digits": len(str(M)), "x_digits": len(str(x)),
           "n_res": len(residual), "covered": len(targets) - len(residual)}
    if budget_digits is not None:
        out["under_budget"] = x < 10 ** budget_digits
    return out


# --------------------------------------------------------------------------
# CLI experiments
# --------------------------------------------------------------------------

def _load_state(path, budget_digits):
    spec = json.load(open(path))
    st = JointState(spec["Q"], spec["cover"], budget_digits)
    if "N0" in spec and int(spec["M"]) == st.M:
        assert st.x == int(spec["N0"]) % st.M, "CRT mismatch vs stored N0"
    return spec, st


def cmd_baseline(args):
    spec, st = _load_state(args.spec, args.budget_digits)
    print(f"cover: {len(st.chosen)} odd moduli, M = {len(str(st.M))} digits, "
          f"|U| = {st.n_res()}, boost = {st.boost:.2f}")
    print(f"budget B = 10^{args.budget_digits};  M/B = {st.M / st.B:.3e}")
    print(f"x = {len(str(st.x))} digits, x/M = {st.x / st.M:.6f}")
    k_lo, k_hi = st.K(x=st.M - 1), st.K(x=0)
    print(f"K range over all x in [0,M): [{k_lo}, {k_hi}]  "
          f"-> max |dlogK| = {math.log(k_hi) - math.log(max(k_lo, 1)):.2e}")
    print(f"E = {st.E():.2f};  Phi = {st.phi():.3f} "
          f"(old objective logM+E = {math.log(st.M) + st.E():.2f})")
    # x/M distribution over random top-4 reassignments of random moduli
    rng = random.Random(args.seed)
    rs = sorted(st.chosen)[-40:]
    tops = {r: st.top_residues(r, 4) for r in rs}
    ratios, dres = [], []
    base_res = st.n_res()
    for _ in range(args.samples):
        block = rng.sample(rs, 12)
        asg = {r: rng.choice(tops[r]) for r in block}
        x, n = eval_assignment(st, block, asg)
        ratios.append(x / st.M)
        dres.append(n - base_res)
    ratios.sort()
    dec = [ratios[int(f * (len(ratios) - 1))] for f in
           (0, .1, .25, .5, .75, .9, 1.0)]
    print(f"x/M over {args.samples} random top-4 reassignments "
          f"(12 of the largest 40 moduli):")
    print("  deciles (0,10,25,50,75,90,100%): "
          + " ".join(f"{d:.3f}" for d in dec))
    print(f"  min x/M = {ratios[0]:.3e}  (uniform predicts "
          f"~{1 / args.samples:.1e});  d|U| range "
          f"[{min(dres)},{max(dres)}]")


def cmd_mitm(args):
    spec, st = _load_state(args.spec, args.budget_digits)
    nblock = args.lists * args.group
    block = sorted(st.chosen)[-nblock:]
    allowed, n_exposed = block_allowed(st, block, args.c)
    L = args.c ** len(block[0::args.lists])
    predicted = (math.log2(args.lists) + 1) * math.log10(L)
    print(f"block = largest {nblock} moduli {block[0]}..{block[-1]}, "
          f"top-{args.c} residues, {args.lists} lists of ~{L} combos")
    print(f"exposed targets (covered only via block): {n_exposed}")
    print(f"entropy budget ~ {predicted:.1f} digits of cancellation")
    T = int(st.M * args.frac)
    sols = klist_solve(st, block, allowed, args.lists, T, seed=args.seed)
    print(f"target x/M < {args.frac:.1e}: {len(sols)} solutions")
    base_res = st.n_res()
    scored = []
    for x_val, asg in sols:
        x, n = eval_assignment(st, block, asg)
        assert x == x_val % st.M
        scored.append((n, x))
    scored.sort()
    for n, x in scored[:10]:
        print(f"  x/M = {x / st.M:.3e}  ({len(str(x))} digits)   "
              f"|U| = {n} ({n - base_res:+d})")
    if scored:
        n, x = scored[0]
        print(f"best: x/M = {x / st.M:.3e} at |U| = {n} "
              f"(base {base_res}); log10(M/x) = "
              f"{math.log10(st.M / max(x, 1)):.1f} digits cancelled")


def cmd_push(args):
    spec, st = _load_state(args.spec, args.budget_digits)
    print(f"base: M = {len(str(st.M))} digits, |U| = {st.n_res()}")
    st = extend_cover(st, args.target_digits)
    print(f"extended: {len(st.chosen)} odd moduli, M = {len(str(st.M))} "
          f"digits, |U| = {st.n_res()}, boost = {st.boost:.2f}")
    over = math.log10(st.M) - args.budget_digits
    print(f"overshoot: M/B = 10^{over:.2f} -> need {over:.1f} digits "
          f"of cancellation")
    nblock = args.lists * args.group
    block = sorted(st.chosen)[-nblock:]
    allowed, n_exposed = block_allowed(st, block, args.c)
    L = args.c ** len(block[0::args.lists])
    predicted = (math.log2(args.lists) + 1) * math.log10(L)
    print(f"block = largest {nblock} moduli {block[0]}..{block[-1]}, "
          f"top-{args.c} residues -> {args.lists} lists of ~{L}; "
          f"entropy ~ {predicted:.1f} digits")
    sols = klist_solve(st, block, allowed, args.lists, st.B,
                       slack=args.slack, seed=args.seed)
    print(f"{len(sols)} representatives under 10^{args.budget_digits}")
    if not sols:
        print("no solution: raise --c, lower --target-digits, or reseed")
        return
    scored = []
    for x_val, asg in sols:
        x, n = eval_assignment(st, block, asg)
        assert x == x_val % st.M and x < st.B
        scored.append((n, x, asg))
    scored.sort(key=lambda t: t[0])
    n, x, asg = scored[0]
    for r in block:
        st.set_residue(r, asg[r])
    assert st.x == x and st.n_res() == n
    E = st.E()
    print(f"best: x = {len(str(x))} digits (< 10^{args.budget_digits}), "
          f"M = {len(str(st.M))} digits, |U| = {n}, E = {E:.2f}")
    print(f"cancellation achieved: log10(M/x) = "
          f"{math.log10(st.M / x):.1f} digits")
    out_spec = {
        "Q": st.Q,
        "cover": sorted((int(r), int(a)) for r, a in st.chosen.items()),
        "residual": [int(q) for q in st.targets[st.cnt == 0]],
        "boost": st.boost, "m_digits": math.log10(st.M),
        "E": E, "N0": str(st.x), "M": str(st.M),
        "budget_digits": args.budget_digits,
        "name": f"push_m{args.target_digits}_b{args.budget_digits}"
                f"_s{args.seed}",
    }
    json.dump(out_spec, open(args.out, "w"))
    chk = verify_system(out_spec, args.budget_digits)
    print("verified:", chk)
    print("wrote", args.out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("baseline")
    p.add_argument("spec")
    p.add_argument("--budget-digits", type=int, default=197)
    p.add_argument("--samples", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.set_defaults(fn=cmd_baseline)

    p = sub.add_parser("mitm")
    p.add_argument("spec")
    p.add_argument("--budget-digits", type=int, default=197)
    p.add_argument("--lists", type=int, default=2)
    p.add_argument("--group", type=int, default=8)
    p.add_argument("--c", type=int, default=4)
    p.add_argument("--frac", type=float, default=1e-8)
    p.add_argument("--seed", type=int, default=0)
    p.set_defaults(fn=cmd_mitm)

    p = sub.add_parser("push")
    p.add_argument("spec")
    p.add_argument("--budget-digits", type=int, default=197)
    p.add_argument("--target-digits", type=int, default=208)
    p.add_argument("--lists", type=int, default=4)
    p.add_argument("--group", type=int, default=8)
    p.add_argument("--c", type=int, default=5)
    p.add_argument("--slack", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="push_spec.json")
    p.set_defaults(fn=cmd_push)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
