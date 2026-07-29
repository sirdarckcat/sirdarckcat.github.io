"""Door 1, D1.2: sum-product BP + decimation on the cover-assignment
factor graph.

Variables: moduli r (domain: classes 1..r-1). Factors: primes j with
psi_j = exp(-beta * [no incident modulus covers j]). Each prime meets
each modulus through exactly ONE class c_{r,j} = j mod r, so the
factor->variable message collapses to a single ratio per (j, r):

  lambda_{j,r} = 1 / (1 - (1-e^-beta) * prod_{r' != r} (1 - q_{j,r'}))

where q_{j,r} = cavity probability that modulus r takes class c_{r,j}.
Variable class-scores are bincounts of log-lambda; cavity subtraction
removes each prime's own contribution. Damped, log-space, vectorized.

Main: (1) validation vs exact enumeration on a 6-moduli synthetic;
(2) beta sweep tracking Bethe E[|U|]; (3) BP-guided decimation ->
concrete assignment, compared to the greedy plateau 867.
"""
import json
import os
import sys
import time

import numpy as np
from sympy import primerange

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(23)


class Instance:
    def __init__(self, moduli, res):
        self.moduli = moduli              # list of r
        self.res = res                    # dict r -> int32 array (len J)
        self.J = len(next(iter(res.values())))

    @classmethod
    def q122k(cls):
        inst = json.load(open(os.path.join(HERE, 'instance_q122k.json')))
        Q = inst['Q']
        moduli = [int(r) for r in inst['moduli']]
        P = np.array(list(primerange(3, Q)), dtype=np.int64)
        return cls(moduli, {r: (P % r).astype(np.int32) for r in moduli}), inst

    def ucount(self, assign):
        cc = np.zeros(self.J, dtype=np.int16)
        for r in self.moduli:
            cc += (self.res[r] == assign[r])
        return int((cc == 0).sum())


class BP:
    def __init__(self, inst, beta, damp=0.5):
        self.I = inst
        self.beta = beta
        self.damp = damp
        self.w = 1.0 - np.exp(-beta)
        self.R = len(inst.moduli)
        # q[j, i]: cavity prob modulus i covers prime j; 0 where res==0
        self.cover_ok = np.stack(
            [inst.res[r] != 0 for r in inst.moduli], axis=1)
        self.q = np.where(
            self.cover_ok,
            np.array([1.0 / (r - 1) for r in inst.moduli])[None, :]
            * (1 + 0.01 * rng.standard_normal((inst.J, self.R))), 0.0)
        self.q = np.clip(self.q, 0.0, 0.9)
        self.frozen = {}                  # modulus index -> fixed class

    def freeze(self, i, a):
        self.frozen[i] = a
        r = self.I.moduli[i]
        self.q[:, i] = np.where(self.I.res[r] == a, 1.0, 0.0)

    def iterate(self, iters=300, tol=1e-7):
        """Sequential (Gauss-Seidel) BP: each modulus update sees the
        freshest cavity products, maintained incrementally via Lp."""
        log1mq = np.log1p(-np.clip(self.q, 0, 1 - 1e-12))
        Lp = log1mq.sum(axis=1)
        for it in range(iters):
            dq_max = 0.0
            for i, r in enumerate(self.I.moduli):
                if i in self.frozen:
                    continue
                res = self.I.res[r]
                Pcav = np.exp(Lp - log1mq[:, i])
                loglam = np.where(self.cover_ok[:, i],
                                  -np.log1p(-self.w * np.clip(Pcav, 0, 1)),
                                  0.0)
                s = np.bincount(res, weights=loglam, minlength=r)
                s[0] = -np.inf
                mx = s[1:].max()
                es = np.exp(s - mx)
                denom = es[1:].sum()
                sc = s[res] - loglam
                ec = np.exp(sc - mx)
                qn = np.where(self.cover_ok[:, i],
                              ec / (denom - es[res] + ec), 0.0)
                qn = self.damp * qn + (1 - self.damp) * self.q[:, i]
                dq_max = max(dq_max, float(np.abs(qn - self.q[:, i]).max()))
                self.q[:, i] = qn
                new_l = np.log1p(-np.clip(qn, 0, 1 - 1e-12))
                Lp += new_l - log1mq[:, i]
                log1mq[:, i] = new_l
            if dq_max < tol:
                return it + 1
        return iters

    def marginals(self):
        """Belief per modulus over classes (list of arrays, index=class)."""
        log1mq = np.log1p(-np.clip(self.q, 0, 1 - 1e-12))
        Lp = log1mq.sum(axis=1)
        Pcav = np.exp(Lp[:, None] - log1mq)
        loglam = np.where(self.cover_ok,
                          -np.log1p(-self.w * np.clip(Pcav, 0, 1)), 0.0)
        out = []
        for i, r in enumerate(self.I.moduli):
            s = np.bincount(self.I.res[r], weights=loglam[:, i], minlength=r)
            s[0] = -np.inf
            if i in self.frozen:
                b = np.zeros(r)
                b[self.frozen[i]] = 1.0
            else:
                b = np.exp(s - s[1:].max())
                b[0] = 0.0
                b /= b.sum()
            out.append(b)
        return out

    def expected_uncovered(self):
        log1mq = np.log1p(-np.clip(self.q, 0, 1 - 1e-12))
        Pfull = np.exp(log1mq.sum(axis=1))
        eb = np.exp(-self.beta)
        return float((eb * Pfull / (1 - self.w * Pfull)).sum())


