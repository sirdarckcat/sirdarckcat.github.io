#!/usr/bin/env python3
"""What 'few repeated strikes' is worth on the 200,000 cover (the best members of a window have more strikes and fewer repeats than chance).

    python3 cover_repeats.py [depth = 30000] [members = 12000]

A strike: a later prime s divides N - q for a row q the cover left; a repeat: a strike on a row already struck.  Two questions:
as a score, does the repeat count of the first later primes (463 to 1,000) say anything about the rows finally left that the
rows left after those primes do not; as a constraint, what would it buy if no row were struck twice by those primes.
Members are modelled by independent uniform classes at the later primes (the Chinese remainder theorem; the Lean session's
sieve of 240,000 real members of this cover has strikes and repeats exactly at chance)."""
import sys, math, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import cover_record as cr
rows, p = cr.load(cr.S + "q200000_m89.txt"); rows = rows[rows < 200000]; n = len(rows)
Z1, Z2 = 1000, int(sys.argv[1]) if len(sys.argv) > 1 else 30000; NM = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
sv = np.ones(Z2 + 1, dtype=bool); sv[:2] = False
for i in range(2, int(Z2 ** .5) + 1):
    if sv[i]: sv[i * i::i] = False
later = [int(s) for s in np.nonzero(sv)[0] if s > 463]
rng = np.random.default_rng(7)
# per prime: rows sorted by class
tabs = []
for s in later:
    c = rows % s; o = np.argsort(c, kind="stable"); cs = c[o]; start = np.searchsorted(cs, np.arange(s + 1))
    tabs.append((s, o, start))
I1 = np.zeros(NM); U1 = np.zeros(NM); I2 = np.zeros(NM); U2 = np.zeros(NM)
for m in range(NM):
    cnt = np.zeros(n, dtype=np.int16); early = np.zeros(n, dtype=np.int16)
    for (s, o, start) in tabs:
        a = rng.integers(s); idx = o[start[a]:start[a + 1]]
        if len(idx):
            cnt[idx] += 1
            if s <= Z1: early[idx] += 1
    I1[m] = early.sum(); U1[m] = (early > 0).sum(); I2[m] = cnt.sum(); U2[m] = (cnt > 0).sum()
S1 = n - U1; S2 = n - U2; R1 = I1 - U1; R2 = I2 - U2
print(f"cover: {n} rows; members simulated: {NM}; early primes 463 to {Z1}: {sum(1 for s in later if s <= Z1)}; all primes to {Z2}: {len(later)}")
print(f"early primes: strikes {I1.mean():.1f}, distinct {U1.mean():.1f}, repeats {R1.mean():.2f} (sd {R1.std():.2f}); chance for these strikes: {(I1 - n * (1 - np.exp(-I1 / n))).mean():.2f}")
print(f"to {Z2}: strikes {I2.mean():.1f}, distinct {U2.mean():.1f}, repeats {R2.mean():.1f}; rows left mean {S2.mean():.1f} sd {S2.std():.2f}")
# is the early repeat count a score beside the early rows left?  regress the final rows left on (S1, R1)
X = np.column_stack([np.ones(NM), S1 - S1.mean(), R1 - R1.mean()]); beta, res, rk, svals = np.linalg.lstsq(X, S2, rcond=None)
resid = S2 - X @ beta; se = math.sqrt(resid.var() / NM) / R1.std()
X0 = np.column_stack([np.ones(NM), S1 - S1.mean()]); b0 = np.linalg.lstsq(X0, S2, rcond=None)[0]; r0 = S2 - X0 @ b0
print(f"final rows left on early rows left: slope {b0[1]:.4f} (survival through the later primes: {S2.mean() / S1.mean():.4f}); residual sd {r0.std():.3f}")
print(f"adding the early repeat count: coefficient {beta[2]:+.4f} +- {se:.4f} rows per repeat; residual sd {resid.std():.3f}; correlation of repeats with the residual {np.corrcoef(R1, r0)[0, 1]:+.4f}")
print(f"correlation of early repeats with early rows left: {np.corrcoef(R1, S1)[0, 1]:+.3f}; with early strikes: {np.corrcoef(R1, I1)[0, 1]:+.3f}")
# the best members by final rows left: their early strikes and repeats against all
top = S2 <= np.quantile(S2, 0.015)
print(f"emptiest 1.5% at {Z2}: early strikes {I1[top].mean():.1f} against {I1.mean():.1f}; early repeats {R1[top].mean():.2f} against {R1.mean():.2f} (chance for their strikes {(I1[top] - n * (1 - np.exp(-I1[top] / n))).mean():.2f}); "
      f"all: strikes {I2[top].mean():.1f} against {I2.mean():.1f}, repeats {R2[top].mean():.1f} against {R2.mean():.1f}")
# as a constraint: the two pins that fit the window; the heaviest classes of the first primes, and their overlap
best = []
for (s, o, start) in tabs[:40]:
    sizes = np.diff(start); a = int(np.argmax(sizes)); best.append((int(sizes[a]), s, a, set(o[start[a]:start[a + 1]].tolist())))
best.sort(reverse=True)
(f1, s1, a1, r1), (f2, s2, a2, r2) = best[0], best[1]
print(f"two heaviest classes among the first 40 later primes: {f1} rows mod {s1}, {f2} rows mod {s2}, rows in both: {len(r1 & r2)}; the mean class holds {n / s1:.1f}; expected overlap of two random classes {n / (s1 * s2):.4f} rows")
w1000 = math.log(463) / math.log(1000); w8 = math.log(463) / math.log(1e8)
print(f"if no row were struck twice by the early primes: {R1.mean():.1f} more rows struck at {Z1}, of which {R1.mean() * w8 / w1000:.1f} would still be standing at 1e8; at {-math.log(1 - p / w8):.4f} nats each: {R1.mean() * w8 / w1000 * -math.log(1 - p / w8):.2f} nats, for pins on {sum(1 for s in later if s <= Z1)} primes ({sum(math.log(s) for s in later if s <= Z1):.0f} nats of modulus)")
