"""Item 2, the variance of the number S of rows left after a deeper sieve, recomputed from the cover file alone.

S(N) = number of rows q of the cover with N - q free of prime factors in (z, B], z = 463 (N - q has no prime factor up
to z by the definition of a row).  Model: N uniform modulo every prime s in (z, B], independently (exact over a full
period of the members).  Then
   E S = n w,   w = prod_{z < s <= B} (1 - 1/s)
   Var S = n w (1 - w) + w^2 sum_{i != j} (rho_ij - 1),   rho_ij = prod_s (1 - nu_s/s) / (1 - 1/s)^2,
nu_s = 1 if s divides q_i - q_j, else 2.  A difference below 467^2 has at most one prime factor s0 above 463, so
   rho_ij = R (s0 - 1)/(s0 - 2) if it has one (and s0 <= B), else R,   R = prod_{z < s <= B} (1 - 1/(s - 1)^2).
The sum over pairs is computed twice: from the largest prime factor of every difference, and from the class counts of
the rows modulo every prime s (sum over classes of K (K - 1), divided by s - 2).

  python selection_check.py FILE Q [B] [LINES]      LINES: how many cover lines of the file (default 1)"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from covlib import primes_upto, read_covers, rows_of

Z = 463
path = sys.argv[1]; Q = int(sys.argv[2]); B = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10 ** 8
nlines = int(sys.argv[4]) if len(sys.argv) > 4 else 1
assert Q < 467 * 467

PR = primes_upto(B)
big = PR[PR > Z].astype(np.float64)
w_exact = math.exp(float(np.sum(np.log1p(-1.0 / big))))
R_exact = math.exp(float(np.sum(np.log1p(-1.0 / (big - 1.0) ** 2))))
w_appr = math.log(Z) / math.log(B); R_appr = math.exp(-1.0 / (Z * math.log(Z)))
print(f"# B = {B:.3g}: primes in ({Z}, B]: {len(big):,d}")
print(f"# w: exact product {w_exact:.6f}; ln {Z} / ln B = {w_appr:.6f} (ratio {w_appr / w_exact:.5f})")
print(f"# R = prod (1 - 1/(s-1)^2): exact {R_exact:.8f}; exp(-1/({Z} ln {Z})) = {R_appr:.8f}")

# largest prime factor above Z of every d < Q (0 if none)
s0 = np.zeros(Q, dtype=np.int64)
for s in PR[(PR > Z) & (PR < Q)]:
    s0[s::s] = s
inv = np.where((s0 > 0) & (s0 <= B), 1.0 / np.maximum(s0 - 2, 1), 0.0)
ODD = primes_upto(Q - 1)[1:]
smalls = [int(x) for x in PR[(PR > Z) & (PR < Q) & (PR <= B)]]

def analyse(classes, full):
    rows = rows_of(classes, Q, ODD); n = len(rows)
    d = np.abs(rows[:, None] - rows[None, :])
    T_pairs = float(inv[d].sum())                                  # ordered pairs i != j (the diagonal has d = 0, inv 0)
    npairs = int((inv[d] > 0).sum())
    # the same from the class counts (every prime for the first line, as a check; the primes up to 997 otherwise)
    T_classes = 0.0; disp = []
    for s in (smalls if full else [x for x in smalls if x <= 997]):
        K = np.bincount(rows % s, minlength=s).astype(np.float64)
        T_classes += float((K * (K - 1)).sum()) / (s - 2)
        if s <= 997: disp.append((s, K))
    if not full: T_classes = float("nan")
    out = {"n": n, "T_pairs": T_pairs, "T_classes": T_classes, "npairs": npairs, "disp": disp}
    for tag, w, R in (("exact", w_exact, R_exact), ("approx", w_appr, R_appr)):
        pair = n * (n - 1) * (R - 1) + R * T_pairs
        ind = n * w * (1 - w); var = ind + w * w * pair
        out[tag] = {"mean": n * w, "ind": ind, "pair": pair, "var": var, "sd_ratio": math.sqrt(var / ind)}
    return out

covers = read_covers(path)
print(f"# {path}: {len(covers)} cover lines, Q = {Q:,d}")
print("line | rows (claimed) | ordered pairs whose difference has a prime factor in (463, B] | sum of 1/(s0-2) over them, from the differences | from the class counts | "
      "with the exact w and R: E S | n w (1-w) | pair term w^2 sum(rho-1) | Var S | sd ratio | with w = ln 463/ln B and R = exp(-1/(463 ln 463)): n w (1-w) | Var S | sd ratio")
ratios = []
for i, (claimed, classes) in enumerate(covers[:nlines]):
    a = analyse(classes, i == 0); e = a["exact"]; x = a["approx"]
    ratios.append((e["sd_ratio"], x["sd_ratio"], a["n"], e["var"], e["ind"], float(np.mean([K[1:].var() / K[1:].mean() for _, K in a["disp"]]))))
    if i < 5 or i == nlines - 1:
        print(f"{i} | {a['n']} ({claimed}) | {a['npairs']:,d} | {a['T_pairs']:.3f} | {a['T_classes']:.3f} | {e['mean']:.2f} | {e['ind']:.2f} | {e['var'] - e['ind']:+.2f} | {e['var']:.2f} | {e['sd_ratio']:.4f} | "
              f"{x['ind']:.2f} | {x['var']:.2f} | {x['sd_ratio']:.4f}", flush=True)
    if i == 0:
        first = a
if nlines > 1:
    r = np.array(ratios)
    print(f"# sd ratio over the first {len(r)} lines: exact w and R: min {r[:,0].min():.4f} max {r[:,0].max():.4f} mean {r[:,0].mean():.4f}; "
          f"approximate w and R: min {r[:,1].min():.4f} max {r[:,1].max():.4f} mean {r[:,1].mean():.4f}")
    print(f"# over those lines: rows {int(r[:,2].min())} to {int(r[:,2].max())}; Var S (exact constants) {r[:,3].min():.2f} to {r[:,3].max():.2f}; binomial {r[:,4].min():.2f} to {r[:,4].max():.2f}; "
          f"sd S {np.sqrt(r[:,3]).min():.3f} to {np.sqrt(r[:,3]).max():.3f}; mean variance/mean of the class counts modulo 467..997: {r[:,5].min():.3f} to {r[:,5].max():.3f}")
# dispersion of the class counts of the first line modulo the primes 467..997
n = first["n"]; vals = {"all s classes, population variance": [], "the s - 1 nonzero classes, population variance": [], "all s classes, sample variance": []}
for s, K in first["disp"]:
    vals["all s classes, population variance"].append(K.var() / K.mean())
    K1 = K[1:]; vals["the s - 1 nonzero classes, population variance"].append(K1.var() / K1.mean())
    vals["all s classes, sample variance"].append(K.var(ddof=1) / K.mean())
print(f"# class counts of the rows of line 0 modulo the {len(first['disp'])} primes 467..997: variance / mean, averaged over the primes:")
for k, v in vals.items(): print(f"#   {k}: {np.mean(v):.4f} (min {np.min(v):.3f}, max {np.max(v):.3f})")