def validate():
    """Two-part gate. (a) Soft regime (beta=0.6): BP must track exact
    E[U] and marginals reasonably. (b) Operational: BP-guided
    decimation must reach (or nearly reach) the toy's EXACT optimum
    min|U| — the regime BP is actually used in. Loopy-BP marginal
    fidelity in the glassy regime is not required (and not attainable)."""
    moduli = [3, 5, 7, 11, 13, 17]
    J = 200
    res = {r: rng.integers(0, r, size=J).astype(np.int32) for r in moduli}
    inst = Instance(moduli, res)
    grids = np.meshgrid(*[np.arange(1, r) for r in moduli], indexing='ij')
    confs = np.stack([g.ravel() for g in grids], axis=1)
    C = len(confs)
    unc = np.zeros(C)
    for jj in range(J):
        cov = np.zeros(C, dtype=bool)
        for i, r in enumerate(moduli):
            cov |= (confs[:, i] == res[r][jj])
        unc += ~cov
    exact_min = int(unc.min())
    # (a) soft regime
    beta = 0.6
    w = np.exp(-beta * unc)
    Z = w.sum()
    exact_EU = float((w * unc).sum() / Z)
    bp = BP(inst, beta, damp=0.3)
    it = bp.iterate(1500)
    bp_EU = bp.expected_uncovered()
    marg = bp.marginals()
    errs = []
    for i, r in enumerate(moduli):
        ex = np.array([(w * (confs[:, i] == a)).sum() / Z for a in range(r)])
        errs.append(np.abs(ex - marg[i]).max())
    print(f"validation a (soft, beta={beta}): {it} iters; E[U] "
          f"exact={exact_EU:.2f} bp={bp_EU:.2f} "
          f"(rel {abs(bp_EU-exact_EU)/exact_EU:.1%}); max marginal "
          f"err={max(errs):.3f}", flush=True)
    ok_a = abs(bp_EU - exact_EU) / exact_EU < 0.10
    # (b) operational: decimation vs exact optimum
    best_dec = None
    for beta_d in (1.5, 2.5):
        assign, u = decimate(inst, beta_d, verbose=False)
        best_dec = u if best_dec is None else min(best_dec, u)
    print(f"validation b (operational): decimation best={best_dec} vs "
          f"exact optimum={exact_min} (greedy-style range: "
          f"{int(np.percentile(unc, 0.01))}..)", flush=True)
    ok_b = best_dec <= exact_min + 2
    return ok_a and ok_b


def beta_sweep(inst):
    print("beta sweep (Bethe E[|U|]):", flush=True)
    for beta in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
        bp = BP(inst, beta)
        it = bp.iterate(400)
        print(f"  beta={beta}: E[|U|]={bp.expected_uncovered():.1f} "
              f"({it} iters)", flush=True)


def decimate(inst, beta, verbose=True):
    bp = BP(inst, beta)
    bp.iterate(400)
    order = []
    while len(bp.frozen) < bp.R:
        marg = bp.marginals()
        best, bi, ba = -1.0, None, None
        for i in range(bp.R):
            if i in bp.frozen:
                continue
            m = marg[i]
            top = float(m.max())
            if top > best:
                best, bi, ba = top, i, int(m.argmax())
        bp.freeze(bi, ba)
        order.append((inst.moduli[bi], ba, best))
        bp.iterate(150)
        if verbose and len(bp.frozen) % 22 == 0:
            print(f"  decimated {len(bp.frozen)}/{bp.R}", flush=True)
    assign = {inst.moduli[i]: a for i, a in bp.frozen.items()}
    return assign, inst.ucount(assign)


if __name__ == '__main__':
    t0 = time.time()
    ok = validate()
    print(f"validation {'PASS' if ok else 'FAIL'}", flush=True)
    if not ok:
        sys.exit(1)
    inst, meta = Instance.q122k()
    beta_sweep(inst)
    for beta in (1.5, 2.5, 3.5):
        t1 = time.time()
        assign, u = decimate(inst, beta)
        print(f"decimation beta={beta}: |U| = {u}  (greedy 867)  "
              f"[{time.time()-t1:.0f}s]", flush=True)
        json.dump({str(r): int(a) for r, a in assign.items()},
                  open(os.path.join(HERE, f'd12_assign_b{beta}.json'), 'w'))
    print(f"total {time.time()-t0:.0f}s", flush=True)
