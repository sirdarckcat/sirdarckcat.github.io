# T5 (research session): an even N with g(N) >= 1,000,000 in as few digits as possible. Step 1: the cover.
# Moduli: the odd primes up to X (629 of them up to 4,657 for about 2,000 digits, 491 up to 3,527 for about 1,500). Rows: the odd
# primes q < Q = 1,000,003. A class a_r for every modulus (nonzero); N = a_r (mod r) for all r makes N - q divisible by r for every
# row q = a_r (mod r). The rows in no class are left to luck. Greedy (fullest nonzero class of what is left, moduli in increasing
# order), then 1-flip descent to a local optimum, then iterated local search (perturb a few moduli, descend, keep if better).
#   python3 cover.py X [seconds of local search] [seed]      -> cover_X<X>.txt (r:a pairs) and the rows left
import sys, time, math
import numpy as np

import os
Q = int(os.environ.get('COVER_Q', 1000003))

def odd_primes_below(n):
    s = np.ones(n, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    p = np.nonzero(s)[0]; return p[p > 2]

class Cover:
    def __init__(self, X):
        self.rows = odd_primes_below(Q).astype(np.int64)
        self.mods = odd_primes_below(X + 1)
        self.R = np.empty((len(self.mods), len(self.rows)), np.int16)      # rows mod each modulus (all moduli are < 32768)
        for i, r in enumerate(self.mods): self.R[i] = self.rows % r
        self.cls = np.zeros(len(self.mods), np.int64); self.cnt = np.zeros(len(self.rows), np.int16)

    def greedy(self):
        unc = np.ones(len(self.rows), bool)
        for i, r in enumerate(self.mods):
            c = np.bincount(self.R[i][unc], minlength=r); c[0] = -1
            a = int(np.argmax(c)); self.cls[i] = a
            hit = self.R[i] == a; self.cnt += hit; unc &= ~hit

    def left(self): return int(np.count_nonzero(self.cnt == 0))

    def best_move(self, i):
        r = int(self.mods[i]); a = int(self.cls[i]); Ri = self.R[i]
        loss = int(np.count_nonzero((Ri == a) & (self.cnt == 1)))
        g = np.bincount(Ri[self.cnt == 0], minlength=r); g[0] = -1; g[a] = -1
        c = int(np.argmax(g)); return c, int(g[c]) - loss

    def move(self, i, c):
        Ri = self.R[i]; self.cnt[Ri == self.cls[i]] -= 1; self.cnt[Ri == c] += 1; self.cls[i] = c

    def descend(self, order=None):
        improved = True
        while improved:
            improved = False
            for i in (order if order is not None else range(len(self.mods))):
                c, d = self.best_move(i)
                if d > 0: self.move(i, c); improved = True

    def save(self, path, note=""):
        open(path, "w").write(f"# Q = {Q:,} (odd primes below it are the rows); {len(self.mods)} moduli = the odd primes up to {int(self.mods[-1])}; "
                              f"rows in no class: {self.left():,}. {note}\n" + " ".join(f"{int(r)}:{int(a)}" for r, a in zip(self.mods, self.cls)) + "\n")

if __name__ == "__main__":
    X = int(sys.argv[1]); secs = float(sys.argv[2]) if len(sys.argv) > 2 else 0; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    t0 = time.time(); C = Cover(X); print(f"{len(C.rows):,} rows, {len(C.mods)} moduli up to {int(C.mods[-1])} ({time.time() - t0:.0f} s)", flush=True)
    C.greedy(); g = C.left(); print(f"greedy (increasing order): {g:,} rows left ({time.time() - t0:.0f} s)", flush=True)
    C.descend(); d = C.left(); print(f"after 1-flip descent: {d:,} rows left ({time.time() - t0:.0f} s)", flush=True)
    rng = np.random.default_rng(seed); best = d; bestcls = C.cls.copy(); bestcnt = C.cnt.copy(); it = acc = 0; t1 = time.time()
    while time.time() - t1 < secs:                                            # iterated local search
        it += 1; k = int(rng.integers(2, 8)); idx = rng.choice(len(C.mods), k, replace=False)
        for i in idx:
            r = int(C.mods[i]); C.move(i, int(rng.integers(1, r)))
        C.descend(order=list(idx) + list(rng.permutation(len(C.mods))))
        v = C.left()
        if v <= best:
            if v < best: acc += 1; print(f"  local search {it}: {v:,} rows left ({time.time() - t0:.0f} s)", flush=True)
            best = v; bestcls = C.cls.copy(); bestcnt = C.cnt.copy()
        else: C.cls = bestcls.copy(); C.cnt = bestcnt.copy()
    C.save(f"cover_X{X}.txt" if Q == 1000003 else f"cover_X{X}_Q{Q}.txt", f"greedy {g:,}, descent {d:,}, local search ({it} rounds, seed {seed}) {best:,}")
    print(f"final: {best:,} rows left after {it} rounds of local search; written cover_X{X}.txt ({time.time() - t0:.0f} s)")
