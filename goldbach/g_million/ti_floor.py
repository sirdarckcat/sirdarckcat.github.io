# T5: the floor of a cover problem by thermodynamic integration, from heatbath_pt2's statistics (<k> per beta).
# Configurations: a nonzero class for every modulus, so ln Z(0) = sum ln(r - 1). d ln Z / d beta = -<k>, so
#   ln Z(beta) = ln Z(0) - int_0^beta <k> dbeta',   S(beta) = ln Z(beta) + beta <k>(beta)
# is the log-count of covers with k near <k>(beta). The count of the best covers is S at the floor k0, and S(k0) >= 0. Below the
# coldest beta measured, b_c, every cover has dS/dk = beta >= b_c, so the floor obeys k0 >= <k>(b_c) - S(b_c)/b_c (a lower bound,
# given equilibrium up to b_c). With an extrapolation of beta(k) below, the estimate is k0 = the k where S reaches 0.
#   python3 ti_floor.py Q X stats1 [stats2 ...]
import sys
import numpy as np

def load(path):
    a = np.loadtxt(path, comments="#")
    return a[:, 0], a[:, 1], a[:, 2]

if __name__ == "__main__":
    Q, X = int(sys.argv[1]), int(sys.argv[2])
    s = np.ones(Q, bool); s[:2] = False
    for i in range(2, int(Q ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    P = np.nonzero(s)[0]; rows = P[(P > 2) & (P < Q)]; mods = P[(P > 2) & (P <= X)]
    lnZ0 = float(np.sum(np.log(mods - 1.0)))
    logp = np.zeros(len(rows))
    for r in mods.tolist():
        logp += np.where(rows % r == 0, 0.0, np.log1p(-1.0 / (r - 1)))
    k0 = float(np.exp(logp).sum())
    print(f"Q = {Q:,}, moduli up to {X} ({len(mods)}): ln Z(0) = {lnZ0:.1f}; <k> at beta = 0 (exact) = {k0:.1f}")
    for path in sys.argv[3:]:
        b, mk, sd = load(path)
        m = mk.copy()
        if b[0] == 0: print(f"{path}: <k> at beta 0 measured {m[0]:.1f} (exact {k0:.1f})"); m[0] = k0
        else: b = np.concatenate([[0.0], b]); m = np.concatenate([[k0], m]); sd = np.concatenate([[np.nan], sd])
        integ = np.concatenate([[0.0], np.cumsum(np.diff(b) * (m[1:] + m[:-1]) / 2)])
        S = lnZ0 - integ + b * m
        # var check: d<k>/dbeta = -var(k)
        print(f"{path}:\n  beta    <k>      sd    S(nats)  -d<k>/dbeta  var")
        for i in range(0, len(b), max(1, len(b) // 20)):
            dk = -(m[min(i + 1, len(b) - 1)] - m[max(i - 1, 0)]) / (b[min(i + 1, len(b) - 1)] - b[max(i - 1, 0)])
            print(f"  {b[i]:5.2f} {m[i]:8.1f} {sd[i]:6.1f} {S[i]:9.1f} {dk:10.1f} {sd[i] ** 2:8.1f}")
        bc, kc, Sc = b[-1], m[-1], S[-1]
        lb = kc - Sc / bc
        # extrapolation: beta(k) linear in k from the last quarter of the measured points, integrated until S = 0
        j = len(b) * 3 // 4
        A = np.polyfit(m[j:], b[j:], 1)     # beta = A0 k + A1
        k, Sx = kc, Sc
        while Sx > 0 and k > 0:
            k -= 1; Sx -= max(bc, np.polyval(A, k + 0.5))
        print(f"  coldest beta {bc:.2f}: <k> = {kc:.1f}, S = {Sc:.1f} nats; floor >= {lb:.1f} (bound); "
              f"floor ~ {k} (beta(k) linear from the last quarter, beta at the floor {np.polyval(A, k):.2f})")
