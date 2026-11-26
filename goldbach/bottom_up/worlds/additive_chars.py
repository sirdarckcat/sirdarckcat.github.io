# World 4, converse table, the entry "lists that are intervals or progressions of classes": is the row set U of the 200,000 covers
# structured under ADDITIVE characters modulo the later primes? (The research session measured the multiplicative labelling, 26 Nov.)
# For a set U and a prime s, the class counts c_s(a) = #{q in U : q = a mod s} have Fourier coefficients F(h) = sum_a c_s(a) e(-ha/s).
# A list of heavy classes that is an interval or a progression {a0 + j b} shows as a large |F(h)| at h = b^-1 (and its multiples).
# Power(h) = |F(h)|^2 / |U| is 1 on average for i.i.d. uniform residues (an exponential variable). Measured over h = 1..(s-1)/2 and
# the 213 primes 467..1999, for the 300 covers' U, against: (R1) random subsets of the odd primes below 200,000 of the same size,
# (R2) i.i.d. uniform residues (pure noise). Also the same for the heavy-class lists themselves (top 1/8, 1/4, 1/2 of the classes).
#   python3 additive_chars.py > additive_chars.out
import numpy as np, math
rng = np.random.default_rng(20261126)
G = 200000

def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]

odd = primes_upto(G); odd = odd[odd > 2]
lines = [l for l in open("../covers/q200000_m89.txt") if l.startswith("COVER")]
def rows(line):
    cov = [tuple(map(int, w.split(":"))) for w in line.split() if ":" in w]
    alive = np.ones(len(odd), bool)
    for r, a in cov: alive &= (odd % r) != a
    return odd[alive], max(r for r, _ in cov)
Us = [rows(l) for l in lines]
maxmod = max(m for _, m in Us)
later = [int(p) for p in primes_upto(1999) if p > maxmod]
assert len(later) == 213, len(later)

def stats_counts(res_by_s, n):
    """res_by_s: dict s -> residues array (length n). Returns mean power, mean over s of max power/ln s, max over s of max/ln s."""
    allp = []; mx = []
    for s in later:
        c = np.bincount(res_by_s[s], minlength=s).astype(float)
        F = np.fft.fft(c)[1:(s + 1) // 2]
        pw = np.abs(F) ** 2 / n
        allp.append(pw.mean()); mx.append(pw.max() / math.log(s))
    return float(np.mean(allp)), float(np.mean(mx)), float(np.max(mx))

def stats_lists(res_by_s, frac):
    """Fourier of the heavy-class list (top frac of classes by count, ties at random), normalised so a random list has mean 1."""
    allp = []; mx = []
    for s in later:
        c = np.bincount(res_by_s[s], minlength=s).astype(float)
        L = int(round(frac * s))
        order = np.lexsort((rng.random(s), -c))[:L]
        ind = np.zeros(s); ind[order] = 1.0
        F = np.fft.fft(ind)[1:(s + 1) // 2]
        pw = np.abs(F) ** 2 / (L * (1 - L / s) * s / (s - 1))
        allp.append(pw.mean()); mx.append(pw.max() / math.log(s))
    return float(np.mean(allp)), float(np.mean(mx)), float(np.max(mx))

def summarize(name, sets):
    out = {k: [] for k in ("cnt", "l8", "l4", "l2")}
    for U in sets:
        rb = {s: (U % s) for s in later}
        out["cnt"].append(stats_counts(rb, len(U)))
        out["l8"].append(stats_lists(rb, 1 / 8)); out["l4"].append(stats_lists(rb, 1 / 4)); out["l2"].append(stats_lists(rb, 1 / 2))
    print(f"\n{name}: {len(sets)} sets, size {np.mean([len(U) for U in sets]):.1f}")
    for k, lab in (("cnt", "class counts"), ("l8", "heaviest 1/8 of classes"), ("l4", "heaviest 1/4"), ("l2", "heaviest 1/2")):
        a = np.array(out[k])
        print(f"  {lab:24s} mean power {a[:,0].mean():.4f} (sd over sets {a[:,0].std():.4f}) | per-prime max / ln s: mean {a[:,1].mean():.3f}"
              f" | largest over the 213 primes: mean {a[:,2].mean():.3f}, max {a[:,2].max():.3f}")
    return out

print("additive characters of the rows modulo the 213 primes 467..1999 (h = 1..(s-1)/2)")
real = summarize("the 300 covers at 200,000 (rows U)", [U for U, _ in Us])
n = int(round(np.mean([len(U) for U, _ in Us])))
r1 = summarize("R1: random subsets of the odd primes below 200,000", [np.sort(rng.choice(odd, n, replace=False)) for _ in range(300)])
r2 = summarize("R2: i.i.d. uniform residues (pure noise)", [rng.integers(0, 2 ** 62, n) for _ in range(300)])
# per-cover comparison of the largest character with R1
a = np.array(real["cnt"])[:, 2]; b = np.array(r1["cnt"])[:, 2]
print(f"\nlargest character over the 213 primes (class counts): covers {a.mean():.3f} +- {a.std():.3f}, R1 {b.mean():.3f} +- {b.std():.3f}")
